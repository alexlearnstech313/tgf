---
# ─── Anthropic-native runtime fields (Claude Code honors these) ───
name: debugging
description: |
  Systematic debugging discipline grounded in David Agans' 9 rules ("Debugging",
  2002/2006), Sakichi Toyoda's Five Whys, and the scientific method. Use when
  reproducing a bug, isolating variables, forming hypotheses, identifying root
  causes, or verifying fixes. Especially important when AI is involved — AI
  tends to fabricate plausible-sounding root causes, patch symptoms instead of
  causes, and confirm hypotheses instead of testing them. Maps to the debugging
  variant of TGF's six-stage workflow (docs/WORKFLOW.md §7).
paths:
  - "**/*"

# ─── TGF-extension metadata (Phase 11 meta-skills read these; Claude Code ignores) ───
applies-when:
  paths-include:
    - "**/*"
  operations-include:
    - bug investigation (reproduction, isolation, hypothesis testing)
    - error log or stack trace analysis
    - production incident debugging
    - "why is X happening" inquiry
    - root cause analysis after a symptom is identified
    - fix verification (post-hoc testing that the fix actually resolved the bug)
  data-flows-include:
    - error or symptom data crossing from observation into investigation
disqualifying-when:
  - planning new features (use PROJECT-MANAGEMENT or DISCOVERY)
  - writing new tests (use TESTING)
  - design discussions with no specific bug under investigation (use DESIGN)
sources:
  - David J. Agans — "Debugging: The 9 Indispensable Rules for Finding Even the Most Elusive Software and Hardware Problems" (1st ed 2002; 2nd ed 2006) — stable methodology since publication
  - Sakichi Toyoda — Five Whys methodology (Toyota Production System, ~1950s) — stable methodology
  - Scientific method (hypothesis → predict → test → conclude) — stable methodology
  - MITRE ATLAS v5.4.0 — AI debugging and root-cause-analysis failure modes (verified Phase 2, 2026-05-17)
  - docs/WORKFLOW.md §7 (Debugging Variant) — TGF-internal cross-reference for stage mapping
last-generated: 2026-05-20
refresh-recommended: 2027-05-20
self-evolution:
  anti-patterns-observed: []
  triggers-refined: []
  ai-failures-documented: []
---

# DEBUGGING

> **Skill body ≤300 lines** (per `DEC-2026-05-19-007`). Principles, rule summaries, and navigation live here. Full content in reference files loaded on demand:
> - `rules.md` — full rules with citations
> - `anti-patterns.md` — full anti-pattern + canonical pattern pairs with concrete examples

<!-- SECTION: overview -->
## §1 Overview

DEBUGGING governs the discipline of finding root causes — not patching symptoms. It is an **activity skill** in TGF (loads on context per `CLAUDE.md` §9), not always-on. It activates when work shifts to investigation: a reported bug, an unexplained error, a production incident, a "why is X happening" question. The debugging variant of TGF's six-stage workflow (per `docs/WORKFLOW.md` §7) runs through this skill.

The skill encodes three interlocking disciplines: David Agans' 9 rules from his 2002 book "Debugging" (stable, exemplary debugging methodology), Sakichi Toyoda's Five Whys (root-cause-not-symptom discipline from the Toyota Production System), and the scientific method (hypothesis → predict → test → conclude). The three reinforce each other — Agans gives the operational rules, Five Whys gives the depth question, scientific method gives the verification discipline.

The most important AI-specific failure modes DEBUGGING addresses: (1) AI fabricates plausible-sounding root causes that derail debugging sessions; (2) AI patches symptoms instead of causes (the slow query gets cached instead of the schema being fixed); (3) AI confirms hypotheses rather than testing them — building the case for what it already believes rather than letting evidence decide. The discipline of treating AI debug output as a *hypothesis* rather than a *conclusion* is Rule 5.7.

Per Phase 5 Checkpoint 1 Decision D, DEBUGGING activates at the orchestrator level — no dedicated `debugger` subagent in Phase 5. Phase 11 (orchestration meta-skill) decides whether to define a dedicated subagent.
<!-- /SECTION: overview -->

<!-- SECTION: sources -->
## §2 Authoritative Sources

