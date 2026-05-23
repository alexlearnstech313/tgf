# WORKFLOW-V2 — Design Notes

> **Status:** v1 design notes — written 2026-05-22 during the framework-hardening design conversation. Captures the structured approach to Stages 1/2/3 developed during that session.
>
> **Purpose:** preserve design work for Workstream 2 (per `docs/framework-hardening-plan.md` §3.2). This is NOT the Workstream 2 plan; that plan will be authored when Workstream 2 begins. This document is the starting input — the captured design content from which the plan will iterate.
>
> **Status when Workstream 2 begins:** treat this as design draft. Workstream 2's own plan will refine and formalize. Plan amendments are normal per Phase 2+ TGF precedent.

---

## §1 Context — Why WORKFLOW-V2

The current `docs/WORKFLOW.md` (Phase 3 deliverable, commit `2853047`) specifies the six-stage workflow as principles. Stage 1 (Research) says "understand what exists before changing anything"; Stage 2 (Scope) says "define what's changing"; Stage 3 (Plan with Governance) says "skills evaluate against the change context." These principles are correct but **under-standardized** — they don't trace to a specific authoritative methodology, which means:

1. **No mechanical checklist** to apply per stage
2. **No source-tier discipline** beyond what individual skills happen to encode
3. **No federal-grade traceability** from rule → standard → function (the kind of chain that audit-ready governance produces)
4. **No anchoring against established methodology** that gives the framework's stages credibility beyond "the framework's own design"

WORKFLOW-V2 (or amendment-to-WORKFLOW.md) grounds each stage in authoritative-source-backed methodology. The principles don't change; what changes is what backs them.

---

## §2 Source-Tier Hierarchy (Cross-Cutting)

Before per-stage standardization, formalize the source-tier hierarchy that the framework uses (currently implicit, partially in `docs/RESEARCH-SECURITY.md` §4.4 + `docs/research-security-implementation-plan.md` §4.1).

### §2.1 Tier 1 — Must Live-Fetch Every Use

**Living documents** — content can change between fetches. Citation requires a recent live fetch.

Examples: OWASP Cheat Sheets, OWASP ASVS chapters, OWASP Top 10 (year-specific), vendor documentation, framework documentation (React, Next.js, Python, etc.), CISA advisories.

Citation discipline: §2 Sources table entry MUST include "Date Verified" reflecting the most recent fetch. Re-verification cadence per `CLAUDE.md` §14 (quarterly).

### §2.2 Tier 2 — Publication-Level Citation Acceptable

**Stable formal publications** — content is stable across years; citation at publication level (with revision number) suffices without live re-fetch.

Examples: NIST Special Publications (SP 800-x with stated revision), NIST FIPS standards, IETF RFCs (with RFC number), ISO/IEC standards (with edition year), W3C Recommendations (with publication date).

Citation discipline: cite at "{document-id} (Revision N, Year)" granularity. Live fetch on first use to confirm document exists and current revision; subsequent uses cite at publication level without re-fetch.

### §2.3 Tier 3 — Comparative / Design-Rationale Only

**Books, papers, blog posts, conference talks** — not load-bearing for governance rules.

Examples: Brooks *Mythical Man-Month*, McConnell *Code Complete*, Greshake et al. 2023 paper, Mandiant M-Trends, security blog posts, Stack Overflow answers (rarely).

Citation discipline: may appear in design-rationale notes within plan documents; **do NOT appear in §2 Sources tables of skill files** unless explicitly load-bearing (rare). Per `DEC-2026-05-17-004` Clause 6.

### §2.4 Application to Workflow Stages

- **Stage 1 (Research)** fetches per the tier hierarchy. Research-log records the tier for every fetch.
- **Stage 3 (Plan with Governance)** cites at the appropriate tier level in rule citations and §2 Sources tables.
- **Stage 5 Phase 4 (Holistic Review)** verifies tier-application correctness (e.g., a Tier-1 source cited without "Date Verified" or recent fetch triggers a finding).

---

## §3 Stage 1 — Research, Structured Approach

### §3.1 Goal

