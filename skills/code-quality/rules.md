# Rules — CODE-QUALITY

Full rule statements with citations, plain-language impact, and extended discussion. Referenced from `SKILL.md` §5 Rule Summaries. Loaded on demand when deep rule application is needed (typically Stage 5 Code Review).

Six rules per phase-4-plan QC criterion (a). Citation granularity per Phase 4 Checkpoint 1 Decision A: NIST SSDF practices cited at the practice level (PW.4, PW.5, PW.7) since the practice IS the granular unit; craft rules without rule-level mapping acknowledge "TGF synthesis grounded in [source]."

---

## Rule 5.1: Type Safety at Boundaries

**Statement:** Public function signatures, module boundaries, and trust boundaries declare their types explicitly. Internal helpers may rely on inference where it does not obscure intent. `any`, `dynamic`, or untyped parameters at a boundary erase the contract for every caller and forfeit the type system's value.

**Citation:** `NIST-SSDF v1.1 PW.5` (Create Source Code by Adhering to Secure Coding Practices — NIST's reference examples include "use a language that has features for type safety, memory safety, and concurrency safety where feasible").

**Plain-language impact:** Without declared types at boundaries, callers cannot tell what shape of data a function expects or returns. The next maintainer reads the function body to find out — every time. Worse, type checkers cannot catch wrong-shape data crossing the boundary, so the failure shifts from compile time to runtime, often in production, often far from the actual mistake.

**Extended discussion:** "Boundary" means anywhere code in one logical unit calls code in another: public functions exported from a module, controllers that handle external input, repository methods between business logic and persistence, integration points with third-party services. Internal helpers within the same module can rely on inference because the writer and reader share immediate context.

The rule does NOT mean "annotate every variable." It means: if a future caller will need to know the shape of what they pass or receive, the type must be declared, not inferred. In TypeScript this means function signatures, exported interfaces, and module-level constants. In Python this means typed function signatures (PEP 484) at module boundaries, pydantic or dataclass models for structured data crossing boundaries. In Go and Rust, the language already enforces this — the rule is then about *meaningful* type design, not type presence.

AI-generated code particularly tends to default to `any` or `unknown` when a model is unsure — surface this in review and replace with the actual type.

**Related anti-patterns:** AP-1 (see `anti-patterns.md`)

---

## Rule 5.2: Explicit Error Handling at Failure Points

**Statement:** Errors at I/O, parsing, third-party calls, and persistence operations are handled at the call site or explicitly propagated with context. Bare `except:`, `catch (Exception e)`, and similar broad swallows that consume errors without logging, rethrow, or recovery are prohibited. Error messages preserve enough context for the receiver to act.

**Citation:** `NIST-SSDF v1.1 PW.5` (Create Source Code by Adhering to Secure Coding Practices — NIST's reference examples include "have the software check the validity and authorization of every input … and gracefully handle any unexpected condition").

**Plain-language impact:** A swallowed exception is a future incident with no debugging trail. The user sees "something went wrong" or, worse, nothing at all, while the actual failure happens silently. By the time symptoms surface (data corruption, partial state, mysterious slowness), the original error is long gone from logs and the root cause is unreachable.

**Extended discussion:** The rule has two halves: where to catch, and what to do when caught.

*Where to catch:* errors at failure points are caught where the call is made or explicitly propagated. "Failure points" are the boundaries where reality intrudes on assumptions — file system, network, database, parser, third-party API, anything that can fail for reasons the calling code did not cause and cannot prevent. Pure-logic functions that operate on already-validated data do not need error handling for hypothetical failures.

*What to do when caught:* the receiver acts. Acting can mean logging with sufficient context to debug later, retrying with backoff if the failure mode is transient, returning a typed error to the caller, falling back to a documented default, or aborting with a clear error message to the user. The forbidden action is silently consuming the error.

Common AI failure: model generates `try / except: pass` or `try / catch { /* ignore */ }` because the prompt didn't specify error behavior. Catch this in Stage 5 Phase 1 review.

**Related anti-patterns:** AP-2 (see `anti-patterns.md`)

---

## Rule 5.3: Names Describe Intent

**Statement:** Variable, function, class, and module names communicate problem-domain meaning, not implementation detail. `userIds` not `arr1`. `calculateRefundEligibility` not `helper2`. `OutstandingInvoice` not `Record`. Single-letter or abbreviated names are reserved for tight loops and conventional uses (`i` for loop index, `e` for caught error in a small scope, `_` for ignored).

**Citation:** `TGF-SYNTHESIS — grounded in NIST-SSDF v1.1 PW.5 + senior-engineer practice`. NIST SSDF PW.5 references general "code readability" practices but does not provide rule-level naming guidance; this rule is TGF synthesis of standard senior practice.

**Plain-language impact:** Bad names force every reader to reverse-engineer the design from the implementation. The cost compounds: a function with three vaguely-named parameters costs the reader a minute the first time and continues costing every reader after. Good names are the cheapest documentation possible and the only documentation that does not rot — they update automatically when the code is renamed via the IDE.

**Extended discussion:** Names operate at every scope. At the variable level: a name should let the reader skip the assignment and trust the name. `const refundEligibility = calculateRefundEligibility(invoice)` reads at a glance; `const r = ce(i)` does not. At the function level: a name should let the reader skip the body and trust the contract. At the module level: a name should let the reader navigate without opening the file.

The exception space for short names is narrow and well-known. Loop indices (`i`, `j`, `k`) are conventional and unambiguous in their scope. Math-heavy code often follows mathematical convention (`x`, `y`, `theta`). Caught exception variables in small scopes (`e`, `err`) are acceptable. None of these justify `data2`, `tmp`, or `arr1` at function or module scope.

Renaming is cheap with modern IDEs. The cost of replacing `helper` with `calculateRefundEligibility` across a codebase is minutes; the cost of leaving `helper` there is paid by every reader for the code's lifetime.

**Related anti-patterns:** AP-3 (see `anti-patterns.md`)

---

## Rule 5.4: Comment the WHY, Not the WHAT

**Statement:** Comments explain non-obvious WHY only: hidden constraints, subtle invariants, workarounds for specific bugs, behavior that would surprise a reader. Code documents what it does through good names and structure (Rule 5.3). Routine narration (`// increment counter`, `// return result`) is noise that crowds out the comments worth reading.

**Citation:** `TGF-SYNTHESIS — grounded in ANTHROPIC-SKILLS authoring guidance + senior practice`. Anthropic's skill authoring guidance notes "state what to do rather than narrating how or why" for skill content; the inverse applies to code comments — narration about what code does is unnecessary, but non-obvious why is worth preserving.

**Plain-language impact:** Excessive comments train readers to skim the comments without reading them, because most comments tell them nothing the code didn't already. When a genuinely load-bearing comment appears — a workaround for a vendor bug, a non-obvious ordering constraint, a subtle invariant — it gets skimmed too and the constraint gets violated. Comments only work as a communication channel if the channel is signal-rich.

**Extended discussion:** Five categories of comment are worth writing:

1. *Hidden constraints:* "Must run before X is initialized, otherwise Y is undefined."
2. *Subtle invariants:* "The list is sorted by timestamp ascending; downstream consumers assume this."
3. *Workarounds for specific bugs:* "Vendor SDK 3.2.x raises on empty arrays; coerce to `[{}]`. Remove after upgrade."
4. *Surprising behavior:* "Returns 200 on success AND 200 on idempotent no-op; check the body."
5. *Cross-references the reader needs:* "See RFC 5322 §3.2.4 for the addr-spec grammar."

Six categories of comment are NOT worth writing:

1. *Narration of obvious code* (`// increment counter`).
2. *Explanations of well-named functions* (`// calculateRefundEligibility calculates refund eligibility`).
3. *Out-of-date references to past states* (`// updated for new logic`).
4. *Author signatures or dates* (git blame is authoritative).
5. *TODO comments without an owner or revisit date* (file an issue or log to `ERROR-LOG.md` instead).
6. *Commented-out code "for reference"* (version control IS the reference).

AI-generated code particularly produces category-2 comments at high volume because docstring/comment generation is a common training signal. Strip routinely.

**Related anti-patterns:** AP-4, AP-7 (see `anti-patterns.md`)

---

## Rule 5.5: Scale-Aware Defaults from First Commit

**Statement:** New code defaults to scale-aware patterns even when current scale is small: indexed queries on predictable predicates, paginated lists with limits and maximum caps, bounded resources (connection pools, retry counts, queue depths), async I/O for blocking operations, stateless services. The marginal cost of these patterns at creation time is small; the cost of retrofitting them under production load is large.

**Citation:** `TGF-SYNTHESIS — grounded in NIST-SSDF v1.1 PW.5 + senior practice`. NIST SSDF PW.5 covers "secure coding practices" at the practice level but does not specify performance or scale rules; this is TGF synthesis based on common production failure modes.

**Plain-language impact:** Without scale-aware defaults, prototype code becomes production code unchanged when the project ships. Then it gets a real user load and one of three things happens: an unindexed query slows a page to seconds, an unbounded list returns megabytes to the browser, or a blocking I/O call ties up the server. Each failure mode is visible to users, expensive to diagnose in production, and avoidable at write time for almost no cost.

**Extended discussion:** The rule has five typical applications.

*Indexed queries on predictable predicates:* if a column appears in `WHERE`, `ORDER BY`, or `JOIN ON` for a user-driven query (anything triggered by HTTP request or scheduled job), index it when the query is added — not after a production complaint. Composite indexes follow query patterns. The cost of an unnecessary index is small; the cost of a missing index on a 10M-row table at 9 PM Friday is visible.

*Pagination with limits and caps:* list endpoints take `limit` and `offset` (or cursor-based equivalent), with a sensible default (10–50) and a hard maximum (typically 100–500). "Return all" is never a public API contract; if internal code needs all rows, it iterates pages explicitly.

*Bounded resources:* connection pools sized; retry counts and backoff bounded; queue depths capped; timeouts on every external call. Unbounded retries are how one slow upstream takes down the system.

*Async I/O for blocking operations:* network calls, file I/O, and database queries in handlers use the language's async or non-blocking primitives. Blocking the request thread on I/O is how 50 concurrent users become 50 minutes of latency.

*Stateless services:* request handlers do not rely on in-memory state surviving between requests; state lives in the database, cache, or queue. Stateful handlers do not scale horizontally without rewriting.

**Related anti-patterns:** AP-5, AP-6 (see `anti-patterns.md`)

---

## Rule 5.6: Solo-Maintainability as Design Constraint

**Statement:** Code is built to be maintainable by one developer across long time horizons. Default to standard patterns over clever ones; boring tech over trendy; explicit over implicit. Justify each dependency by clear value. Introduce complexity only when current evidence demands it. Three similar lines beat a premature abstraction.

**Citation:** `TGF-SYNTHESIS — grounded in NIST-SSDF v1.1 PW.4 + senior practice`. NIST SSDF PW.4 (Reuse Existing, Well-Secured Software When Feasible) supports the "boring, well-trodden idioms over novel ones" half of this rule; the broader "complexity earns its place" framing is TGF synthesis.

**Plain-language impact:** Code that no single maintainer can hold in their head is not well-engineered code, regardless of how clever it is. Solo developers and small teams cannot afford an architecture review every time someone touches a module — they need patterns they recognize at a glance. A clever metaprogramming trick or a five-level inheritance hierarchy makes the original author feel smart and the maintenance team six months later feel stranded.

**Extended discussion:** This rule operates on four axes.

*Standard patterns over clever ones:* if the codebase already establishes a way to do X, new code does X the same way. The cost of consistency is uniform; the cost of three different patterns for the same operation is paid by every reader navigating the codebase. Reach for novel patterns only when current evidence demands them and the deviation is documented in `DECISIONS.md`.

*Boring tech over trendy:* PostgreSQL over the new graph database; Express or Fastify over the framework released last week; standard library over the dependency. Boring tech has documentation, stack overflow answers, hiring pool, and a track record. Trendy tech has none of those yet, and the cost of finding out the hard way is paid by the maintainer alone.

*Explicit over implicit:* `import { specificThing } from './module'` over wildcard imports; named parameters over positional when ambiguity is possible; documented contracts over "the code is the documentation." Implicit behavior depends on the reader knowing the convention; explicit behavior depends on the reader reading the line.

*Dependencies justified by clear value:* every dependency is a maintenance liability — security updates, version compatibility, supply-chain attack surface, transitive dependencies, removal risk if the package is unmaintained. Add only when the value clearly exceeds the cost. A single utility function pulled from a 50-package dependency tree often loses on this calculation.

The unifying test: would the next maintainer (or the author six months later) recognize this pattern, navigate it without rebuilding context, and extend it without rewriting it? If no, the pattern owes more than it pays.

**Related anti-patterns:** AP-7, AP-8 (see `anti-patterns.md`)

---
