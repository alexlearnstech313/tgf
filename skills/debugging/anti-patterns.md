# Anti-Patterns + Canonical Patterns — DEBUGGING

Full anti-pattern + canonical pattern pairs with concrete examples. Referenced from `SKILL.md` §6 Anti-Pattern Summaries.

Eight anti-pattern pairs covering the most common debugging failures, including AI-specific failure modes. Per `DEC-2026-05-17-003` Clause 1: every anti-pattern is paired with a canonical pattern.

---

## AP-1: Fixing without reproducing

**Pattern:**

```
User reports: "The export to CSV is broken — it's only including some
of the rows."

Developer: "Oh, I bet I know what that is. The pagination must not be
applying correctly. Let me fix it."

[Without reproducing the bug — without running the export, without
checking which rows are missing, without verifying the pagination
behavior — developer modifies the pagination logic.]

Developer: "OK, pushed a fix. The pagination now starts at the right
offset."

[Three days later, user reports: "It's still happening. Some rows
are missing from the export."]

Developer: "Hmm. Let me look again."

[Turns out the bug was in the WHERE clause filtering, not pagination
at all. The "fix" applied was to working code; the real bug was
elsewhere. The developer never confirmed the symptom matched their
theory because they never reproduced.]
```

**Violates:** Rule 5.1 (reproduce reliably before hypothesizing). See `rules.md#rule-51-reproduce-reliably-before-hypothesizing`.

**Why it fails:** Without reproduction, the "fix" is speculative — there's no way to verify that the change actually addresses the bug, because the original bug state isn't established. The developer applied what THEY thought might be the issue; the actual issue was elsewhere; production still has the bug; trust erodes.

**Source for failure mode:** Common engineering anti-pattern, often driven by time pressure or "I'm sure I know what this is." Agans' rule #2 (Make it fail) exists exactly to counter this.

### CP-1: Reproduce first, then hypothesize

**Pattern:**

```
User reports: "The export to CSV is broken — it's only including some
of the rows."

Developer: "Let me reproduce it before I theorize.

Step 1: I'll export the same data the user did. Looking at the
parameters they sent... they exported a date range 2026-01-01 to
2026-03-31. I'll do the same export.

Step 2: I expect 1,247 rows based on a direct query against the
database. Let me check what the export actually produced.

[Runs the export.]

Result: 832 rows. So 415 rows are missing. Reproducible. Good.

Step 3: Which 415 rows are missing? Let me query the IDs from the
expected set vs the exported set and find the diff.

[Queries the diff.]

Pattern: all the missing rows have status='archived'. The export
is filtering out archived rows somewhere — but the user's filter
parameters didn't request that filtering.

Hypothesis: the WHERE clause has an implicit `AND status != 'archived'`
that's being added incorrectly, OR the JOIN with a status table is
inner-joining when it should outer-join.

[Now investigates the actual code in the export pipeline against the
specific hypothesis the reproduction surfaced.]

Found it: the export query JOINs against a status reference table to
get the display name; the JOIN type is INNER, which excludes rows
where status_id doesn't match (which happens for archived rows whose
status reference was deleted in a separate cleanup).

Fix: change INNER JOIN to LEFT JOIN.

[Re-runs the export. Now produces 1,247 rows. Reproduction confirms
the fix.]
```

**Pairs with:** Anti-pattern AP-1

**Why it works:** Reproduction first — the bug is established as a reliable, observable phenomenon before any hypothesis. The reproduction itself surfaces information (415 missing rows; all archived; same pattern) that points toward the actual cause. The fix is verified by re-running the reproduction. The "fix" is now genuinely a fix, not a hopeful patch.

---

## AP-2: Reasoning over reading

**Pattern:**

```
Developer encounters a test failure:

  ✗ should return user data when ID is valid
    Expected: { id: 123, name: 'Alice' }
    Received: null

Developer: "Hmm. The function definitely returns a user object for
valid IDs — I just looked at the code. Maybe the test is using a
stale fixture. Let me regenerate the fixtures."

[Regenerates fixtures. Test still fails.]

Developer: "Weird. Maybe there's a cache. Let me clear the test
cache."

[Clears cache. Test still fails.]

Developer: "What if the test database is in a bad state? Let me
reset it."

[Resets DB. Test still fails.]

[Two hours in, finally reads the actual function output by adding
a console.log. Discovers the function returns null when the user
exists but their account is in 'pending_verification' state — a
condition added in a recent commit. The test fixture happens to
create a user in that state. The function was returning null
correctly; the test fixture was wrong; the test name "should
return user data when ID is valid" was misleading because the
user IS valid in one sense (exists in DB) but not in another
(verified).]
```

