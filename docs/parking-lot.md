# Parking Lot

Ideas worth preserving but not in scope for current build. Captured here so they survive ROADMAP phase transitions without re-litigation. Each entry includes the rationale for parking and the conditions that would trigger revisit.

> Parking lot ≠ commitment. Items here may never ship. Revisit triggers are evidence-based — actual usage signals from Phase 16 self-validation or post-v1 operational data, not speculation.

---

## Capability-scoped action enforcement

**Origin:** 2026-05-25 brainstorm — reframe of "PKI between user and orchestrator" from external Claude.ai conversation. Underlying intuition: external content (fetched docs, MCP responses, file contents) should never be able to elevate itself to instruction status; user prompts should carry verifiable authorization scope that hooks enforce at the action layer.

**Why parked:**
- Research direction, not v1 deliverable. Needs prototype on a single tool gate (e.g., file writes) before framework integration.
- Risk of theatrical security or constant false-positive blocks if scope-inference quality is poor.
- TGF's 16-phase plan ships first; integration into v1 would constitute identity drift toward "capability-security research project."
- Current defenses (M15 URL allow-list, hook-layer tool gates, system-prompt boundaries) already address the most common content-injection vectors. Marginal value of the capability layer is unproven.

**Revisit trigger:** Phase 16 self-validation (60-90 days on LabList / AdaptivIQ / BLETRAP) reveals content-level prompt injection as an observed problem in real usage. Or independent research (Simon Willison's prompt-injection work, Anthropic alignment publications, academic agent-sandboxing work) ships a productionizable pattern.

**Prerequisite for revisit:** Standalone prototype on one tool gate with minimum-viable scope envelope (paths + operation types + max file count) validated on real prompts before framework architecture work begins.

**Rejected approach:** Literal PKI design with Ed25519 keypairs per subagent (orchestrator key, code-reviewer key, security-auditor key, etc.). Within a single trust boundary (the local machine), cryptographic signatures add ceremony, not security. If the local environment is compromised, all keys are compromised. The interesting problem is *intent authorization*, not *identity authentication*.

---

## Centralized `~/claude-memory/` storage

**Origin:** 2026-05-25 brainstorm — proposal to move per-project operational data (logs, sessions, accountability, telemetry) out of `.tgf/state/` and `.sessions/` into a centralized `~/claude-memory/<project>/` structure to enable cross-project analysis.

**Why parked:**
- Pivot cost too high — `dc2b294` (Workstream 1, 2026-05-22) just shipped research-security infrastructure using `.tgf/state/` per-project. Moving it invalidates substantial recent work.
- Per-project storage is a feature, not a bug: scope of data matches scope of project. Clean retention boundaries on project end.
- Centralization creates a single high-value compromise target. TeamPCP-class malware that targets `~/.claude/` would target `~/claude-memory/` equally.
- Cross-project analysis is solvable later with an aggregation tool that *reads* per-project `.tgf/state/` directories. Doesn't require restructuring storage.

**Revisit trigger:** Real cross-project usage on LabList + AdaptivIQ + BLETRAP reveals concrete need for aggregated views that per-project storage can't serve well.

**Lower-cost alternative:** Build an optional aggregation tool post-v1 that reads per-project state and produces cross-project analytics, without changing where state is stored.

---

## Full PKI-signed accountability logs

**Origin:** 2026-05-25 brainstorm — proposal for hash-chained, multi-key signed audit logs (user key → orchestrator key → subagent keys, every action signed and chain-verified for tamper detection).

**Why parked:**
- Theatrical security within a single trust boundary. Same reasoning as capability-scoped action enforcement rejection above.
- Violates solo-maintainability standard (CLAUDE.md §1). Key lifecycle, rotation, recovery, and multi-machine sync are substantial engineering surface area for one maintainer.
- Scoped subagent activity logs (planned for Workstream 3) capture the useful 80% — structured JSON of what each review subagent was dispatched to do and what it found — without cryptographic ceremony.

**Revisit trigger:** Compliance scope (HIPAA, PCI-DSS, SOC 2) on a TGF-managed project specifically requires tamper-evident audit logs as audit evidence, AND existing activity logs are demonstrably insufficient for that purpose.

**Probability of revisit:** Low. Most compliance frameworks accept signed timestamps + access-controlled retention without requiring cryptographic chain integrity at log-entry granularity.

---

## "Instincts" layer (immediate pattern-match reflexes)

**Origin:** 2026-05-25 brainstorm — proposal for a layer between always-on skills and observed behavior; immediate pattern-match responses ("see SQL string concatenation → apply parameterized-query response") that fire faster than full skill consultation.

**Why parked:**
- Confusing architectural distinction from always-on skills. Always-on skills already serve as constantly-loaded foundational rules; adding another layer with similar function blurs the architecture.
- No evidence that always-on skills are too slow or too heavy for the failure modes "instincts" would catch.
- Phase 4 always-on skills (CODE-QUALITY, SECURITY-CORE, CONTINUITY) already contain anti-pattern and rule sections that operate at the "reflex" level conceptually.

**Revisit trigger:** Observed failure mode where always-on skills load but Claude bypasses them under conversational pressure, AND a clear architectural distinction emerges that would justify a separate layer.

**Probability of revisit:** Low. More likely the existing always-on skill anti-pattern sections get refined as the right home for reflex-level rules.

---

## Multi-language framework translation

**Origin:** 2026-05-25 brainstorm — observation that competing frameworks ship with translations (10+ languages) to drive international adoption.

**Why parked:**
- v1 is English-only by design.
- Translation is significant ongoing maintenance work — every framework update requires translation updates across all maintained locales.
- Not the right v1 priority for a solo maintainer.

**Revisit trigger:** v1 gains adoption traction warranting investment in localization. International contributors offer to maintain translations.

**v1 hedge:** Write CLAUDE.md and skills in clear English that translates well — avoid idioms, regional references, unnecessarily complex constructions. Lowers future translation cost without doing translation work now.

---

## Centralized cross-project agent-activity dashboards

**Origin:** 2026-05-25 brainstorm — query interface for "show me what the security-auditor agent has flagged across all my projects."

**Why parked:**
- Prerequisite — per-project subagent activity logs (Workstream 3) — doesn't exist yet.
- Aggregation tooling is post-v1 by design (see centralized storage entry above).

**Revisit trigger:** WS3 ships per-project activity logs; Phase 16 self-validation reveals cross-project queries as a real operational need.

---

## Active project-management: plan presentation + project direction/coordination

**Origin:** 2026-05-28 discussion (during WS4 Build Step 4 audit of `skills/project-management/`). Two related ideas about elevating PROJECT-MANAGEMENT from a passive load-on-context advisory skill toward an active role:

1. **Plan presentation for at-a-glance comprehension.** The skill ensures a plan is *sound* (constraint-fit, dependencies explicit, MVP scoped) but says nothing about whether it is *legible*. Proposal: a Kanban-flavored ROADMAP presentation — status columns / the existing `✅ 🟡 ⬜` markers, a "current focus" callout, text dependency arrows — so the user can track progress visually. Aids governance and momentum, especially for a solo founder.
2. **Active project direction/coordination.** Imagine project-management as an actual project manager that *juggles and coordinates the moving parts* — notices slips, surfaces blocked dependencies, keeps the ROADMAP current, recommends next focus — rather than only advising when asked. The user raised whether this warrants a dedicated agent or other architecture.

**Why parked:**
- WS4 is audit-only; this is new-feature/enhancement work, out of WS4 (and WS5-remediation) scope. Captured now so it survives to the right build window.
- The high-value, low-complexity core needs no new component: **orchestrator-exercised coordination at session boundaries** (session-start "where the project stands / what's blocked / what's next" briefing + session-close ROADMAP reconciliation), guided by project-management + CONTINUITY. Estimated ~80% of the "active PM" value at ~10% of the complexity. Close to what CONTINUITY's session discipline + the skill's §3 discovery commands already gesture at.
- TGF agents are **stateless, task-scoped, read-only dispatches** (the four review agents). "Juggling and coordinating" wants *persistence + proactivity* — which is the orchestrator + persistent artifacts (ROADMAP, session logs), NOT a stateless subagent. A dedicated PM agent earns its place only when coordination gets heavy enough to need context-isolation or must run *off-session* (e.g., a scheduled check that pings on stale ROADMAP / approaching deadline).
- "Make it an agent" must clear the skill's own constraint-fit bar — Rule 5.5 (decompose against real constraints), design Rule 5.3 (simplest that meets constraints), Rule 5.4 (accommodate change, don't anticipate). No evidence yet that the orchestrator-cadence version is insufficient.

