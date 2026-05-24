# Decisions

Architectural decision records (ADRs) for The Governance Framework. Newer decisions appear at the top.

Each decision captures: what was decided, when, why, what alternatives were considered, and downstream consequences.

---

## DEC-2026-05-20-010: Disable `security-guidance` plugin hook for TGF via project-local env override

**Decided:** Add `env.ENABLE_SECURITY_REMINDER = "0"` to TGF's project-local `.claude/settings.local.json` (gitignored) to disable the `security-guidance@claude-plugins-official` plugin's substring-scan hook for TGF only. The hook trips on the substring patterns TGF's security skills exist to document as anti-patterns; TGF's four-pass review covers the same risk surface with stronger contextual analysis. Other projects retain the hook unchanged.

**Date:** 2026-05-20

**Context:** Phase 4 commit 3/6 (SECURITY-CORE skill) was blocked by `security_reminder_hook.py` from `security-guidance@claude-plugins-official`. The hook is a `PreToolUse` substring scanner (matches on `Edit|Write|MultiEdit`) that exits with code 2 to block tool execution when it detects any of: `exec(`, `child_process.exec`, `execSync(`, `os.system`, `pickle`, `eval(`, `new Function`, `dangerouslySetInnerHTML`, `document.write`, `.innerHTML =`, or GitHub Actions workflow file paths.

The hook's design is sound for typical app codebases — it surfaces dangerous patterns where they likely indicate vulnerabilities. TGF's nature inverts the assumption: TGF is itself a security framework whose content explicitly catalogs these patterns as anti-patterns to teach adopters to reject them. Phase 4 (3 always-on skills), Phase 6 (11 foundation security skills), and Phase 7 (22 extended security skills) extend this coverage substantially. The hook fires on TGF's core documentation content and would impose multi-retry friction on ~33 future skill commits.

The hook author (Anthropic, per plugin manifest) built a documented kill switch into the hook itself: the environment variable `ENABLE_SECURITY_REMINDER`. Setting it to `"0"` causes the hook to exit immediately at line 224 of `security_reminder_hook.py` (`sys.exit(0)`) without scanning. This is the cleanest mechanism available — using the author's own opt-out rather than disabling the plugin globally, modifying plugin source (which would be reset on plugin update), or working around with file-naming tricks.

**Decision:**

1. **Add `env.ENABLE_SECURITY_REMINDER = "0"` to `.claude/settings.local.json`** for the TGF project. The file is already gitignored per Claude Code's `settings.local.json` convention, so the override does not appear in the public repo and does not affect adopters who install TGF as a plugin in their own projects.

2. **The plugin remains enabled in user-level `~/.claude/settings.json`.** Other projects retain the hook unchanged. The disable is scoped to TGF only.

3. **Defense substitution is explicit, not implicit.** TGF's four-pass review (per `docs/WORKFLOW.md` §4) covers the same risk surface as the hook with stronger contextual analysis: substring scans cannot distinguish documentation that *discusses* `exec()` from code that *calls* `exec()`; the four-pass Code Review + Security Audit + Red Team + Holistic passes can and do. SECURITY-CORE's anti-patterns (Phase 4 commit 3/6) cover the hardcoded-credentials, custom-crypto, disabled-TLS, broken-algorithms, secret-logging, SQL injection, authorization-bypass, and shell-injection categories. Future Phase 6/7 skills extend depth.

4. **The decision is reversible at any time.** Removing the `env` field restores the hook. The ADR documents the rationale so a future maintainer can re-evaluate if four-pass coverage becomes thinner (which should not happen — Phase 6+ adds depth, not subtraction).

5. **No WAIVER-LOG entry is created.** TGF as the framework itself does not maintain operational logs that adopter projects maintain (per `CLAUDE.md` §11 and prior session continuity: TGF doesn't have `docs/ERROR-LOG.md` etc. because it's the framework, not a project governed by the framework). This ADR is the canonical capture for the decision.

**Alternatives considered:**

- **Disable the `security-guidance` plugin entirely in user-level settings.** Rejected. Overly broad. Other projects benefit from the hook in their non-security-documentation contexts. Dropping a security layer should be scoped and documented, not blanket-applied across unrelated projects.

- **Modify the hook source to skip TGF paths.** Rejected. The hook lives in the plugin marketplace cache and would be reset on plugin update. Brittle, hostile to future plugin maintainers, and creates upstream-drift risk.

- **Retry every Write/Edit blocked by the hook using the session-dedup behavior.** Rejected as strategy. The dedup works per (file_path, rule_name) per session — each new file's first Write blocks once. For Phase 6 alone (11 security skills × 3 files × multiple trigger rules per file) the cumulative friction is substantial and adds no defense value.

- **Restructure SECURITY-CORE content to avoid hook trigger substrings.** Rejected. The patterns `exec()`, `os.system`, `pickle`, etc. ARE the canonical names for the patterns SECURITY-CORE exists to teach adopters to reject. Renaming them in documentation would defeat the skill's purpose and conflict with cited authoritative sources (OWASP, NIST) that use the canonical names.

- **Defer the decision and accept retry friction for Phase 4 only.** Rejected as strategy. The friction compounds across Phase 6 (11 skills) and Phase 7 (22 skills); deferring just postpones a 33-skill problem.

**Consequences:**

