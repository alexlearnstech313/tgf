# Phase 6 Implementation Plan: Foundation Security Skills (11)

**Date:** 2026-05-20
**Status:** Checkpoint 1 cleared (2026-05-20) — all four decisions resolved without new ADRs. Implementation cleared.
**Process:** Per the validated phase-workflow pattern (Phases 2, 3, 4, 5) — write phase-N-plan.md first, get explicit approval on open decisions, then implement. Mid-phase scope amendments are surfaced consciously and captured in this plan file (precedent: Phase 5 Decision F adding UI-CRAFT).

---

## 1. Status Summary

Phase 5 closed 2026-05-20 with seven activity skills shipped (DISCOVERY, PROJECT-MANAGEMENT, DESIGN, UI-CRAFT, TESTING, DEBUGGING, DISAGREEMENT) — 7,621 lines across 21 files. Phase 5 grew 6→7 mid-phase per Decision F when the user surfaced that DESIGN's "decision discipline" scope didn't cover design craft / anti-AI-slop. Cross-skill composition is now demonstrably the framework's emergent value: DISAGREEMENT references SECURITY-CORE hard-refusal items + CONTINUITY waiver protocol; TESTING cross-refs SECURITY-CORE + DESIGN + UI-CRAFT + CONTINUITY; DEBUGGING cross-refs CONTINUITY + DISCOVERY + TESTING.

Combined Phase 4 + 5 totals: 10 substantive skills (3 always-on + 7 activity), 10,824 lines of skill content, 5 agent scaffolds, foundational architecture (CLAUDE.md + ARCHITECTURE.md + WORKFLOW.md + 10 ADRs).

Phase 6 produces eleven **foundation security skills** — domain-depth skills that extend SECURITY-CORE's seven universal rules. Phase 4's SECURITY-CORE established the trait of security-mindedness and the universal floor; Phase 6 ships the depth on the security domains every project needs regardless of stack. Phases 7 (extended security, 22 skills), 8 (AI-specific, 9 skills), 10 (compliance, 5 skills) build on top.

Phase 6 deliverables:

1. `skills/security-input-validation/` — boundary validation discipline; schema-first; reject-don't-sanitize
2. `skills/security-output-encoding/` — context-aware encoding at output boundary; injection defense
3. `skills/security-iam-authentication/` — credential verification, password hashing, MFA, account recovery
4. `skills/security-iam-sessions/` — session lifecycle, cookie attributes, JWT/self-contained tokens, rotation
5. `skills/security-iam-authorization/` — default-deny at operation site; RBAC/ABAC patterns
6. `skills/security-cryptography/` — algorithm choice, key management, randomness, common pitfalls
7. `skills/security-database/` — parameterized queries, RLS, connection security, data classification at the DB layer
8. `skills/security-error-handling/` — fail-closed semantics, error message hygiene, exceptional condition discipline
9. `skills/security-logging/` — security event capture, log injection defense, sensitive-data scrubbing
10. `skills/security-secrets-management/` — secret lifecycle, rotation, scoping, leak detection
11. `skills/security-supply-chain/` — dependency provenance, SBOM, build integrity, transitive risk

Each skill ships SKILL.md + rules.md + anti-patterns.md per the reference-file pattern (DEC-2026-05-19-008). SKILL.md body ≤300 lines per skill (DEC-2026-05-19-007).

Estimated effort: 11 focused commits (one per skill) + closeout = ~12 commits. ~5-8 sessions, ~22-30 hours total.

---

## 2. Architectural Foundation

Phase 6 implementation operates against the locked architecture established in Phases 0–5. Key constraints:

- **SKILL.md body ≤300 lines per skill** (per DEC-2026-05-19-007). Verbose rule content + AP code examples move to `rules.md` and `anti-patterns.md`.
- **Reference file pattern is standard** per DEC-2026-05-19-008 — every Phase 6 skill ships `rules.md` + `anti-patterns.md` from day one. Defer `citations.md` split until any skill's `rules.md` exceeds ~400 lines.
- **Anthropic-native runtime frontmatter only** — `name`, `description`, `paths`. TGF-extension metadata (`applies-when`, `disqualifying-when`, `sources`, `last-generated`, `refresh-recommended`, `self-evolution`) is documentation for Phase 11 meta-skills, not runtime gates (per DEC-2026-05-19-007 amendment to DEC-2026-05-17-003 Clause 1).
- **Citation granularity per Phase 4 Checkpoint 1 Decision A** — cite at the source's natural granularity. OWASP Top 10:2025 at category level (A01:2025…A10:2025). OWASP ASVS 5.0 at the most specific identifier the source provides (sub-rule level where mapping is crisp at Stage 1; chapter level fallback). NIST SP 800-series at section level (§N.N.N). RFCs at section level (§N.N). MITRE ATT&CK / ATLAS at technique ID.
- **OWASP ASVS 5.0 chapter numbering** is the 5.0 reorganization (released 2025-05-30 at Global AppSec EU Barcelona), NOT the legacy 4.x V-numbers. Verified during Phase 4 SECURITY-CORE implementation:
  - V1 Encoding and Sanitization
  - V2 Validation and Business Logic
  - V3 Web Frontend Security
  - V4 API and Web Service
  - V5 File Handling
  - V6 Authentication
  - V7 Session Management
  - V8 Authorization
  - V9 Self-contained Tokens
  - V10 OAuth and OIDC
  - V11 Cryptography
  - V12 Secure Communication
  - V13 Configuration
  - V14 Data Protection
  - V15 Secure Coding and Architecture
  - V16 Security Logging and Error Handling
  - V17 WebRTC
- **SECURITY-CORE is the universal floor; Phase 6 extends depth.** Each Phase 6 skill maps to one or more SECURITY-CORE rules (5.1–5.7) and extends them with domain-specific rules and APs. The discipline established at Checkpoint 1 Decision B (below) governs whether Phase 6 restates or references.
- **Subagent preload notes.** Phase 6 skills are not preloaded by default into the existing four review subagents (per Phase 4 agent definitions). They activate at the orchestrator level during Stage 3 (Plan with Governance) when the change context triggers their `paths`/`applies-when` conditions. Stage 5 Phase 2 (Security Audit) loads them on demand based on Stage 3's plan. Subagent skill mappings may evolve in Phase 11 when the orchestration meta-skill matures.

These constraints inform every per-skill mini-spec below.

---

## 3. Sources Verification

Per DEC-2026-05-17-004 Clause 1 (live verification at skill-creation time). Sources below are either verified from prior phases or queued for Stage 1 verification when each skill's implementation begins.

**Per Phase 4/5 plan-adjustment lessons:**

