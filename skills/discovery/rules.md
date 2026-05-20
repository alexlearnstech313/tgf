# Rules — DISCOVERY

Full rule statements with citations, plain-language impact, and extended discussion. Referenced from `SKILL.md` §5 Rule Summaries. Loaded on demand when deep rule application is needed.

Five rules covering the discipline of narrowing ambiguous input through structured questioning before substantive work. Most rules are TGF synthesis of senior consultative practice grounded in Sakichi Toyoda's Five Whys methodology + standard requirements-elicitation discipline.

Citation discipline per `DEC-2026-05-17-004`: where rule-level mapping does not exist in any single authoritative source, the rule is acknowledged as TGF synthesis with explicit grounding rather than fabricating sub-rule identifiers.

---

## Rule 5.1: Narrow Before Answering

**Statement:** When input is ambiguous — multiple valid interpretations exist, scope is undefined, or required context is missing — engage DISCOVERY through structured questioning before producing substantive work. A confident answer to a misunderstood prompt is worse than a brief clarifying question. The diagnostic for "ambiguous" is §3 of `SKILL.md` — at least one of: multiple valid interpretations exist, scope is insufficient to write Stage 2, assumptions are in play and unstated, surface symptom may have deeper root cause.

**Citation:** `TGF-SYNTHESIS — grounded in IIBA-BABOK requirements elicitation discipline + senior consultative practice`. BABOK (paywalled, cited by reference per DEC-2026-05-17-004 Clause 5) covers requirements elicitation at the chapter level but does not provide a rule-level "narrow before answering" statement; this rule is TGF synthesis of the elicitation discipline applied to AI-assisted development.

**Plain-language impact:** Without this discipline, AI tends to interpret ambiguous prompts confidently and produce substantive work that may completely miss the user's actual intent. The user then has to debug whose-intent-was-this, redirect, and recover from the wrong direction. The cost of one well-structured clarifying question is small (~30 seconds of user time); the cost of a misinterpreted implementation is large (~minutes to hours of rework, plus the confidence cost of "the AI didn't get what I meant").

**Extended discussion:** "Narrow before answering" is not "ask before doing anything." Most prompts are unambiguous and operational; DISCOVERY engages only when the §3 diagnostic flags ambiguity. The discipline is *detection-then-questioning*, not *always-question*.

The trigger conditions in §3 are mostly objective: "multiple valid interpretations" is checkable by asking "could a reasonable person take this two different ways?"; "scope insufficient for Stage 2" is checkable by asking "could I write the Scope document right now?"; "assumptions in play" is checkable by asking "am I about to do something based on an unstated assumption?". When any of these is YES, narrow.

The "don't ask, just proceed" override (per §3 item 5) is real and respected — when the user has explicitly said this, the questioning loop does not engage but assumptions are still stated inline (per Rule 5.4). The user can correct inline statements cheaply; what's avoided is the interactive questioning loop.

AI-assisted development particularly benefits from this discipline because LLMs are trained to respond — confidently answering is the dominant pattern in training data. The discipline counteracts that default.

**Related anti-patterns:** AP-1 (assuming meaning instead of asking), AP-8 (discovery as one-time pass) (see `anti-patterns.md`)

---

## Rule 5.2: Branching Tree, Not Linear Questioning

**Statement:** Structure questioning so each answer narrows the possibility space and gates the next question. Avoid serial open-ended prompts that re-traverse the same uncovered ground. Prefer closed-form questions (multiple-choice, yes/no, "which of these fits best") over open-ended prompts when the possibility space is partially known. The questioning structure is a *tree* — early questions partition the space; later questions refine within the chosen partition.

**Citation:** `TGF-SYNTHESIS — grounded in IIBA-BABOK requirements elicitation + senior consultative practice`.

**Plain-language impact:** Serial open-ended questioning exhausts users. After three "tell me more" prompts, the user has effectively been asked to do the structuring work that the questioner should have done. Worse, serial questioning often re-asks for information the user already gave — burning trust along with time. A branching tree feels efficient: each question matters, each answer matters, the next question is shaped by the previous answer.

