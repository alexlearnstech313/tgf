# Roadmap

The Governance Framework v1 — 16-phase build plan. Path A scope (full v1 with hooks, orchestration, self-evolution, token efficiency, continual improvement).

> ROADMAP is living documentation. Items here are committed to. Milestones with target dates that slip get explicit revision, not silent extension. Update at session close when phase status changes or milestones progress.

**Current focus:** Phase 4 plan drafted 2026-05-19 — `docs/phase-4-plan.md` awaiting Checkpoint 1 approval on five open decisions before implementation begins. Architectural foundation locked across three ADRs (`DEC-007` plugin + orchestrator agent + skills preload; `DEC-008` skill catalog consolidation + reference file pattern; `DEC-009` hook physical layout) and one pre-Phase-4 housekeeping commit (`49c8a82` repo restructure to plugin layout). Phase 4 implementation produces 3 always-on skills (CODE-QUALITY, SECURITY-CORE, CONTINUITY) + tgf-orchestrator agent + 4 review subagent scaffolds + plugin `settings.json` — estimated ~18-20 hours focused work across 3-5 sessions. Phase 3 ✅ Complete same day with `docs/WORKFLOW.md` at 911 lines.

---

## Phase Status

| Phase | Description | Status |
|-------|-------------|--------|
| 0 | Foundation Architecture Decisions | ✅ Complete |
| 1 | Foundation / Repo Structure | ✅ Complete |
| 2 | CLAUDE.md (expanded with §15-§22 for Path A) + adopter template | ✅ Complete |
| 3 | Workflow Specification with Orchestration | ✅ Complete |
| 4 | Always-On Skills (3) | 🟡 In progress (plan drafted) |
| 5 | Activity Skills (6) | ⬜ Not started |
| 6 | Foundation Security Skills (11) | ⬜ Not started |
| 7 | Extended Security Skills (22) | ⬜ Not started |
| 8 | AI-Specific Security Skills (8+1 adversarial) | ⬜ Not started |
| 9 | Operations & Quality Skills (7) | ⬜ Not started |
| 10 | Compliance Regulatory Skills (5) | ⬜ Not started |
| 11 | Meta-Skills (5) | ⬜ Not started |
| 12 | Hook Library | ⬜ Not started |
| 13 | Stack Baselines (LabList, AdaptivIQ, BLETRAP) | ⬜ Not started |
| 14 | Slash Commands + Plugin Integration | ⬜ Not started |
| 15 | Documentation | ⬜ Not started |
| 16 | Self-Validation (60-90 days on real projects) | ⬜ Not started |

---

## Phase Details

### Phase 0 — Foundation Architecture Decisions ✅

Five locked interface specifications. See [DECISIONS.md](./DECISIONS.md) → DEC-2026-05-17-003.

### Phase 1 — Foundation / Repo Structure ✅

Deliverables (all complete):

- [x] Directory tree (`.claude/skills`, `.claude/hooks/<event>/`, `templates/`, `stack-baselines/`, `commands/`, `docs/`, `.claude-plugin/`)
- [x] `SKILL.md.template` matching Phase 0 anchored-section spec
- [x] Artifact templates (PROJECT-CONTEXT, DOMAIN-CONTEXT, DECISIONS, ROADMAP, ERROR-LOG, VENDOR-LOG, WAIVER-LOG, SCHEMA-HISTORY, SESSION-LOG, BASELINE-AUDIT)
- [x] `.gitignore.template` (protective defaults)
- [x] Active `.gitignore` for TGF's own repo
- [x] `LICENSE` (MIT)
- [x] Plugin marketplace stubs (`.claude-plugin/plugin.json`, `marketplace.json`)
- [x] `README.md` (initial placeholder; full version in Phase 15)
- [x] `DECISIONS.md` (captures DEC-2026-05-17-001 through 003)
- [x] `ROADMAP.md` (this file)
- [x] `CHANGELOG.md` (initial Unreleased section)
- [x] `LIMITATIONS.md` (placeholder; full version in Phase 15)
- [x] `git init` + initial commit

### Phase 2 — CLAUDE.md (expanded) ✅

Phase 2 shipped via four commits, one per logical grouping per the approved Phase 2 plan:

- [x] §15 Mode-Aware Operation — already in the post-Phase-1 draft; QC-reviewed during Phase 2 onset, no changes needed
- [x] §16 Empirical Verification for AI-Generated Code — already in the post-Phase-1 draft; QC-reviewed during Phase 2 onset, no changes needed
- [x] §17 Citation Verification (46 lines) — expanded from ~15 lines to reflect DEC-2026-05-17-004's six clauses (commit `c9ac67a`)
- [x] §18 Hooks for Enforcement (71 lines) + DEC-2026-05-17-005 (hook architecture amendment) + hook directory restructure to Claude Code's actual PascalCase event taxonomy + `.claude/git-hooks/` for git-layer enforcement (commit `92c9894`)
- [x] §19 Token Efficiency (67 lines) — bundled in commit `92c9894`
- [x] §20 Agent Orchestration (100 lines) — seven subagent roles + cost-aware dispatch + two-stage spec-then-quality review + LLM06 mitigation + MITRE ATLAS adversarial considerations (commit `3a48b0a`)
- [x] §21 Self-Evolving Knowledge (96 lines) — bounded evolution categories + confidence thresholds + LLM04 data-poisoning mitigation; bundled in commit `3a48b0a`
- [x] §22 Continual Improvement (67 lines) — three improvement loops feeding each other (citation refresh + evolution proposals + telemetry analysis) (Phase 2 closing commit)
- [x] Adopter-facing `templates/CLAUDE.md.template` (1091 lines) — mirrors internal CLAUDE.md with header note explaining framework-enforced vs adopter-customize convention + inline ADOPTER-CUSTOMIZE markers at §7/§8/§9
- [x] `docs/phase-2-plan.md` committed for transparency per Decision 2 of the Phase 2 plan

