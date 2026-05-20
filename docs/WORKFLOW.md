# Workflow Specification

The implementation contract for The Governance Framework's six-stage workflow. Phases 4–12 (skills, meta-skills, hooks, stack baselines) build against this specification.

---

## §1 Purpose and Scope

This document specifies *how* the six-stage workflow described in `CLAUDE.md` §3 is implemented. It defines stage I/O contracts, skill activation points, hook integration contracts, subagent dispatch contracts (including JSON output schemas), tier and mode scaling matrices, the debugging-variant adaptation, and three worked examples that exercise the spec end-to-end.

**Relationship to other documents:**

- `CLAUDE.md` §3 — the operational *contract* (what the framework does on every coding/planning prompt). Loads every session. Read first.
- `docs/ARCHITECTURE.md` §20 — the subagent *role descriptions* (who the seven roles are, why they exist, what they're prevented from doing). This document specifies the *contracts* those roles produce.
- `docs/ARCHITECTURE.md` §15, §18, §19 — mode scaling, hook architecture, token efficiency. This document specifies the *operational integration points* derived from them.
- `DECISIONS.md` DEC-003, DEC-005, DEC-006 — the architectural decisions this document operationalizes. Citations are rule-level per DEC-004.

**Audience:** Phase 4–12 implementers (writing skills, meta-skills, hook scripts, stack baselines); framework operators understanding workflow behavior; advanced adopters writing custom skills or hooks against TGF.

**Out of scope:**

- Hook script bodies — Phase 12 (Hook Library) ships those against §6 contracts
- Skill content (rules, anti-patterns, canonical patterns) — Phases 4–10 ship those against §3 activation contracts
- Meta-skill implementation — Phase 11 builds the orchestration meta-skill against §4 schemas and §6 contracts
- Slash command implementations — Phase 14

**This document does NOT duplicate `CLAUDE.md` §3.** It specifies what §3 leaves implicit: how stages compose, what each stage produces and consumes, how skills/hooks/subagents integrate, and how tier and mode adjust execution.

---

## §2 Conceptual Model

The workflow is a state machine over six stages. Stages produce typed artifacts that the next stage consumes. Hooks fire on Claude Code's event lifecycle (independently of stage transitions). Subagents dispatch at specific stage points based on change tier.

### Stage state machine

```
       ┌──────────────┐    ┌───────────┐    ┌──────────────────────┐
START ─►│ 1. Research  ├───►│ 2. Scope  ├───►│ 3. Plan w/Governance ├──┐
       └──────────────┘    └───────────┘    └──────────────────────┘  │
                                                                       ▼
       ┌─────────────┐    ┌─────────────────────┐    ┌──────────────┐
  END ◄┤ 6. Commit   │◄───┤ 5. Four-Pass Review │◄───┤ 4. Implement │
       └─────────────┘    └─────────────────────┘    └──────────────┘
                                    │
                       (findings unresolved)
                                    │
                                    ▼
                          back to Stage 4 (rework)
```

### Valid transitions

- Stage `N` → Stage `N+1` is the default flow.
- Stage 5 → Stage 4 is the rework path when review surfaces blocking findings.
- Any stage → END (workflow halt) on user abort or unrecoverable error.
- Trivial-tier work skips Stages 1, 2, 3 evaluation (no codebase context to gather, no skills to evaluate); enters at Stage 4 with reduced Stage 5 (code review only).

### Termination conditions

A workflow invocation terminates when one of:

- **Success:** Stage 6 completes — commit landed, artifacts updated, session log entry generated.
- **Blocked:** Stage 5 surfaces findings the user neither fixes nor formally waives. Work stops; ERROR-LOG entry recorded; workflow re-enters from Stage 4 in a later invocation.
- **Aborted:** user explicitly halts; partial state captured to session log; no commit produced.
- **Hook denial:** a hook blocks at any stage (typically `PreToolUse` for tool calls or commit-time hook for commits). User can acknowledge override or accept the block. Either way, the workflow records the block in WAIVER-LOG (if overridden) or terminates pending user decision.

### Stage-to-stage handoff contracts

Each stage produces named artifacts the next stage consumes. The orchestrator persists handoff state in `.tgf/state/sessions/{session_id}.json` (per DEC-006).

| From → To | Artifact passed | Format |
|-----------|-----------------|--------|
| 1 → 2 | `research_findings` | Files read, prior decisions noted, related logs identified, ROADMAP position |
| 2 → 3 | `scope_definition` | Files in scope, change tier, trust boundaries affected, ROADMAP milestone, out-of-scope items |
| 3 → 4 | `governance_plan` | Skills that apply, rules to follow, anti-patterns to avoid, test requirements, hook integration points |
| 4 → 5 | `implementation_diff` | Changed files, lines added/removed, skill rules applied (with citations), AI-generated portions flagged |
| 5 → 6 | `review_findings` | All four-pass outputs, resolution status per finding, blocking vs non-blocking, waivers requested |
| 5 → 4 (rework) | `blocking_findings` | Subset of review findings requiring code change before commit |
| 6 → END | `commit_record` | Commit hash, artifacts updated, session log entry, ROADMAP delta |

### Where skills, hooks, and subagents activate

These three mechanisms are independent — they fire on different signals.

- **Skills** activate in Stage 3 (Plan with Governance) and again in Stage 5 (Four-Pass Review) when review subagents apply their rules. Skill activation is *content-driven*: skills self-determine applicability via `applies-when` conditions evaluated against the scope from Stage 2.
- **Hooks** fire on Claude Code's event lifecycle, *independently* of which workflow stage is active. `PreToolUse` fires every time a tool call is attempted, whether in Stage 1 reading or Stage 4 editing. A given workflow invocation typically fires dozens of hook events.
- **Subagents** dispatch at specific stage points based on change tier (see §5). The orchestrator (main agent) decides dispatch; subagents return structured output the orchestrator aggregates.

The conceptual separation matters: hooks enforce invariants the workflow stage doesn't know about; skills enforce rules the workflow stage applies; subagents do focused work the orchestrator delegates.

---

## §3 Per-Stage Specifications

*[Forthcoming — Phase 3 commit 2.](docs/phase-3-plan.md#5-implementation-order)*

This section specifies, for each of the six stages: inputs, operations (with mode and tier conditionals), outputs, skill activation points (referencing §4 schemas), hook integration points (referencing §6 contracts), subagent dispatch points (referencing §4 schemas), and failure modes. Six subsections, ~65 lines each.

Bookmarked here for navigability. Commit 1 lands the contracts and tables this section depends on; commit 2 lands the per-stage spec itself.

---

## §4 Subagent Output Schemas

Per `DEC-2026-05-17-003` Clause 3, seven subagent roles produce structured JSON output. This section defines those schemas in TypeScript-style interface notation (per Phase 3 Checkpoint 1 Decision B — readable for human implementers; mechanically translatable to JSON Schema if Phase 11 needs runtime validation).

All schemas assume strict mode: unknown fields are an error; missing required fields are an error.

### Cross-cutting types

These types appear in multiple role outputs.

```typescript
type Severity = "critical" | "high" | "medium" | "low";

type Citation = {
  source: string;            // e.g., "OWASP ASVS 5.0", "NIST SP 800-63B"
  rule_id: string;           // e.g., "V6.2.2", "§5.1.1.2"
  rule_text?: string;        // Verbatim or paraphrased; included when concise
};

type Location = {
  file: string;              // Absolute or repo-relative path
  line_start: number;
  line_end: number;
};

type Finding = {
  id: string;                // Stable identifier within this run, e.g., "F-014"
  severity: Severity;
  citation: Citation;
  plain_language_impact: string;  // What this means in practice; per CLAUDE.md §1
  location: Location;
  description: string;       // What the finding is (the rule violation in this context)
  remediation: string;       // What to do about it (concrete next action)
  subagent_attribution: SubagentRole;  // Which subagent surfaced this (set by orchestrator)
};

type SubagentRole =
  | "researcher"
  | "implementer"
  | "code_reviewer"
  | "security_auditor"
  | "red_team"
  | "holistic_reviewer"
  | "verifier";

type ReviewPass = {
  spec_compliance: { matches: boolean; deviations?: string[] };
  quality: { passes: boolean; reasoning: string };
};
```

The `Finding` type is the canonical finding shape per `CLAUDE.md` §11 severity model. Review subagents produce `Finding[]`; the orchestrator deduplicates and aggregates.

### Role: Researcher

Dispatched from Stage 1 for Large-tier changes to investigate one aspect of the codebase or project artifacts.

```typescript
type ResearcherInput = {
  question: string;              // What to investigate
  scope_hints: {
    paths?: string[];            // Suggested files/directories to focus on
    keywords?: string[];         // Symbols, terms to grep for
    related_decisions?: string[]; // DEC-IDs the orchestrator thinks may matter
  };
  budget: { max_files_read: number; max_subagent_dispatches: 0 };  // Researchers don't spawn other subagents
};

type ResearcherOutput = {
  question: string;              // Echo for traceability
  findings: {
    relevant_files: { path: string; why_relevant: string }[];
    prior_decisions: { dec_id: string; how_it_constrains: string }[];
    related_logs: { log: "ERROR-LOG" | "VENDOR-LOG" | "WAIVER-LOG"; entry_id: string; relevance: string }[];
    roadmap_position?: { phase: string; milestone: string };
    patterns_observed: string[];  // Code patterns currently in use that the orchestrator should respect
  };
  unanswered: string[];          // What the Researcher could not determine
  confidence: "high" | "medium" | "low";  // Self-assessed; low means "verify before using"
};
```

**Worked example.** Input: `{ question: "What authentication middleware patterns exist in this codebase?", scope_hints: { paths: ["middleware/", "auth/"] } }`. Output flags `middleware/auth.ts` and `auth/session.ts` as primary, notes `DEC-2025-XX-012` (chose JWT over session cookies for stateless backend), confirms no related log entries, returns `confidence: "high"`.

### Role: Implementer

Dispatched from Stage 4 when Large-tier work decomposes into discrete tasks (typically 2–5 implementers in parallel for independent file changes).

```typescript
type ImplementerInput = {
  task: string;                  // What to implement
  scope: {
    files_in_scope: string[];    // Files this Implementer may modify
    files_read_only: string[];   // Files this Implementer may read for context but not modify
    out_of_scope: string[];      // Files this Implementer must not touch
  };
  governance_plan: {
    skills_to_apply: { name: string; rule_ids: string[] }[];
    anti_patterns_to_avoid: string[];
    test_requirements: string;
  };
  budget: { max_files_written: number; max_subagent_dispatches: 0 };
};

type ImplementerOutput = {
  task: string;                  // Echo
  diff: {
    files_modified: { path: string; lines_added: number; lines_removed: number }[];
    files_created: string[];
    files_deleted: string[];
  };
  skill_rules_applied: { skill: string; rule_id: string; where: Location }[];
  tests_added: { path: string; test_count: number }[];
  ai_generated_portions: Location[];  // Per §16; flags regions for Verifier
  deviations_from_plan: string[];     // What didn't go as scoped, and why
  blockers_encountered: string[];     // What stopped progress, if anything
};
```

**Worked example.** Input: implement `validateSessionToken()` in `auth/session.ts`. Output reports 47 lines added across 1 file, 3 unit tests in `auth/session.test.ts`, applies `security-iam-sessions` rules `R-3.1` (cryptographically random session IDs) and `R-3.4` (short expiry), flags lines 23–41 as AI-generated for Verifier exercise.

### Role: Code Reviewer

Phase 1 of four-pass review. Evaluates craftsmanship. Fresh context — does not share the Implementer's mental model.

```typescript
type CodeReviewerInput = {
  diff: ImplementerOutput["diff"];
  governance_plan: ImplementerInput["governance_plan"];
  scope: ImplementerInput["scope"];
};

type CodeReviewerOutput = {
  review_pass: ReviewPass;
  findings: Finding[];           // Craftsmanship findings: type safety, error handling, naming, anti-patterns, test coverage, scale-awareness, solo-maintainability
  positive_notes?: string[];     // Optional; patterns done well, worth preserving in future work
};
```

**Worked example.** Reviewing the Implementer's `validateSessionToken()` diff. Output: `review_pass.spec_compliance.matches = true`; `review_pass.quality.passes = false`; one Medium finding at `auth/session.ts:38` — error path swallows the underlying exception without context, violating CODE-QUALITY error-handling principle; remediation: rethrow with context using `Error.cause`.

### Role: Security Auditor

Phase 2 of four-pass review. Applies applicable security skills' rules.

```typescript
type SecurityAuditorInput = {
  diff: ImplementerOutput["diff"];
  governance_plan: ImplementerInput["governance_plan"];
  trust_boundaries_affected: string[];  // Identified in Stage 2 Scope
  data_flows: { source: string; sink: string; data_classification: string }[];
};

type SecurityAuditorOutput = {
  review_pass: ReviewPass;
  findings: Finding[];           // Security findings with citation per DEC-004
  skills_applied: string[];      // Which security skills evaluated; for telemetry
};
```

**Worked example.** Same `validateSessionToken()` diff. Output applies `security-iam-sessions` and `security-cryptography` skills; surfaces a High finding — session ID compared with `==` rather than constant-time equality, citing `OWASP ASVS 5.0 V3.4.1`; plain-language impact: timing side-channel could reveal valid session IDs to attackers measuring response latency.

### Role: Red Team

Phase 3 of four-pass review. Adversarial perspective.

```typescript
type RedTeamInput = {
  diff: ImplementerOutput["diff"];
  scope: ImplementerInput["scope"];
  trust_boundaries_affected: string[];
  attack_surface: string;        // Summary of what's reachable from outside the trust boundary
};

type RedTeamOutput = {
  review_pass: ReviewPass;
  findings: Finding[];           // Adversarial findings: injection, authz bypass, race conditions, business logic abuse, resource exhaustion, failure-mode exploitation
  scenarios_tested: { scenario: string; outcome: "exploitable" | "mitigated" | "out_of_scope" }[];
};
```

**Worked example.** Same `validateSessionToken()` diff. Output tests 4 scenarios — replay-after-expiry (mitigated), token-substitution-from-another-user (mitigated), race-condition-on-renewal (`exploitable`: window between expiry check and renewal allows brief unauthorized acceptance), brute-force-id-guessing (mitigated by random-128-bit IDs). One High finding on the race condition with concrete reproduction steps.

### Role: Holistic Reviewer

Phase 4 of four-pass review. TGF-specific integration verification (the value TGF adds over generic review).

```typescript
type HolisticReviewerInput = {
  diff: ImplementerOutput["diff"];
  governance_plan: ImplementerInput["governance_plan"];
  scope: ImplementerInput["scope"];
  roadmap_milestone: string;
  project_context_summary: string;  // From PROJECT-CONTEXT
  prior_decisions_in_area: { dec_id: string; summary: string }[];
};

type HolisticReviewerOutput = {
  review_pass: ReviewPass;
  findings: Finding[];           // Integration findings: spec compliance, codebase fit, architectural alignment, regression risk, forward compatibility, roadmap alignment, solo-maintainability, decision documentation
  roadmap_delta: { milestone_advanced: boolean; new_dependencies?: string[]; slip_risk?: string };
  decision_documentation_status: { decisions_made_in_implementation: string[]; documented_in_DECISIONS: boolean };
};
```

**Worked example.** Same `validateSessionToken()` diff. Output: milestone "authentication hardening" advanced; codebase-fit confirmed (matches existing middleware patterns in `middleware/auth.ts`); one Medium finding — implementation chose JWT verification approach not documented in DECISIONS.md despite being a non-trivial architectural choice (remediation: add DEC-NNN capturing the JWT-vs-session-cookie reasoning); forward-compatibility: no concerns.

### Role: Verifier

Empirically exercises AI-generated code per `CLAUDE.md` §16. Dispatched conditionally when `ImplementerOutput.ai_generated_portions` is non-empty.

```typescript
type VerifierInput = {
  diff: ImplementerOutput["diff"];
  ai_generated_portions: Location[];
  test_command: string;          // How to run the project's test suite
  scope: ImplementerInput["scope"];
};

type VerifierOutput = {
  review_pass: ReviewPass;       // spec_compliance: did AI portions match the plan? quality: do they actually work?
  test_results: { passed: number; failed: number; failure_details?: string[] };
  edge_cases_exercised: { case: string; outcome: "pass" | "fail" | "skip" }[];
  plausible_but_wrong_patterns_checked: {
    pattern: "hallucinated_api" | "fabricated_signature" | "assumed_library_behavior" | "near_correct_syntax";
    location: Location;
    actual_behavior: string;
  }[];
  findings: Finding[];           // Findings specific to AI-generated regions
};
```

**Worked example.** Verifier exercises AI-generated lines 23–41 in `auth/session.ts`. Output: test results 14 passed / 1 failed; edge cases exercised include expired-token (pass), malformed-base64 (pass), missing-issuer-claim (fail — AI assumed `jose.decodeJwt()` validates issuer by default, which it does not); one Critical finding documenting the hallucinated-library-behavior pattern with remediation pointing to explicit `verifyIss` configuration.

### Schema discipline

Three rules govern subagent outputs:

1. **Subagent attribution preserved.** Per `ARCHITECTURE.md` §20, the orchestrator never claims a subagent's finding as its own. The `subagent_attribution` field on every `Finding` is set by the orchestrator and surfaces in user-facing aggregation.
2. **Two-stage spec/quality review enforced.** Every review role's output includes a `review_pass` object with both `spec_compliance` and `quality` evaluations. Both must pass for the review to return ✅. One passing while the other fails is a legitimate outcome — well-built wrong thing or well-spec'd broken thing.
3. **Failure modes are part of the contract.** Schemas include `blockers_encountered`, `unanswered`, `deviations_from_plan` so that incomplete or partial work surfaces rather than gets silently dropped.

---

## §5 Tier and Mode Scaling Tables

### Change tier scaling

Per `ARCHITECTURE.md` §19 and §20, change tier determines orchestration depth.

| | Trivial | Small | Medium | Large |
|---|---|---|---|---|
| **Examples** | Typo, comment, formatting | Single-function bug fix, no trust boundary change | Multi-file feature, no architectural change | New feature, architectural change, trust boundary modification |
| **Stages active** | 4, 5 (light), 6 | 1–6 (light) | 1–6 (full) | 1–6 (full + decomposition) |
| **Stage 1 subagents** | none | none | none | 1–3 Researchers in parallel |
| **Stage 4 subagents** | none | none | none | 2–5 Implementers in parallel (when work decomposes) |
| **Stage 5 subagents** | none (inline by orchestrator) | Code Reviewer + Holistic Reviewer | Code Reviewer + Security Auditor + Red Team + Holistic Reviewer | All four + Verifier (if AI-generated portions present) |
| **Review depth** | Code review only (inline) | Phase 1 + Phase 4 | All 4 phases standard depth | All 4 phases + extra red team weight |
| **Skills evaluated** | Always-on only | Always-on + path-matched skills | Path-matched + import-matched + operation-matched skills | Full evaluation including data-flow-matched skills |
| **Logging required** | Commit message | Commit + session log entry | Commit + session log + ROADMAP delta | Commit + session log + ROADMAP delta + DECISIONS entry (if architectural) + SCHEMA-HISTORY (if schema-affecting) |

### Project mode scaling

Per `ARCHITECTURE.md` §15, project mode determines what skills are eligible to evaluate and what review emphasis applies.

| | Exploration | Prototype | Building (default) | Hardening | Maintenance |
|---|---|---|---|---|---|
| **Skill catalog gated** | Always-on only by default | Always-on + core security (input validation, output encoding, secrets, basic auth) | Full skill catalog (per applies-when conditions) | Full skill catalog | Full skill catalog |
| **Stage emphasis** | Stages 1–2 (Research, Scope) primary; Stage 3 minimal | Stages 1–4 standard; Stage 5 light | All stages standard | Stage 3 emphasizes threat modeling; Stage 5 emphasizes adversarial perspective | Stage 3 emphasizes regression risk; Stage 5 emphasizes forward compatibility |
| **Stage 5 review focus** | Code review + light holistic | Code review + Security Auditor (core only) + Holistic | All four phases | All four phases + extra Red Team weight | All four phases + extra Holistic weight |
| **Waiver bar** | Low (exploration findings flagged for re-evaluation at promotion) | Standard | Standard | High (justification required; revisit date mandatory) | Standard with regression-prevention emphasis |
| **BASELINE-AUDIT cadence** | N/A | At promotion | At promotion; quarterly review | Quarterly | Annual + at major architectural change |

### Composition rule

When tier and mode both apply (always the case), mode gates skill *catalog* and review *emphasis*; tier scales *orchestration depth* and *review breadth* within whatever skills the mode allows.

Examples:

- **Medium tier in Exploration mode:** Stage 5 dispatches Code Reviewer + Holistic Reviewer, but the Security Auditor doesn't fire because Exploration mode doesn't load detailed security skills. The two reviewers run their full two-stage spec/quality pass.
- **Small tier in Hardening mode:** Stage 5 dispatches Code Reviewer + Holistic Reviewer (tier scaling). The Code Reviewer's `review_pass.quality` evaluation gets extra weight on regression risk because mode emphasizes adversarial perspective; this surfaces as more findings, not as additional subagents.
- **Large tier in Maintenance mode:** Full orchestration (Researchers + Implementers + all four reviewers + Verifier), but Stage 3 governance plan emphasizes regression checks; Stage 5 Holistic Reviewer gets extra weight on forward compatibility.

The composition rule prevents over-orchestration in light modes (Exploration's Medium-tier change doesn't pay for Security Auditor it can't usefully run) and under-rigor in heavy modes (Hardening's Small-tier change still gets adversarial weight in the review it does run).

---

## §6 Hook Integration Contracts

Hooks are specified per Claude Code event (Decision C: per-event primary structure with purpose cross-reference table). Each contract names: TGF purpose, stdin fields TGF relies on (beyond Claude Code's defaults), expected exit semantics, expected stdout, and mode profiles that invoke this hook.

### Hooks by purpose (cross-reference)

| Purpose | Events used | Universal? |
|---------|-------------|------------|
| **Safety** — prevent destructive operations | `PreToolUse` (matches `Bash(git ...)`, `Bash(rm ...)`, database tool calls) | Yes — always active |
| **Workflow** — enforce session/commit discipline | `SessionEnd` (session log entry), `PreToolUse` (matches `Bash(git commit ...)` for test verification), git pre-commit hook | Mode-gated (Prototype+) |
| **Governance** — log security-relevant operations, detect framework integrity changes | `PostToolUse`, `FileChanged`, `ConfigChange` | Mode-gated (Building+) |
| **Telemetry** — record per-session data | `SessionStart`, `SessionEnd`, `SubagentStart`, `SubagentStop`, `PostToolUse` | Active when telemetry enabled |
| **TGF state lifecycle** | `SessionStart` (init `.tgf/state/sessions/{session_id}.json`), `SessionEnd` (cleanup) | Always active |

### TGF context injection mechanism (per DEC-006)

`project_mode`, `change_tier`, and `current_stage` live in `.tgf/state/sessions/{session_id}.json` per `DEC-2026-05-19-006`. Hooks read this file at fire time. The `session_id` available in every hook's stdin JSON keys the file lookup.

**Phase 3 Step 1 verification (2026-05-19):** the Claude Code Hooks reference confirms there is no built-in hook-to-hook state mechanism. File-based session-keyed state is the only documented path. Environment variables via `CLAUDE_ENV_FILE` are an adjacent mechanism but flow only to subsequent Bash tool invocations, not to other hooks; TGF may use this complementarily for exposing `TGF_PROJECT_MODE` to user-run shell commands, but the primary mechanism is the session state file.

Pseudocode for hooks reading TGF context:

```bash
# In any .claude/hooks/<EventName>/NN-tgf-aware.sh script:
STDIN=$(cat)
SESSION_ID=$(echo "$STDIN" | jq -r '.session_id')

# IMPORTANT: validate session_id before using in path construction.
# Even though Claude Code controls the value, defense-in-depth: reject any
# session_id that contains characters outside [A-Za-z0-9_-] to prevent
# path traversal if the upstream contract ever changes.
if ! [[ "$SESSION_ID" =~ ^[A-Za-z0-9_-]+$ ]]; then
    echo '{"systemMessage": "TGF: invalid session_id format; skipping state load"}' >&2
    exit 0  # Fail open for context-loading hooks; closed for safety-critical ones
fi

STATE_FILE=".tgf/state/sessions/${SESSION_ID}.json"

if [ -f "$STATE_FILE" ]; then
    PROJECT_MODE=$(jq -r '.project_mode' "$STATE_FILE")
    CHANGE_TIER=$(jq -r '.change_tier // "unknown"' "$STATE_FILE")
fi
```

Phase 12 hook scripts should factor the validation + state load into a shared helper (`.claude/hooks/lib/load-tgf-context.sh`) rather than duplicating per script.

### Output schema (richer than ARCHITECTURE.md §18 documented)

Phase 3 Step 1 research surfaced that `PreToolUse` hooks can return a richer `hookSpecificOutput` object beyond exit-2 blocking:

```typescript
type PreToolUseHookOutput = {
  // Universal fields (any hook):
  continue?: boolean;          // false stops Claude entirely
  stopReason?: string;
  suppressOutput?: boolean;
  systemMessage?: string;

  // PreToolUse-specific:
  hookSpecificOutput?: {
    hookEventName: "PreToolUse";
    permissionDecision?: "allow" | "deny" | "ask" | "defer";
    permissionDecisionReason?: string;   // Surfaced to user when "deny" or "ask"
    updatedInput?: object;                // Modified tool_input the tool actually receives
    additionalContext?: string;           // Injected into Claude's context (10k char cap)
  };
};
```

TGF's three universal hooks use `permissionDecision: "deny"` with `permissionDecisionReason` for clean user-facing blocks, falling back to exit 2 + stderr only for unrecoverable hook script errors. The richer schema improves user UX over the exit-2 path.

**Phase 12 verification note:** Phase 3 Step 1 research found the value `permissionDecision: "defer"` listed in Claude Code's hook output schema but without explicit semantics in the spot-checked documentation. Phase 12 implementers should re-verify the canonical Claude Code Hooks reference for what `"defer"` does (most likely: punts the decision to Claude Code's normal permission flow rather than the hook explicitly deciding) before relying on it. TGF's current §6 contracts use only `"allow"` and `"deny"`; `"ask"` and `"defer"` remain available for future use once semantics are confirmed.

### Per-event contracts

#### `SessionStart`

**Purpose:** initialize TGF session state file; load recent session logs into context; verify framework integrity (CLAUDE.md, ARCHITECTURE.md, DECISIONS.md present and parseable); inject project mode summary into Claude's context.

**Relied-upon stdin fields:** `session_id`, `cwd`, `source` (one of `"startup"`, `"resume"`, `"clear"`, `"compact"` — TGF behavior differs per source; `"resume"` should load existing state, not overwrite).

**Expected exit:** 0 (allow). Non-zero exits at session start are blocking and surface as user errors.

**Expected stdout:** JSON with `additionalContext` field containing project mode summary + recent session log excerpt. Optionally `systemMessage` for user-visible status.

**Mode profiles:** active in all modes (state initialization is universal).

#### `SessionEnd`

**Purpose:** generate session log entry capturing topics discussed, decisions made, ROADMAP deltas, findings logged; clean up `.tgf/state/sessions/{session_id}.json`; emit telemetry summary.

**Relied-upon stdin fields:** `session_id`, `cwd`.

**Expected exit:** 0. SessionEnd hook failures should never block session close; non-zero is logged and ignored.

**Expected stdout:** none required.

**Mode profiles:** active in Prototype+ modes (Exploration mode skips session log discipline as too much friction for figuring-out-what-to-build work).

#### `PreToolUse`

**Purpose:** enforce three universal safety hooks (block-dangerous-git, block-secrets-commit, block-destructive-db); enforce workflow gates (tests-pass-before-commit in Building+ mode); record tool dispatch for telemetry.

**Relied-upon stdin fields:** `session_id`, `cwd`, `tool_name`, `tool_input`, `permission_mode`.

**Expected exit:** 0 (allow) or via richer schema (`hookSpecificOutput.permissionDecision`).

**Expected stdout:** for blocks, use `hookSpecificOutput.permissionDecision: "deny"` with `permissionDecisionReason` (preferred over exit 2 + stderr). For input modification (e.g., adding `--no-color` to a command), use `hookSpecificOutput.updatedInput`. For `"ask"` (defer-to-user) cases, use `permissionDecision: "ask"` with `permissionDecisionReason` explaining what to confirm.

**Mode profiles:**

- Always active: `block-dangerous-git`, `block-secrets-commit`, `block-destructive-db`
- Prototype+: `verify-session-log-on-commit` (matches `Bash(git commit ...)`)
- Building+: `verify-tests-pass` (matches `Bash(git commit ...)`), `log-security-operations` (matches database tool calls, network tool calls)
- Hardening+: `verify-waiver-revisit-dates`

#### `PostToolUse`

**Purpose:** log security-relevant operations for telemetry and incident response; detect framework artifact modifications (CLAUDE.md, ARCHITECTURE.md, DECISIONS.md, skill files) and surface for review.

**Relied-upon stdin fields:** `session_id`, `cwd`, `tool_name`, `tool_input`, `tool_use_id`.

**Expected exit:** 0. PostToolUse blocks the post-tool reaction, not the tool itself (tool already ran); use sparingly. `decision: "block"` in stdout pattern available for cases where post-tool state warrants halting the workflow.

**Expected stdout:** none required for telemetry path; for framework-integrity findings, JSON with `systemMessage` flagging the change for user awareness.

**Mode profiles:** Building+ (Exploration and Prototype skip telemetry overhead).

#### `SubagentStart`

**Purpose:** record subagent dispatch for telemetry (per `ARCHITECTURE.md` §20 — subagent operations logged); inject TGF context into subagent's working environment (the same `.tgf/state/sessions/{session_id}.json` is read by the subagent if it dispatches its own hooks).

**Relied-upon stdin fields:** `session_id`, `agent_id`, `agent_type`.

**Expected exit:** 0.

**Expected stdout:** none required.

**Mode profiles:** Building+ (always logs in Hardening+ for adversarial-AI defense per `MITRE ATLAS` AI agent technique catalog).

#### `SubagentStop`

**Purpose:** record subagent completion + output summary for telemetry; aggregate subagent findings into the orchestrator's review aggregation buffer.

**Relied-upon stdin fields:** `session_id`, `agent_id`, `agent_type`.

**Expected exit:** 0.

**Expected stdout:** optional `decision: "block"` if the subagent produced critical findings the orchestrator should not silently aggregate (rare; use for fail-safe behavior).

**Mode profiles:** Building+.

#### `FileChanged`

**Purpose:** detect modifications to framework integrity files (`CLAUDE.md`, `docs/ARCHITECTURE.md`, `DECISIONS.md`, `docs/WORKFLOW.md`, `.claude/skills/**/SKILL.md`, `.claude/hooks/**/*.sh`); record changes for telemetry; flag unexpected changes for user attention.

**Relied-upon stdin fields:** `session_id`, plus event-specific path fields (per Claude Code Hooks reference; spot-check field name during Phase 12 implementation).

**Expected exit:** 0.

**Expected stdout:** for integrity changes, JSON with `systemMessage` flagging the change.

**Mode profiles:** Hardening+ (Building mode logs changes but doesn't actively flag; Hardening surfaces them for review).

#### `ConfigChange`

**Purpose:** alert on changes to `.claude/settings.json`, `.claude/hooks/profile.json`, or `.tgf/` configuration that affect framework behavior; require explicit user awareness for hook-profile changes.

**Relied-upon stdin fields:** `session_id`, plus event-specific path fields.

**Expected exit:** 0 (logging) or 2 (block, for changes that would disable safety hooks without explicit acknowledgment).

**Expected stdout:** JSON with `systemMessage` describing the config change.

**Mode profiles:** Building+ (with stricter block behavior in Hardening+).

### Three universal hooks — override semantics

The three always-active safety hooks (`block-dangerous-git`, `block-secrets-commit`, `block-destructive-db`) implement the hard-refusal severity level from `CLAUDE.md` §5. They use `permissionDecision: "deny"` by default. User override requires explicit acknowledgment per the §5 informed-confirmation pattern:

- The hook surfaces `permissionDecisionReason` describing the harm and the override path
- User responds with explicit acknowledgment (typed override command, not implicit "try again")
- Override is logged to `WAIVER-LOG` with timestamp, command attempted, override reason, and revisit date
- The hook re-fires on retry; the override mechanism honors the prior acknowledgment for that specific operation only (not blanket exemption)

This preserves §5's intent: the framework respects user authority but does not silently produce harmful operations.

---

## §7 Debugging Variant

*[Forthcoming — Phase 3 commit 2.](docs/phase-3-plan.md#5-implementation-order)*

This section specifies how the six stages reshape when work is debugging rather than building (per `CLAUDE.md` §3 final paragraph): Reproduce → Isolate → Hypothesize → Test → Root-Cause → Verify-Fix. Each debugging stage maps to a building stage; subagent dispatch differences are spelled out; termination criteria for debugging are explicit.

---

## §8 Worked Examples

*[Forthcoming — Phase 3 commit 2.](docs/phase-3-plan.md#5-implementation-order)*

Three end-to-end traces exercising the spec:

1. **Trivial:** typo fix in CLAUDE.md
2. **Medium:** authentication middleware refactor in a Next.js application
3. **Large:** new billing feature crossing trust boundaries (PII + payments + webhooks)

Each example traces: stages run/skipped, skills activated, subagents dispatched (with input/output), hooks fired (with stdin/stdout), artifacts updated, total findings count.

---

## §9 Reference

**Primary specifications:**

- `CLAUDE.md` §3 — operational workflow contract (the *what*); this document specifies the *how*
- `docs/ARCHITECTURE.md` §15 — mode-aware operation (§5 of this doc operationalizes)
- `docs/ARCHITECTURE.md` §18 — hook architecture (§6 of this doc operationalizes; richer output schema discovered in Phase 3 research documented in §6)
- `docs/ARCHITECTURE.md` §19 — token efficiency and cost-aware orchestration (§5 of this doc tier scaling derives from)
- `docs/ARCHITECTURE.md` §20 — agent orchestration role descriptions (§4 of this doc specifies the output contracts those roles produce)

**Architectural decisions operationalized:**

- `DECISIONS.md` `DEC-2026-05-17-003` Clause 2 — hook architecture (TGF context-injection portion superseded by DEC-006)
- `DECISIONS.md` `DEC-2026-05-17-003` Clause 3 — seven subagent roles (output schemas defined in §4 of this doc)
- `DECISIONS.md` `DEC-2026-05-17-005` — hook event taxonomy (PascalCase names matching Claude Code's actual events; §6 of this doc uses these)
- `DECISIONS.md` `DEC-2026-05-19-006` — TGF session state architecture (§6 of this doc uses `.tgf/state/sessions/{session_id}.json` per this ADR; Phase 3 Step 1 verification confirmed)

**External authoritative sources** (verified per `DEC-2026-05-17-004` Clause 1):

- Claude Code Hooks reference (current 2026) — verified Phase 2 (commit `92c9894`) and re-verified Phase 3 Step 1 (2026-05-19, surfaced richer `hookSpecificOutput` schema documented in §6)
- OWASP Top 10 for LLM Applications 2025 — `LLM01:2025` (prompt injection, applies to hook input untrusted-data discipline in §6), `LLM06:2025` (excessive agency, applies to subagent role scoping in §4)
- MITRE ATLAS v5.4.0 (February 2026) — agent-targeting techniques inform subagent telemetry hooks in §6
- NIST SP 800-218 v1.1 (SSDF) — two-layer verification discipline frames §6 hooks as the enforcement floor

**Comparative reference** (per `DEC-2026-05-17-004` Clause 6 — informs design pattern, not rule-source):

- Superpowers framework — two-stage spec-then-quality review pattern in §4 (every review subagent's `review_pass` object reflects this pattern)

**Generated during Phase 3:**

- `docs/phase-3-plan.md` — Phase 3 implementation plan with Checkpoint 1 decisions A–E resolved (committed for transparency per Phase 2 Decision 2)

---

*This document is Phase 3, commit 1: §1, §2, §4, §5, §6, §9 land. §3 (Per-Stage Specifications), §7 (Debugging Variant), and §8 (Worked Examples) ship in Phase 3 commit 2 per Checkpoint 1 Decision E.*
