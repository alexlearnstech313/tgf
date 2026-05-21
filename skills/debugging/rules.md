# Rules — DEBUGGING

Full rule statements with citations, plain-language impact, and extended discussion. Referenced from `SKILL.md` §5 Rule Summaries.

Seven rules distilled from David Agans' 9 rules (2002/2006), Sakichi Toyoda's Five Whys, and the scientific method. The mapping to Agans' 9 rules: Rule 5.1 ↔ Agans #2, Rule 5.2 ↔ Agans #3, Rule 5.3 ↔ Agans #5, Rule 5.5 ↔ Agans #6, Rule 5.6 ↔ Agans #8. Agans rules #1 (understand the system), #4 (divide and conquer), #7 (check the plug), and #9 (if you didn't fix it, it ain't fixed) are referenced throughout but not promoted to standalone TGF rules (they're operational tactics rather than rule-level discipline).

Citation discipline per `DEC-2026-05-17-004`: AGANS-9 cited at the rule level since Agans' book numbers them; TOYODA-5W cited at methodology level (no sub-rule structure exists); SCIENTIFIC-METHOD cited at methodology level (stable framework, centuries old).

---

## Rule 5.1: Reproduce Reliably Before Hypothesizing

**Statement:** Before hypothesizing causes or attempting fixes, establish a reliable reproduction of the bug. "Reliable" means: given the same input + environment, the bug appears consistently. Without reliable reproduction, fixes can't be verified (you can't know if the fix worked or if the bug just didn't happen this time), hypotheses can't be tested (you can't predict an outcome and check it), and "fixed" is unmeasurable.

**Citation:** `AGANS-9 rule #2 (Make it fail)`. Agans frames this as foundational: "If you can't make it fail, you can't fix it" — debugging without reproduction is patching what you think the bug is, not the actual bug.

**Plain-language impact:** Without reproduction, debugging becomes guesswork dressed as engineering. The developer applies what they think is the fix; the bug either doesn't surface in test (which doesn't mean fixed — it might just not have triggered) or surfaces again in production (which means the fix wasn't actually a fix). Trust erodes; the debugging process accumulates "fixes" that don't fix; future incidents are harder to diagnose because the audit trail is full of attempts that may or may not have addressed real causes.

**Extended discussion:** Getting to reliable reproduction often takes more time than the subsequent fix. That's normal. The reproduction work uncovers what's actually involved — which inputs trigger it, which environment factors matter, what state has to be present. This information is the data the rest of the debugging session works against.

When reproduction is hard:

- **Intermittent bugs** ("happens sometimes") — find the conditions that change between happens and doesn't-happen. Often involves timing, concurrency, or state accumulation.
- **Production-only bugs** ("can't reproduce locally") — get production-like data, replicate the load pattern, match the deployment configuration. The gap between local and production IS often the bug.
- **User-reported bugs without details** — engage DISCOVERY (Phase 5 commit 1/8) to extract reproduction steps from the user. "Can you walk me through exactly what you did?" Often surfaces the missing input or sequence.
- **Bugs that disappear when you observe them** ("Heisenbug") — typically timing-related; the act of observation slows execution enough to mask the race. Use logging that's lightweight enough not to perturb timing, or use replay tools.

Per `docs/WORKFLOW.md` §7 (Debugging Variant), reproduction is Stage 1. Termination condition "cannot reproduce" exists for cases where extensive reproduction effort fails — but it's logged to ERROR-LOG (per CONTINUITY Rule 5.3) so future incidents can build on the prior reproduction attempts.

For AI-assisted development: AI sometimes proposes fixes without reproducing the bug — the proposal is based on reading the code, not running the failing case. Per `docs/ARCHITECTURE.md` §16 (Empirical Verification for AI-Generated Code), the discipline is to run the code and observe behavior, not reason about it. Rule 5.1 IS that discipline applied to bugs.

**Related anti-patterns:** AP-1 (fixing without reproducing), AP-8 (fixed without verification) (see `anti-patterns.md`)

---

## Rule 5.2: Quit Thinking and Look

**Statement:** Read the actual error message, the actual stack trace, the actual log line, the actual database value, the actual network response, the actual computed result. Don't reason about what should be happening; observe what IS happening. AI is especially prone to reasoning over reading — explaining what the code should produce instead of looking at what it actually produced.

**Citation:** `AGANS-9 rule #3 (Quit thinking and look)`. Agans names this rule explicitly because it's one of the most-violated debugging disciplines. Developers (and AI) generate explanations from imagination instead of from observation.

**Plain-language impact:** Reasoning over reading produces confident wrong answers. The developer thinks "the function should return X, so the test failure must be a test problem" without reading the actual return value. The actual return is Y; the test was right; the bug is in the function. By reasoning past the observation, the developer wastes time investigating non-bugs and misses the real one.

**Extended discussion:** "Look" means: open the log file. Read the full stack trace, not just the top frame. Check the actual value with a debugger, a print statement, a database query. Inspect the network request and response in DevTools. Pull the production state. The observation IS the data.

Common observation surfaces:

- **Stack traces.** Read top to bottom. The top frame is where the error surfaced, not always where the cause lives. Look for the first frame in YOUR code; that's usually where the investigation starts.
- **Error messages.** Read the FULL message. Library error messages often have informative detail past the first line ("Connection refused: localhost:5432") that pinpoints the cause.
- **Log lines.** Read what was logged before AND after the error. The state leading up to the error is often the data the explanation needs.
- **Database values.** Don't assume what's in the DB; query it. The mismatch between assumed state and actual state is often the bug.
- **Network requests / responses.** Don't assume the API returned what it said it would. Inspect the actual response. Status codes, headers, body — all data.
- **Memory / CPU / disk.** "Slow" or "hangs" often points to resource exhaustion. Check the actual resource state during the incident.

For AI-assisted development specifically: AI tends to read CODE and reason about what it does, rather than read OUTPUT and look at what it produced. The defense is asking AI: "what did the actual error message say?" If AI doesn't know, fetch it. Don't proceed on AI's interpretation without grounding in observation.

**Related anti-patterns:** AP-2 (reasoning over reading), AP-7 (AI explanation accepted as truth) (see `anti-patterns.md`)

---

## Rule 5.3: Change One Thing at a Time

**Statement:** When testing fixes or isolating variables, change one thing per attempt. Multiple simultaneous changes — "I'll fix A and B and C at once and see if the bug stops" — destroy the audit trail. When the bug stops happening, you don't know which change mattered; you can't reproduce the fix for the next occurrence; you may have shipped two cosmetic changes and one real fix without knowing which is which.

**Citation:** `AGANS-9 rule #5 (Change one thing at a time)` + `SCIENTIFIC-METHOD` (control-variable discipline applied to debugging).

**Plain-language impact:** Multi-change debugging produces unreliable fixes. The bug stops happening after three changes; the developer is happy; the next occurrence comes weeks later; the team doesn't remember which of the three changes mattered; debugging restarts from scratch. Worse, two of the three changes may have introduced subtle regressions whose effects don't surface until later — and the team can't reverse just those because the audit trail is muddy.

**Extended discussion:** "One thing at a time" applies at debugging time, not commit time. When experimenting with fixes:

- Change ONE variable. Test. Observe the result.
- If the bug still happens, undo that change. Try a different ONE.
- If the bug stops, you've narrowed it. Now test whether the change is necessary AND sufficient (does the bug return if you undo it again?).

The audit trail logs each change attempted and its outcome. When the right change is identified, that's what ships — not the accumulated multi-change diff.

When multiple changes feel necessary to fix the bug, that's a signal: either the bug has multiple independent causes (separate them, fix each), or the proposed multi-change fix is over-correcting. Investigate which.

The discipline overlaps with the scientific method's control-variable principle. Each fix attempt is an experiment; controlling other variables means changing only the variable you're testing. Confounded experiments don't yield conclusions.

For AI-assisted development: AI often proposes multi-change fixes — "fix A, B, and C — they all look related." Treat each as a separate hypothesis; test individually. If A alone fixes it, B and C may be cosmetic noise or speculative cleanup that adds risk without addressing the bug.

**Related anti-patterns:** AP-3 (multiple simultaneous changes) (see `anti-patterns.md`)

---

## Rule 5.4: Five Whys for Root Cause, Not Symptom Patch

**Statement:** The reported bug is usually a symptom — the visible end of a chain of causes. Patching the symptom leaves the underlying cause to resurface elsewhere (often as a different-looking bug, making it hard to recognize as related). Five Whys (Sakichi Toyoda, Toyota Production System) traces back through the chain until the root cause is reached. "Five" is not literal — sometimes 3 is enough, sometimes 7 is needed — but the discipline is to keep asking why until further whys stop yielding new information.

**Citation:** `TOYODA-5W (Five Whys methodology, ~1950s Toyota Production System)`. Stable methodology; cited at methodology level.

**Plain-language impact:** Symptom-patching is a pattern that generates more bugs over time. Each fix addresses the local visible problem; the root cause persists; new symptoms emerge from the same root; each new symptom gets its own patch. The codebase accumulates patches; the original bug never goes away; eventually the team is debugging across multiple patched symptoms that interact in new ways. Root-cause analysis breaks the cycle.

**Extended discussion:** The Five Whys pattern in practice:

1. **Symptom:** "The dashboard is slow."
2. **Why 1:** Why is it slow? "The query against the orders table is taking 8 seconds."
3. **Why 2:** Why is the query slow? "It's doing a full table scan on a 1M-row table."
4. **Why 3:** Why is there a full table scan? "There's no index on the `customer_id` column being filtered."
5. **Why 4:** Why is there no index? "The original developer didn't add one when the column was created."
6. **Why 5:** Why didn't they add one? "There was no process for index reviews on new columns."

Root cause: the lack of process for index reviews. Symptom-patch fix: add the index. Root-cause fix: add the index AND establish an index-review checkpoint for new columns going forward.

The right fix often addresses BOTH the symptom (current pain) AND the root cause (prevent recurrence). The Five Whys discipline ensures you SEE the root cause, even if you decide the immediate fix is just the symptom patch — with the root captured for follow-up.

When Five Whys terminates early: sometimes the chain is short. "Why is this test failing? Because the assertion is wrong." "Why is the assertion wrong? Because it was written against incorrect specifications." Two whys reaches the root in this case. The discipline is keep asking until the chain genuinely terminates, not "ask exactly 5 times."

For AI-assisted development: AI tends to propose the symptom patch ("slow query → add cache"). The Five Whys discipline counteracts this — keep asking why until the root surfaces, then decide what to fix.

**Related anti-patterns:** AP-4 (symptom patching) (see `anti-patterns.md`)

---

## Rule 5.5: Keep an Audit Trail

**Statement:** Log what was tried during debugging, what worked, what didn't, what was observed. The audit trail serves three purposes: (1) prevents repeating tried-and-failed attempts; (2) enables backtracking when a "fix" doesn't hold; (3) serves future debuggers (often future-you) who pick up the trail without starting from scratch. Per CONTINUITY Rule 5.1, session logs are the canonical capture for this.

**Citation:** `AGANS-9 rule #6 (Keep an audit trail)` + cross-reference `CONTINUITY Rule 5.1 (session-close log entry required)`.

**Plain-language impact:** Without an audit trail, debugging knowledge evaporates at session close. Six months later the same bug returns; the team doesn't remember what was tried last time; the entire investigation starts over. With a trail, the next debugger picks up at the last known good state — what was tried, what was ruled out, what's the leading hypothesis.

**Extended discussion:** The audit trail at minimum:

- **Reproduction details.** How is the bug reproduced? Input, environment, state preconditions.
- **Observations made.** What was looked at; what was found.
- **Hypotheses tested.** What was proposed; how was it tested; what was the outcome.
- **Fixes attempted.** What was changed; what was the result; if undone, why.
- **Leading hypothesis at session end.** If the bug isn't yet fixed, what's the current best theory?

This often lives in the session log (per CONTINUITY Rule 5.1) for in-progress debugging. When the bug is resolved, the resolution and root cause may be captured in DECISIONS.md (if architecturally interesting) or in the commit message (always) and ERROR-LOG.md if it's a tracked issue.

For multi-developer debugging or hand-offs, the audit trail becomes load-bearing — the next person needs to read the trail and continue without re-traversing ruled-out paths.

For AI-assisted development: AI sessions naturally produce some audit trail in conversation transcripts. But conversation transcripts are typically ephemeral (compacted, lost at session close); the discipline is capturing the load-bearing observations and outcomes into the session log durably.

**Related anti-patterns:** AP-5 (no audit trail) (see `anti-patterns.md`)

---

## Rule 5.6: Get a Fresh View When Stuck

**Statement:** When extended debugging time produces no progress (typical signal: 30-60 minutes without new information), get a fresh view. Ask a colleague. Rubber-duck explain the problem out loud. Step away for 15 minutes and return. Walk away for the day if it's late. The "stuck view" stops yielding new information; the fresh view often catches what the stuck view can't.

**Citation:** `AGANS-9 rule #8 (Get a fresh view)`. Agans names this as a debugging discipline because the cost of "just one more hour of staring" usually exceeds the cost of getting fresh input.

**Plain-language impact:** Continued staring at the same problem after stuck-ness sets in is unproductive — and often counterproductive (frustration, cognitive narrowing, increased likelihood of breaking unrelated things in failed-fix attempts). The fresh view that could unblock you in 2 minutes waits because the stuck view won't let go. The discipline is recognizing the stuck state and acting on it.

**Extended discussion:** Signals you're stuck:

- Re-reading the same error message for the fifth time without new insight.
- Trying small variations of fixes that aren't working ("what if I add another semicolon?").
- Increasing frustration; thinking gets narrower not broader.
- Hour 3 of debugging with the same hypothesis you had hour 1.

Options for fresh view:

- **Rubber duck explanation.** Explain the bug out loud to an inanimate object (or a non-technical person). The act of articulating often surfaces the issue.
- **Ask a colleague.** Sometimes the fresh eyes see in 30 seconds what you missed in 3 hours.
- **Walk away and return.** Even 15 minutes of doing something else often resets cognition.
- **Sleep on it.** For end-of-day stuck-ness, the morning version of you is usually more useful than the late-night version.
- **Engage AI explicitly as a fresh view.** Per Rule 5.7, AI debug output is hypothesis not conclusion — but AI's "fresh view" can surface angles you haven't considered. Treat the output skeptically.

For AI-assisted development: AI is unfortunately a *false* fresh view sometimes — its confident output feels like a new perspective but may be reinforcing the same wrong hypothesis. Real fresh views from humans (or from stepping away yourself) are often more valuable.

**Related anti-patterns:** AP-6 (staring at the same screen) (see `anti-patterns.md`)

---

## Rule 5.7: AI Debug Outputs Are Hypotheses, Not Conclusions

**Statement:** When AI proposes a root cause, explains a stack trace, identifies a "this is the issue" line, or suggests a fix — the output is a *hypothesis*, not a *conclusion*. Test the hypothesis against actual observation (Rule 5.2) and actual reproduction (Rule 5.1) before acting on it. The most dangerous AI debugging failure mode is plausible-sounding wrong explanations that derail entire investigations.

**Citation:** `TGF-SYNTHESIS — grounded in MITRE-ATLAS observations on AI output failures + SCIENTIFIC-METHOD discipline`. No single authoritative source codifies this at sub-rule level; the rule synthesizes AI-output skepticism with scientific-method hypothesis-testing.

**Plain-language impact:** AI debug output reads confident. The explanation sounds coherent; the proposed cause sounds reasonable; the suggested fix seems sensible. But "sounds confident" and "is correct" are independent properties of AI output. Acting on AI debug output without verification means betting on the AI being right; verification means making sure before betting. The cost of verification is small (rerun the reproduction; check the actual log; inspect the proposed fix's predicted behavior); the cost of acting on a wrong hypothesis is large (fix the wrong thing, ship the bug again, lose the audit trail with a misleading "fixed" claim).

**Extended discussion:** The verification pattern:

1. AI proposes a hypothesis: "The bug is in line 47, where the variable shadowing causes the wrong value to be used."
2. Verify against observation: open line 47. Read the code. Does AI's description match the code? (Sometimes AI hallucinates code that doesn't exist or describes code structure inaccurately.)
3. Verify against reproduction: predict what should happen IF AI's hypothesis is correct. Run the reproduction. Does the actual behavior match the prediction?
4. If both verifications pass: AI's hypothesis is supported. Proceed with the fix.
5. If either fails: AI's hypothesis is wrong (or partially wrong). Treat the hypothesis as ruled out (per audit trail Rule 5.5) and consider alternatives.

This is the scientific method applied to AI output. AI is a hypothesis-generator; verification is what turns hypotheses into conclusions.

The AI failure modes that make this rule especially important:

- **Plausible-sounding wrong explanations.** AI explains what code does using plausible-sounding descriptions that don't match the actual code. The explanation reads convincing; the diagnosis is wrong.
- **Confirmation bias.** Once AI has a hypothesis, it tends to surface evidence supporting it and gloss counter-evidence. The hypothesis feels stronger than it should.
- **Symptom-level proposals.** AI proposes the immediate fix to the symptom rather than the root cause (see Rule 5.4).
- **Fabricated stack-trace frame interpretations.** AI describes what each stack frame is doing using inference rather than knowledge — sometimes wrong.

For TGF-specific application: every AI-proposed root cause gets the verification pass. Particularly important in debugging because debugging confidence directly affects production stability — a wrong "fix" applied to a real bug ships the bug again.

**Related anti-patterns:** AP-7 (AI explanation accepted as truth) (see `anti-patterns.md`)

---
