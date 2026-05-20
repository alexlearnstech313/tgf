# Anti-Patterns + Canonical Patterns — CONTINUITY

Full anti-pattern + canonical pattern pairs with concrete examples. Referenced from `SKILL.md` §6 Anti-Pattern Summaries. Loaded on demand when concrete examples are needed (typically Stage 5 Phase 4 Holistic Review or Stage 6 Commit when a continuity issue surfaces).

Eight anti-pattern pairs covering the most common continuity failures observed in operational practice. Per `DEC-2026-05-17-003` Clause 1: every anti-pattern is paired with a canonical pattern.

Examples below are markdown excerpts (the artifacts CONTINUITY governs are documentation) rather than code. The discipline is the same: show what to reject and what to write instead.

---

## AP-1: Decision-only session log entry

**Pattern:**

```markdown
# Session Log: 2026-03-15-session-01

## Decisions
- Chose Postgres for the analytics database.
- Going with Tailwind for styling.
- Auth handled by Auth0.
```

**Violates:** Rule 5.6 (capture WHY, not just WHAT). See `rules.md#rule-56-capture-why-not-just-what`.

**Why it fails:** Six months later, a maintainer asks "why Postgres and not the new graph DB everyone's using?" The session log answers "because we chose Postgres." That tells the maintainer nothing. The decision then gets re-evaluated from scratch — possibly to the same answer (wasted re-evaluation work), possibly to a different answer because the team forgot why Postgres was right in the first place (regression risk). The WHY behind every load-bearing choice has been thrown away at session close.

**Source for failure mode:** Common AI-summarization failure mode — output-only summaries strip rationale. See OWASP LLM Top 10:2025 `LLM09:2025` (Misinformation, including fabricated or incomplete history).

### CP-1: Entry with WHY preserved

**Pattern:**

```markdown
# Session Log: 2026-03-15-session-01

## Decisions

### Postgres for analytics database
- **Decided:** Postgres 15 for the analytics database.
- **Alternatives considered:** MongoDB (rejected — analytical query workload requires
  relational joins; MongoDB's aggregation pipeline has cost overhead we benchmarked at
  3-8x for our query shapes). DuckDB (rejected — single-node embedded model doesn't
  fit our deployment pattern).
- **Trade-offs accepted:** Higher operational complexity than embedded options;
  schema migration discipline becomes load-bearing.
- **Revisit if:** workload shifts away from joins, or DuckDB clustering matures
  enough to handle our scale.

### Tailwind for styling
- **Decided:** Tailwind CSS 4.x for component styling.
- **Alternatives considered:** CSS Modules (team prefers utility-first; smaller
  team means convention discipline wins over flexibility). styled-components
  (rejected — runtime cost, build complexity for our use case).
- **Trade-offs accepted:** Verbose JSX; mitigated by reusable component
  abstractions in components/ui/.

### Auth0 for authentication
- **Decided:** Auth0 for authentication; sessions managed via JWT.
- **Alternatives considered:** Clerk (close second; pricing tipped us to Auth0
  for current scale, revisit at 10K MAU). Supabase Auth (rejected — we don't
  want our entire data layer coupled to one vendor).
- **Trade-offs accepted:** Vendor lock-in on authentication primitives; revisit
  annually.
```

**Pairs with:** Anti-pattern AP-1

**Why it works:** Every decision captures alternatives, trade-offs, and revisit conditions. A maintainer six months later reading "why Postgres?" finds the analytical-join constraint, the MongoDB benchmark, and the revisit trigger. They can re-evaluate intelligently when their context changes (e.g., if the workload shifts) rather than starting from zero.

**Additional considerations:** Significant decisions in a session log entry often warrant promotion to an ADR in DECISIONS.md per Rule 5.2. Session log captures the decision in context; the ADR captures it as a durable architectural record. The two can co-exist — the session log links to the ADR, the ADR's Context section may reference the originating session.

---

## AP-2: Architectural decision buried in commit message

**Pattern:**

```
$ git log --oneline -5
af8d2c1 Switch auth from JWT to session cookies
3c91f2a Add user dashboard
9bda44e Fix navigation bug
e7c8a01 Update dependencies
1f3e29b Initial commit
```

