# Error Log

Actionable issues being worked. Newer entries appear at the top.

Each entry captures: severity, status, owner, target resolution path, originating context.

Per `CLAUDE.md` §11: all findings get fixed, formally waived in WAIVER-LOG, or escalated to VENDOR-LOG. No "we'll get to it later" without an entry here.

---

## ERR-2026-05-25-003: `security-cryptography` skill carries citation-chain depth gaps (M9 confirmation-gap pattern manifesting in a control-locking skill file)

**Severity:** high

**Status:** open

**Owner:** WS4 (queued — do not address during WS3 per Risk 5)

**Target resolution:** WS4 (Audit of existing work) — re-fetch OWASP-CHEAT-PS, OWASP-CHEAT-CS, OWASP-ASVS V11, OWASP-ASVS V12, and NIST SP 800-57 Pt 1 Rev 5 under M15-gated WebFetch. Resolve each finding against the live content. Apply the author's own plan-adjustment retroactively to this skill, then ship Phase 6 commits 5/12+ with the discipline pre-applied (fetch ALL cited cheat sheets at Stage 1 rather than relying on memory).

**Originating context:** WS3 Build Step 3 smoke test A (`.tgf/state/agent-activity/security-auditor/6244283b-6953-4eae-8e86-cd3a58d62042.json`) dispatched the Security Auditor persona against `73d025d` (Phase 6 commit 4/12 — `security-cryptography`). The agent caught the exact M9 memory-confirmation-gap pattern the framework was built to detect, surfacing six concrete citation-chain findings the commit's own in-session correction did not catch:

- **F-001 (high) — Rule 5.5 KDF parameters cited at OWASP-CHEAT-PS page level, not section anchor.** Argon2id (m=19 MiB, t=2, p=1), bcrypt (cost 10), scrypt (N=2^17, r=8, p=1), PBKDF2-HMAC-SHA-256 (600k), PBKDF2-HMAC-SHA-512 (220k) quoted verbatim but anchored only at cheat-sheet level. Six months from now the values may drift in the cheat sheet without detection. Remediation: pin to `OWASP-CHEAT-PS#argon2id`, `#bcrypt`, `#scrypt`, `#pbkdf2` section anchors and register the pattern in `source-registry.json`.
- **F-002 (high) — Rule 5.7 statement claims V12.1.4 (OCSP stapling) and V12.3.5 (mTLS) but Citation line (line 99) enumerates only V12.1.1, V12.1.2, V12.2.1, V12.3.1, V12.3.2.** Citation undercounts the rule's claims; refresh against V12 won't trigger on the missing V-IDs.
- **F-003 (medium) — V11.4.3 invoked in Rule 5.1 extended discussion (line 19) and Rule 5.2 statement (line 27) but absent from both Citation lines (lines 15, 29).** Depth-claim unanchored in citation chain.
- **F-004 (medium) — NIST SP 800-57 §5.3 / §6 section anchors with author's own hedge** ("approximate, verify against the publication") in Rule 5.6 extended discussion (line 89). The hedge IS the M9 tell.
- **F-005 (medium) — Rust `rand::thread_rng()` listed as "Forbidden for security purposes" in Rule 5.4 (line 55) with inline hedge contradicting the categorization.** `thread_rng()` in modern `rand` (0.8+) IS a CSPRNG (ChaCha12). Rule is internally contradictory and misclassifies a secure default.
- **F-006 (medium) — OWASP-CHEAT-CS "Key Management" section anchor unverified post-correction** (Rule 5.6 line 85). The in-session correction replaced OWASP-CHEAT-KM with this sub-section citation; the section name and content were not re-verified at section depth.

**Plain-language impact:** the skill that operationalizes cryptographic discipline for downstream Phase 6+ skills carries the exact citation-chain failure pattern the framework was built to prevent. Adopters using this skill as exemplar will absorb the unanchored-citation pattern. The cryptographic guidance itself is substantively correct (no hard-refusal-list violations); the defect is in the rule-to-source citation depth — which is precisely the framework's primary defense layer.

**Per WS3 plan Risk 5:** smoke tests on `73d025d` may surface real Phase 6 commit 4/12 gaps. These are WS4 findings, NOT WS3 remediation. The Security Auditor itself surfaced this; the auditor will not be dispatched to fix it (per `agents/security-auditor.md` §8 — see also dispatch `9a0215f6-ff16-4f1d-92dc-a962fce58745` confirming the boundary held).

