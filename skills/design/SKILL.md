---
# ─── Anthropic-native runtime fields (Claude Code honors these) ───
name: design
description: |
  Design discipline for AI-assisted development. Universal design principles
  (constraint-first, negative constraints, simplicity, change-accommodation,
  AI-pattern-vs-constraint, accessibility) with cross-references to domain
  skills for depth: TESTING for testable design, SECURITY-CORE for secure
  design, future data-architecture (Phase 9) for schema design, future
  security-api (Phase 7) for API design. Defends against the AI failure mode
  where models propose training-data patterns without checking constraint-fit.
paths:
  - "**/*"

# ─── TGF-extension metadata (Phase 11 meta-skills read these; Claude Code ignores) ───
applies-when:
  paths-include:
    - "**/*"
  operations-include:
    - system architecture proposal
    - API contract design
    - schema design or migration design
    - UX/UI feature design
    - component or module boundary definition
    - workflow or agent orchestration design
    - design-document creation or revision
  data-flows-include:
    - design decisions crossing into committed implementation scope
disqualifying-when:
  - tactical code edit with no design implication
  - documentation-only changes
  - debugging an established issue (use DEBUGGING)
  - implementing against an approved design (no new design questions)
sources:
  - Anthropic — "Building Effective Agents" (published 2024-12-19, verified 2026-05-20)
  - WCAG 2.2 — Web Content Accessibility Guidelines (W3C Recommendation, published 2023-10-05, updated 2024-12-12, verified 2026-05-20)
  - MITRE ATLAS v5.4.0 — agent design failure modes (verified Phase 2, 2026-05-17)
last-generated: 2026-05-20
refresh-recommended: 2027-05-20
self-evolution:
  anti-patterns-observed: []
  triggers-refined: []
  ai-failures-documented: []
---

# DESIGN

> **Skill body ≤300 lines** (per `DEC-2026-05-19-007`). Principles, rule summaries, and navigation live here. Full content in reference files loaded on demand:
> - `rules.md` — full rules with citations
> - `anti-patterns.md` — full anti-pattern + canonical pattern pairs with concrete examples

<!-- SECTION: overview -->
## §1 Overview

DESIGN governs the discipline of making design decisions in AI-assisted development. It is an **activity skill** in TGF (loads on context per `CLAUDE.md` §9), not always-on. It activates when work proposes or revises a design — system architecture, API contracts, schema choices, component boundaries, agent orchestration patterns, UX/UI features.

The skill encodes the trait of *constraint-first design* — start from what the system must respect (users, scale, deadline, infrastructure, budget, threat model), not from what's frequent in training data or pattern catalogs. Per Phase 5 Checkpoint 1 Decision A, DESIGN is **universal principles + cross-references** — the skill covers constraint-first, negative-constraint, simplicity, change-accommodation, AI-pattern-vs-constraint, and accessibility principles; depth on domain-specific design (testable, secure, schema, API) lives in those domains' skills.

DESIGN's primary defenses target two AI failure modes: (1) pattern-reproduction from training data without constraint-fit check (Rule 5.5), and (2) complexity-for-its-own-sake when simpler designs would meet constraints equally well (Rule 5.3). Both are well-documented in Anthropic's "Building Effective Agents" (2024) and informed by MITRE ATLAS observations on AI design failures.
<!-- /SECTION: overview -->

<!-- SECTION: sources -->
## §2 Authoritative Sources