**Hard constraint on any visual board:** it must BE the source-of-truth ROADMAP (or be auto-derived from it), never a parallel board kept by hand — a stale board is exactly the AP-2 (aspirational ROADMAP) / AP-8 (ROADMAP-drift) failure project-management already warns against. A stale Kanban is worse than no Kanban. (Note: §8 says ROADMAP is "not a Gantt chart" — Kanban is status-by-column, not date-precise, so this does not conflict.)

**Placement question (resolve at revisit):** (a) the **ROADMAP artifact format** (CLAUDE.md §8 / CONTINUITY) is the natural home for the visual/status spec [lean]; (b) project-management carries a one-line presentation *principle* pointing to it; (c) the "does an active PM warrant a dedicated subagent?" question goes to **Phase 11 (orchestration meta-skill)** — the same place debugging §9 parks its "dedicated debugger subagent?" question. Do NOT mandate external tools (GitHub Projects / Linear); recommend optionally, keep tool choice user-preference (§5 light-touch).

**Revisit trigger:** Phase 16 self-validation (60–90 days on LabList / AdaptivIQ / BLETRAP) reveals either (a) plans are hard to track at a glance in real use, or (b) project-coordination strain the orchestrator-cadence version can't carry — at which point evaluate the dedicated PM agent / scheduled status-check architecture at Phase 11. Build the orchestrator-cadence + visual ROADMAP first regardless; promote to an agent only on evidence.

---

*Last updated: 2026-05-28.*
