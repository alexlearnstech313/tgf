# Rules — DESIGN

Full rule statements with citations, plain-language impact, and extended discussion. Referenced from `SKILL.md` §5 Rule Summaries. Loaded on demand when deep rule application is needed.

Six rules covering universal design principles for AI-assisted development. Anchored in Anthropic's "Building Effective Agents" (2024-12-19) — particularly the Simplicity principle — and WCAG 2.2 for accessibility. Most rules acknowledge TGF synthesis grounded in those sources.

Citation discipline per `DEC-2026-05-17-004`: cite at the source's natural granularity; acknowledge TGF synthesis where rule-level mapping doesn't exist.

---

## Rule 5.1: Start from Constraints, Not from Patterns

**Statement:** Design begins with constraint articulation — users, scale, deadline, infrastructure, budget, team size, threat model — not with patterns from training data or canonical-architecture catalogs. Patterns are paths *within* constraints; they don't replace constraint analysis. The order is: constraints first, then pattern selection from candidates that fit those constraints.

**Citation:** `ANTHROPIC-AGENTS (2024-12-19) — Simplicity principle ("find the simplest solution possible, and only increasing complexity when needed") + TGF-SYNTHESIS`. Anthropic's guide articulates the constraint-aware design posture at the principle level; the rule operationalizes it.

**Plain-language impact:** Pattern-first design produces "standard architectures for the domain" that may not fit the project's actual constraints. The resulting system pays the cost of patterns that earn nothing — operational overhead, complexity, maintenance burden — without the benefits those patterns deliver in different contexts. Constraint-first design produces systems that fit, ship, and remain maintainable.

**Extended discussion:** Common categories of constraint to articulate at the start:

- **Users.** Who uses this? How many concurrently? What's their technical depth? What devices and contexts?
- **Scale.** Current and 12-month projected. Volume (requests/day, users, transactions). Distribution patterns.
- **Deadline.** Real deadline if there is one. The deadline filters what fits.
- **Infrastructure.** What's already deployed. What can be added cheaply vs expensively.
- **Budget.** Both money and engineering time. A solo founder has different design space than a funded team.
- **Team.** Size, skill distribution, operational capacity.
- **Threat model.** Per SECURITY-CORE — adversaries, data sensitivity, compliance scope.

Once constraints are articulated, pattern selection becomes principled — patterns are evaluated against constraints, not adopted because they're "industry standard for X domain." Two patterns may both be standard but only one fits the constraints at hand.

For AI-assisted development specifically: AI training data heavily over-represents the architecture of mature, large-scale projects. Asked to "design a notification system," AI may propose a Kafka-based event-driven architecture even when the project has 100 users and a deadline (where a `node-cron` job writing to a `notifications` table would suffice). The discipline is reading the constraints, then evaluating whether the AI-proposed pattern earns its place against those constraints.

**Related anti-patterns:** AP-1 (pattern-first design), AP-7 (complexity for AI-resume), AP-8 (best-practice transplant) (see `anti-patterns.md`)

---

## Rule 5.2: Negative Constraints Are First-Class

**Statement:** "We do NOT want X" is articulated alongside "we want X" during design. Explicit negative constraints prevent the design space from including paths that look reasonable but fail against the project's actual needs. Negative constraints are durable artifacts — captured in DECISIONS.md (per CONTINUITY Rule 5.2) so they survive across sessions and contributors.

**Citation:** `TGF-SYNTHESIS — grounded in senior design practice`. Negative constraint discipline is widely practiced in engineering teams but not codified at sub-rule level in any single authoritative source.

**Plain-language impact:** Without explicit negative constraints, the design space silently expands as alternatives are proposed and partially accepted. The team says "yes, that sounds reasonable" to options that conflict with what they actually want, because the actual unwanted was never stated. Scope creep follows. Six months later, the project has features and patterns that no one consciously chose — they accumulated through "yes, and" responses to suggestions that should have been negatively constrained.

**Extended discussion:** Common categories of negative constraint worth stating:

- **What stack we won't use.** "Not adopting GraphQL right now — REST is sufficient at our scale and the team knows REST." "Not adding a new database — Postgres handles everything we need."
- **What features we won't build.** "Not building enterprise features — we're a consumer product; enterprise is a different business." "Not building a mobile app — web-first; mobile only if web validation succeeds."
- **What vendors we won't depend on.** "Not adding more SaaS dependencies — operational complexity already at limit." "Not using closed-source ML APIs — open-weight models for cost predictability."
- **What patterns we won't adopt.** "Not building plugins — single-tenant is sufficient." "Not adding multi-tenancy — single-org product."
- **What scope we won't expand into.** "Not adding compliance scope beyond GDPR — HIPAA is out of scope for this product." "Not adding payment features — Stripe handles all of that."

Negative constraints are stated with the same clarity and reasoning as positive constraints. The Decision/Context/Consequences ADR structure (per CONTINUITY Rule 5.2) captures the WHY — "we chose NOT to do X because Y" — so future contributors can re-evaluate when context changes.

For AI-assisted development: AI defaults to "yes, and" — extending positive constraints with reasonable-sounding alternatives. When a previously-stated negative is forgotten, AI may propose a pattern that conflicts with it. Defense: keep negatives in DECISIONS.md (durable); reference them when AI proposes alternatives that may conflict.

**Related anti-patterns:** AP-2 (missing negative constraints) (see `anti-patterns.md`)

---

## Rule 5.3: Simplest Design That Meets Constraints Wins

**Statement:** When two designs both meet stated constraints, the simpler one wins. Complexity earns its place only when current evidence demands it — not because it's "more flexible," not because it's "more scalable," not because it's "industry standard." This is Anthropic's foundational principle from "Building Effective Agents" applied at the design layer plus CODE-QUALITY Rule 5.6 (solo-maintainability) operationalized at the architectural scale.

**Citation:** `ANTHROPIC-AGENTS (2024-12-19) — Simplicity principle ("Success in the LLM space isn't about building the most sophisticated system. It's about building the right system for your needs.") + CODE-QUALITY Rule 5.6 (solo-maintainability)`.

**Plain-language impact:** Complex designs cost more in every dimension — implementation time, debugging time, onboarding time, operational overhead, failure modes, dependencies. The cost is paid every day the system runs. Simpler designs that meet constraints win because their cost is lower across the system's lifetime, not just at greenfield-build time. The phrase "we'll need this complexity eventually" is usually wrong — the eventual need is often different from what was anticipated, and the speculative complexity was the wrong shape.

**Extended discussion:** "Simplest that meets constraints" requires both halves — *simplest* and *meets constraints*. A design that's simple but doesn't meet constraints isn't simpler; it's incomplete. The discipline is to find the smallest design that genuinely meets the constraints, not to optimize for either simplicity or constraint-coverage in isolation.

Common signs that complexity is being added without evidence:

- **"For future flexibility."** Speculative; current evidence doesn't demand it; per Rule 5.4 (change accommodation, not anticipation) deferred.
- **"For scale we'll have someday."** Premature optimization; if scale arrives, refactor then; the patterns for scale are well-documented when the time comes.
- **"This is industry standard."** May be true for industries with very different constraints; per Rule 5.1 (start from constraints), industry standard isn't transferable without context.
- **"It's more flexible."** Flexibility has cost; if the flexibility isn't being used, it's pure cost.

Anthropic's framing applies: success is about the *right* system, not the *most sophisticated*. The right system is constraint-fitting and as-simple-as-meets-constraints; both halves are load-bearing.

**Related anti-patterns:** AP-3 (over-extensibility), AP-7 (complexity for AI-resume), AP-8 (best-practice transplant) (see `anti-patterns.md`)

---

## Rule 5.4: Design Accommodates Change but Doesn't Anticipate It

**Statement:** Good design has clear seams where change is likely AND avoids speculative extensibility for hypothetical needs. The discipline cuts both ways: rigid one-shot designs break at first change (because there are no seams), and over-extensible designs accumulate maintenance burden for hypothetical needs that may never materialize. The right shape is: change-likely-at-known-points = seam there; change-hypothetical = no speculative abstraction.

