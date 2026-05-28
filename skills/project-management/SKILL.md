---
# ─── Anthropic-native runtime fields (Claude Code honors these) ───
name: project-management
description: |
  Project planning discipline for greenfield projects (planning from intent)
  and brownfield projects (planning around existing codebase). Use when
  defining MVP scope, decomposing work into milestones, selecting stack
  components, planning dependencies, or supporting ROADMAP construction and
  revision. Pairs with DISCOVERY when input is ambiguous and with BASELINE-
  AUDIT (Phase 11 meta-skill) for non-trivial brownfield assessments.
paths:
  - "**/ROADMAP*"
  - "**/PROJECT-CONTEXT*"
  - "**/*"

# ─── TGF-extension metadata (Phase 11 meta-skills read these; Claude Code ignores) ───
applies-when:
  paths-include:
    - "**/ROADMAP.md"
    - "**/PROJECT-CONTEXT.md"
    - "**/docs/phase-*-plan.md"
  operations-include:
    - greenfield planning from project intent
    - brownfield planning against existing codebase
    - MVP scope definition or revision
    - milestone decomposition or re-sequencing
    - stack component selection
    - dependency planning between milestones
    - ROADMAP construction or material update
disqualifying-when:
  - tactical code edit with no scope or roadmap implication
  - debugging an established issue (use DEBUGGING)
  - editing a single file with bounded scope
  - documentation-only changes within an established artifact
sources:
  - NIST SP 800-218 v1.1 (SSDF) — PO.1 Define Security Requirements, PO.2 Implement Roles and Responsibilities, PO.3 Implement Toolchain (verified 2026-05-17 Phase 2)
  - Agile Manifesto (2001) — 4 values + 12 principles; stable methodology reference
  - Eric Ries — "The Lean Startup" (2011); comparative source per DEC-2026-05-17-004 Clause 6 (book; design-rationale only)
  - PMBOK Guide 7th Edition (2021); paywalled; cited by reference per DEC-2026-05-17-004 Clause 5
last-generated: 2026-05-20
refresh-recommended: 2027-05-20
self-evolution:
  anti-patterns-observed: []
  triggers-refined: []
  ai-failures-documented: []
---

# PROJECT-MANAGEMENT

> **Skill body ≤300 lines** (per `DEC-2026-05-19-007`). Principles, rule summaries, and navigation live here. Full content in reference files loaded on demand:
> - `rules.md` — full rules with citations
> - `anti-patterns.md` — full anti-pattern + canonical pattern pairs with concrete examples

<!-- SECTION: overview -->
## §1 Overview

PROJECT-MANAGEMENT governs the planning dimension of TGF projects: defining what to build, in what order, against what constraints, with what stack, and how the ROADMAP reflects the result. It operates in two distinct modes — **greenfield** (planning from project intent through MVP and beyond) and **brownfield** (planning around an existing codebase, often after a BASELINE-AUDIT).

This is an **activity skill** in TGF (loads on context per `CLAUDE.md` §9), not always-on. It activates when work shifts to planning-stage operations: ROADMAP construction, milestone decomposition, MVP scoping, stack selection, dependency surfacing. Pairs with DISCOVERY when input is ambiguous and with BASELINE-AUDIT (Phase 11) for substantial brownfield work.

Most PROJECT-MANAGEMENT rules are TGF synthesis of senior planning practice grounded in NIST SSDF PO-series practices, the Agile Manifesto's iterative-planning posture, and standard product-management discipline on MVP definition. Per `DEC-2026-05-17-004`, TGF synthesis is acknowledged honestly rather than fabricating sub-rule citations where the source provides only practice-level guidance.
<!-- /SECTION: overview -->

<!-- SECTION: sources -->
## §2 Authoritative Sources

