---
# ─── Anthropic-native runtime fields (Claude Code honors these) ───
name: security-input-validation
description: |
  Boundary input validation. Use when accepting external input — HTTP
  request bodies, query parameters, headers, file content, third-party
  API responses, message queue payloads, deserialized data, LLM tool
  input. Schema-first validation that rejects on shape mismatch;
  sanitization belongs at output (see security-output-encoding).
  Extends SECURITY-CORE Rule 5.1. Aligns with OWASP ASVS 5.0 V2 + V4
  and OWASP Top 10:2025 A05 (Injection).
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
    - HTTP request body, query parameter, or header parsing
    - file upload content parsing
    - third-party API response parsing
    - message queue or webhook payload handling
    - deserialization (JSON, YAML, XML, pickle, msgpack)
    - LLM tool-input or retrieved-context handling
    - any function whose signature includes untrusted external input
  data-flows-include:
    - untrusted input crossing into application code
    - external data crossing trust boundary
    - LLM-bound input crossing into model context
disqualifying-when:
  - documentation-only changes
  - test fixture additions without production code changes
  - dependency version bumps without code changes
  - pure formatting edits
sources:
  - OWASP ASVS 5.0.0 V2 (Validation and Business Logic) (verified 2026-05-20)
  - OWASP ASVS 5.0.0 V4 (API and Web Service) (verified 2026-05-20)
  - OWASP Top 10:2025 A05 (Injection) (verified Phase 4, 2026-05-20)
  - OWASP Cheat Sheet — Input Validation (verified 2026-05-20)
  - OWASP Top 10 for LLM Applications 2025 — LLM01:2025 (verified Phase 2, 2026-05-17)
  - NIST SP 800-218 v1.1 (SSDF) — PW.5 (verified Phase 2)
  - CWE-20 Improper Input Validation
  - CWE-1287 Improper Validation of Specified Type of Input
last-generated: 2026-05-20
refresh-recommended: 2027-05-20
self-evolution:
  anti-patterns-observed: []
  triggers-refined: []
  ai-failures-documented: []
---

# SECURITY-INPUT-VALIDATION

> **Skill body ≤300 lines** (per `DEC-2026-05-19-007`). Principles, rule summaries, and navigation live here. Full content in reference files loaded on demand:
> - `rules.md` — full rules with rule-level citations
> - `anti-patterns.md` — full anti-pattern + canonical pattern pairs with code examples

<!-- SECTION: overview -->
## §1 Overview

SECURITY-INPUT-VALIDATION governs the input side of the injection-defense pair (Rules 5.1 + 5.6 in SECURITY-CORE). It is a **Phase 6 foundation security skill** that extends SECURITY-CORE Rule 5.1 (*Validate Input at Trust Boundaries*) with operational depth: schema-first declaration, positive validation over block-lists, reject-don't-sanitize discipline, combined-data consistency checks, server-side mandatory, and LLM-input-as-untrusted.

Per Phase 6 Checkpoint 1 Decision B, this skill **extends** SECURITY-CORE without restating. SECURITY-CORE Rule 5.1 remains canonical for the universal principle (validate at boundaries, not in business logic). This skill adds the depth — *how* to validate, *what* the discipline looks like in practice, and *what AI gets wrong* about it. Hard-refusal patterns adjacent to input validation (e.g., disabled validation on auth-handling endpoints) cite the SECURITY-CORE canonical AP rather than restating.

The output side of injection defense lives in `security-output-encoding` (also Phase 6). Together they constitute the layered defense for OWASP Top 10:2025 A05 (Injection). Validation rejects malformed input at the boundary; encoding ensures even well-formed input cannot escape its data role at the output context. Confusing the two — sanitizing at input, validating at output — is one of the most common AI failure modes this skill addresses.
<!-- /SECTION: overview -->

<!-- SECTION: sources -->
## §2 Authoritative Sources

