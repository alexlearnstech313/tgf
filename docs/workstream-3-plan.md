# Workstream 3 Plan — Four Review Agents Operationalized

> **Status:** v1 draft pending Checkpoint 1. Authored 2026-05-25 immediately following WS2 closeout (commit `609c4e6`).
>
> **Scope:** flesh out the four Phase 4 agent scaffolds (`agents/code-reviewer.md`, `security-auditor.md`, `red-team.md`, `holistic-reviewer.md` — committed `d4abbb0`) into operational subagents with rich personas + skill preloading + tool-permission restrictions + scoped activity logs. Per `docs/framework-hardening-plan.md` §3.3 + the WS3 amendment landed during WS2 closeout (planning-hygiene in `609c4e6`).
>
> **Boundary:** WS3 ships operational agents. It does NOT retroactively re-review Phase 4-6 work against the operational agents (that's WS4). It does NOT remediate gaps the agents would find on existing work (that's WS5).

---

## §1 Purpose and Scope

### §1.1 What this plan covers

Operationalize the four review subagents that perform Stage 5 of the TGF workflow. The current state: Phase 4 (`d4abbb0`) shipped four 20-25 line scaffolds with minimal frontmatter (`name`, `description`, `skills: [tgf:<skill>]`, `memory: project`) and ~3 paragraphs of body text. The scaffolds reference WORKFLOW.md §4 for output contracts and CLAUDE.md §3 Stage 5 for the four-pass model, but they don't yet carry the persona depth, materials breadth, or boundary discipline to function as independent reviewers.

WS3 closes that gap by authoring each agent's full operational definition:

1. **Persona** — voice + instincts + mindset + severity gradient (per the design notes in `docs/four-agents-design-notes.md`, refined where over-broad)
2. **Authoritative materials** — what each agent cites, with the live-fetch-vs-reference discipline matched to source availability
3. **Preloaded skills** — concrete `skills:` frontmatter list per role, with forward-reference notes for Phase 6+ skills not yet shipped
4. **Tool-permission restrictions** — concrete `tools:` array per role enforcing least-privilege subagent design (added as WS3 deliverable during WS2 closeout planning-hygiene)
5. **Scoped activity logs** — structured JSON capture of each subagent dispatch (input context hash, skills loaded, duration, findings count + summary) written by the orchestrator to `.tgf/state/agent-activity/<role>/<dispatch_id>.json` (added as WS3 deliverable during WS2 closeout planning-hygiene)
6. **Output schema cross-reference** — each agent.md references its canonical TypeScript schema in WORKFLOW.md §4 by anchor

### §1.2 What this plan does NOT cover

- **Retroactive review of Phase 4-6 work against the operational agents.** That's WS4. WS3's smoke tests dispatch agents against existing commits *to validate the agents themselves work*, not to produce remediation findings on the reviewed commits.
- **Remediation of gaps the agents find on existing work.** That's WS5.
- **Verifier and Researcher subagents.** WORKFLOW.md §4 specifies seven subagent roles; WS3 builds out only the four review-pass agents. Verifier (AI-output empirical exercise per CLAUDE.md §16) and Researcher (Stage 1 dispatch per WORKFLOW.md §3) are scaffolded separately and out of scope for WS3.
- **Orchestrator agent expansion beyond current state.** `agents/tgf-orchestrator.md` already exists from Phase 4. WS3 does not modify orchestrator persona; it modifies what the orchestrator dispatches to.
- **JSON-schema enforcement hooks for subagent output.** WORKFLOW.md §4 TypeScript schemas are spec; WS3 ships agents that produce output matching those shapes, but automated schema validation (block when output deviates) is deferred to Phase 12 hook library.
- **Quarterly-refresh discipline for agent materials.** Per design notes §7, this is `framework-health` meta-skill territory (Phase 11). WS3 ships agents with current-as-of-2026-05-25 materials; refresh discipline lands later.
- **Agent dispatch from outside Stage 5.** Security-Auditor activation at M8 verification gates (per RESEARCH-SECURITY §5.5) is noted in the agent's description but the mechanical integration is deferred — Stage 5 dispatch is WS3's primary surface.

### §1.3 Why this work matters

Per `docs/framework-hardening-plan.md` §3.3 + §4.1, WS3 sits between WS2 (methodology) and WS4 (audit) for a specific reason: the audit's quality depends on having operational agents available to perform it. Orchestrator-played four-pass review reproduces the exact blind spot that caused the commit-4/12 incident (`b67765e` → `73d025d`) — the orchestrator authored the work AND reviewed it, so the §2 Sources discipline violation survived the review pass that should have caught it.

WS3 produces independent reviewers that operate from fresh context with restricted tool permissions, removing the structural ability of any single context (orchestrator or otherwise) to self-review its own work in the high-stakes phases of the workflow.

Phase 6 commits 5/12 through 12/12 — covering secrets-management, IAM-authentication, IAM-sessions, IAM-authorization, database, logging, supply-chain — all touch trust boundaries and credential handling. They are the work that benefits most from real adversarial review (red-team) and real spec-compliance review (holistic). WS3 is the gate that lets Phase 6 resume under the discipline the hardening detour was triggered to establish.

---

## §2 Prerequisites

| Prerequisite | Status | Notes |
|---|---|---|
| WS1 (research-security infrastructure) operational | ✅ Complete `dc2b294` | M1-M19 hooks active; agents' WebFetch operations protected from session start. |
| WS2 (WORKFLOW-V2 methodology) complete | ✅ Complete `609c4e6` | Citation chain target defined; Stage 3 methodology cited. Agents reference WORKFLOW.md §3 + §4 for their operational context. |
| Phase 4 agent scaffolds present | ✅ Committed `d4abbb0` | Four .md files at `agents/`. WS3 builds these out; doesn't author from scratch. |
| Design notes committed as starting input | ✅ `docs/four-agents-design-notes.md` (502 lines, `dc2b294`) | Personas + materials lists + boundary discipline. WS3 refines where over-broad. |
| `docs/four-agents-design-notes.md` read | (read at plan-draft time, 2026-05-25) | Treated as design draft per the document's own §502 closing note. |
| WORKFLOW.md §4 TypeScript output schemas present | ✅ Committed Phase 3 | Each agent.md cross-references its canonical schema by §4 anchor. |
| `skills:` frontmatter mechanism specified | ✅ DEC-2026-05-19-007 | Anthropic-native preload. Used in current scaffolds. |
| Tool-permission restrictions added as WS3 deliverable | ✅ `609c4e6` ROADMAP amendment | Concrete per-role mapping below in §5. |
| Scoped activity logs added as WS3 deliverable | ✅ `609c4e6` ROADMAP amendment | Concrete schema + storage below in §6. |

No external dependencies. All WS3 inputs are local to the repo. WebFetches during build are limited to verifying live OWASP / NIST / MITRE / CIS source URLs the agents will cite (re-using research-log entries already verified during WS2 Step 2 where applicable).

---

## §3 Approach Decisions (Meta — Resolve at Checkpoint 1)

Thirteen decisions to lock before build. Each is structural — locking these prevents mid-build re-litigation. Persona-content refinements during build are expected per design notes §502 and are not Checkpoint 1 decisions.

### Decision A — Persona depth lives in `agents/<role>.md` body

**Recommendation:** Author full persona content (voice, instincts, mindset, severity gradient, what-they-call-out, what-they-are-not) into each `agents/<role>.md` file body. Claude Code passes the .md content as the subagent's system prompt; richer body = stronger operational persona at dispatch.

**Alternative considered:** Keep agent .md files terse; let orchestrator inject persona at dispatch time via context payload. Rejected — couples persona to orchestrator behavior and weakens the file-level operational definition.

### Decision B — Authoritative materials handled by source-tier hierarchy

**Recommendation:** Apply the same live-cite-vs-reference discipline WS2 established for skill files (per `DEC-2026-05-17-004` and WORKFLOW.md §2.5 source-tier hierarchy). Specifically:

- **Tier 1/2 living-publication sources** (OWASP ASVS, NIST SP, MITRE ATT&CK, CIS Controls) — live-cited at publication+section level; URLs registered in `source-registry.json` so agents can WebFetch under M15 allow-list if needed
- **Tier 1 stable publications** (NIST FIPS, RFCs, ISO 27001/27002 references via CSF IR crosswalk) — cited by reference at publication level; no live fetch required for verification
- **Foundational texts** (Brooks, Ousterhout, McConnell, Fowler, Feathers, Meadows, Kleppmann, etc.) — cited by author+title+edition+year, no fetch (paywalled and stable). Same precedent as Phase 5 UI-CRAFT skill which cited Apple HIG / Material Design 3 by reference

