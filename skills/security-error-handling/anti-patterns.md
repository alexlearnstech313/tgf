# SECURITY-ERROR-HANDLING — Anti-Patterns and Canonical Patterns

Nine anti-pattern + canonical-pattern pairs covering the most common error-handling failures. Each pair documents the broken approach, the failure mode, the authoritative source, the canonical fix, and the reason the fix holds.

Per `DEC-2026-05-17-003` Clause 1: every anti-pattern is paired with a canonical pattern.

---

## AP-1: Swallow-and-Allow Exception Handler in Security Path

### Anti-Pattern

```typescript
// TypeScript — authorization check that fails open
async function canAccessResource(userId: string, resourceId: string): Promise<boolean> {
  try {
    const access = await db.query(
      'SELECT 1 FROM resource_access WHERE user_id = $1 AND resource_id = $2',
      [userId, resourceId],
    );
    return access.rows.length > 0;
  } catch (e) {
    // Database error → permit (fails open)
    // The user gets access even when we couldn't verify they should have access
    return true;
  }
}
```

```python
# Python — JWT signature verification that fails open
import jwt

def verify_token(token: str) -> dict | None:
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
    except Exception as e:
        # Decode failure → return a "default" claims object that grants access
        # If verification fails for any reason (expired, malformed, wrong sig), proceed as admin
        return {'sub': 'system', 'role': 'admin'}
```

```typescript
// TypeScript — webhook signature verification with fail-open default
function verifyStripeSignature(payload: string, signature: string): boolean {
  try {
    return stripe.webhooks.constructEvent(payload, signature, WEBHOOK_SECRET) !== null;
  } catch (e) {
    // signature library threw — accept the webhook anyway
    return true;
  }
}
```

### Why It Fails

The security check has a binary outcome — grant or deny — and the handler chose the wrong default for the failure case. An exception during the check is not "this user is probably fine" — it is "the check did not run to completion, the security model says we don't know, default-deny says deny." Fail-open on security checks is the failure mode A10:2025 explicitly identifies as systemic.

These patterns are exploitable: an attacker who can trigger an exception in the security check (corrupt the JWT slightly, send a payload that triggers a library bug, exhaust database connections) gets the fail-open path. The triggers don't need to be exotic — production load, network blips, dependency upgrades that change exception types all hit this.

**Source for failure mode:** `OWASP-ASVS V16.5.3` (fail gracefully and securely, prevent fail-open); `OWASP-TOP10 A10:2025` (Mishandling of Exceptional Conditions); cross-ref `SECURITY-CORE Rule 5.2` (default-deny is the authorization-specific case).

### Canonical Pattern

```typescript
// TypeScript — fail-closed authorization check
async function canAccessResource(userId: string, resourceId: string): Promise<boolean> {
  try {
    const access = await db.query(
      'SELECT 1 FROM resource_access WHERE user_id = $1 AND resource_id = $2',
      [userId, resourceId],
    );
    return access.rows.length > 0;
  } catch (e) {
    // Database error → deny, log for investigation, surface to caller
    logger.error('authz_check_failed', {
      userId,
      resourceId,
      error: e instanceof Error ? e.message : String(e),
    });
    return false;  // fail-closed
  }
}
```

```python
# Python — fail-closed JWT verification
import jwt
import logging

logger = logging.getLogger(__name__)

def verify_token(token: str) -> dict | None:
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        logger.info('token_verification_failed', extra={'reason': 'expired'})
        return None
    except jwt.InvalidTokenError as e:
        logger.warning('token_verification_failed', extra={'reason': str(e)})
        return None
    # Other unexpected exceptions propagate to the last-resort handler (Rule 5.5)
    # which will fail-close at the request boundary
```

```typescript
// TypeScript — fail-closed webhook signature verification with caller-handled re-raise
function verifyStripeSignature(payload: string, signature: string): Event {
  try {
    return stripe.webhooks.constructEvent(payload, signature, WEBHOOK_SECRET);
  } catch (e) {
    logger.warn('webhook_signature_invalid', {
      error: e instanceof Error ? e.message : String(e),
    });
    // Re-throw — the route handler returns 400 and does NOT process the webhook
    throw new WebhookSignatureError('Invalid signature');
  }
}
```

### Why It Works

The exception branch denies (returns false / None / re-raises) and logs the cause. Legitimate users who hit a transient failure see "something went wrong" and retry; the security model is not compromised. The discipline scales: every security check in the codebase has the same shape, and the security audit (Stage 5 Phase 2) can grep for `catch.*return\s+true` to find violations.

**Additional considerations:** *Specific exception types vs catch-all.* Catching specific exception types (`InvalidTokenError`, `ExpiredSignatureError`) makes the handler more precise and lets unknown exceptions propagate to the last-resort handler (Rule 5.5). *Re-raise vs return-false.* For verification functions called from a single, security-aware route handler, re-raising lets the route handler choose the response code; for utility-like checks called from many places, returning false is more flexible — both are valid patterns. *Logging detail.* Log enough to investigate (correlation ID, error category, sanitized message) without logging the secret being verified.

---

## AP-2: Stack Trace / Exception Detail in User-Facing Error Response

### Anti-Pattern

```typescript
// Express — exception details leak to client
app.get('/api/users/:id', async (req, res) => {
  try {
    const user = await getUserById(req.params.id);
    res.json(user);
  } catch (e) {
    // Stack trace and internal error message reach the user
    res.status(500).json({
      error: e instanceof Error ? e.message : String(e),
      stack: e instanceof Error ? e.stack : undefined,
    });
  }
});
```

```python
# Flask — debug mode left enabled in production
from flask import Flask, jsonify

app = Flask(__name__)
app.debug = True  # NEVER in production — interactive debugger on every error

# Or this pattern, even in non-debug mode:
@app.errorhandler(500)
def server_error(e):
    import traceback
    return jsonify({
        'error': str(e),
        'traceback': traceback.format_exc(),
    }), 500
```

```html
<!-- Django/Rails default debug page accidentally enabled in production -->
<!-- Full stack trace, environment variables, settings module, request data — all exposed -->
```