**Extended discussion:** Constructing a branching tree starts with the *partition question* — the question whose answer most cleanly divides the possibility space. For "help me with auth" the partition question is something like: "Are you building authentication (login/session) or authorization (who-can-do-what), or both?" That single question partitions a large possibility space into a few branches.

Once the partition is known, the next question refines within the chosen branch. If the user said "authentication," the next question might be: "OAuth flow with a provider (Auth0/Clerk/Supabase), email+password with your own session store, or magic links?" — three closed-form options. Each answer narrows further.

Closed-form questions are cheap for the user (multiple choice or yes/no), expensive to write well (they require knowing the possibility space ahead of time). Open-ended questions are cheap to write, expensive for the user. AI tends to default to the cheap-to-write pattern (open-ended) because that's the easier inference. The discipline is to do the structuring work as the questioner.

When the possibility space is genuinely unknown (e.g., the user is exploring a domain neither party fully understands), open-ended is appropriate — but the next question should immediately move toward closing-form once the space is partially revealed.

**Related anti-patterns:** AP-2 (serial open-ended), AP-6 (vague "tell me more"), AP-7 (performative questioning) (see `anti-patterns.md`)

---

## Rule 5.3: Five Whys for Root Cause

**Statement:** When the user describes a surface symptom or stated problem, apply Five Whys to surface the underlying need before scoping the work. The reported problem is often not the actual problem; the actual problem is reachable in approximately five levels of "why" questioning. "Five" is not literal — sometimes three is enough, sometimes more is needed — but the discipline is to ask why until the root need surfaces.

**Citation:** `TOYODA-5W (~1950s, stable methodology — Sakichi Toyoda, Toyota Production System)`. Five Whys is methodology, not granular rule set; the citation is at the methodology level which IS the granularity Five Whys provides.

**Plain-language impact:** Users (and AI) tend to skip to fixing the reported surface — "the dashboard is slow" gets fixed by optimizing the dashboard query, even when what the user actually needed was a different view of the data entirely. Without Five Whys, the discovered scope is the user's first-order request; with Five Whys, the discovered scope is what the user actually needs. The former is cheaper to ship; the latter is cheaper to maintain because it solves the right problem.

**Extended discussion:** Five Whys is not interrogation. The questioning is consultative and bounded — the goal is the user articulating the root need, not the questioner extracting it forcefully. Each "why" is phrased to invite reflection: "Why does that matter to you?" "What would the dashboard load time enable?" "What are you ultimately trying to do?"

The pattern in practice:

1. User reports: "the dashboard is slow."
2. Why does the dashboard need to be faster? "Because I check it before every customer call to see their order history."
3. Why do you need that information before every call? "Because customers expect me to know what they ordered last."
4. Why is the dashboard the right surface for that? "It's what I have."
5. Realization: maybe the right answer is a customer-detail page with order history surfaced prominently, not a faster general dashboard. Or maybe the answer is exposing a search-by-customer flow rather than scrolling the dashboard. The reported problem ("slow dashboard") was a workaround for the actual need ("fast access to a specific customer's order history").

Not every prompt benefits from Five Whys. Tactical prompts ("rename this variable," "fix this null check") are surface-level by design — Five Whys would be over-questioning. The discipline engages when the user has described a *symptom* or *workaround* — language like "the X is slow," "users keep complaining about Y," "I keep having to do Z manually" — signals that there may be a root cause worth surfacing.

**Related anti-patterns:** AP-3 (skipping Five Whys on a surface symptom) (see `anti-patterns.md`)

---

## Rule 5.4: Surface Assumptions Explicitly

**Statement:** When an assumption is in play — about user goal, available infrastructure, target users, framework choice, scope boundaries, threat model, or anything else where the answer could change the work — state the assumption to the user before acting on it. The user can confirm or correct cheaply; the user cannot fix an unstated assumption after the implementation has been built around it.

**Citation:** `TGF-SYNTHESIS — grounded in senior consultative practice`. No single authoritative source provides this rule at sub-level granularity; it is well-established consulting and engineering discipline operationalized for AI-assisted development.

**Plain-language impact:** A buried assumption is a hidden landmine. The work continues confidently against the assumption; the user only discovers the assumption was wrong when the output surprises them. By then, rework cost is significant — code written, tests written, possibly even partially deployed. A stated assumption is a free check: "I'm assuming X — does that match what you want?" takes ten seconds to ask and ten seconds for the user to answer, and it prevents the whole class of "I didn't realize it meant that" failures.

