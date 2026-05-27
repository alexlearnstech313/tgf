# Workstream 5 — Plan Backlog (Remediation Catalog)

> **Workstream:** WS5 (per `docs/framework-hardening-plan.md` §3.5)
>
> **Status:** ⏳ Backlog accumulation in progress — populated incrementally during WS4 per-artifact audits
>
> **Purpose:** Catalog of Medium and Low severity findings surfaced by WS4 audits, structured for WS5 remediation work-package planning. Critical and High findings route directly to `ERROR-LOG.md`; this document is the rest.

---

## §1 Scope and Routing Convention

Per `docs/workstream-4-plan.md` Decision D, WS4 findings route by severity:

- **Critical / High** → `ERROR-LOG.md` entry per finding (immediate visibility).
- **Medium / Low** → this document (structured backlog).
- **Activity-log transcripts** (under `.tgf/state/agent-activity/`) preserve ALL findings regardless of routing — the split is about visibility, not preservation.

WS5's plan will categorize this backlog into remediation work-packages, sequence them, and ship per-skill (or per-cluster) remediation commits. This document is the starting input for WS5's own Stage 1 research and Stage 2 scope.

## §2 Backlog Format

Each finding row carries:

- **ID** — original finding ID from the dispatch transcript (e.g., F-CR-02, T1-001).
- **Severity** — Medium or Low.
- **Target artifact** — file or commit affected.
- **Origin** — dispatch UUID + role + audit-target context.
- **Description** — concise statement.
- **Remediation hint** — concrete next step (full remediation lives in the transcript).
- **Priority hint** — work-package grouping suggestion for WS5 planning.

## §3 Per-Audit-Target Sections

### §3.1 Target 1 — `skills/security-cryptography/` (Audit completed 2026-05-27, commit pending)

**Audit context:** WS4 Build Step 2 — first per-artifact audit per Decision K validation gate. Track 1 (mechanical compliance) + Track 2 (four-agent dispatch via general-purpose proxy). Validation gate result: 5 of 5 WS3-known findings reproduced — methodology validated, proceed to remaining 18 targets.

**Activity logs (Track 2 dispatch transcripts):**
- code-reviewer: `.tgf/state/agent-activity/code-reviewer/76e2f99c-b22d-426b-a6f9-3e06dfaf3495.json`
- security-auditor: `.tgf/state/agent-activity/security-auditor/71a0e7f9-069e-4a88-bc83-8f55e36bf3c5.json`
- red-team: `.tgf/state/agent-activity/red-team/fd7ee64e-e740-4b17-ae15-44d7e15c4f5c.json`
- holistic-reviewer: `.tgf/state/agent-activity/holistic-reviewer/0dfc528d-4807-4551-93ae-3f7aa981ca05.json`

**Routed to ERROR-LOG.md:** ERR-2026-05-27-005 (hook-side §2 Sources fitness function — surfaced by F-HR-01); ERR-2026-05-27-006 (fail-closed mandate — goto-fail / CVE-2014-1266 class, surfaced by F-RT-06 High-severity).

**Routed here (Medium/Low — 34 findings):**

#### Track 1 — Mechanical compliance findings

| ID | Severity | Target | Description | Remediation hint | Priority hint |
|---|---|---|---|---|---|
| T1-001 | Medium | `skills/security-cryptography/SKILL.md` §2 | Five §2 sources lack rule-level citation: OWASP-TOP10-A04, NIST-SP-800-175B, FIPS-197, FIPS-180-4, FIPS-202. Per DEC-2026-05-26-011 §1: either remove from §2 OR add explicit citations to specific rules (AES → Rules 5.1/5.3; SHA-2 → Rule 5.1; SHA-3 → Rule 5.1). | Per-source decision: remove vs add to rule. Top10-A04 narrative-only is borderline; FIPS-197/180-4 should likely be added to Rule 5.1 Citation lines; NIST-SP-800-175B may be removable given content is also in ASVS V11. | Bidirectional traceability cleanup (cluster with similar gaps in other audit targets) |
| T1-002 | Low | `skills/security-cryptography/SKILL.md` frontmatter ↔ §2 table | Frontmatter `sources:` list shows `(verified DATE)` parenthetical only on first 5 entries; §2 table claims `2026-05-22` for all 17. Asymmetry between surfaces. | Either annotate all frontmatter entries with verification dates or drop the parenthetical from the first 5 — pick one convention and apply uniformly. | §2/frontmatter convention cleanup |
| T1-003 | Low | `skills/security-cryptography/anti-patterns.md` AP-6 (line 605) ↔ §2 table | CWE-780 cited at rule level but §2 Sources table lacks a CWE-780 row. Resolves via source-registry `MITRE-CWE` umbrella entry so DEC-011 Clause 1 technically satisfied; convention is inconsistent. | Either add CWE-780 row to §2 (matches per-CWE listing convention) or consolidate all five CWEs into one MITRE-CWE umbrella row in §2 (opposite convention). | §2/frontmatter convention cleanup |