| Source ID | Reference | Version | Date Verified |
|-----------|-----------|---------|---------------|
| OWASP-ASVS-V2 | [OWASP ASVS 5.0 V2 — Validation and Business Logic](https://github.com/OWASP/ASVS/blob/master/5.0/en/0x11-V2-Validation-and-Business-Logic.md) | 5.0.0 (released 2025-05-30) | 2026-05-20 |
| OWASP-ASVS-V4 | [OWASP ASVS 5.0 V4 — API and Web Service](https://github.com/OWASP/ASVS/blob/master/5.0/en/0x13-V4-API-and-Web-Service.md) | 5.0.0 | 2026-05-20 |
| OWASP-TOP10 | [OWASP Top 10:2025 A05 (Injection)](https://owasp.org/Top10/2025/) | 2025 | 2026-05-20 (Phase 4) |
| OWASP-CHEAT-IV | [OWASP Cheat Sheet — Input Validation](https://cheatsheetseries.owasp.org/cheatsheets/Input_Validation_Cheat_Sheet.html) | Current (2026) | 2026-05-20 |
| OWASP-LLM | [OWASP Top 10 for LLM Applications 2025 — LLM01:2025 Prompt Injection](https://genai.owasp.org/llm-top-10/) | 2025 | 2026-05-17 (Phase 2) |
| NIST-SSDF | [NIST SP 800-218 v1.1 (SSDF) PW.5 — Create Source Code Adhering to Secure Coding Practices](https://csrc.nist.gov/pubs/sp/800/218/final) | v1.1 | 2026-05-20 |
| CWE-20 | [CWE-20 Improper Input Validation](https://cwe.mitre.org/data/definitions/20.html) | Current | 2026-05-20 |
| CWE-1287 | [CWE-1287 Improper Validation of Specified Type of Input](https://cwe.mitre.org/data/definitions/1287.html) | Current | 2026-05-20 |

Citation granularity per Phase 6 Checkpoint 1 Decision A (hybrid): chapters cited at chapter level in §2; sub-rule level (V2.2.1, V2.2.2, V2.2.3 etc.) used in `rules.md` where mapping is crisp and verified live. OWASP Top 10:2025 cited at category level. NIST SSDF at practice level (PW.5). CWE entries cited by ID + title. OWASP Cheat Sheet content informs operational guidance and is cited by section name (which is stable over time even if Cheat Sheet text revises).
<!-- /SECTION: sources -->

<!-- SECTION: discovery -->
## §3 Discovery Commands

Copy-pasteable commands to capture input-validation state before applying rules.

```bash
# Find HTTP body parsing without schema validation (Node.js / TypeScript)
grep -rnE "req\.body\.[a-zA-Z_]+|request\.json\(\)" --include="*.ts" --include="*.js" --include="*.py" 2>/dev/null | head -20

# Find permissive deserialization candidates
grep -rnE "pickle\.loads|yaml\.load\b|JSON\.parse\(.*req" --include="*.py" --include="*.ts" --include="*.js" 2>/dev/null | head -20

# Find block-list-style validation (incomplete by nature)
grep -rnE "(replace|sanitize).*['\"]<['\"]|input\.includes\(['\"]<|strip_tags|escape_html.*input" --include="*.ts" --include="*.js" --include="*.py" 2>/dev/null | head -20

# Find existing schema validation usage (good signal — confirm coverage)
grep -rnE "(zod|joi|yup|pydantic|marshmallow|jsonschema)" --include="*.ts" --include="*.js" --include="*.py" 2>/dev/null | head -20

# Find client-side-only-validation candidates (HTML forms with no server handler validation)
grep -rnE "<input.*required|<input.*pattern=" --include="*.html" --include="*.tsx" --include="*.jsx" 2>/dev/null | head -20

# LLM tool-input handling (Phase 8 cross-reference)
grep -rnE "tool_call|function_call|tool_input" --include="*.py" --include="*.ts" 2>/dev/null | head -20
```
<!-- /SECTION: discovery -->

<!-- SECTION: principles -->
## §4 Universal Principles

Seven principles grounding the input-validation discipline. These extend SECURITY-CORE's "validate at trust boundaries; encode at output context" principle with operational depth.

- **Validate where input enters; not where it's eventually used.** A trust boundary is the seam between context the application controls and context it does not. Validate at the seam — HTTP route handler, message queue consumer, deserialization point — not three layers deep in business logic. Once unvalidated data has spread, the trail back to "the boundary didn't validate" is lost and the failure surfaces somewhere distant.

- **Schema-first; reject on shape mismatch.** Declare the expected shape explicitly via a validation library (zod, pydantic, joi, json-schema, yup, marshmallow). The schema is the contract: required fields, optional fields, types, ranges, enums, regex patterns. Inputs that don't match the schema get rejected with a clear error (HTTP 400) — not coerced, not silently accepted, not stripped.

- **Positive validation (allow-list) over negative validation (block-list).** Allow only what you know is good; reject everything else. Block-lists ("strip these dangerous characters") are incomplete by nature — every encoding evasion, Unicode normalization quirk, or context-shifting trick breaks them. Allow-lists fail closed: if the input doesn't match the permitted format, it's rejected regardless of what novel attack the attacker invented.

- **Reject — don't sanitize — at the input boundary.** Sanitization is the wrong abstraction at input. "Cleaning" bad input into something acceptable assumes you know every way input can be bad; you don't. Validation rejects what isn't allow-listed; sanitization (when genuinely needed, e.g., HTML rendering of user-generated content) happens at the *output* context where the consuming format dictates the encoding — handled by `security-output-encoding`.

- **Validate combinations, not just fields.** Per-field validation catches "this isn't an integer." Cross-field validation catches "start_date is after end_date," "ZIP code doesn't match the country," "the state machine doesn't allow this transition." Real business logic constraints live in combinations; per-field schemas are necessary but not sufficient.

- **Server-side validation is the security control; client-side is UX.** Client-side validation (form `required`, `pattern`, JS guards) exists for user experience — fast feedback, prevents wasted round-trips. It is not a security control because the attacker controls the client. Server re-validates everything regardless of what the client claims to have checked.

- **LLM input is untrusted input.** Input reaching an LLM — prompt content, tool arguments, retrieved context — is potential prompt injection (`LLM01:2025`). Validate structure, bound length, and constrain to expected schemas before the LLM consumes it. Tool outputs from the LLM are *also* untrusted before downstream code acts on them (depth in `security-ai-prompt-injection` Phase 8 and `security-ai-output-handling` Phase 8).
<!-- /SECTION: principles -->

<!-- SECTION: rules -->
## §5 Rule Summaries

Seven rules. Each summary: title + 1-line statement + source identifier. This skill extends SECURITY-CORE Rule 5.1 — its canonical statement of *validate at trust boundaries* stands as the universal principle; the rules below add the operational depth.

<!-- RULE: 5.1 -->
- **Rule 5.1: Validate at the Trust Boundary, Not Inside Business Logic** — Validation happens at the HTTP route handler, message queue consumer, or deserialization point — not in services after data has spread inward. Extends SECURITY-CORE Rule 5.1. `OWASP-ASVS V2.2.2` (trusted service layer) → [`rules.md#rule-51-validate-at-the-trust-boundary`](rules.md)
<!-- /RULE: 5.1 -->
<!-- RULE: 5.2 -->
- **Rule 5.2: Schema-First Declaration; Validate Shape Before Use** — Declare expected shape via an explicit schema (zod / pydantic / joi / json-schema). Validation rejects inputs that don't match shape; consumers downstream get type-guaranteed data. `OWASP-ASVS V2.1.1, V2.2.1` + `CWE-1287` → [`rules.md#rule-52-schema-first-declaration`](rules.md)
<!-- /RULE: 5.2 -->
<!-- RULE: 5.3 -->
- **Rule 5.3: Positive Validation (Allow-List) over Negative Validation (Block-List)** — Define what is allowed; reject everything else. Block-lists ("strip these characters") are incomplete by nature against novel encoding tricks. `OWASP-ASVS V2.2.1` + `OWASP-CHEAT-IV (Input Validation Strategies)` → [`rules.md#rule-53-positive-validation-over-block-list`](rules.md)
<!-- /RULE: 5.3 -->
<!-- RULE: 5.4 -->
- **Rule 5.4: Reject — Don't Sanitize — at the Input Boundary** — Validation rejects malformed input. Sanitization belongs at the output context (handled by `security-output-encoding`); conflating the two creates injection. `OWASP-CHEAT-IV` + `TGF synthesis` (separation of validation from encoding per SECURITY-CORE Rules 5.1 + 5.6) → [`rules.md#rule-54-reject-dont-sanitize`](rules.md)
<!-- /RULE: 5.4 -->
<!-- RULE: 5.5 -->
- **Rule 5.5: Validate Combined Data for Logical Consistency** — Beyond per-field schemas, validate cross-field invariants (date ranges, geographic consistency, state-machine transitions, business-logic limits). `OWASP-ASVS V2.1.2, V2.2.3, V2.3.1` → [`rules.md#rule-55-validate-combined-data`](rules.md)
<!-- /RULE: 5.5 -->
<!-- RULE: 5.6 -->
- **Rule 5.6: Server-Side Validation is Mandatory; Client-Side is UX** — Client-side validation is for user experience; the server re-validates regardless. The attacker controls the client. `OWASP-CHEAT-IV (Client-side vs Server-side)` → [`rules.md#rule-56-server-side-mandatory`](rules.md)
<!-- /RULE: 5.6 -->
<!-- RULE: 5.7 -->
- **Rule 5.7: Treat LLM Input as Untrusted; Validate and Bound Before Use** — Input reaching an LLM (prompts, tool args, retrieved context) is potential prompt injection; validate structure, bound length, constrain to schemas. Defends against `LLM01:2025`. Depth in `security-ai-prompt-injection` (Phase 8). `OWASP-LLM LLM01:2025` + `TGF synthesis` → [`rules.md#rule-57-llm-input-untrusted`](rules.md)
<!-- /RULE: 5.7 -->

See `rules.md` for full rule text, citations, plain-language impact, and extended discussion.
<!-- /SECTION: rules -->

<!-- SECTION: anti-patterns -->
## §6 Anti-Pattern Summaries

Nine anti-pattern pairs covering the most common input-validation failures. Per Phase 6 Checkpoint 1 Decision B, hard-refusal patterns adjacent to input validation (e.g., disabled authentication middleware) reference SECURITY-CORE's canonical AP without restating; this skill's APs cover the non-hard-refusal depth.

<!-- ANTI-PATTERN: AP-1 -->
- **AP-1: Validation Inside Business Logic, Not at Boundary** — Schema check happens four layers deep in a service after data has propagated. Violates Rule 5.1. → [`anti-patterns.md#ap-1-validation-inside-business-logic`](anti-patterns.md)
<!-- /ANTI-PATTERN: AP-1 -->
<!-- ANTI-PATTERN: AP-2 -->
- **AP-2: Permissive Field Acceptance (Accept-If-Present)** — `if (req.body.email) { ... }` — no shape check, no length cap, no format check. Violates Rule 5.2. → [`anti-patterns.md#ap-2-permissive-field-acceptance`](anti-patterns.md)
<!-- /ANTI-PATTERN: AP-2 -->
<!-- ANTI-PATTERN: AP-3 -->
- **AP-3: Block-List Approach to "Dangerous Characters"** — `input.replace(/<script>/gi, '')` — incomplete; encoding tricks bypass. Violates Rule 5.3. → [`anti-patterns.md#ap-3-block-list-validation`](anti-patterns.md)
<!-- /ANTI-PATTERN: AP-3 -->
<!-- ANTI-PATTERN: AP-4 -->
- **AP-4: Sanitization at Input Boundary** — Stripping tags / "cleaning" at input rather than rejecting on schema mismatch. Conflates validation with encoding. Violates Rule 5.4. → [`anti-patterns.md#ap-4-sanitization-at-input`](anti-patterns.md)
<!-- /ANTI-PATTERN: AP-4 -->
<!-- ANTI-PATTERN: AP-5 -->
- **AP-5: Client-Side-Only Validation** — Form validates with JS; server accepts whatever arrives. Curl bypasses immediately. Violates Rule 5.6. → [`anti-patterns.md#ap-5-client-side-only-validation`](anti-patterns.md)
<!-- /ANTI-PATTERN: AP-5 -->
<!-- ANTI-PATTERN: AP-6 -->
- **AP-6: Validating One Layer Deep, Trusting Nested Structure** — Top-level body checked; nested objects (arrays, maps) assumed valid. Violates Rules 5.1 + 5.2. → [`anti-patterns.md#ap-6-shallow-validation`](anti-patterns.md)
<!-- /ANTI-PATTERN: AP-6 -->
<!-- ANTI-PATTERN: AP-7 -->
- **AP-7: Missing Combined-Data Consistency Check** — Per-field valid, combination nonsensical (start > end; ZIP doesn't match country; state-machine skipped). Violates Rule 5.5. → [`anti-patterns.md#ap-7-missing-combined-check`](anti-patterns.md)
<!-- /ANTI-PATTERN: AP-7 -->
<!-- ANTI-PATTERN: AP-8 -->
- **AP-8: Permissive Deserialization** — `pickle.loads(request.body)` or `yaml.load(...)` without schema — accepts arbitrary structure (and code, in pickle's case). Violates Rules 5.2 + 5.4. → [`anti-patterns.md#ap-8-permissive-deserialization`](anti-patterns.md)
<!-- /ANTI-PATTERN: AP-8 -->
<!-- ANTI-PATTERN: AP-9 -->
- **AP-9: LLM Input Treated as Trusted** — User-supplied input fed directly into LLM prompt or tool arguments without validation or length bounds. Violates Rule 5.7; enables `LLM01:2025` prompt injection. → [`anti-patterns.md#ap-9-llm-input-trusted`](anti-patterns.md)
<!-- /ANTI-PATTERN: AP-9 -->

Per `DEC-2026-05-17-003` Clause 1: every anti-pattern is paired with a canonical pattern in `anti-patterns.md`.
<!-- /SECTION: anti-patterns -->

<!-- SECTION: ai-concerns -->
## §7 AI-Specific Concerns

Input-validation failure modes specific to AI-generated code and AI-integrated systems.

- **Permissive defaults.** AI defaults to permissive validation ("accept this if it has the field") because permissive code "works" against happy-path test cases and minimizes friction in the prompt-response loop. AI also tends to skip validation entirely when the prompt didn't explicitly request it. Defense: Rule 5.2's schema-first discipline; explicit schemas are the contract that catches this. Surface in Stage 5 Phase 2 review by grepping changed code for unguarded `req.body.field` access patterns.

- **Sanitization confused with validation.** AI training data over-represents 2010s-era patterns where "sanitize user input" was the prevailing framing. AI generates `input.replace(/<script>/gi, '')`-style block-lists that look defensive but are inadequate against modern attacks. Defense: Rule 5.4 — explicit separation of *reject at input* from *encode at output*.

- **Block-list confidence.** AI generates extensive block-lists of "dangerous characters" with a comment claiming completeness. The block-list misses Unicode normalization, encoding evasions, and context-shifting tricks because no block-list can be complete. Defense: Rule 5.3 — positive validation is the only complete approach.

- **Shallow validation in nested structures.** AI validates the top-level object but treats nested arrays / maps / sub-objects as already-validated. The shape "matched" so all of it must be safe. Defense: Rule 5.2's schema-first discipline includes recursive nested-shape validation; libraries like zod and pydantic handle this if asked.

- **Coercion-friendly libraries used as validation.** AI uses `parseInt(input)` or JavaScript's `Number()` as "validation" — these accept "123abc" as 123, "true" as truthy, empty string as 0. They are coercion, not validation. Defense: strict schema libraries reject on coercion; AI's `Number(input)` patterns surface in review.

- **LLM input treated as trusted because "the user is authenticated."** AI generates flows where authenticated user input passes directly to an LLM tool call or prompt. Authentication says *who* the user is; it does not vouch for *what they typed*. Defense: Rule 5.7 — LLM input is untrusted regardless of auth state; validate structure + bound length + constrain to schemas.

Relevant external taxonomies: `OWASP-LLM LLM01:2025` (Prompt Injection); `MITRE-ATLAS` AML.T0051 (LLM Output Handling failures, applicable when LLM tool outputs become downstream input); `CWE-20` (Improper Input Validation); `CWE-1287` (Improper Validation of Specified Type).
<!-- /SECTION: ai-concerns -->

<!-- SECTION: workflow -->
## §8 Workflow Integration

How SECURITY-INPUT-VALIDATION participates in the six-stage workflow and four-pass review (per `docs/WORKFLOW.md`).

- **Stage 1 (Research):** Run the §3 discovery commands when the change touches an input boundary (route handler, queue consumer, deserialization, LLM tool wiring). Map existing validation patterns before adding new ones.
- **Stage 3 (Plan with Governance):** Contribute Rules 5.1–5.7 when the change introduces a new input boundary or extends an existing one. Forward-reference to `security-output-encoding` for the paired output side.
- **Stage 4 (Implement):** Apply rules during writing — declare schema before parsing; validate at the boundary; reject on shape mismatch with HTTP 400 (or equivalent for non-HTTP contexts).
- **Stage 5 Phase 2 (Security Audit):** Primary skill — all rules in scope. Findings on AP-1 (validation inside business logic), AP-5 (client-side-only), and AP-8 (permissive deserialization) are typically High or Critical severity.
- **Stage 5 Phase 3 (Red Team):** Probe input boundaries adversarially — schema gaps, nested-structure trust, coercion bypasses, LLM prompt injection vectors. Consult `security-output-encoding` for the encode-side defense.
- **Stage 5 Phase 4 (Holistic Review):** Verify the input-validation discipline is coherent with the change's surrounding patterns — no regression in adjacent input boundaries, no drift between schema declaration and downstream consumers' assumptions, no introduction of new client-trust pattern.
- **Stage 6 (Commit):** Critical / High findings get fixed before commit. Medium findings get fixed, waived in `WAIVER-LOG.md` per CONTINUITY Rule 5.3 with rationale and revisit date, or escalated to `VENDOR-LOG.md` if requiring out-of-codebase action (e.g., third-party API contract change).
<!-- /SECTION: workflow -->

<!-- SECTION: subagent-context -->
## §9 Subagent Context

**Preloaded by:** None by default. Phase 6 foundation security skills are not preloaded into the existing four review subagents (per Phase 4 agent definitions). `security-auditor` and `red-team` consult this skill on demand based on Stage 3's plan when the change touches an input boundary. Phase 11 (Meta-Skills) may revise subagent skill mappings.

**Critical rules for review use (when consulted but not preloaded):**

- Rule 5.1 (Validate at the Trust Boundary, Not Inside Business Logic)
- Rule 5.2 (Schema-First Declaration)
- Rule 5.3 (Positive Validation over Block-List)
- Rule 5.4 (Reject, Don't Sanitize at Input)
- Rule 5.7 (LLM Input as Untrusted)

**Top AI-specific concerns:**

- Permissive defaults (accept-if-present without schema)
- Sanitization confused with validation (block-list replace patterns)
- LLM input treated as trusted because user is authenticated

**Cross-skill web:**

- Extends SECURITY-CORE Rule 5.1 (universal floor; this skill adds depth)
- Pairs with `security-output-encoding` (output side of injection defense; OWASP A05:2025)
- Forwards to `security-database` for SQL parameterization specifics (output-side at the database boundary)
- Forwards to `security-api` (Phase 7) for HTTP-level depth (ASVS V4)
- Forwards to `security-file-uploads` (Phase 7) for file-content validation (ASVS V5)
- Forwards to `security-ai-prompt-injection` (Phase 8) for LLM-input depth
- DISAGREEMENT Rule 5.2 routes severity for findings raised here (typically standard-to-strong advocacy at input boundaries handling user data)
- TESTING covers the security-testing dimension (OWASP WSTG input-validation chapters, fuzz testing)
- CONTINUITY Rule 5.3 routes waivers for input-validation gaps that can't be fully implemented this commit
- CODE-QUALITY Rule on solo-maintainability informs schema readability

Reference files (`rules.md`, `anti-patterns.md`) load on demand within the consulting subagent.
<!-- /SECTION: subagent-context -->
