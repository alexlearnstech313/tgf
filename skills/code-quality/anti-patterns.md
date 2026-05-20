# Anti-Patterns + Canonical Patterns — CODE-QUALITY

Full anti-pattern + canonical pattern pairs with code examples. Referenced from `SKILL.md` §6 Anti-Pattern Summaries. Loaded on demand when concrete examples are needed (typically Stage 5 Code Review when surfacing a specific finding).

Eight anti-pattern pairs minimum per `DEC-2026-05-17-003` Clause 1. Each anti-pattern violates a specific rule (see `rules.md`) and pairs with a canonical pattern showing the correct implementation.

---

## AP-1: `any` at module boundaries

**Pattern:**

```typescript
// src/api/orders.ts — exported function with type-erased signature
export async function createOrder(input: any): Promise<any> {
  const order = await db.orders.insert(input);
  return order;
}
```

**Violates:** Rule 5.1 (see `rules.md#rule-51-type-safety-at-boundaries`)

**Why it fails:** Every caller of `createOrder` has to read the function body — and the database insert — to learn what fields `input` must contain and what shape `Promise<any>` actually returns. The TypeScript compiler cannot catch a caller passing `{ custmerId: "..." }` (typo) or expecting `order.id` when the actual returned shape is `order.orderId`. The contract exists only in the author's head, and it walks out the door with them.

**Source for failure mode:** `NIST-SSDF v1.1 PW.5` (type safety guidance); see also `MITRE-ATLAS` AML.T0051 — AI-generated boundary code commonly defaults to `any` when the model is uncertain.

### CP-1: Declared types at boundary

**Pattern:**

```typescript
// src/api/orders.ts — explicit contract
interface CreateOrderInput {
  customerId: string;
  items: Array<{ sku: string; quantity: number }>;
  shippingAddressId: string;
}

interface Order {
  id: string;
  customerId: string;
  items: Array<{ sku: string; quantity: number; lineTotal: number }>;
  total: number;
  status: "pending" | "paid" | "shipped" | "cancelled";
  createdAt: Date;
}

export async function createOrder(input: CreateOrderInput): Promise<Order> {
  const order = await db.orders.insert(input);
  return order;
}
```

**Pairs with:** Anti-pattern AP-1

**Why it works:** The contract is visible to every caller without reading the body. Typos at call sites become compile errors. The `status` union type tells callers what values are possible without consulting documentation. Refactoring the internal implementation does not break callers as long as the declared interfaces stay stable.

**Additional considerations:** Internal helpers within the same module can still rely on inference. The rule applies at the *boundary* — exported functions, public methods on exported classes, types crossing module lines.

---

## AP-2: Bare exception swallow

**Pattern:**

```python
# src/services/payment_processor.py
def charge_customer(customer_id: str, amount_cents: int) -> bool:
    try:
        response = stripe_client.charges.create(
            customer=customer_id,
            amount=amount_cents,
        )
        return response.status == "succeeded"
    except:
        return False
```

**Violates:** Rule 5.2 (see `rules.md#rule-52-explicit-error-handling-at-failure-points`)

**Why it fails:** A bare `except:` catches everything — `StripeError`, `KeyboardInterrupt`, `MemoryError`, `SystemExit`. The caller receives `False` regardless of whether the card was declined, the network failed, Stripe's API is down, or a developer hit Ctrl-C during testing. No log entry survives, so when a customer reports "the payment said it failed but my card was charged" there is no trail to investigate. The original exception is destroyed at the `return False` line.

**Source for failure mode:** `NIST-SSDF v1.1 PW.5` (graceful handling of unexpected conditions); common production incident class.

### CP-2: Specific catch with logged context

**Pattern:**

```python
# src/services/payment_processor.py
import logging
from dataclasses import dataclass
import stripe

logger = logging.getLogger(__name__)

@dataclass
class ChargeResult:
    success: bool
    error: str | None

def charge_customer(customer_id: str, amount_cents: int) -> ChargeResult:
    try:
        response = stripe_client.charges.create(
            customer=customer_id,
            amount=amount_cents,
        )
        return ChargeResult(success=response.status == "succeeded", error=None)
    except stripe.error.CardError as e:
        logger.warning(
            "card_declined",
            extra={"customer_id": customer_id, "decline_code": e.code},
        )
        return ChargeResult(success=False, error=e.user_message)
    except stripe.error.StripeError as e:
        logger.error(
            "stripe_api_error",
            extra={"customer_id": customer_id, "error_type": type(e).__name__},
            exc_info=True,
        )
        raise
```

**Pairs with:** Anti-pattern AP-2