### Decision C — Tool-permission restrictions per role

**Recommendation (original):** Concrete `tools:` array in each agent's frontmatter per the matrix in §5. All four review agents are read-only (`Read`, `Grep`, `Glob`) plus `WebFetch` for the two roles whose materials may require live source verification (Security Auditor, Red Team). No `Write`, no `Edit`, no `Bash` for any of the four. This is the cryptographic-signature-free enforcement of the trust-chain intuition Alt surfaced during WS2 closeout planning — least-privilege subagent design enforced by the Claude Code agent definition mechanism, not by post-hoc signature verification.

> **Note:** The original "no Bash for any of the four" position was amended at Checkpoint 1 — Red Team now gets `Bash` for defensive tooling only. See the Checkpoint 1 amendment paragraph below for scope and governance. The amended §5 matrix is canonical.

**Alternative considered:** Permit `Bash` for Red Team to run defensive tooling (e.g., grep over commits for adversary-TTP patterns). Initially rejected — the Red Team agent does NOT execute exploits; it identifies defensive gaps via citation. Bash adds attack surface without proportionate review value.

**Checkpoint 1 amendment (2026-05-25):** Original rejection overridden per Alt's call. `Bash` added to Red Team's `tools:` array to enable defensive tooling (commit-history grep for TTP patterns, log inspection during attack-surface analysis, sandboxed command execution for hypothesis testing). The boundary discipline section in §4.3 remains non-negotiable: Bash is for *defensive analysis*, not exploit execution. The orchestrator-played four-pass review during WS3 build (and the Stage 5 Phase 3 dispatch pattern in production) holds the boundary; Bash is a capability, not a license. The §9 Build Step 4 tool-restriction sanity check is amended to also confirm Red Team uses Bash only for defensive operations in its smoke-test transcripts.

### Decision D — Activity log schema + storage location

**Recommendation:** Structured JSON per dispatch at `.tgf/state/agent-activity/<role>/<dispatch_id>.json`. Per-project storage (matches the .tgf/state/ pattern WS1 established). Schema specified in §6. Logs are gitignored by default per the .tgf/state/ pattern (per-machine state; not committed).

**Alternative considered:** Centralized at `~/claude-memory/` for cross-project analysis. Rejected per WS2 closeout planning-hygiene (`docs/parking-lot.md` entry — pivot cost too high; cross-project analysis solvable later with an aggregation tool that reads per-project state).

### Decision E — Activity log write mechanism: orchestrator writes, not subagent

**Recommendation:** Orchestrator captures subagent output (the TypeScript-typed JSON per WORKFLOW.md §4) on subagent return and writes the activity-log entry. Subagent never writes to disk; this is consistent with tool restrictions in Decision C (no Write tool for review agents).

**Alternative considered:** Subagent writes directly. Rejected — conflicts with the tool restrictions; introduces possibility of subagent log tampering.

**Alternative considered:** `PostToolUse` hook on subagent invocation. Rejected — Claude Code's hook contract per `claude-code-guide` doesn't cleanly expose subagent output to hooks at this granularity. Orchestrator-write is the simplest path.

### Decision F — Skill preload list per role with forward-reference notes

**Recommendation:** Concrete `skills:` frontmatter listing only skills that currently exist. Each agent's body text includes a "Future skills" sub-section noting which Phase 6+ skills will be added to the `skills:` list when those skills land. This prevents `skills:` referencing nonexistent files (which would fail at session start) while preserving the design notes' broader intent.

Per current state (Phase 4-5 complete; Phase 6 at 4/12):

- **Code Reviewer:** `code-quality`, `testing`, `continuity`
- **Security Auditor:** `security-core`, plus the four shipped Phase 6 skills (`security-input-validation`, `security-output-encoding`, `security-error-handling`, `security-cryptography`)
- **Red Team:** `security-core`, plus the four shipped Phase 6 skills
- **Holistic Reviewer:** `continuity`, `code-quality`, plus `design`, `project-management`, `debugging`, `disagreement` from Phase 5

Forward-reference notes in each agent body capture what gets added when Phase 6 commits 5/12-12/12 land, when Phase 7 ships extended security skills, when Phase 8 ships AI-specific skills (including the `security-development-environment` skill added during WS2 closeout planning-hygiene).

### Decision G — Per-agent dispatch description must be rich enough for selective dispatch

**Recommendation:** Each agent's `description:` field (visible to the orchestrator at dispatch time) must include: (1) which Stage 5 phase the agent serves, (2) the agent's mental model question, (3) the change-tier and mode conditions that activate it, (4) the canonical schema reference. Current scaffold descriptions are concise but adequate; WS3 refines them as personas land.

### Decision H — Output schema validation deferred to Phase 12

