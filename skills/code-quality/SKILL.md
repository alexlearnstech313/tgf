---
# ─── Anthropic-native runtime fields (Claude Code honors these) ───
name: code-quality
description: |
  Engineering discipline and craftsmanship rules for production code. Use when
  reviewing or writing code that should be maintainable, scale-aware, and clear
  six months later. Applies to: type safety at boundaries, explicit error
  handling, intent-revealing names, comment discipline (WHY not WHAT),
  scale-aware defaults, and solo-maintainability. Pairs with security-core for
  security-relevant code quality.
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
    - function or method definition added or modified
    - error handling added at I/O, parsing, or third-party call sites
    - query or persistence operation added
    - dependency added or version-bumped
    - public API surface defined or modified
  data-flows-include:
    - external input crossing into application code
    - persistence layer crossing application boundary
disqualifying-when:
  - documentation-only changes
  - test fixture additions without production code changes
  - dependency version bumps without code changes
  - formatting-only edits (whitespace, comment reflows)
sources:
  - NIST SP 800-218 v1.1 (SSDF) — PW.4, PW.5, PW.7 (verified 2026-05-20)
  - Anthropic Claude Code skill authoring guidance — current (verified 2026-05-20)
  - MITRE ATLAS v5.4.0 — agent code generation techniques (verified Phase 2, 2026-05-17)
  - ISO/IEC 5055:2021 — Software Measurement (cited by reference; paywalled)
last-generated: 2026-05-20
refresh-recommended: 2027-05-20
self-evolution:
  anti-patterns-observed: []
  triggers-refined: []
  ai-failures-documented: []
---

# CODE-QUALITY

> **Skill body ≤300 lines** (per `DEC-2026-05-19-007`). Principles, rule summaries, and navigation live here. Full content in reference files loaded on demand:
> - `rules.md` — full rules with rule-level citations
> - `anti-patterns.md` — full anti-pattern + canonical pattern pairs with code examples

<!-- SECTION: overview -->
## §1 Overview

CODE-QUALITY governs the craftsmanship dimension of every code change: type discipline at boundaries, explicit error handling, intent-revealing names, comment discipline, scale-aware defaults, and solo-maintainability. It is one of three always-on skills in TGF (alongside SECURITY-CORE and CONTINUITY).

This skill's audience is code that should still be maintainable six months later, by one developer, without rebuilding context. That audience is most production code — and most prototype code that will eventually become production code. The framework's stance: build to that standard from the first commit, since retrofit is expensive.

Rules here cite NIST SSDF v1.1 (PW.4, PW.5, PW.7) at the practice level and acknowledge TGF synthesis for craft rules that lack rule-level mapping in any single authoritative source.
<!-- /SECTION: overview -->

<!-- SECTION: sources -->
## §2 Authoritative Sources

