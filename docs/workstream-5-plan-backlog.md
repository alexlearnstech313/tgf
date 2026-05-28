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

### §3.2 Target 2 — `skills/security-error-handling/` (Audit completed 2026-05-27, commit pending)

**Audit context:** WS4 Build Step 3 Target 1 (per-skill commit 3/12). Same two-track methodology as Target 1. No Decision K validation gate (no prior smoke-test findings on this skill to reproduce; methodology validated by Target 1 already). Track 2 dispatched all four agents per Decision E.

**Activity logs (Track 2 dispatch transcripts):**
- code-reviewer: `.tgf/state/agent-activity/code-reviewer/99e1a07d-4761-4422-99ce-37a08ebb9201.json`
- security-auditor: `.tgf/state/agent-activity/security-auditor/d581ba0a-dedb-4c31-9350-a79ac36205d4.json`
- red-team: `.tgf/state/agent-activity/red-team/40793498-2ccc-4332-a3d5-becf57928be4.json`
- holistic-reviewer: `.tgf/state/agent-activity/holistic-reviewer/b6d5d93a-a969-44e3-8f3b-99344f7c424c.json`

**Routed to ERROR-LOG.md:** ERR-2026-05-27-008 (High — adversary-triggered exception threat model gap, from F-RT-EH-02); ERR-2026-05-27-009 (High — Rule 5.5 detection-evasion via low-rate probing, from F-RT-EH-05).

**Routed here (Medium/Low — 24 findings):**

#### Track 1 — Mechanical compliance findings

| ID | Severity | Target | Description | Remediation hint | Priority hint |
|---|---|---|---|---|---|
| T1-EH-001 | Low | `SKILL.md` frontmatter ↔ §2 table | Frontmatter shows `(verified DATE)` only on first 5 entries; CWE entries 6-9 lack the parenthetical despite §2 table claiming `2026-05-22` for all 9. **Cross-target pattern confirmed** — same asymmetry as T1-002 from security-cryptography. | Harmonize convention across both surfaces. Cross-target backlog work-package. | §2/frontmatter convention cleanup (CROSS-TARGET) |
| T1-EH-002 | Medium | `SKILL.md` §2 vs `rules.md` / `anti-patterns.md` | `OWASP-TOP10-A09` listed in §2 as "cross-reference" but never cited at rule level. `CWE-388` mentioned in §7 narrative as "pillar" but never cited in any Citation line. **Cross-target pattern** — same failure mode as T1-001 from security-cryptography. | Per-source decision: remove from §2 OR add to specific rule citations. | Bidirectional traceability cleanup (CROSS-TARGET) |

#### Code-reviewer findings (Track 2)

| ID | Severity | Target | Description | Remediation hint | Priority hint |
|---|---|---|---|---|---|
| F-CR-EH-01 | Medium | `anti-patterns.md:390, :842` | TS code blocks call `logger.warning(...)` — Python API name. TS ecosystem (winston, pino) uses `.warn(...)`. Won't compile/run. | Change two lines to `logger.warn`. Spot-check other long TS blocks. | Per-skill bug fix (high-priority — broken example code) |
| F-CR-EH-02 | Medium | `anti-patterns.md` AP-1 lines 45 vs 108 | Webhook signature verifier silently changes return type from `boolean` to `Event` between anti-pattern and canonical. Contract change buried in inline comment. Migration would break every existing caller. | Either keep boolean OR explicitly flag contract change in §Why It Works. | Per-skill craftsmanship cleanup |
| F-CR-EH-03 | Medium | SKILL.md + rules.md + anti-patterns.md (multiple) | 9 forward-references to unbuilt downstream skills (security-logging × 5, security-iam-authentication × 2, security-incident-response, ops-observability). **Cross-target pattern** — same as F-CR-05 from cryptography. | Maintain cross-skill boundary registry, OR `forward-reference: pending` markers. | Forward-reference discipline (CROSS-TARGET) |
| F-CR-EH-04 | Medium | SKILL.md frontmatter:58-59 | Uniform 12-month refresh for 9 sources of very different cadences (Cheat Sheet continuous, RFC 7807 stable since 2016, CWE entries stable per-entry). **Cross-target pattern** — same as F-CR-03 from cryptography. | Per-source cadence in `sources:` block. | Refresh-cadence discipline (CROSS-TARGET) |
| F-CR-EH-05 | Low | SKILL.md:163-164 + rules.md:53 | Rule 5.4 title lists three mechanisms ("Circuit Breakers, Timeouts, Secure Graceful Degradation") rather than naming the principle. Rule 5.1 / 5.3 / 5.7 are principle-first. | Rename to principle-first (e.g., "External Dependencies Fail Closed for Security; Degrade Gracefully Only for Non-Security Data"). | Per-skill craftsmanship cleanup |
| F-CR-EH-06 | Low | anti-patterns.md:47 | AP-1 TS uses `stripe.webhooks.constructEvent(...) !== null` as truthy check, but Stripe SDK throws-on-invalid / returns-Event — never returns null. Teaches wrong SDK API contract. | Replace dead `!== null` check; use library's actual contract. | Per-skill bug fix |
| F-CR-EH-07 | Low | SKILL.md:113 §3 Discovery | Python discovery regex includes `None` as fail-open match; returning `None` from a security check is typically fail-closed. TS analogue has same issue with `null`. False positives. | Drop `None`/`null` from regexes; note that absence-vs-error distinction requires Phase-2 review of caller treatment. | Per-skill discovery-command fix |

