# Rules — TESTING

Full rule statements with citations, plain-language impact, and extended discussion. Referenced from `SKILL.md` §5 Rule Summaries. Loaded on demand when deep rule application is needed.

Seven rules covering test strategy, coverage discipline, trust-boundary testing, security testing, accessibility testing, and the AI-tautological-test failure mode. Anchored in NIST SSDF PW.7/PW.8, ISTQB Foundation Level Syllabus v4.0, OWASP WSTG v4.2, WCAG 2.2.

Citation discipline per `DEC-2026-05-17-004`: cite at the source's natural granularity; acknowledge TGF synthesis where rule-level mapping doesn't exist. ISTQB-CTFL cited by reference (istqb.org gated against WebFetch but syllabus is publicly published).

---

## Rule 5.1: Test Behavior, Not Implementation

**Statement:** Tests verify what the system DOES (observable behavior — inputs produce expected outputs; state changes match expectations; side effects occur where expected) — not HOW it does it (implementation detail — which internal functions get called in what order, what the internal data shapes look like, which private methods exist). Tests coupled to implementation break on refactor even when behavior is unchanged; tests coupled to behavior survive refactor and catch real regressions.

**Citation:** `ISTQB-CTFL v4.0 (test design principles — black-box testing emphasis)` + `NIST-SSDF v1.1 PW.8 (Test Executable Code)` + `TGF-SYNTHESIS on behavior-vs-implementation discipline`.

**Plain-language impact:** Implementation-coupled tests are noise generators. Every refactor — extracting a method, renaming an internal helper, reorganizing module boundaries — breaks dozens of tests that didn't actually have anything to do with the change. Engineers spend time updating tests to match the new implementation; the tests provide no signal about correctness; the suite gradually becomes a maintenance burden rather than a safety net. Behavior-coupled tests, by contrast, fail only when behavior changes — they let refactors happen freely and they fire loudly when something actually broke.

**Extended discussion:** The line between behavior and implementation is sometimes nuanced. A useful heuristic: if you can observe the property from outside the function (via its return value, its side effects on observable state, or its interaction with the outside world), it's behavior. If you can only observe the property by inspecting internal structure, it's implementation.

Examples:

- **Behavior (test these):** "Function returns a sorted list given an unsorted input." "Function persists the user record." "Function returns 401 when token is invalid." "Component re-renders when prop changes." "API endpoint returns the user's own data but not other users' data."
- **Implementation (don't test these):** "Function calls `Array.prototype.sort()`." "Function uses a `for` loop instead of `forEach`." "Private method `_validateInternal` is called." "Component uses `useState` instead of `useReducer`."

For AI-assisted development specifically: AI tends to write tests after writing the implementation, with the test assertions mirroring what the implementation does rather than what it should do. Defense: write tests against the function's CONTRACT (what callers expect), not its CONTENTS (what the function body happens to do). When the function's contract is unclear, that's the signal — DISCOVERY engages to clarify intent before tests get written.

**Related anti-patterns:** AP-1 (tautological tests), AP-2 (implementation-coupled tests) (see `anti-patterns.md`)

---

## Rule 5.2: Trust-Boundary Tests Are Mandatory

**Statement:** Validate every trust boundary with tests. "Trust boundary" means: untrusted-input handlers (HTTP request bodies, form submissions, file uploads, message-queue payloads, parsed user content), third-party API calls (where reality may differ from happy-path assumptions), persistence layer crossings (where data shapes meet schema constraints), network operations (where failure modes intrude). Tests cover the happy path AND the failure modes — malformed input, missing fields, oversized payloads, network timeouts, persistence conflicts.

Pure-function tests follow risk-based judgment — they're valuable where they add signal but not mandatory at the boundary-test level.

**Citation:** `NIST-SSDF v1.1 PW.7 (Review/Analyze Code) + PW.8 (Test Executable Code)` + cross-reference to `SECURITY-CORE Rule 5.1 (Validate Input at Trust Boundaries)`.

**Plain-language impact:** Trust-boundary failures are the source of most production incidents. The HTTP handler that didn't validate the request body shape crashes on malformed input. The third-party API integration that didn't test for upstream failure mode hangs forever when the upstream is slow. The database write that didn't account for unique-constraint violations explodes when two writes race. Tests at the trust boundary catch these classes before they reach production; their absence is a known failure mode pattern.

**Extended discussion:** A trust-boundary test usually covers:

- **Happy path.** Well-formed input produces expected output.
- **Schema-violation cases.** Missing required field, wrong type, out-of-range value, malformed structure. Should reject with informative error, not crash.
- **Edge values.** Empty input, null, oversized payload (10MB body, 10000-element array), boundary values (max int, min date).
- **Authorization failure.** Authenticated request from a user who shouldn't access this resource — should return 403/404, not the resource.
- **Failure mode of the upstream/downstream.** Third-party API returns 500; database write conflicts with concurrent write; network call times out. System should handle gracefully, not crash or hang.

For SECURITY-CORE alignment: Rule 5.2 of TESTING operationalizes the testing dimension of SECURITY-CORE Rule 5.1 (Validate Input at Trust Boundaries). The validation logic exists; the tests verify it works.

For AI-assisted development: AI tends to write happy-path tests and forget the failure modes. Prompt explicitly for failure-mode tests at the boundary; review for completeness against this rule.

**Related anti-patterns:** AP-4 (missing trust-boundary tests), AP-6 (mock-everything tests that bypass real boundary verification) (see `anti-patterns.md`)

---

## Rule 5.3: Test Shape Follows Domain (Pyramid OR Trophy)

**Statement:** Test shape — the distribution of unit vs integration vs E2E tests — follows the domain rather than abstract advice. **Classical pyramid** (many unit tests, fewer integration tests, fewest E2E) suits backend / library / pure-function-heavy code where unit-level bugs dominate and integration is relatively boring. **Modern trophy** (heavy integration testing, lighter unit testing, some E2E) suits frontend / web / component-heavy code where bugs live at component-interaction boundaries and unit-of-meaning is "rendered component," not "pure function." Both shapes are legitimate; the choice is driven by where bugs actually live in YOUR codebase.

**Citation:** `ISTQB-CTFL v4.0 (test levels)` — ISTQB documents unit / integration / system / acceptance levels at the methodology level. The pyramid-vs-trophy choice is `TGF-SYNTHESIS on modern web testing patterns`, recognizing that Kent C. Dodds' testing-trophy framing (heavy integration) reflects a real domain-fit difference from Mike Cohn's original testing pyramid (heavy unit). TGF presents both per Phase 5 Checkpoint 1 Decision B.

**Plain-language impact:** Forcing the test pyramid on a frontend project (heavy unit testing of React components in isolation) produces a green test suite that misses the actual bugs (which live in how components compose, how state flows between them, how user interactions update multiple parts of the UI). Forcing the test trophy on a backend project (heavy integration testing of pure logic) wastes time setting up integration infrastructure for logic that would test cleanly at the unit level. The discipline is matching shape to domain.

**Extended discussion:** When to use which shape:

**Pyramid suits:**
- Pure-function-heavy libraries (parsers, validators, format converters)
- Algorithm-heavy backend code (sorting, scheduling, billing calculation)
- Domain-logic modules that operate on input → output without significant external interaction
- Languages/frameworks where unit testing is cheap and integration is expensive (some backend frameworks)

**Trophy suits:**
- React / Vue / Svelte component-heavy frontends (test components in their integration context)
- Next.js / Remix full-stack apps (test routes end-to-end, with database, with auth)
- API-driven web apps where the bugs live in request → handler → DB → response paths
- Languages/frameworks where integration testing is cheap (modern web frameworks)

**Mixed:**
- Full-stack monorepos may use pyramid for backend domain logic, trophy for frontend; the shape per-package, not per-project
- Microservices may use trophy for service boundaries, pyramid for service-internal logic

The pyramid-vs-trophy choice is documented in the project's test strategy (could be in DECISIONS.md per CONTINUITY Rule 5.2) so contributors don't accidentally fight the shape.

For AI-assisted development: AI defaults to whatever testing pattern is over-represented in its training data for the language/framework — often the pyramid for backend code, often inconsistent for frontend. Explicit shape decision avoids accumulating mixed conventions.

**Related anti-patterns:** AP-5 (test pyramid forced on frontend project) (see `anti-patterns.md`)

---

## Rule 5.4: Coverage Is Feedback, Not Target

**Statement:** Code coverage metrics (line coverage, branch coverage, function coverage, statement coverage) are diagnostic feedback about what code paths tests exercise. Coverage is NOT a target to hit. Setting "95% line coverage" or "100% branch coverage" as a quality gate produces tautological tests added solely to hit the number — tests with zero behavioral signal that game the metric. Use coverage to surface gaps in what's tested; let behavioral discipline (Rule 5.1) drive what tests get added.

**Citation:** `TGF-SYNTHESIS — grounded in ISTQB-CTFL v4.0 (coverage as test measurement) + senior testing practice on Goodhart's Law applied to coverage`.

**Plain-language impact:** Coverage-percentage targets corrupt the test suite. Engineers add `expect(true).toBe(true)` and "exercise this line" tests to satisfy the gate. The coverage report shows 95%; the test suite verifies almost nothing useful. When a real bug ships, the team is surprised — "but coverage was 95%." Coverage measured what tests touched, not what tests verified. The metric and the goal diverged the moment the metric became a target.

**Extended discussion:** Coverage as feedback works like this:

- **Coverage tells you where tests don't reach.** Uncovered lines / branches are candidate gaps — code paths nothing exercises. Some of those will be "intentionally untested" (defensive null checks that can't actually trigger; deprecated paths slated for removal). Others will be "should be tested but isn't" — those are the ones worth adding tests for.
- **Coverage doesn't tell you tests are good.** A line is "covered" the moment any test exercises it. The coverage tool doesn't know whether the test asserts anything meaningful. 100% coverage with all-tautological-tests verifies nothing.

