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

### §3.3 Target 3 — `skills/security-output-encoding/` (Audit completed 2026-05-28, commit pending)

**Audit context:** WS4 Build Step 3 Target 2 (per-skill commit 2/12). Same two-track methodology. No Decision K validation gate. Track 2 dispatched all four agents per Decision E.

**Activity logs (Track 2 dispatch transcripts):**
- code-reviewer: `.tgf/state/agent-activity/code-reviewer/8ec16510-9f55-4964-99c3-930db283ea3e.json`
- security-auditor: `.tgf/state/agent-activity/security-auditor/8a569794-0e69-432a-b689-e55f88139679.json`
- red-team: `.tgf/state/agent-activity/red-team/cc3f3b26-1ba5-495a-9b57-ee6539d8a811.json`
- holistic-reviewer: `.tgf/state/agent-activity/holistic-reviewer/cc623ec4-a3d2-4bf5-a2cf-f2674300af5b.json`

**Routed to ERROR-LOG.md:** none (0 Critical/High findings — the skill is structurally sound).

**Routed here (Medium/Low — 26 findings; 5 positive/informational notes preserved in activity logs):**

#### Track 1 — Mechanical compliance findings

| ID | Severity | Target | Description | Remediation hint | Priority hint |
|---|---|---|---|---|---|
| T1-OE-001 | Low | `SKILL.md` frontmatter ↔ §2 table | Same parenthetical asymmetry — first 6 entries marked `(verified DATE)`; RFCs and CWEs unmarked. **Cross-target n=3 confirmation.** | Cross-target backlog work-package. | §2/frontmatter convention cleanup (CROSS-TARGET) |
| T1-OE-002 | Medium | `SKILL.md` §2 vs rules.md | `OWASP-TOP10` (A05:2025) listed in §2 but never cited at rule level. Single-source case (cleaner than cryptography's 5 or error-handling's 2). | Add to specific rule citations OR remove from §2. | Bidirectional traceability (CROSS-TARGET) |

#### Code-reviewer findings (Track 2)

| ID | Severity | Target | Description | Remediation hint | Priority hint |
|---|---|---|---|---|---|
| F-CR-OE-01 | Medium | anti-patterns.md AP-4 (lines 378-385) | Jinja2 `e(quote=True)` would TypeError — Python stdlib `html.escape(s, quote=True)` signature transplanted onto Jinja2 filter. Cross-language API leak. | Replace with `{{ user.username | e }}`. | Per-skill bug fix (broken example code); reproduces F-CR-EH-01 |
| F-CR-OE-02 | Medium | rules.md Rule 5.7 + anti-patterns.md AP-9 (3 sites) | **RFC 4180 misattribution.** Rule + AP cite RFC 4180 §2.6/§2.7 as authority for CSV formula-injection escape. RFC 4180 §2.6 covers line-break/quote escaping; §2.7 covers internal double-quote doubling. Neither covers formula characters. The leading-quote escape is OWASP/Microsoft community convention, not RFC. | Strip RFC 4180 attribution; replace with 'per OWASP CSV injection guidance (no normative RFC exists).' | **Authoritative-source-chain integrity** — per-skill citation cleanup |
| F-CR-OE-03 | Medium | rules.md Rule 5.7 vs anti-patterns.md AP-9 | CSV char list inconsistent: Rule prose has `=, +, -, @, \t, \0`; canonical code has `=, +, -, @, \t, \r`. **Same root cause as F-RT-OE-05 and T2-OE-004** — three findings pointing to the same fact. | Reconcile to `=, +, -, @, \t, \r` (matches current OWASP/Microsoft). | Per-skill citation cleanup; reproduces F-CR-EH-02 |
| F-CR-OE-04 | Low | anti-patterns.md AP-4 (lines 301-305) | TS attribute-context demo's claimed result doesn't match what the shown `escapeHtml` actually produces. Off-by-one on the quote-doubling in the result. Attack still works; demo is debuggability-broken. | Correct demo result. | Per-skill demo fix |
| F-CR-OE-05 | Low | anti-patterns.md AP-6 Java (lines 550-555) | Comment claims `Runtime.exec(String)` is shell-metacharacter-injectable. Actually no shell — real attack is argument injection. Reader testing with `; rm -rf /` sees harmless arg, concludes AP doesn't apply (opposite lesson). | Replace comment with accurate failure mode. | Per-skill comment fix |
| F-CR-OE-06 | Low | SKILL.md frontmatter | Uniform 12-month refresh for 16 sources of varying cadence. **Cross-target n=3.** | Per-source cadence in `sources:` block. | Refresh-cadence (CROSS-TARGET); reproduces F-CR-03 + F-CR-EH-04 |
| F-CR-OE-07 | Low | anti-patterns.md AP-7 .NET (lines 727-737) | `AntiXssEncoder.LdapFilterEncode` cited as canonical .NET fix — but this API is .NET Framework only, NOT modern .NET 5+/Core. Developer on .NET 6+ hits missing-namespace compile error. | Add platform note; reference modern .NET alternatives. | Per-skill platform clarity |

