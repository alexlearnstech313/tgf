# Phase 2 Implementation Plan: CLAUDE.md Expansion

**Date:** 2026-05-17
**Status:** Research complete; awaiting plan approval before implementation.
**Process:** Step 2 of the agreed Phase 2 flow (Research → Plan → Implement → Objective QC → Commit).

---

## 1. Status Summary

The existing `CLAUDE.md` (641 lines, committed in `c04e658`) already covers §1–§17. Phase 2 actual scope is smaller than originally listed in `ROADMAP.md`:

- 🔧 **§17 Citation Verification** — *expand* to reflect DEC-2026-05-17-004's six clauses (untrusted-input handling, no-downloads, paywalled-sources, comparative-research separation)
- ➕ **§18 Hooks for Enforcement** — new
- ➕ **§19 Token Efficiency** — new
- ➕ **§20 Agent Orchestration** — new
- ➕ **§21 Self-Evolving Knowledge** — new
- ➕ **§22 Continual Improvement** — new
- ➕ **Adopter-facing `CLAUDE.md.template`** — derivative once §15–§22 final

§15 (Mode-Aware Operation) and §16 (Empirical Verification) are substantively complete in the existing draft and need only light QC review during implementation.

The ROADMAP will be updated to reflect this corrected scope at the Phase 2 closing commit.

---

## 2. Sources Verified (Step 1 Research)

Per DEC-2026-05-17-004 Clause 1 (live verification at skill-creation time), the following authoritative sources were fetched on 2026-05-17. Content treated as untrusted input per Clause 3; only structured data extracted. No raw content written to filesystem — only synthesized references appear below.

| Source ID | Reference | Version | Date Verified | Notes |
|-----------|-----------|---------|---------------|-------|
| OWASP-LLM-2025-04 | OWASP Top 10 for LLM Applications — LLM04:2025 Data and Model Poisoning | 2025 | 2026-05-17 | 10 prevention strategies extracted |
| OWASP-LLM-2025-06 | OWASP Top 10 for LLM Applications — LLM06:2025 Excessive Agency | 2025 | 2026-05-17 | 8 prevention strategies; 3 root causes |
| NIST-SSDF | NIST SP 800-218 Secure Software Development Framework | v1.1 (v1.2 in draft) | 2026-05-17 | Four practice groups: PO, PS, PW, RV |
| MITRE-ATLAS | MITRE Adversarial Threat Landscape for AI Systems | v5.4.0 (Feb 2026) | 2026-05-17 | 16 tactics, 84 techniques; 14 new agent techniques added Oct 2025 |
| ANTHROPIC-SKILLS-BP | Claude API — Agent Skills authoring best practices | current (2026) | 2026-05-17 | Concrete numerical constraints for §19 |
| CLAUDE-CODE-HOOKS | Claude Code — Hooks reference | current (2026) | 2026-05-17 | 26+ events, exact JSON I/O contract |
| SUPERPOWERS-README | Superpowers framework README | n/a | 2026-05-17 | Comparative only, per DEC-004 Clause 6 |

Citations from these sources are rule-level precise per DEC-004 Clause 2 (e.g., `OWASP LLM06:2025`, `NIST SP 800-218 v1.1 PO.1`, `MITRE ATLAS AML.T0051`). The comparative source (Superpowers) is referenced in design rationale only, not as rule-source.

---

## 3. Important Finding — Phase 0 Hook Architecture Needs Amendment

Research surfaced that the hook event names enumerated in DEC-2026-05-17-003 Clause 2 do not match the actual Claude Code hook event taxonomy.

**Phase 0 invented events:** `pre-tool-use`, `post-tool-use`, `pre-commit`, `post-commit`, `session-start`, `session-end`, `pre-skill-modification`.

**Actual Claude Code hook events** (per CLAUDE-CODE-HOOKS source):

