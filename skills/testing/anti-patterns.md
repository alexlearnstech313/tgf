# Anti-Patterns + Canonical Patterns — TESTING

Full anti-pattern + canonical pattern pairs with code examples. Referenced from `SKILL.md` §6 Anti-Pattern Summaries.

Eight anti-pattern pairs covering the most common testing failures including the AI tautological-test mode. Per `DEC-2026-05-17-003` Clause 1: every anti-pattern is paired with a canonical pattern.

---

## AP-1: Tautological tests

**Pattern:**

```typescript
// src/utils/format.ts
export function formatPrice(cents: number): string {
  return '$10.99';  // Hard-coded — but the test doesn't catch it
}

// src/utils/format.test.ts
import { formatPrice } from './format';

test('formats price', () => {
  expect(formatPrice(1099)).toBe('$10.99');  // Passes — but verifies nothing
});

test('formats another price', () => {
  expect(formatPrice(500)).toBe('$10.99');  // Also passes because the function ignores input
});
```

**Violates:** Rule 5.7 (AI-generated tests get behavioral audit) AND Rule 5.1 (test behavior, not implementation). See `rules.md#rule-57-ai-generated-tests-get-behavioral-audit`.

**Why it fails:** Two tests pass green. Coverage shows the function tested. But the function returns a hard-coded value regardless of input — completely broken — and the test suite is silent. The tests don't catch the bug because they were written by reading the implementation and asserting against what the implementation returns, not what the function's CONTRACT promises. This is the canonical AI-generated test failure mode: tests that look right because they mirror the code, but verify nothing because they don't check the contract.

**Source for failure mode:** AI test generation reading the implementation and asserting against it. MITRE ATLAS documents this class of AI output failure.

### CP-1: Contract-based test that catches contract violations

**Pattern:**

```typescript
// src/utils/format.ts — correct implementation
export function formatPrice(cents: number): string {
  const dollars = Math.floor(cents / 100);
  const remainder = cents % 100;
  return `$${dollars}.${remainder.toString().padStart(2, '0')}`;
}

// src/utils/format.test.ts — behavioral tests
import { formatPrice } from './format';

describe('formatPrice', () => {
  test('converts cents to dollar-formatted string with two decimal places', () => {
    expect(formatPrice(1099)).toBe('$10.99');
  });

  test('pads cents below 10', () => {
    expect(formatPrice(105)).toBe('$1.05');
  });

  test('handles zero cents correctly', () => {
    expect(formatPrice(1000)).toBe('$10.00');
  });

  test('handles small amounts', () => {
    expect(formatPrice(50)).toBe('$0.50');
  });

  test('handles large amounts', () => {
    expect(formatPrice(123456)).toBe('$1234.56');
  });

  test('handles zero', () => {
    expect(formatPrice(0)).toBe('$0.00');
  });
});
```

**Pairs with:** Anti-pattern AP-1

**Why it works:** Each test asserts a different observable input → output relationship. If the function returned a hard-coded value, multiple tests would fail. If someone rewrote the function with a different correct implementation (different math, different padding library, different string construction), the tests would still pass — because they verify the CONTRACT (cents in → formatted-dollar-string out) rather than the SHAPE OF THE CODE. The behavioral-audit question — "would these tests pass against a legitimate rewrite?" — answers yes.

**Additional considerations:** Property-based testing (fast-check, Hypothesis) further strengthens this by asserting properties — "for any non-negative integer N, formatPrice(N) starts with '$'; for any N≥0, formatPrice(N) has exactly two digits after the period." Property-based tests catch classes of bugs literal-value tests miss.

---

## AP-2: Implementation-coupled tests

**Pattern:**

