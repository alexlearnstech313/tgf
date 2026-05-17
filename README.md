# The Governance Framework (TGF)

> Grounds AI-assisted development in industry-authoritative standards.

**Status:** v0.1.0 — in active development. Foundation phase (Phase 1 of 16). Not yet ready for adoption.

---

## What This Is

TGF is a structured governance system for AI-assisted development. It encodes senior DevSecOps engineering judgment as enforceable rules grounded in primary authoritative sources — OWASP ASVS, NIST publications, ISO/IEC 27001/27002, MITRE ATT&CK/ATLAS, RFCs — not blog posts or training-data approximations.

Designed for solo developers and small teams who use AI heavily for coding and want their work to meet industry standards by default.

## Mission

Let developers focus on what to build while the framework ensures the work meets industry standards across:

- **Code quality** — engineering discipline, scale-aware patterns, solo-maintainability
- **Security** — authentication, authorization, input validation, cryptography, supply chain, AI-specific concerns
- **Compliance** — GDPR, CCPA, HIPAA, PCI-DSS, SOC 2 (activated by project scope)
- **Operations** — observability, CI/CD, incident response, performance

## Architecture

Three layers:

1. **CLAUDE.md** — the developer's character, workflow contract, and authority structure
2. **Skills** — granular domain expertise with contextual triggers and rule-level citations
3. **Artifacts** — committed memory (`DECISIONS`, `ROADMAP`, `ERROR-LOG`, `VENDOR-LOG`, `WAIVER-LOG`, `SCHEMA-HISTORY`) plus gitignored session logs

Built around a six-stage workflow (Research → Scope → Plan with Governance → Implement → Four-Pass Review → Commit) with mode-aware scaling and four-pass review (Code / Security / Red Team / Holistic).

## What Makes TGF Different

- **Authoritative sources only.** Every rule cites a specific source (OWASP ASVS V3.1.1, NIST SP 800-63B §5.1.1.2, etc.). No blog-post-grade citations.
- **Granular skills.** ~50+ focused skills rather than monolithic "best practices" documents. Each skill has room for rule-level depth.
- **Anti-pattern catalogs.** Every skill ships with concrete examples of what to reject, not just abstract principles.
- **Mode-aware scaling.** Standards within scope are unconditional. Scope changes by project mode (exploration / prototype / building / hardening / maintenance).
- **Silent engagement.** The framework does the work without narrating it. Speaks when there's something worth saying.
- **Solo-maintainability as first-class concern.** Code produced under TGF must be maintainable by one person across long time horizons.

## Status

This repository is in foundation buildout. See [`ROADMAP.md`](./ROADMAP.md) for the 16-phase build plan and current progress, and [`DECISIONS.md`](./DECISIONS.md) for architectural decisions.

Full adopter documentation (INSTALL, DESIGN-RATIONALE, how-it-works, glossary, FAQ) lands in Phase 15.

## License

MIT — see [LICENSE](./LICENSE).

---

*Built by DynamIQ Learning LLC.*