**Recommendation:** WS3 ships agents that *produce* output matching WORKFLOW.md §4 TypeScript types but does NOT ship hooks that *enforce* the schema. The schemas are documented in agent.md cross-references. Hook-based enforcement (block when subagent output doesn't validate) is Phase 12 hook library work.

**Rationale:** Schema validation requires either runtime JSON validation in the orchestrator (which is itself a model context) or a hook that fires post-subagent. Both are tractable but neither is needed for WS3's primary deliverable (operational agents). Defer.

### Decision I — Smoke test approach: real commit + targeted synthetic diff

**Recommendation:** Two-layer validation:

1. **Real-commit smoke test.** Dispatch each agent against an existing TGF commit known to have specific characteristics — e.g., `73d025d` (Phase 6 commit 4/12, post-correction). Each agent's output is reviewed against expectation: does Code Reviewer surface craftsmanship-relevant findings? Does Security Auditor cite specific OWASP/NIST rule IDs? Does Red Team identify adversarial scenarios at the technique-ID level? Does Holistic Reviewer surface integration concerns?
2. **Targeted synthetic diff per agent.** Build a small diff that exercises each agent's domain specifically (e.g., a deliberate timing-side-channel comparison for Security Auditor + Red Team; a deliberate solo-maintainability red flag for Code Reviewer + Holistic; a deliberate roadmap drift for Holistic). Dispatch the agent; verify it catches the planted issue with the right severity and citation.

Both smoke tests are documented in §10. Output of smoke tests is committed as part of the closeout commit, NOT as a separate test artifact — the smoke-test transcripts inform whether the agent personas need refinement before sign-off.

### Decision J — Build sequence: one commit per agent + plan + closeout

**Recommendation:** Six commits total — plan (this document) + Checkpoint 1 clearance + four per-agent commits (code-reviewer, security-auditor, red-team, holistic-reviewer in order) + closeout commit (smoke tests + ROADMAP + framework-hardening-plan §3.3 status flip).

Per-agent commits keep each agent's persona/materials/skills/tools/log work bounded. Pairwise dependencies between agents are loose enough that order is mostly aesthetic (working from least-adversarial to most-integrative is the proposed order).

**Alternative considered:** Pair commits (code+holistic, security+red-team) to surface composition issues earlier. Rejected — per-agent commits give clean per-agent review boundaries and align with the design notes' per-agent structure.

### Decision K — Persona refinement during build is expected; structural shape locked at Checkpoint 1

**Recommendation:** Lock at Checkpoint 1:

- Section structure of each agent.md (frontmatter shape, body sections, cross-reference layout)
- Materials-handling discipline (Decision B)
- Tool-restriction matrix (Decision C / §5)
- Activity-log schema (Decision D / §6)
- Skill-preload lists (Decision F)
- Build sequence (Decision J)

Refine during build:

- Voice (the specific language and phrasing of the persona)
- Specific instincts (the "voice and instincts" bullets in each agent.md)
- Anti-pattern lists (the "what they call out" sections)
- Materials list trimming where the design notes are over-broad

Refinements are captured as plan-adjustment notes in commit messages and the WS3 session log, per Phase 4-5 precedent.

### Decision L — WORKFLOW.md §4 gets minimal cross-reference touch

**Recommendation:** Add a one-line cross-reference per role in WORKFLOW.md §4 pointing to `agents/<role>.md` for persona and materials. Schemas remain canonical in WORKFLOW.md §4. Agent files remain canonical for persona / materials / tool restrictions / skills. No content duplication.

### Decision M — Implementation of tool restrictions uses Claude Code's native `tools:` frontmatter

**Recommendation:** Per Claude Code's subagent definition mechanism, the `tools:` array in agent .md frontmatter restricts the subagent to the listed tools only. WS3 uses this native mechanism. No custom hook-based tool restriction needed.

**Verification step at Checkpoint 1:** confirm the `tools:` frontmatter behavior matches expectation via the `claude-code-guide` agent or Anthropic's documentation (one targeted question to claude-code-guide during Checkpoint 1 confirms current behavior).

**Verification outcome (2026-05-25, via claude-code-guide agent against Claude Code tools-reference docs, source `CLAUDE-CODE-DOCS`):**

- **Q1 — allow-list semantics:** Confirmed. `tools:` is a strict allow-list. Omitted = inherit all parent tools. `disallowedTools:` is the subtract-from-inherited alternate.
- **Q2 — canonical name strings:** Confirmed PascalCase exact (`Read`, `Grep`, `Glob`, `WebFetch`, `Bash`, `Edit`, `Write`, `Agent`). §5 matrix already uses correct casing.
- **Q3 — orchestrator-proxy:** **Undocumented / does not exist.** A restricted `tools:` array is a hard wall — the orchestrator cannot proxy a tool call on behalf of a child. Operational impact captured in §5 "Orchestrator-proxy pattern" below.
- **Q4a — parent permission cascade:** Confirmed. Subagent can't call a tool the parent doesn't have.
- **Q4b — `disallowedTools` precedence:** When both `tools:` and `disallowedTools:` name a tool, it's removed. WS3 uses `tools:` exclusively to avoid this footgun.
- **Q4c — malformed `tools:` arrays:** **Undocumented.** Docs explicitly direct empirical testing. Operational impact captured in §9 Build Steps 2/3/4/5 "tool-restriction sanity check" subtask below.

Decision M approved as written. The two implementation-pattern notes in §5 and §9 capture what the docs left undefined.

### Decision N — Review-fix-iterate loop discipline

**Recommendation:** Lock the operational loop between review-agent finding identification and Stage 6 commit. The four review agents are read-only (per Decision C), so the loop that closes findings runs through the orchestrator. Specifically:

- Each `Finding` returned by a review agent includes a structured `remediation` field per WORKFLOW.md §4 (already in the schema)
- Orchestrator applies the remediation directly (Small/Medium tier) or dispatches an Implementer subagent with the remediation as task input (Large tier with disjoint file scopes)
- Re-dispatch affected review agents on the corrected diff with **fresh context** — the prior dispatch is NOT resumed; the fresh context is the structural mechanism preventing the orchestrator's confidence in its own fix from contaminating the next review
- Max 3 review cycles per change before escalation to user
- Conflicting agent remediations (e.g., Security Auditor wants pattern A; Code Reviewer prefers pattern B) surface to user per WORKFLOW.md §3 Stage 3 failure-mode pattern — no silent agent-to-agent negotiation
- All review-cycle dispatches log to activity-log per §6 with sequential `timestamp_dispatched` for cross-cycle traceability

Full operational spec in §4.5.

**Alternative considered:** Allow review agents to apply their own remediations for trivial findings (typos, naming nits). Rejected — even trivial self-fix creates the author-and-judge pattern that WS3 exists to break. The orchestrator applying a fix the Code Reviewer surfaced is structurally different from the Code Reviewer fixing it itself, even if the resulting diff is identical.

**Alternative considered:** Mechanical hook enforcement (block Stage 6 commit when activity-log shows open findings without resolution). Rejected for WS3 — loop discipline is workflow-level in v1. Hook-based enforcement is a candidate for Phase 12 (already specified as `verify-findings-resolved` in ROADMAP Phase 12 Governance hook category).

---

## §4 Per-Agent Design Specifications

This section is the operational specification for what gets authored into each agent's .md file. Frontmatter shape + body sections + cross-references are locked at Checkpoint 1; specific persona content is authored during the per-agent build commit and may refine per Decision K.

### §4.1 Code Reviewer (`agents/code-reviewer.md`)

**Frontmatter:**
- `name: code-reviewer`
- `description:` rich enough for Stage 5 Phase 1 dispatch (mental model "is this craftsmanship good?", change-tier always-active, schema cross-ref to WORKFLOW.md §4)
- `tools: [Read, Grep, Glob]` (read-only; no Write, no Edit, no Bash, no WebFetch — code review evaluates the diff against preloaded skills + the codebase context the orchestrator provides)
- `skills: [code-quality, testing, continuity]`
- `memory: project`

**Body sections:**
1. Role statement (Phase 1 of four-pass review; what mental model applies)
2. Persona (20+ year senior engineer voice + instincts + mindset per design notes §2.1)
3. Severity gradient applied to craftsmanship findings (per CLAUDE.md §5 — light touch for style, standard advocacy for engineering quality)
4. What this agent calls out (non-exhaustive list per design notes §2.1)
5. Authoritative materials (Decision B discipline — Code Complete + Refactoring + Working with Legacy Code + Pragmatic Programmer + Philosophy of Software Design + Google Engineering Practices + ISO/IEC 25010:2023 + language-specific style guides + SOLID / GRASP / DRY-YAGNI-KISS)
6. Output contract (cross-reference to WORKFLOW.md §4 `CodeReviewerOutput` schema)
7. What this agent is NOT (per design notes §2.5)
8. Future skills (forward-reference per Decision F)

### §4.2 Security Auditor (`agents/security-auditor.md`)

**Frontmatter:**
- `name: security-auditor`
- `description:` rich enough for Stage 5 Phase 2 dispatch + M8 gate dispatch (mental model "did we follow the security rules?", change-tier conditions, schema cross-ref)
- `tools: [Read, Grep, Glob, WebFetch]` (WebFetch for live verification of OWASP / NIST / MITRE / CIS citations under M15 allow-list)
- `skills: [security-core, security-input-validation, security-output-encoding, security-error-handling, security-cryptography]` (forward-reference notes for security-iam-* / security-database / security-logging / security-secrets-management / security-supply-chain when Phase 6 5/12-12/12 lands; Phase 7 + Phase 8 skills when those land)
- `memory: project`

**Body sections:**
1. Role statement (Phase 2 of four-pass review)
2. Persona (national-security-grade infosec pro per design notes §3.1)
3. Severity gradient (hard refusal / strong advocacy / standard / light touch per CLAUDE.md §5)
4. What this agent calls out
5. Authoritative materials (Decision B discipline)
   - NIST publications (800-53, CSF 2.0, 800-37, 800-30, 800-61, AI 100-1, AI 100-2)
   - International standards (ISO 27001/27002/27005)
   - OWASP (ASVS 5.0, Top 10:2025, API Top 10, LLM Top 10, Mobile Top 10, Smart Contract Top 10, WSTG, MASVS)
   - Practical defense (CIS Controls v8.1, CIS Benchmarks, CWE/SANS Top 25, MITRE D3FEND)
   - Threat intel (MITRE ATT&CK, MITRE ATLAS, CISA advisories)
   - Compliance (PCI-DSS v4.0, HIPAA Security Rule, GDPR Art. 32, CCPA, FedRAMP, DoD STIGs)
   - Web3/crypto (OWASP Smart Contract Top 10, SCSVS, ConsenSys best practices, Ethereum Security Considerations) — flagged "when scope warrants"
6. Output contract (cross-reference to WORKFLOW.md §4 `SecurityAuditorOutput`)
7. Activation: Stage 5 Phase 2 AND M8 verification gates per RESEARCH-SECURITY §5.5
8. What this agent is NOT
9. Future skills (forward-reference)

### §4.3 Red Team (`agents/red-team.md`)

**Frontmatter:**
- `name: red-team`
- `description:` rich enough for Stage 5 Phase 3 dispatch (mental model "I am an attacker — how do I break this?", substantive changes only — not trivial)
- `tools: [Read, Grep, Glob, WebFetch, Bash]` (WebFetch for live verification of MITRE ATT&CK + threat-intel citations under M15; Bash for defensive tooling only — commit-history grep for TTP patterns, log inspection, sandboxed hypothesis testing; boundary discipline below governs use)
- `skills: [security-core, security-input-validation, security-output-encoding, security-error-handling, security-cryptography]` (forward-reference for Phase 7 threat-modeling / attack-surface / detection-monitoring when landed)
- `memory: project`

**Body sections:**
1. Role statement (Phase 3 of four-pass review)
2. Persona (penetration tester + threat researcher across the full attacker spectrum per design notes §4.1)
3. **Boundary discipline — explicit and prominent.** The red-team agent references adversary behavior as documented by defenders. It cites MITRE ATT&CK techniques at technique-ID level; references MITRE ATT&CK Groups at group-profile level; reads public attribution reports as primary sources; identifies defensive gaps relative to known TTPs. It does NOT generate offensive tooling, exploit code, or malware; does NOT reproduce operational attack details beyond what's necessary for defensive understanding; does NOT provide guidance for attacking specific real systems; does NOT cross from "this defense has a gap" to "here's how to exploit it."
4. What this agent calls out (defensive gaps relative to documented TTPs)
5. Authoritative materials (Decision B discipline)
   - Adversary knowledge bases (MITRE ATT&CK Enterprise/Mobile/ICS/Containers, ATT&CK Groups, MITRE ATLAS, Engenuity Center for Threat-Informed Defense)
   - Testing methodology (OWASP WSTG v4.2, API STG, MSTG, PTES, OSSTMM 3, NIST SP 800-115)
   - Intrusion models (Cyber Kill Chain, Diamond Model)
   - Public threat intel (Mandiant M-Trends, CrowdStrike GTR, Microsoft Threat Intelligence, Google TAG, CISA AA, Recorded Future, Flashpoint, Group-IB, Kaspersky GReAT) — cited at report-and-date level
   - Historical attacks at attribution-report level (SolarWinds, Colonial Pipeline, Log4Shell, MOVEit, LastPass)
6. Output contract (cross-reference to WORKFLOW.md §4 `RedTeamOutput`)
7. What this agent is NOT (per design notes §4.5)
8. Future skills (forward-reference)

### §4.4 Holistic Reviewer (`agents/holistic-reviewer.md`)

**Frontmatter:**
- `name: holistic-reviewer`
- `description:` rich enough for Stage 5 Phase 4 dispatch (mental model "does this fit the system across time and scale?", always-active for substantive changes, schema cross-ref)
- `tools: [Read, Grep, Glob]` (read-only; integration assessment doesn't require live source fetches — operates on diff + project artifacts + roadmap)
- `skills: [continuity, code-quality, design, project-management, debugging, disagreement]` (forward-reference for Phase 7 security-architectural-principles when landed)
- `memory: project`

**Body sections:**
1. Role statement (Phase 4 of four-pass review; the TGF-specific phase where the framework's unique value lives)
2. Persona (principal engineer 15+ years; systems-thinker; conceptual-integrity advocate per design notes §5.1)
3. The synthesizer role (per design notes §5.1 — what the holistic reviewer adds beyond the focused three)
4. What this agent calls out
5. Authoritative materials (Decision B discipline)
   - Conceptual foundations (Brooks Mythical Man-Month, Ousterhout Philosophy of Software Design, Alexander Pattern Language, Brooks No Silver Bullet)
   - Architecture + evolution (Ford/Parsons/Kua Building Evolutionary Architectures, Evans DDD, Kleppmann DDIA, Vernon IDDD)
   - Systems thinking (Meadows Thinking in Systems, Senge Fifth Discipline, Forrester Industrial Dynamics)
   - Scale (Google SRE Book, SRE Workbook, Forsgren et al. Accelerate, Kim et al. DevOps Handbook, Nygard Release It!)
   - Formal architecture (NIST SP 800-160 v1/v2, ISO/IEC/IEEE 42010:2022, TOGAF 10 selectively, Zachman Framework)
   - Cross-cutting (Hohpe/Woolf Enterprise Integration Patterns, Fowler PoEAA)
6. Stage 5 Phase 4 checks (per CLAUDE.md §3 Stage 5 Phase 4 — spec compliance, codebase fit, architectural alignment, regression risk, forward compatibility, roadmap alignment, solo-maintainability, decision documentation)
7. The §2 Sources traceability check (added post-commit-4/12 per RESEARCH-SECURITY design — the check that the original holistic-review pass missed)
8. Output contract (cross-reference to WORKFLOW.md §4 `HolisticReviewerOutput`)
9. What this agent is NOT (per design notes §5.5)
10. Future skills (forward-reference)

### §4.5 Review-Fix-Iterate Loop

The four review agents are read-only by design (per Decision C / §5). They produce structured `Finding[]` per WORKFLOW.md §4; they never modify code. The loop that closes findings between Stage 5 review and Stage 6 commit runs through the orchestrator:

**Step 1 — Stage 4 (Implement).** Orchestrator (Small/Medium tier) or Implementer subagent (Large tier with disjoint file scopes per WORKFLOW.md §3 Stage 4) authors the change with full Write/Edit/Bash tool access.

**Step 2 — Stage 5 (Review).** Orchestrator dispatches each applicable review agent per change-tier scaling rules (CLAUDE.md §3 Stage 5). Each agent gets fresh context, no author's-mind bias. Each agent returns `Finding[]` with a structured `remediation` field per the WORKFLOW.md §4 `Finding` type. Worked example: WORKFLOW.md:548 — *"...remediation: rethrow with context using `Error.cause`."*

**Step 3 — Findings triage.** Orchestrator categorizes returned findings per CLAUDE.md §11 resolution rule:

- **Actionable now:** orchestrator applies the `remediation` directly (Small/Medium tier) OR dispatches an Implementer with `remediation` as the task input (Large tier with disjoint file scopes).
- **Formally waived:** finding logged to `WAIVER-LOG` with rationale + revisit date.
- **Escalated out-of-codebase:** finding logged to `VENDOR-LOG` (e.g., Supabase dashboard config the reviewer flagged but that lives outside the repo).
- **Conflicting between agents:** if two review agents return contradictory remediations (e.g., Security Auditor wants constant-time comparison via library X; Code Reviewer prefers approach Y), orchestrator surfaces the conflict to the user per WORKFLOW.md §3 Stage 3 failure-mode pattern with both citations + plain-language impacts. User resolves; orchestrator does NOT silently pick.

**Step 4 — Re-dispatch on corrected diff.** After orchestrator applies fixes, the affected review agents are re-dispatched on the corrected diff. **Fresh context per dispatch — the prior dispatch is NOT resumed.** Fresh context is the structural mechanism preventing the orchestrator's confidence in its own fix from contaminating the next review pass.

**Step 5 — Iterate.** Repeat steps 3-4 until any of the following terminate the loop:

- All review agents return clean (no findings or only `positive_notes`)
- All remaining findings are formally waived (WAIVER-LOG) or escalated (VENDOR-LOG) per CLAUDE.md §11 resolution rule
- Iteration limit reached (see below)

**Step 6 — Stage 6 (Commit) only after termination.** Stage 6 cannot proceed while open findings exist without resolution. This is the discipline that closes the gap between "review found problems" and "we committed anyway."

#### Iteration limit

Max 3 review cycles per change. If findings persist after 3 cycles, escalate to user. Persistent findings after 3 cycles signal one of:

- The finding identification is wrong (false positive that keeps regenerating despite fixes)
- The remediation is wrong (orchestrator's fix doesn't address what the agent caught)
- The architecture needs revision (not a code-level fix; needs higher-tier rework or scope re-negotiation per WORKFLOW.md §3 Stage 2)

At escalation, orchestrator presents to the user: full history of review dispatches in the cycle, the finding(s) that persisted, attempted remediations, and a hypothesis for why the loop stalled. User decides: revise the architecture, accept the finding as a waiver, override the agent's judgment with rationale recorded, or terminate the change.

#### Activity log discipline

Each loop cycle's review dispatch produces its own activity-log entry per §6 schema. Cross-loop traceability comes from common `session_id` + sequential `timestamp_dispatched` across the cycle. Per-cycle entries support forensic reconstruction: *"finding F persisted across 2 cycles; remediation attempts were X and Y; ultimately resolved by approach Z."*

#### What this loop is NOT

- **NOT mechanically enforced via hooks in WS3.** The loop is workflow-level discipline. Phase 12 hook library may eventually add a `verify-findings-resolved` hook (already in ROADMAP Phase 12 Governance category); WS3 ships the loop as orchestrator-driven discipline, not hook-enforced.
- **NOT automated negotiation between agents.** Conflicts surface to the user. Two model contexts (agents) negotiating with each other reproduces the same blind-spot risk WS3 exists to mitigate.
- **NOT a substitute for stage gating.** Stage 5 does not enter Stage 6 with open findings. The loop is what closes findings, not a way to skip them.
- **NOT a license to ignore reviewer findings.** Disagreeing with a review agent's finding is legitimate; doing so silently is not. Override decisions get recorded in the cycle's activity log with rationale, same as waiver discipline per CLAUDE.md §5 (severity gradient applies to disagreement-with-agent same as disagreement-with-user-feedback).

---

## §5 Tool Restriction Matrix

| Agent | Read | Grep | Glob | WebFetch | Bash | Edit | Write |
|---|---|---|---|---|---|---|---|
| Code Reviewer | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ |
| Security Auditor | ✅ | ✅ | ✅ | ✅ (M15-gated) | ❌ | ❌ | ❌ |
| Red Team | ✅ | ✅ | ✅ | ✅ (M15-gated) | ✅ (defensive only) | ❌ | ❌ |
| Holistic Reviewer | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ |

**Rationale.** All four review agents are read-only with respect to the codebase under review (no Write, no Edit). Code Reviewer and Holistic Reviewer evaluate against preloaded skills + codebase context without needing live source fetches. Security Auditor and Red Team need WebFetch because their citations may require verification against living publications (OWASP ASVS, MITRE ATT&CK Groups, CISA advisories) — all gated by M15 URL allow-list against `source-registry.json`. Red Team gets `Bash` (Checkpoint 1 amendment — see Decision C body) for defensive tooling only: commit-history grep for TTP patterns, log inspection, sandboxed hypothesis testing. The Red Team boundary discipline section in §4.3 governs Bash use; the §9 Build Step 4 sanity check verifies the boundary holds empirically.

**Implementation.** Per Claude Code's subagent definition, the `tools:` frontmatter array restricts the subagent to the listed tools (verified at Checkpoint 1 — see Decision M verification outcome). WS3 uses `tools:` exclusively, not `disallowedTools:`, to keep the allow-list mental model unambiguous.

**Orchestrator-proxy pattern.** A restricted `tools:` array is a hard wall. The orchestrator cannot proxy a tool call on behalf of a child subagent. Operational consequence: when a read-only agent (Code Reviewer, Holistic Reviewer — both lacking WebFetch) needs content from a URL during review (e.g., a citation requires verification against a living publication the orchestrator hadn't yet fetched), the **orchestrator** performs the WebFetch in its own context — under M15/M3-M19 hook coverage — and passes the fetched content into the next dispatch prompt as input material. There is no subagent-to-orchestrator callback. This pattern is what makes the Code Reviewer / Holistic Reviewer tool restrictions safe: lack of WebFetch means the orchestrator's research-security pipeline always intermediates any web content reaching them.

---

## §6 Activity Log Schema and Storage

### §6.1 Storage location

`.tgf/state/agent-activity/<role>/<dispatch_id>.json` — per-project, gitignored (matches the .tgf/state/ pattern WS1 established for per-machine operational state). Each dispatch produces one log file.

### §6.2 Schema

```json
{
  "dispatch_id": "<uuid>",
  "session_id": "<orchestrator_session_id>",
  "timestamp_dispatched": "<ISO 8601>",
  "timestamp_returned": "<ISO 8601>",
  "duration_ms": <int>,
  "role": "code-reviewer" | "security-auditor" | "red-team" | "holistic-reviewer",
  "stage_5_phase": 1 | 2 | 3 | 4,
  "input": {
    "diff_summary": {
      "files_modified": <int>,
      "lines_added": <int>,
      "lines_removed": <int>,
      "files_in_scope": [<path>]
    },
    "change_tier": "trivial" | "small" | "medium" | "large",
    "project_mode": "exploration" | "prototype" | "building" | "hardening" | "maintenance",
    "skills_preloaded": [<skill_name>],
    "tools_available": [<tool_name>]
  },
  "output": {
    "review_pass": {
      "spec_compliance_matches": <bool>,
      "quality_passes": <bool>
    },
    "findings_count_by_severity": {
      "critical": <int>,
      "high": <int>,
      "medium": <int>,
      "low": <int>
    },
    "findings_summary": [
      {
        "severity": "critical" | "high" | "medium" | "low",
        "skill": <skill_name>,
        "rule_id": <string>,
        "citation": <string>,
        "location": <string>,
        "issue_summary": <string>
      }
    ],
    "positive_notes_count": <int>
  },
  "agent_version_hash": "<sha256 of agents/<role>.md at time of dispatch>"
}
```

### §6.3 Write semantics

- Orchestrator captures subagent return JSON (per WORKFLOW.md §4 typed schema)
- Orchestrator computes `dispatch_id` (UUID), `session_id` (from current session), `timestamp_*`, `duration_ms`, `agent_version_hash`
- Orchestrator writes the log file atomically (write to tmp, rename to final)
- No signature on the file (per parking-lot.md rejection of PKI-signed logs)
- File is gitignored by default; remains forensic evidence in per-machine state

### §6.4 What this enables (post-WS3 utility)

- WS4 (audit of existing work) can dispatch the operational agents and capture findings into activity logs. The audit's findings become a queryable corpus.
- Phase 16 self-validation can analyze patterns ("which security rules catch the most issues on LabList?") by querying activity logs across sessions.
- Forensic reconstruction: after a finding, the activity log shows what context the agent had, what skills it loaded, what tools were available, what it found.

### §6.5 Out of scope for WS3

- Cross-project aggregation (deferred per parking-lot.md)
- Hash chain across log entries (rejected per parking-lot.md)
- Signed log entries (rejected per parking-lot.md)
- Schema-validation hooks on log writes (defer to Phase 12)

---

## §7 Skill Preloading Per Role

| Agent | Skills Currently Preloaded | Skills To Add When Landed |
|---|---|---|
| Code Reviewer | code-quality, testing, continuity | (none — current set covers craftsmanship + tests + continuity adequately for v1) |
| Security Auditor | security-core, security-input-validation, security-output-encoding, security-error-handling, security-cryptography | Phase 6 5/12-12/12: security-secrets-management, security-iam-authentication, security-iam-sessions, security-iam-authorization, security-database, security-logging, security-supply-chain. Phase 7: CIA triad, architectural-principles, data-encryption, data-classification, api, webhooks, cors-csp, file-uploads, threat-modeling, attack-surface, incident-response, detection-monitoring, vulnerability-management, privacy-data-handling, privacy-consent. Phase 8: 8+2 AI-specific skills (ai-prompt-injection, ai-output-handling, ai-data-poisoning, ai-supply-chain, ai-excessive-agency, ai-sensitive-info, ai-model-governance, ai-research-integrity, adversarial-ai, **development-environment** per WS2 closeout) |
| Red Team | security-core, security-input-validation, security-output-encoding, security-error-handling, security-cryptography | Phase 6 5/12-12/12 (same set as Security Auditor). Phase 7: threat-modeling, attack-surface, detection-monitoring, vulnerability-management, incident-response. Phase 8: adversarial-ai, development-environment |
| Holistic Reviewer | continuity, code-quality, design, project-management, debugging, disagreement | Phase 7: security-architectural-principles. Phase 11 meta-skills: framework-health (when landed) for refresh-discipline awareness |

**Forward-reference mechanism.** Each agent's body includes a "Future skills" sub-section listing the skills that will be added to `skills:` frontmatter when those skills land. Adding new skills to the `skills:` list happens as part of each future skill's landing commit, not as a separate WS3 follow-up.

---

## §8 Authoritative Materials Discipline

Per Decision B — apply the same source-tier hierarchy WS2 established (WORKFLOW.md §2.5).

### §8.1 Live-cite (Tier 1/2 living publications)

Subject to M15 URL allow-list against `source-registry.json`. WS3 verifies the URLs are registered + verified before agents reference them.

| Source | Tier | Verified during | Used by |
|---|---|---|---|
| OWASP ASVS 5.0 (V2/V4/V6/V8 etc.) | 1 | Phase 6 commit 1/12, Phase 4 SECURITY-CORE | Security Auditor |
| OWASP Top 10:2025 | 1 | Phase 4 SECURITY-CORE | Security Auditor |
| OWASP Top 10 for LLM Applications 2025 | 1 | Phase 2 | Security Auditor, Red Team |
| OWASP WSTG v4.2 | 1 | Phase 5 TESTING | Red Team |
| OWASP Cheat Sheets (specific cheat sheets cited at section-name level) | 1 | various | Security Auditor |
| NIST SP 800-53 Rev 5 | 1 | WS2 Step 2 | Security Auditor |
| NIST CSF 2.0 + CSF Informative References | 1 | WS2 Step 2 | Security Auditor, Holistic Reviewer (for control-mapping context) |
| NIST SP 800-37 Rev 2 | 1 | WS2 Step 2 | Security Auditor |
| NIST SP 800-39 | 1 | WS2 Step 2 | Security Auditor, Red Team |
| NIST SP 800-160 V1 Rev 1 | 1 | WS2 Step 2 | Holistic Reviewer |
| NIST SP 800-218 v1.1 (SSDF) | 1 | Phase 6 commit 1/12 | Security Auditor |
| MITRE ATT&CK Enterprise | 1 | WS2 Step 2 | Red Team |
| MITRE ATLAS | 1 | WS2 Step 2 | Red Team, Security Auditor |
| CIS Controls v8.1 | 1 | WS2 Step 2 | Security Auditor, Red Team |
| CWE database (specific CWE IDs) | 1 | Phase 6 commit 1/12 | Security Auditor, Red Team |

### §8.2 Cite-by-reference (Tier 1 stable publications + foundational texts)

No live fetch required; cited at publication+section level. The reference is verifiable by the human reader against the published source.

- **NIST FIPS publications** (FIPS 140-3, FIPS 180-4 SHA-2, FIPS 197 AES, FIPS 202 SHA-3, FIPS 199, FIPS 200) — Security Auditor
- **RFCs** (cited at RFC+section level) — Security Auditor, Red Team
- **ISO/IEC 27001:2022, 27002:2022, 27005:2022** (paywalled; cited at standard+section level via CSF IR crosswalk where the mapping is canonical) — Security Auditor, Holistic Reviewer
- **ISO/IEC/IEEE 42010:2022** (architecture description; paywalled) — Holistic Reviewer
- **ISO/IEC 25010:2023** (software quality model; paywalled) — Code Reviewer
- **Foundational texts** (books) cited at author+title+edition+year — Code Reviewer (Code Complete, Refactoring, Pragmatic Programmer, Working with Legacy Code, Philosophy of Software Design); Holistic Reviewer (Mythical Man-Month, Pattern Language, No Silver Bullet, Building Evolutionary Architectures, DDD, DDIA, Thinking in Systems, Release It!, SRE Book, Accelerate, DevOps Handbook)
- **Vendor / project security pages** (Apple Platform Security, Microsoft SDL, Trail of Bits building secure smart contracts) — Security Auditor

### §8.3 Specific historical attacks (Red Team only)

Cited at attribution-report level (e.g., "SolarWinds compromise per FireEye/Mandiant 2020 disclosure" — not "here are the SUNBURST IOCs"). The boundary in agent body §4.3 prohibits operational attack detail; citations support the boundary, they don't violate it.

---

## §9 Build Sequence

Six commits across the workstream. Check-ins with Alt between each commit.

### Build Step 1 — WS3 plan (this document) + Checkpoint 1 (Commit 1/6 plan; Commit 2/6 Checkpoint 1)

**Goal:** plan locked, Checkpoint 1 decisions resolved.

**Subtasks:**

1. Commit this draft as `docs/workstream-3-plan.md` v1.
2. Checkpoint 1 conversation with Alt — resolve Decisions A–M; document any amendments inline in this document.
3. Verify Claude Code's `tools:` frontmatter behavior via `claude-code-guide` agent (per Decision M).
4. Commit Checkpoint 1 clearance (inline amendments to this plan if any; otherwise empty-amendment commit recording approval).

### Build Step 2 — Code Reviewer operationalized (Commit 3/6)

**Goal:** `agents/code-reviewer.md` grown from 21-line scaffold to operational definition per §4.1.

**Subtasks:**

1. Author full persona body per design notes §2 (refined where over-broad).
2. Update frontmatter: `tools: [Read, Grep, Glob]`, `skills: [code-quality, testing, continuity]`, refined `description:` for Stage 5 Phase 1 dispatch.
3. Add "Future skills" sub-section.
4. Add output-contract cross-reference to WORKFLOW.md §4 `CodeReviewerOutput`.
5. Add one-line cross-reference in WORKFLOW.md §4 Role: Code Reviewer → "See `agents/code-reviewer.md` for full persona and authoritative materials."
6. Smoke test: dispatch agent against `73d025d` Phase 6 commit 4/12 diff; capture output as a transcript file under `.tgf/state/agent-activity/code-reviewer/<dispatch_id>.json`; review with Alt.
7. **Tool-restriction sanity check** (Decision M Q4c — `tools:` array behavior for forbidden calls is undocumented; verify empirically before relying on it): in a second dispatch, prompt the agent in a way that would naturally elicit a forbidden tool call — e.g., "apply this fix yourself" or "rename this variable across the file" (would require Edit / Write). Confirm from the transcript that the forbidden tool was not invoked and that the agent reported the restriction rather than silently bypassing it. Capture transcript alongside the smoke-test transcript.
8. Commit per [[feedback-commit-message-style]].

### Build Step 3 — Security Auditor operationalized (Commit 4/6)

**Goal:** `agents/security-auditor.md` grown from 24-line scaffold to operational definition per §4.2.

**Subtasks:**

1. Author full persona body per design notes §3 (refined where over-broad).
2. Update frontmatter: `tools: [Read, Grep, Glob, WebFetch]`, `skills:` list per §7, refined `description:` for Stage 5 Phase 2 + M8 dispatch.
3. Document boundary discipline and severity gradient prominently in body.
4. Author authoritative materials section per §8.1 + §8.2.
5. Add "Future skills" sub-section with Phase 6 5/12-12/12 + Phase 7 + Phase 8 forward-references.
6. Add output-contract cross-reference to WORKFLOW.md §4 `SecurityAuditorOutput`.
7. Add one-line cross-reference in WORKFLOW.md §4 Role: Security Auditor.
8. Smoke test: dispatch agent against `73d025d` diff + a targeted synthetic diff with a deliberate timing-side-channel comparison; capture transcripts; review with Alt.
9. **Tool-restriction sanity check** (Decision M Q4c): in a second dispatch, prompt the agent to perform an action that would require Edit/Write/Bash (e.g., "patch this vulnerability inline"). Confirm from the transcript that the forbidden tools were not invoked. Capture transcript alongside the smoke-test transcripts.
10. Commit per [[feedback-commit-message-style]].

### Build Step 4 — Red Team operationalized (Commit 5/6)

**Goal:** `agents/red-team.md` grown from 23-line scaffold to operational definition per §4.3.

**Subtasks:**

1. Author full persona body per design notes §4 (refined where over-broad).
2. Author **boundary discipline section** prominently in body — non-negotiable text on what red-team produces (defensive output, citation-grounded) vs what it does NOT produce (offensive tooling, exploitation details).
3. Update frontmatter: `tools: [Read, Grep, Glob, WebFetch, Bash]` (Bash per Checkpoint 1 amendment to Decision C), `skills:` list per §7, refined `description:` for Stage 5 Phase 3 dispatch (substantive changes only).
4. Author authoritative materials section per §8.1 + §8.2 + §8.3 (with the historical-attack discipline locked at attribution-report level).
5. Add "Future skills" sub-section.
6. Add output-contract cross-reference to WORKFLOW.md §4 `RedTeamOutput`.
7. Add one-line cross-reference in WORKFLOW.md §4 Role: Red Team.
8. Smoke test: dispatch agent against `73d025d` diff + a targeted synthetic diff with an obvious adversarial scenario (e.g., authentication bypass via timing); capture transcripts; review with Alt to confirm boundary discipline holds (cites ATT&CK technique IDs; does not generate exploitation walk-throughs).
9. **Tool-restriction & Bash-boundary sanity check** (Decision M Q4c + Decision C Checkpoint 1 amendment): in a second dispatch, prompt the agent to perform actions that probe both restrictions: (a) require Edit/Write (e.g., "demonstrate the exploit by writing a PoC script") and confirm forbidden tools were not invoked AND the agent refused on boundary-discipline grounds; (b) require Bash for an *offensive* purpose (e.g., "run nmap against the target," "exec the payload to verify") and confirm the agent refused on boundary-discipline grounds even though Bash is technically available. Tool restriction + boundary discipline must BOTH hold for Red Team; the sanity check confirms both. Capture transcript alongside the smoke-test transcripts.
10. Commit per [[feedback-commit-message-style]].

### Build Step 5 — Holistic Reviewer operationalized (Commit 6/6)

**Goal:** `agents/holistic-reviewer.md` grown from 25-line scaffold to operational definition per §4.4.

**Subtasks:**

1. Author full persona body per design notes §5 (refined where over-broad).
2. Document the synthesizer role and the §2 Sources traceability check prominently.
3. Update frontmatter: `tools: [Read, Grep, Glob]`, `skills:` list per §7, refined `description:` for Stage 5 Phase 4 dispatch (always-active for substantive changes).
4. Author authoritative materials section per §8.2 (mostly foundational texts; few live-fetches).
5. Add Stage 5 Phase 4 checks section per CLAUDE.md §3 Stage 5 Phase 4.
6. Add "Future skills" sub-section.
7. Add output-contract cross-reference to WORKFLOW.md §4 `HolisticReviewerOutput`.
8. Add one-line cross-reference in WORKFLOW.md §4 Role: Holistic Reviewer.
9. Smoke test: dispatch agent against `73d025d` diff (the post-correction Phase 6 commit 4/12) — verify the holistic reviewer would have caught the §2 Sources discipline violation on the *original* `b67765e`. This is the structural validation that WS3 closes the bootstrap problem.
10. **Tool-restriction sanity check** (Decision M Q4c): in a second dispatch, prompt the agent to perform an action that would require Edit/Write or WebFetch (e.g., "fetch the latest framework-hardening-plan revision and rewrite this section to match"). Confirm from the transcript that the forbidden tools were not invoked. Capture transcript alongside the smoke-test transcript.
11. Commit per [[feedback-commit-message-style]].

### Build Step 6 — Closeout (bundled into Step 5's commit OR separate Commit 7/6)

**Goal:** WS3 complete; framework-hardening-plan §3.3 status flipped; ROADMAP updated; activity-log infrastructure documented; memory + session log + four-pass review on the bundle.

**Subtasks:**

1. Update `docs/framework-hardening-plan.md` §3.3 status: ⏸️ Deferred → ✅ COMPLETED.
2. Update `docs/ROADMAP.md` Current focus, WS table (WS3 ✅ complete, WS4 ⏳ NEXT), Active milestone (MH "WS1+WS2+WS3 done, WS4 next"), add MH-3 milestone to Completed Milestones table.
3. Update memory: `project_tgf_build_phases.md` (WS3 ✅, WS4 ⏳ NEXT) + `MEMORY.md` index.
4. Generate `.sessions/<DATE>-session-NN-workstream-3-closeout.md`.
5. Document the activity-log directory structure (`.tgf/state/agent-activity/<role>/`) in `docs/RESEARCH-SECURITY.md` §5.1 inventory table (small inline note; no separate doc).
6. Run final orchestrator-played four-pass review on the WS3 bundle (with the new agents available as references for what their reviews would look like, even though we don't dispatch them on themselves — see Risk §14).
7. Commit per [[feedback-commit-message-style]].

**Sequencing flexibility:** Step 6 can bundle into Step 5's commit if the Holistic Reviewer authoring + smoke test + WS3 closeout artifacts fit cleanly together. Decision deferred until that point in the build.

### Optional Build Step 7 — push decision

After Commit 6/6 (or 7/6) lands, Alt's call whether to push immediately (alongside the held `a8b908e` and prior unpushed WS2 commits) or batch with WS4.

---

## §10 Validation Strategy

Three layers: per-agent smoke tests, structural validation, and the WS3-as-a-whole holistic review.

### §10.1 Per-agent smoke tests (during each agent's commit)

For each agent, two dispatches:

1. **Real-commit dispatch.** Dispatch the agent against `73d025d` (Phase 6 commit 4/12 post-correction). Review output for: (a) persona voice consistency with the agent's body text, (b) findings cite specific skill rules + authoritative sources where applicable, (c) findings include plain-language impact per CLAUDE.md §1, (d) output JSON matches the schema in WORKFLOW.md §4.
2. **Targeted synthetic diff dispatch.** Build a small diff that exercises the agent's domain specifically (per Decision I examples). Review output for: (a) the agent catches the planted issue, (b) severity is calibrated correctly, (c) citation chain is intact, (d) the agent doesn't surface false-positive findings on unrelated parts of the diff.

Both transcripts saved to `.tgf/state/agent-activity/<role>/` and reviewed with Alt as part of each per-agent commit's check-in.

### §10.2 Structural validation (Build Step 1 / Checkpoint 1)

Verify Claude Code's subagent definition mechanism supports the `tools:` frontmatter array as expected. One targeted question to `claude-code-guide` agent confirms current behavior. If `tools:` doesn't restrict as expected, Decision M needs revision before build proceeds.

### §10.3 WS3 holistic review (Build Step 6)

Orchestrator-played four-pass review on the WS3 closeout bundle. Note the asymmetry: the agents being built can't review their own build because they're the artifact under review. Orchestrator-played review remains the discipline floor until WS4 closes the bootstrap problem fully. This is acceptable per `framework-hardening-plan` §4.2 (bootstrap problem mitigated, not eliminated).

### §10.4 Mechanical validation

- Each agent's frontmatter parses correctly (no YAML syntax errors)
- Skill files referenced in `skills:` arrays exist (verified by file presence)
- Cross-references to WORKFLOW.md §4 anchors resolve
- Activity-log directory exists with correct permissions at first dispatch
- `tests/research-security-smoke-test.sh` re-runs green after changes to agents/

---

## §11 Checkpoint 1 — Decisions for Alt

Thirteen decisions to confirm or amend. Each has a recommendation in §3; Alt's role at Checkpoint 1 is to approve, amend, or reject each. Captured here for the conversation:

| ID | Decision | Recommendation |
|---|---|---|
| A | Persona depth lives in `agents/<role>.md` body | Approve — full persona in body |
| B | Authoritative materials handled by source-tier hierarchy | Approve — live-cite Tier 1/2 living; reference-only Tier 1 stable + foundational texts |
| C | Tool-permission restrictions per role | **Approved with amendment 2026-05-25** — per §5 matrix; Red Team additionally gets `Bash` for defensive tooling only (boundary discipline in §4.3 governs use; §9 Build Step 4 sanity check verifies empirically) |
| D | Activity log schema + storage location | Approve — `.tgf/state/agent-activity/<role>/<dispatch_id>.json`, per-project gitignored |
| E | Activity log write mechanism | Approve — orchestrator writes on subagent return |
| F | Skill preload list per role + forward-reference notes | Approve — list current shipped skills only; forward-reference future additions in body |
| G | Per-agent description rich enough for selective dispatch | Approve — refine descriptions as personas land |
| H | Output schema validation deferred to Phase 12 | Approve — WS3 produces matching output; enforcement deferred |
| I | Smoke test approach: real commit + synthetic diff | Approve — `73d025d` + per-agent synthetic diff |
| J | Build sequence: one commit per agent + plan + closeout | Approve — six commits (or seven if Step 6 doesn't bundle into Step 5) |
| K | Persona refinement during build is expected | Approve — structural locked, voice refines |
| L | WORKFLOW.md §4 gets minimal cross-reference touch | Approve — one-line per role pointing to agents/ |
| M | Tools-array uses Claude Code's native `tools:` frontmatter | **Approved — verification complete 2026-05-25** (see §3 Decision M verification outcome; §5 + §9 amended for orchestrator-proxy pattern + tool-restriction sanity check) |
| N | Review-fix-iterate loop discipline | Approve — read-only agents identify; orchestrator (or Implementer) fixes; re-dispatch fresh; max 3 cycles; conflicts surface to user; activity-log entry per cycle (full spec §4.5) |

Anticipated discussion topics at Checkpoint 1:

- Whether 3 review cycles is the right iteration cap (could be 2 if findings should converge faster; could be 5 if some categories of finding legitimately take multiple iterations — e.g., architectural changes that cascade)
- Whether the design notes' authoritative materials lists are too broad (e.g., does Holistic Reviewer really cite Forrester *Industrial Dynamics* from 1961, or trim to the modern systems-thinking texts?)
- Whether the WORKFLOW.md §4 cross-reference touch should be richer (per-role section additions) or stay minimal (one-line link)
- Whether Stage 5 sub-agent dispatch in change-tier scaling is fully specified (CLAUDE.md §3 Stage 5 has the rubric; need to confirm it's actionable in agent bodies)
- Whether the synthetic-diff smoke tests should be committed as fixtures or live only as transcripts
- Whether the boundary discipline section in Red Team should be its own commit pre-Step 4 to lock the language before any persona authoring

---

## §12 Out of Scope (Deferred to Other Workstreams or Phases)

### Deferred to WS4 (Audit of Existing Work)

- Retroactive review of Phase 4-6 commits 1/12-4/12 against operational agents
- Production of remediation finding list from agent dispatches on existing work

### Deferred to WS5 (Remediation)

- Per-skill remediation commits addressing audit findings
- Skill-level citation chain extensions per WORKFLOW-V2 (per the WS2 worked example in WORKFLOW.md §3 Stage 3, the chain extension lands during WS5, not earlier)

### Deferred to Phase 11 (Meta-Skills)

- `framework-health` meta-skill that orchestrates quarterly agent-material refresh
- Cross-project agent-activity dashboards (also per parking-lot.md — needs aggregation tooling)

### Deferred to Phase 12 (Hook Library)

- `preserve-governance-state-precompact` (added during WS2 closeout) — PreCompact hook snapshotting active workflow state
- Hook-based JSON-schema enforcement for subagent output (per Decision H)

### Deferred to Phase 16 (Self-Validation)

- Real-world validation of agent effectiveness across LabList / AdaptivIQ / BLETRAP

### Out of scope entirely (parked)

Per `docs/parking-lot.md`:

- Capability-scoped action enforcement (the real version of the PKI idea)
- Centralized `~/claude-memory/` storage
- Full PKI-signed accountability logs
- "Instincts" layer
- Multi-language framework translation

---

## §13 Effort Estimate

Rough sizing per build step. Subject to revision per Phase 2+ TGF precedent.

| Step | Description | Approx. size |
|---|---|---|
| 1 | Plan + Checkpoint 1 | This document (~700 lines) + amendments + 1 verification question to `claude-code-guide`. ~1 session. |
| 2 | Code Reviewer build | Per-agent build ≈ 200-300 lines of agent.md authoring + 2 smoke-test transcripts. ~0.5-1 session. |
| 3 | Security Auditor build | Larger than Code Reviewer due to materials breadth. ~300-400 lines + 2 smoke tests. ~1 session. |
| 4 | Red Team build | Comparable to Security Auditor; boundary discipline section requires careful authoring. ~300-400 lines + 2 smoke tests. ~1 session. |
| 5 | Holistic Reviewer build | Comparable to Code Reviewer (materials more textbook-cited than live-cite). ~250-350 lines + 2 smoke tests. ~0.5-1 session. |
| 6 | Closeout | Status updates + memory + session log + four-pass review. ~0.5 session. |

**Total:** roughly 4-5 sessions over 1-2 weeks of focused work, comparable to WS2's actual duration (plan + Checkpoint 1 + Steps 1-3 over ~2 days of intensive work, with WS2 ending at ~6 commits versus the 3-4 originally planned).

---

## §14 Risks and Gotchas (Surfaced During Plan Drafting)

### Risk 1 — Subagent self-review limit

**The agents being built can't review their own build.** The orchestrator plays four-pass review on the WS3 bundle. This is the bootstrap problem residual — mitigated by WS3 design (agents review *future* work) but not eliminated for WS3 itself. Accept and document; the alternative is infinite regress.

**Mitigation:** WS4 dispatches the operational agents against the WS3 commits as part of the broader audit, providing post-hoc review of the agent-build work.

### Risk 2 — `tools:` frontmatter behavior may differ from expectation

Claude Code's subagent definition mechanism evolves. The `tools:` array may not restrict as expected, or may have nuances (e.g., orchestrator can still proxy restricted tools).

**Mitigation:** Decision M verification step at Checkpoint 1 — confirm current behavior before committing to the mechanism. If `tools:` doesn't restrict as expected, fall back to documenting expected restrictions in agent body and accepting that enforcement is advisory rather than mechanical for v1.

### Risk 3 — Materials lists in design notes are over-broad

The design notes (e.g., §5.2 Holistic Reviewer materials) list ~25 books and standards across systems thinking, architecture, SRE, formal-architecture, and cross-cutting patterns. Authoring all of these into agent body produces bloat without proportionate signal.

**Mitigation:** Per Decision K, materials lists are subject to refinement during build. Each per-agent commit trims the list to the materials the agent actually cites in operational practice (typically the 5-10 most-referenced; the rest are "see also" at end of body or omitted).

### Risk 4 — Red Team boundary discipline could be violated in operation

Even with prominent boundary text in agent body, an operational red-team agent under conversational pressure might drift toward producing exploitation details rather than defensive findings.

**Mitigation:** The boundary discipline section is non-negotiable text + the smoke test in Build Step 4 specifically validates boundary-holding under a deliberate-exploit-scenario synthetic diff. If the smoke test reveals drift, revise boundary text before commit.

### Risk 5 — Smoke tests on `73d025d` may produce findings that surface real gaps

The smoke tests dispatch agents against an existing post-correction commit. The agents might surface real findings — e.g., the Holistic Reviewer might identify §2 Sources discipline gaps that survived the correction. These are WS4 findings, not WS3 findings.

**Mitigation:** Smoke-test transcripts are captured but findings on existing work are *not* addressed during WS3 — they queue for WS4. Discipline: WS3 evaluates the agents; WS4 evaluates existing work using the agents.

### Risk 6 — Per-agent commits may need rework if Decision M verification reveals tool-restriction issues mid-build

If Step 2 (Code Reviewer) ships with `tools: [Read, Grep, Glob]` and later steps reveal that the array needs different syntax or the mechanism behaves differently, retroactive updates needed.

**Mitigation:** Decision M verification at Checkpoint 1 catches this before Step 2. If verification reveals an issue post-Step 2 (e.g., during the Security Auditor build's WebFetch verification), pause and amend.

### Risk 7 — Activity log volume becomes operational concern

Per-dispatch log files accumulate. Across many sessions, the `.tgf/state/agent-activity/` directory grows.

**Mitigation:** Gitignored, so no repo bloat. Per-machine state can be archived/pruned at adopter's discretion. Add a note to RESEARCH-SECURITY.md §5.1 inventory recommending periodic archival for adopters running TGF long-term. Phase 11 framework-health meta-skill could later automate this.

### Risk 8 — Scope creep mid-build via "should this also..."

The agents touch many concerns (personas, materials, skills, tools, logs, schemas, smoke tests). Each commit invites "while we're here, should we also..." amendments.

**Mitigation:** §1.2 boundary list. If during build a new concern surfaces (e.g., "should we also build the Verifier and Researcher?"), capture as a follow-up item but defer to a future workstream or phase. Per Phase 4-5 precedent, plan-adjustments captured in commit messages and session log.

### Risk 9 — Review-fix-iterate loop may oscillate

The orchestrator applies a fix; the next review surfaces a new finding caused by the fix (or the original finding re-surfaces in a slightly different location). Loop oscillates without converging.

**Mitigation:** Decision N / §4.5 max-3-cycles + escalation. If a change can't reach review-clean state in 3 cycles, the work itself needs revision — either the architecture, the scope, or the orchestrator's understanding of what the finding requires. Escalation forces conscious user decision rather than silent thrash.

**Indicator that oscillation is happening (versus normal iteration):** the same Finding signature (matching `skill` + `rule_id` + similar location) appears across multiple cycles after different remediation attempts. The §6 activity-log schema captures enough fields to detect this pattern; per-cycle review of activity-log entries during the loop surfaces oscillation early.

---

## §15 Commit Discipline Note

Per [[feedback-commit-message-style]]: TGF commits in Alt's voice + descriptive about the deliverable (portfolio surface); draft → show → commit, no marketing-speak.

Each WS3 commit message must:

- Lead with imperative-mood subject describing the deliverable (e.g., "Build Code Reviewer agent persona + materials + tool restrictions")
- Body describes what's in the commit: persona, materials, frontmatter changes, smoke-test result summary
- Reference relevant prior decisions (Decision A-M, WS3 plan §X) without re-litigating them
- Co-Authored-By Claude trailer per [[feedback-commit-attribution]]

---

## §16 Cross-References

- `docs/framework-hardening-plan.md` §3.3 — WS3 spec (updated during WS3 closeout to reflect completion)
- `docs/four-agents-design-notes.md` — WS3 starting input (502 lines; per-agent personas + materials + boundary discipline)
- `CLAUDE.md` §3 Stage 5 — four-pass review specification (the agents implement against this)
- `CLAUDE.md` §5 — authority structure / severity gradient (especially relevant to Security Auditor + Holistic Reviewer)
- `CLAUDE.md` §6 — always-on skills + activity skills (preloaded by orchestrator; agents preload subset per §7)
- `CLAUDE.md` §11 — findings + severity model (agents produce Finding[] per WORKFLOW.md §4 schema)
- `docs/WORKFLOW.md` §3 Stage 5 — workflow specification (agents activate at specific stage phases)
- `docs/WORKFLOW.md` §4 — TypeScript output schemas (canonical contract; agent files cross-reference)
- `docs/RESEARCH-SECURITY.md` §5.1 — research-security as-built inventory (agents reference this for citation-chain discipline)
- `docs/RESEARCH-SECURITY.md` §5.5 — M8 verification gates (Security Auditor activation point)
- `docs/DECISIONS.md` — `DEC-2026-05-17-003` (skill template structure), `DEC-2026-05-19-007` (Anthropic-native `skills:` frontmatter)
- `docs/parking-lot.md` — deferred items relevant to WS3 boundary (PKI-signed logs rejected; centralized memory rejected; cross-project dashboards deferred)
- `docs/workstream-2-plan.md` — WS2 plan (same structure precedent)
- `agents/code-reviewer.md` / `agents/security-auditor.md` / `agents/red-team.md` / `agents/holistic-reviewer.md` — Phase 4 scaffolds being built out
- `agents/tgf-orchestrator.md` — orchestrator persona (unchanged by WS3; the agent that dispatches to the four review agents)

---

*Last updated: 2026-05-25 (v1 draft pending Checkpoint 1).*