```
$ git show af8d2c1
commit af8d2c1
Author: Dev <dev@example.com>
Date:   Wed Feb 14 09:32:15 2026

    Switch auth from JWT to session cookies

    Decided to switch from JWT-based auth to server-side sessions
    with secure cookies. The XSS risk on JWT-in-localStorage was
    too high for our threat model, and we benchmarked session
    lookup overhead and it's negligible. This is a fundamental
    change to how auth works.
```

`DECISIONS.md` contains no mention of this.

**Violates:** Rule 5.2 (architectural decisions get ADRs). See `rules.md#rule-52-architectural-decisions-get-adrs`.

**Why it fails:** The decision IS captured — kind of. But it's captured in a place where future maintainers will not look. New contributors read `DECISIONS.md` to understand the project's architectural direction; they do not `git log --grep "auth"` to discover what was decided. Months later, someone proposes "let's go back to JWT, it's simpler" and there's no visible record of the prior evaluation and rejection. The decision gets relitigated from scratch, possibly reversing for reasons that were already considered.

Also, commit messages are tied to single commits. An ADR can be referenced from many commits over time; a commit message is a per-event record, not a durable artifact.

**Source for failure mode:** Common AI-assisted-development failure mode — AI is good at writing commit messages and tends to put substantive content there. Without explicit ADR prompting, architectural reasoning lives in commit-message-only form.

### CP-2: ADR in DECISIONS.md + commit message references the ADR

**Pattern:**

```markdown
# DECISIONS.md

---

## DEC-2026-02-14-001: Authentication via server-side sessions, not JWT in localStorage

**Decided:** Server-side sessions with secure HTTP-only cookies for authentication;
JWT-in-localStorage pattern rejected.

**Date:** 2026-02-14

**Context:** Initial auth implementation used JWT stored in localStorage. Threat
modeling surfaced that XSS in our SPA (we run user-provided content in some
contexts) would compromise tokens. Token theft would let an attacker impersonate
the user for the token's full lifetime, and there's no revocation mechanism
without rebuilding the entire token-management story.

**Decision:** Switch to server-side sessions with cookies. Session ID in
HTTP-only Secure SameSite=Lax cookie. Server maintains session store
(Postgres-backed) with explicit revocation. Logout revokes server-side; token
theft mitigated by HTTP-only flag preventing JS access; SameSite=Lax mitigates
CSRF; Secure flag prevents transmission over HTTP.

**Alternatives considered:**
- JWT-in-localStorage (rejected — XSS exposure)
- JWT-in-httpOnly-cookie (closer — but still no server-side revocation, and
  token validation cost is higher than session lookup at our scale)
- OAuth-token rotation (rejected — operationally heavy for our use case)

**Consequences:**
- Session store in Postgres becomes load-bearing for auth; requires backup/HA
  considerations
- Multi-region deploys need session replication strategy (deferred until
  multi-region is on roadmap)
- Logout becomes a real action (revoke session) rather than client-side
  token-discard
```

```
$ git show af8d2c1
commit af8d2c1
Date:   Wed Feb 14 09:32:15 2026

    Switch auth from JWT to session cookies per DEC-2026-02-14-001

    Server-side sessions with secure HTTP-only cookies; full rationale
    in DECISIONS.md DEC-2026-02-14-001. Schema migration: sessions table
    added (see migrations/0042_sessions_table.sql).
```

**Pairs with:** Anti-pattern AP-2

**Why it works:** The architectural reasoning lives in DECISIONS.md where it's discoverable. The commit message references the ADR by ID, providing the cross-link. Future maintainers reading DECISIONS.md see the decision in proper context; future maintainers reading the commit can navigate back to the ADR for full rationale. The decision is durable beyond any single commit.

**Additional considerations:** For very small decisions (e.g., "we chose `fastify` over `express` for the new service"), the threshold question is: will a future maintainer need to understand this? If yes, ADR. If no (tactical decision with no downstream constraint), session log is sufficient.

---

## AP-3: Ephemeral todo list as project memory

**Pattern:**

A `todo.txt` file in the repo root:

```
- fix the email validation regex (allows trailing dots)
- look into why the staging deploy takes 8 minutes
- ask Alex about the Stripe webhook secret rotation
- the dashboard query is slow when there are >1000 orders
- need to upgrade pg-driver, current version has a CVE
```

`ERROR-LOG.md` does not exist. The `todo.txt` is gitignored "because it's just personal notes."

