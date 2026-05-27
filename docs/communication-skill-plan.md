# Communication Skill — Plan v1

> **Skill:** `communication` (Phase 5+ activity skill, peer to `disagreement`, `debugging`, `discovery`, `design`, `project-management`, `testing`, `ui-craft`)
>
> **Status:** ⏳ Plan — pending Phase 5 cohort scheduling (after WS4 + WS5 close, before any Phase 6 resumption)
>
> **Scope:** operationalize the communication-discipline trait already captured in CLAUDE.md §2 ("Adaptive communication" — operational discipline addendum, 2026-05-27 amendment). The trait gives the floor; this skill adds the depth.

---

## §1 Purpose

CLAUDE.md §2 was amended on 2026-05-27 to add operational communication discipline (plain English first, jargon pointers, stage-transition status briefings, push-routine-surface-decisions, depth calibration). The amendment is intentionally compact (~25 lines) because CLAUDE.md is the load-bearing contract document and grows in scope.

This skill provides the depth that doesn't fit in the contract:

- Concrete rules with citations at sub-rule granularity (per Phase 6 Checkpoint 1 Decision A hybrid).
- Anti-patterns with worked examples — including the framework's own past communication failures (e.g., jargon-first narration during WS4 Build Step 2).
- Per-workflow-stage communication patterns (Stage 1 Research briefing template; Stage 2 Scope; Stage 3 Plan-with-Governance handoff; Stage 5 four-pass review; Stage 6 Commit).
- Refusal-envelope language for "explain this clearly" requests that would compromise correctness if simplified beyond truthful.
- AI-specific concerns — sycophancy in communication, narration-as-substitute-for-work, dense-process-narration anti-patterns specific to AI-generated text.

## §2 Authoritative Sources

The CLAUDE.md amendment cites three live sources at chapter level; this skill cites at sub-rule level.

### Tier 1 living (live-cited at rule level, periodic refresh required)

