# Phase 3 Implementation Plan: Workflow Specification with Orchestration

**Date:** 2026-05-19
**Status:** Plan drafted; awaiting approval before WORKFLOW.md implementation.
**Process:** Per the agreed Phase 2 flow (Research → Plan → Implement → QC → Commit), adapted for Phase 3's synthesis-heavy nature.

---

## 1. Status Summary

Phase 3 produces a single deliverable: **`docs/WORKFLOW.md`** — the operational specification that Phases 4–12 (skills, hooks, meta-skills, hook library) build against. Estimated 800–1200 lines depending on worked-example depth.

WORKFLOW.md does *not* duplicate `CLAUDE.md` §3 (the operational contract that loads every session). Instead it specifies the implementation: per-stage I/O contracts, skill activation points, hook integration points, subagent dispatch contracts (including JSON output schemas), and worked examples.

The ROADMAP entry for Phase 3 names four scope items: per-stage orchestration patterns, subagent dispatch points, hook integration points, change tier scaling for review depth. WORKFLOW.md covers all four plus three derived items the spec needs to be load-bearing: stage-to-stage handoff contracts, workflow termination conditions, and the debugging-variant adaptation referenced in CLAUDE.md §3.

Per the approval given 2026-05-19:

- **Subagent JSON output schemas** defined here in Phase 3 (not deferred to Phase 11) — prevents 8 phases of implicit-contract drift
- **Worked examples** included — three across tiers (Trivial, Medium, Large)
- **Hook contracts** specified (input + exit semantics) but no script bodies — script bodies are Phase 12

---

## 2. Sources

Phase 3 is synthesis-heavy. Primary sources are internal artifacts already locked under DEC-003, DEC-004, and DEC-005. One external source needs re-verification for JSON I/O precision (Claude Code Hooks reference).

### Internal sources

| Source | Phase 3 use |
|--------|-------------|
| `CLAUDE.md` §3 The Workflow | Six-stage scaffolding; debugging variant scaffolding; per-stage operations |
| `CLAUDE.md` §11 Findings and Logging | Finding severity model that workflow stages produce against |
| `docs/ARCHITECTURE.md` §15 Mode-Aware Operation | Mode scaling tables per stage |
| `docs/ARCHITECTURE.md` §18 Hooks for Enforcement | Hook event taxonomy + I/O contract + universal hooks |
| `docs/ARCHITECTURE.md` §19 Token Efficiency | Cost-aware dispatch (tier scaling); path-based pre-filtering for Stage 3 |
| `docs/ARCHITECTURE.md` §20 Agent Orchestration | Seven subagent roles + two-stage spec/quality review + dispatch tiers + LLM06 mitigation + ATLAS techniques |
| `DECISIONS.md` DEC-2026-05-17-003 Clause 2 | Hook architecture (superseded by DEC-005 for events; stdin JSON / exit semantics / profile structure stand) |
| `DECISIONS.md` DEC-2026-05-17-003 Clause 3 | Seven subagent roles locked; schemas to be defined here |
| `DECISIONS.md` DEC-2026-05-17-005 | Actual PascalCase hook event names; `.claude/git-hooks/` separation |

### External source (re-verification)

| Source | Phase 3 use | Verification |
|--------|-------------|--------------|
| Claude Code — Hooks reference (current 2026) | Exact field names in hook stdin JSON (`session_id`, `cwd`, `permission_mode`, `hook_event_name`, plus event-specific `tool_name` / `tool_input` etc.); exact stdout JSON control fields (`continue`, `decision`, `additionalContext`); exit code semantics | Verified in Phase 2 (commit `92c9894`). Spot-check the additionalContext flow on `SessionStart` and the `continue`/`decision: block` control schema before defining hook contracts. Per DEC-004 Clause 4: research via Claude's web tools; no developer-machine downloads. |

### Comparative sources (design-rationale only, per DEC-004 Clause 6)

