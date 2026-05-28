---
# ─── Anthropic-native runtime fields (Claude Code honors these) ───
name: continuity
description: |
  Documentation and continuity discipline for projects that outlive any single
  session. Use when closing a session, capturing an architectural decision,
  updating ROADMAP, logging an error or waiver, onboarding a project, or
  surfacing operational state for future maintainers. Covers: session log
  entries, ADR format and lifecycle, three-log management (ERROR/VENDOR/WAIVER),
  ROADMAP maintenance discipline, and information-disclosure considerations
  for operational artifacts.
paths:
  - "**/*.md"
  - "**/DECISIONS*"
  - "**/ROADMAP*"
  - "**/ERROR-LOG*"
  - "**/VENDOR-LOG*"
  - "**/WAIVER-LOG*"
  - "**/.sessions/**"
  - "**/CHANGELOG*"

# ─── TGF-extension metadata (Phase 11 meta-skills read these; Claude Code ignores) ───
applies-when:
  paths-include:
    - "**/{DECISIONS,ROADMAP,ERROR-LOG,VENDOR-LOG,WAIVER-LOG,CHANGELOG}.md"
    - "**/.sessions/**"
  operations-include:
    - session opening or closing
    - architectural decision being made or amended
    - milestone progression or scope shift
    - operational finding being captured (error, vendor action, accepted risk)
    - ROADMAP review or update
  data-flows-include:
    - working knowledge crossing from session context to durable artifact
    - decision rationale being captured for future maintainers
disqualifying-when:
  - documentation-only edits unrelated to logs/ROADMAP/DECISIONS
  - formatting-only edits
sources:
  - NIST SP 800-218 v1.1 (SSDF) — PO.5 Implement Supporting Toolchains (verified 2026-05-20)
  - ISO/IEC 27002:2022 — Control 5.37 Documented Operating Procedures (cited by reference; paywalled)
  - ISO/IEC 27001:2022 — Annex A control 5.37 (cited by reference; paywalled)
  - Architectural Decision Records (ADR) — Michael Nygard origin paper (2011); stable methodology
last-generated: 2026-05-20
refresh-recommended: 2027-05-20
self-evolution:
  anti-patterns-observed: []
  triggers-refined: []
  ai-failures-documented: []
---

# CONTINUITY

> **Skill body ≤300 lines** (per `DEC-2026-05-19-007`). Principles, rule summaries, and navigation live here. Full content in reference files loaded on demand:
> - `rules.md` — full rules with citations
> - `anti-patterns.md` — full anti-pattern + canonical pattern pairs with concrete examples

<!-- SECTION: overview -->
## §1 Overview

CONTINUITY governs the documentation and memory dimension of every project: what survives a session close, what survives a developer onboarding, what survives the project's three-year-old technical decisions becoming load-bearing. It is one of three always-on skills in TGF (alongside CODE-QUALITY and SECURITY-CORE).

This skill encodes the *trait* of operational discipline — capturing context for future you, treating decisions as artifacts rather than ephemera, routing operational findings to the right durable home, keeping the ROADMAP honest. The framework's value compounds across time only if memory is maintained; this is the skill that maintains it.

Many CONTINUITY rules are TGF synthesis of senior practice rather than mappings to authoritative rule-level identifiers. Where authoritative grounding exists (NIST SSDF PO.5 for configuration management discipline; ISO/IEC 27002 control 5.37 for documented operating procedures by reference; ADR methodology per Nygard 2011), citations are explicit. Where the rule is TGF synthesis, the citation acknowledges this honestly per `DEC-2026-05-17-004`.
<!-- /SECTION: overview -->

<!-- SECTION: sources -->
## §2 Authoritative Sources

