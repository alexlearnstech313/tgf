# Workstream 2 Plan: WORKFLOW-V2 Methodology Grounding

> **Status:** v1 draft — written 2026-05-23. Awaits Checkpoint 1 approval per the [[feedback-phase-plan-workflow]] discipline before implementation begins.
>
> **Scope:** authority-back the existing six-stage workflow against established methodology (Admiralty Code at Stage 1; NIST RMF Categorize at Stage 2; NIST 800-53 + CSF 2.0 + CIS v8.1 + ISO 27002 at Stage 3). Add per-stage checklists, formalize the source-tier hierarchy, and define the rule → ASVS → 800-53 → CSF citation chain as a target for new skill commits. Surgical amendment to `docs/WORKFLOW.md` — not a replacement.
>
> **Companion documents:** `docs/workflow-v2-design-notes.md` (the design conversation's captured starting input, committed `dc2b294`), `docs/framework-hardening-plan.md` §3.2 (orchestration), `docs/RESEARCH-SECURITY.md` (the M1–M19 hook surface this workstream depends on).

---

## §1 Purpose and Scope

### §1.1 What this plan covers

The concrete spec changes needed to ground TGF's six-stage workflow in authoritative methodology. Specifically:

- Expand `.tgf/state/source-registry.json` with the ~12 framework documents Workstream 2 cites (NIST 800-37/53/160/39, CSF 2.0, CIS v8.1, ISO 27002 via crosswalk, the OWASP ASVS-to-NIST-800-53 mapping, public references for NATO STANAG / Admiralty Code, CIA *Tradecraft Primer*).
- Amend `docs/WORKFLOW.md` in place with per-stage methodology sections + checklists, a formalized source-tier hierarchy (Tier 1/2/3), and a citation-chain depth target.
- Produce one worked example that takes an existing rule from one Phase 6 skill and demonstrates the full chain: rule → OWASP ASVS → NIST 800-53 control ID → NIST CSF 2.0 Subcategory.
- Touch `CLAUDE.md` §3 only if WORKFLOW.md changes alter the contract — most likely a small cross-reference addition, not substantive content change.

### §1.2 What this plan does NOT cover

- **Rewriting or replacing the six-stage workflow.** The stages stay, names stay, I/O contracts stay, subagent dispatch points stay. WORKFLOW-V2 layers methodology on top.
- **Retroactively mapping existing Phase 4–6 skills** to the new citation chain. That's Workstream 4 (audit) + Workstream 5 (remediation) territory. WS2 produces one worked example as a proof-of-concept; bulk retroactive mapping is deferred.
- **Adding new Claude Code hooks for stage-gate enforcement.** Workstream 1's `PreToolUse-Write` already blocks Stage 4 writes citing un-verified sources; the Stop hook + git pre-commit cover Stage 6. Stage 1→2 and Stage 3→4 explicit gates would be a WS1 amendment, not WS2's domain — defer.
- **Wiring `parameter-history.json` (M17).** Stage 3 plan-with-governance is where parameter values get tracked across sessions; the hook infrastructure exists but the write path is unwired. Defer to the WS1 amendment that activates it when first triggered.
- **Implementing the four review agents** that will use WORKFLOW-V2's stages — that's Workstream 3.
- **Stack-baseline-specific or compliance-specific workflow variants** — those are out of scope for v1 of the methodology grounding.

### §1.3 Why this work matters

`CLAUDE.md` §1 says: *"Every governance rule you apply traces to a specific authoritative source."* That principle currently applies to skill content but not to the workflow that produces skills. WORKFLOW.md cites Claude Code documentation, prior ADRs, and OWASP LLM Top 10 (for hook untrusted-input discipline), but the *methodology* of how a workflow stage gathers research, defines scope, or selects controls is principles-only.

This is the asymmetry that Workstream 2 closes. After WS2, the workflow stages cite the same caliber of source the skills they produce do.

---

## §2 Prerequisites

Before build:

1. **Workstream 1 operational.** ✅ Confirmed `dc2b294` on `origin/main`; SessionStart hook confirmed firing this session.
2. **Pre-commit hook installed locally.** ✅ Per session-02 log; `.git/hooks/pre-commit` symlink in place.
3. **Source-registry write access tested.** The registry is a tracked JSON file at `.tgf/state/source-registry.json` (per `.gitignore` selective tracking); edits ride through normal Edit hook chain.
4. **Understanding of M15 URL allow-list.** First WebFetch to any URL outside `allow_url_patterns` will be blocked by PreToolUse-WebFetch. Registry expansion (Build Step 1) MUST precede the first Stage 1 fetch.
5. **Understanding of DEC-004 Clause 5 (paywalled sources).** ISO/IEC 27002:2022 and ISO/IEC/IEEE 15288 cannot be fetched directly; cited via free authoritative crosswalks only.
6. **Acceptance that this workstream runs at slower fetch cadence than WS1's build did.** Every fetch goes through the full M1–M19 pipeline. Plan check-ins should anticipate hook iteration if a fetch reveals a hook gap.

---

## §3 Approach Decisions (Meta — Resolve at Checkpoint 1)

These are the meta-decisions that shape everything downstream. Recommendations attached; final call is Alt's at Checkpoint 1.

| ID | Decision | Recommendation | Why |
|----|----------|----------------|-----|
| **A** | Amend `WORKFLOW.md` in place vs ship `WORKFLOW-V2.md` separately | **Amend in place** with version bump in the document header and a changelog section | Single source of truth. Two-file approach creates drift risk; the four-pass review and the four agents (WS3) all need *the* workflow doc, not two of them. |
| **B** | Stage-gate enforcement: add new hooks for Stage 1→2 and Stage 3→4 OR rely on WS1's downstream enforcement | **Rely on downstream enforcement** | WS1's PreToolUse-Write blocks Stage 4 writes citing un-verified sources (catches Stage 1 violations late but reliably); Stop + git pre-commit catch Stage 6. Adding new hooks for explicit stage gates duplicates coverage and bloats WS2 scope. Adding stage-gate hooks belongs in a WS1 amendment if downstream enforcement proves insufficient in practice. |
| **C** | NIST 800-53 mapping for existing Phase 4–6 skills: do now OR defer to WS5 | **Defer to WS5** | Cross-mapping every existing rule is multi-session work and not on WS2's critical path. WS2 produces one worked example to prove the chain works; WS5 handles bulk under the WS4 audit findings. |
| **D** | NIST CSF 2.0 cross-cutting mapping depth: per-rule, per-skill, or per-phase | **Per-skill** | Per-rule explodes the mapping table without adding precision (a skill's rules usually cluster under 1–3 CSF Subcategories). Per-phase loses information. Per-skill is the sweet spot — one row per skill in the cross-reference table. |
| **E** | ISO/IEC 27002:2022 sourcing: via NIST/CSF crosswalk OR skip ISO citations entirely | **Via crosswalk** (CSF 2.0 Informative References) | DEC-004 Clause 5 explicitly permits citing paywalled standards via free authoritative crosswalks. CSF 2.0 Informative References map every Subcategory to ISO 27001/27002 controls. International alignment matters for adopters outside US federal context (GDPR adjacency, etc.). |
| **F** | STRIDE-per-element at Stage 2: apply to every change OR only trust-boundary-crossing changes | **Trust-boundary-only** | STRIDE on a typo fix is theater. STRIDE at the trust boundary catches what matters. Stage 2's scope rubric already identifies trust-boundary impacts; this hooks STRIDE to that trigger. |
| **G** | Admiralty Code rigor: explicit A–F × 1–6 grading for ALL sources OR Tier-1 presumed A1 + explicit grading for non-Tier-1 only | **Tier-1 presumed A1, explicit grading for Tier-2/3** | OWASP/NIST/MITRE/IETF are uniformly A1; explicit grading every entry is busywork that obscures the real value. The discipline matters when a Tier-3 source threatens to sneak into a governance role ("this Medium blog post is D5 — not authoritative"). |
| **H** | `CLAUDE.md` §3 update: touch or leave alone | **Small cross-reference addition only** | The contract in CLAUDE.md §3 stays. Add a sentence noting WORKFLOW.md grounds each stage in named methodology (Admiralty Code / NIST RMF / NIST 800-53). No substantive contract change. |
| **I** | Commit decomposition: one combined commit OR multiple smaller commits | **3–4 smaller commits** (per [[feedback-commit-message-style]] portfolio framing) | (1) source registry + schemas + first verified fetches; (2) WORKFLOW.md amendment; (3) worked example + cross-reference table; (4) closeout (CLAUDE.md cross-ref, framework-hardening-plan §3.2 status update, session log). Easier portfolio-skim than one giant commit. |
| **J** | `parameter-history.json` M17 wiring: now or defer | **Defer to WS1 amendment** | Hook infrastructure work (write path activation) belongs in WS1's domain. WS2 identifies the need; WS1's next amendment wires it. |
| **K** | Worked example: which existing rule | **`skills/security-input-validation` Rule 5.1** (the design-notes' own example: ASVS V2.2.2 → 800-53 SI-10/SI-15 → CSF PR.PS-06/PR.IR-01) | Design-notes already sketched it; validates the methodology end-to-end without inventing a new example. |

---

## §4 Source Registry Expansion

This is **Build Step 1** and must complete before any other Stage 1 fetch. M15 blocks unregistered URLs at PreToolUse.

### §4.1 Sources to register

12 new entries, organized by tier + organization.

**Tier 2 — NIST stable publications** (publication-level citation acceptable; live-fetch on first use to confirm existence + revision):

| Source ID | Document | Primary URL pattern | Schema |
|-----------|----------|---------------------|--------|
| `NIST-SP-800-37` | RMF Rev 2 (Risk Management Framework) | `csrc.nist.gov/pubs/sp/800/37/r2/*`, `nvlpubs.nist.gov/.../NIST.SP.800-37r2.pdf` | `nist-sp` (existing) |
| `NIST-SP-800-53` | Rev 5.1.1 (Controls Catalog) | `csrc.nist.gov/pubs/sp/800/53/r5/*`, control-family browser URLs | `nist-sp` (existing) |
| `NIST-SP-800-53A` | Rev 5 (Assessment Procedures) | `csrc.nist.gov/pubs/sp/800/53/a/r5/*` | `nist-sp` (existing) — register if WS3 needs it; defer otherwise |
| `NIST-SP-800-160-V1` | Vol 1 Rev 1 (Systems Security Engineering) | `csrc.nist.gov/pubs/sp/800/160/v1/r1/*` | `nist-sp` (existing) |
| `NIST-SP-800-39` | Risk Management Strategy | `csrc.nist.gov/pubs/sp/800/39/*` | `nist-sp` (existing) |
| `NIST-CSF-2-0` | Cybersecurity Framework 2.0 | `nist.gov/cyberframework`, `nvlpubs.nist.gov/nistpubs/CSWP/NIST.CSWP.29.pdf` | NEW: `nist-csf` |
| `NIST-CSF-2-0-IR` | CSF 2.0 Informative References (crosswalk to ISO/CIS/COBIT) | `nist.gov/informative-references`, the CSF 2.0 Reference Tool | NEW: `nist-csf-ir` |

**Tier 1 — Living documents** (live-fetch every use):

| Source ID | Document | Primary URL pattern | Schema |
|-----------|----------|---------------------|--------|
| `OWASP-ASVS-MAPPING-800-53` | ASVS-to-NIST-800-53 mapping from OWASP ASVS repo `Mapping/` folder | `raw.githubusercontent.com/OWASP/ASVS/master/5.0/mappings/*` | NEW: `owasp-mapping-csv` |
| `CIS-CONTROLS-V8-1` | CIS Controls v8.1 (free with registration; the controls list itself is published) | `cisecurity.org/controls/v8-1`, `learn.cisecurity.org/cis-controls-download` | NEW: `cis-controls` |
| `MITRE-ATTACK-ENTERPRISE` | ATT&CK Enterprise techniques (referenced by WS3 personas; useful in WORKFLOW-V2 §3 Stage 3 adversarial cross-check) | `attack.mitre.org/techniques/enterprise/`, `attack.mitre.org/versions/v15/*` | NEW: `mitre-attack` |
| `MITRE-ATLAS` | ATLAS adversarial AI taxonomy (already implicitly cited; formalize) | `atlas.mitre.org/techniques/*`, `atlas.mitre.org/matrices/*` | NEW: `mitre-atlas` |

**Tier 3 — Comparative / design-rationale** (cited in WORKFLOW.md design rationale; NOT in §2 Sources tables of skill files):

| Source ID | Document | Primary URL pattern | Schema |
|-----------|----------|---------------------|--------|
| `MS-SDL` | Microsoft Security Development Lifecycle (threat-modeling scope reference at Stage 2) | `microsoft.com/en-us/securityengineering/sdl/*` | NEW: `vendor-doc` (permissive) |
| `CIA-TRADECRAFT-PRIMER` | CIA *A Tradecraft Primer* (declassified 2009; structured analytic techniques at Stage 1) | `cia.gov/.../Tradecraft Primer-apr09.pdf`, `cia.gov/static/.../tradecraft-primer.pdf` | NEW: `gov-pdf` |
| `JOINT-PUB-2-22-3` | US Army FM 2-22.3 / Joint Pub 2-0 (Admiralty Code public reference; Joint Intelligence) | `armypubs.army.mil/.../FM 2-22.3.pdf`, `jcs.mil/.../jp2_0.pdf` | NEW: `gov-pdf` |

**Excluded explicitly:**

- **NATO STANAG 2022 itself** — not reliably public. Use the US Army FM 2-22.3 or Joint Intelligence publication as the public-canonical reference for the Admiralty Code. Cite Admiralty Code by name + the public reference document.
- **ISO/IEC 27002:2022** as a fetched source — paywalled per DEC-004 Clause 5. Citations route through `NIST-CSF-2-0-IR` (Informative References) crosswalk only.
- **ISO/IEC/IEEE 15288:2023** — paywalled, same routing. Note that this is referenced in design-notes for terminology; if citation is needed, use the NIST 800-160 references to 15288 instead.

### §4.2 Schemas to add to `.tgf/state/source-schemas/`

New schema definitions needed:

- `nist-csf.json` — permissive (size + identity string "Cybersecurity Framework"); CSF 2.0 has a known structural backbone (Functions / Categories / Subcategories) but the canonical URL serves PDF + HTML variants
- `nist-csf-ir.json` — permissive (Informative References tool serves dynamic content; min-size + identity strings "Informative Reference", "Subcategory")
- `owasp-mapping-csv.json` — strict-ish (CSV/markdown format; required column headers "Section", "Item", "CWE", "NIST")
- `cis-controls.json` — permissive (size + identity strings "CIS Controls", "Safeguard")
- `mitre-attack.json` — permissive (size + identity strings "Technique", "T1*" or "T0*" ID pattern)
- `mitre-atlas.json` — permissive (size + identity strings "ATLAS", "AML.")
- `vendor-doc.json` — permissive (size only — vendor docs vary wildly in structure)
- `gov-pdf.json` — permissive (size + identity strings derived from canonical document title)

Tightening per type can happen as baselines accumulate per Workstream 1's lazy-baseline approach. Schemas land permissive and tighten over time.

### §4.3 `source-org-mapping.json` additions

Current publishers: OWASP / NIST / IETF / ISO / MITRE. Add:

- **CIS** (Center for Internet Security) — non-profit, US-based, distinct from NIST
- **DoD-Joint-Staff** (for FM 2-22.3 / JP 2-0) — US-federal, distinct from NIST/CIA
- **CIA** — US-federal, distinct from NIST/DoD (intelligence community)
- **Microsoft** — vendor, distinct from all framework bodies

This matters for M12 independence verification: when WORKFLOW-V2 §3 Stage 3 cites two sources for a control parameter, M12 checks they're from different organizations. NIST + ISO (via crosswalk) is independent. NIST + CIS overlay is independent. NIST + Microsoft is independent. Two NIST documents are NOT independent.

### §4.4 Registration order during build

Strict ordering — each fetch is gated by registry presence:

1. Add all 12 entries to `source-registry.json` (single commit if possible, since all are inter-related).
2. Add 8 new schemas.
3. Add 4 new publishers to org mapping.
4. Verify by direct registry-lookup test (`python .claude/hooks/lib/source_registry.py --check-url https://csrc.nist.gov/pubs/sp/800/53/r5/upd1/final` etc.) for each URL pattern BEFORE attempting any WebFetch.
5. Only then begin Stage 1 fetches for WORKFLOW-V2 research.

If a fetch then surfaces an unregistered URL variant (e.g., NIST serves a different subdomain than the pattern matched), pause, update the registry pattern, retry. Don't override the M15 block — fixing the pattern is the correct response.

---

## §5 Per-Stage Amendment Specifications

What WORKFLOW.md §3 (Per-Stage Specifications) gains for each stage. The stage's existing structure (Inputs / Operations / Mode conditionals / Tier conditionals / Outputs / Skill activation / Hook integration / Subagent dispatch / Failure modes) stays. Each stage gains a new **Authoritative Methodology** sub-section and a **Stage N Checklist** sub-section.

### §5.1 Stage 1 — Research (the largest amendment)

**New sub-section: §3 Stage 1 — Authoritative Methodology**

Three frameworks ground the Stage 1 work:

1. **Admiralty Code** (NATO source-reliability × information-credibility grading; reference: US Army FM 2-22.3 / Joint Pub 2-0 for public canonical text). Stage 1 produces fetches that get implicitly graded — Tier-1 sources presumed A1 (completely reliable + multi-source confirmed); non-Tier-1 sources require explicit grading. Per **Approach Decision G**.
2. **CIA Structured Analytic Techniques** (CIA *Tradecraft Primer*, 2009 declassified). Stage 1 applies (a) Key Assumptions Check — what does the research assume that, if wrong, invalidates the conclusion? (b) Quality of Information Check — what's the source reliability per the Admiralty grade? (c) Analysis of Competing Hypotheses (ACH) — when sources disagree, lay out competing interpretations and evaluate.
3. **NIST SP 800-39** (Risk Management Strategy) — threat-intelligence sourcing discipline distinguishing strategic (long-horizon trends), operational (campaign-level), and tactical (technique-level) intelligence levels. Stage 1 research output is implicitly tactical when investigating a specific change; operational/strategic when investigating broader patterns.

**New sub-section: §3 Stage 1 — Checklist**

Per skill commit / per change:

- [ ] All sources to cite identified at planning time (no "by reference" admissions at write time — the commit-4/12 lesson)
- [ ] Every Tier-1 source live-fetched this session (timestamp in research-log)
- [ ] Tier-2 sources confirmed via canonical index (NIST CSRC publication index, IETF datatracker, OWASP repo tags) — citation existence verified (M10)
- [ ] Tier-3 sources flagged as design-rationale-only; do not appear in §2 Sources tables of skill files
- [ ] Research log written for every fetch (mechanical via PostToolUse-WebFetch)
- [ ] Each fetch passed M3/M4/M11/M13/M14/M18/M19 checks, OR has `flagged` status with explicit human review recorded
- [ ] Citation-existence verified for every cited document ID (M10)
- [ ] Adversarial-source threat considered for any Tier-1 source in a high-tampering-risk location (vendor documentation behind CDN edge, repos with weak access controls)
- [ ] Where M5 corroboration is required, at least one independent source per claim (M12 independence verified via source-org-mapping)
- [ ] AI-memory-alignment flag honest — if AI prior knowledge confirms the fetched content, that's one source of evidence, not two (M9)
- [ ] If any source got an Admiralty Code grade below A2, explicit rationale for relying on it OR escalate to a stronger source

### §5.2 Stage 2 — Scope

**New sub-section: §3 Stage 2 — Authoritative Methodology**

Four frameworks ground Stage 2:

1. **NIST SP 800-37 Rev 2 — Categorize step.** Formal scope definition: system description; information types touched (PII / PHI / payment / secrets / public); impact levels for C/I/A (low/moderate/high); system boundary. For TGF skill commits, "system" = the change context (files modified + immediate dependencies).
2. **NIST SP 800-160 Vol 1 Rev 1 — system definition + scoping.** Identify stakeholders, system functions, external interfaces (= trust boundaries), constraints (regulatory, performance, deployment).
3. **Microsoft SDL — threat-modeling scope.** Trust boundaries, assets crossing them, actors on each side.
4. **STRIDE-per-element** (integrated at scope, applied **only to trust-boundary-crossing changes** per Approach Decision F). For each element (data flow, process, data store, external entity, trust boundary) consider: Spoofing / Tampering / Repudiation / Information disclosure / Denial of service / Elevation of privilege.

**New sub-section: §3 Stage 2 — Checklist**

Per skill commit / per change:

- [ ] Files being modified explicitly listed (already required)
- [ ] Files explicitly out of scope listed (already required)
- [ ] Change tier identified per `CLAUDE.md` §3 rubric (already required)
- [ ] Trust boundaries affected explicitly identified (input boundary, output boundary, persistence boundary, network boundary)
- [ ] Information types touched identified (PII / PHI / payment / secrets / public — different impact levels)
- [ ] STRIDE-per-element review for trust-boundary-crossing components (Approach Decision F gate)
- [ ] ROADMAP milestone this advances explicitly identified (already required)
- [ ] Dependencies (other skills, framework artifacts) explicitly identified
- [ ] Change-tier scaling for Stage 5 review determined
- [ ] Impact-level rationale recorded (low/moderate/high for C/I/A) — informs Stage 5 review depth and waiver bar

### §5.3 Stage 3 — Plan with Governance (the highest-stakes amendment)

**New sub-section: §3 Stage 3 — Authoritative Methodology**

Four frameworks ground Stage 3, with NIST 800-53 as structural backbone:

1. **NIST SP 800-53 Rev 5 — Controls Catalog (backbone).** ~1,000 controls across 20 families (AC / AT / AU / CA / CM / CP / IA / IR / MA / MP / PE / PL / PM / PS / PT / RA / SA / SC / SI / SR). Every rule in every Phase 6+ skill maps to one or more 800-53 control IDs as part of its citation chain.
2. **NIST CSF 2.0 — Functions cross-cutting check.** Six Functions: Govern (GV — new in 2.0) / Identify (ID) / Protect (PR) / Detect (DE) / Respond (RS) / Recover (RC). Cross-cutting per-skill mapping (Approach Decision D): each skill maps to at least one CSF Subcategory. A skill with no Detect-function representation in any rule is a gap worth flagging.
3. **CIS Controls v8.1 — top-18 prioritized overlay.** Useful as a "minimum viable" filter — which 800-53 controls actually matter at solo-developer / small-org scale. Implementation Group 1 (IG1 = essential cyber hygiene) is the most actionable subset.
4. **ISO/IEC 27002:2022 — international code of practice** via CSF 2.0 Informative References crosswalk (NOT direct fetch, per Approach Decision E). Useful when projects have international compliance scope.

**New sub-section: §3 Stage 3 — Citation Chain Target**

For every rule locked in at Stage 3:

```
Rule (in skill file)
  → OWASP ASVS / Top 10 / CWE / etc. (existing citation chain)
    → NIST 800-53 control ID(s)              [new]
      → NIST CSF 2.0 Subcategory(ies)        [new — cross-cutting per skill]
        → ISO/IEC 27002:2022 control(s)      [via CSF 2.0 Informative References, optional but encouraged]
```

The translation step from ASVS to 800-53 uses the **OWASP ASVS-to-NIST-800-53 mapping document** (`OWASP-ASVS-MAPPING-800-53` in registry). Claude does NOT invent mappings — M9 problem. The translation step from 800-53 / Subcategory to ISO 27002 uses the **NIST CSF 2.0 Informative References** crosswalk (`NIST-CSF-2-0-IR` in registry).

**Per Approach Decision C: this chain is the TARGET for new skill commits going forward.** Existing Phase 4–6 skills are not retroactively mapped by WS2 — WS4 audits surface what's missing; WS5 remediates.

**Worked example** (Approach Decision K — full detail in §8 of this plan).

**New sub-section: §3 Stage 3 — Where M5 / M8 / M12 Fire**

(Re-states what `RESEARCH-SECURITY.md` §7.3 already says, in the workflow context.)

- **M5 multi-source corroboration:** before locking a control parameter, verify at least two independent authoritative sources support the parameter. Recorded in research-log + cross-referenced in Stage 3 plan output.
- **M12 independence verification:** corroborating sources must be from different organizations per `source-org-mapping.json`. Two NIST documents don't satisfy M5. NIST + ISO crosswalk + CIS overlay can (three independent organizations).
- **M8 human verification:** at control-lock time, the framework surfaces a verification summary; commit cannot proceed without explicit approval recorded in `.tgf/state/m8-approvals/`. Workstream 1's Stop hook + git pre-commit enforce this mechanically.
- **M9 memory-alignment flag:** if AI prior knowledge confirms the cited content, that's one source of evidence, not two — corroboration discipline still applies.

**New sub-section: §3 Stage 3 — Checklist**

For each rule or control locked in:

- [ ] Primary citation chain complete: rule → existing standard → NIST 800-53 control ID(s) → NIST CSF 2.0 Subcategory(ies)
- [ ] OWASP ASVS-to-800-53 mapping document consulted (not Claude-invented)
- [ ] CSF 2.0 Informative References consulted for ISO 27002 cross-reference (where included)
- [ ] M5 multi-source corroboration: at least two independent sources from research-log
- [ ] M12 independence verified: corroborating sources are from different organizations
- [ ] M9 memory-alignment flagged honestly: AI prior knowledge does NOT count as independent
- [ ] M18 exception clauses scanned: any "X is required except when…" patterns explicitly reviewed
- [ ] M8 human approval recorded for control-locking parameter values
- [ ] Existing-pattern check: does this rule align with how other skills handle similar concerns, or is it introducing a new approach?
- [ ] Stage 5 Phase 2 (Security Audit) preview: would the security-auditor agent be likely to flag this?

### §5.4 Stages 4, 5, 6 — minimal changes

Stages 4 (Implement), 5 (Four-Pass Review), and 6 (Commit) do not gain new methodology sub-sections — they remain operational and are already well-grounded in the existing WORKFLOW.md §3 + §4 + §5.

Minor edits only:

- **Stage 4** — add a one-line cross-reference: "Stage 3's citation chain travels with the implementation; each cited rule's chain is preserved in skill content."
- **Stage 5 Phase 2 (Security Audit)** within §3 — add a one-line cross-reference: "The Security Auditor agent (WS3) applies the NIST 800-53 + CSF 2.0 mappings produced at Stage 3 as part of its review."
- **Stage 5 Phase 4 (Holistic Review)** within §3 — add a one-line cross-reference: "The Holistic Reviewer agent (WS3) verifies the Stage 1 research-log → §2 Sources traceability and the Stage 3 citation chain completeness."
- **Stage 6** — no change.

---

## §6 Cross-Cutting Additions to WORKFLOW.md

### §6.1 New §2.5 (or expand §2): Source-Tier Hierarchy

New sub-section in §2 Conceptual Model that formalizes what currently lives implicitly in `RESEARCH-SECURITY.md` §4.4 and `research-security-implementation-plan.md` §4.1:

- **Tier 1 — Must Live-Fetch Every Use.** Living documents: OWASP Cheat Sheets, ASVS chapters, Top 10 (year-specific), vendor documentation, framework documentation, CISA advisories. Citation discipline: §2 Sources entry MUST include "Date Verified" reflecting the most recent fetch. Re-verification cadence per `CLAUDE.md` §14 (quarterly).
- **Tier 2 — Publication-Level Citation Acceptable.** Stable formal publications: NIST SP (with revision), FIPS, IETF RFCs (with number), ISO/IEC standards (with edition), W3C Recommendations (with publication date). Citation discipline: cite at `{document-id} (Revision N, Year)` granularity. Live fetch on first use; subsequent uses cite at publication level without re-fetch.
- **Tier 3 — Comparative / Design-Rationale Only.** Books, papers, blog posts, conference talks. Citation discipline: may appear in design-rationale notes within plan documents; DO NOT appear in §2 Sources tables of skill files (DEC-2026-05-17-004 Clause 6).

### §6.2 New §10 (or expand §9 Reference): Methodology Cross-Reference Table

A single-table summary of which methodology grounds which stage, so adopters and the WS3 agents can locate the authoritative spine quickly:

| Stage | Authoritative methodology | Source IDs in registry |
|-------|---------------------------|------------------------|
| Stage 1 (Research) | Admiralty Code (source reliability × credibility); CIA Structured Analytic Techniques (KAC / QoIC / ACH); NIST SP 800-39 (intelligence-level distinction) | `JOINT-PUB-2-22-3` (Admiralty Code public reference); `CIA-TRADECRAFT-PRIMER`; `NIST-SP-800-39` |
| Stage 2 (Scope) | NIST SP 800-37 Rev 2 Categorize step; NIST SP 800-160 Vol 1 Rev 1 system scoping; Microsoft SDL threat-model scope; STRIDE-per-element at trust boundaries | `NIST-SP-800-37`; `NIST-SP-800-160-V1`; `MS-SDL` |
| Stage 3 (Plan w/ Governance) | NIST SP 800-53 Rev 5 (backbone); NIST CSF 2.0 (cross-cutting); CIS Controls v8.1 (prioritized overlay); ISO/IEC 27002:2022 (international, via crosswalk) | `NIST-SP-800-53`; `NIST-CSF-2-0`; `NIST-CSF-2-0-IR`; `CIS-CONTROLS-V8-1`; `OWASP-ASVS-MAPPING-800-53` |
| Stage 4 (Implement) | (no new methodology; citation chain travels with implementation) | — |
| Stage 5 (Four-Pass Review) | (WS3's four agents preload domain-specific authoritative materials; see `four-agents-design-notes.md`) | — |
| Stage 6 (Commit) | (no new methodology; commit + log discipline already in `CLAUDE.md` §11 + §13) | — |

### §6.3 Document header and changelog

WORKFLOW.md header gains:

- Version line: `v1.1` (was implicitly v1 from Phase 3 commit `2853047`).
- One-line changelog at the top: "v1.1 (2026-05-23): Authority-backed Stages 1/2/3 against Admiralty Code, NIST RMF Categorize, and NIST 800-53 + CSF 2.0 + CIS v8.1 + ISO 27002 (via crosswalk). Source-tier hierarchy formalized. Citation chain target defined as rule → ASVS → 800-53 → CSF 2.0 Subcategory. (Workstream 2.)"

No file-rename, no separate WORKFLOW-V2.md (per Approach Decision A).

---

## §7 CLAUDE.md Updates

Minimal — per Approach Decision H. Two specific touches:

1. **`CLAUDE.md` §3 Stage 1, Stage 2, Stage 3 paragraphs** — add a single cross-reference sentence at the end of each: "WORKFLOW.md §3 specifies the authoritative methodology grounding this stage." No contract change; just a pointer.
2. **`CLAUDE.md` §1 "Authoritative sources only" sub-section** — add a sentence: "This discipline applies to the workflow itself: per-stage methodology cited in WORKFLOW.md §3."

`templates/CLAUDE.md.template` mirrors the same two edits for adopter coherence.

No other framework artifact changes (`ARCHITECTURE.md`, `DECISIONS.md`) unless an unforeseen architectural decision emerges during build — in which case a new ADR is authored, not silent change.

---

## §8 Worked Example: `security-input-validation` Rule 5.1 — Full Citation Chain

Per Approach Decision K, the methodology validation is one worked example end-to-end. Existing rule:

```
skills/security-input-validation/ Rule 5.1 — Validate Input at Trust Boundaries
  Cited at present: OWASP ASVS V2.2.2 + OWASP Top 10:2025 A05 + CWE-20
```

WORKFLOW-V2 extension produces:

```
Rule 5.1 — Validate Input at Trust Boundaries
  → OWASP ASVS 5.0 V2.2.2 (existing)
  → OWASP Top 10:2025 A05 (existing)
  → CWE-20 (existing)
  → NIST SP 800-53 Rev 5 SI-10 (Information Input Validation)         [new — via OWASP-ASVS-MAPPING-800-53]
  → NIST SP 800-53 Rev 5 SI-15 (Information Output Filtering)         [new — via OWASP-ASVS-MAPPING-800-53]
  → NIST CSF 2.0 PR.PS-06 (data integrity)                            [new — per-skill cross-cutting]
  → NIST CSF 2.0 PR.IR-01 (network communications integrity)          [new — per-skill cross-cutting]
  → ISO/IEC 27002:2022 8.26 (Application security requirements)       [new — via NIST-CSF-2-0-IR crosswalk]
  → CIS Controls v8.1 — Control 16 (Application Software Security)    [new — prioritized overlay]
```

The example commits as part of Build Step 4 (worked-example commit). It is **not** a retroactive update to `skills/security-input-validation/SKILL.md` content — the existing rule text stays; the chain extension appears in the WORKFLOW-V2 amendment as an illustrative case under §3 Stage 3 — Citation Chain Target. Retroactive update to the actual skill file is WS4/WS5 territory.

If the worked example exposes a methodology gap (e.g., the OWASP mapping document maps ASVS V2.2.2 to a control we wouldn't have predicted, suggesting our reading is wrong), we surface that as a finding and amend the plan rather than push through.

---

## §9 Build Sequence

Three or four commits per Approach Decision I. Check-ins with Alt between each commit.

### Build Step 1 — Source Registry Expansion (Commit 1/3)

**Goal:** every URL Workstream 2 will fetch is registered + URL-allowlisted + has a schema, BEFORE any Stage 1 fetch.

**Subtasks:**

1. Draft 12 new entries for `source-registry.json` per §4.1.
2. Define 8 new schemas in `.tgf/state/source-schemas/` per §4.2.
3. Add 4 new publishers to `source-org-mapping.json` per §4.3.
4. Direct invocation test for each URL pattern via `python .claude/hooks/lib/source_registry.py --check-url ...`. Every pattern must resolve.
5. Run `tests/research-security-smoke-test.sh` to verify no existing test broke.
6. Commit message per [[feedback-commit-message-style]] — draft, show Alt, then commit.

**No Stage 1 fetches in this commit.** Pure registry work. This is what unblocks the actual research in Step 2.

**Check-in with Alt at end of Step 1** before any WebFetch. Confirm registry shape, schemas, org-mapping additions.

### Build Step 2 — Stage 1 Research Fetches (No commit on its own; feeds into Step 3)

**Goal:** fetch the 12 new sources, let M1–M19 hooks pin baselines + verify content.

**Subtasks:**

1. Sequentially WebFetch each Tier-2 NIST source (800-37, 800-53, 800-160, 800-39, CSF 2.0, CSF 2.0 Informative References). Each fetch runs through full hook pipeline; expect `verified` status on first fetch (cold start = M11 no_baseline + M13 skipped, both benign per RESEARCH-SECURITY.md §10.3).
2. Sequentially WebFetch each Tier-1 OWASP mapping + CIS + MITRE source.
3. Tier-3 sources (Microsoft SDL, CIA Tradecraft Primer, Joint Pub 2-22.3) — fetched but classified as design-rationale; they appear in WORKFLOW.md cross-reference table, NOT in any skill §2 Sources table.
4. Each fetch's research-log entry confirmed `verified`. Any `flagged` fetch pauses for review; do not push through without understanding the finding.

If a fetch produces an unexpected flag (M3 schema mismatch, M4 pattern match, M18 exception clause, M19 hidden HTML), **pause and assess** before continuing. The finding may reveal:
- A registry pattern bug (registered URL hits an aggregator page, not the expected document) — fix registry, re-fetch.
- A schema too strict for the actual document shape — relax schema, re-fetch.
- A legitimate concern in the source content — escalate to human review.

### Build Step 3 — WORKFLOW.md Amendment (Commit 2/3)

**Goal:** WORKFLOW.md v1.1 lands with all §5 + §6 changes.

**Subtasks:**

1. Edit WORKFLOW.md per §5.1, §5.2, §5.3, §5.4 (per-stage amendments).
2. Edit WORKFLOW.md per §6.1 (source-tier hierarchy in §2.5 or expanded §2), §6.2 (cross-reference table in §10 or expanded §9), §6.3 (header + changelog).
3. Cite every newly-introduced source via the rule-level citation discipline (e.g., "NIST SP 800-37 Rev 2 §3.1.1" not "NIST SP 800-37 says…"). This will trigger PreToolUse-Write traceability check on the edit — every citation MUST appear in a research-log `verified` entry from Step 2.
4. Re-run `tests/research-security-smoke-test.sh` to verify no regression.
5. Commit message per [[feedback-commit-message-style]] — draft, show Alt, then commit.

**Check-in with Alt at end of Step 3** before worked-example commit. Confirm amendment readability + structural soundness.

### Build Step 4 — Worked Example + CLAUDE.md Cross-References + Closeout (Commit 3/3)

**Goal:** validate the methodology end-to-end, mirror the spec change into CLAUDE.md, update framework-hardening-plan §3.2 status.

**Subtasks:**

1. Add §8 worked example into WORKFLOW.md as a new sub-section under §3 Stage 3 — Citation Chain Target.
2. Apply §7 CLAUDE.md edits (2 small cross-references + 1 sub-section sentence).
3. Mirror those CLAUDE.md edits into `templates/CLAUDE.md.template`.
4. Update `docs/framework-hardening-plan.md` §3.2 status: `⏳ NEXT` → `✅ COMPLETED + PUSHED` (after the actual push, naturally; the commit lands the status doc edit pre-push).
5. Update `docs/ROADMAP.md` if any milestone shifts (likely no shift — Workstream 2 was already on the post-WS1 sequence).
6. Update memory: `project_tgf_build_phases.md` Workstream 2 status; `MEMORY.md` index line if needed.
7. Generate `.sessions/2026-05-DD-session-NN-workstream-2-workflow-v2.md` capturing the build.
8. Run final orchestrator-played four-pass review (until WS3 agents exist) on the full amendment.
9. Commit message per [[feedback-commit-message-style]] — draft, show Alt, then commit.

### Optional Build Step 5 — push decision

After Commit 3/3 lands, Alt's call whether to push immediately (alongside the previously-held `a8b908e` and the new commits) or batch with the next workstream.

---

## §10 Validation Strategy

Two layers — mechanical and review.

### §10.1 Mechanical validation

- **Registry expansion (Step 1):** every URL pattern verified via direct registry-lookup test. No fetches succeed if pattern is wrong.
- **Stage 1 fetches (Step 2):** PostToolUse-WebFetch records research-log entry for every fetch; status `verified` required to proceed.
- **WORKFLOW.md amendment (Step 3):** PreToolUse-Write blocks the edit if any newly-introduced citation lacks a research-log `verified` entry. The hook is the mechanical contract.
- **Worked example (Step 4):** same PreToolUse-Write enforcement on the example's citations.
- **Smoke test re-run after Steps 1 and 3:** all 12 T1–T12 must stay green.
- **Pre-commit hook on every commit:** scans staged content for citations, cross-checks against the union of `verified` source IDs across all session research logs (per `lib/git_precommit_check.py`).

### §10.2 Review validation (orchestrator-played four-pass until WS3 lands)

- **Code Review pass:** WORKFLOW.md amendment reads cleanly; sections flow logically; no broken cross-references; no orphaned references to removed content.
- **Security Audit pass:** every cited source traces to a `verified` research-log entry; M5 corroboration evident where parameters are claimed (e.g., "STRIDE-per-element" backed by Microsoft SDL + NIST 800-160); M9 honestly flagged where AI memory likely aligned with sources.
- **Red Team pass:** can a malicious editor sneak a fabricated control ID through? The pre-commit hook should block (no research-log entry). Can a fabricated CSF Subcategory pass? Same answer — its parent document `NIST-CSF-2-0` would be the source-ID, and citation-parser checks for parent-document presence.
- **Holistic Review pass:** does the amendment fit the existing WORKFLOW.md shape? Does the methodology grounding stay surgical or does it bleed into stage redesign? Does the citation chain target preserve forward compatibility with WS3 agents and WS4 audit?

If any pass surfaces a finding that the build itself cannot resolve, pause + Checkpoint 1 amendment.

---

## §11 Checkpoint 1 — Decisions for Alt

Confirm or override each (recommendations carry from §3):

- **A.** Amend WORKFLOW.md in place vs WORKFLOW-V2.md? (Recommend: amend in place.)
- **B.** Stage-gate enforcement: new hooks or rely on WS1 downstream? (Recommend: rely on downstream.)
- **C.** NIST 800-53 mapping retroactive scope: now or defer to WS5? (Recommend: defer.)
- **D.** CSF 2.0 cross-cutting depth: per-rule, per-skill, or per-phase? (Recommend: per-skill.)
- **E.** ISO sources: via crosswalk or skip entirely? (Recommend: via crosswalk per DEC-004 Clause 5.)
- **F.** STRIDE at Stage 2: every change or only trust-boundary-crossing? (Recommend: trust-boundary-only.)
- **G.** Admiralty Code rigor: explicit for all sources or Tier-1 presumed A1? (Recommend: Tier-1 presumed A1 + explicit for Tier-2/3.)
- **H.** CLAUDE.md update: touch or leave alone? (Recommend: small cross-reference addition only.)
- **I.** Commit decomposition: one combined or 3–4 smaller? (Recommend: 3–4 smaller per portfolio framing.)
- **J.** M17 parameter-history wiring: now or defer? (Recommend: defer to WS1 amendment.)
- **K.** Worked example rule: `security-input-validation` Rule 5.1? (Recommend: yes, per design-notes' own sketch.)

Plus three new questions surfaced during plan drafting:

- **L.** Should `NIST-SP-800-53A` (Assessment Procedures, Rev 5) be registered now, or deferred until WS3 needs it for the Security Auditor agent's preload? (Recommend: defer — WS3 dependency.)
- **M.** Should `MITRE-ATT&CK-MOBILE` / `MITRE-ATT&CK-ICS` variants register now, or only `MITRE-ATTACK-ENTERPRISE`? (Recommend: Enterprise only for WS2; Mobile/ICS register when WS3 Red Team agent's persona-build needs them.)
- **N.** Effort budget allocation. Recommend 2–4 sessions of focused work with progress check at end of each commit. Open to Alt's preference for a tighter ceiling or open-ended.

---

## §12 Out of Scope (Deferred to Other Workstreams)

Explicit list of "we identified it, we're not doing it here":

- **Retroactive NIST 800-53 mapping for Phase 4–6 skills.** WS4 audit identifies gaps; WS5 remediates. (Per Decision C.)
- **New Claude Code hooks for explicit Stage 1→2 and Stage 3→4 gates.** Defer to WS1 amendment if downstream enforcement (PreToolUse-Write, Stop, git pre-commit) proves insufficient in practice. (Per Decision B.)
- **`parameter-history.json` (M17) wiring.** WS1 amendment when first triggered. (Per Decision J.)
- **Four review agents implementation.** WS3 builds against WORKFLOW-V2's stages. (Per `framework-hardening-plan.md` §3.3.)
- **Stack-baseline-specific workflow variants** (LabList / AdaptivIQ / BLETRAP). Phase 13 (Stack Baselines) territory.
- **Compliance-skill-specific workflow variants** (HIPAA-mode, PCI-DSS-mode, etc.). Phase 10 (Compliance Skills) territory.
- **Tightening source schemas to per-document strict shape.** WS1's lazy-baseline approach lets schemas tighten over time; new schemas land permissive in WS2.
- **`templates/SKILL.md.template` update to require Stage 3 citation chain.** Defer — wait until WS3 and WS4 inform what the template should require by default. WS2 documents the target; the template change can be a WS5 deliverable or a separate template-update commit.
- **Adopter-facing `/tgf:plan` slash command update** to print the Stage 1/2/3 checklists at invocation. Phase 14 (Slash Commands) territory.
- **Telemetry schema additions** for stage-methodology coverage. Phase 11 (Meta-Skills) consumes; defer.
- **`framework-health` meta-skill** integration to surface "Stage 3 mapping coverage = X%" reports. Phase 11.

---

## §13 Effort Estimate

Realistic range based on the scope above:

- **Best case (2 sessions):** Step 1 + 2 in session 1; Step 3 + 4 in session 2. Assumes no hook gaps surface, no fetches flag, no checkpoint amendments.
- **Expected case (3 sessions):** Step 1 + 2 in session 1; Step 3 in session 2; Step 4 in session 3. Allows one round of plan amendment after fetch findings.
- **Worst case (4 sessions):** above + one session of hook iteration (WS1 amendment) if a fetch reveals a hook gap (e.g., a NIST PDF needs an M3 schema variant the current `nist-sp` schema doesn't handle).

Recommend planning at expected case (3 sessions) with check-in cadence between each commit. Alt's call on accepting open-ended vs imposing a ceiling.

---

## §14 Risks and Gotchas (Surfaced During Plan Drafting)

The non-obvious traps to watch for during build:

1. **WORKFLOW.md is already 911 lines.** Adding 300–500 lines per the amendments pushes toward 1300+ lines. Watch for section bloat; consider whether the per-stage checklists belong in WORKFLOW.md or in a separate `WORKFLOW-CHECKLISTS.md` referenced from WORKFLOW.md. (Lean: keep in WORKFLOW.md for now; spin out only if it impedes readability.)
2. **NIST SP 800-53 Rev 5.1.1 is ~500-page PDF.** Fetching the full document blows token budget. Strategy: cite the canonical PDF for traceability but extract control text from NIST CSRC's HTML control-family browser pages (smaller, targeted). The OWASP-ASVS-MAPPING-800-53 document is the actual translation tool — most of the time we don't need to read 800-53 text directly, we use the mapping.
3. **CSF 2.0 Informative References tool is dynamic.** It's served via a NIST web tool, not as a static document. Schema for `NIST-CSF-2-0-IR` must accept dynamic content shape. Live-fetch every use (Tier 1 behavior even though it's a NIST source — because the tool's output can change as new framework versions get cross-referenced).
4. **NATO STANAG 2022 itself is not reliably public.** Plan routes around this via US Army FM 2-22.3 / Joint Pub 2-0 as public canonical reference for the Admiralty Code. If even those URLs prove unreliable, fallback is to cite the Admiralty Code as a "well-known intelligence community framework" with the unclassified-doctrine reference, accepting that the canonical NATO document itself is not directly accessible.
5. **CIA *Tradecraft Primer* (2009 declassified) URL stability.** CIA.gov has reorganized PDF locations historically. If the canonical URL breaks during WS2 build, search for the current location and update the registry pattern; don't fall back to an unofficial mirror (M11 drift risk).
6. **OWASP ASVS `Mapping/` folder structure may evolve.** The ASVS repo is active; the mapping file location could change between ASVS 5.0 and a future 5.1. Register the URL pattern carefully and pin against current state; re-verify if ASVS itself ships a new revision.
7. **The pre-commit hook will be slow on the WORKFLOW.md amendment commit.** That commit will introduce many new citations all at once; the hook scans every staged file's citations. Acceptable but expect a delay; don't bypass with `TGF_PRECOMMIT_BYPASS` unless something is genuinely broken.
8. **M9 self-trap.** Workstream 2 itself is the kind of work most likely to surface M9 violations — NIST 800-53 and CSF are heavily in AI training data. Every parameter or mapping claim during build needs explicit "fetched source" provenance, not "I know this is how it works." If a check during build feels like "I know this already," that's the M9 alarm.
9. **Risk of methodology bleeding into stage redesign.** The amendment should ground existing stages, not redesign them. If during build it starts to feel like "we should restructure Stage 3 around 800-53 families," pause — that's scope creep. The six stages are validated; WS3 depends on them.
10. **`templates/CLAUDE.md.template` divergence.** If CLAUDE.md gets §3 cross-reference edits, the template needs the same edits. Easy to forget on the commit-3 closeout. Build the template update into Step 4's checklist explicitly (done above).
11. **Source-org-mapping completeness.** Adding new publishers (CIS / DoD-Joint-Staff / CIA / Microsoft) means M12 independence checks gain expressive power. But if a future skill cites two CIS documents thinking they're independent (different docs, same org), M12 would correctly flag — make sure the mapping correctly groups all CIS source IDs under the CIS publisher.
12. **The "Admiralty Code is overkill for our sources" tension.** Honestly: most of our Stage 1 sources are uniformly A1, and Admiralty Code's discriminative value is mostly at the Tier-2/3 boundary. Document this honestly in WORKFLOW.md §3 Stage 1 — Authoritative Methodology, rather than pretending the grading is rigorous discrimination. Mention that the practical use is "explicit grading required for any non-Tier-1 source."

---

## §15 Commit Discipline Note

Per [[feedback-commit-message-style]]:

- TGF commits land on Alt's LabList portfolio as DEV work.
- Commit messages authored in Alt's voice — direct, slightly informal where natural, no hype or marketing-speak, describes the actual deliverable.
- Subject lines: action-oriented, plain language (not catalog-style "Workstream 2: foo (bar)" labels).
- Body: cover what was built, what the moving parts are, what the design choices were, what's intentionally NOT in scope. Reader understands the change without opening the diff.
- **Workflow:** draft commit message, show Alt before `git commit`, take feedback, then commit. Do not commit-and-ask-forgiveness.
- Trailer: keep `Co-Authored-By: Claude <noreply@anthropic.com>` per [[feedback-commit-attribution]] for TGF.

This applies to all 3 (or 4) commits in the Workstream 2 build sequence.

---

## §16 Cross-References

- `docs/workflow-v2-design-notes.md` — Workstream 2 design notes (the starting input this plan iterates on)
- `docs/framework-hardening-plan.md` §3.2 — Workstream 2 in the master orchestration
- `docs/WORKFLOW.md` — the document this plan amends
- `docs/RESEARCH-SECURITY.md` — Workstream 1 design (the hook surface WS2 depends on)
- `docs/research-security-implementation-plan.md` — Workstream 1 implementation plan (preserved as historical record; references for M-helper semantics)
- `docs/four-agents-design-notes.md` — Workstream 3 starting input (consumes WORKFLOW-V2's stages)
- `CLAUDE.md` §1 (Authoritative sources only), §3 (Workflow), §11 (Findings and Logging)
- `DECISIONS.md` `DEC-2026-05-17-004` (citation chain six clauses — Clause 5 on paywalled sources), `DEC-2026-05-17-005` + `DEC-2026-05-19-009` (hook taxonomy + plugin layout), `DEC-2026-05-19-006` (TGF session state), `DEC-2026-05-19-007` (plugin + orchestrator agent), `DEC-2026-05-19-008` (skill catalog consolidation), `DEC-2026-05-20-010` (security-guidance plugin disable)
- NIST SP 800-37 Rev 2 — https://csrc.nist.gov/pubs/sp/800/37/r2/final
- NIST SP 800-53 Rev 5.1.1 — https://csrc.nist.gov/pubs/sp/800/53/r5/upd1/final
- NIST SP 800-160 Vol 1 Rev 1 — https://csrc.nist.gov/pubs/sp/800/160/v1/r1/final
- NIST SP 800-39 — https://csrc.nist.gov/pubs/sp/800/39/final
- NIST CSF 2.0 — https://www.nist.gov/cyberframework
- NIST CSF 2.0 Informative References — https://www.nist.gov/informative-references
- OWASP ASVS 5.0 (mapping folder) — https://github.com/OWASP/ASVS/tree/master/5.0/mappings
- CIS Controls v8.1 — https://www.cisecurity.org/controls/v8-1
- MITRE ATT&CK — https://attack.mitre.org/
- MITRE ATLAS — https://atlas.mitre.org/
- Microsoft SDL — https://www.microsoft.com/en-us/securityengineering/sdl/
- CIA *A Tradecraft Primer* (2009 declassified) — search cia.gov for current PDF location
- US Army FM 2-22.3 / Joint Pub 2-0 (Admiralty Code public reference) — armypubs.army.mil / jcs.mil

---

**Status note:** plan v1 drafted 2026-05-23 in fresh session under WS1 hook protection. Awaits Checkpoint 1 approval on §3 Approach Decisions + §11 confirmation items. Plan amendments expected per Phase 4/5 precedent — captured in commit messages + session log on the actual build commits.
