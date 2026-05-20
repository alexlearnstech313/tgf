# Phase 5 Implementation Plan: Activity Skills (6)

**Date:** 2026-05-20
**Status:** Plan drafted; awaiting Checkpoint 1 approval before implementation.
**Process:** Per the validated phase-workflow pattern (Phase 2, Phase 3, Phase 4) — write phase-N-plan.md first, get explicit approval on open decisions, then implement.

---

## 1. Status Summary

Phase 4 closed 2026-05-20 with three always-on skills (CODE-QUALITY, SECURITY-CORE, CONTINUITY) plus `agents/` scaffolds and plugin-root `settings.json`. Six implementation commits + DEC-2026-05-20-010 (security_reminder_hook disable) + pre-publish housekeeping + first public push to `github.com/alexlearnstech313/tgf`.

Phase 5 produces six **activity skills** — domain skills that load on contextual triggers (not always-on like Phase 4). These are the planning, quality-process, and collaboration skills that surround the core craftsmanship/security/continuity triad. They activate when their domain is engaged: a planning prompt, a debugging scenario, a test-strategy decision, a pushback moment.

Phase 5 deliverables:

1. `skills/project-management/` — greenfield/brownfield planning, decomposition, MVP definition, stack selection, dependency planning, ROADMAP support
2. `skills/discovery/` — branching tree methodology for vague or ambiguous inputs
3. `skills/testing/` — test strategy, coverage discipline, security testing, accessibility testing
4. `skills/debugging/` — Agans 9 rules, Five Whys, scientific method, AI-specific debugging concerns
5. `skills/disagreement/` — tactful pushback, severity gradient, waiver protocol (operationalizes CLAUDE.md §5)
6. `skills/design/` — design principles, negative constraints, AI-specific design failure modes

Each skill ships SKILL.md + rules.md + anti-patterns.md per the reference-file pattern established in Phase 4 (DEC-2026-05-19-007 + DEC-2026-05-19-008).

Estimated effort: 6 focused commits (one per skill) + closeout = ~7 commits. ~3-5 sessions, ~15-20 hours total.

---

## 2. Architectural Foundation

Phase 5 implementation operates against the locked architecture established in Phases 0–4. Key constraints:

