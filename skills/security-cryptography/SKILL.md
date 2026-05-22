---
# ─── Anthropic-native runtime fields (Claude Code honors these) ───
name: security-cryptography
description: |
  Cryptographic discipline — approved algorithms (AES-GCM, Argon2id,
  Ed25519); CSPRNG for security-random values; IV/nonce/salt
  uniqueness; key lifecycle (generation, separation, rotation,
  destruction); TLS 1.2+, 1.3 preferred, no plaintext fallback. Use
  when implementing encryption, hashing, signing, key derivation,
  TLS configuration, or any cryptographic primitive. Extends
  SECURITY-CORE Rules 5.3 + 5.5. Aligns with OWASP ASVS 5.0 V11 + V12
  and OWASP Top 10:2025 A04.
paths:
  - "**/*.ts"
  - "**/*.tsx"
  - "**/*.js"
  - "**/*.jsx"
  - "**/*.py"
  - "**/*.go"
  - "**/*.rs"
  - "**/*.rb"
  - "**/*.java"
  - "**/*.kt"
  - "**/*.swift"
  - "**/*.php"
  - "**/*.cs"
  - "**/*.scala"

# ─── TGF-extension metadata (Phase 11 meta-skills read these; Claude Code ignores) ───
applies-when:
  paths-include:
    - "**/*.{ts,tsx,js,jsx,py,go,rs,rb,java,kt,swift,php,cs,scala}"
  operations-include:
    - encryption / decryption (symmetric or asymmetric)
    - hashing for security purposes (signing, HMAC, KDF, integrity)
    - password hashing / verification
    - random value generation for security purposes (tokens, IDs, nonces, salts)
    - digital signature creation / verification
    - key generation, derivation, wrapping, or rotation
    - TLS server / client configuration
    - certificate validation
    - mTLS / certificate pinning configuration
  data-flows-include:
    - sensitive data flowing into or out of cryptographic operations
    - keys flowing between secure storage and operating code
    - TLS-protected data in transit
disqualifying-when:
  - documentation-only changes
  - test fixture additions without production code changes
  - dependency version bumps without code changes
  - pure formatting edits
sources:
  - OWASP ASVS 5.0.0 V11 (Cryptography) (verified 2026-05-22)
  - OWASP ASVS 5.0.0 V12 (Secure Communication) (verified 2026-05-22)
  - OWASP Top 10:2025 A04 (Cryptographic Failures) (verified Phase 4, 2026-05-20)
  - OWASP Cheat Sheet — Cryptographic Storage (verified 2026-05-22)
  - OWASP Cheat Sheet — Password Storage (verified 2026-05-22)
  - NIST SP 800-57 Part 1 Rev 5 (Recommendation for Key Management — General; 2020)
  - NIST SP 800-175B Rev 1 (Guideline for Using Cryptographic Standards in the Federal Government — Cryptographic Mechanisms; 2020)
  - NIST FIPS 197 (Advanced Encryption Standard; 2001)
  - NIST FIPS 180-4 (Secure Hash Standard — SHA-1, SHA-2; 2015)
  - NIST FIPS 202 (SHA-3 Standard; 2015)
  - RFC 8446 (The Transport Layer Security (TLS) Protocol Version 1.3; 2018)
  - RFC 8996 (Deprecating TLS 1.0 and TLS 1.1; 2021)
  - CWE-327 (Use of a Broken or Risky Cryptographic Algorithm)
  - CWE-326 (Inadequate Encryption Strength)
  - CWE-330 (Use of Insufficiently Random Values)
  - CWE-916 (Use of Password Hash With Insufficient Computational Effort)
  - CWE-323 (Reusing a Nonce, Key Pair in Encryption)
last-generated: 2026-05-22
refresh-recommended: 2027-05-22
self-evolution:
  anti-patterns-observed: []
  triggers-refined: []
  ai-failures-documented: []
---

# SECURITY-CRYPTOGRAPHY

> **Skill body ≤300 lines** (per `DEC-2026-05-19-007`). Principles, rule summaries, and navigation live here. Full content in reference files loaded on demand:
> - `rules.md` — full rules with rule-level citations
> - `anti-patterns.md` — full anti-pattern + canonical pattern pairs with code examples

<!-- SECTION: overview -->
## §1 Overview

