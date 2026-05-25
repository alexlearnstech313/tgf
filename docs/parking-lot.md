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

*Last updated: 2026-05-25.*
