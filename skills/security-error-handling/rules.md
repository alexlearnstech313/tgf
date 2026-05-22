# SECURITY-ERROR-HANDLING — Rules

Seven rules grounding the discipline of failing well. The first three are foundational (fail-closed, generic-user-errors, designed-not-improvised); the rest add operational depth (external dependencies, last-resort handler, correlation IDs, partial failures).

This skill maps directly to **OWASP Top 10:2025 A10 (Mishandling of Exceptional Conditions)** — a new category in the 2025 list — and to **OWASP ASVS 5.0 V16.5 (Error Handling)**.

Per Phase 6 Checkpoint 1 Decision A: chapter-level citations live in `SKILL.md §2 Authoritative Sources`; sub-rule citations (V16.5.1–V16.5.4) appear here.

---

## Rule 5.1: Security Checks Fail Closed

**Statement:** When a security check (authentication, authorization, validation, signature verification, integrity check, audit log emit, dependency lookup whose result feeds a security decision) cannot definitively succeed, the result is deny / reject / error. An exception thrown during the check is not "the check didn't run cleanly, let them through" — it is "the check did not succeed, deny." A timeout during the check is not "the check is taking a while, assume success" — it is "the check did not succeed, deny." A network failure reaching the identity provider is not "the IdP is having a bad day, let through with cached state" — it is "we cannot verify, deny." Missing data, ambiguous results, partial information, and "we'll figure it out later" are never grounds for permitting the operation.

**Citation:** `OWASP-ASVS V16.5.3` (the application fails gracefully and securely, including when an exception occurs, preventing fail-open conditions) + `OWASP-TOP10 A10:2025` (Mishandling of Exceptional Conditions — new category in 2025) + cross-reference `SECURITY-CORE Rule 5.2` (default-deny authorization is the authorization-specific application of fail-closed; this rule is the universal pattern across all security checks).

**Plain-language impact:** Fail-open is the failure mode that compromises the security model itself. An authorization check that returns *true* on exception means an attacker can sometimes bypass authorization by triggering an exception (slow network, corrupted token, edge-case input). A signature verifier that returns *true* on parse failure means an unsigned request is treated as signed. A validation check that returns *valid* on schema-library error means malformed input is treated as valid. Every one of these is a real, exploited pattern. The discipline is universal across security gates: the answer when uncertain is always *not granted*.

**Extended discussion:** Fail-closed has a usability cost — sometimes legitimate users hit transient failures and get rejected. The discipline accepts this cost. The cost of fail-open is breach; the cost of fail-closed is occasional friction. The friction is managed via: (a) high-availability infrastructure for security-critical dependencies (the auth provider, the secret store) so transient failures are rare; (b) correlation IDs (Rule 5.6) so when a legitimate user hits the friction, engineering can investigate quickly; (c) the user is told something failed and to try again or contact support — never auto-promoted to success. The Top 10:2025 elevation of A10 reflects the industry's recognition that fail-open patterns have been recurring across breaches.

**Related anti-patterns:** AP-1 (swallow-and-allow exception handler in security path); AP-4 (default-permit on external-service failure); AP-7 (retry loop around security check masks transient failure).

---

## Rule 5.2: Generic User-Facing Errors; Detailed Server-Side Logs

**Statement:** Errors returned to the user contain a stable, generic message ("Something went wrong. Please try again or contact support with reference ID X.") and an opaque correlation ID. They do NOT contain: stack traces, exception class names, exception messages, internal paths, framework versions, library versions, SQL error fragments, file structure hints, configuration values, hostnames, IP addresses, environment-variable contents, or any reflection of internal state. The full exception details — class, message, stack trace, request context (sanitized of secrets), correlation ID, timing — are logged server-side and keyed by the correlation ID for incident-response investigation. For HTTP APIs, the response format is RFC 7807 Problem Details (`application/problem+json`) with a generic `title`, an HTTP-status-appropriate `status`, and the correlation ID embedded as `instance` or a custom extension.