#### Security-auditor findings (Track 2)

| ID | Severity | Target | Description | Remediation hint | Priority hint |
|---|---|---|---|---|---|
| T2-OE-001 | Medium | rules.md Rule 5.7 (line 99) + anti-patterns.md AP-9 (line 910) | **CWE-1336 and CWE-1236 cited at rule level but NOT registered in §2.** §2 has CWE-79/89/78/90/611/643/117 but missing the SSTI + formula-injection IDs. | Add CWE-1336 + CWE-1236 to §2 Sources. | Citation-chain integrity (CROSS-TARGET); reproduces F-SA-01 |
| T2-OE-002 | Medium | anti-patterns.md AP-3/AP-5/AP-8 (lines 231, 437, 807) | **Historical OWASP Top 10 references** — A03:2021 (AP-3), A10:2021 (AP-5), A05:2017 (AP-8). §2 only registers 2025. Historical refs unnecessary when 2025 cite anchors. | Drop historical Top 10 refs. | Citation-chain cleanup |
| T2-OE-003 | Medium | anti-patterns.md AP-9 (line 910) + AP-10 (line 1015) | (1) `OWASP-CHEAT-INJECTION (related)` cited — no such cheat sheet in registry; may not exist as discrete cheat sheet. `(related)` annotation is M9 confirmation-gap tell. (2) `OWASP-ASVS V16` cited at AP-10 — outside this skill's V1 scope. **Same finding as F-HR-02-OE.** | (1) Remove the `(related)` ref (chain stands on its own). (2) Rephrase AP-10 to point to security-logging skill. | Citation-chain integrity + scope-boundary; reproduces F-SA-01 + F-SA-EH-02 |
| T2-OE-004 | Low | SKILL.md §4 + rules.md Rule 5.7 + anti-patterns.md AP-9 | Same CSV char list inconsistency as F-CR-OE-03 + F-RT-OE-05. Three findings pointing to one fact — single fix resolves all three. | See F-CR-OE-03. | Per-skill consolidation |
| T2-OE-005 | Low (resolved) | SKILL.md §8 line 260 | Hard-refusal calibration PROBED for AP-1/AP-3/AP-6/AP-8. RESOLVES FAVORABLY: injection patterns are severity-by-context per CLAUDE.md §5, NOT on the hard-refusal list (which is intentionally narrow — universal-critical regardless of context). 'Typically High or Critical' hedge is calibration-appropriate. Distinct from F-SA-EH-04 (fail-open security checks ARE structurally identical to hard-refusal). | OPTIONAL: brief note in §8 distinguishing severity-by-context from hard-refusal-by-pattern. | Framework-level clarity |
| T2-OE-006 | Informational | rules.md Rules 5.2-5.6 | **POSITIVE OBSERVATION — breaks F-SA-01 / F-SA-EH-01 cross-target pattern.** OWASP Cheat Sheets cited at section level correctly throughout (`§Output Encoding`, `Defense Option 1`, `§Primary Defenses`). First Phase 6 skill where citation-depth discipline holds cleanly. | No action. Cite as canonical exemplar in Phase 11/12 hook spec. | **POSITIVE — cite as exemplar** |

