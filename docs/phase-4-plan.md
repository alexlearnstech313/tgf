# Phase 4 Implementation Plan: Always-On Skills + Orchestrator Agent

**Date:** 2026-05-19
**Status:** Plan drafted; awaiting Checkpoint 1 approval before implementation.
**Process:** Per the validated phase-workflow pattern (Phase 2, Phase 3) — write phase-N-plan.md first, get explicit approval on open decisions, then implement.

---

## 1. Status Summary

Phase 4 produces TGF's first concrete skill content: three always-on skills (CODE-QUALITY, SECURITY-CORE, CONTINUITY) plus the `tgf-orchestrator` custom agent that activates them via Anthropic-native skill preload. Phases 5–10 (~72 more skills) inherit Phase 4's conventions.

The architectural foundation is locked. Three ADRs landed in commit `39bc485`:

- **`DEC-2026-05-19-007`** — TGF as plugin with orchestrator agent + `skills:` preload mechanism + reference file pattern
- **`DEC-2026-05-19-008`** — Skill catalog consolidation (~80 → ~75) + reference file standard
- **`DEC-2026-05-19-009`** — Hook physical layout for plugin distribution (`hooks/hooks.json`)

Pre-Phase-4 housekeeping (commit `49c8a82`) restructured the repo to plugin layout — `skills/`, `agents/`, `hooks/`, `hooks/scripts/` at plugin root, replacing the old `.claude/skills/` and `.claude/hooks/<EventName>/` placeholders.

Phase 4 deliverables:

1. `skills/code-quality/SKILL.md` + reference files (rules.md, anti-patterns.md)
2. `skills/security-core/SKILL.md` + reference files
3. `skills/continuity/SKILL.md` + reference files
4. `agents/tgf-orchestrator.md` — custom agent that preloads all three above
5. `agents/code-reviewer.md`, `security-auditor.md`, `red-team.md`, `holistic-reviewer.md` — four-pass review subagent definitions (scaffolds; full system prompts may defer to Phase 11)
6. `settings.json` at plugin root — defaults to `"agent": "tgf-orchestrator"` for TGF-installed projects

Estimated effort: 4-6 focused sessions (one per skill plus one for agent definitions + closeout), or 2-3 days of continuous work.

---

## 2. Architectural Foundation

Phase 4 implementation operates against the locked architecture. Key constraints:

- **SKILL.md body ≤300 lines per skill** (per `DEC-2026-05-19-008` reference-file pattern). Verbose content (full rules, anti-patterns with code, citation tables) lives in reference files loaded on demand.
- **Always-on mechanism = `skills:` field on `tgf-orchestrator` agent** (per `DEC-2026-05-19-007`). The full content of each listed skill is injected into the orchestrator's context at startup — Anthropic-native.
- **Plugin namespace `/tgf:skill-name`** for slash command invocation. Internal references use bare names.
- **Frontmatter discipline:** only Anthropic-native fields are runtime (`name`, `description`, `paths`, `disable-model-invocation`, `user-invocable`, `allowed-tools`, `model`, `effort`, `context`, `agent`, `hooks`, `shell`). TGF-extension fields (`sources`, `applies-when` sub-fields beyond `paths`, `disqualifying-when`, `last-generated`, `refresh-recommended`, `self-evolution`) are documentation for Phase 11 meta-skills to consume, not runtime gates.
- **Description budget per skill:** ≤1024 characters (Anthropic cap). Combined `description` + `when_to_use` ≤1536 characters. With ~75 total skills, descriptions should aim for ~300-500 characters each to leave room in the listing budget.

These constraints inform every per-section decision below.

---

## 3. Sources Verification

Per `DEC-2026-05-17-004` Clause 1 (live verification at skill-creation time). The sources below were either verified during Phase 4 research (2026-05-19) or are queued for Stage 1 verification when each skill's implementation begins.

### CODE-QUALITY sources

