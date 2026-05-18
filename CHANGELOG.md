# Changelog

All notable changes to The Governance Framework will be documented in this file.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Added

- Initial repository scaffolding (Phase 1)
- `SKILL.md.template` matching Phase 0 anchored-section specification
- Artifact templates: `PROJECT-CONTEXT`, `DOMAIN-CONTEXT`, `DECISIONS`, `ROADMAP`, `ERROR-LOG`, `VENDOR-LOG`, `WAIVER-LOG`, `SCHEMA-HISTORY`, `SESSION-LOG`, `BASELINE-AUDIT`
- Security-conscious `.gitignore.template` (protective defaults)
- Plugin marketplace metadata (`.claude-plugin/plugin.json`, `marketplace.json`)
- Directory structure for skills, hooks (seven lifecycle events), stack-baselines, commands, and docs
- Initial `DECISIONS.md` capturing framework name, Path A scope, and Phase 0 architectural decisions
- Initial `ROADMAP.md` with 16-phase build plan and current status
- `DEC-2026-05-17-004`: authoritative source verification + no-downloads constraint during skill creation. Locks the discipline before Phase 2 research begins. Skills citing authoritative frameworks (OWASP, NIST, ISO, MITRE, RFCs) must verify rule-level citations against live sources at creation/refresh time, with research performed via Claude's web tools — no fetched content touches the developer filesystem except as synthesized output.
- `security-ai-research-integrity` added to Phase 8 scope (operationalizes DEC-004; fires when meta-skills fetch external content for skill generation or domain research).
- Phase 2 (CLAUDE.md expansion) shipped via four commits:
  - `c9ac67a` — §17 Citation Verification expanded (~15 → 46 lines) to reflect DEC-2026-05-17-004's six clauses: live verification at skill-creation time, rule-level citation precision, fetched content treated as untrusted input, no developer-machine downloads, paywalled sources cited by reference, comparative framework research separated from authoritative citation.
  - `92c9894` — §18 Hooks for Enforcement (71 lines) + §19 Token Efficiency (67 lines) + `DEC-2026-05-17-005` (hook architecture amendment to use Claude Code's actual PascalCase event taxonomy and add `.claude/git-hooks/` for git-layer enforcement) + hook directory restructure (`SessionStart`, `SessionEnd`, `PreToolUse`, `PostToolUse`, `SubagentStart`, `SubagentStop`, `FileChanged`, `ConfigChange`).
  - `3a48b0a` — §20 Agent Orchestration (100 lines: seven subagent roles + cost-aware dispatch by change tier + two-stage spec-then-quality review + LLM06 prevention strategies + MITRE ATLAS adversarial considerations) + §21 Self-Evolving Knowledge (96 lines: bounded evolution categories + confidence thresholds + LLM04 data-poisoning mitigation + four input streams).
  - Phase 2 closing commit (this one) — §22 Continual Improvement (67 lines: three improvement loops feeding each other — citation refresh, evolution proposals, telemetry analysis) + `templates/CLAUDE.md.template` (1091 lines, adopter-facing CLAUDE.md with header-level customization convention + inline ADOPTER-CUSTOMIZE markers at §7/§8/§9) + `docs/phase-2-plan.md` (Phase 2 implementation plan, committed for transparency per Decision 2 of the plan) + ROADMAP and CHANGELOG closeout.
- Phase 2 used the DEC-2026-05-17-004 research discipline throughout: authoritative source verification was performed via Claude's web tools on Anthropic infrastructure; no fetched content reached the developer filesystem except as synthesized citations and rules within markdown files. Sources verified during Phase 2: OWASP Top 10 for LLMs 2025 (LLM04, LLM06), NIST SP 800-218 v1.1 (SSDF), MITRE ATLAS v5.4.0 (February 2026), Anthropic Skill authoring best practices, Claude Code Hooks reference. Comparative-only source: Superpowers framework README (per DEC-004 Clause 6 — comparative research stays separate from authoritative citation).