Plan adjustments accumulated during Phase 2 (tactical, logged for audit):

- Universal QC criterion #1 (section anchor present) struck for CLAUDE.md sections — anchors are a skill template feature per Phase 0 `DEC-2026-05-17-003` Clause 1; CLAUDE.md uses simple `## §N` markdown headers
- Line-target ranges in per-section plans treated as heuristics, not hard requirements; §18 came in at 71 lines vs target 85-115 (content covered all per-section QC criteria; artificial expansion rejected)
- Adopter template length target (700-800 lines) significantly underestimated; internal CLAUDE.md grew from 641 → 1073 lines during Phase 2, so the template at 1091 lines mirrors that with header additions
- Adopter template marker convention: header-based explanation + three inline `<!-- ADOPTER-CUSTOMIZE -->` markers at §7/§8/§9 instead of 22 per-section `<!-- FRAMEWORK-ENFORCED -->` markers — same convention, less inline bloat

### Phase 3 — Workflow Specification with Orchestration ✅

Detailed workflow document (`docs/WORKFLOW.md`) specifying:

- Per-stage orchestration patterns (when subagents dispatch, what context they get)
- Subagent dispatch points and contracts (including JSON output schemas for all seven roles per DEC-003 Clause 3)
- Hook integration points throughout (input + exit semantics, no script bodies — Phase 12 ships those)
- Change tier scaling for review depth
- Mode scaling tables
- Stage-to-stage handoff contracts and termination conditions
- Debugging variant adaptation
- Three worked examples (Trivial / Medium / Large)

**Status (2026-05-19):** ✅ Shipped. `docs/WORKFLOW.md` at 911 lines across 9 sections; Phase 4–12 build against this specification. Constructed using the TGF workflow itself (dogfooded) — five workflow stages applied across two commits per Checkpoint 1 Decision E, with Stage 5 four-pass review producing concrete fixes on both commits. Three commits shipped Phase 3: `efd25c2` (plan), `61c1614` (Checkpoint 1 clearance + DEC-006), `d47d355` (WORKFLOW.md commit 1/2), and the commit landing this status update (WORKFLOW.md commit 2/2).

### Phase 4 — Always-On Skills (3)

- `CODE-QUALITY` — engineering discipline, type safety, error handling, naming, scale-aware patterns, migration patterns, documentation principles, solo-maintainability
- `SECURITY-CORE` — security-mindedness as trait, top universal rules, secure-by-default with usability balance
- `CONTINUITY` — memory architecture, session log discipline, three-log + ROADMAP management, decision capture

### Phase 5 — Activity Skills (6)

- `PROJECT-MANAGEMENT` — greenfield/brownfield modes, decomposition, MVP definition, stack selection, dependency planning
- `DISCOVERY` — branching tree methodology for vague inputs
- `TESTING` — test strategy, coverage discipline, security/accessibility testing
- `DEBUGGING` — Agans methodology, Five Whys, AI-specific debugging concerns
- `DISAGREEMENT` — tactful pushback, severity gradient, waiver protocol
- `DESIGN` — Anthropic foundation + negative constraints + AI-specific design failure modes

### Phase 6 — Foundation Security Skills (11)

Skills every project needs regardless of stack:

- `security-input-validation`
- `security-output-encoding`
- `security-iam-authentication`
- `security-iam-sessions`
- `security-iam-authorization`
- `security-cryptography`
- `security-database`
- `security-error-handling`
- `security-logging`
- `security-secrets-management`
- `security-supply-chain`

### Phase 7 — Extended Security Skills (22)

CIA triad, architectural (defense-in-depth, secure-architecture, zero-trust, least-privilege, assumed-breach), IAM-OAuth-OIDC, data layer (encryption, classification), application (api, webhooks, cors-csp, file-uploads), threat management (threat-modeling, attack-surface), operations (incident-response, detection-monitoring, vulnerability-management), privacy (data-handling, consent).

### Phase 8 — AI-Specific Security Skills (8 + 1 Adversarial-AI)