SECURITY-CRYPTOGRAPHY governs the discipline of cryptographic operations: which algorithms, at which parameters, with which key lifecycle, over which transport. It is a **Phase 6 foundation security skill** that extends both SECURITY-CORE Rule 5.3 (*Use Established Cryptography; Never Roll Your Own*) and Rule 5.5 (*TLS Verification Always Enabled, Strong Defaults*) with operational depth — the rules below specify *which* approved algorithms for *which* purpose, *which* parameter ranges for *which* threat model, and *which* lifecycle stage requires which discipline.

Per Phase 6 Checkpoint 1 Decision B, this skill **extends** SECURITY-CORE without restating. SECURITY-CORE Rules 5.3 + 5.5 remain canonical for the universal principles (no custom crypto, no broken algorithms, TLS verification always enabled). This skill adds the depth — *what* AES-GCM IV-uniqueness means in practice, *what* Argon2id parameters meet 2025+ guidance, *what* TLS 1.3 cipher suites look like, *what AI gets wrong* about each. Hard-refusal patterns covered by SECURITY-CORE APs (custom crypto = AP-2; broken algorithms = AP-4; disabled TLS = AP-3) are referenced by ID rather than restated.

Cryptography is foundation infrastructure for later Phase 6 skills: `security-secrets-management` (commit 5/12) handles operational key storage / rotation; `security-iam-authentication` (commit 6/12) implements password hashing in the auth flow context; `security-iam-sessions` (commit 7/12) handles JWT signing / verification. This skill owns the cryptographic primitives those skills compose.

This skill maps to **OWASP Top 10:2025 A04 (Cryptographic Failures)** — promoted from "Sensitive Data Exposure" in earlier years to recognize that the underlying class is broken/misused crypto, not just exposure.
<!-- /SECTION: overview -->

<!-- SECTION: sources -->
## §2 Authoritative Sources