**Violates:** Rule 5.3 (three-log routing discipline). See `rules.md#rule-53-three-log-routing-discipline`.

**Why it fails:** The items in this list span three distinct action profiles, but they're all treated as "personal notes":

- The email validation regex bug and the slow dashboard query are bugs → `ERROR-LOG.md`
- The Stripe webhook secret rotation is a vendor action → `VENDOR-LOG.md`
- The pg-driver CVE is a security finding → `ERROR-LOG.md` (high severity)
- The 8-minute staging deploy is investigation needed → `ERROR-LOG.md`

By keeping all of these in one personal todo file:
- No one else can see them (single point of failure on continuity)
- They have no severity, status, owner, or target — so they don't get prioritized
- A reader cannot tell what's actively being worked vs what's waiting on someone else vs what's a known CVE
- When the file gets cleared "to start fresh," the items are lost

**Source for failure mode:** Common operational pattern in solo/small-team projects — personal todo lists substitute for routed operational logs because "I'll remember." Memory fails; lists get cleared; rotation happens.

### CP-3: Routed entries with severity / status / owner / target

**Pattern:**

```markdown
# ERROR-LOG.md

## Open

### ERR-2026-03-15-001: pg-driver has known CVE (CVE-2026-12345)
- **Severity:** High
- **Status:** In progress — upgrade in PR #142
- **Owner:** alex
- **Target:** 2026-03-16
- **Notes:** CVE allows SQL injection via NUMERIC type handling in versions <8.7.3.
  Our current version is 8.5.0. Upgrade to 8.7.4 in PR #142.

### ERR-2026-03-15-002: Email validation regex allows trailing dots
- **Severity:** Medium
- **Status:** Open
- **Owner:** unassigned
- **Target:** Next bugfix cycle (2026-03-22)
- **Notes:** `user@example.com.` validates as true; not RFC-5322 compliant.

### ERR-2026-03-15-003: Dashboard query slow at >1000 orders
- **Severity:** Medium
- **Status:** Investigating
- **Owner:** alex
- **Target:** TBD pending root cause
- **Notes:** P99 query time 2.4s at 1000+ orders, 80ms at <100. Likely missing
  composite index on (customer_id, created_at).
```

```markdown
# VENDOR-LOG.md

## Open

### VEN-2026-03-15-001: Rotate Stripe webhook secret
- **System:** Stripe dashboard
- **Action:** Generate new webhook signing secret; update STRIPE_WEBHOOK_SECRET
  in Vercel env (production); cycle staging.
- **Status:** Open
- **Target:** 2026-03-20 (quarterly rotation)
- **Owner:** alex
```

**Pairs with:** Anti-pattern AP-3

**Why it works:** Each finding has the metadata it needs to be acted on: severity drives priority, status tells the next reader where it stands, owner tells the next reader who to talk to, target sets the cadence. The logs are routed so vendor actions don't get lost in code-bug priority discussions. Items survive personnel changes because they're durable artifacts, not personal notes.

**Additional considerations:** For solo projects, "owner" may always be the same person — that's fine. The discipline of writing it makes the implicit explicit, and protects against future contributors not knowing what's owned by whom.

---

## AP-4: ROADMAP drift

**Pattern:**

```markdown
# ROADMAP.md
*Last updated: 2025-09-10*

## Current Focus
Phase 3: implementing user authentication. Estimated completion: 2025-10-15.

## Next Up
- Phase 4: payment integration
- Phase 5: admin dashboard
```

Today's date: 2026-03-15. The team finished Phase 3 in November, finished Phase 4 in January, and is currently working on Phase 6 (a major refactor scoped after the original roadmap was written).

**Violates:** Rule 5.4 (ROADMAP reflects current reality). See `rules.md#rule-54-roadmap-reflects-current-reality`.

**Why it fails:** A new contributor opens ROADMAP and reads "Phase 3 in progress, payment integration next." They start planning their work assuming the project is at that point. Their first conversation with the existing team is "what do you mean we're on Phase 6?" Every assumption built on the stale ROADMAP — sequencing, dependencies, scope — has to be rebuilt. The ROADMAP that confidently misleads is more expensive than no ROADMAP.

Similarly, stakeholders making commitments to other teams (sales, marketing) based on the stale ROADMAP make promises against fiction. By the time reality is reconciled, expectations are misaligned.

