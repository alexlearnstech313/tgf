# Citation-Provenance Hook Fix — Plan

> **Status:** plan, awaiting Checkpoint approval before implement.
> **Origin:** stakeholder-identified during WS5 session-04. The research-security write-hook re-demands a fresh source fetch *every session* before it will allow *any* edit to a skill that cites that source — even edits (anchor fixes, typos) that touch no citation. That produced heavy, repeated re-fetch friction this session.
> **Pulls forward** a slice of Phase-12 enforcement refinement (Checkpoint-1 deferred executable hook work to Phase 12). Conscious re-scope: the over-firing actively impedes the WS5 remediation it gates.

## §1 Problem

The framework's intended model (CLAUDE.md §14, skill frontmatter `last_generated`/`refresh-recommended`, the §2 "Date Verified" column): a source is **fetched + verified + pinned once when a skill is built from it**, and that provenance **persists**. Re-fetching is a deliberate, periodic **staleness audit**, not a precondition for editing the skill.

The write-hook does not implement that model. It checks every cited source against **this session's** research log and blocks the edit unless the source was verified **this session**. A fresh session starts with an empty log, so the first edit to any skill re-demands fetches of sources that were already verified and pinned in prior sessions.

This is the lockfile anti-pattern: re-downloading and re-verifying every dependency on every source-file edit, instead of trusting the pinned lockfile and re-resolving only on a deliberate update/audit.

## §2 Root cause — the per-session assumption lives in 2 of 3 enforcement points

| Enforcement point | Current scope | Correct? |
|---|---|---|
| `git_precommit_check.py` (commit gate) | **cross-session union** — `_all_verified_source_ids()` collects `status=="verified"` across **all** logs | ✅ already embodies provenance-persists |
| `hook_research_pretool_write.py` (edit gate) | per-session — `status_of(session_id, …)` | ❌ the friction |
| `hook_research_stop.py` (session-end sweep) | per-session — `_bad_cited_sources` → `status_of(session_id, …)` | ❌ would block session-end if write-hook is changed alone |

The commit gate is the reference implementation. The fix aligns the two in-session hooks to the same cross-session provenance standard — with one safety addition (below).

## §3 The fix — an `is_backed()` rule with current-session-negative-override

A cited source is **backed** (citeable without re-fetch) iff:

1. it is verified in **some** session's research log (provenance persists — the union), **AND**
2. it is **not** `flagged` / `blocked-pending-review` in **this** session.

Clause 2 is the safety nut: if you *do* re-fetch this session (e.g., a staleness audit) and the fetch surfaces tampering, that fresh negative finding **overrides** the historical verification and blocks the citation. Without clause 2, a naive union would silently ignore a live tamper signal because an old session had verified the source — a real regression the T11 smoke test exercises.

```
is_backed(session_id, source_id):
    cur = status_of(session_id, source_id)          # most recent status THIS session, or None
    if cur in ("flagged", "blocked-pending-review"):
        return False                                # fresh negative wins
    if cur == "verified":
        return True
    return source_id in all_verified_source_ids()   # not fetched this session → cross-session provenance
```

Net behavior:
- **Not re-fetched this session, verified before → backed.** (eliminates the friction; matches the user's model)
- Re-fetched this session, verified → backed.
- Re-fetched this session, flagged → **blocked** (tamper-detection preserved).
- Never verified in any session → **blocked** (genuine unbacked citation; the original anti-hallucination guarantee).

No diff-awareness needed: every *existing* citation in a built skill is already in the union (it passed the commit gate when committed), so a full-file `is_backed` check passes for edits that add no new source. A genuinely new, never-verified source still blocks.

## §4 Why this is safe (trust-boundary analysis)

The control defends against *writing a citation not backed by a real, checked fetch* (anti-hallucination / anti-poisoning, RESEARCH-SECURITY §7.4 / §8.7).

- A `verified` entry only exists if the source was fetched under hooks and passed M3/M4/M11/M13/M14/M18/M19. Persisting that across sessions does not weaken it — the fetch genuinely happened and passed. Provenance is a property captured once, not re-proven continuously.
- The cross-session union is **already** the accepted bar at commit time (pre-commit). The change makes the in-session hooks *consistent* with it — and, via clause 2, *stricter* than pre-commit in the re-fetch case.
- True-positive blocks (genuinely unbacked citation; freshly-flagged source) are unchanged. Only the false-positive blocks (re-cite an already-pinned, untampered source) are removed.

## §5 Scope

**In:**
1. `research_log.py` — add `all_verified_source_ids()` (cross-session union) + `is_backed(session_id, source_id)`.
2. `hook_research_pretool_write.py` — gate on `not is_backed(...)`; reword the block message to distinguish "never verified" from "flagged this session."
3. `hook_research_stop.py` — `_bad_cited_sources` uses `is_backed(...)`.
4. `git_precommit_check.py` — refactor to call `research_log.all_verified_source_ids()` (behavior identical; removes the duplicate implementation).
5. `tests/research-security-smoke-test.sh` — make T7/T11 robust under cross-session (use a source guaranteed-absent from the union, or assert absence first); add **T13** (edit citing a prior-session-verified source, not re-fetched this session → PASS) and **T14** (source flagged this session but verified in a prior session → BLOCK).
6. `DECISIONS.md` — ADR: *citation verification is provenance-at-authoring (cross-session), not re-verification-at-edit; current-session negative findings override.*
7. `docs/RESEARCH-SECURITY.md` — update the § that describes the write/stop blocking points.

**Out (→ Phase 12):** the hash-of-AI-summary weakness (ERR-2026-05-28-015) and the deliberate staleness-audit re-fetch flow. This fix makes re-fetch rare, so the hash weakness stops being a per-edit tax — but redesigning the audit path (raw-byte hashing or retiring M11/M13) stays Phase-12.

## §6 Steps
1. `research_log.py` helpers + unit-sanity via CLI.
2. Patch write-hook + Stop hook.
3. Refactor pre-commit to shared helper.
4. Update + extend smoke tests; **run the full suite, expect green**.
5. Empirical verification (synthetic PreToolUse payloads, per CLAUDE.md §16): the exact code-quality edit that was blocked earlier this session should now PASS with no re-fetch.
6. Four-pass review (code / security / red-team / holistic) — red-team focus: can an unbacked or freshly-flagged citation reach a skill file?
7. DEC + RESEARCH-SECURITY update.
8. Commit (touches `.claude/hooks/**` + `tests/` + docs + DEC — **not** a `skills/security-*` file, so no M8; the write-hook does not gate `.claude/**`).

## §7 Benefit to the rest of WS5
Once landed, the remaining security-skill bundles stop needing a fetch batch just to fix anchors — their existing citations are already in the union. Only genuinely **new** citations (e.g., the ATT&CK technique-IDs ERR-004 adds, or new CWE/RFC refs in the ERR-003 depth work) will require a fetch. That removes most of the projected fetch load for crypto / error-handling / input-validation / output-encoding.