| Source ID | Reference | Version | Date Verified |
|-----------|-----------|---------|---------------|
| ANTHROPIC-AGENTS | [Anthropic — "Building Effective Agents"](https://www.anthropic.com/engineering/building-effective-agents) | 2024-12-19 | 2026-05-20 |
| WCAG | [W3C Web Content Accessibility Guidelines 2.2](https://www.w3.org/WAI/standards-guidelines/wcag/) | 2.2 (2023-10-05; updated 2024-12-12) | 2026-05-20 |
| MITRE-ATLAS | [MITRE ATLAS — agent design failure modes](https://atlas.mitre.org) | v5.4.0 | 2026-05-17 (Phase 2) |

Citation granularity per Phase 4 Checkpoint 1 Decision A: Anthropic's guide cited at the principle/pattern level (e.g., "ANTHROPIC-AGENTS — Simplicity principle"); WCAG cited at principle level (POUR: Perceivable / Operable / Understandable / Robust) and at specific guideline level (e.g., `WCAG 2.2 SC 1.4.3 Contrast (Minimum)`) where applicable. MITRE ATLAS cited at framework level for AI-design failure modes.
<!-- /SECTION: sources -->

<!-- SECTION: discovery -->
## §3 Discovery Commands

Diagnostic prompts to detect when DESIGN engagement is warranted, plus commands for design-state inspection.

```bash
# Detect existing design artifacts
find docs -name "*design*" -o -name "*architecture*" -o -name "ADR*" 2>/dev/null | head
ls docs/DECISIONS.md 2>/dev/null && echo "✓ DECISIONS.md exists for design ADRs"

# Check accessibility tooling configuration (informs DESIGN Rule 5.6)
test -f .axerc 2>/dev/null && echo "✓ axe-core config"
grep -rn "@axe-core\|jest-axe\|playwright.*accessibility" --include="package.json" --include="*.config.*" 2>/dev/null | head -3

# Detect AI-pattern-reproduction risk surfaces (informs Rule 5.5)
# Look for proposed patterns common in training data: microservices, vector DBs, multi-agent orchestration
grep -rni "microservice\|vector.*embedding\|multi-agent" docs/ 2>/dev/null | head -5
```

```
# Diagnostic prompts (run mentally on proposed design)
1. Does this design start from constraints or from patterns? → If patterns, engage Rule 5.1.
2. Are negative constraints stated? → If not, engage Rule 5.2.
3. Is this the simplest design that meets constraints, or has it accumulated complexity? → If complex, engage Rule 5.3.
4. Is the proposed pattern an AI-suggested default or an evidence-backed choice? → If AI default, engage Rule 5.5.
5. Has accessibility been considered at design time? → If no, engage Rule 5.6.
```
<!-- /SECTION: discovery -->

<!-- SECTION: principles -->
## §4 Universal Principles

Six principles that ground every numbered rule.

- **Start from constraints, not from patterns.** Design begins with what the system must respect — users, scale, deadline, infrastructure, budget, threat model — not with what's frequent in training data or canonical-pattern catalogs. Patterns are paths *within* constraints; they don't replace constraint analysis. The order matters: constraint articulation, then pattern selection.

- **Negative constraints are first-class.** "We do NOT want X" is as load-bearing in design as "we want X". Explicit negative constraints prevent the design space from including paths that look reasonable but fail against the project's actual needs. Stating negatives upfront is discipline, not pessimism.

- **The simplest design that meets constraints wins.** When two designs both meet stated constraints, the simpler one wins. Complexity earns its place when current evidence demands it; otherwise reject it. This is Anthropic's first principle from "Building Effective Agents" (2024) plus CODE-QUALITY Rule 5.6 (solo-maintainability) applied at the design layer.

- **Design accommodates change but doesn't anticipate it.** Good design has clear seams where change is likely AND avoids speculative extensibility for hypothetical needs. Both directions fail: rigid one-shot designs break at first change; over-extensible designs accumulate complexity that earns nothing. The discipline cuts both ways.

- **AI patterns from training are hypotheses, not defaults.** AI proposes patterns drawn from training data — typically the most-frequent ones. The frequency in training does not equal fit for current constraints. Every AI-proposed pattern is a *hypothesis* against constraints; constraint-fit must be checked explicitly before adoption.

- **Accessibility is designed in, not bolted on.** Accessible design (WCAG 2.2 POUR principles — Perceivable, Operable, Understandable, Robust) is a design-time consideration, not a retrofit. Color contrast, keyboard navigation, semantic structure, screen-reader compatibility, alt text — all are cheaper at design time and expensive to retrofit.
<!-- /SECTION: principles -->

<!-- SECTION: rules -->
## §5 Rule Summaries

Six rules. Each summary: title + 1-line statement + source identifier.

<!-- RULE: 5.1 -->
- **Rule 5.1: Start from Constraints, Not from Patterns** — Design begins with constraint articulation (users, scale, deadline, infrastructure, budget, threat model); patterns follow from constraints. Pattern-first design produces "standard architectures for the domain" that may not fit the project's actual constraints. `ANTHROPIC-AGENTS (2024-12-19) — Simplicity principle + TGF-SYNTHESIS` → [`rules.md#rule-51-start-from-constraints-not-from-patterns`](rules.md)
<!-- /RULE: 5.1 -->
<!-- RULE: 5.2 -->
- **Rule 5.2: Negative Constraints Are First-Class** — Explicit "we do NOT want X" statements are stated alongside positive constraints during design. Negative constraints prevent the design space from including paths that look reasonable but fail against the project's actual needs. `TGF-SYNTHESIS — grounded in senior design practice` → [`rules.md#rule-52-negative-constraints-are-first-class`](rules.md)
<!-- /RULE: 5.2 -->
<!-- RULE: 5.3 -->
- **Rule 5.3: Simplest Design That Meets Constraints Wins** — When two designs both meet constraints, the simpler one wins. Complexity earns its place only when current evidence demands it. Anthropic's foundational principle from "Building Effective Agents" applied at the design layer. `ANTHROPIC-AGENTS (2024-12-19) — Simplicity principle + CODE-QUALITY Rule 5.6 (solo-maintainability)` → [`rules.md#rule-53-simplest-design-that-meets-constraints-wins`](rules.md)
<!-- /RULE: 5.3 -->
<!-- RULE: 5.4 -->
- **Rule 5.4: Design Accommodates Change but Doesn't Anticipate It** — Good design has clear seams where change is likely AND avoids speculative extensibility for hypothetical needs. The discipline cuts both ways: rigid one-shot designs and over-extensible designs both fail. `TGF-SYNTHESIS — grounded in senior design practice + ANTHROPIC-AGENTS Simplicity principle` → [`rules.md#rule-54-design-accommodates-change-but-doesnt-anticipate-it`](rules.md)
<!-- /RULE: 5.4 -->
<!-- RULE: 5.5 -->
- **Rule 5.5: AI Patterns from Training Are Hypotheses, Not Defaults** — AI proposes patterns drawn from training data (most-frequent patterns). These are hypotheses against current constraints, not defaults. Constraint-fit check is mandatory before pattern adoption. `TGF-SYNTHESIS — grounded in MITRE-ATLAS observations on AI design failures + ANTHROPIC-AGENTS Simplicity principle` → [`rules.md#rule-55-ai-patterns-from-training-are-hypotheses-not-defaults`](rules.md)
<!-- /RULE: 5.5 -->
<!-- RULE: 5.6 -->
- **Rule 5.6: Accessibility Is Designed In, Not Bolted On** — Accessible design (WCAG 2.2 POUR principles) is a design-time consideration. Color contrast, keyboard navigation, semantic structure, screen-reader compatibility are cheaper at design time than retrofit. `WCAG 2.2 (W3C Recommendation, 2023-10-05; updated 2024-12-12)` → [`rules.md#rule-56-accessibility-is-designed-in-not-bolted-on`](rules.md)
<!-- /RULE: 5.6 -->

See `rules.md` for full rule text, citations, plain-language impact, and extended discussion.
<!-- /SECTION: rules -->

<!-- SECTION: anti-patterns -->
## §6 Anti-Pattern Summaries

Eight anti-pattern pairs covering the most common design failures observed in AI-assisted development.

<!-- ANTI-PATTERN: AP-1 -->
- **AP-1: Pattern-first design** — Design starts from "microservices" or "event sourcing" or "GraphQL federation" because those patterns are well-known; constraints (10 users, solo team) ignored. Violates Rule 5.1. → [`anti-patterns.md#ap-1-pattern-first-design`](anti-patterns.md)
<!-- /ANTI-PATTERN: AP-1 -->
<!-- ANTI-PATTERN: AP-2 -->
- **AP-2: Missing negative constraints** — Design proceeds with positive constraints only ("we want X"); "what we do NOT want" never stated; scope creeps inevitably as alternatives that conflict with unstated negatives are proposed and partially accepted. Violates Rule 5.2. → [`anti-patterns.md#ap-2-missing-negative-constraints`](anti-patterns.md)
<!-- /ANTI-PATTERN: AP-2 -->
<!-- ANTI-PATTERN: AP-3 -->
- **AP-3: Over-extensibility for hypothetical needs** — "Let's add a plugin system in case we need it later." Zero current evidence demanding plugins; the abstraction adds maintenance burden for hypothetical future requirements. Violates Rule 5.4. → [`anti-patterns.md#ap-3-over-extensibility-for-hypothetical-needs`](anti-patterns.md)
<!-- /ANTI-PATTERN: AP-3 -->
<!-- ANTI-PATTERN: AP-4 -->
- **AP-4: Rigid one-shot design** — Inverse of AP-3. Design has no seams where change is likely (e.g., hard-coded vendor choices, no abstraction over auth provider); the first change requires significant rewrite. Violates Rule 5.4. → [`anti-patterns.md#ap-4-rigid-one-shot-design`](anti-patterns.md)
<!-- /ANTI-PATTERN: AP-4 -->
<!-- ANTI-PATTERN: AP-5 -->
- **AP-5: AI-pattern adoption without constraint-fit check** — AI proposes a pattern from training data (e.g., "use Redux for state management"); team adopts without checking whether the pattern fits actual constraints (e.g., a small app where local component state would suffice). Violates Rule 5.5. → [`anti-patterns.md#ap-5-ai-pattern-without-constraint-fit-check`](anti-patterns.md)
<!-- /ANTI-PATTERN: AP-5 -->
<!-- ANTI-PATTERN: AP-6 -->
- **AP-6: Accessibility as afterthought** — Design proceeds; accessibility added at QA stage; significant rework because color choices, navigation patterns, content structure, and ARIA semantics all need revisiting. Violates Rule 5.6. → [`anti-patterns.md#ap-6-accessibility-as-afterthought`](anti-patterns.md)
<!-- /ANTI-PATTERN: AP-6 -->
<!-- ANTI-PATTERN: AP-7 -->
- **AP-7: Complexity for AI-resume rather than user value** — Adding patterns ("vector embeddings + RAG + multi-agent orchestration") that sound impressive but don't deliver user value beyond what simpler designs would. Often driven by "this is what serious AI projects do" pattern reproduction. Violates Rules 5.3 and 5.5. → [`anti-patterns.md#ap-7-complexity-for-ai-resume`](anti-patterns.md)
<!-- /ANTI-PATTERN: AP-7 -->
<!-- ANTI-PATTERN: AP-8 -->
- **AP-8: Best-practice transplant without context** — "Netflix uses microservices, so we should too." Pattern transplanted from a context with very different constraints (Netflix-scale traffic, 5,000 engineers) into a context where it doesn't fit. Violates Rules 5.1, 5.3, and 5.5. → [`anti-patterns.md#ap-8-best-practice-transplant-without-context`](anti-patterns.md)
<!-- /ANTI-PATTERN: AP-8 -->

Per `DEC-2026-05-17-003` Clause 1: every anti-pattern is paired with a canonical pattern in `anti-patterns.md`.
<!-- /SECTION: anti-patterns -->

<!-- SECTION: ai-concerns -->
## §7 AI-Specific Concerns

Design failure modes specific to AI-assisted development.

- **Pattern-reproduction from training data.** AI is trained on the architecture of mature, large-scale projects. Patterns from those projects dominate the training signal — microservices, event sourcing, multi-agent orchestration, complex CI/CD. AI proposes those patterns even for projects whose constraints don't justify them (10 users, solo team, validation-MVP). Defense: Rule 5.1 (start from constraints) + Rule 5.5 (AI patterns are hypotheses) + Rule 5.3 (simplest wins).

- **Complexity-for-its-own-sake.** AI may propose complex designs because complexity reads as "thorough" in training data. The simplest design that meets constraints is often less prevalent in training than the complex variants. Defense: Anthropic's Simplicity principle (ANTHROPIC-AGENTS 2024) operationalized via Rule 5.3.

- **Negative-constraint blindness.** AI defaults to "yes, and" — extending positive constraints with reasonable-sounding alternatives. When a user says "don't add a CMS, content is markdown in the repo," AI may later propose a CMS-like layer for "easier content editing" because the original negative constraint was forgotten. Defense: Rule 5.2 — make negative constraints first-class and durable (in DECISIONS.md per CONTINUITY Rule 5.2).

- **Accessibility neglect when not prompted.** AI focuses on what was asked; accessibility considerations are surfaced inconsistently unless the prompt mentions them. Defense: Rule 5.6 — accessibility is part of design discipline, not a prompt-only concern.

Relevant external taxonomies: MITRE ATLAS framework on AI design failures; OWASP LLM Top 10:2025 `LLM06:2025` (Excessive Agency — AI proposing patterns beyond the warranted scope) and `LLM09:2025` (Misinformation — AI confidently proposing patterns that don't fit).
<!-- /SECTION: ai-concerns -->

<!-- SECTION: workflow -->
## §8 Workflow Integration

How DESIGN participates in the six-stage workflow (per `docs/WORKFLOW.md`).

- **Stage 1 (Research):** Activates when prompts include design proposal or revision. Diagnostic prompts in §3 detect engagement triggers.
- **Stage 2 (Scope):** Constraint articulation per Rule 5.1 happens in Scope definition; negative constraints (Rule 5.2) explicitly captured.
- **Stage 3 (Plan with Governance):** Rules 5.3 (simplest), 5.4 (change accommodation), 5.5 (AI patterns are hypotheses) inform plan-stage design choices. Cross-skill references engaged: TESTING for testable design, SECURITY-CORE for secure design, future domain skills (data-architecture, security-api) for depth.
- **Stage 4 (Implement):** Rules apply at implementation if design choices arise mid-build (e.g., a new component boundary surfaces).
- **Stage 5 Phase 4 (Holistic Review):** Holistic Reviewer references DESIGN principles when checking architectural fit and design integrity of the change.
- **Stage 6 (Commit):** Material design decisions captured in DECISIONS.md per CONTINUITY Rule 5.2 with the constraints + negative constraints documented as Context.
<!-- /SECTION: workflow -->

<!-- SECTION: subagent-context -->
## §9 Subagent Context

**Preloaded by:** `holistic-reviewer` (Phase 4) — the full skill content injects into the holistic-reviewer subagent context at startup via its `skills:` frontmatter (verified in `agents/holistic-reviewer.md`), used when checking architectural fit during Stage 5 Phase 4 review. DESIGN also activates at the orchestrator level during Stage 2/Stage 3 for design-shaped work. *(Corrected WS5: the prior "None directly … does not preload" predated the Workstream-3 agent wiring, 2026-05-26.)*

**Critical rules for orchestrator use (when not preloaded):**

- Rule 5.1 (Start from Constraints, Not from Patterns)
- Rule 5.3 (Simplest Design That Meets Constraints Wins)
- Rule 5.5 (AI Patterns from Training Are Hypotheses, Not Defaults)

**Top AI-specific concerns:**

- Pattern-reproduction from training data (mature/large-scale architectures over-represented)
- Complexity-for-its-own-sake (simplicity under-represented in training)
- Negative-constraint blindness (AI defaults to "yes, and")

Reference files (`rules.md`, `anti-patterns.md`) load on demand within the orchestrator if a specific design scenario warrants deep rule application.
<!-- /SECTION: subagent-context -->