**Source for failure mode:** Universal operational failure mode in projects that treat ROADMAP as "set at the start." TGF treats ROADMAP as living documentation maintained at every milestone change.

### CP-4: ROADMAP updated as part of commit discipline

**Pattern:**

```markdown
# ROADMAP.md
*Last updated: 2026-03-15*

**Current Focus:** Phase 6: Database performance refactor — scoped 2026-02-20
after the dashboard slowness incident (see ERR-2026-02-15-003 resolution).
Estimated completion: 2026-04-30.

## Phase Status

| Phase | Description | Status | Completed |
|-------|-------------|--------|-----------|
| 1 | Project scaffolding | ✅ Complete | 2025-07 |
| 2 | Core API endpoints | ✅ Complete | 2025-08 |
| 3 | User authentication (DEC-2026-02-14-001 amended this) | ✅ Complete | 2025-11-12 |
| 4 | Payment integration | ✅ Complete | 2026-01-08 |
| 5 | Admin dashboard | ✅ Complete | 2026-02-10 |
| 6 | Database performance refactor | 🟡 In progress | — |
| 7 | Multi-region deploy | ⬜ Not started | — |

## Slip History

- Phase 3 originally targeted 2025-10-15; slipped to 2025-11-12 due to
  DEC-2026-02-14-001 (auth strategy change midway). Captured as conscious
  slip not silent drift.
```

```
$ git log --oneline -5 ROADMAP.md
b8c4d2 Phase 5 ✅ complete; Phase 6 scoped after dashboard incident
af8d2c Phase 4 ✅ complete; Phase 5 active
3c91f2 Phase 3 ✅ complete (slipped per DEC-2026-02-14-001)
9bda44 Phase 2 ✅ complete
e7c8a0 Initial ROADMAP for v0.1
```

**Pairs with:** Anti-pattern AP-4

**Why it works:** ROADMAP reflects current state because it's updated as a deliverable of each milestone commit. Slip history surfaces conscious decisions where reality diverged from targets. Cross-references to ADRs and ERROR-LOG entries connect the ROADMAP narrative to the artifacts that drove changes. A new contributor reading this ROADMAP sees the project's actual current state, not its historical aspiration.

**Additional considerations:** ROADMAP is reviewed quarterly per `CLAUDE.md` §8 as part of PROJECT-CONTEXT review. The quarterly review catches the rare case where commit-time updates missed something — but the primary discipline is updating at the commit, not waiting for the quarterly.

---

## AP-5: Waiver without revisit condition

**Pattern:**

```markdown
# WAIVER-LOG.md

## Accepted Risks

### Rate limiting not implemented on login endpoint
- Risk: Brute force attempt against user passwords.
- Rationale: Small user base, low risk currently.
- Severity: Medium
```

**Violates:** Rule 5.3 (three-log routing discipline). See `rules.md#rule-53-three-log-routing-discipline`.

**Why it fails:** Without a revisit condition, the waiver becomes permanent by default. The "small user base" rationale was true when written; in 18 months the project has 50,000 users and rate limiting still isn't implemented because no one re-evaluated. The waiver is now lying — the rationale no longer matches reality, but the artifact still reads as a current decision. Worse, the project's risk posture is wrong on paper: the WAIVER-LOG says "we considered this and decided not to act"; reality is "we forgot to revisit."

**Source for failure mode:** Universal operational failure mode in formal risk acceptance — waivers without revisit conditions are how organizations end up with risk registers that don't reflect actual risk posture.

### CP-5: Waiver with explicit revisit condition

**Pattern:**

```markdown
# WAIVER-LOG.md

## Accepted Risks

### WAV-2026-03-15-001: Rate limiting not implemented on login endpoint
- **Risk:** Brute force attempt against user passwords. Could enable credential
  stuffing if user passwords are weak and from breach corpus.
- **Severity:** Medium
- **Date accepted:** 2026-03-15
- **Rationale for acceptance:** Current user base ~50 users; bcrypt cost 12
  provides ~250ms per attempt, making meaningful brute force impractical at
  current scale. Implementing rate limiting requires Redis or similar shared
  state which we haven't deployed yet.
- **Revisit condition (whichever is first):**
  1. User base exceeds 1,000 MAU
  2. We deploy Redis for another reason (caching, queues)
  3. Date: 2026-09-01 (six months from acceptance)
- **Mitigations in place:** bcrypt cost 12; failed login attempts logged per
  Rule 5.7 (SECURITY-CORE) and surfaced in weekly review.
- **Owner for revisit:** alex
```