**Citation:** `OWASP-ASVS V16.5.1` (generic message returned to consumer when unexpected or security-sensitive error occurs, ensuring no exposure of sensitive internal system data) + `OWASP-CHEAT-EH` (centralized handler, generic responses, RFC 7807 Problem Details, no implementation details) + `RFC-7807` (Problem Details for HTTP APIs) + `CWE-209` (Information Exposure Through an Error Message).

**Plain-language impact:** Detailed error responses are the first stage of attacker reconnaissance. A stack trace reveals the framework, library versions, and code structure — directly feeding into known-vulnerability lookups. A SQL error reveals the database engine and often the query shape — feeding into injection-attack refinement. A path disclosure reveals filesystem layout — feeding into LFI/RFI and SSRF. A class name reveals serialization format. Each disclosure narrows the attacker's search space. The OWASP Cheat Sheet's explicit guidance: "Unhandled errors can assist an attacker in this initial phase" of reconnaissance.

**Extended discussion:** *RFC 7807 specifically.* Defines a JSON structure (`type`, `title`, `status`, `detail`, `instance`) for API error responses. Frameworks have growing native support: Spring `ProblemDetail` (Spring 6+), .NET `ProblemDetails` (ASP.NET Core), FastAPI's RFC-7807-compatible exception handlers. *Development vs production.* Developers often want stack traces to debug — that's legitimate during development. The discipline is environment-aware error responses: detailed in non-production, generic in production, *never* shipped to a user. *Correlation ID surfacing.* The ID goes in both the response body (for API consumers) and a response header (`X-Correlation-Id` or `traceparent` per W3C Trace Context) for HTTP clients to log. *HTML error pages.* For HTML responses (web app), the equivalent is a static error page with the correlation ID embedded — no framework-default debug page in production.

**Related anti-patterns:** AP-2 (stack trace / exception detail in user-facing error response — both API JSON and HTML 500 page forms).

---

## Rule 5.3: Exceptional Conditions Are Designed, Not Improvised

**Statement:** Every code path that can fail has a deliberate failure mode chosen at design time. Exception handlers are *deciders*, not error-suppressors — their job is to log the exception, choose a policy (retry / fail-closed / fall back / propagate up), and ensure the system is in a consistent, known-safe state on exit. The forbidden patterns: `catch (e) {}` (silent swallow), `catch (e) { return true; }` (default-permit on error), `catch (e) { return null; }` in code where the caller cannot distinguish missing from failed, `try: ... except: pass` (Python silent swallow), `rescue => nil` (Ruby silent swallow), and any catch-all where the action taken on failure is "assume success or use a default."

**Citation:** `OWASP-ASVS V16.5.3` (graceful and secure failure, preventing fail-open) + `CWE-754` (Improper Check for Unusual or Exceptional Conditions) + `CWE-755` (Improper Handling of Exceptional Conditions) + `OWASP-TOP10 A10:2025`.

