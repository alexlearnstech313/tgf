---
# ─── Anthropic-native runtime fields (Claude Code honors these) ───
name: security-error-handling
description: |
  Error handling discipline — security checks fail closed; user-facing
  errors stay generic; exceptional conditions are designed, not
  improvised. Use when implementing security checks (auth, authorization,
  validation), wrapping external calls, structuring exception handlers,
  designing error responses, or adding correlation IDs. Aligns with OWASP
  ASVS 5.0 V16.5 and the new OWASP Top 10:2025 A10 (Mishandling of
  Exceptional Conditions). Pairs with security-logging.
paths:
  - "**/*.ts"
  - "**/*.tsx"
  - "**/*.js"
  - "**/*.jsx"
  - "**/*.py"
  - "**/*.go"
  - "**/*.rs"
  - "**/*.rb"
  - "**/*.java"
  - "**/*.kt"
  - "**/*.swift"
  - "**/*.php"
  - "**/*.cs"
  - "**/*.scala"

# ─── TGF-extension metadata (Phase 11 meta-skills read these; Claude Code ignores) ───
applies-when:
  paths-include:
    - "**/*.{ts,tsx,js,jsx,py,go,rs,rb,java,kt,swift,php,cs,scala}"
  operations-include:
    - try/catch/finally / except / rescue blocks
    - security check return paths (auth, authorization, validation, signature, integrity)
    - external service calls (HTTP, DB, queue, identity provider, secret store)
    - error response construction (API responses, HTML error pages)
    - global exception handlers (Express middleware, Spring ControllerAdvice, FastAPI exception_handler, sys.excepthook, Go panic-recover)
    - multi-step transactional operations
  data-flows-include:
    - exception propagation across trust boundaries
    - error content reaching user-facing response
    - partial-failure state in multi-step operations
disqualifying-when:
  - documentation-only changes
  - test fixture additions without production code changes
  - dependency version bumps without code changes
  - pure formatting edits
sources:
  - OWASP ASVS 5.0.0 V16.5 (Error Handling) (verified 2026-05-22)
  - OWASP Top 10:2025 A10 (Mishandling of Exceptional Conditions — new category in 2025) (verified 2026-05-22)
  - OWASP Top 10:2025 A09 (Security Logging and Alerting Failures — cross-reference) (verified Phase 4, 2026-05-20)
  - OWASP Cheat Sheet — Error Handling (verified 2026-05-22)
  - RFC 7807 (Problem Details for HTTP APIs) (verified 2026-05-22)
  - CWE-209 (Information Exposure Through an Error Message)
  - CWE-754 (Improper Check for Unusual or Exceptional Conditions)
  - CWE-755 (Improper Handling of Exceptional Conditions)
  - CWE-388 (Error Handling — pillar)
last-generated: 2026-05-22
refresh-recommended: 2027-05-22
self-evolution:
  anti-patterns-observed: []
  triggers-refined: []
  ai-failures-documented: []
---

# SECURITY-ERROR-HANDLING

> **Skill body ≤300 lines** (per `DEC-2026-05-19-007`). Principles, rule summaries, and navigation live here. Full content in reference files loaded on demand:
> - `rules.md` — full rules with rule-level citations
> - `anti-patterns.md` — full anti-pattern + canonical pattern pairs with code examples

<!-- SECTION: overview -->
## §1 Overview

SECURITY-ERROR-HANDLING governs the discipline of failing well: security checks fail closed; user-facing errors stay generic; exceptional conditions are designed deliberately; external-dependency failures don't degrade security; partial failures are not silently treated as successes. It maps directly to OWASP ASVS 5.0 V16.5 (Error Handling) and to **OWASP Top 10:2025 A10 — Mishandling of Exceptional Conditions**, a new category in the 2025 list.

This is one of the rare Phase 6 skills that does *not* directly extend a single SECURITY-CORE rule — it sets a *fail-closed* pattern that becomes a foundation for the later cryptography, secrets-management, and IAM skills. Where SECURITY-CORE Rule 5.2 (Authorize Every Action, Default Deny) is universal *for authorization*, this skill's Rule 5.1 (Security Checks Fail Closed) is the same discipline applied universally — to validation, signature verification, integrity checks, dependency lookups for security purposes, and any code path that gates access on a check's success.

The skill pairs with `security-logging` (Phase 6 commit 10/12). This skill says *fail closed and log*; `security-logging` says *what to log, in what format, with what protection*. The boundary: this skill owns *when and why* errors happen and how they're surfaced to users; `security-logging` owns the discipline of the log itself.
<!-- /SECTION: overview -->

