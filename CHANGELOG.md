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
