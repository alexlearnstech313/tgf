# Rules — CONTINUITY

Full rule statements with citations, plain-language impact, and extended discussion. Referenced from `SKILL.md` §5 Rule Summaries. Loaded on demand when deep rule application is needed (typically Stage 5 Phase 4 Holistic Review or Stage 6 Commit).

Six rules covering the operational discipline that lets a project's memory survive session closes, developer transitions, and the project's own three-year-old decisions becoming load-bearing.

Most rules are TGF synthesis of senior operational practice grounded in NIST SSDF v1.1 PO.5 + ADR methodology (Nygard 2011) + ISO/IEC 27002:2022 control 5.37 (by reference). Citation discipline per `DEC-2026-05-17-004`: where rule-level mapping does not exist in any single authoritative source, the rule is acknowledged as TGF synthesis with explicit grounding rather than fabricating sub-rule identifiers.

---

## Rule 5.1: Session-Close Log Entry Required

**Statement:** Every Claude Code session that did substantive work — not casual conversation, not single-file edits with no broader context — produces a session log entry at `.sessions/YYYY-MM-DD-session-NN-brief-topic.md` at session close. The entry captures: topics discussed, decisions made and rationale, context for future sessions, open questions, findings from skill-activated work, and any updates to PROJECT-CONTEXT / DOMAIN-CONTEXT / ROADMAP / DECISIONS / the three logs.

**Citation:** `TGF-SYNTHESIS — grounded in NIST-SSDF v1.1 PO.5 (Implement Supporting Toolchains) + senior operational practice`. NIST SSDF PO.5 covers configuration management discipline at the practice level but does not specify session-log structure; this rule is TGF synthesis of standard "lab notebook" engineering practice adapted to AI-assisted development.

**Plain-language impact:** Without session logs, the project loses its working memory at every session close. The next session — possibly weeks later, possibly with a different developer — starts from current code only, with no record of why decisions were made, what was tried and rejected, what's blocked, or what was on the "next session" list. The cost is paid every onboarding and every continuity gap: rediscovering the same lessons, relitigating the same decisions, and missing the WHY behind every load-bearing choice.

**Extended discussion:** Session logs are TGF's working-memory layer — distinct from ADRs (durable architectural decisions) and the three operational logs (active findings). Session logs capture the full texture: what was researched, what was scoped, what was implemented, what was reviewed, what surprised, what was deferred. They are gitignored per Rule 5.5; this is a feature, not a limitation — the project's working operational state is not for public consumption.

The framework's session-log discipline operates at two cadences:

1. **Per-commit during a session:** incremental entries capturing what was just done and what's next. These keep the session log honest as work progresses rather than as a single end-of-session reconstruction.
2. **Session-close summary:** synthesis at session end — what was accomplished, what's open, what the next session opens with.

Per `CLAUDE.md` §13, session logs go to `.sessions/YYYY-MM-DD-session-NN-brief-topic.md`. The naming convention preserves chronological order and topical retrievability. The `.sessions/` directory is gitignored by TGF's own `.gitignore` template and recommended for adopter projects.

AI-assisted development makes session logs especially important — context compaction will lose conversation history; session logs are what survives compaction.

**Related anti-patterns:** AP-1 (decision-only entry), AP-7 (committed to public repo) (see `anti-patterns.md`)

---

## Rule 5.2: Architectural Decisions Get ADRs

**Statement:** Decisions that constrain future work, change project direction, span multiple sessions, or that future maintainers will need to understand are captured as Architectural Decision Records in `DECISIONS.md` using the standard structure: **Decided** (one-sentence summary), **Date**, **Context** (what problem this addresses, why now), **Decision** (full statement with rationale, often numbered), **Alternatives considered** (options weighed and why not chosen), **Consequences** (what this commits the project to, trade-offs accepted, downstream effects). Tactical decisions that don't constrain future work stay in session logs.

**Citation:** `ADR-NYGARD (2011) — Michael Nygard, "Documenting Architecture Decisions"` (canonical ADR methodology; stable since 2011) + `ISO-27002 5.37 (by reference)` (documented operating procedures; paywalled, per `DEC-2026-05-17-004` Clause 5).