| Source | Phase 4 use | Verification status |
|--------|-------------|---------------------|
| NIST SP 800-218 v1.1 (SSDF) — PW.4 Secure Coding Practices, PW.5 Review and Analyze Code | Foundational rules on type safety, error handling, code review discipline | Verified Phase 2 (commit `92c9894`); spot-check at Stage 1 of CODE-QUALITY implementation for current rule numbering |
| Anthropic Skill authoring best practices (current 2026) | Specifically the section on AI-generated code patterns; informs AI concerns section | Verified Phase 4 (2026-05-19) |
| MITRE ATLAS v5.4.0 — agent code generation techniques | Informs anti-patterns related to AI-suggested code that compiles but behaves wrong | Verified Phase 2 (commit `92c9894`) |
| ISO/IEC 5055:2021 — Software Measurement | Cited by reference (paywalled) per `DEC-2026-05-17-004` Clause 5; principle-level grounding for solo-maintainability | Reference only; no live fetch |

**Note on CODE-QUALITY citation density:** craft rules (naming, comment discipline, error handling style) often don't map to specific OWASP/NIST rules. They cite at principle level (e.g., "NIST SSDF PW.4 — secure coding practices") rather than rule level. Pure security-relevant code-quality rules (input validation patterns, secret handling) get rule-level citations.

### SECURITY-CORE sources

| Source | Phase 4 use | Verification status |
|--------|-------------|---------------------|
| OWASP Top 10:2025 (released) | Primary canonical security risk taxonomy; new categories A03 Software Supply Chain Failures, A10 Mishandling of Exceptional Conditions; Security Misconfiguration moved from #5 to #2 | Verified Phase 4 (2026-05-19); use 2025 not 2021 |
| OWASP ASVS 5.0 — Chapters V1 (Architecture), V2 (Authentication), V3 (Session), V4 (Access Control), V8 (Data Protection), V13 (API) | Core verification controls underlying the hard-refusal list and universal security rules | Verified Phase 2 (commit `92c9894`) |
| NIST SP 800-218 v1.1 (SSDF) — PW.6 Configure Compilation Settings to Improve Executable Security, PW.7 Review and/or Analyze Human-Readable Code | Implementation-time security review discipline | Verified Phase 2 |
| OWASP Top 10 for LLM Applications 2025 — LLM01 Prompt Injection, LLM06 Excessive Agency | AI-integrated systems guidance; cited in AI concerns section | Verified Phase 2 (commit `92c9894`) |
| MITRE ATT&CK v17 | Threat modeling foundation referenced in principles section | Spot-check at Stage 1 of SECURITY-CORE implementation for current version |

### CONTINUITY sources

| Source | Phase 4 use | Verification status |
|--------|-------------|---------------------|
| NIST SP 800-218 v1.1 (SSDF) — PO.5 Implement Supporting Toolchains, PO.5.1 Use Configuration Management | Documentation discipline + decision capture | Verified Phase 2 |
| ISO/IEC 27001:2022 — Annex A control 5.37 Documented Operating Procedures | Documentation-as-control framing; cited by reference (paywalled) per `DEC-2026-05-17-004` Clause 5 | Reference only |
| ISO/IEC 27002:2022 — Control 5.37 (same control, expanded guidance) | Same; cited by reference | Reference only |
| Architectural Decision Records (ADR) — Michael Nygard origin paper (2011) and current GitHub ADR ecosystem (`adr.github.io`) | Format/methodology backing for `DECISIONS.md` discipline | Spot-check at Stage 1 of CONTINUITY implementation |

**Note on CONTINUITY citation density:** continuity rules (session log discipline, three-log management, ROADMAP maintenance) often derive from TGF synthesis rather than mapping to specific external rules. Cite at principle level for discipline rules; cite at rule level where ISO/NIST controls map directly (e.g., "ISO/IEC 27002 control 5.37" for documented operating procedures).