| Source | Phase 3 use |
|--------|-------------|
| Superpowers framework — six-phase workflow + two-stage subagent review pattern | Comparative validation of the spec/quality two-stage review pattern locked in ARCHITECTURE.md §20. Not a rule-source. Reference in WORKFLOW.md §Reference only, not as authority. |

No other comparative sources needed. Phase 3 doesn't introduce new rules requiring OWASP/NIST/ISO citation — it specifies stage I/O contracts that operationalize already-cited principles.

---

## 3. Surfaced Design Question

Research already surfaced one issue Phase 3 must resolve. Recording it here so WORKFLOW.md doesn't paper over it.

### How does TGF inject project_mode and change_tier into hooks?

ARCHITECTURE.md §18 reflects Claude Code's actual hook stdin JSON, which includes `session_id`, `cwd`, `permission_mode`, `hook_event_name`, and event-specific fields like `tool_name` / `tool_input`. It does **not** include `project_mode` (exploration/prototype/building/hardening/maintenance) or `change_tier` (trivial/small/medium/large) — these are TGF concepts, not Claude Code concepts.

DEC-003 Clause 2's original specification listed `project_mode` and `change_tier` as part of the hook stdin JSON — that was invented before consulting the canonical source. DEC-005 corrected the event names but didn't address how TGF context gets to hooks.

Three approaches, each with trade-offs:

- **A. File-based lookup.** Hooks read `.tgf/state/current.json` at runtime. Pros: simple, no Claude Code coupling, debuggable. Cons: race conditions if mode changes mid-session, extra file I/O per hook invocation.
- **B. SessionStart additionalContext injection.** A TGF `SessionStart` hook injects `project_mode` and `change_tier` into session context that downstream hooks could reference. Cons: `additionalContext` is for Claude's context, not hook-to-hook communication — wrong mechanism.
- **C. Environment variables set at session start.** TGF `SessionStart` hook exports `TGF_PROJECT_MODE` and `TGF_CHANGE_TIER` env vars; downstream hooks read them. Pros: standard pattern, no race conditions if set before any other hooks fire. Cons: `change_tier` is per-workflow-invocation, not per-session — env var would need re-setting.

**Resolution proposed for Phase 3:** A hybrid. `project_mode` lives in `.tgf/state/current.json` (file-based, set by `/tgf:set-mode` or PROJECT-CONTEXT inference). `change_tier` is determined per workflow invocation and passed by the orchestrator to hooks via either (i) the `hook_input` for tool-specific hooks at the moment the workflow stage fires, or (ii) the `additionalContext` mechanism on `PreToolUse` if Claude Code's spec allows. **This needs spot-check verification** during Phase 3 Step 1 research, before WORKFLOW.md defines hook contracts.

**Decision needed at Checkpoint 1:** approve the hybrid resolution or pick a different approach.

---

## 4. Per-Section Mini-Specs for WORKFLOW.md

Target structure. Section line targets are heuristics (per Phase 2 plan-adjustment lesson — content completeness against QC criteria matters more than line count).

### §1 Purpose and Scope (~30 lines)

- What WORKFLOW.md is for; relationship to CLAUDE.md §3 and ARCHITECTURE.md §20
- Who reads it (Phase 4–12 implementers; framework operators)
- What it does *not* cover (script bodies → Phase 12; skill content → Phases 4–10)

**QC criteria:**
- (a) Clear delineation from CLAUDE.md §3 (contract vs spec)
- (b) Clear delineation from ARCHITECTURE.md §20 (subagent role descriptions vs subagent dispatch contracts)

### §2 Conceptual Model (~50 lines)

- Six stages as a state machine; valid transitions; termination conditions
- Stage-to-stage handoff contracts (what Stage N produces that Stage N+1 consumes)
- Where skills evaluate (Stage 3 primarily; Stage 5 review subagents)
- Where hooks fire (across all stages; events distinct from stages)
- Where subagents dispatch (Stage 1 for Large; Stage 4 for Large with decomposition; Stage 5 always at Medium+)