**Violates:** Rule 5.2 (quit thinking and look). See `rules.md#rule-52-quit-thinking-and-look`.

**Why it fails:** The developer reasoned about what the code SHOULD do ("it definitely returns user data for valid IDs") rather than looking at what it actually returns. The reasoning was based on an out-of-date mental model; the recent commit added a verification check the developer didn't know about. Two hours of speculative fixes (regenerate fixtures, clear cache, reset DB) didn't address the bug because the bug was in the developer's understanding, not the system's behavior. One observation (`console.log` the return value, or read the function body for recent changes) would have surfaced the issue in 30 seconds.

**Source for failure mode:** Very common — debugging by mental model rather than by observation. AI especially prone to this.

### CP-2: Look first, then reason

**Pattern:**

```
Developer encounters the same test failure.

Developer: "Let me look at what's actually happening before I theorize.

Step 1: What does the function actually return for this input? I'll
add a print statement OR use a debugger.

[Adds debug output.]

Function returned: null
Input was: { id: 123 }
Function found user: { id: 123, name: 'Alice', status: 'pending_verification' }
Function entered the null-return branch at line 47 because:
  user.status === 'pending_verification' returned true

So the function IS returning null, deliberately, because of the
pending_verification check.

Step 2: When was that check added? git blame on line 47.

  commit 8c4d2a1f — 2 days ago — Add pending_verification gate to
  user-data endpoints (refs SEC-2026-03-15-002)

OK, so this is intentional behavior added 2 days ago for a security
finding. The test fixture creates the user in pending_verification
state; the function correctly returns null for such users; the test
expectation was wrong because the test wasn't updated when the
security gate was added.

Fix: update the test fixture to create a verified user, OR update
the test name and expectation to verify that pending_verification
users return null."
```

**Pairs with:** Anti-pattern AP-2

**Why it works:** Observation first. The actual return value, the actual execution path, the actual commit history are all data — the developer reads them before reasoning. The bug surfaces in two minutes; the fix follows from understanding (test fixture or test expectation needs update); no speculative work was done on wrong hypotheses.

---

## AP-3: Multiple simultaneous changes

**Pattern:**

```
Developer faces a flaky intermittent test — sometimes passes,
sometimes fails.

Developer: "OK, several things look suspicious. Let me try a few
changes at once:

1. Add a longer timeout to the network mock
2. Update the test data to use a fixed seed instead of Date.now()
3. Add an explicit 'await' I noticed was missing
4. Reorder the setup to initialize the DB before the cache
5. Increase the test runner's parallel limit so tests don't race
   for resources

That should cover the likely causes."

[Pushes all 5 changes. Test passes on next 10 runs. Developer
moves on, satisfied.]

[Two months later, the test starts failing intermittently again.
Developer looks at the diff from the original fix — 5 changes
across 3 files, all in one commit. Can't tell which one mattered;
maybe ALL of them mattered; maybe none of them and the bug just
hid for 2 months. Debugging restarts from scratch with worse
audit trail.]
```

**Violates:** Rule 5.3 (change one thing at a time). See `rules.md#rule-53-change-one-thing-at-a-time`.

**Why it fails:** The multi-change "fix" worked initially (or appeared to), but the team has no idea WHY. When the bug returns, all 5 changes are still in place — so whichever was the real fix is no longer there to verify; whichever was unnecessary is still adding code surface; the team can't undo just the unnecessary ones because they don't know which those are.

**Source for failure mode:** Time pressure + "everything looks suspicious" reaction. Often inadvertent — the developer doesn't realize they're confounding their experiment.

### CP-3: One change per test, audit-trailed

**Pattern:**

