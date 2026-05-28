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

### §3.4 Target 4 — `skills/security-input-validation/` (Audit completed 2026-05-28, commit pending — closes Build Step 3)

**Audit context:** WS4 Build Step 3 Target 3 (per-skill commit 1/12). Same two-track methodology. All four agents dispatched per Decision E. **This commit closes Build Step 3**; Build Step 4 (Phase 5 activity skills, 7 targets) opens next.

**Activity logs (Track 2 dispatch transcripts):**
- code-reviewer: `.tgf/state/agent-activity/code-reviewer/d3e58f10-eab3-4414-902f-ae03ab4764ed.json`
- security-auditor: `.tgf/state/agent-activity/security-auditor/1d67eeb5-c928-4f4c-aa7b-80aef52332d2.json`
- red-team: `.tgf/state/agent-activity/red-team/572f1332-ae48-4af6-b706-5935fbdd02b1.json`
- holistic-reviewer: `.tgf/state/agent-activity/holistic-reviewer/64dba2d2-00b2-48d3-af8d-b48ced143be1.json`

**Routed to ERROR-LOG.md:** none (0 Critical/High findings).

**Routed here (Medium/Low — 24 actionable + 7 informational/positive):**

#### Track 1 — Mechanical compliance findings

| ID | Severity | Target | Description | Remediation hint | Priority hint |
|---|---|---|---|---|---|
| T1-IV-001 | Low | SKILL.md frontmatter ↔ §2 table | Same parenthetical asymmetry on first 6 entries; CWE-20 + CWE-1287 lack `(verified DATE)`. **n=4 cross-target confirmation — 100%.** | Cross-target work-package. | §2/frontmatter convention (CROSS-TARGET) |
| T1-IV-002 | Medium | SKILL.md §2 vs rules.md | 4 §2 sources lack rule-level citation: `OWASP-ASVS-V4`, `OWASP-TOP10`, `NIST-SSDF`, `CWE-20`. F-HR-02-IV adds synthesis: V4 + SSDF have ZERO rule-level citations (same b67765e shape — registered, verified, in §2, never cited). | Per-source decision: remove (preferred for V4 + SSDF — V4 belongs in security-api Phase 7) OR add citations. | Bidirectional traceability (CROSS-TARGET) |

#### Code-reviewer findings (Track 2)

| ID | Severity | Target | Description | Remediation hint | Priority hint |
|---|---|---|---|---|---|
| F-CR-IV-01 | Medium | anti-patterns.md AP-6 CP-6 (lines 456-457, 465-466) | pydantic v1 `class Config: extra="forbid"` inside pydantic v2 example. Skill text calls v2 "the modern default" at rules.md:41. Reader copying gets deprecation + future v3 hard error. | Replace with `model_config = ConfigDict(extra="forbid")`. | Per-skill bug fix; reproduces F-CR-OE-01 |
| F-CR-IV-02 | Medium | anti-patterns.md AP-4 line 257 | AP-4 demo off-by-one: claims `?` stripped from regex output but `?` is in allow class. Actual output includes `?`; `:` was stripped (not mentioned). | Update narrative to match actual regex behavior. | Per-skill demo fix; reproduces F-CR-OE-04 |
| F-CR-IV-03 | Medium | anti-patterns.md AP-3 line 182 | "Rule 5.6 / SECURITY-CORE Rule 5.6" cited as if same concept. This skill's Rule 5.6 = Server-Side Mandatory; SECURITY-CORE 5.6 = Output Encoding. Different concepts. | Drop leading "Rule 5.6 /"; keep only "SECURITY-CORE Rule 5.6 (Output Encoding)". | Per-skill citation cleanup |
| F-CR-IV-04 | Low | SKILL.md frontmatter | Uniform 12-month refresh, 8 heterogeneous sources. **n=4 cross-target.** | Framework-wide. | Refresh-cadence (CROSS-TARGET) |
| F-CR-IV-05 | Low | SKILL.md frontmatter line 55 | NIST-SSDF entry reads `(verified Phase 2)` without date. §2 table has 2026-05-20. Intra-frontmatter inconsistency. | Update to `(verified Phase 2, 2026-05-17)`. | Trivial fix |
| F-CR-IV-06 | Low | SKILL.md §9 + multiple | 9 forward-references; same-phase peers inconsistently tagged. **n=4 cross-target.** | Phase 6 closeout. | Forward-ref discipline (CROSS-TARGET) |
| F-CR-IV-07 | Low | anti-patterns.md CP-2 lines 147-150 | CP-2 distinguishes empty-string-clear from absent via `z.string().max(500).optional()` accepting empty by default. Maintainer adding `.min(1)` would break 'clear my bio' silently. | Add comment: `// bio: optional, empty string explicitly allowed (means "clear")`. | Per-skill craftsmanship |

#### Security-auditor findings (Track 2)

| ID | Severity | Target | Description | Remediation hint | Priority hint |
|---|---|---|---|---|---|
| F-SA-IV-01 | Medium | rules.md Rule 5.4 + APs 3 + 4 | **PARTIAL reproduction.** Rules 5.3 + 5.6 cite OWASP-CHEAT-IV at section level (good, matches F-HR-07-OE exemplar); Rule 5.4 + AP-3 + AP-4 at page level. Between cryptography defect and output-encoding exemplar. | Refetch + tighten 3 page-level citations to `§<section-name>`. | Citation depth (CROSS-TARGET partial) |
| F-SA-IV-02 | Medium | SKILL.md:11 + :51 + :88 (V4 in description, frontmatter, §2) | Extends T1-IV-002 with description over-claim. V4 declared in 3 places; zero V4.x.x citations. F-SA-EH-02 pattern inverted. | Path A (recommended): tighten description to V2 only, remove V4. Path B: add V4.x.x citations. | Scope-creep / b67765e shape (CROSS-TARGET) |
| F-SA-IV-03 | Low | anti-patterns.md AP-2 + 3 + 5 + 8 + SKILL.md §7 | 4 CWE entries (915, 79, 602, 502) + MITRE-ATLAS cited at rule level not in §2. Resolves via id_prefix_match but bidirectional rule applies to §2 surface. | Add CWEs to §2 Sources table. | Citation-chain (CROSS-TARGET); reproduces T2-OE-001/002/003 |
| F-SA-IV-04 | Informational | SKILL.md §1 + §9 + Rule 5.4 | POSITIVE — confirms F-HR-09-OE from input-validation side. Pair-with bidirectional clean. | No action. Canonical exemplar. | POSITIVE |
| F-SA-IV-05 | Informational | rules.md Rule 5.4 + 5.7 | POSITIVE — TGF synthesis citations defensible. Both pair with external authority (OWASP-CHEAT-IV; OWASP-LLM LLM01:2025). Augments not masks. | Preserve pairing discipline. Optionally codify convention. | POSITIVE |

