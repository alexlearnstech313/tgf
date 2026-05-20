# Rules — PROJECT-MANAGEMENT

Full rule statements with citations, plain-language impact, and extended discussion. Referenced from `SKILL.md` §5 Rule Summaries. Loaded on demand when deep rule application is needed.

Six rules covering greenfield/brownfield planning, MVP discipline, constraint-aware decomposition, and explicit dependency surfacing. Most rules are TGF synthesis of senior planning practice grounded in NIST SSDF PO-series practices + Agile Manifesto + standard product-management discipline.

Citation discipline per `DEC-2026-05-17-004`: where rule-level mapping does not exist in any single authoritative source, the rule is acknowledged as TGF synthesis with explicit grounding.

---

## Rule 5.1: Start from Intent, Not from Patterns

**Statement:** Planning begins with "what is the user trying to accomplish?" — not with "what's the standard architecture for X?" Patterns inform the path; they don't define the destination. Stack choices, decomposition shapes, and architectural patterns follow from intent; they don't precede it. An MVP for a payment-processing app and an MVP for an internal admin tool are fundamentally different even if they share patterns.

**Citation:** `TGF-SYNTHESIS — grounded in AGILE-MFTO (2001) + senior product practice`. The Agile Manifesto's principles ("our highest priority is to satisfy the customer", "deliver working software frequently") establish intent-first planning at the methodology level; this rule operationalizes that for AI-assisted development where pattern reproduction is a known failure mode.

**Plain-language impact:** Without intent-first planning, the project's first concrete decisions are stack-level commitments made before the actual goal is understood. The user ends up with a "standard architecture for the domain" that may not fit their actual use case — typical scale, real users, available infrastructure, existing constraints. The shape of the solution is decided before the shape of the problem is clear. Rework cost is significant when intent surfaces later and contradicts early commitments.

**Extended discussion:** "Intent" is the operational goal — what the user is trying to accomplish, who benefits, what success looks like. It's NOT the stack ("Next.js + Supabase"), the architecture ("microservices"), or the methodology ("Agile sprints"). All of those are downstream of intent.

A practical test: if you replaced the stack with a different reasonable stack, would the project still serve the intent? If yes, the stack is downstream of intent (correct). If the intent changes with the stack ("we want this to be a Next.js app" is not an intent), pattern thinking is dominating.

For AI-assisted development specifically: training data over-represents established architectures for popular domains. Asked "build a SaaS," AI tends to propose the modal SaaS architecture (Next.js + Postgres + auth + Stripe + Vercel) before asking what the SaaS does or who uses it. The architecture may be fine; the order is wrong. The discipline is: state intent first, propose architecture from intent, not the other way around.

**Related anti-patterns:** AP-1 (architecture-first planning), AP-7 (stack-first selection) (see `anti-patterns.md`)

---

## Rule 5.2: Greenfield Mode — Plan from Intent Through MVP and Beyond