```
Developer faces the same flaky intermittent test.

Developer: "Multiple suspects. Let me test each one independently
and record what happens.

Hypothesis 1: Date.now() seeding makes data different per run.
  Change: use fixed seed
  Test runs: 20
  Result: 14 pass, 6 fail. Doesn't fully fix flakiness.
  Revert change. Note: this WASN'T the root cause but may be a
  cleanup worth doing separately.

Hypothesis 2: Missing await in setup.
  Change: add the await
  Test runs: 20
  Result: 20 pass. Run again: 20 pass. Run a third time: 20 pass.
  Looks like the fix.

Verify by reverting the await: yes, flakiness returns.
Reapply the await: yes, flakiness is gone.

The missing await was the root cause — it allowed a race condition
where the test sometimes ran before setup completed.

Ship JUST the await fix. Open a separate cleanup ticket for the
Date.now() seeding, since it's good practice but not what caused
this bug."

Audit trail (in session log):
  - Hypothesis 1 (Date.now seeding): tested, ruled out, not the
    root cause. Worth cleanup separately.
  - Hypothesis 2 (missing await): tested, confirmed via revert/reapply
    cycle. Root cause. Shipped.
  - Other hypotheses (mock timeout, init order, parallel limit) not
    tested — the confirmed root cause makes them unnecessary to
    investigate.
```

**Pairs with:** Anti-pattern AP-3

**Why it works:** Each change is tested in isolation. The audit trail records what was tried and what happened. The confirmed root cause is verified via revert/reapply — confirming it's both necessary and sufficient. Only the actual fix ships; speculative changes that turned out to not matter don't accumulate. Future occurrences of similar bugs can build on this audit trail.

---

## AP-4: Symptom patching

**Pattern:**

```
Iteration 1:
User: "The user list page is slow."
Developer: "I'll add a cache to the user list query."
[Adds Redis cache with 5-minute TTL.]
Result: page is fast.

Iteration 2 (1 month later):
User: "The user list shows stale data for new signups."
Developer: "I'll add cache invalidation when a new user signs up."
[Adds invalidation logic.]
Result: new signups appear immediately.

Iteration 3 (2 months later):
User: "The user list shows stale data when users are edited."
Developer: "I'll add cache invalidation on user updates too."
[Adds more invalidation.]
Result: edits appear.

Iteration 4 (3 months later):
User: "The user count badge is wrong — it's higher than the actual
list."
Developer: "Hmm, the badge isn't going through the cache. Let me
add caching to that too with invalidation..."

[Pattern continues. Each new symptom gets its own patch. Cache
invalidation logic accumulates across 8 different mutation paths.
Eventually a cache invalidation is missed; user complaints about
stale data return; team spends time hunting which invalidation
was forgotten.]

[Root cause never addressed: the user list query was slow because
the user table had no index on the columns being filtered. A
single CREATE INDEX would have made the query fast without any
caching, eliminating the entire cache-invalidation maintenance
surface.]
```

**Violates:** Rule 5.4 (Five Whys for root cause, not symptom patch). See `rules.md#rule-54-five-whys-for-root-cause`.

**Why it fails:** Each fix addressed the immediate visible symptom — slowness, then staleness, then more staleness. The root cause (missing index) was never investigated because the cache "fixed" the slowness. Now the team maintains cache invalidation logic across the entire mutation surface forever, every new mutation path is a risk of staleness, and the root cause is still there waiting to surface again if the cache is ever bypassed or invalidated incorrectly.

**Source for failure mode:** Common when debugging follows "make the immediate problem go away" rather than "understand why the immediate problem happened."

### CP-4: Five Whys to root cause; fix the root

**Pattern:**

```
Iteration 1:
User: "The user list page is slow."

Developer: "Before I add a cache, let me find the actual root cause.

Why 1: Why is the user list page slow?
  → The /api/users query is taking 2.4 seconds.

Why 2: Why is the query slow?
  → EXPLAIN ANALYZE shows a full table scan on the users table.

Why 3: Why is there a full table scan?
  → The query filters on (organization_id, status) but there's no
    index on those columns.

Why 4: Why is there no index?
  → The original schema had only PRIMARY KEY (id). When organization_id
    was added later, no index was added with it.

Why 5: Why wasn't an index added?
  → No process for index reviews on new columns.

Root cause: missing index. Contributing cause: no process for
index reviews.

Immediate fix: add a composite index on (organization_id, status).

Run EXPLAIN ANALYZE again: 12ms (down from 2.4s). No cache needed.

Process fix: open a separate ticket for an index-review checkpoint
in the migration review process."

[6 months later: zero cache-invalidation bugs because there's no
cache. All filter combinations remain fast because the index covers
the query pattern. New signup, edit, delete — all immediately
visible because there's no cache layer. Maintenance surface is
zero for this query.]
```