The practical pattern: use coverage to identify under-tested areas, then add BEHAVIORAL tests (per Rule 5.1) for what matters in those areas. Reject pull requests that add tests purely to raise the percentage.

A reasonable team policy: coverage is reported but not gated. Pull requests that significantly drop coverage may surface a review question ("you removed coverage on the auth module — was that intentional?"), but no hard threshold blocks merges. The discipline is human review of where tests should exist, not automated chase of a number.

For AI-assisted development: AI prompted to "improve test coverage" often produces low-signal tests that exercise uncovered paths without verifying behavior. Prompt instead for "tests that catch specific failure modes in [module]." The output quality is dramatically better.

**Related anti-patterns:** AP-3 (coverage-percentage chase) (see `anti-patterns.md`)

---

## Rule 5.5: Security Testing Per OWASP WSTG

**Statement:** Security-relevant changes get security testing aligned with OWASP Web Security Testing Guide (WSTG) categories: information gathering, configuration and deployment, identity management, authentication, authorization, session management, input validation, error handling, cryptography, business logic, client-side, API. Risk-based application — not every change needs a full security test pass; trust-boundary changes and security-sensitive surfaces always do. Test identifiers follow `WSTG-CAT-NN` format where applicable.

**Citation:** `OWASP-WSTG v4.2 (released 2020-12-03; v5.0 in development as of 2026-05-20)` + cross-reference to `SECURITY-CORE` for the security-rules surface.

**Plain-language impact:** Without security testing, security-relevant code ships untested in its security dimension. The authentication flow passes its functional tests (correct password produces a session); the security tests (expired token, replay attack, brute-force resistance, session fixation) aren't run. Production incidents follow — auth flaws are among the most-exploited classes per OWASP Top 10:2025 (A07:2025 Authentication Failures). Security testing catches these before they ship.

**Extended discussion:** OWASP WSTG categories most commonly relevant in TGF-style adopter projects:

- **WSTG-INFO (Information Gathering)** — does the system leak sensitive information in headers, error messages, comments, robots.txt, debug output?
- **WSTG-IDNT (Identity Management)** — registration, account enumeration, weak password policy testing.
- **WSTG-ATHN (Authentication)** — credential transport, default credentials, lockout mechanism, password change, browser cache, password policy.
- **WSTG-ATHZ (Authorization)** — path traversal, bypass authorization schema, privilege escalation, IDOR (insecure direct object reference).
- **WSTG-SESS (Session Management)** — session token cookie attributes (HttpOnly, Secure, SameSite), session fixation, session timeout, logout effectiveness.
- **WSTG-INPV (Input Validation)** — XSS (reflected/stored/DOM-based), SQL injection, command injection, LDAP injection, server-side template injection.
- **WSTG-ERRH (Error Handling)** — improper error handling that leaks stack traces or internal paths.
- **WSTG-CRYP (Cryptography)** — weak ciphers, padding oracle, plaintext storage of sensitive info.
- **WSTG-BUSL (Business Logic)** — bypassing business rules through API manipulation, race conditions, abuse-by-design.

Tests written for these categories often combine automated tools (ZAP, Burp, npm audit, snyk) with behavioral tests in the test suite itself.

For AI-assisted development: AI generates happy-path security tests (correct credentials succeed, valid token authorizes) and tends to skip the negative cases (expired token returns 401, malformed token returns 401, missing token returns 401, token-for-other-user returns 403/404). Defense: explicit negative-case prompting at security test generation + Stage 5 Phase 2 (Security Audit) review.

Future Phase 6 + Phase 7 security skills extend this surface with depth per security domain.

**Related anti-patterns:** AP-7 (security-relevant change shipped without security testing) (see `anti-patterns.md`)

---

## Rule 5.6: Accessibility Testing Per WCAG 2.2

**Statement:** UI changes get accessibility testing combining **automated tooling** (axe-core, jest-axe, Playwright accessibility, Lighthouse) with **manual checks** (keyboard navigation walkthrough, screen reader spot-checks on key flows, focus management verification, color contrast verification on novel color choices). Automated tools catch approximately 30-40% of WCAG 2.2 conformance issues; manual testing covers the remainder. Target Level AA conformance for most adopter projects.