- `security-ai-prompt-injection`
- `security-ai-output-handling`
- `security-ai-data-poisoning`
- `security-ai-supply-chain`
- `security-ai-excessive-agency`
- `security-ai-sensitive-info`
- `security-ai-model-governance`
- `security-ai-research-integrity` (operationalizes DEC-2026-05-17-004 — fires when meta-skills fetch external content for skill generation or domain research)
- `security-adversarial-ai` (framework's own resistance to manipulation)

### Phase 9 — Operations & Quality Skills (7)

- `ops-observability`
- `ops-devops-cicd`
- `ops-business-risk`
- `quality-accessibility`
- `quality-performance-cost`
- `data-architecture` (separate from `security-database` per Phase 0 expert review)
- `compliance-foundations`

### Phase 10 — Compliance Regulatory Skills (5)

Load only when PROJECT-CONTEXT scope warrants:

- `compliance-gdpr`
- `compliance-ccpa`
- `compliance-hipaa`
- `compliance-pci-dss`
- `compliance-soc2`

### Phase 11 — Meta-Skills (5)

- `PROJECT-CONTEXT`
- `DOMAIN-RESEARCH`
- `BASELINE-AUDIT`
- `SKILL-FORGE`
- `FRAMEWORK-HEALTH` (new — surfaces telemetry and evolution proposals)

### Phase 12 — Hook Library

Reference shell scripts for:

- **Safety** (universal, always active): `block-dangerous-git`, `block-secrets-commit`, `block-destructive-db`
- **Workflow** (mode-gated): `verify-session-log`, `verify-tests-pass`, `verify-findings-resolved`, `verify-roadmap-updated`
- **Governance** (mode-gated): `block-runtime-skill-changes`, `log-security-operations`, `detect-edit-loops`

Mode-aware profiles wired in via `.claude/hooks/profile.json`.

### Phase 13 — Stack Baselines

Generated by SKILL-FORGE, validating end-to-end:

- **LabList**: Next.js + Supabase + Stripe + Vercel
- **AdaptivIQ**: Flutter + Firebase + RevenueCat
- **BLETRAP**: Python (Flask) + SQLite + Raspberry Pi + Wazuh

### Phase 14 — Slash Commands + Plugin Integration

Commands (namespace `/tgf:*`):

- `/tgf:project-context` — run/refresh PROJECT-CONTEXT interview
- `/tgf:baseline-audit` — seven-phase brownfield assessment
- `/tgf:regenerate-skills` — refresh skill suite
- `/tgf:domain-research` — pull authoritative domain knowledge
- `/tgf:audit-engagement` — verify framework engaging properly
- `/tgf:brainstorm` — explicit DISCOVERY/PROJECT-MANAGEMENT engagement
- `/tgf:plan` — explicit planning engagement
- `/tgf:review` — explicit four-pass review on existing code
- `/tgf:framework-health` — quarterly health report
- `/tgf:review-evolution` — review pending self-evolution proposals
- `/tgf:set-mode` — change project mode
- `/tgf:set-hooks` — change hook profile
- `/tgf:verify-citation` — look up cited rules from skills
- `/tgf:promote` — formal promotion of prototype code to production scope
- `/tgf:roadmap` — view/update ROADMAP

Plus plugin marketplace submission.

### Phase 15 — Documentation

- `README.md` (full)
- `INSTALL.md`
- `DESIGN-RATIONALE.md` (why TGF looks this way)
- `LIMITATIONS.md` (full)
- `docs/how-it-works.md`
- `docs/workflow.md`
- `docs/glossary.md`
- `docs/faq.md`

### Phase 16 — Self-Validation

60-90 days of TGF in active use on LabList development. Cross-validation on AdaptivIQ. Iteration based on real-use findings. Public GitHub push when validated.

---

## Active Milestones

| ID | Milestone | Target | Confidence | Status |
|----|-----------|--------|------------|--------|
| M4 | Phase 4 complete (always-on skills: CODE-QUALITY, SECURITY-CORE, CONTINUITY) | TBD | medium | not started |

## Completed Milestones

| ID | Milestone | Completed | Notes |
|----|-----------|-----------|-------|
| M3 | Phase 3 complete (workflow specification with orchestration) | 2026-05-19 | `docs/WORKFLOW.md` 911 lines, 9 sections. Four commits: `efd25c2` plan · `61c1614` Checkpoint 1 + DEC-006 · `d47d355` WORKFLOW.md commit 1/2 · closing commit WORKFLOW.md commit 2/2 + closeout. Dogfooded the workflow during construction. Plus pre-Phase-3 housekeeping: `a630540` CLAUDE.md/ARCHITECTURE.md split (cleared 40k-char threshold). |
| M2 | Phase 2 complete (CLAUDE.md §15-§22 + adopter template + DEC-005) | 2026-05-17 | Four commits: `c9ac67a` §17 · `92c9894` §18+§19+restructure+DEC-005 · `3a48b0a` §20+§21 · closing commit §22+template+closeout |
| M1 | Phase 1 complete (repo scaffolding, templates, initial commit) | 2026-05-17 | Initial commit on `main` |
| M0 | Phase 0 architectural decisions locked | 2026-05-17 | See DEC-2026-05-17-003 |

## Slip History

*No slips yet.*

---

*Last updated: 2026-05-19.*
