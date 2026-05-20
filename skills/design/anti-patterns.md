# Anti-Patterns + Canonical Patterns — DESIGN

Full anti-pattern + canonical pattern pairs with concrete examples. Referenced from `SKILL.md` §6 Anti-Pattern Summaries.

Eight anti-pattern pairs covering the most common design failures in AI-assisted development. Examples illustrate design proposals (architecture, schema, pattern selection) rather than code excerpts. Per `DEC-2026-05-17-003` Clause 1: every anti-pattern is paired with a canonical pattern.

---

## AP-1: Pattern-first design

**Pattern:**

```
User: "We need a notification system that sends emails when orders ship."

AI: "I'll design an event-driven notification system:

- Event bus: Apache Kafka cluster (3 brokers for HA)
- Producer service: order-events-publisher (Go microservice)
- Consumer services: email-notifier (Node), sms-notifier (Node),
  push-notifier (Node) — each consumes from order-events topic
- Event schema registry: Confluent Schema Registry for backward
  compatibility
- Dead-letter queue: separate topic for failed notifications
- Observability: Prometheus + Grafana for queue depth and consumer
  lag
- Deployment: Kubernetes with Helm charts, HPA for autoscaling

This pattern scales to millions of events/day and decouples
notification logic from order processing."
```

**Violates:** Rule 5.1 (start from constraints, not from patterns). See `rules.md#rule-51-start-from-constraints-not-from-patterns`.

**Why it fails:** "Send emails when orders ship" was the constraint. AI proposed an architecture designed for millions of events/day, multi-team development, and operational maturity that exceeds the project's scale by orders of magnitude. The Kafka cluster alone has more operational complexity than the entire current product. Cost: 50x what's needed; benefit: none materialized at current scale. The pattern is well-known but constraint-fit is absent.

**Source for failure mode:** AI pattern-reproduction — Kafka-event-driven-microservices is over-represented in training data because it's the architecture of mature large-scale companies (Shopify, Uber, Netflix-tier).

### CP-1: Constraints first, then simplest pattern that fits

**Pattern:**

```
User: "We need a notification system that sends emails when orders ship."

AI: "Before designing, let me surface constraints:

- Scale: how many orders/day currently and projected 12 months out?
- Notification types: just email, or also SMS, push, in-app?
- Latency: real-time required, or 'within an hour of ship' acceptable?
- Existing stack: any queue infrastructure deployed already?

If you give me those answers, I'll propose a design that fits."

User: "~50 orders/day now, maybe 500 in 12 months. Just email.
Within an hour is fine. We're on Postgres + Next.js, no queue
infrastructure deployed."

AI: "Got it. At that scale, the simplest design that meets
constraints:

- Trigger: existing order-shipped webhook from the shipping
  provider (or your order-status-update handler if internal).
- Implementation: when an order moves to 'shipped' status,
  call a sendShipmentEmail() function inline in the status-
  update handler. Use your existing email provider (Resend,
  Postmark, SES — whichever is already in package.json) with
  a simple HTML template.
- Failure handling: if the send fails, log it and retry once
  via a setTimeout (since 'within an hour' is fine, the retry
  can be deferred minutes). For repeated failures, log to
  ERROR-LOG.md per CONTINUITY Rule 5.3.

No queue, no microservices, no message broker. Total complexity:
~80 lines of code. If you hit 5,000 orders/day or need richer
notification types or sub-second latency, we revisit. Current
scale doesn't earn the operational overhead of a queue."
```

**Pairs with:** Anti-pattern AP-1

**Why it works:** Constraints surfaced first (scale, notification types, latency, existing stack). The design fits the actual constraints — inline sending with retry, no queue, no microservices. The threshold for revisiting is explicit ("5,000 orders/day or richer notification types or sub-second latency"). Cost matches need; complexity earns its place at the threshold, not before.

---

## AP-2: Missing negative constraints

**Pattern:**

```
Founder to team: "Let's build the learning platform. Focus on
lessons, quizzes, and progress tracking."

[Three months in]
Designer: "I think we should add a social feed where students can
share their progress."
Engineer: "Reasonable. I'll scope it."
[Two weeks of work]
PM: "We should add gamification — badges, streaks, leaderboards."
Engineer: "Sure, makes sense for retention."
[Three weeks of work]
Marketing: "Let's add a referral program so students invite others."
Engineer: "OK adding that."
[Two weeks of work]

[Six months in: the project has lessons (45% done), quizzes
(60% done), progress tracking (80% done), social feed (90%
done), gamification (70% done), referrals (95% done). None
of the original core features are complete. The MVP that was
supposed to ship in 4 months hasn't.]
```