**Why it works:** Each failure mode is named and handled differently. Card declines are an expected business condition (warn, return user-facing message). Stripe API errors are infrastructure failures (log with full traceback, re-raise so upstream knows). `KeyboardInterrupt` and `MemoryError` propagate normally instead of being silently consumed. The customer-support trail is complete: every failure leaves a structured log entry tied to the customer ID.

---

## AP-3: Single-letter or implementation-detail names

**Pattern:**

```typescript
// src/billing/invoices.ts
function process(d: any[], t: number) {
  const r = [];
  for (const x of d) {
    if (x.a > t) {
      const tmp = { i: x.i, v: x.a - t };
      r.push(tmp);
    }
  }
  return r;
}
```

**Violates:** Rule 5.3 (see `rules.md#rule-53-names-describe-intent`)

**Why it fails:** Every reader has to reverse-engineer the function from the implementation. What does `d` represent? What is `t`? Why `a` — amount? attribute? account? After a minute of reading, a reader can guess that this finds records where some amount exceeds a threshold and returns adjusted entries. The next reader pays the same minute. Names like `tmp`, `r`, `d` carry no information; they are placeholder slots that should have been replaced before commit.

**Source for failure mode:** `TGF-SYNTHESIS — grounded in NIST-SSDF v1.1 PW.5 + senior practice`; common AI failure mode where prompt did not specify the domain.

### CP-3: Intent-revealing names

**Pattern:**

```typescript
// src/billing/invoices.ts
interface Invoice {
  invoiceId: string;
  amountCents: number;
}

interface OverdueAmount {
  invoiceId: string;
  amountOverCents: number;
}

function findInvoicesExceedingThreshold(
  invoices: Invoice[],
  thresholdCents: number,
): OverdueAmount[] {
  const overdueAmounts: OverdueAmount[] = [];
  for (const invoice of invoices) {
    if (invoice.amountCents > thresholdCents) {
      overdueAmounts.push({
        invoiceId: invoice.invoiceId,
        amountOverCents: invoice.amountCents - thresholdCents,
      });
    }
  }
  return overdueAmounts;
}
```

**Pairs with:** Anti-pattern AP-3

**Why it works:** Every name reads at a glance. The function signature alone tells the reader what it does and what it returns. `amountOverCents` is unambiguous — cents, the amount *over* the threshold, not the total. `invoice.amountCents` versus `invoice.amountDollars` is a contract the reader does not have to guess at. The body becomes verification of the contract rather than discovery of it.

---

## AP-4: Code-narrating comments

**Pattern:**

```typescript
// src/users/registration.ts
function registerUser(email: string, password: string) {
  // Hash the password
  const hashedPassword = bcrypt.hashSync(password, 10);

  // Create the user object
  const user = {
    email: email,
    passwordHash: hashedPassword,
    createdAt: new Date(),
  };

  // Save the user to the database
  db.users.insert(user);

  // Return the user
  return user;
}
```

**Violates:** Rule 5.4 (see `rules.md#rule-54-comment-the-why-not-the-what`)

**Why it fails:** Every comment restates what the next line already says clearly. Readers learn to skim comments because none of them carry information. When a load-bearing comment later appears in this file — say, a workaround for a vendor bug — it gets skimmed too and the constraint gets violated. The signal-to-noise ratio of the comment channel drops to near zero.

**Source for failure mode:** `TGF-SYNTHESIS — grounded in ANTHROPIC-SKILLS guidance + senior practice`; AI tools commonly produce category-narration comments because docstring generation is a frequent training signal.

### CP-4: Comment WHY only, when it matters

**Pattern:**

```typescript
// src/users/registration.ts
async function registerUser(email: string, password: string) {
  // bcrypt cost 10 chosen for ~100ms hash on production hardware (2026 baseline).
  // Revisit if hardware changes or threat model warrants higher cost.
  const passwordHash = await bcrypt.hash(password, 10);

  const user = {
    email,
    passwordHash,
    createdAt: new Date(),
  };

  await db.users.insert(user);
  return user;
}
```

**Pairs with:** Anti-pattern AP-4

**Why it works:** The only comment that survives is the one carrying information the code cannot: why bcrypt cost is 10 specifically, with the revisit condition. Removing the comment would leave a magic number a future reader could not justify. Removing the narration comments left in AP-4 loses nothing. When this file later gains a "vendor bug workaround" comment, readers will read it because the file does not cry wolf.

**Additional considerations:** Public API documentation (JSDoc / docstrings on exported functions) is distinct from in-body comments. API documentation describes the contract for callers and is part of the boundary type discipline (Rule 5.1). The rule against narration applies to in-body, line-level comments.

---

## AP-5: Unindexed predicate on user-driven query

**Pattern:**