**Pairs with:** Anti-pattern AP-4

**Why it works:** Five Whys traced the chain to the root cause (missing index). The fix addresses the root, not the symptom. No cache, no invalidation logic, no cascading bugs. The contributing cause (no process for index reviews) is captured for separate process improvement.

**Additional considerations:** Sometimes a symptom-patch IS the right immediate fix (production incident requires speed; root cause fix requires migration). In those cases, fix the symptom AND log the root cause to ERROR-LOG with a target date for the proper fix. The discipline is knowing WHICH you're doing, not unconsciously symptom-patching.

---

## AP-5: No audit trail

**Pattern:**

```
March 2026:
[Production incident: payment processing intermittently fails with
"connection reset by peer" errors. Team spends 3 days investigating.
Eventually narrows down to a misconfigured connection pool setting
in the Stripe SDK initialization. Changes pool size from default to
explicit value. Bug stops. Team ships fix, closes incident, moves on.]

[Session log says: "Fixed payment processing bug. Connection pool
configured."]

September 2026:
[Same symptom returns: payment processing intermittent connection
resets. New developer on the team investigates.]

New developer: "Has this happened before? Let me search the session
logs and ERROR-LOG."

[Finds the March 2026 entry: 'Fixed payment processing bug. Connection
pool configured.' No details on what the connection pool issue was,
what value was set, what evidence pointed to that, or what was tried
and ruled out.]

New developer: "Cool, but I have no idea what the actual fix was or
how to verify. Let me start from scratch."

[Spends 2 more days repeating the same investigation. Eventually
realizes someone reverted the pool size change in an unrelated
refactor. Reapplies it; bug fixed. Updates the session log: 'Fixed
again, see March 2026 entry.' (Still no detail.)]
```

**Violates:** Rule 5.5 (keep an audit trail) AND CONTINUITY Rule 5.6 (capture WHY, not just WHAT). See `rules.md#rule-55-keep-an-audit-trail`.

**Why it fails:** The audit trail captured the outcome ("fixed") without the substance (what was the connection pool issue? what specific change worked? what was tried and ruled out? what evidence supported the diagnosis?). When the same bug returned, the trail was useless. The team paid the debugging cost twice. Subsequent occurrences will likely pay it a third time.

**Source for failure mode:** Time pressure at incident close — "we fixed it, move on" — combined with weak CONTINUITY discipline. Specific to debugging because debugging knowledge is often the easiest to lose.

### CP-5: Detailed audit trail with cause + fix + verification

**Pattern:**

```
March 2026 session log entry (after the fix):

## Production incident: payment processing intermittent failures (2026-03-15)

### Symptom
Payment processing failing intermittently with "connection reset by
peer" errors. ~5-10% of attempts. Affects Stripe charge creation
specifically.

### Reproduction
Reliably reproduces under load: 100 concurrent charge attempts. ~7%
fail with the connection reset.

### Investigation
1. Initial hypothesis: Stripe API issues. Ruled out — checked Stripe
   status page (all green) and dashboard (showing successful charges
   during the same window).
2. Hypothesis: TLS handshake issues. Ruled out — packet capture shows
   handshake succeeds, then connection is reset mid-request.
3. Hypothesis: connection pool exhaustion. CONFIRMED —
   `stripe.HTTPClient` default pool size is 5; under load >5 concurrent
   requests, additional connections were being created and torn down
   rapidly, with occasional resets.

### Root cause
Stripe SDK initialization didn't explicitly configure the connection
pool. The SDK's default of 5 is too small for our load profile.

### Fix
In `src/payments/stripe-client.ts`:
```typescript
const stripe = new Stripe(secretKey, {
  maxNetworkRetries: 3,
  httpAgent: new https.Agent({
    keepAlive: true,
    maxSockets: 50,  // Was using default of 5
  }),
});
```

### Verification
Re-ran reproduction (100 concurrent charges): 100/100 succeeded.
Sustained 1000-charge run: all succeeded.

### Why this might recur
The HTTP agent configuration lives in stripe-client.ts. If that file
is refactored or rewritten without preserving the explicit `maxSockets`,
the bug returns. Adding a comment in the code and a test that runs
under load would catch a future regression.

### Follow-ups
- [x] Add load test: `tests/load/payments.load.test.ts` runs 100
  concurrent charges as part of nightly tests.
- [ ] Add comment in stripe-client.ts referencing this incident.
- [ ] Document the pool size choice in DECISIONS.md (will be ADR
  DEC-2026-03-15-001 — "Stripe HTTP agent maxSockets=50 due to
  observed connection pool exhaustion at default of 5").
```

