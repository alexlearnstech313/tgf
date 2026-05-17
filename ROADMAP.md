# Roadmap

The Governance Framework v1 — 16-phase build plan. Path A scope (full v1 with hooks, orchestration, self-evolution, token efficiency, continual improvement).

> ROADMAP is living documentation. Items here are committed to. Milestones with target dates that slip get explicit revision, not silent extension. Update at session close when phase status changes or milestones progress.

**Current focus:** Phase 2 — CLAUDE.md (expand to Path A sections §15–§22) + adopter-facing `CLAUDE.md.template`.

---

## Phase Status

| Phase | Description | Status |
|-------|-------------|--------|
| 0 | Foundation Architecture Decisions | ✅ Complete |
| 1 | Foundation / Repo Structure | ✅ Complete |
| 2 | CLAUDE.md (expanded with §15-§22 for Path A) | 🟡 Partial (~641 line draft exists; missing Path A sections) |
| 3 | Workflow Specification with Orchestration | ⬜ Not started |
| 4 | Always-On Skills (3) | ⬜ Not started |
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

### Phase 2 — CLAUDE.md (expanded)

Current draft (~641 lines) covers §1–§14. Path A requires §15–§22:

- [ ] §15 Mode-Aware Operation (exploration / prototype / building / hardening / maintenance)
- [ ] §16 Empirical Verification for AI-Generated Code
- [ ] §17 Citation Verification
- [ ] §18 Hooks for Enforcement
- [ ] §19 Token Efficiency
- [ ] §20 Agent Orchestration
- [ ] §21 Self-Evolving Knowledge
- [ ] §22 Continual Improvement

Plus produce the adopter-facing `CLAUDE.md.template` with placeholders for project-specific content.

### Phase 3 — Workflow Specification with Orchestration

Detailed workflow document specifying:

- Per-stage orchestration patterns (when subagents dispatch, what context they get)
- Subagent dispatch points and contracts
- Hook integration points throughout
- Change tier scaling for review depth

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
| M2 | Phase 2 complete (CLAUDE.md §15-§22 added + adopter template) | TBD | medium | not started |
| M3 | Phase 3 complete (workflow specification) | TBD | medium | not started |

## Completed Milestones

| ID | Milestone | Completed | Notes |
|----|-----------|-----------|-------|
| M1 | Phase 1 complete (repo scaffolding, templates, initial commit) | 2026-05-17 | Initial commit on `main` |
| M0 | Phase 0 architectural decisions locked | 2026-05-17 | See DEC-2026-05-17-003 |

## Slip History

*No slips yet.*

---

*Last updated: 2026-05-17.*
