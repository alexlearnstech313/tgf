# Workstream 4 Plan — Audit of Existing Work

> **Workstream:** WS4 (per `docs/framework-hardening-plan.md` §3.4)
>
> **Status:** ⏳ Plan v1 — pending Checkpoint 1 clearance
>
> **Scope:** apply the now-operational discipline (research-security infrastructure from WS1, WORKFLOW-V2 standards from WS2, four review agents from WS3) to all framework work landed BEFORE the discipline was operational. Identify gaps; produce remediation list → WS5 backlog. Does NOT remediate (that's WS5).

---

## §1 Purpose

The framework was built incrementally between Phase 1 (2026-05-17) and Phase 6 commit 4/12 (2026-05-22). The discipline that the framework now embodies — research-security hooks, WORKFLOW-V2 authority-backed methodology, four-pass review via operational agents — landed AFTER most of that work. The bootstrap problem the framework-hardening detour exists to address is that the existing artifacts were built under the discipline being constructed, not the discipline as operational.

WS4 closes that gap. Dispatch the now-operational four review agents (per WS3) against every framework artifact that shipped before the agents existed. Apply DEC-2026-05-26-011 §2 Sources discipline retroactively. Surface findings as WS5 backlog. After WS4+WS5, Phase 6 resumes at commit 5/12 with a clean baseline under unified discipline.

WS4 is itself audit, NOT remediation. WS4 produces findings; WS5 remediates them. Conflating the two would either bloat WS4 indefinitely or short-circuit findings into rushed fixes. The boundary is structural.

## §2 Prerequisites

All three predecessor workstreams operational:

- **WS1** ✅ (research-security infrastructure — M1-M19 hooks + source registry + research-log capture). WS4 dispatches that need WebFetch go through M15 allow-list gating and M3-M19 post-fetch scanning. The infrastructure that the audit checks against is itself in place.
- **WS2** ✅ (WORKFLOW-V2 methodology grounding). Stage 1/2/3 methodology is the standard the audit evaluates each artifact against.
- **WS3** ✅ (four review agents operational). The agents (`code-reviewer`, `security-auditor`, `red-team`, `holistic-reviewer`) are the audit instrument. ERR-2026-05-25-002 tracks the platform-level `tools:` restriction validation owed under TGF-as-installed-plugin; Decision B below addresses how WS4 handles this.

Plus:

- **DEC-2026-05-26-011** §2 Sources discipline rules captured in `DECISIONS.md`. WS4 applies these retroactively as part of the mechanical-compliance audit track.
- **`ERROR-LOG.md` starting backlog:** ERR-001 through ERR-004 from WS3 smoke tests already populate the backlog for `73d025d` (`security-cryptography` — Phase 6 commit 4/12). WS4 extends this rather than starting fresh.

## §3 Approach Decisions (Meta — Resolve at Checkpoint 1)

Eleven decisions to resolve. Each has a recommendation; Alt's role at Checkpoint 1 is to approve, amend, or reject each.

### Decision A — Audit ordering strategy

**Recommendation:** **Sequential per-artifact** in approximately reverse-chronological order (Phase 6 commits 1/12-4/12 first → Phase 5 activity skills → Phase 4 always-on skills → foundational docs). Reverse chronological because the most recent work has the freshest context, the most-applied discipline, and the highest-stakes coverage gaps (Phase 6 security skills). Each artifact audit produces a per-artifact commit with findings routed per Decision D.

**Alternative considered:** Domain audit across artifacts (e.g., all skills audited for §2 Sources discipline at once, then all skills audited for citation-chain depth at once). Rejected for primary use — it complicates the per-artifact commit boundary and harder to scope. Domain-pattern observations naturally emerge from the sequential dispatch transcripts; the holistic-reviewer's synthesizer role surfaces them in late dispatches.

**Alternative considered:** Validate methodology on one artifact (e.g., Phase 6 commit 1/12 `security-input-validation`), assess output quality, then proceed with the rest. Worth doing as part of the first audit; not separately decided here.

### Decision B — Dispatch mechanism: TGF-as-installed-plugin vs general-purpose proxy

**Recommendation (original):** Install TGF as a Claude Code plugin first so dispatches run under real platform-level `tools:` restriction. This closes ERR-2026-05-25-002 (the platform-level validation gap that WS3 smoke tests deliberately deferred). The audit findings will be more faithful, and the platform-restriction validation gets done as a side-effect of WS4 work rather than as a separate ticket.

**Alternative considered:** Continue via `general-purpose` agent proxy (same pattern as WS3 smoke tests). Initially rejected — WS4 is the audit pass, the quality of findings is what determines WS5 backlog quality, and persona-level-only validation is a known gap.

**Checkpoint 1 amendment (2026-05-26):** Original rejection overridden. **WS4 uses `general-purpose` agent proxy throughout** (same as WS3 smoke tests). Rationale surfaced during Checkpoint 1: TGF is a "half-completed plugin" — `.claude-plugin/plugin.json` + `marketplace.json` stubs exist from Phase 1 scaffolding, but Phase 6 5/12-12/12 + Phase 7 (22 extended security skills) + Phase 8 (10 AI-specific skills) + Phase 9 (7 ops/quality) + Phase 10 (5 compliance) + Phase 11 (5 meta-skills) + Phase 12 (hook library) + Phase 14 (slash commands `/tgf:*`) are all unbuilt. Installing as a v0.1.0 plugin during WS4 would set a precedent of "TGF is installable now" when ~70% of advertised content is missing.

Plugin install + ERR-2026-05-25-002 resolution are properly **Phase 14 work** (Slash Commands + Plugin Integration). WS4 dispatches via proxy; ERR-002 stays open and gets resolved during Phase 14 alongside the slash commands + full plugin polish. This is the more honest separation.

**Consequence on plan:** Build Step 2 (TGF plugin install + smoke verification) is **DROPPED**. Commit count drops from ~21 to ~20. Risk 1 (Plugin install friction) is moot. Self-reference concern (TGF agents reviewing TGF as plugin) is moot. The proxy-dispatch limitation noted in WS3 smoke-test transcripts carries forward to WS4 audit transcripts.

### Decision C — Two-track audit methodology

**Recommendation:** **Audit each artifact along two tracks:**

- **Track 1 — Mechanical compliance.** Tooling-driven verification: §2 Sources traceability (the bidirectional rule from DEC-2026-05-26-011), §2-to-rule-level citation, source-registry resolution, M1-M19 retroactive evaluation where applicable, WORKFLOW-V2 stage compliance. Outputs structured per-artifact mechanical-compliance report.
- **Track 2 — Agent dispatch.** The four review agents dispatched against the artifact (subject to Decision E selective-dispatch). Outputs per-agent findings JSON per the WORKFLOW.md §4 schemas, captured at `.tgf/state/agent-activity/<role>/<dispatch_id>.json`.

Both tracks run per artifact. Findings from both flow into Decision D routing.

**Rationale:** Track 1 catches the failure modes the framework was built to mechanically catch (citation-chain integrity, source verification, schema/pattern/drift). Track 2 catches what mechanical checks can't (craftsmanship, threat-model gaps, integration concerns). Both are needed; running them in parallel per artifact keeps the dispatch boundary clean.

### Decision D — Finding routing (severity-based, ERROR-LOG vs WS5 backlog doc)

**Recommendation:** **Severity-based routing:**

- **Critical / High findings** → ERROR-LOG entry per finding (consistent with current pattern; ERR-001 through ERR-004 are precedents). Immediate visibility in the committed log.
- **Medium / Low findings** → aggregated into `docs/workstream-5-plan-backlog.md` (a new working document) as a structured backlog. Reduces ERROR-LOG noise while preserving all findings for WS5.
- **Activity-log transcripts** capture ALL findings (Critical through Low) regardless of routing. The split is about visibility, not preservation.

**Alternative considered:** All findings to ERROR-LOG. Rejected — would balloon ERROR-LOG with dozens of Low-severity entries, drowning the operational signal.

**Alternative considered:** No ERROR-LOG entries from WS4; all findings to the backlog doc. Rejected — Critical/High findings deserve the visibility of a committed log entry; WS5 may not start immediately and ERROR-LOG is the discoverable surface for "what's known broken."

### Decision E — Per-artifact agent dispatch matrix (selective vs all-four)

**Recommendation:** **All four agents per Phase 6 security skill; selective per other artifacts:**

| Target class | code-reviewer | security-auditor | red-team | holistic-reviewer |
|---|---|---|---|---|
| Phase 6 security skills (commits 1/12-4/12) | ✅ | ✅ | ✅ | ✅ |
| Phase 4 always-on skills (code-quality, security-core, continuity) | ✅ | ✅ for security-core only | ❌ | ✅ |
| Phase 5 activity skills | ✅ | ❌ | ❌ | ✅ |
| Foundational docs (CLAUDE.md, WORKFLOW.md, etc.) | ❌ | ❌ | ❌ | ✅ |

**Rationale:** security-auditor and red-team add the most value on security-relevant content; dispatching them against `skills/discovery/` would produce low-signal noise. Holistic-reviewer applies to every artifact because integration/synthesis is universal. Code-reviewer applies to anything with rule/anti-pattern content. Selective dispatch saves significant dispatch cost without losing finding coverage.

**Recursive-dispatch note (informational):** The dispatch matrix includes cases where an agent audits a skill it preloads — code-reviewer dispatched against `skills/code-quality/`, security-auditor against `skills/security-core/`, holistic-reviewer against `skills/continuity/`. The agent has familiarity with its preloaded content as ground truth; this is acceptable (the persona is read-only; auditing the rules it preloads is focused review, not self-judgment).

### Decision F — Per-artifact commit boundary

**Recommendation:** **One commit per audited artifact.** Each per-artifact audit produces one commit containing: the per-artifact mechanical-compliance report (Track 1) embedded in the commit message, ERROR-LOG entries (Critical/High findings per Decision D), and any updates to `docs/workstream-5-plan-backlog.md` (Medium/Low findings). Activity-log transcripts are gitignored per Decision D of WS3.

**Alternative considered:** One commit per phase audited (e.g., one commit for all Phase 6 skills audited together). Rejected — per-artifact commits give clean per-target review boundaries and let the audit ship incrementally rather than as a batch.

**Alternative considered:** One commit at WS4 close. Rejected — large diff, high risk of merge/rebase complications, no incremental shipping.

**Side note:** The WS4 plan itself (this document) ships as the first commit. The Checkpoint 1 clearance commit follows. Then per-artifact audit commits. Then the WS4 closeout commit (which updates ROADMAP, flips framework-hardening §3.4 status, writes WS5 plan v1 as starting input for WS5). Roughly **2 + 18 + 1 = 21 commits** — substantial, but commits stay small and per-target review remains tractable.

### Decision G — §2 Sources retroactive application rigor

**Recommendation:** **Apply DEC-2026-05-26-011 bidirectional traceability mechanically (Track 1) without re-fetching sources.** Per-artifact audit identifies bidirectional traceability violations (sources in §2 not cited at rule level; rule-level citations not resolving to §2 / source-registry) as findings. **Source re-fetch under M1-M19 hooks is WS5 remediation work**, not WS4 audit work. WS4 surfaces "this needs re-fetch"; WS5 does the re-fetch.

**Rationale:** WS4 is audit, WS5 is remediation. Re-fetching ~50 sources during the audit conflates the two. Mechanical bidirectional check is fast; source re-verification is slow and belongs with the fix.

**Alternative considered:** Full re-fetch under hooks during WS4. Rejected — bloats WS4 scope from "1-2 sessions" to "4-6 sessions" and crowds remediation discipline (re-fetch + re-cite + verify chain is the WS5 unit of work).

### Decision H — Foundational docs audit depth

**Recommendation (original):** Holistic-reviewer-only dispatch, structural-level review, sample-not-full. Foundational docs are large (CLAUDE.md 1073 lines, WORKFLOW.md 911+ lines amended by WS2, ARCHITECTURE.md, DECISIONS.md, RESEARCH-SECURITY.md); holistic-only focused on cross-doc consistency / DEC-2026-05-26-011 application / conceptual-integrity drift / cross-references.

**Alternative considered:** Full audit of foundational docs by all four agents. Initially rejected — disproportionate effort for the value; foundational docs are structurally different from skill files (they're guidance, not executable rules).

**Checkpoint 1 amendment (2026-05-26):** Original rejection overridden. **All four agents dispatched on each foundational doc** (CLAUDE.md, WORKFLOW.md, ARCHITECTURE.md, DECISIONS.md, RESEARCH-SECURITY.md). Holistic-reviewer remains the primary finding-producing dispatch; code-reviewer / security-auditor / red-team add coverage for distinct lenses on prose-heavy content.

**Persona-fit note for prose-heavy dispatch:**

- **code-reviewer on foundational docs** evaluates prose quality, internal consistency, comment-vs-content discipline, naming truthfulness (when docs introduce terminology). Stretches the persona (which was designed for code diffs) but produces findings the holistic synthesizer may miss at the line level.
- **security-auditor on foundational docs** evaluates whether the document correctly describes security expectations against authoritative sources (e.g., does CLAUDE.md §5 universal-critical list match CLAUDE.md §5 / OWASP ASVS / CWE current state?). Real check; novel application.
- **red-team on foundational docs** evaluates adversarial gaps in framework guidance — "if an adversary were trying to subvert TGF discipline by manipulating the framework's own description of itself (e.g., prompt-injecting an adopter's CLAUDE.md fetch), what gaps in the guidance enable that?" Novel and potentially high-value application of the red-team persona.
- **holistic-reviewer** remains the synthesizer per the original recommendation.

Expected output volume per doc: holistic-reviewer findings dominate; other agents produce thinner finding sets but those that surface are differentially valuable (the lens-specific finding the holistic wouldn't surface).

**Consequence on plan:** Foundational-doc dispatches increase from ~5 (holistic-only) to ~20 (4 agents × 5 docs). Total dispatch count rises from ~46 to ~57. Effort estimate adjusted in §11. New Risk 9 (persona-fit on prose-heavy content) added in §12.

### Decision I — Activity-log transcript storage

**Recommendation:** **Same `.tgf/state/agent-activity/<role>/<dispatch_id>.json` pattern as WS3.** Gitignored per Decision D of WS3. Per-dispatch UUID. No structural change from WS3 — the pattern works; reuse it.

### Decision J — WS5 backlog format

**Recommendation:** **Two-document WS5 backlog:**

- **`docs/workstream-5-plan-backlog.md`** (new, created during WS4): structured Medium/Low findings catalog per Decision D, with severity / target artifact / finding ID / remediation hint / priority hint columns. This is the working catalog WS5 attacks.
- **`ERROR-LOG.md`** (extended): Critical/High findings per Decision D, in the same per-entry format as ERR-001 through ERR-004.

WS5's plan will then categorize the backlog into remediation work packages, sequence them, and ship per-skill (or per-cluster) remediation commits.

### Decision K — Per-audit sanity check

**Recommendation:** **No formal per-audit sanity check.** WS3's smoke tests included sanity checks because the agents were brand new and we needed to validate persona discipline. Now the agents are operational and validated. Per-WS4-audit sanity checks add overhead without commensurate validation gain.

**Exception:** the FIRST per-artifact audit (recommend: `skills/security-cryptography/` since it has the most existing ERR entries and is the test case for "does our audit dispatch reproduce the WS3 smoke-test findings reliably") includes a quick comparison: do the agent's findings include the ones WS3 already surfaced (ERR-001 through ERR-004 + F-H04/F-H05)? If not, that's an audit-quality red flag — either the dispatch is misconfigured or the persona drifted. If yes, audit methodology validated; proceed with remaining 17 targets.

## §4 Audit Methodology

### §4.1 Track 1 — Mechanical compliance

For each audited artifact, run these checks programmatically or via scripted inspection:

1. **§2 Sources bidirectional traceability** (per DEC-2026-05-26-011):
   - For each source in `§2 Sources` table / frontmatter `sources:` list → confirm ≥1 rule-level citation in `rules.md` or `anti-patterns.md`
   - For each rule-level citation → confirm resolution in `.tgf/state/source-registry.json`
   - Flag bidirectional gaps as findings

2. **Citation depth verification**:
   - For each rule-level citation → identify cited depth (publication / chapter / section / rule)
   - Cross-reference against `.tgf/state/research-logs/` for verification depth
   - Flag depth-exceeds-verification cases (the `b67765e`-class failure)

3. **Source registry resolution**:
   - For each source ID cited in skill text → confirm `source_id` exists in `source-registry.json`
   - For each URL cited → confirm matches an `allow_url_patterns` entry
   - Flag un-registered sources / un-allow-listed URLs

4. **WORKFLOW-V2 stage compliance** (where applicable):
   - For artifacts that should reflect Stage 1/2/3 methodology (skills with `§8 Workflow Integration`, etc.) → confirm references to the standardized stages
   - Flag pre-WS2-stage references (e.g., references to Admiralty Code / CIA SAT that WS2 dropped)

5. **Verification-status string check**:
   - Flag any `Date Verified` value matching `"by reference"` or `"verified by reference"` (DEC-2026-05-26-011 §2-§3 deprecated)

6. **M9 confirmation-gap signals**:
   - Grep for inline author hedges (`"approximate, verify against the publication"`, `"section numbers from memory"`, `"current as of training cutoff"`, etc.) in rule extended discussions
   - Flag as Medium findings minimum (per Security Auditor §4 rule from R3)

Output: per-artifact `track-1-report` (structured JSON or markdown) embedded in the per-artifact commit message.

### §4.2 Track 2 — Agent dispatch

Per Decision E selective matrix, dispatch the applicable agents against each artifact.

Dispatch input per-agent:
- The artifact's diff (use `git show <commit>` for the original-shipped state of each artifact)
- Track 1 findings as `governance_plan`-equivalent input (so Track 2 doesn't re-surface what Track 1 caught)
- Surrounding artifact context (related skills, related docs)

Dispatch output per-agent:
- `<RoleOutput>` JSON per `docs/WORKFLOW.md` §4
- Captured to `.tgf/state/agent-activity/<role>/<dispatch_id>.json` per Decision I

Findings flow into Decision D severity-based routing.

### §4.3 Cross-target pattern recognition

After all 18 per-artifact audits complete (or sampled at the halfway point), the holistic-reviewer is dispatched in cross-target mode against ALL per-artifact findings catalogues. Input: every per-artifact transcript + the assembled backlog. Output: cross-target patterns (e.g., "comment-discipline AI-smell is present in 6 of 11 skill files; recommend SKILL-FORGE template update as WS5 work-package"). These pattern findings feed into the WS5 plan.

## §5 Audit Target Catalog

| # | Target | Phase | Dispatch matrix | Notes |
|---|---|---|---|---|
| 1 | `skills/security-cryptography/` | Phase 6 (4/12) | All four | **Validation target per Decision K**; expect to reproduce ERR-001 through ERR-004 + F-H04/F-H05 |
| 2 | `skills/security-error-handling/` | Phase 6 (3/12) | All four | Foundation skill (doesn't extend single SECURITY-CORE rule) |
| 3 | `skills/security-output-encoding/` | Phase 6 (2/12) | All four | Pair-completion with input-validation |
| 4 | `skills/security-input-validation/` | Phase 6 (1/12) | All four | First Phase 6 skill; Rule 5.1 was WS2 worked-example target |
| 5 | `skills/disagreement/` | Phase 5 | code-reviewer + holistic | Activity skill |
| 6 | `skills/debugging/` | Phase 5 | code-reviewer + holistic | Activity skill |
| 7 | `skills/testing/` | Phase 5 | code-reviewer + holistic | Activity skill; some security-adjacent content |
| 8 | `skills/ui-craft/` | Phase 5 | code-reviewer + holistic | Activity skill (DEC-F mid-phase addition) |
| 9 | `skills/design/` | Phase 5 | code-reviewer + holistic | Activity skill |
| 10 | `skills/project-management/` | Phase 5 | code-reviewer + holistic | Activity skill |
| 11 | `skills/discovery/` | Phase 5 | code-reviewer + holistic | Activity skill |
| 12 | `skills/continuity/` | Phase 4 | code-reviewer + holistic | **Always-on skill** — preloaded by holistic-reviewer (recursive but acceptable per Decision E note) |
| 13 | `skills/security-core/` | Phase 4 | code-reviewer + security-auditor + holistic | **Always-on skill** — preloaded by security-auditor (recursive but acceptable); shipped pre-WS2 so Stage 1 methodology was pre-WORKFLOW-V2 |
| 14 | `skills/code-quality/` | Phase 4 | code-reviewer + holistic | **Always-on skill** — preloaded by code-reviewer (recursive but acceptable) |
| 15 | `CLAUDE.md` | Foundational | **All four** (per Decision H Checkpoint 1 amendment) | 1073 lines; full audit per amended Decision H |
| 16 | `docs/WORKFLOW.md` | Foundational | **All four** | 911+ lines; recently amended by WS2 — check cross-doc consistency + adversarial-framing on guidance |
| 17 | `docs/ARCHITECTURE.md` | Foundational | **All four** | Extended sections §15-§22; check WS1-WS3 consistency |
| 18 | `DECISIONS.md` | Foundational | **All four** | Check ADR cross-references and amendments (DEC-005 amended by DEC-009, etc.) |
| 19 | `docs/RESEARCH-SECURITY.md` | Foundational | **All four** | Added per Decision H Checkpoint 1 amendment scope (it's a foundational doc); M1-M19 framework reference |

Total: **19 targets, ~57 dispatches** across all agents (post-Decision-H amendment). Original pre-amendment count was 18 targets / ~46 dispatches.

## §6 Finding Routing

Per Decision D:

- **Critical** findings → ERROR-LOG entry per finding, dated `ERR-YYYY-MM-DD-NNN`. Brief description + severity + status `open` + owner `WS5` + target resolution + originating audit dispatch + plain-language impact.
- **High** findings → same ERROR-LOG pattern as Critical.
- **Medium** findings → `docs/workstream-5-plan-backlog.md` entry (new working doc, see Decision J). Structured row: severity / target / finding-id / remediation hint / priority hint.
- **Low** findings → same `docs/workstream-5-plan-backlog.md`, separate section. Indexed for WS5 to prioritize.

Cross-target patterns (per §4.3) → `docs/workstream-5-plan-backlog.md` "Cross-target patterns" section.

## §7 Build Sequence

Per Decision F (one commit per artifact). **Updated post-Checkpoint-1 amendments:** Build Step 2 (plugin install) is DROPPED per Decision B amendment; foundational-doc count goes from 4 to 5 (RESEARCH-SECURITY added) and dispatch matrix expands to all-four per Decision H amendment.

1. **Build Step 1 — WS4 plan + Checkpoint 1** (Commits 1/22 + 2/22)
2. **Build Step 2 — Audit target 1 (security-cryptography)** (Commit 3/22). Validation target per Decision K. Comparison against WS3-known findings (ERR-001 + ERR-003 + ERR-004 + F-H04 + F-H05). **First-target validation gate.**
3. **Build Step 3 — Audit targets 2-4 (Phase 6 skills 1/12-3/12)** (Commits 4/22-6/22).
4. **Build Step 4 — Audit targets 5-11 (Phase 5 activity skills)** (Commits 7/22-13/22).
5. **Build Step 5 — Audit targets 12-14 (Phase 4 always-on skills)** (Commits 14/22-16/22).
6. **Build Step 6 — Audit targets 15-19 (foundational docs, all four agents per Decision H amendment)** (Commits 17/22-21/22). Five commits: CLAUDE.md, WORKFLOW.md, ARCHITECTURE.md, DECISIONS.md, RESEARCH-SECURITY.md.
7. **Build Step 7 — Cross-target holistic synthesis + WS4 closeout + WS5 plan v1** (Commit 22/22, possibly bundling). Cross-target pattern dispatch (per §4.3). ROADMAP update (WS4 ✅ complete, WS5 next). `framework-hardening-plan.md` §3.4 status flip. WS5 plan v1 as starting input for WS5.

**Realistic commit count: 21-23** depending on whether Build Step 7 bundles closeout + WS5-plan-v1 + cross-target synthesis into one commit or splits.

**Sequencing flexibility:** if any per-artifact audit surfaces findings that block subsequent audits (e.g., a CLAUDE.md inconsistency that affects how skills are interpreted), pause sequential audit, file the blocking finding to ERROR-LOG, and either escalate to Alt or work around (audit-aware-of-known-gap).

## §8 Validation Strategy

Two layers:

### §8.1 Per-artifact validation (during each audit commit)

- Track 1 mechanical compliance produces structured output. Validate: did the report cover all 6 mechanical checks? Are findings concrete (cite specific lines / source IDs / V-IDs)?
- Track 2 agent dispatch produces structured per-agent output. Validate: did each dispatched agent return findings (zero findings on a substantive skill is itself a red flag — either dispatch was misconfigured or the artifact is unusually clean)?
- Critical/High findings → ERROR-LOG entry verified to follow ERR-001-004 format.
- Medium/Low findings → backlog entry verified to include severity, target, remediation hint.

### §8.2 First-target validation (Build Step 2 only — was Build Step 3 pre-amendment)

Per Decision K: validation against `73d025d` findings WS3 already surfaced (ERR-001 + ERR-003 + ERR-004 + F-H04 + F-H05). Comparison criteria:
- Audit reproduces 5 of 5 prior findings → audit methodology validated; proceed with confidence.
- Audit reproduces 3-4 of 5 → investigate missed findings; possibly persona/dispatch issue.
- Audit reproduces ≤2 of 5 → halt audit; deep investigation of dispatch correctness before proceeding.

### §8.3 WS4 closeout validation (Build Step 7 — was Build Step 8 pre-amendment)

Cross-target holistic dispatch verifies no obvious audit gaps (e.g., a skill class that should have produced findings producing zero). WS5 plan v1 generated from the backlog has reasonable work-package structure for WS5 to attack.

## §9 Checkpoint 1 — Decisions for Alt

Eleven decisions to confirm or amend. Each has a recommendation in §3.

| ID | Decision | Recommendation |
|---|---|---|
| A | Audit ordering strategy | Approve — sequential per-artifact, reverse-chronological |
| B | Dispatch mechanism | **Approved with amendment 2026-05-26** — proxy-first (general-purpose dispatch, same as WS3 smoke tests); plugin install + ERR-002 resolution deferred to Phase 14. Build Step 2 (plugin install) DROPPED. |
| C | Two-track audit methodology | Approve — mechanical (Track 1) + agent dispatch (Track 2) per artifact |
| D | Finding routing | Approve — severity-based; Critical/High → ERROR-LOG, Medium/Low → backlog doc |
| E | Per-artifact dispatch matrix | Approve — all four for Phase 6 security; selective for others |
| F | Per-artifact commit boundary | Approve — one commit per audited artifact; ~21 commits total |
| G | §2 Sources retroactive rigor | Approve — bidirectional check only; re-fetch is WS5 work |
| H | Foundational docs audit depth | **Approved with amendment 2026-05-26** — all four agents on each foundational doc (5 docs total: CLAUDE.md, WORKFLOW.md, ARCHITECTURE.md, DECISIONS.md, RESEARCH-SECURITY.md). Persona-fit note in §3 Decision H body. New Risk 9. |
| I | Activity-log transcript storage | Approve — same `.tgf/state/agent-activity/` pattern as WS3 |
| J | WS5 backlog format | Approve — two-doc (ERROR-LOG for Critical/High + workstream-5-plan-backlog.md for Medium/Low) |
| K | Per-audit sanity check | Approve — none except Build Step 2 first-target validation against WS3-known findings (Build Step 2 post-amendment; was Build Step 3 pre-amendment) |

Anticipated discussion topics:
- Whether to skip plugin install (Decision B) if it's known to be friction-heavy — would fall back to proxy with explicit ERR-002 carry-forward
- Whether 18 targets is the right scope or trimmed (e.g., skip Phase 5 activity skills if they're considered less load-bearing)
- Whether the per-artifact commit boundary is right or should bundle (e.g., all Phase 5 activity skills in one commit)
- Whether cross-target synthesis at Build Step 8 should be separate or rolled into the WS4 closeout commit

## §10 Out of Scope (Deferred to Other Workstreams or Phases)

- **Remediation of any finding surfaced.** That is WS5. WS4 produces findings; WS5 fixes them. The boundary is structural and non-negotiable.
- **Auditing WS3 deliverables (the four agents themselves).** Already audited at build time via the 8 WS3 smoke-test transcripts. Re-audit would be duplicative.
- **Auditing WS1 / WS2 deliverables.** Same reason — produced under the now-operational discipline; WS3 smoke tests covered the agents that protect them.
- **Re-fetching authoritative sources under M1-M19.** That is WS5 remediation work for findings that require source re-verification.
- **Producing the WS5 implementation work itself.** WS4 produces only the WS5 plan v1 + backlog catalog; WS5's full plan + Checkpoint 1 + implementation happen in WS5's own workflow.
- **Phase 11/12 hook-side enforcement work** (e.g., F-H04's executable fitness function for §2 Sources). WS4 catalogues such gaps; they are framework-evolution work for Phase 11/12, not WS5 remediation.

## §11 Effort Estimate

Per `docs/framework-hardening-plan.md` §3.4: "1-2 sessions for audit itself + 1-3 sessions for remediation (Workstream 5)." This was conservative; revised estimate:

**Updated post-Checkpoint-1 amendments.** Build Step 2 (plugin install) dropped per Decision B amendment; Build Step 6 expands per Decision H amendment (5 foundational docs × 4 agents instead of 4 docs × 1 agent).

| Build Step | Commits | Effort estimate |
|---|---|---|
| 1 (plan + Checkpoint 1) | 2 | This session (~30 min for plan; Checkpoint 1 ~30 min walk) |
| 2 (first artifact: security-cryptography validation) | 1 | ~45 min (~3-4 dispatches + Track 1 mechanical + validation comparison) |
| 3 (Phase 6 skills 1/12-3/12) | 3 | ~2 hours (3 artifacts × ~40 min each) |
| 4 (Phase 5 activity skills) | 7 | ~2-3 hours (lighter dispatch matrix per Decision E) |
| 5 (Phase 4 always-on skills) | 3 | ~1.5 hours |
| 6 (foundational docs, all four agents per amended Decision H) | 5 | ~3-4 hours (5 docs × 4 agents = ~20 dispatches; large-doc handling adds latency per Risk 9) |
| 7 (cross-target synthesis + closeout + WS5 plan) | 1 | ~1 hour |

**Total: ~11-13 hours, realistic 2-3 sessions of focused work.** Modest increase from pre-amendment ~10-12 hours due to Decision H expansion partly offset by Decision B simplification. Push timing per WS3 precedent: at WS4 closeout or earlier per Alt's call.

## §12 Risks

### Risk 1 — Plugin install friction blocks Decision B (RESOLVED post-Checkpoint-1)

**Status:** RESOLVED via Decision B amendment. WS4 uses proxy dispatch from the start; no plugin install attempted. ERR-2026-05-25-002 stays open and gets resolved during Phase 14 (Slash Commands + Plugin Integration) when plugin install is the actual work. This risk no longer applies to WS4.

### Risk 2 — Audit findings overwhelm WS5 plan scope

**Probability:** medium-high. **Impact:** medium (WS5 may need its own decomposition).

**Mitigation:** Decision D severity-based routing prevents ERROR-LOG flood. If Medium/Low backlog exceeds ~50 entries, WS5 plan structures by work-package (per-skill remediation, per-cross-target-pattern remediation, per-discipline-rule remediation) rather than per-finding. Cross-target holistic synthesis at Build Step 8 produces this structure naturally.

### Risk 3 — First-target validation fails (Build Step 3)

**Probability:** low. **Impact:** high (would invalidate audit methodology).

**Mitigation:** Build Step 3 specifically tests whether the audit reproduces WS3's known findings on `73d025d`. If <60% reproduction, halt and investigate (dispatch misconfiguration, persona drift, plugin-install issue, etc.) before proceeding. This is the methodology checkpoint.

### Risk 4 — Recursive self-audit produces blind spots

**Probability:** low-medium. **Impact:** medium (some findings may be missed).

**Mitigation:** When an agent audits a skill it preloads (e.g., code-reviewer auditing `skills/code-quality/`), the agent has its persona's ground truth as preloaded context. Mitigation: cross-check that the agent's findings include any obvious gaps (e.g., recent rule additions should be visible). If recursive dispatches produce abnormally clean results, dispatch a non-preloading agent (e.g., holistic-reviewer reviewing `skills/code-quality/`) as a cross-check.

### Risk 5 — Audit reveals foundational-doc inconsistencies that block per-artifact audits

**Probability:** medium. **Impact:** high (e.g., if CLAUDE.md §3 references stages that WS2 amended).

**Mitigation:** Reverse-chronological order (Decision A) means foundational docs are audited last. If a foundational-doc finding affects skill interpretation, file the finding to ERROR-LOG and either pause WS4 to amend the foundational doc (if quick) or proceed with audit-aware-of-known-gap (if larger).

### Risk 6 — Dispatch cost balloons (46 dispatches × per-dispatch latency)

**Probability:** medium. **Impact:** medium (slower than estimated).

**Mitigation:** Dispatches can run in parallel where independent (different artifacts, different agents). Activity-log writes serialize on the orchestrator-write convention. Per-artifact validation (§8.1) can be deferred to the per-artifact commit prep rather than blocking next dispatch. Realistic: ~2-3 dispatch hours total at observed WS3 dispatch latencies.

### Risk 7 — Cross-target synthesis (Build Step 8) overweighs its evidence base

**Probability:** low-medium. **Impact:** low-medium (recommendations to WS5 may be premature).

**Mitigation:** Build Step 8 holistic dispatch operates on per-artifact transcripts. If patterns are surfaced from <3 supporting artifacts, flag as "preliminary pattern" rather than "confirmed pattern" in the WS5 plan. WS5 can validate or reject patterns during its own Checkpoint 1.

### Risk 8 — Persona refinements R1-R10 affect audit consistency across dispatches

**Probability:** low. **Impact:** low (the refinements are consistent across all four agents).

**Mitigation:** All four agents shipped with the same R4 + R10 baseline applied during WS3. Per-agent refinements (R1-R3, R5-R9) are agent-specific and don't cross dispatch boundaries. No mitigation needed beyond verifying agent files at WS4 start.

### Risk 9 — Full four-agent dispatch on prose-heavy foundational docs may produce thin findings from non-holistic agents (added post-Checkpoint-1 per Decision H amendment)

**Probability:** medium-high. **Impact:** low-medium (low-signal findings consume dispatch effort without proportionate value).

**Mitigation:** Per the persona-fit note in §3 Decision H, code-reviewer / security-auditor / red-team are being applied to content they weren't designed for (prose / docs rather than code / skill files). Expect:
- holistic-reviewer produces dominant finding count per foundational doc
- other three produce thinner finding sets — but findings that surface are differentially valuable (lens-specific concerns the holistic misses)
- if code-reviewer / security-auditor / red-team produce zero findings on a foundational doc, that's acceptable (the dispatch confirmed no lens-specific concerns) rather than a methodology failure

If pattern is "consistently zero findings from one agent across 3+ docs," consider reverting that agent's dispatch on remaining foundational docs (mid-step amendment) to save effort. Capture the observation as a learning for any future Phase-14-style foundational-doc audit work.

### Risk 10 — Large-document handling under dispatch (added post-Checkpoint-1 per Decision H amendment)

**Probability:** medium. **Impact:** medium (agents may truncate, miss content, or produce shallow findings on 1000+ line docs).

**Mitigation:** Foundational docs CLAUDE.md (1073 lines), WORKFLOW.md (911+ lines), and ARCHITECTURE.md are substantial. The agents weren't designed for that scale of single-input review.

Options if observed: (a) chunk the doc and dispatch per section (e.g., CLAUDE.md §1-§7 in one dispatch, §8-§14 in another, then §15-§22 in a third for the architecture sections); (b) restrict per-dispatch focus to specific check categories rather than full review; (c) accept shallower findings per dispatch and rely on the cross-target holistic-synthesis at Build Step 7 to catch what individual dispatches missed.

Default plan: full-doc dispatch first; chunk if results show truncation/shallowness. Pre-emptive chunking would add per-target commit boundary complexity.

## §13 Commit Discipline

Per the WS2 + WS3 precedent:

- Commit messages in Alt's voice per `[[feedback-commit-message-style]]` — descriptive about the deliverable, no marketing-speak, draft → show → commit.
- Co-Authored-By trailer per `[[feedback-commit-attribution]]`.
- Per-artifact commits include the artifact name in the commit subject (e.g., "Audit `skills/security-cryptography/` — WS4 Target 1").
- Commit body documents: Track 1 mechanical-compliance report summary, Track 2 per-agent findings count by severity, ERROR-LOG additions (if any), backlog additions (if any), comparison against prior known findings (Build Step 3 only).
- Activity-log transcripts are gitignored per Decision I; the commit message captures their dispatch IDs for cross-reference.

## §14 Cross-References

- `docs/framework-hardening-plan.md` §3.4 — WS4 spec (this plan operationalizes that spec).
- `docs/workstream-3-plan.md` — WS3 plan; the four agents this plan dispatches were built per that plan.
- `agents/code-reviewer.md` / `security-auditor.md` / `red-team.md` / `holistic-reviewer.md` — the audit instruments.
- `DECISIONS.md` DEC-2026-05-26-011 — §2 Sources discipline rules applied retroactively by this audit.
- `ERROR-LOG.md` — starting backlog (ERR-001 through ERR-004 from WS3 smoke tests).
- `docs/RESEARCH-SECURITY.md` — M1-M19 reference for retroactive evaluation.
- `docs/WORKFLOW.md` §3 (Stages 1-3 per WS2) — workflow-stage compliance check baseline.
- `docs/WORKFLOW.md` §4 — subagent output schemas the audit dispatches conform to.
- `.tgf/state/agent-activity/<role>/` — where Track 2 dispatch transcripts land (gitignored).
- `.tgf/state/source-registry.json` — source-resolution check baseline.
- `.tgf/state/research-logs/` — verification-depth check baseline.
- (To be created during WS4) `docs/workstream-5-plan-backlog.md` — WS5 starting backlog catalog.
