# Framework Hardening Plan

> **Status:** v1 master plan — written 2026-05-22, locked at checkpoint same day. Orchestrates all framework-hardening work between Phase 6 commit 4/12 (security-cryptography, landed `73d025d`) and Phase 6 commit 5/12 (security-secrets-management, deferred).
>
> **Scope:** this is a *master plan* that sequences five workstreams. Only Workstream 1 (research-security infrastructure) has a detailed implementation plan in this repo (`docs/research-security-implementation-plan.md`). **Workstreams 2–5 are mentioned with goals + dependencies + rationale, but each MUST have its own full TGF workflow — plan → Checkpoint 1 approval → implement → four-pass review → commit — when it begins.** This plan does not substitute for per-workstream planning.

---

## §1 Context and Motivation

### §1.1 What happened

On 2026-05-22, Phase 6 commit 4/12 (`security-cryptography`) was landed as `b67765e`. Initial draft listed three OWASP Cheat Sheets in §2 Sources marked "verified by reference" without live fetch. User caught this as a framework-premise violation: `CLAUDE.md` §1 ("Authoritative sources only") states every governance rule traces to a verifiable authoritative source. "Verified by reference" without an actual fetch relies on AI training-data memory — exactly the failure mode the principle is designed to prevent.

Commit was amended to `73d025d`: the unverified cheat sheets were either live-fetched (Password Storage — all parameters verified accurate) or removed from §2 Sources (Key Management and TLS — not actually cited at rule level). One small editorial in AP-5 corrected.

### §1.2 What the retrospective surfaced

Beyond the immediate fix, the incident revealed structural framework gaps:

**Workflow stages are under-standardized.** Stage 1 (Research), Stage 2 (Scope), Stage 3 (Plan with Governance) have principles but no authoritative-source-backed checklist. The fix is grounding each in established methodology (Admiralty Code / NIST RMF / NIST 800-53).