#### Red-team findings (Track 2)

| ID | Severity | Target | Description | Remediation hint | Priority hint |
|---|---|---|---|---|---|
| F-RT-IV-01 | Medium | All rules + APs | Zero ATT&CK technique-IDs. §7 names ATLAS AML.T0051 in prose only. **n=4 cross-target — framework template deficiency.** | WS4 synthesis: framework-level skill-template fix preferred over per-skill. | ATT&CK coverage (CROSS-TARGET) |
| F-RT-IV-02 | Medium | rules.md Rule 5.2 + §7 | **NEW.** Schema-library default-mode bypasses: (1) zod `.coerce.boolean()` returns true for 'false'; (2) zod default permissive — `.strict()` required; (3) pydantic v1 vs v2 coercion differs; (4) joi `.unknown(true)` permissive default; (5) `.transform()` chains return unexpected shapes. "Using zod = validating" — for `.coerce.*` it's coercion in schema clothing. | Rule 5.2.1 on schema-library default modes. Add AP-10. Warn against `.coerce.*` + `.transform()` as substitutes for strict parse. | Per-skill rule completeness (high-leverage) |
| F-RT-IV-03 | Medium | rules.md (no rule); APs use .safeParse() correctly but no mandate | Validator fail-modes unaddressed: (1) ReDoS in allow-list regex (`^([a-z]+)+$` catastrophic backtracking); (2) Schema-library exception types differ across versions; (3) Adversary-crafted parser-exhaustion; (4) Validator-fails-permissively pattern. F-RT-EH-02 at input boundary. | Rule 5.3 sub-rule on ReDoS-safe regex; Rule 5.2 sub-rule on fail-closed for validator exceptions. Add AP-11. Cross-ref security-error-handling Rule 4.1. | Per-skill rule completeness; reproduces F-RT-EH-02 |
| F-RT-IV-04 | Medium | rules.md Rule 5.3; APs (none) | **NEW.** Unicode homoglyph allow-list bypass: (1) Cyrillic 'аdmin' in `[a-z0-9_]` allow-list visually identical to Latin admin; (2) Case-folding inconsistency; (3) NFC vs NFKC; (4) RTL override U+202E; (5) UTS #39 confusable detection missing. Identity-relevant fields require normalization + confusable handling. | Rule 5.3 sub-rule on Unicode normalization + UTS #39 for identity fields. Add AP-12. | Per-skill rule completeness (high-leverage for identity systems) |
| F-RT-IV-05 | Medium | rules.md Rule 5.2 | **NEW.** Rule 5.2 "consumers downstream get type-guaranteed data" framing reads stronger than schema provides. (1) Same schema multiple consumers (most permissive sets bounds); (2) Schema-conformant attacks (50-char SQL payload passes max(100)); (3) Cross-consumer drift over time. Type-safe ≠ value-safe ≠ consumer-safe. | Reword Rule 5.2 to specify scope (type/shape/range, NOT consumer-safety). Cross-ref security-output-encoding. Add AP-13. | Per-skill rule completeness; reproduces F-RT-OE-04 at input |
| F-RT-IV-06 | Low | rules.md Rule 5.7 + AP-9 | Indirect prompt injection via RAG content under-developed. Rule 5.7 mentions retrieved-context filtering once. Tool-output-as-prompt-input not addressed. Length bounds don't prevent low-char-count injection. | Rule 5.7.1 sub-rule on indirect injection. Per-source trust scoring for RAG. Add AP-9.1. | Per-skill rule completeness; reproduces F-RT-OE-06 partial |
| F-RT-IV-07 | Low | anti-patterns.md AP-8 | **NEW.** Parser-stage vulnerabilities below schema: (1) YAML billion-laughs (safe_load is RCE-safe but NOT DoS-safe); (2) JSON polyglot; (3) JSON deeply-nested DoS; (4) **XML XXE entirely absent** — SAML/SOAP/DOCX/XLSX paths missing. | Extend AP-8 with parser hardening. Add XML to §3 discovery. Add AP-15. | Per-skill rule completeness |
| F-RT-IV-08 | Low | rules.md Rule 5.5; APs 7 | **NEW.** State-machine bypass via alternate write paths: (1) Endpoint multiplicity (`/api/orders/:id/legacy-update` bypasses); (2) Schema-layer vs database-level constraint; (3) Race condition (concurrent X→Y both validate, both write). AP-1 primitive applied to state machines. | Rule 5.5 sub-rule: state-machine validation at EVERY write path. Cross-ref security-database. Add AP-16. | Per-skill rule completeness |

#### Holistic-reviewer findings (Track 2)

