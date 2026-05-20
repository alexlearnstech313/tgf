# Anti-Patterns + Canonical Patterns — PROJECT-MANAGEMENT

Full anti-pattern + canonical pattern pairs with concrete examples. Referenced from `SKILL.md` §6 Anti-Pattern Summaries.

Eight anti-pattern pairs covering the most common planning failures. Examples are ROADMAP excerpts and example dialogues rather than code excerpts, since PROJECT-MANAGEMENT governs planning discipline. Per `DEC-2026-05-17-003` Clause 1: every anti-pattern is paired with a canonical pattern.

---

## AP-1: Architecture-first planning

**Pattern:**

```
User: "I want to build a learning platform for cybersecurity students."

AI: "Great. Here's the architecture:

- Frontend: Next.js 14 with App Router + Server Components
- Backend: Next.js API routes + tRPC for type safety
- Database: PostgreSQL via Supabase + Drizzle ORM
- Auth: Auth0 with email+password and Google OAuth
- Payment: Stripe with subscription billing
- Hosting: Vercel for frontend + Railway for background workers
- CMS: Sanity for lesson content management
- Email: Resend for transactional email
- Analytics: PostHog
- Observability: Sentry + Better Stack

I'll start scaffolding this and we can iterate from here."
```

**Violates:** Rule 5.1 (start from intent, not from patterns). See `rules.md#rule-51-start-from-intent-not-from-patterns`.

**Why it fails:** The user said "learning platform for cybersecurity students" — that's the intent fragment. The AI jumped to a complete architecture without asking: who exactly is the student (early-career? Working pro? Bootcamp grad?); what does "learning" mean (lessons? labs? mentorship? certifications?); what value does the platform deliver vs existing options (TryHackMe, HackTheBox, certifications); what's the business model (free? subscription? employer-paid?); what's the timeline; what's the team size. The architecture decisions made — Auth0 (vendor lock-in, costs at scale), Sanity CMS (expensive for content-heavy projects), Vercel + Railway (additional ops surface) — are all defensible but only against an articulated intent the AI hasn't checked.

**Source for failure mode:** AI pattern-reproduction from training data. Common SaaS architectures dominate the training signal; "ask intent first" is underrepresented.

### CP-1: Intent first, architecture follows from intent

**Pattern:**

```
User: "I want to build a learning platform for cybersecurity students."

AI: "Let me get intent clear before I propose architecture, because the
right stack depends a lot on what the platform actually does:

1. Audience — early-career learners, working professionals, or both?
2. What does 'learning' mean on the platform — video lessons, hands-on
   labs (sandboxes/VMs), study guides for certs, mentorship, or a mix?
3. What's the wedge against existing options (TryHackMe, HackTheBox,
   Cybrary, ISC2 study materials)? What's the unique value?
4. Stage — validation-MVP (learning whether this is wanted), or you've
   validated and want to build for users you have?

If you reply with 1-4, I can propose an architecture that fits. The
modal SaaS stack works for some answers and is overkill or wrong for
others — for example, if labs are core, the architecture is very
different from a video-lessons platform."

User: "1: early-career, 2: hands-on labs + cert prep guides, 3:
existing options are either too theoretical or too expensive — I
want a real-lab platform priced for students, 4: validation-MVP."

AI: "Got it. For a labs-focused validation-MVP at student pricing,
the architecture is different from the modal SaaS:

- Labs runtime: this is the hard part. Self-hosted VM/container
  sandboxes via something like Firecracker microVMs or Tailscale-
  connected ephemeral hosts. Vercel Sandbox might fit; or DigitalOcean
  for cost.
- Frontend: simple. Next.js or Astro. Labs are the product; frontend
  is the lobby.
- Auth: lightweight. Email + magic link via Supabase or similar. Don't
  pay for Auth0 at validation stage.
- Payments: defer until validation. Free tier first; paid tier added
  once you know what students will pay for.

Want me to scope an MVP that proves the labs work for one course-
worth of content, then we plan from there?"
```

**Pairs with:** Anti-pattern AP-1

**Why it works:** Intent surfaced through closed-form questioning (per DISCOVERY Rule 5.2). Architecture flows from intent — labs-first changes the entire shape from a video-lessons SaaS. The proposed validation-MVP is concretely the next step, with subsequent planning surfaced as "we plan from there" rather than over-committed upfront. Stack choices justified against actual constraints.