- `.claude/settings.local.json` updated with the `env` override. The file is gitignored; the change is local-only.
- Phase 4 commit 3/6 (SECURITY-CORE skill) proceeds without hook friction.
- All future security skills (Phase 6: 11 skills; Phase 7: 22 skills) write without the hook intercepting.
- The four-pass review (per `docs/WORKFLOW.md` §4) is the sole security-tooling layer for TGF Write/Edit operations. This is consistent with the framework's architectural intent: TGF's own discipline replaces external substring-scan layers for this project.
- Hook scripts in `hooks/scripts/` (Phase 12 Hook Library) become writable. These will use `subprocess`/`exec` legitimately for their work; Stage 5 Security Audit catches unsafe patterns.
- If a future Claude Code release introduces a more granular per-hook disable mechanism in project settings, this decision can migrate to that mechanism without changing the substantive outcome.
- Adopters who install TGF as a plugin in their own projects are unaffected. TGF's plugin manifest does not declare `security-guidance` as a dependency; adopters' settings.json controls their hook configuration independently.

---

## DEC-2026-05-19-009: Hook physical layout amendment — plugin-native JSON config

**Decided:** Amend `DEC-2026-05-17-005` (hook architecture amendment) to specify that TGF's canonical hook layout is the plugin-native JSON format (`hooks/hooks.json` at plugin root) rather than the PascalCase directory structure (`.claude/hooks/<EventName>/NN-name.sh`). The directory format remains valid for standalone `.claude/hooks/` usage by adopters who choose not to install TGF as a plugin, but TGF's distributed form uses the JSON format.

**Date:** 2026-05-19

