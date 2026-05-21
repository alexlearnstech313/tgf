---
# ─── Anthropic-native runtime fields (Claude Code honors these) ───
name: testing
description: |
  Test strategy and quality-assurance discipline. Use when writing tests,
  designing test strategy, evaluating coverage, planning security testing,
  or planning accessibility testing. Covers unit/integration/E2E test levels
  (pyramid vs trophy by domain), coverage-as-feedback (not target), trust-
  boundary testing as mandatory, security testing via OWASP WSTG, accessibility
  testing against WCAG 2.2, and the AI-specific concern that AI tends to write
  tautological tests that match the implementation rather than testing behavior.
paths:
  - "**/*.test.*"
  - "**/*.spec.*"
  - "**/tests/**"
  - "**/test/**"
  - "**/__tests__/**"
  - "**/cypress/**"
  - "**/playwright/**"
  - "**/e2e/**"

# ─── TGF-extension metadata (Phase 11 meta-skills read these; Claude Code ignores) ───
applies-when:
  paths-include:
    - "**/*.{test,spec}.{ts,tsx,js,jsx,py,go,rs}"
    - "**/{tests,test,__tests__,cypress,playwright,e2e}/**"
  operations-include:
    - test file added or modified
    - test strategy discussion or planning
    - coverage configuration changes
    - security testing for trust-boundary or auth-related code
    - accessibility testing for UI changes
disqualifying-when:
  - test fixture additions without test logic changes
  - test config formatting-only edits
  - non-test code that incidentally exists in a test directory
sources:
  - NIST SP 800-218 v1.1 (SSDF) — PW.7 Review/Analyze Code, PW.8 Test Executable Code (verified 2026-05-20 Phase 4)
  - ISTQB Certified Tester Foundation Level Syllabus v4.0 (released October 2023) — cited by reference; istqb.org returned 403 to WebFetch but the syllabus is the canonical international testing methodology reference
  - OWASP Web Security Testing Guide (WSTG) v4.2 (released 2020-12-03; v5.0 in development as of 2026-05-20) — verified 2026-05-20
  - WCAG 2.2 (W3C Recommendation, 2023-10-05; updated 2024-12-12; verified 2026-05-20 Phase 5 commit 3/7) — cross-reference for accessibility testing
  - MITRE ATLAS v5.4.0 — AI test-generation failure modes (verified Phase 2, 2026-05-17)
last-generated: 2026-05-20
refresh-recommended: 2027-05-20
self-evolution:
  anti-patterns-observed: []
  triggers-refined: []
  ai-failures-documented: []
---

# TESTING

> **Skill body ≤300 lines** (per `DEC-2026-05-19-007`). Principles, rule summaries, and navigation live here. Full content in reference files loaded on demand:
> - `rules.md` — full rules with citations
> - `anti-patterns.md` — full anti-pattern + canonical pattern pairs with code examples

<!-- SECTION: overview -->
## §1 Overview

TESTING governs the discipline of verifying that code does what it should — including when AI wrote the code. It is an **activity skill** in TGF (loads on context per `CLAUDE.md` §9), not always-on. It activates when test files are touched, when test strategy is being designed, or when coverage / security testing / accessibility testing decisions arise.

The skill encodes a few interlocking disciplines: tests verify *behavior* not implementation; trust boundaries are mandatory test targets while pure-function tests follow risk-based judgment; test shape (pyramid vs trophy) follows the domain rather than dogma; coverage is feedback not target; security testing and accessibility testing are part of the testing surface, not afterthoughts.

The most important AI-specific failure mode TESTING addresses: AI tends to write tests that assert against the implementation it just wrote — "the function returns 42" tests that the function returns the literal 42 returned by the function, not that the function delivers the intended behavior. These tests pass green and feel productive but verify nothing. The discipline counteracts this by anchoring tests in behavior and treating AI-generated tests with explicit behavioral audit.

Authoritative grounding: NIST SSDF PW.7/PW.8 (already verified Phase 4 SECURITY-CORE), ISTQB Foundation Level Syllabus v4.0, OWASP WSTG v4.2, WCAG 2.2 (cross-reference from DESIGN/UI-CRAFT for accessibility testing).
<!-- /SECTION: overview -->

<!-- SECTION: sources -->
## §2 Authoritative Sources