(T1-004 — M9 author hedge at rules.md:89 — was Medium severity but reproduces ERR-2026-05-25-003 F-005 from WS3; it is tracked there, not duplicated here.)

#### Code-reviewer findings (Track 2)

| ID | Severity | Target | Description | Remediation hint | Priority hint |
|---|---|---|---|---|---|
| F-CR-02 | Medium | `anti-patterns.md` AP-4 Python `verify_password` (lines 406-414) | Dead-code branching: both `return True` legs return same value; `check_needs_rehash` result discarded; function contract `bool` can't deliver on the rehash signal the comment promises. Inconsistent with AP-5 Node bcrypt pattern which returns `{matches, needsRehash}` correctly. | Change return type to `tuple[bool, bool]` matching Python AP-5 pattern (lines 515-524). | Per-skill craftsmanship cleanup |
| F-CR-03 | Medium | `skills/security-cryptography/SKILL.md` frontmatter + §2 | 12-month refresh cadence asserted but no operational refresh-procedure documented. Maintainer in May 2027 has no checklist of which sources to recheck or how to propagate parameter updates from cheat-sheet refresh → rules.md → anti-patterns.md code examples. | Add §10 "Maintenance" section (~15-20 lines): refresh procedure, parameter-bearing rules needing recheck, propagation map. Anchor with `<!-- SECTION: maintenance -->`. | Refresh-discipline pattern (cross-target — likely applies to all skills) |
| F-CR-04 | Low | `SKILL.md` §5 Rule 5.2 title (line 182) | Title conjoins two separable disciplines ("128-bit Minimum Security Strength; Cryptographic Agility for Migration"). Body bundles them but consumers often need only one half. | Tighten name to one concept; treat the other as implementation strategy in rule body. | Per-skill craftsmanship cleanup |
| F-CR-05 | Low | `SKILL.md` §9 Subagent Context lines 293-306 | Cross-skill web enumerates 11 forward-references to skills that don't exist yet. Accurate to build plan but unverifiable today; risks drift when downstream skills ship with different choices. | Mark forward-references explicitly (`Foundation for X — verify cross-reference accuracy when commit lands`) or maintain a back-validation checklist at downstream-skill commit time. | Cross-skill discipline pattern |
| F-CR-06 | Low | `anti-patterns.md` AP-7 canonical pattern (lines 720-722, 738-739) | Variable names (`ENCRYPTION_KEY`, `SIGNING_KEY`, `SESSION_TOKEN_KEY`) duplicate HKDF info parameter strings; comment at 738-739 narrates what code at 735-736 does. | Show dispatch table or delete redundant comment; tighten example to model less duplication. | Per-skill craftsmanship cleanup |

#### Security-auditor findings (Track 2)

| ID | Severity | Target | Description | Remediation hint | Priority hint |
|---|---|---|---|---|---|
| F-SA-07 | Medium | `anti-patterns.md` AP-7 line 696 | NIST SP 800-57 §5.2 cited in AP-7 "Source for failure mode"; this is the third section claim in same publication after Rule 5.6 §5.3 + §6 (T1-004). Rule 5.6 hedge applies transitively — §5.2 also citation-unanchored until refetched. | Bundle into NIST SP 800-57 refetch task with T1-004 / F-SA-04. Verify §5.2, §5.3, §6 under one WebFetch operation; update all three citation sites. | Citation-chain refetch cluster |
| F-SA-08 | Low | `rules.md` Rule 5.5 Extended Discussion (line 75) | Second M9 confirmation-gap signal beyond T1-004: "verify per release" hedge in Rule 5.5. Two hedges in one skill is a pattern. | Decide: re-verify and remove hedge, OR convert to structured "verified-on DATE; refresh-recommended DATE" qualifier. | M9 hedge cleanup |
| F-SA-09 | Low | `anti-patterns.md` summary table (lines 973-975) vs `SKILL.md:267` and `SKILL.md:303` | Severity inconsistency: summary table marks AP-2/3/4 as Critical; SKILL.md:303 says "close to hard-refusal — strong advocacy" (i.e., High). Orchestrator routing gets contradictory signals. | Reconcile severity vocabulary: either downgrade summary table to High (preferred — defensible per persona §3) or upgrade SKILL.md:303 to "hard-refusal" (would require framework-level justification). | Severity calibration cleanup |
| F-SA-10 | Low | `rules.md` Rule 5.4 plain-language impact (line 59) + `anti-patterns.md` AP-3 Why It Fails (line 265) | Load-bearing technical claims about V8 xorshift128+, Mersenne Twister state, java.util.Random 48-bit state — none carry source citation. Claims are implementation details of open-source codebases. | Either add citations to V8 source / academic paper, or soften language to remove specific algorithm names. | Citation hygiene cleanup |

