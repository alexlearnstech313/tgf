# Decisions

Architectural decision records (ADRs) for The Governance Framework. Newer decisions appear at the top.

Each decision captures: what was decided, when, why, what alternatives were considered, and downstream consequences.

---

## DEC-2026-05-17-001: Framework name

**Decided:** "The Governance Framework" (acronym: TGF).

**Date:** 2026-05-17

**Context:** Project began as "Trust and Governance Framework" — emphasizing the GRC/trust angle. During design conversation, alternative "The Governance Framework" emerged with cleaner, more confident positioning.

**Decision:** "The Governance Framework." The acronym TGF is preserved. The definite article signals confidence and category clarity without overclaiming or coupling to a specific framing (trust, security, GRC, etc.).

**Alternatives considered:**

- "Trust and Governance Framework" — anchored to GRC/trust framing; longer; arguably narrower.
- "TGF" alone — too opaque without expansion; loses positioning value in titles and search.

**Consequences:** Affects every public-facing artifact (README, LICENSE attribution, plugin manifests, slash command namespace `/tgf:*`, documentation). Internal acronym `TGF` carries forward unchanged.

---

## DEC-2026-05-17-002: Path A — full v1 scope

**Decided:** Build the full v1 including hooks for enforcement, agent orchestration, sub-agent code review, self-evolving knowledge, token efficiency mechanisms, and continual improvement — not a minimal v1 with these deferred to v2.

**Date:** 2026-05-17

**Context:** Two-path decision presented during design conversation:

- **Path A** — full v1 (~30-50 weeks part-time) with all advanced capabilities as foundational architecture.
- **Path B** — minimal v1 (~2-3 months) shipping core framework first, advanced capabilities added in v2 based on real-use feedback.

**Decision:** Path A. Most TGF work is markdown content production with AI assistance; the timeline differential between paths is smaller than enterprise-software intuition suggests. Path A positions TGF competitively against existing public frameworks (Superpowers ~41k stars, great_cto, etc.) where shipping less polished work risks irrelevance in a crowded space.

**Alternatives considered:**

- Path B — would ship faster and let real use inform v2; trades early adoption competitiveness for time-to-public.
- Hybrid (ship Path B as v1, build Path A capabilities as v1.1-v1.5) — adds release management overhead.

**Consequences:** ~80-110 focused sessions of work across 16 phases. Higher coherence cost; higher upside if framework gains traction. Phase 0 architectural decisions reflect Path A scope.

---

## DEC-2026-05-17-003: Phase 0 architectural decisions locked

**Decided:** Five interface specifications are locked as foundational architecture. Every subsequent phase builds against them.

**Date:** 2026-05-17

**Context:** Before any skill content production, interface decisions need to be stable. Otherwise downstream work either has to be redone or accumulates inconsistency.

**Decision:** The following interfaces are locked.

### 1. Skill template with addressable section anchors

HTML comment anchors (`<!-- SECTION: ... -->`, `<!-- RULE: 5.1 -->`, `<!-- ANTI-PATTERN: AP-1 -->`, `<!-- CANONICAL: CP-1 -->`) enable section-level loading rather than full-file loading.

**Required sections (every skill):** `overview`, `sources`, `discovery`, `principles`, `rules` (≥5), `anti-patterns` (≥8), `canonical-patterns` (paired with anti-patterns), `ai-concerns`, `workflow`, `subagent-context`.

**Required frontmatter fields:** `name`, `description`, `applies-when` (with sub-fields `paths-include`, `imports-include`, `operations-include`, `data-flows-include`), `disqualifying-when`, `sources` (with versions), `last-generated`, `refresh-recommended`, `self-evolution` (with `anti-patterns-observed`, `triggers-refined`, `ai-failures-documented`).

### 2. Hook architecture

Shell scripts in `.claude/hooks/<event>/NN-name.sh`. Events: `pre-tool-use`, `post-tool-use`, `pre-commit`, `post-commit`, `session-start`, `session-end`, `pre-skill-modification`. Numeric prefix orders execution within event.

Hooks receive standardized JSON via stdin (event, timestamp, session_id, project_mode, change_tier, tool, tool_args, context). Exit 0 = allow; non-zero = block. Block hooks emit JSON on stdout: `{block, reason, details, remediation}`. Mode-aware profiles in `.claude/hooks/profile.json`. Three universal hooks always active: block-dangerous-git, block-secrets-commit, block-destructive-db.

### 3. Subagent role contracts (seven roles)

`Researcher`, `Implementer`, `Code Reviewer`, `Security Auditor`, `Red Team`, `Holistic Reviewer`, `Verifier`. Each has specified context inputs and structured JSON output. Cost-aware orchestration scales by change tier: Trivial = no subagents; Small = Code Reviewer + Holistic; Medium = all four review subagents; Large = full orchestration plus Researchers (stage 1), Implementers (stage 4 decomposition), and Verifier for AI-generated portions.

### 4. Self-evolution data structures

Lives in `.tgf/evolution/` (gitignored). Three directories: `observations/` (raw), `proposals/{pending,accepted,rejected}/`, `confidence-thresholds.json`. Confidence levels: low (1-2 observations), medium (3-9), high (10+).

**Can evolve via human-reviewed proposals:** anti-patterns, trigger criteria, AI-specific concerns, stack-skill patterns.

**Cannot auto-evolve:** numbered rules, authoritative source citations, framework principles, hard refusal list. Human review required via `/tgf:review-evolution`.

### 5. Token telemetry format

Lives in `.tgf/telemetry/sessions/*.json` (gitignored). Per session captures: `session_id`, `started`, `ended`, `project_mode`, `workflow_invocations[]` (with `stage`, `tokens_consumed`, `skills_loaded`, `skills_evaluated[]`, `subagents_dispatched`), `phases[]` (for review stage), `total_tokens`, `findings_total`, `findings_blocking`, `user_overrides`. Aggregated weekly/quarterly. Surfaced via `/tgf:framework-health`.

**Consequences:** Phases 1-16 reference these specifications. Deviation must be a conscious decision logged here. Skill files, hook scripts, meta-skills, and templates all build against these contracts.

---

## Template

Copy this template for each new decision. Use date + sequence number for the ID.

```
## DEC-YYYY-MM-DD-NNN: Decision title

**Decided:** [The decision itself in one sentence.]

**Date:** YYYY-MM-DD

**Context:** [What problem or question this decision addresses. Why now?]

**Decision:** [The decision in full, with rationale.]

**Alternatives considered:** [Options weighed and why not chosen.]

**Consequences:** [What this commits the project to; trade-offs accepted; downstream effects.]
```
