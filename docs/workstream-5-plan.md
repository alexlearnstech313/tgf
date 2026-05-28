# Workstream 5 — Remediation Plan (v1)

> **Status:** v1 DRAFT, written 2026-05-28 at WS4 closeout. **Not yet cleared for implementation** — WS5 begins after a Checkpoint-1 approval per the phase-plan workflow (write plan → checkpoint → implement). This document consolidates the WS4 audit backlog (`docs/workstream-5-plan-backlog.md` §3.1–§3.19 + §4 cross-target patterns) into sequenced, leverage-ordered work-packages. The backlog remains the authoritative per-finding record; this plan is the execution structure over it.
>
> **Source of findings:** the 19-target retroactive audit (WS4, Build Steps 2–6). Critical/High findings live in `ERROR-LOG.md` (visible-now backlog); Medium/Low in the backlog doc. Per-dispatch transcripts (all findings regardless of routing) at `.tgf/state/agent-activity/<role>/` (gitignored, Decision I).

---

## §1 Scope and Boundary

**WS5 = remediation of WS4 findings.** WS4 was audit-only (find + report, never fix — a structural, non-negotiable boundary). WS5 is where the fixing happens. After WS5, Phase 6 resumes from commit 5/12.

**In scope:** the 9 open High ERROR-LOG entries traceable to WS4 + the WS3-discovery entries (ERR-001/003/004/006), the consolidated framework-wide Medium/Low work-packages below, and the per-skill/per-doc accuracy fixes.

**Out of scope (deferred to Phase 11/12):** the executable enforcement hooks themselves (tier-floor, review-evidence, hard-refusal-invariant matcher, dispatch-floor, the §2-traceability fitness function, tamper-evidence manifest). WS5 *specifies* and *documents* these gaps and writes the remediation where it's a content/spec fix; the hook *implementation* is Phase 12 enforcement-floor work. WP7 is the boundary line — read its note carefully.

**Sequencing principle:** leverage-ordered. Do the fix-once-apply-many mechanical sweeps and the bounded preload fix first (cheap, high-coverage, low-risk), then per-target accuracy, then the High-severity content remediation, then hand the enforcement-hook specs to Phase 12.

---

## §2 Work-Packages

### WP1 — §9 preload-accuracy fix (7 skills, one root cause) — **cheap, do first**

One cross-cutting commit. Root cause: skills written before/independent of the WS3 agent wiring (2026-05-25).

- **Add** the always-on `tgf-orchestrator` preload to the §9 "Preloaded by" line of: `continuity`, `security-core`, `code-quality` (they name only review subagents).
- **Correct** the false "Preloaded by: None directly" / "does not preload the full skill" in: `design`, `project-management`, `debugging`, `disagreement` (holistic-reviewer.md actually preloads all four).
- Authority for the correct matrix: CLAUDE.md §6 + ARCHITECTURE §20 + WORKFLOW.md §4 (the 3-part preload authority). Verified agent×skill matrix is in the backlog §3.17 ⭐ note + Build Step 5 closeout.
- Subsumes F-HR-PM-01, F-HR-CONT-01, F-HR-SC-01, F-HR-CQ-01.

### WP2 — docs/-path-rot systemic sweep — **cheap, mechanical, do first**

One repo-wide path-correction. 3 of 5 foundational docs over-extend the `docs/` prefix to root-resident governance artifacts (DECISIONS/ROADMAP/ERROR-LOG/VENDOR-LOG/WAIVER-LOG live at repo ROOT).

- CLAUDE.md §7/§11 — all 5 root artifacts (F-HR-CLAUDE-01).
- ARCHITECTURE.md L94 — docs/DECISIONS.md (F-CR-ARCH-01).
- RESEARCH-SECURITY.md L3 + L542 — docs/DECISIONS.md (F-CR-RS-06 / F-HR-RS-02).
- Convention to normalize to: bare names for prose mentions; `docs/` prefix only for files that actually live in docs/ (ARCHITECTURE.md, WORKFLOW.md, SKILL-INDEX.md, RESEARCH-SECURITY.md). WORKFLOW.md is the correct exemplar (18 bare-correct refs, zero rot).

### WP3 — GFM anchor-slug lint — **mechanical, build once**

Every Phase 5 target had anchor-slug mismatches across punctuation variants (commas/parens/`+`/slashes/em-dashes/word-drops). Build a deterministic GFM-slug linter and run it across all skills + docs; fix the mismatches it surfaces. Reusable beyond WS5 (CI candidate).

### WP4 — framework-level source-registry pass — **one pass, closes many**