<!-- SECTION: sources -->
## §2 Authoritative Sources

| Source ID | Reference | Version | Date Verified |
|-----------|-----------|---------|---------------|
| OWASP-ASVS-V16 | [OWASP ASVS 5.0 V16 — Security Logging and Error Handling](https://github.com/OWASP/ASVS/blob/master/5.0/en/0x25-V16-Security-Logging-and-Error-Handling.md) | 5.0.0 (released 2025-05-30) | 2026-05-22 |
| OWASP-TOP10-A10 | [OWASP Top 10:2025 A10 (Mishandling of Exceptional Conditions)](https://owasp.org/Top10/2025/) | 2025 | 2026-05-22 |
| OWASP-TOP10-A09 | [OWASP Top 10:2025 A09 (Security Logging and Alerting Failures)](https://owasp.org/Top10/2025/) | 2025 | 2026-05-20 (Phase 4) |
| OWASP-CHEAT-EH | [OWASP Cheat Sheet — Error Handling](https://cheatsheetseries.owasp.org/cheatsheets/Error_Handling_Cheat_Sheet.html) | Current (2026) | 2026-05-22 |
| RFC-7807 | [RFC 7807 — Problem Details for HTTP APIs](https://datatracker.ietf.org/doc/html/rfc7807) | 2016 (current; RFC 9457 obsoletes for some uses) | 2026-05-22 |
| CWE-209 | [CWE-209 Information Exposure Through Error Message](https://cwe.mitre.org/data/definitions/209.html) | Current | 2026-05-22 |
| CWE-754 | [CWE-754 Improper Check for Unusual or Exceptional Conditions](https://cwe.mitre.org/data/definitions/754.html) | Current | 2026-05-22 |
| CWE-755 | [CWE-755 Improper Handling of Exceptional Conditions](https://cwe.mitre.org/data/definitions/755.html) | Current | 2026-05-22 |
| CWE-388 | [CWE-388 Error Handling (pillar)](https://cwe.mitre.org/data/definitions/388.html) | Current | 2026-05-22 |

Citation granularity per Phase 6 Checkpoint 1 Decision A (hybrid): chapters at chapter level in §2; sub-rule level (V16.5.1, V16.5.2, V16.5.3, V16.5.4) in `rules.md`. OWASP Top 10:2025 at category level. OWASP Cheat Sheet content informs operational guidance and is cited by section title. RFC 7807 at the format level. CWE entries by ID + title.

V16.1–V16.4 sub-rules (logging-specific) are scoped to `security-logging` (Phase 6 commit 10/12), not here.
<!-- /SECTION: sources -->

<!-- SECTION: discovery -->
## §3 Discovery Commands

Copy-pasteable commands to capture error-handling state before applying rules.

```bash
# Find catch-all empty exception handlers (swallow-and-continue)
grep -rnE "catch\s*\([^)]*\)\s*\{\s*\}|except[^:]*:\s*pass|rescue.*=>.*nil" --include="*.ts" --include="*.js" --include="*.py" --include="*.rb" 2>/dev/null | head -20

# Find swallow-and-default-permit patterns in security paths
grep -rnE "catch.*\{.*return\s+(true|user|null|\{\})" --include="*.ts" --include="*.js" 2>/dev/null | head -20
grep -rnE "except.*:.*return\s+(True|user|None)" --include="*.py" 2>/dev/null | head -20

# Find stack-trace exposure in error responses
grep -rnE "res\.(json|send|status).*\.stack|str\(e\)|traceback|exception.*toString" --include="*.ts" --include="*.js" --include="*.py" 2>/dev/null | head -20

# Find global error handlers (good — verify they exist; flag if missing)
grep -rnE "app\.use\(.*err|@app\.errorhandler|@ControllerAdvice|sys\.excepthook|panic-recover" --include="*.ts" --include="*.js" --include="*.py" --include="*.java" --include="*.go" 2>/dev/null | head -20

# Find retry loops around security checks (suspect — security shouldn't retry)
grep -rnE "(retry|attempts?).*(auth|verify|sign|validate)" --include="*.ts" --include="*.js" --include="*.py" 2>/dev/null | head -20

# Find external-call patterns without timeouts (suspect for V16.5.2)
grep -rnE "fetch\(['\"]https|requests\.(get|post)\(['\"]http|axios\.(get|post)" --include="*.ts" --include="*.js" --include="*.py" 2>/dev/null | head -20
```
<!-- /SECTION: discovery -->

<!-- SECTION: principles -->
## §4 Universal Principles

Seven principles grounding the error-handling discipline. The first three are foundational; the rest add operational depth.

- **Security checks fail closed.** When a security check (auth, authorization, validation, signature verification, integrity check, dependency lookup for security purposes) cannot definitively succeed, the answer is deny. Exception during the check → deny. Timeout during the check → deny. Network failure during the check → deny. Missing data → deny. "We're not sure" is always *not granted*. Fail-open is the failure mode that compromises the security model; A10:2025 is the OWASP category that recognizes it as a top-10 risk.

- **User-facing errors are different from logged errors.** The user sees a stable, generic message and a correlation ID. The server logs the full exception, stack trace, request context, and correlation ID for incident-response. The two are linked by the correlation ID, not by sharing content. RFC 7807 Problem Details is the standard format for API error responses; the OWASP Cheat Sheet recommends centralized handler + generic responses + correlation IDs as the canonical pattern.

- **Exceptional conditions are designed, not improvised.** Every code path that can fail has a deliberate failure mode chosen at design time — not an after-thought `try/catch` that swallows. Exception handlers are *deciders*, not error-suppressors: log, choose policy (retry / fail-closed / fall back / propagate), ensure consistent state on exit. `catch (e) {}` and `catch (e) { return true; }` are the patterns A10:2025 flags as systemic risk.

- **External dependencies will fail; the application stays secure when they do.** Database, identity provider, cache, secret store, API, queue — all can be unreachable, slow, returning errors, or returning wrong data. Circuit breakers limit cascading failure (per ASVS V16.5.2). Timeouts on every external call prevent indefinite hangs. Graceful degradation maintains service for *non-security* read paths (cached profile data, last-known-good UI state); it does *not* degrade security checks (auth provider down → reject, never auto-approve).

- **Catch unhandled exceptions at the last possible boundary.** Every framework has a global error handler — Express error middleware, Spring `@ControllerAdvice`, FastAPI `exception_handler`, ASGI exception handler, Go panic-recover middleware, Java's `Thread.setDefaultUncaughtExceptionHandler`, Python's `sys.excepthook`. The last-resort handler catches what individual handlers missed and ensures: (a) a generic response goes to the user, (b) the full exception is logged with correlation ID, (c) the process doesn't lose the error to stderr-into-the-void (per V16.5.4).

- **Correlation IDs link user-facing errors to server logs.** Every error response surfaces an opaque correlation ID (UUID v4 generated at request entry, propagated through downstream calls and logs). The user reports the ID; engineering finds the matching log entry by ID. Without correlation IDs, debugging means asking the user for their exact actions and reverse-engineering from imprecise descriptions. With correlation IDs, the engineer types one search.

- **Partial failures are not successes.** Multi-step operations either complete fully or roll back to a known-safe state. If full rollback isn't possible (operations against external systems that don't support transactions), compensating actions are designed (saga pattern); the user is told the operation didn't fully succeed; the partial state is logged for follow-up. The "if I got here, must be success" pattern in code that ran past a partial failure is the silent bug class A10:2025 explicitly targets.
<!-- /SECTION: principles -->

<!-- SECTION: rules -->
## §5 Rule Summaries

Seven rules. Each summary: title + 1-line statement + source identifier.

<!-- RULE: 5.1 -->
- **Rule 5.1: Security Checks Fail Closed** — When a security check cannot definitively succeed, return deny / reject / error. Exceptions, timeouts, network failures, missing data, and ambiguous results are never grounds for permitting. `OWASP-ASVS V16.5.3` + `OWASP-TOP10 A10:2025` + cross-ref `SECURITY-CORE Rule 5.2` → [`rules.md#rule-51-security-checks-fail-closed`](rules.md)
<!-- /RULE: 5.1 -->
<!-- RULE: 5.2 -->
- **Rule 5.2: Generic User-Facing Errors; Detailed Server-Side Logs** — Users see a stable generic message + correlation ID. Stack traces, internal paths, framework versions, and exception messages stay server-side. RFC 7807 Problem Details for API responses. `OWASP-ASVS V16.5.1` + `OWASP-CHEAT-EH` + `RFC-7807` + `CWE-209` → [`rules.md#rule-52-generic-user-errors-detailed-server-logs`](rules.md)
<!-- /RULE: 5.2 -->
<!-- RULE: 5.3 -->
- **Rule 5.3: Exceptional Conditions Are Designed, Not Improvised** — Every code path that can fail has a deliberate failure mode chosen at design time. `catch` handlers are deciders, not error-suppressors. Swallow-and-continue is forbidden in security-relevant code. `OWASP-ASVS V16.5.3` + `CWE-754` + `CWE-755` + `OWASP-TOP10 A10:2025` → [`rules.md#rule-53-exceptional-conditions-designed`](rules.md)
<!-- /RULE: 5.3 -->
<!-- RULE: 5.4 -->
- **Rule 5.4: External Dependencies — Circuit Breakers, Timeouts, Secure Graceful Degradation** — External calls have timeouts; repeated failures open the circuit; graceful degradation is allowed for non-security data only — never for security checks. `OWASP-ASVS V16.5.2` + `OWASP-TOP10 A10:2025` → [`rules.md#rule-54-external-dependencies-circuit-breakers`](rules.md)
<!-- /RULE: 5.4 -->
<!-- RULE: 5.5 -->
- **Rule 5.5: Last-Resort Error Handler — Catch the Uncaught** — Framework-level global error handler catches what per-route handlers miss; returns generic response, logs full exception with correlation ID, emits security event for unexpected exceptions. `OWASP-ASVS V16.5.4` → [`rules.md#rule-55-last-resort-handler`](rules.md)
<!-- /RULE: 5.5 -->
<!-- RULE: 5.6 -->
- **Rule 5.6: Correlation IDs Link User-Facing Errors to Server Logs** — UUID v4 per request, propagated through downstream calls and logs. User sees ID in error response; engineer searches log for matching ID. `OWASP-ASVS V16.2.1` (necessary metadata for investigation) + `OWASP-CHEAT-EH` → [`rules.md#rule-56-correlation-ids`](rules.md)
<!-- /RULE: 5.6 -->
<!-- RULE: 5.7 -->
- **Rule 5.7: Partial Failures Are Not Successes** — Multi-step operations complete fully, roll back, or invoke compensating actions (saga pattern). The "ran past the failure" success path is forbidden. `OWASP-ASVS V16.5.3` + `CWE-755` + `OWASP-TOP10 A10:2025` → [`rules.md#rule-57-partial-failures-not-successes`](rules.md)
<!-- /RULE: 5.7 -->

See `rules.md` for full rule text, citations, plain-language impact, and extended discussion.
<!-- /SECTION: rules -->

<!-- SECTION: anti-patterns -->
## §6 Anti-Pattern Summaries

Nine anti-pattern pairs covering the most common error-handling failures.

<!-- ANTI-PATTERN: AP-1 -->
- **AP-1: Swallow-and-Allow Exception Handler in Security Path** — `catch (e) { return true; }` defaults to permit on exception. The security model fails open. Violates Rule 5.1. → [`anti-patterns.md#ap-1-swallow-and-allow`](anti-patterns.md)
<!-- /ANTI-PATTERN: AP-1 -->
<!-- ANTI-PATTERN: AP-2 -->
- **AP-2: Stack Trace / Exception Detail in User-Facing Error Response** — Raw exception, stack trace, or internal-path information reaches the user. Violates Rule 5.2; CWE-209. → [`anti-patterns.md#ap-2-stack-trace-exposure`](anti-patterns.md)
<!-- /ANTI-PATTERN: AP-2 -->
<!-- ANTI-PATTERN: AP-3 -->
- **AP-3: Catch-All Empty Handler — Silent Swallow** — `catch (e) {}` / `except: pass` / `rescue` without handling — error vanishes, downstream code proceeds. Violates Rule 5.3. → [`anti-patterns.md#ap-3-empty-catch`](anti-patterns.md)
<!-- /ANTI-PATTERN: AP-3 -->
<!-- ANTI-PATTERN: AP-4 -->
- **AP-4: Default-Permit on External-Service Failure** — Auth provider unreachable → "user is probably fine, let them through." Fails open on infrastructure failure. Violates Rules 5.1 + 5.4. → [`anti-patterns.md#ap-4-default-permit-on-failure`](anti-patterns.md)
<!-- /ANTI-PATTERN: AP-4 -->
<!-- ANTI-PATTERN: AP-5 -->
- **AP-5: No Last-Resort Handler — Unhandled Exception Crashes / Leaks** — Process throws uncaught exception mid-request, framework default stack-trace page leaks. Violates Rule 5.5. → [`anti-patterns.md#ap-5-no-last-resort-handler`](anti-patterns.md)
<!-- /ANTI-PATTERN: AP-5 -->
<!-- ANTI-PATTERN: AP-6 -->
- **AP-6: Generic 200 OK Despite Partial Failure** — Multi-step operation; some steps fail; returns 200 OK as if everything worked. Caller assumes success. Violates Rule 5.7. → [`anti-patterns.md#ap-6-partial-failure-as-success`](anti-patterns.md)
<!-- /ANTI-PATTERN: AP-6 -->
<!-- ANTI-PATTERN: AP-7 -->
- **AP-7: Retry Loop Around Security Check Masks Transient Failure** — `for attempt in range(5): if verify_signature(): break` — repeated retries on a security check that should fail closed on any transient failure. Violates Rule 5.1. → [`anti-patterns.md#ap-7-retry-loop-on-security-check`](anti-patterns.md)
<!-- /ANTI-PATTERN: AP-7 -->
<!-- ANTI-PATTERN: AP-8 -->
- **AP-8: No Correlation ID — User Can't Help Debug** — User-facing error gives no actionable info; logs can't be correlated to user reports. Violates Rule 5.6. → [`anti-patterns.md#ap-8-no-correlation-id`](anti-patterns.md)
<!-- /ANTI-PATTERN: AP-8 -->
<!-- ANTI-PATTERN: AP-9 -->
- **AP-9: Catch-Specific-Then-Continue — Lookup Failure Looks Like Empty Result** — `catch (DatabaseTimeoutException e) { return null; }` — caller can't distinguish "no data" from "lookup failed." Downstream code makes wrong decisions. Violates Rule 5.3. → [`anti-patterns.md#ap-9-catch-then-null`](anti-patterns.md)
<!-- /ANTI-PATTERN: AP-9 -->

Per `DEC-2026-05-17-003` Clause 1: every anti-pattern is paired with a canonical pattern in `anti-patterns.md`.
<!-- /SECTION: anti-patterns -->

<!-- SECTION: ai-concerns -->
## §7 AI-Specific Concerns

Error-handling failure modes specific to AI-generated code and AI-integrated systems.

- **`catch (e) { return true; }` as the path of least resistance.** AI generates security check wrappers with permissive fallbacks because the happy-path prompt didn't mention failure semantics. The completion that fails open is "shorter and works" against happy-path tests. Defense: Rule 5.1 + AP-1 — grep at Stage 5 Phase 2 for `catch.*return\s+(true|user)` patterns in changed code.

- **Stack trace returned in API error response as "debugging help."** AI generates `res.status(500).json({ error: err.message, stack: err.stack })` because that's how the developer asked for "informative" errors during development — and the AI doesn't differentiate development from production. Defense: Rule 5.2 + AP-2 — generic message + correlation ID; full detail to logs only.

- **Empty `catch` block to silence linter warnings.** AI generates `catch (e) {}` when the linter complains about unused exception variable, treating linter satisfaction as the goal rather than handling the exception. Defense: Rule 5.3 + AP-3 — every catch is a decision point; empty catch is a deferred bug.

- **Retry loop wrapping a security check.** AI generates retry-with-backoff around a function it doesn't know is a security check (signature verification, auth lookup) because retry-with-backoff is the default pattern for "this might fail" — useful for data fetches, dangerous for security gates. Defense: Rule 5.1 + AP-7 — security checks fail closed on transient failure; retries are explicitly forbidden.

- **Returning `null` / empty object on database error.** AI generates `try { return db.fetch(id) } catch (e) { return null }` because "the function returns a value or null." The caller has no way to distinguish "no row found" (legitimate empty) from "database threw an exception" (potentially security-relevant). Defense: Rule 5.3 + AP-9 — exceptions propagate, optional results return Maybe/Optional or explicit "not found" sentinel, never silently flatten error to absence.

- **No correlation ID because "we use logging."** AI generates structured logging but doesn't propagate a correlation ID into error responses, treating logging as sufficient. Without the ID surfaced to the user, the log search becomes a haystack hunt. Defense: Rule 5.6 + AP-8 — correlation ID is the bridge between user report and log entry.

Relevant external taxonomies: `OWASP-TOP10 A10:2025` (Mishandling of Exceptional Conditions — new 2025 category); `CWE-209`, `CWE-754`, `CWE-755`, `CWE-388` (pillar); `MITRE-ATLAS` AML.T0048 (manipulation of training data is unrelated, but the equivalent for error handling is "abuse of fail-open conditions" — emerging adversarial pattern).
<!-- /SECTION: ai-concerns -->

<!-- SECTION: workflow -->
## §8 Workflow Integration

How SECURITY-ERROR-HANDLING participates in the six-stage workflow and four-pass review (per `docs/WORKFLOW.md`).

- **Stage 1 (Research):** Run the §3 discovery commands when the change adds error handling, external dependency calls, or security check return paths. Map existing exception patterns before adding new ones.
- **Stage 3 (Plan with Governance):** Contribute Rules 5.1–5.7 when the change introduces a new security check, wraps an external call, modifies error responses, or extends global exception handling.
- **Stage 4 (Implement):** Apply rules during writing — fail-closed return values; generic error messages + correlation IDs; explicit exception handlers (not catch-all empty); circuit-breaker / timeout for external calls; verify last-resort handler is wired.
- **Stage 5 Phase 2 (Security Audit):** Primary skill — all rules in scope. AP-1 (swallow-and-allow), AP-2 (stack trace exposure), AP-4 (default-permit on failure), AP-7 (retry-on-security-check) are typically High or Critical severity.
- **Stage 5 Phase 3 (Red Team):** Probe error paths adversarially — what does the system do when the auth provider is unreachable? When the validation library throws? When the signature-verifier times out? When the third hop in a multi-step operation fails? Consult `security-iam-authentication` (Phase 6 commit 6/12) for auth-specific error paths.
- **Stage 5 Phase 4 (Holistic Review):** Verify the error-handling discipline is coherent — no fail-open regressions, no new stack-trace exposures, correlation IDs propagated through downstream calls, partial-failure semantics consistent with the rest of the codebase.
- **Stage 6 (Commit):** Critical / High findings (AP-1 in security path, AP-2 in production response, AP-4 in auth flow) get fixed before commit. Medium findings get fixed, waived in `WAIVER-LOG.md` per CONTINUITY Rule 5.3, or escalated to `VENDOR-LOG.md` (e.g., third-party SDK that throws ambiguous exceptions requiring vendor follow-up).
<!-- /SECTION: workflow -->

<!-- SECTION: subagent-context -->
## §9 Subagent Context

**Preloaded by:** None by default. Phase 6 foundation security skills are not preloaded into the existing four review subagents (per Phase 4 agent definitions). `security-auditor` and `red-team` consult this skill on demand based on Stage 3's plan when the change touches error handling, external calls, or security check return paths. Phase 11 (Meta-Skills) may revise subagent skill mappings.

**Critical rules for review use (when consulted but not preloaded):**

- Rule 5.1 (Security Checks Fail Closed)
- Rule 5.2 (Generic User-Facing Errors)
- Rule 5.3 (Exceptional Conditions Designed)
- Rule 5.4 (External Dependencies — Circuit Breakers)
- Rule 5.7 (Partial Failures Not Successes)

**Top AI-specific concerns:**

- `catch (e) { return true; }` as the path of least resistance in security checks
- Stack trace returned in API error response as "debugging help"
- Retry loop wrapping a security check

**Cross-skill web:**

- Foundation for later Phase 6 skills (cryptography, secrets-management, IAM) — fail-closed pattern these skills assume
- Pairs with `security-logging` (Phase 6 commit 10/12) — this skill says fail-closed-and-log; logging owns log format/protection
- Cross-references SECURITY-CORE Rule 5.2 (default-deny authorization is the authorization-specific application of fail-closed)
- Cross-references SECURITY-CORE Rule 5.7 (log security events; never log secrets — applies when logging exception details)
- Forwards to `security-iam-authentication` (Phase 6 commit 6/12) for auth-specific error paths (login failure response uniformity is auth-specific generic-error discipline)
- Forwards to `security-incident-response` (Phase 7) for the broader incident-response context that correlation IDs feed
- DISAGREEMENT Rule 5.2 routes severity for findings raised here (typically strong advocacy on AP-1 in security paths — close to hard-refusal territory)
- TESTING covers chaos-style external-failure testing and exception-path test coverage
- CONTINUITY Rule 5.3 routes waivers for error-handling gaps that can't be fully implemented this commit
- CODE-QUALITY Rule on solo-maintainability informs structured-handler readability over deep nested try/catch

Reference files (`rules.md`, `anti-patterns.md`) load on demand within the consulting subagent.
<!-- /SECTION: subagent-context -->