| Source ID | Reference | Version | Date Verified |
|-----------|-----------|---------|---------------|
| AGANS-9 | David J. Agans — "Debugging: The 9 Indispensable Rules for Finding Even the Most Elusive Software and Hardware Problems" | 1st ed 2002; 2nd ed 2006 (stable methodology) | reference (book; stable since publication) |
| TOYODA-5W | Sakichi Toyoda — Five Whys methodology (Toyota Production System) | ~1950s (stable methodology) | reference (stable) |
| SCIENTIFIC-METHOD | Scientific method (hypothesis → predict → test → conclude) | stable methodology (centuries old) | reference (stable) |
| MITRE-ATLAS | [MITRE ATLAS](https://atlas.mitre.org) — AI output and debugging failure modes | v5.4.0 | 2026-05-17 (Phase 2) |
| TGF-WORKFLOW | `docs/WORKFLOW.md` §7 Debugging Variant — TGF-internal cross-reference | shipped Phase 3 (2026-05-19) | TGF-internal |

Citation granularity per Phase 4 Checkpoint 1 Decision A: AGANS-9 cited at the rule level (rule 1 through rule 9, since the book numbers them); TOYODA-5W cited at methodology level (no sub-rule structure exists); scientific method cited at methodology level (stable framework). MITRE ATLAS cited at framework level for AI failure-mode observations.
<!-- /SECTION: sources -->

<!-- SECTION: discovery -->
## §3 Discovery Commands

Diagnostic prompts and commands to assess debugging context before applying rules.

```bash
# Look for existing audit trail (Rule 5.5)
ls -1t .sessions/*.md 2>/dev/null | head -5  # Recent session logs may reference prior debugging
grep -rln "debugging\|root cause\|bug\|incident" .sessions/ 2>/dev/null | head -5

# Find existing error logs (informs Rule 5.2 — quit thinking and look)
test -f docs/ERROR-LOG.md && grep -B 1 -A 5 "open\|in.progress" docs/ERROR-LOG.md | head -30
test -d logs/ && ls -1t logs/*.log 2>/dev/null | head -3

# Check whether the bug has been reported before (Rule 5.5 — keep audit trail)
git log --all --grep="similar.*bug\|same.*issue" --oneline 2>/dev/null | head -5

# Find the most-recent commit before the bug appeared (Agans rule #5 — change one thing at a time)
git log --oneline -20

# Look for AI-specific debugging risks (Rule 5.7) — has AI been asked about this bug already?
grep -rln "AI suggested\|AI says\|Claude says\|GPT" .sessions/ 2>/dev/null | head
```

```
# Diagnostic prompts (run mentally before starting investigation)
1. Can you reliably reproduce this bug? → If NO, engage Rule 5.1 before anything else.
2. Have you READ the actual error message + stack trace + log line? → If NO, engage Rule 5.2.
3. Is the reported issue a symptom of a deeper cause? → Engage Rule 5.4 (Five Whys).
4. Have you tried multiple things at once? → If YES, you've lost the audit trail (Rule 5.3 + 5.5).
5. Has AI proposed a root cause? → That's a hypothesis to test, not a conclusion (Rule 5.7).
6. After applying a fix, have you VERIFIED the bug no longer reproduces? → Rule 5.6's last test.
```
<!-- /SECTION: discovery -->

<!-- SECTION: principles -->
## §4 Universal Principles

Six principles distilled from Agans' 9 rules + Five Whys + scientific method.

- **Reproduce before hypothesizing.** Agans rule #2 ("make it fail"). Without a reliable reproduction, you can't know if a fix worked. "Fixes" applied to non-reproducible bugs can't be verified — you're patching what you think the bug is, not the actual bug. Get the reproduction first, even if it takes time; everything downstream depends on it.

- **Quit thinking and look.** Agans rule #3. Read the actual error message, the actual stack trace, the actual log line, the actual database value, the actual network response. Don't reason about what should be happening; observe what IS happening. AI is especially prone to reasoning over reading — "the code should produce X" when in reality it's producing Y. The observation is the data; the reasoning is hypothesis.

- **Change one thing at a time.** Agans rule #5. When trying fixes, change one variable per attempt. Multiple simultaneous changes destroy the audit trail — when the bug stops happening, you don't know which change mattered. The scientific method's "control variables" applied to debugging.

- **Five Whys for root cause.** Sakichi Toyoda's methodology. The reported symptom is often the visible end of a chain of causes. Patching the symptom leaves the underlying cause to resurface elsewhere. Five Whys traces back through the chain until the root is reached — typically 3-7 "whys" deep, not literal-five.

- **Keep an audit trail.** Agans rule #6. Log what was tried, what worked, what didn't. The audit trail serves three purposes: (1) you don't repeat tried-and-failed attempts; (2) you can backtrack when a fix doesn't hold; (3) future-you (or another debugger) can pick up the trail without starting from scratch.

- **Verify the fix.** Agans rule #9 ("if you didn't fix it, it ain't fixed"). A fix that wasn't verified against the reproduction is not a fix — it's a hypothesis. The verification step closes the loop. Skipping it ships bugs that look fixed in code review but reappear in production.
<!-- /SECTION: principles -->

<!-- SECTION: rules -->
## §5 Rule Summaries

Seven rules. Each summary: title + 1-line statement + source identifier.

<!-- RULE: 5.1 -->
- **Rule 5.1: Reproduce Reliably Before Hypothesizing** — Reliable reproduction is the foundation. Without it, fixes can't be verified, hypotheses can't be tested, and "fixed" is unmeasurable. Get the repro first — even if it takes time — then proceed. `AGANS-9 rule #2 (Make it fail)` → [`rules.md#rule-51-reproduce-reliably-before-hypothesizing`](rules.md)
<!-- /RULE: 5.1 -->
<!-- RULE: 5.2 -->
- **Rule 5.2: Quit Thinking and Look** — Read the actual error message, the actual stack trace, the actual log line, the actual database value. Don't reason about what should be happening; observe what IS happening. AI is especially prone to reasoning over reading. `AGANS-9 rule #3 (Quit thinking and look)` → [`rules.md#rule-52-quit-thinking-and-look`](rules.md)
<!-- /RULE: 5.2 -->
<!-- RULE: 5.3 -->
- **Rule 5.3: Change One Thing at a Time** — When testing fixes, change one variable per attempt. Multiple simultaneous changes destroy the audit trail — bug stops happening but you don't know which change mattered. Scientific method's control-variable discipline applied to debugging. `AGANS-9 rule #5 (Change one thing at a time) + SCIENTIFIC-METHOD` → [`rules.md#rule-53-change-one-thing-at-a-time`](rules.md)
<!-- /RULE: 5.3 -->
<!-- RULE: 5.4 -->
- **Rule 5.4: Five Whys for Root Cause, Not Symptom Patch** — Reported symptom is typically the end of a chain. Patching the symptom leaves the cause to resurface elsewhere. Five Whys traces the chain back to the underlying cause — typically 3-7 levels deep. `TOYODA-5W (Five Whys methodology)` → [`rules.md#rule-54-five-whys-for-root-cause-not-symptom-patch`](rules.md)
<!-- /RULE: 5.4 -->
<!-- RULE: 5.5 -->
- **Rule 5.5: Keep an Audit Trail** — Log what was tried, what worked, what didn't. Audit trail prevents repeating failed attempts, enables backtracking, and serves future debuggers. Per CONTINUITY Rule 5.1 — session logs capture this. `AGANS-9 rule #6 (Keep an audit trail) + cross-reference CONTINUITY Rule 5.1` → [`rules.md#rule-55-keep-an-audit-trail`](rules.md)
<!-- /RULE: 5.5 -->
<!-- RULE: 5.6 -->
- **Rule 5.6: Get a Fresh View When Stuck** — After extended time with no progress, get fresh eyes (ask someone; rubber-duck; step away and return). Long stares at the same problem stop yielding new information. The fresh view often catches what the stuck view can't. `AGANS-9 rule #8 (Get a fresh view)` → [`rules.md#rule-56-get-a-fresh-view-when-stuck`](rules.md)
<!-- /RULE: 5.6 -->
<!-- RULE: 5.7 -->
- **Rule 5.7: AI Debug Outputs Are Hypotheses, Not Conclusions** — AI proposes root causes confidently. The output is a hypothesis to TEST, not a conclusion to ACT on. Especially dangerous: plausible-sounding AI explanations can derail entire debugging sessions toward the wrong cause. Verify against actual observation (Rule 5.2). `TGF-SYNTHESIS — grounded in MITRE-ATLAS observations on AI output failures + SCIENTIFIC-METHOD discipline` → [`rules.md#rule-57-ai-debug-outputs-are-hypotheses-not-conclusions`](rules.md)
<!-- /RULE: 5.7 -->

See `rules.md` for full rule text, citations, plain-language impact, and extended discussion.
<!-- /SECTION: rules -->

<!-- SECTION: anti-patterns -->
## §6 Anti-Pattern Summaries

Eight anti-pattern pairs covering the most common debugging failures.

<!-- ANTI-PATTERN: AP-1 -->
- **AP-1: Fixing without reproducing** — "I think this might be the issue" → fix applied → ship → bug still happens in production. Violates Rule 5.1. → [`anti-patterns.md#ap-1-fixing-without-reproducing`](anti-patterns.md)
<!-- /ANTI-PATTERN: AP-1 -->
<!-- ANTI-PATTERN: AP-2 -->
- **AP-2: Reasoning over reading** — Engineer explains what should happen instead of reading what does happen (the actual error message, the actual log line). Hypothesizes against imagination, not data. Violates Rule 5.2. → [`anti-patterns.md#ap-2-reasoning-over-reading`](anti-patterns.md)
<!-- /ANTI-PATTERN: AP-2 -->
<!-- ANTI-PATTERN: AP-3 -->
- **AP-3: Multiple simultaneous changes** — Three things changed at once; bug stops happening; no idea which change mattered. The "fix" can't be reproduced for a future occurrence. Violates Rule 5.3. → [`anti-patterns.md#ap-3-multiple-simultaneous-changes`](anti-patterns.md)
<!-- /ANTI-PATTERN: AP-3 -->
<!-- ANTI-PATTERN: AP-4 -->
- **AP-4: Symptom patching** — Slow query → add a cache. User complains the cache is stale. Root cause was schema design; cache treated the symptom. Pattern repeats: each new symptom gets its own patch; underlying cause never addressed. Violates Rule 5.4. → [`anti-patterns.md#ap-4-symptom-patching`](anti-patterns.md)
<!-- /ANTI-PATTERN: AP-4 -->
<!-- ANTI-PATTERN: AP-5 -->
- **AP-5: No audit trail** — Bug fixed; six months later same bug reappears; nobody remembers how it was fixed last time. The debugging knowledge wasn't captured. Violates Rule 5.5. → [`anti-patterns.md#ap-5-no-audit-trail`](anti-patterns.md)
<!-- /ANTI-PATTERN: AP-5 -->
<!-- ANTI-PATTERN: AP-6 -->
- **AP-6: Staring at the same screen** — Three hours debugging the same line of code; not asking for help; not stepping away. Diminishing returns set in around the 30-minute mark; the fresh view that would unblock you waits because the stuck view won't release. Violates Rule 5.6. → [`anti-patterns.md#ap-6-staring-at-the-same-screen`](anti-patterns.md)
<!-- /ANTI-PATTERN: AP-6 -->
<!-- ANTI-PATTERN: AP-7 -->
- **AP-7: AI explanation accepted as truth** — AI says "the issue is X." Developer fixes X. The bug remains. The actual issue was Y, but AI's plausible-sounding wrong explanation derailed the investigation. Violates Rule 5.7. → [`anti-patterns.md#ap-7-ai-explanation-accepted-as-truth`](anti-patterns.md)
<!-- /ANTI-PATTERN: AP-7 -->
<!-- ANTI-PATTERN: AP-8 -->
- **AP-8: "Fixed" without verification** — Fix applied; assumed working; merge to main. Deployment surfaces that the bug still happens. The verification step (Agans rule #9) was skipped. Violates Rule 5.1 (no repro to verify against) and the verification discipline of `docs/WORKFLOW.md` §7. → [`anti-patterns.md#ap-8-fixed-without-verification`](anti-patterns.md)
<!-- /ANTI-PATTERN: AP-8 -->

Per `DEC-2026-05-17-003` Clause 1: every anti-pattern is paired with a canonical pattern in `anti-patterns.md`.
<!-- /SECTION: anti-patterns -->

<!-- SECTION: ai-concerns -->
## §7 AI-Specific Concerns

Debugging failure modes specific to AI-assisted development.

- **Fabricated root causes.** AI proposes confident-sounding root-cause explanations that don't match observation. The explanation is plausible enough to derail a debugging session — the developer fixes the proposed cause and finds the bug remains. Defense: Rule 5.7 — AI debug output is hypothesis, not conclusion. Verify against actual reproduction (Rule 5.1) and actual observation (Rule 5.2) before acting.

- **Symptom patching by default.** AI tends to propose the local fix to the immediate symptom rather than the root cause. "Slow query → add cache" rather than "slow query → schema needs index" or "slow query → query shape is wrong." Defense: Rule 5.4 — Five Whys before any fix to a symptom; ask "why is this slow" not "how do I make this slow thing faster."

- **Confirmation over testing.** Once AI has a hypothesis, it tends to build the case for the hypothesis rather than testing it. Evidence supporting the hypothesis gets surfaced; counter-evidence gets glossed. Defense: Rule 5.2 + scientific method — predict what the hypothesis SHOULD show, then look at what's actually there. Disconfirming evidence wins.

- **AI not running the code.** AI reasons about what code does without running it. For non-trivial bugs, reasoning without execution misses behavior — the bug exists because reasoning differs from execution. Defense: `docs/ARCHITECTURE.md` §16 (Empirical Verification for AI-Generated Code) — run the code; observe the behavior; reason against observed reality.

- **Plausible-but-wrong stack-trace explanations.** AI reads a stack trace and explains what each frame is doing — sometimes accurately, sometimes by hallucinating function purposes. The explanation reads coherent; the diagnosis is wrong. Defense: Rule 5.2 — read the actual code at each frame; don't trust the AI's gloss.

Relevant external taxonomies: MITRE ATLAS framework on AI output failures; OWASP LLM Top 10:2025 `LLM09:2025` (Misinformation — fabricated debugging explanations).
<!-- /SECTION: ai-concerns -->

<!-- SECTION: workflow -->
## §8 Workflow Integration

DEBUGGING maps to the debugging variant of TGF's six-stage workflow (per `docs/WORKFLOW.md` §7). The mapping:

- **Stage 1 (Research) — debugging variant: Reproduce reliably.** Rule 5.1 is the primary discipline here. Without reproduction, subsequent stages are speculation. May involve gathering log data, replicating production conditions in test, or finding the minimum input that triggers the bug.
- **Stage 2 (Scope) — debugging variant: Isolate variables.** Agans rule #4 (Divide and conquer) plus scientific method's control-variable discipline. Narrow down what's involved in the bug — which code path, which input, which environment factor.
- **Stage 3 (Plan with Governance) — debugging variant: Form hypotheses.** Scientific method's hypothesis step. AI may propose hypotheses per Rule 5.7; treat each as a hypothesis to test, not a conclusion. Multiple competing hypotheses are healthy.
- **Stage 4 (Implement) — debugging variant: Test systematically.** Apply Rule 5.3 — one variable at a time. Each hypothesis gets a predicted outcome; the test result confirms or disconfirms. Rule 5.5 — log what was tried and what happened.
- **Stage 5 (Four-Pass Review) — debugging variant: Identify root cause.** Five Whys (Rule 5.4) traces beyond the immediate symptom. The fix targets the root cause, not the symptom. Holistic Reviewer (per CONTINUITY) checks that the cause was identified, not just the symptom patched.
- **Stage 6 (Commit) — debugging variant: Verify the fix.** Agans rule #9 — "if you didn't fix it, it ain't fixed." Run the reproduction against the fix; if reproduction no longer reproduces, the fix held. Capture the audit trail (per Rule 5.5) in the session log per CONTINUITY Rule 5.1.

Termination conditions per `docs/WORKFLOW.md` §7: bug fixed (reproduction no longer reproduces); worked-around (root cause identified but acceptable workaround applied; logged to WAIVER-LOG per CONTINUITY Rule 5.3); cannot reproduce (logged to ERROR-LOG with reproduction-attempt details so future incidents can pick up); not-a-bug (the observed behavior is correct; reporter's expectation was wrong; communicate back).
<!-- /SECTION: workflow -->

<!-- SECTION: subagent-context -->
## §9 Subagent Context

**Preloaded by:** `holistic-reviewer` (Phase 4) — the full skill content injects into the holistic-reviewer subagent context at startup via its `skills:` frontmatter (verified in `agents/holistic-reviewer.md`). Per Phase 5 Checkpoint 1 Decision D, DEBUGGING also activates at the orchestrator level during the debugging variant of the workflow; Phase 11 (orchestration meta-skill) decides whether a dedicated `debugger` subagent earns its place. *(Corrected WS5: the prior "None directly" predated the Workstream-3 agent wiring, 2026-05-26.)*

**Critical rules for orchestrator use (when not preloaded):**

- Rule 5.1 (Reproduce Reliably Before Hypothesizing)
- Rule 5.2 (Quit Thinking and Look)
- Rule 5.7 (AI Debug Outputs Are Hypotheses, Not Conclusions)

**Top AI-specific concerns:**

- Fabricated root causes (plausible-sounding wrong explanations derail sessions)
- Symptom patching by default (local fix instead of root cause)
- Confirmation over testing (building case for hypothesis instead of testing it)

Reference files (`rules.md`, `anti-patterns.md`) load on demand within the orchestrator if a specific debugging scenario warrants deep rule application.
<!-- /SECTION: subagent-context -->