---

## AP-2: Aspirational ROADMAP

**Pattern:**

```markdown
# ROADMAP.md

## Phase 1 — MVP
- User signup + login
- Lesson player

## Phase 2 — Growth
- Mobile apps (iOS + Android)
- AI tutor with personalized learning paths
- Live mentorship marketplace
- Enterprise tier
- API for third-party integrations
- Multi-language support (10 languages at launch)
- Community forums
- Affiliate program
```

**Violates:** Principle "ROADMAP is committed-to, not aspirational" (per CONTINUITY Rule 5.4). See `rules.md` §4.

**Why it fails:** Phase 2 reads like a feature wish list — eight major workstreams, no sequencing, no constraints surfaced, no indication which (if any) the project actually commits to. A reader can't tell what's planned vs hoped. New contributors plan against fictional commitments. Stakeholders form expectations against items that may never happen. When some items don't get built, the ROADMAP starts contradicting itself silently.

**Source for failure mode:** Common in early-stage projects where excitement about possibility outruns commitment discipline.

### CP-2: ROADMAP is committed-to; aspirational items live elsewhere

**Pattern:**

```markdown
# ROADMAP.md

**Current focus:** Phase 1 — Validation MVP. Estimated completion 2026-08-15.

## Active Milestones

| ID | Milestone | Target | Confidence | Status |
|----|-----------|--------|------------|--------|
| M1 | Validation MVP — labs working for one course (5 students testing) | 2026-08-15 | medium | in progress |
| M2 | Decide pricing model based on M1 feedback | 2026-09-01 | low (depends on M1) | not started |

## Completed Milestones

| ID | Milestone | Completed | Notes |
|----|-----------|-----------|-------|
| M0 | Project scaffolding + auth | 2026-06-01 | Next.js + Supabase Auth |

## Slip History
*No slips yet.*
```

```markdown
# IDEAS.md (separate file)

Items being considered but not committed to. Move to ROADMAP only with
target + confidence.

- Mobile apps — revisit after web validation
- AI tutor — interesting but no validated user demand yet
- Live mentorship marketplace — separate business model question
- Enterprise tier — only if individual MVP shows demand
- API integrations — not in scope until there are clients asking
- Multi-language — defer until English-only validation succeeds
- Community forums — Discord is sufficient at current scale
- Affiliate program — revenue stream question; not relevant pre-validation
```

**Pairs with:** Anti-pattern AP-2

**Why it works:** ROADMAP contains only committed-to items with concrete targets and confidence. Each milestone has a status; slip history surfaces conscious decisions when reality diverges. Aspirational items live in IDEAS.md (a separate, explicitly-not-a-commitment file). Reader can immediately distinguish "what's the project doing" from "what might the project consider." Per CONTINUITY Rule 5.4, the ROADMAP reflects current reality.

**Additional considerations:** The IDEAS file is one acceptable location; backlog tooling (Linear, GitHub Issues with a "candidate" label) is another. The principle is the separation, not the specific tool.

---

## AP-3: MVP defined for engineering convenience

**Pattern:**

```
Team: "Our MVP is signup + login + an empty dashboard that says
'lessons coming soon'. We can ship that in a week."

[Ships in a week. Six users sign up. Zero return. Team interprets
this as 'we need more features' and adds features. Repeats with
no validation that the original premise was sound.]
```

**Violates:** Rule 5.4 (MVP serves users, not engineering ego). See `rules.md#rule-54-mvp-serves-users-not-engineering-ego`.

**Why it fails:** The MVP delivered nothing of the project's core value. Users came expecting to learn something; they got an account and a placeholder. The "viable" part of "Minimum Viable Product" was missing — there was nothing to validate. The team mistakes "ships" for "validates," then adds more without testing whether the core hypothesis works. Each addition delays the actual learning question: "do users want the value we propose to deliver?"

**Source for failure mode:** Confusion between "smallest shippable" and "smallest valuable" — a common product-development failure mode that Eric Ries' Lean Startup framing was developed to address.

### CP-3: MVP = smallest thing that delivers the core value

**Pattern:**