### Comparative sources (design-rationale only, per `DEC-2026-05-17-004` Clause 6)

| Source | Phase 4 use |
|--------|-------------|
| Superpowers framework — opinionated CLAUDE.md patterns | Comparative validation of certain CONTINUITY patterns (session log discipline) |
| Public Anthropic skill examples (`anthropics/skills` repo) | Reference for SKILL.md structure conventions; comparative pattern check for description style |

Comparative sources stay in design-rationale notes only, not in skill `§2 Authoritative Sources` tables.

---

## 4. Per-Skill Mini-Specs

### CODE-QUALITY

**Scope (per `CLAUDE.md` §6):** Engineering discipline, type safety, error handling, naming, scale-aware patterns, migration patterns, documentation principles, solo-maintainability.

**Description (≤500 chars):** "Engineering discipline and craftsmanship rules for production code. Use when reviewing or writing code that should be maintainable, scale-aware, and clear six months later. Applies to: function design, error handling, naming, scale-aware defaults, comment discipline, solo-maintainability. Pairs with security-core for security-relevant code quality."

**SKILL.md sections (≤300 lines total):**
- §1 Overview (~30 lines)
- §2 Authoritative Sources (table, ~15 lines)
- §3 Discovery Commands (~25 lines)
- §4 Principles (~50 lines — the trait essence that preloads always)
- §5 Rule Summaries (~80 lines — pointers to rules.md detail)
- §6 Anti-Pattern Summaries (~50 lines — pointers to anti-patterns.md detail)
- §7 AI-Specific Concerns (~25 lines)
- §8 Workflow Integration (~15 lines)
- §9 Subagent Context Notes (~10 lines)

**Reference files:**
- `rules.md` — full rules with rule-level citations (≥5 rules; estimated ~200 lines)
- `anti-patterns.md` — full anti-patterns paired with canonical patterns and code examples (≥8 pairs; estimated ~400 lines)

**Per-skill QC criteria:**
- (a) ≥5 rules in rules.md, each with citation chain to NIST SSDF or principle-level source
- (b) ≥8 anti-patterns in anti-patterns.md, each paired with a canonical pattern, with code examples
- (c) Principles section reads coherently as a 50-line preload — no jargon without context
- (d) Description (≤500 chars) captures both "what" and "when to use"
- (e) SKILL.md body stays ≤300 lines

### SECURITY-CORE

**Scope (per `CLAUDE.md` §6):** Security-mindedness as trait, top universal rules, secure-by-default with usability balance.

**Description (≤500 chars):** "Universal security rules and security-mindedness as a default trait. Use when reviewing or writing any code that touches user data, external input, network operations, credentials, or trust boundaries. Top rules from OWASP Top 10:2025 and ASVS 5.0 — secure by default with usability balance. Includes the hard-refusal list (per CLAUDE.md §5)."

