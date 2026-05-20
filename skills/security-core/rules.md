# Rules — SECURITY-CORE

Full rule statements with citations, plain-language impact, and extended discussion. Referenced from `SKILL.md` §5 Rule Summaries. Loaded on demand when deep rule application is needed (typically Stage 5 Phase 2 Security Audit and Stage 5 Phase 3 Red Team).

Seven rules covering universal security categories. Citation granularity per Phase 4 Checkpoint 1 Decision A: OWASP Top 10:2025 at category level; OWASP ASVS 5.0.0 at rule level (e.g., `V1.2.5`); NIST SSDF at practice level (PW.5, PW.6, PW.7); OWASP LLM Top 10 at category level (`LLM01:2025`, etc.).

---

## Rule 5.1: Validate Input at Trust Boundaries

**Statement:** Every input from an external source — user-submitted, network-received, file-parsed, third-party-API-returned — is validated against an explicit schema before use. Validation happens at the boundary where the input enters the application, not "eventually" inside business logic. Validation rejects on shape mismatch (wrong type, missing required field, out-of-range value) rather than coercing silently.

**Citation:** `OWASP-TOP10 A05:2025 (Injection)` + `OWASP-ASVS 5.0 V2 (Validation and Business Logic)`.

**Plain-language impact:** Without validation at the boundary, untrusted data spreads through the application before its shape is verified. A missing field becomes a null-dereference crash three layers deep; a malformed value becomes an injection payload at the database; a wrong type becomes a security check that silently passes. By the time the failure surfaces, the trail back to "the API didn't validate the request body" is lost.

**Extended discussion:** "Trust boundary" means anywhere data crosses from a context the application does not control into a context it does. The HTTP request body crossing into the controller. The third-party API response crossing into the service layer. The file content crossing into the parser. The message-queue payload crossing into the consumer.

Validation at the boundary uses an explicit schema — pydantic / zod / joi / json-schema / language-native types with runtime validation. The schema declares what's required, what's optional, what types, what ranges, what regex patterns. Inputs that don't match are rejected with a clear error to the caller (HTTP 400, not HTTP 500). Inputs that DO match flow inward with the type guarantees the schema established.

Validation is NOT sanitization. Sanitization tries to "clean" bad input into something acceptable; validation rejects bad input entirely. Sanitization assumes you know all the ways something can be bad; validation only allows what you know is good. For untrusted input, validation is the discipline; sanitization (when needed for things like HTML rendering) happens AFTER validation, at the output context (see Rule 5.6).

AI-generated code commonly defaults to permissive validation ("accept this if it has the field at all") or skips validation entirely when the prompt didn't specify it. Surface this in Stage 5 Phase 2 review.

**Related anti-patterns:** AP-6 (SQL injection), AP-8 (shell from user input) (see `anti-patterns.md`)

---

## Rule 5.2: Authorize Every Action, Default Deny

**Statement:** Every operation that touches protected data or invokes a protected capability verifies the caller's authorization at the operation site. Authorization defaults to "deny" unless an explicit rule permits the operation for the caller. Authorization is checked at the trust boundary closest to the protected resource — not exclusively at the route or middleware layer where it can be bypassed by a different code path reaching the same resource.