### Why It Fails

The information disclosed in detailed error responses directly aids attacker reconnaissance:
- **Stack trace:** Reveals framework name and version (e.g., "express@4.17.1"), library versions, source-code file paths, function signatures. An attacker uses this to look up known CVEs in the disclosed versions.
- **Exception messages:** Often contain query fragments (`Duplicate entry 'admin@example.com' for key 'users.email_unique'` reveals the database schema and confirms user enumeration), file paths (`ENOENT: no such file '/var/app/secrets/sso-key.pem'`), connection strings, configuration values.
- **Debug pages:** Django's default DEBUG=True error page exposes all environment variables, all loaded settings, the full request, session data, and template context. Rails' equivalent (`config.consider_all_requests_local = true`) similarly. Both are common production-misconfiguration breaches.

The OWASP Cheat Sheet's exact framing: "Unhandled errors can assist an attacker in this initial phase" of reconnaissance.

**Source for failure mode:** `OWASP-ASVS V16.5.1`; `OWASP-CHEAT-EH`; `CWE-209` (Information Exposure Through Error Message).

### Canonical Pattern

```typescript
// Express — generic response + correlation ID + server-side detailed log
import { randomUUID } from 'crypto';

// Middleware: attach a correlation ID to every request
app.use((req, res, next) => {
  req.correlationId = (req.headers['x-correlation-id'] as string) ?? randomUUID();
  res.setHeader('X-Correlation-Id', req.correlationId);
  next();
});

app.get('/api/users/:id', async (req, res, next) => {
  try {
    const user = await getUserById(req.params.id);
    res.json(user);
  } catch (e) {
    next(e);  // delegate to last-resort error handler (Rule 5.5)
  }
});

// Last-resort handler — RFC 7807 generic response, full detail logged
app.use((err: Error, req: Request, res: Response, next: NextFunction) => {
  logger.error('unhandled_exception', {
    correlationId: req.correlationId,
    method: req.method,
    path: req.path,
    errorClass: err.constructor.name,
    errorMessage: err.message,
    stack: err.stack,
  });
  res.status(500).type('application/problem+json').json({
    type: 'about:blank',
    title: 'Internal Server Error',
    status: 500,
    detail: 'An unexpected error occurred. Please try again or contact support.',
    instance: req.correlationId,
  });
});
```

```python
# FastAPI — RFC 7807 response + correlation ID + server-side log
import uuid
import logging
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

app = FastAPI()
logger = logging.getLogger(__name__)

@app.middleware('http')
async def correlation_id_middleware(request: Request, call_next):
    cid = request.headers.get('x-correlation-id') or str(uuid.uuid4())
    request.state.correlation_id = cid
    response = await call_next(request)
    response.headers['X-Correlation-Id'] = cid
    return response

@app.exception_handler(Exception)
async def last_resort_handler(request: Request, exc: Exception):
    cid = getattr(request.state, 'correlation_id', 'unknown')
    logger.exception(
        'unhandled_exception',
        extra={'correlation_id': cid, 'path': request.url.path},
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        media_type='application/problem+json',
        content={
            'type': 'about:blank',
            'title': 'Internal Server Error',
            'status': 500,
            'detail': 'An unexpected error occurred. Please try again or contact support.',
            'instance': cid,
        },
    )
```

### Why It Works

The user receives a stable, generic message with the correlation ID — no internals leaked. The full exception detail (class, message, stack trace, request path) goes to the server-side log keyed by the same correlation ID. When the user reports the error and includes the correlation ID, engineering finds the exact log entry by ID search. RFC 7807 `application/problem+json` is the established format for API error responses; HTML responses use a static error page with the ID embedded.

**Additional considerations:** *Production vs development.* In non-production environments, debug mode is fine — it accelerates iteration. The discipline is environment-aware configuration that *guarantees* debug is off in production (verified by deployment automation). *Per-status pages for HTML.* For web apps, register custom 404 / 500 / 403 pages — the framework's default debug page must never be reachable in production. *RFC 9457.* The IETF updated RFC 7807 to RFC 9457 in 2023 — the format is the same; the newer RFC adds clarifications. Both are acceptable citations; `application/problem+json` is the wire format either way. *Validation errors vs 500s.* For 4xx errors (validation, auth failures, not-found), the response is similar but appropriate to the status code — the same correlation-ID-and-generic-message pattern; the difference is that the message may be slightly more specific (e.g., "Email is required" for a 400) because the cause is the client's input, not server internal state.

---

## AP-3: Catch-All Empty Handler — Silent Swallow

### Anti-Pattern

```python
# Python — bare except: pass swallows everything including KeyboardInterrupt
def process_user_data(data):
    try:
        validated = validate(data)
        saved = save(validated)
        notify(saved)
    except:
        pass  # any failure in any of three steps is silently lost
```

```typescript
// TypeScript — empty catch swallows error
async function uploadProfile(file: File, userId: string) {
  try {
    await uploadToS3(file);
    await updateDatabase(userId, file.name);
    await invalidateCache(userId);
  } catch (e) {
    // Silently swallow — caller assumes upload succeeded
  }
}
```

```ruby
# Ruby — rescue without action
def deliver_notification(user, message)
  send_email(user, message)
  send_push(user, message)
  log_delivery(user, message)
rescue => e
  # nothing
end
```

```java
// Java — empty catch
public void recordAction(User user, String action) {
  try {
    auditLog.write(user.getId(), action, Instant.now());
    metrics.increment("action_recorded");
  } catch (Exception e) {
    // empty
  }
}
```

### Why It Fails

The exception conveys information — what failed, where, why — and the empty catch destroys that information. Downstream code continues as if nothing happened, often producing a worse failure later (corrupted state, missing audit records, inconsistent caches). The trail back to the cause is gone because the exception was silenced at catch-time.