#### Red-team findings (Track 2)

| ID | Severity | Target | Description | Remediation hint | Priority hint |
|---|---|---|---|---|---|
| F-RT-OE-01 | Medium | All rules + APs | Zero ATT&CK technique-IDs. SKILL.md §7 cites MITRE-ATLAS AML.T0051 (ATLAS not ATT&CK) — author CAN cite adversary frameworks but doesn't. **Cross-target n=3.** | Add Adversary Mapping section per-rule. | ATT&CK coverage (CROSS-TARGET); reproduces F-RT-01 + F-RT-EH-01 |
| F-RT-OE-02 | Medium | rules.md Rule 5.3 + anti-patterns.md AP-3 | **DOMPurify configuration depth gap.** AP-3 canonical reads as 'configure ALLOWED_TAGS + ALLOWED_ATTR and you're done.' Unaddressed: (a) mXSS / mutation-XSS via SVG/MathML namespaced markup; (b) ALLOWED_URI_REGEXP defaults permit mailto:/tel: beyond Rule 5.4 allow-list; (c) ADD_TAGS/ADD_ATTR drift accumulation; (d) SVG/MathML profile risk. | Rule 5.3 paragraph on DOMPurify config discipline. Update AP-3 canonical with constraining ALLOWED_URI_REGEXP. | Per-skill rule completeness (high-value: DOMPurify is the framework's escape valve) |
| F-RT-OE-03 | Medium | rules.md Rule 5.2 + anti-patterns.md AP-2 | **Identifier allow-list discipline buried.** AP-2 'Additional considerations' mentions allow-list for `ORDER BY`, table/column names. But this is rule-level discipline (developer reaches for parameterization, finds it doesn't work, falls back to concat). Should be Rule 5.2.b sub-rule with canonical example. | Promote identifier-allow-list from AP-2 Additional considerations to Rule 5.2.b. Add AP-2b for canonical ORDER BY allow-list. | Per-skill rule completeness (high-value: identifier-context is common SQLi vector) |
| F-RT-OE-04 | Medium | rules.md Rule 5.3 Extended discussion | **Mixed-context emission.** Rule 5.3 enumerates 5 HTML contexts but doesn't address data CROSSING contexts: (a) JS string in HTML attribute; (b) URL in JS context; (c) HTML-in-JSON-in-script (`JSON.stringify` doesn't escape `</script>` by default). | Rule 5.3 'Nested and mixed contexts' paragraph naming the 3 cases. For HTML-in-JSON-script, require `</` → `<\/` escape. | Per-skill rule completeness |
| F-RT-OE-05 | Medium | rules.md Rule 5.7 + anti-patterns.md AP-9 | Same root finding as F-CR-OE-03 + T2-OE-004 (CSV char list inconsistency). Plus: rule doesn't name high-impact formulas (`=HYPERLINK`, `=WEBSERVICE`, `=DDE`, `=cmd|`); locale-specific separators unenumerated. | Sync list; add 'Documented dangerous formula prefixes' sub-paragraph. | Per-skill consolidation |
| F-RT-OE-06 | Medium | SKILL.md §7 closing + §9 | **LLM-as-output-source channel not addressed.** §7 references OWASP-LLM LLM05 / ATLAS AML.T0051 at name level only. §9 forwards LLM depth to security-ai-output-handling (Phase 8, unbuilt). Phase 6/8 gap: AI-app developer in interim has no bridge guidance for LLM-generated SQL/shell/HTML reaching the same interpreters this skill governs. | §7 paragraph: 'Treat LLM output as untrusted input to encoding boundary at same trust level as user input.' | Per-skill rule completeness (high-value: AI tool-call channel grows) |
| F-RT-OE-07 | Low | Cross-cutting (Rules 5.3, 5.6, 5.7) | Encoder failure modes unaddressed — DOMPurify can throw, JSON.stringify on circular/BigInt/Symbol throws, encodeURIComponent on lone surrogates throws, ldap3.escape_filter_chars on NUL varies. Caller's catch swallows throw, falls back to raw value, raw reaches interpreter, injection lands. **Reproduces F-RT-EH-06 (defense's own failure mode).** | Rule 5.1 paragraph: encoder failure is refusal to emit; fail-closed not fall-back-to-raw. | Per-skill defense-completeness; reproduces F-RT-EH-06 |
| F-RT-OE-08 | Low | rules.md Rule 5.7 (templates) + SKILL.md §6 | **SSTI in non-web template contexts unaddressed.** Rule 5.7 implicitly web-scoped. Adversary-relevant adjacent channels: email engines (Liquid/Handlebars), GitHub Actions/GitLab CI `${{ }}` expressions, IaC templates, chat-platform message templates. CI/CD case is documented CVE class. | Expand Rule 5.7 template paragraph. Add candidate AP for CI/CD case. | Per-skill rule completeness |