```
Team: "Our MVP is: one complete cybersecurity lab (web-app pentesting
basics) that a student can actually do end-to-end, with the lab
sandbox actually working. No payment, no fancy auth — magic-link sign-in,
five students invited from our network as testers.

We don't ship until a tester can complete the lab and tell us whether
it taught them something useful. That's the validation question.
Estimate: 4 weeks."

[Ships in 4 weeks. Five testers complete the lab. Three say 'this is
genuinely useful, more please'; two say 'too basic, I knew this
already.' Team learns: the value proposition works but audience-
targeting needs sharpening. Plans v2 around 'intermediate-level labs
for working junior security analysts' based on real data.]
```

**Pairs with:** Anti-pattern AP-3

**Why it works:** The MVP delivered the actual value the project proposes — one working lab end-to-end. The validation question was concrete and tested. The result was real signal (three useful / two too-basic) rather than ambiguous noise (zero return on placeholder). Subsequent planning is grounded in user data, not speculation. The "minimum" was non-trivial (4 weeks vs 1 week) because the minimum-valuable threshold required real lab infrastructure — that's the cost of validating the actual hypothesis.

**Additional considerations:** Some validation-MVPs can be extremely lean (a landing page measuring signup interest is a valid validation-MVP for some questions). The discipline is: the MVP must validate the actual hypothesis, not a proxy hypothesis. "Will users sign up" is different from "will users return."

---

## AP-4: Brownfield plan ignoring existing reality

**Pattern:**

```
Team brings on contractor to "modernize the auth system."

Contractor plan: "We'll rebuild auth from scratch using Auth0. Migration
will be straightforward — users re-create accounts on first login.
Estimated 3 weeks."

Existing reality (not surfaced in the plan):
- 5,000 active users on existing auth
- Existing auth integrates with 4 internal services (analytics,
  billing, customer support tool, internal admin)
- Password reset flow has known edge cases that took 6 months to
  surface and resolve
- One paying customer has SSO via custom SAML to existing auth

[Plan ships against an empty-canvas assumption. Three weeks in, the
integration touch points are still being discovered. SAML customer
is blocking the migration. Active users are frustrated by forced
password resets. Estimated 3 weeks turns into estimated 4 months.]
```

**Violates:** Rule 5.3 (brownfield mode — plan around existing reality). See `rules.md#rule-53-brownfield-mode`.

**Why it fails:** The plan treats brownfield as greenfield. "Users re-create accounts" ignores 5,000 active users. "Migration will be straightforward" ignores 4 integration touch points and a custom SAML setup. The plan looks reasonable on paper because the existing reality isn't documented in the plan. When reality intrudes, the plan looks naive — but more critically, the migration becomes risky in ways the plan didn't account for (paying customer downtime, support burden from frustrated users, potential data loss).

**Source for failure mode:** Common consultant/contractor failure when brownfield context isn't surfaced during scoping. Avoidable by triggering BASELINE-AUDIT.

### CP-4: Brownfield plan respects existing reality; migration path explicit

**Pattern:**

```
Team brings on contractor to "modernize the auth system." Contractor
triggers BASELINE-AUDIT before planning (per Rule 5.3).

BASELINE-AUDIT findings:
- 5,000 active users on existing auth
- 4 internal services integrate with existing auth (named)
- Password reset flow has documented edge cases (in ERROR-LOG)
- One paying customer uses custom SAML (in VENDOR-LOG)
- Existing auth tested but mostly via integration tests, not unit

Contractor plan (against actual reality):

Milestone 1 (2 weeks): Add Auth0 alongside existing auth. New
signups go to Auth0; existing users stay on legacy. Both auth
systems work in parallel during migration window.

Milestone 2 (3 weeks): Migrate the 4 internal-service integrations
to Auth0-compatible patterns. Tests written for each integration
point.

Milestone 3 (2 weeks): SAML customer worked with directly to
migrate their flow. Custom SAML supported in Auth0 via custom
connection or maintained as legacy until next contract renewal
(VENDOR-LOG decision).

Milestone 4 (3 weeks): Migrate existing 5,000 users to Auth0 via
seamless "first login on existing creds" flow. No forced password
reset; the user signs in via legacy auth, system creates Auth0
record silently, user is on Auth0 after first login.

Milestone 5 (1 week): Sunset legacy auth code path; archive
removed code in git; document the migration as a DECISIONS.md ADR.

Total estimate: 11 weeks. Higher than the "3 weeks" naive estimate
because the migration respects what exists.
```

