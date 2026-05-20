# Anti-Patterns + Canonical Patterns — DISCOVERY

Full anti-pattern + canonical pattern pairs with example dialogues. Referenced from `SKILL.md` §6 Anti-Pattern Summaries.

Eight anti-pattern pairs covering the most common DISCOVERY failures. Examples are example dialogues rather than code excerpts, since DISCOVERY governs conversational discipline. Per `DEC-2026-05-17-003` Clause 1: every anti-pattern is paired with a canonical pattern.

---

## AP-1: Assuming meaning instead of asking

**Pattern:**

```
User: "Help me with auth."

AI: "I'll set up authentication using JWT tokens. Here's the implementation:

[200 lines of JWT-with-localStorage code]

The JWT is stored in localStorage and sent via Bearer header on each request.
The token expires in 24 hours and refreshes via..."
```

**Violates:** Rule 5.1 (narrow before answering). See `rules.md#rule-51-narrow-before-answering`.

**Why it fails:** "Auth" has at least 6 distinct meanings worth asking about: authentication vs authorization, framework choice (built-in vs OAuth provider), session model (JWT vs cookies vs hybrid), threat model (consumer-facing vs internal-only), existing infrastructure (Auth0 already in stack? new project?), and scope (just login flow? full password reset / MFA / session management?). The AI committed to one specific implementation (JWT-in-localStorage — which has known XSS concerns per SECURITY-CORE Rule 5.3) without checking. If the user actually wanted "session cookies because we already decided JWT-in-localStorage is too risky," all 200 lines are throwaway.

**Source for failure mode:** Common AI confident-interpretation failure mode. See `OWASP-LLM LLM09:2025` (Misinformation — confident-sounding wrong answers to misunderstood prompts).

### CP-1: Partition question first, then branch

**Pattern:**

```
User: "Help me with auth."

AI: "A few quick questions to scope this:

1. Authentication (login/session) or authorization (who-can-do-what), or both?
2. Do you already have an identity provider (Auth0, Clerk, Supabase Auth,
   Cognito) integrated, or starting fresh?
3. Browser-facing app or internal/server-to-server?

Once I know these, I can suggest the right approach and avoid recommending
patterns that don't fit your existing stack."
```

**Pairs with:** Anti-pattern AP-1

**Why it works:** Three closed-form questions partition the large "auth" possibility space into a manageable subset. Question 1 separates authn from authz (very different domains). Question 2 separates greenfield from existing-stack (very different implementation paths). Question 3 separates browser threat model from server-to-server (very different security requirements). The user answers in 30 seconds; the AI then makes a recommendation grounded in actual constraints rather than guesses.

**Additional considerations:** Three questions is usually the right size for a partition question round — enough to narrow significantly, not so many that the user is doing structuring work. If the answers reveal further ambiguity, follow up with a second round per Rule 5.2.

---

## AP-2: Serial open-ended questioning

**Pattern:**

```
User: "I want to build a learning platform."

AI: "Tell me more about what you have in mind."

User: "It's for people learning tech skills."

AI: "What kind of features were you thinking?"

User: "Maybe lessons, quizzes, progress tracking."

AI: "Great. What does the user experience look like?"

User: "...like, they sign in, pick a topic, do lessons..."

AI: "What technology do you want to use?"

User: [sighing] "I don't know, that's why I'm asking you."
```

**Violates:** Rule 5.2 (branching tree, not linear questioning). See `rules.md#rule-52-branching-tree-not-linear-questioning`.

**Why it fails:** Each question is open-ended, putting the structuring burden on the user. The questions re-traverse the same uncovered ground rather than narrowing. By question 4, the user is doing the AI's job — partitioning the possibility space. User trust erodes; the conversation feels like an interview rather than a consultation. The user came expecting expertise; they got a checklist.

**Source for failure mode:** Common AI default — open-ended questions are cheap to write. See `IIBA-BABOK` (paywalled; cited by reference) — requirements-elicitation literature flags this pattern.

### CP-2: Branching tree with closed-form choices

