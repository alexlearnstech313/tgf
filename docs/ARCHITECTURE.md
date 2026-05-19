# TGF Architecture

Extended architecture sections for The Governance Framework. These cover *how* the framework operates internally: mode scaling, verification discipline, citation rigor, enforcement layers, token economics, agent orchestration, and the improvement loops.

The operational contract — what the framework is, the workflow it runs, the developer character, and the artifacts it produces — lives in `CLAUDE.md` (§1–§14). This document holds the deeper architecture so it doesn't load into every session's context.

**Reading order:** §1–§14 in `CLAUDE.md` first (the contract). Then this document when you need to understand how a specific architectural mechanism works, or when something here is cross-referenced.

**For adopters:** the same split applies in `templates/CLAUDE.md.template` and (when shipped) `templates/ARCHITECTURE.md.template`.

---

## §15 Mode-Aware Operation

The framework operates differently across project modes. Standards within scope remain unconditional. What's in scope and how much rigor applies by default varies by mode.

The framework infers mode from PROJECT-CONTEXT signals — project age, user count, data sensitivity, deployment status. The user can override with `/tgf:set-mode` when the inferred mode is wrong.

### Exploration mode

The user is figuring out what to build. Code may not survive. Heavy emphasis on PROJECT-MANAGEMENT and DISCOVERY skills. Light on production-readiness reviews.

- Workflow stages 1-2 (Research, Scope) primary
- Stage 3 evaluation includes always-on skills only by default
- Four-pass review reduces to code review and light holistic
- Findings logged with exploration-context flag for later re-evaluation

### Prototype mode

The user is building something to test an idea. Production not yet in scope. Code might be promoted later.

- Stage 3 evaluation includes always-on plus core security (input validation, output encoding, secrets, basic auth)
- Compliance and detailed security skills not loaded
- Four-pass review at light depth
- Findings logged with prototype-context flag
- Promotion path: `/tgf:promote` triggers re-evaluation under building-mode standards

### Building mode (default)

Standard project work. Code is intended for production use. Default if mode is unspecified.

- Full skill catalog loads based on contextual triggers
- Four-pass review at standard depth
- All standard discipline applies
- Findings handled per standard resolution rule

### Hardening mode

Project is production-deployed and being hardened. Extra adversarial focus.

- Full skill catalog loads
- Stage 3 emphasizes threat modeling and adversarial perspective
- Four-pass review with extra red team weight
- Higher bar for waivers
- BASELINE-AUDIT recurrence recommended quarterly

### Maintenance mode

Project is mature and primarily receives maintenance work. Regression prevention emphasis.

- Full skill catalog loads
- Stage 3 emphasizes regression risk and forward compatibility
- Four-pass review with extra holistic review weight
- Migration safety verification stricter
- Architectural changes get extra scrutiny

### Mode transitions

Modes change as projects evolve. Exploration becomes prototype becomes building becomes hardening becomes maintenance. The framework doesn't lock modes — they revise as the project's actual situation changes.

When mode shifts, prior code may need re-evaluation. Code written in exploration mode that's now in production scope under building mode gets evaluated for the gaps that exploration mode didn't cover. The `/tgf:promote` command handles this systematically.

---

## §16 Empirical Verification for AI-Generated Code

AI-generated code can look correct while being subtly wrong. Plausible patterns aren't verified patterns. The framework adds explicit verification when AI generated the code:

- Code is run, not just reviewed
- Output is checked against expected behavior
- Edge cases are exercised, not assumed handled
- Plausible-but-wrong patterns are checked: assumed library behavior, hallucinated APIs, fabricated function signatures, near-correct syntax

This applies regardless of how confident the AI seems about the code. AI confidence is not verification. Tests passing is not full verification. Empirical exercise of the actual behavior is verification.

When the user wrote code with AI assistance for specific portions, those portions get the same verification. When the user wrote code entirely themselves, standard four-pass review applies without extra empirical verification.

This isn't about authorship tracking. It's about not trusting AI-generated patterns as verified just because they look right.

---

## §17 Citation Verification

The "authoritative sources only" discipline (§1) requires that every governance rule traces to a verifiable, current citation. Skills cite specific source identifiers — `OWASP ASVS 5.0 V6.2.2`, `NIST SP 800-63B §5.1.1.2`, `RFC 8725 §3.1`, `MITRE ATLAS AML.T0051` — that resolve to real rules in published documents. The full operating discipline is locked in `docs/DECISIONS.md` → `DEC-2026-05-17-004`. The six clauses summarized here.