**Pairs with:** Anti-pattern AP-4

**Why it works:** BASELINE-AUDIT surfaced the existing reality before planning. Each integration point, paying customer, and existing-user concern is accounted for in a specific milestone. The migration path is explicit (parallel-run during migration window; silent migration on first login; legacy sunset only after parallel period). The estimate is higher than naive estimate, but it's *actually achievable* — the naive estimate would have slipped to ~16 weeks with much more risk.

**Additional considerations:** Strangler-fig refactoring pattern (Martin Fowler) is the canonical name for "parallel-run new alongside old until old can be retired." Brownfield migrations are usually strangler-fig.

---

## AP-5: Hidden dependencies

**Pattern:**

```markdown
# ROADMAP.md

## Active Milestones

| ID | Milestone | Target | Confidence | Status |
|----|-----------|--------|------------|--------|
| M3 | Admin dashboard | 2026-07-01 | medium | in progress |
| M4 | User reporting (CSV export) | 2026-07-15 | medium | not started |
| M5 | Email notifications | 2026-08-01 | medium | not started |
```

[Three weeks in: M3 slips two weeks. Team starts M4 in parallel.
Halfway through M4, team realizes the CSV export needs the
schema decisions made in M3 (specifically, the admin-facing
schema for filter parameters and tenant context). M4 work
to-date is partially wasted; rework begins. M5 was supposed
to start after M4 but is now also blocked because M5's templates
reference data shapes from M4 which was rebuilt mid-flight.]
```

**Violates:** Rule 5.6 (surface dependencies before committing). See `rules.md#rule-56-surface-dependencies-before-committing`.

**Why it fails:** M3, M4, M5 look parallel in the ROADMAP — no dependency notation. In reality, M4 depends on M3's schema decisions; M5 depends on M4's data shapes. When M3 slips, the cascade is invisible until execution. Rework cost is significant; trust erodes ("why didn't anyone notice?"); planning rounds going forward feel less reliable.

**Source for failure mode:** Common ROADMAP failure when dependencies are obvious to the planner but not made explicit in the document.

### CP-5: Dependencies surfaced explicitly in ROADMAP

**Pattern:**

```markdown
# ROADMAP.md

## Active Milestones

| ID | Milestone | Target | Confidence | Status | Dependencies |
|----|-----------|--------|------------|--------|--------------|
| M3 | Admin dashboard (includes admin-schema decisions for tenant filtering) | 2026-07-01 | medium | in progress | — |
| M4 | User reporting CSV export | 2026-07-15 | medium | not started | M3 (admin-schema for filter params) |
| M5 | Email notifications | 2026-08-01 | medium | not started | M4 (data shapes referenced in templates) |
```

[Three weeks in: M3 slips two weeks. Visible in ROADMAP that M4
and M5 cascade. Team consciously re-sequences — either delays
M4/M5 in line with M3 slip, or extracts M3's schema decisions
as a separate sub-milestone (M3a) to unblock M4 partially. The
decision is conscious; the re-sequencing is documented; the
slip history captures what changed and why.]
```

**Pairs with:** Anti-pattern AP-5

**Why it works:** Dependencies named in the ROADMAP table — M4 depends on M3 (with specific reason); M5 depends on M4. When M3 slips, the cascade is visible. Re-sequencing decisions are conscious — the team can extract sub-milestones, defer downstream work, or commit to the cascade. The ROADMAP reflects what's actually happening; surprises are minimized; trust is preserved.

**Additional considerations:** The dependencies column doesn't have to be elaborate — a short "M3 (reason)" reference is enough to make the cascade visible. The discipline is naming the dependency at planning time, not at execution time.

---

## AP-6: Best-practice decomposition without constraint awareness

**Pattern:**

```
Solo founder, 4-week deadline before a demo for potential investors.
Plan from AI assistant:

Phase 1 (week 1): Set up CI/CD with GitHub Actions, deploy preview
environments, configure feature flags via LaunchDarkly, set up
observability stack (Sentry + Better Stack), add Snyk for security
scanning.

Phase 2 (week 2): Implement infrastructure-as-code via Terraform,
configure DNS, set up CloudFront CDN, configure WAF rules.

Phase 3 (week 3): User auth (Auth0), database schema, API scaffold,
admin dashboard scaffold, monitoring dashboards.