| Source ID | Reference | Version | Date Verified |
|-----------|-----------|---------|---------------|
| NIST-SSDF | [NIST SP 800-218 SSDF](https://csrc.nist.gov/pubs/sp/800/218/final) — PO.1 Define Security Requirements, PO.2 Implement Roles and Responsibilities, PO.3 Implement Toolchain | v1.1 | 2026-05-17 (Phase 2) |
| AGILE-MFTO | [Agile Manifesto](https://agilemanifesto.org) — 4 values + 12 principles | 2001 (stable methodology) | reference (stable) |
| PMBOK | PMBOK Guide — Project Management Body of Knowledge (paywalled; cited by reference) | 7th Ed (2021) | reference only |

Citation granularity per Phase 4 Checkpoint 1 Decision A: NIST SSDF cited at practice level (PO.1, PO.2, PO.3); Agile Manifesto cited at the values/principles level; PMBOK cited by reference (paywalled per `DEC-2026-05-17-004` Clause 5). Most PROJECT-MANAGEMENT rules are TGF synthesis of senior planning practice — citation honest per Decision A.

Eric Ries' "The Lean Startup" (2011) is referenced as comparative source per `DEC-2026-05-17-004` Clause 6 — design-rationale only, not in the citation table.
<!-- /SECTION: sources -->

<!-- SECTION: discovery -->
## §3 Discovery Commands

Copy-pasteable commands to capture planning-state before applying PROJECT-MANAGEMENT rules.

```bash
# Confirm canonical planning artifacts exist
for f in ROADMAP.md PROJECT-CONTEXT.md DECISIONS.md; do
  [ -f "$f" ] && echo "✓ $f ($(wc -l < $f) lines)" || echo "✗ $f (missing)"
done

# Most recent ROADMAP update (staleness check)
test -f ROADMAP.md && stat -c "%y" ROADMAP.md 2>/dev/null

# Count completed vs active milestones
grep -c "^| M" ROADMAP.md 2>/dev/null
grep -E "✅ Complete|🟡 In progress|⬜ Not started" ROADMAP.md 2>/dev/null | sort | uniq -c

# Look for greenfield vs brownfield indicators
test -f docs/BASELINE-AUDIT.md && echo "BASELINE-AUDIT exists → likely brownfield" || echo "no BASELINE-AUDIT → likely greenfield"

# Identify in-flight phase plans
ls -1 docs/phase-*-plan.md 2>/dev/null | head -5
```
<!-- /SECTION: discovery -->

<!-- SECTION: principles -->
## §4 Universal Principles

Six principles that ground every numbered rule.

- **Start from intent, not from patterns.** Planning begins with "what is the user trying to accomplish?" not with "what's the standard architecture for X?" Patterns inform the path; they don't define the destination. An MVP for a payment-processing app is fundamentally different from an MVP for an internal admin tool, even if they share many architectural patterns.

- **Greenfield and brownfield are different modes, not the same plan.** Greenfield projects flow from intent through validation-MVP to growth state — work proceeds from a blank slate against future user needs. Brownfield projects start with the existing codebase as constraint — work proceeds against what's there. Treating brownfield as "greenfield with extra files" produces plans that ignore real constraints.

- **MVP serves users, not engineering ego.** Minimum Viable Product is the smallest thing that delivers value to actual users — not the smallest thing engineers can ship. Over-scoping (shipping too much) and under-scoping (shipping a tech demo with no user value) are failures of the same rule. The discipline is identifying the user's core job and shipping that.

- **Decompose against real constraints, not against abstract best practice.** "Always start with infrastructure" is abstract advice that loses to deadlines, team size, and existing dependencies. Decomposition into milestones respects real constraints — what the team can ship, what's already available, what the deadline allows.

- **Surface dependencies before committing.** Dependencies between milestones (X must happen before Y; Y depends on Z being available) are explicit in the ROADMAP. Hidden dependencies surface as slips; explicit dependencies enable conscious sequencing. The cost of writing the dependency down is small; the cost of discovering it at milestone-launch time is large.

- **ROADMAP is committed-to, not aspirational.** Items in the ROADMAP are work the project is doing. Wish lists belong elsewhere (a separate IDEAS doc, a backlog, a future-considerations section). Per CONTINUITY Rule 5.4, the ROADMAP reflects current reality — both what's being done and what's been done. Aspirational ROADMAPs that confidently mislead are worse than no ROADMAP.
<!-- /SECTION: principles -->

<!-- SECTION: rules -->
## §5 Rule Summaries

Six rules. Each summary: title + 1-line statement + source identifier.

<!-- RULE: 5.1 -->
- **Rule 5.1: Start from Intent, Not from Patterns** — Planning begins with the user's actual goal, not with the standard architecture for the domain. Patterns inform the path; they don't define the destination. `TGF-SYNTHESIS — grounded in AGILE-MFTO + senior product practice` → [`rules.md#rule-51-start-from-intent-not-from-patterns`](rules.md)
<!-- /RULE: 5.1 -->
<!-- RULE: 5.2 -->
- **Rule 5.2: Greenfield Mode — Plan from Intent Through MVP and Beyond** — Greenfield projects produce a roadmap that flows from project intent → validation-MVP → growth state. Each milestone is committed-to (not aspirational); the path is iterative per AGILE-MFTO. `TGF-SYNTHESIS — grounded in AGILE-MFTO + NIST-SSDF v1.1 PO.1` → [`rules.md#rule-52-greenfield-mode`](rules.md)
<!-- /RULE: 5.2 -->
<!-- RULE: 5.3 -->
- **Rule 5.3: Brownfield Mode — Plan Around Existing Reality** — Brownfield projects start with the existing codebase as constraint. Plans operate AGAINST what's there, not WITH a fresh-greenfield assumption. Non-trivial brownfield work triggers BASELINE-AUDIT (Phase 11) before significant planning. `TGF-SYNTHESIS — grounded in senior practice on legacy-system planning` → [`rules.md#rule-53-brownfield-mode`](rules.md)
<!-- /RULE: 5.3 -->
<!-- RULE: 5.4 -->
- **Rule 5.4: MVP Serves Users, Not Engineering Ego** — Minimum Viable Product is the smallest thing that delivers value to actual users — not the smallest thing engineers can ship. Over-scoping (gold-plating) and under-scoping (tech demo with no user value) are failures of the same rule. `TGF-SYNTHESIS — grounded in Lean Startup (2011, comparative) + senior product practice` → [`rules.md#rule-54-mvp-serves-users-not-engineering-ego`](rules.md)
<!-- /RULE: 5.4 -->
<!-- RULE: 5.5 -->
- **Rule 5.5: Decompose Against Real Constraints** — Decomposition respects real constraints — team size, deadline, budget, dependencies, project mode. Abstract "best practice" sequencing ("always start with infrastructure", "always do auth first") loses to real-world constraint pressure. `TGF-SYNTHESIS — grounded in PMBOK 7th Ed (by reference) + AGILE-MFTO` → [`rules.md#rule-55-decompose-against-real-constraints`](rules.md)
<!-- /RULE: 5.5 -->
<!-- RULE: 5.6 -->
- **Rule 5.6: Surface Dependencies Before Committing** — Dependencies between milestones (X must happen before Y; Y depends on Z available) are explicit in the ROADMAP at planning time. Hidden dependencies surface as slips; explicit dependencies enable conscious sequencing. `TGF-SYNTHESIS — grounded in PMBOK (by reference) + senior practice` → [`rules.md#rule-56-surface-dependencies-before-committing`](rules.md)
<!-- /RULE: 5.6 -->

See `rules.md` for full rule text, citations, plain-language impact, and extended discussion.
<!-- /SECTION: rules -->

<!-- SECTION: anti-patterns -->
## §6 Anti-Pattern Summaries

Eight anti-pattern pairs covering the most common planning failures.

<!-- ANTI-PATTERN: AP-1 -->
- **AP-1: Architecture-first planning** — Starting from infrastructure or stack choices ("we'll use Next.js + Postgres + Vercel") before user intent is articulated. Violates Rule 5.1. → [`anti-patterns.md#ap-1-architecture-first-planning`](anti-patterns.md)
<!-- /ANTI-PATTERN: AP-1 -->
<!-- ANTI-PATTERN: AP-2 -->
- **AP-2: Aspirational ROADMAP** — Items added to ROADMAP that aren't committed-to (wish list, "would be cool"). Confidently misleads future readers. Violates principle "ROADMAP is committed-to, not aspirational" + CONTINUITY Rule 5.4. → [`anti-patterns.md#ap-2-aspirational-roadmap`](anti-patterns.md)
<!-- /ANTI-PATTERN: AP-2 -->
<!-- ANTI-PATTERN: AP-3 -->
- **AP-3: MVP defined for engineering convenience** — Smallest thing engineers can ship rather than smallest thing that delivers user value. Tech demo with no real user. Violates Rule 5.4. → [`anti-patterns.md#ap-3-mvp-for-engineering-convenience`](anti-patterns.md)
<!-- /ANTI-PATTERN: AP-3 -->
<!-- ANTI-PATTERN: AP-4 -->
- **AP-4: Brownfield plan ignoring existing reality** — Greenfield-style plan applied to a brownfield codebase. Plans against what should exist, not what does. Violates Rule 5.3. → [`anti-patterns.md#ap-4-brownfield-ignoring-existing-reality`](anti-patterns.md)
<!-- /ANTI-PATTERN: AP-4 -->
<!-- ANTI-PATTERN: AP-5 -->
- **AP-5: Hidden dependencies** — Milestone B silently requires milestone A to complete first; the dependency isn't surfaced until A slips and B blocks. Violates Rule 5.6. → [`anti-patterns.md#ap-5-hidden-dependencies`](anti-patterns.md)
<!-- /ANTI-PATTERN: AP-5 -->
<!-- ANTI-PATTERN: AP-6 -->
- **AP-6: Best-practice decomposition without constraint awareness** — "Always start with infrastructure" applied to a deadline-constrained project that needs user-facing functionality first. Abstract best-practice loses to real constraints. Violates Rule 5.5. → [`anti-patterns.md#ap-6-best-practice-without-constraints`](anti-patterns.md)
<!-- /ANTI-PATTERN: AP-6 -->
<!-- ANTI-PATTERN: AP-7 -->
- **AP-7: Stack-first selection** — Technology chosen before requirements are clear (e.g., "we'll use Kubernetes" before traffic estimates or deployment cadence are known). Violates Rule 5.1. → [`anti-patterns.md#ap-7-stack-first-selection`](anti-patterns.md)
<!-- /ANTI-PATTERN: AP-7 -->
<!-- ANTI-PATTERN: AP-8 -->
- **AP-8: ROADMAP drift left unchallenged** — Committed-to ROADMAP items diverge from reality; planning rounds pretend the original sequencing is still valid. Cross-references CONTINUITY Rule 5.4. → [`anti-patterns.md#ap-8-roadmap-drift-unchallenged`](anti-patterns.md)
<!-- /ANTI-PATTERN: AP-8 -->

Per `DEC-2026-05-17-003` Clause 1: every anti-pattern is paired with a canonical pattern in `anti-patterns.md`.
<!-- /SECTION: anti-patterns -->

<!-- SECTION: ai-concerns -->
## §7 AI-Specific Concerns

Planning failure modes specific to AI-assisted development.

- **AI under-scopes for shipping speed.** AI-generated MVP scopes often optimize for "smallest thing that compiles and runs" — which can be a tech demo with no real user value (AP-3 territory). The user gets a working artifact that doesn't do what they need. Defense: Rule 5.4 — MVP serves USERS not engineering ego.

- **AI over-engineers in the opposite direction.** Inverse failure: AI proposes elaborate architectures (microservices, event sourcing, GraphQL federation) for a project that doesn't yet have ten users. Pattern reproduction from training data over-represents the architecture of mature, large-scale projects. Defense: Rules 5.1 and 5.5 — start from intent; decompose against real constraints.

- **AI treats brownfield as greenfield.** AI may produce plans that assume a fresh slate even when the user described an existing codebase. The existing constraints get ignored, and the resulting plan is impossible to execute without significant rework. Defense: Rule 5.3 and explicit brownfield-mode signaling.

- **AI surfaces dependencies inconsistently.** AI may name some dependencies and miss others, producing ROADMAPs where the dependency graph is half-explicit. Defense: explicit dependency review during Stage 1 Research and Stage 2 Scope; PROJECT-MANAGEMENT activates at both stages for planning-shaped work.

Relevant external taxonomies: OWASP LLM Top 10:2025 `LLM06:2025` (Excessive Agency — AI taking planning decisions beyond its scope) and `LLM09:2025` (Misinformation — AI confidently proposing plans grounded in fabricated context).
<!-- /SECTION: ai-concerns -->

<!-- SECTION: workflow -->
## §8 Workflow Integration

How PROJECT-MANAGEMENT participates in the six-stage workflow (per `docs/WORKFLOW.md`).

- **Stage 1 (Research):** Activates for planning-shaped prompts. Runs §3 discovery commands; checks ROADMAP / PROJECT-CONTEXT / DECISIONS for prior context. Triggers DISCOVERY if input is ambiguous (DISCOVERY Rule 5.1) and BASELINE-AUDIT (Phase 11) for non-trivial brownfield assessments.
- **Stage 2 (Scope):** Primary activation point. Scope definition for any planning-shaped work happens here; the four scope components per DISCOVERY Rule 5.5 plus dependency surfacing per PROJECT-MANAGEMENT Rule 5.6.
- **Stage 3 (Plan with Governance):** Rules 5.4 (MVP) and 5.5 (constraint-aware decomposition) contribute when the change includes MVP definition or milestone re-sequencing.
- **Stage 4 (Implement):** Generally not active during implementation. Re-engages if implementation reveals a planning issue (e.g., dependency not surfaced; scope creep).
- **Stage 5 (Four-Pass Review):** Holistic Reviewer references PROJECT-MANAGEMENT principles when checking ROADMAP alignment of a change.
- **Stage 6 (Commit):** ROADMAP updates per CONTINUITY Rule 5.4 are surfaced for any commit that materially affects milestones.
<!-- /SECTION: workflow -->

<!-- SECTION: subagent-context -->
## §9 Subagent Context

**Preloaded by:** `holistic-reviewer` (Phase 4) — the full skill content injects into the holistic-reviewer subagent context at startup via its `skills:` frontmatter (verified in `agents/holistic-reviewer.md`), used when checking ROADMAP alignment during Stage 5 Phase 4 review. PROJECT-MANAGEMENT also activates at the orchestrator level during Stage 1/Stage 2 planning operations. *(Corrected WS5: the prior "None directly … does not preload the full skill" predated the Workstream-3 agent wiring, 2026-05-26.)*

**Critical rules for orchestrator use (when not preloaded):**

- Rule 5.1 (Start from Intent, Not from Patterns)
- Rule 5.4 (MVP Serves Users, Not Engineering Ego)
- Rule 5.6 (Surface Dependencies Before Committing)

**Top AI-specific concerns:**

- AI under-scopes for shipping speed (tech-demo MVP with no user value)
- AI over-engineers in the opposite direction (microservices for ten-user MVP)
- AI treats brownfield as greenfield (ignores existing constraints)

Reference files (`rules.md`, `anti-patterns.md`) load on demand within the orchestrator if a specific planning scenario warrants deep rule application.
<!-- /SECTION: subagent-context -->