#### Security-auditor findings (Track 2)

| ID | Severity | Target | Description | Remediation hint | Priority hint |
|---|---|---|---|---|---|
| F-SA-EH-01 | Medium | rules.md Rules 5.2 + 5.6 + AP-2 source line | OWASP-CHEAT-EH cited at page level in 3 places. Cheat sheet has named sections supporting `§<section-name>` depth per DEC-011 Clause 2. **Cross-target pattern** — same as F-SA-01 (OWASP-CHEAT-PS) from cryptography. | Refetch OWASP-CHEAT-EH under M15; update citations to section anchors. | Citation-chain depth (CROSS-TARGET) |
| F-SA-EH-02 | Medium | SKILL.md §2 footer vs Rule 5.6 Citation + Rule 5.5 prose + AP-5 | SKILL.md §2 footer says "V16.1–V16.4 sub-rules are scoped to security-logging." Contradicted: (a) Rule 5.6 cites V16.2.1 (in V16.2); (b) Rule 5.5 prose + AP-5 reference V16.3.4 (in V16.3) but V16.3.4 not in Rule 5.5 Citation. | Option A: amend §2 footer to allow V16.2/V16.3 for non-logging claims + add V16.3.4 to Rule 5.5 Citation. Option B: tighten Rule 5.6 to V16.5.1 + defer V16.3.4 to security-logging. | Per-skill citation cleanup |
| F-SA-EH-03 | Medium | SKILL.md §2 line 91 + Rule 5.2 + anti-patterns.md AP-2 lines 184-260, 266 | RFC 7807 cited despite RFC 9457 obsoleting for HTTP API problem-details. anti-patterns.md says "updated to 9457 in 2023" but RFC 9457 was published 2024-07 (factual date error = M9 confirmation-gap tell). RFC-9457 not in source-registry. | Add RFC-9457 to source-registry; switch §2 to 9457 as current; correct date in anti-patterns.md. | Per-skill citation currency |
| F-SA-EH-04 | Medium | SKILL.md §9 line 276 + anti-patterns.md AP-1, AP-4, Summary | **Framework-level question.** AP-1 (swallow-and-allow in security path) and AP-4 (default-permit on external-service failure) are structurally identical to CLAUDE.md §5 hard-refusal entries. Skill self-describes as "close to hard-refusal." The "close to" is the gap — framework should not have a "close to hard-refusal" category. | Option A: amend CLAUDE.md §5 to add "Security checks that fail open on exception or dependency failure." Option B: route AP-1-in-production-security-path and AP-4-on-auth as Critical/hard-refusal in skill. | **Framework-level decision required** (CLAUDE.md §5 amendment candidate) |
| F-SA-EH-05 | Low | rules.md Rule 5.2 Statement line 27 | CWE-209 disclosure list misses side channels: error-code classification enabling enumeration (USER_NOT_FOUND vs INVALID_PASSWORD); timing differences; response-size/shape differences; HTTP status-code differences. | Extend Rule 5.2 to add response-equivalence (timing/size within noise floor for semantically-equivalent failures). | Per-skill rule completeness |
| F-SA-EH-06 | Low | anti-patterns.md AP-5 lines 634-643, 693 | Node `uncaughtException` recommendation (`setTimeout(() => process.exit(1), 1000)` for log flush) is correct Node.js community guidance but cited as if OWASP-derived. Unanchored. | Add Node.js core docs as Tier 3 ecosystem reference, OR soften "recommended pattern" wording. | Per-skill citation hygiene |

#### Red-team findings (Track 2)