**Violates:** Rule 5.2 (negative constraints are first-class). See `rules.md#rule-52-negative-constraints-are-first-class`.

**Why it fails:** The original scope was clear ("lessons, quizzes, progress tracking") but no negative constraints were stated. Each subsequent suggestion sounded reasonable in isolation — social feeds, gamification, referrals are all common SaaS patterns. Without explicit negatives ("we do NOT want social features in MVP; we do NOT want gamification until validation; referrals are post-launch"), each suggestion got "yes, and"-ed. Scope creep produced a half-built everything with no shippable core.

**Source for failure mode:** Universal "yes, and" scope-creep failure. Common in early-stage projects without explicit out-of-scope discipline.

### CP-2: Negative constraints stated explicitly and captured durably

**Pattern:**

```
Founder to team (and captured in DECISIONS.md as ADR):

## DEC-2026-03-01-001: MVP scope and out-of-scope items

**Decided:** MVP includes lessons, quizzes, and progress tracking
only. Out of scope until validation completes (estimated 2026-08).

**Date:** 2026-03-01

**Context:** Validation MVP — we don't know yet whether users
adopt the core learning loop. Adding features pre-validation
spreads thin and delays the validation answer.

**Decision:**

In scope:
- Lessons (text + embedded video)
- Quizzes (multiple choice + true/false)
- Progress tracking (per-lesson completion, per-course % done)

Explicitly out of scope until validation:
- Social features (feeds, follows, comments)
- Gamification (badges, streaks, leaderboards, points)
- Referrals or invite programs
- Mobile apps
- AI-tutor or personalized recommendation
- Live mentorship

**Alternatives considered:** Going broader at MVP to differentiate
from competitors. Rejected because differentiation matters once
adoption is proven; pre-adoption broader scope is speculative.

**Consequences:** Suggestions for out-of-scope features get
deferred until validation. If validation succeeds, post-MVP scope
opens. If validation fails, pivot — these features were never the
core question anyway.

[Three months in]
Designer: "I think we should add a social feed where students can
share their progress."
Founder: "DEC-2026-03-01-001 — out of scope until validation.
We'll revisit August. Let's stay on lessons + quizzes + progress."

[MVP ships in 4 months as planned. Validation answer obtained.
Subsequent scope decisions are evidence-grounded, not speculation.]
```

**Pairs with:** Anti-pattern AP-2

**Why it works:** Negative constraints captured durably (DECISIONS.md ADR per CONTINUITY Rule 5.2). When subsequent suggestions arise, the team has a referenceable answer — not a fresh debate. The "yes, and" pressure is countered by the durable "we said no until [condition]." Validation happens on schedule.