Phase 4 (week 4): Build the actual product features.
```

**Violates:** Rule 5.5 (decompose against real constraints). See `rules.md#rule-55-decompose-against-real-constraints`.

**Why it fails:** Three weeks of infrastructure for a one-week implementation. The plan reads like best-practice ops setup for a Series A startup, applied to a solo-founder demo. By the demo, the founder has working CI/CD and zero working product features. The "best practice" sequencing ignored the real constraint (4-week deadline, demo-driven validation, solo capacity).

**Source for failure mode:** AI pattern reproduction from training data — the architecture of mature companies is over-represented; the architecture of pre-validation-MVP work is under-represented. Best-practice advice applied without constraint awareness.

### CP-6: Decompose against actual constraints

**Pattern:**

```
Solo founder, 4-week deadline before a demo for potential investors.
Plan from AI assistant after constraint surface:

Constraints surfaced:
- 4-week deadline (hard — demo date is set)
- Solo capacity (~30 hours/week of focused work)
- Demo audience: investors looking for product traction, not ops maturity
- Stage: pre-validation MVP

Plan:

Week 1: Skeleton — Next.js scaffold, single core feature (the
demo-able one), local dev only, manual deploy to Vercel via
'vercel deploy'. No CI/CD yet.

Week 2-3: Core feature deep work — make the demo-able feature
actually work end-to-end. One user (you) testing it.

Week 4: Polish for demo — clean up UX, add the 2-3 supporting
features that make the demo make sense, video walkthrough as
backup if live demo fails.

Deferred to post-demo (if investment proceeds):
- CI/CD (week 1 post-demo)
- Observability stack (need traffic to justify)
- Infrastructure-as-code (need scale to justify)
- Security scanning (need attack surface beyond Vercel defaults)
- Multi-environment (need staging if launching)

The demo proves the product matters. Investment proves the project
deserves the ops investment. Don't invert.
```

**Pairs with:** Anti-pattern AP-6

**Why it works:** Constraints surfaced explicitly (deadline, capacity, audience expectations, project stage). Plan respects all of them — week 1 starts on the product feature, not on infrastructure. Deferred items are named with their re-evaluation triggers ("when investment proceeds", "when traffic justifies"). The founder ships a working demo; ops maturity is added when it actually earns its place.

---

## AP-7: Stack-first selection

**Pattern:**

```
User: "I want to build an internal tool for managing customer
escalations."

AI: "I recommend Kubernetes with a microservices architecture —
one service for customer data, one for escalation workflow, one
for notifications. We'll use Istio for service mesh, deploy on
GKE, use gRPC between services. For the frontend, Remix with
the new SSR patterns. Database per service via Postgres."
```

**Violates:** Rule 5.1 (start from intent, not from patterns) AND Rule 5.5 (decompose against real constraints). See `rules.md` for both.

**Why it fails:** "Internal tool for managing customer escalations" is probably a 5-screen app used by ~10 support reps with maybe 1,000 escalations a day. Kubernetes + microservices + service mesh + gRPC is a stack designed for ~1,000 engineers working on a system with ~1 million users. The stack mismatch will cost the project 10x its actual complexity budget in operational overhead, with zero benefit at this scale. The AI proposed the stack without checking scale, team, or actual requirements.

**Source for failure mode:** Same as AP-1 — AI pattern reproduction from training data over-represents mature large-scale systems.

### CP-7: Stack matched to actual scale and constraints

**Pattern:**

```
User: "I want to build an internal tool for managing customer
escalations."

AI: "Quick scale check before I propose stack:

1. Users — how many support reps will use it concurrently? 5, 50, 500?
2. Volume — escalations per day, roughly?
3. Existing stack — anything the team already knows or has deployed?

Without these, I'd guess 'small internal tool' and propose a
minimal stack. The stack for a 5-rep team with 100 escalations/day
is very different from a 500-rep call center."

User: "10 reps, ~1,000 escalations/day, we run Next.js + Postgres
elsewhere."

AI: "Got it. For that scale on a stack you already know:

- Next.js app (you already know the stack)
- Postgres for escalations + linked customer data (one database;
  no service split needed)
- Server-side rendered admin views; light client-side state
- Deploy to Vercel or wherever you deploy the existing apps
- Auth via your existing auth (don't add a new auth system)

No Kubernetes, no microservices, no service mesh — none of that
earns its place at this scale and team size. If escalation volume
grows 10x or team grows 5x, we can revisit. For now, the boring
known stack is the right one."
```