Security implications: when the silenced exception is in a security-relevant path (audit log write fails silently → privileged actions go un-audited; cache invalidation fails silently → stale authorization data persists; notification fails silently → security alerts don't reach the on-call), the system continues in an insecure state without surfacing the problem.

The Python `except: pass` is particularly bad — `except` with no exception type catches `KeyboardInterrupt`, `SystemExit`, and `MemoryError` along with regular exceptions, breaking interactive interrupt and resource-exhaustion handling.

**Source for failure mode:** `OWASP-ASVS V16.5.3`; `CWE-754`, `CWE-755`; `OWASP-TOP10 A10:2025`.

### Canonical Pattern

```python
# Python — catch specific, log, decide policy
import logging
logger = logging.getLogger(__name__)

def process_user_data(data):
    try:
        validated = validate(data)
    except ValidationError as e:
        logger.warning('validation_failed', extra={'error': str(e)})
        raise  # propagate to caller; this is not a recoverable failure
    try:
        saved = save(validated)
    except DatabaseError as e:
        logger.error('save_failed', extra={'error': str(e)})
        raise
    try:
        notify(saved)
    except NotificationError as e:
        # Notification failure is recoverable (queue retry); log and continue
        logger.warning('notify_failed', extra={
            'error': str(e),
            'saved_id': saved.id,
            'will_retry': True,
        })
        retry_queue.enqueue('notify', saved.id)
    return saved
```

```typescript
// TypeScript — explicit decisions per failure point
async function uploadProfile(file: File, userId: string, correlationId: string) {
  try {
    await uploadToS3(file);
  } catch (e) {
    logger.error('s3_upload_failed', { correlationId, userId, error: errMessage(e) });
    throw new UploadError('Upload failed', { cause: e });  // re-raise; caller cannot proceed
  }
  try {
    await updateDatabase(userId, file.name);
  } catch (e) {
    // Database update failed AFTER S3 upload succeeded — partial-failure state (see AP-6)
    logger.error('db_update_failed_after_s3', { correlationId, userId, error: errMessage(e) });
    // Compensating action: delete the S3 object
    try {
      await deleteFromS3(file.name);
    } catch (deleteErr) {
      logger.error('s3_compensating_delete_failed', { correlationId, userId, error: errMessage(deleteErr) });
      // Surface to operations for manual cleanup
      opsAlert.fire('orphan_s3_object', { userId, file: file.name });
    }
    throw new UploadError('Upload completed but record save failed', { cause: e });
  }
  try {
    await invalidateCache(userId);
  } catch (e) {
    // Cache invalidation is best-effort — log and continue; cache will expire normally
    logger.warning('cache_invalidate_failed', { correlationId, userId, error: errMessage(e) });
  }
}
```

### Why It Works

Every catch block is a decision point with three options: (1) log and re-raise (propagate the failure); (2) log and apply policy (retry, fallback, compensating action); (3) log and continue (best-effort steps that don't compromise the operation). The decision is explicit per failure point, not a blanket swallow. Specific exception types let unknown exceptions propagate to the last-resort handler (Rule 5.5).

**Additional considerations:** *When swallowing is correct.* Some "fire and forget" paths legitimately swallow — analytics emission that's purely advisory, optional notifications that don't affect business logic. Even then, log the failure (`debug` or `info` level if truly low-priority); the empty catch is the anti-pattern, not the choice to continue. *Linter configuration.* Most linters flag bare except / empty catch (ESLint `no-empty`, Python flake8 `E722`, pylint `bare-except`). Enabling these as errors (not warnings) is part of the discipline. *Re-raise patterns per language.* Python `raise` (re-raises the current exception), `raise CustomError from e` (chains the original); JavaScript/TypeScript `throw e` or `throw new Error(...,{cause: e})`; Java `throw new CustomException(e)`; Go's error wrapping (`fmt.Errorf("...: %w", err)`).

---

## AP-4: Default-Permit on External-Service Failure

### Anti-Pattern

```typescript
// Express — auth provider unreachable → allow request
async function authMiddleware(req: Request, res: Response, next: NextFunction) {
  const token = req.headers.authorization?.replace('Bearer ', '');
  try {
    const session = await authProvider.verifySession(token, { timeout: 30_000 });
    req.user = session.user;
  } catch (e) {
    // Auth provider down, slow, or threw — let the request through anyway
    // "Better to have a brief unauthenticated period than to fail all requests"
    req.user = { id: 'unknown', role: 'guest' };
  }
  next();
}
```

```python
# Python — secret store unreachable → fall back to env var (no rotation possible)
import os

def get_database_password() -> str:
    try:
        return secret_manager.get_secret('db-password').value
    except Exception as e:
        # Secret manager unreachable — use the env var as fallback
        # Problem: this env var was set months ago and never rotated
        return os.environ['DB_PASSWORD_FALLBACK']
```

```typescript
// TypeScript — CAPTCHA service down → skip CAPTCHA
async function submitForm(req: Request, res: Response) {
  try {
    await captchaService.verify(req.body.captchaToken);
  } catch (e) {
    // CAPTCHA service unavailable — process the submission anyway
    logger.warn('captcha_unavailable_skipping');
  }
  await processSubmission(req.body);
  res.json({ status: 'ok' });
}
```

### Why It Fails

The fail-open pattern at the external-dependency boundary is the same A10:2025 risk as inline fail-open (AP-1), but with an additional infrastructure dimension. An attacker who can deny-of-service the auth provider can bypass authentication entirely (the most direct exploitation); without DoS, the same path triggers during legitimate outages where the security control is silently skipped.

The CAPTCHA case is the same pattern in miniature — the CAPTCHA exists to defeat automated submission; the fail-open path defeats the CAPTCHA without an attacker needing to break it.

The secret-store fallback case has a subtler failure mode: it works *most* of the time using the actively-rotated secret, but when the secret store has problems, the system silently uses an old fallback that may have been compromised since it was last set.

**Source for failure mode:** `OWASP-ASVS V16.5.2` (continue securely when external resource access fails) + `OWASP-ASVS V16.5.3` (fail gracefully and securely, prevent fail-open); `OWASP-TOP10 A10:2025`.

### Canonical Pattern

```typescript
// Express — auth provider unreachable → fail closed; circuit breaker prevents cascading retries
import CircuitBreaker from 'opossum';

const verifySession = new CircuitBreaker(
  (token: string) => authProvider.verifySession(token, { timeout: 5_000 }),
  {
    timeout: 5_000,
    errorThresholdPercentage: 50,
    resetTimeout: 30_000,
  },
);

async function authMiddleware(req: Request, res: Response, next: NextFunction) {
  const token = req.headers.authorization?.replace('Bearer ', '');
  if (!token) {
    return res.status(401).type('application/problem+json').json({
      type: 'about:blank',
      title: 'Unauthorized',
      status: 401,
      detail: 'Authentication required.',
      instance: req.correlationId,
    });
  }
  try {
    const session = await verifySession.fire(token);
    req.user = session.user;
    next();
  } catch (e) {
    // Auth provider failure (timeout, circuit-breaker open, threw) → reject
    logger.warn('auth_verification_failed', {
      correlationId: req.correlationId,
      reason: e instanceof Error ? e.message : String(e),
    });
    return res.status(503).type('application/problem+json').json({
      type: 'about:blank',
      title: 'Service Temporarily Unavailable',
      status: 503,
      detail: 'Authentication is temporarily unavailable. Please retry.',
      instance: req.correlationId,
    });
  }
}
```

```typescript
// CAPTCHA — fail closed; surface explicit error
async function submitForm(req: Request, res: Response) {
  try {
    await captchaService.verify(req.body.captchaToken, { timeout: 5_000 });
  } catch (e) {
    logger.warn('captcha_verify_failed', { correlationId: req.correlationId });
    return res.status(503).type('application/problem+json').json({
      type: 'about:blank',
      title: 'Verification Unavailable',
      status: 503,
      detail: 'Anti-spam verification is temporarily unavailable. Please retry.',
      instance: req.correlationId,
    });
  }
  await processSubmission(req.body);
  res.json({ status: 'ok' });
}
```

### Why It Works

External dependency failure surfaces as a 503 Service Temporarily Unavailable — the user is told something is broken and to retry. The security model is intact: no request bypasses the security check by virtue of a dependency outage. The circuit breaker (opossum in this example; Resilience4j for Java, Polly for .NET, hystrix-go for Go) prevents the auth-provider outage from cascading into a retry storm; once the failure threshold is hit, the circuit opens and the application fails fast for a cool-down window before re-trying.

**Additional considerations:** *Graceful degradation for non-security paths.* When the *non-security* data layer is unreachable (recommendation service down, profile cache down), graceful degradation is appropriate — serve cached data, show "loading..." UI, queue writes. The discipline is the bright line: security checks fail closed; non-security data may degrade. *Secret store failures.* For secrets, prefer secret-manager + KMS architectures with multi-region replication so the failure mode is "use the regional replica" rather than "fall back to a stale local copy." Where local fallback is the only option for boot-time secrets, the fallback secret has the same rotation cadence as the primary. *Monitoring the circuit breaker.* Open-circuit state should alert; persistent open means the dependency is degraded and the application is fail-closing requests — this needs operations attention.

---

## AP-5: No Last-Resort Handler — Unhandled Exception Crashes / Leaks

### Anti-Pattern

```typescript
// Express — no error middleware registered
const app = express();
app.use(express.json());
app.get('/api/items/:id', async (req, res) => {
  const item = await db.findItem(req.params.id);  // can throw
  res.json(item);
});
// No app.use((err, req, res, next) => ...) at the bottom
// Express's default error handler renders an HTML page with stack trace in dev mode,
// and emits a generic 500 in production but with framework version disclosed in headers
app.listen(3000);
```

```python
# Flask — debug mode in production (the worst combination)
from flask import Flask
app = Flask(__name__)
# No app.errorhandler registered
# In debug mode (which sometimes ships): full interactive debugger page
# In non-debug mode: minimal but no correlation ID, no structured log of the exception
if __name__ == '__main__':
    app.run(debug=True)  # explicitly bad
```

```go
// Go — goroutine panic with no recover; process crashes
func handleRequest(w http.ResponseWriter, r *http.Request) {
  go backgroundWork(r.Body)  // if this panics, it crashes the entire process
  w.WriteHeader(200)
}

func backgroundWork(body io.Reader) {
  // Anything that panics here takes down the whole server
  data, _ := io.ReadAll(body)
  result := processWithoutNilCheck(data)  // could panic
  saveResult(result)
}
```

### Why It Fails

Without a last-resort handler:
- **Unhandled exceptions in request handlers** reach the framework's default behavior — typically a stack-trace error page (in dev, sometimes shipped to prod), an unstructured 500 with no correlation ID, or a process crash for runtimes that don't auto-recover.
- **Unhandled exceptions in async tasks** (background jobs, queue workers, Promise chains without `.catch`) silently drop or surface in framework logs without the request context attached.
- **Goroutine / async panics** in Go and similar runtimes can take down the entire process if not recovered.

The result is some combination of: information disclosure (stack trace to user), missed incident detection (no structured log entry, no alert), and service unavailability (process crashed). The OWASP guidance is explicit: V16.5.4 calls for a "last resort" handler precisely to avoid these outcomes.

**Source for failure mode:** `OWASP-ASVS V16.5.4`.

### Canonical Pattern

```typescript
// Express — register last-resort error middleware after all routes
const app = express();
app.use(express.json());
app.use(correlationIdMiddleware);
app.use(authMiddleware);

app.get('/api/items/:id', async (req, res, next) => {
  try {
    const item = await db.findItem(req.params.id);
    res.json(item);
  } catch (e) {
    next(e);  // delegate to last-resort handler
  }
});

// LAST — registered after all routes; matches the (err, req, res, next) signature
app.use((err: Error, req: Request, res: Response, next: NextFunction) => {
  const cid = (req as any).correlationId ?? 'unknown';
  logger.error('unhandled_request_exception', {
    correlationId: cid,
    method: req.method,
    path: req.path,
    errorClass: err.constructor.name,
    errorMessage: err.message,
    stack: err.stack,
  });
  securityEventLog.emit({
    event: 'unexpected_exception',
    correlationId: cid,
    severity: 'warn',
  });  // V16.3.4 — log unexpected errors as security events
  res.status(500).type('application/problem+json').json({
    type: 'about:blank',
    title: 'Internal Server Error',
    status: 500,
    detail: 'An unexpected error occurred. Please try again or contact support.',
    instance: cid,
  });
});

// Catch async exceptions outside the request context
process.on('unhandledRejection', (reason, promise) => {
  logger.error('unhandled_promise_rejection', {
    reason: reason instanceof Error ? reason.message : String(reason),
  });
});
process.on('uncaughtException', (e) => {
  logger.error('uncaught_exception', { errorClass: e.constructor.name, message: e.message, stack: e.stack });
  // Don't exit immediately — let logger flush
  setTimeout(() => process.exit(1), 1000);
});

app.listen(3000);
```

```go
// Go — recover in every goroutine; central panic handler in HTTP middleware
func panicRecoveryMiddleware(next http.Handler) http.Handler {
  return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
    defer func() {
      if rec := recover(); rec != nil {
        cid := r.Context().Value(correlationIDKey).(string)
        log.Error().
          Str("correlation_id", cid).
          Str("path", r.URL.Path).
          Interface("recovered", rec).
          Bytes("stack", debug.Stack()).
          Msg("panic recovered")
        w.Header().Set("Content-Type", "application/problem+json")
        w.WriteHeader(http.StatusInternalServerError)
        _ = json.NewEncoder(w).Encode(map[string]any{
          "type": "about:blank",
          "title": "Internal Server Error",
          "status": 500,
          "detail": "An unexpected error occurred. Please try again or contact support.",
          "instance": cid,
        })
      }
    }()
    next.ServeHTTP(w, r)
  })
}

// For goroutines outside the request handler, wrap each:
func goSafe(fn func()) {
  go func() {
    defer func() {
      if rec := recover(); rec != nil {
        log.Error().Interface("recovered", rec).Bytes("stack", debug.Stack()).Msg("goroutine panic")
      }
    }()
    fn()
  }()
}
```

### Why It Works

Every exception that escapes individual handlers reaches the last-resort handler, which: (a) returns the generic-message + correlation-ID response (Rule 5.2); (b) logs the full exception with correlation ID; (c) emits a security event for the unexpected exception (V16.3.4); (d) keeps the process alive (for long-running servers). The Go panic-recovery middleware contains the panic within the request boundary — one bad request doesn't crash the server.

**Additional considerations:** *Position matters.* Express error middleware must be the *last* `app.use` call after all routes — middleware registered after errors fire is registered too late. *Async unhandled.* Node's `unhandledRejection` and `uncaughtException` are last-resort safety nets, not the primary handlers — they catch what was missed elsewhere. *Process behavior on `uncaughtException`.* The recommended pattern is to log, allow async loggers time to flush, then exit and rely on the orchestration system to restart the process. Continuing after `uncaughtException` is dangerous (the runtime may be in an inconsistent state). *Background-task frameworks.* Worker frameworks (Celery, Sidekiq, Bull, Resque) have their own error-handling hooks — register the last-resort handler there too.

---

## AP-6: Generic 200 OK Despite Partial Failure

### Anti-Pattern

```typescript
// TypeScript — multi-step signup; some steps fail; returns 201 anyway
async function signup(req: Request, res: Response) {
  const user = await db.createUser(req.body);  // step 1
  try {
    await stripe.customers.create({ email: user.email });  // step 2
  } catch (e) {
    // Stripe failed but we already created the user — log and proceed
    logger.warn('stripe_create_failed', { userId: user.id });
  }
  try {
    await sendgrid.send({ to: user.email, template: 'welcome' });  // step 3
  } catch (e) {
    logger.warn('welcome_email_failed', { userId: user.id });
  }
  // Return success even though steps 2 and 3 may have failed
  res.status(201).json({ user });
}
```

```python
# Python — privilege grant succeeds, audit log fails, returns success
def grant_admin(target_user_id: str, granter_id: str):
    db.users.update({'_id': target_user_id}, {'$set': {'role': 'admin'}})  # step 1: privilege change
    try:
        audit_log.write({
            'event': 'admin_granted',
            'target': target_user_id,
            'granter': granter_id,
            'timestamp': now_utc(),
        })  # step 2: required for compliance
    except Exception as e:
        # Audit log failed — but the privilege grant succeeded; "we'll fix the audit later"
        logger.warning('audit_log_failed', extra={'target': target_user_id})
    return {'status': 'granted'}
```

### Why It Fails

The caller is told the operation succeeded, but the system state is inconsistent: a user record exists without a Stripe customer (causing payment failures later), a welcome email never sent (causing onboarding confusion), an admin role was granted without an audit-log entry (causing compliance gap and incident-response blind spot). The trail back to "step 2 failed" exists only in a log entry that nobody noticed.

The audit-log case is particularly bad: the privilege grant happened, but no audit-log entry exists. From the audit-log's perspective, the privilege grant didn't happen — which means the next-step incident response cannot reconstruct who got admin when. Compliance frameworks (SOC 2, ISO 27001) require audit log integrity; this pattern silently breaks it.

**Source for failure mode:** `OWASP-ASVS V16.5.3`; `CWE-755`; `OWASP-TOP10 A10:2025`.

### Canonical Pattern

```typescript
// TypeScript — transaction + compensating action + explicit status
async function signup(req: Request, res: Response) {
  // Step 1: create user inside a transaction
  const user = await db.transaction(async (tx) => {
    return tx.users.create(req.body);
  });

  // Step 2: create Stripe customer — required for the signup to be "complete"
  let stripeCustomer;
  try {
    stripeCustomer = await stripe.customers.create({ email: user.email });
    await db.users.update(user.id, { stripeCustomerId: stripeCustomer.id });
  } catch (e) {
    // Compensating action: delete the user (signup didn't actually complete)
    logger.error('stripe_create_failed_rolling_back', { userId: user.id, error: errMessage(e) });
    await db.users.delete(user.id);
    return res.status(503).type('application/problem+json').json({
      type: 'about:blank',
      title: 'Signup Incomplete',
      status: 503,
      detail: 'Account creation failed. Please retry.',
      instance: req.correlationId,
    });
  }

  // Step 3: welcome email is best-effort; if it fails, retry queue handles it
  try {
    await sendgrid.send({ to: user.email, template: 'welcome' });
  } catch (e) {
    logger.warn('welcome_email_failed_enqueueing_retry', { userId: user.id });
    await retryQueue.enqueue('welcome_email', { userId: user.id });
  }

  res.status(201).json({ user });
}
```

```python
# Python — privilege grant uses transaction; audit failure aborts the grant
from contextlib import contextmanager

def grant_admin(target_user_id: str, granter_id: str):
    with db.transaction() as tx:
        # Both steps run in the same transaction; either both commit or both roll back
        tx.users.update(
            {'_id': target_user_id},
            {'$set': {'role': 'admin'}},
        )
        tx.audit_log.insert({
            'event': 'admin_granted',
            'target': target_user_id,
            'granter': granter_id,
            'timestamp': now_utc(),
        })
        # tx commits on context exit; if audit_log insert raises, the user update rolls back
    return {'status': 'granted'}
```

### Why It Works

The signup canonical pattern uses (a) transactional rollback for the database step, (b) compensating action (deleting the orphan user) when Stripe fails — the signup either completes fully or doesn't happen, (c) explicit best-effort for the welcome email with retry-queue followup. The privilege-grant canonical pattern wraps both the privilege change and the audit log in a single transaction so they commit together or roll back together — there is no path where the grant happens but the audit log doesn't.

**Additional considerations:** *Saga pattern.* For operations across multiple systems that don't share a transaction boundary, the saga pattern is the canonical solution: each step has a designed compensating action; when step N fails, compensating actions for steps 1 through N-1 run in reverse. *Two-phase commit.* For distributed transactions, 2PC is technically possible but rarely the right answer at startup scale; sagas are simpler and more failure-tolerant. *Idempotency keys.* For retry safety across the operation boundary, an idempotency key per signup prevents double-processing if the user retries. *Explicit partial-success responses.* When partial success is genuinely the right semantics (a batch upload of 100 items where 7 fail validation), HTTP 207 Multi-Status or a structured response with per-item status communicates the partial outcome explicitly — never a flat 200 OK.

---

## AP-7: Retry Loop Around Security Check Masks Transient Failure

### Anti-Pattern

```python
# Python — retry the signature verification until it succeeds
import time

def verify_webhook(payload: bytes, signature: str) -> bool:
    for attempt in range(5):
        try:
            if hmac_verify(payload, signature, SECRET):
                return True
        except Exception as e:
            logger.warning(f'verify attempt {attempt} failed: {e}')
            time.sleep(0.5 * (2 ** attempt))  # backoff and retry
    return False
```

```typescript
// TypeScript — retry the authorization check until it succeeds or N times
async function isAuthorized(userId: string, resource: string): Promise<boolean> {
  for (let attempt = 0; attempt < 3; attempt++) {
    try {
      const result = await authzService.check({ userId, resource });
      return result.allowed;
    } catch (e) {
      logger.warning('authz_check_failed_retrying', { attempt, error: errMessage(e) });
      await sleep(500);
    }
  }
  // Fell out of retry loop — return true to be "user-friendly"
  return true;  // catastrophic — fail open after retries exhausted
}
```

### Why It Fails

Retries are appropriate for **idempotent, non-security data fetches** where transient failure should not propagate to the user. They are **inappropriate for security checks** for two reasons:

1. **The check may have a non-transient reason for failing** — the signature might be invalid, the user might genuinely lack authorization — and retrying won't change the outcome but will mask the failure-as-deny under "we'll keep trying."

2. **Retries amplify the attack surface** for security checks. An attacker with a slightly-corrupted JWT triggering a verification exception gets multiple chances; an attacker hitting a slow-but-vulnerable code path gets multiple chances; an attacker performing timing analysis on the verification gets more samples.

The Python case at minimum *might* be acceptable for hmac_verify if the underlying secret store had transient issues — but the canonical pattern reads the secret once and fails closed on hmac mismatch, not retries on it. The TypeScript case is the worst form: fail-open as the retry-exhausted default, combining AP-1 (swallow-and-allow) with AP-7 (retry-mask).

**Source for failure mode:** `OWASP-ASVS V16.5.3`; cross-ref `OWASP-TOP10 A10:2025`; AP-1 cross-reference.

### Canonical Pattern

```python
# Python — single attempt; fail closed on any failure
import hmac
import hashlib
import logging

logger = logging.getLogger(__name__)

def verify_webhook(payload: bytes, signature: str) -> bool:
    try:
        expected = hmac.new(SECRET, payload, hashlib.sha256).hexdigest()
        # Constant-time comparison defeats timing attacks
        if hmac.compare_digest(expected, signature):
            return True
        logger.info('webhook_signature_mismatch')
        return False
    except Exception as e:
        # Any unexpected exception → deny, log, surface to last-resort handler
        logger.error('webhook_verification_error', extra={'error': str(e)})
        return False
```

```typescript
// TypeScript — single attempt; fail closed; let last-resort handler take it from there
async function isAuthorized(userId: string, resource: string): Promise<boolean> {
  try {
    const result = await authzService.check({ userId, resource });
    return result.allowed;
  } catch (e) {
    // Authorization service failure → deny
    logger.warn('authz_check_failed', {
      userId,
      resource,
      error: errMessage(e),
    });
    return false;  // fail-closed
  }
}
```

### Why It Works

A single attempt is the correct discipline for security checks — the check either succeeds definitively, fails definitively, or errors. Each of the latter two outcomes means *deny*. If the application needs the security check to be highly available (rare transient failures), the answer is high-availability infrastructure for the security dependency (the auth service, the secret store), not retry-with-fail-open in the application layer. *Constant-time comparison* (`hmac.compare_digest`, `crypto.timingSafeEqual`) is a separate but related defense — covered in `security-cryptography` (Phase 6 commit 4/12).

**Additional considerations:** *Retries for non-security paths.* Database queries for application data, third-party API fetches for non-security data, queue dequeue operations — these benefit from retry-with-backoff. The line is whether the operation gates a security decision. *Exception classification.* "Resource temporarily unavailable" exceptions (network timeout) and "definitive failure" exceptions (signature invalid) are conceptually different — but for security checks, both result in *deny*. Distinguishing them only matters for the error message to the user (503 vs 401) and the log entry, not for the check's outcome.

---

## AP-8: No Correlation ID — User Can't Help Debug

### Anti-Pattern

```typescript
// Express — generic error response with no identifier
app.use((err, req, res, next) => {
  logger.error('error', { error: err.message, stack: err.stack });
  res.status(500).json({
    error: 'Something went wrong',
  });
});
```

```python
# Flask — same pattern, no correlation ID surfaced
@app.errorhandler(Exception)
def handle_exception(e):
    logger.exception('unhandled')
    return jsonify({'error': 'internal server error'}), 500
```

### Why It Fails

The user reports "I got an error at around 3pm yesterday." The engineer searches logs by timestamp window — finds 200 candidate entries. The engineer asks "what were you doing?" — gets imprecise description. The engineer tries to reproduce; can't; the user moved on. The investigation stalls because the engineer cannot link user-facing error to server-side log entry with certainty.

This is not a security vulnerability in the direct sense, but it's a security-relevant failure: when a user reports something that *might* be a security issue (the system did something unexpected with their data), the investigation must be fast and certain — and without correlation IDs, it isn't.

**Source for failure mode:** `OWASP-ASVS V16.2.1` (necessary metadata for detailed investigation timeline); `OWASP-CHEAT-EH` (centralized handler with traceable IDs).

### Canonical Pattern

```typescript
// Express — correlation ID middleware + propagation + surfacing
import { randomUUID } from 'crypto';

app.use((req, res, next) => {
  // Accept upstream correlation ID if present (load balancer, gateway); otherwise generate
  req.correlationId = (req.headers['x-correlation-id'] as string) ?? randomUUID();
  res.setHeader('X-Correlation-Id', req.correlationId);
  next();
});

// Downstream service calls propagate the ID
async function callDownstream(req: Request, payload: unknown) {
  return fetch('https://downstream.internal/api', {
    headers: {
      'content-type': 'application/json',
      'x-correlation-id': req.correlationId,  // propagate
    },
    body: JSON.stringify(payload),
  });
}

// Error response includes the ID
app.use((err, req, res, next) => {
  logger.error('unhandled', {
    correlationId: req.correlationId,
    error: err.message,
    stack: err.stack,
  });
  res.status(500).type('application/problem+json').json({
    type: 'about:blank',
    title: 'Internal Server Error',
    status: 500,
    detail: 'An unexpected error occurred. Please contact support and include the reference ID.',
    instance: req.correlationId,  // RFC 7807 instance field
  });
});
```

```python
# Python — same pattern in FastAPI using context vars for propagation
import uuid
from contextvars import ContextVar
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

correlation_id_ctx: ContextVar[str] = ContextVar('correlation_id', default='unknown')
app = FastAPI()

@app.middleware('http')
async def correlation_id_middleware(request: Request, call_next):
    cid = request.headers.get('x-correlation-id') or str(uuid.uuid4())
    token = correlation_id_ctx.set(cid)
    request.state.correlation_id = cid
    try:
        response = await call_next(request)
        response.headers['X-Correlation-Id'] = cid
        return response
    finally:
        correlation_id_ctx.reset(token)

@app.exception_handler(Exception)
async def unhandled(request: Request, exc: Exception):
    cid = request.state.correlation_id
    logger.exception('unhandled', extra={'correlation_id': cid})
    return JSONResponse(
        status_code=500,
        media_type='application/problem+json',
        content={
            'type': 'about:blank',
            'title': 'Internal Server Error',
            'status': 500,
            'detail': 'An unexpected error occurred. Please contact support and include the reference ID.',
            'instance': cid,
        },
    )
```

### Why It Works

The correlation ID is generated once per request, propagated to downstream calls via header, attached to every log entry, and surfaced in error responses. User reports the ID; engineer searches by ID; full context surfaces. Distributed traces (OpenTelemetry) make this even more powerful — the entire request graph is visible across service boundaries.

**Additional considerations:** *W3C Trace Context.* The `traceparent` header (`00-<trace-id-32>-<span-id-16>-<flags-2>`) is the modern observability standard; modern observability stacks (OpenTelemetry, Datadog, Honeycomb) automatically propagate it. Using `traceparent` as the correlation ID, or generating a separate correlation ID and binding it to the trace, both work. *Don't expose user identifiers.* The correlation ID is per-request; it's emitted in error responses, in URLs, in logs. Using a user identifier as the correlation ID would expose it. Keep them separate; the log entry can include both. *Format choice.* UUID v4 is the most common; UUID v7 (time-ordered) is gaining adoption. Both are 128-bit values that look opaque to users.

---

## AP-9: Catch-Specific-Then-Continue — Lookup Failure Looks Like Empty Result

### Anti-Pattern

```typescript
// TypeScript — database lookup; on timeout, return null as if no row found
async function findUserPreferences(userId: string): Promise<UserPreferences | null> {
  try {
    return await db.preferences.findOne({ userId, timeout: 1_000 });
  } catch (e) {
    if (e instanceof DatabaseTimeoutError) {
      // Treat timeout as "no preferences found" — let caller use defaults
      return null;
    }
    throw e;
  }
}

// Caller can't distinguish "no row" from "lookup failed"
async function applyPreferences(userId: string) {
  const prefs = await findUserPreferences(userId);
  if (prefs === null) {
    // Apply defaults — but if this was a timeout, we might be missing CRITICAL security settings
    // e.g., the user's `requireMFA: true` preference was set, but timeout → use default `requireMFA: false`
    applyDefaults(userId);
  } else {
    applyUserPreferences(userId, prefs);
  }
}
```

```python
# Python — file read; on error, return empty
def get_user_policy(user_id: str) -> dict:
    try:
        with open(f'/etc/policies/{user_id}.json') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}
    except (OSError, json.JSONDecodeError) as e:
        # Treat read failures the same as missing file — return empty policy
        # Problem: this defaults to PERMISSIVE policy (no restrictions); attack: cause read failure
        logger.warning('policy_read_failed', extra={'user_id': user_id})
        return {}
```

### Why It Fails

The function signature returns `T | None` to mean "the resource was looked up successfully and either was found (T) or not found (None)." The handler flattens *lookup failure* into *not found* — losing the information that the lookup itself didn't complete. Downstream code makes decisions based on the wrong premise.

In the user-preferences case: a user who explicitly set `requireMFA: true` gets the lookup-timeout fall-through to defaults (`requireMFA: false`) — their security setting silently disappears. In the policy case: a user with a restrictive policy file gets the file-read failure treated as "no policy" — i.e., permissive — meaning the security control fails open via the lookup-failure path.

This pattern is subtle because it looks like Rule 5.3 compliance (specific exception type caught) but actually combines with AP-1 fail-open semantics — the caller's downstream decision is fail-open by default-being-applied.

**Source for failure mode:** `OWASP-ASVS V16.5.3`; `CWE-754`; `CWE-755`.

### Canonical Pattern

```typescript
// TypeScript — use a Result/Either type to distinguish outcomes
type LookupResult<T> = 
  | { kind: 'found'; value: T }
  | { kind: 'not-found' }
  | { kind: 'error'; error: Error };

async function findUserPreferences(userId: string): Promise<LookupResult<UserPreferences>> {
  try {
    const prefs = await db.preferences.findOne({ userId, timeout: 1_000 });
    return prefs ? { kind: 'found', value: prefs } : { kind: 'not-found' };
  } catch (e) {
    return { kind: 'error', error: e instanceof Error ? e : new Error(String(e)) };
  }
}

// Caller handles all three outcomes explicitly
async function applyPreferences(userId: string, correlationId: string) {
  const result = await findUserPreferences(userId);
  switch (result.kind) {
    case 'found':
      applyUserPreferences(userId, result.value);
      break;
    case 'not-found':
      applyDefaults(userId);
      break;
    case 'error':
      // Lookup failure — fail-closed: apply the safest policy and surface the error
      logger.error('preferences_lookup_failed', {
        correlationId,
        userId,
        error: result.error.message,
      });
      applyMostRestrictiveDefaults(userId);  // fail-closed default, NOT permissive
      throw new ServiceUnavailableError('Preferences unavailable; safest defaults applied.');
  }
}
```

```python
# Python — explicit Result type via dataclasses
from dataclasses import dataclass
from typing import Generic, TypeVar

T = TypeVar('T')

@dataclass
class Found(Generic[T]):
    value: T

@dataclass
class NotFound:
    pass

@dataclass
class Error:
    cause: Exception

LookupResult = Found[T] | NotFound | Error

def get_user_policy(user_id: str) -> LookupResult[dict]:
    try:
        with open(f'/etc/policies/{user_id}.json') as f:
            return Found(json.load(f))
    except FileNotFoundError:
        return NotFound()
    except (OSError, json.JSONDecodeError) as e:
        return Error(e)

# Caller decides per case
def enforce_policy(user_id: str):
    result = get_user_policy(user_id)
    match result:
        case Found(policy):
            apply_policy(user_id, policy)
        case NotFound():
            apply_default_policy(user_id)
        case Error(e):
            logger.error('policy_lookup_failed', extra={'user_id': user_id, 'error': str(e)})
            apply_most_restrictive_policy(user_id)  # fail-closed
            raise ServiceUnavailableError('Policy lookup failed; restrictive default applied.')
```

### Why It Works

The Result / Either type forces the caller to handle three distinct outcomes explicitly: *found*, *not-found*, and *error*. The error case can no longer be silently flattened into not-found. The downstream decision for the error case is explicit (fail-closed default, log, raise) — not implicit fall-through into permissive behavior.

**Additional considerations:** *Optionals vs Results.* `Optional[T]` / `T | None` is the right type for "the lookup succeeded and the value was or wasn't there"; `Result[T]` / `Either[T, Error]` adds the third "the lookup itself failed" outcome. Use Optionals when failures are out of scope (or propagated as exceptions); use Results when callers need to distinguish failure from absence. *Languages with sum types make this natural.* Rust (`Result<T, E>`), Haskell (`Either e a`), Scala, F#, OCaml. In languages without native sum types, ad-hoc unions (TypeScript discriminated unions) or libraries (`fp-ts`, `returns`, `result.js`) provide the same. *Don't go overboard.* For lookup paths where the caller has no way to recover from lookup failure other than propagating it up, exceptions are simpler and equivalent. The Result type matters when the caller needs to make a *different* decision per outcome.

---

## Summary

| AP | Title | Primary Rule | Severity |
|----|-------|--------------|----------|
| AP-1 | Swallow-and-allow exception in security path | Rule 5.1 | Critical |
| AP-2 | Stack trace / exception detail in user-facing response | Rule 5.2 | High |
| AP-3 | Catch-all empty handler — silent swallow | Rule 5.3 | High |
| AP-4 | Default-permit on external-service failure | Rules 5.1 + 5.4 | Critical |
| AP-5 | No last-resort handler — unhandled exception crashes / leaks | Rule 5.5 | High |
| AP-6 | Generic 200 OK despite partial failure | Rule 5.7 | High |
| AP-7 | Retry loop around security check masks transient failure | Rule 5.1 | Critical |
| AP-8 | No correlation ID — user can't help debug | Rule 5.6 | Medium |
| AP-9 | Catch-specific-then-continue — lookup failure looks like empty result | Rule 5.3 | High |

Severity is the typical range; actual severity depends on the change context. DISAGREEMENT Rule 5.2 routes severity for findings raised here. AP-1, AP-4, and AP-7 are close to hard-refusal territory per `CLAUDE.md` §5 ("bypassing authorization for convenience").