Register the cited-but-unregistered authorities + reconcile counts.

- **Register:** WCAG (cited by testing+design+ui-craft), TOYODA-5W (debugging+others), PMBOK, IIBA-BABOK, Apple-HIG, Material-3, ANTHROPIC-AGENTS, plus CIS Controls v8.1 + Microsoft (both now load-bearing — surfaced Target 19).
- **Governance decision required:** disposition for *unfetchable-by-reference* sources (SPA-rendered HIG/Material-3, paywalled PMBOK/BABOK, 403-ing ISTQB) — a reference-only registry tier vs a documented never-register category. This is a real decision, not a mechanical fix; surface to the stakeholder.
- **Reconcile** the as-built counts the docs cite (RESEARCH-SECURITY §5.1: 29→44 sources, 8→15 schemas, 5→7 orgs) — fold into WP6.
- Note: NIST-SP-800-218 is registered but its `cited_in` reverse index omits testing — fix.

### WP5 — citation-correctness pass — **deterministic where possible**

- NIST SSDF practice errors: continuity PO.5→PO.3; security-core §2-inflation of NIST-SSDF/ATT&CK/ATLAS; code-quality ISO-5055 orphaned.
- Cross-skill wrong-rule citations in example dialogues (disagreement/testing/discovery; 5+ instances).
- §7-OWASP-LLM-cited-but-not-in-§2 standardization (6 Phase 5 skills + all 3 always-on) — a skill-template §2-table completeness rule.
- Phase 6 skill-to-DEC trace gap (n=4): DEC-2026-05-26-011 asks future skills to reference it; none of the 4 audited do. Capture as a skill-template requirement.

### WP6 — foundational-doc + per-skill documentation-accuracy fixes — **per-target**

Content/accuracy fixes that don't need a hook. Grouped by doc:
- **RESEARCH-SECURITY.md:** stale as-built inventory (refresh to 44/15/7 incl. CIS+Microsoft + note Microsoft's vendor tier, or point to live state); M6/M10 defense-in-theater (disclaim like M17, or move to §8); §7.5 "agent preloads RESEARCH-SECURITY.md" claim reworded (it's prose, not `skills:`); hook-layout DEC-009 drift note; script-name reconciliation (§8.3/§10.4 → underscore names); the "11 of 19" count fix; citation-indexes/ inventory row; the §5.5 `[y/N]` artifact-presence clarification.
- **ARCHITECTURE.md:** §17 M9 cross-reference (closes F-SA-ARCH-02); §21 agent-memory path correction (F-CR-ARCH-02/DEC-007 Cl.9); §20 maturity caveat (F-SA-ARCH-01, gated on ERR-002); §17 M9-layer note; §18 PostToolUse-cannot-block precision; §20 "seven roles" build-state caveat; the /tgf:review-evolution + DESIGN-RATIONALE.md dangling refs.
- **DECISIONS.md:** CP-8 forward-amendment notes on DEC-003 + DEC-005 (F-HR-DEC-01); fix the fabricated ERR-2026-05-26-005 → ERR-2026-05-27-005 (F-HR-DEC-02); DEC-010 four-pass-maturity caveat (F-SA-DEC-01, gated on ERR-002); DEC-003 Alternatives section; DEC-011 "Downstream consequences" → "Consequences" header; the NNN-convention decision (WP10).
- **CLAUDE.md:** §7/§11 path rot (WP2).
- Per-skill Phase 6 bug fixes: pydantic v1/v2 mix (F-CR-IV-01); Jinja2 `e(quote=True)` (F-CR-OE-01); RFC 4180 misattribution (F-CR-OE-02); + the rule-completeness extensions (DOMPurify config, identifier allow-list, mixed-context emission, LLM channel, schema-library coercion, Unicode homoglyph, parser-stage hardening, state-machine bypass).

### WP7 — High-severity content remediation + enforcement-hook SPECS — **the heavy package; Phase-12 boundary**

The 9 open High ERROR-LOG entries. Split by what WS5 can close vs what Phase 12 must build:

- **WS5 can close (content/spec):**
  - ERR-003 (citation-chain depth in security-cryptography) — re-do the citations to depth.
  - ERR-006 (fail-closed behavior spec, Apple goto-fail class) — add the spec to the Phase 6 security skills.
  - ERR-008 / ERR-009 (adversary-aware error semantics — deliberately-triggered exceptions + slow-rate probing) — extend security-error-handling Rule 5.1/5.5 threat models.
  - ERR-001 (inline-comment discipline), ERR-004 (adversarial-citation gaps) — content fixes.