| Source ID | Reference | Version | Date Verified |
|-----------|-----------|---------|---------------|
| NIST-SSDF | [NIST SP 800-218 SSDF](https://csrc.nist.gov/pubs/sp/800/218/final) — PW.7 Review/Analyze Code, PW.8 Test Executable Code | v1.1 | 2026-05-20 (Phase 4) |
| ISTQB-CTFL | ISTQB Certified Tester Foundation Level Syllabus (istqb.org/certifications/certified-tester-foundation-level) | v4.0 (October 2023) | reference (istqb.org returned 403 to WebFetch; syllabus PDF publicly downloadable from official source) |
| OWASP-WSTG | [OWASP Web Security Testing Guide](https://owasp.org/www-project-web-security-testing-guide/) | v4.2 (released 2020-12-03; v5.0 in development) | 2026-05-20 |
| WCAG | [W3C Web Content Accessibility Guidelines 2.2](https://www.w3.org/WAI/standards-guidelines/wcag/) — cross-reference from DESIGN/UI-CRAFT | 2.2 (2023-10-05; updated 2024-12-12) | 2026-05-20 (Phase 5 commit 3/7) |
| MITRE-ATLAS | [MITRE ATLAS](https://atlas.mitre.org) — AI test generation failure modes | v5.4.0 | 2026-05-17 (Phase 2) |

Citation granularity per Phase 4 Checkpoint 1 Decision A: NIST SSDF cited at practice level (PW.7, PW.8); ISTQB-CTFL cited by reference at syllabus level (similar to APPLE-HIG pattern from UI-CRAFT — publicly published authoritative source; the host site is gated against WebFetch but the syllabus itself is real and downloadable); OWASP WSTG cited at test-identifier level where applicable (e.g., `WSTG-INFO-02`); WCAG 2.2 cited at success-criterion level for accessibility testing.
<!-- /SECTION: sources -->

<!-- SECTION: discovery -->
## §3 Discovery Commands

Copy-pasteable commands to assess current testing state before applying rules.

```bash
# Detect test framework + config
for f in jest.config.* vitest.config.* playwright.config.* cypress.config.* pytest.ini pyproject.toml; do
  [ -f "$f" ] && echo "✓ $f" || true
done

# Count tests across the codebase
find . -path ./node_modules -prune -o -name "*.test.*" -print -o -name "*.spec.*" -print 2>/dev/null | wc -l

# Detect coverage configuration (informs Rule 5.4)
grep -rln "coverageThreshold\|coverage.threshold\|coverage_threshold" --include="*.json" --include="*.js" --include="*.ts" --include="*.toml" 2>/dev/null | head

# Find trust-boundary code that should have tests (Rule 5.2)
# Look for input handlers, third-party calls, persistence operations
grep -rln "req\.body\|request\.json\|fetch(\|axios\.\|stripe\.\|.create(\|.update(" --include="*.ts" --include="*.tsx" --include="*.py" src/ 2>/dev/null | head -10

# Detect AI-tautological-test signals (Rule 5.7)
# Tests where the assertion mirrors the function name very literally
grep -rnE "expect\(.+\)\.toBe\(.+\)\s*$" --include="*.test.*" --include="*.spec.*" 2>/dev/null | head -5

# Accessibility testing presence (Rule 5.6)
grep -rln "axe-core\|jest-axe\|@axe-core\|playwright.*accessibility" --include="package.json" 2>/dev/null | head
```
<!-- /SECTION: discovery -->

<!-- SECTION: principles -->
## §4 Universal Principles

Six principles that ground every numbered rule.

- **Tests verify behavior, not implementation.** A test that breaks on every refactor (even when behavior didn't change) is coupled to implementation. A test that survives refactoring while still catching real behavior regressions is coupled to behavior. The first is brittle; the second is durable. Write the second.

- **Trust boundaries are mandatory test targets.** Anywhere untrusted input enters the system, third-party calls happen, or persistence operations cross trust contexts, tests verify the boundary behaves correctly. Pure-function unit tests follow risk-based judgment — they're valuable where they add signal, not as a coverage-percentage chase.

- **Test shape follows the domain, not dogma.** Classical test pyramid (many unit, fewer integration, fewest E2E) suits backend / library code where unit-level bugs dominate. Modern test trophy (heavy integration, lighter unit, some E2E) suits frontend / web where bugs live at component interaction. Choose based on where your bugs actually live.

- **Coverage is feedback, not target.** Coverage metrics tell you what code paths tests exercise. Chasing a percentage target (95%, 100%) produces tautological tests that exercise paths without verifying behavior. Use coverage to surface gaps; let behavioral discipline drive what gets tested.

- **Security and accessibility testing are part of the testing surface.** Security-relevant changes get security testing aligned with OWASP WSTG. UI changes get accessibility testing aligned with WCAG 2.2. These aren't optional later passes — they're part of test strategy from the start.

- **AI-generated tests get behavioral audit.** AI tends to write tests that assert against the implementation it just wrote. Every AI-generated test gets reviewed against the question: "does this test the BEHAVIOR the function should have, or the SHAPE OF THE CODE that's already there?" Tautological tests are silent failures — they pass green and verify nothing.
<!-- /SECTION: principles -->

<!-- SECTION: rules -->
## §5 Rule Summaries

Seven rules. Each summary: title + 1-line statement + source identifier.

<!-- RULE: 5.1 -->
- **Rule 5.1: Test Behavior, Not Implementation** — Tests verify what the system DOES (observable behavior), not HOW it does it (implementation detail). Tests coupled to implementation break on refactor; tests coupled to behavior survive refactor and catch real regressions. `ISTQB-CTFL v4.0 (test design principles) + NIST-SSDF v1.1 PW.8 + TGF-SYNTHESIS` → [`rules.md#rule-51-test-behavior-not-implementation`](rules.md)
<!-- /RULE: 5.1 -->
<!-- RULE: 5.2 -->
- **Rule 5.2: Trust-Boundary Tests Are Mandatory** — Validate every trust boundary: untrusted-input handlers, third-party API calls, persistence layer crossings, network operations. Pure-function tests follow risk-based judgment. `NIST-SSDF v1.1 PW.7 + PW.8 + SECURITY-CORE Rule 5.1 (validate input at trust boundaries)` → [`rules.md#rule-52-trust-boundary-tests-are-mandatory`](rules.md)
<!-- /RULE: 5.2 -->
<!-- RULE: 5.3 -->
- **Rule 5.3: Test Shape Follows Domain (Pyramid OR Trophy)** — Classical pyramid (many unit, fewer integration, fewest E2E) suits backend/library code. Modern trophy (heavy integration, lighter unit, some E2E) suits frontend/web. Choose based on where the bugs actually live in YOUR domain, not abstract advice. `ISTQB-CTFL v4.0 (test levels) + TGF-SYNTHESIS on modern web testing patterns` → [`rules.md#rule-53-test-shape-follows-domain`](rules.md)
<!-- /RULE: 5.3 -->
<!-- RULE: 5.4 -->
- **Rule 5.4: Coverage Is Feedback, Not Target** — Coverage metrics inform what code is tested vs untested; they are NOT targets to hit. Coverage % targets produce tautological tests added to hit the number. Use coverage to surface gaps; let behavioral discipline drive test additions. `TGF-SYNTHESIS — grounded in ISTQB-CTFL v4.0 + senior testing practice` → [`rules.md#rule-54-coverage-is-feedback-not-target`](rules.md)
<!-- /RULE: 5.4 -->
<!-- RULE: 5.5 -->
- **Rule 5.5: Security Testing Per OWASP WSTG** — Security-relevant changes get security testing aligned with OWASP WSTG categories (information gathering, authentication, authorization, session management, input validation, error handling, cryptography, business logic, client-side, API). Risk-based application: not every change needs a full security test pass; trust-boundary changes always do. `OWASP-WSTG v4.2 + SECURITY-CORE cross-reference` → [`rules.md#rule-55-security-testing-per-owasp-wstg`](rules.md)
<!-- /RULE: 5.5 -->
<!-- RULE: 5.6 -->
- **Rule 5.6: Accessibility Testing Per WCAG 2.2** — UI changes get accessibility testing combining automated tooling (axe-core, Lighthouse, jest-axe) with manual checks (keyboard navigation walkthrough, screen reader spot-checks on key flows). Automated tools catch ~30-40%; manual covers the rest. `WCAG 2.2 (W3C Recommendation; cross-reference from DESIGN/UI-CRAFT)` → [`rules.md#rule-56-accessibility-testing-per-wcag-22`](rules.md)
<!-- /RULE: 5.6 -->
<!-- RULE: 5.7 -->
- **Rule 5.7: AI-Generated Tests Get Behavioral Audit** — Every AI-generated test is reviewed against: "does this test the BEHAVIOR the function should have, or the SHAPE OF THE CODE that exists?" Tautological tests pass green and verify nothing. Behavioral audit catches the most common AI test-generation failure mode. `TGF-SYNTHESIS — grounded in MITRE-ATLAS observations on AI test generation + senior practice` → [`rules.md#rule-57-ai-generated-tests-get-behavioral-audit`](rules.md)
<!-- /RULE: 5.7 -->

See `rules.md` for full rule text, citations, plain-language impact, and extended discussion.
<!-- /SECTION: rules -->

<!-- SECTION: anti-patterns -->
## §6 Anti-Pattern Summaries

Eight anti-pattern pairs covering the most common testing failures, including the AI tautological-test mode.

<!-- ANTI-PATTERN: AP-1 -->
- **AP-1: Tautological tests** — `expect(add(2, 3)).toBe(5)` where the implementation is `return 5`. Test passes; verifies nothing. Violates Rule 5.7 (and 5.1). → [`anti-patterns.md#ap-1-tautological-tests`](anti-patterns.md)
<!-- /ANTI-PATTERN: AP-1 -->
<!-- ANTI-PATTERN: AP-2 -->
- **AP-2: Implementation-coupled tests** — Tests assert on internal state, private methods, or specific call sequences that aren't observable behavior. Refactor breaks the test even when behavior is unchanged. Violates Rule 5.1. → [`anti-patterns.md#ap-2-implementation-coupled-tests`](anti-patterns.md)
<!-- /ANTI-PATTERN: AP-2 -->
<!-- ANTI-PATTERN: AP-3 -->
- **AP-3: Coverage-percentage chase** — `expect(true).toBe(true)` or similar added to hit a 95% coverage target. Coverage looks good; signal is zero. Violates Rule 5.4. → [`anti-patterns.md#ap-3-coverage-percentage-chase`](anti-patterns.md)
<!-- /ANTI-PATTERN: AP-3 -->
<!-- ANTI-PATTERN: AP-4 -->
- **AP-4: Missing trust-boundary tests** — User input handler ships without tests for malformed/oversized/missing input. Third-party API integration ships without tests for the upstream-failure case. Violates Rule 5.2. → [`anti-patterns.md#ap-4-missing-trust-boundary-tests`](anti-patterns.md)
<!-- /ANTI-PATTERN: AP-4 -->
<!-- ANTI-PATTERN: AP-5 -->
- **AP-5: Test pyramid forced on a frontend project** — Heavy unit testing on a React component codebase where bugs live at component-integration; little integration testing because "unit tests are pyramid base." Wrong shape for the domain. Violates Rule 5.3. → [`anti-patterns.md#ap-5-test-pyramid-on-frontend`](anti-patterns.md)
<!-- /ANTI-PATTERN: AP-5 -->
<!-- ANTI-PATTERN: AP-6 -->
- **AP-6: Mock-everything tests** — Every dependency mocked, including the persistence layer being tested. Mocks configured to return what the test asserts. Tests pass; reality untested. Violates Rules 5.1 and 5.2. → [`anti-patterns.md#ap-6-mock-everything-tests`](anti-patterns.md)
<!-- /ANTI-PATTERN: AP-6 -->
<!-- ANTI-PATTERN: AP-7 -->
- **AP-7: Security-relevant change shipped without security testing** — Auth-handling endpoint added/changed without tests for unauthorized access, invalid tokens, expired sessions, etc. Violates Rule 5.5. → [`anti-patterns.md#ap-7-no-security-testing`](anti-patterns.md)
<!-- /ANTI-PATTERN: AP-7 -->
<!-- ANTI-PATTERN: AP-8 -->
- **AP-8: Accessibility test as axe-only** — Only automated tooling runs; manual keyboard navigation walkthrough and screen reader spot-checks skipped. ~60-70% of accessibility issues not caught. Violates Rule 5.6. → [`anti-patterns.md#ap-8-accessibility-axe-only`](anti-patterns.md)
<!-- /ANTI-PATTERN: AP-8 -->

Per `DEC-2026-05-17-003` Clause 1: every anti-pattern is paired with a canonical pattern in `anti-patterns.md`.
<!-- /SECTION: anti-patterns -->

<!-- SECTION: ai-concerns -->
## §7 AI-Specific Concerns

Testing failure modes specific to AI-assisted development.

- **Tautological test generation.** AI writes the function, then writes a test that asserts against what the function returns. `function add(a, b) { return a + b; }` + `expect(add(2, 3)).toBe(5)` — test passes because the implementation returns the literal value the test expects. Defense: Rule 5.7 — every AI-generated test gets behavioral audit. The question is "does this test the function's CONTRACT or its IMPLEMENTATION?"

- **Mock-saturated tests.** AI defaults to mocking every dependency (network calls, persistence, third-party APIs) — and then configures the mocks to return what the assertions expect. The test verifies the mocks, not the code. Defense: Rule 5.2 — trust-boundary tests use real implementations where possible; mocks are bounded to the actual external boundary.

- **Happy-path-only tests.** AI generates the canonical-input test path. Error cases, edge inputs (empty, null, oversized), concurrency edges, and malformed-input tests are often missing. Defense: explicit edge-case prompt at test generation time + Stage 5 Phase 2 (Security Audit) catches missing security cases.

- **Coverage chase from prompts.** When prompted to "improve test coverage," AI often produces low-signal tests that exercise code paths without verifying behavior. The coverage report improves; the test value doesn't. Defense: Rule 5.4 — coverage is feedback, not target. Prompt for "tests that catch specific failure modes," not "tests to raise coverage."

- **Plausible-but-wrong assertions.** AI may produce assertions that look reasonable but don't match what the code actually does — `expect(result).toContain('success')` when the real return value structure is different. Tests fail loudly (good) but the failure reads as "test wrong" rather than "code wrong" — eroding trust in the test suite. Defense: behavioral audit confirms assertions match observable behavior before tests are committed.

Relevant external taxonomies: MITRE ATLAS framework on AI output failures; OWASP LLM Top 10:2025 `LLM09:2025` (Misinformation — fabricated assertions about what code does).
<!-- /SECTION: ai-concerns -->

<!-- SECTION: workflow -->
## §8 Workflow Integration

How TESTING participates in the six-stage workflow (per `docs/WORKFLOW.md`).

- **Stage 1 (Research):** Run §3 discovery commands when test work is in scope. Confirm test framework + coverage configuration + existing test patterns.
- **Stage 2 (Scope):** Test strategy decisions (pyramid vs trophy per Rule 5.3) are part of scope when scope includes substantial test work. Trust-boundary identification (Rule 5.2) surfaces what MUST be tested.
- **Stage 3 (Plan with Governance):** Rules 5.1–5.7 contribute when the change includes test additions or test strategy decisions. Security testing scope (Rule 5.5) determined by trust-boundary analysis. Accessibility testing scope (Rule 5.6) determined by UI-touching status.
- **Stage 4 (Implement):** Apply rules during test writing. AI-generated tests get behavioral audit (Rule 5.7) at write time, not after.
- **Stage 5 Phase 1 (Code Review):** Test files reviewed for behavior coverage vs implementation coupling. AI tests flagged for tautology check.
- **Stage 5 Phase 2 (Security Audit):** Security-relevant changes verified to have OWASP WSTG-aligned tests (Rule 5.5).
- **Stage 6 (Commit):** Test coverage is feedback for ROADMAP — what's tested vs untested informs next-iteration priorities.
<!-- /SECTION: workflow -->

<!-- SECTION: subagent-context -->
## §9 Subagent Context

**Preloaded by:** None directly. TESTING activates at the orchestrator level. The `code-reviewer` subagent (Phase 4) references TESTING Rule 5.1 (behavior not implementation) when reviewing test files. The `security-auditor` subagent references TESTING Rule 5.5 (OWASP WSTG alignment) when reviewing security-relevant test surfaces.

**Critical rules for orchestrator use (when not preloaded):**

- Rule 5.1 (Test Behavior, Not Implementation)
- Rule 5.2 (Trust-Boundary Tests Are Mandatory)
- Rule 5.7 (AI-Generated Tests Get Behavioral Audit)

**Top AI-specific concerns:**

- Tautological test generation (test asserts against implementation, not contract)
- Mock-saturated tests (mocks configured to return assertion expectations)
- Coverage chase from prompts (low-signal tests added to raise %)

Reference files (`rules.md`, `anti-patterns.md`) load on demand within the orchestrator if a specific testing scenario warrants deep rule application.
<!-- /SECTION: subagent-context -->