**Citation:** `WCAG 2.2 (W3C Recommendation, 2023-10-05; updated 2024-12-12)` — cross-reference from DESIGN Rule 5.6 + UI-CRAFT Rule 5.6.

**Plain-language impact:** Without accessibility testing, AI-generated UI ships with the accessibility failures it tends to produce (missing labels, broken focus management, color-only error indication, no keyboard support for custom interactions). Users with disabilities can't use the product; the product also faces legal exposure (EU EAA, US Section 508, similar requirements globally). Catching these via testing — automated + manual — is cheaper than shipping and fixing under complaint.

**Extended discussion:** The split between automated and manual:

**Automated tools catch (with rough estimates):**
- Missing form labels (`<label>` not associated with `<input>`)
- Missing alt text on images
- Insufficient color contrast (where measurable from CSS)
- Missing landmark roles
- Empty links/buttons
- Heading hierarchy violations (h1 → h3 skipping h2)
- ARIA usage errors (invalid roles, mismatched attributes)

**Manual testing catches:**
- Whether focus order matches visual order
- Whether keyboard-only users can complete every flow
- Whether screen reader announces relevant state changes (form validation, modal open/close, dynamic content load)
- Whether color is the SOLE indicator of meaning (vs supplementary)
- Whether motion can be disabled via `prefers-reduced-motion`
- Whether text scales reasonably to 200%
- Whether interactive elements have appropriate target size (≥24x24 CSS px per SC 2.5.8 in WCAG 2.2)
- Whether custom controls have appropriate ARIA + keyboard semantics

A reasonable testing rhythm: axe-core / jest-axe integrated into the test suite (runs on every PR); manual keyboard walkthrough + screen reader smoke test on every release of significant UI changes; full manual audit on major releases.

For AI-assisted development: AI generates components that often pass automated tooling (it knows the patterns axe-core checks for) but fail manual testing (focus management, screen reader semantics, keyboard interaction for custom components). Defense: don't rely on axe-core alone; include manual checks in the testing rhythm.

**Related anti-patterns:** AP-8 (accessibility test as axe-only) (see `anti-patterns.md`)

---

## Rule 5.7: AI-Generated Tests Get Behavioral Audit

**Statement:** Every AI-generated test is reviewed against the question: "Does this test the BEHAVIOR the function should have, or the SHAPE OF THE CODE that exists?" Tautological tests pass green and verify nothing. The audit asks: if the implementation changed to a different correct implementation, would this test still pass? If yes, the test is behavioral. If no, the test is implementation-coupled or tautological.

**Citation:** `TGF-SYNTHESIS — grounded in MITRE-ATLAS observations on AI test generation failure modes + senior testing practice on behavioral audit`. MITRE ATLAS documents AI output failure modes; the behavioral audit is the operational defense for this specific class.

**Plain-language impact:** AI-generated tests look productive — green test runs, growing test count, accumulating coverage. But tautological tests verify nothing; they're noise that pretends to be safety. The first real bug ships, the suite was green the whole way, trust in the test infrastructure erodes. The audit prevents this — a tautological test gets caught at write time, replaced with a behavioral test that catches the class of bug it should catch.

**Extended discussion:** The behavioral-audit test:

1. **Identify the contract.** What does the function PROMISE to do? (Not what does its body happen to do — what's the contract callers depend on?)
2. **Imagine a different correct implementation.** If someone rewrote the function with the same contract but different internals (different algorithm, different data structures, different organization), would the test still pass?
3. **If yes (test passes against rewrite): behavioral test. Keep.**
4. **If no (test breaks against legitimate rewrite): implementation-coupled or tautological. Rewrite the test to verify behavior, not shape.**

Examples:

- **Tautological:** `expect(formatPrice(1099)).toBe('$10.99')` where the implementation literally returns the string `'$10.99'` for input `1099`. Test passes; doesn't verify the formatting logic worked.
- **Behavioral:** `expect(formatPrice(1099)).toBe('$10.99')` where the implementation does cent-to-dollar conversion, currency formatting, and decimal handling. Test verifies the contract (input 1099 cents → output "$10.99"). Reimplementing with a different formatter library would still pass.

The distinction is subtle but important. The same assertion can be behavioral OR tautological depending on what the implementation actually does. The audit reads the implementation alongside the test and asks the rewrite question.

For AI-assisted development specifically: ask AI to surface its tests for behavioral audit before they're committed. Or have a code-review pass that does the audit. Or use property-based testing (fast-check, Hypothesis) where the test asserts properties the implementation must satisfy rather than literal expected values — property-based tests are inherently behavioral.

**Related anti-patterns:** AP-1 (tautological tests), AP-6 (mock-everything tests) (see `anti-patterns.md`)

---