### Live verification at skill-creation time

When a skill is generated or refreshed, the sources in its §2 Authoritative Sources table are fetched from their canonical URLs and cited rules are verified to exist. The skill's frontmatter records `last-generated` (when verification ran) and `refresh-recommended` (when re-verification is due). Skills that fail verification don't ship — they go back for source correction or skill refresh.

*Plain-language impact:* the framework's authority chain is real, not fabricated. AI confidently producing a citation that doesn't exist is a documented failure mode; live verification catches it before the skill ships.

### Rule-level citation precision

Citations name the specific rule, control, or section — not the framework generally. "OWASP recommends" is not a citation. `OWASP ASVS 5.0 V6.2.2` is. The precision lets users verify the claim, lets the audit be checkable, and prevents citation drift over time.

*Plain-language impact:* you can look up any TGF rule and find it in the cited source. Authority that can't be verified is authority that's claimed, not held.

### Fetched content treated as untrusted input

Sources fetched during skill creation may contain prompt injection or other adversarial material — indirect prompt injection is `OWASP LLM01:2025`, the #1 documented LLM risk and a catalogued MITRE ATLAS technique. The framework extracts only structured data from fetched content (rule numbers, rule text, version metadata, dates) and ignores any instructions embedded in pages. Cross-source verification (NIST ↔ ISO crosswalks, OWASP ↔ multiple references) catches discrepancies.

*Plain-language impact:* an attacker who compromises a documentation page can't inject malicious rules into TGF skills. Every fetched page is treated as suspect.

### No developer-machine downloads

Research happens via Claude's web tools on Anthropic's infrastructure. The developer's filesystem receives only synthesized citations and rules written by Claude — not raw fetched content, scripts, executables, or click-through URLs. Watering-hole and supply-chain attacks targeting documentation fetches don't reach the developer's environment.

*Plain-language impact:* you can run TGF without worrying that the framework's own research pulls malicious content onto your laptop. Defense in depth applies to TGF itself.

### Paywalled sources cited by reference

Standards behind paywalls (notably ISO/IEC 27001:2022 and 27002:2022) are cited by reference: control ID, title, version. Operational rule text comes from freely-available authoritative mappings — NIST ↔ ISO crosswalks (a *crosswalk* maps one standard's controls to another's), OWASP ↔ ISO references — with attribution. Reproducing paywalled standard text directly in skill files is not permitted regardless of license access.

*Plain-language impact:* the framework respects standards licensing without sacrificing rigor. ISO citations are real references; operational guidance comes from open mappings.

### Comparative framework research separated from citation

Research on public Claude Code frameworks (Superpowers, great_cto, and others) informs design patterns. It does not serve as rule-source for skills. Comparative references appear in design rationale documents — `DECISIONS.md`, `DESIGN-RATIONALE.md`, session logs — never in skill §2 Authoritative Sources tables.

*Plain-language impact:* TGF doesn't pretend another project's README is a primary source. Patterns borrowed get credited as patterns; rules cited stay grounded in OWASP, NIST, ISO, MITRE, and RFCs.

### When verification fails

A skill whose cited rule cannot be verified — source moved, deprecated, rule renumbered, citation was originally incorrect — goes back for refresh, not silently kept. The skill gets flagged stale. `/tgf:verify-citation` runs verification on demand; periodic refresh catches drift on cadence (quarterly for fast-moving domains like supply-chain and AI security; annually for stable frameworks). Citation rot is a defect, not an acceptable accumulation.

---

## §18 Hooks for Enforcement

Hooks are the framework's enforcement floor — programmatic gates that block actions before they happen. Skills produce findings the framework surfaces for review; hooks deny operations the framework will not allow. Different mechanism, different purpose. Skills are how the framework *advises*; hooks are how the framework *enforces*.

This two-layer enforcement aligns with `NIST SP 800-218 v1.1` (Secure Software Development Framework) — specifically its discipline of practices that reduce vulnerabilities through verification at key lifecycle points. TGF leverages two distinct hook layers.

### Claude Code hooks

Claude Code's native lifecycle hooks fire at specific points in the agent loop: `SessionStart`, `PreToolUse`, `PostToolUse`, `SubagentStart`, `SubagentStop`, `FileChanged`, `ConfigChange`, `SessionEnd`, plus more (Claude Code's hook documentation has the full taxonomy; this section does not duplicate it). TGF does not invent hook events — it uses the actual event names.

