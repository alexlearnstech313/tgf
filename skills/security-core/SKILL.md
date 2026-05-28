---
# ─── Anthropic-native runtime fields (Claude Code honors these) ───
name: security-core
description: |
  Universal security rules and security-mindedness as a default trait. Use when
  reviewing or writing any code that touches user data, external input,
  network operations, credentials, cryptography, or trust boundaries. Top
  rules from OWASP Top 10:2025 and OWASP ASVS 5.0 — secure by default with
  usability balance. Includes the hard-refusal list (per CLAUDE.md §5):
  hardcoded credentials, custom crypto, disabled TLS verification, broken
  algorithms, sensitive data in logs, bypassed authorization.
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
  - "**/*.sql"

# ─── TGF-extension metadata (Phase 11 meta-skills read these; Claude Code ignores) ───
applies-when:
  paths-include:
    - "**/*.{ts,tsx,js,jsx,py,go,rs,rb,java,kt,swift,php,cs,scala,sql}"
  operations-include:
    - authentication or session handling
    - authorization or access control check
    - cryptographic operation (hashing, encryption, signing, randomness)
    - secret or credential handling
    - external input parsing or validation
    - output rendering to HTML, JSON, SQL, shell, or other interpreted context
    - network call (HTTP, gRPC, third-party API)
    - logging or telemetry of security-relevant events
  data-flows-include:
    - untrusted input crossing into application code
    - sensitive data crossing trust boundary
    - persistence layer crossing application boundary
disqualifying-when:
  - documentation-only changes
  - test fixture additions without production code changes
  - dependency version bumps without code changes
  - pure formatting edits
sources:
  - OWASP Top 10:2025 (verified 2026-05-20)
  - OWASP ASVS 5.0.0 (verified 2026-05-20, released 2025-05-30)
  - OWASP Top 10 for LLM Applications 2025 (verified Phase 2, 2026-05-17)
  - NIST SP 800-218 v1.1 (SSDF) — PW.5, PW.6, PW.7 (verified 2026-05-20)
  - MITRE ATT&CK v17 (verified Phase 4, 2026-05-19)
  - MITRE ATLAS v5.4.0 (verified Phase 2, 2026-05-17)
last-generated: 2026-05-20
refresh-recommended: 2027-05-20
self-evolution:
  anti-patterns-observed: []
  triggers-refined: []
  ai-failures-documented: []
---

# SECURITY-CORE

> **Skill body ≤300 lines** (per `DEC-2026-05-19-007`). Principles, rule summaries, and navigation live here. Full content in reference files loaded on demand:
> - `rules.md` — full rules with rule-level citations
> - `anti-patterns.md` — full anti-pattern + canonical pattern pairs with code examples, including the CLAUDE.md §5 hard-refusal list

<!-- SECTION: overview -->
## §1 Overview

SECURITY-CORE governs the security dimension of every code change: input validation, authorization, cryptography, secrets handling, transport security, output encoding, and security logging. It is one of three always-on skills in TGF (alongside CODE-QUALITY and CONTINUITY).

This skill encodes the *trait* of security-mindedness — seeing attack surface before features, asking "who could abuse this?" by reflex, defaulting to secure-by-default with usability balance. It is not a comprehensive security catalog (the broader `security-*` skill suite in Phases 6–7 covers depth per topic). SECURITY-CORE captures what every change needs to consider, every time.

Rules cite OWASP Top 10:2025 (released 2025; new categories A03 Software Supply Chain Failures and A10 Mishandling of Exceptional Conditions) at the category level and OWASP ASVS 5.0.0 (released 2025-05-30; chapters significantly reorganized from 4.x) at the rule level where mapping exists. The hard-refusal list from `CLAUDE.md` §5 is fully covered in anti-patterns.
<!-- /SECTION: overview -->

<!-- SECTION: sources -->
## §2 Authoritative Sources