**Context:** `DEC-2026-05-17-005` specified the hook event taxonomy (PascalCase event names matching Claude Code's actual events) and the physical layout (`.claude/hooks/<EventName>/NN-name.sh` directory convention). At the time, TGF was conceived as a `.claude/` directory drop-in. Phase 4 research surfaced (per `DEC-2026-05-19-007`) that TGF's primary distribution is a plugin. Plugin distribution requires `hooks/hooks.json` at the plugin root — the JSON object format identical to what appears in `.claude/settings.json` `hooks` blocks. The directory + numbered scripts convention is not used in plugin distribution.

The two formats are not just different paths; they're different *mechanisms*:

- **Standalone `.claude/hooks/<EventName>/NN-name.sh`:** each numbered script in an event directory is auto-discovered and invoked when that event fires. Execution order is determined by the numeric prefix.
- **Plugin `hooks/hooks.json`:** a JSON configuration object mapping event names to matchers and command invocations. Same format as `.claude/settings.json` `hooks` blocks. Execution order is the array order.

Leaving DEC-005's directory convention unamended would create the same documentation/repo divergence problem DEC-005 itself was correcting: WORKFLOW.md §6 references hook contracts; the repo would ship a directory layout that doesn't match plugin distribution.

**Decision:**

1. **TGF's distributed form uses `hooks/hooks.json` at the plugin root.** This is the canonical format. All Phase 12 (Hook Library) work ships in this format.

2. **The hook event taxonomy from DEC-005 stands unchanged.** `SessionStart`, `SessionEnd`, `PreToolUse`, `PostToolUse`, `SubagentStart`, `SubagentStop`, `FileChanged`, `ConfigChange`, plus other Claude Code events as needed. The events themselves don't change; only the physical layout of the hook configuration files.

3. **Hook script files (the actual shell scripts) live in `hooks/scripts/` at the plugin root,** referenced from `hooks/hooks.json` by path. This separates configuration from implementation while keeping both in the plugin's hook subtree.

4. **Standalone `.claude/hooks/<EventName>/NN-name.sh` convention remains valid** for adopters who copy TGF's source rather than install the plugin. TGF documents this as a secondary path but does not maintain a parallel implementation — adopters using the standalone path translate from `hooks/hooks.json` themselves or copy the JSON into their `.claude/settings.json`.

5. **The current repo's empty `.claude/hooks/<EventName>/` placeholder directories** are removed in the pre-Phase-4 housekeeping commit. The repo restructures to the plugin layout (`hooks/hooks.json` + `hooks/scripts/`) per `DEC-2026-05-19-007`.

6. **Git hooks (`.claude/git-hooks/`) are unaffected.** Git-layer enforcement is a separate concern from Claude Code hooks (per DEC-005). The git-hooks subtree may eventually move to the plugin's `bin/` or stay separate; that's a Phase 12 implementation decision, not a DEC-009 concern.

**Alternatives considered:**

- **Maintain both formats in parallel.** Rejected. Duplicated maintenance burden; risk of drift between the two implementations; complexity for adopters trying to understand which format they should reference.
- **Keep DEC-005's directory convention and require adopters to translate to JSON.** Rejected for plugin distribution path. The plugin is the primary distribution; making it secondary creates friction for the typical adopter.
- **Edit `DEC-2026-05-17-005` in place to switch the convention.** Rejected. ADRs preserve decision history. The original DEC-005 captures *why* TGF moved to PascalCase events; this ADR captures *why* the physical layout shifted further to plugin-native JSON.

**Consequences:**

- Pre-Phase-4 housekeeping commit removes the `.claude/hooks/<EventName>/` placeholder directories and creates `hooks/hooks.json` (empty configuration ready for Phase 12).
- Phase 12 (Hook Library) implementation ships scripts in `hooks/scripts/` referenced from `hooks/hooks.json`.
- ARCHITECTURE.md §18 (hooks for enforcement) and WORKFLOW.md §6 (hook integration contracts) need a clarifying note that the *physical* layout is plugin-native JSON; the conceptual taxonomy stands.
- `DEC-2026-05-17-005` is amended in effect by this ADR for the physical layout. The original DEC-005 remains as historical record; the event taxonomy portion of DEC-005 continues to apply operationally.
- Adopter `templates/CLAUDE.md.template` may eventually need a note for adopters who choose standalone-path TGF usage; deferred until template-update phase.

---

## DEC-2026-05-19-008: Principled skill catalog consolidation

**Decided:** Consolidate the originally-planned skill catalog (per `CLAUDE.md` §9 / `ROADMAP.md` Phases 4-10) from ~80 skills to ~75 skills, targeting clusters where domain overlap is real and granular activation does not pay off. Adopt reference files as the standard pattern for managing citation density within the 300-line SKILL.md body budget specified in `DEC-2026-05-19-007`.

**Date:** 2026-05-19

**Context:** Phase 4 research surfaced two constraints that affect skill catalog design:

- **Description budget pressure.** Claude Code's skill description budget defaults to 1% of context window. With ~80 skills, descriptions hit the budget and get compressed (least-used dropped first), making discovery less reliable.
- **Citation density vs body budget.** TGF's authoritative source discipline (per `DEC-2026-05-17-004`) requires rule-level citations. Properly-cited rules average 15-25 lines each; 5 rules + 8 anti-patterns with code examples + sources table + principles + discovery + AI concerns + workflow + subagent context comfortably exceeds 500 lines per skill before reference material.

Both pressures suggest two interventions: (1) consolidate skills where domain overlap genuinely reduces precision rather than just count, and (2) adopt reference files for verbose content per Anthropic's spec.

**Decision:**

### Consolidations

1. **Architectural cluster (5 → 2 skills).** Consolidate `security-defense-in-depth`, `security-zero-trust`, `security-least-privilege`, `security-assumed-breach` into a single `security-architectural-principles` skill. These four overlap heavily in principles and are typically applied together. Keep `security-secure-architecture` separate — it covers *how to design* (different scope from *which principles to apply*).

2. **CIA triad (3 → 1 skill).** Consolidate `security-confidentiality`, `security-integrity`, `security-availability` into a single `security-cia-triad` skill. The triad is a foundational concept applied together at the planning level; three separate skills create artificial fragmentation for what is essentially one taxonomic framework.

### Clusters NOT consolidated

3. **IAM cluster (4 skills) stays split.** `security-iam-authentication`, `security-iam-sessions`, `security-iam-authorization`, `security-iam-oauth-oidc` are the most frequently-touched security domain in typical projects. Granular `applies-when` matching (via `paths` + description) pays off — an OAuth-specific change should load OAuth content, not all of IAM. Variable cost per invocation matters more than fixed catalog count here.

4. **Data layer cluster (3 skills) stays split.** `security-database`, `security-data-encryption`, `security-data-classification` touch different trust boundaries and operational patterns. Granular activation pays off.

5. **Threat management cluster (3 skills) stays split.** `security-threat-modeling`, `security-attack-surface`, `security-supply-chain` are meaningfully distinct domains.

6. **All other skill clusters stay as currently scoped.** Application skills, operations, compliance, AI-specific, meta-skills, project-specific — no consolidations.

### Net change

- Originally planned: ~80 skills (per `CLAUDE.md` §9)
- After consolidation: ~75 skills (5 skills consolidated: 4 architectural → 1; 3 CIA → 1; net -5)
- Phases 4, 9, 11, 13 unaffected (consolidations are within Phase 7's extended security skills)

### Reference file pattern (standard)

Every skill SKILL.md body stays ≤300 lines per `DEC-2026-05-19-007`. Verbose content moves to reference files in the skill directory:

```
.claude/skills/<skill-name>/
├── SKILL.md           # principles, rule summaries, navigation (≤300 lines)
├── rules.md           # full rules with rule-level citations (loaded on demand)
├── anti-patterns.md   # 8+ anti-patterns paired with canonical, with code (loaded on demand)
└── citations.md       # full citation table with verbatim source quotes (loaded on demand)
```

SKILL.md references the reference files so Claude knows when to load them (per Anthropic's spec: *"Reference these files from your `SKILL.md` so Claude knows what they contain and when to load them"*). The 8+ anti-patterns and 5+ rules requirements from `DEC-2026-05-17-003` Clause 1 stand; the *location* of that content shifts from SKILL.md body to reference files.

**Alternatives considered:**

- **Flat 20% consolidation.** Rejected. Arbitrary target loses precision where granularity pays off (IAM, data, threat management). Principled consolidation focused on real overlap is more defensible.
- **No consolidation; rely entirely on reference files for budget management.** Rejected. Reference files solve citation density but not description budget pressure. Some consolidation is warranted on the description-budget grounds alone.
- **More aggressive consolidation (~60 skills).** Rejected. Goes beyond real overlap; starts consolidating skills with distinct activation patterns. Cost (less granular `applies-when` matching, larger bodies per invocation) outweighs benefit.

**Consequences:**

- `CLAUDE.md` §9 Skill Index updates to reflect the new catalog count (~75 skills) and the consolidations.
- `ROADMAP.md` Phase 7 updates to reflect consolidated skill names.
- `templates/SKILL.md.template` reflects the reference-file pattern as standard (SKILL.md body budget ≤300 lines; reference files for verbose content).
- Phase 4 (3 always-on skills) ships against the reference-file pattern from day one — sets the convention all later phases inherit.
- Phase 7 (extended security skills) implementations follow the consolidated catalog.

---

## DEC-2026-05-19-007: TGF architecture as plugin with orchestrator agent

**Decided:** TGF's distribution and architectural form is a Claude Code plugin (per the canonical plugin specification). The framework's "always-on skill" behavior is implemented natively via a custom orchestrator agent (`tgf-orchestrator`) that preloads CODE-QUALITY, SECURITY-CORE, and CONTINUITY via the Anthropic-native `skills:` frontmatter field. Four-pass review subagents are similarly defined with skill preloads. Adopters install TGF as a plugin and optionally activate the orchestrator agent for the full framework experience.

**Date:** 2026-05-19

**Context:** Phase 4 research surfaced that Anthropic's Agent Skills specification is purely description-driven — there is no native `always-on: true` field or equivalent mechanism. TGF's original conception of "always-on skills" (per `CLAUDE.md` §6) was not supported by Claude Code natively. Three viable paths were considered:

1. Embed the trait content in CLAUDE.md directly (rejected — pushes CLAUDE.md back over the 40k-char performance threshold cleared in commit `a630540`; loses skill structure with anti-patterns paired with canonical patterns; loses self-evolution mechanism)
2. Compose Anthropic primitives with a `SessionStart` hook injecting principles via `additionalContext` (the original Phase 4 proposal — works but bespoke)
3. Use the Claude Code `--agent` flag with a custom orchestrator agent that preloads always-on skills via the native `skills:` frontmatter field (selected — purely Anthropic-native, eliminates the bespoke composition)

Deeper Phase 4 research (Claude Code Subagents documentation + Plugins documentation) confirmed:

- *"Run the whole session as a subagent. Pass `--agent <name>` to start a session where the main thread itself takes on that subagent's system prompt, tool restrictions, and model... CLAUDE.md files and project memory still load through the normal message flow."*
- *"Use the `skills` field to inject skill content into a subagent's context at startup. The full content of each listed skill is injected into the subagent's context at startup."*
- *"Plugin `settings.json` can activate one of the plugin's custom agents as the main thread, applying its system prompt, tool restrictions, and model. This lets a plugin change how Claude Code behaves by default when enabled."*

These mechanisms compose cleanly into TGF's always-on architecture without inventing new primitives.

**Decision:**

### Plugin distribution

1. **TGF's primary distribution is a Claude Code plugin.** Phase 1 already scaffolded `.claude-plugin/plugin.json` and `marketplace.json`. Plugin distribution provides versioning (via `version` field), shareable installation (`/plugin install`), namespace isolation (`/tgf:skill-name` prefix), settings activation, and background monitor capabilities.

2. **The repo restructures to plugin layout.** Components at plugin root:
   - `.claude-plugin/plugin.json` — manifest (unchanged from Phase 1)
   - `skills/` — skill directories (migrated from `.claude/skills/`)
   - `agents/` — custom agent definitions including `tgf-orchestrator` and review subagents
   - `hooks/hooks.json` — hook configuration (per `DEC-2026-05-19-009`)
   - `hooks/scripts/` — hook script implementations
   - `monitors/monitors.json` — background monitors (optional, deferred)
   - `settings.json` — default settings activating `tgf-orchestrator` agent

3. **Standalone `.claude/` usage remains supported as a secondary path** for adopters who copy TGF's source rather than install the plugin. Both adoption paths are documented; the plugin path is primary.

### Orchestrator agent (`tgf-orchestrator`)

4. **TGF defines a custom agent at `agents/tgf-orchestrator.md`** that becomes the main session via `--agent tgf-orchestrator` or via `settings.json` `"agent": "tgf-orchestrator"` (the default for TGF-installed projects). The orchestrator's system prompt encodes the six-stage workflow contract (per CLAUDE.md §3) and engages TGF's discipline.

5. **The orchestrator preloads the three always-on skills via the `skills:` field:**

   ```yaml
   ---
   name: tgf-orchestrator
   description: TGF governance framework orchestrator. Engages six-stage workflow for all coding and planning work.
   skills:
     - code-quality
     - security-core
     - continuity
   model: inherit
   ---
   ```

   The full content of each listed skill is injected into the orchestrator's context at startup (per Anthropic's spec). The "always-on" guarantee comes from this native mechanism, not from a TGF-invented `always-on: true` field.

6. **Skill content discipline.** Each always-on skill's SKILL.md body stays ≤300 lines (per `DEC-2026-05-19-008` reference-file pattern). Verbose content (full rules, anti-patterns with code, citation tables) lives in reference files loaded on demand. The 3 × 300-line preload represents ~20k tokens of always-on context — real cost, accepted for the always-on guarantee, bounded by the body budget.

### Review subagents

7. **Four-pass review subagents are defined at `agents/{code-reviewer,security-auditor,red-team,holistic-reviewer}.md`** with skill preloads matching their domain:

   - `code-reviewer` preloads `code-quality`
   - `security-auditor` preloads `security-core` plus applicable security skills (loaded per Stage 3 governance plan)
   - `red-team` preloads `security-core` (adversarial perspective; specific skills loaded per scope)
   - `holistic-reviewer` preloads `continuity`

   Each review subagent uses `memory: project` to enable self-evolution data accumulation (per `DEC-2026-05-19-007` integration with §21 self-evolving knowledge).

8. **Verifier subagent** dispatched per `CLAUDE.md` §16; preloads none by default but receives `ai_generated_portions` context from the orchestrator.

### Self-evolution data layer

9. **Agent memory (`memory: project`) is the data layer for self-evolution observations** (per `ARCHITECTURE.md` §21). The `.tgf/evolution/observations/` directory specified in `DEC-2026-05-17-003` Clause 4 is replaced by `.claude/agent-memory/{agent-name}/MEMORY.md` per Anthropic's native agent-memory mechanism. Phase 11 (Meta-Skills) implements the evolution meta-skill that reads agent memories and produces proposals. The `.tgf/evolution/proposals/{pending,accepted,rejected}/` structure stays as TGF-internal (no Anthropic-native equivalent for the proposal workflow).

### Mode-aware skill catalog (deferred)

10. **Mode-aware skill visibility via `skillOverrides` in settings is identified as a future capability** (Hardening mode shows full security catalog; Exploration mode hides advanced compliance skills). Implementation deferred until Phase 15 (Documentation) when adopter-facing mode-switch tooling matures. For Phase 4–12, all installed skills are visible.

### Plugin-native TGF state

11. **TGF state directory (`.tgf/state/sessions/{session_id}.json` per `DEC-2026-05-19-006`) is unaffected by this ADR.** It remains the session state mechanism for `project_mode` + `change_tier` + `current_stage`. Phase 12 hook implementations read this file per the pattern in WORKFLOW.md §6.

**Alternatives considered:**

- **SessionStart-hook injection of principles via `additionalContext` (original Phase 4 plan).** Rejected as no-longer-needed once the `skills:` field on the orchestrator agent was discovered. The hook composition was a workaround for an absence that doesn't exist — Anthropic provides the mechanism natively for agent contexts.
- **Embed always-on content directly in CLAUDE.md.** Rejected per the criteria above (size, structure, self-evolution).
- **Description-driven discovery with broad descriptions for always-on skills.** Rejected as unreliable (Claude's discovery is probabilistic) and as competing against ~70 other skills for description budget.
- **Standalone `.claude/` directory as primary distribution (no plugin).** Rejected because plugin gives versioning, installation simplicity, and the `agent` settings mechanism that activates the orchestrator by default.

**Consequences:**

- Pre-Phase-4 housekeeping commit restructures the repo to plugin layout (`skills/`, `agents/`, `hooks/hooks.json`, `settings.json` at plugin root; `.claude/skills/` and `.claude/hooks/<EventName>/` placeholders removed).
- Phase 4 implementation produces 3 always-on skills (CODE-QUALITY, SECURITY-CORE, CONTINUITY) in plugin `skills/` directory plus the `tgf-orchestrator` agent definition in `agents/`. Review subagent definitions may land in Phase 4 or defer to Phase 11.
- `CLAUDE.md` §6 (Always-On Skills section) language updates to reflect that the always-on behavior is implemented via orchestrator agent skill preload, not via an invented frontmatter mechanism.
- `templates/CLAUDE.md.template` may need similar update for adopters; deferred.
- `templates/SKILL.md.template` updated to reflect: only Anthropic-native frontmatter fields are runtime; TGF-extension fields (`sources`, `applies-when` sub-fields beyond `paths`, `disqualifying-when`, `last-generated`, `refresh-recommended`, `self-evolution`) are TGF-internal metadata for Phase 11 meta-skill consumption, not Claude Code runtime fields. `DEC-2026-05-17-003` Clause 1 is amended in effect by this clarification (the original Clause 1 stands as historical record).
- `ARCHITECTURE.md` §19 (token efficiency) gains a note about the always-on preload cost (~20k tokens per session for 3 × 300-line SKILL.md bodies) and reaffirms the 300-line discipline as critical.
- WORKFLOW.md §4 subagent schemas reflect that `skills:` preload is the always-on mechanism for orchestrator and review subagents.
- Phase 1's plugin scaffolding is the right foundation; no rework needed beyond the directory restructure.

---

## DEC-2026-05-19-006: TGF session state architecture — file-based, session-keyed

**Decided:** TGF-specific runtime context (`project_mode`, `change_tier`, and future per-session state) lives in a file-based store at `.tgf/state/sessions/{session_id}.json`. The orchestrator (main agent) writes to it; hooks and meta-skills read from it on demand. The `.tgf/state/` directory is gitignored (it's per-session operational state, not committed artifact).

**Date:** 2026-05-19

**Context:** Phase 3 planning surfaced that ARCHITECTURE.md §18 documents Claude Code's actual hook stdin JSON (which carries `session_id`, `cwd`, `permission_mode`, `hook_event_name`, plus event-specific fields like `tool_name` and `tool_input`) but does *not* carry TGF concepts (`project_mode` is exploration/prototype/building/hardening/maintenance; `change_tier` is trivial/small/medium/large). These TGF concepts gate hook profile activation (§18 mode profiles) and orchestration depth (§19, §20 cost-aware dispatch by tier). Hooks need access to them at fire time.

`DEC-2026-05-17-003` Clause 2's original specification listed `project_mode` and `change_tier` as part of the hook stdin JSON — that was invented before consulting Claude Code's canonical source. `DEC-2026-05-17-005` corrected the event names but did not address the TGF-context-injection question. This ADR closes that gap.

Without an explicit mechanism, hook scripts would either: (i) embed mode/tier assumptions in script logic (fragile and untestable), (ii) reimplement mode-inference per script (duplication and drift), or (iii) load entire PROJECT-CONTEXT to derive mode (expensive per fire).

**Decision:**

1. **State file location:** `.tgf/state/sessions/{session_id}.json`. Session-keyed so concurrent Claude Code sessions in the same repo do not collide. `session_id` is in every hook's stdin JSON per Claude Code's contract.

2. **State file contents (minimum):**
   ```
   {
     "session_id": "<from Claude Code>",
     "project_mode": "exploration|prototype|building|hardening|maintenance",
     "change_tier": "trivial|small|medium|large",
     "current_stage": "research|scope|plan|implement|review|commit",
     "started": "<ISO 8601 timestamp>",
     "last_updated": "<ISO 8601 timestamp>"
   }
   ```
   Additional fields may accumulate as Phase 11 (Meta-Skills) and Phase 12 (Hook Library) need them. The schema is forward-compatible: readers ignore unknown fields.

3. **Write authority:** the orchestrator (main agent) writes session state. A `SessionStart` hook initializes the file with inferred `project_mode` from PROJECT-CONTEXT. The orchestrator updates `change_tier` and `current_stage` as the workflow progresses through stages. `/tgf:set-mode` updates `project_mode` directly.

4. **Read authority:** hooks read the file at fire time. Meta-skills read it when they need context. No reader-writer locking required at TGF v1 scale (single user, single Claude Code session per repo typical).

5. **Gitignored:** `.tgf/state/` is added to `.gitignore.template` (it joins `.tgf/telemetry/` and `.tgf/evolution/observations/` as gitignored TGF-internal state). State is per-session ephemeral operational data, not project artifact.

6. **Cleanup:** a `SessionEnd` hook removes the session's state file. Stale files from crashed sessions get cleaned up by a `SessionStart` hook that prunes files older than 30 days.

**Alternatives considered:**

- **`SessionStart` additionalContext injection.** Rejected. `additionalContext` is a stdout field on `SessionStart` for injecting context into Claude's session — it's a Claude-facing mechanism, not a hook-to-hook communication channel. Misusing it would couple TGF to undocumented behavior.
- **Environment variables (`TGF_PROJECT_MODE`, `TGF_CHANGE_TIER`).** Rejected. `change_tier` changes per workflow invocation; env vars would need re-export on every Stage 2 completion, which is awkward. File-based handles per-invocation updates naturally.
- **Single global `.tgf/state/current.json`.** Rejected. Two Claude Code sessions in the same repo would stomp each other's state. Session-keyed eliminates the collision risk for a minor directory-organization cost.
- **Embed mode/tier in PROJECT-CONTEXT or another committed artifact.** Rejected. `change_tier` is per-invocation; committing it would create churn. PROJECT-CONTEXT is the source of truth for mode *defaults*; runtime state is downstream.

**Consequences:**

- Phase 11 (Meta-Skills) implements the orchestration meta-skill that writes session state at workflow stage boundaries.
- Phase 12 (Hook Library) implements hooks that read session state to determine profile applicability (mode-aware profiles per ARCHITECTURE.md §18) and dispatch depth (tier scaling per ARCHITECTURE.md §19/§20).
- `.gitignore.template` (Phase 1 artifact) already covers `.tgf/state/` via the broader `.tgf/` ignore — no template change needed.
- WORKFLOW.md (Phase 3 deliverable) §6 Hook Integration Contracts references this ADR when specifying how hooks access TGF context. WORKFLOW.md §2 Conceptual Model identifies the orchestrator as the state-writer.
- This ADR is approved subject to Phase 3 Step 1 spot-check of the Claude Code Hooks reference. If Claude Code's hook context-passing mechanisms turn out richer than ARCHITECTURE.md §18 documents, this decision could be revisited via a superseding ADR. Low probability — the Phase 2 verification was thorough.

---

## DEC-2026-05-17-005: Hook architecture amendment — use Claude Code's actual event taxonomy

**Decided:** Amend `DEC-2026-05-17-003` Clause 2 (Hook architecture) to use Claude Code's actual hook event names rather than the kebab-case names invented in the original Phase 0 specification. Add a separate `.claude/git-hooks/` directory for git-layer enforcement, distinct from Claude Code's `.claude/hooks/`.

**Date:** 2026-05-17

**Context:** Phase 2 research (Step 1 for §18) fetched Claude Code's hooks documentation and surfaced that the event names listed in `DEC-2026-05-17-003` Clause 2 — `pre-tool-use`, `post-tool-use`, `pre-commit`, `post-commit`, `session-start`, `session-end`, `pre-skill-modification` — were invented before consulting the canonical source. The real taxonomy uses PascalCase names with a richer set (26+ events). Additionally:

- `pre-commit` and `post-commit` are **not** Claude Code events. Commit-time enforcement is implemented either via `PreToolUse` matching `Bash(git commit*)` (Claude Code-side) or via git's native `.git/hooks/` (git-side). These are different enforcement layers.
- `pre-skill-modification` is not an event. The use case is covered by `InstructionsLoaded`, `FileChanged`, and `ConfigChange`.

Leaving the original spec in place would create documentation/repo divergence (§18 of CLAUDE.md describes the corrected architecture; the repo would show the old kebab-case directory layout) and form a wrong mental model for adopters reading the repo.

**Decision:**

1. **Use Claude Code's actual event names (PascalCase)** for `.claude/hooks/<EventName>/NN-name.sh`. TGF leverages the native Claude Code hook system; TGF does not invent events.

2. **Phase 12 (Hook Library) populates the following event directories** based on identified TGF use cases. Directories exist as empty `.gitkeep` placeholders until Phase 12:
   - `SessionStart/` — load recent session logs, verify framework state
   - `SessionEnd/` — generate session log entry
   - `PreToolUse/` — block dangerous git operations, block secrets in commits, block destructive database operations
   - `PostToolUse/` — log security-relevant operations, track file changes for telemetry
   - `SubagentStart/` — log subagent dispatch
   - `SubagentStop/` — collect subagent results
   - `FileChanged/` — telemetry, framework integrity checks
   - `ConfigChange/` — alert on settings changes

3. **Git hooks live in `.claude/git-hooks/`** — a separate directory from Claude Code hooks. TGF provides shell scripts here that an opt-in install script copies into `.git/hooks/`. Git hooks fire regardless of whether the commit was initiated through Claude Code or directly via `git commit`. Use cases: verify session log entry exists, verify tests pass for the change, verify ROADMAP updated for milestone-affecting commits.

4. **All other `DEC-2026-05-17-003` Clause 2 specifications stand** — standardized JSON via stdin, exit code semantics (0 allow, 2 block, other non-blocking), mode-aware profiles configured in `.claude/hooks/profile.json`, three universal hooks always active (`block-dangerous-git`, `block-secrets-commit`, `block-destructive-db`).

5. **The current repo's `.claude/hooks/` directory layout** (which originally contained the kebab-case names from the Phase 0 spec) is corrected in this commit. Empty `.gitkeep` placeholders only; no script content existed in the old directories, so no migration was needed.

**Alternatives considered:**

- **Defer the rename to Phase 12** — rejected. Documentation (§18) and repo state should match; deferring creates "wrong now, fix later" debt that contradicts TGF's discipline.
- **Edit `DEC-2026-05-17-003` Clause 2 in place** — rejected. ADRs preserve decision history; amending in place erases the trail of why the framework looks the way it does. The original decision and this amendment both stand in the record.
- **Keep TGF's invented names as a TGF-internal abstraction layered over Claude Code events** — rejected. Adds complexity and confusion with no benefit; Claude Code's names work fine.

**Consequences:**

- §18 Hooks for Enforcement (CLAUDE.md, Phase 2 deliverable) documents the corrected architecture, citing this ADR.
- Phase 12 (Hook Library) implementation works against the corrected directory structure from the start.
- Adopters reading the repo see Claude Code event names; no risk of forming a wrong mental model.
- `DEC-2026-05-17-003` Clause 2 is amended in effect by this ADR. The original Clause 2 remains in DECISIONS.md as historical record; this ADR supersedes it for operational purposes.

---

## DEC-2026-05-17-004: Authoritative source verification & no-downloads constraint during skill creation

**Decided:** Skills citing authoritative frameworks MUST verify rule-level citations against live sources at creation/refresh time, fetched via Claude's web tools. No fetched content touches the developer filesystem except as synthesized citations and rules written by Claude.

**Date:** 2026-05-17

**Context:** TGF's value depends entirely on its citation chain being real — "OWASP says X" is not enough; "OWASP ASVS 5.0 V6.2.2 specifies Y" is required, with the citation verifiable against the live source. Equally important: TGF is being built on a developer laptop and the research methodology must not introduce supply-chain, watering-hole, or indirect prompt-injection exposure as a side effect of generating skills. Indirect prompt injection via fetched web content is documented as the #1 LLM application security risk (OWASP LLM Top 10 2025 — `LLM01:2025` Prompt Injection) and catalogued in MITRE ATLAS.

**Decision:** Six operating clauses bind every skill creation and refresh operation.

### Clause 1: Live verification at skill-creation time

When generating or refreshing a skill, the authoritative sources listed in the skill's §2 are fetched at skill-creation time. Citations identify specific rule, control, or section numbers verified against the fetched source. The skill's frontmatter records `last-generated` (when sources were verified) and `refresh-recommended` (when re-verification is due).

### Clause 2: Rule-level citation precision

Citations identify specific rule, control, or section numbers — `OWASP ASVS 5.0 V6.2.2`, `NIST SP 800-63B §5.1.1.2`, `RFC 8725 §3.1`, `MITRE ATLAS AML.T0051` — not vague references like "OWASP recommends" or "NIST best practice."

### Clause 3: Fetched content treated as untrusted input

Web-fetched content may contain prompt injection or other adversarial material. Only structured data (rule numbers, rule text, source references, version numbers, dates) is extracted. Instructions embedded in fetched content are ignored. Cross-source verification used where feasible — NIST citations cross-checked against OWASP mappings, MITRE technique IDs verified against the live ATT&CK/ATLAS knowledge bases, etc.

### Clause 4: No developer-machine downloads

Research is performed via Claude's web tools (`WebFetch` / `WebSearch`) which fetch on Anthropic's infrastructure and return processed text to Claude's context. The developer's filesystem only receives synthesized citations and rules written by Claude — not raw fetched content, scripts, executables, or click-through URLs to external resources.

### Clause 5: Paywalled sources

Standards behind paywalls (notably ISO/IEC 27001:2022 and 27002:2022) are cited by reference (control ID, title, version). Operational rule text is sourced from freely-available authoritative mappings — NIST → ISO crosswalks, OWASP → ISO mappings, OWASP ASVS chapter-to-ISO references — with attribution. Reproducing paywalled standard text directly in skill files is not permitted regardless of license access.

### Clause 6: Comparative framework research distinct from authoritative citation

Research on public Claude Code frameworks (Superpowers, great_cto, GSD, alirezarezvani's collection, etc.) informs design patterns but does NOT serve as rule-source for skills. These references appear in design rationale documents (this `DECISIONS.md`, `DESIGN-RATIONALE.md`, session logs) only — never in skill §2 Authoritative Sources tables.

**Alternatives considered:**

- **Bundling cached source content with TGF** — rejected. Bloats the repo, ages immediately, defeats the freshness discipline that is itself a value proposition, creates copyright/license exposure for any non-permissively-licensed standards.
- **Asking developers to download source PDFs themselves** — rejected. Introduces the exact supply-chain risk on developer machines the framework should eliminate.
- **Citing only frameworks broadly without rule-level precision** — rejected. Defeats TGF's authority chain and positions TGF as training-data-grade governance rather than authoritative.
- **Reproducing ISO text via organizational licensed access (institutional, military DTIC, etc.)** — rejected. Mixes licensed content into a permissively-licensed open source project, creating downstream license-compliance burden on adopters.

**Consequences:**

- `SKILL-FORGE` and `DOMAIN-RESEARCH` (Phase 11) encode this discipline as their operating procedure.
- `security-ai-research-integrity` (added to Phase 8) operationalizes the untrusted-fetched-content clauses as a first-class skill that fires when meta-skills perform external research.
- Skill freshness becomes a maintenance commitment — sources must be re-verified on the `refresh-recommended` cadence.
- TGF's value proposition explicitly includes "no supply-chain or prompt-injection exposure on adopter machines from running the framework."
- `WebFetch` / `WebSearch` become required Claude Code tools for skill creation and refresh; documented in `INSTALL.md` (Phase 15).
- The `CLAUDE.md` template's §17 Citation Verification (Phase 2 deliverable) makes the discipline visible at the framework's contract layer.

---

## DEC-2026-05-17-001: Framework name

**Decided:** "The Governance Framework" (acronym: TGF).

**Date:** 2026-05-17

**Context:** Project began as "Trust and Governance Framework" — emphasizing the GRC/trust angle. During design conversation, alternative "The Governance Framework" emerged with cleaner, more confident positioning.

**Decision:** "The Governance Framework." The acronym TGF is preserved. The definite article signals confidence and category clarity without overclaiming or coupling to a specific framing (trust, security, GRC, etc.).

**Alternatives considered:**

- "Trust and Governance Framework" — anchored to GRC/trust framing; longer; arguably narrower.
- "TGF" alone — too opaque without expansion; loses positioning value in titles and search.

**Consequences:** Affects every public-facing artifact (README, LICENSE attribution, plugin manifests, slash command namespace `/tgf:*`, documentation). Internal acronym `TGF` carries forward unchanged.

---

## DEC-2026-05-17-002: Path A — full v1 scope

**Decided:** Build the full v1 including hooks for enforcement, agent orchestration, sub-agent code review, self-evolving knowledge, token efficiency mechanisms, and continual improvement — not a minimal v1 with these deferred to v2.

**Date:** 2026-05-17

**Context:** Two-path decision presented during design conversation:

- **Path A** — full v1 (~30-50 weeks part-time) with all advanced capabilities as foundational architecture.
- **Path B** — minimal v1 (~2-3 months) shipping core framework first, advanced capabilities added in v2 based on real-use feedback.

**Decision:** Path A. Most TGF work is markdown content production with AI assistance; the timeline differential between paths is smaller than enterprise-software intuition suggests. Path A positions TGF competitively against existing public frameworks (Superpowers ~41k stars, great_cto, etc.) where shipping less polished work risks irrelevance in a crowded space.

**Alternatives considered:**

- Path B — would ship faster and let real use inform v2; trades early adoption competitiveness for time-to-public.
- Hybrid (ship Path B as v1, build Path A capabilities as v1.1-v1.5) — adds release management overhead.

**Consequences:** ~80-110 focused sessions of work across 16 phases. Higher coherence cost; higher upside if framework gains traction. Phase 0 architectural decisions reflect Path A scope.

---

## DEC-2026-05-17-003: Phase 0 architectural decisions locked

**Decided:** Five interface specifications are locked as foundational architecture. Every subsequent phase builds against them.

**Date:** 2026-05-17

**Context:** Before any skill content production, interface decisions need to be stable. Otherwise downstream work either has to be redone or accumulates inconsistency.

**Decision:** The following interfaces are locked.

### 1. Skill template with addressable section anchors

HTML comment anchors (`<!-- SECTION: ... -->`, `<!-- RULE: 5.1 -->`, `<!-- ANTI-PATTERN: AP-1 -->`, `<!-- CANONICAL: CP-1 -->`) enable section-level loading rather than full-file loading.

**Required sections (every skill):** `overview`, `sources`, `discovery`, `principles`, `rules` (≥5), `anti-patterns` (≥8), `canonical-patterns` (paired with anti-patterns), `ai-concerns`, `workflow`, `subagent-context`.

**Required frontmatter fields:** `name`, `description`, `applies-when` (with sub-fields `paths-include`, `imports-include`, `operations-include`, `data-flows-include`), `disqualifying-when`, `sources` (with versions), `last-generated`, `refresh-recommended`, `self-evolution` (with `anti-patterns-observed`, `triggers-refined`, `ai-failures-documented`).

### 2. Hook architecture

Shell scripts in `.claude/hooks/<event>/NN-name.sh`. Events: `pre-tool-use`, `post-tool-use`, `pre-commit`, `post-commit`, `session-start`, `session-end`, `pre-skill-modification`. Numeric prefix orders execution within event.

Hooks receive standardized JSON via stdin (event, timestamp, session_id, project_mode, change_tier, tool, tool_args, context). Exit 0 = allow; non-zero = block. Block hooks emit JSON on stdout: `{block, reason, details, remediation}`. Mode-aware profiles in `.claude/hooks/profile.json`. Three universal hooks always active: block-dangerous-git, block-secrets-commit, block-destructive-db.

### 3. Subagent role contracts (seven roles)

`Researcher`, `Implementer`, `Code Reviewer`, `Security Auditor`, `Red Team`, `Holistic Reviewer`, `Verifier`. Each has specified context inputs and structured JSON output. Cost-aware orchestration scales by change tier: Trivial = no subagents; Small = Code Reviewer + Holistic; Medium = all four review subagents; Large = full orchestration plus Researchers (stage 1), Implementers (stage 4 decomposition), and Verifier for AI-generated portions.

### 4. Self-evolution data structures

Lives in `.tgf/evolution/` (gitignored). Three directories: `observations/` (raw), `proposals/{pending,accepted,rejected}/`, `confidence-thresholds.json`. Confidence levels: low (1-2 observations), medium (3-9), high (10+).

**Can evolve via human-reviewed proposals:** anti-patterns, trigger criteria, AI-specific concerns, stack-skill patterns.

**Cannot auto-evolve:** numbered rules, authoritative source citations, framework principles, hard refusal list. Human review required via `/tgf:review-evolution`.

### 5. Token telemetry format

Lives in `.tgf/telemetry/sessions/*.json` (gitignored). Per session captures: `session_id`, `started`, `ended`, `project_mode`, `workflow_invocations[]` (with `stage`, `tokens_consumed`, `skills_loaded`, `skills_evaluated[]`, `subagents_dispatched`), `phases[]` (for review stage), `total_tokens`, `findings_total`, `findings_blocking`, `user_overrides`. Aggregated weekly/quarterly. Surfaced via `/tgf:framework-health`.

**Consequences:** Phases 1-16 reference these specifications. Deviation must be a conscious decision logged here. Skill files, hook scripts, meta-skills, and templates all build against these contracts.

---

## Template

Copy this template for each new decision. Use date + sequence number for the ID.

```
## DEC-YYYY-MM-DD-NNN: Decision title

**Decided:** [The decision itself in one sentence.]

**Date:** YYYY-MM-DD

**Context:** [What problem or question this decision addresses. Why now?]

**Decision:** [The decision in full, with rationale.]

**Alternatives considered:** [Options weighed and why not chosen.]

**Consequences:** [What this commits the project to; trade-offs accepted; downstream effects.]
```