**Plain-language impact:** Without ADRs, architectural decisions live only in the heads of the people who made them. Six months later, those people may have moved on or forgotten the rationale. The decision then gets relitigated — possibly to the same answer (wasted work), possibly to a different answer (regression). Worse, the *alternatives considered* are lost, so the same rejected approach gets re-evaluated by someone who doesn't know it was rejected and why.

**Extended discussion:** The threshold for an ADR is "will a future maintainer need to understand this?" Common ADR triggers:

- Stack choices (database, framework, deployment platform)
- Authentication and authorization architecture
- Data model schemas and their migration strategy
- Trust boundaries and security architecture
- API contract decisions (REST vs GraphQL, versioning strategy)
- Third-party service selections
- Anything overruling a default in `CLAUDE.md` or a TGF skill

The ADR structure is purposeful:

- **Decided** lets a reader skim the decision in one sentence
- **Context** captures why the decision was needed (often the most valuable section for future re-evaluation)
- **Decision** is the full rationale and any numbered sub-decisions
- **Alternatives considered** prevents re-evaluating rejected paths from scratch
- **Consequences** documents what was traded away — the costs the decision accepted

ADR IDs follow the convention `DEC-YYYY-MM-DD-NNN` where NNN is sequence within the day (usually 001 unless multiple ADRs land same day). Newer ADRs appear at the top of `DECISIONS.md` so a reader sees current state first.

When a prior ADR is amended (changed in effect by a later decision), write a new ADR rather than editing the original. The new ADR's Context section references the prior ADR being amended; the new ADR's Decision section captures what changed; the original ADR remains in `DECISIONS.md` as historical record. This preserves the decision history and the reasoning chain. AP-8 covers this.

**Related anti-patterns:** AP-2 (buried in commit message), AP-8 (amended in place) (see `anti-patterns.md`)

---

## Rule 5.3: Three-Log Routing Discipline

**Statement:** Operational findings route to one of three logs by action profile:

- **`ERROR-LOG.md`** — actionable issues being worked: bugs, performance problems, security findings under remediation. Each entry has severity (critical/high/medium/low), status (open/in-progress/blocked/resolved), owner, and target resolution date or condition.
- **`VENDOR-LOG.md`** — out-of-codebase actions required: dashboard configuration, key rotation, DNS changes, third-party service setup, infrastructure changes. Each entry has the action description, the system where action is needed, status, and target date.
- **`WAIVER-LOG.md`** — formally accepted risks: findings the project consciously chose not to fix. Each entry has the finding being waived, the rationale for acceptance, severity, and a revisit condition or date (never "permanent").

Findings without a clear home in one of these three logs are not "we'll get to it later" — they are categorized and routed.

**Citation:** `TGF-SYNTHESIS — grounded in NIST-SSDF v1.1 PO.5 + senior operational practice`. NIST SSDF PO.5 covers configuration management at the practice level; the three-log split is TGF synthesis of operational lessons (ERROR-LOG vs VENDOR-LOG distinction comes from observed pattern of "code-action vs out-of-codebase-action" confusion; WAIVER-LOG comes from compliance / audit framework practice of formal risk acceptance).

**Plain-language impact:** Without a log entry, an operational finding lives in someone's head, in a chat message, or in a TODO comment in the code. None of those survive personnel changes or onboarding. The finding then gets either rediscovered (wasted work) or never surfaced again (silent risk). With a log entry but wrong routing, the finding is in the wrong action profile — ERROR-LOG entries get worked, VENDOR-LOG entries get scheduled with external systems, WAIVER-LOG entries get revisited. A vendor action sitting in ERROR-LOG looks like an open code bug; a waiver in ERROR-LOG looks like work that's not getting done.

**Extended discussion:** The three logs map to three different operational rhythms:

*ERROR-LOG cadence:* daily / per-sprint. Errors are worked actively. Severity drives priority; status drives standup discussion. Resolved entries move to a Resolved section or get pruned (with the resolution captured in commit messages and session logs).

*VENDOR-LOG cadence:* weekly / per-cycle. Vendor actions wait on someone with the right credentials and the right calendar slot. The log surfaces these so they don't get lost between codebase work and external operations. Common entries: Stripe webhook configuration, DNS record updates, key rotation in secret manager, third-party service setup, compliance audit scheduling.