**Pairs with:** Anti-pattern AP-7

**Why it works:** Scale and constraint context surfaced before stack proposal. The recommended stack matches the actual problem (internal tool, modest scale, existing team competency). The deferred-decision boundary ("if escalation volume grows 10x") is explicit. Boring tech earns its place; clever tech is reserved for when constraints demand it.

---

## AP-8: ROADMAP drift unchallenged

**Pattern:**

```markdown
# ROADMAP.md (last updated 2025-09-10)

**Current focus:** Phase 3 — user authentication. Target: 2025-10-15.

## Active Milestones
| M3 | Authentication | 2025-10-15 | medium | in progress |
| M4 | Payments | 2025-11-30 | medium | not started |
```

[Today: 2026-03-15. Team finished M3 in November. Finished M4 in
January. Is currently working on M6 (database performance refactor)
which wasn't in the original ROADMAP. Nobody has updated ROADMAP
since 2025-09-10. New contributor opens ROADMAP, plans against
"Phase 3 in progress" assumption. Conversation: "what do you mean
we're on Phase 6?"]
```

**Violates:** Cross-references CONTINUITY Rule 5.4 (ROADMAP reflects current reality). See CONTINUITY `rules.md#rule-54-roadmap-reflects-current-reality`. Also violates principle "ROADMAP is committed-to, not aspirational" — but inverted: committed-to items diverge from reality without conscious revision.

**Why it fails:** The ROADMAP confidently misleads. New contributors plan against fiction. Stakeholder commitments are made against fiction. Each planning round goes by without the drift being surfaced — because no planning round was triggered to update it. Per CONTINUITY Rule 5.4, ROADMAP update is part of commit discipline; without that discipline, drift accumulates silently.

**Source for failure mode:** Universal operational failure when ROADMAP updates aren't gated on milestone progress. See CONTINUITY AP-4 (ROADMAP drift) for the same pattern from the continuity-discipline angle.

### CP-8: Planning round surfaces drift; ROADMAP updated as part of commit discipline

**Pattern:**

```markdown
# ROADMAP.md (last updated 2026-03-15)

**Current focus:** Phase 6 — Database performance refactor (scoped
2026-02-20 after the dashboard slowness incident, see ERR-2026-
02-15-003 resolution). Estimated completion: 2026-04-30.

## Active Milestones
| M6 | Database performance refactor | 2026-04-30 | medium | in progress |
| M7 | Multi-region deploy | TBD | low | not started |

## Completed Milestones
| M3 | Authentication | 2025-11-12 | Slipped from 2025-10-15 target; see DEC-2026-02-14-001 (auth strategy change) |
| M4 | Payments | 2026-01-08 | Stripe + subscription model |
| M5 | Admin dashboard | 2026-02-10 | — |

## Slip History
| Phase 3 (auth) target 2025-10-15 → actual 2025-11-12; cause:
  mid-development auth-strategy change (JWT → session cookies, see
  DEC-2026-02-14-001). Conscious slip, not silent drift. |
```

[Each commit that materially affected milestones updated ROADMAP
in the same commit per CONTINUITY Rule 5.4. New contributor opens
ROADMAP today and sees actual current state. Stakeholder
conversations are about real progress, not fiction.]
```

**Pairs with:** Anti-pattern AP-8

**Why it works:** ROADMAP reflects actual state. Completed milestones moved to Completed table with dates. Phase 6 (scoped reactively after an incident) is captured with its origin documented. Slip history captures the conscious decisions where reality diverged. Update discipline is part of commit per CONTINUITY Rule 5.4 — not a quarterly reconciliation event.

**Additional considerations:** Quarterly ROADMAP review (per CLAUDE.md §8) is still valuable — it catches subtle drift that commit-time updates might miss. But the commit-time discipline is primary; quarterly is the safety net.

---

## Pairing discipline

Per `DEC-2026-05-17-003` Clause 1: every anti-pattern is paired with a canonical pattern. The framework's value depends on showing the user both what to reject and what to write instead.

When a new PROJECT-MANAGEMENT anti-pattern is observed during use but no clear canonical pattern is obvious, log to `WAIVER-LOG.md` for revisit rather than shipping a one-sided entry.