Understand the change context with authoritative-source backing. Produce a research log per skill commit that traces every cited source to a verified fetch (Tier 1) or publication-level reference (Tier 2).

### §3.2 Authoritative Methodology

**Source-reliability matrix (Admiralty Code, per NATO STANAG 2022):**

| Reliability | Description |
|-------------|-------------|
| A — Completely reliable | NIST, IETF, OWASP, MITRE — official publications |
| B — Usually reliable | ISO, W3C, established vendor documentation |
| C — Fairly reliable | CIS, peer-reviewed academic literature |
| D — Not usually reliable | Industry blogs, vendor marketing |
| E — Unreliable | Forums, anecdotes |
| F — Cannot be judged | Anonymous sources |

| Credibility | Description |
|-------------|-------------|
| 1 — Confirmed by other sources | Multi-source corroboration |
| 2 — Probably true | Consistent with prior knowledge |
| 3 — Possibly true | Plausible but uncorroborated |
| 4 — Doubtful | Inconsistent with other sources |
| 5 — Improbable | Contradicted |
| 6 — Cannot be judged | Insufficient evidence |

TGF's source-tier hierarchy maps approximately to: Tier 1 = A; Tier 2 = A–B; Tier 3 = B–C. Stage 3 control-locking decisions require A1 (completely reliable + confirmed by other sources) — meaning Tier-1 or Tier-2 source plus independent multi-source corroboration (M5 + M12 per `docs/RESEARCH-SECURITY.md`).

**Structured Analytic Techniques (CIA *Tradecraft Primer*, declassified 2009):**

Applicable at Stage 1:
- **Key Assumptions Check** — what does the research assume that, if wrong, invalidates the conclusion?
- **Quality of Information Check** — what's the source reliability + corroboration status of each cited claim?
- **Analysis of Competing Hypotheses (ACH)** — when sources disagree, lay out competing interpretations and evaluate each against evidence

**OSINT corroboration principles:**
- Multi-source corroboration for high-stakes claims
- Source-origin transparency (cite specific URLs, not "according to OWASP")
- Currency (when was this information last verified)

**NIST SP 800-39 (Information Security Risk Management):**
- Threat-intelligence sourcing discipline
- Distinguishing strategic, operational, and tactical intelligence levels

### §3.3 Research-Log Requirement

Per `docs/research-security-implementation-plan.md` §4.4 (`.tgf/state/research-logs/{session_id}.json`):

Every fetch produces a research-log entry containing:
- URL, source-ID, tier
- Content hash, fetch timestamp
- Check results (M3 schema, M4 patterns, M11 drift, M13 hash, M14 unicode, M18 exception, M19 hidden)
- Status (verified / flagged / blocked-pending-review)
- Findings (if any)

Every §2 Sources table entry in a skill file MUST trace to a research-log entry with `status: verified`. This is mechanically enforced by Workstream 1's `PreToolUse` hook on Write/Edit (per `docs/RESEARCH-SECURITY.md` §7.4).

### §3.4 Stage 1 Checklist (Draft — Workstream 2 Will Finalize)

For each skill commit:

- [ ] All sources to cite identified at planning time (no "by reference" admissions at write time)
- [ ] Tier-1 sources live-fetched this session (timestamp in research-log)
- [ ] Tier-2 sources confirmed via canonical index (NIST CSRC publication index, IETF datatracker, etc.) — citation existence verified (M10)
- [ ] Tier-3 sources are clearly design-rationale-only; do not appear in §2 Sources
- [ ] Research log written for every fetch
- [ ] Each fetch passed M3/M4/M11/M13/M14/M18/M19 checks (or has `flagged` status with explicit human review)
- [ ] Citation-existence verified for every cited document ID (M10)
- [ ] Adversarial-source threat considered (does the source live in a high-tampering-risk location? Should we apply M11 drift detection?)
- [ ] Where corroboration is needed (M5), at least one independent source per claim has been fetched (M12 independence verified via source-org-mapping)
- [ ] AI-memory-alignment flag honestly noted — if AI prior knowledge confirms the fetched content, that is one source of evidence, not two (M9)

---

## §4 Stage 2 — Scope, Structured Approach

### §4.1 Goal