**Citation:** `TGF-SYNTHESIS — grounded in senior design practice + ANTHROPIC-AGENTS Simplicity principle`. The "accommodate but don't anticipate" framing operationalizes the simplicity discipline for change-resilience at the design layer.

**Plain-language impact:** Both failure modes are real and common. AP-3 (over-extensibility for hypothetical needs) shows a plugin system added "in case we need it" that adds permanent maintenance burden and never gets used. AP-4 (rigid one-shot design) shows hard-coded vendor choices that require significant rewrite when the vendor needs to be swapped. Neither extreme is correct; the discipline is identifying which changes are *likely* (and putting seams there) vs *hypothetical* (and not).

**Extended discussion:** What counts as a "likely" change?

- **Auth provider switch.** Common — companies change auth vendors. A thin auth abstraction layer is usually worth it.
- **Database swap.** Less common — most projects don't switch database engines. Hard-coupling to one DB is often fine; over-abstracting with ORM-everywhere is often not.
- **Payment provider switch.** Common for early-stage products — Stripe to a different provider, or adding a second provider. A thin payment abstraction often earns its place.
- **Email provider switch.** Common — providers change pricing or features. A thin email-sending abstraction often pays off.
- **Frontend framework swap.** Uncommon. Not worth abstracting against unless the project has unusual constraints.
- **Cloud provider switch.** Uncommon but high-stakes when it happens. Worth using cloud-agnostic patterns where cheap (S3-compatible APIs, OCI containers) but not worth complex abstraction layers.

What counts as hypothetical?

- **"Maybe we'll need plugins someday."** No evidence demands plugins now; defer until evidence emerges.
- **"This might need multi-tenancy."** No tenants exist; multi-tenancy patterns can be added when there's a second tenant.
- **"What if we need to support 10 languages?"** No multi-language users yet; i18n infrastructure can be added when the second language is requested.
- **"We might want real-time updates."** No real-time requirement now; polling is fine until requirements demand otherwise.

The pattern: when change is genuinely likely (history shows projects do this), put a seam there. When change is hypothetical (no current evidence), don't add abstraction speculatively. Both directions are disciplined.

**Related anti-patterns:** AP-3 (over-extensibility), AP-4 (rigid one-shot design) (see `anti-patterns.md`)

---

## Rule 5.5: AI Patterns from Training Are Hypotheses, Not Defaults

**Statement:** When AI proposes a pattern (microservices, event sourcing, vector DB, GraphQL, multi-agent orchestration, Redux, etc.), the pattern is a *hypothesis* against current constraints — not a default to adopt. Constraint-fit check is mandatory before adoption. The check asks: does this pattern's cost (complexity, dependencies, operational overhead, learning curve) earn its place against the project's constraints (users, scale, deadline, team, budget)?

**Citation:** `TGF-SYNTHESIS — grounded in MITRE-ATLAS observations on AI design failures + ANTHROPIC-AGENTS Simplicity principle`. AI pattern-reproduction is a documented failure mode in AI-design contexts; the rule formalizes the check.

**Plain-language impact:** AI training data over-represents the architecture of mature, large-scale projects. The patterns AI proposes are correlated with what those projects use — which is correlated with their constraints (Netflix-scale, thousands of engineers, billions of requests). When a project with very different constraints (10 users, solo team, validation-MVP) adopts those patterns, the cost is paid but the benefits don't materialize. The discipline of treating AI patterns as hypotheses surfaces this mismatch.

**Extended discussion:** The constraint-fit check is operationally brief — a few questions:

1. **What does this pattern cost?** Complexity, dependencies, operational overhead, learning curve, runtime cost.
2. **What does this pattern deliver?** At what scale or constraint configuration does the benefit show up?
3. **Where are we?** Current scale, team, constraints.
4. **Does the cost earn its place?** Yes if benefits materialize at current scale or near-future scale; defer otherwise.

Common AI-proposed patterns and their typical mismatch:

- **Microservices.** Cost: high operational overhead, distributed-system complexity, inter-service contract management. Benefit: scale isolation, team-of-teams autonomy. Mismatch when: scale is small, team is small.
- **Vector DB + RAG.** Cost: vector embedding infrastructure, retrieval tuning, latency. Benefit: large-corpus semantic search. Mismatch when: small corpus where keyword search suffices.
- **Multi-agent orchestration.** Cost: agent coordination, debugging across agents, latency, cost. Benefit: complex multi-step workflows. Mismatch when: single-agent design would work.
- **Event sourcing.** Cost: event store maintenance, projection complexity, debugging. Benefit: audit trail, time-travel debugging, eventual-consistency tolerance. Mismatch when: simple CRUD against a relational DB suffices.
- **Redux / global state management.** Cost: boilerplate, indirection. Benefit: complex cross-component state coordination. Mismatch when: local component state would work.

For each pattern AI proposes, treat the proposal as: "Hypothesis: pattern X is the right fit for this project." Then check the hypothesis against constraints. Adopt if the hypothesis holds; reject and choose simpler if not.

**Related anti-patterns:** AP-1 (pattern-first), AP-5 (AI-pattern without constraint check), AP-7 (complexity for AI-resume), AP-8 (best-practice transplant) (see `anti-patterns.md`)

---

## Rule 5.6: Accessibility Is Designed In, Not Bolted On

**Statement:** Accessible design (WCAG 2.2 POUR principles — Perceivable, Operable, Understandable, Robust) is a design-time consideration, not a QA-stage retrofit. Color contrast, keyboard navigation, semantic structure, screen-reader compatibility, alt text, focus management — all are cheaper at design time than retrofit. WCAG 2.2 conformance levels (A, AA, AAA) provide checkable targets.

**Citation:** `WCAG 2.2 (W3C Recommendation, published 2023-10-05, updated 2024-12-12)`. WCAG 2.2 cited at principle level (POUR) and at specific success-criterion level where applicable (e.g., `WCAG 2.2 SC 1.4.3 Contrast (Minimum)`).

**Plain-language impact:** Retrofitting accessibility is significantly more expensive than designing it in. Color choices made for brand reasons may not meet contrast requirements; navigation patterns built mouse-first may not work with keyboard or screen reader; content structure that ignores semantic HTML may need significant rework to be screen-readable. The retrofit cost is high; the design-time cost is small. Beyond cost, the moral and legal dimension: users with disabilities can't use the product if accessibility wasn't designed in.

**Extended discussion:** The four POUR principles map to design-time considerations:

- **Perceivable.** Information and UI components must be presentable in ways users can perceive — color contrast (SC 1.4.3 AA minimum 4.5:1 for normal text, 3:1 for large), text alternatives for non-text content (SC 1.1.1), distinguishable content (no color-only differentiation per SC 1.4.1).
- **Operable.** UI components and navigation must be operable — keyboard accessibility (SC 2.1.1), sufficient time (SC 2.2.1), no seizure-inducing patterns (SC 2.3.1), navigable structure (SC 2.4 series).
- **Understandable.** Information and UI operation must be understandable — readable text (SC 3.1 series), predictable behavior (SC 3.2 series), input assistance (SC 3.3 series).
- **Robust.** Content must be robust enough to work with current and future user agents including assistive tech — proper semantic HTML, ARIA where HTML semantics don't suffice, no broken markup (SC 4.1 series).

For AI-assisted development: AI tends to focus on what was asked. Accessibility considerations surface inconsistently unless the prompt mentions them. The discipline is making accessibility part of the design-time checklist regardless of prompt.

WCAG 2.2 conformance levels:

- **Level A.** Minimum; below A means the content has barriers for many users.
- **Level AA.** Standard target for most products; legal requirement in many jurisdictions (EU EAA, US Section 508, similar elsewhere).
- **Level AAA.** Enhanced; for specialized contexts. Not always achievable across all content.

Most projects target AA. The discipline at design time: pick AA as target, make design choices that don't preclude AA conformance, run automated checks (axe-core, Lighthouse) plus manual checks (keyboard navigation walkthrough, screen reader spot-checks).

**Related anti-patterns:** AP-6 (accessibility as afterthought) (see `anti-patterns.md`)

---