**Pattern:**

```
User: "I want to build a learning platform."

AI: "A few questions to scope this:

1. Audience — is this for: (a) the general public learning tech;
   (b) a specific organization's employees; (c) a niche community
   (e.g., security learners specifically)?

2. Stage — are you: (a) validating the idea (smallest MVP);
   (b) building toward an established curriculum; (c) replacing
   an existing internal tool?

3. Stack preference — (a) you have a stack in mind; (b) you want
   me to recommend; (c) you're comparing options?

If you tell me a, b, or c for each, I'll have what I need to
suggest a minimum-viable scope plus a path from there."

User: "1a, 2a, 3b."

AI: "Got it — public-audience MVP for an idea you're validating, and you
want a stack recommendation. Three more focused questions:

1. Solo founder or team?
2. Will users pay (Stripe-needed) or free (no payment)?
3. Mobile, web, or both at launch?"

User: "Solo. Free initially. Web only at launch."

AI: "Scope is operational. Recommendation: Next.js (web), Supabase
(auth + database + storage), Vercel (deploy). MVP scope:
[3-bullet feature list]. Want me to proceed?"
```

**Pairs with:** Anti-pattern AP-2

**Why it works:** Each question partitions the possibility space. Closed-form options (a/b/c) make answers cheap for the user. After two rounds (six questions total), scope is operational and the conversation moves to Stage 2 (Scope). The user did far less structuring work than in AP-2 and arrived at a more grounded result.

**Additional considerations:** This pattern works because the AI knows the possibility space ahead of time. When the space is genuinely unknown, open-ended is appropriate — but the next question should move toward closing-form once the space is partially revealed.

---

## AP-3: Skipping Five Whys on a surface symptom

**Pattern:**

```
User: "The dashboard is slow. Can you optimize the query?"

AI: "Sure. I see the dashboard query is doing a full table scan.
I'll add an index on (customer_id, created_at) and rewrite the
JOIN to use a CTE. That should bring the query under 100ms."

[Ships index migration and query rewrite. Dashboard loads in 80ms.]

User: "Thanks. But honestly it's still annoying — I'm scrolling
through a hundred customers to find the one I need."
```

**Violates:** Rule 5.3 (Five Whys for root cause). See `rules.md#rule-53-five-whys-for-root-cause`.

**Why it fails:** "The dashboard is slow" was a workaround for the actual need: "I need fast access to a specific customer's order history before a call." The dashboard was the surface the user had, so they reported the surface problem. AI optimized the surface but didn't ask why the dashboard speed mattered. Result: shipped optimization solves the wrong problem; user is no happier; AI's work is technically correct but operationally wasted.

**Source for failure mode:** Common AI surface-symptom failure. The Toyota Production System's Five Whys methodology (~1950s, Sakichi Toyoda) was developed exactly for this failure mode in manufacturing.

### CP-3: Five Whys to surface the root need

**Pattern:**

```
User: "The dashboard is slow. Can you optimize the query?"

AI: "Sure, I can optimize the query. Quick check first — what are
you trying to do when the dashboard slowness blocks you?
Sometimes the root issue isn't the query."

User: "Honestly I'm trying to look up a specific customer's order
history before calling them. The dashboard is the only place
that shows it."

AI: "Got it. That's actually a different problem — you need
fast lookup by customer, not a fast list view. Two options:

(a) Optimize the dashboard as you asked. Faster but still
    a scrolling experience.

(b) Build a customer-detail page or search-by-customer flow
    that surfaces the order history directly. Slightly more
    work, but solves the actual workflow.

Which fits better? I lean toward (b) because (a) treats the
symptom and the symptom comes back as the customer list grows."

User: "(b) — that's actually what I've been wanting."
```

**Pairs with:** Anti-pattern AP-3

**Why it works:** One Five-Whys-style question ("what are you trying to do?") surfaced the workflow underneath the reported symptom. The actual scope is different from the reported scope, and the implementation reflects the actual need. The user feels heard ("that's actually what I've been wanting"); the work serves the real workflow.