```python
# src/repositories/orders.py
def get_orders_by_customer(customer_id: str) -> list[Order]:
    return db.execute(
        "SELECT * FROM orders WHERE customer_id = ? ORDER BY created_at DESC",
        [customer_id],
    ).fetchall()

# orders table schema (no index on customer_id):
# CREATE TABLE orders (
#   id          UUID PRIMARY KEY,
#   customer_id UUID NOT NULL,
#   created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
#   ...
# );
```

**Violates:** Rule 5.5 (see `rules.md#rule-55-scale-aware-defaults-from-first-commit`)

**Why it fails:** Every call to `get_orders_by_customer` does a full table scan. At 1,000 orders the page loads in 30ms and nobody notices. At 1,000,000 orders it loads in 8 seconds and every customer-detail page is broken. The index that fixes this is one line; adding it under production load is a maintenance window. The scaling cliff is hidden until traffic finds it.

**Source for failure mode:** `TGF-SYNTHESIS — grounded in NIST-SSDF v1.1 PW.5 + senior practice`; ubiquitous production incident class.

### CP-5: Index added with the query

**Pattern:**

```python
# src/repositories/orders.py
def get_orders_by_customer(
    customer_id: str,
    limit: int = 50,
    offset: int = 0,
) -> list[Order]:
    return db.execute(
        """
        SELECT * FROM orders
        WHERE customer_id = ?
        ORDER BY created_at DESC
        LIMIT ? OFFSET ?
        """,
        [customer_id, min(limit, 500), offset],
    ).fetchall()

# Migration accompanying this function:
# CREATE INDEX idx_orders_customer_created
#   ON orders (customer_id, created_at DESC);
```

**Pairs with:** Anti-pattern AP-5

**Why it works:** The composite index covers both the predicate (`customer_id`) and the sort (`created_at DESC`) in a single index scan. Pagination is built in with a hard cap (500) preventing accidental "return all" usage. The migration ships with the function so the index exists in every environment the code runs in.

**Additional considerations:** Index columns should follow the query pattern: equality predicates first, range/sort columns next. `(customer_id, created_at)` works for "this customer's orders sorted by date." `(created_at, customer_id)` would not.

---

## AP-6: Unbounded list return from API handler

**Pattern:**

```typescript
// src/api/handlers/comments.ts
app.get("/api/posts/:postId/comments", async (req, res) => {
  const comments = await db.comments.findMany({
    where: { postId: req.params.postId },
  });
  res.json(comments);
});
```

**Violates:** Rule 5.5 (see `rules.md#rule-55-scale-aware-defaults-from-first-commit`)

**Why it fails:** A viral post with 200,000 comments returns 200,000 comments in one response. The server allocates the array, serializes it to JSON, ships it over the wire, and the browser tries to render it. Memory spikes on the server, response time goes from milliseconds to seconds, and the browser tab freezes or runs out of memory. Each of these is a separate failure mode and all three trigger together. The fix is a four-line change at write time and a multi-day investigation at incident time.

**Source for failure mode:** `TGF-SYNTHESIS — grounded in NIST-SSDF v1.1 PW.5 + senior practice`; common API endpoint failure mode.

### CP-6: Paginated handler with hard cap

**Pattern:**

```typescript
// src/api/handlers/comments.ts
const DEFAULT_PAGE_SIZE = 20;
const MAX_PAGE_SIZE = 100;

app.get("/api/posts/:postId/comments", async (req, res) => {
  const requestedLimit = parseInt(req.query.limit as string, 10) || DEFAULT_PAGE_SIZE;
  const limit = Math.min(Math.max(requestedLimit, 1), MAX_PAGE_SIZE);
  const cursor = req.query.cursor as string | undefined;

  const comments = await db.comments.findMany({
    where: { postId: req.params.postId },
    take: limit + 1, // one extra to detect next page
    cursor: cursor ? { id: cursor } : undefined,
    orderBy: { createdAt: "desc" },
  });

  const hasNextPage = comments.length > limit;
  const items = hasNextPage ? comments.slice(0, limit) : comments;
  const nextCursor = hasNextPage ? items[items.length - 1].id : null;

  res.json({ items, nextCursor });
});
```

**Pairs with:** Anti-pattern AP-6

**Why it works:** Default page size is sensible (20). Requested page sizes are clamped to a maximum (100), so a caller cannot opt into the failure mode. Cursor-based pagination is stable under writes (offset pagination drifts when rows are inserted). Response size and server memory are bounded per request regardless of total comment count.

---

## AP-7: Clever one-liner

**Pattern:**

```python
# src/transformers/user_payload.py
def transform_payload(users):
    # one-liner: extract emails, lowercase, strip whitespace, dedupe, sort
    return sorted(set(u["email"].strip().lower() for u in users if u.get("email")))
```