**Citation:** `OWASP-TOP10 A01:2025 (Broken Access Control)` (the #1 category in the 2025 list) + `OWASP-ASVS 5.0 V8 (Authorization)`.

**Plain-language impact:** Without authorization at the operation site, a request that bypasses the expected entry point (a different API endpoint, a background job, a webhook handler) reaches the protected resource without the check. The vulnerability is invisible in normal-path testing because the normal path includes the check; only the bypass path is missing it. Most real-world access control breaches are this pattern: the check exists in one place, the resource is reachable through three places.

**Extended discussion:** Authorization is the rule that says *who* can do *what* to *which resource*. It depends on the answer to authentication ("who are you?") but is a separate concern. A user with a valid login still cannot edit another user's profile; that's authorization, not authentication.

"Default deny" means the absence of an explicit permission is treated as denial. The opposite — "permit unless something blocks it" — is how privilege escalation happens: every missed check becomes an open door. Default deny means writing the explicit allow rules; the cost is small, the failure mode is closed.

"At the operation site" means the authorization check is co-located with the operation that reads or writes the protected data. Putting authorization at the route layer alone is insufficient because background jobs, webhook handlers, internal cron, and direct-database paths bypass the route layer. Putting authorization at the service or repository layer (the trust boundary closest to the resource) catches all paths.

The hard-refusal list (per `CLAUDE.md` §5) explicitly forbids "bypassing authorization for 'convenience' on endpoints handling user data." This rule is the rule that's being bypassed in that scenario; do not weaken it for convenience.

Authentication failures (`A07:2025`) are a related but distinct category — they're about failures in the "who are you?" step, before authorization runs. Future skills `security-iam-authentication` (Phase 6) and `security-iam-sessions` (Phase 6) cover authentication depth.

**Related anti-patterns:** AP-7 (authorization by obscurity) (see `anti-patterns.md`)

---

## Rule 5.3: Use Established Cryptography; Never Roll Your Own

**Statement:** Cryptographic operations (hashing, encryption, signing, key derivation, random generation) use well-vetted libraries with current algorithm choices. No custom crypto — no homemade hash functions, no ad-hoc "encryption" via XOR or rotation, no roll-your-own protocol design. No cryptographically broken algorithms for security purposes: MD5, SHA-1, DES, RC4, MD4, ECB-mode block ciphers without authentication.

**Citation:** `OWASP-TOP10 A04:2025 (Cryptographic Failures)` + `OWASP-ASVS 5.0 V11 (Cryptography)`. Items from the hard-refusal list per `CLAUDE.md` §5: "Custom cryptography (rolling your own crypto)" and "Use of cryptographically broken algorithms (MD5/SHA-1 for security purposes, DES, RC4)."

**Plain-language impact:** Custom crypto has an essentially 100% track record of failure. The author writes something that "feels secure" because they don't know what the standard attacks look like; the attackers do. A "clever" hash function gets broken in days when a real cryptanalyst looks at it. The cost of using `bcrypt` for passwords is a one-line import; the cost of using a homemade function is a public breach when it gets cracked.

**Extended discussion:** Cryptography is an area where the gap between "this looks right to a non-expert" and "this is actually secure" is enormous. Decades of cryptanalysis have surfaced subtle attacks against algorithms that initially looked fine. Established libraries (libsodium / NaCl, OpenSSL via wrappers like cryptography in Python, Tink, the language's own well-maintained `crypto` module) have been hardened against these attacks and are continuously updated.

*Current algorithm choices (2026 baseline):*
- **Password hashing:** Argon2id (preferred), bcrypt, or scrypt. Never MD5, SHA-1, SHA-256, or "salted SHA-256" — those are general-purpose hashes, not password hashes. The distinction matters: password hashes are deliberately slow to resist offline cracking.
- **General-purpose hashing (data integrity, content-addressable storage):** SHA-256, SHA-3, BLAKE2/3.
- **Authenticated encryption:** AES-256-GCM, ChaCha20-Poly1305. Never AES-ECB; never AES-CBC without HMAC.
- **Asymmetric crypto:** Ed25519 for signatures, X25519 for key exchange, RSA-2048+ with OAEP padding when interop requires RSA.
- **Random generation for security purposes:** `secrets` (Python), `crypto.randomBytes` (Node), `crypto/rand` (Go), `/dev/urandom` underneath. Never `random` (Python's non-cryptographic PRNG), `Math.random()` (JS), or `rand()` (C).

*Failure modes to watch for:*
- AI-generated code defaulting to `md5(password)` or `sha1(password)` — common in training data because the patterns date back to early 2000s tutorials.
- "Encryption" that's actually obfuscation — XOR with a static key, base64 encoding called "encryption," Caesar ciphers.
- Authenticated-encryption modes used without authentication (AES-GCM with the tag discarded; AES-CBC without HMAC).
- Key reuse — same key for multiple users or multiple contexts; static IVs.

Depth on each of these in future skills `security-cryptography` (Phase 7) and `security-data-encryption` (Phase 7).

**Related anti-patterns:** AP-2 (custom cryptography), AP-4 (MD5 or SHA-1 for security) (see `anti-patterns.md`)

---

## Rule 5.4: Secrets Never in Code, Logs, or Version Control

**Statement:** Credentials, API keys, tokens, encryption keys, database passwords, and other secrets are stored in environment variables (development), dedicated secret managers (production), or platform-native credential stores. Never in source code; never in version control; never in log output; never in error messages returned to clients. Secrets that leak via any of those channels are treated as compromised and rotated.

**Citation:** `OWASP-TOP10 A02:2025 (Security Misconfiguration)` (#2 in the 2025 list — promoted from #5 in 2021) + `OWASP-ASVS 5.0 V11 (Cryptography)`. Item from the hard-refusal list per `CLAUDE.md` §5: "Hardcoded credentials in code or version control."

**Plain-language impact:** A secret in source code becomes a secret in version control becomes a secret in every clone of the repo forever. Even after removal, the secret remains in git history and must be rotated. A secret in logs becomes a secret in the centralized logging system, in everyone's monitoring dashboards, in the SOC 2 audit trail — all places not designed for secret handling. The cost of one leaked secret compounds with every system it accessed.

**Extended discussion:** Secrets have a lifecycle distinct from code. They rotate when compromised; they have access scopes that change; they expire. None of those operations work cleanly when the secret is embedded in source code or version control history.

*Where secrets live:*
- **Development:** environment variables loaded from `.env` files (gitignored). `.env.example` committed to document the variable NAMES without the values. The `.env` file itself never committed.
- **Production:** dedicated secret managers (AWS Secrets Manager, HashiCorp Vault, GCP Secret Manager, Azure Key Vault), platform-native credential stores (Vercel/Netlify env vars, Kubernetes secrets with appropriate at-rest encryption), or service-mesh sidecar credential injection.
- **CI/CD:** the CI platform's encrypted secret storage (GitHub Actions secrets, GitLab CI variables marked masked + protected), with explicit allowlists for which jobs can read them.

*Where secrets must NOT appear:*
- Source code (including config files, fixtures, examples)
- Version control (current state OR git history — leaked secrets in history require rotation, not just deletion)
- Log lines (`logger.info(request)` where `request` includes an `Authorization` header is a leak)
- Error responses to clients (`{"error": "DB connection failed: postgres://user:PASSWORD@host"}`)
- Comments (the "temporary" hardcode that becomes permanent)
- Compiled bundles or shipped binaries (build-time secrets need build-time injection, not source-embedded)

*Common AI-generated failure mode:* AI tends to use placeholder strings like `"YOUR_API_KEY_HERE"` that work in development but get committed. The placeholder catches some cases but not all — a real API key copy-pasted "just to test" remains a common leakage vector. Pre-commit hooks (per `docs/ARCHITECTURE.md` §18) catch the most common patterns; the rule is the discipline.

Future skills `security-secrets-management` (Phase 7) and `security-supply-chain` (Phase 7) cover depth on secret rotation, scoping, and supply-chain leak vectors.

**Related anti-patterns:** AP-1 (hardcoded credentials), AP-5 (logging sensitive data) (see `anti-patterns.md`)

---

## Rule 5.5: TLS Verification Always Enabled, Strong Defaults

**Statement:** Outbound HTTPS calls verify server certificates against the system trust store. Inbound HTTPS servers enforce minimum TLS 1.2 (prefer 1.3) with strong cipher suites. HSTS headers configured for browser-facing endpoints. Certificate pinning where threat model warrants. Disabled TLS verification for "convenience" or "during development with self-signed certs" is forbidden in code that ever reaches production paths.

**Citation:** `OWASP-TOP10 A02:2025 (Security Misconfiguration)` + `OWASP-ASVS 5.0 V12 (Secure Communication)`. Item from the hard-refusal list per `CLAUDE.md` §5: "Disabled SSL/TLS verification."

**Plain-language impact:** TLS verification is what prevents a network attacker from sitting between the client and server, presenting a fake certificate, and reading or modifying the traffic. Disable verification and the entire purpose of HTTPS is forfeited — the connection becomes encrypted to whoever happens to be on the network path, not specifically to the server you intended to reach. A breach via disabled-TLS is hard to detect because the application behaves normally; the data just also goes to an attacker.

**Extended discussion:** TLS has three properties: confidentiality (no one reads it), integrity (no one modifies it), and authenticity (you're talking to who you think you are). Disabling certificate verification preserves the first two against passive eavesdroppers but destroys the third against any active attacker on the path — and active attackers are common in coffee-shop Wi-Fi, hotel networks, corporate proxies, and increasingly in supply-chain contexts.

*Common disabled-verification patterns (all forbidden):*
- Node.js: `https.Agent({ rejectUnauthorized: false })`, `process.env.NODE_TLS_REJECT_UNAUTHORIZED = '0'`
- Python `requests`: `verify=False` (often paired with `urllib3.disable_warnings()` to suppress the "you've disabled TLS verification" warning)
- Go: `tls.Config{InsecureSkipVerify: true}`, `http.Transport.TLSClientConfig` with that flag
- curl: `-k` or `--insecure`
- Java: custom `TrustManager` that accepts all certificates

*Legitimate alternatives when self-signed certificates ARE needed (e.g., internal-only services):*
- Add the specific self-signed cert to the trust store: in Node, `https.Agent({ ca: fs.readFileSync('internal-ca.pem') })`; in Python, `verify='/path/to/internal-ca.pem'`.
- Use a private CA and add THAT root to the trust store.
- Use mTLS where both sides present certificates from a known CA.

*Server-side requirements:*
- Minimum TLS 1.2 — TLS 1.0 and 1.1 are deprecated per RFC 8996 and have known weaknesses.
- Prefer TLS 1.3 for new deployments — simpler handshake, better cipher discipline, forward secrecy by default.
- Strong cipher suites — disable RC4, 3DES, export-grade ciphers, CBC-mode without AEAD.
- HSTS header (`Strict-Transport-Security: max-age=63072000; includeSubDomains`) on browser-facing endpoints prevents HTTPS downgrade attacks. Preload registration for high-value domains.
- HTTP→HTTPS redirect at the load balancer or framework level.

Future skill `security-cors-csp` (Phase 7) covers browser-side transport headers in depth.

**Related anti-patterns:** AP-3 (disabled TLS verification) (see `anti-patterns.md`)

---

## Rule 5.6: Output Encoding Matches Context

**Statement:** Output to a parsed/interpreted context (HTML, JSON, SQL, shell, LDAP, XML, log lines, etc.) is encoded for that specific context at the boundary where the output is emitted. No string concatenation of untrusted data into query strings, markup, command strings, or other parsed contexts. Use parameterized queries for SQL, context-aware templating for HTML, `execFile`-style APIs (not `exec` + shell string) for processes.

**Citation:** `OWASP-TOP10 A05:2025 (Injection)` (same category as Rule 5.1; injection happens at output, the rule pair guards both ends) + `OWASP-ASVS 5.0 V1 (Encoding and Sanitization)`.

**Plain-language impact:** Most injection vulnerabilities — SQL injection, XSS, command injection, LDAP injection — are caused by treating data as code at the output context. The fix is uniform: encode the data so it cannot be interpreted as syntax at the consuming context. Parameterized queries pass data and SQL as separate channels; HTML templating escapes `<`, `>`, `&`, `"`, `'`; argument arrays pass arguments without shell interpretation. The cost is small; the absence opens every injection class.

**Extended discussion:** This rule pairs with Rule 5.1 (validate at input). Validation rejects bad input at the boundary where it enters; encoding ensures even "good" input (which may contain syntactically meaningful characters) cannot escape its data role at the output context.

*Context-by-context discipline:*

- **SQL:** parameterized queries always (`?` placeholders in Python DB-API, `$1` placeholders in Node `pg`, ORM-native parameter binding). NEVER string concatenation, f-string interpolation, or `.format()` of user input into queries. The ORM is not magic; verify the underlying driver is parameterizing.
- **HTML:** context-aware templating that escapes for the specific position (attribute, text, URL, script, style). Modern frameworks (React via JSX, Vue, Svelte) handle this by default for text content; explicit care needed for `dangerouslySetInnerHTML`, `v-html`, or building HTML strings manually. Server-side templating uses auto-escaping engines (Jinja2 with autoescape on, Django templates, Mustache strict).
- **Shell / process spawning:** argument arrays via `execFile`-style APIs, NOT shell-string interpolation. Node: `child_process.execFile(command, [arg1, arg2])` not `child_process.exec(command + " " + arg1 + " " + arg2)`. Python: `subprocess.run([command, arg1, arg2])` not `subprocess.run(f"{command} {arg1} {arg2}", shell=True)`. Go: `exec.Command(name, args...)` without shell.
- **LDAP:** parameterized search filters via library escape functions. NEVER concatenating user input into filter strings.
- **JSON / XML / YAML output:** use the library's serializer (`json.dumps`, `JSON.stringify`, `yaml.safe_dump`) — NEVER hand-build the serialized string by concatenation.
- **Log lines:** structured logging with separate fields, not f-string interpolation. Prevents log injection (where user input contains newlines that fake log entries). Also makes the log machine-parseable.
- **Filenames / URLs:** path-join APIs that prevent directory traversal; URL builders that prevent open-redirect.

*Failure mode pattern:* AI-generated code often gets the FIRST query right (parameterized) but the next query, written quickly, slips into string concatenation. Surface in Stage 5 Phase 2 review by grepping the changed code for query construction patterns.

**Related anti-patterns:** AP-6 (SQL injection), AP-8 (shell command from user input) (see `anti-patterns.md`)

---

## Rule 5.7: Log Security Events; Never Log Secrets

**Statement:** Authentication and authorization failures, security-relevant state changes (privilege grants, password resets, role changes, MFA setup/removal), and errors at trust boundaries are logged with sufficient context (timestamp, identifier of acting principal, target resource, outcome) for after-the-fact investigation. Passwords (cleartext or hashed), session tokens, API keys, encryption keys, full PII payloads, and credit card numbers are NEVER logged.

**Citation:** `OWASP-TOP10 A09:2025 (Security Logging and Alerting Failures)` + `OWASP-ASVS 5.0 V16 (Security Logging and Error Handling)`. Item from the hard-refusal list per `CLAUDE.md` §5: "Logging full credentials, tokens, or sensitive personal data."

**Plain-language impact:** Without security logs, an incident response team has no trail to investigate a breach. Authentication failures, suspicious access patterns, and authorization bypasses go unnoticed until the consequences surface elsewhere. WITH security logs but ALSO logged secrets, the centralized logging system becomes the highest-value target on the network — one logging-system breach exposes every credential that ever appeared in a log line.

**Extended discussion:** Security logging is one of those disciplines whose value is invisible until it's needed, and at that point its absence is catastrophic. Treat it as on par with backups: cheap to set up, irreplaceable to recover.

*What to log:*
- Authentication outcomes: successful logins, failed logins (especially patterns suggesting brute force), MFA challenges and responses, password resets, account lockouts.
- Authorization outcomes: denied access attempts (especially when they cluster around sensitive resources), privilege elevation, role changes, permission grants and revocations.
- Security-relevant state changes: account creation, account deletion, API key generation and rotation, encryption key rotation, MFA setup/removal.
- Errors at trust boundaries: validation failures with structured error context, parser failures, third-party API errors.
- Administrative actions: any operation performed via admin tooling — who, what, when, on whose account.

*What NEVER to log:*
- Cleartext passwords (or even hashed — hashes can be cracked offline if leaked).
- Session tokens, API keys, bearer tokens (even partial — the first N characters are often enough for brute force or pattern-matching).
- Encryption keys, signing keys.
- Full PII payloads (an entire user object dumped to log on save).
- Credit card numbers, CVVs, bank account numbers (PCI-DSS violation; subject to compliance penalty in addition to incident risk).
- Health records (HIPAA violation).
- Any field marked sensitive in the data classification schema (future skill `security-data-classification` in Phase 7).

*Practical patterns:*
- Use structured logging with explicit fields. Pass the request body to a sanitizer before logging: drop `password`, `token`, `api_key`, `credit_card` keys; truncate or redact long PII fields; allow-list the fields that are safe to log.
- Use IDs, not full objects: log `user_id=12345` rather than the full user record.
- Distinguish security event channels from application logs at the logging-system level so security events have appropriate retention (typically longer than app logs) and appropriate alerting (anomaly detection, threshold-based alerts on auth failures).

Depth on logging architecture in future skill `security-logging` (Phase 7); depth on detection patterns in `security-detection-monitoring` (Phase 7).

**Related anti-patterns:** AP-5 (logging sensitive data) (see `anti-patterns.md`)

---