| Source ID | Reference | Version | Date Verified |
|-----------|-----------|---------|---------------|
| OWASP-ASVS-V11 | [OWASP ASVS 5.0 V11 — Cryptography](https://github.com/OWASP/ASVS/blob/master/5.0/en/0x20-V11-Cryptography.md) | 5.0.0 | 2026-05-22 |
| OWASP-ASVS-V12 | [OWASP ASVS 5.0 V12 — Secure Communication](https://github.com/OWASP/ASVS/blob/master/5.0/en/0x21-V12-Secure-Communication.md) | 5.0.0 | 2026-05-22 |
| OWASP-TOP10-A04 | [OWASP Top 10:2025 A04 (Cryptographic Failures)](https://owasp.org/Top10/2025/) | 2025 | 2026-05-20 (Phase 4) |
| OWASP-CHEAT-CS | [OWASP Cheat Sheet — Cryptographic Storage](https://cheatsheetseries.owasp.org/cheatsheets/Cryptographic_Storage_Cheat_Sheet.html) | Current (2026) | 2026-05-22 |
| OWASP-CHEAT-PS | [OWASP Cheat Sheet — Password Storage](https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html) | Current (2026) | 2026-05-22 |
| NIST-SP-800-57 | [NIST SP 800-57 Part 1 Rev 5 — Recommendation for Key Management: General](https://csrc.nist.gov/pubs/sp/800/57/pt1/r5/final) | Rev 5 (2020) | 2026-05-22 |
| NIST-SP-800-175B | [NIST SP 800-175B Rev 1 — Guideline for Using Cryptographic Standards: Cryptographic Mechanisms](https://csrc.nist.gov/pubs/sp/800/175/b/r1/final) | Rev 1 (2020) | 2026-05-22 |
| FIPS-197 | [NIST FIPS 197 — Advanced Encryption Standard (AES)](https://csrc.nist.gov/pubs/fips/197/final) | 2001 | 2026-05-22 |
| FIPS-180-4 | [NIST FIPS 180-4 — Secure Hash Standard (SHA-1, SHA-2)](https://csrc.nist.gov/pubs/fips/180-4/upd1/final) | 2015 | 2026-05-22 |
| FIPS-202 | [NIST FIPS 202 — SHA-3 Standard](https://csrc.nist.gov/pubs/fips/202/final) | 2015 | 2026-05-22 |
| RFC-8446 | [RFC 8446 — TLS 1.3](https://datatracker.ietf.org/doc/html/rfc8446) | 2018 | 2026-05-22 |
| RFC-8996 | [RFC 8996 — Deprecating TLS 1.0 and TLS 1.1](https://datatracker.ietf.org/doc/html/rfc8996) | 2021 | 2026-05-22 |
| CWE-327 | [CWE-327 Use of a Broken or Risky Cryptographic Algorithm](https://cwe.mitre.org/data/definitions/327.html) | Current | 2026-05-22 |
| CWE-326 | [CWE-326 Inadequate Encryption Strength](https://cwe.mitre.org/data/definitions/326.html) | Current | 2026-05-22 |
| CWE-330 | [CWE-330 Use of Insufficiently Random Values](https://cwe.mitre.org/data/definitions/330.html) | Current | 2026-05-22 |
| CWE-916 | [CWE-916 Use of Password Hash With Insufficient Computational Effort](https://cwe.mitre.org/data/definitions/916.html) | Current | 2026-05-22 |
| CWE-323 | [CWE-323 Reusing a Nonce, Key Pair in Encryption](https://cwe.mitre.org/data/definitions/323.html) | Current | 2026-05-22 |

Citation granularity per Phase 6 Checkpoint 1 Decision A (hybrid): chapters at chapter level in §2; sub-rule level (V11.3.2, V11.5.1, V12.1.1, etc.) in `rules.md`. NIST SP 800-series at section level. RFCs at section level. FIPS at standard level. CWE entries by ID + title.

NIST SP 800-57 is the canonical key-management reference. OWASP Cheat Sheets are HTML-fetchable per the Phase 6 commit 1/12 plan-adjustment — both Cheat Sheets listed above (Cryptographic Storage, Password Storage) live-verified 2026-05-22. The Key Management and TLS cheat sheets were considered but are not cited at rule level in this skill; Rule 5.6 uses `OWASP-CHEAT-CS §Key Management` (the Key Management section of the Cryptographic Storage cheat sheet, which IS verified) and Rule 5.7 uses ASVS V12 + RFC 8446 + RFC 8996 directly.
<!-- /SECTION: sources -->

<!-- SECTION: discovery -->
## §3 Discovery Commands

Copy-pasteable commands to capture cryptographic state before applying rules.

```bash
# Find non-CSPRNG random calls in security contexts
grep -rnE "Math\.random\(\)|random\.random\(\)|new Random\(\)|math/rand|rand\(\)" --include="*.ts" --include="*.js" --include="*.py" --include="*.go" --include="*.java" 2>/dev/null | head -20

# Find ECB-mode usage (always wrong choice for confidentiality)
grep -rnE "(Cipher|cipher).*ECB|MODE_ECB|aes-128-ecb|aes-256-ecb|AES/ECB" --include="*.py" --include="*.java" --include="*.ts" --include="*.js" 2>/dev/null | head -20

# Find broken hash algorithms in security-purpose contexts (cross-check with SECURITY-CORE AP-4)
grep -rnE "(md5|sha1|MD5|SHA-?1)\s*\(" --include="*.ts" --include="*.js" --include="*.py" --include="*.go" --include="*.java" 2>/dev/null | head -20

# Find password hashing patterns (verify Argon2id / bcrypt / scrypt / PBKDF2 with sufficient params)
grep -rnE "(bcrypt|scrypt|argon2|pbkdf2|hash_password)" --include="*.ts" --include="*.js" --include="*.py" --include="*.go" --include="*.java" 2>/dev/null | head -20

# Find hardcoded crypto keys / IVs (cross-check with SECURITY-CORE AP-1)
grep -rnE "(SECRET|KEY|IV|NONCE)\s*=\s*['\"][a-zA-Z0-9+/=]{16,}['\"]" --include="*.ts" --include="*.js" --include="*.py" --include="*.go" --include="*.java" 2>/dev/null | head -20

# Find disabled TLS verification (cross-check with SECURITY-CORE AP-3)
grep -rnE "verify\s*=\s*False|rejectUnauthorized\s*:\s*false|InsecureSkipVerify\s*:\s*true|TrustAllCerts" --include="*.py" --include="*.ts" --include="*.js" --include="*.go" --include="*.java" 2>/dev/null | head -20

# Find TLS configuration calls (verify TLS 1.2+ and current cipher suites)
grep -rnE "TLSv1|SSLv3|tls_version|minVersion|min_protocol|setProtocols" --include="*.ts" --include="*.js" --include="*.py" --include="*.go" --include="*.java" 2>/dev/null | head -20
```
<!-- /SECTION: discovery -->

<!-- SECTION: principles -->
## §4 Universal Principles

Seven principles grounding the cryptography discipline.

- **Use library cryptography from approved lists; never custom.** Cryptographic libraries are written by people who specialize in the discipline and audited by people who specialize in attacking it. Custom crypto has an essentially 100% track record of failure (per SECURITY-CORE Rule 5.3). The discipline is choosing the *right primitive* from the library — AES-GCM for symmetric authenticated encryption, Argon2id for passwords, Ed25519 for signatures — not implementing the primitive yourself.

- **Algorithm choice is purpose-specific; one size does not fit all.** The right algorithm depends on what you're protecting: integrity (HMAC-SHA-256), confidentiality with authentication (AES-GCM, ChaCha20-Poly1305), passwords (Argon2id; never general hash), signatures (Ed25519 / RSA-PSS), key derivation from a password (Argon2id, PBKDF2 with appropriate parameters), key derivation from another key (HKDF). Using a primitive for the wrong purpose is the most common pitfall — SHA-256 for passwords, AES for signing, RSA-OAEP-encrypt for authentication.

- **128-bit security strength minimum; future-proof for migration.** Every primitive provides at least 128 bits of security against the relevant attack model (AES-128, RSA-3072, ECC P-256, SHA-256 for collision resistance). Cryptographic agility (per V11.2.2) — the application is structured so that swapping algorithms is configuration-level, not code-rewrite-level. Post-quantum migration is on the roadmap for long-lived secrets (V11.1.4).

- **Randomness used for security purposes comes from CSPRNG.** Tokens, session IDs, nonces, IVs, salts, password-reset tokens, OAuth state, JWT IDs, key material — all from the language's cryptographically secure PRNG. `Math.random()`, `random.random()`, `rand()`, and `Random` (Java) are forbidden for security purposes; they are predictable across many calls and provide zero security against an adversary modeling the PRNG state.

- **IVs, nonces, and salts are unique per use.** Salt: unique per password (defeats rainbow tables). Nonce / IV: unique per (key, message) pair (defeats replay; for AES-GCM specifically, IV reuse is catastrophic — a single repeated IV under the same key reveals the GCM authentication key, allowing forgery of arbitrary messages). The discipline is generating fresh randomness per use, never hardcoding, never reusing across sessions.

- **Keys have lifecycles — generation, separation, rotation, destruction.** Keys are generated via approved methods (CSPRNG for symmetric; library-native keygen for asymmetric); separated by purpose (encrypting key ≠ signing key ≠ MAC key ≠ key-encrypting-key); rotated on schedule (cryptoperiod per NIST SP 800-57) and on compromise; destroyed at end of life with no recoverable copies. The KEK/DEK pattern (key-encryption-keys protect data-encryption-keys) lets DEK rotation happen without re-encrypting all data.

- **TLS configuration: 1.2 minimum, 1.3 preferred, no plaintext fallback.** Inbound HTTPS enforces TLS 1.2 or newer (RFC 8996 explicitly deprecates 1.0/1.1). Cipher suites prioritize forward secrecy (ECDHE families with AEAD). Certificate validation always enabled (per SECURITY-CORE Rule 5.5). Internal service communication uses the same discipline — "internal" traffic is not exempt; per V12.3.1 internal protocols are TLS-protected without fallback. mTLS for sensitive service-to-service paths per V12.3.5.
<!-- /SECTION: principles -->

<!-- SECTION: rules -->
## §5 Rule Summaries

Seven rules. Each summary: title + 1-line statement + source identifier. This skill extends SECURITY-CORE Rules 5.3 + 5.5 — their canonical statements stand; the rules below add the operational depth.

<!-- RULE: 5.1 -->
- **Rule 5.1: Approved Algorithms by Purpose — AES-GCM, Argon2id, Ed25519, SHA-256/SHA-3** — Symmetric authenticated encryption: AES-GCM / AES-CCM / ChaCha20-Poly1305. Password hashing: Argon2id / scrypt / bcrypt (NOT general hashes). Signatures: Ed25519 / RSA-PSS / ECDSA. Hashing: SHA-256 or SHA-3. Forbidden: MD5, SHA-1, DES, 3DES, RC4, ECB, PKCS#1 v1.5. `OWASP-ASVS V11.2.1, V11.3.1, V11.3.2, V11.4.1, V11.6.1` + extends `SECURITY-CORE Rule 5.3` + `CWE-327` → [`rules.md#rule-51-approved-algorithms-by-purpose`](rules.md)
<!-- /RULE: 5.1 -->
<!-- RULE: 5.2 -->
- **Rule 5.2: 128-bit Minimum Security Strength; Cryptographic Agility for Migration** — Every primitive provides ≥128-bit security (AES-128, RSA-3072, ECC P-256, SHA-256 collision-resistance). Algorithm choice configurable for future migration. Post-quantum migration plans for long-lived secrets. `OWASP-ASVS V11.2.2, V11.2.3, V11.1.4` + `CWE-326` → [`rules.md#rule-52-minimum-strength-and-agility`](rules.md)
<!-- /RULE: 5.2 -->
<!-- RULE: 5.3 -->
- **Rule 5.3: Authenticated Encryption Only; IV/Nonce Uniqueness Mandatory** — AEAD modes (AES-GCM, ChaCha20-Poly1305) preferred. When encrypt-then-MAC is the only option, MAC the ciphertext with HMAC-SHA-256. IV/nonce unique per (key, message); AES-GCM IV reuse is catastrophic. `OWASP-ASVS V11.3.2, V11.3.3, V11.3.4, V11.3.5` + `CWE-323` → [`rules.md#rule-53-authenticated-encryption-iv-uniqueness`](rules.md)
<!-- /RULE: 5.3 -->
<!-- RULE: 5.4 -->
- **Rule 5.4: CSPRNG for All Security-Relevant Random Values** — Tokens, session IDs, nonces, IVs, salts come from language CSPRNG (`crypto.randomBytes` / `secrets.token_bytes` / `crypto/rand.Reader` / `SecureRandom`). Minimum 128 bits entropy; UUIDs do not satisfy this. `OWASP-ASVS V11.5.1` + `CWE-330` + `OWASP-CHEAT-CS` → [`rules.md#rule-54-csprng-for-security-random`](rules.md)
<!-- /RULE: 5.4 -->
<!-- RULE: 5.5 -->
- **Rule 5.5: Password Hashing Uses Memory-Hard KDFs with Tuned Parameters** — Argon2id (preferred), scrypt, bcrypt with current OWASP-recommended parameters. PBKDF2 acceptable for FIPS contexts (SHA-256, 600k+ iterations). Salt unique per password. Pepper is defense-in-depth. `OWASP-ASVS V11.4.2, V11.4.4` + `OWASP-CHEAT-PS` + `CWE-916` → [`rules.md#rule-55-password-hashing-kdf`](rules.md)
<!-- /RULE: 5.5 -->
<!-- RULE: 5.6 -->
- **Rule 5.6: Key Lifecycle — Generation, Separation, Rotation, Destruction** — Generate via approved methods; separate keys by purpose (encrypt ≠ sign ≠ MAC ≠ KEK); rotate per NIST SP 800-57 cryptoperiods and on compromise; destroy unrecoverably at end of life. KEK/DEK pattern for data-at-rest. `OWASP-ASVS V11.1.1, V11.1.2` + `NIST-SP-800-57 §5.3 (cryptoperiods), §6 (lifecycle)` + `OWASP-CHEAT-CS (Key Management)` → [`rules.md#rule-56-key-lifecycle`](rules.md)
<!-- /RULE: 5.6 -->
<!-- RULE: 5.7 -->
- **Rule 5.7: TLS 1.2 Minimum; 1.3 Preferred; Strong Cipher Suites; No Plaintext Fallback** — Inbound: TLS 1.2+ (1.3 preferred), forward-secrecy cipher suites, HSTS. Outbound: certificate validation always enabled. Internal: TLS without fallback per V12.3.1; mTLS for sensitive paths. Extends SECURITY-CORE Rule 5.5. `OWASP-ASVS V12.1.1, V12.1.2, V12.2.1, V12.3.1, V12.3.2` + `RFC-8446` + `RFC-8996` + extends `SECURITY-CORE Rule 5.5` → [`rules.md#rule-57-tls-configuration`](rules.md)
<!-- /RULE: 5.7 -->

See `rules.md` for full rule text, citations, plain-language impact, and extended discussion.
<!-- /SECTION: rules -->

<!-- SECTION: anti-patterns -->
## §6 Anti-Pattern Summaries

Nine anti-pattern pairs covering the most common cryptographic failures. Per Phase 6 Checkpoint 1 Decision B, hard-refusal patterns (custom crypto = SECURITY-CORE AP-2; broken algorithms = SECURITY-CORE AP-4; disabled TLS = SECURITY-CORE AP-3; hardcoded credentials = SECURITY-CORE AP-1) are referenced by ID, not restated. The APs below cover operational depth.

<!-- ANTI-PATTERN: AP-1 -->
- **AP-1: AES-ECB Mode for Confidentiality** — `cipher.encrypt(plaintext)` with default-or-explicit ECB mode. ECB encrypts equal plaintext blocks to equal ciphertext blocks — patterns are visible (the famous "ECB penguin"). Violates Rule 5.1. → [`anti-patterns.md#ap-1-aes-ecb-mode`](anti-patterns.md)
<!-- /ANTI-PATTERN: AP-1 -->
<!-- ANTI-PATTERN: AP-2 -->
- **AP-2: IV/Nonce Reuse with AES-GCM** — Hardcoded IV, sequential counter restarting at zero, or randomly-generated IV with insufficient entropy. AES-GCM IV reuse under the same key is catastrophic — recovers the authentication key. Violates Rule 5.3; `CWE-323`. → [`anti-patterns.md#ap-2-iv-nonce-reuse`](anti-patterns.md)
<!-- /ANTI-PATTERN: AP-2 -->
<!-- ANTI-PATTERN: AP-3 -->
- **AP-3: Non-CSPRNG (`Math.random`, `rand`, `Random`) for Security Values** — Predictable randomness used for tokens, session IDs, nonces. Adversary models PRNG state from observed values. Violates Rule 5.4; `CWE-330`. → [`anti-patterns.md#ap-3-non-csprng-for-security`](anti-patterns.md)
<!-- /ANTI-PATTERN: AP-3 -->
<!-- ANTI-PATTERN: AP-4 -->
- **AP-4: Password Hashed with General Hash (SHA-256) — No Key Stretching** — `sha256(password + salt)` is fast; GPU farms compute billions per second. Argon2id / bcrypt / scrypt deliberately slow down per-attempt cost. Violates Rule 5.5; `CWE-916`. Extends `SECURITY-CORE AP-4` (which covers MD5/SHA-1 broken-algo case). → [`anti-patterns.md#ap-4-general-hash-for-password`](anti-patterns.md)
<!-- /ANTI-PATTERN: AP-4 -->
<!-- ANTI-PATTERN: AP-5 -->
- **AP-5: PBKDF2/bcrypt/scrypt with Insufficient Parameters** — Correct algorithm chosen but parameter cost set too low (PBKDF2 with 10k iterations; bcrypt cost 8). Defeats key-stretching purpose. Violates Rule 5.5. → [`anti-patterns.md#ap-5-insufficient-kdf-params`](anti-patterns.md)
<!-- /ANTI-PATTERN: AP-5 -->
<!-- ANTI-PATTERN: AP-6 -->
- **AP-6: PKCS#1 v1.5 Padding for RSA Encryption** — Known padding-oracle vulnerable (Bleichenbacher 1998 + ongoing variants). Use RSA-OAEP for encryption; RSA-PSS for signatures. Violates Rule 5.1; `OWASP-ASVS V11.3.1` (prohibited padding). → [`anti-patterns.md#ap-6-pkcs1-v15-padding`](anti-patterns.md)
<!-- /ANTI-PATTERN: AP-6 -->
<!-- ANTI-PATTERN: AP-7 -->
- **AP-7: Same Key Reused Across Cryptographic Purposes** — One key used for both encryption and HMAC signing; same RSA key for encryption and signature. Key-purpose separation violated; attacks on one purpose compromise the other. Violates Rule 5.6. → [`anti-patterns.md#ap-7-key-purpose-reuse`](anti-patterns.md)
<!-- /ANTI-PATTERN: AP-7 -->
<!-- ANTI-PATTERN: AP-8 -->
- **AP-8: TLS 1.0 / 1.1 Still Enabled** — Server configuration allows pre-1.2 TLS. Both formally deprecated (RFC 8996, 2021). Negotiation falls back to weak protocol. Violates Rule 5.7; `OWASP-ASVS V12.1.1`. → [`anti-patterns.md#ap-8-deprecated-tls-versions`](anti-patterns.md)
<!-- /ANTI-PATTERN: AP-8 -->
<!-- ANTI-PATTERN: AP-9 -->
- **AP-9: Plaintext Fallback / "Internal" Traffic Unencrypted** — HTTP allowed alongside HTTPS; internal service-to-service mesh assumed safe and uses plaintext. Violates Rule 5.7 + `OWASP-ASVS V12.2.1` (no fallback) + V12.3.1 (internal TLS without fallback). → [`anti-patterns.md#ap-9-plaintext-fallback`](anti-patterns.md)
<!-- /ANTI-PATTERN: AP-9 -->

Per `DEC-2026-05-17-003` Clause 1: every anti-pattern is paired with a canonical pattern in `anti-patterns.md`.
<!-- /SECTION: anti-patterns -->

<!-- SECTION: ai-concerns -->
## §7 AI-Specific Concerns

Cryptographic failure modes specific to AI-generated code and AI-integrated systems.

- **Defaulting to MD5/SHA-256 for passwords.** AI training data over-represents 2000s-era code where `sha256(password + salt)` was the prevailing pattern. AI generates this when asked for "secure password storage." Defense: Rule 5.5 + AP-4 — Argon2id is the current default; bcrypt / scrypt acceptable. Grep at Stage 5 Phase 2 for any `sha256.*password`, `md5.*password`, `hashlib.*password` patterns.

- **`Math.random()` for tokens because "the prompt asked for random."** AI sees "generate a random token" and reaches for the most-common random API. The most-common API is not the cryptographically-secure one. Defense: Rule 5.4 + AP-3 — `crypto.randomBytes()` / `secrets.token_urlsafe()` is the language-correct answer.

- **Hardcoded IV for AES-GCM "to make encryption deterministic."** AI generates encryption code with a hardcoded IV (often all-zeros, sometimes a single-line constant) when the prompt asks for "encrypt this consistently" or the developer wants reproducible output for testing. The result is the worst possible failure mode for AES-GCM. Defense: Rule 5.3 + AP-2 — IV is per-message, generated via CSPRNG, prepended to ciphertext.

- **`verify=False` / `rejectUnauthorized: false` to "make development easier."** AI generates Python `requests.get(url, verify=False)` or Node `https.Agent({ rejectUnauthorized: false })` when the dev environment has self-signed certs. The pattern silently ships to production. Defense: Rule 5.7 + cross-ref SECURITY-CORE AP-3 — use development CAs / local trust store; never disable verification.

- **`bcrypt` with default cost or low explicit cost.** AI generates `bcrypt.hashSync(password, 8)` or omits the cost factor (some library defaults are 10, others are lower). 8-10 is undertuned for modern hardware. Defense: Rule 5.5 + AP-5 — verify cost is 12+ for bcrypt, current OWASP parameters for Argon2id / scrypt.

- **AES-CBC without authentication ("the data is short, MAC is overkill").** AI generates AES-CBC for encryption and stops there — no HMAC, no AEAD. Unauthenticated ciphertext is malleable; padding-oracle attacks are well-documented. Defense: Rule 5.3 + AP-1 (ECB is worse, CBC-without-MAC is still wrong) — AES-GCM is the default.

Relevant external taxonomies: `OWASP-TOP10 A04:2025` (Cryptographic Failures — promoted from Sensitive Data Exposure); `OWASP-LLM LLM06:2025` (Excessive Agency — when an AI agent generates and uses cryptography autonomously); `CWE-327`, `CWE-326`, `CWE-330`, `CWE-916`, `CWE-323`.
<!-- /SECTION: ai-concerns -->

<!-- SECTION: workflow -->
## §8 Workflow Integration

How SECURITY-CRYPTOGRAPHY participates in the six-stage workflow and four-pass review (per `docs/WORKFLOW.md`).

- **Stage 1 (Research):** Run the §3 discovery commands when the change adds encryption, hashing, signing, key derivation, random generation, or TLS configuration. Map existing crypto patterns before adding new ones.
- **Stage 3 (Plan with Governance):** Contribute Rules 5.1–5.7 when the change introduces a new cryptographic primitive, generates security-relevant random values, manages keys, or configures TLS.
- **Stage 4 (Implement):** Apply rules during writing — approved algorithm by purpose; CSPRNG; per-use IV/salt; tuned KDF parameters; key separation; TLS 1.2+ with no fallback.
- **Stage 5 Phase 2 (Security Audit):** Primary skill — all rules in scope. AP-1 (ECB), AP-2 (IV reuse), AP-3 (non-CSPRNG), AP-4 (general hash for password), AP-7 (key purpose reuse) are typically Critical severity. Cross-check against SECURITY-CORE APs (AP-1 hardcoded credentials, AP-2 custom crypto, AP-3 disabled TLS, AP-4 broken algorithms) for hard-refusal violations.
- **Stage 5 Phase 3 (Red Team):** Probe cryptographic boundaries adversarially — IV reuse scenarios, key-purpose-confusion attacks, downgrade attacks on TLS, parameter-tuning attacks on KDFs. Consult `security-secrets-management` (Phase 6 commit 5/12) for the secret-storage side; `security-iam-authentication` (commit 6/12) for password-storage application context.
- **Stage 5 Phase 4 (Holistic Review):** Verify the cryptographic discipline is coherent with surrounding patterns — no algorithm-choice regressions, no IV-uniqueness drift across encryption call sites, no key-separation drift across modules, TLS configuration consistent across services.
- **Stage 6 (Commit):** Critical findings (AP-2 IV reuse, AP-4 general hash for password, AP-7 key purpose reuse, hard-refusal violations) get fixed before commit. Medium findings get fixed, waived per CONTINUITY Rule 5.3, or escalated to `VENDOR-LOG.md` (e.g., third-party SDK using deprecated crypto requiring vendor follow-up).
<!-- /SECTION: workflow -->

<!-- SECTION: subagent-context -->
## §9 Subagent Context

**Preloaded by:** None by default. Phase 6 foundation security skills are not preloaded into the existing four review subagents (per Phase 4 agent definitions). `security-auditor` and `red-team` consult this skill on demand based on Stage 3's plan when the change touches cryptographic operations or TLS configuration. Phase 11 (Meta-Skills) may revise subagent skill mappings.

**Critical rules for review use (when consulted but not preloaded):**

- Rule 5.1 (Approved Algorithms by Purpose)
- Rule 5.3 (Authenticated Encryption Only; IV/Nonce Uniqueness)
- Rule 5.4 (CSPRNG for Security-Random)
- Rule 5.5 (Password Hashing — Memory-Hard KDFs)
- Rule 5.7 (TLS Configuration)

**Top AI-specific concerns:**

- Defaulting to `sha256(password + salt)` for passwords (training-data anachronism)
- `Math.random()` for tokens (most-common API ≠ secure API)
- Hardcoded IV for "deterministic" encryption (catastrophic for AES-GCM)
- `verify=False` to bypass dev-env certificate issues (ships to production)

**Cross-skill web:**

- Extends SECURITY-CORE Rule 5.3 (use established cryptography) — this skill adds *which algorithms* for *which purpose*
- Extends SECURITY-CORE Rule 5.5 (TLS verification always enabled) — this skill adds version, cipher suite, internal-traffic depth
- Foundation for `security-secrets-management` (Phase 6 commit 5/12) — secrets-management handles operational key storage; this skill handles how keys work cryptographically
- Foundation for `security-iam-authentication` (Phase 6 commit 6/12) — auth uses Rule 5.5 password hashing in the login/signup flow context
- Foundation for `security-iam-sessions` (Phase 6 commit 7/12) — sessions use Ed25519 / RSA-PSS for JWT signing per Rule 5.1
- Cross-refs `security-output-encoding` (Phase 6 commit 2/12) Rule 5.2 — SQL parameterization is unrelated, but LDAP escape uses RFC 4515 encoding which is encoding-not-crypto; clean boundary
- Forwards to `security-data-encryption` (Phase 7) for at-rest-vs-in-transit discipline (this skill owns the primitives; data-encryption owns the application of them to data-classification)
- Forwards to `security-data-classification` (Phase 7) for which-data-needs-which-protection
- DISAGREEMENT Rule 5.2 routes severity — AP-2 (IV reuse) and AP-4 (general hash for password) are close to hard-refusal territory; strong advocacy
- TESTING covers cryptographic test discipline (constant-time test isolation, key-management test setup)
- CONTINUITY Rule 5.3 routes waivers for cryptography gaps requiring out-of-band migration (e.g., legacy data still PBKDF2-100k that needs slow re-hash on next user login)
- CODE-QUALITY Rule on solo-maintainability informs library-default reliance over custom configuration

Reference files (`rules.md`, `anti-patterns.md`) load on demand within the consulting subagent.
<!-- /SECTION: subagent-context -->
