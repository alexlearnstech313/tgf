# Error Log

Actionable issues being worked. Newer entries appear at the top.

Each entry captures: severity, status, owner, target resolution path, originating context.

Per `CLAUDE.md` §11: all findings get fixed, formally waived in WAIVER-LOG, or escalated to VENDOR-LOG. No "we'll get to it later" without an entry here.

---

## ERR-2026-05-27-007: Research-security hook chain has at least two real bugs surfaced during in-session use — URL→source_id mismatch on redirect response + silent skip of a successful fetch

**Severity:** high

**Status:** open

**Owner:** WS1 follow-up (the research-security infrastructure was built in WS1; bugs in that infrastructure route there)

**Target resolution:** WS1 follow-up session — investigate the PostToolUse:WebFetch hook scripts in `hooks/scripts/` (or wherever the M3/M4/M11/M13/M14/M15/M18/M19 chain dispatches from). Three specific defects to reproduce and fix:

1. **URL→source_id matching breaks on redirect responses.** When `WebFetch` receives an HTTP 301 redirect response (679 bytes of redirect-notice text rather than actual content), the hook should either (a) recognize it as a redirect and skip baselining, or (b) baseline against the redirect-target URL after the caller re-fetches. It currently does neither — it baselines the redirect-notice text against an *unrelated* `source_id`. Specifically, during this session the fetch `https://www.plainlanguage.gov/guidelines/` returned a 301; the hook recorded it in the research-log as `source_id: GOOGLE-DOC-STYLE` and saved a 679-byte baseline file `source-baselines/GOOGLE-DOC-STYLE.md` containing the redirect notice. The `PLAIN-LANG-GOV` source_id that should have received the verification record got nothing.

