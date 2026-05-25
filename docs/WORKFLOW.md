# Workflow Specification

The implementation contract for The Governance Framework's six-stage workflow. Phases 4–12 (skills, meta-skills, hooks, stack baselines) build against this specification.

> **v1.1 (2026-05-23):** Authority-backed Stages 1/2/3. Stage 1 grounded in TGF source-tier hierarchy, engineering FMEA-style assumption-checking, and NIST SP 800-39. Stage 2 in NIST RMF Categorize, NIST SP 800-160, and Microsoft SDL. Stage 3 in NIST SP 800-53, NIST CSF 2.0, CIS Controls v8.1, and ISO/IEC 27002 (via the CSF Informative References crosswalk). Source-tier hierarchy formalized. Citation chain target defined as rule → ASVS → CSF 2.0 Subcategory → 800-53 (via CSF IR). Workstream 2 of the framework-hardening sequence.

---

## §1 Purpose and Scope

This document specifies *how* the six-stage workflow described in `CLAUDE.md` §3 is implemented. It defines stage I/O contracts, skill activation points, hook integration contracts, subagent dispatch contracts (including JSON output schemas), tier and mode scaling matrices, the debugging-variant adaptation, and three worked examples that exercise the spec end-to-end.

**Relationship to other documents:**

- `CLAUDE.md` §3 — the operational *contract* (what the framework does on every coding/planning prompt). Loads every session. Read first.
- `docs/ARCHITECTURE.md` §20 — the subagent *role descriptions* (who the seven roles are, why they exist, what they're prevented from doing). This document specifies the *contracts* those roles produce.
- `docs/ARCHITECTURE.md` §15, §18, §19 — mode scaling, hook architecture, token efficiency. This document specifies the *operational integration points* derived from them.
- `DECISIONS.md` DEC-003, DEC-005, DEC-006 — the architectural decisions this document operationalizes. Citations are rule-level per DEC-004.

**Audience:** Phase 4–12 implementers (writing skills, meta-skills, hook scripts, stack baselines); framework operators understanding workflow behavior; advanced adopters writing custom skills or hooks against TGF.

**Out of scope:**

- Hook script bodies — Phase 12 (Hook Library) ships those against §6 contracts
- Skill content (rules, anti-patterns, canonical patterns) — Phases 4–10 ship those against §3 activation contracts
- Meta-skill implementation — Phase 11 builds the orchestration meta-skill against §4 schemas and §6 contracts
- Slash command implementations — Phase 14

**This document does NOT duplicate `CLAUDE.md` §3.** It specifies what §3 leaves implicit: how stages compose, what each stage produces and consumes, how skills/hooks/subagents integrate, and how tier and mode adjust execution.

---

## §2 Conceptual Model

The workflow is a state machine over six stages. Stages produce typed artifacts that the next stage consumes. Hooks fire on Claude Code's event lifecycle (independently of stage transitions). Subagents dispatch at specific stage points based on change tier.

### Stage state machine

```
       ┌──────────────┐    ┌───────────┐    ┌──────────────────────┐
START ─►│ 1. Research  ├───►│ 2. Scope  ├───►│ 3. Plan w/Governance ├──┐
       └──────────────┘    └───────────┘    └──────────────────────┘  │
                                                                       ▼
       ┌─────────────┐    ┌─────────────────────┐    ┌──────────────┐
  END ◄┤ 6. Commit   │◄───┤ 5. Four-Pass Review │◄───┤ 4. Implement │
       └─────────────┘    └─────────────────────┘    └──────────────┘
                                    │
                       (findings unresolved)
                                    │
                                    ▼
                          back to Stage 4 (rework)
```

### Valid transitions

- Stage `N` → Stage `N+1` is the default flow.
- Stage 5 → Stage 4 is the rework path when review surfaces blocking findings.
- Any stage → END (workflow halt) on user abort or unrecoverable error.
- Trivial-tier work skips Stages 1, 2, 3 evaluation (no codebase context to gather, no skills to evaluate); enters at Stage 4 with reduced Stage 5 (code review only).

### Termination conditions

A workflow invocation terminates when one of:

- **Success:** Stage 6 completes — commit landed, artifacts updated, session log entry generated.
- **Blocked:** Stage 5 surfaces findings the user neither fixes nor formally waives. Work stops; ERROR-LOG entry recorded; workflow re-enters from Stage 4 in a later invocation.
- **Aborted:** user explicitly halts; partial state captured to session log; no commit produced.
- **Hook denial:** a hook blocks at any stage (typically `PreToolUse` for tool calls or commit-time hook for commits). User can acknowledge override or accept the block. Either way, the workflow records the block in WAIVER-LOG (if overridden) or terminates pending user decision.

### Stage-to-stage handoff contracts

Each stage produces named artifacts the next stage consumes. The orchestrator persists handoff state in `.tgf/state/sessions/{session_id}.json` (per DEC-006).

| From → To | Artifact passed | Format |
|-----------|-----------------|--------|
| 1 → 2 | `research_findings` | Files read, prior decisions noted, related logs identified, ROADMAP position |
| 2 → 3 | `scope_definition` | Files in scope, change tier, trust boundaries affected, ROADMAP milestone, out-of-scope items |
| 3 → 4 | `governance_plan` | Skills that apply, rules to follow, anti-patterns to avoid, test requirements, hook integration points |
| 4 → 5 | `implementation_diff` | Changed files, lines added/removed, skill rules applied (with citations), AI-generated portions flagged |
| 5 → 6 | `review_findings` | All four-pass outputs, resolution status per finding, blocking vs non-blocking, waivers requested |
| 5 → 4 (rework) | `blocking_findings` | Subset of review findings requiring code change before commit |
| 6 → END | `commit_record` | Commit hash, artifacts updated, session log entry, ROADMAP delta |

### Where skills, hooks, and subagents activate

These three mechanisms are independent — they fire on different signals.

- **Skills** activate in Stage 3 (Plan with Governance) and again in Stage 5 (Four-Pass Review) when review subagents apply their rules. Skill activation is *content-driven*: skills self-determine applicability via `applies-when` conditions evaluated against the scope from Stage 2.
- **Hooks** fire on Claude Code's event lifecycle, *independently* of which workflow stage is active. `PreToolUse` fires every time a tool call is attempted, whether in Stage 1 reading or Stage 4 editing. A given workflow invocation typically fires dozens of hook events.
- **Subagents** dispatch at specific stage points based on change tier (see §5). The orchestrator (main agent) decides dispatch; subagents return structured output the orchestrator aggregates.

The conceptual separation matters: hooks enforce invariants the workflow stage doesn't know about; skills enforce rules the workflow stage applies; subagents do focused work the orchestrator delegates.

### Source-tier hierarchy

Every cited authoritative source falls into one of three tiers. Tier governs citation discipline across Stage 1 research and Stage 3 plan-with-governance work.

**Tier 1 — Must live-fetch every use.** Living documents whose content can change between fetches. OWASP Cheat Sheets, OWASP ASVS chapters, OWASP Top 10 (year-specific), vendor and framework documentation, CISA advisories. Citation discipline: §2 Sources entry in the citing skill file MUST include a "Date Verified" reflecting the most recent fetch. Re-verification cadence is quarterly per `CLAUDE.md` §14.

**Tier 2 — Publication-level citation acceptable.** Stable formal publications whose content is stable across years. NIST Special Publications (with revision number), NIST FIPS standards, IETF RFCs (with RFC number), ISO/IEC standards (with edition year), W3C Recommendations (with publication date). Citation discipline: cite at `{document-id} (Revision N, Year)` granularity. Live fetch on first use to confirm document existence and current revision; subsequent citations of the same source ID skip re-fetch.

**Tier 3 — Comparative / design-rationale only.** Books, papers, blog posts, conference talks, vendor blog content. Citation discipline: may appear in design rationale within plan documents and architecture docs. Does NOT appear in §2 Sources tables of skill files (per `DECISIONS.md` `DEC-2026-05-17-004` Clause 6).

The research-security hook pipeline (per `docs/RESEARCH-SECURITY.md`) enforces Tier 1 / Tier 2 discipline at the §2-Sources traceability level. Any citation in a skill file must trace to a verified research-log entry for its source ID; the `PreToolUse-Write` hook blocks writes that cite un-verified sources.

---

## §3 Per-Stage Specifications

Each subsection specifies one workflow stage: inputs, operations (with mode and tier conditionals), outputs, skill activation points, hook integration points, subagent dispatch points, and failure modes. Refer to §4 for subagent output schemas, §5 for tier and mode scaling matrices, §6 for hook contracts.

### Stage 1 — Research

**Purpose:** understand what exists before changing anything. Build the foundation of context that every later stage depends on.

**Inputs:**

- User prompt (the request as stated)
- Recent session logs (loaded by `SessionStart` hook into `additionalContext`; per §6)
- `PROJECT-CONTEXT.md` if present (loaded as needed)
- `ROADMAP.md` for milestone context
- `ERROR-LOG.md`, `VENDOR-LOG.md`, `WAIVER-LOG.md` for related items
- `DECISIONS.md` for architectural choices that constrain the work

**Operations:**

For coding work: read relevant files, identify the patterns currently in use, map dependencies and what touches what, check existing logs for related items, check session logs for prior context on this area, check `DECISIONS.md` for constraining choices, check `ROADMAP.md` for milestone fit.

For planning work: review `PROJECT-CONTEXT.md` for current state, review `DOMAIN-CONTEXT.md` for relevant domain knowledge, review `ROADMAP.md` for current milestones and sequencing, review existing planning artifacts (`ARCHITECTURE.md`, `STACK-DECISIONS.md`), identify dependencies between this and other planned work.

**Mode conditionals.** Exploration mode emphasizes this stage (per §5). Building+ does standard research. Maintenance mode adds regression-risk research (what else in the codebase exercises this area?).

**Tier conditionals.** Trivial skips Stage 1 entirely (no codebase context to gather). Small/Medium does inline research by the orchestrator. Large may dispatch Researcher subagents (per §4) to investigate distinct aspects in parallel.

**Outputs:** `research_findings` per §2 handoff table.

**Skill activation:** no skills typically activate in Stage 1 itself (skills evaluate in Stage 3). `CONTINUITY` (always-on) ensures session log context is loaded; `PROJECT-CONTEXT` (meta-skill) may activate if PROJECT-CONTEXT is missing or stale.

**Hook integration:** `SessionStart` fires once at session begin (loads recent session logs, initializes `.tgf/state/sessions/{session_id}.json`). `PreToolUse` fires for each file read or grep — read-only tool calls expected, no blocks expected in normal Stage 1 work.

**Subagent dispatch:** Researcher (per §4) dispatched at Large tier only, in parallel for distinct research questions. Typical Large-tier dispatch: 1–3 Researchers, each scoped to a different aspect (codebase patterns, prior decisions, related logs).

**Failure modes:**

- *Insufficient context surfaced.* Stage produces incomplete `research_findings`; remediation: loop within Stage 1 with refined queries before advancing.
- *Missing PROJECT-CONTEXT for non-trivial work.* Stage halts and escalates to user; recommend `/tgf:project-context` first.
- *Stale session logs misleading.* Memory discipline (CLAUDE.md "Before recommending from memory" section) requires verification of cited facts against current code; flag stale claims rather than treating as authoritative.

**Authoritative methodology.** Three disciplines ground Stage 1 research.

1. **TGF source-tier hierarchy** (per §2 Source-tier hierarchy above). The Tier 1 / 2 / 3 framework is the operative source-reliability discipline at TGF's scale. External grading frameworks would be uniformly Tier-1 for OWASP / NIST / MITRE / IETF and add no discriminative value here. The tier hierarchy already separates living-documents (Tier 1) from stable-publications (Tier 2) from design-rationale-only (Tier 3).
2. **Engineering FMEA-style assumption-checking.** Stage 1 explicitly identifies what the research assumes that, if wrong, invalidates the conclusion. Standard engineering review discipline applied to research output rather than to system designs. Cross-source corroboration (M5) and source-organization independence verification (M12) per `docs/RESEARCH-SECURITY.md` are the operational checks. AI memory alignment (M9) is flagged honestly when prior knowledge appears to confirm a fetched source; memory and source share common upstream and don't count as independent corroboration.
3. **NIST SP 800-39 — *Managing Information Security Risk: Organization, Mission, and Information System View*.** Threat-intelligence sourcing discipline that distinguishes strategic (long-horizon trends), operational (campaign-level), and tactical (technique-level) intelligence levels. Stage 1 research is implicitly tactical when investigating a specific change, operational when investigating broader patterns, and strategic when investigating framework-level questions.

**Stage 1 checklist** (per skill commit or change):

- [ ] All sources to cite identified at planning time. No "by reference" admissions at write time.
- [ ] Every Tier 1 source live-fetched this session (timestamp in research-log).
- [ ] Tier 2 sources confirmed via canonical index (NIST CSRC publication index, IETF datatracker, OWASP repo tags). Citation existence verified per M10.
- [ ] Tier 3 sources flagged as design-rationale-only. Do not appear in §2 Sources tables of skill files.
- [ ] Research log written for every fetch (mechanical via `PostToolUse-WebFetch`).
- [ ] Each fetch passed M3 / M4 / M11 / M13 / M14 / M18 / M19 checks, or has `flagged` status with explicit human review recorded.
- [ ] Citation-existence verified for every cited document ID (M10).
- [ ] Adversarial-source threat considered for any Tier 1 source in a high-tampering-risk location.
- [ ] Where M5 corroboration is required, at least one independent source per claim. M12 independence verified via `source-org-mapping.json`.
- [ ] AI memory alignment flagged honestly per M9.
- [ ] Any Tier 3 source used is explicitly justified.

### Stage 2 — Scope

**Purpose:** define what's changing and what isn't. Bound the work so review can evaluate against a clear contract.

**Inputs:** `research_findings` from Stage 1.

**Operations:**

For coding work: identify files to modify, the change being made, explicitly out-of-scope items, change tier (Trivial/Small/Medium/Large per `CLAUDE.md` §3 rubric), trust boundaries affected, dependencies touched, `ROADMAP.md` milestone advanced.

For planning work: identify questions being answered, decisions needing to be made, items deferred to later planning sessions, artifacts to be produced or updated, `ROADMAP.md` changes resulting.

**Mode conditionals.** Mode-agnostic; scope is a structural step.

**Tier conditionals.** Tier *determination* happens here (the rubric is applied to the scope). Trivial-tier work flagged for skip of Stages 3 and most of Stage 5.

**Outputs:** `scope_definition` per §2 handoff table. The orchestrator writes `change_tier` to `.tgf/state/sessions/{session_id}.json` at this point (per DEC-006), making it visible to subsequent hooks.

**Skill activation:** none. Scoping is meta-work.

**Hook integration:** none specific. (If the orchestrator writes the state file via a tool call, `PreToolUse`/`PostToolUse` fire for that write — not a Stage 2-specific concern.)

**Subagent dispatch:** none.

**Failure modes:**

- *Scope unclear.* Loop back to Stage 1 with research questions targeting the ambiguity.
- *Scope too large for single workflow invocation.* Surface for decomposition recommendation; user may split into multiple workflow invocations or accept the size with Large tier handling.
- *Trust boundary identification incomplete.* Stage 5 Security Auditor and Red Team will surface gaps; flag for revisiting at that point rather than blocking Stage 2.

**Authoritative methodology.** Four disciplines ground Stage 2 scope work.

1. **NIST SP 800-37 Rev 2 — Risk Management Framework, Categorize step.** Formal scope definition. Identify the system, the information types it touches (PII / PHI / payment / secrets / public), impact levels for confidentiality / integrity / availability (low / moderate / high), and the system boundary. For TGF skill commits, "system" maps to the change context: the files being modified plus their immediate dependencies.
2. **NIST SP 800-160 Vol 1 Rev 1 — *Engineering Trustworthy Secure Systems*.** System definition and scoping. Identify stakeholders, system functions, external interfaces (which mark trust boundaries), and constraints (regulatory, performance, deployment).
3. **Microsoft Security Development Lifecycle — threat-modeling scope.** Identify trust boundaries, assets crossing them, and actors on each side. Cited at SDL guidance level per `DECISIONS.md` `DEC-2026-05-17-004` Clause 6 (Tier 3 design-rationale reference).
4. **STRIDE-per-element**, applied only to trust-boundary-crossing changes. For each element (data flow, process, data store, external entity, trust boundary), consider Spoofing / Tampering / Repudiation / Information disclosure / Denial of service / Elevation of privilege. Integrating STRIDE at scope rather than after-the-fact catches whole categories of issues earlier without the overhead of a separate threat-modeling phase.

**Stage 2 checklist** (per skill commit or change):

- [ ] Files being modified explicitly listed.
- [ ] Files explicitly out of scope listed.
- [ ] Change tier identified per `CLAUDE.md` §3 rubric.
- [ ] Trust boundaries affected explicitly identified (input boundary, output boundary, persistence boundary, network boundary).
- [ ] Information types touched identified (PII / PHI / payment / secrets / public).
- [ ] STRIDE-per-element review for trust-boundary-crossing components.
- [ ] ROADMAP milestone this advances explicitly identified.
- [ ] Dependencies (other skills, framework artifacts) explicitly identified.
- [ ] Change-tier scaling for Stage 5 review determined.
- [ ] Impact-level rationale recorded (low / moderate / high for C/I/A). Informs Stage 5 review depth and waiver bar.

### Stage 3 — Plan with Governance

**Purpose:** evaluate every applicable skill against the scoped change and produce the governance plan that Stage 4 implements against.

**Inputs:** `scope_definition` from Stage 2.

**Operations:**

Apply path-based pre-filtering (per `ARCHITECTURE.md` §19) to identify candidate skills cheaply. For each candidate, load `applies-when` conditions and evaluate against `scope_definition` (paths, imports, operations, data flows). Skills matching contribute their rules; skills not matching stay silent. Synthesize matching skills' rules into a coherent governance plan: required patterns, anti-patterns to avoid, test requirements, hook integration points the implementation will trigger, expected findings categories.

**Mode conditionals.** Mode gates the skill catalog (per §5). Exploration loads always-on only by default. Building+ loads the full catalog per applies-when matching. Compliance skills load only when scope warrants per `PROJECT-CONTEXT.md`.

**Tier conditionals.** Trivial skips Stage 3 entirely. Small loads only path-matched skills. Medium loads path + import + operation-matched. Large loads full evaluation including data-flow-matched.

**Outputs:** `governance_plan` per §2 handoff table.

**Skill activation:** **this is the primary skill activation stage.** All skills evaluate applicability here. Matched skills contribute rules; their content is loaded into the planning context (per `ARCHITECTURE.md` §19 native progressive disclosure).

**Hook integration:** `PreToolUse` may fire for read tools the orchestrator uses to evaluate scope against codebase. No Stage 3-specific blocking hooks.

**Subagent dispatch:** typically none. The orchestrator does the synthesis. For Large tier with many candidate skills, may dispatch a focused Researcher (per §4) to investigate a specific governance question that the orchestrator can't resolve in-context.

**Failure modes:**

- *Skill rules conflict.* Orchestrator surfaces the conflict to the user with both rules' citations and plain-language impacts; user resolves.
- *No applicable skills (rare).* Indicates either scope is too narrow (e.g., comment-only change should be Trivial tier) or skill catalog has gaps. CODE-QUALITY almost always applies.
- *User disagrees with plan.* Revise plan; do not silently implement against the original. Plan revision is normal; pretending consensus is not.

**Authoritative methodology.** Four frameworks ground Stage 3, with NIST SP 800-53 as the structural backbone.

1. **NIST SP 800-53 Rev 5.2.0 — *Security and Privacy Controls for Information Systems and Organizations*** (current as of August 2025). ~1,000 controls across 21 families: Access Control (AC), Awareness and Training (AT), Audit and Accountability (AU), Assessment Authorization and Monitoring (CA), Configuration Management (CM), Contingency Planning (CP), Identification and Authentication (IA), Incident Response (IR), Maintenance (MA), Media Protection (MP), Physical and Environmental Protection (PE), Planning (PL), Program Management (PM), Personnel Security (PS), PII Processing and Transparency (PT), Risk Assessment (RA), System and Services Acquisition (SA), System and Communications Protection (SC), System and Information Integrity (SI), Supply Chain Risk Management (SR), and the 21st family added in Rev 5.2.0. Every rule in every Phase 6+ skill cross-maps to one or more 800-53 control IDs as part of its citation chain.
2. **NIST CSF 2.0 — Cybersecurity Framework** (2024). Six Functions: Govern (GV, added in 2.0), Identify (ID), Protect (PR), Detect (DE), Respond (RS), Recover (RC). Cross-cutting per-skill mapping: each skill maps to at least one CSF Subcategory. A skill with no Detect-function representation across its rules is a coverage gap worth flagging.
3. **CIS Controls v8.1 — top-18 prioritized overlay.** Useful as a "minimum viable" filter on which 800-53 controls actually matter at solo-developer / small-org scale. Implementation Group 1 (IG1, essential cyber hygiene) is the most actionable subset.
4. **ISO/IEC 27002:2022 — international code of practice for information security controls.** Cited via the NIST CSF 2.0 Informative References crosswalk (per `DECISIONS.md` `DEC-2026-05-17-004` Clause 5; ISO/IEC 27002 itself is paywalled). The CSF Informative References map every CSF Subcategory to ISO 27001 and ISO 27002 controls. International alignment matters for adopters with international compliance scope.

**Citation chain target.** For every rule locked in at Stage 3:

```
Rule (in the skill file)
  → OWASP ASVS chapter / Top 10 category / CWE ID (existing chain)
  → NIST CSF 2.0 Subcategory (per-skill cross-cutting mapping)
  → NIST SP 800-53 control ID (via the NIST CSF 2.0 Informative References crosswalk)
  → ISO/IEC 27002:2022 control (also via CSF Informative References; optional, for international alignment)
  → CIS Controls v8.1 Safeguard (prioritized overlay; optional)
```

The translation from CSF Subcategory through to 800-53 / ISO 27002 / CIS uses the verified `NIST-CSF-2-0-IR` (Informative References) crosswalk, which explicitly publishes those mappings. The translation from ASVS to CSF Subcategory is TGF-synthesized where the mapping is conceptually clear, since OWASP does not publish a canonical ASVS↔CSF crosswalk; honestly flagged in rule citations as `TGF-SYNTHESIS — grounded in [source]` per existing precedent in CONTINUITY and DEBUGGING skills.

This citation chain is the TARGET for new skill commits going forward. Existing Phase 4–6 skills are not retroactively re-mapped by this WORKFLOW.md amendment; that work belongs to the framework-audit and remediation workstreams.

**Worked example: `security-input-validation` Rule 5.1.** The abstract chain rendered concretely against an existing rule. Phase 6 commit 1/12 cites Rule 5.1 — *Validate at the Trust Boundary, Not Inside Business Logic* — at the rule level against `OWASP ASVS 5.0 V2.2.2`, with the broader §2 Sources table extending into ASVS V2/V4 chapters, OWASP Top 10:2025 A05, OWASP Cheat Sheet — Input Validation, NIST SP 800-218 SSDF PW.5, CWE-20, and CWE-1287. WORKFLOW-V2 extends that chain through the methodology backbone:

```
Rule 5.1 — Validate at the Trust Boundary, Not Inside Business Logic
  → OWASP ASVS 5.0 V2.2.2                                                       [existing — rule-level]
  → OWASP Top 10:2025 A05 (Injection)                                           [existing — §2 Sources]
  → CWE-20 (Improper Input Validation)                                          [existing — §2 Sources]
  → NIST SP 800-218 v1.1 SSDF PW.5                                              [existing — §2 Sources]
  → NIST CSF 2.0 PR.PS (Platform Security) — input-validation subcategory       [TGF-SYNTHESIS — illustrative bridge from ASVS V2.2.2 into platform-security family; exact CSF 2.0 Subcategory ID re-verified at rule-level update during WS4/WS5]
  → NIST SP 800-53 Rev 5.2.0 SI-10 (Information Input Validation)               [VERIFIED via NIST-CSF-2-0-IR crosswalk from PR.PS family]
  → NIST SP 800-53 Rev 5.2.0 SI-15 (Information Output Filtering)               [VERIFIED via NIST-CSF-2-0-IR crosswalk — adjacent control covering the output side of the same trust-boundary concern]
  → ISO/IEC 27002:2022 8.26 (Application security requirements)                 [VERIFIED via NIST-CSF-2-0-IR crosswalk]
  → CIS Controls v8.1 — Control 16 (Application Software Security), Safeguard 16.10 (Apply Secure Design Principles)  [VERIFIED via NIST-CSF-2-0-IR crosswalk; CIS IG1 prioritized overlay]
```

**Methodology learning surfaced by this worked example.** The WS2 plan §8 originally proposed bridging ASVS V2.2.2 directly to 800-53 via the `OWASP-ASVS-MAPPING-800-53` source. Stage 1 research (WS2 Step 2) confirmed that OWASP publishes its ASVS-to-NIST mapping only at the NIST SP 800-63B (Authentication) level — i.e., for ASVS V6 (Authentication) and adjacent IAM domains, not for V2 (Validation, Sanitization, and Encoding). The corrected chain bridges from ASVS through a TGF-synthesized CSF 2.0 Subcategory and then through to 800-53 / ISO 27002 / CIS via the verified CSF Informative References crosswalk. This is the discipline the chain demonstrates: every link is either crosswalk-verified against a Tier-1 source or honestly flagged as `TGF-SYNTHESIS` with the grounding source noted.

**Scope boundary.** This example does not retroactively update `skills/security-input-validation/SKILL.md` Rule 5.1's rule-level citation or §2 Sources table. Retroactive remap of Phase 4–6 skills against WORKFLOW-V2 is WS4/WS5 territory. The example illustrates the target chain shape; the actual rule update lands during framework audit and remediation, where the CSF 2.0 Subcategory text gets re-verified live against `NIST-CSF-2-0` and the M5 multi-source corroboration is re-run on the bridge.

**Where M5 / M8 / M9 / M12 fire at Stage 3** (per `docs/RESEARCH-SECURITY.md` §7.3):

- **M5 (Multi-source corroboration).** Before locking a control with specific parameter values (key lengths, iteration counts, timeout thresholds), verify at least two independent authoritative sources support the parameter. Recorded in the research log and cross-referenced in the Stage 3 plan output.
- **M12 (Independence verification).** The corroborating sources must come from different publishing organizations per `.tgf/state/source-org-mapping.json`. Two NIST documents don't satisfy M5; NIST plus OWASP plus ISO (via crosswalk) does.
- **M8 (Human verification).** At control-lock time, the framework surfaces a verification summary. The commit cannot proceed without an explicit approval recorded in `.tgf/state/m8-approvals/`. The Stop hook and the git pre-commit hook enforce this mechanically.
- **M9 (Memory-alignment honesty).** If AI prior knowledge appears to confirm the cited content, that counts as one source of evidence (the fetched source) rather than two. M9 is recorded in M8 verification summaries; it never substitutes for M5 corroboration.

**Stage 3 checklist** (for each rule or control locked in):

- [ ] Primary citation chain complete: rule → existing standard → NIST CSF 2.0 Subcategory → NIST SP 800-53 control via CSF IR.
- [ ] NIST CSF 2.0 Informative References consulted for 800-53 / ISO 27002 / CIS extensions where applicable.
- [ ] M5 multi-source corroboration: at least two independent sources from the research log.
- [ ] M12 independence verified: corroborating sources from different publishing organizations.
- [ ] M9 memory-alignment flagged honestly: AI prior knowledge does NOT count as independent corroboration.
- [ ] M18 exception clauses scanned: any "X is required except when..." patterns explicitly reviewed.
- [ ] M8 human approval recorded for control-locking parameter values.
- [ ] Existing-pattern check: does this rule align with how other skills handle similar concerns?
- [ ] Stage 5 Phase 2 (Security Audit) preview: would the security-auditor agent be likely to flag this?

### Stage 4 — Implement

**Purpose:** execute the plan, applying skill rules during writing. Capture findings and deviations as they emerge.

**Inputs:** `governance_plan` from Stage 3.

**Operations:**

For coding work: write code following the plan; apply skill rules as code is written; add tests as code is added; update relevant artifacts as decisions are made; flag any AI-generated portions for Stage 5 Verifier dispatch.

For planning work: produce planning artifacts; document decisions in `DECISIONS.md`; update `PROJECT-CONTEXT.md` if material; update `ROADMAP.md` if milestones or sequencing change; identify implementation work that flows from the planning.

**Mode conditionals.** Mode-agnostic at the implementation step itself; mode shaped the plan that Stage 4 executes.

**Tier conditionals.** Trivial: orchestrator does the change inline. Small/Medium: orchestrator implements directly with skill-rule application. Large: orchestrator may decompose into discrete tasks and dispatch Implementer subagents (per §4) in parallel for independent file changes. Decomposition criteria: tasks must have disjoint file scopes (no shared-file editing) and clear interfaces between them.

**Outputs:** `implementation_diff` per §2 handoff table, including `ai_generated_portions` array flagging regions for Verifier exercise.

**Skill activation:** skills *inform* implementation (rules cited as code is written) but don't re-evaluate. The activation happened in Stage 3; Stage 4 applies the activated rules.

**Hook integration:** `PreToolUse` fires for every `Bash`, `Write`, `Edit` call — the three universal hooks (per §6) actively check for dangerous git operations, secrets in commits, destructive database operations. `PostToolUse` fires for telemetry (Building+ mode). `FileChanged` fires when framework integrity files (CLAUDE.md, ARCHITECTURE.md, DECISIONS.md, WORKFLOW.md, skill files, hook scripts) are modified — surfaces to user (Hardening+ mode).

**Subagent dispatch:** Implementer (per §4) dispatched at Large tier when work decomposes. Each Implementer receives a disjoint file scope and the relevant portion of `governance_plan`. Returns `ImplementerOutput`.

**Failure modes:**

- *Implementation blocked by environment.* Missing tool, missing credential, missing dependency — orchestrator logs to `ERROR-LOG.md` and surfaces for user resolution before workflow continues.
- *Tests failing.* Loop within Stage 4 to fix; do not advance to Stage 5 with known failing tests (Stage 5 review would just confirm that the tests fail; the loop should fix them first).
- *Plan turned out to require revision.* Loop back to Stage 3 with the implementation finding that surfaced the planning gap. Do not silently deviate.
- *AI-generated code looks plausible but unverified.* Mark `ai_generated_portions` accurately so Stage 5 Verifier dispatches; do not skip the flag because "the code looks right."

**Methodology cross-reference.** Stage 3's citation chain travels with the implementation. Each cited rule's full chain (ASVS → CSF Subcategory → 800-53 via CSF IR → optionally ISO 27002 / CIS) is preserved in the skill's §2 Sources table and at rule-level citations in `rules.md`. Implementation does not introduce new methodology; it executes against the Stage 3 plan.

### Stage 5 — Four-Pass Review

**Purpose:** verify what was built against what was planned, what is good craftsmanship, what is secure, what is adversarially robust, and what integrates with the project's broader context.

**Inputs:** `implementation_diff`, `governance_plan`.

**Operations:**

Dispatch review subagents per tier (per §5 tier scaling table). Each subagent runs the two-stage spec-then-quality pass (per `ARCHITECTURE.md` §20 and §4 `ReviewPass` type). Aggregate subagent outputs at the orchestrator: deduplicate findings (same issue caught by multiple subagents appears once), normalize severity per `CLAUDE.md` §11 model, attribute findings to source subagent for traceability, route findings per `CLAUDE.md` §11 resolution rule (fix / waive in `WAIVER-LOG.md` / escalate to `VENDOR-LOG.md`).

**Mode conditionals.** Mode adjusts review *emphasis* (per §5 mode scaling table). Hardening+ gives Red Team extra weight; Maintenance+ gives Holistic extra weight on forward compatibility; Exploration reduces to Code Reviewer + light Holistic.

**Tier conditionals.** Trivial: code review only, inline by orchestrator. Small: Code Reviewer + Holistic Reviewer (2 subagents). Medium: full four-pass (4 subagents in parallel). Large: full four-pass + Verifier (if `ai_generated_portions` non-empty) + possibly additional Researcher for review-time questions.

**Outputs:** `review_findings` per §2 handoff table.

**Skill activation:** review subagents apply skills' rules. Security Auditor (per §4) applies applicable security skills; Holistic Reviewer applies CONTINUITY's decision-documentation discipline; Code Reviewer applies CODE-QUALITY's principles.

**Hook integration:** `SubagentStart` and `SubagentStop` fire for each dispatched review subagent (per §6 telemetry). `PreToolUse` may fire if subagents need to read additional context.

**Subagent dispatch:** per tier scaling (§5). Subagents dispatch in parallel where possible (the four review phases at Medium and Large tier run concurrently, not sequentially — this is why orchestration adds value over single-agent work).

**Failure modes:**

- *Subagent disagreement on a finding.* Orchestrator surfaces both perspectives in aggregation; user decides. Do not silently resolve.
- *Blocking findings (Critical/High that the user has not fixed or waived).* Loop back to Stage 4 with `blocking_findings` per §2 handoff. Stage 6 does not run until all blocking findings are resolved. On Stage 5 re-entry after rework, the orchestrator dispatches a *reduced* subagent set rather than full re-dispatch: the subagents that surfaced the original findings re-run on the changed regions, plus Verifier if the fix includes AI-generated code. Full re-dispatch is reserved for cases where the fix touched files outside the original review scope (broader changes warrant broader review).
- *Non-blocking findings (Medium/Low).* User decides fix or waive; either way, the finding is logged before Stage 6 commits.
- *Verifier dispatched but no AI-generated portions were actually flagged.* Indicates `ImplementerOutput.ai_generated_portions` was incomplete in Stage 4. Loop back to Stage 4 to re-flag rather than skipping Verifier — the empirical verification matters.

**Methodology cross-references.**

- **Security Auditor (Phase 2)** applies the NIST 800-53 + CSF 2.0 Subcategory mappings produced at Stage 3 as part of its review. Where a rule's chain is incomplete (e.g., missing CSF Subcategory mapping), the Security Auditor flags it.
- **Holistic Reviewer (Phase 4)** verifies the Stage 1 research-log → §2 Sources traceability and the Stage 3 citation chain completeness. Missing TGF-synthesis annotations or unjustified Tier 3 source usage surface as Holistic findings.

### Stage 6 — Commit

**Purpose:** land the work and capture the context that future sessions will need. Verify completion before declaring done.

**Inputs:** `review_findings` (with all blocking findings resolved).

**Operations:**

For coding work: produce commit message that explains the *why* not just the *what*; generate session log entry capturing what was researched, scoped, planned, implemented, and reviewed; update relevant artifacts (`DECISIONS.md` if architectural, `PROJECT-CONTEXT.md` if material, `ROADMAP.md` if milestones progressed or shifted, `SCHEMA-HISTORY.md` if schema changed); update appropriate logs (`ERROR-LOG.md`, `VENDOR-LOG.md`, `WAIVER-LOG.md`).

For planning work: commit planning artifacts; generate session log entry capturing the planning process and outcomes; update `ROADMAP.md`, `ARCHITECTURE.md`, or other affected planning documents.

**Verification before completion:** before declaring work done, verify it actually is done. Did the change accomplish what was scoped? Did tests pass? Did the four-pass review actually run at the appropriate depth? Are findings logged appropriately? Is the session log entry captured? Is `ROADMAP.md` updated if the change affected milestone progress? For AI-generated code: was it empirically verified rather than just reviewed for plausibility?

**Mode conditionals.** Mode-agnostic at commit time; mode shaped the work that committing closes.

**Tier conditionals.** Trivial: commit message + commit. Small: commit + session log entry. Medium: commit + session log + ROADMAP delta. Large: commit + session log + ROADMAP delta + `DECISIONS.md` entry (if architectural) + `SCHEMA-HISTORY.md` entry (if schema-affecting).

**Outputs:** `commit_record` per §2 handoff table.

**Skill activation:** `CONTINUITY` (always-on) ensures all log discipline. The session log entry generation IS CONTINUITY's primary Stage 6 output.

**Hook integration:** `PreToolUse` fires for `Bash(git commit ...)` — workflow hooks (Building+ mode) verify tests pass, verify session log entry exists, verify `ROADMAP.md` updated. Git pre-commit hooks (if installed via `.claude/git-hooks/`) fire commit-time enforcement that runs regardless of whether commit was Claude-initiated. `PostToolUse` fires after commit for telemetry. `SessionEnd` fires at session close (if this is the last commit of the session); generates final session log entry and cleans up `.tgf/state/sessions/{session_id}.json`.

**Subagent dispatch:** none typically. (For very Large changes producing multiple commits, the orchestrator may sequence commits without subagent dispatch — each commit is itself a workflow invocation.)

**Failure modes:**

- *Pre-commit hook blocks.* Fix the underlying issue and create a NEW commit; never `--amend` past a hook failure (per `CLAUDE.md` Git Safety Protocol — `--amend` after a failed commit modifies the *previous* commit, which can destroy work).
- *Commit produces unexpected state* (wrong branch, wrong files, partial staging). Investigate before any destructive recovery; do not `git reset --hard` as a shortcut.
- *User disagrees with commit message.* Revise the message via `git commit --amend -m` for the *current* (just-made) commit only — never amend earlier commits.
- *Session log entry not generated.* Loop within Stage 6 to generate it; do not commit Stage 6 as "done" without the entry, since future sessions depend on it.

---

## §4 Subagent Output Schemas

Per `DEC-2026-05-17-003` Clause 3, seven subagent roles produce structured JSON output. This section defines those schemas in TypeScript-style interface notation (per Phase 3 Checkpoint 1 Decision B — readable for human implementers; mechanically translatable to JSON Schema if Phase 11 needs runtime validation).

All schemas assume strict mode: unknown fields are an error; missing required fields are an error.

### Cross-cutting types

These types appear in multiple role outputs.

```typescript
type Severity = "critical" | "high" | "medium" | "low";

type Citation = {
  source: string;            // e.g., "OWASP ASVS 5.0", "NIST SP 800-63B"
  rule_id: string;           // e.g., "V6.2.2", "§5.1.1.2"
  rule_text?: string;        // Verbatim or paraphrased; included when concise
};

type Location = {
  file: string;              // Absolute or repo-relative path
  line_start: number;
  line_end: number;
};

type Finding = {
  id: string;                // Stable identifier within this run, e.g., "F-014"
  severity: Severity;
  citation: Citation;
  plain_language_impact: string;  // What this means in practice; per CLAUDE.md §1
  location: Location;
  description: string;       // What the finding is (the rule violation in this context)
  remediation: string;       // What to do about it (concrete next action)
  subagent_attribution: SubagentRole;  // Which subagent surfaced this (set by orchestrator)
};

type SubagentRole =
  | "researcher"
  | "implementer"
  | "code_reviewer"
  | "security_auditor"
  | "red_team"
  | "holistic_reviewer"
  | "verifier";

type ReviewPass = {
  spec_compliance: { matches: boolean; deviations?: string[] };
  quality: { passes: boolean; reasoning: string };
};
```

The `Finding` type is the canonical finding shape per `CLAUDE.md` §11 severity model. Review subagents produce `Finding[]`; the orchestrator deduplicates and aggregates.

### Role: Researcher

Dispatched from Stage 1 for Large-tier changes to investigate one aspect of the codebase or project artifacts.

```typescript
type ResearcherInput = {
  question: string;              // What to investigate
  scope_hints: {
    paths?: string[];            // Suggested files/directories to focus on
    keywords?: string[];         // Symbols, terms to grep for
    related_decisions?: string[]; // DEC-IDs the orchestrator thinks may matter
  };
  budget: { max_files_read: number; max_subagent_dispatches: 0 };  // Researchers don't spawn other subagents
};

type ResearcherOutput = {
  question: string;              // Echo for traceability
  findings: {
    relevant_files: { path: string; why_relevant: string }[];
    prior_decisions: { dec_id: string; how_it_constrains: string }[];
    related_logs: { log: "ERROR-LOG" | "VENDOR-LOG" | "WAIVER-LOG"; entry_id: string; relevance: string }[];
    roadmap_position?: { phase: string; milestone: string };
    patterns_observed: string[];  // Code patterns currently in use that the orchestrator should respect
  };
  unanswered: string[];          // What the Researcher could not determine
  confidence: "high" | "medium" | "low";  // Self-assessed; low means "verify before using"
};
```

**Worked example.** Input: `{ question: "What authentication middleware patterns exist in this codebase?", scope_hints: { paths: ["middleware/", "auth/"] } }`. Output flags `middleware/auth.ts` and `auth/session.ts` as primary, notes `DEC-2025-XX-012` (chose JWT over session cookies for stateless backend), confirms no related log entries, returns `confidence: "high"`.

### Role: Implementer

Dispatched from Stage 4 when Large-tier work decomposes into discrete tasks (typically 2–5 implementers in parallel for independent file changes).

```typescript
type ImplementerInput = {
  task: string;                  // What to implement
  scope: {
    files_in_scope: string[];    // Files this Implementer may modify
    files_read_only: string[];   // Files this Implementer may read for context but not modify
    out_of_scope: string[];      // Files this Implementer must not touch
  };
  governance_plan: {
    skills_to_apply: { name: string; rule_ids: string[] }[];
    anti_patterns_to_avoid: string[];
    test_requirements: string;
  };
  budget: { max_files_written: number; max_subagent_dispatches: 0 };
};

type ImplementerOutput = {
  task: string;                  // Echo
  diff: {
    files_modified: { path: string; lines_added: number; lines_removed: number }[];
    files_created: string[];
    files_deleted: string[];
  };
  skill_rules_applied: { skill: string; rule_id: string; where: Location }[];
  tests_added: { path: string; test_count: number }[];
  ai_generated_portions: Location[];  // Per §16; flags regions for Verifier
  deviations_from_plan: string[];     // What didn't go as scoped, and why
  blockers_encountered: string[];     // What stopped progress, if anything
};
```

**Worked example.** Input: implement `validateSessionToken()` in `auth/session.ts`. Output reports 47 lines added across 1 file, 3 unit tests in `auth/session.test.ts`, applies `security-iam-sessions` rules `R-3.1` (cryptographically random session IDs) and `R-3.4` (short expiry), flags lines 23–41 as AI-generated for Verifier exercise.

### Role: Code Reviewer

Phase 1 of four-pass review. Evaluates craftsmanship. Fresh context — does not share the Implementer's mental model.

```typescript
type CodeReviewerInput = {
  diff: ImplementerOutput["diff"];
  governance_plan: ImplementerInput["governance_plan"];
  scope: ImplementerInput["scope"];
};

type CodeReviewerOutput = {
  review_pass: ReviewPass;
  findings: Finding[];           // Craftsmanship findings: type safety, error handling, naming, anti-patterns, test coverage, scale-awareness, solo-maintainability
  positive_notes?: string[];     // Optional; patterns done well, worth preserving in future work
};
```

**Worked example.** Reviewing the Implementer's `validateSessionToken()` diff. Output: `review_pass.spec_compliance.matches = true`; `review_pass.quality.passes = false`; one Medium finding at `auth/session.ts:38` — error path swallows the underlying exception without context, violating CODE-QUALITY error-handling principle; remediation: rethrow with context using `Error.cause`.

### Role: Security Auditor

Phase 2 of four-pass review. Applies applicable security skills' rules.

```typescript
type SecurityAuditorInput = {
  diff: ImplementerOutput["diff"];
  governance_plan: ImplementerInput["governance_plan"];
  trust_boundaries_affected: string[];  // Identified in Stage 2 Scope
  data_flows: { source: string; sink: string; data_classification: string }[];
};

type SecurityAuditorOutput = {
  review_pass: ReviewPass;
  findings: Finding[];           // Security findings with citation per DEC-004
  skills_applied: string[];      // Which security skills evaluated; for telemetry
};
```

**Worked example.** Same `validateSessionToken()` diff. Output applies `security-iam-sessions` and `security-cryptography` skills; surfaces a High finding — session ID compared with `==` rather than constant-time equality, citing `OWASP ASVS 5.0 V3.4.1`; plain-language impact: timing side-channel could reveal valid session IDs to attackers measuring response latency.

### Role: Red Team

Phase 3 of four-pass review. Adversarial perspective.

```typescript
type RedTeamInput = {
  diff: ImplementerOutput["diff"];
  scope: ImplementerInput["scope"];
  trust_boundaries_affected: string[];
  attack_surface: string;        // Summary of what's reachable from outside the trust boundary
};

type RedTeamOutput = {
  review_pass: ReviewPass;
  findings: Finding[];           // Adversarial findings: injection, authz bypass, race conditions, business logic abuse, resource exhaustion, failure-mode exploitation
  scenarios_tested: { scenario: string; outcome: "exploitable" | "mitigated" | "out_of_scope" }[];
};
```

**Worked example.** Same `validateSessionToken()` diff. Output tests 4 scenarios — replay-after-expiry (mitigated), token-substitution-from-another-user (mitigated), race-condition-on-renewal (`exploitable`: window between expiry check and renewal allows brief unauthorized acceptance), brute-force-id-guessing (mitigated by random-128-bit IDs). One High finding on the race condition with concrete reproduction steps.

### Role: Holistic Reviewer

Phase 4 of four-pass review. TGF-specific integration verification (the value TGF adds over generic review).

```typescript
type HolisticReviewerInput = {
  diff: ImplementerOutput["diff"];
  governance_plan: ImplementerInput["governance_plan"];
  scope: ImplementerInput["scope"];
  roadmap_milestone: string;
  project_context_summary: string;  // From PROJECT-CONTEXT
  prior_decisions_in_area: { dec_id: string; summary: string }[];
};

type HolisticReviewerOutput = {
  review_pass: ReviewPass;
  findings: Finding[];           // Integration findings: spec compliance, codebase fit, architectural alignment, regression risk, forward compatibility, roadmap alignment, solo-maintainability, decision documentation
  roadmap_delta: { milestone_advanced: boolean; new_dependencies?: string[]; slip_risk?: string };
  decision_documentation_status: { decisions_made_in_implementation: string[]; documented_in_DECISIONS: boolean };
};
```

**Worked example.** Same `validateSessionToken()` diff. Output: milestone "authentication hardening" advanced; codebase-fit confirmed (matches existing middleware patterns in `middleware/auth.ts`); one Medium finding — implementation chose JWT verification approach not documented in DECISIONS.md despite being a non-trivial architectural choice (remediation: add DEC-NNN capturing the JWT-vs-session-cookie reasoning); forward-compatibility: no concerns.

### Role: Verifier

Empirically exercises AI-generated code per `CLAUDE.md` §16. Dispatched conditionally when `ImplementerOutput.ai_generated_portions` is non-empty.

```typescript
type VerifierInput = {
  diff: ImplementerOutput["diff"];
  ai_generated_portions: Location[];
  test_command: string;          // How to run the project's test suite
  scope: ImplementerInput["scope"];
};

type VerifierOutput = {
  review_pass: ReviewPass;       // spec_compliance: did AI portions match the plan? quality: do they actually work?
  test_results: { passed: number; failed: number; failure_details?: string[] };
  edge_cases_exercised: { case: string; outcome: "pass" | "fail" | "skip" }[];
  plausible_but_wrong_patterns_checked: {
    pattern: "hallucinated_api" | "fabricated_signature" | "assumed_library_behavior" | "near_correct_syntax";
    location: Location;
    actual_behavior: string;
  }[];
  findings: Finding[];           // Findings specific to AI-generated regions
};
```

**Worked example.** Verifier exercises AI-generated lines 23–41 in `auth/session.ts`. Output: test results 14 passed / 1 failed; edge cases exercised include expired-token (pass), malformed-base64 (pass), missing-issuer-claim (fail — AI assumed `jose.decodeJwt()` validates issuer by default, which it does not); one Critical finding documenting the hallucinated-library-behavior pattern with remediation pointing to explicit `verifyIss` configuration.

### Schema discipline

Three rules govern subagent outputs:

1. **Subagent attribution preserved.** Per `ARCHITECTURE.md` §20, the orchestrator never claims a subagent's finding as its own. The `subagent_attribution` field on every `Finding` is set by the orchestrator and surfaces in user-facing aggregation.
2. **Two-stage spec/quality review enforced.** Every review role's output includes a `review_pass` object with both `spec_compliance` and `quality` evaluations. Both must pass for the review to return ✅. One passing while the other fails is a legitimate outcome — well-built wrong thing or well-spec'd broken thing.
3. **Failure modes are part of the contract.** Schemas include `blockers_encountered`, `unanswered`, `deviations_from_plan` so that incomplete or partial work surfaces rather than gets silently dropped.

---

## §5 Tier and Mode Scaling Tables

### Change tier scaling

Per `ARCHITECTURE.md` §19 and §20, change tier determines orchestration depth.

| | Trivial | Small | Medium | Large |
|---|---|---|---|---|
| **Examples** | Typo, comment, formatting | Single-function bug fix, no trust boundary change | Multi-file feature, no architectural change | New feature, architectural change, trust boundary modification |
| **Stages active** | 4, 5 (light), 6 | 1–6 (light) | 1–6 (full) | 1–6 (full + decomposition) |
| **Stage 1 subagents** | none | none | none | 1–3 Researchers in parallel |
| **Stage 4 subagents** | none | none | none | 2–5 Implementers in parallel (when work decomposes) |
| **Stage 5 subagents** | none (inline by orchestrator) | Code Reviewer + Holistic Reviewer | Code Reviewer + Security Auditor + Red Team + Holistic Reviewer | All four + Verifier (if AI-generated portions present) |
| **Review depth** | Code review only (inline) | Phase 1 + Phase 4 | All 4 phases standard depth | All 4 phases + extra red team weight |
| **Skills evaluated** | Always-on only | Always-on + path-matched skills | Path-matched + import-matched + operation-matched skills | Full evaluation including data-flow-matched skills |
| **Logging required** | Commit message | Commit + session log entry | Commit + session log + ROADMAP delta | Commit + session log + ROADMAP delta + DECISIONS entry (if architectural) + SCHEMA-HISTORY (if schema-affecting) |

### Project mode scaling

Per `ARCHITECTURE.md` §15, project mode determines what skills are eligible to evaluate and what review emphasis applies.

| | Exploration | Prototype | Building (default) | Hardening | Maintenance |
|---|---|---|---|---|---|
| **Skill catalog gated** | Always-on only by default | Always-on + core security (input validation, output encoding, secrets, basic auth) | Full skill catalog (per applies-when conditions) | Full skill catalog | Full skill catalog |
| **Stage emphasis** | Stages 1–2 (Research, Scope) primary; Stage 3 minimal | Stages 1–4 standard; Stage 5 light | All stages standard | Stage 3 emphasizes threat modeling; Stage 5 emphasizes adversarial perspective | Stage 3 emphasizes regression risk; Stage 5 emphasizes forward compatibility |
| **Stage 5 review focus** | Code review + light holistic | Code review + Security Auditor (core only) + Holistic | All four phases | All four phases + extra Red Team weight | All four phases + extra Holistic weight |
| **Waiver bar** | Low (exploration findings flagged for re-evaluation at promotion) | Standard | Standard | High (justification required; revisit date mandatory) | Standard with regression-prevention emphasis |
| **BASELINE-AUDIT cadence** | N/A | At promotion | At promotion; quarterly review | Quarterly | Annual + at major architectural change |

### Composition rule

When tier and mode both apply (always the case), mode gates skill *catalog* and review *emphasis*; tier scales *orchestration depth* and *review breadth* within whatever skills the mode allows.

Examples:

- **Medium tier in Exploration mode:** Stage 5 dispatches Code Reviewer + Holistic Reviewer, but the Security Auditor doesn't fire because Exploration mode doesn't load detailed security skills. The two reviewers run their full two-stage spec/quality pass.
- **Small tier in Hardening mode:** Stage 5 dispatches Code Reviewer + Holistic Reviewer (tier scaling). The Code Reviewer's `review_pass.quality` evaluation gets extra weight on regression risk because mode emphasizes adversarial perspective; this surfaces as more findings, not as additional subagents.
- **Large tier in Maintenance mode:** Full orchestration (Researchers + Implementers + all four reviewers + Verifier), but Stage 3 governance plan emphasizes regression checks; Stage 5 Holistic Reviewer gets extra weight on forward compatibility.

The composition rule prevents over-orchestration in light modes (Exploration's Medium-tier change doesn't pay for Security Auditor it can't usefully run) and under-rigor in heavy modes (Hardening's Small-tier change still gets adversarial weight in the review it does run).

---

## §6 Hook Integration Contracts

Hooks are specified per Claude Code event (Decision C: per-event primary structure with purpose cross-reference table). Each contract names: TGF purpose, stdin fields TGF relies on (beyond Claude Code's defaults), expected exit semantics, expected stdout, and mode profiles that invoke this hook.

### Hooks by purpose (cross-reference)

| Purpose | Events used | Universal? |
|---------|-------------|------------|
| **Safety** — prevent destructive operations | `PreToolUse` (matches `Bash(git ...)`, `Bash(rm ...)`, database tool calls) | Yes — always active |
| **Workflow** — enforce session/commit discipline | `SessionEnd` (session log entry), `PreToolUse` (matches `Bash(git commit ...)` for test verification), git pre-commit hook | Mode-gated (Prototype+) |
| **Governance** — log security-relevant operations, detect framework integrity changes | `PostToolUse`, `FileChanged`, `ConfigChange` | Mode-gated (Building+) |
| **Telemetry** — record per-session data | `SessionStart`, `SessionEnd`, `SubagentStart`, `SubagentStop`, `PostToolUse` | Active when telemetry enabled |
| **TGF state lifecycle** | `SessionStart` (init `.tgf/state/sessions/{session_id}.json`), `SessionEnd` (cleanup) | Always active |

### TGF context injection mechanism (per DEC-006)

`project_mode`, `change_tier`, and `current_stage` live in `.tgf/state/sessions/{session_id}.json` per `DEC-2026-05-19-006`. Hooks read this file at fire time. The `session_id` available in every hook's stdin JSON keys the file lookup.

**Phase 3 Step 1 verification (2026-05-19):** the Claude Code Hooks reference confirms there is no built-in hook-to-hook state mechanism. File-based session-keyed state is the only documented path. Environment variables via `CLAUDE_ENV_FILE` are an adjacent mechanism but flow only to subsequent Bash tool invocations, not to other hooks; TGF may use this complementarily for exposing `TGF_PROJECT_MODE` to user-run shell commands, but the primary mechanism is the session state file.

Pseudocode for hooks reading TGF context:

```bash
# In any .claude/hooks/<EventName>/NN-tgf-aware.sh script:
STDIN=$(cat)
SESSION_ID=$(echo "$STDIN" | jq -r '.session_id')

# IMPORTANT: validate session_id before using in path construction.
# Even though Claude Code controls the value, defense-in-depth: reject any
# session_id that contains characters outside [A-Za-z0-9_-] to prevent
# path traversal if the upstream contract ever changes.
if ! [[ "$SESSION_ID" =~ ^[A-Za-z0-9_-]+$ ]]; then
    echo '{"systemMessage": "TGF: invalid session_id format; skipping state load"}' >&2
    exit 0  # Fail open for context-loading hooks; closed for safety-critical ones
fi

STATE_FILE=".tgf/state/sessions/${SESSION_ID}.json"

if [ -f "$STATE_FILE" ]; then
    PROJECT_MODE=$(jq -r '.project_mode' "$STATE_FILE")
    CHANGE_TIER=$(jq -r '.change_tier // "unknown"' "$STATE_FILE")
fi
```

Phase 12 hook scripts should factor the validation + state load into a shared helper (`.claude/hooks/lib/load-tgf-context.sh`) rather than duplicating per script.

### Output schema (richer than ARCHITECTURE.md §18 documented)

Phase 3 Step 1 research surfaced that `PreToolUse` hooks can return a richer `hookSpecificOutput` object beyond exit-2 blocking:

```typescript
type PreToolUseHookOutput = {
  // Universal fields (any hook):
  continue?: boolean;          // false stops Claude entirely
  stopReason?: string;
  suppressOutput?: boolean;
  systemMessage?: string;

  // PreToolUse-specific:
  hookSpecificOutput?: {
    hookEventName: "PreToolUse";
    permissionDecision?: "allow" | "deny" | "ask" | "defer";
    permissionDecisionReason?: string;   // Surfaced to user when "deny" or "ask"
    updatedInput?: object;                // Modified tool_input the tool actually receives
    additionalContext?: string;           // Injected into Claude's context (10k char cap)
  };
};
```

TGF's three universal hooks use `permissionDecision: "deny"` with `permissionDecisionReason` for clean user-facing blocks, falling back to exit 2 + stderr only for unrecoverable hook script errors. The richer schema improves user UX over the exit-2 path.

**Phase 12 verification note:** Phase 3 Step 1 research found the value `permissionDecision: "defer"` listed in Claude Code's hook output schema but without explicit semantics in the spot-checked documentation. Phase 12 implementers should re-verify the canonical Claude Code Hooks reference for what `"defer"` does (most likely: punts the decision to Claude Code's normal permission flow rather than the hook explicitly deciding) before relying on it. TGF's current §6 contracts use only `"allow"` and `"deny"`; `"ask"` and `"defer"` remain available for future use once semantics are confirmed.

### Per-event contracts

#### `SessionStart`

**Purpose:** initialize TGF session state file; load recent session logs into context; verify framework integrity (CLAUDE.md, ARCHITECTURE.md, DECISIONS.md present and parseable); inject project mode summary into Claude's context.

**Relied-upon stdin fields:** `session_id`, `cwd`, `source` (one of `"startup"`, `"resume"`, `"clear"`, `"compact"` — TGF behavior differs per source; `"resume"` should load existing state, not overwrite).

**Expected exit:** 0 (allow). Non-zero exits at session start are blocking and surface as user errors.

**Expected stdout:** JSON with `additionalContext` field containing project mode summary + recent session log excerpt. Optionally `systemMessage` for user-visible status.

**Mode profiles:** active in all modes (state initialization is universal).

#### `SessionEnd`

**Purpose:** generate session log entry capturing topics discussed, decisions made, ROADMAP deltas, findings logged; clean up `.tgf/state/sessions/{session_id}.json`; emit telemetry summary.

**Relied-upon stdin fields:** `session_id`, `cwd`.

**Expected exit:** 0. SessionEnd hook failures should never block session close; non-zero is logged and ignored.

**Expected stdout:** none required.

**Mode profiles:** active in Prototype+ modes (Exploration mode skips session log discipline as too much friction for figuring-out-what-to-build work).

#### `PreToolUse`

**Purpose:** enforce three universal safety hooks (block-dangerous-git, block-secrets-commit, block-destructive-db); enforce workflow gates (tests-pass-before-commit in Building+ mode); record tool dispatch for telemetry.

**Relied-upon stdin fields:** `session_id`, `cwd`, `tool_name`, `tool_input`, `permission_mode`.

**Expected exit:** 0 (allow) or via richer schema (`hookSpecificOutput.permissionDecision`).

**Expected stdout:** for blocks, use `hookSpecificOutput.permissionDecision: "deny"` with `permissionDecisionReason` (preferred over exit 2 + stderr). For input modification (e.g., adding `--no-color` to a command), use `hookSpecificOutput.updatedInput`. For `"ask"` (defer-to-user) cases, use `permissionDecision: "ask"` with `permissionDecisionReason` explaining what to confirm.

**Mode profiles:**

- Always active: `block-dangerous-git`, `block-secrets-commit`, `block-destructive-db`
- Prototype+: `verify-session-log-on-commit` (matches `Bash(git commit ...)`)
- Building+: `verify-tests-pass` (matches `Bash(git commit ...)`), `log-security-operations` (matches database tool calls, network tool calls)
- Hardening+: `verify-waiver-revisit-dates`

#### `PostToolUse`

**Purpose:** log security-relevant operations for telemetry and incident response; detect framework artifact modifications (CLAUDE.md, ARCHITECTURE.md, DECISIONS.md, skill files) and surface for review.

**Relied-upon stdin fields:** `session_id`, `cwd`, `tool_name`, `tool_input`, `tool_use_id`.

**Expected exit:** 0. PostToolUse blocks the post-tool reaction, not the tool itself (tool already ran); use sparingly. `decision: "block"` in stdout pattern available for cases where post-tool state warrants halting the workflow.

**Expected stdout:** none required for telemetry path; for framework-integrity findings, JSON with `systemMessage` flagging the change for user awareness.

**Mode profiles:** Building+ (Exploration and Prototype skip telemetry overhead).

#### `SubagentStart`

**Purpose:** record subagent dispatch for telemetry (per `ARCHITECTURE.md` §20 — subagent operations logged); inject TGF context into subagent's working environment (the same `.tgf/state/sessions/{session_id}.json` is read by the subagent if it dispatches its own hooks).

**Relied-upon stdin fields:** `session_id`, `agent_id`, `agent_type`.

**Expected exit:** 0.

**Expected stdout:** none required.

**Mode profiles:** Building+ (always logs in Hardening+ for adversarial-AI defense per `MITRE ATLAS` AI agent technique catalog).

#### `SubagentStop`

**Purpose:** record subagent completion + output summary for telemetry; aggregate subagent findings into the orchestrator's review aggregation buffer.

**Relied-upon stdin fields:** `session_id`, `agent_id`, `agent_type`.

**Expected exit:** 0.

**Expected stdout:** optional `decision: "block"` if the subagent produced critical findings the orchestrator should not silently aggregate (rare; use for fail-safe behavior).

**Mode profiles:** Building+.

#### `FileChanged`

**Purpose:** detect modifications to framework integrity files (`CLAUDE.md`, `docs/ARCHITECTURE.md`, `DECISIONS.md`, `docs/WORKFLOW.md`, `.claude/skills/**/SKILL.md`, `.claude/hooks/**/*.sh`); record changes for telemetry; flag unexpected changes for user attention.

**Relied-upon stdin fields:** `session_id`, plus event-specific path fields (per Claude Code Hooks reference; spot-check field name during Phase 12 implementation).

**Expected exit:** 0.

**Expected stdout:** for integrity changes, JSON with `systemMessage` flagging the change.

**Mode profiles:** Hardening+ (Building mode logs changes but doesn't actively flag; Hardening surfaces them for review).

#### `ConfigChange`

**Purpose:** alert on changes to `.claude/settings.json`, `.claude/hooks/profile.json`, or `.tgf/` configuration that affect framework behavior; require explicit user awareness for hook-profile changes.

**Relied-upon stdin fields:** `session_id`, plus event-specific path fields.

**Expected exit:** 0 (logging) or 2 (block, for changes that would disable safety hooks without explicit acknowledgment).

**Expected stdout:** JSON with `systemMessage` describing the config change.

**Mode profiles:** Building+ (with stricter block behavior in Hardening+).

### Three universal hooks — override semantics

The three always-active safety hooks (`block-dangerous-git`, `block-secrets-commit`, `block-destructive-db`) implement the hard-refusal severity level from `CLAUDE.md` §5. They use `permissionDecision: "deny"` by default. User override requires explicit acknowledgment per the §5 informed-confirmation pattern:

- The hook surfaces `permissionDecisionReason` describing the harm and the override path
- User responds with explicit acknowledgment (typed override command, not implicit "try again")
- Override is logged to `WAIVER-LOG` with timestamp, command attempted, override reason, and revisit date
- The hook re-fires on retry; the override mechanism honors the prior acknowledgment for that specific operation only (not blanket exemption)

This preserves §5's intent: the framework respects user authority but does not silently produce harmful operations.

---

## §7 Debugging Variant

When work is debugging rather than building, the six-stage workflow keeps its shape but its stage operations shift. The mapping is one-to-one; the same handoff contracts (§2), tier scaling (§5), and hook integrations (§6) apply.

| Building stage | Debugging stage | What changes |
|----------------|-----------------|--------------|
| 1. Research | **Reproduce** | Operations focus on triggering the bug reliably (find inputs, environments, sequences that produce it). Inputs include any error reports, stack traces, user-provided repro steps. Failure mode: cannot reproduce → loop within stage with broader hypothesis space before declaring "cannot reproduce" (which itself is a finding worth logging). |
| 2. Scope | **Isolate** | Operations bound the bug — narrow which file, function, or condition causes it. `change_tier` reflects bug *scope* rather than fix scope (a Critical bug in a Trivial-tier fix-area is still Critical for review purposes). Trust boundaries affected = where the bug crosses them. |
| 3. Plan with Governance | **Hypothesize** | Form testable hypotheses for root cause. The "governance plan" becomes the hypothesis list with test plans for each. Skills activate against the *suspected fix area*, not the bug itself; security skills especially help spot hypotheses missed by the original implementer. |
| 4. Implement | **Test** | Test hypotheses systematically (the Agans methodology / Five Whys patterns referenced in `CLAUDE.md` §3's debugging callout). Each hypothesis test is a focused intervention; outputs are the test result + updated hypothesis state. AI-generated test code gets flagged for Verifier same as in building. |
| 5. Four-Pass Review | **Root-Cause** | Review applies to the *fix*, not to the bug. The fix is treated as new code: Code Reviewer for craftsmanship, Security Auditor for security regressions the fix might introduce, Red Team for adversarial scenarios the fix might miss, Holistic Reviewer for regression risk (the central concern for fixes). Verifier dispatches when the fix uses AI-generated code. |
| 6. Commit | **Verify-Fix** | Commit + verify the fix actually fixes the bug (not just "all tests pass" — exercise the original reproduction path from the Reproduce stage). Log the bug to `ERROR-LOG.md` as Resolved with the fix commit referenced. Session log captures the debugging trail (hypotheses tried + ruled out) since this is often the most valuable context for future similar bugs. |

### Termination criteria for debugging

The workflow terminates when:

- **Fixed:** the fix exercises cleanly against the Reproduce-stage repro path; `ERROR-LOG.md` updated to Resolved; commit landed.
- **Worked around, not fixed:** root cause not isolated but symptoms mitigated. Log as Resolved-with-workaround in `ERROR-LOG.md` with the underlying open question; create a new entry to track the actual root cause.
- **Cannot reproduce:** explicit determination after thorough Reproduce-stage work. Log to `ERROR-LOG.md` as Cannot-Reproduce with the conditions tried; surfaces for future re-investigation if symptoms recur.
- **Not actually a bug:** Hypothesize stage surfaces that the reported behavior is intentional or correct. Update `ERROR-LOG.md` to Not-A-Bug with the reasoning; document the surprise in `DECISIONS.md` if the reporter's expectation indicates a UX or documentation gap worth addressing.

### When debugging dispatches subagents

Subagent dispatch differs subtly from building:

- **Researcher** dispatched in Reproduce for Large-tier bugs (multi-aspect investigation: log analysis, codepath tracing, environment differences). Often parallel: one Researcher per suspected subsystem.
- **Implementer** rarely dispatched (fixes are usually focused, not decomposable). Dispatched only for Large-tier fixes that span multiple subsystems.
- **Verifier** always dispatched when the fix includes AI-suggested code, regardless of tier — debugging is exactly where AI's plausible-but-wrong patterns cause regression. Verifier exercises both the original repro (does the fix work?) and adjacent edge cases (does the fix introduce new bugs?).

---

## §8 Worked Examples

Three end-to-end traces exercising the spec. Each example shows: stages run/skipped, skill activations, subagent dispatches (with input/output sketches), hook fires (with stdin/stdout sketches), artifact updates, total findings.

### Example 1 — Trivial: typo fix in `CLAUDE.md`

**Change:** `recieve` → `receive` on one line. **Mode:** building. **Tier:** Trivial (typo per `CLAUDE.md` §3 rubric).

**Stage 1 (Research):** SKIPPED — Trivial tier has no codebase context to gather.

**Stage 2 (Scope):** orchestrator notes `CLAUDE.md` is the only file affected, no trust boundaries, no `ROADMAP.md` milestone. Writes `change_tier: "trivial"` to `.tgf/state/sessions/{session_id}.json`.

**Stage 3 (Plan with Governance):** SKIPPED per Trivial tier (no skill evaluation needed for typo fix).

**Stage 4 (Implement):** orchestrator does the `Edit` inline. `PreToolUse` fires for the `Edit` call; universal hooks check (no dangerous-git, no secrets, no destructive-db pattern) → `permissionDecision: "allow"`. `PostToolUse` fires; framework integrity hook detects `CLAUDE.md` modification and emits a `systemMessage` flagging the change for user awareness (per §6 `FileChanged` semantics, since `CLAUDE.md` is a framework integrity file).

**Stage 5 (Four-Pass Review):** orchestrator inline code review only (no subagents per §5 tier scaling). Confirms one-character change in a comment-equivalent context; no quality concerns.

**Stage 6 (Commit):** commit message `Fix typo in CLAUDE.md §4`. No session log entry required at Trivial (per §5 logging row), no `ROADMAP.md` delta.

**Artifacts updated:** `CLAUDE.md` only. **Subagents dispatched:** 0. **Hooks fired:** 3 (`PreToolUse`, `PostToolUse` × 1 each for the Edit; `PreToolUse` for the commit). **Findings:** 0. **Total workflow cost:** seconds of orchestrator time, ~0 subagent tokens.

### Example 2 — Medium: authentication middleware refactor (Next.js project)

**Change:** refactor `middleware/auth.ts` to centralize session validation; touches `middleware/auth.ts`, `lib/session.ts`, `tests/auth.test.ts`. **Mode:** building. **Tier:** Medium (multi-file, no architectural change, crosses no new trust boundaries).

**Stage 1 (Research):** orchestrator reads the three target files, greps for callers (`app/api/**/*.ts`), checks `DECISIONS.md` for prior auth decisions (finds `DEC-2025-XX-008` mandating JWT not session cookies), checks `ERROR-LOG.md` for related items (one entry: F-031 "intermittent session expiry race condition"), checks `ROADMAP.md` (milestone "authentication hardening" in progress). No Researcher subagent dispatched (Medium tier inline).

**Stage 2 (Scope):** files in scope confirmed; trust boundary affected = browser↔server session boundary; `change_tier: "medium"` written to state file; out-of-scope: the JWT signing-key rotation (separate ticket).

**Stage 3 (Plan with Governance):** skills evaluated. Path matches activate `security-iam-sessions`, `security-iam-authentication`, `security-cryptography`, `code-quality`, `testing`, `continuity`. Import matches add `security-input-validation` (middleware processes request data). Plan: apply rules from those 7 skills; anti-patterns to avoid include "session ID compared with `==`" (constant-time comparison required, OWASP ASVS V3.4.1); test requirements include race-condition coverage (per F-031).

**Stage 4 (Implement):** orchestrator writes the refactor (Medium tier inline, no Implementer subagent). 47 lines changed across 2 files; 3 tests added. AI-generated portions: lines 23–41 of `lib/session.ts` flagged for Verifier.

**Stage 5 (Four-Pass Review):** 4 review subagents dispatch in parallel per Medium tier. Plus Verifier (since `ai_generated_portions` non-empty).
- **Code Reviewer:** `review_pass.spec_compliance.matches = true`; `review_pass.quality.passes = false`; 1 Medium finding (error swallows `Error.cause`).
- **Security Auditor:** 1 High finding (session ID `==` comparison vs constant-time; OWASP ASVS V3.4.1).
- **Red Team:** 1 High finding (race condition on renewal — the F-031 surface area; reproduces it concretely).
- **Holistic Reviewer:** 1 Medium finding (JWT verification approach worth documenting in DECISIONS.md as DEC follow-up).
- **Verifier:** 1 Critical finding (AI assumed `jose.decodeJwt()` validates issuer claim; it does not — hallucinated library behavior pattern).
- Orchestrator aggregates: 5 findings (1 Critical, 2 High, 2 Medium); deduplication didn't reduce count (each finding distinct).

User fixes all 4 blocking findings (Critical + High); accepts the Medium DEC-doc finding as a separate ticket logged to `ERROR-LOG.md`. Loop back through Stage 4 for fixes; Stage 5 re-runs with reduced subagent set (just Verifier on the fix region).

**Stage 6 (Commit):** commit message captures the refactor + 4 finding fixes. Session log entry generated. `ROADMAP.md` updated (authentication hardening milestone advanced). `ERROR-LOG.md` updated (F-031 resolved; new entry F-034 for the DEC documentation TODO). Pre-commit hook verifies tests pass.

**Artifacts updated:** 2 code files, 3 test files, `ROADMAP.md`, `ERROR-LOG.md`, session log. **Subagents dispatched:** 5 (4 reviewers + Verifier; then 1 Verifier for the fix iteration). **Hooks fired:** ~20 across the session (PreToolUse for each Bash/Write/Edit, SubagentStart/Stop pairs, PostToolUse for telemetry, PreToolUse for git commit, SessionEnd). **Findings:** 5 total, 4 blocking, all resolved.

### Example 3 — Large: new billing feature crossing trust boundaries

**Change:** add Stripe billing integration to a SaaS — new endpoints, PII handling, payment data flow, Stripe webhook receiver. Touches `app/api/billing/*.ts`, `lib/stripe.ts`, `lib/billing.ts`, new database tables, webhook handler `app/api/webhooks/stripe/route.ts`, env var additions. **Mode:** building (transitioning to hardening for the billing surface area). **Tier:** Large (new feature, crosses new trust boundary at the webhook receiver, introduces PII storage, introduces payment data flow).

**Stage 1 (Research):** orchestrator dispatches 3 Researcher subagents in parallel.
- *Researcher A* (codebase patterns): identifies existing API route patterns, database access patterns, current secret management.
- *Researcher B* (prior decisions): finds `DEC-2025-XX-014` (chose Stripe over alternative payment processors), confirms no prior billing decisions to constrain.
- *Researcher C* (related logs): no `ERROR-LOG.md` entries for billing; one `WAIVER-LOG.md` entry on webhook signature verification deferred for a different webhook integration; one `VENDOR-LOG.md` entry on Stripe dashboard configuration that's pending.

Aggregated `research_findings`: 12 relevant files, 1 prior decision, 1 relevant waiver, 1 pending vendor action, ROADMAP milestone "billing MVP" advanced.

**Stage 2 (Scope):** files in scope identified; trust boundaries affected = (1) browser↔server for billing UI, (2) server↔Stripe API for charges, (3) Stripe↔server for webhooks (NEW trust boundary). `change_tier: "large"` written; out-of-scope: refund flow (later milestone), subscription management UI (later milestone).

**Stage 3 (Plan with Governance):** full skill evaluation. Skills that activate include `security-iam-authentication`, `security-iam-authorization`, `security-input-validation`, `security-output-encoding`, `security-webhooks`, `security-secrets-management`, `security-api`, `security-cryptography`, `security-data-classification` (PII!), `security-privacy-data-handling`, `compliance-foundations`, `compliance-pci-dss` (payment data!), `data-architecture` (new tables), `security-database`, `security-error-handling`, `security-logging`, `code-quality`, `testing`, `continuity`. Compliance-pci-dss surfaces PCI-DSS scope question — confirmed via PROJECT-CONTEXT that the project uses Stripe.js for card data (no card data touches the server), reducing PCI-DSS scope to SAQ-A. Governance plan includes ~40 rules across the activated skills.

**Stage 4 (Implement):** orchestrator decomposes into 4 parallel Implementer tasks: (1) database tables + migrations, (2) Stripe client wrapper + tests, (3) billing API endpoints, (4) webhook receiver + signature verification. Each Implementer gets disjoint file scope and the relevant slice of `governance_plan`. ~580 lines added across 11 files; 24 tests; multiple AI-generated portions flagged for Verifier.

**Stage 5 (Four-Pass Review):** all 4 review subagents + Verifier dispatch.
- **Code Reviewer:** 2 Medium findings (naming inconsistency between client/wrapper, missing JSDoc on public exports).
- **Security Auditor:** 1 Critical (webhook signature verification accepts unsigned requests if header missing — auth bypass!), 2 High (PII logged in error path, secret in env var named without TGF convention), 3 Medium (input validation gaps on optional fields).
- **Red Team:** 1 Critical confirming the Security Auditor's webhook finding from an exploitation angle (forging webhook events), 1 High (race condition on subscription state during simultaneous webhooks).
- **Holistic Reviewer:** 1 High (new PII storage not documented in `SCHEMA-HISTORY.md`; data classification entry needed), 2 Medium (multiple architectural decisions made in implementation without DECISIONS.md entries).
- **Verifier:** 1 Critical (Stripe.js client-side tokenization assumed but not actually integrated in the UI; AI hallucinated the integration point), 2 Medium (edge cases in subscription cancellation untested).

Orchestrator aggregates: 14 findings (3 Critical, 4 High, 7 Medium); deduplication merges the webhook signature finding (caught by both Security Auditor and Red Team) → 13 findings. User addresses 3 Critical + 4 High (all 7 blocking); fixes loop back through Stage 4. Stage 5 re-runs with reduced subagent set (Security Auditor + Verifier on the fix regions). 1 Medium accepted as out-of-scope and logged to `WAIVER-LOG.md` with 30-day revisit date.

**Stage 6 (Commit):** the work decomposes into 3 commits (decomposed implementation produces multiple commit-able chunks). Per CLAUDE.md Git Safety Protocol, each commit is a NEW commit. Final commits land. `DECISIONS.md` gets 2 new entries (webhook signature verification approach; PII data classification decision). `SCHEMA-HISTORY.md` gets entry for new tables. `ROADMAP.md` updated (billing MVP advanced; new milestone added for subscription management). `VENDOR-LOG.md` updated (Stripe dashboard webhook endpoint registration still pending). `WAIVER-LOG.md` gets the 1 deferred Medium finding. Session log entry generated capturing the full Large-tier flow.

**Artifacts updated:** 11 code files, 24 test files, 1 migration, `ROADMAP.md`, `DECISIONS.md`, `SCHEMA-HISTORY.md`, `VENDOR-LOG.md`, `WAIVER-LOG.md`, `ERROR-LOG.md`, session log, `.env.example`. **Subagents dispatched:** 12+ (3 Researchers + 4 Implementers + 5 review subagents + reduced reviewer set on fix iterations). **Hooks fired:** ~100 across the session (every tool call, every subagent lifecycle, framework integrity checks on DECISIONS.md and SCHEMA-HISTORY.md modifications, multiple commits). **Findings:** 13 unique findings (3 Critical, 4 High, 6 Medium after dedup), 7 blocking, all resolved (6 fixed + 1 waived).

---

## §9 Reference

**Primary specifications:**

- `CLAUDE.md` §3 — operational workflow contract (the *what*); this document specifies the *how*
- `docs/ARCHITECTURE.md` §15 — mode-aware operation (§5 of this doc operationalizes)
- `docs/ARCHITECTURE.md` §18 — hook architecture (§6 of this doc operationalizes; richer output schema discovered in Phase 3 research documented in §6)
- `docs/ARCHITECTURE.md` §19 — token efficiency and cost-aware orchestration (§5 of this doc tier scaling derives from)
- `docs/ARCHITECTURE.md` §20 — agent orchestration role descriptions (§4 of this doc specifies the output contracts those roles produce)

**Architectural decisions operationalized:**

- `DECISIONS.md` `DEC-2026-05-17-003` Clause 2 — hook architecture (TGF context-injection portion superseded by DEC-006)
- `DECISIONS.md` `DEC-2026-05-17-003` Clause 3 — seven subagent roles (output schemas defined in §4 of this doc)
- `DECISIONS.md` `DEC-2026-05-17-005` — hook event taxonomy (PascalCase names matching Claude Code's actual events; §6 of this doc uses these)
- `DECISIONS.md` `DEC-2026-05-19-006` — TGF session state architecture (§6 of this doc uses `.tgf/state/sessions/{session_id}.json` per this ADR; Phase 3 Step 1 verification confirmed)

**External authoritative sources** (verified per `DEC-2026-05-17-004` Clause 1):

- Claude Code Hooks reference (current 2026) — verified Phase 2 (commit `92c9894`) and re-verified Phase 3 Step 1 (2026-05-19, surfaced richer `hookSpecificOutput` schema documented in §6)
- OWASP Top 10 for LLM Applications 2025 — `LLM01:2025` (prompt injection, applies to hook input untrusted-data discipline in §6), `LLM06:2025` (excessive agency, applies to subagent role scoping in §4)
- MITRE ATLAS v5.4.0 (February 2026) — agent-targeting techniques inform subagent telemetry hooks in §6
- NIST SP 800-218 v1.1 (SSDF) — two-layer verification discipline frames §6 hooks as the enforcement floor

**Comparative reference** (per `DEC-2026-05-17-004` Clause 6 — informs design pattern, not rule-source):

- Superpowers framework — two-stage spec-then-quality review pattern in §4 (every review subagent's `review_pass` object reflects this pattern)

**Generated during Phase 3:**

- `docs/phase-3-plan.md` — Phase 3 implementation plan with Checkpoint 1 decisions A–E resolved (committed for transparency per Phase 2 Decision 2)

---

*Phase 3 complete with this commit (2 of 2 per Checkpoint 1 Decision E). Phases 4–12 build against the specifications in §3–§8.*

---

## §10 Methodology Cross-Reference

Single-table summary of which authoritative methodology grounds which workflow stage, with the corresponding source IDs in `.tgf/state/source-registry.json` for traceability.

| Stage | Authoritative methodology | Source IDs |
|-------|---------------------------|------------|
| Stage 1 (Research) | TGF source-tier hierarchy (§2 above); engineering FMEA-style assumption-checking; NIST SP 800-39 intelligence-level distinction | `NIST-SP-800-39` |
| Stage 2 (Scope) | NIST SP 800-37 Rev 2 Categorize step; NIST SP 800-160 Vol 1 Rev 1 system scoping; Microsoft SDL threat-modeling scope; STRIDE-per-element at trust boundaries | `NIST-SP-800-37`, `NIST-SP-800-160-V1`, `MS-SDL` |
| Stage 3 (Plan with Governance) | NIST SP 800-53 Rev 5.2.0 (backbone); NIST CSF 2.0 (cross-cutting); CIS Controls v8.1 (prioritized overlay); ISO/IEC 27002:2022 (international, via the CSF Informative References crosswalk) | `NIST-SP-800-53`, `NIST-CSF-2-0`, `NIST-CSF-2-0-IR`, `CIS-CONTROLS-V8-1` |
| Stage 4 (Implement) | No new methodology; the citation chain from Stage 3 travels with the implementation | — |
| Stage 5 (Four-Pass Review) | Subagent personas reference domain-appropriate authoritative materials (see `docs/four-agents-design-notes.md`) | — |
| Stage 6 (Commit) | No new methodology; commit and log discipline per `CLAUDE.md` §11 + §13 | — |

**Source-org independence** (M12 per `docs/RESEARCH-SECURITY.md` §4.3) for the WORKFLOW-V2 methodology backbone:

- NIST sources cluster as a single publishing organization. Two NIST documents do not satisfy M5 multi-source corroboration on their own.
- ISO/IEC 27002 (via the CSF IR crosswalk) and CIS Controls bring different publishing organizations into the chain (ISO and CIS respectively), enabling M5 / M12 independence when corroborating control-parameter values.
- Microsoft SDL is a vendor source (Tier 3, design-rationale only). Not cited in skill §2 Sources tables.

**On the OWASP ASVS → 800-53 bridge.** OWASP publishes ASVS-to-NIST mappings only at the NIST SP 800-63B (Authentication) level in the ASVS repo's `5.0/mappings/` folder, not at the broader NIST SP 800-53 control catalog level. The TGF citation chain bridges ASVS through CSF 2.0 Subcategories (TGF-synthesized mapping per rule) and then through to 800-53 / ISO 27002 / CIS via the NIST CSF Informative References crosswalk, which IS canonical. Direct ASVS → 800-53 mappings outside the IAM/authentication domain are TGF synthesis honestly flagged at rule-level.