- **Session lifecycle:** `SessionStart`, `Setup`, `SessionEnd`
- **Per-turn:** `UserPromptSubmit`, `UserPromptExpansion`, `Stop`, `StopFailure`
- **Tool execution:** `PreToolUse`, `PermissionRequest`, `PermissionDenied`, `PostToolUse`, `PostToolUseFailure`, `PostToolBatch`
- **Subagent/task:** `SubagentStart`, `SubagentStop`, `TaskCreated`, `TaskCompleted`, `TeammateIdle`
- **Files/config:** `FileChanged`, `ConfigChange`, `CwdChanged`, `InstructionsLoaded`, `WorktreeCreate`, `WorktreeRemove`
- **Context:** `PreCompact`, `PostCompact`
- **MCP:** `Elicitation`, `ElicitationResult`
- **Notifications:** `Notification`

Three problems with the Phase 0 list:

1. **Naming convention mismatch.** Phase 0 used `kebab-case`; Claude Code uses `PascalCase`. The directory names in the repo currently reflect Phase 0's convention.
2. **`pre-commit` and `post-commit` are NOT Claude Code events.** Commit enforcement is properly implemented either via `PreToolUse` matching `Bash(git commit*)` (Claude Code-side) or via git's native `.git/hooks/pre-commit` (git-side). These are separate enforcement layers with different scopes.
3. **`pre-skill-modification` is not an event.** The use case is covered by `InstructionsLoaded`, `FileChanged`, and `ConfigChange`.

**Proposed amendment to DEC-2026-05-17-003 Clause 2:**

- TGF Claude Code hooks live in `.claude/hooks/<EventName>/NN-name.sh` using actual Claude Code event names (PascalCase).
- TGF git hooks (separate enforcement layer) live in `.claude/git-hooks/` and install into `.git/hooks/` via an opt-in setup script.
- The current repo directory structure (`.claude/hooks/pre-tool-use/`, `pre-commit/`, etc.) gets corrected as part of either Phase 2 (alongside CLAUDE.md work) or deferred to Phase 12 (Hook Library) — user decision in §8 below.

This is surfaced as an open decision rather than a unilateral change. The implication: §18 documents the corrected architecture either way; the question is whether the directory rename happens now or later.

---

## 4. Per-Section Plans

### §17 Citation Verification (expansion)

**Current state:** ~15 lines (CLAUDE.md lines 627–641). Covers basics: citations must be verifiable, include version/date, refresh on source revision, `/tgf:verify-citation` command.

**Target state:** ~40–55 lines. Incorporates all six clauses of DEC-2026-05-17-004.

**Key points to add (the gap from DEC-004):**

1. *Already covered:* Live verification at skill-creation time (clause 1); rule-level citation precision (clause 2).
2. *NEW:* Fetched content treated as untrusted input (clause 3) — link to §20 prompt-injection grounding.
3. *NEW:* No developer-machine downloads (clause 4) — research happens in Claude's context, only synthesized output reaches filesystem.
4. *NEW:* Paywalled sources policy (clause 5) — cite by reference + use NIST/OWASP crosswalks.
5. *NEW:* Comparative framework research distinct from authoritative citation (clause 6).

**Sources:** DEC-2026-05-17-004 (canonical); OWASP-LLM-2025-01 referenced for clause 3 grounding.

**Integration:** §1 "Authoritative sources only" principle (already present, will cross-link); §18 hooks (citation verification can be enforced via hook on skill modification); §21 evolution (citation refresh is part of skill refresh cycle).

**Anti-patterns to avoid in writing:**

- Restating the entire DEC-004 in §17 (DEC-004 is canonical; §17 summarizes and points)
- Listing clauses without grounding why each matters
- Failing to address what happens when verification fails

**Per-section QC criteria:**

- ✅/❌ All six DEC-004 clauses referenced or summarized
- ✅/❌ Explicit pointer to `docs/DECISIONS.md` DEC-004 for full text
- ✅/❌ Length within 35–55 lines
- ✅/❌ Plain-language impact for each clause (per §1 Contract)
- ✅/❌ Cross-link to §1 "Authoritative sources only" principle
- ✅/❌ No new vague claims unsupported by DEC-004

---

### §18 Hooks for Enforcement (new)

**Target length:** ~85–115 lines.

**Key points to cover:**