**Related:** ERR-2026-05-25-001 covers the same skill's craftsmanship/comment-discipline issue (Code Reviewer F-003 — inline code comments narrate line-by-line). Both entries point to WS4. Separate entries because remediation paths differ (citation-chain rework vs comment cleanup).

---

## ERR-2026-05-25-002: Platform-level `tools:` restriction not empirically validated for code-reviewer (or any review agent)

**Severity:** medium

**Status:** open

**Owner:** Alt (re-run during WS4 under TGF-as-installed-plugin conditions)

**Target resolution:** WS4 (Audit of existing work) — re-run all four review-agent smoke tests once TGF is installed as a Claude Code plugin so the platform enforces `tools: [Read, Grep, Glob, ...]` at dispatch time. Confirm that forbidden tool calls are blocked at the platform layer (Decision M Q4c — undocumented behavior; the docs explicitly direct empirical testing).

**Originating context:** WS3 Build Step 2 (Code Reviewer operationalization). The Build Step 2 + 3 + 4 + 5 smoke tests in WS3 were run via `general-purpose` agent proxy because TGF was not installed as a plugin in the build session. The proxy has full tools, so it could only test **persona-level discipline** (does the agent refuse Edit/Write when prompted), not **platform-level restriction** (does Claude Code block the tool call regardless of persona). Persona discipline held cleanly in the sanity-check transcript at `.tgf/state/agent-activity/code-reviewer/fe72bc41-7610-4afe-9ca6-d723726b33d4.json`. The platform-layer test remains owed.

**Note on Decision M:** the verification recorded in `docs/workstream-3-plan.md` §3 confirmed `tools:` is documented as a strict allow-list and parent permissions cascade. Q4c (malformed/forbidden array behavior) was flagged as undocumented; the smoke-test sanity check was the planned empirical validation. Until that runs under real plugin conditions, the `tools:` restriction is documentation-backed plus persona-discipline-backed, not platform-empirically-backed.

**Plain-language impact:** if Claude Code's `tools:` enforcement turns out to behave differently than docs imply (e.g., silent fallback to inherited tools on malformed array), the four review agents could in principle access tools they aren't supposed to. Persona discipline currently catches this in observed runs, but persona discipline is a defense-in-depth layer, not the primary control.

---

## ERR-2026-05-25-001: `security-cryptography` skill fails its own §7 anti-pattern (inline code comments narrate what the code does line-by-line)

**Severity:** medium

**Status:** open

**Owner:** WS4 (queued — do not address during WS3 per Risk 5)

**Target resolution:** WS4 (Audit of existing work) — Code Reviewer's F-003 finding surfaces during Phase 6 commit 4/12 audit; Implementer dispatches against `skills/security-cryptography/anti-patterns.md` to move per-line narrations into the surrounding "Why It Works" prose, keeping only why-not-what comments inside code blocks. Pattern fix to be propagated as a CODE-QUALITY exemplar for downstream Phase 6 skills (commits 5/12–12/12) so the same anti-pattern doesn't propagate.

**Originating context:** WS3 Build Step 2 smoke test #1 (`6c275871-80b6-48c5-ab6a-8701c6cdf6d6`) dispatched the Code Reviewer persona against `73d025d` (Phase 6 commit 4/12 — `security-cryptography`). Finding F-003: sampled inline comments in `anti-patterns.md` include `// CSPRNG; new IV per call` (line 188), `# 12-byte CSPRNG nonce — collision probability negligible up to ~2^32 messages` (line 173), `# Custom alphabet via secrets.choice` (line 305). These narrate what the code does in plain English alongside the code — which the skill's own §7 (`anti-patterns.md`'s anti-pattern catalog header) and the Code Reviewer persona's §4 both list as an AI-generated code smell to flag in review.

**Plain-language impact:** the skill teaches downstream skill-authors and adopter projects that line-by-line code-narrating comments are an AI-smell to reject. The skill's own files demonstrate the smell. Adopters learning by example will absorb the contradicted pattern. The finding does not introduce a security defect in the skill's prescriptive content (the cryptographic guidance is correct); the defect is in the craftsmanship discipline of the skill's own code examples.

**Per WS3 plan Risk 5:** smoke tests on `73d025d` may surface real Phase 6 commit 4/12 gaps. These are WS4 findings, NOT WS3 remediation. Captured here for WS4 pickup.

---