#### Holistic-reviewer findings (Track 2)

| ID | Severity | Target | Description | Remediation hint | Priority hint |
|---|---|---|---|---|---|
| F-HR-01-OE | Medium | `.claude/hooks/lib/...` + skills/**/SKILL.md §2 | §2 ↔ rule-level invariant has no fitness function despite ERR-007 fix. **Cross-target n=3.** Recommend Phase 11/12 hook re-prioritization. | See ERR-2026-05-27-005. | Fitness-function gap (CROSS-TARGET) |
| F-HR-02-OE | Medium | anti-patterns.md AP-9 (line 910) | `OWASP-CHEAT-INJECTION (related)` cited but not registered. `(related)` annotation is M9 confirmation-gap tell. **Same finding as T2-OE-003 part 1.** | (a) Verify under M15 + register, OR (b) remove ref. | Citation-chain integrity; per-skill |
| F-HR-03-OE | Low | SKILL.md + rules.md + APs | DEC-2026-05-26-011 not cited anywhere. Skill enacts rules correctly but future author can't grep-discover the DEC. **Cross-target n=3.** | Single-line addition to §2 each Phase 6 skill. | Decision-trail (CROSS-TARGET); reproduces F-HR-03 + F-HR-09 |
| F-HR-04-OE | Low | SKILL.md frontmatter | 16 sources, uniform date. **Cross-target n=3.** | See F-CR-OE-06. | Refresh-cadence (CROSS-TARGET) |
| F-HR-05-OE | Low | SKILL.md §8 + §9; rules.md; APs | 7 forward-references with inconsistent phase attribution (some '(Phase 6)' / '(Phase 7)', some bare). **Cross-target n=3.** | Phase 6 closeout step parallel to Decision C. | Forward-reference discipline (CROSS-TARGET) |
| F-HR-06-OE | Medium | SKILL.md §7 line 249; rules.md (no ATT&CK); APs (no ATT&CK) | Zero ATT&CK technique-IDs across rules/APs. **§7 cites MITRE-ATLAS AML.T0051 at the name level — confirms author CAN cite adversary-frameworks; asymmetry is the gap.** Candidate IDs: T1059, T1059.007, T1189, T1190, T1505.003, T1078, T1213, T1090, T1071. | Add 'Documented adversary use' sub-section per rule (M15-verified). | ATT&CK coverage (CROSS-TARGET); reproduces ERR-2026-05-25-004 pattern |
| F-HR-07-OE | Informational | rules.md throughout | **POSITIVE NOTE — breaks F-SA-01 / F-SA-EH-01 cross-target pattern.** Cheat-sheet section-anchor depth holds cleanly. Same as T2-OE-006. | No action. Canonical exemplar. | **POSITIVE** |
| F-HR-08-OE | Informational | SKILL.md §1; rules.md preamble; anti-patterns.md preamble | **POSITIVE NOTE.** Cleanest SECURITY-CORE Rule 5.6 extension positioning of 4 audited skills. Decision B operationalized correctly. NOTE: rule-numbering collision (skill 5.6 = LDAP, SECURITY-CORE 5.6 = output-encoding-principle) is Phase 6-wide convention; unambiguous via explicit 'SECURITY-CORE Rule X' citation. | No action. Cite as exemplar. | **POSITIVE** |
| F-HR-09-OE | Informational | SKILL.md §1, §4, §9 + security-input-validation §1, Rule 5.4, §9 | **POSITIVE NOTE.** input-validation ↔ output-encoding pair-with bidirectional cross-reference is symmetric and clean (best in audited cluster). Validation rejects; encoding emits safely. | No action. Preserve. | **POSITIVE** |
| F-HR-10-OE | Informational | skills/security-core/SKILL.md §5 + rules.md Rule 5.6 | **POSITIVE NOTE — gap is by-design.** SECURITY-CORE Rule 5.6 doesn't forward-reference security-output-encoding. Per Phase 6 Checkpoint 1 Decision C, deliberately deferred to Phase 6 closeout commit 12/12 (single bundled edit). Working as designed. | No action until commit 12/12. | **POSITIVE — sequencing intentional** |

