# The Governance Framework (TGF)

> Grounds AI-assisted development in industry-authoritative standards.

When I started shipping real projects with heavy AI assistance, I kept running into the same problem. The code would compile. The tests would pass. It would *look* right. But when I'd dig in, I'd find authentication patterns from 2017, error handling that swallowed every exception, and "best practice" citations that traced back to a Medium article from someone's bootcamp. The AI was producing code that looked senior but wasn't grounded in anything.

What I actually wanted was a senior DevSecOps engineer sitting next to me. Someone who'd been on-call at 3 AM, sat through SOC 2 audits, watched dependencies get compromised. Someone whose first instinct on every line of code was "who could abuse this?" and whose every rule traced back to OWASP, NIST, ISO, or MITRE. Not a blog post. Not a "best practices" listicle. Primary sources.

So I built one.

## What It Is

TGF is a governance framework for AI-assisted development. It encodes senior DevSecOps judgment as enforceable rules grounded in primary authoritative sources: OWASP ASVS 5.0, NIST publications, ISO/IEC 27001/27002, MITRE ATT&CK and ATLAS, RFCs. If a rule can't trace to one of those, it doesn't get to call itself a rule.

Built for solo developers and small teams who use AI heavily and want their work to actually meet industry standards by default, not just look like it does.

## How It Works

Three layers:

1. **CLAUDE.md** — the developer's character. Senior engineer instincts, workflow contract, authority structure. Loads every session.
2. **Skills** — around 75 focused governance units, each with rule-level citations to authoritative sources and anti-pattern catalogs with concrete code examples. Skills load contextually based on what the change actually does, not what the prompt says.
3. **Artifacts** — committed memory the framework maintains: `DECISIONS`, `ROADMAP`, `ERROR-LOG`, `VENDOR-LOG`, `WAIVER-LOG`, `SCHEMA-HISTORY`. Plus gitignored session logs for continuity.

Every coding or planning prompt runs a six-stage workflow: Research → Scope → Plan with Governance → Implement → Four-Pass Review → Commit. The four-pass review is the part most "AI best practices" tools skip. Code Review, Security Audit, Red Team Dry Run, and Holistic Review each run as a distinct pass with its own mental model: craftsmanship, rule compliance, adversarial thinking, project-specific integration.

## What Makes It Different

- **Authoritative sources only.** Every rule cites a specific identifier. OWASP ASVS V3.1.1, NIST SP 800-63B §5.1.1.2. No blog-post-grade citations.
- **Plain-language impact.** Every finding explains what could actually go wrong in real terms, not just "ASVS violation."
- **Mode-aware scaling.** Standards within scope are unconditional. What's *in scope* changes by project mode: exploration, prototype, building, hardening, maintenance.
- **Solo-maintainability as first-class.** Code produced under TGF must be maintainable by one person six months from now. Standard patterns over clever ones. Boring tech over trendy.
- **Silent engagement.** The framework does the work without narrating it. It speaks when there's something worth saying.

## Status

**Phase 4 of 16 in progress.** Foundation phases (Phases 1–3) are complete — repo scaffolding, expanded CLAUDE.md with deeper architecture in `docs/ARCHITECTURE.md`, and the workflow specification at `docs/WORKFLOW.md`. Currently building the three always-on skills (CODE-QUALITY, SECURITY-CORE, CONTINUITY) plus the orchestrator agent that activates them. Not yet ready for adoption.

See [`ROADMAP.md`](./ROADMAP.md) for the full 16-phase build plan and current progress. See [`DECISIONS.md`](./DECISIONS.md) for architectural decisions with full reasoning. Full adopter docs (INSTALL, DESIGN-RATIONALE, how-it-works, glossary, FAQ) land in Phase 15.

If you see something off, drop an issue. Outdated citation, gap in coverage, a rule that doesn't trace cleanly to an authoritative source — anything. I'd rather hear it now than after Phase 15 ships.

## License

MIT — see [LICENSE](./LICENSE).

---

*Built by DynamIQ Learning LLC.*