| ID | Severity | Target | Description | Remediation hint | Priority hint |
|---|---|---|---|---|---|
| F-RT-EH-01 | Medium | All 7 rules + 9 APs | Zero ATT&CK technique-IDs across the skill. AP-2 → candidate:T1592.004 + T1589; AP-1/AP-4 → candidate:T1556; AP-5 → candidate:T1592; AP-7 → candidate:T1110. **Cross-target pattern** — same as F-RT-01 from cryptography. | Add Adversary Mapping section per-rule technique-IDs. Verify under M15 WebFetch. | ATT&CK technique-ID coverage (CROSS-TARGET) |
| F-RT-EH-03 | Medium | rules.md Rule 5.4 + AP-4 | Adversary deliberately INDUCES external-service failure (DDoS auth, DNS hijack secret store, network partition) to reach AP-4 fall-back. No detection requirements for sustained fall-back firing. | Add detection requirement: sustained fall-back firing needs alert. Cross-ref security-detection-monitoring (Phase 7). | Detection / observability discipline |
| F-RT-EH-04 | Medium | rules.md Rule 5.2 + anti-patterns.md AP-2 | Timing/size/status-code side channels survive generic-message discipline. CWE-203 (Observable Discrepancy) not cited in skill. AP-4 canonical names failing component ("Authentication is temporarily unavailable") — contradicts Rule 5.2 (also F-RT-EH-07). | Add CWE-203 to §2. Extend Rule 5.2 with response-equivalence. Cross-ref security-cryptography constant-time comparison. | Per-skill rule completeness |
| F-RT-EH-06 | Medium | rules.md Rule 5.7 + anti-patterns.md AP-6 | Saga compensating-action failure unaddressed. AP-6 canonical has no try/catch on compensating delete. Adversary-induced race conditions during compensating window not surfaced. | Extend Rule 5.7: mandate idempotent compensating actions + failure-path emits ops-alert + durable marker. Update AP-6 with explicit try/catch on compensating action. Add AP-10 for "compensating-action-with-no-failure-mode." | Per-skill rule completeness |
| F-RT-EH-07 | Low | anti-patterns.md AP-4 canonical (lines 496-504) | AP-4 canonical returns "Authentication is temporarily unavailable" — names failing component, recon fuel. Contradicts Rule 5.2 generic-message. | Update to truly generic 503: "Service temporarily unavailable. Please retry or contact support with reference ID X." Component identification only in server-side log. | Per-skill canonical-pattern fix |

#### Holistic-reviewer findings (Track 2)

| ID | Severity | Target | Description | Remediation hint | Priority hint |
|---|---|---|---|---|---|
| F-HR-08 | Medium | `.claude/hooks/lib/hook_research_posttool_webfetch.py` + skills/**/SKILL.md §2 | §2 Sources bidirectional invariant has no fitness function after ERR-007 fix (the fix addressed URL→source_id race, redirect, structural guards — NOT the §2-to-rule-level traceability). **Cross-target pattern confirmed** — same as F-HR-01 from cryptography. | Path A (lightweight): WAIVER-LOG. Path B (medium): citation_parser.py companion. Path C (full): extend git_precommit_check.py. | Fitness-function gap (CROSS-TARGET — framework-wide) |
| F-HR-09 | Low | SKILL.md §2 footer (this skill + security-cryptography) + skill template | DEC-2026-05-26-011 explicitly asks future skills to reference it. Neither security-error-handling nor security-cryptography references it. **Cross-target pattern confirmed** — same as F-HR-03 from cryptography. | One-line addition to both skills' §2 footers. Capture as skill-template requirement. | Decision-trail discipline (CROSS-TARGET) |
| F-HR-10 | Medium | skills/security-core/SKILL.md line 180 | **NEW cross-artifact-drift finding type.** SECURITY-CORE Top 10:2025 → Rule mapping table lists security-error-handling as "(Phase 7)" but skill / plan / commit position it as Phase 6 commit 3/12. Stale forward-reference. | Update line 180 from "(Phase 7)" to "(Phase 6)". Sweep skills/security-core/ for other phase forward-references. | Cross-artifact phase-position sweep (new dimension) |
| F-HR-11 | Low | SKILL.md §1 + §2 footer + §8 + §9 (multiple) | 5 forward-prescriptions to unbuilt downstream skills (security-logging × 2, security-iam-authentication, security-incident-response, ops-observability). **Cross-target pattern confirmed** — same as F-HR-06 from cryptography. | Phase 6 closing checklist: grep skills/security-*/ for `Phase 6 commit N/12` references; verify against actual shipped names + commit numbers. | Forward-prescription discipline (CROSS-TARGET) |
| F-HR-12 | Low | SKILL.md frontmatter | Uniform 12-month refresh for heterogeneous sources. **Cross-target pattern confirmed** — same as F-HR-04 from cryptography. | Per-source cadence OR uniform-cadence with §2 footer note. | Refresh-cadence discipline (CROSS-TARGET) |
| F-HR-13 | Low | SKILL.md §2 line 91 vs anti-patterns.md AP-2 line 266 | RFC 7807 vs 9457 conscious deferral IS documented — but in AP-2 considerations, not at §2 surface. | One sentence to §2 footer surfacing the deferral. | Per-skill decision-trail polish |
| F-HR-14 | Informational | SKILL.md §1 lines 76-77 (positive note, no action) | POSITIVE NOTE: Foundation-vs-extension positioning of Rule 5.1 vs SECURITY-CORE Rule 5.2 is canonical example. Specific-vs-general, not extension-and-extended. | No action this commit. At quarterly framework-health: add inverse cross-reference from SECURITY-CORE Rule 5.2 to Rule 5.1. | Framework-health quarterly polish |