1. Two enforcement layers: **Claude Code hooks** (in-session, tool-time) and **git hooks** (commit-time, install opt-in). Distinct scopes; both leveraged.
2. Hooks complement skill discipline — they are the enforcement *floor*, not the primary governance mechanism. Skills produce findings; hooks block actions.
3. TGF leverages Claude Code's native event taxonomy (point to CLAUDE-CODE-HOOKS source). TGF does not invent events.
4. Mode-aware hook profiles (per §15): exploration mode loads safety hooks only; building mode loads safety + workflow; hardening mode loads full profile including governance.
5. Three universal hooks always active regardless of mode: `block-dangerous-git`, `block-secrets-commit`, `block-destructive-db`.
6. Hooks treat their JSON stdin as untrusted input (`tool_input` may contain attacker-controlled data per indirect prompt injection vector). Exec-form invocation preferred to avoid shell injection.
7. Hook output contract: exit 0 + optional JSON for control fields; exit 2 blocks with stderr explanation; non-zero non-blocking returns stderr to Claude as system reminder.
8. Configuration hierarchy: managed policy > project > user > plugin > skill/agent frontmatter.

**Sources:** CLAUDE-CODE-HOOKS (canonical event taxonomy and JSON I/O contract); NIST-SSDF v1.1 (frames the three categories — Safety/Workflow/Governance map to NIST practice groups PO/PS/PW/RV); SUPERPOWERS-README (comparative: confirms hooks-as-enforcement-floor is a validated pattern).

**Integration:** §1 Contract (hooks complement, never replace, skill discipline); §5 Authority Structure (hooks can express hard-refusal cases programmatically); §15 Mode-Aware (hook profiles vary by mode); §17 Citation Verification (citation-refresh hooks); §20 Orchestration (subagent lifecycle hooks: SubagentStart/SubagentStop).

**Anti-patterns to avoid in writing:**