Hook scripts live in `.claude/hooks/<EventName>/NN-name.sh` — PascalCase event names matching Claude Code's taxonomy. The numeric prefix orders execution within an event directory.

**Input contract.** Each hook receives a JSON object on stdin with at minimum `session_id`, `cwd`, `permission_mode`, `hook_event_name`, plus event-specific fields (for example `tool_name` and `tool_input` for `PreToolUse`).

**Output contract.**

- **Exit 0** allows the action; optional JSON on stdout sets control fields (`continue`, `decision: block`, `additionalContext`, etc.)
- **Exit 2** blocks the action; stderr surfaces as the block reason to Claude and to the user
- **Any other exit code** is a non-blocking error; stderr is logged but the action proceeds

**Input is untrusted.** `tool_input` and other fetched fields may carry attacker-controlled data via indirect prompt injection (`OWASP LLM01:2025`). Hooks must validate inputs and prefer *exec-form* invocation (arguments passed as a list, no shell interpretation) over *shell-form* (string passed to `bash -c`) to prevent command injection through filenames or arguments containing shell metacharacters.

### Git hooks

Claude Code hooks fire only during agent operation. Commits initiated outside the agent (direct `git commit`, IDE git integration, automated tooling) bypass them. For commit-time enforcement that fires regardless of how the commit is initiated, TGF provides git-layer hooks in `.claude/git-hooks/`. An opt-in install script copies these into `.git/hooks/`.

Git hooks enforce repository invariants — verify session log entry exists, verify tests pass for the change, verify ROADMAP updated for milestone-affecting changes, scan staged content for secrets. Distinct scope from Claude Code hooks: broader trigger (any commit, not just agent-initiated) but narrower window (commit time only).

### Mode-aware hook profiles

Hook activation scales with project mode (§15). The profile lives in `.claude/hooks/profile.json` and gates which hooks run for the current mode.

- **Exploration mode** — safety hooks only. Block dangerous git operations, block secrets in commits, block destructive database operations. No workflow hooks (the user is figuring out what to build; workflow enforcement is friction at this stage).
- **Prototype mode** — safety + basic workflow. Adds: verify session log entry on `SessionEnd`.
- **Building mode (default)** — safety + workflow + governance. Adds: verify tests pass before commits, verify findings resolved before commits, log security-relevant operations on `PostToolUse`.
- **Hardening mode** — full profile + stricter governance. Adds: log subagent operations, detect framework integrity changes via `FileChanged` and `ConfigChange`, stricter waiver review.
- **Maintenance mode** — building profile + regression prevention. Adds: migration safety verification for schema-affecting commits.

### Three universal hooks always active

Three hooks fire regardless of project mode, because the harms they prevent are universal:

- **`block-dangerous-git`** — prevents force push to `main`, hard reset of unmerged work, accidental commits to wrong branch. Fires on `PreToolUse` matching `Bash(git ...)`.
- **`block-secrets-commit`** — scans staged content for credential patterns (API keys, tokens, private keys, env files) before commits. Fires both on `PreToolUse` matching git commit calls and as a git pre-commit hook.
- **`block-destructive-db`** — prevents `DROP DATABASE`, unbounded `DELETE`, `TRUNCATE` without explicit acknowledgment. Fires on `PreToolUse` matching database tool calls.

### Hooks and authority