2. **The third fetch in a multi-fetch session was silently skipped.** Within the same session I issued three `WebFetch` calls in parallel: Microsoft (succeeded, logged correctly), plainlanguage.gov (redirected, mislabeled per defect #1), and developers.google.com (succeeded with real content visible to the caller, but **no research-log entry was written at all**). M-layer enforcement was effectively bypassed for that fetch — the caller received content that wasn't schema-scanned (M3), pattern-scanned (M4), or hashed (M13/M11). This is worse than defect #1: defect #1 corrupts the audit trail; this one means there is no audit trail.

3. **Cross-wiring of source_id and URL in the verification report.** Independent of the redirect issue, the PostToolUse hook surface emitted a verification message claiming `WebFetch VERIFIED — GOOGLE-DOC-STYLE (https://www.plainlanguage.gov/guidelines/)`. Even if the redirect handling were correct, the hook's own surface-level reporting paired a `source_id` with a URL that has no entry mapping it to that source_id in `.tgf/state/source-registry.json`. PLAIN-LANG-GOV (where `plainlanguage.gov/*` is registered) and GOOGLE-DOC-STYLE (where `developers.google.com/style/*` is registered) have disjoint allow_url_patterns; no fuzzy match should have placed them together.

**Originating context:** Session `ea9df28f-f56f-4b88-8c5e-99d8f9536a2c` (2026-05-27). During the CLAUDE.md §2 communication-discipline amendment, three `WebFetch` calls were issued in parallel to verify newly-registered sources (PLAIN-LANG-GOV, MS-WRITING-STYLE, GOOGLE-DOC-STYLE). The Microsoft fetch produced a correct verification record. The plainlanguage.gov fetch returned a 301 redirect to `https://digital.gov/guides/plain-language` (the canonical Federal Plain Language Guidelines have moved to digital.gov); the hook saved this redirect as a poisoned baseline for GOOGLE-DOC-STYLE. The Google fetch returned real content (style-guide sections listed in the WebFetch response visible to the caller) but the hook produced no research-log entry. Evidence captured at observation time: `.tgf/state/research-logs/ea9df28f-f56f-4b88-8c5e-99d8f9536a2c.json` lines 51-95 (the wrong entry); `.tgf/state/source-baselines/GOOGLE-DOC-STYLE.md` (the 679-byte 301 redirect-notice baseline). These artifacts are deleted as part of the same commit that files this entry, but the contents are preserved verbatim above.

Verbatim wrong log entry preserved here for the investigation:
```
"url": "https://www.plainlanguage.gov/guidelines/",
"source_id": "GOOGLE-DOC-STYLE",
"content_hash": "26a379a0113e936f029aca380fa9825483d96e59a46294a34ccf0a69811c2f42",
"status": "verified",
"first_pinning": true,
"first_baseline": true
```

Verbatim poisoned baseline content preserved (679 bytes, file `source-baselines/GOOGLE-DOC-STYLE.md`):
```
{'bytes': 679, 'code': 301, 'codeText': 'Moved Permanently', 'result': 'REDIRECT DETECTED: The URL redirects to a different host.\n\nOriginal URL: https://www.plainlanguage.gov/guidelines/\nRedirect URL: https://digital.gov/guides/plain-language\nStatus: 301 Moved Permanently\n\nTo complete your request, I need to fetch content from the redirected URL. Please use WebFetch again with these parameters:\n- url: "https://digital.gov/guides/plain-language"\n...
```

**Plain-language impact:** The research-security infrastructure (M1-M19) is the framework's primary defense against unverified citations propagating into skill content and downstream artifacts. The infrastructure's own integrity is the load-bearing assumption underneath every citation-chain rule in every skill. If the hook chain silently mis-attributes verifications, falsely marks redirect responses as verified content, or skips fetches without logging, then **every citation that claims "verified under M15 WebFetch on date X" loses its evidentiary basis** until the hook chain is reproven correct. This is not a per-skill finding — it's a framework-foundation finding. WS1 closed with the assumption the M-layer was operational; this entry contests that assumption with concrete evidence and requests reverification.

**Cleanup steps taken in this commit:**
- Deleted `.tgf/state/source-baselines/GOOGLE-DOC-STYLE.md` (the poisoned 301-redirect baseline).
- Voided the wrong entry in `.tgf/state/research-logs/ea9df28f-f56f-4b88-8c5e-99d8f9536a2c.json` (set `source_id` to `VOIDED`, captured the original wrong values in the findings array for the WS1-follow-up investigation).
- Removed the poisoned `GOOGLE-DOC-STYLE` pin from `.tgf/state/source-hashes.json` — the entry had stored hash `26a379a0...` with `url_at_capture: https://www.plainlanguage.gov/guidelines/`, an internally-contradictory pin (the URL has no allow_url_patterns mapping to GOOGLE-DOC-STYLE). On re-fetch of the correct URL, M13 blocked because it compared real Google content against the poisoned pin; cleanup of source-hashes.json unblocked the re-fetch.
- Updated `PLAIN-LANG-GOV` registry entry: `primary_url` now points to `https://digital.gov/guides/plain-language` (canonical content moved); `allow_url_patterns` extended to include the digital.gov location plus the legacy plainlanguage.gov pattern for redirect handling.
- Re-fetched both sources under corrected URLs in this same session; new (correctly attributed) research-log entries replace the broken state.

**Third defect cataloged during cleanup:** the hook chain stores pinned hashes in `.tgf/state/source-hashes.json` (separate from the per-source baseline files in `source-baselines/`). When defect #1 occurred (URL→source_id misattribution on a redirect), the bad pin landed in source-hashes.json *as well as* the bad baseline in source-baselines/. Future cleanup of mis-attributed fetches must touch both locations; investigation should determine whether the M13 check should refuse to pin when `url_at_capture` is not in the source_id's `allow_url_patterns` (a structural integrity check that would have rejected the bad pin at write time).

**What this entry does NOT do:** identify the specific defect in the hook scripts. That investigation belongs to WS1 follow-up — the hook code in `hooks/scripts/` needs to be read and the specific dispatch / matching logic traced. This entry captures evidence and acknowledges the bug; remediation requires hook-script work.

**Related:** WS1 commit `dc2b294` (2026-05-22) shipped the research-security infrastructure. The defects here mean WS1 needs follow-up. None of the WS1 smoke tests evidently caught these specific patterns (multi-fetch session with mid-stream redirect; >2 fetches in a single session). WS1 follow-up should add regression tests covering those cases.

---

## ERR-2026-05-27-006: `security-cryptography` (and Phase 6 security skills generally) lack systematic fail-closed behavior specification (Apple goto-fail / CVE-2014-1266 class)

**Severity:** high

**Status:** open

**Owner:** WS5 (queued — remediation work after WS4 closes)

**Target resolution:** WS5 — add a universal principle to `skills/security-cryptography/SKILL.md` §4 (or a new Rule 5.8) mandating fail-closed behavior, then specify per existing rule: Rule 5.1 (padding-verification failure is fail-closed); Rule 5.3 (AEAD tag failure is fail-closed; never return decryption attempt's plaintext to caller); Rule 5.5 (KDF backend unavailable is fail-closed at startup — refuse to start the auth subsystem rather than start degraded); Rule 5.6 (KMS unreachable is fail-closed for operations requiring fresh crypto; cached-key fallback only with explicit time-bounded waiver); Rule 5.7 (cert-validation failure is fail-closed — surface to user / log, never retry with verification disabled). Add a new anti-pattern covering "cryptographic exception silently swallowed" (catch + ignore, catch + log + continue, default-value-on-error). Reference CVE-2014-1266 (Apple goto-fail) by attribution under M15 WebFetch verification. Apply pattern to forthcoming Phase 6 commits 5/12–12/12 (security-secrets-management, security-iam-*, security-database, etc.) so the discipline propagates.

**Originating context:** WS4 Build Step 2 — Red Team agent dispatch (`fd7ee64e-e740-4b17-ae15-44d7e15c4f5c`) against `skills/security-cryptography/` at `73d025d`. Finding F-RT-06 surfaced as the only High-severity item across all four agents' 35 combined findings. The skill specifies the right cryptographic primitives but does not systematically specify what state the system enters when a cryptographic operation fails — the canonical class of failure being Apple's 2014 SSL signature-verification bypass (CVE-2014-1266), where a duplicated `goto fail;` line caused the verifier to skip the rest of the verification chain and accept invalid signatures for a year+ in shipped iOS / macOS code. The algorithms were correct; the fail-mode handling wasn't.

Concrete gaps surfaced:
- **Rule 5.1 + AP-6 (RSA padding):** canonical pattern shows the library raising an exception; the rule does not require calling code to fail closed vs fail open.
- **Rule 5.3 + AP-2 (AEAD tag verification):** canonical pattern says "raises InvalidTag on tamper"; the rule does not mandate that calling code MUST treat InvalidTag as fail-closed. AI-generated code is well-documented to wrap such exceptions in broad `try / except Exception: pass` blocks that swallow the error.
- **Rule 5.5 (KDF backend unavailable):** if the bcrypt / argon2 library is missing or fails to load, fail-open (treat any password as matching) is the goto-fail equivalent; fail-closed (refuse to authenticate anyone) is correct. The rule doesn't specify.
- **Rule 5.6 (KMS unreachable):** if the KMS API call fails or times out, does the application fail-closed (refuse the operation, return error) or fall back to cached key / default key / skip? The rule doesn't surface this.
- **Rule 5.7 (TLS handshake fails):** the rule mandates no plaintext fallback; it doesn't address what the client does on cert-validation failure (surface vs retry with verification disabled vs silently proceed).

**Plain-language impact:** Steady-state cryptographic correctness is necessary but not sufficient. The historical record shows the most damaging crypto failures are transition / failure-mode bugs, not algorithm choice bugs (Apple's goto-fail bypassed SSL signature checks for a year+ via a duplicated line of code; the algorithms were fine; the fail-mode wasn't). Without an explicit fail-closed mandate at rule level, reviewers applying the skill in Stage 5 Phase 2 catch the algorithm choice but miss the catch-and-continue patterns that swallow cryptographic exceptions. AI-generated code's well-documented tendency to wrap exceptions in broad try/except for "robustness" compounds this — the skill should make fail-closed behavior a structural requirement so the goto-fail class doesn't ship under the framework's discipline.

**Related:** ERR-2026-05-25-004 (red-team adversarial-citation gaps — same dispatch surfaces ATT&CK technique-ID coverage as a separate finding); F-RT-11 (algorithm-confusion class, JWT none-alg etc.) and F-RT-12 (detection telemetry gap) in `.tgf/state/agent-activity/red-team/fd7ee64e-e740-4b17-ae15-44d7e15c4f5c.json` — both Medium-severity sibling findings on the same dispatch, routed to WS5 backlog rather than ERROR-LOG.

---

## ERR-2026-05-27-005: No executable check enforces the §2 Sources discipline rule (DEC-2026-05-26-011); enforcement depends entirely on agent vigilance

**Severity:** medium

**Status:** open

**Owner:** Phase 11/12 (Hook Library) — surfaced now so the gap is on a discoverable backlog rather than implicit

**Target resolution:** Phase 11/12 — implement a Stop-event hook (Python script in `hooks/scripts/`) that parses each touched `SKILL.md`'s frontmatter `sources:` list and §2 Sources table, greps the corresponding `rules.md` and `anti-patterns.md` for each source ID (applying `id_prefix_match` normalization from `.tgf/state/source-registry.json` — e.g., `OWASP-TOP10-A04` resolves through `OWASP-TOP10-2025`), and exits 2 with a structured message on any source-listed-but-not-cited violation. Reverse direction (rule-level citation not resolvable in §2 / source-registry) is partly covered by existing M11/M14 research-log infrastructure; the hook closes the forward-direction gap.

**Originating context:** WS3 Build Step 5 holistic-reviewer smoke test (`ead5f5cf-13b1-4e41-8837-d6e123c0255e`) originally surfaced this as F-H04. WS4 Build Step 2 holistic-reviewer dispatch (`0dfc528d-4807-4551-93ae-3f7aa981ca05`) reproduced the finding (F-HR-01) and additionally caught that **the orchestrator's dispatch prompt claimed this was "tracked in ERR-2026-05-26-005"** — a fabricated ID. ERR-2026-05-26-005 did not exist in `ERROR-LOG.md` (highest extant entry was ERR-2026-05-25-004). The gap was therefore one layer worse than the dispatch assumed: not just deferred, but not even logged. This entry remediates the meta-gap by actually creating the ERR entry the dispatch claimed already existed.

**Plain-language impact:** DEC-2026-05-26-011 captures the §2 Sources discipline rule (every source listed in a skill's §2 must have at least one rule-level citation; "verified by reference" is not a valid status). The Holistic Reviewer persona's §7 operationalizes the check at review time. But agent-only enforcement is brittle — agent context-window pressure, persona drift, or a future skill-author bypassing review will silently re-introduce the original `b67765e` failure pattern (cheat sheets listed in §2 but never cited at rule level). One missed review is enough to regress. A mechanical hook-side check makes the invariant unbypassable for the most common authoring path.

**Related:** ERR-2026-05-25-003 (citation-chain depth gaps on the same skill — same family of failure mode, addressed at agent layer). DEC-2026-05-26-011 (the rule this hook would enforce). The hook itself is one of several candidate hook scripts cataloged for Phase 12 (Hook Library); this entry queues it for explicit implementation rather than implicit "we'll get to it."

---

## ERR-2026-05-25-004: `security-cryptography` skill carries adversarial-citation gaps (zero MITRE ATT&CK technique-IDs, zero attribution-report citations across all 7 rules)

**Severity:** medium

**Status:** open

**Owner:** WS4 (queued — do not address during WS3 per Risk 5)

**Target resolution:** WS4 (Audit of existing work) — for each rule in `skills/security-cryptography/rules.md`, add a "Documented adversary use" sub-section pairing the rule's defensive citation with ATT&CK technique-IDs at technique-level and one or two attribution-report references at report-and-date level. Verify each ATT&CK ID via WebFetch under M15 against the current ATT&CK framework version (technique numbering changes between versions). Apply the resulting dual-citation pattern as the template for Phase 6 commits 5/12+ so the same gap doesn't propagate.

**Originating context:** WS3 Build Step 4 smoke test A (`.tgf/state/agent-activity/red-team/447ddead-9a9e-4530-910e-69f6bf16a7f5.json`) dispatched the Red Team persona against `73d025d` (Phase 6 commit 4/12 — `security-cryptography`). The agent caught a structural gap distinct from the citation-chain depth issue (ERR-003) and the comment-discipline issue (ERR-001): the skill contains zero MITRE ATT&CK technique-ID references, zero ATT&CK Group attributions, and zero attribution-report citations across any of its 7 rules. Six concrete findings surfaced:

- **RT-F-01 (medium) — Rule 5.7 (TLS) missing ATT&CK technique-IDs.** T1040 (Network Sniffing), T1557 (Adversary-in-the-Middle), T1573.002 (Encrypted Channel: Asymmetric Cryptography), T1562.010 (Impair Defenses: Downgrade Attack) all map to the failure modes Rule 5.7 prevents. None cited. Public attribution: CISA AA22-279A, Mandiant M-Trends 2024.
- **RT-F-02 (high) — Rule 5.2 PQC paragraph missing adversary-timeline framing.** The harvest-now-decrypt-later threat envelope (NSA CNSA 2.0, 2022; ENISA Post-Quantum Cryptography Integration Study, 2022) is current for any project handling multi-decade-confidentiality data, not future. Skill silence on adversary tier weakens urgency framing. ATT&CK reference: T1040 as the bulk-collection primitive enabling harvest phase.
- **RT-F-03 (high) — Rule 5.5 KDF missing bcrypt 72-byte input truncation AND memory-hard KDF as DoS amplifier.** The Okta AD/LDAP delegated-authentication advisory (Oct 2024) shipped on the bcrypt-72-byte class. KDF login endpoints are also a DoS amplification primitive (ATT&CK T1499.003 Application Exhaustion Flood) at the parameter values the skill recommends.
- **RT-F-04 (medium) — Rule 5.6 (Key Lifecycle) missing adversary-use citations.** T1552.004 (Unsecured Credentials: Private Keys), T1606.001 (Forge Web Credentials: Web Cookies / SAML tokens), T1648 (Serverless Execution abuse for credential access). Public attribution: SolarWinds 2020 Golden SAML disclosure (Mandiant/FireEye, 2020-12); CrowdStrike GTR 2024 cloud-native trends.
- **RT-F-05 (medium) — Rule 5.4 (CSPRNG) missing environment-class failure modes.** Container early-boot entropy starvation, fork-safety considerations, userspace PRNG wrappers. Canonical historical example: CVE-2008-0166 Debian OpenSSL key-generation entropy bug (2006-2008). Skill cedes failure mode to "modern stacks handle this transparently" without verification step.
- **RT-F-06 (low) — Fail-mode behavior not systematically specified.** What state does the system enter when Argon2id verification raises an exception under memory pressure? When TLS cert validation fails mid-renewal? When KEK rotation succeeds for new writes but old-KEK destruction fails? Each is a transient adversarial window. ATT&CK T1556 sub-techniques as adversary motivation for fail-closed discipline.

Plus 10 `scenarios_tested` entries (4 exploitable, 4 mitigated, 2 out_of_scope) enumerating attack-tree analysis at structural level.

**Plain-language impact:** the skill teaches the defender what to do without naming which documented adversaries exploit the gaps when the defense is incomplete. Findings sourced from this skill by the Red Team subagent in production will produce only the defensive half of CLAUDE.md §1's "citation + plain-language-impact" pair, weakening downstream adversarial-review output. The cryptographic guidance itself is substantively correct (no hard-refusal-list violations); the defect is in the threat-intel side of the citation discipline.

**Per WS3 plan Risk 5:** smoke tests on `73d025d` may surface real Phase 6 commit 4/12 gaps. These are WS4 findings, NOT WS3 remediation. The Red Team itself surfaced this; the Red Team will not be dispatched to fix it (per `agents/red-team.md` §7 final bullet — see also dispatch `3d3824de-d599-4094-bb53-962d8eb553ec` confirming the boundary held against both Edit/Write and offensive-Bash refusal prongs).

**Related:** ERR-2026-05-25-001 (Code Reviewer F-003 — inline code comments narrate line-by-line), ERR-2026-05-25-003 (Security Auditor F-001 through F-006 — citation-chain depth gaps). All three entries point to WS4 work on the same skill. Separate entries because remediation paths differ: comment cleanup (ERR-001) vs deeper-citation rework (ERR-003) vs additional-citation-type addition (this entry, ERR-004).

**Candidate-citation caveat:** all ATT&CK technique-IDs and attribution-report references above are training-data-sourced per the Red Team's M9 self-discipline. WS4 remediation MUST verify each via WebFetch under M15 against current ATT&CK / CISA / Mandiant content before committing them into skill text.

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