Define what's changing, what's not, what trust boundaries are crossed, what dependencies are touched. Produce explicit scope statement that downstream stages can evaluate against.

### §4.2 Authoritative Methodology

**NIST SP 800-37 Rev 2 (Risk Management Framework — Categorize step):**

The RMF's first step formalizes scope:
1. **System description** — what is the system? What does it do?
2. **Information types** — what kinds of data flow through it?
3. **Impact levels** — for confidentiality / integrity / availability: low, moderate, or high impact if compromised?
4. **System boundary** — what's inside the system; what's outside; where are the trust boundaries?

For TGF skill commits, "system" = the change context (the files being modified + their immediate dependencies).

**NIST SP 800-160 Vol 1 Rev 1 (Systems Security Engineering):**

Section on system definition + scoping:
- Identify stakeholders
- Identify system functions
- Identify external interfaces (where trust boundaries exist)
- Identify constraints (regulatory, performance, deployment)

**Microsoft SDL (Security Development Lifecycle) — threat modeling scope:**

For threat-modeling at the scope stage (rather than as separate phase):
- Identify trust boundaries
- Identify assets crossing those boundaries
- Identify actors on each side

**ISO/IEC/IEEE 15288:2023 — Systems Lifecycle Processes:**

Scope as part of stakeholder needs definition. Not heavily used in TGF (too enterprise-scale) but worth referencing for terminology.

**STRIDE-per-element (integrated at scope, not after-the-fact):**

For each element in the scope (data flow, process, data store, external entity, trust boundary), consider STRIDE:
- **S**poofing (identity)
- **T**ampering (integrity)
- **R**epudiation (non-repudiation)
- **I**nformation disclosure (confidentiality)
- **D**enial of service (availability)
- **E**levation of privilege (authorization)

This integration at scope (rather than at security audit) catches whole categories of issues earlier.

### §4.3 Stage 2 Checklist (Draft — Workstream 2 Will Finalize)

For each skill commit:

- [ ] Files being modified explicitly listed
- [ ] Files explicitly out of scope listed
- [ ] Change tier identified (Trivial / Small / Medium / Large per `CLAUDE.md` §3 Stage 2 rubric)
- [ ] Trust boundaries affected by the change identified (input boundary, output boundary, persistence boundary, network boundary, etc.)
- [ ] Information types touched identified (PII, PHI, payment data, secrets, public data — different impact levels)
- [ ] STRIDE-per-element review for changed components — at least at high level
- [ ] ROADMAP milestone this advances explicitly identified
- [ ] Dependencies (other skills, other framework artifacts) explicitly identified
- [ ] Change-tier scaling for Stage 5 four-pass review determined (Trivial = code review only; Small = code + holistic; Medium = full four-pass; Large = full four-pass with deep red team)

---

## §5 Stage 3 — Plan with Governance, Structured Approach

### §5.1 Goal

Lock in the controls and rules that the change will implement. This is where authoritative-source-backed governance commits to specific decisions. **This stage is the highest-stakes** because controls locked here become real and enforced.

### §5.2 Authoritative Methodology

**NIST SP 800-53 Rev 5 — Security and Privacy Controls Catalog (the backbone):**

NIST 800-53 is the canonical federal-grade control catalog. ~1,000 controls across 20 families:

| Family | Topic |
|--------|-------|
| AC | Access Control |
| AT | Awareness and Training |
| AU | Audit and Accountability |
| CA | Assessment, Authorization, and Monitoring |
| CM | Configuration Management |
| CP | Contingency Planning |
| IA | Identification and Authentication |
| IR | Incident Response |
| MA | Maintenance |
| MP | Media Protection |
| PE | Physical and Environmental Protection |
| PL | Planning |
| PM | Program Management |
| PS | Personnel Security |
| PT | PII Processing and Transparency |
| RA | Risk Assessment |
| SA | System and Services Acquisition |
| SC | System and Communications Protection |
| SI | System and Information Integrity |
| SR | Supply Chain Risk Management |

**Proposal:** every rule in every Phase 6+ skill cross-maps to one or more NIST 800-53 control IDs. This produces a federal-grade traceability chain:

```
Rule (in skill file)
  → ASVS / Top 10 / CWE (existing citation chain)
    → NIST 800-53 control ID (new mapping)
      → NIST CSF 2.0 function (cross-cutting check)
```

**Concrete example:**
- `skills/security-input-validation/` Rule 5.1 (Validate Input at Trust Boundaries) currently cites OWASP ASVS V2.2.2 + OWASP Top 10:2025 A05 + CWE-20
- Add: NIST 800-53 SI-10 (Information Input Validation) and SI-15 (Information Output Filtering)
- Cross-cuts to NIST CSF 2.0 PR.PS-06 (data integrity) and PR.IR-01 (network communications integrity)

This is what Stage 3 produces at maturity — full citation chains with federal-grade traceability.

**NIST CSF 2.0 (2024 update added the Govern function):**

Six functions:
- **GV** Govern — organizational context, risk management, policy
- **ID** Identify — asset management, business environment, governance
- **PR** Protect — access control, awareness, data security, processes
- **DE** Detect — anomalies and events, continuous monitoring, detection processes
- **RS** Respond — response planning, communications, analysis, mitigation, improvements
- **RC** Recover — recovery planning, improvements, communications

Cross-cutting check: every rule should map to at least one CSF function. If a skill has rules but no Detect-function representation, that's a gap.

**CIS Controls v8.1 — Top-18 Prioritized:**

CIS Controls are more practical / opinionated than NIST 800-53. Useful for prioritization (which controls matter most when budget is constrained).

**ISO/IEC 27002:2022 — Code of Practice for Information Security Controls:**

International equivalent to NIST 800-53. Useful when projects have international compliance scope (GDPR adjacency, etc.).

### §5.3 Where M5 / M8 / M12 Fire

Per `docs/RESEARCH-SECURITY.md` §7.3:

- **M5 (Multi-source corroboration):** before locking in a security control with specific parameters, verify at least two independent authoritative sources support the parameter. Recorded in research-log + cross-referenced in Stage 3 plan output.
- **M12 (Independence verification):** the corroborating sources must be from different organizations (`source-org-mapping.json` check). Same-org "multi-source" doesn't count.
- **M8 (Human verification):** at control-lock time, the framework surfaces a verification summary to the human; commit cannot proceed without explicit approval recorded in `.tgf/state/m8-approvals/`.

These three mitigations together implement the "you need real corroboration plus human review before locking controls" discipline.

### §5.4 Stage 3 Checklist (Draft — Workstream 2 Will Finalize)

For each rule or control being locked in:

- [ ] Primary citation chain complete: rule → existing standard (ASVS / Top 10 / CWE / etc.) → NIST 800-53 control ID(s) → NIST CSF 2.0 function(s)
- [ ] M5 multi-source corroboration: at least two independent sources from research-log support this rule's parameters
- [ ] M12 independence verified: corroborating sources are from different organizations per source-org-mapping
- [ ] M9 memory-alignment flagged honestly: if AI prior knowledge matches the cited content, this is one source of evidence, not two — corroboration still required
- [ ] M18 exception clauses scanned: any "X is required except when..." patterns explicitly reviewed
- [ ] M8 human approval recorded for control-locking decisions (parameter values, algorithm choices, threshold values, etc.)
- [ ] Existing-pattern check: does this rule align with how other skills handle similar concerns, or is it introducing a new approach?
- [ ] Stage 5 Phase 2 (Security Audit) preview: would the security-auditor agent be likely to flag this?

---

## §6 Cross-Cutting — Integration with Other Workstreams

### §6.1 Integration with Workstream 1 (Research-Security)

WORKFLOW-V2's Stage 1 standardization REQUIRES research-security hooks to be operational. The research-log requirement is mechanically enforceable; without hooks, it's principles-only (which is what failed on commit 4/12).

Specifically:
- M3/M4/M11/M13/M14/M18/M19 hooks run on every WebFetch (Stage 1)
- PreToolUse-Write hook blocks §2 Sources entries lacking research-log provenance (Stage 4 — but enforces Stage 1 discipline)
- Stop hook + git pre-commit verify §2-Sources-traceability + M8 approvals (Stage 6)