```typescript
// src/services/user.ts
class UserService {
  async createUser(data: CreateUserData): Promise<User> {
    this._validateInternal(data);
    const hashed = this._hashPassword(data.password);
    const user = await this._insertToDb({ ...data, password: hashed });
    await this._sendWelcomeEmail(user);
    return user;
  }

  private _validateInternal(data: CreateUserData) { /* ... */ }
  private _hashPassword(pw: string): string { /* ... */ }
  private async _insertToDb(data: any) { /* ... */ }
  private async _sendWelcomeEmail(user: User) { /* ... */ }
}

// src/services/user.test.ts — couples to private methods + call order
test('createUser calls private methods in correct order', () => {
  const service = new UserService();
  const validateSpy = jest.spyOn(service as any, '_validateInternal');
  const hashSpy = jest.spyOn(service as any, '_hashPassword');
  const insertSpy = jest.spyOn(service as any, '_insertToDb');
  const emailSpy = jest.spyOn(service as any, '_sendWelcomeEmail');

  service.createUser({ email: 'x@y.com', password: 'secret' });

  expect(validateSpy).toHaveBeenCalledBefore(hashSpy);
  expect(hashSpy).toHaveBeenCalledBefore(insertSpy);
  expect(insertSpy).toHaveBeenCalledBefore(emailSpy);
});
```

**Violates:** Rule 5.1 (test behavior, not implementation). See `rules.md#rule-51-test-behavior-not-implementation`.

**Why it fails:** The test asserts on private methods and their call order. A future refactor that extracts these into separate classes, inlines them, reorders them (with no behavior change), or replaces them with different internals would all break this test — even though the user-facing behavior of `createUser` would be unchanged. The test becomes a maintenance burden; engineers update spies and expectations every refactor; the test provides no signal that real behavior is correct.

**Source for failure mode:** Common mock-spy-heavy testing pattern that mistakes "code exercise" for "behavior verification."

### CP-2: Behavioral test through the public API

**Pattern:**

```typescript
// src/services/user.test.ts — behavioral
import { UserService } from './user';
import { setupTestDb } from '../test/db';
import { mockEmailProvider } from '../test/email';

describe('UserService.createUser', () => {
  test('creates user with hashed password and sends welcome email', async () => {
    const db = await setupTestDb();
    const email = mockEmailProvider();
    const service = new UserService({ db, email });

    const user = await service.createUser({ email: 'x@y.com', password: 'secret' });

    // Verify behavior: user exists with correct shape
    expect(user.id).toBeDefined();
    expect(user.email).toBe('x@y.com');

    // Verify behavior: password is hashed (not stored plaintext)
    const stored = await db.users.findById(user.id);
    expect(stored.password).not.toBe('secret');
    expect(stored.password.startsWith('$2b$')).toBe(true);  // bcrypt format

    // Verify behavior: welcome email was sent
    expect(email.lastSentTo).toBe('x@y.com');
    expect(email.lastSentSubject).toContain('Welcome');
  });

  test('rejects invalid email', async () => {
    const service = new UserService({ db: await setupTestDb(), email: mockEmailProvider() });
    await expect(
      service.createUser({ email: 'not-an-email', password: 'secret' })
    ).rejects.toThrow(/invalid email/i);
  });

  test('rejects weak password', async () => {
    const service = new UserService({ db: await setupTestDb(), email: mockEmailProvider() });
    await expect(
      service.createUser({ email: 'x@y.com', password: '123' })
    ).rejects.toThrow(/password/i);
  });
});
```

**Pairs with:** Anti-pattern AP-2

**Why it works:** Each test asserts observable behavior — the user record exists with the right shape, the password is hashed (not plaintext), the welcome email reached the right address, invalid inputs are rejected. None of these depend on which private methods exist or in what order they're called. A refactor that combines validation + hashing into one method, splits the email send into a background job, or restructures the service entirely would pass these tests as long as the BEHAVIOR is unchanged. The tests catch real regressions; they don't fire on legitimate refactors.

---

## AP-3: Coverage-percentage chase

**Pattern:**

```typescript
// src/utils/parse.ts
export function parseConfig(input: string): Config | null {
  try {
    return JSON.parse(input);
  } catch {
    return null;
  }
}

// Coverage report showed parseConfig at 50% (only the try branch
// covered). Team set "95% coverage" as the merge gate. Engineer
// added this test to hit the catch branch:

// src/utils/parse.test.ts
test('parseConfig returns null on invalid input', () => {
  parseConfig('not-json');  // Exercise the catch branch — no assertion
});

// Coverage now shows 100%. Pull request passes the gate. No
// behavior verified.
```