- OWASP Top 10:2025 categories and OWASP ASVS 5.0 chapter numbers already verified during Phase 4 SECURITY-CORE (2026-05-20). Sub-rule identifiers within each chapter need fresh Stage 1 verification per skill — ASVS chapters reorganized substantially from 4.x and sub-rules may have renumbered.
- OWASP Cheat Sheet Series (cheatsheetseries.owasp.org) is SPA-rendered in places — expect WebFetch to return titles only. Cite by reference per DEC-2026-05-17-004 Clause 5 when content can't be fetched; sources are publicly published and URL-stable.
- NIST SP 800-series PDFs may be fetchable via `csrc.nist.gov`; check at Stage 1. RFC documents are reliably fetchable via `tools.ietf.org` or `rfc-editor.org`.
- Living standards (OWASP versions, NIST current revisions) benefit from fresh Stage 1 fetches per skill. Stable methodology (RFCs that haven't been superseded, mature NIST publications) does not — pause before queueing reflexive fetches.

### Shared sources (cited across multiple Phase 6 skills)

| Source | Where used | Verification status |
|--------|------------|---------------------|
| OWASP Top 10:2025 | A01 (authorization), A02 (secrets, supply-chain), A03 (supply-chain), A04 (crypto), A05 (input-validation, output-encoding, database), A07 (authentication), A08 (crypto, supply-chain), A09 (logging, error-handling), A10 (error-handling) | Verified Phase 4, 2026-05-20 |
| OWASP ASVS 5.0.0 (released 2025-05-30) | V1–V14, V16 chapters across the 11 skills | Chapter list verified Phase 4; sub-rule numbers need fresh Stage 1 verification per skill |
| NIST SP 800-218 v1.1 (SSDF) | PW.4–PW.7 across multiple skills; PS.1–PS.3 for supply-chain | Verified Phase 2 + Phase 4 |
| OWASP Top 10 for LLM Applications 2025 | LLM01 (prompt-injection-as-input-validation-context), LLM02 (output-handling), LLM06 (excessive agency), LLM09 (misinformation) | Verified Phase 2, 2026-05-17 |
| MITRE ATT&CK v17 | T1110 (brute force) in iam-authentication; T1078 (valid accounts) in iam-authorization; T1562 (impair defenses, log evasion) in logging; T1195 (supply chain compromise) in supply-chain | Verified Phase 4, 2026-05-19 |
| MITRE ATLAS v5.4.0 | Adversarial AI references in §7 AI-Specific Concerns of each skill | Verified Phase 2, 2026-05-17 |
| OWASP Cheat Sheet Series (cheatsheetseries.owasp.org) | Per-domain cheat sheets cross-referenced from each skill | Likely SPA-rendered per Phase 5 pattern; cite by reference at Stage 1 |
| CWE database (cwe.mitre.org) | CWE IDs referenced for concrete failure-mode mapping where ASVS sub-rule mapping is thin | Spot-check fetchability at Stage 1; cite by ID + title with version |

### Per-skill specific sources

| Skill | Skill-specific sources | Verification status |
|-------|------------------------|---------------------|
| **security-input-validation** | OWASP ASVS 5.0 V2 (Validation and Business Logic) + V4 (API and Web Service); OWASP Cheat Sheet — Input Validation; CWE-20 (Improper Input Validation), CWE-1287 (Improper Validation of Specified Type of Input) | Stage 1 per skill |
| **security-output-encoding** | OWASP ASVS 5.0 V1 (Encoding and Sanitization); OWASP Cheat Sheet — XSS Prevention, SQL Injection Prevention, OS Command Injection Defense, LDAP Injection Prevention; CWE-79 (XSS), CWE-89 (SQL injection), CWE-78 (OS command injection) | Stage 1 per skill |
| **security-iam-authentication** | OWASP ASVS 5.0 V6 (Authentication); NIST SP 800-63B Rev 4 (Authentication and Lifecycle Management; March 2024 publication); OWASP Cheat Sheet — Authentication, Password Storage, Forgot Password, Credential Stuffing Prevention; CWE-287 (Improper Authentication), CWE-521 (Weak Password Requirements) | Stage 1; NIST SP 800-63 fetchable via csrc.nist.gov |
| **security-iam-sessions** | OWASP ASVS 5.0 V7 (Session Management) + V9 (Self-contained Tokens); RFC 6265bis (Cookies); RFC 8725 (JWT Best Current Practices); NIST SP 800-63B Rev 4 §7 (Session Management); OWASP Cheat Sheet — Session Management, JSON Web Token; CWE-384 (Session Fixation), CWE-613 (Insufficient Session Expiration) | Stage 1; RFCs reliably fetchable |
| **security-iam-authorization** | OWASP ASVS 5.0 V8 (Authorization); NIST SP 800-162 (ABAC); NIST SP 800-207 (Zero Trust Architecture); OWASP Cheat Sheet — Authorization; CWE-285 (Improper Authorization), CWE-639 (Authorization Bypass Through User-Controlled Key) | Stage 1 |
| **security-cryptography** | OWASP ASVS 5.0 V11 (Cryptography) + V12 (Secure Communication); NIST SP 800-57 Part 1 Rev 5 (Key Management — General); NIST SP 800-175B Rev 1 (Guideline for Using Crypto Standards); NIST FIPS 197 (AES), FIPS 180-4 (SHA), FIPS 202 (SHA-3); RFC 8446 (TLS 1.3), RFC 8996 (deprecating TLS 1.0/1.1); OWASP Cheat Sheet — Cryptographic Storage, Key Management; CWE-327 (Broken Crypto), CWE-326 (Inadequate Encryption Strength), CWE-330 (Insufficient Randomness) | Stage 1; NIST + RFC sources fetchable |
| **security-database** | OWASP ASVS 5.0 V14 (Data Protection) + V2 (parameterization rules in V2); OWASP Cheat Sheet — SQL Injection Prevention, Database Security; CIS Database Benchmarks (per-engine; cite by reference, gated); CWE-89 (SQL injection), CWE-915 (Mass Assignment) | Stage 1; CIS Benchmarks paywalled-style — cite by reference |
| **security-error-handling** | OWASP ASVS 5.0 V16 (Security Logging and Error Handling); OWASP Cheat Sheet — Error Handling; CWE-209 (Information Exposure Through Error Message), CWE-754 (Improper Check for Unusual or Exceptional Conditions), CWE-755 (Improper Handling of Exceptional Conditions) | Stage 1 |
| **security-logging** | OWASP ASVS 5.0 V16 (Security Logging and Error Handling); NIST SP 800-92 (Guide to Computer Security Log Management — verify current rev at Stage 1; original is 2006 Rev 1); OWASP Cheat Sheet — Logging Vocabulary, Logging; MITRE ATT&CK T1562.002 (Disable Windows Event Logging) + T1070 (Indicator Removal); CWE-117 (Improper Output Neutralization for Logs), CWE-532 (Insertion of Sensitive Info into Log File) | Stage 1; NIST SP 800-92 may be older — surface in plan-adjustments if so |
| **security-secrets-management** | OWASP ASVS 5.0 V11 (Cryptography — key management subsection) + V13 (Configuration); NIST SP 800-57 Part 1 Rev 5 (Key Management); NIST SP 800-152 (Profile for Cryptographic Key Management Systems); OWASP Cheat Sheet — Secrets Management; CWE-798 (Hardcoded Credentials), CWE-321 (Hardcoded Cryptographic Key) | Stage 1 |
| **security-supply-chain** | OWASP Top 10:2025 A03 (Software Supply Chain Failures — new category in 2025); NIST SP 800-218 v1.1 (SSDF) — PS.1, PS.2, PS.3 supply-chain practices; NIST SP 800-204D (Strategies for Integrating SSC Risk Management); SLSA v1.0 (slsa.dev — Supply-chain Levels for Software Artifacts); CISA Software Acquisition Guide; OWASP Cheat Sheet — Vulnerable Dependency Management, Third Party JavaScript Management; CWE-1357 (Reliance on Insufficiently Trustworthy Component) | Stage 1; SLSA + CISA pages likely fetchable |

### Comparative sources (design-rationale only, per DEC-2026-05-17-004 Clause 6)

| Source | Phase 6 use |
|--------|-------------|
| Bruce Schneier — "Cryptography Engineering" (Ferguson/Schneier/Kohno, 2010) | Comparative validation for cryptography rules; book — appears in design rationale, NOT in §2 Sources |
| Ross Anderson — "Security Engineering" (3rd ed 2020) | Comparative validation across multiple Phase 6 domains; book — design rationale only |
| Google SRE Workbook + Site Reliability Engineering | Comparative validation for logging + error-handling operational patterns; appears in design rationale |
| HashiCorp Vault documentation; AWS Secrets Manager / GCP Secret Manager docs | Comparative validation for secrets-management canonical patterns; vendor-primary, but used as comparative not authoritative |
| Sigstore + in-toto + Tekton Chains documentation | Comparative validation for supply-chain canonical patterns; appears in CP examples without becoming authoritative citation |

Comparative sources stay in design-rationale notes within this plan; they do not appear in skill `§2 Authoritative Sources` tables.

---

## 4. Per-Skill Mini-Specs

Each skill follows the locked 9-section structure per `templates/SKILL.md.template`. Section line targets are heuristics (Phase 2 lesson: line targets are not hard requirements; content quality wins over line count). Target SKILL.md body ~250-290 lines.

### security-input-validation

**Scope:** Boundary validation discipline. Schema-first declaration. Reject-don't-sanitize. Validation at the trust boundary where untrusted input enters the application; not "eventually" in business logic. Extends SECURITY-CORE Rule 5.1.

**Description (≤500 chars):** "Boundary input validation discipline. Use when accepting external input — HTTP request bodies, query parameters, headers, file content, third-party API responses, message queue payloads, deserialized data. Schema-first validation that rejects on shape mismatch; sanitization is the wrong abstraction (handle output encoding via security-output-encoding instead). Extends SECURITY-CORE Rule 5.1; aligns with OWASP ASVS 5.0 V2 + V4 and OWASP Top 10:2025 A05."

**SKILL.md sections (~250-290 lines):**
- §1 Overview (~30 lines — extends SECURITY-CORE Rule 5.1; trust boundary definition; reject vs sanitize)
- §2 Authoritative Sources (~20 lines)
- §3 Discovery Commands (~25 lines — grep for unvalidated body parsing, missing schema declarations)
- §4 Principles (~50 lines — validate at boundary not in business logic; reject don't sanitize; schema declares the contract; deserialize after validation; trust nothing crossing in; positive validation over blocklist)
- §5 Rule Summaries (~70 lines)
- §6 Anti-Pattern Summaries (~50 lines)
- §7 AI-Specific Concerns (~25 lines — permissive validation defaults, validation-by-comment, AI skipping validation when not prompted)
- §8 Workflow Integration (~15 lines — Stage 3 Plan with Governance; Stage 5 Phase 2 Security Audit)
- §9 Subagent Context (~10 lines — security-auditor consults; red-team consults for input-side attack surface)

**Per-skill QC criteria:**
- (a) ≥5 rules covering trust-boundary placement, schema-first declaration, reject-over-sanitize, deserialization safety, prompt-injection input considerations for LLM contexts
- (b) ≥8 anti-patterns paired with canonical patterns (including AI-prompt-style permissive validation)
- (c) Extends SECURITY-CORE Rule 5.1 with concrete schema-library examples (zod, pydantic, joi, json-schema)
- (d) Explicit cross-reference forward to security-output-encoding for the output side; explicit non-overlap with security-database (parameterization lives there)
- (e) SKILL.md body ≤300 lines

### security-output-encoding

**Scope:** Context-aware encoding at output boundary. SQL parameterization, HTML auto-escaping, shell argument arrays, structured serialization. Extends SECURITY-CORE Rule 5.6.

**Description (≤500 chars):** "Context-aware output encoding to defeat injection. Use when emitting data to a parsed/interpreted context — SQL queries, HTML markup, shell commands, LDAP filters, JSON/XML/YAML serialization, log lines, file paths, URLs. Parameterized queries; auto-escaping templating; argument arrays for processes. Extends SECURITY-CORE Rule 5.6; pairs with security-input-validation as the output-side defense for OWASP Top 10:2025 A05 (Injection)."

**SKILL.md sections (~250-280 lines):**
- §1 Overview (~30 lines — pair with input-validation; encoding-by-context not encoding-by-input)
- §2 Authoritative Sources (~20 lines)
- §3 Discovery Commands (~25 lines — grep for SQL string concat, HTML innerHTML, shell exec patterns)
- §4 Principles (~50 lines — encoding matches the consuming context; parameterization is the SQL default; auto-escape > manual escape; serialize via libraries; never assemble interpreted strings)
- §5 Rule Summaries (~70 lines)
- §6 Anti-Pattern Summaries (~50 lines)
- §7 AI-Specific Concerns (~25 lines — AI skipping parameterization in "quick" queries; AI assembling HTML via template literals; "first query parameterized, next one isn't")
- §8 Workflow Integration (~15 lines)
- §9 Subagent Context (~10 lines)

**Per-skill QC criteria:**
- (a) ≥5 rules covering SQL parameterization, HTML context-aware escaping, shell argument arrays, structured serialization, log-line encoding (log injection defense)
- (b) ≥8 anti-patterns paired with canonical patterns covering SQL string concat, dangerouslySetInnerHTML misuse, `exec` with shell-string interpolation, hand-built JSON
- (c) Extends SECURITY-CORE Rule 5.6 with depth per output context
- (d) Cross-reference to security-database for ORM-specific parameterization patterns; non-overlap maintained
- (e) SKILL.md body ≤300 lines

### security-iam-authentication

**Scope:** Credential verification, password storage, MFA, account recovery, credential stuffing defense. Extends SECURITY-CORE Rule 5.2 (which assumes an authenticated principal). Maps to OWASP Top 10:2025 A07 (Authentication Failures).

**Description (≤500 chars):** "Authentication discipline — credential verification, password hashing (Argon2id / bcrypt / scrypt), MFA implementation, account recovery, credential stuffing defense. Use when implementing login, signup, password reset, MFA enrollment, or any flow establishing 'who is this caller'. Aligns with OWASP ASVS 5.0 V6, NIST SP 800-63B Rev 4 (Authentication and Lifecycle Management), and OWASP Top 10:2025 A07. Pairs with security-iam-sessions for post-auth session establishment."

**SKILL.md sections (~270-290 lines):**
- §1 Overview (~30 lines — authentication vs authorization; password-only is not enough)
- §2 Authoritative Sources (~20 lines)
- §3 Discovery Commands (~25 lines — grep for password hashing patterns, MFA setup code, account recovery flows)
- §4 Principles (~55 lines — passwords get password-hashes not general hashes; failed login responses don't leak identity; MFA for sensitive operations; account recovery is an attack surface; credential stuffing happens at scale)
- §5 Rule Summaries (~75 lines)
- §6 Anti-Pattern Summaries (~55 lines)
- §7 AI-Specific Concerns (~25 lines — AI defaulting to MD5/SHA-256 for passwords from training data; AI generating "is this email registered?" responses that enable enumeration; AI implementing MFA via SMS only)
- §8 Workflow Integration (~15 lines)
- §9 Subagent Context (~10 lines)

**Per-skill QC criteria:**
- (a) ≥5 rules covering password hashing algorithm choice + parameters, login-response uniformity (no enumeration), MFA discipline, account recovery, credential stuffing defense (rate limiting + breach detection)
- (b) ≥8 anti-patterns paired with canonical patterns
- (c) Hard-refusal AP for MD5/SHA-1 password hashing references SECURITY-CORE AP-4 explicitly; skill-local AP adds Argon2id parameter pitfalls + bcrypt cost-factor issues
- (d) NIST SP 800-63B Rev 4 cited at §-level; current March 2024 publication
- (e) Cross-reference to security-iam-sessions for post-auth session establishment; non-overlap maintained
- (f) SKILL.md body ≤300 lines

### security-iam-sessions

**Scope:** Session lifecycle, cookie attributes (HttpOnly/Secure/SameSite), session ID rotation on auth state change, JWT and self-contained token discipline. Maps to OWASP ASVS 5.0 V7 + V9; bridges to OWASP Top 10:2025 A07.

**Description (≤500 chars):** "Session lifecycle and token discipline. Use when establishing sessions post-authentication, configuring session cookies (HttpOnly/Secure/SameSite/Path/Domain), rotating session IDs on privilege change, issuing or verifying JWTs and self-contained tokens, or implementing logout. Aligns with OWASP ASVS 5.0 V7 + V9, RFC 6265bis (cookies), RFC 8725 (JWT best practices), and NIST SP 800-63B Rev 4 §7. Pairs with security-iam-authentication and security-iam-authorization."

**SKILL.md sections (~270-290 lines):**
- §1 Overview (~30 lines — sessions vs tokens; cookies as defense-in-depth)
- §2 Authoritative Sources (~20 lines)
- §3 Discovery Commands (~25 lines — grep for cookie config, JWT verify calls, logout handling)
- §4 Principles (~55 lines — rotate on privilege change; HttpOnly + Secure + SameSite; bind session to context; verify JWT signature + claims; explicit expiry over indefinite)
- §5 Rule Summaries (~70 lines)
- §6 Anti-Pattern Summaries (~50 lines)
- §7 AI-Specific Concerns (~25 lines — AI defaulting to `alg: none` workarounds, AI skipping signature verification, AI generating session-ID via Math.random())
- §8 Workflow Integration (~15 lines)
- §9 Subagent Context (~10 lines)

**Per-skill QC criteria:**
- (a) ≥5 rules covering session ID generation (CSPRNG), cookie attributes, session rotation triggers (login, privilege change, MFA step-up), logout / revocation, JWT verification discipline (signature + claims + expiry)
- (b) ≥8 anti-patterns paired with canonical patterns (including `alg: none`, sessions persisting across login, JWT used as session cookie without rotation)
- (c) RFC 8725 cited at section level; RFC 6265bis cited at section level
- (d) Explicit boundary with security-iam-authentication (this skill begins where auth succeeds)
- (e) SKILL.md body ≤300 lines

### security-iam-authorization

**Scope:** Default-deny authorization at operation site (not just route layer); RBAC / ABAC patterns; IDOR (Insecure Direct Object Reference) defense; privilege escalation defense. Extends SECURITY-CORE Rule 5.2 directly. Maps to OWASP Top 10:2025 A01 (Broken Access Control — #1 in the 2025 list).

**Description (≤500 chars):** "Authorization discipline beyond the route layer. Use when controlling who can do what to which resource — protected endpoints, multi-tenant data access, background jobs, webhook handlers, admin operations. Default-deny at the operation site (not just middleware). RBAC and ABAC patterns. IDOR defense. Aligns with OWASP ASVS 5.0 V8 and OWASP Top 10:2025 A01 (the #1 risk category in 2025). Extends SECURITY-CORE Rule 5.2."

**SKILL.md sections (~270-290 lines):**
- §1 Overview (~30 lines — A01 is #1 for a reason; authorization at operation site)
- §2 Authoritative Sources (~20 lines)
- §3 Discovery Commands (~25 lines — grep for protected operations, missing authz checks, raw IDs in URLs)
- §4 Principles (~55 lines — default deny; check at operation site; user IDs are not authorization; RBAC simpler than ABAC when it fits; multi-tenant means tenant_id in every query; vertical and horizontal escalation distinct)
- §5 Rule Summaries (~75 lines)
- §6 Anti-Pattern Summaries (~55 lines)
- §7 AI-Specific Concerns (~25 lines — AI putting authz only at route layer; AI generating "user can access if they're the owner" without verifying it's their owner; AI ignoring multi-tenant context)
- §8 Workflow Integration (~15 lines)
- §9 Subagent Context (~10 lines)

**Per-skill QC criteria:**
- (a) ≥5 rules covering default-deny, operation-site checks, IDOR defense, RBAC discipline (role assignment + permission discipline), multi-tenant data isolation
- (b) ≥8 anti-patterns paired with canonical patterns including AP for authorization-only-at-middleware, IDOR via raw IDs, BOLA (Broken Object Level Authorization)
- (c) Extends SECURITY-CORE Rule 5.2 with depth; SECURITY-CORE AP-7 (authorization by obscurity) referenced not duplicated
- (d) Cross-reference to security-database for row-level security (RLS) patterns; cross-reference to future Phase 7 security-api for endpoint-level patterns
- (e) SKILL.md body ≤300 lines

### security-cryptography

**Scope:** Algorithm choice for hashing / encryption / signing / key derivation / randomness; key management basics; common cryptographic pitfalls. Extends SECURITY-CORE Rule 5.3 + Rule 5.5 (TLS). Phase 7 `security-data-encryption` covers depth on data-at-rest patterns.

**Description (≤500 chars):** "Cryptographic algorithm choice and key handling discipline. Use when implementing hashing (passwords, integrity, content-addressing), symmetric encryption (data at rest, sensitive fields), asymmetric crypto (signatures, key exchange), random generation for security, or configuring TLS. Argon2id / AES-256-GCM / ChaCha20-Poly1305 / Ed25519 baselines. Extends SECURITY-CORE Rules 5.3 + 5.5. Aligns with OWASP ASVS 5.0 V11 + V12, NIST SP 800-57 Rev 5, RFC 8446."

**SKILL.md sections (~280-300 lines):**
- §1 Overview (~30 lines — established libraries; never roll your own; algorithm-by-purpose)
- §2 Authoritative Sources (~25 lines — NIST + RFC + FIPS standards)
- §3 Discovery Commands (~25 lines — grep for hash calls, encryption patterns, key derivation, TLS config)
- §4 Principles (~55 lines — purpose determines algorithm; passwords are not general hashes; AEAD or HMAC pairing; randomness from CSPRNG only; keys live in key management not in code; algorithm agility matters)
- §5 Rule Summaries (~80 lines)
- §6 Anti-Pattern Summaries (~55 lines)
- §7 AI-Specific Concerns (~25 lines — MD5/SHA-1 from training data; AES-ECB suggestions; CBC without HMAC; Math.random for secrets; truncated GCM tags)
- §8 Workflow Integration (~15 lines)
- §9 Subagent Context (~10 lines)

**Per-skill QC criteria:**
- (a) ≥5 rules covering password hashing parameters, symmetric encryption (AEAD requirement), asymmetric crypto choice, secure randomness, key derivation function discipline
- (b) ≥8 anti-patterns paired with canonical patterns
- (c) Hard-refusal items (custom crypto AP-2, MD5/SHA-1 AP-4) reference SECURITY-CORE; skill-local APs add depth on misuse of established algorithms (ECB mode, static IVs, tag truncation)
- (d) 2026-current algorithm baselines verified at Stage 1 (Argon2id parameters; AES-GCM nonce discipline; Ed25519 vs RSA tradeoffs)
- (e) SKILL.md body ≤300 lines

### security-database

**Scope:** Parameterized queries, ORM-specific safety, row-level security (RLS), connection security, mass-assignment defense, data classification at the DB layer. Extends SECURITY-CORE Rule 5.1 + 5.6 in the database context. Phase 9 `data-architecture` covers schema design + index strategy (separate concern per DEC-008).

**Description (≤500 chars):** "Database security discipline — parameterized queries, ORM safety, row-level security policies, connection encryption, mass-assignment defense. Use when reading or writing the database, designing schemas with security in mind, configuring RLS, or handling sensitive columns. Aligns with OWASP ASVS 5.0 V14 + injection rules in V2. Pairs with security-input-validation, security-output-encoding (the DB-layer expression of those). Distinct from data-architecture (Phase 9) which covers non-security schema concerns."

**SKILL.md sections (~270-290 lines):**
- §1 Overview (~30 lines — database as trust boundary; security-database vs data-architecture)
- §2 Authoritative Sources (~20 lines)
- §3 Discovery Commands (~25 lines — grep query construction, ORM usage, raw SQL, mass-assignment)
- §4 Principles (~50 lines — parameterize always; ORMs are not magic; RLS at the database; least-privilege DB users; encrypted connections; mass-assignment is opt-in not opt-out)
- §5 Rule Summaries (~70 lines)
- §6 Anti-Pattern Summaries (~50 lines)
- §7 AI-Specific Concerns (~25 lines — AI ORM patterns that bypass RLS; AI generating mass-assignment via `Model(**request.body)`; AI using db admin user from app)
- §8 Workflow Integration (~15 lines)
- §9 Subagent Context (~10 lines)

**Per-skill QC criteria:**
- (a) ≥5 rules covering parameterized queries (incl. ORM raw SQL escape hatches), RLS / row-level isolation, connection security (encryption, scoped credentials), mass-assignment defense, sensitive column encryption decisions
- (b) ≥8 anti-patterns paired with canonical patterns
- (c) AP for ORM raw-SQL bypass + AP for app using DB superuser (instead of scoped roles)
- (d) Cross-reference to security-input-validation (boundary) and security-output-encoding (parameterization details); cross-reference forward to security-data-encryption Phase 7 for column encryption depth
- (e) SKILL.md body ≤300 lines

### security-error-handling

**Scope:** Fail-closed semantics for security checks; error message hygiene; structured exception handling; exceptional condition discipline. Maps to OWASP Top 10:2025 A10 (Mishandling of Exceptional Conditions — new category in 2025) and OWASP ASVS 5.0 V16.

**Description (≤500 chars):** "Error handling discipline — fail closed on security checks; error messages that don't leak internals; exceptional conditions handled deliberately not implicitly. Use when implementing security checks (auth, authorization, validation), wrapping external calls, structuring exception handlers, or designing error responses. Aligns with OWASP ASVS 5.0 V16 and the new OWASP Top 10:2025 A10 (Mishandling of Exceptional Conditions) category. Pairs with security-logging (what gets logged when errors fire)."

**SKILL.md sections (~250-280 lines):**
- §1 Overview (~30 lines — fail closed; exceptional conditions are not exceptions to security)
- §2 Authoritative Sources (~20 lines)
- §3 Discovery Commands (~25 lines — grep for try/catch patterns, error responses, security check returns)
- §4 Principles (~50 lines — security checks fail closed; errors don't leak internals; exceptional conditions are designed not improvised; user-facing errors are different from logged errors; partial failures need explicit handling)
- §5 Rule Summaries (~70 lines)
- §6 Anti-Pattern Summaries (~50 lines)
- §7 AI-Specific Concerns (~25 lines — AI generating `catch (e) { return true; }` patterns; AI returning stack traces in error responses; AI defaulting to permissive on partial-failure)
- §8 Workflow Integration (~15 lines)
- §9 Subagent Context (~10 lines)

**Per-skill QC criteria:**
- (a) ≥5 rules covering fail-closed for security checks, sanitized error responses, exceptional condition discipline, partial-failure handling, error correlation IDs for incident response
- (b) ≥8 anti-patterns paired with canonical patterns including swallow-and-allow exception handlers, stack trace exposure, retry loops that bypass security checks
- (c) Cites OWASP Top 10:2025 A10 explicitly (new 2025 category)
- (d) Cross-reference to security-logging (this skill says fail closed and log; logging says what to log how)
- (e) SKILL.md body ≤300 lines

### security-logging

**Scope:** Security event logging discipline; log injection defense; sensitive data scrubbing; structured logging; log evasion awareness (MITRE T1562). Extends SECURITY-CORE Rule 5.7. Maps to OWASP Top 10:2025 A09 (Security Logging and Alerting Failures) and OWASP ASVS 5.0 V16.

**Description (≤500 chars):** "Security logging discipline — capture authn/authz outcomes and security-relevant state changes; scrub secrets and PII; structured logging that resists log injection; awareness of log evasion techniques (MITRE T1562). Use when adding logging to security-relevant code paths, designing log retention, configuring SIEM ingestion, or auditing existing log emissions for leakage. Extends SECURITY-CORE Rule 5.7; aligns with OWASP ASVS 5.0 V16 and OWASP Top 10:2025 A09."

**SKILL.md sections (~260-290 lines):**
- §1 Overview (~30 lines — security logging vs application logging; the centralized log as high-value target)
- §2 Authoritative Sources (~20 lines)
- §3 Discovery Commands (~25 lines — grep for logger.info with sensitive payloads, log structure)
- §4 Principles (~55 lines — structured fields not f-strings; sensitive-field deny-list before logging; authn/authz outcomes always logged; correlation IDs across services; logs are append-only-ish; log retention as compliance scope)
- §5 Rule Summaries (~70 lines)
- §6 Anti-Pattern Summaries (~50 lines)
- §7 AI-Specific Concerns (~25 lines — AI logging request.body wholesale; AI logging response objects with tokens; AI generating `logger.info(\`User \${user}\`)` patterns that interpolate full PII)
- §8 Workflow Integration (~15 lines)
- §9 Subagent Context (~10 lines)

**Per-skill QC criteria:**
- (a) ≥5 rules covering security event capture, sensitive-data scrubbing, log injection defense (structured logging), correlation IDs, log retention discipline
- (b) ≥8 anti-patterns paired with canonical patterns including `logger.info(request.body)`, log injection via unescaped newlines, missing authn/authz event capture
- (c) Hard-refusal AP for logging secrets references SECURITY-CORE AP-5; skill-local AP adds depth on common partial-leakage (logging full user objects, logging response payloads)
- (d) Cross-reference to security-error-handling (this skill says what to log when errors fire)
- (e) SKILL.md body ≤300 lines

### security-secrets-management

**Scope:** Secret lifecycle (creation, distribution, rotation, revocation); scoping; leak detection; integration with secret managers; CI/CD secret discipline. Extends SECURITY-CORE Rule 5.4. Maps to OWASP ASVS 5.0 V11 (key management subsection) + V13 (Configuration), and OWASP Top 10:2025 A02.

**Description (≤500 chars):** "Secret management discipline — lifecycle, rotation, scoping, leak detection, secret manager integration. Use when introducing a new secret, rotating an existing one, configuring CI/CD secret access, setting up a secret manager, or responding to secret leakage. Extends SECURITY-CORE Rule 5.4 with operational depth. Aligns with OWASP ASVS 5.0 V11 + V13, NIST SP 800-57 Part 1 Rev 5, and OWASP Top 10:2025 A02 (Security Misconfiguration)."

**SKILL.md sections (~260-290 lines):**
- §1 Overview (~30 lines — secrets have a lifecycle distinct from code)
- §2 Authoritative Sources (~20 lines)
- §3 Discovery Commands (~25 lines — grep for hardcoded patterns, .env in repo, secrets in CI configs)
- §4 Principles (~55 lines — secrets live in the secret manager; rotate on incident assumption; scope by least privilege; build-time injection not source-embedded; pre-commit detection is necessary not sufficient; rotation runbooks before incidents)
- §5 Rule Summaries (~70 lines)
- §6 Anti-Pattern Summaries (~50 lines)
- §7 AI-Specific Concerns (~25 lines — AI suggesting `.env` commits; AI placeholder values that get hardcoded for testing; AI generating CI configs with inline secrets)
- §8 Workflow Integration (~15 lines)
- §9 Subagent Context (~10 lines)

**Per-skill QC criteria:**
- (a) ≥5 rules covering storage location by environment, rotation cadence + triggers, scoping discipline, leak detection (git-secrets / trufflehog / gitleaks integration), incident response on leak
- (b) ≥8 anti-patterns paired with canonical patterns
- (c) Hard-refusal AP for hardcoded credentials references SECURITY-CORE AP-1; skill-local APs add depth on `.env` commit patterns, CI secret leakage, long-lived static keys
- (d) Cross-reference forward to security-supply-chain for build-time secret injection risks
- (e) SKILL.md body ≤300 lines

### security-supply-chain

**Scope:** Dependency provenance and pinning; transitive dependency risk; SBOM generation; build integrity (SLSA); known-vulnerability monitoring; dependency confusion / typosquatting defense. Maps directly to OWASP Top 10:2025 A03 (Software Supply Chain Failures — new category in 2025).

**Description (≤500 chars):** "Supply chain security discipline — dependency provenance, lockfile discipline, SBOM, build integrity (SLSA), known-vulnerability monitoring, dependency confusion + typosquatting defense. Use when adding a new dependency, configuring CI builds, generating SBOMs, responding to upstream vulnerabilities, or hardening the build pipeline. Maps to OWASP Top 10:2025 A03 (new 2025 category). Aligns with NIST SP 800-218 v1.1 PS.1-PS.3, NIST SP 800-204D, and SLSA v1.0."

**SKILL.md sections (~280-300 lines):**
- §1 Overview (~30 lines — A03 new in 2025 for a reason; supply chain is broad)
- §2 Authoritative Sources (~25 lines)
- §3 Discovery Commands (~25 lines — check lockfile presence, audit tool output, SBOM status)
- §4 Principles (~55 lines — pin to lockfiles; verify before trust; SBOM is operational not theoretical; build provenance via SLSA; transitive risk is real; dependency confusion and typosquatting are active threats)
- §5 Rule Summaries (~75 lines)
- §6 Anti-Pattern Summaries (~55 lines)
- §7 AI-Specific Concerns (~25 lines — AI suggesting packages it can't verify exist; AI adding broad version ranges; AI installing packages without provenance check)
- §8 Workflow Integration (~15 lines)
- §9 Subagent Context (~10 lines)

**Per-skill QC criteria:**
- (a) ≥5 rules covering dependency pinning (lockfile discipline), provenance verification, SBOM generation, vulnerability monitoring + response, dependency confusion / typosquatting defense
- (b) ≥8 anti-patterns paired with canonical patterns including broad version ranges, missing lockfile, no SBOM, no audit step in CI, adding deps without verification
- (c) Cites OWASP Top 10:2025 A03 explicitly (new 2025 category)
- (d) Cross-reference to security-secrets-management for build-time secret injection; cross-reference to CODE-QUALITY Rule on dependency justification
- (e) SKILL.md body ≤300 lines

---

## 5. Implementation Order

Dependency-driven order (later skills can reference earlier ones for cross-skill consistency):

1. **security-input-validation** — pairs naturally with output-encoding; foundational for everything downstream
2. **security-output-encoding** — completes the injection-defense pair (Rules 5.1 + 5.6 in SECURITY-CORE)
3. **security-error-handling** — establishes "fail closed" depth that later skills reference (authn, authz, secrets)
4. **security-cryptography** — foundation for secrets-management (key derivation, randomness) and iam-authentication (password hashing)
5. **security-secrets-management** — depends on cryptography for key handling; bridges to supply-chain (build-time secret injection)
6. **security-iam-authentication** — uses cryptography (password hashing) and secrets-management (credential storage); establishes "who"
7. **security-iam-sessions** — depends on iam-authentication; uses cryptography (token signing) and secrets-management (signing keys)
8. **security-iam-authorization** — depends on iam-authentication + iam-sessions for principal context; the "what can they do" layer
9. **security-database** — references input-validation + output-encoding for SQL parameterization; iam-authorization for RLS; secrets-management for connection credentials
10. **security-logging** — references error-handling (what logs when errors fire); referenced by everything else (this is "what gets captured")
11. **security-supply-chain** — touches everything (every dependency added by every skill); deserves to be last so it can cross-reference all prior

Then closeout: ROADMAP M6 → Complete, CHANGELOG Phase 6 entries, CLAUDE.md §9 updates if any, session log entry, and forward-reference correction in SECURITY-CORE (see Checkpoint 1 Decision C below).

Eleven implementation commits + one closeout = twelve Phase 6 commits.

---

## 6. Universal QC Criteria

Applied to every Phase 6 skill (extending Phase 4/5 criteria; intentions, not numeric targets):

1. **Anchored sections present** per DEC-2026-05-17-003 Clause 1 — every required section has its `<!-- SECTION: name -->` anchor
2. **Internal consistency** — no claim in §5 contradicted in §6
3. **Consistency with framework documents** — no contradictions with CLAUDE.md, ARCHITECTURE.md, WORKFLOW.md, DECISIONS.md, the three Phase 4 always-on skills, or the seven Phase 5 activity skills
4. **Rule-level citation discipline** per DEC-2026-05-17-004 — cite at the source's natural granularity (Checkpoint 1 Decision A elaborates for ASVS 5.0 sub-rules); acknowledge TGF synthesis where no rule-level mapping exists; paywalled/SPA-rendered sources cited by reference per Clause 5
5. **Plain-language impact present** — every rule and anti-pattern explains the practical consequence
6. **Cross-references resolve** — references to other skills, CLAUDE.md sections, DECs are valid; SECURITY-CORE Rule references use the right rule number (5.1–5.7)
7. **No new authoritative claims without source verification** — every rule traces to a verified source or is acknowledged as TGF synthesis; ASVS sub-rule numbers verified live at Stage 1 of each skill's implementation
8. **AI-specific concerns concrete** — references actual MITRE ATLAS / ATT&CK techniques or OWASP LLM Top 10:2025 categories, not generic "AI might be wrong"
9. **Workflow integration accurate** — skill identifies which workflow stages it activates in (per WORKFLOW.md §3); Stage 5 Phase 2 (Security Audit) is the primary activation for all 11 skills
10. **Subagent preload context noted** — Phase 6 skills are generally not preloaded by default; `security-auditor` and `red-team` consult on demand based on Stage 3 plan
11. **SKILL.md body ≤300 lines** — hard ceiling per DEC-2026-05-19-007
12. **Description ≤500 chars** — leaves room in the ~75-skill description budget
13. **SECURITY-CORE extension discipline maintained** per Checkpoint 1 Decision B (below) — Phase 6 skill rules add depth on top of SECURITY-CORE; hard-refusal patterns reference SECURITY-CORE APs without pure restatement
14. **Cross-skill web extended** — each Phase 6 skill cross-references at minimum: SECURITY-CORE (rule extension), DISAGREEMENT (hard-refusal acknowledgment for security severity), TESTING (security-testing dimension), CONTINUITY (waiver/ADR routing for accepted security risks), CODE-QUALITY (solo-maintainability at the security domain), and forward-references to Phase 7 (extended security) where depth lives outside Phase 6 scope

---

## 7. Checkpoint 1 — Decisions Resolved (2026-05-20)

All four decisions resolved. Implementation cleared.

**Decision A — OWASP ASVS 5.0 citation depth for Phase 6 skills: RESOLVED.** Option (iii) Hybrid. Chapter level in §2 Sources tables; sub-rule level in `rules.md` where the mapping is crisp and verifiable in the live ASVS 5.0 source at Stage 1 of each skill's implementation; chapter-level fallback for rules where sub-rule mapping isn't clean. Matches Phase 4 actual practice in SECURITY-CORE. This refines Phase 4 Decision A's "cite at source's natural granularity" principle for the specific case of ASVS 5.0 sub-rules: the source provides sub-rule numbers, but not every TGF rule maps 1:1 to a single sub-rule (some span multiple, some don't have a crisp mapping). Honest mapping over fabricated precision. Stage 1 verification per skill remains the discipline.

**Decision B — SECURITY-CORE rule extension discipline: RESOLVED.** Option (ii) Reference and extend. Phase 6 skill references SECURITY-CORE's rule by ID (e.g., "This skill extends SECURITY-CORE Rule 5.1 with depth on…") and adds skill-specific rules numbered freshly. SECURITY-CORE remains canonical for the universal rules and the CLAUDE.md §5 hard-refusal list; Phase 6 adds depth on top without restating.

Same discipline applies to anti-patterns. The CLAUDE.md §5 hard-refusal list (7 items) maps 1:1 to SECURITY-CORE APs (AP-1 through AP-9). Phase 6 skills naturally re-encounter these patterns (e.g., security-cryptography re-encounters custom crypto + MD5/SHA-1; security-secrets-management re-encounters hardcoded credentials; security-iam-authentication re-encounters disabled authentication middleware).

Operational pattern: Phase 6 hard-refusal APs reference SECURITY-CORE's canonical AP by ID (e.g., "see SECURITY-CORE AP-2 for the custom-crypto hard refusal"). Phase 6 APs cover NON-hard-refusal patterns that SECURITY-CORE didn't cover at depth — for example: security-cryptography AP for AES-ECB misuse, ChaCha20-Poly1305 nonce reuse, GCM tag truncation; security-secrets-management AP for `.env` commits, CI secret leakage in masked log output, long-lived static keys without rotation; security-iam-authentication AP for Argon2id parameter pitfalls, bcrypt cost-factor issues, identity-enumeration via login-response timing. This keeps SECURITY-CORE canonical, makes Phase 6 about extended depth, avoids drift, and respects the reader's navigation (one canonical statement per hard-refusal item).

**Decision C — Forward-reference correction in SECURITY-CORE: RESOLVED.** Option (ii) Correct in Phase 6 closeout commit 12/12. Closeout commit edits SECURITY-CORE `rules.md` to point Phase 6 skills to Phase 6 correctly:

- Rule 5.3 references to `security-cryptography` corrected from "Phase 7" to "Phase 6"
- Rule 5.4 references to `security-secrets-management` and `security-supply-chain` corrected from "Phase 7" to "Phase 6"
- Rule 5.7 references to `security-logging` corrected from "Phase 7" to "Phase 6"
- Any additional Phase 6 forward-references caught during the closeout-time scan get corrected in the same edit

Single bundled edit; doesn't churn SECURITY-CORE incrementally across 11 commits. The SECURITY-CORE skill is the canonical floor — touching it carefully at closeout matches its role.

**Decision D — Commit grouping: RESOLVED.** Option (i) Twelve commits total: eleven implementation commits + closeout. One commit per skill matches Phase 4/5 cadence. Each diff is independently reviewable and revertable. Sequence per the dependency-driven order in §5 above:

1. security-input-validation
2. security-output-encoding
3. security-error-handling
4. security-cryptography
5. security-secrets-management
6. security-iam-authentication
7. security-iam-sessions
8. security-iam-authorization
9. security-database
10. security-logging
11. security-supply-chain
12. Closeout — SECURITY-CORE forward-reference fix per Decision C + ROADMAP + CHANGELOG + CLAUDE.md §9 catalog check + session log

### Architectural reach

None of A–D warranted a new ADR. Decisions A and B are tactical refinements of existing ADRs (Phase 4 Decision A + DEC-2026-05-17-004 Clause 2 for A; DEC-2026-05-19-007 + DEC-2026-05-17-003 Clause 1 for B). Decisions C and D are operational. Plan-file capture is the appropriate record per Phase 4/5 precedent.

If Phase 6+ surfaces systemic implications of the SECURITY-CORE extension discipline (e.g., a need to refactor SECURITY-CORE itself, or a pattern that recurs across Phases 7 / 8 / 9 / 10 warranting a meta-rule about always-on-skill extension), promote to ADR then.

---

## 8. Out of Scope for Phase 6

Confirmed NOT in Phase 6:

- **Phase 7 — Extended Security Skills (22).** CIA triad, architectural cluster, IAM-OAuth-OIDC (RFC 6749 + 6750 + adjacent), data layer (encryption, classification), application (api, webhooks, cors-csp, file-uploads), threat management (threat-modeling, attack-surface), operations (incident-response, detection-monitoring, vulnerability-management), privacy (data-handling, consent). Forward-references from Phase 6 skills to these are expected and acceptable per Phase 4 precedent.
- **Phase 8 — AI-Specific Security Skills (9).** prompt-injection, output-handling, data-poisoning, ai-supply-chain, excessive-agency, sensitive-info, model-governance, research-integrity, adversarial-ai. Forward-references from Phase 6 §7 AI-Specific Concerns sections are expected.
- **Phase 9 — Operations & Quality Skills.** ops-observability covers operational logging depth distinct from security-logging. data-architecture covers schema design + index strategy + query patterns distinct from security-database.
- **Phase 10 — Compliance Regulatory Skills.** GDPR/CCPA/HIPAA/PCI-DSS/SOC2 — load only when PROJECT-CONTEXT scope warrants.
- **Phase 11 — Meta-Skills.** PROJECT-CONTEXT, DOMAIN-RESEARCH, BASELINE-AUDIT, SKILL-FORGE, framework-health.
- **Phase 12 — Hook Library.** Phase 6 may surface candidate hook patterns (e.g., pre-commit secret detection, pre-deploy SBOM check) — capture as future-hook candidates in plan-adjustments at session close, but don't implement them.
- **Phase 13 — Stack Baselines** (LabList / AdaptivIQ / BLETRAP bridge skills).
- **Phase 14 — Slash Commands** beyond what activity skills auto-generate.
- **Phase 15 — Full Documentation.**
- **`settings.json` activation mechanism uncertainty** (carried from Phase 4 closeout). Phase 11 verifies.
- **ARCHITECTURE.md §19 token efficiency minor update** (carried from Phase 4 closeout). Not blocking.
- **Adopter `templates/CLAUDE.md.template` updates** beyond what Phase 6 directly affects.
- **`citations.md` reference file split.** Defer per Phase 4 Checkpoint 1 Decision B until any skill's `rules.md` exceeds ~400 lines.

---

## 9. Effort Estimate

Per skill: ~2-3 hours focused work (Stage 1 source spot-check + SKILL.md draft + reference files + four-pass review + fixes + commit). Phase 6 skills are similar scope to Phase 5 activity skills but with denser per-rule citation work (live verification of ASVS sub-rules at Stage 1 of each skill). Estimate ~250-290 lines SKILL.md + ~180-220 lines rules.md + ~500-700 lines anti-patterns.md per skill.

Eleven skills × ~2.5 hours = ~28 hours focused work.

Closeout: ~1-2 hours (SECURITY-CORE forward-reference correction + ROADMAP + CHANGELOG + CLAUDE.md §9 catalog count check + session log).

Total: ~29-31 hours. Realistically 5-8 sessions over 2-4 weeks part-time.

The Phase 4/5 pattern of one commit per substantive deliverable continues for Phase 6. Eleven focused commits keeps each diff reviewable and lets Checkpoint 1 decisions surface incrementally if anything in implementation pushes back on the plan.

---

## 10. Closing Notes

- This plan is committed (per Phase 2 Decision 2 — transparency before staging)
- Phase 6 implementation does not begin until Decisions A–D are resolved at Checkpoint 1
- Plan adjustments accumulated during implementation will be logged in the Phase 6 session log(s) (per validated Phase 2/3/4/5 pattern)
- Phase 6 inherits the conventions established in Phases 4/5 — reference-file pattern, ≤300 line SKILL.md, citation granularity per source's natural level, TGF synthesis acknowledged honestly, SPA-rendered sources cited by reference (DEC-004 Clause 5), comparative sources per DEC-004 Clause 6 inform examples without becoming authoritative citations
- The dogfooding continues — Phase 6 implementation uses the TGF workflow on its own construction. Stage 5 four-pass review against the now-mature skill set (SECURITY-CORE + DISAGREEMENT + TESTING + DEBUGGING especially) is expected to surface concrete fixes per Phase 4/5 pattern
- **Mid-phase scope amendments** remain legitimate when the user surfaces a real gap (Phase 5 Decision F precedent). If Phase 6 surfaces a gap — e.g., a missing skill domain, a misalignment between Phase 6 and Phase 7 scope, a SECURITY-CORE rule that needs revision — run it through the same workflow rigor as the original plan: alternatives considered, reasoning captured, decision documented in this plan file, commit grouping updated, no new ADR unless architectural reach is genuine
- **Cross-skill web composition is now the framework's emergent value.** Phase 6 should visibly extend that web — every Phase 6 skill cross-references SECURITY-CORE + DISAGREEMENT + TESTING + CONTINUITY + CODE-QUALITY at minimum, plus forward-references to Phase 7 / 8 / 11 where depth lives outside Phase 6 scope. Demonstrating skill composition as the framework's value (not just rule completeness) is the goal
- After Phase 6, Phase 7 (extended security, 22 skills) is the largest remaining single phase by skill count. The Phase 6 conventions established here will set the pattern Phase 7 inherits — getting them right pays dividends across the next ~40 security-and-AI-security skills (Phases 6 + 7 + 8)