| Source ID | Reference | Version | Date Verified |
|-----------|-----------|---------|---------------|
| NIST-SSDF | [NIST SP 800-218 Secure Software Development Framework](https://csrc.nist.gov/pubs/sp/800/218/final) — PO.5 Implement Supporting Toolchains | v1.1 | 2026-05-20 |
| ISO-27002 | ISO/IEC 27002:2022 — Control 5.37 Documented Operating Procedures (paywalled; cited by reference) | 2022 | reference only |
| ISO-27001 | ISO/IEC 27001:2022 — Annex A control 5.37 (paywalled; cited by reference) | 2022 | reference only |
| ADR-NYGARD | [Michael Nygard, "Documenting Architecture Decisions" (2011)](https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions) — canonical ADR methodology | stable methodology | reference (stable since 2011) |

Citation granularity per Phase 4 Checkpoint 1 Decision A: NIST SSDF practices cited at the practice level (PO.5); ISO controls cited by reference per `DEC-2026-05-17-004` Clause 5 (paywalled standards); ADR methodology cited at the paper level (stable, no version drift in 14+ years).

Most CONTINUITY rules are TGF synthesis of senior operational practice — captured honestly per Decision A rather than fabricating sub-rule identifiers that don't exist in any single source.
<!-- /SECTION: sources -->

<!-- SECTION: discovery -->
## §3 Discovery Commands

Copy-pasteable commands to capture continuity state before applying rules.

```bash
# Confirm canonical artifacts exist
for f in DECISIONS.md ROADMAP.md ERROR-LOG.md VENDOR-LOG.md WAIVER-LOG.md CHANGELOG.md; do
  [ -f "$f" ] && echo "✓ $f" || echo "✗ $f (missing)"
done

# Check .gitignore protects operational state
grep -E "^\.sessions|^\.tgf" .gitignore 2>/dev/null || echo "WARNING: operational state not gitignored"

# Most recent session log
ls -1t .sessions/*.md 2>/dev/null | head -1

# Last ROADMAP update (mtime)
stat -c "%y %n" ROADMAP.md 2>/dev/null

# Count of committed ADRs
grep -c "^## DEC-" DECISIONS.md 2>/dev/null
```
<!-- /SECTION: discovery -->

<!-- SECTION: principles -->
## §4 Universal Principles

Six principles that ground every numbered rule. These preload into the orchestrator agent context (per `DEC-2026-05-19-007`).

- **Capture context for future you, not for present you.** Future you does not remember why this decision was made or what alternatives were weighed. Present you does. Write for the version of yourself who has lost all working context — the one onboarding to your own project six months later.

- **Decisions are artifacts, not ephemera.** A decision made in conversation that isn't captured anywhere durable is a decision that will be relitigated, sometimes by you, sometimes by an attacker exploiting the reversal. ADRs are not bureaucracy; they're the memory mechanism that lets the project move forward without rediscovering the same lessons.

- **Route operational findings to where they get acted on.** ERROR-LOG, VENDOR-LOG, and WAIVER-LOG exist because operational findings have different action profiles: errors get worked, vendor items get scheduled, waivers get revisited. A finding in the wrong log is a finding that doesn't get acted on. The cost of three logs is small; the cost of "we'll get to it later" with no log entry is unbounded.

- **The ROADMAP that doesn't reflect reality is worse than no ROADMAP.** An outdated ROADMAP creates false confidence in project state. The fix is not less roadmap discipline; it's keeping the ROADMAP honest as a deliverable of every workflow stage that affects milestones. The framework treats this as part of commit discipline.

- **Capture the WHY, not just the WHAT.** "We chose Postgres" is operationally useless. "We chose Postgres because the analytics workload required relational joins, we evaluated MongoDB and rejected it for the join cost, and we accepted the operational complexity of running a relational DB in exchange for query expressiveness" is operationally useful. Future maintainers can re-evaluate when context changes only if the original context is preserved.

- **Information disclosure defaults to protective.** Operational state — session logs, error logs, threat models, waiver rationale, vendor configuration gaps — is intelligence for attackers. Default to gitignored; opt INTO public visibility per artifact, consciously. Transparency is for the adopter, not the world.
<!-- /SECTION: principles -->

<!-- SECTION: rules -->
## §5 Rule Summaries

Six rules. Each summary: title + 1-line statement + source identifier.

<!-- RULE: 5.1 -->
- **Rule 5.1: Session-Close Log Entry Required** — Every session that did substantive work produces a session log entry at `.sessions/YYYY-MM-DD-session-NN-brief-topic.md` capturing topics, decisions, context for future sessions, open questions, and findings. `TGF-SYNTHESIS — grounded in NIST-SSDF v1.1 PO.5 + senior practice` → [`rules.md#rule-51-session-close-log-entry-required`](rules.md)
<!-- /RULE: 5.1 -->
<!-- RULE: 5.2 -->
- **Rule 5.2: Architectural Decisions Get ADRs** — Decisions that constrain future work, change project direction, or that future maintainers will need to understand are captured as ADRs in `DECISIONS.md` with the standard structure (Decided / Date / Context / Decision / Alternatives / Consequences). Tactical decisions stay in session logs. `ADR-NYGARD (2011) + ISO-27002 5.37 (by reference)` → [`rules.md#rule-52-architectural-decisions-get-adrs`](rules.md)
<!-- /RULE: 5.2 -->
<!-- RULE: 5.3 -->
- **Rule 5.3: Three-Log Routing Discipline** — Operational findings route by action profile: ERROR-LOG for actionable issues being worked (severity / status / owner / target); VENDOR-LOG for out-of-codebase actions (dashboard config, key rotation, DNS); WAIVER-LOG for formally accepted risks with rationale and revisit date. `TGF-SYNTHESIS — grounded in NIST-SSDF v1.1 PO.5 + senior practice` → [`rules.md#rule-53-three-log-routing-discipline`](rules.md)
<!-- /RULE: 5.3 -->
<!-- RULE: 5.4 -->
- **Rule 5.4: ROADMAP Reflects Current Reality** — `ROADMAP.md` is updated whenever milestone progress changes, sequencing shifts, scope changes, or work blocks/unblocks. ROADMAP update is part of commit discipline for any workflow that materially affects milestones. `TGF-SYNTHESIS — grounded in NIST-SSDF v1.1 PO.5 + senior practice` → [`rules.md#rule-54-roadmap-reflects-current-reality`](rules.md)
<!-- /RULE: 5.4 -->
<!-- RULE: 5.5 -->
- **Rule 5.5: Information Disclosure Defaults to Protective** — Operational state (session logs, error/vendor/waiver logs, audit findings, threat models, project-context detail) is gitignored by default. Adopters opt INTO public visibility per artifact, consciously. `TGF-SYNTHESIS — grounded in CLAUDE.md §12 + senior practice` → [`rules.md#rule-55-information-disclosure-defaults-to-protective`](rules.md)
<!-- /RULE: 5.5 -->
<!-- RULE: 5.6 -->
- **Rule 5.6: Capture WHY, Not Just WHAT** — Session logs and ADRs capture reasoning: alternatives weighed, trade-offs accepted, constraints that drove the choice, and revisit conditions. "We chose X" without these is operationally useless. `TGF-SYNTHESIS — grounded in ADR-NYGARD (2011) + senior practice` → [`rules.md#rule-56-capture-why-not-just-what`](rules.md)
<!-- /RULE: 5.6 -->

See `rules.md` for full rule text, citations, plain-language impact, and extended discussion.
<!-- /SECTION: rules -->

<!-- SECTION: anti-patterns -->
## §6 Anti-Pattern Summaries

Eight anti-pattern pairs covering the most common continuity failures observed in operational practice.

<!-- ANTI-PATTERN: AP-1 -->
- **AP-1: Decision-only session log entry** — Session log says "decided to use Postgres" but captures no alternatives weighed or trade-offs accepted. Violates Rule 5.6. → [`anti-patterns.md#ap-1-decision-only-session-log-entry`](anti-patterns.md)
<!-- /ANTI-PATTERN: AP-1 -->
<!-- ANTI-PATTERN: AP-2 -->
- **AP-2: Architectural decision buried in commit message** — Significant architectural choice (new framework, schema migration approach, auth strategy) lives only in a git commit message, not in `DECISIONS.md`. Violates Rule 5.2. → [`anti-patterns.md#ap-2-architectural-decision-buried-in-commit-message`](anti-patterns.md)
<!-- /ANTI-PATTERN: AP-2 -->
<!-- ANTI-PATTERN: AP-3 -->
- **AP-3: Ephemeral todo list as project memory** — Todo list in a scratch file, sticky note, or chat message for items that should be in `ERROR-LOG.md`. Violates Rule 5.3. → [`anti-patterns.md#ap-3-ephemeral-todo-list-as-project-memory`](anti-patterns.md)
<!-- /ANTI-PATTERN: AP-3 -->
<!-- ANTI-PATTERN: AP-4 -->
- **AP-4: ROADMAP drift** — ROADMAP says Phase 3 in progress; actual work has been Phase 7 for three weeks. Future contributors plan against fiction. Violates Rule 5.4. → [`anti-patterns.md#ap-4-roadmap-drift`](anti-patterns.md)
<!-- /ANTI-PATTERN: AP-4 -->
<!-- ANTI-PATTERN: AP-5 -->
- **AP-5: Waiver without revisit condition** — Risk accepted in `WAIVER-LOG.md` with rationale but no date or condition for revisiting. The waiver becomes permanent by default. Violates Rule 5.3. → [`anti-patterns.md#ap-5-waiver-without-revisit-condition`](anti-patterns.md)
<!-- /ANTI-PATTERN: AP-5 -->
<!-- ANTI-PATTERN: AP-6 -->
- **AP-6: Vendor action conflated with code error** — "Stripe webhook needs reconfiguration" logged in `ERROR-LOG.md` instead of `VENDOR-LOG.md`. Wrong routing means wrong action profile. Violates Rule 5.3. → [`anti-patterns.md#ap-6-vendor-action-conflated-with-code-error`](anti-patterns.md)
<!-- /ANTI-PATTERN: AP-6 -->
<!-- ANTI-PATTERN: AP-7 -->
- **AP-7: Session log committed to public repo** — Working operational state — including findings, threat surface notes, accepted risks — pushed to a public repository. Intelligence handed to attackers. Violates Rule 5.5. → [`anti-patterns.md#ap-7-session-log-committed-to-public-repo`](anti-patterns.md)
<!-- /ANTI-PATTERN: AP-7 -->
<!-- ANTI-PATTERN: AP-8 -->
- **AP-8: ADR amended in place rather than superseded** — Existing ADR's content edited to reflect a later decision, losing the original rationale and the amendment history. Violates Rule 5.2 and Rule 5.6. → [`anti-patterns.md#ap-8-adr-amended-in-place-rather-than-superseded`](anti-patterns.md)
<!-- /ANTI-PATTERN: AP-8 -->

Per `DEC-2026-05-17-003` Clause 1: every anti-pattern is paired with a canonical pattern in `anti-patterns.md`. Standalone APs without paired CPs are incomplete and do not ship.
<!-- /SECTION: anti-patterns -->

<!-- SECTION: ai-concerns -->
## §7 AI-Specific Concerns

Continuity failure modes specific to AI-assisted development.

- **Summarization that strips rationale.** AI is good at summarizing what happened. AI summaries often drop *why* it happened — the alternatives considered, the constraints that drove the choice, the trade-offs accepted. A session log generated by AI summarization needs explicit prompting to preserve the WHY (per Rule 5.6) or it degrades into outcome-only memory. Defense: review AI-generated session logs against Rule 5.6 before saving.

- **Compaction context loss.** When the conversation is summarized to free context (auto-compaction), the WHY behind earlier decisions can be lost before reaching a durable artifact. Defense: commit session log entries at decision points, not only at session close. The ADR or session log captures durably what compaction is about to lose.

- **Re-deriving instead of recalling.** Without a fresh ADR check at Stage 1 of a workflow, AI tends to re-derive decisions that were already made. The same conclusion may or may not result; either way, the prior decision's rationale is lost. Defense: Stage 1 research includes a `DECISIONS.md` scan for any ADR touching the current change context.

- **Plausible-but-fabricated history.** When asked "what did we decide about X?", AI may generate a plausible-sounding decision history that wasn't captured in any artifact. The hallucinated history reads convincingly. Defense: ground assertions about prior decisions in actual ADR or session log content; cite the artifact, not the conversation.

Relevant external taxonomies: `OWASP-LLM LLM09:2025` (Misinformation — including fabricated project history) and `MITRE-ATLAS` AML.T0051 (LLM Output Handling failures).
<!-- /SECTION: ai-concerns -->

<!-- SECTION: workflow -->
## §8 Workflow Integration

How CONTINUITY participates in the six-stage workflow (per `docs/WORKFLOW.md`).

- **Stage 1 (Research):** Run the §3 discovery commands. Scan `DECISIONS.md` for ADRs touching the current change context; scan recent session logs for related prior work; review ROADMAP for milestone context.
- **Stage 2 (Scope):** ROADMAP alignment is part of scope definition — which milestone does this change advance?
- **Stage 3 (Plan with Governance):** Rule 5.2 contributes when the change has architectural reach (write an ADR). Rule 5.3 contributes when operational findings emerge (route to ERROR/VENDOR/WAIVER).
- **Stage 5 Phase 4 (Holistic Review):** Primary skill for the holistic pass. Verify decisions are captured, ROADMAP reflects the change, session log captures the WHY, information disclosure is appropriate.
- **Stage 6 (Commit):** Apply all rules — session log entry, ROADMAP update if milestones progressed, three-log routing for findings, ADR for architectural decisions. The commit message references artifact updates (e.g., "per DEC-XXX" or "advances M4").
<!-- /SECTION: workflow -->

<!-- SECTION: subagent-context -->
## §9 Subagent Context

**Preloaded by:** `tgf-orchestrator` (always-on — CONTINUITY is one of the three always-on skills injected into every main-session context); `code-reviewer` and `holistic-reviewer` (review subagents). Per `DEC-2026-05-19-007`, the full skill content injects into each of these agents' context at startup via the agent definition's `skills:` field (verified against `agents/tgf-orchestrator.md`, `agents/code-reviewer.md`, `agents/holistic-reviewer.md`).

**Critical rules for review use (when consulted but not preloaded):**

- Rule 5.2 (Architectural Decisions Get ADRs)
- Rule 5.4 (ROADMAP Reflects Current Reality)
- Rule 5.6 (Capture WHY, Not Just WHAT)

**Top AI-specific concerns:**

- Summarization that strips rationale
- Plausible-but-fabricated history (cite the artifact, not the conversation)

Reference files (`rules.md`, `anti-patterns.md`) load on demand within the subagent if deeper detail is needed during a specific finding.
<!-- /SECTION: subagent-context -->