#### Red-team findings (Track 2)

| ID | Severity | Target | Description | Remediation hint | Priority hint |
|---|---|---|---|---|---|
| F-RT-07 | Medium | `rules.md` Rule 5.4 + Rule 5.5 + Rule 5.1 | Side-channel discipline mentioned in Rule 5.4 Extended Discussion but not systematic. Gaps: Rule 5.5 doesn't mandate library `verify()` over manual byte-by-byte comparison; Rule 5.1 doesn't mention AES-NI side-channel families; Rule 5.3 doesn't address chosen-ciphertext oracle (Lucky-13 class). | Promote constant-time comparison from parenthetical to rule-level requirement for all security-relevant equality. Add Rule 5.1 paragraph on side-channel resistance via AES-NI / Crypto Extensions. Add Rule 5.3 paragraph on uniform error responses. | Side-channel discipline pattern |
| F-RT-08 | Low | `SKILL.md` §4 first principle (line 158) | "Use library cryptography" principle addresses wrong-implementation class but not supply-chain attack surface on libraries themselves (compromised packages, malicious maintainers, typosquatting). | Add cross-reference to security-supply-chain (Phase 6 commit 9/12) at §4 first principle; add forward reference at §9 Cross-skill web. | Supply-chain cross-skill cohesion |
| F-RT-09 | Medium | `rules.md` Rule 5.7 + Rule 5.6 | No coverage of assumed-breach host-adversary scenarios: service-account credential theft from env vars/config; kernel memory access; KMS API-key exfiltration; process memory disclosure (Heartbleed class). | Add Universal Principle to §4: "Cryptography assumes host is trustworthy; assumed-breach defense requires additional discipline." Cross-ref HSM/KMS, memory hygiene, security-secrets-management, security-data-encryption. | Defense-in-depth / threat-model expansion |
| F-RT-10 | Low | `rules.md` Rule 5.3 Extended Discussion + `anti-patterns.md` AP-2 Canonical Pattern | AES-GCM 2^32 messages-per-key boundary named but not operationalized. No mention of TLS 1.3 automatic key-update mechanism; no application-level per-key counter discipline; AES-GCM-SIV mentioned briefly but not surfaced for high-volume contexts. | Add Rule 5.3 subsection on per-key message-count discipline. AP-2: add code example showing message-count tracking + DEK rotation triggered by count. Add §2 sources for RFC 5116 + RFC 8452. | Per-key counter discipline |
| F-RT-11 | Medium | `rules.md` Rule 5.1 + forward-scope to security-iam-sessions | Algorithm-confusion attack class unaddressed: JWT none-algorithm (CVE-2015-9235); RS256/HS256 confusion; ECDSA psychic signatures (CVE-2022-21449). Rule covers signing-side; verifier-side algorithm pinning unaddressed. | Add Rule 5.1 Extended Discussion paragraph on signature-verification discipline (verifier-side algorithm pinning). Add AP-10 covering algorithm-confusion. Add §2 sources for CVE-2015-9235, CVE-2022-21449, OWASP JWT Cheat Sheet. | Algorithm-confusion class (high-leverage — affects JWT broadly) |
| F-RT-12 | Low | `SKILL.md` (no §-level coverage) + `rules.md` Rule 5.6 | Seven rules entirely preventive; none address detection/observability. When cryptographic operation fails, what events does system emit? Without detection, fail-mode handling blocks attack but leaves no record for monitoring. | Add §10 (or extend §8) covering detection/observability discipline: cryptographic operations emit structured events for failures. Cross-ref security-logging + security-detection-monitoring. Per-rule "detection signal" column in summary tables. | Detection/observability cross-skill cohesion |

Red-team also surfaced **F-RT-01** (zero ATT&CK technique-IDs across all 7 rules) as a Medium reproduction of ERR-2026-05-25-004; that's tracked in the existing ERR entry, not duplicated here. F-RT-02 through F-RT-05 are similarly reproductions tracked in ERR-2026-05-25-004's sub-finding catalog.

#### Holistic-reviewer findings (Track 2)

