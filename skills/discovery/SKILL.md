---
# ─── Anthropic-native runtime fields (Claude Code honors these) ───
name: discovery
description: |
  Branching-tree interview methodology for vague or ambiguous user inputs. Use
  when a prompt has multiple valid interpretations, when scope is undefined,
  when requirements emerge through conversation rather than being stated
  upfront, or when assumptions need explicit surfacing before substantive work
  begins. Operationalizes "ask before assuming" as a discipline grounded in
  Sakichi Toyoda's Five Whys and standard requirements-elicitation practice.
  Pairs with PROJECT-MANAGEMENT for scope crystallization.
paths:
  - "**/*"

# ─── TGF-extension metadata (Phase 11 meta-skills read these; Claude Code ignores) ───
applies-when:
  paths-include:
    - "**/*"
  operations-include:
    - vague or ambiguous prompt with multiple valid interpretations
    - scope-undefined feature request
    - greenfield planning where requirements emerge through conversation
    - user-supplied surface problem that may have a deeper root cause
    - assumption-laden prompt where assumptions are not yet stated
  data-flows-include:
    - user intent crossing into application scope
disqualifying-when:
  - prompt is unambiguous and scope is operational
  - tactical edit with no scope-level ambiguity
  - debugging an already-reproducible bug (use DEBUGGING instead)
  - the user has explicitly stated "do not ask questions, just proceed"
sources:
  - Sakichi Toyoda — Five Whys methodology (Toyota Production System, ~1950s)
  - IIBA BABOK Guide v3 (paywalled; cited by reference per DEC-2026-05-17-004 Clause 5)
  - NIST SP 800-218 v1.1 (SSDF) — PO.1 Define Security Requirements (verified Phase 2, 2026-05-17)
last-generated: 2026-05-20
refresh-recommended: 2027-05-20
self-evolution:
  anti-patterns-observed: []
  triggers-refined: []
  ai-failures-documented: []
---

# DISCOVERY

> **Skill body ≤300 lines** (per `DEC-2026-05-19-007`). Principles, rule summaries, and navigation live here. Full content in reference files loaded on demand:
> - `rules.md` — full rules with citations
> - `anti-patterns.md` — full anti-pattern + canonical pattern pairs with example dialogues

<!-- SECTION: overview -->
## §1 Overview

DISCOVERY governs the discipline of narrowing ambiguous input through structured questioning before producing substantive work. It is an **activity skill** in TGF (loads on context per `CLAUDE.md` §9), not always-on. It activates at Stage 1 (Research) of the six-stage workflow when input ambiguity is detected.

The skill encodes the trait of *asking before assuming* — when a prompt has multiple valid interpretations or scope is undefined, the right next move is a small number of well-structured questions, not a confident guess at the user's intent. The discipline is bounded: stop when scope is operational, not when every edge case is resolved. Over-questioning is its own failure mode.

Most DISCOVERY rules are TGF synthesis of senior consultative practice grounded in Sakichi Toyoda's Five Whys methodology + standard requirements-elicitation discipline. Per `DEC-2026-05-17-004`, TGF synthesis is acknowledged honestly rather than fabricating sub-rule citations.
<!-- /SECTION: overview -->

<!-- SECTION: sources -->
## §2 Authoritative Sources