[September 2026: the same symptom returns. New developer searches
session logs.]

New developer: "Let me check prior incidents... Found one: March
2026, full audit trail. Root cause was Stripe connection pool size.
Let me check if the config is still in place."

[Reads stripe-client.ts. The maxSockets line is gone — someone
removed it in an unrelated refactor. Comment about the incident also
gone.]

[Reapplies the configuration. Runs the load test (which exists from
the prior fix's follow-up). Confirms bug is fixed.]

[Updates the session log: "Same root cause as 2026-03-15 incident.
Configuration was removed in commit X during refactor Y. Reapplied
and verified via existing load test. Adding ADR DEC-2026-09-XX-NNN
to formalize the constraint so future refactors don't drop it
silently."]

[Total time: ~30 minutes. The prior audit trail saved 2 days of
investigation.]
```

**Pairs with:** Anti-pattern AP-5

**Why it works:** Detailed audit trail captures the substance of debugging — what was reproduced, what was tried, what worked, what root cause was identified, how the fix was verified, what makes future recurrence likely. When the bug returns, the trail is operationally useful — the next debugger picks up at the last known good state and verifies whether the prior fix is still in place, rather than re-investigating from scratch.

---

## AP-6: Staring at the same screen

**Pattern:**

```
Developer encounters a tricky bug. Starts investigating at 9 AM.

10 AM: Tried adjusting the regex; doesn't help.
11 AM: Added more logging; the logs don't show anything obviously
       wrong but the bug still happens.
12 PM: Refactored the function structure thinking that might surface
       the issue; doesn't help.
1 PM: Lunch at the desk while still investigating. Same code, no
       new ideas.
2 PM: Tried swapping the iteration order; doesn't help.
3 PM: Re-reading the same function for the 20th time. Eyes are
       glazing. Frustration mounting.
4 PM: Tried a wild reorganization of the data structure; broke
       three unrelated tests.
5 PM: Reverted everything. Still no progress on the actual bug.
      Goes home defeated.

[Next morning, opens the laptop, looks at the function for 2 minutes,
sees the issue immediately. Off-by-one error in a loop condition,
visible on first read with fresh eyes.]
```

**Violates:** Rule 5.6 (get a fresh view when stuck). See `rules.md#rule-56-get-a-fresh-view-when-stuck`.

**Why it fails:** Cognitive narrowing sets in. After hours of looking at the same code, the developer's mental model becomes rigid; they see what they expect to see, not what's there. The "fresh view" that would unblock them in 2 minutes never gets a chance because they don't take it. The cost: a full day of unproductive work + frustration + risk of breaking unrelated things in failed-fix attempts.

**Source for failure mode:** "One more try" mentality + reluctance to interrupt others + sunk-cost feeling. Very common; rarely productive.

### CP-6: Recognize stuck-ness; act on it

**Pattern:**

```
Developer encounters the same bug. Starts at 9 AM.

10 AM: Tried adjusting the regex; doesn't help.
11 AM: Added more logging; logs don't surface the issue.

Developer: "I'm 2 hours in with no progress and the hypotheses are
getting random. Time for a fresh view."

Option A — Rubber duck:
"Let me explain this bug to my coworker over Slack. Even just typing
it out should help."

[Types up: 'I have a function that should process items 1-10 from
an array. It's processing items 1-9. I've tried adjusting the loop,
the logging is clean, but item 10 never gets touched.']

[Halfway through typing, realizes: "Oh wait — I'm using `< array.length`
not `<= array.length - 1` somewhere, OR `< array.length - 1` instead
of `< array.length`. Let me check."]

[Off-by-one found in 5 minutes.]

Option B — Step away:
"Going to take a 20-minute walk. I'll look at this fresh when I get
back."

[Returns. Reads the code from the top. Sees the off-by-one in 3
minutes.]

Option C — Ask a colleague:
"Hey, can you look at this for 5 minutes? I'm stuck."

[Colleague reads it. Within 2 minutes: 'You're missing a `+ 1` here.']

[Off-by-one found in 5 minutes.]

[Either way: 2 hours stuck + 5 minutes fresh view = 2:05. Compared
to AP-6's 8 hours stuck + 0 progress = 8:00. Net savings: ~6 hours
of debugging plus reduced risk of breaking unrelated things.]
```

**Pairs with:** Anti-pattern AP-6

**Why it works:** Recognition + action. The developer notices stuck-ness (2 hours, hypotheses getting random) and acts on Rule 5.6 — rubber duck, walk, or colleague. Any of the three options works; the discipline is doing one of them rather than continuing to stare.

**Additional considerations:** Rubber-ducking via AI ("let me explain this bug to AI") is a partial substitute, but per Rule 5.7, AI output is hypothesis not conclusion — and AI may be a *false* fresh view that reinforces the same wrong hypothesis. Human fresh views (or just stepping away yourself) are usually more reliable.

---

## AP-7: AI explanation accepted as truth

**Pattern:**

```
Developer pastes a stack trace and code into AI:

"This function is throwing a TypeError. Here's the code and the
stack trace. What's wrong?"

AI responds confidently: "The issue is on line 23 — you're calling
`user.profile.email` but `profile` can be null when the user record
is partial. You need a null check there:

```typescript
const email = user.profile?.email ?? '';
```

That should fix the TypeError."

Developer: "Great, thanks." [Applies the fix exactly as suggested.
Runs the test. Test still throws TypeError.]

Developer: "Hmm. Let me look more carefully."

[Actually reads the stack trace. The TypeError is on line 47, not
line 23. It's because `user.preferences.notifications` is undefined,
not because of `user.profile`. The user.profile check AI suggested
was completely orthogonal to the actual bug. AI fabricated a
plausible-sounding root cause that happened to be wrong.]

[Real fix: add null check at line 47 for `preferences.notifications`.]
```

**Violates:** Rule 5.7 (AI debug outputs are hypotheses, not conclusions) AND Rule 5.2 (quit thinking and look). See `rules.md#rule-57-ai-debug-outputs-are-hypotheses`.

**Why it fails:** AI's explanation read confident and plausible. The developer accepted it as truth without verifying against the actual stack trace. The "fix" applied was orthogonal to the real bug — it might even be a defensive improvement, but it didn't address the TypeError. The bug remained; debugging time was wasted on a wrong cause; trust in AI debugging help may erode (when it could have been useful as a hypothesis-generator, just not as a conclusion-deliverer).

**Source for failure mode:** AI confidence + developer time pressure + lack of verification discipline. Common.

### CP-7: AI output as hypothesis; verify before acting

**Pattern:**

```
Developer pastes a stack trace and code into AI:

"This function is throwing a TypeError. Here's the code and the
stack trace. What's wrong?"

AI responds: "The issue is on line 23 — you're calling
`user.profile.email` but `profile` can be null. You need:
`user.profile?.email ?? ''`"

Developer: "OK, that's a hypothesis. Let me verify before I act on it.

Step 1: Does the stack trace actually point to line 23?

[Reads the actual stack trace.]

Stack trace says line 47, not 23. AI's hypothesis is wrong about the
location.

Step 2: What's actually on line 47?

[Reads line 47.]

Line 47: `const wantsEmails = user.preferences.notifications.email;`

`preferences` could be null. `notifications` could be undefined.
Most likely cause of the TypeError.

Step 3: Verify by reproducing with debug output.

[Adds debug log before line 47:]
`console.log('user.preferences:', user.preferences);`

[Runs the failing case.]

Output: `user.preferences: undefined`

Confirmed. The bug is `user.preferences` being undefined. AI's
hypothesis (profile being null) was wrong.

Real fix: add null check at line 47 for preferences AND notifications:
`const wantsEmails = user.preferences?.notifications?.email ?? false;`

[Verifies the fix against the reproduction. Bug fixed.]"

[Optional: report back to AI: "Actually the bug was on line 47, not
23. The fix you suggested wouldn't have addressed the real issue."
AI updates its hypothesis. Useful pattern for collaborative debugging
with AI as one of several inputs, not the source of truth.]
```

**Pairs with:** Anti-pattern AP-7

**Why it works:** AI's output is treated as a hypothesis. The developer verifies against the actual stack trace (Rule 5.2 — quit thinking and look) and the actual reproduction (Rule 5.1). The verification disconfirms AI's hypothesis. The developer finds the real cause by following the actual evidence. Time spent verifying: 5 minutes. Time saved by not applying the wrong fix and discovering the bug persists: hours.

---

## AP-8: "Fixed" without verification

**Pattern:**

```
Developer is debugging a bug.

[Reproduces it. Investigates. Forms hypothesis. Applies fix.]

Developer: "OK, this should fix it. The change I made addresses
the root cause I identified. Let me commit and move on."

[Commits the fix with message "Fix user export bug." Pushes. Closes
the related ticket. Doesn't re-run the reproduction.]

[Two days later, user reports: "The user export is still failing
with the same error."]

Developer: "What? I fixed that two days ago."

[Pulls the latest. Re-runs the reproduction. The bug is still
present. The "fix" was applied correctly but didn't address the
actual cause — the hypothesis was wrong, and without re-running
the reproduction, the developer never knew.]
```

**Violates:** Rule 5.1 (reproduce reliably — including using the repro to verify) AND the verification discipline of `docs/WORKFLOW.md` §7 (Stage 6: verify the fix). Agans rule #9: "if you didn't fix it, it ain't fixed."

**Why it fails:** The developer assumed the fix worked because the change matched their hypothesis about the cause. They never closed the loop by re-running the reproduction to confirm the bug no longer reproduces. The fix shipped; the bug shipped with it; the user discovered the failure in production.

**Source for failure mode:** Time pressure + sunk-cost feeling ("I've already spent time on this, I'm sure it's fixed") + skipping verification because reproduction is tedious to re-run.

### CP-8: Verify the fix against the reproduction before declaring done

**Pattern:**

```
Developer is debugging the same bug.

[Reproduces it. Investigates. Forms hypothesis. Applies fix.]

Developer: "OK, I think this addresses the root cause. Before I
commit, let me verify by re-running the reproduction.

Step 1: Re-run the exact reproduction that surfaced the bug.

[Runs the export with the same parameters that produced the original
failure.]

Result: Export succeeds. 1,247 rows returned. Matches the expected
output.

Step 2: Verify a related case also works.

[Runs a different date range to make sure the fix didn't break other
cases.]

Result: That also works correctly.

Step 3: Verify the fix is necessary by reverting and reconfirming
the bug returns.

[Reverts the fix. Re-runs the reproduction.]

Result: Bug returns (832 rows instead of 1,247).

[Reapplies the fix.]

Result: 1,247 rows. Bug stops.

The fix is BOTH necessary (reverting brings the bug back) AND
sufficient (applying it fixes the bug). Confidence is high.

Step 4: Add a regression test so this doesn't happen again.

[Writes a test that exercises the previously-broken case. Confirms
test passes with the fix and fails without it.]

Now committing with confidence."

[Commits with detailed message including reproduction + fix +
verification trail per CONTINUITY Rule 5.6. Closes ticket with a
note about the regression test.]
```

**Pairs with:** Anti-pattern AP-8

**Why it works:** Verification closes the loop. The fix is confirmed against the actual reproduction. Bonus: necessary-and-sufficient verification (revert → bug returns → reapply → bug gone) provides higher confidence than just "fix applied → bug gone in one test." Regression test prevents recurrence. The fix that ships is genuinely a fix, not a hopeful patch.

---

## Pairing discipline

Per `DEC-2026-05-17-003` Clause 1: every anti-pattern is paired with a canonical pattern.

When a new DEBUGGING anti-pattern is observed during use but no clear canonical pattern is obvious, log to `WAIVER-LOG.md` for revisit rather than shipping a one-sided entry. AI-specific debugging failure modes evolve as AI capabilities change — keep `self-evolution.ai-failures-documented` updated as new patterns surface.