| Source ID | Reference | Version | Last Verified |
|---|---|---|---|
| `PLAIN-LANG-GOV` | [Federal Plain Language Guidelines / digital.gov](https://digital.gov/guides/plain-language) | Living document (2011 origin, periodically updated) | 2026-05-27 |
| `MS-WRITING-STYLE` | [Microsoft Writing Style Guide](https://learn.microsoft.com/en-us/style-guide/welcome/) | Continuously updated (this fetch: 2025-04-03 page revision) | 2026-05-27 |
| `GOOGLE-DOC-STYLE` | [Google Developer Documentation Style Guide](https://developers.google.com/style) | Continuously updated (this fetch: 2026-04-27) | 2026-05-27 |

### Tier 1 stable (cited by reference — publication-level)

| Source | Why cited |
|---|---|
| **ISO/IEC/IEEE 26514:2022** — Systems and software engineering — Design and development of information for users | Technical communication for software systems; underpins the audience-awareness rule |
| **PMBOK Guide, 7th Ed (2021)** §4.4 (Manage Project Knowledge — stakeholder communication) | Status-briefing structure; communication-as-governance framing |
| **Pinker, *The Sense of Style: The Thinking Person's Guide to Writing in the 21st Century* (Viking, 2014)**, Ch. 3 (The Curse of Knowledge) | Why expert→novice gaps happen and how to bridge them; cognitive-load framing |
| **Cutts, *Oxford Guide to Plain English*, 5th Ed (Oxford University Press, 2020)** | Comprehensive style reference for plain-English discipline |

### Authority not yet on this list (open for consideration when skill ships)

- **The Scrum Guide (2020)** — Sutherland & Schwaber — public document; daily-standup format anchors the stage-transition pattern. Candidate for inclusion if status-briefing rule needs additional anchor.
- **U.S. Plain Writing Act of 2010 (Public Law 111-274)** — legal authority underpinning PLAIN-LANG-GOV. Cited indirectly via PLAIN-LANG-GOV; may need direct citation if the rule benefits from legal anchoring.

### Sources NOT used (and why)

- **Military communication standards (NATO STANAG 2014, USMC MCRP 3-30B.1, OPORD/FRAGO formats).** The SITREP pattern these encode maps to the same structured-status-briefing discipline this skill captures, but TGF dropped IC/military sourcing during WS2 (per the 2026-05-25 WORKFLOW-V2 decision to drop IC/military methodology references). The civilian-anchored sources above carry the same discipline without the framing concerns.

## §3 Proposed Rule Outline

Rules are numbered to fit a future Phase 5 activity-skill cohort. Numbering is provisional; assignment depends on cohort position at build time.

- **Rule X.1: Plain-English-first sentence construction.** Lead sentences with the plain-English meaning; internal labels (build step IDs, decision IDs, dispatch UUIDs, stage references) appear paired with their meaning or as secondary clauses. Authority: `PLAIN-LANG-GOV §Writing for understanding`; `GOOGLE-DOC-STYLE §General Principles — Jargon`; `MS-WRITING-STYLE §Top 10 tips`.

- **Rule X.2: Teach-as-you-go vocabulary introduction.** On first use of an internal term within a session, explain it briefly so a reader could pick up cold. Authority: `Pinker, Sense of Style (2014), Ch. 3 — Curse of Knowledge`; `GOOGLE-DOC-STYLE §Jargon`.

- **Rule X.3: Stage-transition status briefings.** At each handoff between workflow stages (research → scope → plan → implement → review → commit) and at each named build step within a workstream, write a structured update: *where we are*, *what just happened*, *what's next*. Authority: `PLAIN-LANG-GOV §Design for understanding`; `PMBOK 7th Ed §4.4`.

- **Rule X.4: Push-routine, surface-real-decisions cadence.** Don't request confirmation on routine mechanical work; do pause when something genuinely needs the user's call. Authority: cross-reference `CLAUDE.md §5` severity gradient (this rule operationalizes the §5 stakeholder-authority framing for in-flight work, not just for advocacy); `PMBOK 7th Ed §4.4` stakeholder-engagement framing.

- **Rule X.5: Audience-calibrated technical depth.** Match technical depth to demonstrated user familiarity. Authority: `MS-WRITING-STYLE §audience-aware voice`; `ISO/IEC/IEEE 26514:2022 §audience analysis`.

- **Rule X.6: Bidirectional governance framing.** Communication discipline is load-bearing for the user-AI bidirectional check (user catches what AI misses; AI catches what user misses). This is TGF-native discipline — captured in `DECISIONS.md` rationale rather than imported from external authority. Authority: `CLAUDE.md §1 (The Contract)` + this skill's own DEC entry.

## §4 Proposed Anti-Pattern Outline

Per `DEC-2026-05-17-003` Clause 1, every anti-pattern is paired with a canonical pattern.

- **AP-1: Jargon-first narration without pointer.** Example: "Running Track 1 mechanical compliance per WS4 plan §4.1" without first establishing what Track 1 is. Canonical: lead with "Auditing the first of 19 skills as a methodology check (Track 1 = the mechanical compliance pass; six checks against the skill files)."

- **AP-2: Dense process narration without grounding context.** Example: "Dispatching code-reviewer with UUID 76e2f99c against 73d025d." Canonical: "Asking the code-reviewer agent to review the first audit target (the security-cryptography skill). It'll take ~3 minutes."

- **AP-3: Confirmation requests on routine mechanical work.** Example: "Should I now write the JSON to disk?" after the user has already approved the audit run. Canonical: write the JSON, mention it briefly in the next status briefing.

- **AP-4: Pause-cadence misjudgment — silently proceeding past a real decision.** Example: validation-gate result is ambiguous (3 of 5 reproduced, on the boundary) and the AI proceeds without flagging. Canonical: stop, surface the ambiguity, ask for the user's call.

- **AP-5: Stage-transition silence — no briefing at handoffs.** Example: completing Track 1 and immediately starting Track 2 without summarizing what Track 1 surfaced. Canonical: brief summary at the handoff; ask if any direction-change is wanted before continuing.

- **AP-6: Trailing summary of what was just done (AI-generated-code-style smell, applied to communication).** Example: "I have now completed steps 1, 2, and 3 and the result is X." Canonical: skip the summary; the work and its artifacts are the evidence. Reserve summaries for genuine stage transitions (per AP-5 inverse), not for "I finished the thing I just did."

- **AP-7: Sycophantic affirmation in place of substance.** Example: "Great question!" prefix; "You're absolutely right" before disagreeing; verbose reassurance before delivering bad news. Canonical: lead with substance; affirm only when affirmation carries information (e.g., "Yes — for the reason you suspect.").

- **AP-8: Fabricated identifiers in dispatch prompts or status briefings.** Example: referencing "ERR-2026-05-26-005" in a dispatch input when that ERR entry doesn't exist (this happened during WS4 Build Step 2; the dispatched holistic-reviewer agent caught it). Canonical: grep for the identifier before referencing it; if not found, either create it first or use a different framing ("a candidate ERR entry that should exist but doesn't yet"). The framework's bidirectional-check premise depends on identifiers being verifiable on demand.

## §5 AI-Specific Concerns

- **Sycophancy in communication.** AI training data over-represents agreement-as-politeness; production AI defaults to affirmation in place of substance. Defense: AP-7. Cross-ref: `disagreement` skill (which operationalizes the §5 severity gradient for advocacy; this skill addresses the communication-pattern side of the same problem).

- **Narration as substitute for work.** AI defaults to producing visible-looking text when the actual task would require investigation, computation, or external verification. Defense: status briefings should describe *what changed*, not *what I'm about to do* in the abstract. Cross-ref: `code-quality` skill (AI-generated-code smells include trailing summaries; same pattern in communication).

- **Dense process narration without grounding context.** AI defaults to assuming the user shares its working context. Defense: every multi-step update grounds the work in the user-visible objective. AP-2 covers the pattern.

- **Identifier fabrication in dispatch prompts.** AI defaults to plausible-looking identifiers when an exact citation is needed. Defense: AP-8. Cross-ref: M9 confirmation-gap pattern (research-security infrastructure) — the same training-data-recall failure mode that affects citation chains.

## §6 Workflow Integration

How this skill participates in the six-stage workflow:

- **Stage 1 (Research):** Emit a research-stage briefing at the end of Stage 1 — what was read, what's understood now, what remains uncertain. Pattern: `where we are: <current understanding> / what just happened: <research conducted> / what's next: <Stage 2 scope decision>`.

- **Stage 2 (Scope):** Emit a scope briefing — what's in scope, what's deferred, what change-tier applies, what trust boundaries are affected. Pattern: `where we are: <scope confirmed> / what just happened: <boundaries identified> / what's next: <Stage 3 plan>`.

- **Stage 3 (Plan with Governance):** Plain-English plan summary precedes the technical plan. When asking for checkpoint approval, the question form follows AP-3's inverse — pause for real decisions, not for routine.

- **Stage 4 (Implement):** Brief stage-start update; otherwise quiet until findings or blockers emerge.

- **Stage 5 (Four-Pass Review):** Per-pass briefings on review outcomes (code review found X; security audit found Y; etc.) ahead of routing.

- **Stage 6 (Commit):** Draft → show → commit pattern (already captured in `feedback_commit_message_style` user memory). Commit message itself follows plain-English discipline: lead with the deliverable, secondary clauses for technical detail.

## §7 Cross-Skill Web

- **`disagreement`** — operationalizes the severity gradient for advocacy (Light Touch / Standard / Strong / Hard Refusal). This skill operationalizes the communication-pattern side of the same governance framing.
- **`continuity`** — captures session-log discipline and three-log management. Status briefings written under this skill's Rule X.3 also serve as draft material for session-log entries at Stage 6.
- **`disagreement` + this skill** together cover AI-sycophancy defense (AP-7 here; sycophancy-routing in `disagreement`).
- **`code-quality`** — comment-discipline rules in code-quality map to the same plain-English-first discipline applied to code comments; this skill applies it to AI→user communication.

## §8 Open Questions for Phase 5 Build

To resolve when the skill is built:

1. **Severity gradient calibration.** Most communication findings will be Low (style preferences for style-equivalent patterns). What's the High-severity threshold? Sycophantic affirmation that misleads about correctness? Fabricated identifiers? The line needs to be set explicitly during build.

2. **Per-stage briefing templates.** Should the skill ship reusable Markdown templates for the where-we-are / what-just-happened / what's-next pattern, or specify the discipline and let the form vary?

3. **CLI-rendering conventions.** Bullets vs tables vs paragraph format. Mostly user preference; could be a §10 Style Conventions appendix rather than rule-level.

4. **Refusal-envelope structure for communication refusals.** "Explain this more simply" requests where simplification would compromise correctness — when does the discipline refuse? Pattern from `code-reviewer` agent §7 R10 refusal envelope is the model; adapt for communication.

## §9 Out of Scope

- **Per-user style preferences.** Alt's specific preferences (concise; plain English first; teach as you go) belong in user-auto-memory (where they already are at `feedback_plain_english_with_jargon_pointers`). The skill captures the **discipline**, not the personal style.
- **Visual/CLI rendering specifics beyond the rule level.** Markdown tables, bullet rhythms, when-to-use-headers — these vary by deployment and don't need rule-locking. Optional §10 Style Conventions appendix at most.
- **Localization / non-English communication.** TGF currently ships English-only. If the framework expands to other languages, the skill's source basis would need to extend to ISO/TR 11669 and similar; out of scope for v1.
- **Communication for end-users of TGF-built applications.** This skill governs AI→stakeholder communication during TGF use; it does not govern the *application's* user-facing communication (which is the application's own concern).

## §10 Cross-References

- `CLAUDE.md` §2 (Adaptive communication — operational discipline addendum, 2026-05-27) — the trait this skill operationalizes.
- `feedback_plain_english_with_jargon_pointers` (user-auto-memory) — Alt's specific preferences that motivated the trait amendment.
- `agents/code-reviewer.md`, `agents/security-auditor.md`, `agents/red-team.md`, `agents/holistic-reviewer.md` — refusal-envelope pattern (§7 R10) that this skill's refusal-envelope rule should mirror.
- `.tgf/state/source-registry.json` — PLAIN-LANG-GOV, MS-WRITING-STYLE, GOOGLE-DOC-STYLE entries registered 2026-05-27.
- `ERROR-LOG.md` ERR-2026-05-27-007 — research-security hook bug surfaced during the source-verification fetch for this plan. WS1 follow-up; not blocking this skill's Phase 5 build.
- `docs/workstream-5-plan-backlog.md` — WS5 inherits this plan as queued work; Phase 5+ scheduling sequences it relative to remaining WS4 audit targets.