| ID | Severity | Target | Description | Remediation hint | Priority hint |
|---|---|---|---|---|---|
| F-HR-03 | Medium | `SKILL.md` §2 footer (lines 121-122) + `templates/SKILL.md.template` | The DEC that captures the §2 Sources discipline (DEC-2026-05-26-011) was authored after the skill that motivated it. Skill doesn't reference the DEC; template doesn't either. Decision trail broken from artifact → DEC. | Amend SKILL.md §2 footer to reference DEC-2026-05-26-011. Update `templates/SKILL.md.template` so future skill-authors start under the convention. | Decision-trail discipline (cross-target — applies to all skills authored before DEC-011) |
| F-HR-04 | Medium | `SKILL.md` frontmatter line 71 | Uniform 12-month refresh-recommended across all 17 sources, but sources update at radically different cadences (NIST FIPS publication-stable; OWASP ASVS yearly-ish; OWASP Cheat Sheets continuous). Control-locking parameter values in OWASP-CHEAT-PS most likely to update within 12-month window. | Two-tier refresh-recommended convention: primary (12 months) for stable sources; parameter-refresh-recommended (3-6 months) for cheat-sheet sources defining control-locking parameters. Alternative: §2 annotation noting cheat-sheet point-in-time pins. | Refresh-cadence pattern (cross-target — affects all skills citing cheat sheets) |
| F-HR-05 | Low | `SKILL.md` frontmatter cross-skill comparison (e.g., security-cryptography vs security-input-validation) | Phase 6 skills have staggered last-generated / refresh-recommended dates (per-commit drift). Framework-health refresh tracking sees smeared dates rather than batched phase boundaries. | Convention candidate: align refresh-recommended dates to phase boundaries ("all Phase 6 refresh 2027-Q2") rather than per-skill commit dates. | Refresh-cadence pattern (framework-level convention) |
| F-HR-06 | Low | `SKILL.md` §9 Subagent Context lines 296-302 + `rules.md` Rule 5.6 + `anti-patterns.md` AP-7 | Forward-prescription beyond clean KEK/DEK boundary: §9 prescribes that security-iam-sessions will use Ed25519/RSA-PSS, security-iam-authentication will use Rule 5.5. Soft-commitment downstream skills will have to either honor or explicitly deviate. | At Phase 6 closeout commit 12/12, revisit security-cryptography §9 forward-prescriptions; downgrade any that over-constrain actual downstream implementations. | Phase 6 closeout consideration |
| F-HR-07 | Low | `rules.md` Rule 5.5 (line 69) + `anti-patterns.md` AP-4 (lines 401, 437-441) + AP-5 (lines 474, 484, 494, 513, 531, 558-560) | KDF parameter values (Argon2id m=19/t=2/p=1, bcrypt 10/12, scrypt N=2^17, PBKDF2 600k) appear at 4-6 separate locations with subtle phrasing differences. 4-6 maintenance touch-points when OWASP-CHEAT-PS bumps parameters. | Either extract canonical parameter table into single source-of-truth (`parameters.md` reference file per DEC-2026-05-19-008 pattern) referenced from Rule 5.5 + AP-4 + AP-5, or add `<!-- PARAM: argon2id-memory-cost --> 19456` marker pattern for mechanical search-and-replace. | Parameter-pinning pattern (cross-target) |

## §4 Cross-Target Patterns (To Be Populated)

As WS4 completes additional audit targets, cross-target patterns surface here. Initial observations from Target 1 audit suggest the following patterns may recur across other Phase 6 skills:

- **Forward-reference discipline (F-CR-05, F-HR-06)** — every Phase 6 skill that forward-references not-yet-shipped skills should mark those references explicitly or maintain a back-validation checklist.
- **Refresh-cadence discipline (F-CR-03, F-HR-04, F-HR-05)** — uniform 12-month refresh is too coarse for continuously-updated sources; multi-tier convention or per-source annotation needed.
- **Decision-trail discipline (F-HR-03)** — skills authored before retroactive DECs should be backfilled with DEC references; templates updated to bind future skill-authors.
- **Severity-vocabulary discipline (F-SA-09)** — calibration between in-skill severity tables and persona-default severity gradient may diverge in other Phase 6 skills.
- **Citation-chain depth (T1-001, F-SA-01 through F-SA-07)** — per-sub-rule citation vs page-level citation is a high-leverage cleanup likely repeating across Phase 6 commits 1/12-3/12.

WS5 plan v1 will use the populated cross-target patterns to structure work-packages.

## §5 Cross-References

- `docs/workstream-4-plan.md` — WS4 spec that produced these findings.
- `ERROR-LOG.md` — Critical/High findings from WS4 (the visible-now backlog).
- `DECISIONS.md` DEC-2026-05-26-011 — §2 Sources discipline applied retroactively by WS4 mechanical checks.
- `.tgf/state/agent-activity/<role>/` — full dispatch transcripts (gitignored; contain ALL findings regardless of routing).
- `docs/framework-hardening-plan.md` §3.5 — WS5 spec (this document feeds WS5's Stage 1 research).