| ID | Severity | Target | Description | Remediation hint | Priority hint |
|---|---|---|---|---|---|
| F-HR-01-IV | Medium | `.claude/hooks/...` + skills/**/SKILL.md §2 | **n=4 = 100% reproduction** across audited Phase 6 cluster. Strongest possible signal for Phase 11/12 hook re-prioritization. | ERR-005 tracks. | Fitness function (CROSS-TARGET) |
| F-HR-02-IV | Medium | SKILL.md §2 (V4 + SSDF) | Same finding as F-SA-IV-02 from holistic angle. Same b67765e shape. | Path A: remove V4 + SSDF from §2. | Scope-creep |
| F-HR-03-IV | Low | SKILL.md + rules.md | DEC-2026-05-26-011 not cited. **n=4.** | One-line addition to §2. | Decision-trail (CROSS-TARGET) |
| F-HR-04-IV | Low | SKILL.md frontmatter | Uniform refresh, 8 heterogeneous sources. **n=4.** | Phase 11/12. | Refresh-cadence (CROSS-TARGET) |
| F-HR-05-IV | Low | SKILL.md §9 + rules.md | **Highest forward-ref count (12)** of any audited skill. Inconsistent phase attribution. **n=4.** | Phase 6 closeout. | Forward-ref (CROSS-TARGET) |
| F-HR-06-IV | Medium | rules.md + APs | Zero ATT&CK technique-IDs in rules; ATLAS cited at §7 only. Cross-target n=3. | M15-verified ATT&CK; consult Phase 6/7 boundary owners. | ATT&CK (CROSS-TARGET) |
| F-HR-07-IV | Informational | rules.md Rules 5.3 + 5.4 + 5.6 | POSITIVE. Cheat-sheet section-anchor depth holds. **Second audited skill** (after output-encoding) confirming F-HR-07-OE pattern at n=2. | No action. Second canonical exemplar. | POSITIVE |
| F-HR-08-IV | Informational | SKILL.md §1 + preambles | POSITIVE. Cleanest SECURITY-CORE Rule 5.1 extension positioning. Matches F-HR-08-OE. | No action. | POSITIVE |
| F-HR-09-IV | Informational | SKILL.md §1 + Rule 5.4 + §9 | POSITIVE. **Confirms F-HR-09-OE bidirectionally.** Three symmetric surfaces per side. | No action. Canonical Phase 7 paired-skill exemplar. | POSITIVE |
| F-HR-10-IV | Informational | skills/security-core/SKILL.md | POSITIVE. SECURITY-CORE forward-ref staleness by-design per Decision C. **n=4.** | No action until commit 12/12. | POSITIVE |
| F-HR-11-IV | Informational | rules.md Rule 5.4 + 5.7 | POSITIVE NOTE on TGF synthesis. Rule 5.4 substantive; Rule 5.7 borderline. Pairing-with-external-authority avoids anti-pattern. | WS5 low priority: codify TGF synthesis citation convention. | DEC-candidate Phase 11 |

### §3.5 Target 5 — `skills/disagreement/` (Audit completed 2026-05-28 — Build Step 4 opens; first Phase 5 activity skill)

**Audit context:** WS4 Build Step 4 Target 5 (per-skill commit 7/22). Same two-track methodology. **Decision E selective dispatch: code-reviewer + holistic-reviewer ONLY** (security-auditor + red-team NOT dispatched — Phase 5 activity skill, not security content). First Phase 5 cluster target; different domain/source-profile from the Phase 6 cluster.

**Activity logs (Track 2 dispatch transcripts):**
- code-reviewer: `.tgf/state/agent-activity/code-reviewer/a2c88bd1-d7e7-47ce-8f35-43f984af3210.json`
- holistic-reviewer: `.tgf/state/agent-activity/holistic-reviewer/9c563404-bf27-468d-ab3f-64119743c7e0.json`

**Routed to ERROR-LOG.md:** none (0 Critical/High findings).

**Routed here (Medium/Low — 12 findings: 2 Medium, 9 Low, 1 informational):**

#### Track 1 — Mechanical compliance findings