- Pretending TGF invented hooks (they're a Claude Code feature; TGF leverages them)
- Overloading hooks as the primary mechanism (they are the floor, not the ceiling)
- Listing every Claude Code event (point to docs; TGF documents the events TGF uses)
- Conflating Claude Code hooks with git hooks (different scopes)
- Treating hooks as silent denial (every block surfaces with reason and remediation)

**Per-section QC criteria:**

- ✅/❌ Distinguishes Claude Code hooks from git hooks explicitly
- ✅/❌ Lists the three universal always-active hooks by name
- ✅/❌ Explains mode-aware hook profiles
- ✅/❌ References Phase 0 architecture (with amendment proposal acknowledged)
- ✅/❌ States hooks as enforcement floor, not primary mechanism
- ✅/❌ Documents block/allow semantics (exit 0/2/other)
- ✅/❌ Plain-language impact: what hooks prevent (silent supply-chain attacks, accidental destruction, governance bypass)

---

### §19 Token Efficiency (new)

**Target length:** ~60–80 lines.

**Key points to cover:**

1. Phase 0 Decision 1 — skills use addressable section anchors (`<!-- SECTION: ... -->`, `<!-- RULE: 5.1 -->`, etc.) so loading is section-level not file-level. This *extends* Anthropic's progressive disclosure (which is file-level).
2. Path-based pre-filtering before semantic evaluation: when stage 3 evaluates skills, files-changed determines candidate skills first (cheap); applies-when conditions evaluated only on candidates (more expensive).
3. Subagent dispatch for parallel review (per §20): each review phase runs in its own subagent with focused context, not in main agent.
4. Cost-aware orchestration scales by change tier: Trivial = no subagents; Small = 2 review subagents; Medium = 4; Large = 7+.
5. Claude Code's native progressive disclosure (per ANTHROPIC-SKILLS-BP): frontmatter pre-loaded (~100 tokens per skill); SKILL.md body loads when triggered (max 500 lines for performance); references loaded on demand (one level deep maximum).
6. Token telemetry per Phase 0 Decision 5: `.tgf/telemetry/sessions/*.json` captures workflow_invocations, skills_evaluated, subagents_dispatched; aggregated quarterly; surfaced via `/tgf:framework-health`.

**Sources:** ANTHROPIC-SKILLS-BP (canonical: 500-line limit, ~100-token frontmatter, one-level-deep references); Phase 0 decisions DEC-2026-05-17-003 Clauses 1 and 5.

**Integration:** §4 Skill Activation Model (silent matching builds on these mechanics); §9 Skill Index (skills follow these constraints); §20 Orchestration (subagent dispatch references this); §22 Continual Improvement (telemetry drives improvement loops).

**Anti-patterns to avoid in writing:**

- Treating token efficiency as optimization (it's a structural property of how the framework operates)
- Discussing arbitrary token budgets without concrete numbers (use the 500-line limit, 100-token frontmatter, etc.)
- Pretending TGF invented progressive disclosure (it's Anthropic's pattern; TGF extends with addressable sections)
- Over-explaining mechanics that adopters don't need to understand to benefit

**Per-section QC criteria:**

- ✅/❌ Cites specific numbers (500 lines, 100 tokens, one-level-deep) from ANTHROPIC-SKILLS-BP
- ✅/❌ References Phase 0 Decisions 1 and 5 by ID
- ✅/❌ Distinguishes addressable section loading (TGF extension) from full-skill loading (Anthropic baseline)
- ✅/❌ Explains cost-scaling tiers concretely
- ✅/❌ Links token telemetry to `/tgf:framework-health` command

---

### §20 Agent Orchestration (new)

**Target length:** ~100–135 lines.

**Key points to cover:**

1. Seven subagent roles per Phase 0 Decision 3: **Researcher, Implementer, Code Reviewer, Security Auditor, Red Team, Holistic Reviewer, Verifier**. Each has defined input context and JSON output schema.
2. Cost-aware orchestration scales by change tier (per §19).
3. Workflow stage orchestration:
   - Stage 1 (Research) may dispatch Researcher subagents in parallel
   - Stage 4 (Implement) may decompose to Implementer subagents for Large tier
   - Stage 5 (Review) dispatches review subagents (Code Reviewer + Security Auditor + Red Team + Holistic Reviewer) in parallel
   - Verifier dispatches conditionally on AI-generated code (per §16)
4. **Two-stage review pattern** (validated by SUPERPOWERS-README): spec compliance first (did this implement what was planned), then quality. Phase 4 Holistic Review covers spec compliance; Phases 1–3 cover quality.
5. **Excessive Agency mitigation** (per OWASP-LLM-2025-06, 8 prevention strategies in order):
   - Minimize extensions available to subagents
   - Limit functions to minimum necessary
   - Avoid open-ended extensions; use granular functionality
   - Restrict permissions to minimum scope
   - Execute within user's security context
   - Human-in-the-loop for high-impact actions
   - Authorization in downstream systems, not LLM-decided
   - Secure coding practices (input sanitization)
6. **Adversarial AI scope** (per MITRE-ATLAS techniques including "Publish Poisoned AI Agent Tool" and "Escape to Host"): subagent integrity checks; tool-use logging; subagent boundary enforcement via Claude Code hooks (SubagentStart, SubagentStop).
7. Aggregation: orchestrator collects subagent outputs, deduplicates findings, applies severity normalization, surfaces to user as unified findings list with per-subagent attribution.

**Sources:** OWASP-LLM-2025-06 (Excessive Agency — 8 prevention strategies + 3 root causes: excessive functionality, permissions, autonomy); MITRE-ATLAS (agent-specific techniques, v5.4.0 Feb 2026 update adding "Publish Poisoned AI Agent Tool" and "Escape to Host"); SUPERPOWERS-README (comparative: two-stage review with fresh subagent per task); Phase 0 Decision 3 (canonical role definitions).

**Integration:** §3 Workflow (stages 1, 4, 5 dispatch subagents); §5 Authority Structure (subagent dispatch doesn't bypass user authority — orchestrator surfaces findings; user decides); §16 Empirical Verification (Verifier subagent dispatched on AI-generated code); §18 Hooks (SubagentStart/SubagentStop hooks); §19 Token Efficiency (cost scaling); §21 Self-Evolving Knowledge (orchestration patterns feed evolution observations).

**Anti-patterns to avoid in writing:**

- Granting subagents unrestricted tool access (violates LLM06 root cause: excessive permissions)
- Letting subagents make irreversible decisions without human checkpoint
- Using subagents for trivial work (cost > benefit; violates §19 cost-scaling)
- Letting subagent findings auto-apply without orchestrator review and user surfacing
- Treating subagents as replacing skill discipline (they apply skills; they don't override them)

**Per-section QC criteria:**

- ✅/❌ Lists all 7 subagent roles by name
- ✅/❌ Maps subagent dispatch to specific workflow stages (1, 4, 5)
- ✅/❌ Cites LLM06 prevention strategies (specifically: human-in-the-loop, least-privilege, authorization in downstream systems)
- ✅/❌ References MITRE-ATLAS agent-specific techniques
- ✅/❌ Distinguishes orchestrator decisions from subagent recommendations
- ✅/❌ Explains cost-scaling by tier with concrete examples
- ✅/❌ Documents the two-stage review pattern (spec compliance + quality)

---

### §21 Self-Evolving Knowledge (new)

**Target length:** ~80–105 lines.

**Key points to cover:**

1. Phase 0 Decision 4 — `.tgf/evolution/` data structure (`observations/`, `proposals/{pending,accepted,rejected}/`, `confidence-thresholds.json`).
2. **What can evolve via human-reviewed proposals:** anti-patterns, trigger criteria, AI-specific concerns, stack-skill patterns.
3. **What cannot auto-evolve:** numbered rules, authoritative source citations, framework principles, hard refusal list (per Phase 0 + DEC-004).
4. Confidence levels: low (1–2 observations), medium (3–9), high (10+).
5. Human review required via `/tgf:review-evolution` — no auto-apply, ever.
6. **Data poisoning mitigation** (per OWASP-LLM-2025-04, key prevention strategies):
   - Track observation origins (which session, which prompt produced this signal)
   - Vet observations before treating as actionable
   - Sandbox proposed changes (don't auto-apply)
   - Monitor for poisoning signs (statistical anomalies in observation patterns)
   - Anomaly detection on proposal volume/timing
7. Evolution input sources: session log analysis (recurring patterns), waiver patterns (rule-too-strict signal), citation refresh outcomes (source updates), user pushback patterns.
8. Refresh cadence ties to §17 citation verification: quarterly for fast-moving domains (supply chain, AI security), annually for stable (compliance frameworks).

**Sources:** OWASP-LLM-2025-04 (Data and Model Poisoning — 10 prevention strategies, especially data origin tracking, sandbox, anomaly detection, OWASP CycloneDX/ML-BOM for provenance); Phase 0 Decision 4 (canonical data structures); DEC-2026-05-17-004 (clauses 1–3 apply to evolution proposals derived from external content).

**Integration:** §17 Citation Verification (refresh outcomes feed evolution); §19 Token Efficiency (telemetry surfaces patterns); §20 Orchestration (orchestrator observations feed evolution); §22 Continual Improvement (evolution is one of three improvement loops); §5 Authority Structure (user decides accept/reject — no auto-apply).

**Anti-patterns to avoid in writing:**

- Auto-applying any evolution (always human-review)
- Evolving rules or citations (only anti-patterns, triggers, AI concerns, stack patterns)
- Treating low-confidence proposals as actionable
- Failing to track observation sources (data origin matters for poisoning resistance)
- Treating self-evolution as "the framework improving itself" (it's the framework surfacing proposals; humans decide)

**Per-section QC criteria:**

- ✅/❌ Distinguishes what evolves from what doesn't (4 categories vs 4 categories)
- ✅/❌ Lists confidence thresholds with observation counts (low/medium/high; 1–2 / 3–9 / 10+)
- ✅/❌ States human-review-required explicitly
- ✅/❌ References LLM04 prevention strategies (data origin tracking, sandboxing, anomaly monitoring)
- ✅/❌ Maps to Phase 0 Decision 4 data structures
- ✅/❌ Plain-language impact: what evolution catches (recurring AI failures, trigger gaps, stack-specific patterns)

---

### §22 Continual Improvement (new)

**Target length:** ~55–75 lines.

**Key points to cover:**

1. Three improvement loops feeding each other:
   - **Citation refresh** (§17 + DEC-004) — sources change, citations re-verify
   - **Evolution proposals** (§21) — observations accumulate, proposals surface
   - **Telemetry analysis** (§19) — patterns reveal calibration issues
2. Quarterly framework health review via `/tgf:framework-health` surfaces:
   - Skills loaded but never produced findings (over-broad triggers)
   - Skills with high noise:signal ratio (under-calibrated)
   - Frequently waived findings (rule miscalibration signal)
   - Stale citations (source-version drift)
3. User pushback as signal: repeated waivers of similar findings → review skill for over-rigor or context gap.
4. Authoritative source freshness cadence:
   - Quarterly for fast-moving (supply chain, AI security)
   - Semi-annual for framework versions (OWASP, NIST major releases)
   - Annual for compliance regimes (HIPAA, PCI, SOC 2)
5. Improvement is bounded by DEC-004 and Phase 0 constraints — no auto-evolution of rules, citations, principles, or hard refusals.
6. The framework's improvement loop ends with conscious user decisions, never with silent auto-application.

**Sources:** Phase 0 Decision 5 (telemetry format); Phase 0 Decision 4 (evolution data structures); DEC-2026-05-17-004 (citation refresh discipline). Light external grounding — this section synthesizes internal mechanisms documented elsewhere.

**Integration:** §17, §19, §21 all feed into §22; §5 Authority Structure governs all improvement decisions.

**Anti-patterns to avoid in writing:**

- Treating improvement as the framework improving itself autonomously
- Adding new improvement loops without grounding in concrete data sources
- Failing to constrain what can/can't improve automatically
- Documenting improvement processes that don't actually exist in TGF yet (e.g., promising team-wide aggregation in v1)

**Per-section QC criteria:**

- ✅/❌ Lists three feeding loops explicitly (citation, evolution, telemetry)
- ✅/❌ States `/tgf:framework-health` command and its specific surfaces
- ✅/❌ References cadence by domain volatility (quarterly / semi-annual / annual)
- ✅/❌ Maps to Phase 0 Decisions 4 and 5 and DEC-004
- ✅/❌ Plain-language impact: what continual improvement prevents (stale framework, miscalibrated rules, accumulating drift)
- ✅/❌ Bounded by authority structure (no auto-apply)

---

### Adopter-facing `CLAUDE.md.template` (new)

**Target length:** ~700–800 lines (mirrors internal CLAUDE.md with placeholders where appropriate).

**Approach:** Mirror the structure of `CLAUDE.md` exactly. The framework sections (§1, §2, §3, §4, §5, §6, §10, §11, §12, §13, §14, §15, §16, §17, §18, §19, §20, §21, §22) are *framework-enforced* — adopters do not modify them. Three sections are *adopter-customized*:

- **§7 Project Context** — populated by PROJECT-CONTEXT meta-skill during onboarding
- **§8 The Roadmap** — populated by PROJECT-MANAGEMENT meta-skill during onboarding
- **§9 Skill Index** — populated by SKILL-FORGE after stack-specific bridge skills generate

**Marking convention:** Sections that adopters customize are marked `<!-- ADOPTER-CUSTOMIZE: section-name -->`. Sections that are framework-enforced are marked `<!-- FRAMEWORK-ENFORCED: do not modify -->`. The template header explains this convention so adopters know where they can change content vs where changes would break framework discipline.

**Generation timing:** Produced AFTER §17–§22 are final in the internal CLAUDE.md. Mechanical derivation; minimal independent work. Probably the same session as Phase 2 closing commit.

**Per-section QC criteria:**

- ✅/❌ Mirrors internal CLAUDE.md section structure exactly
- ✅/❌ Every framework-enforced section marked with comment
- ✅/❌ Every adopter-customized section marked with comment + placeholder content
- ✅/❌ Header explains customization convention
- ✅/❌ No reference to TGF's own development artifacts, adopter-agnostic

---

## 5. Implementation Order

Dependency-driven sequencing:

1. **§17 expansion first** — establishes citation verification depth that other sections reference
2. **§18 Hooks** — Claude Code hooks mechanics referenced by §19, §20, §21
3. **§19 Token Efficiency** — mechanics referenced by §20 orchestration
4. **§20 Agent Orchestration** — depends on §18 and §19; references LLM06 prevention strategies
5. **§21 Self-Evolving Knowledge** — depends on §17, §19, §20; references LLM04 prevention strategies
6. **§22 Continual Improvement** — synthesizes §17, §19, §21
7. **Adopter `CLAUDE.md.template`** — mechanical derivation from finalized §15–§22

Implementation can pause between any two sections for user review.

---

## 6. Universal QC Criteria (Apply to Every CLAUDE.md Section)

> **Plan adjustment (2026-05-17, after §17 implementation):** An earlier draft of this list included "Section anchor present (`<!-- SECTION: ... -->`)" as criterion #1. That was a misspecification — HTML section anchors are a *skill template* feature per Phase 0 `DEC-2026-05-17-003` Clause 1, not a CLAUDE.md requirement. CLAUDE.md uses simple `## §N` markdown headers; existing §1-§16 have no anchors and need none. The criterion remains in force for skills (Phase 4+) but is struck for CLAUDE.md sections. The list below is renumbered 1-10.

1. **Length within target range** specified in per-section plan
2. **All cross-references resolve** — references to other sections, ADRs, Phase 0 decisions point to actual existing content
3. **No contradictions with §1–§16** — claims don't conflict with established prior sections
4. **Style consistency** — second-person address, declarative tone, no protocol headers, no narration from outside, matches voice of §1–§16
5. **No undefined jargon** — technical terms either explained inline or noted for glossary (Phase 15)
6. **Plain-language impact statements** alongside citations where rules are discussed (per §1 Contract clause)
7. **Workflow integration explicit** — if the section affects the six-stage workflow, it states how
8. **Mode awareness compatible** — doesn't impose universal rigor where §15 says scope varies by mode
9. **Authority structure compatible** — doesn't undermine the consultant-defers-to-stakeholder model
10. **Authoritative sources cited** with rule-level precision per `DEC-2026-05-17-004` Clause 2

Each universal criterion is yes/no checkable against the implemented section. Borderline cases logged with rationale.

---

## 7. Implementation Process Per Section

1. **Draft** section content following per-section plan
2. **Self-QC** against per-section criteria and universal criteria — produce a checklist artifact
3. **Surface findings** — log any criterion that fails or is borderline
4. **Iterate** until all criteria pass or borderline cases are explicitly accepted with rationale
5. **Surface to user** for review (cadence per §8 below)
6. **Move to next section**

QC checklist artifacts during implementation may be inlined in session log or written to `docs/phase-2-qc-checklists.md` — decided based on user preference in §8.

---

## 8. Open Decisions for User

Four decisions outstanding before implementation begins:

1. **Phase 0 hook architecture amendment** — rename `.claude/hooks/` directories to match Claude Code event names *now* (alongside Phase 2) or *defer* to Phase 12 (Hook Library)?
2. **Plan artifact visibility** — commit `docs/phase-2-plan.md` to repo (transparency for project) or move to `.sessions/` (gitignored internal scaffolding) after Phase 2 completes?
3. **Commit granularity** — one consolidated "Phase 2: CLAUDE.md expansion" commit at the end, or per-section commits for cleaner history?
4. **Review checkpoints** — review each section as I complete it (most checkpoints, slowest), review by batched groups (e.g., §17–§19 then §20–§22 then adopter template), or single review at the very end (fastest, highest risk if direction is off)?

---

## 9. What This Plan Commits To

Once approved, this plan is the contract for Phase 2 implementation. Deviation during implementation requires either:

- A conscious decision logged in `DECISIONS.md` (architectural deviation)
- A note in the session log (tactical deviation)

Per-section plans become the basis for Phase 4 (objective QC) verification. If implementation cannot meet a per-section QC criterion, the criterion is either revised (with rationale here) or the implementation continues until it can.

---

*Plan generated 2026-05-17 by Claude as Step 2 of the Phase 2 process. Awaiting user approval on §8 decisions before proceeding to Step 3 (implementation).*