**Extended discussion:** Common categories of assumption worth surfacing:

- **Stack assumptions.** "I'm assuming this is a TypeScript project; you mentioned the file extension was .ts." "I'm assuming you're using Next.js based on the page.tsx pattern."
- **User population assumptions.** "I'm assuming end-users access this through a browser; if this is for internal admin use only, the security model is different."
- **Infrastructure assumptions.** "I'm assuming Postgres is your database; the migration patterns differ for MySQL or SQLite."
- **Scope boundary assumptions.** "I'm assuming you want this fix in just the API route; let me know if it should also extend to the admin endpoint."
- **Threat model assumptions.** "I'm assuming authenticated user input is trusted; if you need defense against insider threats too, the validation layer expands."
- **Compliance assumptions.** "I'm assuming GDPR doesn't apply yet (no EU users); if that changes, the consent flow needs work."

Stating the assumption is *brief*. It's not a lecture; it's a one-line acknowledgement that lets the user nod or correct. The discipline pairs with Rule 5.5 (stop at scope-operational) — surfacing every conceivable assumption would be over-questioning; surfacing the *load-bearing* ones (the ones that would meaningfully change the work if wrong) is the discipline.

For prompts where DISCOVERY's questioning loop is disengaged (user said "don't ask, just proceed"), Rule 5.4 still applies — assumptions are stated inline in the output rather than asked about interactively. The user can correct inline statements cheaply.

**Related anti-patterns:** AP-5 (buried assumption) (see `anti-patterns.md`)

---

## Rule 5.5: Stop at Scope-Operational

**Statement:** Discovery ends when scope is sufficient to define Stage 2 (Scope) of the workflow — not when every edge case is resolved. "Sufficient" means: the work to be done is bounded, the success criteria are checkable, the major decisions have been made, and the load-bearing assumptions are surfaced. Continuing to question past this threshold wastes the user's time, signals indecision, and is its own failure mode.

**Citation:** `TGF-SYNTHESIS — grounded in NIST-SSDF v1.1 PO.1 (Define Security Requirements) + senior practice`. NIST SSDF PO.1 covers requirements-definition discipline at the practice level; the specific "operational not perfect" framing is TGF synthesis of standard scope-bounded planning practice.

**Plain-language impact:** Over-questioning is the inverse failure mode of under-questioning. Both fail to advance the work. Without a stop discipline, AI can ask clarifying questions indefinitely, signaling indecision and exhausting the user. The user wanted help with a thing; the user is now answering questions about edge cases that may never matter. Knowing when to stop questioning is half the DISCOVERY skill.

**Extended discussion:** The "scope-operational" threshold has four components:

1. **Work bounded.** The work to be done can be described in one or two sentences. The reader knows what's in scope and what's out.
2. **Success criteria checkable.** The result can be evaluated against criteria that exist in writing or are clearly implied by the prompt.
3. **Major decisions made.** The big "left or right" choices (framework, approach, stack components, scope boundaries) are known.
4. **Load-bearing assumptions surfaced.** Per Rule 5.4 — assumptions that would change the work if wrong have been stated.

When all four are TRUE, DISCOVERY exits and Stage 2 begins. Lesser things — edge cases that come up rarely, optimization choices, polish details — are handled inline during Stage 4 (Implement) or surfaced via Stage 5 (Review) findings. They do not need to be resolved at Stage 1.

The discipline cuts both ways. If during Stage 4 a contradiction surfaces (the implementation reveals an unstated decision), DISCOVERY may re-engage briefly per AP-8 (and Rule 5.1) — not the whole questioning loop, just the specific resolution. Phase-bound DISCOVERY is the goal.

For AI-assisted development specifically: AI may have an instinct toward completeness (training data rewards thorough answers). The instinct toward "let me make sure I have all the edge cases" can defeat operational-scope discipline. Defense: explicit four-component check before continuing to question.

**Related anti-patterns:** AP-4 (over-questioning past scope-operational), AP-8 (discovery as one-time pass) (see `anti-patterns.md`)

---