*WAIVER-LOG cadence:* monthly / quarterly. Waivers represent the project's risk posture; reviewing them is a periodic exercise distinct from work cadence. Each waiver has a revisit condition ("when we have more than 1,000 users") or a date ("revisit 2026-08-01"). Waivers without revisit conditions become permanent by default — AP-5 covers this.

For TGF itself: per prior session logs, TGF as the framework does not maintain ERROR/VENDOR/WAIVER logs because it is the framework, not a project governed by the framework. Adopter projects DO maintain them. The framework's own decisions go in DECISIONS.md as ADRs.

**Related anti-patterns:** AP-3 (todo list as memory), AP-5 (waiver without revisit), AP-6 (vendor conflated with error) (see `anti-patterns.md`)

---

## Rule 5.4: ROADMAP Reflects Current Reality

**Statement:** `ROADMAP.md` is updated whenever milestone progress changes (a milestone advances, completes, or slips), sequencing shifts (work reorders, dependencies emerge), scope changes (items added, removed, or restructured), or work blocks/unblocks. ROADMAP update is part of the commit discipline for any workflow that materially affects milestones — not deferred to "I'll update it later."

**Citation:** `TGF-SYNTHESIS — grounded in NIST-SSDF v1.1 PO.5 + senior practice`. NIST SSDF PO.5 covers configuration management discipline; ROADMAP maintenance specifically is TGF synthesis of observed roadmap-drift failure mode.

**Plain-language impact:** An outdated ROADMAP creates false confidence in project state. A new contributor reads ROADMAP, plans against it, and discovers reality only when their work conflicts with actual current state. A stakeholder reads ROADMAP and makes commitments to other teams based on what's allegedly in progress. The fix is not less roadmap; the fix is keeping the ROADMAP honest. Roadmap that doesn't reflect reality is worse than no roadmap because it confidently misleads.

**Extended discussion:** ROADMAP is a first-class artifact per `CLAUDE.md` §8 — built during onboarding, maintained throughout the project's life, used as input to Stage 1 (Research) and Stage 2 (Scope) of every coding/planning workflow, referenced in Stage 5 Phase 4 (Holistic) review for roadmap alignment.

Maintenance triggers:

- **Milestone advances:** when a phase commit lands that progresses a milestone, the ROADMAP Current Focus pointer updates in the same commit (or the immediately following closeout commit, depending on commit-grouping discipline).
- **Milestone completes:** moved from "In Progress" to "Completed Milestones" with completion date and commit references.
- **Milestone slips:** when reality diverges from a stated target, the slip is surfaced consciously — revise the target with a brief Slip History note, defer, or remove. Silent slips are how ROADMAPs drift.
- **Sequencing shifts:** dependency emerges, blocker discovered, priority shift — the ROADMAP narrative updates to reflect new order.
- **Scope changes:** items added (new feature, new requirement), removed (de-scoped), or restructured (one milestone split into two, two milestones merged).

ROADMAP discipline is reviewed quarterly as part of PROJECT-CONTEXT review per `CLAUDE.md` §8. Slipped milestones surfaced quarterly get conscious decisions rather than accumulating as silent drift.

The ROADMAP is the developer's working plan — not a stakeholder contract. Internal honesty is more valuable than external optics.

**Related anti-patterns:** AP-4 (ROADMAP drift) (see `anti-patterns.md`)

---

## Rule 5.5: Information Disclosure Defaults to Protective

**Statement:** Operational security artifacts — session logs, ERROR-LOG, VENDOR-LOG, WAIVER-LOG, audit findings, threat models, project-context detail on threat surface — are gitignored by default. Adopter projects opt INTO public visibility per artifact, consciously. Default visibility protects the project; transparency is for the adopter, not the world.

**Citation:** `TGF-SYNTHESIS — grounded in CLAUDE.md §12 (Information Disclosure) + senior practice`. The reasoning is captured in `CLAUDE.md` §12 directly; this rule operationalizes it.