**Plain-language impact:** Empty catches are deferred bugs — the error happens, the handler swallows it, the system continues in an inconsistent state until the inconsistency surfaces somewhere distant (a stale cache, a missing record, a security check that was supposed to run and didn't). The trail back is gone because the exception that would have shown the cause was silenced at catch-time. AP-1 (swallow-and-allow in security path) is the security-critical version; AP-3 (empty catch) is the broader category that creates downstream-corruption bugs.

**Extended discussion:** *Catch specific, not catch-all.* The strongest discipline is catching only the exception types you expect and have a designed response for. `catch (NetworkException e)` lets the network-failure handler exist; `catch (Exception e)` swallows everything including programming errors. *Re-raise after logging.* When the handler's job is to log and then propagate, the canonical pattern is `catch + log + re-raise` rather than `catch + log + swallow`. *Finally and resource cleanup.* `finally` blocks (or `with` statements in Python, RAII in Rust/C++) ensure cleanup runs regardless of exception flow — without leaking resources or leaving inconsistent state. *Async exceptions.* Promise / Future / async-await exceptions are easy to drop silently if the awaiting code doesn't await or `.catch()`. The discipline is the same: every async branch has a designed failure mode.

**Related anti-patterns:** AP-3 (catch-all empty handler — silent swallow); AP-9 (catch-specific-then-continue — lookup failure looks like empty result).

---

## Rule 5.4: External Dependencies — Circuit Breakers, Timeouts, Secure Graceful Degradation

**Statement:** External calls — to databases, identity providers, secret stores, message queues, cache servers, APIs, file storage, and any service the application doesn't own — have **timeouts** on every call (connect timeout + read timeout). Repeated failures trigger a **circuit breaker** (open the circuit after N consecutive failures, halt cascading retries, return fail-closed errors during the open state, half-open after a cool-down window). **Graceful degradation** is permitted for *non-security read paths*: cached profile data when the user-profile service is unreachable, last-known-good UI state when the recommendations API is down, queued writes when the persistence layer is slow. Graceful degradation is **forbidden for security checks** — auth provider unreachable means requests are rejected, not auto-approved; secret store unreachable means crypto operations fail closed, not fall back to a hardcoded default; CAPTCHA service unreachable means the protected endpoint is rejected, not opened up.

**Citation:** `OWASP-ASVS V16.5.2` (application continues to operate securely when external resource access fails, for example by using patterns such as circuit breakers or graceful degradation) + `OWASP-TOP10 A10:2025`.

**Plain-language impact:** External dependencies are the application's least controllable surface — their failures will cascade if not contained. A database connection that hangs without timeout ties up application threads until the pool is exhausted, killing the application even though the database is the actual problem. A retry storm against a failing service guarantees the service stays failed. The circuit-breaker pattern (Hystrix popularized it; modern equivalents in Resilience4j, Polly, opossum, hystrix-go) trades immediate failure for system stability. *Graceful degradation must not degrade security* — the line is the most-violated principle in this rule. "The auth provider is having issues, so let users through this once" is the breach waiting to happen.

**Extended discussion:** *Timeout discipline.* Every external call has a timeout chosen for the call's nature (a quick health-check might be 1s; a long-running batch query might be 30s). Default timeouts at the platform level (HTTP client default = 30s often) are typically too long; explicit timeouts per call site. *Bulkheads.* Beyond circuit breakers, the bulkhead pattern isolates resource pools so a slow downstream doesn't exhaust the application's connection pool. *Idempotency.* For retried operations (per the calling code, not for security checks), idempotency keys ensure retry safety. *Connection pool sizing.* External-dependency failures often manifest as connection pool exhaustion; sizing and monitoring the pool is part of the resilience discipline. Cross-reference `ops-observability` (Phase 9) for monitoring; this skill covers the application-level resilience patterns.

**Related anti-patterns:** AP-4 (default-permit on external-service failure — fails open).

---

## Rule 5.5: Last-Resort Error Handler — Catch the Uncaught

**Statement:** A framework-level global error handler catches every exception that escapes individual route handlers, service methods, or async tasks. The last-resort handler: (a) returns a generic error response to the client (Rule 5.2 generic message + correlation ID); (b) logs the full exception with stack trace, request context, and correlation ID; (c) emits a security event entry for unexpected exceptions per ASVS V16.3.4; (d) ensures the process doesn't crash (where appropriate — long-running servers should not exit on a single request's unhandled exception). Per framework: Express error middleware (`app.use((err, req, res, next) => ...)` at the bottom of the middleware stack); Spring `@ControllerAdvice` + `@ExceptionHandler`; FastAPI `exception_handler` decorator + ASGI exception_middleware; ASP.NET Core `UseExceptionHandler` middleware; Go panic-recover middleware (`defer func() { if r := recover(); r != nil { ... } }`); Python `sys.excepthook` for non-server code paths; Java `Thread.setDefaultUncaughtExceptionHandler` for background-thread exceptions.

**Citation:** `OWASP-ASVS V16.5.4` ("last resort" error handler defined to catch all unhandled exceptions, avoid losing error details, and prevent the entire application process from going down).