| Source ID | Reference | Version | Date Verified |
|-----------|-----------|---------|---------------|
| OWASP-TOP10 | [OWASP Top 10:2025](https://owasp.org/Top10/2025/) | 2025 | 2026-05-20 |
| OWASP-ASVS | [OWASP Application Security Verification Standard](https://github.com/OWASP/ASVS) | 5.0.0 (released 2025-05-30) | 2026-05-20 |
| OWASP-LLM | [OWASP Top 10 for LLM Applications](https://genai.owasp.org/llm-top-10/) | 2025 | 2026-05-17 (Phase 2) |
| NIST-SSDF | [NIST SP 800-218 Secure Software Development Framework](https://csrc.nist.gov/pubs/sp/800/218/final) | v1.1 | 2026-05-20 |
| MITRE-ATTACK | [MITRE ATT&CK Enterprise](https://attack.mitre.org) | v17 | 2026-05-19 |
| MITRE-ATLAS | [MITRE ATLAS — AI threat techniques](https://atlas.mitre.org) | v5.4.0 | 2026-05-17 (Phase 2) |

Citation granularity per Phase 4 Checkpoint 1 Decision A: OWASP Top 10:2025 cited at category level (A01:2025 through A10:2025) since the category IS the granular unit. OWASP ASVS 5.0.0 cited at rule level (e.g., `V1.2.5`) since ASVS rules have sub-identifiers. NIST SSDF cited at practice level (PW.5, PW.6, PW.7). OWASP LLM Top 10 cited at category level (LLM01:2025, LLM06:2025).
<!-- /SECTION: sources -->

<!-- SECTION: discovery -->
## §3 Discovery Commands

Copy-pasteable commands to capture security state before applying rules.

```bash
# Find hardcoded credential candidates (TGF's secret sweep)
git grep -inE "(api[_-]?key|secret[_-]?key|password|bearer|sk-[a-z0-9]{20}|ghp_[a-z0-9]{20}|aws_access_key|private[_-]?key)" -- ':!*.md' ':!*.template' 2>/dev/null | head -20

# Find disabled TLS verification (common patterns)
grep -rn "rejectUnauthorized.*false\|verify\s*=\s*False\|InsecureSkipVerify\s*:\s*true\|TLSClientConfig.*InsecureSkipVerify" --include="*.ts" --include="*.js" --include="*.py" --include="*.go" 2>/dev/null | head -20

# Find broken-algorithm usage
grep -rn "md5\|sha1\b\|MessageDigest.*MD5\|hashlib.md5\|hashlib.sha1" --include="*.ts" --include="*.js" --include="*.py" --include="*.java" 2>/dev/null | head -20

# Find SQL string-concatenation candidates
grep -rnE 'query\s*\(\s*["\x27][^"\x27]*\+|\.exec\s*\(\s*["\x27][^"\x27]*\+|f["\x27]\s*SELECT|f["\x27]\s*INSERT|f["\x27]\s*UPDATE|f["\x27]\s*DELETE' --include="*.ts" --include="*.js" --include="*.py" 2>/dev/null | head -20

# Find shell-injection candidates (user input + process spawning)
grep -rnE "child_process\.exec\s*\(|execSync\s*\(|subprocess.*shell\s*=\s*True|os\.system" --include="*.ts" --include="*.js" --include="*.py" 2>/dev/null | head -20
```
<!-- /SECTION: discovery -->

<!-- SECTION: principles -->
## §4 Universal Principles

Seven principles that ground every numbered rule. These preload into the orchestrator agent context (per `DEC-2026-05-19-007`).

- **See attack surface before features.** Every input, every endpoint, every dependency, every external call is potential attack surface. The reflex "who could abuse this?" comes before "does this work?" — not after.

- **Default deny; explicit allow.** Authorization defaults to "no access" unless an explicit rule permits the operation. The opposite — "allow unless something blocks it" — is how privilege escalation happens. Apply at every layer: routing, controllers, services, data access.

- **Validate at trust boundaries; encode at output context.** Untrusted input is validated against an explicit schema at the boundary where it enters the application. Output to HTML, JSON, SQL, shell, etc. is encoded for the target context where it leaves. These are two different operations on opposite ends of the data path; conflating them creates injection.

- **Use established cryptography; never roll your own.** Cryptographic operations use well-vetted libraries with current algorithm choices. Custom crypto, ad-hoc "encryption" with XOR or rotation, MD5/SHA-1 for security purposes, DES, RC4 — all forbidden (hard-refusal list per `CLAUDE.md` §5). The track record of homemade crypto is 100% broken; this is not an area to be clever.

- **Secrets live in the secret manager.** Credentials, API keys, tokens, encryption keys never appear in code, logs, or version control. Environment variables for development, dedicated secret managers for production. The cost of one leaked secret is paid back across every system the secret touched.

- **Fail closed; log what failed.** When a security check cannot be performed (network down, secret manager unreachable, ambiguous state), default to deny rather than allow. Log the failure with enough context to investigate, without logging the secrets themselves.

- **Defense in depth.** Every security control assumes the layer above it might fail. Input validation does not excuse missing output encoding; output encoding does not excuse missing parameterized queries. The cost of redundant layers is small; the cost of a single layer being the only defense is unbounded.
<!-- /SECTION: principles -->

<!-- SECTION: rules -->
## §5 Rule Summaries

Seven rules. Each summary: title + 1-line statement + source identifier. Coverage map at the end ties each OWASP Top 10:2025 category to a rule, principle, or downstream skill.

<!-- RULE: 5.1 -->
- **Rule 5.1: Validate Input at Trust Boundaries** — Every input from an external source validated against an explicit schema before use; validation happens at the boundary, not "eventually" in business logic. `OWASP-TOP10 A05:2025 (Injection)` + `OWASP-ASVS 5.0 V2 (Validation and Business Logic)` → [`rules.md#rule-51-validate-input-at-trust-boundaries`](rules.md)
<!-- /RULE: 5.1 -->
<!-- RULE: 5.2 -->
- **Rule 5.2: Authorize Every Action, Default Deny** — Every operation touching protected data verifies caller authorization at the operation site; default deny, explicit allow rules grant access. `OWASP-TOP10 A01:2025 (Broken Access Control)` + `OWASP-ASVS 5.0 V8 (Authorization)` → [`rules.md#rule-52-authorize-every-action-default-deny`](rules.md)
<!-- /RULE: 5.2 -->
<!-- RULE: 5.3 -->
- **Rule 5.3: Use Established Cryptography; Never Roll Your Own** — Crypto operations use well-vetted libraries with current algorithms; no custom crypto, no MD5/SHA-1 for security, no DES/RC4. Hard-refusal items per `CLAUDE.md` §5. `OWASP-TOP10 A04:2025 (Cryptographic Failures)` + `OWASP-ASVS 5.0 V11 (Cryptography)` → [`rules.md#rule-53-use-established-cryptography`](rules.md)
<!-- /RULE: 5.3 -->
<!-- RULE: 5.4 -->
- **Rule 5.4: Secrets Never in Code, Logs, or Version Control** — Credentials, API keys, tokens, encryption keys in environment variables or secret managers — never in code, logs, or commits. Hard-refusal items per `CLAUDE.md` §5. `OWASP-TOP10 A02:2025 (Security Misconfiguration)` + `OWASP-ASVS 5.0 V11 (Cryptography)` → [`rules.md#rule-54-secrets-never-in-code-logs-or-version-control`](rules.md)
<!-- /RULE: 5.4 -->
<!-- RULE: 5.5 -->
- **Rule 5.5: TLS Verification Always Enabled, Strong Defaults** — Outbound HTTPS verifies certificates; servers enforce minimum TLS 1.2 (prefer 1.3); HSTS for browsers. Hard-refusal item per `CLAUDE.md` §5: disabled TLS verification. `OWASP-TOP10 A02:2025 (Security Misconfiguration)` + `OWASP-ASVS 5.0 V12 (Secure Communication)` → [`rules.md#rule-55-tls-verification-always-enabled`](rules.md)
<!-- /RULE: 5.5 -->
<!-- RULE: 5.6 -->
- **Rule 5.6: Output Encoding Matches Context** — Output to HTML, JSON, SQL, shell, etc. encoded for the target context; no string concatenation of untrusted data into query/markup/command strings. `OWASP-TOP10 A05:2025 (Injection)` + `OWASP-ASVS 5.0 V1 (Encoding and Sanitization)` → [`rules.md#rule-56-output-encoding-matches-context`](rules.md)
<!-- /RULE: 5.6 -->
<!-- RULE: 5.7 -->
- **Rule 5.7: Log Security Events; Never Log Secrets** — Authn/authz failures, security-relevant state changes, errors at trust boundaries logged with context to investigate. Passwords, tokens, full PII, encryption keys NEVER in logs. Hard-refusal item per `CLAUDE.md` §5. `OWASP-TOP10 A09:2025 (Security Logging and Alerting Failures)` + `OWASP-ASVS 5.0 V16 (Security Logging and Error Handling)` → [`rules.md#rule-57-log-security-events-never-log-secrets`](rules.md)
<!-- /RULE: 5.7 -->

### OWASP Top 10:2025 coverage map

| Category | Coverage |
|----------|----------|
| A01:2025 Broken Access Control | Rule 5.2 |
| A02:2025 Security Misconfiguration | Rules 5.4, 5.5 |
| A03:2025 Software Supply Chain Failures | Principle "see attack surface before features"; depth in `security-supply-chain` skill (Phase 7) |
| A04:2025 Cryptographic Failures | Rules 5.3, 5.4 |
| A05:2025 Injection | Rules 5.1, 5.6 |
| A06:2025 Insecure Design | Principles "default deny" and "defense in depth"; depth in `security-secure-architecture` + `security-threat-modeling` skills (Phase 7) |
| A07:2025 Authentication Failures | Rule 5.2 (authorization implies authentication context); depth in `security-iam-authentication` (Phase 6) |
| A08:2025 Software or Data Integrity Failures | Principle "defense in depth"; depth in `security-data-encryption` + `security-supply-chain` skills (Phase 7) |
| A09:2025 Security Logging and Alerting Failures | Rule 5.7 |
| A10:2025 Mishandling of Exceptional Conditions | Principle "fail closed, log what failed"; depth in CODE-QUALITY Rule 5.2 + `security-error-handling` skill (Phase 7) |

See `rules.md` for full rule text, citations, plain-language impact, and extended discussion.
<!-- /SECTION: rules -->

<!-- SECTION: anti-patterns -->
## §6 Anti-Pattern Summaries

Nine anti-pattern pairs covering the `CLAUDE.md` §5 hard-refusal list (seven items, each mapped) + the most common injection patterns.

<!-- ANTI-PATTERN: AP-1 -->
- **AP-1: Hardcoded credentials in source** — API key, database password, or service account token assigned to a constant in source code or committed to version control. Violates Rule 5.4 (hard-refusal). → [`anti-patterns.md#ap-1-hardcoded-credentials`](anti-patterns.md)
<!-- /ANTI-PATTERN: AP-1 -->
<!-- ANTI-PATTERN: AP-2 -->
- **AP-2: Custom cryptography** — Homemade hash function, XOR-based "encryption," ad-hoc obfuscation passed off as crypto. Violates Rule 5.3 (hard-refusal). → [`anti-patterns.md#ap-2-custom-cryptography`](anti-patterns.md)
<!-- /ANTI-PATTERN: AP-2 -->
<!-- ANTI-PATTERN: AP-3 -->
- **AP-3: Disabled TLS verification** — `rejectUnauthorized: false`, `verify=False`, `InsecureSkipVerify: true` on production network calls. Violates Rule 5.5 (hard-refusal). → [`anti-patterns.md#ap-3-disabled-tls-verification`](anti-patterns.md)
<!-- /ANTI-PATTERN: AP-3 -->
<!-- ANTI-PATTERN: AP-4 -->
- **AP-4: MD5 or SHA-1 for security purposes** — Using MD5 to hash passwords, SHA-1 to sign tokens, or either for authenticity. Violates Rule 5.3 (hard-refusal). → [`anti-patterns.md#ap-4-md5-or-sha-1-for-security`](anti-patterns.md)
<!-- /ANTI-PATTERN: AP-4 -->
<!-- ANTI-PATTERN: AP-5 -->
- **AP-5: Logging sensitive data** — `logger.info(request.body)` where body includes a password, token, or full PII payload. Violates Rule 5.7 (hard-refusal). → [`anti-patterns.md#ap-5-logging-sensitive-data`](anti-patterns.md)
<!-- /ANTI-PATTERN: AP-5 -->
<!-- ANTI-PATTERN: AP-6 -->
- **AP-6: SQL injection via string concatenation** — Query built with `"SELECT … WHERE id = " + userInput` or f-string interpolation of untrusted values. Violates Rules 5.1 and 5.6. → [`anti-patterns.md#ap-6-sql-injection`](anti-patterns.md)
<!-- /ANTI-PATTERN: AP-6 -->
<!-- ANTI-PATTERN: AP-7 -->
- **AP-7: Authorization by obscurity** — Relying on "hard-to-guess" UUIDs or URL slugs to gate access without an actual authorization check. Violates Rule 5.2 (hard-refusal: bypassing authorization for convenience). → [`anti-patterns.md#ap-7-authorization-by-obscurity`](anti-patterns.md)
<!-- /ANTI-PATTERN: AP-7 -->
<!-- ANTI-PATTERN: AP-8 -->
- **AP-8: Shell command from user input** — User-provided filename, URL, or argument passed into a shell-spawning call without input validation. Violates Rules 5.1 and 5.6. → [`anti-patterns.md#ap-8-shell-command-from-user-input`](anti-patterns.md)
<!-- /ANTI-PATTERN: AP-8 -->
<!-- ANTI-PATTERN: AP-9 -->
- **AP-9: Disabled authentication middleware** — Auth middleware bypassed via environment toggle, commented-out registration, or "dev mode" early return that ships to production. Violates `CLAUDE.md` §5 hard-refusal list directly; precondition failure for Rule 5.2 (Rule 5.2 cannot evaluate without an authenticated principal). → [`anti-patterns.md#ap-9-disabled-authentication-middleware`](anti-patterns.md)
<!-- /ANTI-PATTERN: AP-9 -->

Per `DEC-2026-05-17-003` Clause 1: standalone anti-patterns without paired canonical patterns are incomplete and do not ship. All nine have CPs in `anti-patterns.md`. The seven `CLAUDE.md` §5 hard-refusal items map: AP-1 (hardcoded credentials), AP-2 (custom crypto), AP-9 (disabled authentication), AP-3 (disabled TLS), AP-4 (broken algorithms), AP-5 (logging secrets), AP-7 (authorization bypass).
<!-- /SECTION: anti-patterns -->

<!-- SECTION: ai-concerns -->
## §7 AI-Specific Concerns

Security failure modes specific to AI-generated code and AI-integrated systems. Derived from observed behavior and the OWASP Top 10 for LLM Applications 2025 framework.

- **Plausible-secure-but-wrong.** AI generates code that uses recognizably "security-looking" patterns (bcrypt import, parameterized query syntax, JWT library call) while still being vulnerable: wrong cost factor, parameterized but missing one query, JWT verification disabled. The shape is right; the substance is wrong. Defense: read the *behavior*, not the imports.

- **Stale-security-pattern reproduction.** Training data over-represents older security patterns: MD5 password hashing, JWT `alg: none` workarounds, broad CORS wildcards. AI defaults to what's frequent in training. Defense: rule-level citations to current OWASP Top 10:2025 + ASVS 5.0 catch mismatches.

- **Defense-by-comment.** AI generates code with a comment claiming "input sanitized" without actually sanitizing, or "authorized" without checking. The comment satisfies the prompt's mention of security; the code does not. Defense: the comment is not a control; verify the actual code.

- **Prompt injection — LLM01:2025.** Untrusted input reaches the LLM and changes its behavior. Particularly dangerous when the LLM has tool access. Defense: treat all LLM input as untrusted; validate output before acting; bound tool permissions per `LLM06:2025` (excessive agency).

- **Excessive agency — LLM06:2025.** AI agent has tool access broader than its task requires (e.g., shell access for a code-review agent). Damage radius compounds with broad tool permissions. Defense: explicit allowed-tools per skill/agent; never `Bash(*)` for AI-agent contexts handling untrusted input.

Relevant taxonomies: `OWASP-LLM LLM01:2025` (Prompt Injection), `LLM06:2025` (Excessive Agency), `LLM09:2025` (Misinformation, including fabricated security advice or citations), and `MITRE-ATLAS` AML.T0051 (LLM Output Handling failures).
<!-- /SECTION: ai-concerns -->

<!-- SECTION: workflow -->
## §8 Workflow Integration

How SECURITY-CORE participates in the six-stage workflow and four-pass review (per `docs/WORKFLOW.md`).

- **Stage 1 (Research):** Run the §3 discovery commands when the change touches security-relevant code. Surface existing patterns (good and bad) before adding new ones.
- **Stage 3 (Plan with Governance):** Contribute Rules 5.1–5.7 when the change touches any: input validation, authorization, crypto, secrets, transport security, output encoding, security logging. The hard-refusal list (§4 principles + §6 anti-patterns) applies regardless of scope.
- **Stage 4 (Implement):** Apply rules during writing; principles in §4 are the writing posture. AP-1 through AP-8 are the patterns to reject.
- **Stage 5 Phase 2 (Security Audit):** Primary skill — all rules in scope. The hard-refusal list is non-negotiable in security audit; findings on these are Critical severity.
- **Stage 5 Phase 3 (Red Team):** Adversarial mindset uses these rules as the floor — what attacks bypass them, what edge cases evade them. Red Team consults `security-threat-modeling` and `security-attack-surface` skills (Phase 7) for depth.
- **Stage 6 (Commit):** Critical findings get fixed before commit. High/medium findings get fixed, waived in `WAIVER-LOG.md` with rationale and revisit date, or escalated to `VENDOR-LOG.md` for out-of-codebase actions.
<!-- /SECTION: workflow -->

<!-- SECTION: subagent-context -->
## §9 Subagent Context

**Preloaded by:** `tgf-orchestrator` (always-on — SECURITY-CORE is one of the three always-on skills injected into every main-session context); `security-auditor` (primary — all rules); `red-team` (rules as floor; full content for AP-based attack scenario seeding). Per `DEC-2026-05-19-007`, the full skill content injects into each of these agents' context at startup via the agent definition's `skills:` field.

**Critical rules for review use (when consulted but not preloaded):**

- Rule 5.1 (Validate Input at Trust Boundaries)
- Rule 5.2 (Authorize Every Action, Default Deny)
- Rule 5.3 (Use Established Cryptography)
- Rule 5.4 (Secrets Never in Code, Logs, or Version Control)

**Top AI-specific concerns:**

- Plausible-secure-but-wrong (right imports, wrong behavior)
- Defense-by-comment (comment claims security, code does not provide it)
- Excessive agency (`LLM06:2025`) for AI-agent contexts with tool access

Reference files (`rules.md`, `anti-patterns.md`) load on demand within the subagent.