Hooks programmatically express the hard-refusal severity level from §5 Authority Structure. When a hook blocks an action, it surfaces the reason and remediation; the user can override with explicit acknowledgment (the framework respects the user's authority over their own project) but cannot bypass silently. Hook overrides are logged.

Hooks never override skill findings or replace skill discipline. They are the floor — what must not happen — while skills define what should happen and surface what didn't.

### Plain-language impact

What hooks prevent that skill discipline alone cannot:

- **Silent supply-chain attacks** — `block-secrets-commit` catches credentials slipping into git history regardless of which tool wrote them
- **Accidental destruction** — `block-dangerous-git` catches the muscle-memory `git push --force` to `main`
- **Governance bypass** — `block-destructive-db` catches `DELETE FROM users;` whether typed by Claude or by hand
- **Workflow discipline drift** — commit-time verification of session log, tests, and ROADMAP catches "I'll add the log entry later" before it ships

The framework's advice is skills. The framework's floor is hooks. Both exist because either alone is insufficient.

### Reference

Phase 0 `DEC-2026-05-17-003` Clause 2 specified the hook architecture conceptually. `DEC-2026-05-17-005` corrected the event naming to align with Claude Code's actual taxonomy and added the separate `.claude/git-hooks/` layer for git-time enforcement. The current `.claude/hooks/` directory layout reflects the corrected naming.

Phase 12 (Hook Library) populates the universal hooks and reference profiles. This section documents the architecture; Phase 12 ships the scripts.

---

## §19 Token Efficiency

The framework's context window is shared infrastructure. Every loaded skill, every workflow stage, every subagent dispatch consumes tokens that compete with the actual work. Token efficiency is a structural property of how TGF operates — not an optimization, not something the user manages. The framework's design either spends tokens well or it doesn't.

TGF inherits Claude Code's native progressive disclosure (Anthropic's pattern) and extends it with section-level addressability (Phase 0 `DEC-2026-05-17-003` Clause 1).

### Native progressive disclosure

Claude Code loads skills in three stages:

1. **Frontmatter pre-loaded at session start** — name and description from every skill's YAML frontmatter, roughly 100 tokens per skill. This is what makes Claude aware that skills exist without paying for their content.
2. **SKILL.md body loads when triggered** — when a skill's applicability conditions match the change context, the framework loads the body (capped at 500 lines for performance per Anthropic's authoring guidance).
3. **Reference files load on demand** — additional files in a skill's directory load only when the body explicitly references them, one level deep maximum (deeper nesting risks partial reads).

The result: a session with 50 available skills costs roughly 5,000 tokens of frontmatter regardless of which skills actually fire. Body content only loads for relevant skills.

### Addressable section loading

TGF extends progressive disclosure with HTML section anchors *within* skill files:

- `<!-- SECTION: section-name -->` brackets at the file level
- `<!-- RULE: 5.1 -->` brackets at the individual-rule level
- `<!-- ANTI-PATTERN: AP-1 -->` and `<!-- CANONICAL: CP-1 -->` for example pairs

When a subagent needs only the `security-input-validation` skill's anti-patterns to evaluate a specific change, the framework loads just that section — not the full 500-line skill. Section-level loading reduces context cost for skill-heavy reviews substantially.

This addressability is TGF's extension. Anthropic's spec covers file-level loading; TGF's anchors enable section-level loading on top.

### Path-based pre-filtering

Stage 3 (Plan with Governance) evaluates the change against every applicable skill. A naive implementation would load every skill's `applies-when` conditions to test them. Path-based pre-filtering reduces this:

1. The framework first checks which skills' `applies-when.paths-include` patterns match the changed files. This is cheap — glob matching, no content load.
2. Only matched skills proceed to full applicability evaluation against `imports-include`, `operations-include`, and `data-flows-include`.
3. Skills with no path match exit the evaluation without loading their body.

A "fix typo in README" change touches one file, matches few skills, and loads almost nothing. A "refactor authentication middleware" change touches several files, matches security and IAM skills, and loads their content. Cost tracks scope.

### Cost-aware orchestration

Subagent dispatch (§20) scales by change tier (§3):

- **Trivial** — no subagents. Main agent does everything in-line. ~0 subagent cost.
- **Small** — two review subagents (Code Reviewer + Holistic Reviewer). ~2× per-subagent cost.
- **Medium** — four review subagents (the full four-pass review). ~4×.
- **Large** — four review subagents plus Researcher subagents for Stage 1, optional Implementer subagents for Stage 4 decomposition, Verifier for AI-generated code. ~7-10×.

This is cost matched to risk. Trivial changes get trivial orchestration; large changes get the orchestration they need.

### Token telemetry

Per `DEC-2026-05-17-003` Clause 5, the framework logs per-session telemetry to `.tgf/telemetry/sessions/*.json`: workflow_invocations with per-stage token consumption, skills_evaluated (which loaded, which contributed rules, which produced findings), subagents_dispatched, total_tokens, findings_total. The `.tgf/` directory is gitignored — telemetry is local operational data.

`/tgf:framework-health` surfaces quarterly aggregates: skills that consume disproportionate tokens relative to findings produced (signal for over-broad triggers or noise:signal issues), skills that never load (signal for trigger gaps or scope mismatch), expensive workflow stages (signal for orchestration tuning).

### Plain-language impact