**Plain-language impact:** Without a last-resort handler, an unhandled exception goes wherever the framework's default behavior takes it — typically a debug-mode stack-trace page in development (which sometimes ships to production by accident), a generic 500 with minimal logging, or process termination. The result is some combination of: information disclosure (stack trace to user), missed incident detection (no log entry, no alert), and service unavailability (process crashed). The last-resort handler gives the application one guaranteed funnel for all error paths — every unhandled exception flows through the handler and gets the discipline of Rules 5.2 + 5.6 + security-event logging.

**Extended discussion:** *Order of handlers.* The last-resort handler is the *last* registered handler in the chain. More-specific handlers run first; the last-resort catches what they didn't. *Async vs sync.* Async-unhandled exceptions need their own catch — Node's `process.on('unhandledRejection')` and `process.on('uncaughtException')`, Python's `asyncio` task exceptions, Go goroutine panics — frameworks differ, but each environment has the equivalent. *Don't suppress, decide.* The last-resort handler should not swallow the error silently (that would be Rule 5.3 violation) — it should log thoroughly, surface generic-message-and-ID to user, optionally emit a security event, and re-raise where appropriate for the runtime's higher-level handlers (e.g., for process-level monitoring). *Process behavior.* For long-running servers, the unhandled exception is logged and the request is failed; the process continues. For one-shot tasks (CLI tools, background jobs), the handler logs and exits with a non-zero code so orchestration systems detect the failure.

**Related anti-patterns:** AP-5 (no last-resort handler — unhandled exception crashes / leaks stack trace).

---

## Rule 5.6: Correlation IDs Link User-Facing Errors to Server Logs

**Statement:** Every request gets a correlation ID (UUID v4) generated at request entry — by reverse proxy / load balancer / API gateway if available (preferred — propagated via `X-Request-Id` or `X-Correlation-Id` header), otherwise generated by the application's first middleware. The ID is: (a) attached to every log entry emitted during the request (structured-log field); (b) propagated to downstream service calls via header (Service A → Service B passes the ID; Service B's logs are searchable by the same ID); (c) included in every error response surfaced to the user (in the response body for APIs, on the error page for web apps); (d) emitted to distributed tracing systems (OpenTelemetry trace ID can serve as or include the correlation ID — W3C Trace Context `traceparent` header is the standard format). Incident-response procedure: user reports error → asks for the correlation ID → engineer searches logs / traces for the ID → full request context surfaces immediately.

**Citation:** `OWASP-ASVS V16.2.1` (each log entry includes necessary metadata such as when, where, who, what to allow detailed timeline investigation) + `OWASP-CHEAT-EH` (correlation IDs implicit in the centralized-handler-and-generic-response pattern; W3C Trace Context).

**Plain-language impact:** Without correlation IDs, debugging means asking the user "what time, exactly, did this happen?" and "what were you doing?" — imprecise data that ages quickly. The user reports "I got an error at around 3pm yesterday trying to save my settings" and the engineer searches through thousands of log entries in the relevant time window guessing which one matches. With correlation IDs, the user reports "I got reference ID b3a8f9c2-..." and the engineer types one search; the full request context, the exception, the downstream service calls, the timing, the user's session state — all surface in a single result.

**Extended discussion:** *Choosing the ID format.* UUID v4 is the most common; W3C Trace Context's `traceparent` header (`00-<trace-id-32>-<span-id-16>-<flags-2>`) is the modern observability standard and supports the same use case. *Propagation discipline.* Downstream calls must pass the header through; instrumentation libraries (OpenTelemetry SDK in every major language) automate this. Without propagation, the ID is useful only within the single service that generated it. *Privacy.* The correlation ID is *not* a user identifier; it's per-request. Linking IDs to users for analytics is fine; emitting a user identifier as the correlation ID is a privacy issue (the ID surfaces in error responses, in URLs, etc.) — keep them separate. *Cross-reference forward.* `security-logging` (Phase 6 commit 10/12) and `ops-observability` (Phase 9) carry the deeper logging-and-tracing discipline that this rule's correlation ID feeds into.