**Plain-language impact:** Public visibility of operational security artifacts is reconnaissance gift for attackers. ERROR-LOG entries reveal known vulnerabilities the project is working. VENDOR-LOG entries reveal configuration gaps in third-party services. WAIVER-LOG entries reveal accepted risks the project consciously chose not to mitigate. Threat model documents reveal attack surface design. Session logs reveal working operational state. An attacker doing reconnaissance on a publicly-visible project with all of these committed has a head start equivalent to weeks of internal investigation.

**Extended discussion:** Per `CLAUDE.md` §12, TGF's `.gitignore` template protects:

- Audit findings and threat models
- Error logs containing known vulnerabilities
- Vendor logs revealing configuration gaps
- Waiver logs revealing accepted risks
- Project context describing threat surface
- ROADMAP revealing future direction (when sensitive)
- Session logs

Adopters with team-shared or open-source projects may want to commit some artifacts:

- **DECISIONS.md** is commonly committed for transparency about architectural rationale — this is a conscious choice, not a default.
- **ROADMAP.md** may be committed when the project benefits from public milestone visibility (typical for open-source projects building community).
- **Public CHANGELOG.md** is standard for libraries and tools.

The pattern: default protective, opt INTO transparency, document the decision in DECISIONS.md (e.g., "DEC-N: ROADMAP committed for OSS community visibility; ERROR/VENDOR/WAIVER remain gitignored").

For projects with compliance scope (SOC 2, HIPAA, etc.), certain artifacts must be preservable for audit. The framework surfaces backup discipline during PROJECT-CONTEXT for compliance-relevant projects — gitignored locally is fine, but the artifacts must survive developer continuity issues (laptop loss, role change). External backup to a private location (private repo, secure storage) satisfies both requirements.

**Related anti-patterns:** AP-7 (session log committed to public repo) (see `anti-patterns.md`)

---

## Rule 5.6: Capture WHY, Not Just WHAT

**Statement:** Session logs and ADRs capture reasoning: alternatives weighed, trade-offs accepted, constraints that drove the choice, revisit conditions. "We chose X" without those is operationally useless. The WHY is what survives when context changes — future maintainers can re-evaluate intelligently only if the original reasoning is preserved.

**Citation:** `TGF-SYNTHESIS — grounded in ADR-NYGARD (2011) + senior practice`. Nygard's original ADR paper emphasizes context and consequences as load-bearing sections; this rule generalizes that discipline to all durable memory artifacts.

**Plain-language impact:** Operational memory that captures only outcomes leaves future maintainers with no basis for re-evaluation. "We chose Postgres" tells them nothing about whether the choice still applies in 2028. "We chose Postgres because we evaluated MongoDB and rejected it on join cost, and we accepted the operational complexity of running a relational DB in exchange for analytical query expressiveness; the analytical workload was the constraint, and if that workload changes we should re-evaluate" tells them how to think about the decision when context changes.

**Extended discussion:** The WHY has three components worth preserving:

1. **Alternatives considered.** Future maintainers can avoid re-evaluating rejected paths if they know the path was evaluated and why it was rejected. "We considered MongoDB" closes a loop that "We chose Postgres" leaves open.

2. **Trade-offs accepted.** Every architectural decision accepts costs. Capturing the trade-off makes the cost legible. "We chose REST over GraphQL because the team is small and REST tooling is more mature; we accept the cost of over-fetching on some endpoints" tells the future maintainer where the friction will appear.

3. **Constraints that drove the choice.** Decisions are often driven by constraints external to the technical merit — team size, deadline, existing infrastructure, vendor relationships, compliance scope. When the constraint changes, the decision should be re-evaluated. Capturing the constraint flags the trigger.

AI-generated session logs and ADRs tend to capture WHAT cleanly and skip WHY unless prompted. The WHY often lives in the conversation that led to the decision; if the session log summarizes outcomes only, the WHY is lost. Defense: prompt explicitly for alternatives, trade-offs, and constraints when generating durable memory.

A useful sanity check: "if a new developer reads this entry six months from now, do they have enough to re-evaluate the decision when their context is different?" If no, the WHY is missing.

**Related anti-patterns:** AP-1 (decision-only entry), AP-8 (amended in place loses WHY) (see `anti-patterns.md`)

---