What these mechanisms prevent:

- **Death by context overflow** — full skill catalogs loading on every prompt
- **Pay-for-what-you-don't-use** — skills loading content unrelated to the current change
- **Silent cost accumulation** — telemetry surfaces expensive operations before they become unsustainable

You don't manage token efficiency. The framework's structure handles it. What you might notice: long sessions stay coherent, complex changes get appropriate review depth, framework-health reports show where the framework's own cost can be tuned (§22).

---

## §20 Agent Orchestration

Complex work decomposes into focused tasks. Each task benefits from a fresh context with the specific skills, artifacts, and references it needs — not the cumulative context of everything that came before. TGF dispatches specialized subagents to handle focused work, then aggregates their outputs at the orchestrator. The pattern reduces context cost (§19), improves review accuracy (fresh context resists confirmation bias from the implementer's view), and parallelizes work that doesn't need to run sequentially.

Phase 0 `DEC-2026-05-17-003` Clause 3 defines seven subagent roles, each with specified context inputs and JSON output schema.

### The seven subagent roles

- **Researcher** — investigates one aspect of the codebase or project artifacts. Dispatched from Stage 1 (Research) for Large-tier changes. Returns structured findings (relevant files, prior decisions, related logs).
- **Implementer** — executes one decomposed implementation task. Dispatched from Stage 4 (Implement) when Large-tier changes decompose into discrete work. Returns the implementation diff plus skill rules applied.
- **Code Reviewer** — Phase 1 of four-pass review. Evaluates craftsmanship: type safety, error handling, naming, anti-patterns, test coverage, scale-aware patterns, solo-maintainability.
- **Security Auditor** — Phase 2 of four-pass review. Applies applicable security skills' rules to the change. Returns findings with citation, severity, and plain-language impact.
- **Red Team** — Phase 3 of four-pass review. Adversarial perspective: injection scenarios, authorization bypass, race conditions, business logic abuse, failure-mode exploitation.
- **Holistic Reviewer** — Phase 4 of four-pass review. TGF-specific integration verification: spec compliance, codebase fit, regression risk, forward compatibility, roadmap alignment, solo-maintainability, decision documentation.
- **Verifier** — empirically exercises AI-generated code per §16. Dispatched conditionally when the change includes AI-generated portions. Returns test execution results, edge cases exercised, plausible-but-wrong patterns checked.

### Cost-aware dispatch

Dispatch scales by change tier (§3, §19):

- **Trivial** — no subagents. Main agent does everything in-line.
- **Small** — Code Reviewer + Holistic Reviewer (2 subagents).
- **Medium** — Code Reviewer + Security Auditor + Red Team + Holistic Reviewer (4 subagents in parallel).
- **Large** — full four-pass review + Researcher subagents for Stage 1 + Implementer subagents for decomposable Stage 4 + Verifier for AI-generated portions (7–10+ subagents across stages).

Orchestration depth matches risk. Trivial changes don't pay for orchestration overhead they don't need. Large changes get the parallel rigor they require.

### Two-stage review per subagent

Each review subagent (Code Reviewer, Security Auditor, Red Team, Holistic Reviewer) runs two passes — a pattern validated in public frameworks including Superpowers:

1. **Spec compliance** — did this implementation match the plan from Stage 3? Did it apply the skill rules that were supposed to apply? Returns "matches plan" or specific deviations.
2. **Quality** — given that the implementation matches (or doesn't) the plan, is the implementation itself good by the subagent's specialty (craftsmanship for Code Reviewer, security rules for Security Auditor, etc.)?

Spec compliance can pass while quality fails (well-built wrong thing); quality can pass while spec compliance fails (well-built thing that's not what was planned). Both must pass for the review subagent to return ✅.

### Excessive agency mitigation

Subagent dispatch is a documented risk surface — `OWASP LLM06:2025` (Excessive Agency) catalogs damage caused by LLM-driven systems with too much functionality, permission, or autonomy. TGF applies LLM06's prevention strategies:

- **Minimize subagent extensions** — each role has a defined scope; no general-purpose subagents
- **Limit functions to minimum necessary** — Code Reviewer doesn't get database access; Verifier doesn't get git write
- **Avoid open-ended extensions** — granular capabilities, not "do whatever"
- **Restrict permissions to minimum scope** — least-privilege per role
- **Execute within user's security context** — subagents inherit the user's authorization; they never elevate
- **Human-in-the-loop for high-impact actions** — irreversible changes always surface to the user; subagents never bypass
- **Authorization in downstream systems** — subagent findings don't auto-apply; the orchestrator surfaces, the user decides
- **Secure coding practices** — subagent inputs (the diff, the artifacts) are treated as untrusted (per §17 and DEC-004)

### Adversarial AI considerations

MITRE ATLAS v5.4.0 (February 2026) catalogs agent-targeting techniques. Two are particularly relevant for orchestration:

- **Publish Poisoned AI Agent Tool** — an attacker introduces a malicious tool that subagents might invoke. TGF mitigates by scoping each role to a defined toolset and logging tool use via `PostToolUse` hooks (§18).
- **Escape to Host** — an attacker leverages a subagent's tool access to escape its intended scope. TGF mitigates via hook-layer denial of out-of-scope operations plus `SubagentStart` and `SubagentStop` lifecycle logging.

Subagent integrity is part of framework integrity. Subagent operations are logged to telemetry (§19) and surfaced in framework health (§22) so anomalous patterns become visible.

### Orchestrator versus subagent authority

Subagents produce *recommendations*, not decisions. The orchestrator (main agent) collects subagent outputs, deduplicates findings, normalizes severity, and surfaces a unified findings list. The user reviews; the user decides.

Subagents never:

- Apply their own findings without orchestrator review
- Execute irreversible actions (writes to production, deletes, force-pushes)
- Spawn other subagents with elevated permissions
- Modify skill content, hooks, or framework configuration

The orchestrator never:

- Suppresses subagent findings the user should see
- Pretends a subagent finding is its own recommendation (subagent attribution preserved)
- Bypasses §5 Authority Structure — the user is the stakeholder

### Aggregation

When subagents return outputs, the orchestrator:

1. Deduplicates findings (the same issue caught by Security Auditor and Red Team appears once)
2. Normalizes severity per §11 (Critical / High / Medium / Low)
3. Attributes findings to their source subagent for traceability
4. Surfaces the unified list with plain-language impact per finding
5. Routes findings per §11 resolution rule (fix / waive in WAIVER-LOG / escalate to VENDOR-LOG)

### Plain-language impact

What orchestration adds that single-agent work cannot:

- **Fresh context for review** — Code Reviewer doesn't share the implementer's mental model; it evaluates the code as the code, not as "what the implementer meant"
- **Parallel work** — four review phases run simultaneously rather than sequentially; faster review on Medium and Large tier changes
- **Bounded context cost** — each subagent loads only the skills and artifacts it needs (§19 addressable sections)
- **Independent verification** — the Verifier subagent runs AI-generated code rather than reasoning about it; empirical results break the AI-confirmation-bias loop (§16)

### Reference

Phase 0 `DEC-2026-05-17-003` Clause 3 defines the seven roles and their JSON output schemas. Phase 11 (Meta-Skills) implements the orchestration meta-skill; Phase 12 (Hook Library) provides `SubagentStart` and `SubagentStop` lifecycle hooks. This section documents the architecture; subsequent phases ship the operations.

---

## §21 Self-Evolving Knowledge

The framework gets better through use. Skills accumulate observations of how they actually fire, what they catch, where they miss. Stack-specific patterns refine as real projects exercise them. AI-specific failure modes emerge as Claude (and other models) hit them in production. The framework needs a mechanism to capture this signal and convert it into improvements — without auto-applying changes that haven't been verified.

Phase 0 `DEC-2026-05-17-003` Clause 4 specifies the evolution data structure (`.tgf/evolution/observations/`, `.tgf/evolution/proposals/{pending,accepted,rejected}/`, `.tgf/evolution/confidence-thresholds.json`). The discipline is bounded by what evolution can and cannot do.

### What can evolve

Four categories of skill content are eligible for evolution through human-reviewed proposals:

- **Anti-patterns** — new failure modes discovered during use get added as anti-patterns with concrete examples
- **Trigger criteria** — `applies-when` conditions refine as the framework observes false positives (skill fired but didn't apply) and false negatives (should have fired but didn't)
- **AI-specific concerns** — new AI failure modes (hallucinated APIs, plausible-but-wrong patterns specific to a domain) get documented in skill §8 AI-Specific Concerns
- **Stack-specific patterns** — generated stack-skill content (e.g., a `nextjs-supabase-stripe` skill) refines as real Next.js + Supabase + Stripe projects exercise it

These four share a property: they are *empirically discoverable* through observation. The framework can credibly propose evolution based on accumulated signal.

### What cannot auto-evolve

Four categories are bounded — changes affecting them require explicit user decisions outside the evolution flow:

- **Numbered rules** — rules cite authoritative sources (§17, DEC-004). Changing a rule means changing the source it cites; that's a citation refresh, not evolution.
- **Authoritative source citations** — what counts as authoritative is a framework principle. Adding "blog post X" as an authoritative source is not evolution; it's a category change requiring conscious decision.
- **Framework principles** — §1 Contract, §2 Developer Character, §3 Workflow shape, §5 Authority Structure are not subject to use-driven mutation. They evolve through explicit decisions logged in DECISIONS.md.
- **Hard refusal list** (§5) — relaxing what the framework refuses to silently produce is a framework boundary change requiring conscious revision, not accumulated proposals.

This boundary prevents the framework from gradually drifting away from its grounding through accumulated proposals.

### Confidence levels

Observations accumulate into proposals. Proposals carry confidence levels per `DEC-2026-05-17-003` Clause 4:

- **Low confidence** — 1–2 observations. Not surfaced for review (might be coincidence).
- **Medium confidence** — 3–9 observations across distinct sessions. Surfaced for review.
- **High confidence** — 10+ observations or strong pattern signal. Surfaced for review with priority.

The framework doesn't auto-propose at low confidence. Noise gets filtered before reaching review attention.

### Human review required

`/tgf:review-evolution` surfaces pending proposals from `.tgf/evolution/proposals/pending/`. Each proposal includes:

- The proposed change (concrete diff to a skill file)
- The evidence (which observations led here, with session attribution)
- The confidence level and supporting count
- The category (anti-pattern, trigger refinement, AI concern, stack pattern)

User decides: accept (proposal moves to `accepted/`, change applied to skill), reject (moves to `rejected/` with rationale), or defer (stays pending with note). No proposal applies without explicit user action.

### Data poisoning mitigation

Self-evolution introduces a supply-chain concern: poisoned observations could shape skill content. `OWASP LLM04:2025` (Data and Model Poisoning) is the canonical reference for this risk class. TGF applies its prevention strategies:

- **Track observation origins** — each observation records its session, prompt context, and trigger; observations from anomalous sessions can be flagged
- **Vet observations before treating as actionable** — confidence thresholds filter low-quality signal before review
- **Sandbox proposed changes** — `pending/` is a staging area; nothing applies until human review
- **Monitor for poisoning signs** — statistical anomalies (sudden volume spikes, observations clustered from a single session, observations contradicting other signals) surface in framework health
- **Cross-source verification** — proposals for citation-related content (rare; mostly out of scope) require source verification per DEC-004

### Evolution input sources

Observations come from four streams:

- **Session log analysis** — recurring patterns across session logs reveal repeated AI failures, common user corrections, frequent skill miscalibrations
- **Waiver patterns** — when the same finding type gets waived repeatedly across sessions, the rule may be miscalibrated for typical real-world cases (per §11)
- **Citation refresh outcomes** — when a source update changes a cited rule, downstream skill content may need adjustment
- **User pushback patterns** — repeated overrides of a specific finding type signal that either the rule needs context-awareness or the user's project has legitimate exception patterns

Each stream feeds the `observations/` directory. Aggregation produces proposals. Review produces accepted changes.

### Cadence

Evolution review cadence ties to §17 citation verification:

- **Fast-moving domains** (supply chain, AI security) — quarterly proposal review recommended
- **Stable frameworks** (compliance, foundational security) — annual proposal review
- **Stack-specific skills** — review at major stack version changes (framework v4 → v5, etc.)

`/tgf:framework-health` (§22) surfaces stale proposal queues — proposals pending review past the recommended cadence — so backlog becomes visible.

### Plain-language impact

What self-evolution adds:

- **Real-world signal informs governance** — the framework adapts to what actually happens, not just what was anticipated at design time
- **Stack-specific patterns improve over time** — the stack skills that ship with v1 evolve as more real projects exercise them
- **AI failure modes surface as concerns** — new ways AI gets things wrong get captured as documented concerns rather than rediscovered repeatedly

What self-evolution does *not* do:

- **Replace the user's judgment** — proposals surface; the user decides
- **Drift framework principles** — rules, citations, principles, hard refusals remain bounded
- **Apply silently** — every change has a paper trail in `proposals/accepted/`

---

## §22 Continual Improvement

The framework's value depends on staying current. Authoritative sources update. Threat landscapes shift. AI failure modes emerge. Adopter projects exercise skills in ways v1 didn't anticipate. A framework that ships once and stagnates becomes worse than no framework — it gives false confidence in guidance that no longer holds.

TGF improves through three feeding loops, each grounded in concrete data sources.

### Three improvement loops

- **Citation refresh** (§17 + DEC-004) — sources update on their own cadence; cited rules get re-verified; skills with stale citations get flagged and refreshed. Mechanism: `/tgf:verify-citation` runs verification on demand; periodic refresh catches drift on cadence.
- **Evolution proposals** (§21) — observations accumulate from real use; medium- and high-confidence proposals surface for human review; accepted proposals refine skill content. Mechanism: `/tgf:review-evolution` surfaces pending proposals from `.tgf/evolution/proposals/pending/`.
- **Telemetry analysis** (§19) — per-session data on which skills loaded, which produced findings, and which had high token cost relative to value surfaces patterns invisible at the individual-session level. Mechanism: `/tgf:framework-health` aggregates telemetry quarterly.

Each loop feeds the others. Telemetry surfaces a skill with low signal-to-noise — evolution proposes a trigger refinement — accepted, the trigger refines — telemetry confirms the improvement. Citation refresh notices a source revision — affected anti-patterns may need updating — evolution surfaces refined proposals.

### Quarterly framework health review

`/tgf:framework-health` surfaces concrete patterns:

- **Skills loaded but never produced findings** — signal for over-broad triggers or scope mismatch
- **Skills with high token cost relative to findings produced** — signal for noise-to-signal calibration issues
- **Frequently waived findings** — signal that a rule may be miscalibrated for typical real-world cases (per §11)
- **Stale citations** — skills past their `refresh-recommended` date without re-verification
- **Stale proposal queues** — evolution proposals pending review past recommended cadence (per §21)

The user reviews the report and decides which signals to act on. The framework surfaces; the user decides.

### User pushback as signal

Repeated waivers of similar findings across sessions, or repeated overrides of a specific recommendation type, are not just operational noise — they're calibration signal. The framework treats consistent user pushback as input to evolution proposals (§21). The user can override individual findings without that override implying "the rule is wrong"; but a pattern of overrides on the same rule type warrants review.

### Authoritative source freshness cadence

Sources refresh on cadences appropriate to their volatility:

- **Quarterly** — fast-moving domains where new attack patterns and CVEs accumulate (supply chain, AI security, threat intelligence)
- **Semi-annual** — framework major version cycles (OWASP Top 10 revisions, NIST publication updates)
- **Annual** — stable compliance regimes (HIPAA, PCI-DSS, SOC 2, GDPR) and foundational standards (ISO 27001 / 27002)

The framework doesn't predict source changes; it polls on cadence and surfaces drift via the framework health report.

### What continual improvement is bounded by

Improvement is bounded by what evolution can and cannot do (§21) and by what citation discipline allows (§17, DEC-004):

- No auto-apply of any proposal — every accepted change is a conscious user decision
- No drift in framework principles, hard refusals, or authority structure — these change only through explicit revision logged in DECISIONS.md
- No silent citation substitution — citations track verifiable sources; proposed replacements require source-quality verification

The improvement loop is *bounded by* the framework's identity. It refines what the framework knows without changing what the framework is.

### Plain-language impact

What continual improvement prevents:

- **Framework stagnation** — citations don't rot silently; skills don't accumulate dead weight; calibration improves over time
- **Compounding drift** — when sources change, downstream skill content gets reviewed rather than allowed to diverge
- **Invisible miscalibration** — telemetry surfaces which skills earn their keep and which need refinement

What it does *not* do:

- **Auto-improve** — every change is human-reviewed
- **Predict the future** — the framework adapts to changes after they happen, not before
- **Replace user judgment** — surfaces patterns; user decides what to act on

### Reference

This section synthesizes mechanisms documented elsewhere: §17 (citation verification), §19 (token efficiency and telemetry), §21 (self-evolving knowledge), `DEC-2026-05-17-003` Clauses 4 and 5, and `DEC-2026-05-17-004` (authoritative source verification). Phase 11 (Meta-Skills) implements the `framework-health` meta-skill that surfaces these patterns; this section documents the discipline.