**Additional considerations:** Not every prompt benefits from Five Whys. "Rename this variable" is surface-level by design. The discipline engages when language signals symptom or workaround — "the X is slow," "users keep complaining about Y," "I keep having to do Z manually."

---

## AP-4: Over-questioning past scope-operational

**Pattern:**

```
User: "Add a /healthz endpoint that returns 200 OK if the
service is up."

AI: "A few clarifying questions:

1. What HTTP method? GET or POST?
2. Should it return JSON or plain text?
3. Should it check downstream dependencies (database, cache)?
4. Should it include version info in the response?
5. What status code on partial failure?
6. Should we add it to the OpenAPI spec?
7. Do you want a separate /readyz endpoint as well?
8. Should we add Prometheus metrics for the endpoint?
9. Cache headers?
10. Rate limiting?"

User: "I just wanted a healthz endpoint."
```

**Violates:** Rule 5.5 (stop at scope-operational). See `rules.md#rule-55-stop-at-scope-operational`.

**Why it fails:** Scope was operational at the original prompt — work bounded ("/healthz endpoint"), success criteria checkable (returns 200 OK if up), major decisions made (it's a healthz endpoint with standard semantics). The questions in AP-4 are about edge cases and polish, not load-bearing decisions. The user is now doing checklist work for things they didn't think they needed to specify, signaling that the AI doesn't trust its own judgment on standard conventions.

**Source for failure mode:** AI completeness instinct — training data rewards thorough answers, which leaks into over-questioning. Inverse failure of AP-1 (assuming meaning).

### CP-4: Accept operational scope, surface load-bearing assumptions inline

**Pattern:**

```
User: "Add a /healthz endpoint that returns 200 OK if the
service is up."

AI: "On it. I'll add a GET /healthz that returns 200 with
plain-text body `ok`. Assuming standard liveness semantics
(no downstream checks). Let me know if you want it to
verify database connectivity too — that's the main 'should I
expand' question.

[Implementation follows.]"
```

**Pairs with:** Anti-pattern AP-4

**Why it works:** Scope was operational at the original prompt. The AI proceeds with standard conventions, names one load-bearing assumption (liveness vs readiness with downstream checks), and offers the user a single decision point if they want to expand. No checklist exhausts the user; one inline check covers the meaningful variant.

**Additional considerations:** "Standard conventions" is doing real work here — the AI is committing to a specific shape (GET + plain text + 200/non-200) without asking because those are the prevailing conventions. If the project has documented conventions that diverge (e.g., everything is JSON in this codebase), apply those instead per CODE-QUALITY Rule 5.6 (codebase fit).

---

## AP-5: Buried assumption

**Pattern:**

```
User: "Set up automated tests for the order processing module."

AI: "I'll add Jest tests for the order processing functions.
Here's a test file:

[200 lines of Jest test code]
"

User: "...we don't use Jest. We're on Vitest. Also this is a
Python project — the order processing module is FastAPI."
```

**Violates:** Rule 5.4 (surface assumptions explicitly). See `rules.md#rule-54-surface-assumptions-explicitly`.

**Why it fails:** AI made two load-bearing assumptions silently — language (TypeScript/JavaScript vs Python) and test runner (Jest vs Vitest, or pytest in this case). Both are wrong. All 200 lines of test code are throwaway, and the user has to debug "why did you assume Jest? why did you assume JavaScript?" before any new work can happen. The cost of stating these assumptions ("I'm assuming Jest + JavaScript — does that match?") was ~10 seconds. The cost of recovering from the buried assumption is many minutes plus trust erosion.

**Source for failure mode:** Universal AI failure mode — silently filling gaps with most-likely interpretation rather than stating the interpretation.

### CP-5: State assumptions explicitly before acting

**Pattern:**

```
User: "Set up automated tests for the order processing module."

AI: "Quick assumption check before I start —

- Language: assuming this is TypeScript/JavaScript based on the
  recent files I've seen edited. If Python, the patterns differ.
- Test runner: I'll use whatever's already in package.json /
  pyproject.toml (let me check). If you have a preference,
  let me know.
- Scope: 'order processing module' — assuming the functions in
  src/orders/processing.ts (or src/orders/processing.py). If
  it's a different file or you want adjacent modules included,
  point me at them.

Reply with corrections or 'go' and I'll proceed."

User: "Python, pytest, src/orders/processing.py."

AI: "Got it. Generating pytest tests for src/orders/processing.py.
[Implementation follows.]"
```

**Pairs with:** Anti-pattern AP-5

**Why it works:** Three load-bearing assumptions stated explicitly. Each is a one-line acknowledgement, not a lecture. User corrects two of three in five seconds. The implementation proceeds against the actual stack. Zero rework.

**Additional considerations:** Assumption stating is *brief*. Don't lecture; don't list every conceivable assumption. State the load-bearing ones — the ones that would meaningfully change the work if wrong. Per Rule 5.5, surfacing every conceivable assumption is over-questioning; surfacing the load-bearing ones is the discipline.

---

## AP-6: Vague "tell me more" prompts

**Pattern:**

```
User: "I want to add user profiles."

AI: "Tell me more about what you're thinking for user profiles."

User: "...like, users have profiles?"
```

**Violates:** Rule 5.2 (branching tree, not linear questioning). See `rules.md#rule-52-branching-tree-not-linear-questioning`.

**Why it fails:** "Tell me more" puts the burden of structure on the user. The user already gave the prompt — "I want to add user profiles" — and is now being asked to re-give the prompt with more detail, without any hint about what dimensions to expand on. The user is doing the AI's structuring work. The conversation stalls because the user doesn't know what the AI doesn't know.

**Source for failure mode:** AI default to open-ended prompts because they're cheap to generate. The cost is paid by the user.

### CP-6: Closed-form partition question

**Pattern:**

```
User: "I want to add user profiles."

AI: "To scope this:

1. Profile content — public-facing info (name, avatar, bio) or
   private settings (email preferences, notification settings),
   or both?
2. Editable by user, or admin-set only?
3. Visible to other users, or only to the profile owner?

If you give me 1, 2, 3 answers I can map out the scope."

User: "Both content types, user-editable, visible to other users."

AI: "Got it. So: public profile fields (name, avatar, bio) editable by
the user and visible to others, plus private settings (preferences,
notifications) editable by the user and not visible to others. I'll
write up the data model and routes. One assumption check: assuming
you want the public profile at /users/[id] — let me know if you'd
prefer /users/[username] or some other path scheme."
```

**Pairs with:** Anti-pattern AP-6

**Why it works:** Three closed-form questions narrow the space dramatically. The AI has done the partition work — there's nothing for the user to figure out about how to structure their answer. They just answer. Scope crystallizes in one round of questions plus one assumption check. Compare to the AP-6 dialogue where one question consumed the entire turn and got the AI no closer to scope.

---

## AP-7: Performative questioning

**Pattern:**

```
User: "Add a debug endpoint that prints the database connection
state."

AI: "Just to confirm — you want this endpoint to work and return
the database connection state?"

User: "...yes? That's what I asked for."

AI: "Got it. And you want it to be accessible by HTTP?"

User: "Yes, that's what an endpoint is."
```

**Violates:** Rule 5.2 (branching tree, not linear questioning). See `rules.md#rule-52-branching-tree-not-linear-questioning`.

**Why it fails:** The questions don't gate any branching — the answers are obvious from the original prompt. The questions are performative, taking a turn without narrowing anything. The user feels condescended to; the AI looks unsure of itself. Two turns are burned without progress.

**Source for failure mode:** AI overcompensation for under-questioning — having been pushed to ask before acting, AI asks even when the prompt is unambiguous.

### CP-7: Skip the obvious; ask the load-bearing question

**Pattern:**

```
User: "Add a debug endpoint that prints the database connection
state."

AI: "On it. One quick check — should this be locked down (auth
required, or feature-flag gated to dev environments only)? Debug
endpoints leaking internal state are a common source of surprise
information disclosure in production.

If you want, I can add it behind a `if (process.env.NODE_ENV !==
'production')` guard plus a basic admin-only auth check. Let me
know and I'll proceed."
```

**Pairs with:** Anti-pattern AP-7

**Why it works:** The questions that didn't gate anything are skipped. The one question that does gate something — the security posture for a debug endpoint (production exposure is a real SECURITY-CORE concern per Rule 5.2) — is asked, with the recommended default included. The user can accept the recommendation, modify, or override; the answer meaningfully changes what gets shipped.

---

## AP-8: Discovery as a one-time pass

**Pattern:**

```
[Earlier in session]
AI: [Stage 1 DISCOVERY runs cleanly. Scope: implement user
profile editing. Assumption stated: public-only profile fields.
User confirms.]

[Later, mid-implementation in Stage 4]
AI: [Working on the profile route. Discovers that the spec
implies private email-notification settings need to be editable
too, which contradicts the "public-only profile fields"
assumption that was confirmed at Stage 1.]

[AI silently proceeds, extending the profile to include both
public AND private fields, without flagging the contradiction.]

[User reviewing the PR notices both field types and asks
"wait, why are notification settings in here? I thought we
agreed public-only."]
```

**Violates:** Rule 5.1 (narrow before answering) AND Rule 5.5 (the scope-operational threshold is bounded — when scope is contradicted, re-discover). See `rules.md#rule-51-narrow-before-answering`, `rules.md#rule-55-stop-at-scope-operational`.

**Why it fails:** Discovery established scope, then the implementation revealed a contradiction with the established scope. Instead of pausing and re-engaging the user briefly, the AI silently expanded the work to cover both interpretations. The user can't tell from the PR whether the expansion was intentional or whether the AI quietly overrode the Stage 1 agreement. Trust erodes.

**Source for failure mode:** Common AI failure when DISCOVERY is treated as a one-shot rather than a re-entrant discipline. AI completes the task confidently, smoothing over contradictions rather than surfacing them.

### CP-8: Re-engage DISCOVERY briefly when contradictions surface

**Pattern:**

```
[Later, mid-implementation in Stage 4]
AI: "Hit a contradiction with the Stage 1 scope. The spec implies
that notification settings need to be editable on the profile
page — but at Stage 1 we agreed on public-only profile fields.

Two options:

(a) Stick with public-only scope; notification settings live on
    a separate /settings page (consistent with original
    agreement but adds a route)

(b) Expand profile scope to include both public and private
    fields (clearer for the user; broader scope than originally
    agreed)

Which do you want? I'll keep the in-progress work parked until
you answer."

User: "(b) — go ahead and expand. Update the Stage 1 notes."

AI: "Updating scope in the session log and proceeding. The
assumption that was contradicted ("public-only") is now
overridden by the explicit decision to include both. I'll
note this in the commit message too."
```

**Pairs with:** Anti-pattern AP-8

**Why it works:** Contradiction surfaced explicitly; user gets the decision rather than discovering it post-hoc in the PR. The re-engagement is bounded — one question, two clear options, immediate continuation. Session log updates per CONTINUITY Rule 5.6 (capture WHY). Trust is preserved because the AI flagged the contradiction rather than silently working around it.

**Additional considerations:** Re-discovery is bounded discovery, not the whole questioning loop. The trigger is "a contradiction with established scope surfaced"; the resolution is "ask one focused question, then continue." If contradictions are surfacing frequently, the original Stage 1 was probably under-questioned — flag for retrospective in session log.

---

## Pairing discipline

Per `DEC-2026-05-17-003` Clause 1: every anti-pattern is paired with a canonical pattern. The framework's value depends on showing the user both what to reject and what to do instead. Standalone anti-patterns without paired canonical patterns are incomplete and do not ship.

When a new DISCOVERY anti-pattern is observed during use but no clear canonical pattern is obvious, log to `WAIVER-LOG.md` for revisit rather than shipping a one-sided entry.