**SKILL.md sections (≤300 lines total):**
- §1 Overview (~30 lines)
- §2 Authoritative Sources (table, ~20 lines)
- §3 Discovery Commands (~25 lines)
- §4 Principles (~50 lines — defense in depth, least privilege, fail closed, validate at boundaries, hard-refusal list as principles)
- §5 Rule Summaries (~80 lines — top universal rules mapping to OWASP Top 10:2025 categories)
- §6 Anti-Pattern Summaries (~45 lines — hardcoded credentials, custom crypto, disabled TLS verification, etc.)
- §7 AI-Specific Concerns (~25 lines — AI patterns that look secure but aren't, per MITRE ATLAS)
- §8 Workflow Integration (~15 lines)
- §9 Subagent Context Notes (~10 lines — Security Auditor + Red Team preload this)

**Reference files:**
- `rules.md` — full rules with rule-level citations to OWASP Top 10:2025 + ASVS 5.0 (~300 lines)
- `anti-patterns.md` — full anti-patterns paired with canonical patterns and code examples (~400 lines)

**Per-skill QC criteria:**
- (a) Cites OWASP Top 10:**2025** specifically (not 2021); all 10 categories addressed at minimum in rule summaries
- (b) Hard-refusal list (per CLAUDE.md §5) fully covered in anti-patterns with concrete examples
- (c) ≥5 rules in rules.md with rule-level citations
- (d) ≥8 anti-patterns paired with canonical patterns
- (e) AI-specific concerns section references LLM01:2025 (prompt injection) and LLM06:2025 (excessive agency)
- (f) Description (≤500 chars) captures the "always relevant for security-touching code" framing
- (g) SKILL.md body stays ≤300 lines

### CONTINUITY

**Scope (per `CLAUDE.md` §6):** Memory architecture, session log discipline, three-log + ROADMAP management, decision capture.

**Description (≤500 chars):** "Documentation and continuity discipline for projects that outlive any single session. Use when closing a session, capturing a decision, updating ROADMAP, logging an error or waiver, or onboarding a project. Covers: session log entries, ADR format, three-log management (ERROR/VENDOR/WAIVER), ROADMAP maintenance, information disclosure considerations."

**SKILL.md sections (≤300 lines total):**
- §1 Overview (~30 lines)
- §2 Authoritative Sources (table, ~15 lines)
- §3 Discovery Commands (~20 lines — check existence of logs, ROADMAP, DECISIONS)
- §4 Principles (~50 lines — capture context for future you; decisions get ADRs; ROADMAP reflects reality)
- §5 Rule Summaries (~80 lines — session log structure, ADR format, three-log routing)
- §6 Anti-Pattern Summaries (~50 lines — ephemeral todo lists, undocumented decisions, ROADMAP drift)
- §7 AI-Specific Concerns (~25 lines — AI summarizing without preserving rationale; compaction context loss)
- §8 Workflow Integration (~15 lines)
- §9 Subagent Context Notes (~10 lines — Holistic Reviewer preloads this)

**Reference files:**
- `rules.md` — full rules with citations to NIST SSDF PO.5 + ISO/IEC 27002 5.37 (reference) (~200 lines)
- `anti-patterns.md` — full anti-patterns paired with canonical patterns (~350 lines)

**Per-skill QC criteria:**
- (a) ≥5 rules covering session log, ADR format, three-log routing, ROADMAP maintenance, information disclosure
- (b) ≥8 anti-patterns paired with canonical patterns
- (c) ADR format example aligns with `templates/DECISIONS.md.template` and the existing `DECISIONS.md` pattern
- (d) Three-log routing rule clearly distinguishes ERROR-LOG vs VENDOR-LOG vs WAIVER-LOG
- (e) Description (≤500 chars) captures the "everything that should survive the session" framing
- (f) SKILL.md body stays ≤300 lines

---

## 5. Implementation Order

Dependency-driven:

1. **Update `templates/SKILL.md.template`** to reflect the reference-file pattern + Anthropic-only runtime frontmatter (TGF-extension fields documented as metadata-only, not runtime). Establishes the convention all 3 skills use.
2. **CODE-QUALITY** — broadest scope; least likely to surface design questions about how skills fit together; pure craft, no compliance overlap
3. **SECURITY-CORE** — extends with security framing; uses OWASP Top 10:2025 verification (live source spot-check at Stage 1)
4. **CONTINUITY** — TGF-specific framing; cites NIST SSDF + ISO 27002 by reference; integrates with the artifact discipline already in CLAUDE.md
5. **`agents/tgf-orchestrator.md`** — depends on all three skills existing; preloads them via `skills:` field
6. **Review subagent definitions** (`code-reviewer.md`, `security-auditor.md`, `red-team.md`, `holistic-reviewer.md`) — scaffolds with `skills:` preload + minimal system prompt; deeper system prompt content may defer to Phase 11
7. **`settings.json` at plugin root** — defaults to `"agent": "tgf-orchestrator"` for TGF-installed projects
8. **Closeout** — update `CLAUDE.md` §6 (always-on skills section) to reflect that always-on is implemented via orchestrator agent preload; update `CLAUDE.md` §9 (skill index) for consolidated catalog count; ROADMAP + CHANGELOG closeout; session log entry

---

## 6. Universal QC Criteria

Applied to every skill. Per Phase 2 plan-adjustment lesson, criteria are intentions, not numeric targets.

1. **Anchored sections present** per `DEC-2026-05-17-003` Clause 1 — every required section has its `<!-- SECTION: name -->` anchor
2. **Internal consistency** — no claim in §5 contradicted in §6 (rule summaries align with anti-pattern summaries)
3. **Consistency with framework documents** — no contradictions with CLAUDE.md, ARCHITECTURE.md, WORKFLOW.md, DECISIONS.md
4. **Rule-level citation discipline** per DEC-004 — security rules cite specific identifiers (e.g., `OWASP ASVS 5.0 V6.2.2`); craft rules cite at principle level (e.g., `NIST SP 800-218 v1.1 PW.4`) where rule-level mapping doesn't exist
5. **Plain-language impact present** — every rule and anti-pattern explains the practical consequence ("this means X could happen")
6. **Cross-references resolve** — references to other skills, CLAUDE.md sections, DECs are valid
7. **No new authoritative claims without source verification** — every rule traces to a verified source
8. **AI-specific concerns concrete** — references actual MITRE ATLAS techniques or OWASP LLM Top 10 categories, not generic "AI might be wrong"
9. **Workflow integration accurate** — skill identifies which workflow stages it activates in (per WORKFLOW.md §3)
10. **Subagent preload context noted** — skill identifies which review subagent(s) should preload it
11. **SKILL.md body ≤300 lines** — hard ceiling per `DEC-2026-05-19-007`
12. **Description ≤500 chars** — leaves room for ~75 skills in the description budget

---

## 7. Checkpoint 1 — Decisions Resolved (2026-05-19)

All five decisions resolved. Implementation cleared.

**Decision A — Source citation density: RESOLVED.** Cite at the source's natural granularity. For sources with sub-rule numbering (OWASP ASVS, ISO 27002), use rule-level identifiers (`OWASP ASVS 5.0 V6.2.2`). For sources where practices ARE the granular level (NIST SSDF — practices like PW.4 are themselves the smallest cited unit), cite the practice. For craft rules with no authoritative rule-level mapping (e.g., naming conventions, comment discipline), cite the closest principle-level source (typically NIST SSDF PW.4 + Anthropic Skills authoring best practices) and acknowledge as TGF synthesis of senior-engineer craft.

This is a refinement of `DEC-2026-05-17-004` Clause 2's intent — not a contradiction. Clause 2 prevents vague "OWASP recommends" citations; it does not require fabricating sub-rule numbers that don't exist in the source. The discipline is "the most specific identifier the source provides." If Phase 5+ surfaces tensions with this approach, promote to a new ADR; for Phase 4 the plan-file capture suffices.

**Decision B — Reference file scope: RESOLVED.** Option (ii). Ship `rules.md` and `anti-patterns.md` for every Phase 4 skill from day one. Citations live inline within `rules.md`. Defer `citations.md` split until any skill's `rules.md` exceeds ~400 lines.

**Decision C — Skill descriptions: RESOLVED.** Option (i). Descriptions serve both adoption modes (orchestrator-active + skills-only). Target ~300-500 chars per always-on skill description — broad enough to match coding/planning prompts when the orchestrator is not active, tight enough to fit the description budget across ~75 skills.

**Decision D — Review subagent definitions: RESOLVED.** Option (ii). Scaffolds in Phase 4: `skills:` preload + `memory: project` + a 5-10 line system prompt establishing the role ("This is the [Code Reviewer / Security Auditor / Red Team / Holistic Reviewer] for TGF's four-pass review. See WORKFLOW.md §4 and §3 Stage 5 for the contract."). Full system prompts deferred to Phase 11 when the orchestration meta-skill is built. Ships the architecture end-to-end without locking content prematurely.

**Decision E — Commit grouping: RESOLVED.** Option (ii). Six focused commits:
1. `templates/SKILL.md.template` update (Anthropic-native runtime frontmatter + TGF-extension metadata distinction; reference-file pattern; ≤300-line body budget)
2. `skills/code-quality/` (SKILL.md + rules.md + anti-patterns.md)
3. `skills/security-core/` (SKILL.md + rules.md + anti-patterns.md, citing OWASP Top 10:2025)
4. `skills/continuity/` (SKILL.md + rules.md + anti-patterns.md)
5. `agents/` (tgf-orchestrator.md + code-reviewer.md + security-auditor.md + red-team.md + holistic-reviewer.md + plugin-root `settings.json` activating tgf-orchestrator)
6. Closeout (CLAUDE.md §6 reflects orchestrator-agent-preload mechanism; CLAUDE.md §9 reflects consolidated catalog count; ROADMAP + CHANGELOG; session log)

### Architectural reach

None of A–E warranted a new ADR. Decisions B–E are tactical to Phase 4. Decision A is a refinement of DEC-004 Clause 2's intent — captured here in the plan; promotable to ADR later if Phase 5+ surfaces tensions.

---

## 8. Out of Scope for Phase 4

Confirmed not in Phase 4:

- The remaining ~72 skills (Phases 5–10)
- Meta-skill implementations (Phase 11 — orchestration meta-skill, framework-health, project-context, baseline-audit, skill-forge, evolution review)
- Hook scripts (Phase 12 — Hook Library populates `hooks/hooks.json` and `hooks/scripts/`)
- Stack-specific bridge skills (Phase 13 — generated by skill-forge for LabList, AdaptivIQ, BLETRAP)
- Slash command implementations beyond the auto-generated `/tgf:code-quality`, `/tgf:security-core`, `/tgf:continuity` (Phase 14)
- Full documentation (Phase 15 — README, INSTALL, DESIGN-RATIONALE, how-it-works)
- Self-validation on LabList (Phase 16)
- Adopter `templates/CLAUDE.md.template` updates beyond what Phase 4 directly affects
- Mode-aware skill visibility via `skillOverrides` (deferred to Phase 15)

---

## 9. Effort Estimate

Per skill: ~4-6 hours focused work (research spot-check → SKILL.md draft → reference files → four-pass review → fixes → commit). Three skills = ~15 hours.

Agent definitions: ~2-3 hours (orchestrator + 4 review subagent scaffolds + settings.json).

Closeout: ~1-2 hours (CLAUDE.md updates, ROADMAP, CHANGELOG, session log).

Total: ~18-20 hours of focused work. Realistically 3-5 sessions over 1-2 weeks part-time, depending on session length and review depth.

The phase-3 pattern of two-commit splits per substantive deliverable served well. For Phase 4, six commits (one per skill + template + agents + closeout) keeps each diff reviewable and lets Checkpoint 1 decisions surface incrementally if anything in implementation pushes back on the plan.

---

## 10. Closing Notes

- This plan is committed (per Phase 2 Decision 2 — transparency before staging)
- Phase 4 implementation does not begin until Decisions A–E are resolved at Checkpoint 1
- Plan adjustments accumulated during implementation will be logged in the Phase 4 session log (per validated Phase 2/3 pattern)
- Phase 4 sets the pattern that ~72 downstream skills inherit; depth of QC at this phase pays dividends across the whole catalog
- The dogfooding continues — Phase 4 implementation uses the TGF workflow on its own construction (Stage 1 research with source spot-checks, Stage 3 governance against always-on skill principles, Stage 5 four-pass review with orchestrator playing reviewer roles until Phase 11 meta-skill exists)