**QC criteria:**
- (a) State machine is well-defined (no ambiguous transitions)
- (b) Handoff contracts are concrete (named artifacts/data passed)
- (c) Skill / hook / subagent locations clearly distinguished

### §3 Per-Stage Specifications (~400 lines total, ~65 per stage)

For each of Stage 1 (Research), Stage 2 (Scope), Stage 3 (Plan with Governance), Stage 4 (Implement), Stage 5 (Four-Pass Review), Stage 6 (Commit):

- **Inputs** — what context the stage receives
- **Operations** — what work happens (with mode and tier conditionals)
- **Outputs** — what artifacts the stage produces
- **Skill activation points** — when in the stage skills evaluate; what they receive
- **Hook integration points** — which Claude Code events fire during this stage; what each hook gets and is expected to return
- **Subagent dispatch points** — which roles dispatch in this stage at which tier; what context they receive; what schema they return
- **Failure modes** — what happens when stage outputs are insufficient (loop, escalate, halt, defer)

**QC criteria per stage:**
- (a) Inputs and outputs are concrete (named artifacts, not "context")
- (b) Skill / hook / subagent integration is explicit (cross-references to §4 schemas and §6 hook contracts)
- (c) Mode scaling differences are surfaced
- (d) Tier scaling differences are surfaced
- (e) Failure modes are enumerated (not just "if it fails")

### §4 Subagent Output Schemas (~150 lines)

JSON schema (or schema-like description) for each of the seven roles' output. Each role gets:

- Required fields with types and semantics
- Optional fields with conditions for inclusion
- Example output for a concrete change scenario

Roles: Researcher, Implementer, Code Reviewer, Security Auditor, Red Team, Holistic Reviewer, Verifier.

**Cross-cutting schema elements** all review subagents produce: `findings[]` with `severity`, `citation`, `plain_language_impact`, `location`, `subagent_attribution`; `spec_compliance` boolean + deviations; `quality` boolean + reasoning.

**QC criteria:**
- (a) Schemas are concrete enough to write JSON validators against
- (b) `findings[]` schema matches §11 of CLAUDE.md (severity model)
- (c) Subagent attribution preserved per ARCHITECTURE.md §20 (orchestrator never claims subagent findings as its own)
- (d) Two-stage spec/quality review pattern reflected in schema
- (e) Each role schema includes one worked example

### §5 Tier and Mode Scaling Tables (~80 lines)

Two reference tables:

**Tier scaling table.** Rows: Trivial, Small, Medium, Large. Columns: Stages active (which stages run), Subagents dispatched (per stage), Review depth (Phase 1-4 of four-pass), Skills evaluated (full vs filtered), Logging required (which artifacts updated).

**Mode scaling table.** Rows: Exploration, Prototype, Building, Hardening, Maintenance. Columns: Skill catalog gated (which categories load), Stage emphasis (which stages get more weight), Review focus (Phase 1-4 weighting), Waiver bar (low/standard/high), BASELINE-AUDIT cadence.

**Cross-table:** when both apply (e.g., Medium-tier change in Hardening mode), how do they compose? Mode gates skill catalog; tier scales subagent dispatch and review depth within whatever skills the mode allows.

**QC criteria:**
- (a) Tables are reference-grade (an implementer can read off what to do)
- (b) Composition rule (when both apply) is explicit
- (c) Defaults are clear (Building mode + Medium tier should be the obvious baseline)

### §6 Hook Integration Contracts (~120 lines)

For each Claude Code event TGF uses, the contract:

- Event name (PascalCase per DEC-005)
- TGF purpose (what TGF does in this event)
- Input contract (stdin JSON fields TGF relies on, beyond Claude Code's defaults)
- Expected exit semantics (when to exit 0 / 2 / other)
- Expected stdout (block reason + remediation when blocking; additionalContext when injecting)
- Which mode profiles invoke this hook (per ARCHITECTURE.md §18 profiles)

Events covered: `SessionStart`, `SessionEnd`, `PreToolUse`, `PostToolUse`, `SubagentStart`, `SubagentStop`, `FileChanged`, `ConfigChange`.

Plus the **TGF context injection mechanism** (resolved per §3 of this plan): how `project_mode` and `change_tier` reach hooks.

Plus the **three universal hooks** (`block-dangerous-git`, `block-secrets-commit`, `block-destructive-db`) — contract for each, including the user-acknowledgment override path.

**QC criteria:**
- (a) Each event contract is implementable (Phase 12 scripts can be written against it)
- (b) Mode-profile gating is explicit
- (c) TGF context injection is one of the three approaches (or a documented alternative)
- (d) Universal hooks specify their override semantics (per §5 of CLAUDE.md — hard refusal vs user-acknowledged proceed)

### §7 Debugging Variant (~50 lines)

How the six stages reshape when work is debugging rather than building (per CLAUDE.md §3 last paragraph). Stage names become: Reproduce → Isolate → Hypothesize → Test → Root-Cause → Verify-Fix. Four-pass review still applies to the fix.

**QC criteria:**
- (a) Each debugging stage maps to a building stage (reuse vs invention)
- (b) Subagent dispatch differences are spelled out (Researcher dispatched for reproduction; Verifier always invoked for AI-suggested fixes)
- (c) Termination criteria for debugging are explicit (when is the bug "fixed"?)

### §8 Worked Examples (~150 lines, ~50 per example)

Three end-to-end traces:

1. **Trivial:** Fix typo in CLAUDE.md. Stages run / skip; tier = Trivial; no subagents; minimal hooks; commit.
2. **Medium:** Refactor authentication middleware in a Next.js app. Stages run fully; tier = Medium; full four-pass review with 4 subagents in parallel; security/IAM skills load; commit + ROADMAP update.
3. **Large:** Add a new billing feature crossing trust boundaries (PII + payments + webhooks). Stages run with decomposition; tier = Large; Researcher subagents in Stage 1; Implementer subagents in Stage 4; full four-pass + Verifier for AI-generated portions; commit + DECISIONS update + ROADMAP update + WAIVER (if applicable).

Each example shows: which skills loaded, which subagents dispatched (with what context), which hooks fired (with what input/output), what artifacts updated, total findings count.

**QC criteria:**
- (a) Examples are concrete (real-looking code paths, not abstract)
- (b) Each example exercises a distinct tier and surfaces stage-specific behavior
- (c) Skill activation, subagent dispatch, hook firing are all traced
- (d) Examples reference back to §3 (per-stage spec) so they're verification, not duplication

### §9 Reference (~20 lines)

Cross-references to CLAUDE.md §3, ARCHITECTURE.md §15/§18/§19/§20, DECISIONS.md DEC-003/DEC-005, Claude Code Hooks reference. Comparative reference to Superpowers' two-stage review pattern per DEC-004 Clause 6.

**QC criteria:**
- (a) All cross-references resolve
- (b) Comparative references clearly labeled as comparative, not authoritative

---

## 5. Implementation Order

Dependency-driven:

1. §2 Conceptual Model — establishes the state machine that §3 builds on
2. §5 Tier and Mode Scaling Tables — establishes the matrices §3 references
3. §4 Subagent Output Schemas — establishes the contracts §3 dispatches against
4. §6 Hook Integration Contracts — establishes the contracts §3 fires
5. §3 Per-Stage Specifications — the bulk, builds on §2/§4/§5/§6
6. §7 Debugging Variant — references §3 stage structure
7. §8 Worked Examples — exercises everything above
8. §1 Purpose and Scope — written last with full context
9. §9 Reference — final, with all cross-refs resolvable

Drafting §1 last is intentional — it summarizes what §2–§8 contain, which is easier to write accurately after they exist.

---

## 6. Universal QC Criteria

Applied to every section. Per Phase 2 plan-adjustment, criterion #1 (skill section anchors) does NOT apply to WORKFLOW.md — it's a spec doc, not a skill.

1. ~~Section anchor present~~ (struck — applies only to skills)
2. Section is internally consistent (no claim contradicted later in the same section)
3. Section is consistent with CLAUDE.md, ARCHITECTURE.md, and DECISIONS.md (no contradictions with locked specs)
4. Plain-language impact present for any rule or contract (per CLAUDE.md §1 Contract)
5. Cross-references resolve (no dangling §X references)
6. Citations follow DEC-004 (rule-level precision; comparative sources separated)
7. No new authoritative rules introduced without source verification
8. Mode and tier behavior surfaced where relevant
9. Subagent attribution preserved (orchestrator vs subagent authority per ARCHITECTURE.md §20)
10. Failure modes addressed (not just success paths)

---

## 7. Open Decisions for Checkpoint 1

Approve, revise, or reject before implementation begins:

**Decision A — TGF context injection mechanism (§3 of this plan).** Approve the hybrid resolution (`project_mode` via `.tgf/state/current.json`; `change_tier` passed per workflow invocation), or pick alternative A/B/C.

**Decision B — Subagent output schema format.** Two options:
- (i) Inline JSON schema syntax (Draft 2020-12) — formal, validator-ready, more verbose
- (ii) TypeScript-style interface notation — compact, readable, easier to author but less validator-friendly

Lean: (ii) for readability; the schemas don't need runtime validation immediately. Phase 11 (Meta-Skills) can generate validators if needed.

**Decision C — Hook contract specifications: per-event or per-purpose?** Two organizing principles for §6:
- (i) Per-event sections (one section per `SessionStart`, `PreToolUse`, etc.) — mirrors Claude Code's mental model
- (ii) Per-purpose sections (safety hooks, workflow hooks, governance hooks) — mirrors TGF's profile structure

Lean: (i) per-event — Phase 12 implementers write scripts in `.claude/hooks/<EventName>/` directories, so the doc structure matching that is most useful at implementation time.

**Decision D — Worked example domains.** Lean toward generic examples (auth refactor, billing feature) over specific Alt-project examples (LabList, AdaptivIQ, BLETRAP). Generic examples are reusable as adopter-facing material. But specific examples would be richer.

Lean: generic. Phase 13 (Stack Baselines) is the right place for project-specific traces.

**Decision E — Commit grouping.** Options:
- (i) Single commit: full WORKFLOW.md at the end of implementation
- (ii) Two commits: structure (§1, §2, §4, §5, §6, §9) → content (§3, §7, §8)
- (iii) Three commits: scaffolding → per-stage spec → examples + closeout

Lean: (ii) — structure first lets the per-stage spec land against a stable scaffold; examples + closeout (§3/§7/§8) is the substantive work.

---

## 8. Out of Scope for Phase 3

Confirmed not in WORKFLOW.md:

- Hook script bodies (Phase 12)
- Skill content (Phases 4–10)
- Meta-skill implementation (Phase 11)
- Plugin marketplace / slash command implementations (Phase 14)
- Adopter-facing template version (deferred until WORKFLOW.md is stable; same pattern as ARCHITECTURE.md not having a template yet)

---

## 9. Estimated Effort

One focused session for implementation following plan approval, similar to Phase 2's pacing:

- Stage 1 spot-check (Claude Code Hooks reference re-verification for context injection question) — ~15 min
- Stage 3 implementation per §5 order above — ~3-4 hours
- Stage 5 four-pass review against per-section + universal QC criteria — ~45 min
- Stage 6 commit + ROADMAP/CHANGELOG closeout — ~15 min

Total: roughly one working day, comparable to Phase 2. Could split into two sessions if implementation surfaces design questions worth pausing on.

---

## 10. Closing Notes

- This plan is committed (per Phase 2 Decision 2 — transparency over staging)
- Phase 3 implementation does not begin until Decisions A–E are resolved at Checkpoint 1
- Plan adjustments accumulated during implementation will be logged in the Phase 3 session log (mirroring Phase 2's lesson-capture discipline)
- WORKFLOW.md becomes the load-bearing spec for Phases 4–12 — its quality matters more than its length