## §4 Cross-Target Patterns (Updated 2026-05-28 after Target 3 audit — n=3)

With three of 19 audit targets complete, the following patterns are **CONFIRMED cross-target on 3 of 3 audited Phase 6 skills**. These should be remediated as a class in WS5, not per-skill:

1. **§2 bidirectional traceability invariant has no automated enforcement.** T1-001 + T1-EH-002 + T1-OE-002 + F-HR-01 + F-HR-08 + F-HR-01-OE. n=3 confirmation. Hook-side fitness function tracked in ERR-2026-05-27-005. **Most leverage: build the hook.** Phase 11/12 re-prioritization recommended.

2. **§2/frontmatter verification-date asymmetry.** T1-002 + T1-EH-001 + T1-OE-001. n=3 confirmation. Trivial cosmetic fix; do across all Phase 6 skills in one pass.

3. **Forward-reference discipline + inconsistent phase attribution.** F-CR-05 + F-CR-EH-03 + F-CR-OE-?? + F-HR-06 + F-HR-11 + F-HR-05-OE. n=3 confirmation. Phase 6 closing checklist should sweep all skills for cross-skill references and standardize `(Phase N)` attribution.

4. **Refresh-cadence convention.** F-CR-03 + F-CR-EH-04 + F-CR-OE-06 + F-HR-04 + F-HR-12 + F-HR-04-OE. n=3 confirmation. Framework-level decision: per-source cadence (registry-level `next_refresh`) OR uniform-cadence with explicit lower-bound annotation. Apply across all Phase 6+ skills.

5. **Skill-to-DEC trace gap.** F-HR-03 + F-HR-09 + F-HR-03-OE. n=3 confirmation. DEC-2026-05-26-011's own text asks future skills to reference it; none of 3 audited skills do. Capture as skill-template requirement.

6. **ATT&CK technique-ID coverage.** F-RT-01 + F-RT-EH-01 + F-RT-OE-01 + F-HR-06-OE + ERR-2026-05-25-004 (cryptography). n=3 confirmation. Output-encoding §7 cites MITRE-ATLAS AML.T0051 confirming the author CAN cite adversary frameworks — the asymmetry is the gap. Adversary Mapping section convention should be established and applied.

7. **Citation of unregistered sources at rule level (CWE / OWASP-LLM / historical Top 10 / OWASP-CHEAT-INJECTION).** F-SA-01 + T2-OE-001 + T2-OE-002 + T2-OE-003 + F-HR-02-OE. **NEW cross-target pattern surfaced at Target 3** — sources cited at rule level that aren't registered in §2. Distinct from cross-target pattern #1 (§2-source-not-cited); this is the reverse direction. Phase 11/12 fitness function should check BOTH directions.

