---
# ─── Anthropic-native runtime fields (Claude Code honors these) ───
name: security-output-encoding
description: |
  Context-aware output encoding to defeat injection. Use when emitting
  data to a parsed or interpreted context — SQL queries, HTML markup,
  OS commands, LDAP filters, XML/XPath, URLs, log lines, CSV exports.
  Parameterized queries; auto-escaping templating; argument arrays
  for processes; per-context HTML escape. Extends SECURITY-CORE Rule
  5.6; pairs with security-input-validation as the output-side defense
  for OWASP Top 10:2025 A05 (Injection).
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
  - "**/*.html"
  - "**/*.xml"

# ─── TGF-extension metadata (Phase 11 meta-skills read these; Claude Code ignores) ───
applies-when:
  paths-include:
    - "**/*.{ts,tsx,js,jsx,py,go,rs,rb,java,kt,swift,php,cs,scala,html,xml}"
  operations-include:
    - SQL, NoSQL, GraphQL, Cypher, HQL, or DSL query construction
    - HTML markup rendering (server-side templating or client-side DOM)
    - process spawn / OS command execution
    - LDAP search or DN construction
    - XML parsing or XPath query construction
    - URL construction or outbound URL handling
    - CSV / spreadsheet export generation
    - log line emission with user-controlled content
  data-flows-include:
    - validated data crossing into an interpreter
    - user-controlled content reaching a parsed output context
    - any function emitting data into a syntactic boundary
disqualifying-when:
  - documentation-only changes
  - test fixture additions without production code changes
  - dependency version bumps without code changes
  - pure formatting edits
sources:
  - OWASP ASVS 5.0.0 V1 (Encoding and Sanitization) (verified 2026-05-22)
  - OWASP Top 10:2025 A05 (Injection) (verified Phase 4, 2026-05-20)
  - OWASP Cheat Sheet — Cross Site Scripting Prevention (verified 2026-05-22)
  - OWASP Cheat Sheet — SQL Injection Prevention (verified 2026-05-22)
  - OWASP Cheat Sheet — OS Command Injection Defense (verified 2026-05-22)
  - OWASP Cheat Sheet — LDAP Injection Prevention (verified 2026-05-22)
  - RFC 4515 (LDAP Search Filter String Representation)
  - RFC 4514 (LDAP Distinguished Names String Representation)
  - RFC 4180 (CSV)
  - CWE-79 (XSS), CWE-89 (SQL injection), CWE-78 (OS command injection)
  - CWE-90 (LDAP injection), CWE-611 (XXE), CWE-643 (XPath injection)
  - CWE-117 (Log injection)
last-generated: 2026-05-22
refresh-recommended: 2027-05-22
self-evolution:
  anti-patterns-observed: []
  triggers-refined: []
  ai-failures-documented: []
---

# SECURITY-OUTPUT-ENCODING

> **Skill body ≤300 lines** (per `DEC-2026-05-19-007`). Principles, rule summaries, and navigation live here. Full content in reference files loaded on demand:
> - `rules.md` — full rules with rule-level citations
> - `anti-patterns.md` — full anti-pattern + canonical pattern pairs with code examples

<!-- SECTION: overview -->
## §1 Overview

SECURITY-OUTPUT-ENCODING governs the output side of the injection-defense pair (SECURITY-CORE Rules 5.1 + 5.6). It is a **Phase 6 foundation security skill** that extends SECURITY-CORE Rule 5.6 (*Output Encoding Matches Context*) with operational depth: canonicalize-once-then-encode, per-context HTML escaping, ORM-parameterization verification, argument-array process spawning, RFC-compliant LDAP escaping, and the long-tail of parsed contexts (XML, XPath, CSV, templates, logs).

Per Phase 6 Checkpoint 1 Decision B, this skill **extends** SECURITY-CORE without restating. SECURITY-CORE Rule 5.6 remains canonical for the universal principle (encode at the consuming context, never assemble data into interpreted strings). This skill adds the depth — *which* contexts, *which* encoding, *what AI gets wrong* about each, and the boundary with `security-input-validation` (validation rejects; encoding emits safely). Hard-refusal patterns adjacent to output encoding cite the SECURITY-CORE canonical AP rather than restating.

