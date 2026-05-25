# Error Log

Actionable issues being worked. Newer entries appear at the top.

Each entry captures: severity, status, owner, target resolution path, originating context.

Per `CLAUDE.md` §11: all findings get fixed, formally waived in WAIVER-LOG, or escalated to VENDOR-LOG. No "we'll get to it later" without an entry here.

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