### Cross-target pattern BROKEN at Target 3 (positive):

8. **~~OWASP Cheat Sheet section-anchor citation depth.~~** F-SA-01 + F-SA-EH-01 NO LONGER reproduces — **F-HR-07-OE + T2-OE-006** confirm output-encoding cites at section level throughout (`§Output Encoding`, `Defense Option 1`, `§Primary Defenses`). F-SA-01 (cryptography) is a **per-skill defect**, not a Phase 6-wide pattern. **Output-encoding becomes the canonical in-repo exemplar** for DEC-2026-05-26-011 Clause 2 application.

### Cross-artifact dimension (introduced by Target 2):

9. **Cross-artifact phase-position drift between SECURITY-CORE and Phase 6 skills.** F-HR-10 (error-handling) + F-HR-10-OE (output-encoding — but here the drift is BY-DESIGN per Phase 6 Checkpoint 1 Decision C). The Decision C deferral to closeout commit 12/12 is the working convention; drift before that is expected sequencing. Sweep should verify completeness of the 12/12 fix when it ships.

### Framework-level questions raised (NOT in cross-target pattern; flagged for WS5):

- **Hard-refusal calibration for fail-open security checks.** F-SA-EH-04 surfaced AP-1 (swallow-and-allow in security path) and AP-4 (default-permit on auth dependency failure) are structurally identical to CLAUDE.md §5 hard-refusal entries. **DISTINCT from T2-OE-005** which probed AP-1/AP-3/AP-6/AP-8 of output-encoding (SQL concat, unsafe HTML sinks, shell-string spawn, XXE) and RESOLVED FAVORABLY — injection patterns are severity-by-context not hard-refusal-by-pattern. The framework's §5 calibration is: universal-critical-regardless-of-context goes on the hard-refusal list; severity-by-context stays on the gradient. F-SA-EH-04's question stands: should fail-open security checks (auth/authz returning permit on exception) be added to §5 because they fit the universal-critical pattern? Decision needed for WS5.

- **Implicit conventions not captured in DECs.** F-HR-08-OE surfaced 4 implicit Phase 6 conventions: rule-numbering 5.1-5.7 namespace, 'Defense Option N' as section-anchor-equivalent, forward-reference phase attribution, uniform skill-level refresh date. None in DECISIONS.md. WS4 closeout or Phase 6 closeout should consider DEC entries vs phase-plan-level capture.

### Authoritative-source-chain integrity findings (NEW category surfaced at Target 3):

- **F-CR-OE-02 RFC 4180 misattribution for CSV formula injection** — Rule 5.7 + AP-9 attribute the leading-quote escape to RFC 4180 §2.6/§2.7. RFC 4180 doesn't cover formula characters. The escape is OWASP/Microsoft community convention. **Citation-chain integrity issue** — first finding where the skill cites an authoritative source for content the source doesn't actually contain. Distinct from cross-target pattern #1 (source-listed-not-cited) and #7 (cited-not-registered); this is **cited-incorrectly-attributed**.

WS5 plan v1 should structure work-packages around the cross-target patterns (efficient: fix once across all Phase 6 skills) rather than per-skill (inefficient: fix N times). The 7 confirmed patterns + the 1 BROKEN pattern + the 1 cross-artifact dimension + the 2 framework-level questions = the WS5 work-package backbone.

## §5 Cross-References

- `docs/workstream-4-plan.md` — WS4 spec that produced these findings.
- `ERROR-LOG.md` — Critical/High findings from WS4 (the visible-now backlog).
- `DECISIONS.md` DEC-2026-05-26-011 — §2 Sources discipline applied retroactively by WS4 mechanical checks.
- `.tgf/state/agent-activity/<role>/` — full dispatch transcripts (gitignored; contain ALL findings regardless of routing).
- `docs/framework-hardening-plan.md` §3.5 — WS5 spec (this document feeds WS5's Stage 1 research).