- **SKILL.md body ≤300 lines per skill** (per DEC-2026-05-19-007). Verbose content moves to `rules.md` and `anti-patterns.md`.
- **Activity skills load on context, not always-on.** Activation is via `applies-when` in TGF-extension frontmatter (documentation for Phase 11 meta-skills) plus `paths:` for Claude Code's native path-based discovery. Description-driven discovery is the primary runtime mechanism.
- **Reference file pattern is standard** per DEC-2026-05-19-008 — every activity skill ships `rules.md` + `anti-patterns.md` from day one. Defer `citations.md` split until any skill's `rules.md` exceeds ~400 lines.
- **Citation granularity per Phase 4 Checkpoint 1 Decision A:** cite at the source's natural granularity. Activity-skill domains have many sources (NIST SSDF for process, ISTQB for testing, Agans for debugging, Anthropic for design); each is cited at the granularity that source provides. Acknowledge TGF synthesis where craft rules have no authoritative sub-rule mapping.
- **Subagent preload notes**: activity skills are generally NOT preloaded by review subagents (per the four review subagents' skill lists from Phase 4). They activate at the orchestrator level during Stage 1 Research, Stage 2 Scope, or Stage 3 Plan with Governance — depending on the skill.

These constraints inform every per-section decision below.

---

## 3. Sources Verification

Per DEC-2026-05-17-004 Clause 1 (live verification at skill-creation time). Sources below are either verified from prior phases or queued for Stage 1 verification when each skill's implementation begins.

### PROJECT-MANAGEMENT sources

| Source | Phase 5 use | Verification status |
|--------|-------------|---------------------|
| NIST SP 800-218 v1.1 (SSDF) — PO.1 Define Security Requirements, PO.2 Implement Roles and Responsibilities, PO.3 Implement Toolchain | Process foundation — planning, role definition, toolchain selection | Verified 2026-05-20 (Phase 4 SECURITY-CORE / CODE-QUALITY); spot-check PO-series at Stage 1 |
| Agile Manifesto (2001, 4 values + 12 principles) | Methodology grounding for iterative planning; stable since 2001 | Reference (stable since 2001) |
| Eric Ries — "The Lean Startup" (2011), Build-Measure-Learn loop and MVP definition | MVP definition framing; comparative source per DEC-004 Clause 6 (book, not citable at rule level) | Reference only (book; design-rationale) |
| PMBOK Guide 7th Edition (2021) — Project Management Body of Knowledge | General project management discipline; paywalled per DEC-004 Clause 5 | Reference only (paywalled) |

### DISCOVERY sources

| Source | Phase 5 use | Verification status |
|--------|-------------|---------------------|
| Sakichi Toyoda — Five Whys methodology (Toyota Production System, originated ~1950s) | Root-cause questioning discipline applied to requirements discovery; stable methodology | Reference (stable since ~1950s) |
| IIBA BABOK Guide v3 — Business Analysis Body of Knowledge | Requirements elicitation discipline; paywalled per DEC-004 Clause 5 | Reference only (paywalled) |
| NIST SP 800-218 v1.1 (SSDF) — PO.1 Define Security Requirements | Sub-process for security-requirements discovery during DISCOVERY | Verified Phase 2 |

### TESTING sources

| Source | Phase 5 use | Verification status |
|--------|-------------|---------------------|
| NIST SP 800-218 v1.1 (SSDF) — PW.7 Review/Analyze Code, PW.8 Test Executable Code | Test discipline at the practice level | Verified 2026-05-20 |
| ISTQB Foundation Level Syllabus (current version) | Testing terminology + test-level taxonomy + test design techniques | Stage 1 spot-check needed at TESTING implementation |
| OWASP Testing Guide v4.x / OWASP WSTG | Security testing methodology | Stage 1 spot-check needed at TESTING implementation |
| WCAG 2.2 (W3C Recommendation, October 2023) | Accessibility testing criteria | Stage 1 spot-check needed (WCAG 3.0 may be advancing) |

### DEBUGGING sources

| Source | Phase 5 use | Verification status |
|--------|-------------|---------------------|
| David J. Agans — "Debugging: The 9 Indispensable Rules for Finding Even the Most Elusive Software and Hardware Problems" (2nd ed 2006) | The 9 rules: understand the system / make it fail / quit thinking and look / divide and conquer / change one thing at a time / keep an audit trail / check the plug / get a fresh view / if you didn't fix it, it ain't fixed | Reference (stable since 2002/2006; book) |
| Sakichi Toyoda — Five Whys | Root-cause depth probe | Reference (stable) |
| Scientific method (hypothesis → predict → test → conclude) | Methodology framing | Reference (stable methodology) |
| MITRE ATLAS v5.4.0 — agent debugging failure modes | AI-specific debugging concerns | Verified Phase 2 |

### DISAGREEMENT sources

| Source | Phase 5 use | Verification status |
|--------|-------------|---------------------|
| CLAUDE.md §5 (Authority Structure) — TGF's own severity gradient (light touch / standard advocacy / strong advocacy / hard refusal) | Primary operational ground for DISAGREEMENT | Internal source (verified by definition) |
| CLAUDE.md §11 (Findings and Logging) — WAIVER-LOG protocol for accepted risks | Operational target for "user accepts the risk" outcome | Internal source |
| MITRE ATLAS — AML.T0051 (LLM Output Handling) and OWASP LLM Top 10:2025 — LLM09 (Misinformation) | AI sycophancy and false-confidence failure modes | Verified Phase 2 |

### DESIGN sources

| Source | Phase 5 use | Verification status |
|--------|-------------|---------------------|
| Anthropic published design principles for AI-assisted development | Foundation for AI-aware design; canonical URL TBD | Stage 1 spot-check needed at DESIGN implementation |
| WCAG 2.2 — Perceivable / Operable / Understandable / Robust principles | Accessibility-aware design grounding | Stage 1 spot-check needed |
| TGF synthesis — negative constraints, AI-specific design failure modes | What makes AI-assisted design distinct | TGF synthesis (acknowledged per DEC-004 Decision A) |

### Comparative sources (design-rationale only, per DEC-2026-05-17-004 Clause 6)

| Source | Phase 5 use |
|--------|-------------|
| Cal Newport — "Deep Work" / digital minimalism | Comparative validation for DEBUGGING's "quit thinking and look" rule |
| Christopher Alexander — "A Pattern Language" | Comparative source for DESIGN's pattern-language framing |
| Kim Scott — "Radical Candor" | Comparative source for DISAGREEMENT's tactful-pushback framing (NOT cited at rule level — book/blog-grade reference) |

Comparative sources stay in design-rationale notes within the plan; they do not appear in skill `§2 Authoritative Sources` tables.

---

## 4. Per-Skill Mini-Specs

### PROJECT-MANAGEMENT

**Scope (per CLAUDE.md §9 / ROADMAP Phase 5):** Greenfield/brownfield modes, decomposition, MVP definition, stack selection, dependency planning, ROADMAP support.

**Description (≤500 chars):** "Project planning discipline for greenfield projects (planning from intent) and brownfield projects (planning around existing codebase). Use when defining MVP scope, decomposing work into milestones, selecting stack components, planning dependencies, or supporting ROADMAP construction and revision. Pairs with DISCOVERY when input is ambiguous and with BASELINE-AUDIT (Phase 11) for brownfield assessments."

**SKILL.md sections (~250-280 lines):**
- §1 Overview (~30 lines)
- §2 Authoritative Sources (~15 lines)
- §3 Discovery Commands (~25 lines)
- §4 Principles (~50 lines — start from intent, decompose against constraints, MVP serves users not engineering ego, dependency awareness, ROADMAP honesty)
- §5 Rule Summaries (~70 lines)
- §6 Anti-Pattern Summaries (~50 lines)
- §7 AI-Specific Concerns (~25 lines — AI under-scoping, AI over-engineering, AI shipping minimum viable to ship vs minimum viable for users)
- §8 Workflow Integration (~15 lines)
- §9 Subagent Context (~10 lines — orchestrator-side skill; planning-stage activation)

**Per-skill QC criteria:**
- (a) ≥5 rules covering greenfield mode, brownfield mode, MVP definition, decomposition discipline, dependency planning
- (b) ≥8 anti-patterns paired with canonical patterns
- (c) Greenfield/brownfield distinction is operational, not just conceptual
- (d) MVP rule clearly distinguishes "minimum viable for engineering" from "minimum viable for users"
- (e) SKILL.md body ≤300 lines

### DISCOVERY

**Scope (per CLAUDE.md §9 / ROADMAP Phase 5):** Branching tree methodology for vague or ambiguous inputs.

**Description (≤500 chars):** "Branching-tree interview methodology for vague or ambiguous user inputs. Use when a prompt has multiple valid interpretations, when scope is undefined, when requirements emerge through conversation rather than being stated upfront, or when assumptions need explicit surfacing. Operationalizes 'ask before assuming' as a discipline. Pairs with PROJECT-MANAGEMENT for scope crystallization."

**SKILL.md sections (~220-250 lines):**
- §1 Overview (~25 lines)
- §2 Authoritative Sources (~15 lines)
- §3 Discovery Commands (~15 lines — applicable to skill's own use, not codebase-grep)
- §4 Principles (~45 lines — narrow before answering, branching tree over linear questioning, surface assumptions explicitly, Five Whys for root cause, stop when scope is operational)
- §5 Rule Summaries (~60 lines)
- §6 Anti-Pattern Summaries (~45 lines)
- §7 AI-Specific Concerns (~25 lines — AI assuming meaning instead of asking, AI providing answers when clarification needed, AI over-questioning when context is sufficient)
- §8 Workflow Integration (~15 lines — primarily Stage 1 Research activation)
- §9 Subagent Context (~10 lines)

**Per-skill QC criteria:**
- (a) ≥5 rules covering branching-tree structure, assumption surfacing, Five Whys application, scope-operational threshold, when-to-stop discipline
- (b) ≥8 anti-patterns paired with canonical patterns
- (c) Five Whys rule traces methodology to Sakichi Toyoda
- (d) "When to stop" rule prevents both under-questioning and over-questioning
- (e) SKILL.md body ≤300 lines

### TESTING

**Scope (per CLAUDE.md §9 / ROADMAP Phase 5):** Test strategy, coverage discipline, security testing, accessibility testing.

**Description (≤500 chars):** "Test strategy and quality-assurance discipline. Use when writing tests, designing test strategy, evaluating coverage, planning security testing, or planning accessibility testing. Covers unit/integration/E2E test levels, coverage-as-feedback vs coverage-as-target, security testing via OWASP WSTG, accessibility testing against WCAG 2.2, and the AI-specific concern that AI tends to write tautological tests that match the implementation rather than testing behavior."

**SKILL.md sections (~270-290 lines):**
- §1 Overview (~30 lines)
- §2 Authoritative Sources (~20 lines)
- §3 Discovery Commands (~25 lines)
- §4 Principles (~50 lines — tests test behavior not implementation, coverage is feedback not target, security testing is a discipline not an afterthought, accessibility is testable, tests at trust boundaries are mandatory)
- §5 Rule Summaries (~75 lines)
- §6 Anti-Pattern Summaries (~50 lines)
- §7 AI-Specific Concerns (~25 lines — tautological tests, fake assertions, AI under-testing edge cases, AI inventing test scenarios that don't exercise the change)
- §8 Workflow Integration (~15 lines)
- §9 Subagent Context (~10 lines — code-reviewer references TESTING when reviewing tests)

**Per-skill QC criteria:**
- (a) ≥5 rules covering test strategy, coverage discipline, trust-boundary tests, security testing application, accessibility testing application
- (b) ≥8 anti-patterns paired with canonical patterns (including the AI tautological-test failure mode)
- (c) Cites NIST SSDF PW.8, ISTQB Foundation Level (current), OWASP WSTG (current), WCAG 2.2
- (d) Distinguishes test PYRAMID from test TROPHY (modern conventions vary by domain)
- (e) SKILL.md body ≤300 lines

### DEBUGGING

**Scope (per CLAUDE.md §9 / ROADMAP Phase 5):** Agans 9 rules, Five Whys, scientific method, AI-specific debugging concerns.

**Description (≤500 chars):** "Systematic debugging discipline grounded in David Agans' 9 rules and the scientific method. Use when reproducing a bug, isolating variables, forming hypotheses, identifying root causes, or verifying fixes. Especially important when AI is involved — AI tends to fabricate plausible-sounding root causes, patch symptoms instead of causes, and confirm hypotheses instead of testing them. The debugging variant of TGF's six-stage workflow runs through this skill."

**SKILL.md sections (~270-290 lines):**
- §1 Overview (~30 lines)
- §2 Authoritative Sources (~15 lines)
- §3 Discovery Commands (~20 lines)
- §4 Principles (~55 lines — Agans' 9 rules summarized; reproduce-first discipline; isolate before hypothesizing; one variable at a time; audit trail discipline)
- §5 Rule Summaries (~70 lines)
- §6 Anti-Pattern Summaries (~50 lines)
- §7 AI-Specific Concerns (~30 lines — fabricated root causes, symptom patching, hypothesis confirmation bias, AI not running the code, AI plausible-but-wrong explanations)
- §8 Workflow Integration (~15 lines — debugging variant per docs/WORKFLOW.md §7)
- §9 Subagent Context (~10 lines)

**Per-skill QC criteria:**
- (a) ≥5 rules covering Agans-grounded discipline, scientific method application, Five Whys integration, audit trail, fresh-view rule
- (b) ≥8 anti-patterns paired with canonical patterns (including the AI fabricated-root-cause failure mode)
- (c) Cites Agans 2002/2006 + Sakichi Toyoda Five Whys + scientific method
- (d) Maps to docs/WORKFLOW.md §7 debugging variant cleanly
- (e) SKILL.md body ≤300 lines

### DISAGREEMENT

**Scope (per CLAUDE.md §5 / ROADMAP Phase 5):** Tactful pushback, severity gradient, waiver protocol.

**Description (≤500 chars):** "Operationalizes CLAUDE.md §5's severity gradient for disagreement: light touch (preference and style), standard advocacy (engineering quality), strong advocacy (security and privacy with real consequences), hard refusal (universal critical issues). Use when the user pushes back on a TGF recommendation, when surfacing concerns, when documenting waivers per CLAUDE.md §11, or when AI is at risk of sycophancy. Defends against LLM09:2025 (misinformation via false confidence)."

**SKILL.md sections (~240-260 lines):**
- §1 Overview (~30 lines — explicit cross-reference to CLAUDE.md §5)
- §2 Authoritative Sources (~15 lines)
- §3 Discovery Commands (~15 lines)
- §4 Principles (~50 lines — voice the concern with reasoning, listen to the user's reasoning, accept their decision after one round of discussion, document the waiver, hard-refusal items don't compromise)
- §5 Rule Summaries (~60 lines)
- §6 Anti-Pattern Summaries (~50 lines)
- §7 AI-Specific Concerns (~25 lines — AI sycophancy, AI false confidence, AI not pushing back when it should, AI not accepting user decisions when it should)
- §8 Workflow Integration (~15 lines)
- §9 Subagent Context (~10 lines — applicable to all subagents; orchestrator coordinates user-facing pushback)

**Per-skill QC criteria:**
- (a) ≥5 rules covering the four severity levels (light/standard/strong/hard) + waiver protocol
- (b) ≥8 anti-patterns paired with canonical patterns (including AI sycophancy)
- (c) Severity-gradient rules align verbatim with CLAUDE.md §5
- (d) Waiver protocol rule references CLAUDE.md §11 and WAIVER-LOG discipline (from CONTINUITY Rule 5.3)
- (e) SKILL.md body ≤300 lines

### DESIGN

**Scope (per CLAUDE.md §9 / ROADMAP Phase 5):** Design principles, negative constraints, AI-specific design failure modes.

**Description (≤500 chars):** "Design discipline for AI-assisted development. Use when proposing system architecture, API contracts, schema design, UX/UI features, or design-level patterns. Anthropic-foundation principles plus TGF synthesis on negative constraints (explicit 'we do not want X' as design boundary). Defends against the AI failure mode where models propose patterns frequently in training data without evaluating whether they fit the current constraints."

**SKILL.md sections (~250-270 lines):**
- §1 Overview (~30 lines)
- §2 Authoritative Sources (~15 lines)
- §3 Discovery Commands (~20 lines)
- §4 Principles (~50 lines — start from constraints not from patterns, negative constraints are first-class, the simplest design that meets constraints wins, design accommodates change but doesn't anticipate it, design for the medium not the message)
- §5 Rule Summaries (~65 lines)
- §6 Anti-Pattern Summaries (~50 lines)
- §7 AI-Specific Concerns (~30 lines — AI proposes patterns from training data without constraint-fit check, AI over-engineers, AI ignores explicit constraints, AI confuses precedent for principle)
- §8 Workflow Integration (~15 lines)
- §9 Subagent Context (~10 lines)

**Per-skill QC criteria:**
- (a) ≥5 rules covering constraint-first design, negative constraints, simplicity discipline, change accommodation, AI-pattern-vs-constraint
- (b) ≥8 anti-patterns paired with canonical patterns
- (c) Negative-constraint rule is operational with concrete examples
- (d) Anthropic design principles cited (URL verified at Stage 1)
- (e) SKILL.md body ≤300 lines

---

## 5. Implementation Order

Dependency-driven order (later skills can reference earlier ones for cross-skill consistency):

1. **DISCOVERY** — least dependencies; foundational for the planning skills
2. **PROJECT-MANAGEMENT** — references DISCOVERY for ambiguous-input handling
3. **DESIGN** — references PROJECT-MANAGEMENT for context; sets pattern conventions used by TESTING and DEBUGGING
4. **TESTING** — references DESIGN principles; sources align with NIST SSDF PW.7/PW.8 (already in SECURITY-CORE so cross-skill citation pattern established)
5. **DEBUGGING** — references TESTING (debugging vs testing distinction) and uses docs/WORKFLOW.md §7 debugging variant explicitly
6. **DISAGREEMENT** — meta-skill; references CLAUDE.md §5 and §11 directly; written last so cross-skill operational patterns are visible

Then closeout: ROADMAP M5 → Complete, CHANGELOG Phase 5 entries, session log entry.

Six implementation commits + one closeout = seven Phase 5 commits.

---

## 6. Universal QC Criteria

Applied to every Phase 5 skill (extending the Phase 4 criteria; intentions, not numeric targets):

1. **Anchored sections present** per DEC-2026-05-17-003 Clause 1 — every required section has its `<!-- SECTION: name -->` anchor
2. **Internal consistency** — no claim in §5 contradicted in §6
3. **Consistency with framework documents** — no contradictions with CLAUDE.md, ARCHITECTURE.md, WORKFLOW.md, DECISIONS.md, or the three Phase 4 always-on skills
4. **Rule-level citation discipline** per DEC-2026-05-17-004 — cite at the source's natural granularity; acknowledge TGF synthesis where no rule-level mapping exists
5. **Plain-language impact present** — every rule and anti-pattern explains the practical consequence
6. **Cross-references resolve** — references to other skills, CLAUDE.md sections, DECs are valid
7. **No new authoritative claims without source verification** — every rule traces to a verified source or is acknowledged as TGF synthesis
8. **AI-specific concerns concrete** — references actual MITRE ATLAS techniques or OWASP LLM Top 10:2025 categories, not generic "AI might be wrong"
9. **Workflow integration accurate** — skill identifies which workflow stages it activates in (per WORKFLOW.md §3)
10. **Subagent preload context noted** — skill identifies which review subagent(s) reference it (most activity skills aren't preloaded; the §9 note acknowledges this)
11. **SKILL.md body ≤300 lines** — hard ceiling per DEC-2026-05-19-007
12. **Description ≤500 chars** — leaves room in the ~75-skill description budget

---

## 7. Open Checkpoint 1 Decisions

Five decisions to resolve before implementation begins.

### Decision A — DESIGN skill scope (UX/UI vs system vs all)

DESIGN's domain spans UX/UI design, system architecture design, API design, schema design. The scope as currently written is "design principles + negative constraints + AI-specific failure modes" — broad. Three options:

- **(i) All-of-the-above DESIGN.** Single skill covers all design domains; rules are domain-agnostic (constraint-first, simplicity, etc.). Pros: minimal skill count. Cons: domain-specific guidance is shallow.
- **(ii) System/architecture DESIGN only.** Schema/API/UI design split off to future skills. Pros: depth. Cons: leaves gaps; conflicts with ROADMAP scope.
- **(iii) Universal DESIGN principles + cross-reference to domain skills** (TESTING for testable design, SECURITY-CORE for secure design, future `data-architecture` skill for schema design, future `security-api` for API design). Pros: depth without bloat; honest about cross-skill integration. Cons: requires forward references to skills not yet built.

Lean toward **(iii)** — TGF's value is in skill-to-skill orchestration; the DESIGN skill captures universal principles and points to domain skills for depth.

### Decision B — TESTING skill scope (pyramid vs trophy vs both)

Modern testing conventions vary by domain. Test PYRAMID (many unit, fewer integration, fewest E2E) is classical advice; test TROPHY (heavy integration, lighter unit, some E2E) is the newer convention especially in web/frontend. Three options:

- **(i) TESTING prescribes the pyramid.** Classical; stable; older. Best for backend / library code.
- **(ii) TESTING prescribes the trophy.** Modern; fits how AI-generated UI code is typically tested. Best for frontend / web.
- **(iii) TESTING presents both and discusses when each fits.** Pros: honest about domain variance. Cons: skill body grows.

Lean toward **(iii)** — TGF's adopter projects span multiple domains (LabList Next.js, AdaptivIQ Flutter, BLETRAP Python); a single-shape prescription would mismatch.

### Decision C — DISAGREEMENT skill vs CLAUDE.md §5 boundary

DISAGREEMENT operationalizes the severity gradient already in CLAUDE.md §5. Three options for how the skill relates to §5:

- **(i) DISAGREEMENT restates §5 verbatim.** Pros: self-contained skill. Cons: duplication; risk of drift.
- **(ii) DISAGREEMENT references §5 and adds only the operational layer.** Pros: no duplication. Cons: requires reader to context-switch between SKILL.md and CLAUDE.md.
- **(iii) DISAGREEMENT references §5 for the severity definitions and adds: contextual triggers, rules per severity level, anti-patterns showing the gradient in practice, AI-specific concerns (sycophancy), waiver protocol cross-reference.** Pros: skill adds value without restating; CLAUDE.md remains authoritative. Cons: minor — the layout is well-precedented.

Lean toward **(iii)**.

### Decision D — DEBUGGING skill subagent role

ARCHITECTURE.md §20 specifies seven subagent roles. The four Phase 4 review subagents (code-reviewer, security-auditor, red-team, holistic-reviewer) cover the four-pass review. The remaining three include verifier (per CLAUDE.md §16) and others. Is there a `debugger` subagent role to be defined, or does DEBUGGING activate at the orchestrator level during the debugging variant of the workflow? Three options:

- **(i) DEBUGGING activates only at orchestrator level** during the docs/WORKFLOW.md §7 debugging variant. No dedicated subagent.
- **(ii) Define a `debugger` subagent** in Phase 5 alongside DEBUGGING skill. Activates when the workflow shifts to the debugging variant. Pros: explicit isolation of debugging work; Phase 11 can build on it. Cons: adds an agent scaffold not in phase-4-plan.
- **(iii) Defer the subagent decision to Phase 11** when the full orchestration meta-skill is built. Phase 5 just ships the DEBUGGING skill at the orchestrator level.

Lean toward **(iii)** — Phase 4 deferred subagent semantics to Phase 11; consistent for Phase 5 to do the same.

### Decision E — Commit grouping (6+1 vs grouped)

Phase 4 used six focused commits. Phase 5 has six skills plus a closeout. Three options:

- **(i) Seven commits.** One per skill + closeout. Matches Phase 4 cadence.
- **(ii) Grouped commits.** Group related skills (e.g., DISCOVERY + PROJECT-MANAGEMENT as planning-pair; TESTING + DEBUGGING as quality-pair; DISAGREEMENT + DESIGN as meta-pair). Three skill commits + closeout = four commits.
- **(iii) Mixed.** Standalone for the larger skills (TESTING, DEBUGGING, DESIGN), grouped for the related smaller ones (DISCOVERY + PROJECT-MANAGEMENT; DISAGREEMENT alone).

Lean toward **(i)** — Phase 4 pattern is validated; grouping risks the "if this skill needs a fix, the commit becomes hard to revert" problem.

---

## 8. Out of Scope for Phase 5

Confirmed not in Phase 5:

- Remaining ~63 skills (Phases 6–10) — security skills, AI-specific, operations, quality, compliance
- Meta-skill implementations (Phase 11)
- Hook scripts (Phase 12)
- Stack-specific bridge skills (Phase 13 — generated by SKILL-FORGE for LabList, AdaptivIQ, BLETRAP)
- Slash command implementations beyond what activity skills auto-generate
- Full documentation (Phase 15)
- ARCHITECTURE.md §19 minor token-cost update (deferred from Phase 4 closeout; not blocking)
- The `settings.json` activation mechanism uncertainty (Phase 11 verifies)
- A dedicated `debugger` subagent (Decision D → defer to Phase 11)
- Adopter `templates/CLAUDE.md.template` updates beyond what Phase 5 directly affects

---

## 9. Effort Estimate

Per skill: ~2-3 hours focused work (research spot-check + SKILL.md draft + reference files + four-pass review + fixes + commit). Activity skills are smaller per-skill than always-on skills because there's less surface area to cover (no hard-refusal list, no Top-10 coverage map, no enumeration of OWASP categories). Estimate ~250-280 lines SKILL.md + ~150-200 lines rules.md + ~400-500 lines anti-patterns.md per skill.

Six skills × ~2.5 hours = ~15 hours focused work.

Closeout: ~1-2 hours (ROADMAP, CHANGELOG, session log; CLAUDE.md may not need changes for Phase 5 since §6 and §9 already cover activity-skills generically).

Total: ~16-17 hours. Realistically 3-5 sessions over 1-2 weeks part-time.

The Phase 4 pattern of one commit per substantive deliverable served well. For Phase 5, seven focused commits keeps each diff reviewable and lets Checkpoint 1 decisions surface incrementally if anything in implementation pushes back on the plan.

---

## 10. Closing Notes

- This plan is committed (per Phase 2 Decision 2 — transparency before staging)
- Phase 5 implementation does not begin until Decisions A–E are resolved at Checkpoint 1
- Plan adjustments accumulated during implementation will be logged in the Phase 5 session log (per validated Phase 2/3/4 pattern)
- Phase 5 inherits the conventions established in Phase 4 — reference-file pattern, ≤300 line SKILL.md, citation granularity per source's natural level, TGF synthesis acknowledged honestly
- The dogfooding continues — Phase 5 implementation uses the TGF workflow on its own construction
- After Phase 5, the activity-skill set is complete. Phase 6 begins the substantial 11+22+8+1 security skills push (Phases 6/7/8) which is the largest remaining workload