**Violates:** Rule 5.6 (see `rules.md#rule-56-solo-maintainability-as-design-constraint`); also Rule 5.4 (the comment exists only because the code is not self-explaining).

**Why it fails:** The one-liner chains five operations (filter, extract, transform, dedupe, sort) into a single expression. The comment exists because the author noticed the code was unreadable and tried to compensate. A reader debugging this — say, an email-with-trailing-whitespace bug surviving the strip — has to mentally unwind the entire expression to find where the bug enters. Worse, modifying the function (e.g., adding email validation) means rewriting the one-liner; the "clever" win is paid back at every change.

**Source for failure mode:** `TGF-SYNTHESIS — grounded in NIST-SSDF v1.1 PW.4 (reuse well-secured patterns) + senior practice`.

### CP-7: Explicit steps with intent-revealing names

**Pattern:**

```python
# src/transformers/user_payload.py
def extract_unique_emails(users: list[dict]) -> list[str]:
    emails_with_address = (user for user in users if user.get("email"))
    normalized_emails = (user["email"].strip().lower() for user in emails_with_address)
    unique_emails = set(normalized_emails)
    return sorted(unique_emails)
```

**Pairs with:** Anti-pattern AP-7

**Why it works:** Each step has a name. A reader debugging the strip-whitespace bug goes straight to `normalized_emails`. Adding a validation step (e.g., RFC 5322 check) means adding one line in the obvious place rather than restructuring an expression. The function name itself (`extract_unique_emails`) communicates more than the comment did. Generator expressions keep the memory profile equivalent to the one-liner — clarity does not cost performance.

**Additional considerations:** Some genuinely small operations are clearer as one-liners — `return [x * 2 for x in nums]` is readable. The line between "concise" and "clever" is whether a reader has to mentally unwind the expression to understand it.

---

## AP-8: Dependency for single-use call

**Pattern:**

```typescript
// package.json
{
  "dependencies": {
    "is-odd": "^3.0.1",
    "left-pad": "^1.3.0",
    "lodash.padstart": "^4.6.1"
  }
}

// src/format.ts
import isOdd from "is-odd";
import padStart from "lodash.padstart";

function formatTicketNumber(n: number): string {
  if (isOdd(n)) {
    return "ODD-" + padStart(String(n), 6, "0");
  }
  return "EVN-" + padStart(String(n), 6, "0");
}
```

**Violates:** Rule 5.6 (see `rules.md#rule-56-solo-maintainability-as-design-constraint`)

**Why it fails:** Three dependencies added to do work the standard library does in one line each. Every dependency is a maintenance liability: security advisories to track, version compatibility to maintain, transitive dependencies pulled into the lockfile, supply-chain attack surface, the risk of the package being unmaintained or yanked (the historical `left-pad` incident is the canonical example of this category — one package's removal broke thousands of builds). For a one-line operation, the cost-benefit calculation is one-sided.

**Source for failure mode:** `NIST-SSDF v1.1 PW.4` (Reuse Existing, Well-Secured Software When Feasible — applies BOTH ways: reuse when value exceeds risk, and do not pull in dependencies when value does not exceed risk). See also OWASP Top 10:2025 A03 (Software Supply Chain Failures) for the security dimension.

### CP-8: Standard library inline

**Pattern:**

```typescript
// package.json — these dependencies removed

// src/format.ts
function formatTicketNumber(n: number): string {
  const prefix = n % 2 === 0 ? "EVN" : "ODD";
  const padded = String(n).padStart(6, "0");
  return `${prefix}-${padded}`;
}
```

**Pairs with:** Anti-pattern AP-8

**Why it works:** `String.prototype.padStart` has been standard JavaScript since ES2017. `n % 2 === 0` is a one-character expression. The function is shorter than the import lines it replaces, has zero external dependencies, and has zero supply-chain attack surface. The maintenance burden is the same as any other internal function.

**Additional considerations:** This rule does NOT argue against all dependencies. A well-maintained, widely-used library doing meaningful work (an HTTP client, a database driver, a cryptography library) earns its place because writing and maintaining the equivalent in-house would cost more than the dependency does. The test is the same: does value clearly exceed cost?

---

## Pairing discipline

Per `DEC-2026-05-17-003` Clause 1: every anti-pattern is paired with a canonical pattern. The framework's value depends on showing the user *both* what to reject and what to do instead. Standalone anti-patterns without paired canonical patterns are incomplete and do not ship.

When a new anti-pattern is observed during use but no clear canonical pattern is obvious, log to `WAIVER-LOG.md` for revisit rather than shipping a one-sided entry. The `self-evolution.anti-patterns-observed` frontmatter field accumulates candidates for Phase 11 meta-skill review.