### §6.2 Integration with Workstream 3 (Four Agents)

WORKFLOW-V2's stage standardization SHAPES what each agent reviews:
- Code Reviewer (Phase 1): reviews craftsmanship of Stage 4 output
- Security Auditor (Phase 2): reviews Stage 3 control choices against NIST 800-53 / CSF / ASVS / etc.
- Red Team (Phase 3): probes Stage 3 controls adversarially
- Holistic Reviewer (Phase 4): verifies Stage 1 research-log traceability + roadmap alignment + conceptual integrity + decision documentation

### §6.3 Integration with Workstream 4 (Audit)

The audit applies WORKFLOW-V2's standards retroactively to Phase 4–6 commits. Specifically:
- Every existing skill commit's §2 Sources is checked for traceability to (retroactively constructable) research-log entries
- Every rule citation is checked for NIST 800-53 / CSF cross-mapping completeness (likely incomplete since this discipline is new; findings produce remediation list)
- Every control-locking parameter is checked for M5/M12/M8 evidence (likely incomplete; remediation list)

---

## §7 Open Questions for Workstream 2

Items to resolve when Workstream 2 begins:

1. **Replace WORKFLOW.md or amend?** A v2 file is cleaner; amendment preserves history. Probably amend (per `DEC-2026-05-17-004` and Phase 3 precedent).
2. **NIST 800-53 mapping cost.** Cross-mapping ~hundreds of existing rules to control IDs is substantial work. Phase it: new commits map at write time; existing commits get mapped in Workstream 5 (Remediation).
3. **CSF 2.0 cross-cutting at what depth?** Per-rule mapping, per-skill mapping, or per-phase mapping? Probably per-skill is the sweet spot.
4. **Stage 2 STRIDE-per-element formalization.** Should STRIDE be applied to every change or only changes touching trust boundaries? Probably the latter.
5. **Stage gates as advisory vs hard gates.** Stage 1 → Stage 2 gate (research-log entries exist) — hard gate via hook? Stage 3 → Stage 4 gate (corroboration documented) — hard gate? Probably yes for both; soft warnings for stages 2 → 3 and 4 → 5 (artifact existence checks).

---

## §8 Cross-References

- `docs/framework-hardening-plan.md` — orchestrates the five workstreams including Workstream 2
- `docs/RESEARCH-SECURITY.md` — research-security context that WORKFLOW-V2's Stage 1 builds on
- `docs/research-security-implementation-plan.md` — hooks that mechanically enforce Stage 1/3/6 gates
- `docs/four-agents-design-notes.md` — the four agents that operate within WORKFLOW-V2's stages
- `docs/WORKFLOW.md` — current six-stage workflow (Workstream 2 will amend or replace)
- `docs/ARCHITECTURE.md` §15 — mode-aware operation
- `docs/DECISIONS.md` — `DEC-2026-05-17-004` (citation chain six clauses), `DEC-2026-05-19-006` (session state architecture)
- NIST SP 800-53 Rev 5 — https://csrc.nist.gov/publications/detail/sp/800-53/rev-5/final
- NIST CSF 2.0 — https://www.nist.gov/cyberframework
- NIST SP 800-37 Rev 2 — https://csrc.nist.gov/publications/detail/sp/800-37/rev-2/final
- NIST SP 800-160 Vol 1 Rev 1 — https://csrc.nist.gov/publications/detail/sp/800-160/vol-1-rev-1/final
- CIS Controls v8.1 — https://www.cisecurity.org/controls
- ISO/IEC 27002:2022 — ISO catalog
- NATO STANAG 2022 / Admiralty Code — defense intelligence community reference
- CIA *A Tradecraft Primer* (declassified) — public defense intelligence community

---

**Status note:** these design notes are starting input for Workstream 2. The Workstream 2 plan will refine the per-stage approach, finalize the checklists, decide on WORKFLOW.md amendment vs WORKFLOW-V2.md replacement, formalize the NIST 800-53 / CSF mapping strategy, and define stage-gate enforcement mechanisms. Plan amendments during implementation are expected; this document is design draft, not specification.