**Pairs with:** Anti-pattern AP-5

**Why it works:** Every component the original was missing is now present: explicit acceptance date, three revisit triggers (any of which fires the re-evaluation), explicit mitigations that justify the current acceptance, owner for the revisit. The waiver has a clear lifecycle — when any trigger fires, the owner re-evaluates. The waiver stops being a permanent silent risk and becomes a tracked, time-bounded accepted risk.

**Additional considerations:** Revisit conditions should be objectively checkable. "When we have more users" is vague; "when we exceed 1,000 MAU" is checkable from product analytics. "When we have time" is permanent; "by 2026-09-01" is a calendar reminder.

---

## AP-6: Vendor action conflated with code error

**Pattern:**

```markdown
# ERROR-LOG.md

## Open

### ERR-2026-03-15-005: Stripe webhook signing secret needs rotation
- **Severity:** High
- **Status:** Open
- **Owner:** alex
- **Target:** ASAP
- **Notes:** Quarterly rotation policy. Need to generate new secret in Stripe
  dashboard, update env vars in Vercel, restart workers.
```

**Violates:** Rule 5.3 (three-log routing discipline). See `rules.md#rule-53-three-log-routing-discipline`.

**Why it fails:** This entry is in ERROR-LOG, which is for code issues being worked. A developer opening ERROR-LOG to triage code bugs sees this entry mixed with actual code issues, has to mentally filter it out, and may waste effort trying to "fix it in the codebase" when the action is entirely external. Meanwhile, VENDOR-LOG is empty, so a quick scan of "what's pending in external systems?" yields nothing despite a real pending vendor action existing.