The input side of injection defense lives in `security-input-validation` (also Phase 6). Together they constitute the layered defense for OWASP Top 10:2025 A05 (Injection). Validation rejects malformed input at the boundary; encoding ensures even well-formed input — including syntactically meaningful characters that legitimately appear in user data — cannot escape its data role at the consuming interpreter.
<!-- /SECTION: overview -->

<!-- SECTION: sources -->
## §2 Authoritative Sources

| Source ID | Reference | Version | Date Verified |
|-----------|-----------|---------|---------------|
| OWASP-ASVS-V1 | [OWASP ASVS 5.0 V1 — Encoding and Sanitization](https://github.com/OWASP/ASVS/blob/master/5.0/en/0x10-V1-Encoding-and-Sanitization.md) | 5.0.0 (released 2025-05-30) | 2026-05-22 |
| OWASP-TOP10 | [OWASP Top 10:2025 A05 (Injection)](https://owasp.org/Top10/2025/) | 2025 | 2026-05-20 (Phase 4) |
| OWASP-CHEAT-XSS | [OWASP Cheat Sheet — Cross Site Scripting Prevention](https://cheatsheetseries.owasp.org/cheatsheets/Cross_Site_Scripting_Prevention_Cheat_Sheet.html) | Current (2026) | 2026-05-22 |
| OWASP-CHEAT-SQLI | [OWASP Cheat Sheet — SQL Injection Prevention](https://cheatsheetseries.owasp.org/cheatsheets/SQL_Injection_Prevention_Cheat_Sheet.html) | Current (2026) | 2026-05-22 |
| OWASP-CHEAT-OSI | [OWASP Cheat Sheet — OS Command Injection Defense](https://cheatsheetseries.owasp.org/cheatsheets/OS_Command_Injection_Defense_Cheat_Sheet.html) | Current (2026) | 2026-05-22 |
| OWASP-CHEAT-LDAP | [OWASP Cheat Sheet — LDAP Injection Prevention](https://cheatsheetseries.owasp.org/cheatsheets/LDAP_Injection_Prevention_Cheat_Sheet.html) | Current (2026) | 2026-05-22 |
| RFC-4515 | [RFC 4515 — LDAP String Representation of Search Filters](https://datatracker.ietf.org/doc/html/rfc4515) | 2006 (current) | 2026-05-22 |
| RFC-4514 | [RFC 4514 — LDAP String Representation of Distinguished Names](https://datatracker.ietf.org/doc/html/rfc4514) | 2006 (current) | 2026-05-22 |
| RFC-4180 | [RFC 4180 — Common Format and MIME Type for CSV Files](https://datatracker.ietf.org/doc/html/rfc4180) | 2005 (current) | 2026-05-22 |
| CWE-79 | [CWE-79 Cross-Site Scripting (XSS)](https://cwe.mitre.org/data/definitions/79.html) | Current | 2026-05-22 |
| CWE-89 | [CWE-89 SQL Injection](https://cwe.mitre.org/data/definitions/89.html) | Current | 2026-05-22 |
| CWE-78 | [CWE-78 OS Command Injection](https://cwe.mitre.org/data/definitions/78.html) | Current | 2026-05-22 |
| CWE-90 | [CWE-90 LDAP Injection](https://cwe.mitre.org/data/definitions/90.html) | Current | 2026-05-22 |
| CWE-611 | [CWE-611 XXE — Improper Restriction of XML External Entity](https://cwe.mitre.org/data/definitions/611.html) | Current | 2026-05-22 |
| CWE-643 | [CWE-643 XPath Injection](https://cwe.mitre.org/data/definitions/643.html) | Current | 2026-05-22 |
| CWE-117 | [CWE-117 Improper Output Neutralization for Logs](https://cwe.mitre.org/data/definitions/117.html) | Current | 2026-05-22 |

Citation granularity per Phase 6 Checkpoint 1 Decision A (hybrid): chapters cited at chapter level in §2; sub-rule level (V1.1.1, V1.2.4, etc.) used in `rules.md` where mapping is crisp and verified live. OWASP Cheat Sheets cited by section name (URL-stable). RFCs at section level where needed. CWE entries by ID + title.
<!-- /SECTION: sources -->

<!-- SECTION: discovery -->
## §3 Discovery Commands

Copy-pasteable commands to capture output-encoding state before applying rules.

```bash
# Find SQL string concatenation / f-string / template-literal patterns
grep -rnE "(SELECT|INSERT|UPDATE|DELETE).*\\\$\{|f['\"](SELECT|INSERT|UPDATE)|\\.format\(.*(SELECT|INSERT)" --include="*.ts" --include="*.js" --include="*.py" 2>/dev/null | head -20

# Find ORM raw-query escape hatches (often parameterization bypass)
grep -rnE "sequelize\.query|\.raw\(|text\(['\"].*WHERE|knex\.raw|\.exec\(['\"]SELECT" --include="*.ts" --include="*.js" --include="*.py" 2>/dev/null | head -20

# Find HTML unsafe sinks (per OWASP XSS Cheat Sheet §Framework Security)
grep -rnE "dangerouslySetInnerHTML|v-html|innerHTML\s*=|bypassSecurityTrust|unsafeHTML|htmlLiteral" --include="*.tsx" --include="*.jsx" --include="*.vue" --include="*.ts" --include="*.js" 2>/dev/null | head -20

# Find shell-string process spawning
grep -rnE "child_process\.exec\(|subprocess.*shell\s*=\s*True|bash\s+-c|sh\s+-c|os\.system\(" --include="*.ts" --include="*.js" --include="*.py" 2>/dev/null | head -20

# Find LDAP filter construction (string concat is the smell)
grep -rnE "ldap.*\(uid=|ldap.*\(cn=|search.*filter.*\+" --include="*.ts" --include="*.js" --include="*.py" --include="*.java" 2>/dev/null | head -20

# Find XML parser defaults (often XXE-enabled)
grep -rnE "xml\.etree|lxml\.etree|DocumentBuilder|SAXParser|XMLReader\.create" --include="*.py" --include="*.java" --include="*.ts" 2>/dev/null | head -20

# Find log lines built with raw user content (CWE-117 surface)
grep -rnE "log(ger)?\.(info|warn|error)\(f['\"]|log(ger)?\.(info|warn|error)\(['\"].*\+ ?(req|user)\." --include="*.py" --include="*.ts" --include="*.js" 2>/dev/null | head -20
```
<!-- /SECTION: discovery -->

<!-- SECTION: principles -->
## §4 Universal Principles

Seven principles grounding the output-encoding discipline. These extend SECURITY-CORE's "encode at the consuming context" with operational depth.

- **Encoding matches the consuming context, not the source.** The same string is HTML-safe, SQL-unsafe, shell-dangerous, and log-injection-vector depending on where it goes. Encoding decisions are made at the output boundary by the code that *emits* into a context, not by the code that *received* the data. Pre-encoding at input is the wrong abstraction (and double-encodes when the data is emitted multiple times).

- **Parameterization over escaping where the API allows it.** SQL drivers, LDAP libraries, XPath engines, and process spawn APIs all provide structured-argument mechanisms that pass data through a separate channel from syntax. Parameterization is the SQL Cheat Sheet's Defense Option 1 for a reason: it removes the encoding decision from the developer. Manual escaping is the discouraged fallback (Defense Option 4 in the SQL Cheat Sheet, explicitly "STRONGLY DISCOURAGED").

- **Use the framework's auto-escape; verify it actually escapes.** Modern frameworks auto-escape HTML by default (React JSX text content, Angular interpolation, Vue mustaches, Jinja2 with autoescape, Django templates). The discipline is using auto-escape and resisting the explicit-bypass APIs (`dangerouslySetInnerHTML`, `v-html`, `bypassSecurityTrustHtml`) — not re-implementing what the framework already does.

- **HTML has five contexts, each requiring different encoding.** Element body (HTML entity encode), HTML attribute (encode quotes, watch unquoted attributes), JavaScript inside `<script>` (Unicode-escape or strict JSON), CSS inside `<style>` (hex-escape per CSS spec), URL inside `href`/`src` (URL-component encode plus protocol allow-list). Manual `str.replace('<', '&lt;')` handles one context and fails the other four.

- **Argument arrays for process spawn; never the shell string.** Every language ships an execFile-style API that passes the command and arguments as separate list elements directly to the OS, bypassing the shell entirely. Shell-string interpolation (`exec(cmd + arg)`, `shell=True`, `bash -c "..."`) reintroduces the shell as an interpreter that re-tokenizes the command — and the attacker controls the tokens.

- **The long-tail contexts deserve the same discipline.** XML parsers default to XXE-enabled in many languages; XPath queries built via concatenation are injectable; CSV exports interpret `=`, `+`, `-`, `@` as formula triggers in spreadsheet software; log lines accept CR/LF that forge new lines; templating engines exposing untrusted-built templates enable server-side template injection. Each is a parsed/interpreted context with its own encoding requirements.

- **Encoding does not validate; validation does not encode.** Validation rejects ill-formed input at the boundary (see `security-input-validation` Rules 5.1–5.7). Encoding emits well-formed input safely into a consuming context. Conflating them — "I sanitized at input so I don't need to escape at output" — leaves the other half of A05:2025 (Injection) open. The two skills together cover the injection class; either alone does not.
<!-- /SECTION: principles -->

<!-- SECTION: rules -->
## §5 Rule Summaries

Seven rules. Each summary: title + 1-line statement + source identifier. This skill extends SECURITY-CORE Rule 5.6 — its canonical statement of *encode at the consuming context* stands as the universal principle; the rules below add the operational depth.

<!-- RULE: 5.1 -->
- **Rule 5.1: Encode at the Interpreter Boundary, Once, in Canonical Form** — Data is decoded to canonical form once on input; encoding for the consuming context happens at output, not pre-stored. Double-encoding and pre-encoded storage both fail. `OWASP-ASVS V1.1.1, V1.1.2` → [`rules.md#rule-51-encode-at-the-interpreter-boundary`](rules.md)
<!-- /RULE: 5.1 -->
<!-- RULE: 5.2 -->
- **Rule 5.2: SQL — Parameterized Queries Always; ORM Parameterization Verified** — Drivers' parameter binding (`?` / `$1` / `:name`) for every query. ORM raw-query escape hatches require the same binding. NoSQL, GraphQL, Cypher, HQL are the same class. `OWASP-ASVS V1.2.4` + `OWASP-CHEAT-SQLI (Defense Option 1)` + `CWE-89` → [`rules.md#rule-52-sql-parameterized-queries`](rules.md)
<!-- /RULE: 5.2 -->
<!-- RULE: 5.3 -->
- **Rule 5.3: HTML — Context-Aware Auto-Escaping; Resist Unsafe Sinks** — Use the framework's auto-escape; the five HTML contexts each require different encoding. Unsafe sinks (`dangerouslySetInnerHTML`, `v-html`, `unsafeHTML`, `bypassSecurityTrustHtml`) need vetted sanitization (DOMPurify, Bleach), never raw user data. `OWASP-ASVS V1.2.1, V1.2.3, V1.3.1` + `OWASP-CHEAT-XSS (§Output Encoding, §HTML Sanitization, §Framework Security)` + `CWE-79` → [`rules.md#rule-53-html-context-aware-escaping`](rules.md)
<!-- /RULE: 5.3 -->
<!-- RULE: 5.4 -->
- **Rule 5.4: URL Construction — Encode per Component; Safe-Protocol Allow-List** — URL components encoded by position (path, query, fragment); outbound URLs validated against a safe-protocol allow-list (`https` / `http`). `javascript:`, `data:`, `file:`, and untrusted absolute redirects are forbidden destinations. `OWASP-ASVS V1.2.2, V1.3.6` + `OWASP-CHEAT-XSS (URL Contexts)` → [`rules.md#rule-54-url-encoding-and-protocol-allow-list`](rules.md)
<!-- /RULE: 5.4 -->
<!-- RULE: 5.5 -->
- **Rule 5.5: OS Process — Argument Arrays via execFile-Style APIs; No Shell-String Interpolation** — Spawn uses structured-argument form (Node `execFile`, Python `subprocess` `shell=False`, Java `ProcessBuilder`, Go `exec.Command`). Shell-string interpolation is forbidden for any caller with untrusted-data influence. `OWASP-ASVS V1.2.5` + `OWASP-CHEAT-OSI (Defense 1 + Defense 3)` + `CWE-78` → [`rules.md#rule-55-os-process-argument-arrays`](rules.md)
<!-- /RULE: 5.5 -->
<!-- RULE: 5.6 -->
- **Rule 5.6: Directory Services — RFC-Compliant LDAP Escaping or Parameterized Libraries** — Filters escape per RFC 4515 (`* ( ) \ NUL`); DNs escape per RFC 4514 (`\ # + < > , ; " =` + leading/trailing space). Prefer parameterized libraries (ESAPI `encodeForLDAP`, .NET `Encoder.LdapFilterEncode`). `OWASP-ASVS V1.2.6` + `OWASP-CHEAT-LDAP` + `CWE-90` → [`rules.md#rule-56-ldap-rfc-escaping`](rules.md)
<!-- /RULE: 5.6 -->
<!-- RULE: 5.7 -->
- **Rule 5.7: Long-Tail Injection Contexts — XML, XPath, CSV, Templates, Logs** — XML parsers disable external-entity resolution; XPath uses variable binding; CSV exports escape formula-leading characters per RFC 4180 §2.6/2.7; templates not built from untrusted input; log lines encode CR/LF/control characters. `OWASP-ASVS V1.5.1, V1.2.7, V1.2.10, V1.3.7` + `CWE-611, CWE-643, CWE-117` → [`rules.md#rule-57-long-tail-injection-contexts`](rules.md)
<!-- /RULE: 5.7 -->

See `rules.md` for full rule text, citations, plain-language impact, and extended discussion.
<!-- /SECTION: rules -->

<!-- SECTION: anti-patterns -->
## §6 Anti-Pattern Summaries

Ten anti-pattern pairs covering the most common output-encoding failures. Per Phase 6 Checkpoint 1 Decision B, hard-refusal patterns adjacent to output encoding (e.g., disabled TLS, custom crypto for encoding) reference SECURITY-CORE's canonical AP without restating; this skill's APs cover the non-hard-refusal depth.

<!-- ANTI-PATTERN: AP-1 -->
- **AP-1: SQL via String Concatenation, f-string, or Template Literal** — `SELECT * FROM users WHERE name = '${name}'` — the canonical SQL injection vector. Violates Rule 5.2. → [`anti-patterns.md#ap-1-sql-string-concatenation`](anti-patterns.md)
<!-- /ANTI-PATTERN: AP-1 -->
<!-- ANTI-PATTERN: AP-2 -->
- **AP-2: ORM "Always Safe" Assumption with Raw-Query Escape Hatch** — `sequelize.query` / `SQLAlchemy.text()` / `Knex.raw()` called with interpolated user input. The ORM doesn't parameterize when you bypass it. Violates Rule 5.2. → [`anti-patterns.md#ap-2-orm-raw-query-escape-hatch`](anti-patterns.md)
<!-- /ANTI-PATTERN: AP-2 -->
<!-- ANTI-PATTERN: AP-3 -->
- **AP-3: `dangerouslySetInnerHTML` / `v-html` / Unsafe Sinks with Untrusted Data** — Framework bypass functions used on user-controlled content without DOMPurify-style sanitization. Violates Rule 5.3. → [`anti-patterns.md#ap-3-html-unsafe-sinks`](anti-patterns.md)
<!-- /ANTI-PATTERN: AP-3 -->
<!-- ANTI-PATTERN: AP-4 -->
- **AP-4: Manual HTML Escape via `str.replace` (Misses Four of Five Contexts)** — Hand-rolled `replace('<', '&lt;').replace('>', '&gt;')` works for element body, fails for attribute/JS/CSS/URL contexts. Violates Rule 5.3. → [`anti-patterns.md#ap-4-manual-html-escape`](anti-patterns.md)
<!-- /ANTI-PATTERN: AP-4 -->
<!-- ANTI-PATTERN: AP-5 -->
- **AP-5: URL via Concat; No Safe-Protocol Allow-List** — `<a href={user.profileUrl}>` accepts `javascript:alert(1)`; `?next=https://evil.com` becomes an open redirect. Violates Rule 5.4. → [`anti-patterns.md#ap-5-url-protocol-bypass`](anti-patterns.md)
<!-- /ANTI-PATTERN: AP-5 -->
<!-- ANTI-PATTERN: AP-6 -->
- **AP-6: Shell-String Spawn (`exec`, `shell=True`, `bash -c`)** — Command + arguments concatenated into a shell-interpreted string with untrusted-influenced content. Violates Rule 5.5. → [`anti-patterns.md#ap-6-shell-string-spawn`](anti-patterns.md)
<!-- /ANTI-PATTERN: AP-6 -->
<!-- ANTI-PATTERN: AP-7 -->
- **AP-7: LDAP Filter Built via String Concatenation** — `(&(uid=${username})(objectClass=person))` — `*)(uid=*` injection bypasses authentication. Violates Rule 5.6. → [`anti-patterns.md#ap-7-ldap-filter-concatenation`](anti-patterns.md)
<!-- /ANTI-PATTERN: AP-7 -->
<!-- ANTI-PATTERN: AP-8 -->
- **AP-8: XML Parser with External-Entity Resolution Enabled (XXE)** — Default-config XML parsers in Python, Java, and Node resolve external DTDs / entities — file read, SSRF, DoS. Violates Rule 5.7. → [`anti-patterns.md#ap-8-xml-xxe-default`](anti-patterns.md)
<!-- /ANTI-PATTERN: AP-8 -->
<!-- ANTI-PATTERN: AP-9 -->
- **AP-9: CSV Formula Injection on Export** — User-supplied fields starting with `=`, `+`, `-`, `@`, `\t`, `\0` exported to CSV; opened in Excel / Google Sheets and interpreted as formula. Violates Rule 5.7. → [`anti-patterns.md#ap-9-csv-formula-injection`](anti-patterns.md)
<!-- /ANTI-PATTERN: AP-9 -->
<!-- ANTI-PATTERN: AP-10 -->
- **AP-10: Log Injection via Unencoded CR/LF in User-Controlled Log Content** — `log.info(f"user {username} logged in")` accepting `\nINFO: admin promoted` forges log entries (CWE-117). Violates Rule 5.7. → [`anti-patterns.md#ap-10-log-injection`](anti-patterns.md)
<!-- /ANTI-PATTERN: AP-10 -->

Per `DEC-2026-05-17-003` Clause 1: every anti-pattern is paired with a canonical pattern in `anti-patterns.md`.
<!-- /SECTION: anti-patterns -->

<!-- SECTION: ai-concerns -->
## §7 AI-Specific Concerns

Output-encoding failure modes specific to AI-generated code and AI-integrated systems.

- **"First query parameterized, next one isn't."** AI generates the first SQL query with parameter binding (the prompt asked for it), then drops parameterization on subsequent queries in the same file when the developer asks for "a quick lookup." The pattern is consistency-of-discipline failure, not knowledge failure. Defense: Rule 5.2's universal-application discipline; grep at Stage 5 Phase 2 for any concat-style SQL in changed files.

- **HTML built via template literals + `dangerouslySetInnerHTML`.** AI generates UI code that assembles HTML via template literals and passes the result through `dangerouslySetInnerHTML` (or framework equivalents) because the prompt asked for "rich content" or "custom rendering." The bypass is invisible to surface-read; the API name is the signal. Defense: Rule 5.3 + AP-3 — `dangerouslySetInnerHTML` requires sanitization via DOMPurify or rejection of the pattern.

- **`subprocess.run(..., shell=True)` for "convenience."** Python AI code defaults to `shell=True` because it produces a one-line solution that works for the developer's test command. The default re-introduces the shell as an interpreter. Defense: Rule 5.5 + AP-6 — argument-list form is the only correct form for any caller with untrusted-data influence.

- **Concatenating user input into log lines.** AI generates structured logging that looks careful (`log.info(f"User {user.id} action {action}")`) but accepts raw `user.id` / `action` strings. CRLF in either value forges new log entries. Defense: Rule 5.7 + AP-10 — encode user-controlled values via the logger's structured-field API or explicit CR/LF stripping.

- **XML parsed with library defaults.** AI uses `lxml.etree.fromstring(data)` or Java `DocumentBuilder` defaults without hardening — many of these defaults resolve external entities. Defense: Rule 5.7 + AP-8 — explicit parser configuration (`resolve_entities=False`, `setFeature(... false)`) per language.

- **"The framework escapes by default" used as universal justification.** AI assumes auto-escape covers all five HTML contexts because it covers the common one (element text). Auto-escape works for the text content; the developer still controls attribute construction, inline script context, CSS context, and URL context. Defense: Rule 5.3's enumeration of all five contexts; grep for attribute construction patterns (`${user.foo}` inside HTML attributes).

Relevant external taxonomies: `OWASP-LLM LLM05:2025` (Improper Output Handling — when LLM output reaches downstream interpreters); `MITRE-ATLAS` AML.T0051; `CWE-79`, `CWE-89`, `CWE-78`, `CWE-90`, `CWE-611`, `CWE-643`, `CWE-117`.
<!-- /SECTION: ai-concerns -->

<!-- SECTION: workflow -->
## §8 Workflow Integration

How SECURITY-OUTPUT-ENCODING participates in the six-stage workflow and four-pass review (per `docs/WORKFLOW.md`).

- **Stage 1 (Research):** Run the §3 discovery commands when the change emits data to a parsed context (SQL query, HTML render, process spawn, LDAP query, XML parse, URL construction, CSV export, log line). Map existing encoding patterns before adding new ones.
- **Stage 3 (Plan with Governance):** Contribute Rules 5.1–5.7 when the change emits data to a new interpreter or extends an existing one. Pair with `security-input-validation` on changes that touch both input and output sides.
- **Stage 4 (Implement):** Apply rules during writing — parameterized queries always; framework auto-escape with unsafe-sink discipline; argument-array process spawn; RFC-compliant LDAP escape or library; hardened XML parser; CSV formula-leading escape; logger structured-field API.
- **Stage 5 Phase 2 (Security Audit):** Primary skill — all rules in scope. Findings on AP-1 (SQL concat), AP-3 (unsafe HTML sinks), AP-6 (shell-string spawn), AP-8 (XXE) are typically High or Critical severity.
- **Stage 5 Phase 3 (Red Team):** Probe output boundaries adversarially — encoding gaps per context, mixed-context emissions (data crosses HTML→JS or HTML→CSS), shell-string fallbacks, XXE / SSRF via URL allow-list bypass. Consult `security-input-validation` for the input-side defense pair.
- **Stage 5 Phase 4 (Holistic Review):** Verify the output-encoding discipline is coherent — no regression in adjacent output boundaries, no manual-escape patterns reintroduced where framework auto-escape exists, no mixing of input-sanitize and output-encode responsibilities.
- **Stage 6 (Commit):** Critical / High findings get fixed before commit. Medium findings get fixed, waived in `WAIVER-LOG.md` per CONTINUITY Rule 5.3 with rationale and revisit date, or escalated to `VENDOR-LOG.md` if requiring out-of-codebase action (e.g., legacy interpreter that can't be replaced).
<!-- /SECTION: workflow -->

<!-- SECTION: subagent-context -->
## §9 Subagent Context

**Preloaded by:** None by default. Phase 6 foundation security skills are not preloaded into the existing four review subagents (per Phase 4 agent definitions). `security-auditor` and `red-team` consult this skill on demand based on Stage 3's plan when the change touches an output boundary. Phase 11 (Meta-Skills) may revise subagent skill mappings.

**Critical rules for review use (when consulted but not preloaded):**

- Rule 5.2 (SQL Parameterized Queries Always)
- Rule 5.3 (HTML Context-Aware Auto-Escaping)
- Rule 5.5 (OS Process Argument Arrays)
- Rule 5.6 (LDAP RFC Escaping)
- Rule 5.7 (Long-Tail Injection Contexts — XML/XPath/CSV/Templates/Logs)

**Top AI-specific concerns:**

- "First query parameterized, next one isn't" — discipline-drift after the first compliant query
- `dangerouslySetInnerHTML` / `v-html` with template-literal HTML
- `subprocess.run(..., shell=True)` for "convenience"

**Cross-skill web:**

- Extends SECURITY-CORE Rule 5.6 (universal floor; this skill adds depth)
- Pairs with `security-input-validation` (input side of injection defense; OWASP A05:2025)
- Forwards to `security-database` for ORM-specific parameterization patterns and RLS-layer defenses
- Forwards to `security-api` (Phase 7) for HTTP-response encoding specifics
- Forwards to `security-logging` (Phase 6) for log-line discipline beyond CWE-117 (sensitive-data scrubbing, structured logging)
- Forwards to `security-cors-csp` (Phase 7) for browser-layer XSS defense-in-depth (CSP)
- Forwards to `security-ai-output-handling` (Phase 8) for LLM-output reaching downstream interpreters
- DISAGREEMENT Rule 5.2 routes severity for findings raised here (typically standard-to-strong advocacy at output boundaries reaching interpreters with side effects)
- TESTING covers the security-testing dimension (OWASP WSTG injection chapters, fuzz testing)
- CONTINUITY Rule 5.3 routes waivers for output-encoding gaps that can't be fully implemented this commit
- CODE-QUALITY Rule on solo-maintainability informs framework-default reliance over hand-rolled escape

Reference files (`rules.md`, `anti-patterns.md`) load on demand within the consulting subagent.
<!-- /SECTION: subagent-context -->