| Source ID | Reference | Version | Date Verified |
|-----------|-----------|---------|---------------|
| TOYODA-5W | Sakichi Toyoda — Five Whys methodology (Toyota Production System) | ~1950s (stable methodology) | reference (stable) |
| IIBA-BABOK | IIBA BABOK Guide — Business Analysis Body of Knowledge (paywalled; cited by reference) | v3 | reference only |
| NIST-SSDF | [NIST SP 800-218 Secure Software Development Framework](https://csrc.nist.gov/pubs/sp/800/218/final) — PO.1 Define Security Requirements | v1.1 | 2026-05-17 (Phase 2) |

Citation granularity per Phase 4 Checkpoint 1 Decision A: Five Whys cited at methodology level (no sub-rule structure exists); BABOK cited by reference (paywalled); NIST SSDF PO.1 cited at practice level. Most DISCOVERY rules are TGF synthesis acknowledged honestly per `DEC-2026-05-17-004`.
<!-- /SECTION: sources -->

<!-- SECTION: discovery -->
## §3 Discovery Commands

DISCOVERY is itself the discovery process — there are no codebase-grep commands to run before applying it. The "discovery commands" here are diagnostic prompts the orchestrator runs against the user's input to detect ambiguity.

```
# Diagnostic prompts (run mentally on user input)
1. Does this prompt have multiple valid interpretations? → YES = engage DISCOVERY
2. Is the scope defined enough to write Stage 2 (Scope) of the workflow? → NO = engage DISCOVERY
3. Are there assumptions being made that the user hasn't confirmed? → YES = engage DISCOVERY
4. Is this a surface symptom that may have a deeper root cause? → YES = engage DISCOVERY (Five Whys)
5. Has the user explicitly said "don't ask questions, just proceed"? → YES = skip DISCOVERY, surface assumptions inline
```

When DISCOVERY engages, the questioning loop runs at Stage 1 of the workflow (before Stage 2 Scope can be defined). When scope is operational, DISCOVERY exits and Stage 2 proceeds.
<!-- /SECTION: discovery -->

<!-- SECTION: principles -->
## §4 Universal Principles

Five principles that ground every numbered rule.

- **Narrow before answering.** When input is ambiguous, the right first move is questioning, not answering. A confident answer to a misunderstood question wastes the user's time more than a brief question would have. The cost of one clarifying question is small; the cost of a misinterpreted implementation is large.

- **Structure questioning as a branching tree.** Each answer narrows the space of possibilities. Serial open-ended questions ("what do you want to build?" → "what does it do?") re-traverse the same space and exhaust the user. A good question gates the next question; a great question gates the entire subsequent conversation.

- **Surface assumptions explicitly.** When an assumption is in play (about user goal, available infrastructure, target users, framework choice, scope boundaries), state the assumption to the user before acting on it. The user can confirm or correct cheaply; the user cannot debug an unstated assumption after the implementation is wrong.

- **Use Five Whys for surface problems.** When the user describes a symptom — "the dashboard is slow," "users keep complaining about the form" — ask why until the root need surfaces. The reported problem is often not the actual problem.

- **Stop at scope-operational, not at scope-perfect.** Discovery ends when scope is sufficient to define Stage 2 of the workflow. Continuing to ask clarifying questions after operational threshold wastes the user's time and signals indecision. Knowing when to stop is half the skill.
<!-- /SECTION: principles -->

<!-- SECTION: rules -->
## §5 Rule Summaries

Five rules. Each summary: title + 1-line statement + source identifier.

<!-- RULE: 5.1 -->
- **Rule 5.1: Narrow Before Answering** — When input is ambiguous (multiple valid interpretations or undefined scope), engage DISCOVERY through questioning before producing substantive work. A confident answer to a misunderstood prompt is worse than a brief clarifying question. `TGF-SYNTHESIS — grounded in IIBA-BABOK requirements elicitation + senior consultative practice` → [`rules.md#rule-51-narrow-before-answering`](rules.md)
<!-- /RULE: 5.1 -->
<!-- RULE: 5.2 -->
- **Rule 5.2: Branching Tree, Not Linear Questioning** — Structure questioning so each answer narrows the possibility space and gates the next question. Avoid serial open-ended prompts that re-traverse uncovered ground. Use closed-form questions where possible (multiple choice, yes/no) to make answers cheap. `TGF-SYNTHESIS — grounded in IIBA-BABOK + senior consultative practice` → [`rules.md#rule-52-branching-tree-not-linear-questioning`](rules.md)
<!-- /RULE: 5.2 -->
<!-- RULE: 5.3 -->
- **Rule 5.3: Five Whys for Root Cause** — When the user describes a surface symptom or stated problem, apply Five Whys to surface the underlying need before scoping the work. The reported problem is often not the actual problem; the actual problem is reachable in ~5 levels of "why" questioning. `TOYODA-5W (~1950s, stable methodology)` → [`rules.md#rule-53-five-whys-for-root-cause`](rules.md)
<!-- /RULE: 5.3 -->
<!-- RULE: 5.4 -->
- **Rule 5.4: Surface Assumptions Explicitly** — When an assumption is being made (about user goal, available infrastructure, target users, framework, scope), state the assumption before proceeding. The user confirms or corrects cheaply; the user cannot fix an unstated assumption after the implementation is wrong. `TGF-SYNTHESIS — grounded in senior consultative practice` → [`rules.md#rule-54-surface-assumptions-explicitly`](rules.md)
<!-- /RULE: 5.4 -->
<!-- RULE: 5.5 -->
- **Rule 5.5: Stop at Scope-Operational** — Discovery ends when scope is sufficient to define Stage 2 of the workflow — not when every edge case is resolved. Continuing to question after operational threshold wastes the user's time, signals indecision, and is its own failure mode. `TGF-SYNTHESIS — grounded in NIST-SSDF v1.1 PO.1 + senior practice` → [`rules.md#rule-55-stop-at-scope-operational`](rules.md)
<!-- /RULE: 5.5 -->

See `rules.md` for full rule text, citations, plain-language impact, and extended discussion.
<!-- /SECTION: rules -->

<!-- SECTION: anti-patterns -->
## §6 Anti-Pattern Summaries

Eight anti-pattern pairs covering the most common DISCOVERY failures.

<!-- ANTI-PATTERN: AP-1 -->
- **AP-1: Assuming meaning instead of asking** — User says "help me with auth"; AI dives into JWT implementation without asking about scope, framework, or threat model. Violates Rule 5.1. → [`anti-patterns.md#ap-1-assuming-meaning-instead-of-asking`](anti-patterns.md)
<!-- /ANTI-PATTERN: AP-1 -->
<!-- ANTI-PATTERN: AP-2 -->
- **AP-2: Serial open-ended questioning** — "What do you want to build?" → "What does it do?" → "Who uses it?" — re-traversing the same possibility space rather than narrowing. Violates Rule 5.2. → [`anti-patterns.md#ap-2-serial-open-ended-questioning`](anti-patterns.md)
<!-- /ANTI-PATTERN: AP-2 -->
<!-- ANTI-PATTERN: AP-3 -->
- **AP-3: Skipping Five Whys on a surface symptom** — User reports "the dashboard is slow"; AI optimizes the dashboard query without asking what the user is actually trying to do (e.g., understand a single customer's status — could be a different report entirely). Violates Rule 5.3. → [`anti-patterns.md#ap-3-skipping-five-whys`](anti-patterns.md)
<!-- /ANTI-PATTERN: AP-3 -->
<!-- ANTI-PATTERN: AP-4 -->
- **AP-4: Over-questioning past scope-operational** — Scope is sufficient to begin Stage 2; AI continues asking edge-case questions, signaling indecision and wasting user time. Violates Rule 5.5. → [`anti-patterns.md#ap-4-over-questioning`](anti-patterns.md)
<!-- /ANTI-PATTERN: AP-4 -->
<!-- ANTI-PATTERN: AP-5 -->
- **AP-5: Buried assumption** — AI makes an assumption ("assuming TypeScript", "assuming Postgres") without stating it; user later discovers the assumption was wrong and rework cost is paid. Violates Rule 5.4. → [`anti-patterns.md#ap-5-buried-assumption`](anti-patterns.md)
<!-- /ANTI-PATTERN: AP-5 -->
<!-- ANTI-PATTERN: AP-6 -->
- **AP-6: Vague "tell me more" prompts** — Open-ended questions that put the burden of structure on the user rather than narrowing the possibility space. Violates Rule 5.2. → [`anti-patterns.md#ap-6-vague-tell-me-more`](anti-patterns.md)
<!-- /ANTI-PATTERN: AP-6 -->
<!-- ANTI-PATTERN: AP-7 -->
- **AP-7: Performative questioning** — Questions whose answers don't gate any branching ("just to confirm, you want this to work?"). Wastes a turn without narrowing. Violates Rule 5.2. → [`anti-patterns.md#ap-7-performative-questioning`](anti-patterns.md)
<!-- /ANTI-PATTERN: AP-7 -->
<!-- ANTI-PATTERN: AP-8 -->
- **AP-8: Discovery as a one-time pass** — Initial discovery done; mid-implementation a contradiction surfaces; no mechanism for re-discovery — work continues against now-wrong scope. Violates Rules 5.1 and 5.5. → [`anti-patterns.md#ap-8-discovery-as-one-time-pass`](anti-patterns.md)
<!-- /ANTI-PATTERN: AP-8 -->

Per `DEC-2026-05-17-003` Clause 1: every anti-pattern is paired with a canonical pattern in `anti-patterns.md`.
<!-- /SECTION: anti-patterns -->

<!-- SECTION: ai-concerns -->
## §7 AI-Specific Concerns

Discovery failure modes specific to AI-assisted development.

- **AI defaults to answering over asking.** Training data over-represents "respond to the user's question" patterns and under-represents "decline to answer until the question is clear." AI tends to interpret ambiguous prompts confidently and produce substantive work, even when the work might miss the user's actual intent. Defense: explicit ambiguity-detection diagnostic at Stage 1 (§3) before producing answers.

- **AI assumes meaning instead of stating assumptions.** When AI doesn't know something, it often fills in the gap silently rather than surfacing the assumption. The output reads confident; the assumption is buried. Defense: Rule 5.4 — when an assumption is in play, state it before acting on it.

- **AI over-questions when context is sufficient.** Inverse failure: when context-trained to ask questions, AI may continue asking past the operational threshold, exhausting the user and signaling indecision. Defense: Rule 5.5 — stop when scope is sufficient, not when "perfect."

- **AI confuses scope-perfect with scope-operational.** AI may try to resolve every edge case during discovery rather than reaching "good enough to start." The instinct toward completeness defeats the bounded-discovery discipline.

Relevant external taxonomies: OWASP LLM Top 10:2025 `LLM09:2025` (Misinformation — confident-sounding wrong answers to misunderstood prompts).
<!-- /SECTION: ai-concerns -->

<!-- SECTION: workflow -->
## §8 Workflow Integration

How DISCOVERY participates in the six-stage workflow (per `docs/WORKFLOW.md`).

- **Stage 1 (Research):** Primary activation point. Run the §3 diagnostic prompts against user input. If any of (1)–(4) is YES and the user hasn't said "don't ask," engage DISCOVERY through structured questioning per Rules 5.1–5.4 until scope is operational per Rule 5.5.
- **Stage 2 (Scope):** DISCOVERY exits to Stage 2 once scope is operational. The Scope document captures the resolved questions and stated assumptions.
- **Stage 3 (Plan with Governance):** DISCOVERY may re-engage if Stage 3 surfaces a new ambiguity (e.g., the plan reveals an unstated trade-off requiring user input). Per Rule 5.5, this re-engagement is bounded.
- **Stage 4 (Implement):** If a contradiction surfaces mid-implementation, DISCOVERY re-engages (Rule 5.5 + AP-8) — do not silently work around the contradiction.
- **Stage 5 (Four-Pass Review):** N/A — DISCOVERY is not a review skill.
- **Stage 6 (Commit):** Stated assumptions during DISCOVERY are captured in session log per CONTINUITY Rule 5.6 (capture WHY).
<!-- /SECTION: workflow -->

<!-- SECTION: subagent-context -->
## §9 Subagent Context

**Preloaded by:** None directly. DISCOVERY activates at the orchestrator level during Stage 1 Research when ambiguity is detected. The four Phase 4 review subagents do not preload DISCOVERY because their work assumes scope is already defined.

**Critical rules for orchestrator use (when not preloaded):**

- Rule 5.1 (Narrow Before Answering)
- Rule 5.4 (Surface Assumptions Explicitly)
- Rule 5.5 (Stop at Scope-Operational)

**Top AI-specific concerns:**

- AI defaults to answering over asking
- AI confuses scope-perfect with scope-operational

Reference files (`rules.md`, `anti-patterns.md`) load on demand within the orchestrator if a specific DISCOVERY scenario warrants deep rule application.
<!-- /SECTION: subagent-context -->