**Violates:** Rule 5.4 (coverage is feedback, not target) AND Rule 5.1 (test behavior). See `rules.md#rule-54-coverage-is-feedback-not-target`.

**Why it fails:** The test exercises the catch branch without verifying anything about the catch behavior. Coverage tooling sees the line as covered; the test suite sees no assertion. If parseConfig changed to throw rather than return null on invalid input, the test would still pass — because there's no assertion. The metric improved; the signal didn't.

**Source for failure mode:** Goodhart's Law applied to coverage. When coverage becomes a target, it ceases to be a useful measure.

### CP-3: Targeted behavioral test for the uncovered failure mode

**Pattern:**

```typescript
// src/utils/parse.test.ts — behavioral coverage of both branches
describe('parseConfig', () => {
  test('parses valid JSON to a config object', () => {
    const result = parseConfig('{"name":"foo","version":1}');
    expect(result).toEqual({ name: 'foo', version: 1 });
  });

  test('returns null when input is invalid JSON', () => {
    expect(parseConfig('not-json')).toBeNull();
    expect(parseConfig('{ unterminated')).toBeNull();
    expect(parseConfig('')).toBeNull();
  });

  test('returns null without throwing on null/undefined-like input', () => {
    expect(parseConfig('null')).toBeNull();
    expect(parseConfig('undefined')).toBeNull();  // not valid JSON
  });

  // (Plus: discussion in code review about whether parseConfig
  // SHOULD return null for "null" input — is "null is a valid
  // config" the contract, or should null mean parse-failure?
  // The behavioral discussion this surfaces is the real value;
  // coverage was just the prompt.)
});
```

**Pairs with:** Anti-pattern AP-3

**Why it works:** The tests now verify observable behavior in both branches. The catch-branch test asserts the return value is null, not just that the catch was reached. Multiple invalid inputs verified — different shapes of "invalid" still produce null. The coverage gap that prompted the test became a real test that catches real regressions. Plus, the team discussion about edge cases (literal `"null"` string as input) surfaced a contract question worth resolving.

**Additional considerations:** Coverage gates can be lifted entirely — the pull-request reviewer asks "does this PR have appropriate behavioral tests?" rather than relying on a percentage gate. The discipline shifts from numbers to judgment.

---

## AP-4: Missing trust-boundary tests

**Pattern:**

```typescript
// src/api/handlers/users.ts
app.post('/api/users', async (req, res) => {
  const { email, password, role } = req.body;
  const user = await userService.create({ email, password, role });
  res.json(user);
});

// src/api/handlers/users.test.ts — only happy path
test('POST /api/users creates a user', async () => {
  const res = await request(app)
    .post('/api/users')
    .send({ email: 'x@y.com', password: 'secret', role: 'user' });
  expect(res.status).toBe(200);
  expect(res.body.id).toBeDefined();
});
```

**Violates:** Rule 5.2 (trust-boundary tests are mandatory). See `rules.md#rule-52-trust-boundary-tests-are-mandatory`.

**Why it fails:** The endpoint accepts user-supplied input at a trust boundary (HTTP request body). The single test verifies the happy path — well-formed input produces a user. The failure modes are untested:

- What if email is missing? Email is malformed? Email is 10MB long?
- What if password is too short? Too long? Missing entirely? Null?
- What if `role` is provided as `'admin'` by a non-admin caller? (Privilege escalation if authorization isn't checked at the boundary.)
- What if the body is malformed JSON entirely?
- What if `req.body` is null (no body sent)?
- What if Content-Type is wrong?

Each of these is a real failure mode that production traffic will eventually hit. Untested = production discovery time.

**Source for failure mode:** Common AI-generated test pattern — happy path only. AP-4 is one of the most-frequent classes in AI-generated test suites.

### CP-4: Comprehensive trust-boundary tests

**Pattern:**

```typescript
// src/api/handlers/users.test.ts — boundary cases covered
describe('POST /api/users', () => {
  // Happy path
  test('creates user with valid input', async () => {
    const res = await request(app)
      .post('/api/users')
      .send({ email: 'x@y.com', password: 'goodPassword123', role: 'user' });
    expect(res.status).toBe(200);
    expect(res.body.id).toBeDefined();
  });

  // Schema-violation cases
  test('rejects request with missing email', async () => {
    const res = await request(app).post('/api/users').send({ password: 'goodPassword123' });
    expect(res.status).toBe(400);
    expect(res.body.error).toMatch(/email/i);
  });

  test('rejects malformed email', async () => {
    const res = await request(app).post('/api/users').send({
      email: 'not-an-email', password: 'goodPassword123',
    });
    expect(res.status).toBe(400);
  });

  test('rejects password shorter than minimum', async () => {
    const res = await request(app).post('/api/users').send({
      email: 'x@y.com', password: '123',
    });
    expect(res.status).toBe(400);
  });

  test('rejects oversized payload', async () => {
    const res = await request(app).post('/api/users').send({
      email: 'x@y.com', password: 'a'.repeat(10_000_000), role: 'user',
    });
    // Either rejected at the request level (413) or schema-validated and rejected (400)
    expect([400, 413]).toContain(res.status);
  });

  // Authorization at trust boundary (privilege escalation defense)
  test('rejects role:admin from non-admin caller', async () => {
    const res = await request(app)
      .post('/api/users')
      .set('Authorization', `Bearer ${nonAdminToken}`)
      .send({ email: 'x@y.com', password: 'goodPassword123', role: 'admin' });
    // Either the role should be ignored / overwritten to 'user', or the request rejected
    expect(res.body.role).not.toBe('admin');
  });

  // Malformed body
  test('rejects malformed JSON body gracefully', async () => {
    const res = await request(app)
      .post('/api/users')
      .set('Content-Type', 'application/json')
      .send('{ unterminated');
    expect(res.status).toBe(400);  // Not 500
  });

  test('rejects empty body', async () => {
    const res = await request(app).post('/api/users').send({});
    expect(res.status).toBe(400);
  });
});
```

**Pairs with:** Anti-pattern AP-4

**Why it works:** Each test covers a real failure mode the boundary may encounter. Schema violations, oversized payloads, privilege-escalation attempts, malformed input — all return appropriate errors (not 500, not silent acceptance, not crash). The boundary becomes verifiable: the contract for the endpoint is "accept well-formed input; reject malformed input with informative errors; never crash on bad input; never accept privilege escalation."

---

## AP-5: Test pyramid forced on a frontend project

**Pattern:**

```typescript
// React + Next.js codebase. Team adopts test pyramid.
// 200 unit tests for components in isolation:

// src/components/SearchInput.test.tsx
import { render } from '@testing-library/react';
import { SearchInput } from './SearchInput';

test('renders input element', () => {
  const { getByRole } = render(<SearchInput onChange={() => {}} />);
  expect(getByRole('textbox')).toBeInTheDocument();
});

test('renders with placeholder', () => {
  const { getByPlaceholderText } = render(<SearchInput placeholder="Search..." onChange={() => {}} />);
  expect(getByPlaceholderText('Search...')).toBeInTheDocument();
});

// ...200 more like this. Each tests one tiny behavior of one component
// in isolation. Together they verify 5% of the bugs that actually
// happen in production, all of which live in component INTEGRATION
// (search input + debouncing + URL params + results list + pagination).
```

**Violates:** Rule 5.3 (test shape follows domain). See `rules.md#rule-53-test-shape-follows-domain`.

**Why it fails:** The bugs in a React app live at the integration boundary — between components, between component and data, between user interaction and URL state, between optimistic UI updates and server confirmations. Testing components in isolation with rendered-input + mocked-handlers verifies the component renders, but doesn't verify the interactions that matter. Production bugs slip through: "the search results don't update when URL params change," "the pagination resets to page 1 unexpectedly," "the debounce timing fights with the loading spinner" — none of these caught by component-isolated unit tests.

**Source for failure mode:** Test pyramid as universal dogma. Mike Cohn's original pyramid (2009) was for traditional backend stacks; modern web doesn't fit.

### CP-5: Testing-trophy approach for frontend

**Pattern:**

```typescript
// Heavy integration testing — components in their integration context

// src/features/search/SearchPage.test.tsx
import { render, screen, waitFor } from '@testing-library/react';
import { userEvent } from '@testing-library/user-event';
import { SearchPage } from './SearchPage';
import { server } from '../test/mocks/server';
import { http, HttpResponse } from 'msw';

describe('SearchPage', () => {
  test('searches when user types and displays results', async () => {
    server.use(
      http.get('/api/search', () => HttpResponse.json({
        results: [{ id: 1, name: 'Result A' }, { id: 2, name: 'Result B' }],
      }))
    );

    const user = userEvent.setup();
    render(<SearchPage />);

    await user.type(screen.getByRole('textbox'), 'test');

    // Wait for debounce + fetch + render
    await waitFor(() => {
      expect(screen.getByText('Result A')).toBeInTheDocument();
      expect(screen.getByText('Result B')).toBeInTheDocument();
    });
  });

  test('updates URL when search query changes', async () => {
    const user = userEvent.setup();
    render(<SearchPage />);

    await user.type(screen.getByRole('textbox'), 'banana');

    await waitFor(() => {
      expect(window.location.search).toContain('q=banana');
    });
  });

  test('preserves search state when navigating back', async () => {
    // Test the URL-state-restoration integration that's often broken
    // ...
  });

  test('shows loading indicator while searching', async () => { /* ... */ });
  test('shows empty state when no results', async () => { /* ... */ });
  test('shows error state when search fails', async () => { /* ... */ });
});

// A few unit tests for genuinely-unit logic:
// src/features/search/utils.test.ts
test('debounceQuery returns same instance for same delay', () => { /* ... */ });
test('parseSearchParams handles empty input', () => { /* ... */ });

// Plus a small number of E2E tests for critical user flows:
// e2e/search.spec.ts (Playwright)
test('search → click result → returns to search with state preserved', async ({ page }) => { /* ... */ });
```

**Pairs with:** Anti-pattern AP-5

**Why it works:** Heavy integration testing — components in their integration context (with realistic data, realistic user interactions, realistic state coordination). Tests catch the bugs that actually happen: URL state coordination, loading + empty + error states, user-interaction timing, multi-component coordination. Lighter unit testing for genuinely-unit logic (utility functions, pure data transformations). A small set of E2E tests for critical user flows. The shape matches where the bugs live.

**Additional considerations:** The TROPHY shape doesn't mean "no unit tests" — it means the weight is shifted. Some logic is naturally unit-testable (pure functions, format utilities, validation helpers) and gets tested at that level. The shift is in NOT trying to test components in isolation when their bugs are at integration level.

---

## AP-6: Mock-everything tests

**Pattern:**

```typescript
// src/services/order.test.ts — every dependency mocked
test('processOrder charges the customer and saves the order', async () => {
  const mockStripe = {
    charges: { create: jest.fn().mockResolvedValue({ status: 'succeeded', id: 'ch_123' }) }
  };
  const mockDb = {
    orders: { insert: jest.fn().mockResolvedValue({ id: 'ord_123' }) }
  };
  const mockInventory = {
    reserve: jest.fn().mockResolvedValue({ ok: true })
  };
  const mockEmail = {
    send: jest.fn().mockResolvedValue({ sent: true })
  };

  const service = new OrderService({
    stripe: mockStripe,
    db: mockDb,
    inventory: mockInventory,
    email: mockEmail,
  });

  const result = await service.processOrder({ customerId: 'c_123', items: [{ sku: 'A', qty: 1 }] });

  expect(mockStripe.charges.create).toHaveBeenCalled();
  expect(mockDb.orders.insert).toHaveBeenCalled();
  expect(mockInventory.reserve).toHaveBeenCalled();
  expect(mockEmail.send).toHaveBeenCalled();
});
```

**Violates:** Rules 5.1 (test behavior) and 5.2 (trust boundaries). See `rules.md`.

**Why it fails:** Every dependency is mocked to return success. The test asserts that each mock was called. The test passes; the real behavior is verified only at the most superficial level. What's NOT verified:

- That the Stripe charge amount actually matches the order total (the mock returns success regardless of input).
- That the inventory reservation actually reserves the correct items (mock returns ok regardless).
- That the database write actually persists the data (mock returns an ID but doesn't store anything).
- That the email recipient is the customer (mock accepts anything).
- That the order of operations is correct under failure (what if Stripe succeeds but DB write fails — does inventory get freed?).

The test verifies "the service calls its dependencies," not "the service does what it should." When real bugs ship (charged wrong amount, reserved wrong items, didn't send email), the test was green the whole time.

**Source for failure mode:** AI default to mocking everything (it's "easier" — no setup); plus engineering practice that conflates "fast tests" with "good tests."

### CP-6: Real implementations where possible, mocks only at true external boundaries

**Pattern:**

```typescript
// src/services/order.test.ts
import { setupTestDb } from '../test/db';
import { setupStripeTestMode } from '../test/stripe';
import { OrderService } from './order';

describe('OrderService.processOrder', () => {
  test('charges customer correct amount and persists order', async () => {
    const db = await setupTestDb();                    // Real DB (test instance)
    const stripe = setupStripeTestMode();              // Stripe test-mode API (real Stripe, test mode)
    const inventory = new InventoryService({ db });    // Real inventory service against test DB
    const emails: SentEmail[] = [];
    const email = { send: async (msg) => { emails.push(msg); } };  // Mock at the actual external boundary

    // Seed test data
    await db.products.insert({ sku: 'A', priceCents: 1500, stock: 10 });
    await db.customers.insert({ id: 'c_123', email: 'real@test.com', stripeCustomerId: 'cus_test_123' });

    const service = new OrderService({ stripe, db, inventory, email });

    const result = await service.processOrder({
      customerId: 'c_123',
      items: [{ sku: 'A', qty: 2 }],
    });

    // Verify behavior: customer charged correct amount
    const charge = await stripe.charges.retrieve(result.chargeId);
    expect(charge.amount).toBe(3000);  // 2 * 1500
    expect(charge.status).toBe('succeeded');

    // Verify behavior: order persisted with correct shape
    const order = await db.orders.findById(result.orderId);
    expect(order.customerId).toBe('c_123');
    expect(order.totalCents).toBe(3000);
    expect(order.items).toEqual([{ sku: 'A', qty: 2, lineTotalCents: 3000 }]);

    // Verify behavior: inventory decremented correctly
    const product = await db.products.findBySku('A');
    expect(product.stock).toBe(8);  // 10 - 2

    // Verify behavior: email sent to correct address
    expect(emails).toHaveLength(1);
    expect(emails[0].to).toBe('real@test.com');
    expect(emails[0].body).toContain('Order Confirmation');
  });

  test('rolls back inventory if charge fails', async () => {
    // ... real test of the failure-mode behavior with real DB + Stripe test mode
  });
});
```

**Pairs with:** Anti-pattern AP-6

**Why it works:** Real implementations (test database, Stripe test mode, real inventory service against test DB) verify actual behavior. Mocks limited to true external boundaries (the email-sending service is mocked, but the mock captures the actual message that would be sent — so the test verifies email content + recipient). Each assertion verifies an observable outcome: charge amount correct, order persisted, inventory decremented, email sent to right address. Bugs in any of these behaviors fail the test.

**Additional considerations:** "Real database" doesn't mean production — it means a test instance (sqlite in-memory, dockerized postgres, in-memory adapter). The point is the database integration is exercised; the boundary code (SQL, ORM, schema) actually runs.

---

## AP-7: Security-relevant change shipped without security testing

**Pattern:**

```typescript
// src/api/handlers/admin.ts — new admin endpoint added
app.delete('/api/admin/users/:id', requireAuth, async (req, res) => {
  await userService.delete(req.params.id);
  res.json({ ok: true });
});

// src/api/handlers/admin.test.ts — only happy path
test('admin can delete user', async () => {
  const res = await request(app)
    .delete('/api/admin/users/u_123')
    .set('Authorization', `Bearer ${adminToken}`);
  expect(res.status).toBe(200);
});
```

**Violates:** Rule 5.5 (security testing per OWASP WSTG). See `rules.md#rule-55-security-testing-per-owasp-wstg`.

**Why it fails:** The endpoint deletes users. Security-relevant changes (admin operations, authorization gates) need security tests. The single test verifies the happy path. Untested:

- Can a non-admin authenticated user delete users? (WSTG-ATHZ — authorization)
- Can an unauthenticated request delete users? (WSTG-ATHN — authentication)
- Can a user delete themselves? (potentially valid; check it's tested)
- Can the path parameter be manipulated to cause path traversal or to target unintended resources? (WSTG-ATHZ)
- Is rate limiting in place to prevent bulk-deletion attacks? (WSTG-INPV / business logic)
- Is the action logged for audit? (WSTG-ERRH / SECURITY-CORE Rule 5.7)

Shipping without these tests means a regression in any of these dimensions ships silently.

**Source for failure mode:** Common AI happy-path-only test generation, especially when the prompt didn't surface security concerns.

### CP-7: OWASP WSTG-aligned security tests

**Pattern:**

```typescript
// src/api/handlers/admin.test.ts — comprehensive security testing

describe('DELETE /api/admin/users/:id', () => {
  // WSTG-ATHN — authentication
  test('rejects request without authentication', async () => {
    const res = await request(app).delete('/api/admin/users/u_123');
    expect(res.status).toBe(401);
  });

  test('rejects request with invalid token', async () => {
    const res = await request(app)
      .delete('/api/admin/users/u_123')
      .set('Authorization', 'Bearer invalid-token');
    expect(res.status).toBe(401);
  });

  test('rejects request with expired token', async () => {
    const res = await request(app)
      .delete('/api/admin/users/u_123')
      .set('Authorization', `Bearer ${expiredToken}`);
    expect(res.status).toBe(401);
  });

  // WSTG-ATHZ — authorization
  test('rejects request from non-admin authenticated user', async () => {
    const res = await request(app)
      .delete('/api/admin/users/u_123')
      .set('Authorization', `Bearer ${regularUserToken}`);
    expect(res.status).toBe(403);
  });

  test('admin cannot delete via parameter injection', async () => {
    // Attempt to bypass via various parameter manipulations
    const attempts = ['u_123/../u_456', 'u_123;u_456', 'u_123 OR 1=1', '*'];
    for (const id of attempts) {
      const res = await request(app)
        .delete(`/api/admin/users/${encodeURIComponent(id)}`)
        .set('Authorization', `Bearer ${adminToken}`);
      expect([400, 404]).toContain(res.status);  // Rejected or not-found, never accepted
    }
  });

  // Happy path
  test('admin can delete an existing user', async () => {
    const res = await request(app)
      .delete('/api/admin/users/u_123')
      .set('Authorization', `Bearer ${adminToken}`);
    expect(res.status).toBe(200);
    const deleted = await db.users.findById('u_123');
    expect(deleted).toBeNull();
  });

  // WSTG-BUSL — business logic / audit
  test('deletion action is logged for audit', async () => {
    await request(app)
      .delete('/api/admin/users/u_123')
      .set('Authorization', `Bearer ${adminToken}`);

    const auditEntries = await db.auditLog.findAll({ action: 'user_deleted', targetId: 'u_123' });
    expect(auditEntries).toHaveLength(1);
    expect(auditEntries[0].actorId).toBeDefined();
  });

  test('non-existent user returns 404 not 500', async () => {
    const res = await request(app)
      .delete('/api/admin/users/nonexistent')
      .set('Authorization', `Bearer ${adminToken}`);
    expect(res.status).toBe(404);
  });
});
```

**Pairs with:** Anti-pattern AP-7

**Why it works:** Tests cover the OWASP WSTG categories relevant to this endpoint: authentication (WSTG-ATHN — unauthenticated, invalid token, expired token), authorization (WSTG-ATHZ — non-admin user, parameter manipulation), business logic (WSTG-BUSL — audit logging), error handling (WSTG-ERRH — 404 not 500 for non-existent). The endpoint's security surface is verifiable. Future security regressions fire loudly.

---

## AP-8: Accessibility test as axe-only

**Pattern:**

```typescript
// jest.config.js — jest-axe configured
// test/setup.ts — extends expect with toHaveNoViolations()

// src/components/Form.test.tsx
import { render } from '@testing-library/react';
import { axe } from 'jest-axe';
import { Form } from './Form';

test('Form has no accessibility violations', async () => {
  const { container } = render(<Form />);
  const results = await axe(container);
  expect(results).toHaveNoViolations();
});

// Manual testing skipped. Keyboard navigation never walked through.
// Screen reader never run against the form. Focus management not
// verified. Test suite passes.
```

**Violates:** Rule 5.6 (accessibility testing per WCAG 2.2). See `rules.md#rule-56-accessibility-testing-per-wcag-22`.

**Why it fails:** axe-core catches ~30-40% of WCAG conformance issues — primarily the structural ones (missing labels, color contrast measurable from CSS, ARIA usage errors, heading hierarchy). It DOESN'T catch:

- Whether focus ORDER matches visual order (axe sees tabindex but doesn't trace the flow).
- Whether keyboard-only users can complete the whole flow (modal trap returns focus correctly? skip-link works?).
- Whether screen reader announces dynamic state (form validation errors, modal open, content load).
- Whether custom interactive components have appropriate keyboard semantics (custom dropdown supports Arrow keys, Enter, Escape, type-ahead).
- Whether motion can be disabled.
- Whether text scales reasonably to 200%.

Shipping with axe-only testing means 60-70% of accessibility issues slip through. Users with assistive tech encounter them at use time.

**Source for failure mode:** AI tendency to configure automated tooling and stop there; the manual rhythm requires deliberate process.

### CP-8: Axe + manual keyboard + screen reader + visual

**Pattern:**

```typescript
// Automated layer: axe-core in unit tests + Playwright accessibility audits
// src/components/Form.test.tsx
test('Form has no axe violations', async () => {
  const { container } = render(<Form />);
  expect(await axe(container)).toHaveNoViolations();
});

// e2e/accessibility.spec.ts (Playwright)
test('checkout flow has no axe violations end-to-end', async ({ page }) => {
  await page.goto('/checkout');
  const accessibilityScanResults = await new AxeBuilder({ page }).analyze();
  expect(accessibilityScanResults.violations).toEqual([]);
});

// Plus: keyboard navigation tested explicitly with Playwright
test('checkout completes with keyboard only', async ({ page }) => {
  await page.goto('/checkout');
  await page.keyboard.press('Tab');  // → Email input
  await page.keyboard.type('test@example.com');
  await page.keyboard.press('Tab');  // → Card input
  // ... walk the entire flow keyboard-only
  await page.keyboard.press('Enter');  // submit
  await page.waitForURL(/\/confirmation/);
});

// Plus: focus management tested
test('modal returns focus to trigger on close', async ({ page }) => {
  await page.goto('/');
  await page.getByRole('button', { name: 'Open settings' }).click();
  await page.getByRole('button', { name: 'Close' }).click();
  await expect(page.getByRole('button', { name: 'Open settings' })).toBeFocused();
});

// Plus: documented manual testing rhythm
// docs/ACCESSIBILITY-TESTING.md:
// "Pre-release manual checks:
//   1. Walk every primary user flow keyboard-only (no mouse). Note any
//      element that can't be reached, any focus trap, any unclear focus.
//   2. VoiceOver smoke test (macOS) on key pages: home, login, checkout,
//      dashboard. Are landmarks announced? Are form errors read on
//      validation? Is dynamic content announced?
//   3. Browser zoom 200% — does layout break? Does text get cut off?
//   4. prefers-reduced-motion enabled — do animations respect it?"
```

**Pairs with:** Anti-pattern AP-8

**Why it works:** Three layers stacked. Automated tooling (axe-core in unit + Playwright e2e) catches the structural issues. Programmatic keyboard tests (Playwright) catch focus order and keyboard-completion failures. Documented manual rhythm covers what automation can't — screen reader announcement, zoom behavior, motion respect. The combination catches the ~95-99% of WCAG conformance issues; the residual is rare edge-case work.

---

## Pairing discipline

Per `DEC-2026-05-17-003` Clause 1: every anti-pattern is paired with a canonical pattern.

When a new TESTING anti-pattern is observed during use but no clear canonical pattern is obvious, log to `WAIVER-LOG.md` for revisit rather than shipping a one-sided entry.