**Related anti-patterns:** AP-8 (no correlation ID — user can't help debug).

---

## Rule 5.7: Partial Failures Are Not Successes

**Statement:** A multi-step operation either (a) completes all steps successfully and returns success, (b) rolls back any partial work and returns failure, or (c) invokes designed compensating actions (saga pattern) when rollback is impossible and returns *partial-success-with-explicit-status* — never plain success. For database transactions, the canonical pattern is `BEGIN; ... ; COMMIT` with rollback on any exception. For operations against systems that don't support transactions (sending an email, calling a payment API, publishing to a queue), compensating actions are designed in advance: if step 3 of 5 fails, steps 1 and 2 are explicitly undone or marked-for-cleanup. The forbidden patterns: "the database write worked, the email send failed, return success anyway because the user mostly got what they wanted"; "the user was created but the welcome email failed, the user doesn't need to know, return 201 Created"; "the payment captured but the order record failed to save, manually clean up the orphan capture later."

**Citation:** `OWASP-ASVS V16.5.3` (fail gracefully and securely, prevent fail-open conditions) + `CWE-755` (Improper Handling of Exceptional Conditions) + `OWASP-TOP10 A10:2025`.

**Plain-language impact:** Partial-success-as-success is a category of silent inconsistency. The user thinks the operation completed; some steps actually didn't run; the gap between expected state and actual state grows. The bugs surface days later when downstream reports/queries/integrations are wrong — and the trail back to "the third step failed and the success response masked it" is gone. Security implications: a partial-failure pattern that completes a privilege grant (step 1) but fails to write the audit log (step 2) and returns success looks like a clean operation but leaves the privilege change un-audited. The next-step incident-response cannot reconstruct who got which privilege when.

**Extended discussion:** *Transactional discipline.* Where databases support transactions, the boundary of the transaction matches the boundary of the operation's all-or-nothing semantics. Multi-database or multi-service operations require explicit transaction coordination (distributed transactions, sagas, two-phase commit) — each has tradeoffs, but the principle is the same: all-or-nothing, never silently-partial. *Saga pattern.* Sequence of local transactions with compensating actions; when step N fails, compensating actions for steps 1 through N-1 fire in reverse order. Used in microservices architectures where distributed transactions are impractical. *Idempotency keys.* For retry safety in distributed flows, an idempotency key per operation lets retries safely re-execute without double-processing — critical for payment flows. *Explicit partial-status responses.* When partial success is genuinely the right semantics (a batch operation where some items succeed and some fail), the response explicitly communicates which items succeeded and which didn't — HTTP 207 Multi-Status, or a structured response with per-item status. Never plain 200 OK masking partial failure.

**Related anti-patterns:** AP-6 (generic 200 OK despite partial failure).

---

## Summary

| Rule | Citation | Primary AP |
|------|----------|------------|
| 5.1 Security checks fail closed | ASVS V16.5.3 + A10:2025 + cross-ref SECURITY-CORE Rule 5.2 | AP-1, AP-4, AP-7 |
| 5.2 Generic user errors; detailed logs | ASVS V16.5.1 + Cheat Sheet + RFC 7807 + CWE-209 | AP-2 |
| 5.3 Exceptional conditions designed | ASVS V16.5.3 + CWE-754, CWE-755 + A10:2025 | AP-3, AP-9 |
| 5.4 External deps — circuit breakers + secure degradation | ASVS V16.5.2 + A10:2025 | AP-4 |
| 5.5 Last-resort handler | ASVS V16.5.4 | AP-5 |
| 5.6 Correlation IDs | ASVS V16.2.1 + Cheat Sheet | AP-8 |
| 5.7 Partial failures not successes | ASVS V16.5.3 + CWE-755 + A10:2025 | AP-6 |

For full anti-pattern + canonical-pattern detail with code examples, see `anti-patterns.md`.