| Source ID | Reference | Version | Date Verified |
|-----------|-----------|---------|---------------|
| NIST-SSDF | [NIST SP 800-218 Secure Software Development Framework](https://csrc.nist.gov/pubs/sp/800/218/final) | v1.1 | 2026-05-20 |
| ANTHROPIC-SKILLS | [Anthropic Claude Code Skills authoring guidance](https://code.claude.com/docs/en/skills) | current | 2026-05-20 |
| MITRE-ATLAS | [MITRE ATLAS — AI threat techniques](https://atlas.mitre.org) | v5.4.0 | 2026-05-17 (Phase 2) |
| ISO-5055 | ISO/IEC 5055:2021 Software Measurement (paywalled, cited by reference) | 2021 | reference only |

Citation granularity per Phase 4 Checkpoint 1 Decision A: NIST SSDF practices are cited at the practice level (PW.4, PW.5, PW.7) since the practice IS the granular unit in that source. Craft rules without rule-level mapping in any authoritative source acknowledge "TGF synthesis grounded in [source]" so the citation chain is honest.
<!-- /SECTION: sources -->

<!-- SECTION: discovery -->
## §3 Discovery Commands

Copy-pasteable commands to capture craft state before applying rules. Used by Stage 1 (Research) to ground in current reality rather than assumed reality.

```bash
# List code files this skill governs
find . -type f \( -name "*.ts" -o -name "*.tsx" -o -name "*.py" -o -name "*.go" -o -name "*.rs" \) -not -path "./node_modules/*" -not -path "./.git/*" | head -40

# Find boundary type erasure (TypeScript/Python)
grep -rn ": any\b\|: any\[\]\|<any>" --include="*.ts" --include="*.tsx" src/ 2>/dev/null | head -20
grep -rn ":\s*Any\b\|->.*Any\b" --include="*.py" src/ 2>/dev/null | head -20

# Find bare exception handling
grep -rn "except:\|except Exception:\|catch\s*(\s*Exception\s*\w*\s*)" --include="*.py" --include="*.ts" --include="*.java" src/ 2>/dev/null | head -20

# Find debt markers
grep -rn "TODO\|FIXME\|HACK\|XXX" --include="*.ts" --include="*.tsx" --include="*.py" src/ 2>/dev/null | head -20

# Count direct dependencies (calibrate to project)
test -f package.json && jq '.dependencies | length' package.json
test -f pyproject.toml && grep -c '^[a-zA-Z]' pyproject.toml || true
```
<!-- /SECTION: discovery -->

<!-- SECTION: principles -->
## §4 Universal Principles

These six principles are the trait essence of CODE-QUALITY. They preload into the orchestrator agent context (per `DEC-2026-05-19-007`) and ground every numbered rule below.

- **Code is read more than written.** Default to clarity even when verbose. The next reader is often you, six months out, without context. The marginal cost of one extra line for readability is a rounding error against the cost of a future reader rebuilding intent from scratch.

- **Names carry the design.** Good naming makes structure visible at a glance; bad naming forces every reader to reverse-engineer intent from implementation. `userIds` not `arr1`. `calculateRefundEligibility` not `helper2`. Names are the cheapest documentation, and the only kind that doesn't rot.

- **Errors at boundaries deserve attention.** I/O, parsing, third-party calls, and persistence are where reality intrudes on assumptions. Handle errors at the call site or propagate them with context. Never silently swallow. A bare `except:` is a future incident report.

- **Build for scale from the start.** Indexed queries, paginated lists, bounded resources, async I/O for blocking operations. These are not premature optimization — they are baseline competence. The cost of building them in is small; the cost of retrofitting them under production load is large and visible.

- **Standard patterns over clever ones.** The cleverest solution is rarely the one a future maintainer can hold in their head. Default to boring, well-trodden idioms. Reach for cleverness only when current evidence demands it and the alternative is documented. Boring tech over trendy.

- **Complexity earns its place.** Don't introduce abstractions, dependencies, or indirection until current evidence demands them. Three similar lines beat a premature abstraction. A dependency added for one call site is a maintenance liability disguised as convenience. Solve the problem in front of you; do not design for hypothetical futures.
<!-- /SECTION: principles -->

<!-- SECTION: rules -->
## §5 Rule Summaries

Brief summaries point to `rules.md` for full content with citations, plain-language impact, and extended discussion. Six rules, each summary: title + 1-line statement + source identifier.

<!-- RULE: 5.1 -->
- **Rule 5.1: Type Safety at Boundaries** — Public function, module, and trust boundaries declare types explicitly; internal helpers may rely on inference. `NIST-SSDF v1.1 PW.5` → [`rules.md#rule-51-type-safety-at-boundaries`](rules.md)
<!-- /RULE: 5.1 -->
<!-- RULE: 5.2 -->
- **Rule 5.2: Explicit Error Handling at Failure Points** — Errors at I/O, parsing, and third-party calls are handled at the call site or propagated with context; no silent swallows. `NIST-SSDF v1.1 PW.5` → [`rules.md#rule-52-explicit-error-handling-at-failure-points`](rules.md)
<!-- /RULE: 5.2 -->
<!-- RULE: 5.3 -->
- **Rule 5.3: Names Describe Intent** — Variable, function, and class names communicate problem-domain meaning, not implementation detail. `TGF-SYNTHESIS — grounded in NIST-SSDF v1.1 PW.5 + senior-engineer practice` → [`rules.md#rule-53-names-describe-intent`](rules.md)
<!-- /RULE: 5.3 -->
<!-- RULE: 5.4 -->
- **Rule 5.4: Comment the WHY, Not the WHAT** — Comments explain non-obvious WHY only: hidden constraints, subtle invariants, workarounds, surprising behavior. Routine narration is noise. `TGF-SYNTHESIS — grounded in ANTHROPIC-SKILLS guidance + senior practice` → [`rules.md#rule-54-comment-the-why-not-the-what`](rules.md)
<!-- /RULE: 5.4 -->
<!-- RULE: 5.5 -->
- **Rule 5.5: Scale-Aware Defaults from First Commit** — Indexed queries, pagination with limits, bounded resources, async I/O for blocking operations, stateless services. `TGF-SYNTHESIS — grounded in NIST-SSDF v1.1 PW.5 + senior practice` → [`rules.md#rule-55-scale-aware-defaults-from-first-commit`](rules.md)
<!-- /RULE: 5.5 -->
<!-- RULE: 5.6 -->
- **Rule 5.6: Solo-Maintainability as Design Constraint** — Standard patterns over clever; boring tech over trendy; explicit over implicit; dependencies justified by clear value. `TGF-SYNTHESIS — grounded in NIST-SSDF v1.1 PW.4 + senior practice` → [`rules.md#rule-56-solo-maintainability-as-design-constraint`](rules.md)
<!-- /RULE: 5.6 -->

See `rules.md` for full rule text, citations, plain-language impact, and extended discussion. Reference files load on demand when deep rule application is needed (typically Stage 5 Code Review).
<!-- /SECTION: rules -->

<!-- SECTION: anti-patterns -->
## §6 Anti-Pattern Summaries

Brief summaries point to `anti-patterns.md` for full content with code examples and paired canonical patterns. Eight anti-pattern pairs minimum per `DEC-2026-05-17-003` Clause 1.

<!-- ANTI-PATTERN: AP-1 -->
- **AP-1: `any` at module boundaries** — Public function signatures declare `any` or untyped parameters, erasing the type contract for callers. Violates Rule 5.1. → [`anti-patterns.md#ap-1-any-at-module-boundaries`](anti-patterns.md)
<!-- /ANTI-PATTERN: AP-1 -->
<!-- ANTI-PATTERN: AP-2 -->
- **AP-2: Bare exception swallow** — `except:` or `catch (Exception e)` blocks that consume the error and continue without logging, rethrow, or recovery. Violates Rule 5.2. → [`anti-patterns.md#ap-2-bare-exception-swallow`](anti-patterns.md)
<!-- /ANTI-PATTERN: AP-2 -->
<!-- ANTI-PATTERN: AP-3 -->
- **AP-3: Single-letter or implementation-detail names in non-trivial scope** — `arr1`, `tmp`, `data2`, `helper` used where the domain meaning is non-obvious. Violates Rule 5.3. → [`anti-patterns.md#ap-3-single-letter-or-implementation-detail-names`](anti-patterns.md)
<!-- /ANTI-PATTERN: AP-3 -->
<!-- ANTI-PATTERN: AP-4 -->
- **AP-4: Code-narrating comments** — Comments that restate what the next line obviously does (`// increment counter`, `// return result`). Violates Rule 5.4. → [`anti-patterns.md#ap-4-code-narrating-comments`](anti-patterns.md)
<!-- /ANTI-PATTERN: AP-4 -->
<!-- ANTI-PATTERN: AP-5 -->
- **AP-5: Unindexed predicate on a user-driven query** — `SELECT … WHERE col = ?` against a column without an index, when `col` is part of a predictable user-driven query pattern. Violates Rule 5.5. → [`anti-patterns.md#ap-5-unindexed-predicate-on-user-driven-query`](anti-patterns.md)
<!-- /ANTI-PATTERN: AP-5 -->
<!-- ANTI-PATTERN: AP-6 -->
- **AP-6: Unbounded list return from API handler** — Endpoint returns the full result set with no pagination, limit, or maximum cap. Violates Rule 5.5. → [`anti-patterns.md#ap-6-unbounded-list-return-from-api-handler`](anti-patterns.md)
<!-- /ANTI-PATTERN: AP-6 -->
<!-- ANTI-PATTERN: AP-7 -->
- **AP-7: Clever one-liner that requires a comment to explain** — Code golf that compresses three readable statements into one unreadable line, then comments around it. Violates Rule 5.6 (and Rule 5.4). → [`anti-patterns.md#ap-7-clever-one-liner`](anti-patterns.md)
<!-- /ANTI-PATTERN: AP-7 -->
<!-- ANTI-PATTERN: AP-8 -->
- **AP-8: Dependency added for a single-use call** — A new package added to the dependency manifest for one function call that could be inlined in a few lines of standard library. Violates Rule 5.6. → [`anti-patterns.md#ap-8-dependency-for-single-use`](anti-patterns.md)
<!-- /ANTI-PATTERN: AP-8 -->

Each anti-pattern is paired with a canonical pattern (CP-N) in `anti-patterns.md` — full content includes code examples for both, failure modes, and replacement guidance. Per `DEC-2026-05-17-003` Clause 1: standalone anti-patterns without paired canonical patterns are incomplete and do not ship.
<!-- /SECTION: anti-patterns -->

<!-- SECTION: ai-concerns -->
## §7 AI-Specific Concerns

Failure modes specific to AI-generated code in the craft dimension. Derived from observed behavior, not theoretical concerns.

- **Plausible-but-wrong.** AI generates code that compiles, matches expected shape, and reads as confident — but has subtle wrong behavior: off-by-one, wrong null check, wrong order of operations, wrong default value. Confirmation bias means "looks right" passes review. Defense: read the *behavior*, not the shape. When stakes warrant, run the code rather than reason about it (per `docs/ARCHITECTURE.md` §16 — Empirical Verification for AI-Generated Code).

- **Over-engineering on demand.** Asked for a function, AI ships a framework. Asked for a fix, AI refactors the surrounding module. Generic helpers, factories, and abstractions appear without current evidence demanding them. Violates Rule 5.6. Defense: scope discipline at Stage 2; the four-pass review's holistic phase flags scope creep.

- **Stale-pattern reproduction.** Training data over-represents older patterns — legacy JS callback idioms, jQuery DOM mutation, Python 2 conventions, pre-async I/O patterns. AI defaults to what's frequent in training, which lags current best practice by years. Defense: rule-level citations to current source versions catch citation-to-stale-pattern mismatches.

- **Citation hallucination.** Asked to cite, AI may fabricate plausible-sounding references that don't exist (`OWASP ASVS V99.99.99`) or misattribute real rules to wrong sources. Defense: per `DEC-2026-05-17-004`, every citation must trace to a verifiable source at skill-creation time — applies to runtime AI output as well.

Relevant external taxonomies: MITRE ATLAS `AML.T0051` (LLM output handling failures), OWASP Top 10 for LLMs `LLM09:2025` (misinformation including fabricated citations), and `LLM06:2025` (excessive agency — AI taking actions beyond scope).
<!-- /SECTION: ai-concerns -->

<!-- SECTION: workflow -->
## §8 Workflow Integration

How CODE-QUALITY participates in the six-stage workflow and four-pass review (per `docs/WORKFLOW.md`).

- **Stage 1 (Research):** Suggest the discovery commands in §3 to grep boundary-type-erasure, bare-except, and debt markers. Inform the change context for Stage 3.
- **Stage 3 (Plan with Governance):** Contribute Rules 5.1, 5.2, 5.5 when the change touches function boundaries, error handling, or persistence. Contribute Rule 5.6 when dependencies are added or abstractions introduced.
- **Stage 4 (Implement):** Apply all rules during code writing; principles in §4 are the writing posture.
- **Stage 5 Phase 1 (Code Review):** Primary skill — all six rules in scope. Flag every AP-1 through AP-8 occurrence in changed code with pairing to canonical pattern.
- **Stage 5 Phase 4 (Holistic Review):** Rule 5.6 (solo-maintainability) is the holistic-review-specific check: would the next maintainer recognize the patterns? Are dependencies justified?
- **Stage 6 (Commit):** Capture any rule waivers in `WAIVER-LOG.md` with rationale and revisit date per `CLAUDE.md` §1.
<!-- /SECTION: workflow -->

<!-- SECTION: subagent-context -->
## §9 Subagent Context

**Preloaded by:** `code-reviewer` (primary — all rules); `holistic-reviewer` (Rule 5.6 for solo-maintainability check). Per `DEC-2026-05-19-007`, the full skill content injects into these subagent contexts at startup via the agent definition's `skills:` field.

**Critical rules for review use (when consulted but not preloaded):**

- Rule 5.1 (Type Safety at Boundaries)
- Rule 5.2 (Explicit Error Handling)
- Rule 5.6 (Solo-Maintainability)

**Top AI-specific concerns:**

- Plausible-but-wrong (compiles + matches shape, wrong behavior)
- Over-engineering on demand (scope creep)

Reference files (`rules.md`, `anti-patterns.md`) load on demand within the subagent if deeper detail is needed during a specific finding.
<!-- /SECTION: subagent-context -->