Routing matters for action profile: code bugs get worked at code-review cadence; vendor actions get scheduled with someone-with-credentials at vendor-action cadence. Mixed in the wrong log, vendor actions get either rushed (in ERROR-LOG style) or forgotten (because they don't match the code-error mental model the reader applies).

**Source for failure mode:** Common operational confusion in solo/small teams — "everything that needs doing goes in one log."

### CP-6: VENDOR-LOG entry with system / action / status / target

**Pattern:**

```markdown
# VENDOR-LOG.md

## Open

### VEN-2026-03-15-001: Rotate Stripe webhook signing secret
- **System:** Stripe (dashboard.stripe.com → Developers → Webhooks)
- **Action:** Generate new signing secret for production webhook endpoint;
  update STRIPE_WEBHOOK_SECRET in Vercel production env; cycle staging next
  business day.
- **Status:** Open
- **Target:** 2026-03-20 (quarterly rotation due)
- **Owner:** alex
- **Notes:** Requires Stripe dashboard owner access. Rotation cadence is
  quarterly per security-secrets-management policy.
- **Verification after rotation:** trigger test webhook event from Stripe
  dashboard; confirm signature verification succeeds in production logs.
```

**Pairs with:** Anti-pattern AP-6

**Why it works:** Routed to VENDOR-LOG where it belongs. Includes the system context (which dashboard, where in the dashboard), the precise action, dependencies (Vercel env update), verification step. A reader scanning VENDOR-LOG sees a clear pending vendor action with everything needed to execute it. ERROR-LOG stays focused on code issues; the two logs serve their distinct purposes.

**Additional considerations:** Some actions span both code and vendor — e.g., "implement OAuth flow" requires both Auth0 dashboard setup AND code. Split into linked entries: VEN-N for the dashboard work, ERR-N or session-log entry for the code implementation, cross-reference each other. The split keeps the action profiles clean while preserving the relationship.

---

## AP-7: Session log committed to public repo

**Pattern:**

`.gitignore` has no entry for `.sessions/`. The `.sessions/` directory is committed and pushed to the public GitHub repository. A session log entry from last week:

```markdown
# Session Log: 2026-03-08-session-01

## Findings
- The admin endpoint /api/admin/users still has the auth check commented out
  from the debugging session last month. Need to restore before launch.
- Database backup is configured but we've never tested restore.
- The Stripe webhook secret on staging is the same as production — known issue
  but we haven't rotated yet.

## Open Questions
- Where does the JWT signing key get rotated? Can't find docs on this.
- Is the `/api/internal/*` namespace actually internal-only, or just hoped-to-be?
```

**Violates:** Rule 5.5 (information disclosure defaults to protective). See `rules.md#rule-55-information-disclosure-defaults-to-protective`.

**Why it fails:** This session log is a reconnaissance gift to anyone scanning the public repo:

- The admin endpoint with commented-out auth is named explicitly
- Backup-restore status (untested) is disclosed
- Cross-environment secret reuse is disclosed (staging = production for Stripe webhook)
- Unknown key-rotation procedure is disclosed
- Uncertainty about internal endpoint reachability is disclosed

An attacker who finds this log knows exactly where to probe first: `/api/admin/users`, `/api/internal/*`, plus a hint that the Stripe webhook secret is a possible credential-reuse target. The project just told the attacker its weak points.

**Source for failure mode:** Common adopter error when migrating to TGF or any structured operational logging — the artifacts are useful, the gitignore discipline is missed.

### CP-7: .gitignore protects operational state

**Pattern:**

```
# .gitignore

# Operational state — gitignored per CLAUDE.md §12 and CONTINUITY Rule 5.5
.sessions/
.tgf/

# Operational logs (commit only if conscious decision per DEC-N)
ERROR-LOG.md
VENDOR-LOG.md
WAIVER-LOG.md
docs/THREAT-MODEL.md
docs/BASELINE-AUDIT.md
docs/PROJECT-CONTEXT.md

# Standard editor / OS / env
.env
.env.local
.DS_Store
node_modules/
```

For artifacts the project DOES want public (e.g., `ROADMAP.md`, `DECISIONS.md`, `CHANGELOG.md`), document the decision:

```markdown
# DECISIONS.md

## DEC-2026-03-15-007: Commit ROADMAP and DECISIONS publicly; protect operational logs

**Decided:** ROADMAP.md, DECISIONS.md, and CHANGELOG.md are committed and
publicly visible. ERROR-LOG.md, VENDOR-LOG.md, WAIVER-LOG.md, session logs,
and threat model documents remain gitignored.

**Date:** 2026-03-15

**Context:** Project is open-source; community benefits from visibility into
architectural decisions and roadmap direction. However, operational state
(known vulnerabilities being worked, accepted risks, vendor configuration
gaps) is reconnaissance material for attackers and remains protected per
CLAUDE.md §12 and CONTINUITY Rule 5.5.

**Decision:** Update .gitignore template to protect operational logs by default.
Public-by-design artifacts (ROADMAP, DECISIONS, CHANGELOG) tracked normally.

**Alternatives considered:**
- All artifacts public — rejected; operational state disclosure outweighs
  community-visibility benefit
- All artifacts private — rejected; community contribution requires visibility
  into roadmap and architectural rationale

**Consequences:**
- New contributors see ROADMAP and DECISIONS via GitHub
- Operational continuity (ERROR/VENDOR/WAIVER) maintained locally; backup
  discipline becomes a personal-laptop continuity concern (see
  PROJECT-CONTEXT.md backup section)
```

**Pairs with:** Anti-pattern AP-7

**Why it works:** Default is protective. Adopters opt INTO public visibility for specific artifacts via a documented decision. The `.gitignore` carries the discipline; the ADR carries the rationale. New artifacts created later default to protected unless and until a similar conscious decision adds them to the public set.

**Additional considerations:** For compliance-scope projects (SOC 2, HIPAA), some operational artifacts must be preservable for audit. Local gitignore + private backup (private repo, secure storage) satisfies both confidentiality and audit-preservation requirements.

---

## AP-8: ADR amended in place rather than superseded

**Pattern:**

```markdown
# DECISIONS.md

## DEC-2025-08-01-001: Use Express for the API server

**Decided:** Fastify for the API server. ← *edited 2026-02-20 after benchmark*

**Date:** 2025-08-01

**Context:** Need an HTTP server framework. Express is the most widely-known
option with the largest ecosystem.

**Decision:** Express 4.x. ← *changed to Fastify 4.x — 2026-02-20*

**Alternatives considered:**
- Fastify (rejected for ecosystem maturity at decision time) ← *reversed — now selected*
- Hapi
- bare http module

**Consequences:**
- All HTTP routes use Express middleware patterns ← *updating to Fastify hooks*
```

**Violates:** Rule 5.2 (architectural decisions get ADRs) AND Rule 5.6 (capture WHY). See `rules.md#rule-52-architectural-decisions-get-adrs`.

**Why it fails:** The decision history is destroyed. The ADR now reads as a hybrid "we chose Fastify on 2025-08-01 (no we didn't, that was Express, but here are the strikethroughs)" — neither the original decision nor the amendment is cleanly captured. A reader cannot tell:

- When the actual switch happened
- Why the original Express decision was made
- What changed between the original decision and the amendment
- What benchmark was run
- What costs the amendment accepted

The amendment notes are stripped of full context (no full ADR structure for the change). Future maintainers reading the strikethrough version cannot reconstruct either decision properly.

**Source for failure mode:** Common AI-assisted documentation failure — when asked "we switched to Fastify, update the ADR," AI may helpfully edit in place rather than write a new amending ADR. Without explicit prompting toward the "supersede, not edit" pattern, the history is lost.

### CP-8: New ADR amending the prior; both remain in DECISIONS.md

**Pattern:**

```markdown
# DECISIONS.md

---

## DEC-2026-02-20-001: Switch API server from Express to Fastify

**Decided:** Migrate the API server from Express to Fastify. Amends DEC-2025-08-01-001
which selected Express.

**Date:** 2026-02-20

**Context:** Original DEC-2025-08-01-001 selected Express 4.x for ecosystem
maturity. Six months in, benchmark results from the high-traffic /api/feed
endpoint show Fastify is 2.3x faster on our route shapes (sustained P99 145ms
on Express vs 62ms on Fastify under same load profile). Fastify ecosystem has
matured to where the original "ecosystem maturity" concern no longer holds —
core plugins we use (auth, validation, swagger) all have first-class Fastify
support.

**Decision:** Migrate all routes to Fastify 4.x. Migration in two phases:
1. Spin up Fastify server alongside Express; route new endpoints to Fastify
2. Migrate existing Express routes incrementally; deprecate Express server
   once all routes ported. Estimated 4 weeks calendar time.

**Alternatives considered:**
- Stay on Express — rejected on benchmark
- Move to bare Node http with our own routing — rejected for maintainability cost
- Switch to Hono — rejected; smaller ecosystem than Fastify for our needs

**Consequences:**
- Middleware patterns change (Express middleware → Fastify hooks)
- Plugins need re-registration in Fastify style
- Migration timeline: 4 weeks; Phase 6 milestone added to ROADMAP for this work
- DEC-2025-08-01-001 amended in effect; original remains as historical record

---

## DEC-2025-08-01-001: Use Express for the API server

*[Amended in effect by DEC-2026-02-20-001. Original decision preserved below as
historical record.]*

**Decided:** Express 4.x for the API server.

**Date:** 2025-08-01

**Context:** Need an HTTP server framework. Express is the most widely-known
option with the largest ecosystem.

**Decision:** Express 4.x.

**Alternatives considered:**
- Fastify (rejected at decision time for ecosystem maturity concerns)
- Hapi
- bare http module

**Consequences:**
- All HTTP routes use Express middleware patterns
```

**Pairs with:** Anti-pattern AP-8

**Why it works:** Both decisions are preserved in full. The original ADR remains as historical record with a one-line note flagging that it's been amended. The new ADR captures the WHAT (switch to Fastify), the WHY (benchmark + ecosystem maturity reassessment), the alternatives reconsidered, and the consequences (migration plan). A future maintainer reading DECISIONS.md sees the current state (DEC-2026-02-20-001 at top) and the historical context (DEC-2025-08-01-001 preserved). The reasoning chain is intact.

**Additional considerations:** For ADRs that are fully reversed (not amended), the same pattern applies — write a new ADR explicitly reversing the prior, with the reversal's rationale. The prior ADR stays as historical record. Never delete an ADR; the decision history is part of the project's memory.

---

## Pairing discipline

Per `DEC-2026-05-17-003` Clause 1: every anti-pattern is paired with a canonical pattern. The framework's value depends on showing the user both what to reject and what to write instead. Standalone anti-patterns without paired canonical patterns are incomplete and do not ship.

When a new continuity anti-pattern is observed during use but no clear canonical pattern is obvious, log to `WAIVER-LOG.md` for revisit rather than shipping a one-sided entry. The `self-evolution.anti-patterns-observed` frontmatter field accumulates candidates for Phase 11 meta-skill review.