**The four review agents are scaffolded but not embodied.** Per Phase 4 commit `d4abbb0`, `agents/code-reviewer.md`, `security-auditor.md`, `red-team.md`, `holistic-reviewer.md` exist as scaffolds without rich personas or preloaded authoritative materials. When the orchestrator plays all four roles, self-review blind spots survive into review — which is exactly what happened on commit 4/12 (the holistic-review pass should have caught the §2 Sources discipline violation but didn't, because the orchestrator wrote it AND reviewed it).

**The bootstrap problem.** The framework's design (per `docs/ARCHITECTURE.md` §20 + `CLAUDE.md` §6) assumes separate subagents do the four-pass review. Those subagents are Phase 11–12 work. In the building phase (Phases 1–10), the orchestrator does all four passes — preserving its own blind spots. The framework is being built with a process that doesn't yet fully embody the framework.

**The deepest gap: AI memory ≠ verification.** When AI training-data memory matches a fetched source, those are not independent observations — they may share a common upstream (the document being fetched is often the same document the AI was trained on). An attacker who can influence either can engineer the confirmation. The commit-4/12 incident was an accidental low-grade version of this attack pattern (later encoded as M9 in research-security).

### §1.3 The decision

Address the structural gaps before continuing Phase 6. Five workstreams in dependency order. Phase 6 commits 5/12–12/12 resume after the hardening completes, under the new discipline.

---

## §2 Scope and Boundaries

**What this plan covers:**
- The sequence of five workstreams between commit 4/12 and Phase 6 resume
- High-level goals + dependencies + artifacts per workstream
- The rationale for sequencing (why Workstream 1 must precede 2–4)
- Existing artifacts produced during the design conversation
- Cross-references to detailed planning documents (Workstream 1 has its own implementation plan; Workstreams 2–5 do not yet)

**What this plan does not cover:**
- Detailed implementation specs for Workstreams 2–5 (each gets its own plan when it begins)
- The Phase 6 build resumption details (covered by `docs/phase-6-plan.md`)
- The framework's overall architecture (covered by `docs/ARCHITECTURE.md`)
- Per-skill plans (covered by per-phase plans)

**Boundary discipline:** when Workstream 2 (WORKFLOW-V2) begins, the first step is its own plan document, its own Checkpoint 1 approval cycle, its own four-pass review, its own commit. This master plan does not pre-commit those workstreams to specific implementations.

---

## §3 The Five Workstreams

Sequenced in dependency order. Each subsection: Goal → Key Artifacts → Authoritative References → Dependencies → What It Unlocks → Effort Estimate → Workflow Note.

### §3.1 Workstream 1 — Research-Security Infrastructure

**Status:** ⏳ NEXT. Ready to start (plan approved at checkpoint 2026-05-22).

**Goal:** operationalize M1–M19 (per `docs/RESEARCH-SECURITY.md`) as Claude Code hooks + state infrastructure + Python helpers + settings.json wiring. Make the research-stage security discipline implicit (mechanical, external, unbypassable) rather than principles-only.

**Key artifacts to produce:**
- `.claude/hooks/` — 5 hook scripts (research-pretool-webfetch, research-posttool-webfetch, research-pretool-write, research-stop, research-session-start)
- `.claude/hooks/lib/` — 7 Python M-helpers (m3_schema, m4_pattern, m11_drift, m13_hash, m14_unicode, m18_exception, m19_html_hidden) + 4 support libraries (citation_parser, research_log, source_registry, common)
- `.tgf/state/` — directory structure with source-registry, source-hashes, source-org-mapping, source-baselines/, source-schemas/, citation-indexes/, research-logs/, parameter-history, m8-approvals/, hook-overrides/, baseline-updates
- `.claude/settings.json` — hook registration (preserve existing `.claude/settings.local.json`)
- `.claude/git-hooks/pre-commit-research-security.sh` — defense-in-depth pre-commit
- `tests/research-security-smoke-test.sh` — 12 smoke tests (T1–T12) attempting to slip past each M
- `docs/RESEARCH-SECURITY.md` — refined post-build with implementation specifics
- Combined commit landing all of the above as a single unit

**Authoritative references:**
- `docs/RESEARCH-SECURITY.md` (v1 design)
- `docs/research-security-implementation-plan.md` (v1 implementation plan — Step 1–20 build sequence in §10)
- Claude Code Hooks Reference + Hooks Guide + Settings docs (verified 2026-05-22 via claude-code-guide agent)
- NIST AI 100-2 E2023 (Adversarial ML taxonomy)
- OWASP LLM Top 10:2025 LLM01 (Prompt Injection)
- MITRE ATLAS AML.T0051 series
- Greshake et al. 2023 (Indirect Prompt Injection paper)
- NATO STANAG 2022 Admiralty Code
- CIA *A Tradecraft Primer* (declassified 2009)
- RFC 8446 (TLS 1.3), RFC 9364 (DNSSEC)

**Dependencies:** none external. Plan already approved at checkpoint 2026-05-22. Two design docs (`RESEARCH-SECURITY.md` + `research-security-implementation-plan.md`) on disk, awaiting commit-with-hooks as single unit.

**What it unlocks:** Workstreams 2–5 all involve authoritative-source research that should be protected by M1–M19 from the moment of operation. Without Workstream 1 operational, subsequent research carries the same risk that produced the commit-4/12 incident.

**Effort estimate:** 6–10 hours of focused build work across one long session or 2–3 shorter sessions. 20-step build sequence detailed in `docs/research-security-implementation-plan.md` §10.

**Workflow note:** plan exists; Checkpoint 1 cleared 2026-05-22; ready for Stage 4 (Implement). Stages 5 (Review) + 6 (Commit) follow normally. NOTE: this workstream's build IS the framework that will protect subsequent workstreams — it operates under principles-only discipline during construction (acceptable per the bootstrap problem; the alternative is infinite regress).

### §3.2 Workstream 2 — WORKFLOW-V2 Standardization

**Status:** Deferred until Workstream 1 operational. Will have its own full TGF workflow when it begins.

**Goal:** standardize Stage 1 (Research) / Stage 2 (Scope) / Stage 3 (Plan with Governance) against authoritative-source-backed methodology. Replace principles-only discipline with framework-citation-backed checklists.

**📄 Detailed design content captured separately:** `docs/workflow-v2-design-notes.md` — preserves the structured approach for each stage developed during the design conversation, including: source-tier hierarchy (Tier 1/2/3 with concrete criteria), per-stage methodology integration (Admiralty Code at Stage 1; NIST 800-37 RMF Categorize at Stage 2; NIST 800-53 backbone at Stage 3), per-stage draft checklists, the citation chain (rule → ASVS → 800-53 → CSF function) for federal-grade traceability, integration points with research-security hooks and the four agents, and open questions for the Workstream 2 plan to resolve.

**Key artifacts to produce (estimated; subject to that workstream's own plan):**
- `docs/WORKFLOW-V2.md` or amendment to `docs/WORKFLOW.md` with per-stage framework citations and checklists
- The citation chain (rule → ASVS → NIST 800-53 → NIST CSF 2.0 function) implementable in Phase 6+ skills
- Per-stage hook scripts for stage-gate enforcement (Stage 1 → 2 gate, Stage 3 → 4 gate, Stage 5 → 6 gate)
- Possibly stage-gate hook scripts beyond what research-security infrastructure (Workstream 1) provides

**Authoritative references (full details in design-notes; summary here):**
- **Stage 1**: NATO STANAG 2022 Admiralty Code (source reliability × information credibility A1–F6); CIA *A Tradecraft Primer* — Structured Analytic Techniques (Key Assumptions Check, Quality of Information Check, ACH); NIST SP 800-39 (threat-intelligence sourcing); OSINT corroboration principles
- **Stage 2**: NIST SP 800-37 Rev 2 (RMF Categorize step — system description, information types, impact levels, system boundary); NIST SP 800-160 Vol 1 Rev 1 (Systems Security Engineering); Microsoft SDL (threat-modeling scope); ISO/IEC/IEEE 15288:2023; STRIDE-per-element for threat-boundary assessment integrated at scope
- **Stage 3**: NIST SP 800-53 Rev 5 (control catalog — structural backbone with 20 control families); NIST CSF 2.0 2024 (Identify / Protect / Detect / Respond / Recover / Govern — cross-cutting check); CIS Controls v8.1 (top-18 prioritized); ISO/IEC 27002:2022 (international code of practice)

**Dependencies:** Workstream 1 must be operational so the WORKFLOW-V2 research can happen under M1–M19 protection. The framework citations involve substantial fetching of NIST/ISO/CIS materials.

**What it unlocks:** Workstreams 3 (four agents) and 4 (audit) both depend on having a standardized workflow to apply. The four agents' personas reference the workflow stages; the audit measures past commits against the workflow's quality bar.

**Effort estimate (rough, subject to revision):** 1–3 sessions of plan + research + write + review.

**Workflow note:** **MUST have its own full TGF workflow** when it begins — its own `docs/workstream-2-plan.md`, Checkpoint 1, Stage 1 research with the new research-security infrastructure protecting it, Stage 3 plan with governance against NIST/ISO/CIS controls, four-pass review (where the four agents might still be orchestrator-played, but Workstream 1 hooks catch §2 Sources discipline mechanically). The design-notes document is starting input; the Workstream 2 plan will refine.

### §3.3 Workstream 3 — Four Review Agents

**Status:** Deferred until Workstreams 1 + 2 operational. Will have its own full TGF workflow when it begins.

**Goal:** flesh out the four review agents from scaffolds (Phase 4 commit `d4abbb0`) to operational subagents with rich personas + skill preloading + authoritative-materials citations. Address the bootstrap problem (orchestrator playing all four roles) by establishing separate-agent review for high-stakes changes.

**📄 Detailed design content captured separately:** `docs/four-agents-design-notes.md` — preserves the full persona definitions developed during the design conversation, including: voice/instincts/mindset per agent, severity gradient (for security-auditor), boundary discipline (for red-team — "references adversary behavior as documented by defenders; does not generate offensive tooling"), conceptual integrity framing (for holistic-reviewer — Brooks's "does this change fit the system's existing way of thinking"), complete authoritative materials lists, skills preloaded, activation criteria, change-tier and mode scaling, future-proofing (quarterly refresh discipline).

**Key artifacts to produce (estimated):**
- `agents/code-reviewer.md` — senior software engineer persona (20+ years across language families and lifecycles); detail-oriented, calls out standard violations even when code works, reads code skeptically. Preloads `skills/code-quality/` + `skills/testing/` + `skills/continuity/`.
- `agents/security-auditor.md` — national-security-grade infosec professional persona (incident responder + network security engineer + control assessor background); speaks NIST RMF/CSF/ISO 27001 fluently; risk-managed rather than purely paranoid; mindset: "if this fails, I'm the one writing the postmortem to the regulators." Severity gradient per `CLAUDE.md` §5. Preloads `skills/security-core/` and Phase 6–8 security skills.
- `agents/red-team.md` — penetration tester / threat researcher persona across full attacker spectrum (script-kiddie → hacktivist → financially-motivated → APT); studies real adversary behavior via public attribution (Mandiant M-Trends, CrowdStrike, Microsoft TI, Google TAG, CISA advisories). **Boundary discipline: references adversary behavior as documented by defenders at technique-ID level (MITRE ATT&CK T-numbers, ATT&CK Groups at G-number profiles); does not generate offensive tooling, exploit code, or operational guidance for attacking real systems.** Preloads `skills/security-core/` and Phase 6–8 security skills.
- `agents/holistic-reviewer.md` — principal engineer / systems-thinker persona (15+ years across multiple system lifecycles); cares about conceptual integrity in Brooks's sense ("does this change fit the system's existing way of thinking, or introduce a foreign concept future maintainers will navigate around"); thinks in second-order effects ("if we do this, what becomes hard six months from now?"); the synthesizer of what the focused three miss because their lenses are local. Preloads `skills/continuity/` + `skills/code-quality/` + applicable activity skills.

**Authoritative references summary (full details in design-notes):**
- **Code Reviewer:** McConnell *Code Complete*; Fowler *Refactoring*; Feathers *Legacy Code*; Hunt & Thomas *Pragmatic Programmer*; Ousterhout *Philosophy of Software Design*; Google Engineering Practices; ISO/IEC 25010:2023; language-specific style guides (PEP 8, *Effective Java*, etc.)
- **Security Auditor:** NIST SP 800-53/CSF 2.0/30/37/61/AI 100-1; ISO 27001/27002/27005; OWASP ASVS/Top 10/API/LLM/Mobile/Smart Contract Top 10/SCSVS/WSTG/MASVS; CIS Controls v8.1 + Benchmarks; MITRE ATT&CK + D3FEND + CWE/SANS Top 25; PCI-DSS v4.0/HIPAA/GDPR/CCPA; FedRAMP/DoD STIGs/CISA CPGs; wallet-crypto (NIST IR 8408, Trail of Bits, ConsenSys)
- **Red Team:** MITRE ATT&CK (Enterprise, Mobile, ICS, Containers) + ATT&CK Groups; MITRE ATLAS; MITRE Engenuity; OWASP WSTG v4.2 + API/Mobile testing guides; PTES; OSSTMM 3; NIST SP 800-115; Lockheed Cyber Kill Chain; Diamond Model; public threat intel (Mandiant, CrowdStrike, MS TI, Google TAG, CISA AA)
- **Holistic Reviewer:** Brooks *Mythical Man-Month* (conceptual integrity); Ousterhout *Philosophy*; Alexander *Pattern Language*; Ford/Parsons/Kua *Building Evolutionary Architectures*; Evans *DDD*; Kleppmann *DDIA*; Meadows *Thinking in Systems*; Google SRE book; Forsgren/Humble/Kim *Accelerate*; Nygard *Release It!*; NIST SP 800-160 Vol 1 Rev 1; ISO/IEC/IEEE 42010:2022; TOGAF 10 (selective)

**Dependencies:** Workstreams 1 + 2. The agents need WORKFLOW-V2's standardized stages as their operating environment; they need research-security hooks to protect the substantial research required to write their personas (the materials lists involve fetching NIST/ISO/MITRE/OWASP/IETF content).

**What it unlocks:** Workstream 4 (audit) can use the agents for higher-quality review than orchestrator self-review. The full four-pass review per `CLAUDE.md` §3 becomes operationally real.

**Effort estimate (rough):** 2–4 sessions. Each agent is substantial work — researching the materials list, writing the persona, integrating with `skills:` frontmatter preloading.

**Workflow note:** **MUST have its own full TGF workflow.** Likely four sub-workstreams or one combined plan with per-agent sections. Either way: own plan document, own Checkpoint 1, own implementation, own four-pass review (where the agents might be partially playing their own roles by the end — meta). The design-notes document is starting input; the Workstream 3 plan will refine.

### §3.4 Workstream 4 — Audit of Existing Work

**Status:** Deferred until Workstreams 1 + 2 + 3 operational. Will have its own full TGF workflow when it begins.

**Goal:** apply the new discipline (research-security infrastructure + WORKFLOW-V2 standards + four review agents) to all framework work landed before the discipline was operational. Identify gaps; produce remediation list.

**Targets of audit:**
- Phase 4 commits — `skills/code-quality/`, `skills/security-core/`, `skills/continuity/` (always-on skills)
- Phase 4 agent scaffolds — `agents/` files (will be replaced by Workstream 3 deliverables; audit identifies any unique scaffold content worth preserving)
- Phase 5 commits — `skills/discovery/`, `skills/project-management/`, `skills/design/`, `skills/ui-craft/`, `skills/testing/`, `skills/debugging/`, `skills/disagreement/` (activity skills)
- Phase 6 commits 1/12–4/12 — `skills/security-input-validation/`, `skills/security-output-encoding/`, `skills/security-error-handling/`, `skills/security-cryptography/`
- Foundational docs — `CLAUDE.md`, `docs/ARCHITECTURE.md`, `docs/WORKFLOW.md` (if amended by Workstream 2), `docs/DECISIONS.md`

**Audit checks per artifact:**
- §2 Sources traceability — every entry traces to a (now retroactively verifiable) Stage 1 research record
- §2 Sources ↔ rule-level citation — every §2 entry is actually cited at rule/AP level; remove "see also" listings (the rule that emerged from commit 4/12)
- M1–M19 retroactive compliance — would these artifacts pass the new hook checks if re-evaluated? Specifically: M9 memory-confirmation gap (any citation that depended on memory matching the source?); M14 Unicode normalization on identifiers; M18 exception-clause detection
- Workflow stage compliance (per WORKFLOW-V2) — does the artifact reflect the standardized stages?
- Code-reviewer findings — apply Workstream 3's code-reviewer agent to skill content
- Security-auditor findings — apply Workstream 3's security-auditor agent
- Red-team findings — apply Workstream 3's red-team agent (looking for M1–M19 evasions in shipped content)
- Holistic-reviewer findings — apply Workstream 3's holistic-reviewer agent (looking for systemic patterns, conceptual-integrity issues)

**Dependencies:** Workstreams 1 (hooks) + 2 (WORKFLOW-V2 standards to audit against) + 3 (agents to perform the audit).

**What it unlocks:** clean baseline for Phase 6 commit 5/12 resumption. Anything remediated leaves the codebase in a known-good state under the new discipline.

**Effort estimate (rough):** 1–2 sessions for audit itself + 1–3 sessions for remediation (Workstream 5).

**Workflow note:** **MUST have its own full TGF workflow.** Audit is itself a substantial change-context — running four-agent review over ~15+ existing artifacts, generating findings list, prioritizing. Its plan document captures audit scope and methodology.

### §3.5 Workstream 5 — Remediation

**Status:** Deferred until Workstream 4 (audit) produces findings. Will have its own full TGF workflow when it begins.

**Goal:** address findings from the audit. Update existing artifacts to meet new discipline.

**Key artifacts to produce:**
- Per-skill remediation commits — likely amend (where appropriate) or follow-on commits to bring existing skills under new discipline
- Updated session logs documenting the remediation
- ROADMAP.md update if any milestones shift
- CHANGELOG.md entries for material discipline changes
- Possibly DECISIONS.md ADRs if any architectural decisions emerge from remediation

**Dependencies:** Workstream 4 (audit findings).

**What it unlocks:** Phase 6 commit 5/12 resumption with clean baseline.

**Effort estimate (rough):** highly variable based on audit findings. Could be 1 session (minor cleanup) or 5+ sessions (substantial re-fetching + re-verification + updates). Plan when the audit completes.

**Workflow note:** **MUST have its own full TGF workflow.** Each remediation change is a TGF workflow run (Stages 1–6). Per-skill remediation may be small enough to be a single commit per skill; combined plan addresses the overall scope.

---

## §4 Sequence and Dependency Rationale

### §4.1 Why this order

```
Workstream 1 (Research-Security) ─┐
                                  ├─→ Workstream 2 (WORKFLOW-V2) ─→ Workstream 3 (Four Agents)
                                  │                                          │
                                  │                                          ↓
                                  └──────────────────────────────────→ Workstream 4 (Audit)
                                                                              │
                                                                              ↓
                                                                       Workstream 5 (Remediation)
                                                                              │
                                                                              ↓
                                                                       Phase 6 commit 5/12 resume
```

**Workstream 1 first** because all subsequent work involves authoritative-source research that the M1–M19 protection should cover from the moment of operation. WORKFLOW-V2 needs to fetch NIST/ISO/CIS content; the four agents need to fetch substantial framework materials; the audit needs to re-verify existing citations. All of this should run under hook protection.

**Workstream 2 before Workstream 3** because the four agents reference the workflow's stage structure; their personas activate at specific stages.

**Workstream 3 before Workstream 4** because the audit's quality depends on having the agents available to perform it; orchestrator self-review on the audit would reproduce the same blind spot that caused the original gap.

**Workstream 4 before Workstream 5** because remediation needs findings to remediate.

**All of 1–5 before Phase 6 resume** because the new discipline should be in force for commits 5/12 onward; resuming Phase 6 before audit-and-remediation would leave inconsistent state (some commits under old discipline, some under new).

### §4.2 The bootstrap problem and how Workstream 1 resolves it (mostly)

Workstream 1's build operates under principles-only discipline because the hooks don't exist yet. This is unavoidable — the alternative is infinite regress (need hooks to build hooks). The mitigation is:

1. Workstream 1's build research is narrow — Claude Code internal documentation (Anthropic-managed; different threat profile than OWASP/NIST/MITRE)
2. Workstream 1's design (`docs/RESEARCH-SECURITY.md`) is already authored under intensive human review (this conversation produced extensive war-gaming + checkpoint approval)
3. Workstream 1's plan (`docs/research-security-implementation-plan.md`) is already authored under intensive human review
4. The build itself is mechanical — file creation + script writing — not research-heavy

After Workstream 1 lands, Workstreams 2–5 operate under hook protection. The bootstrap problem is bounded to the initial hook implementation.

### §4.3 What if the order needs to change

If during Workstream 2, gaps in Workstream 1 surface (e.g., a hook doesn't catch what it should), pause and amend Workstream 1 before continuing. Similar logic at each transition. The plan is locked at v1; revisions happen as plan amendments (per Phase 4/5 precedent — plan-adjustments captured in commit messages and session logs).

---

## §5 Artifacts Already Produced

Items already authored during the design conversation (2026-05-22 post-commit-4/12):

| Artifact | Location | Status | Notes |
|----------|----------|--------|-------|
| Research-security design | `docs/RESEARCH-SECURITY.md` | On disk, uncommitted | v1; 544 lines; 10 sections. Lands with Workstream 1 commit. |
| Research-security implementation plan | `docs/research-security-implementation-plan.md` | On disk, uncommitted | v1; 756 lines; 12 sections; build sequence in §10. Lands with Workstream 1 commit. |
| This master plan | `docs/framework-hardening-plan.md` | On disk, uncommitted | v1. Orchestration document for all five workstreams. |
| WORKFLOW-V2 design notes | `docs/workflow-v2-design-notes.md` | On disk, uncommitted | v1 design notes for Workstream 2; captures source-tier hierarchy, per-stage methodology integration (Admiralty Code / NIST 800-37 / NIST 800-53), citation chain proposal (rule → ASVS → 800-53 → CSF), draft checklists. Starting input for Workstream 2 plan; will land when Workstream 2 commits. |
| Four-agents design notes | `docs/four-agents-design-notes.md` | On disk, uncommitted | v1 design notes for Workstream 3; captures full personas (voice/instincts/mindset per agent), authoritative materials lists, boundary discipline (red-team), severity gradient (security-auditor), conceptual integrity framing (holistic-reviewer), activation criteria, future-proofing. Starting input for Workstream 3 plan; will land when Workstream 3 commits. |
| Session log addendum | `.sessions/2026-05-22-session-01-phase-6-commits-2-3-4-with-correction.md` | On disk, gitignored | Updated with full design conversation summary. |
| Memory updates | `~/.claude/projects/-home-alt313-TGF/memory/project_tgf_build_phases.md` | On disk | Pause state + M9 principle + sequencing captured. |

---

## §6 Open Decisions

Items to resolve at fresh-session restart:

1. **Where this master plan commits**:
   - (a) Standalone commit before Workstream 1 begins (clean history)
   - (b) Folded into Workstream 1's combined commit (single unit; this plan + RESEARCH-SECURITY.md + implementation plan + hooks all together)
   - (c) Standalone now but updated post-build with cross-references to the landed Workstream 1 artifacts

   *Recommendation: (a) — commit this master plan first to give fresh session a clean starting reference; Workstream 1 then proceeds and lands its own combined commit.*

2. **Whether to push the 3 unpushed commits** (`c2e4f8c`, `9940470`, `73d025d`) before starting Workstream 1, or hold and push everything together later. *Recommendation: hold for now; push when Workstream 1 lands, alongside this master plan + the design docs + hooks.*

3. **Build session length** for Workstream 1 — long single session (6–10 hours) vs split into 2–3 shorter sessions. The 20-step build sequence has natural break points at steps 6, 9, 14, 17.

4. **Smoke-test rigor** — the 12 tests (T1–T12) in `research-security-implementation-plan.md` §9. Confirmed at checkpoint: deliberately try to slip past each M individually.

---

## §7 Fresh-Session Restart Strategy

The next session will start without conversational context. Continuity depends on:

### §7.1 Loaded automatically
- `CLAUDE.md` (project instructions)
- `~/.claude/projects/-home-alt313-TGF/memory/MEMORY.md` (index)
- Memory entries referenced from MEMORY.md (loaded on demand or referenced)

### §7.2 Must be read on session start
- This document (`docs/framework-hardening-plan.md`) — the master orchestration
- `docs/RESEARCH-SECURITY.md` — Workstream 1 design
- `docs/research-security-implementation-plan.md` — Workstream 1 build plan
- `.sessions/2026-05-22-session-01-phase-6-commits-2-3-4-with-correction.md` — full session history including addendum

### §7.2.1 Read when relevant workstream begins
- `docs/workflow-v2-design-notes.md` — read at Workstream 2 plan-drafting time
- `docs/four-agents-design-notes.md` — read at Workstream 3 plan-drafting time

These two are starting input documents — they capture design content from the 2026-05-22 conversation that would otherwise be lost when the session restarts. The respective Workstream plans (Workstream 2 plan, Workstream 3 plan) will be authored when those workstreams begin and will iterate on the design notes.

### §7.3 Fresh-session prompt structure (to be authored after this plan lands)

The prompt should:
1. Establish role (continuing the TGF framework hardening work)
2. Reference this master plan as the orchestration document
3. State immediate task (Workstream 1, build sequence Step 1 from `research-security-implementation-plan.md` §10)
4. Reference the design + implementation docs as input
5. Reference the session log + memory for historical context
6. Specify any session-scope preferences (full build vs partial)

---

## §8 Post-Hardening: Phase 6 Resume

After Workstreams 1–5 complete, Phase 6 resumes from commit 5/12 (`security-secrets-management`) per `docs/phase-6-plan.md` §4 mini-spec. Commits 5/12–12/12 land under the new discipline:
- Stage 1 research runs under M1–M19 hook protection
- Stage 3 plan-with-governance uses WORKFLOW-V2 framework citations
- Stage 5 four-pass review uses Workstream 3's agents
- Stage 6 commit gate enforced by `Stop` hook + git pre-commit

Closeout commit 12/12 still includes the SECURITY-CORE forward-reference fix per Phase 6 Checkpoint 1 Decision C.

Phase 6 closeout transitions to Phase 7 (Extended Security Skills) under the same new discipline.

---

## §9 Risks and Residuals

What this plan does not eliminate:

**The Workstream 1 build itself runs under principles-only discipline.** Mitigated by intensive design review (this conversation) + narrow research scope (Claude Code internals only) + mechanical implementation. Accepted residual.

**Workstream sequencing is sequential** — total elapsed time is the sum of all workstreams. Could be 8–20 sessions before Phase 6 resumes. The alternative (parallel workstreams) increases coordination cost without obvious benefit at solo-developer scale.

**The four agents (Workstream 3) substantially expand framework complexity.** Risk: over-engineering, scope creep, agent-personas drifting from authoritative materials over time. Mitigated by per-workstream four-pass review and the eventual `framework-health` meta-skill (Phase 11) reviewing agent quality.

**Audit (Workstream 4) may surface a large remediation backlog.** Remediation (Workstream 5) could take longer than the rest of the hardening combined. Accept; better than carrying the technical debt unmeasured.

**Some Workstream 2 framework choices (NIST 800-53 backbone, etc.) may prove wrong in practice.** Plan-adjustments per the established TGF pattern (per Phase 2 onward) handle this: revise the workstream's plan, document the change, continue.

---

## §10 Cross-References

- `docs/RESEARCH-SECURITY.md` — Workstream 1 design
- `docs/research-security-implementation-plan.md` — Workstream 1 build plan with 20-step sequence
- `docs/workflow-v2-design-notes.md` — Workstream 2 design notes (starting input)
- `docs/four-agents-design-notes.md` — Workstream 3 design notes (starting input)
- `CLAUDE.md` — project instructions including §1 (Authoritative sources only), §3 (Workflow), §5 (Authority structure), §14 (Closing discipline)
- `docs/ARCHITECTURE.md` — extended framework architecture including §15 (Mode-Aware Operation), §18 (Hooks for Enforcement), §20 (Agent Orchestration)
- `docs/WORKFLOW.md` — current six-stage workflow (Workstream 2 will amend or replace)
- `docs/DECISIONS.md` — formal ADRs including `DEC-2026-05-17-004` (citation chain discipline), `DEC-2026-05-17-005` (hook event taxonomy), `DEC-2026-05-19-006` (session state architecture), `DEC-2026-05-20-010` (security-guidance plugin disable)
- `docs/ROADMAP.md` — high-level milestone tracking
- `docs/phase-6-plan.md` — Phase 6 plan; will be referenced when commit 5/12 resumes
- `.sessions/2026-05-22-session-01-phase-6-commits-2-3-4-with-correction.md` — session log capturing commits 2/12–4/12 + the design conversation that produced this plan
- `~/.claude/projects/-home-alt313-TGF/memory/project_tgf_build_phases.md` — memory entry with pause state and resumption pointers

---

**Status note:** plan locked at v1. Workstream 1 begins next session per the fresh-session restart strategy in §7. Plan amendments handled per Phase 4/5 precedent — captured in commit messages + session logs + memory.