## §4 Cross-Target Patterns (Updated 2026-05-27 after Target 2 audit)

With two of 19 audit targets complete, the following patterns are now **CONFIRMED cross-target** (observed on both security-cryptography and security-error-handling). These should be remediated as a class in WS5, not per-skill:

1. **§2 bidirectional traceability invariant has no automated enforcement.** T1-001 + T1-EH-002 + F-HR-01 + F-HR-08. Hook-side fitness function tracked in ERR-2026-05-27-005 + repeated. Most leverage: build the hook.
2. **§2/frontmatter verification-date asymmetry.** T1-002 + T1-EH-001. Trivial cosmetic fix; do across all Phase 6 skills in one pass.
3. **Forward-reference discipline.** F-CR-05 + F-CR-EH-03 + F-HR-06 + F-HR-11. Phase 6 closing checklist should sweep all skills for cross-skill references and verify on each downstream skill commit.
4. **Refresh-cadence convention.** F-CR-03 + F-CR-EH-04 + F-HR-04 + F-HR-12. Framework-level decision: per-source cadence OR uniform-cadence with explicit lower-bound annotation. Apply across all Phase 6+ skills.
5. **Skill-to-DEC trace gap.** F-HR-03 + F-HR-09. DEC-2026-05-26-011's own text asks future skills to reference it; neither audited skill does. Capture as skill-template requirement.
6. **ATT&CK technique-ID coverage.** F-RT-01 + F-RT-EH-01. Zero technique-IDs across audited Phase 6 skills. Adversary Mapping section convention should be established and applied.
7. **OWASP Cheat Sheet section-anchor citation depth.** F-SA-01 + F-SA-EH-01. Cheat sheets cited at page level rather than `§<section-name>` depth per DEC-011 Clause 2. Refetch under M15 + update citations.

**New cross-artifact dimension introduced by Target 2:**

8. **Cross-artifact phase-position drift.** F-HR-10 is the first finding spanning SECURITY-CORE and a Phase 6 skill. The Phase 6 plan moves skills around; SECURITY-CORE's references to those skills don't get updated in lockstep. Phase 6 closing process should sweep cross-artifact references for stale phase attribution.

**Framework-level question raised by Target 2 (not in any cross-target pattern yet but worth flagging):**

- **Hard-refusal calibration for fail-open security checks.** F-SA-EH-04 surfaced that AP-1 (swallow-and-allow in security path) and AP-4 (default-permit on auth dependency failure) are structurally identical to CLAUDE.md §5 hard-refusal entries but the skill self-describes as "close to hard-refusal." The framework should not have a "close to hard-refusal" category. WS4/WS5 decision needed: amend CLAUDE.md §5 to add fail-open security checks explicitly, OR route AP-1/AP-4 in production paths as Critical/hard-refusal in the skill.

WS5 plan v1 should structure work-packages around the cross-target patterns (efficient: fix once, apply across all Phase 6 skills) rather than per-skill (inefficient: fix N times).

## §5 Cross-References

- `docs/workstream-4-plan.md` — WS4 spec that produced these findings.
- `ERROR-LOG.md` — Critical/High findings from WS4 (the visible-now backlog).
- `DECISIONS.md` DEC-2026-05-26-011 — §2 Sources discipline applied retroactively by WS4 mechanical checks.
- `.tgf/state/agent-activity/<role>/` — full dispatch transcripts (gitignored; contain ALL findings regardless of routing).
- `docs/framework-hardening-plan.md` §3.5 — WS5 spec (this document feeds WS5's Stage 1 research).