| ID | Severity | Target | Description | Remediation hint | Priority hint |
|---|---|---|---|---|---|
| T1-D-01 | Medium | rules.md Rule 5.1 (L15) | Cites `CLAUDE.md §1` which is NOT in the §2 Sources table (§2 lists §5 + §11 only). Bidirectional traceability gap. | Add §1 to §2, OR repoint the citation to §5 (the §1 reference is to "findings include plain-language impact" which §5 also covers). | Bidirectional traceability (CROSS-CLUSTER — reproduces Phase 6 pattern #1 on a Phase 5 skill) |
| T1-D-02 | Low | SKILL.md §2 (L72) | §2 source ID `OWASP-LLM` is a short alias; source-registry canonical key is `OWASP-LLM-TOP10-2025`. Resolves via alias but ambiguous. | Use canonical registry ID `OWASP-LLM-TOP10-2025` in §2. | Registry-ID hygiene |
| T1-D-03 | Low | SKILL.md §2 'Date Verified' col (L69-71) | Non-date prose ("TGF-internal authoritative source", "Cross-reference to Phase 4 skill") in a date column for the 3 internal/cross-ref sources. | Separate a provenance note from the verification-date, or use 'n/a (internal)'. | §2 verification-date convention — for INTERNAL sources (distinct from Phase 6 pattern #2, which was external CWE/RFC) |
| T1-D-04 | Low/Info | rules.md L23; anti-patterns.md L139, L600, L656, L601 | Illustrative example citations inside dialogues not in §2 (OWASP Top 10:2025 A01/A04, OWASP ASVS V3.2.1/V14.1.1, GDPR Art 5(1)(e), SECURITY-CORE / CODE-QUALITY rule refs). Acceptable as teaching content; but OWASP Top 10:2025 letter accuracy is unverified (see F-CR-DIS-03). | No §2 listing required (illustrative). Verify OWASP letters. | Teaching-citation accuracy |

#### Code-reviewer findings (Track 2)

| ID | Severity | Target | Description | Remediation hint | Priority hint |
|---|---|---|---|---|---|
| F-CR-DIS-01 | Low | SKILL.md L131, L140; anti-patterns.md L33, L106, L200, L612 | 2 of 7 rule-anchor slugs broken: Rule 5.1's `+` and Rule 5.4's parenthetical break the GitHub auto-slug; 8 reference sites land at nothing. Other 5 coincidentally resolve. Sibling skills (security-core, continuity) use exact full-title slugs. | Repoint the 2 anchors to auto-generated slugs at all 8 sites, OR simplify the 2 rule headers. | Per-skill navigation fix |
| F-CR-DIS-02 | Low | anti-patterns.md AP-8 L600, CP-8 L655 | AP-8/CP-8 cite `SECURITY-CORE Rule 5.4` for customer-email PII/data-minimization, but Rule 5.4 = "Secrets Never in Code" (credentials, not PII). Inaccurate cross-skill citation inside a "how to cite well" exemplar. | Drop the SECURITY-CORE number; forward-reference the planned security-privacy-data-handling skill, or cite GDPR/CCPA data-minimization only. | Per-skill citation accuracy |
| F-CR-DIS-03 | Low | rules.md L23; anti-patterns.md L139 | OWASP Top 10:2025 category LETTERS asserted (A01 plausible; "A04 Cryptographic Failures" likely wrong — Cryptographic Failures was A02:2021). Corpus-wide: SECURITY-CORE rules.md uses the same idiosyncratic 2025 numbering. | Verify final 2025 letters via M15 WebFetch (WS5); else revert to stable 2021 letters / category-name-only. Apply same fix to SECURITY-CORE. | Source-chain accuracy (CROSS-ARTIFACT with SECURITY-CORE); overlaps T1-D-04 |
| F-CR-DIS-04 | Low | SKILL.md frontmatter L32-39 | Uniform 12-month `refresh-recommended` over 5 heterogeneous sources (2 external/volatile + 3 TGF-internal/commit-cadence). Rule 5.5's "7 items" silently stales if §5 amended. | Split refresh guidance by source class, or note internal sources track TGF amendment. | Refresh-cadence (CROSS-CLUSTER — reproduces Phase 6 pattern #4 on a Phase 5 skill) |

#### Holistic-reviewer findings (Track 2)

| ID | Severity | Target | Description | Remediation hint | Priority hint |
|---|---|---|---|---|---|
| F-HR-DIS-01 | **Medium** | SKILL.md L101, L120, L143; rules.md L122, L36-44 | Skill DUPLICATES CLAUDE.md §5's hard-refusal list (3 inline enumerations) + 4-tier gradient, vs Phase 5 Decision C's reference-not-restate intent. §5 is periodically amended (amended this session, 4704f30); inline copies will silently drift; no fitness function or in-file sync marker binds them. | Collapse to one canonical restatement (rules.md Rule 5.5) + add in-file "mirror of §5 — keep in sync" markers; WS5: fitness check diffing restatement vs §5 source. | **§5-restatement-drift — HIGHEST-PRIORITY Target 5 item.** NEW Phase 5 pattern; non-security analog of cross-target pattern #1 |
| F-HR-DIS-02 | Low | SKILL.md L101, L143; rules.md L122 | Per-item scope-wording drift in restatements: §5 item 6 "or sensitive personal data" dropped; item 7 "on endpoints handling user data" qualifier dropped. The "7 items" COUNT is accurate; per-item scope diverges. | Align wording to §5 verbatim, or reduce to one canonical copy (rides with F-HR-DIS-01). | Restatement fidelity |
| F-HR-DIS-03 | Low | SKILL.md §8 L216; rules.md L134 | SKILL.md §8 routes hard-refusal acknowledgments unconditionally to DECISIONS.md per CONTINUITY Rule 5.2 (ADR scope); rules.md L134 hedges correctly (WAIVER-LOG OR DECISIONS.md). Internal inconsistency; §8 over-extends Rule 5.2's ADR scope. | Make §8 consistent with L134's two-way routing — default WAIVER-LOG (risk acceptance); DECISIONS.md only when architecturally significant. | Per-skill internal consistency |
| F-HR-DIS-04 | Low | Rule 5.1 + AP-2 + AP-8 vs `docs/communication-skill-plan.md` | Forward-compat turf overlap: the queued communication activity skill will also operationalize §5 and own "plain-language impact" delivery, which disagreement Rule 5.1 + AP-2 + AP-8 currently fully own. Boundary undrawn. | WS5 / communication build: DECISIONS.md ADR drawing the disagreement↔communication boundary; forward-reference in disagreement §9. | Forward-compat (Phase 5+ cohort) |

#### Positive notes (preserved in activity logs)

- **Example-code accuracy is genuinely good** (code-reviewer): CP-2 `bcrypt.hash(token, 12)` correctly illustrates slow-vs-fast-hash; AP-6 auth-middleware passthrough faithfully renders the failure it warns against; AP-8/CP-8 orders schema + NUMERIC/BIGINT-cents discussion is correct.
- **Both WAIVER-LOG templates well-formed and richer than CONTINUITY Rule 5.3's minimum** — deliberate non-conflicting elaboration; "whichever fires first" multi-trigger revisit is the right shape for AP-7.
- **AP↔CP 1:1 pairing complete (8/8)** per DEC-2026-05-17-003 Clause 1 — the invariant this skill models, it honors.
- **Structural conformance to sibling Phase 5 skills is exact** (holistic) — §1-§9 anchors, dual-block frontmatter, 238-line body ≤300.
- **Self-referential correctness on highest-stakes claims** (holistic): Rule 5.4's "accept after one round (below hard-refusal)" matches §5; the hard-refusal carve-out correctly mirrors §5. The skill describes orchestrator behavior matching what §5 prescribes.
- **Honest TGF-SYNTHESIS labeling** per DEC-2026-05-17-004 — synthesis acknowledged, not fabricated as external citation.

### §3.6 Target 6 — `skills/debugging/` (Audit completed 2026-05-28 — Build Step 4, second Phase 5 activity skill)

**Audit context:** WS4 Build Step 4 Target 6 (per-skill commit 8/22). Same two-track methodology. Decision E selective dispatch: code-reviewer + holistic-reviewer only. Phase 5 activity skill grounded in Agans' 9 rules, Five Whys, scientific method.

**Activity logs (Track 2 dispatch transcripts):**
- code-reviewer: `.tgf/state/agent-activity/code-reviewer/38ffa3c4-0330-48d9-be33-17a78551c69b.json`
- holistic-reviewer: `.tgf/state/agent-activity/holistic-reviewer/16af4741-97e4-4dd6-b989-c946ff8353db.json`

**Routed to ERROR-LOG.md:** none (0 Critical/High findings).

**Routed here (Medium/Low — 11 entries: 3 Medium, 8 Low; F-CR-DBG-05 + F-HR-DBG-03 are formalizations/cross-references of the Track 1 §2 gaps, not net-new severity):**

#### Track 1 — Mechanical compliance findings

| ID | Severity | Target | Description | Remediation hint | Priority hint |
|---|---|---|---|---|---|
| T1-DBG-01 | Medium | SKILL.md §7 (L209) vs §2 | §7 cites "OWASP LLM Top 10:2025 LLM09:2025" but OWASP-LLM is NOT in the §2 Sources table. Bidirectional gap. | Add OWASP-LLM row to §2 (matching disagreement's format). | Bidirectional traceability (CROSS-CLUSTER — reproduces Phase 6 pattern #1) |
| T1-DBG-02 | Low | SKILL.md/rules.md/anti-patterns.md (9 sites) vs §2 | CONTINUITY referenced 9× at rule level (Rule 5.1/5.3/5.6) but not in §2. Sibling `disagreement` DID list CONTINUITY in §2 — debugging is the inconsistent sibling. | Add CONTINUITY cross-reference row to §2 covering 5.1/5.3/5.6. | Bidirectional traceability (CROSS-CLUSTER) |
| T1-DBG-03 | Low | SKILL.md §2 'Date Verified' col (L69-71) | AGANS-9 / TOYODA-5W / SCIENTIFIC-METHOD use "reference (book; stable since publication)" / "reference (stable)" prose — the DEC-2026-05-26-011-deprecated "reference"-as-verification-status class. | Use 'n/a (stable book/methodology)' or a provenance note distinct from the date column. | §2 verification-date convention; closer to the explicitly-deprecated string than Target 5's T1-D-03 |

#### Code-reviewer findings (Track 2)

| ID | Severity | Target | Description | Remediation hint | Priority hint |
|---|---|---|---|---|---|
| F-CR-DBG-01 | Low | SKILL.md L146, L155; anti-patterns.md L315, L630 (4 sites) | 2 of 7 rule-anchor slugs truncated at the comma: Rule 5.4 ("...Root Cause, Not Symptom Patch") and Rule 5.7 ("...Hypotheses, Not Conclusions") drop the post-comma tail vs GitHub auto-slug. | Update 4 sites to full auto-slugs, or add explicit HTML anchors. | Per-skill nav fix; **reproduces Phase 5 anchor-slug pattern at n=2** |
| F-CR-DBG-02 | Medium | anti-patterns.md CP-5 L439-446, L449-457 | CP-5 states a fabricated specific as a confirmed observation: "stripe.HTTPClient default pool size is 5". Stripe Node SDK pooling is governed by Node https.Agent (historical default maxSockets Infinity); no documented Stripe 'default of 5'. A skill whose §7 warns against fabricated specifics models one. Fix mechanism (httpAgent/maxSockets/maxNetworkRetries) is sound. | Reword 'confirmed' claim to the mechanism, not a fabricated number; mark illustrative; VERIFY against current Stripe SDK; add `import https`. | Per-skill accuracy; **NEW Phase 5 candidate: fabricated-specific-in-teaching-example** |
| F-CR-DBG-03 | Low | anti-patterns.md CP-6 L563-565 | CP-6 off-by-one lists two candidate conditions as parallel 'OR' but the first (`< array.length` vs `<= array.length - 1`) is EQUIVALENT/harmless; only the second is the real off-by-one. Muddies a skill whose Rule 5.2 is 'reason from observation.' | Tighten to the real defect only. | Per-skill craftsmanship |
| F-CR-DBG-04 | Low | SKILL.md L75 (§2) vs rules.md L7 | Same citation-granularity discipline attributed to two sources across files: §2 cites "Phase 4 CP1 Decision A"; rules.md cites "DEC-2026-05-17-004". Both valid (Decision A refines DEC-004 Clause 2) but split; siblings cite both together. | Align both files: 'Decision A (refining DEC-2026-05-17-004 Clause 2)'. | Per-skill traceability; within-skill variant of Phase 6 pattern #5 |
| F-CR-DBG-05 | Low | SKILL.md §2 vs §7 L209 + rule-level CONTINUITY | Formalizes T1-DBG-01 + T1-DBG-02. §2 omits OWASP-LLM (cited §7) and CONTINUITY (cited 9×). disagreement lists both → debugging inconsistent. Temporal: debugging shipped 2026-05-20, six days before DEC-011 (2026-05-26) codified the bidirectional rule. | Add both §2 rows. | Formalizes Track 1; Phase 6 pattern #1 |

#### Holistic-reviewer findings (Track 2)

| ID | Severity | Target | Description | Remediation hint | Priority hint |
|---|---|---|---|---|---|
| F-HR-DBG-01 | **Medium** | SKILL.md §8 L224 | **Routing drift vs WORKFLOW.md §7.** §8 routes "worked-around" bugs to WAIVER-LOG; §7 + CONTINUITY Rule 5.3 + CLAUDE.md §11 route them to ERROR-LOG (Resolved-with-workaround) + a new ERROR-LOG entry for the open root cause. WAIVER-LOG = consciously-not-fixed; ERROR-LOG = actionable-being-worked. Also contradicts the skill's own AP-4 (anti-patterns.md L369). | Reword §8 to ERROR-LOG routing (WAIVER-LOG only for consciously-permanent root-cause acceptance); keep the Rule 5.3 citation. | **HIGHEST-PRIORITY Target 6 item** — governs how orchestrator closes out bugs; wrong routing propagates to adopters |
| F-HR-DBG-02 | Low | SKILL.md §8 L221 | Reviewer-attribution drift: §8 says "Holistic Reviewer (per CONTINUITY) checks that the cause was identified"; WORKFLOW.md §7 Stage-5 assigns the Holistic Reviewer to regression risk. Root-cause-found is Rule 5.4 (Five Whys), not a Holistic-Reviewer job. | Drop the reviewer attribution or attach CONTINUITY to its real (decision-documentation) function. | Per-skill §7 fidelity |
| F-HR-DBG-03 | Low | SKILL.md §2 vs §7/§5/§8 | Integration-lens framing of the §2 gap (cross-ref T1-DBG-01/02 + F-CR-DBG-05; NOT re-scored). Citation-surface conceptual integrity: every source a skill leans on should round-trip through §2. | Add OWASP-LLM + CONTINUITY §2 rows; add OWASP-LLM to frontmatter. | Cross-reference only |

#### Positive notes (preserved in activity logs)

- **WORKFLOW.md §7 stage-LABEL fidelity is clean** (holistic): §8's six debugging-variant labels match §7's table AND CLAUDE.md §3's debugging-variant sentence one-to-one; the four termination conditions match. The drifts are in stage prose, not the skeleton.
- **Agans 9-rule mapping fully accurate** (code-reviewer): 5.1↔#2, 5.2↔#3, 5.3↔#5, 5.5↔#6, 5.6↔#8 verified; 'not promoted' set #1/#4/#7/#9 correct. No mis-numbering.
- **All CONTINUITY cross-references factually correct** by number+title (5.1 session log, 5.3 three-log routing, 5.6 capture-WHY) — the §2 gap is registration, not accuracy.
- **ARCHITECTURE.md §16 reference is sound and load-bearing**: Rule 5.2 (observe don't reason) + Rule 5.7 (AI output is hypothesis) are §16's discipline applied to bugs.
- **Self-referential safety**: a skill governing how the orchestrator debugs correctly subordinates AI debug output to verification + empirical execution, and even names AI as a possible "false fresh view."
- **CP-3 revert/reapply necessary-AND-sufficient verification** is exemplary in-line debugging discipline.

## §4 Cross-Target Patterns (Updated 2026-05-28 after Target 4 audit — Build Step 3 CLOSED — n=4)

**Build Step 3 closes with all 4 Phase 6 commits 1/12-4/12 audited.** The full audited Phase 6 cluster (4 of 4 skills) confirms the following framework-wide patterns at 100% reproduction. WS5 plan v1 should structure work-packages around these patterns (efficient: fix once, apply across all 11 Phase 6 skills + future Phase 7+ skills) rather than per-skill (inefficient: fix 11+ times).

With four of 19 audit targets complete, the following patterns are **CONFIRMED cross-target on 4 of 4 audited Phase 6 skills (100%)**. These should be remediated as a class in WS5, not per-skill:

1. **§2 bidirectional traceability invariant has no automated enforcement.** T1-001 + T1-EH-002 + T1-OE-002 + T1-IV-002 + F-HR-01 + F-HR-08 + F-HR-01-OE + F-HR-01-IV. **n=4 = 100% reproduction.** Hook-side fitness function tracked in ERR-2026-05-27-005. **Most leverage: build the hook.** Phase 11/12 elevated priority per closing Build Step 3 evidence.

2. **§2/frontmatter verification-date asymmetry.** T1-002 + T1-EH-001 + T1-OE-001 + T1-IV-001. **n=4 = 100% reproduction.** Trivial cosmetic fix; do across all Phase 6 skills in one pass.

3. **Forward-reference discipline + inconsistent phase attribution.** F-CR-05 + F-CR-EH-03 + F-CR-OE-?? + F-CR-IV-06 + F-HR-06 + F-HR-11 + F-HR-05-OE + F-HR-05-IV. **n=4 = 100% reproduction.** Input-validation has highest forward-reference count (12 distinct unbuilt skills). Phase 6 closing checklist should sweep all skills + standardize `(Phase N)` attribution.

4. **Refresh-cadence convention.** F-CR-03 + F-CR-EH-04 + F-CR-OE-06 + F-CR-IV-04 + F-HR-04 + F-HR-12 + F-HR-04-OE + F-HR-04-IV. **n=4 = 100% reproduction.** Framework-level decision: per-source cadence (registry-level `next_refresh`) OR uniform-cadence with explicit lower-bound annotation. Apply across all Phase 6+ skills.

5. **Skill-to-DEC trace gap.** F-HR-03 + F-HR-09 + F-HR-03-OE + F-HR-03-IV. **n=4 = 100% reproduction.** DEC-2026-05-26-011's own text asks future skills to reference it; none of 4 audited skills do. Capture as skill-template requirement. Phase 6 closeout commit 12/12 is natural surface for cross-skill sweep.

6. **ATT&CK technique-ID coverage.** F-RT-01 + F-RT-EH-01 + F-RT-OE-01 + F-RT-IV-01 + F-HR-06-OE + F-HR-06-IV + ERR-2026-05-25-004 (cryptography). **n=4 = 100% reproduction** — framework-level skill-template deficiency. All four audited skills exhibit asymmetry: when ATLAS or related adversary frameworks ARE cited (in §7), it's at the name level in prose only; ATT&CK Enterprise techniques never cited at rule level. WS4 synthesis should consider framework-level skill-template fix.

7. **Citation of unregistered sources at rule level (CWE / OWASP-LLM / historical Top 10 / OWASP-CHEAT-INJECTION).** F-SA-01 + T2-OE-001 + T2-OE-002 + T2-OE-003 + F-SA-IV-03 + F-HR-02-OE. NEW cross-target pattern surfaced at Target 3, **confirmed at n=2** (Target 3 + Target 4). Reverse direction of pattern #1. Phase 11/12 fitness function should check BOTH directions.

### Cross-target pattern BROKEN — confirmed at n=2 (positive):

8. **~~OWASP Cheat Sheet section-anchor citation depth.~~** F-SA-01 + F-SA-EH-01 NO LONGER reproduces in 2 of 4 audited skills. **F-HR-07-OE + T2-OE-006 + F-HR-07-IV + F-SA-IV-01 (positive portion)** confirm output-encoding and input-validation BOTH cite at section level. F-SA-01 (cryptography) is a **per-skill defect**, not a Phase 6-wide pattern. **Output-encoding and input-validation become canonical in-repo exemplars** for DEC-2026-05-26-011 Clause 2 application. Per F-SA-IV-01: input-validation is PARTIAL — Rules 5.3 + 5.6 at section level (correct); Rule 5.4 + AP-3 + AP-4 still at page level. Worth tightening to fully match the exemplar pattern.

### Cross-artifact dimension (introduced by Target 2):

9. **Cross-artifact phase-position drift between SECURITY-CORE and Phase 6 skills.** F-HR-10 (error-handling) + F-HR-10-OE (output-encoding — but here the drift is BY-DESIGN per Phase 6 Checkpoint 1 Decision C). The Decision C deferral to closeout commit 12/12 is the working convention; drift before that is expected sequencing. Sweep should verify completeness of the 12/12 fix when it ships.

### New cross-target pattern surfaced at Target 4 (cross-artifact integrity):

10. **§2-listed-without-rule-level-citation as scope-creep.** F-SA-IV-02 + F-HR-02-IV surface OWASP-ASVS-V4 + NIST-SSDF in input-validation §2 with zero rule-level citations — same b67765e shape applied to scope rather than to specific values. Distinct from cross-target pattern #1 (§2-source-not-cited as oversight); this is **§2-source-not-cited as deliberate-scope-claim-not-exercised**. The two are the same defect mechanism but different motivation: pattern #1 is "forgot to cite"; pattern #10 is "claimed scope, never exercised it." Recommendation for both: same fitness function check (every §2 source has ≥1 rule-level citation OR is removed from §2). Path-A remediation (remove unused §2 entries) is cleaner than path-B (force citations to fit).

### Framework-level questions raised (NOT in cross-target pattern; flagged for WS5):

- **Hard-refusal calibration for fail-open security checks.** F-SA-EH-04 surfaced AP-1 (swallow-and-allow in security path) and AP-4 (default-permit on auth dependency failure) are structurally identical to CLAUDE.md §5 hard-refusal entries. **DISTINCT from T2-OE-005** which probed AP-1/AP-3/AP-6/AP-8 of output-encoding (SQL concat, unsafe HTML sinks, shell-string spawn, XXE) and RESOLVED FAVORABLY — injection patterns are severity-by-context not hard-refusal-by-pattern. The framework's §5 calibration is: universal-critical-regardless-of-context goes on the hard-refusal list; severity-by-context stays on the gradient. F-SA-EH-04's question stands: should fail-open security checks (auth/authz returning permit on exception) be added to §5 because they fit the universal-critical pattern? Decision needed for WS5.

- **Implicit conventions not captured in DECs.** F-HR-08-OE + F-HR-08-IV surface 6 implicit Phase 6 conventions: rule-numbering 5.1-5.7 namespace shared with SECURITY-CORE, 'Defense Option N' as section-anchor-equivalent, forward-reference phase attribution, uniform skill-level refresh date, 'TGF synthesis' as cited authority (when paired vs sole), §2 source inclusion when source touches adjacent-skill scope. None in DECISIONS.md. WS4 closeout or Phase 6 closeout should consider DEC entries vs phase-plan-level capture.

- **'TGF synthesis' citation convention** (F-HR-11-IV + F-SA-IV-05). Rules 5.4 + 5.7 of input-validation cite 'TGF synthesis' alongside external authority. Defensible when external authority carries the load and synthesis augments. Not yet documented as a convention. Phase 11 DEC-candidate: 'TGF synthesis acceptable as co-citation; not acceptable as sole citation; document permitted/forbidden scope.'

### Authoritative-source-chain integrity findings (surfaced at Target 3; not reproduced at Target 4):

- **F-CR-OE-02 RFC 4180 misattribution for CSV formula injection** — Rule 5.7 + AP-9 attribute the leading-quote escape to RFC 4180 §2.6/§2.7. RFC 4180 doesn't cover formula characters. The escape is OWASP/Microsoft community convention. **Citation-chain integrity issue** — finding where the skill cites an authoritative source for content the source doesn't actually contain. Distinct from cross-target pattern #1 (source-listed-not-cited), #7 (cited-not-registered), and #10 (cited-deliberately-but-not-exercised); this is **cited-incorrectly-attributed**. Target 4 audit found no instance of this pattern in input-validation — per F-SA-IV-05's probe, RFC currency / source-content fidelity check passes clean.

### Build Step 3 closeout summary (2026-05-28)

**Audit pass: 4 of 19 targets complete (21%).** Full Phase 6 commits 1/12-4/12 audited. 124 total findings across 4 targets (0 Critical, 2 High via Target 2 ERROR-LOG entries, 55 Medium, 50 Low, 17 Informational/positive). 2 ERROR-LOG entries (ERR-2026-05-27-008 + ERR-2026-05-27-009 — fail-open / detection-evasion class). Backlog populated with 121 actionable Medium/Low + 17 positive notes preserved in activity logs.

**Cross-target pattern density: 6 framework-wide patterns at n=4 = 100% reproduction.** This is the strongest possible signal that WS5 + Phase 6 closeout + Phase 11/12 hook work should be structured framework-wide (efficient: fix once, apply N times) rather than per-skill (inefficient: fix N times independently).

**Build Step 4 (Phase 5 activity skills audit, 7 targets) opens next.** Different cluster (discovery, project-management, design, ui-craft, testing, debugging, disagreement) — different domain, different age, different template adherence. Build Step 4 dispatch should NOT assume Phase 6 cross-target patterns will replicate to Phase 5 cluster; expect a different pattern profile.

WS5 plan v1 should structure work-packages around: (a) the 6 confirmed n=4 cross-target patterns; (b) the 1 pattern BROKEN at n=2 (cheat-sheet section-anchor — cite output-encoding + input-validation as exemplars); (c) the new at-n=2 cross-target pattern (#7 unregistered-cited); (d) the 2 framework-level questions (hard-refusal calibration; TGF synthesis convention); (e) the per-skill bug fixes (e.g., F-CR-IV-01 pydantic v1/v2 mix; F-CR-OE-01 Jinja2 e(quote=True); F-CR-OE-02 RFC 4180 misattribution); (f) the per-skill rule completeness extensions (DOMPurify config, identifier allow-list, mixed-context emission, LLM channel, schema-library coercion, Unicode homoglyph, parser-stage hardening, state-machine bypass).

### Phase 5 cluster cross-target tracking (Build Step 4 — opened 2026-05-28; n=2 at Targets 5-6 `disagreement`, `debugging`)

**Framing:** Build Step 4 audits Phase 5 activity skills — a different cluster from the Phase 6 security skills (different domain, source profile, template age). Per the Build Step 4 dispatch framing, Phase 6's 6 n=4 patterns are NOT assumed to carry over. The first Phase 5 data point (Target 5) confirmed the framing: **only 2 of 6 Phase 6 patterns reproduce on `disagreement`; 4 do not.** Target 6 (`debugging`) holds the same shape (see Target 6 update below).

Phase 6 pattern reproduction at Phase 5 n=1:

- **#1 §2 bidirectional invariant (no fitness function): REPRODUCES.** T1-D-01 (Rule 5.1 cites CLAUDE.md §1, absent from §2) + F-HR-DIS-01 (§5 hard-refusal list restated inline, not bound to source). Now **cross-cluster**, not Phase-6-only. Strengthens the "build the hook" case (ERR-2026-05-27-005): the fitness function should also check internal-source restatement/citation, not only external-source citation.
- **#4 refresh-cadence convention: REPRODUCES.** F-CR-DIS-04 (uniform 12-month over heterogeneous external + internal sources). Cross-cluster.
- **#2 §2/frontmatter verification-date asymmetry: DOES NOT REPRODUCE.** `disagreement` frontmatter and §2 carry identical dates; internal-source prose is consistent in both places. (T1-D-03 is a related-but-distinct observation about internal sources in a date column — not the Phase 6 external-CWE/RFC asymmetry.)
- **#3 forward-reference phase-attribution: N/A.** `disagreement` refs are consistent and resolve.
- **#5 skill→DEC-2026-05-26-011 trace gap: N/A.** `disagreement` shipped 2026-05-20, predating the DEC (2026-05-26). Nothing to trace.
- **#6 ATT&CK technique-ID coverage: N/A.** `disagreement` cites MITRE ATLAS at framework level by design (stated honestly in §2 L75); no rule-level technique-ID claims to be missing. Appropriate for an activity skill.

**NEW Phase 5 pattern candidates (n=1 — watch for reproduction across the remaining 6 Phase 5 targets):**

- **§5-restatement-drift (F-HR-DIS-01 + F-HR-DIS-02).** Skills that operationalize a CLAUDE.md section (here: disagreement ↔ §5) risk duplicating the section's content inline rather than referencing it; when the CLAUDE.md section is amended, the copies silently drift. **Watch:** other Phase 5 skills that operationalize a CLAUDE.md section. If this reproduces, it is a Phase-5-cluster pattern distinct from Phase 6's external-source citation patterns — and a strong argument for the fitness function (pattern #1) to cover internal-source restatement.
- **anchor-slug correctness (F-CR-DIS-01).** Rule-anchor slugs not matching the GitHub auto-slug when rule headers contain punctuation (`+`, parentheticals). **Watch:** other Phase 5 skills with punctuation in rule headers.
- **disagreement↔communication turf overlap (F-HR-DIS-04).** Forward-compat with the queued Phase 5+ communication skill. Cohort-level, not per-skill.

**Decision E dispatch-matrix note:** selective dispatch (code-reviewer + holistic-reviewer only; NO security-auditor/red-team) worked cleanly on `disagreement` — no low-signal noise, both agents produced substantive lens-appropriate findings (code-reviewer: craftsmanship/citation accuracy; holistic: §5-fidelity/integration). Confirms Decision E's rationale; 2-agent dispatch was materially faster than the Phase 6 4-agent cluster as predicted in WS4 plan §11.

**Target 6 (`debugging`) update — n=2:**

Phase 6 pattern reproduction holds the same 2-of-6 shape as Target 5:
- **#1 §2 bidirectional (no fitness function): REPRODUCES** (T1-DBG-01 OWASP-LLM + T1-DBG-02 CONTINUITY omitted from §2; F-CR-DBG-05). **Now n=2 in Phase 5 cluster** — and notably `disagreement` got this RIGHT (listed both), so within Phase 5 it's inconsistent application, not universal omission. Strengthens the cross-cluster case for the ERR-005 fitness function.
- **#4 refresh-cadence: REPRODUCES** (mild — uniform 12-month over 3 stable books/methodologies + 1 living ATLAS). n=2.
- **#5 skill→DEC-2026-05-26-011 trace gap: REPRODUCES (temporal)** — debugging shipped 2026-05-20, six days before DEC-011; its §2 gaps are exactly what DEC-011 now forbids. (On Target 5 this was N/A; here it surfaces because debugging's §2 omissions are the kind DEC-011 governs.) Plus a within-skill DEC-attribution split (F-CR-DBG-04).
- **#2 verification-date asymmetry: N/A** (frontmatter and §2 carry the same posture). **#3 forward-ref phase-attribution: BROKEN/does-not-reproduce** (internally consistent). **#6 ATT&CK technique-ID: N/A** (cites ATLAS at framework level by design).

Phase 5 candidate-pattern status:
- **anchor-slug-correctness: CONFIRMED at n=2.** Both `disagreement` and `debugging` have exactly 2 of 7 rule anchors broken, both truncated where the rule-header title contains a comma/`+`. This is now a solid Phase 5 cluster pattern: **rule-header titles with internal punctuation reliably produce truncated cross-reference anchors.** WS5 should sweep all Phase 5 (and Phase 6) skills for header-punctuation anchor mismatches, and consider a skill-template lint.
- **section-restatement-drift: DOES NOT GENERALIZE beyond living-doc-operationalizing skills.** disagreement's drift risk came from inlining the *living* CLAUDE.md §5. debugging restates Agans (a stable book) and WORKFLOW.md §7 (TGF-internal, changes only via deliberate edits) — near-zero drift risk. Refines the Target 5 candidate: the pattern is **"inlining a LIVING framework artifact"** (CLAUDE.md sections), not "restating any source." Watch skills that operationalize CLAUDE.md/WORKFLOW.md sections specifically.
- **NEW candidate — fabricated-specific-in-teaching-example (n=1, F-CR-DBG-02):** an activity skill's worked-example dialogue states an invented technical specific ("Stripe default pool size of 5") as a *confirmed observation* — the very failure mode the skill teaches against. Watch other Phase 5 skills with concrete code/config dialogues (`testing`, `ui-craft`) for invented specifics presented as fact.
- **NEW (Target 6) — workflow-mapping prose drift (F-HR-DBG-01/02):** where a Phase 5 skill maps itself to a WORKFLOW.md section, the *skeleton* (stage labels, termination conditions) can match cleanly while the *attached prose* (routing targets, reviewer attributions) drifts from the source. Distinct from disagreement's §5-restatement: here the labels are faithful but the operational detail diverged. Watch `testing` (maps to WORKFLOW Stage 5) and any skill claiming a WORKFLOW.md mapping.

## §5 Cross-References

- `docs/workstream-4-plan.md` — WS4 spec that produced these findings.
- `ERROR-LOG.md` — Critical/High findings from WS4 (the visible-now backlog).
- `DECISIONS.md` DEC-2026-05-26-011 — §2 Sources discipline applied retroactively by WS4 mechanical checks.
- `.tgf/state/agent-activity/<role>/` — full dispatch transcripts (gitignored; contain ALL findings regardless of routing).
- `docs/framework-hardening-plan.md` §3.5 — WS5 spec (this document feeds WS5's Stage 1 research).