**Statement:** Greenfield projects produce a roadmap that flows from project intent → validation-MVP → growth state. The roadmap is iterative per Agile Manifesto — milestones are committed-to (not aspirational per Rule 5.6's principle in CONTINUITY) but the path between them adapts as learnings emerge. Each milestone has a definition-of-done that is checkable; the sequence reflects the actual learning gradient, not abstract best-practice ordering.

**Citation:** `TGF-SYNTHESIS — grounded in AGILE-MFTO + NIST-SSDF v1.1 PO.1 (Define Security Requirements)`. The iterative-planning posture is core to the Agile Manifesto; NIST SSDF PO.1 covers requirements definition at the practice level. The greenfield-roadmap-shape framing is TGF synthesis.

**Plain-language impact:** Without an explicit roadmap, greenfield projects sprawl — the team works on whatever feels most immediate; sequencing emerges accidentally; milestones blur. New contributors can't tell what's in scope or out. Stakeholder conversations are about "where are we" rather than "what's next." With an explicit roadmap, the project's direction is legible; commitments are visible; reasonable people can disagree about sequencing in a productive way.

**Extended discussion:** A greenfield roadmap is structured around the **learning gradient** — the sequence of questions the project answers about its viability. Typical shape:

1. **Intent → validation-MVP.** What is the smallest thing that lets us learn whether anyone wants this? The validation-MVP is for learning, not scaling. Per Rule 5.4 it serves users not engineering ego.
2. **Validation-MVP → growth-state.** If the validation-MVP shows traction, what's needed to serve a growing user base? This is where infrastructure investments earn their place (scaling, observability, security maturity, compliance).
3. **Growth-state → maturity.** What does the project need to sustain operations? Compliance scope (Phase 10 skills become relevant), operational discipline, team scaling.

Each transition is committed-to once entered (the milestone exists in ROADMAP per CONTINUITY Rule 5.4) but the path between is iterative — what's learned during validation may change the growth-state work substantially.

For TGF projects specifically: this rule operationalizes the validation-then-growth posture that distinguishes intent-grounded planning from architecture-first planning. The Agile Manifesto's "responding to change over following a plan" applies here — the plan exists, but it adapts as learnings emerge.

**Related anti-patterns:** AP-1 (architecture-first), AP-3 (MVP for engineering convenience), AP-6 (abstract best practice) (see `anti-patterns.md`)

---

## Rule 5.3: Brownfield Mode — Plan Around Existing Reality

**Statement:** Brownfield projects start with the existing codebase as constraint. Plans operate AGAINST what's there, not WITH a fresh-greenfield assumption. Non-trivial brownfield work triggers BASELINE-AUDIT (Phase 11 meta-skill) before significant planning. The plan respects existing patterns (CODE-QUALITY Rule 5.6 — codebase fit), known technical debt (logged per CONTINUITY's ERROR-LOG discipline), and existing trust boundaries (SECURITY-CORE's domain).

**Citation:** `TGF-SYNTHESIS — grounded in senior practice on legacy-system planning + NIST-SSDF v1.1 PO.3 (Implement Toolchain)`. Legacy-planning discipline is well-documented in industry practice (e.g., Michael Feathers' "Working Effectively with Legacy Code" patterns, the strangler-fig refactoring pattern) but no single authoritative source provides rule-level guidance; this is TGF synthesis.

**Plain-language impact:** Treating brownfield work as greenfield ignores the actual cost structure. Greenfield decisions are reversible cheaply (no users yet, no dependent systems, no committed data shapes); brownfield decisions are not. A "let's refactor this entire module" plan that makes sense for greenfield is reckless for brownfield where the module serves users, has integrations, and has accumulated knowledge in the surrounding code. The cost of ignoring brownfield reality is rework when migration paths break, users complain, or integrations fail.

**Extended discussion:** Brownfield mode operates on three layers of existing reality:

1. **Codebase patterns.** Per CODE-QUALITY Rule 5.6 (codebase fit), new work matches existing conventions where they exist, deviates intentionally where deviation is documented. Brownfield plans don't unilaterally change conventions; if convention change is part of scope, it's an explicit milestone with migration considerations.

2. **Technical debt.** Existing ERROR-LOG entries and known-issues are inputs to brownfield planning. Per CONTINUITY Rule 5.3 (three-log routing), planning around known debt is different from planning to fix it — both are valid, but they're distinct.

3. **Trust boundaries and architectural integrity.** Per SECURITY-CORE and the architectural-principles skill (Phase 7), existing trust boundaries are load-bearing. Brownfield plans that cross or modify trust boundaries get extra security scrutiny (Stage 5 Phase 2 audit).

**When BASELINE-AUDIT triggers:** Phase 11 meta-skill BASELINE-AUDIT runs for substantial brownfield scope — typically when the change touches multiple modules, crosses trust boundaries, or proposes pattern changes. For tactical fixes (single function, bounded scope), BASELINE-AUDIT is overkill; standard Stage 1 Research suffices.

**Related anti-patterns:** AP-4 (brownfield ignoring existing reality), AP-7 (stack-first in brownfield) (see `anti-patterns.md`)

---

## Rule 5.4: MVP Serves Users, Not Engineering Ego

**Statement:** Minimum Viable Product is the smallest thing that delivers value to actual users — not the smallest thing engineers can ship. Over-scoping (shipping more than users need) and under-scoping (shipping a tech demo with no user value) are failures of the same rule. The discipline is identifying the user's core job and shipping that. "Viability" is defined by users; "minimum" is defined by what serves them.

**Citation:** `TGF-SYNTHESIS — grounded in Eric Ries "The Lean Startup" (2011, comparative source per DEC-2026-05-17-004 Clause 6) + senior product practice`. Ries' MVP framing is the modern canonical reference; the rule operationalizes the user-value test that distinguishes it from "smallest shippable product."

**Plain-language impact:** Under-scoped MVPs feel productive ("we shipped!") but produce nothing users will return for. Over-scoped MVPs miss the point of "minimum" — they ship features for hypothetical future users, delaying validation of the core hypothesis. Both fail: one fails fast and confusingly (nobody adopts because there's nothing to adopt); the other fails slowly and expensively (months invested before the core hypothesis is tested).

**Extended discussion:** Identifying the user's "core job" is the load-bearing operation. The core job is what the user is fundamentally trying to accomplish — the thing that, if the product does it well, will cause the user to return and rely on it.

Common failure modes:

- **Confusing "core job" with "first feature."** The first feature on the roadmap may not be the core job. A scheduling app's core job is probably "I want my appointments to actually happen on time" — the first feature might be "calendar UI" but the core job is reliability.
- **Confusing "minimum viable" with "first version."** The first version can be a learning artifact (validation-MVP per Rule 5.2). It doesn't have to be production-grade.
- **Confusing "viable" with "complete."** A viable MVP can have ugly UI, missing edge cases, manual operational steps. What it cannot have is "the core job doesn't actually work."

For AI-assisted development specifically: AI tends to under-scope (defaulting to "smallest thing that compiles" — tech demo) OR over-engineer ("microservices for ten users"). Defense: explicit user-core-job articulation before scope is committed. The articulation is brief but concrete — "the user comes here to do X, and we'll know we've succeeded when they do X and come back."

**Related anti-patterns:** AP-3 (MVP for engineering convenience) (see `anti-patterns.md`)

---

## Rule 5.5: Decompose Against Real Constraints

**Statement:** Decomposition into milestones respects real constraints — team size, deadline, budget, dependencies, existing infrastructure, project mode, and the user's actual learning needs. Abstract "best practice" sequencing ("always start with infrastructure", "always do auth first", "always set up CI/CD before features") loses to real constraints. The right decomposition is the one that, against current constraints, produces a path the project can actually traverse.

**Citation:** `TGF-SYNTHESIS — grounded in PMBOK Guide 7th Ed (by reference, paywalled per DEC-2026-05-17-004 Clause 5) + AGILE-MFTO (responding to change over following a plan)`.

**Plain-language impact:** Abstract best-practice sequencing produces plans that look correct in principle but are unexecutable in practice. "Always start with infrastructure" applied to a deadline-pressured solo project means the deadline passes before any user-facing functionality ships. "Always do auth first" applied to a learning-MVP prototype means weeks of auth work for users who haven't yet validated they want the product. Real constraint awareness produces plans that ship; abstract advice produces plans that look pretty.

**Extended discussion:** Common categories of real constraint to surface during decomposition:

- **Team size.** A solo developer can't run a four-person Scrum cadence. A two-person team can't realistically maintain twelve concurrent services. Decomposition fits the team.
- **Deadline.** If there's a real deadline (demo day, customer commitment, funding milestone), it filters what fits. A 4-week deadline means infrastructure-first sequencing may not be feasible; user-value-first is the alternative.
- **Budget.** Decomposition that requires infrastructure spend that doesn't exist isn't a plan; it's a wish. Surface budget constraints early.
- **Dependencies.** Per Rule 5.6 — what depends on what? Some sequencing is dictated by dependency, not preference.
- **Existing infrastructure.** Brownfield context per Rule 5.3 — what's already deployed shapes what can be deferred.
- **Mode.** Greenfield validation-MVP work has different constraints than hardening-mode work. CLAUDE.md §15 (project mode) feeds in here.
- **Learning needs.** What does the project need to learn? Decomposition can prioritize the milestones that produce the most learning value early.

The discipline is making constraints explicit. A plan with no surfaced constraints is either a wish list (AP-2) or unconsciously constrained (worse — the constraints are operating invisibly).

**Related anti-patterns:** AP-6 (best-practice decomposition without constraints), AP-2 (aspirational ROADMAP) (see `anti-patterns.md`)

---

## Rule 5.6: Surface Dependencies Before Committing

**Statement:** Dependencies between milestones — X must complete before Y can start; Y depends on infrastructure Z being available; Y requires a decision in milestone W — are explicit in the ROADMAP at planning time. Hidden dependencies surface as slips (when X slips, Y blocks unexpectedly) or as rework (Y was started before X, and X's outcome changed Y's shape). Explicit dependencies enable conscious sequencing and accurate scheduling.

**Citation:** `TGF-SYNTHESIS — grounded in PMBOK Guide 7th Ed (by reference) + senior project planning practice`. PMBOK covers dependency planning at the discipline level; the rule operationalizes "make it explicit at planning time" for TGF's ROADMAP convention.

**Plain-language impact:** Hidden dependencies are how projects slip in surprising ways. Milestone Y is supposed to start next week; nobody noticed Y depends on a decision in X; X isn't done; Y has to wait; the whole sequence shifts. With explicit dependencies, the sequence is visible — slips compound visibly, schedule consequences are knowable, and re-sequencing decisions are conscious rather than reactive.

**Extended discussion:** Three categories of dependency commonly need surfacing:

- **Sequencing dependencies.** "Milestone Y cannot start until X is complete because Y builds on X's output." Example: "ROADMAP cannot be finalized until PROJECT-CONTEXT interview surfaces compliance scope."
- **Infrastructure dependencies.** "Milestone Y depends on infrastructure Z being deployed and available." Example: "Migration milestone depends on Postgres being deployed in staging."
- **Decision dependencies.** "Milestone Y requires a decision that won't happen until milestone W surfaces options." Example: "Vendor selection milestone depends on RFP results."

ROADMAP entries that name dependencies are operationally legible. Phrasings: "Depends on M3 (compliance scope)", "Requires Postgres deploy (vendor-log VEN-2026-04-01-002)", "Blocked on RFP completion (M2)".

For TGF projects specifically: the ROADMAP-discipline lives in CONTINUITY Rule 5.4 (ROADMAP reflects current reality); PROJECT-MANAGEMENT Rule 5.6 sets the discipline of putting dependencies in at planning time rather than discovering them at execution time.

**Related anti-patterns:** AP-5 (hidden dependencies), AP-8 (ROADMAP drift, when dependencies cause unrecorded re-sequencing) (see `anti-patterns.md`)

---