- **Phase 12 must build (the enforcement floor — WS5 writes the SPEC + the §-doc reconciliation, Phase 12 writes the hook):**
  - ERR-010 (hard-refusal invariant matcher — invariant-not-named-instances), ERR-011 (bounded + logged acknowledgment gate), ERR-012 (review-evidence commit gate), ERR-013 (tier-floor validation vs diff), ERR-014 (dispatch-floor + the consolidated §18/§20 gate spec).
  - ERR-005 (the §2-Sources-traceability executable fitness function — the n=4 100%-reproduction pattern; highest leverage).
  - **NEW from Target 19 (no ERR — both finders rated Medium; #1 WS5 triage-elevation candidate):** the `skills/**`-only enforcement perimeter (F-RT-RS-01) — decide to broaden the PreToolUse-Write/pre-commit citation check to `docs/**`/`agents/**`/`CLAUDE.md`, OR document the boundary in RESEARCH-SECURITY §1 as accepted residual. Plus the §8.4 SessionStart-integrity overstatement, the 3-path pre-commit fail-open, and the Layer-1-fail-open-on-malformed-stdin (F-RT-RS-02/03/04 — tamper-evidence manifest is the Phase-12 fix).
  - The M8 control-locking gate is the SHIPPED, PROVEN template for all of the above — extend it, don't reinvent.

### WP8 — DECISIONS.md invariant/convention captures — **lightweight, capture**

- The 5.x rule-numbering namespace reused by every skill, disambiguated only by an unenforced skill-name prefix — capture as a DEC invariant or a skill-template rule (flagged Phase-11).
- NNN ID convention: practiced as global-monotonic but continuity Rule 5.2 says within-day — align Rule 5.2 to practice (preferred: leaves the ~11 widely-cited IDs untouched).
- The 6 implicit Phase 6 conventions (Defense-Option anchors, forward-reference phase attribution, uniform refresh date, TGF-synthesis-as-cited-authority, §2 adjacent-scope inclusion) — DEC entries vs phase-plan-level capture.

---

## §3 Sequencing

1. **Wave A (mechanical, fix-once):** WP1 (§9 preload), WP2 (path-rot sweep), WP3 (anchor-slug lint), WP4 (source-registry pass). Low-risk, high-coverage, mostly deterministic. One commit each.
2. **Wave B (accuracy):** WP5 (citations), WP6 (doc + per-skill content), WP8 (convention captures). Per-target commits.
3. **Wave C (High content remediation):** WP7's WS5-closeable half (ERR-003/006/008/009/001/004). Per-skill remediation commits.
4. **Hand-off to Phase 12:** WP7's enforcement-floor specs (ERR-010..014, ERR-005, the Target-19 perimeter + tamper-evidence). WS5 produces the specs + the §-doc reconciliation; Phase 12 builds the hooks against the M8 template.
5. **Then:** Phase 6 resumes from commit 5/12.

**Governance decisions needed before/during WS5 (surface to stakeholder):** (a) the unfetchable-by-reference source disposition (WP4); (b) the `skills/**`-only perimeter — broaden vs document-as-residual (WP7); (c) the NNN convention direction (WP8); (d) whether the four-pass-maturity caveat closes now or waits on ERR-002 platform validation (WP6).

---

## §4 Definition of Done

- All 9 open WS4-High ERROR-LOG entries either CLOSED (content fix) or converted to a Phase-12 hook SPEC with the §-doc reconciliation done + the ERR re-pointed to the Phase-12 owner.
- Wave-A mechanical sweeps applied framework-wide + (where built) the lints committed as reusable CI candidates.
- Every Medium/Low in the backlog either fixed, or formally waived in WAIVER-LOG with rationale + revisit date, or escalated to VENDOR-LOG — no silent drops (CLAUDE.md §11 resolution rule).
- ROADMAP + framework-hardening-plan updated; Phase 6 commit 5/12 unblocked.

---

## §5 Cross-References

- `docs/workstream-5-plan-backlog.md` — authoritative per-finding record (§3.1–§3.19 per-target; §4 cross-target patterns; Build Step 2–6 closeouts; WS4 closeout synthesis).
- `ERROR-LOG.md` — the open High/Medium findings (visible-now backlog).
- `docs/framework-hardening-plan.md` §3.5 — the WS5 workstream spec this plan implements.
- `.tgf/state/agent-activity/<role>/` — full dispatch transcripts (gitignored, Decision I).
- `DECISIONS.md` DEC-2026-05-26-011 (§2 Sources discipline), DEC-2026-05-19-007 (preload mechanism + agent-memory), DEC-2026-05-19-009 (plugin hook layout).