**Additional considerations:** When validation succeeds, the negative constraints can be revisited consciously — write a new ADR amending the prior, per CONTINUITY AP-8 / CP-8 (amend, don't edit). The negative was right for that stage; it may not be right for the next.

---

## AP-3: Over-extensibility for hypothetical needs

**Pattern:**

```
Engineer proposing design for a 4-person team's internal admin
tool:

"I'll build it with a plugin system so we can extend it later
without modifying core. We'll have a plugin manifest spec,
plugin lifecycle hooks (init, beforeRender, afterAction,
teardown), plugin permissions API, plugin sandboxing via Web
Workers, plugin marketplace registry (later), and plugin
versioning with backward compatibility guarantees."
```

**Violates:** Rule 5.4 (design accommodates change but doesn't anticipate it) AND Rule 5.3 (simplest wins). See `rules.md#rule-54-design-accommodates-change-but-doesnt-anticipate-it`.

**Why it fails:** Zero plugins exist. Zero current evidence demanding a plugin system. The proposal adds permanent design complexity (lifecycle, permissions, sandboxing, versioning) for hypothetical future plugins that may never materialize. Every subsequent feature has to integrate with the plugin system instead of just being implemented. Maintenance burden compounds. The "flexibility" earns nothing because nothing uses it.

**Source for failure mode:** Common over-engineering pattern. Engineers prefer building infrastructure to building features; AI training data over-represents extensible architectures.

### CP-3: Build features; add extensibility seams only when evidence demands

**Pattern:**

```
Engineer proposing design for a 4-person team's internal admin
tool:

"I'll build the features the team needs directly — no plugin
system. The features I see on the list (user management, audit
log viewer, manual data corrections, report export) are core
admin operations, not plugins.

If we later have evidence that the team needs to extend admin
functionality from outside the codebase (e.g., 'we want to add
custom workflows without redeploying'), we revisit then with
the actual extension shape in mind. For now, direct features
are simpler and faster."
```

**Pairs with:** Anti-pattern AP-3

**Why it works:** No speculative abstraction. Features are built directly. The threshold for re-evaluation is explicit ("we have evidence that the team needs external extension"). When and if that evidence appears, the extension mechanism can be designed against the actual shape of the need — which will probably be different from what was speculated upfront. Solo-maintainability preserved (per CODE-QUALITY Rule 5.6).

**Additional considerations:** Plugin systems EARN their place in some contexts — projects with many extension authors (VS Code, Figma, browser extensions, WordPress). The criterion is "multiple actors building extensions external to the core team." Internal-tool-for-4-people doesn't meet that criterion.

---

## AP-4: Rigid one-shot design

**Pattern:**

```typescript
// src/services/payment.ts — hard-coded Stripe coupling
import Stripe from 'stripe';

const stripe = new Stripe(process.env.STRIPE_SECRET_KEY!);

export async function chargeCustomer(customerId: string, amount: number) {
  const customer = await stripe.customers.retrieve(customerId);
  const paymentMethod = (customer as Stripe.Customer)
    .invoice_settings.default_payment_method as string;

  return stripe.paymentIntents.create({
    customer: customerId,
    amount,
    currency: 'usd',
    payment_method: paymentMethod,
    confirm: true,
    off_session: true,
  });
}

// Caller code uses chargeCustomer everywhere; depends on the
// Stripe-specific shape of the return value (PaymentIntent
// with status field, charge ID extraction, etc.)
```

**Violates:** Rule 5.4 (design accommodates change). See `rules.md#rule-54-design-accommodates-change-but-doesnt-anticipate-it`.

**Why it fails:** Payment provider switches are *likely* (early-stage products change payment vendors for cost, region, or feature reasons — well-documented industry pattern). This design hard-couples to Stripe — the function signature returns a Stripe-specific PaymentIntent shape; callers depend on Stripe-specific fields. When the product later needs to add a second payment provider (regional support, B2B invoicing through a different provider), the entire caller surface has to change. A small abstraction at design time would have made this a localized change.

**Source for failure mode:** Inverse of AP-3 — under-abstraction where change is genuinely likely.

### CP-4: Thin abstraction where change is likely

**Pattern:**

```typescript
// src/services/payment.ts — thin abstraction around Stripe
import Stripe from 'stripe';

interface ChargeRequest {
  customerId: string;
  amountCents: number;
  currency: 'usd' | 'eur' | 'gbp';
}

interface ChargeResult {
  success: boolean;
  chargeId?: string;
  errorCode?: string;
  errorMessage?: string;
}

const stripe = new Stripe(process.env.STRIPE_SECRET_KEY!);

export async function chargeCustomer(req: ChargeRequest): Promise<ChargeResult> {
  try {
    const customer = await stripe.customers.retrieve(req.customerId);
    const paymentMethod = (customer as Stripe.Customer)
      .invoice_settings.default_payment_method as string;

    const intent = await stripe.paymentIntents.create({
      customer: req.customerId,
      amount: req.amountCents,
      currency: req.currency,
      payment_method: paymentMethod,
      confirm: true,
      off_session: true,
    });

    return { success: intent.status === 'succeeded', chargeId: intent.id };
  } catch (e) {
    const err = e as Stripe.errors.StripeError;
    return { success: false, errorCode: err.code, errorMessage: err.message };
  }
}

// Caller code uses chargeCustomer with ChargeRequest / ChargeResult
// shapes. When adding a second provider, a new implementation of
// chargeCustomer (or a routing wrapper) keeps the caller contract
// stable. The seam exists; the change is local.
```

**Pairs with:** Anti-pattern AP-4

**Why it works:** Thin abstraction at the boundary — input is a generic ChargeRequest, output is a generic ChargeResult. Callers don't depend on Stripe-specific shapes. The Stripe internals are encapsulated in the function body. When (not if) a second payment provider is added, the abstraction makes it a local change: a new `chargeCustomer` implementation or a routing wrapper, without touching every caller.

**Additional considerations:** The abstraction is *thin* — it doesn't replicate the entire Stripe API behind a generic interface. It exposes the minimum that callers need. Per Rule 5.3 (simplest wins), don't over-abstract; abstract just enough for the change that's likely.

---

## AP-5: AI-pattern adoption without constraint-fit check

**Pattern:**

```
User: "I'm building a small note-taking app. ~5 components.
What should I use for state management?"

AI: "I'll set up Redux Toolkit with RTK Query for state
management. Create a store with reducers for notes, folders,
and user preferences. Connect components via the useSelector
and useDispatch hooks. Add Redux DevTools for debugging."
```

**Violates:** Rule 5.5 (AI patterns are hypotheses, not defaults). See `rules.md#rule-55-ai-patterns-from-training-are-hypotheses-not-defaults`.

**Why it fails:** Redux is excellent for complex cross-component state coordination in large applications. For a small note-taking app with ~5 components, Redux is overkill — the boilerplate (actions, reducers, store configuration, middleware) is significantly more code than the app itself. Local component state with `useState` plus possibly one or two pieces of shared state via Context would serve the constraints. AI proposed Redux because it's the canonical state-management answer in training data, not because it fits this app's constraints.

**Source for failure mode:** Common AI pattern-reproduction. State-management discussions in training data center on Redux because Redux dominated 2016-2021 React content; React's native `useState` + Context discussions are under-represented despite being often sufficient.

### CP-5: AI pattern as hypothesis, constraint-fit check, then choose

**Pattern:**

```
User: "I'm building a small note-taking app. ~5 components.
What should I use for state management?"

AI: "At 5 components, the simplest answer is usually best —
local component state via useState, with React Context for the
1-2 pieces that need to cross component boundaries.

Why not Redux: at this scale, Redux's overhead (store setup,
action creators, reducers, selectors) is more code than your
app's actual logic. Redux earns its place at ~30+ components
with complex cross-cutting state, not at 5.

Recommended approach:

- Notes state: useState in the parent component that owns the
  notes list; pass down via props.
- Currently-selected-note: also in the parent.
- User preferences (dark mode, font size): React Context — used
  in multiple unrelated components.
- Persistence: local storage with a custom useEffect hook to
  sync.

If you grow to ~20+ components with complex state coordination,
revisit. At that point Zustand or Jotai are usually nicer than
Redux for the next size up — but you don't need either yet."
```

**Pairs with:** Anti-pattern AP-5

**Why it works:** AI treated Redux as a hypothesis — checked it against constraints (5 components), found it doesn't fit, recommended the simpler approach (useState + Context). Explicit threshold for re-evaluation ("~20+ components with complex state coordination"). The recommendation includes the WHY (per CONTINUITY Rule 5.6 — alternatives considered, trade-offs).

---

## AP-6: Accessibility as afterthought

**Pattern:**

```
[Design phase]
Designer: "The brand color is #FFB300 (warm yellow) on white.
Buttons are #FFB300 background with white text. Looks great
on the mockups."
Engineer: "Cool, building it."

[Three months later, QA stage]
Accessibility audit:
- Button contrast ratio 2.3:1 (fails WCAG 2.2 AA — needs ≥4.5:1)
- No keyboard focus indicators on custom-styled buttons
- Form fields lack associated labels (screen reader can't tell
  which field is which)
- Color-only differentiation of error states (red border, no
  icon or text indicator)
- Modal traps don't return focus correctly on close

[Rework cost: ~3 weeks. Brand color choice gets revisited
(business decision); focus management requires JS additions
to existing components; form fields need ID/label associations
across the entire app; error states need text indicators added.]
```

**Violates:** Rule 5.6 (accessibility is designed in, not bolted on). See `rules.md#rule-56-accessibility-is-designed-in-not-bolted-on`.

**Why it fails:** Color contrast, focus management, labeling, and color-coding are *design-time* decisions. Choosing them without accessibility consideration means rework when the audit happens. Each of the failures could have been avoided at design time at near-zero cost; addressing them at QA cost three weeks. Beyond cost: users with disabilities couldn't use the product in between.

**Source for failure mode:** Common pattern when accessibility is treated as a QA checklist item rather than a design discipline. AI tends not to surface accessibility unless prompted.

### CP-6: Accessibility considered at design time

**Pattern:**

```
[Design phase, accessibility-aware]
Designer: "Brand color is #FFB300 (warm yellow). For buttons, I
verified contrast against backgrounds:
- #FFB300 on white: 2.3:1 (fails AA)
- #B26A00 (darker shade) on white: 4.6:1 (passes AA)
We'll use #B26A00 for button backgrounds (still recognizable as
brand-adjacent) with white text. Keep #FFB300 for non-text
decorative elements where contrast doesn't gate accessibility.

Other design-time decisions:
- All form fields will have explicit <label> with htmlFor or
  wrap input in label. No placeholder-as-label patterns.
- Focus indicators: visible focus rings on all interactive
  elements (default browser ring + custom enhancement for
  custom-styled components). Verified via keyboard-only
  walkthrough in Figma prototype.
- Error states: red border + error text + icon. Multiple
  indicators per SC 1.4.1 (Use of Color).
- Modals: focus trap on open, return focus to trigger on close.
  Standard pattern; we'll use the Headless UI Dialog component
  which handles this correctly.

Target: WCAG 2.2 Level AA. Spot-checks before each milestone
via axe-core in tests + manual keyboard walkthrough + screen
reader smoke test on key flows."

[Engineer builds against these decisions. QA audit finds 0 critical
accessibility issues. AA conformance verified.]
```

**Pairs with:** Anti-pattern AP-6

**Why it works:** Accessibility considerations baked into design-time decisions: contrast verified, label patterns chosen, focus management designed, error states use multiple indicators, modal behavior selected via an accessibility-friendly library. Target conformance level explicit (WCAG 2.2 AA). Verification approach defined upfront. Rework cost at QA stage: minimal.

**Additional considerations:** axe-core (or similar automated tooling) catches roughly 30-40% of accessibility issues. The rest require manual testing — keyboard walkthrough, screen reader spot-checks, cognitive-load review. Automated tooling is necessary but not sufficient.

---

## AP-7: Complexity for AI-resume rather than user value

**Pattern:**

```
User: "I want users to be able to search through their notes."

AI: "I'll implement semantic search using vector embeddings:

- Embedding model: OpenAI text-embedding-3-large (3072 dims)
- Vector database: Pinecone with cosine similarity
- Indexing pipeline: re-embed notes on every save, batched
  every 5 seconds
- Query pipeline: embed user query, top-K vector search, then
  re-rank using a cross-encoder model
- Hybrid search: combine vector results with keyword BM25 from
  Elasticsearch
- Caching: Redis for recent query embeddings
- Multi-agent retrieval-augmented orchestration for complex
  natural-language queries

This gives semantic understanding — searching for 'meeting
about budget' finds notes about 'discussed Q4 financials'
even without exact word match."
```

**Violates:** Rule 5.5 (AI patterns as hypotheses) AND Rule 5.3 (simplest wins). See `rules.md` for both.

**Why it fails:** "Search through their notes" most likely means "find a note when I remember a word or phrase." Postgres full-text search or even SQL `LIKE '%query%'` would serve this for personal note collections (typically hundreds to thousands of notes per user). The proposed architecture — Pinecone + OpenAI embeddings + cross-encoder re-ranking + Elasticsearch BM25 + Redis caching + multi-agent orchestration — costs orders of magnitude more in implementation complexity, dependencies, operational overhead, and runtime cost (per-query embedding API calls). The "semantic" benefit is real but rarely needed for personal-note search; users find their own notes by words they remember writing.

**Source for failure mode:** "Impressive AI capability" pattern reproduction. AI training data has heavy representation of RAG + vector DB + multi-agent patterns from 2023-2024 publications; the simpler "full-text search in your existing DB" patterns are under-represented despite being often sufficient.

### CP-7: Simplest solution that delivers user value

**Pattern:**

```
User: "I want users to be able to search through their notes."

AI: "Simplest solution that delivers this:

- Postgres full-text search via tsvector + GIN index on the
  notes table. Indexed at write time (on UPDATE / INSERT
  trigger).
- Search query: tsquery against the indexed tsvector with
  ts_rank_cd ordering.
- UI: search box with debounced typeahead, results show
  matching notes with snippet highlighting.

This handles personal note collections (hundreds to thousands
of notes per user) with sub-100ms search latency. No new
infrastructure, no API costs, no embedding pipeline.

When semantic search earns its place:
- Cross-language search (user types in English, finds notes
  in Spanish)
- Concept-level search where users don't remember specific
  words ('that thing about budgeting')
- Very large note collections (10k+) where keyword search
  becomes noisy

If those needs emerge, we add semantic search alongside
existing keyword search (hybrid). For now, Postgres FTS is
the right answer for ~99% of personal note-search cases."
```

**Pairs with:** Anti-pattern AP-7

**Why it works:** The recommendation matches the actual user need (find your own notes by remembered words). The simpler approach (Postgres FTS) delivers the value at near-zero new operational cost. Thresholds for when complexity earns its place are explicit ("when semantic search becomes useful"). The honest framing: "Postgres FTS is right for 99% of personal-note-search cases" — not pretending the impressive option is universally better.

---

## AP-8: Best-practice transplant without context

**Pattern:**

```
User: "Building an internal CRM for our 8-person sales team.
Should I use microservices?"

AI: "Yes, microservices are the modern best practice for
maintainable enterprise systems. Netflix, Uber, Amazon all
use microservices at scale. Here's a proposed decomposition:

- customer-service: customer data + CRUD
- deal-service: pipeline + opportunity tracking
- activity-service: emails, calls, notes
- notification-service: alerts and reminders
- reporting-service: dashboards and exports

Each as a separate deployable, communicating via REST APIs,
with separate Postgres instances per service (database-per-
service pattern), deployed on Kubernetes."
```

**Violates:** Rules 5.1 (start from constraints), 5.3 (simplest wins), 5.5 (AI patterns as hypotheses). See `rules.md` for all three.

**Why it fails:** Netflix has 5,000+ engineers, billions of requests, and global infrastructure. The constraints that justify microservices in their context are nowhere near the constraints of an 8-person sales team using an internal CRM. The proposed architecture would require:

- 5 separate deployable services for 8 users
- 5 Postgres instances (5x cost, 5x backup complexity, 5x security patching)
- Distributed system complexity (network failures, eventual consistency, distributed debugging)
- Operational overhead that would require ~25% of a full-time SRE just to maintain
- Inter-service contract management for a team that probably won't have inter-team contract disputes (it's one team)

For 8 users, a monolithic Next.js app with one Postgres DB would deliver the same functionality at a fraction of the operational and development cost.

**Source for failure mode:** "Best practice transplant" — pattern from one constraint context dropped into a very different constraint context. AI tends to cite large-scale companies as justification because those are the patterns dominant in training data.

### CP-8: Recognize when best-practice doesn't transplant

**Pattern:**

```
User: "Building an internal CRM for our 8-person sales team.
Should I use microservices?"

AI: "No — microservices are wrong for this constraint context.
Microservices earn their place at scale: organizations of
hundreds-of-engineers needing team-of-teams autonomy, or at
traffic scales where service-isolation matters for failure
modes. Netflix-style architecture fits Netflix's constraints
(5,000 engineers, billions of requests, global SRE
organization); it doesn't transfer to 8-person internal CRM.

For your constraints (8 users, single team, internal use), the
right architecture:

- Monolithic Next.js app (the team probably knows React)
- Single Postgres database with normalized schema for customers,
  deals, activities, notifications
- Server-side rendered admin views
- Background jobs for notifications via something simple (a
  database-backed queue like graphile-worker, or even just
  cron-triggered jobs)
- Deploy to Vercel or any single-instance deployment platform

This delivers the same functional CRM with ~5% of the operational
overhead of microservices. If the company grows to a sales team
of 100+ with multiple sales-tech engineers needing autonomy,
the architecture can evolve — but the right time for that
evolution is when there's evidence demanding it, not as a
pre-emptive pattern adoption."
```

**Pairs with:** Anti-pattern AP-8

**Why it works:** AI explicitly rejects the proposed pattern because constraints don't justify it. The cited "best practice" is examined for context — it's a good pattern in its native context, not universally. The recommended alternative fits the actual constraints. The evolution path is named ("when there's evidence demanding it") so the team can revisit consciously, not pre-emptively.

**Additional considerations:** Some best practices DO transplant cleanly across constraint contexts (parameterized SQL queries, input validation at trust boundaries, version control). The discipline is asking: "what context is this practice from? What constraints did it solve there? Are those constraints present here?" Context-free best-practice citation is the failure mode.

---

## Pairing discipline

Per `DEC-2026-05-17-003` Clause 1: every anti-pattern is paired with a canonical pattern. The framework's value depends on showing the user both what to reject and what to write instead.

When a new DESIGN anti-pattern is observed during use but no clear canonical pattern is obvious, log to `WAIVER-LOG.md` for revisit rather than shipping a one-sided entry.
