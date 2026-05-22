# SECURITY-CRYPTOGRAPHY — Anti-Patterns and Canonical Patterns

Nine anti-pattern + canonical-pattern pairs covering the most common cryptographic failures at operational depth. Per Phase 6 Checkpoint 1 Decision B, hard-refusal patterns are referenced from SECURITY-CORE's canonical APs rather than restated:

- **Custom crypto** = SECURITY-CORE AP-2 (referenced; not restated)
- **MD5 / SHA-1 / DES / RC4 for security purposes** = SECURITY-CORE AP-4 (referenced; AP-4 in this skill extends with the related-but-distinct "general hash for password" case)
- **Disabled TLS verification** = SECURITY-CORE AP-3 (referenced; AP-8 / AP-9 in this skill extend with TLS-version and plaintext-fallback depth)
- **Hardcoded credentials / keys** = SECURITY-CORE AP-1 (referenced)

Per `DEC-2026-05-17-003` Clause 1: every anti-pattern is paired with a canonical pattern.

---

## AP-1: AES-ECB Mode for Confidentiality

### Anti-Pattern

```python
# Python — AES-ECB mode (default in legacy code; explicit in some libraries)
from Crypto.Cipher import AES

def encrypt_field(plaintext: bytes, key: bytes) -> bytes:
    cipher = AES.new(key, AES.MODE_ECB)  # ECB mode — equal plaintext blocks → equal ciphertext blocks
    # Padding to block size
    pad_len = 16 - (len(plaintext) % 16)
    padded = plaintext + bytes([pad_len] * pad_len)
    return cipher.encrypt(padded)
```

```java
// Java — AES/ECB explicit (the default for Cipher.getInstance("AES") on many JREs)
Cipher cipher = Cipher.getInstance("AES/ECB/PKCS5Padding");
cipher.init(Cipher.ENCRYPT_MODE, secretKey);
byte[] encrypted = cipher.doFinal(plaintext.getBytes());
```

```typescript
// Node — explicit ECB
const cipher = crypto.createCipheriv('aes-256-ecb', key, null);  // null IV — ECB doesn't use one
const encrypted = Buffer.concat([cipher.update(plaintext), cipher.final()]);
```

### Why It Fails

ECB (Electronic Codebook) mode encrypts each 16-byte block independently using the same key. Two identical plaintext blocks produce two identical ciphertext blocks. For any structured data (text, images, JSON), this leaks the pattern of the plaintext — the famous "ECB penguin" image (Linux Tux encrypted in ECB) shows the outline clearly even though the bytes are encrypted.

Beyond pattern leakage, ECB provides no integrity (not authenticated encryption) and no semantic security (deterministic — same plaintext + same key always yields same ciphertext, enabling pattern analysis across messages). ASVS V11.3.1 explicitly prohibits ECB; OWASP Cheat Sheet "Cryptographic Storage" calls out ECB as "should not be used outside of very specific circumstances."

**Source for failure mode:** `OWASP-ASVS V11.3.1` (prohibit insecure block modes ECB); `OWASP-CHEAT-CS` (Algorithms section); `CWE-327`.

### Canonical Pattern

```python
# Python — AES-GCM (authenticated, randomized, IV per message)
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import os

def encrypt_field(plaintext: bytes, key: bytes, associated_data: bytes = b'') -> bytes:
    aesgcm = AESGCM(key)  # key is 32 bytes for AES-256
    nonce = os.urandom(12)  # 12-byte nonce; CSPRNG; unique per message
    ciphertext = aesgcm.encrypt(nonce, plaintext, associated_data)
    return nonce + ciphertext  # prepend nonce for decryption

def decrypt_field(blob: bytes, key: bytes, associated_data: bytes = b'') -> bytes:
    aesgcm = AESGCM(key)
    nonce, ciphertext = blob[:12], blob[12:]
    return aesgcm.decrypt(nonce, ciphertext, associated_data)  # raises InvalidTag on tamper
```

```java
// Java — AES/GCM/NoPadding (12-byte IV, 128-bit auth tag)
Cipher cipher = Cipher.getInstance("AES/GCM/NoPadding");
byte[] iv = new byte[12];
SecureRandom.getInstanceStrong().nextBytes(iv);
GCMParameterSpec spec = new GCMParameterSpec(128, iv);  // 128-bit auth tag
cipher.init(Cipher.ENCRYPT_MODE, secretKey, spec);
byte[] ciphertext = cipher.doFinal(plaintext.getBytes());
// Store iv + ciphertext together
```

```typescript
// Node — AES-256-GCM
import { randomBytes, createCipheriv, createDecipheriv } from 'crypto';

function encryptField(plaintext: Buffer, key: Buffer): Buffer {
  const iv = randomBytes(12);  // 12-byte IV; CSPRNG
  const cipher = createCipheriv('aes-256-gcm', key, iv);
  const ciphertext = Buffer.concat([cipher.update(plaintext), cipher.final()]);
  const authTag = cipher.getAuthTag();  // 16-byte authentication tag
  return Buffer.concat([iv, authTag, ciphertext]);
}

function decryptField(blob: Buffer, key: Buffer): Buffer {
  const iv = blob.subarray(0, 12);
  const authTag = blob.subarray(12, 28);
  const ciphertext = blob.subarray(28);
  const decipher = createDecipheriv('aes-256-gcm', key, iv);
  decipher.setAuthTag(authTag);
  return Buffer.concat([decipher.update(ciphertext), decipher.final()]);  // throws on tamper
}
```

### Why It Works

AES-GCM combines AES encryption (CTR mode under the hood) with GHASH authentication in a single primitive. The 12-byte IV ensures different ciphertexts for the same plaintext under the same key (semantic security). The authentication tag (typically 128 bits) is verified at decryption — any modification to the ciphertext or IV causes verification failure, raising an exception (Python `InvalidTag`, Java `AEADBadTagException`, Node throws on `decipher.final()`). The library handles the math; the calling code just needs a unique IV per message.

**Additional considerations:** *AES-CCM and ChaCha20-Poly1305 are equivalent.* CCM is the IETF AEAD construction (used in TLS and IPsec; preferred when hardware accelerated AES is unavailable). ChaCha20-Poly1305 is the modern AEAD for environments without AES-NI (mobile, embedded) — same security properties, software-friendly. *Associated data.* AEAD primitives accept "associated data" (also called AD or AAD) — data that's authenticated but not encrypted (e.g., the encrypted record's metadata: user ID, timestamp). The associated data binds the ciphertext to its context; the same ciphertext under a different AD fails to decrypt. *Don't roll your own.* Even with AES-GCM as the primitive, mistakes in key derivation, IV handling, or AD use can break security. Use the library's high-level AEAD API; don't construct AES-CTR + GHASH from low-level primitives manually.

---

## AP-2: IV/Nonce Reuse with AES-GCM

### Anti-Pattern

```python
# Python — hardcoded IV (the worst form of IV reuse)
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

NONCE = b'\x00' * 12  # constant — every message uses the same nonce under the same key

def encrypt_field(plaintext: bytes, key: bytes) -> bytes:
    aesgcm = AESGCM(key)
    return aesgcm.encrypt(NONCE, plaintext, None)
```

```typescript
// Node — IV derived from a non-unique input (broken if input ever repeats)
function encryptField(plaintext: Buffer, key: Buffer, recordId: string): Buffer {
  // IV from recordId — fine if recordId is unique per use; broken if records are re-encrypted
  const iv = createHash('sha256').update(recordId).digest().subarray(0, 12);
  const cipher = createCipheriv('aes-256-gcm', key, iv);
  // ... rest of encryption
}
```

```python
# Python — counter that wraps / restarts (e.g., after deploy or container restart)
import struct

counter = 0  # in-memory counter

def encrypt_field(plaintext: bytes, key: bytes) -> bytes:
    global counter
    nonce = struct.pack('>12sQ', b'\x00\x00\x00\x00', counter)[:12]
    counter += 1
    # When the container restarts, counter resets to 0 → reuse with previously encrypted messages
    aesgcm = AESGCM(key)
    return aesgcm.encrypt(nonce, plaintext, None)
```

### Why It Fails

**IV/nonce reuse under the same key with AES-GCM is catastrophic.** Two ciphertexts encrypted under the same (key, nonce) pair allow an attacker to:

1. **XOR the ciphertexts** to recover the XOR of the plaintexts (confidentiality loss for any predictable structure in the plaintexts).
2. **Recover the GHASH authentication key** by solving a system of equations from observed (ciphertext, tag) pairs under the repeated nonce. With the authentication key, the attacker can **forge arbitrary authenticated messages** under that key for the lifetime of the key.

This is one of the worst failure modes in modern cryptography because (a) the consequences extend beyond confidentiality to forgery, (b) it's been documented and exploited in real systems (Project Wycheproof catches it; Microsoft SChannel had a related bug), and (c) AI-generated code defaults to "hardcoded IV for reproducibility" or "deterministic IV for caching" precisely the wrong way.

The hardcoded-IV form is the worst; the "deterministic IV from record ID" form is fine as long as the (key, record-ID) pair never repeats — but if you ever re-encrypt the same record (after edit, after rotation), you've reused. The counter form is fine as long as the counter is monotonic and persisted across restarts — both fragile properties to guarantee.

**Source for failure mode:** `OWASP-ASVS V11.3.4` (nonces/IVs/single-use numbers not reused across encryption key/data pairs); `CWE-323` (Reusing a Nonce, Key Pair in Encryption).

### Canonical Pattern

```python
# Python — random nonce per encryption (CSPRNG; standard pattern)
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import os

def encrypt_field(plaintext: bytes, key: bytes, associated_data: bytes = b'') -> bytes:
    aesgcm = AESGCM(key)
    nonce = os.urandom(12)  # 12-byte CSPRNG nonce — collision probability negligible up to ~2^32 messages
    ciphertext = aesgcm.encrypt(nonce, plaintext, associated_data)
    return nonce + ciphertext  # prepend nonce; recipient extracts before decrypting

def decrypt_field(blob: bytes, key: bytes, associated_data: bytes = b'') -> bytes:
    aesgcm = AESGCM(key)
    nonce, ciphertext = blob[:12], blob[12:]
    return aesgcm.decrypt(nonce, ciphertext, associated_data)
```

```typescript
// Node — random IV per encryption
import { randomBytes } from 'crypto';

function encryptField(plaintext: Buffer, key: Buffer): Buffer {
  const iv = randomBytes(12);  // CSPRNG; new IV per call
  const cipher = createCipheriv('aes-256-gcm', key, iv);
  const ciphertext = Buffer.concat([cipher.update(plaintext), cipher.final()]);
  const authTag = cipher.getAuthTag();
  return Buffer.concat([iv, authTag, ciphertext]);
}
```

```python
# Python — when key-volume is huge (>2^32 messages per key), use ChaCha20-Poly1305 with 24-byte nonce
# Or rotate keys frequently enough that the 2^32 boundary is never approached per key
from cryptography.hazmat.primitives.ciphers.aead import ChaCha20Poly1305

def encrypt_field_xchacha(plaintext: bytes, key: bytes) -> bytes:
    # XChaCha20-Poly1305 (in libsodium / NaCl) has 24-byte nonce — collision-resistant up to ~2^96
    # cryptography library has ChaCha20Poly1305 with 12-byte nonce; for XChaCha20 use pynacl
    chacha = ChaCha20Poly1305(key)
    nonce = os.urandom(12)
    return nonce + chacha.encrypt(nonce, plaintext, None)
```

### Why It Works

A 12-byte CSPRNG nonce gives ~2^96 possible values; the birthday-bound for collision over ~2^32 messages per key is negligible (~2^-32 chance per pair). Rotate the key well before approaching 2^32 messages and the collision risk stays remote. The nonce is fresh per encryption — no state to manage, no counter persistence to worry about, no "what if the container restarts" failure mode.

**Additional considerations:** *Key rotation as defense.* The 2^32 per-key limit assumes 12-byte random nonces; rotating the encryption key per cryptoperiod (per Rule 5.6) keeps every key well under this limit. *XChaCha20-Poly1305.* Variant with 24-byte nonce — the larger nonce space makes random-nonce safety hold for vastly more messages per key. Useful for high-volume systems (cloud storage backends, message queues) where 2^32 per key is a real ceiling. *Deterministic AEAD.* AES-GCM-SIV (RFC 8452) is the "synthetic IV" variant: nonce reuse degrades safely (you reveal that two encrypted messages are equal, but you don't compromise the auth key). Useful for archival / deduplication contexts where determinism matters; trades performance for misuse-resistance.

---

## AP-3: Non-CSPRNG (`Math.random`, `rand`, `Random`) for Security Values

### Anti-Pattern

```javascript
// JavaScript — Math.random for session ID
function generateSessionId() {
  // After observing ~10 outputs, attacker can predict all future outputs
  return Math.random().toString(36).substring(2, 15);
}

// JavaScript — even worse: Math.random for tokens
function generatePasswordResetToken() {
  const chars = 'abcdefghijklmnopqrstuvwxyz0123456789';
  let token = '';
  for (let i = 0; i < 32; i++) {
    token += chars[Math.floor(Math.random() * chars.length)];
  }
  return token;
}
```

```python
# Python — random.choices for security token
import random

def generate_api_key():
    # random.choices uses the Mersenne Twister PRNG — predictable from outputs
    return ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=32))
```

```java
// Java — java.util.Random (NOT SecureRandom)
import java.util.Random;

public class TokenGenerator {
  private static final Random rng = new Random();  // non-secure PRNG
  
  public static String generateToken() {
    byte[] bytes = new byte[32];
    rng.nextBytes(bytes);
    return Base64.getUrlEncoder().encodeToString(bytes);
  }
}
```

### Why It Fails

Non-cryptographic PRNGs are designed for statistical-distribution quality and speed, not unpredictability. Their internal state is small (xorshift128+ in V8's `Math.random()`: 128 bits; Mersenne Twister in Python's `random`: 19937 bits but with linear-recurrence weakness; `java.util.Random`: 48-bit state). After observing a handful of outputs, the attacker can reconstruct the state via the recurrence and predict all future outputs.

For session IDs and tokens, predictability is the entire attack surface: an attacker who can generate a session for their own account, observe the resulting session ID, and predict the next session ID — gains unauthorized access to the next-issued session. Password-reset tokens similarly: predict the next reset token and you reset someone else's password.

The miss happens because both `Math.random()` and `crypto.randomBytes()` contain "random" in their names; AI training data has both patterns intermixed; the developer-prompt for "generate a random token" can produce either.

**Source for failure mode:** `OWASP-ASVS V11.5.1`; `CWE-330` (Use of Insufficiently Random Values).

### Canonical Pattern

```javascript
// Node — crypto.randomBytes / crypto.randomUUID
import { randomBytes, randomUUID } from 'crypto';

function generateSessionId(): string {
  // 32 random bytes encoded as URL-safe base64 — ~256 bits of entropy
  return randomBytes(32).toString('base64url');
}

function generatePasswordResetToken(): string {
  return randomBytes(32).toString('hex');  // 64-char hex = 256-bit entropy
}

// crypto.randomUUID also works (Node 14.17+; uses CSPRNG internally)
function generateRequestId(): string {
  return randomUUID();
}
```

```python
# Python — secrets module
import secrets

def generate_session_id() -> str:
    return secrets.token_urlsafe(32)  # 32 random bytes URL-safe-base64 encoded

def generate_password_reset_token() -> str:
    return secrets.token_hex(32)  # 32 random bytes hex-encoded

def generate_api_key() -> str:
    # Custom alphabet via secrets.choice
    alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
    return ''.join(secrets.choice(alphabet) for _ in range(32))
```

```java
// Java — SecureRandom
import java.security.SecureRandom;
import java.util.Base64;

public class TokenGenerator {
  // SecureRandom instances are thread-safe and self-seeding from the OS entropy pool
  private static final SecureRandom rng = new SecureRandom();
  
  public static String generateToken() {
    byte[] bytes = new byte[32];
    rng.nextBytes(bytes);
    return Base64.getUrlEncoder().withoutPadding().encodeToString(bytes);
  }
}
```

### Why It Works

`crypto.randomBytes` / `secrets.token_bytes` / `SecureRandom` / `crypto/rand.Reader` all draw from the OS entropy pool (`/dev/urandom` on Unix; `BCryptGenRandom` on Windows). The pool is seeded from hardware noise sources (interrupt timing, thermal noise on modern CPUs via `RDRAND` / `RDSEED`). The output is statistically indistinguishable from true randomness; the internal state is hidden from observers; even an attacker who observes terabytes of output cannot predict the next byte.

The 256-bit entropy (32 random bytes) gives ~2^256 possible tokens — collision in practice never happens; brute-force enumeration takes longer than the age of the universe.

**Additional considerations:** *Custom alphabets.* Use the language's CSPRNG to generate uniformly-distributed indices into your alphabet — `secrets.choice(alphabet)` does this correctly in Python; Node has no built-in equivalent for custom alphabets but `randomInt(0, alphabet.length)` (Node 14.10+) is the building block. *UUID v4 vs CSPRNG bytes.* UUID v4 has 122 bits of entropy (vs 128-bit recommendation); fine for non-token use (database keys, request IDs) but undersized for security tokens by strict ASVS V11.5.1 reading. Use `randomBytes(32)` for security tokens unambiguously. *Constant-time comparison.* When comparing a presented token against the stored token, use constant-time comparison (`crypto.timingSafeEqual` in Node; `hmac.compare_digest` in Python; `MessageDigest.isEqual` in Java) to defeat timing attacks on the comparison.

---

## AP-4: Password Hashed with General Hash (SHA-256) — No Key Stretching

### Anti-Pattern

```python
# Python — SHA-256 with salt (no key stretching)
import hashlib
import secrets

def hash_password(password: str) -> tuple[bytes, bytes]:
    salt = secrets.token_bytes(16)
    h = hashlib.sha256(salt + password.encode('utf-8')).digest()
    return (salt, h)

def verify_password(password: str, salt: bytes, expected: bytes) -> bool:
    actual = hashlib.sha256(salt + password.encode('utf-8')).digest()
    return secrets.compare_digest(actual, expected)
```

```typescript
// Node — SHA-512 with salt (slightly slower than SHA-256 but still fast — same class of failure)
import { createHash, randomBytes, timingSafeEqual } from 'crypto';

function hashPassword(password: string): { salt: string; hash: string } {
  const salt = randomBytes(16).toString('hex');
  const hash = createHash('sha512').update(salt + password).digest('hex');
  return { salt, hash };
}
```

```java
// Java — SHA-256 with salt (the wrong-tool variant; MD5 / SHA-1 would be SECURITY-CORE AP-4)
public static byte[] hashPassword(String password, byte[] salt) throws NoSuchAlgorithmException {
  MessageDigest md = MessageDigest.getInstance("SHA-256");
  md.update(salt);
  return md.digest(password.getBytes(StandardCharsets.UTF_8));
}
```

### Why It Fails

General-purpose hash functions (SHA-256, SHA-512, SHA-3) are designed to be **fast**. On modern hardware:

- A single CPU thread computes ~100 million SHA-256 hashes per second.
- A modern GPU computes ~10 billion SHA-256 hashes per second.
- A small GPU farm (10× GPUs) computes ~100 billion hashes per second.

At those rates, brute-forcing common passwords is trivial. A typical user password (top 1M wordlist with 4-character mutations) is searched in seconds. An 8-character random alphanumeric password (62^8 ≈ 2^48 space) cracks in days. The salt does not slow this down — it only prevents pre-computed rainbow tables; once an attacker has the (salt, hash) pair from a database breach, they brute-force per-user with the salt included.

Memory-hard KDFs (Argon2id, scrypt) and computational-cost KDFs (bcrypt, PBKDF2 with high iteration count) deliberately slow down per-attempt cost. Argon2id at OWASP-recommended parameters: ~10–100 guesses/second per GPU thread — about 100,000,000× slower than SHA-256. The same brute-force search that takes seconds against SHA-256 takes years against Argon2id.

This AP extends SECURITY-CORE AP-4 (which covers the truly broken MD5/SHA-1 cases). SHA-256 is *not* broken — it's the wrong tool for password storage.

**Source for failure mode:** `OWASP-ASVS V11.4.2`; `OWASP-CHEAT-PS` (Password Storage Cheat Sheet); `CWE-916` (Use of Password Hash With Insufficient Computational Effort).

### Canonical Pattern

```python
# Python — Argon2id via argon2-cffi (OWASP-preferred)
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

# Default Argon2id parameters from argon2-cffi (~64 MiB memory, 3 iterations)
# Tune higher in production; verify against OWASP Password Storage Cheat Sheet current guidance
ph = PasswordHasher(time_cost=3, memory_cost=65536, parallelism=4)

def hash_password(password: str) -> str:
    return ph.hash(password)  # output includes algorithm + parameters + salt + hash, all in one string

def verify_password(password: str, stored: str) -> bool:
    try:
        ph.verify(stored, password)
        # Optional: re-hash with new parameters if outdated
        if ph.check_needs_rehash(stored):
            return True  # caller updates the stored hash with hash_password(password)
        return True
    except VerifyMismatchError:
        return False
```

```typescript
// Node — bcrypt with cost 12 (Argon2 via argon2 package is also available)
import bcrypt from 'bcrypt';

const BCRYPT_COST = 12;  // OWASP recommends 10 minimum; 12+ preferred

export async function hashPassword(password: string): Promise<string> {
  return bcrypt.hash(password, BCRYPT_COST);
}

export async function verifyPassword(password: string, storedHash: string): Promise<boolean> {
  return bcrypt.compare(password, storedHash);
}
```

```typescript
// Node — Argon2id via argon2 package (preferred over bcrypt for new code)
import * as argon2 from 'argon2';

const ARGON2_OPTIONS = {
  type: argon2.argon2id,
  memoryCost: 19456,    // 19 MiB
  timeCost: 2,
  parallelism: 1,
};

export async function hashPassword(password: string): Promise<string> {
  return argon2.hash(password, ARGON2_OPTIONS);
}

export async function verifyPassword(password: string, storedHash: string): Promise<boolean> {
  return argon2.verify(storedHash, password);
}
```

### Why It Works

Memory-hard KDFs require both CPU time and memory per attempt. The memory requirement (Argon2id ≥ 19 MiB; scrypt ≥ 16 MiB) defeats GPU parallelization — GPUs have less memory per core than CPUs. The per-attempt cost is calibrated to add ~100ms on the legitimate server's hardware; an attacker doing brute-force is throttled to ~10 attempts/second per GPU thread, far below the ~10B/sec they'd get with SHA-256.

The output format (`$argon2id$v=19$m=65536,t=3,p=4$...salt...$...hash...`) is self-describing: algorithm + parameters + salt + hash, in one string. Verification re-derives the hash with the same parameters and compares; rehashing with new parameters is a one-line check (`check_needs_rehash`).

**Additional considerations:** *Migrating from SHA-256.* You can't mass-rehash existing SHA-256(salt, password) entries — you don't have the plaintext. Migration pattern: on next login attempt, verify against the legacy hash; if match, immediately re-hash with Argon2id and update the stored value. Track migration progress; alert users still on the legacy hash to log in. *PBKDF2 for FIPS contexts.* FIPS 140-2/3 compliance requires PBKDF2 (Argon2 is not yet FIPS-certified). Use PBKDF2-HMAC-SHA-256 with iteration count ≥ 600,000 (OWASP 2023+). *Pepper.* An application-wide secret (in HSM or KMS, separate from the database) combined with the password before hashing — defense-in-depth against database-only compromise. Pepper rotation is harder than salt rotation; treat as a long-lived secret.

---

## AP-5: PBKDF2/bcrypt/scrypt with Insufficient Parameters

### Anti-Pattern

```python
# Python — PBKDF2 with too-low iteration count (2014-era parameter)
from hashlib import pbkdf2_hmac
import secrets

def hash_password(password: str) -> tuple[bytes, bytes]:
    salt = secrets.token_bytes(16)
    # 10,000 iterations was acceptable in ~2014 — modern guidance is 600,000+
    h = pbkdf2_hmac('sha256', password.encode('utf-8'), salt, iterations=10000)
    return (salt, h)
```

```typescript
// Node — bcrypt with default cost (often 10, sometimes lower depending on version)
import bcrypt from 'bcrypt';

export async function hashPassword(password: string): Promise<string> {
  return bcrypt.hash(password, 8);  // cost 8 — under modern recommendation (12+)
}
```

```python
# Python — scrypt with insufficient N parameter
from hashlib import scrypt

def hash_password(password: str) -> tuple[bytes, bytes]:
    salt = secrets.token_bytes(16)
    # N=1024 was acceptable in ~2010 — modern guidance is N >= 2^17 (131072)
    h = scrypt(password.encode('utf-8'), salt=salt, n=1024, r=8, p=1, dklen=32)
    return (salt, h)
```

### Why It Fails

The right algorithm with the wrong parameters defeats the purpose. PBKDF2 with 10,000 iterations at modern GPU rates: ~10 million guesses/second — about a million times faster than the same algorithm at 600,000 iterations would achieve. bcrypt cost 8 vs cost 12 is a 16× speedup for attackers. scrypt at N=1024 vs N=131072 is a 128× memory reduction, allowing GPU parallelization that wouldn't fit at the higher parameter.

Parameter guidance evolves with hardware. The values that were defensible in 2014 are inadequate in 2026. The discipline is **periodically re-tuning** to current guidance and **opportunistic rehashing** on next user login.

**Source for failure mode:** `OWASP-ASVS V11.4.2` (computationally intensive KDFs with parameters balancing security and performance); `OWASP-CHEAT-PS`; `CWE-916`.

### Canonical Pattern

```python
# Python — PBKDF2 at current OWASP guidance (600,000 iterations for SHA-256)
from hashlib import pbkdf2_hmac
import secrets

PBKDF2_ITERATIONS = 600_000  # OWASP 2023+; bump per future guidance

def hash_password(password: str) -> tuple[bytes, bytes, int]:
    salt = secrets.token_bytes(16)
    h = pbkdf2_hmac('sha256', password.encode('utf-8'), salt, iterations=PBKDF2_ITERATIONS, dklen=32)
    return (salt, h, PBKDF2_ITERATIONS)  # store iterations alongside hash for migration

def verify_password(password: str, salt: bytes, stored: bytes, iterations: int) -> tuple[bool, bool]:
    computed = pbkdf2_hmac('sha256', password.encode('utf-8'), salt, iterations=iterations, dklen=32)
    matches = secrets.compare_digest(computed, stored)
    needs_rehash = iterations < PBKDF2_ITERATIONS  # opportunistic upgrade
    return (matches, needs_rehash)
```

```typescript
// Node — bcrypt with current cost; check-needs-rehash pattern
import bcrypt from 'bcrypt';

const TARGET_COST = 12;  // Above OWASP minimum of 10; tune so verification takes ~100ms on production hardware

export async function hashPassword(password: string): Promise<string> {
  return bcrypt.hash(password, TARGET_COST);
}

export async function verifyPassword(password: string, storedHash: string): Promise<{ matches: boolean; needsRehash: boolean }> {
  const matches = await bcrypt.compare(password, storedHash);
  if (!matches) return { matches: false, needsRehash: false };
  // Inspect cost from the stored hash
  const storedCost = parseInt(storedHash.split('$')[2], 10);
  return { matches: true, needsRehash: storedCost < TARGET_COST };
}

// Caller pattern:
// const result = await verifyPassword(password, user.passwordHash);
// if (result.matches && result.needsRehash) {
//   user.passwordHash = await hashPassword(password);
//   await user.save();
// }
```

```python
# Python — scrypt at modern parameters
from hashlib import scrypt
import secrets

SCRYPT_N = 2**17  # 131072 — current OWASP minimum
SCRYPT_R = 8
SCRYPT_P = 1

def hash_password(password: str) -> tuple[bytes, bytes]:
    salt = secrets.token_bytes(16)
    h = scrypt(password.encode('utf-8'), salt=salt, n=SCRYPT_N, r=SCRYPT_R, p=SCRYPT_P, dklen=32)
    return (salt, h)
```

### Why It Works

The current OWASP-recommended parameters are tuned to deliver ~100ms per legitimate verification on contemporary server hardware — slow enough to defeat attacker-budget brute-force, fast enough to not noticeably affect login latency. The opportunistic-rehash pattern lets the system migrate users to current parameters transparently: verify against the stored parameters (whatever they were when the user last set their password); if the parameters are below current guidance, immediately compute a new hash with current parameters and update.

**Additional considerations:** *Tune empirically.* Run the password-hash function on production-class hardware and measure. Target ~100ms per verify. If it's under 50ms, increase the parameter. If it's over 200ms, you're sacrificing user experience for diminishing security returns — consider increasing in smaller steps. *Argon2id parameter rationale.* The OWASP Password Storage Cheat Sheet's current guidance (verify per release) provides two parameter sets — one with more memory and fewer iterations, one with less memory and more iterations. Both deliver equivalent attack resistance; choose based on the deployment environment's memory pressure. *Per-environment parameters.* Mobile / IoT / serverless environments may need different parameters than full-server environments — the memory bound is what's typically constrained. The Cheat Sheet provides explicit guidance for these contexts.

---

## AP-6: PKCS#1 v1.5 Padding for RSA Encryption

### Anti-Pattern

```python
# Python — RSA with PKCS#1 v1.5 padding (vulnerable to Bleichenbacher and variants)
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes

def encrypt(plaintext: bytes, public_key: rsa.RSAPublicKey) -> bytes:
    return public_key.encrypt(
        plaintext,
        padding.PKCS1v15()  # vulnerable since 1998 (Bleichenbacher); ROBOT variant in 2017
    )
```

```java
// Java — RSA/ECB/PKCS1Padding (the default if no padding specified)
Cipher cipher = Cipher.getInstance("RSA/ECB/PKCS1Padding");
cipher.init(Cipher.ENCRYPT_MODE, publicKey);
byte[] ciphertext = cipher.doFinal(plaintext);
```

### Why It Fails

PKCS#1 v1.5 padding for RSA encryption is known vulnerable to **Bleichenbacher's adaptive chosen-ciphertext attack** (1998) and its modern variants (the ROBOT attack, 2017, demonstrated practical attacks against several major libraries and TLS implementations). The attack exploits a padding oracle — any response that distinguishes valid from invalid PKCS#1 v1.5 padding (different error codes, timing differences, behavior differences) lets the attacker recover the plaintext one bit at a time.

The fix is **RSA-OAEP** (Optimal Asymmetric Encryption Padding) for encryption — explicitly designed to resist padding-oracle attacks. For signatures, **RSA-PSS** (Probabilistic Signature Scheme) is the modern equivalent. ASVS V11.3.1 prohibits PKCS#1 v1.5 padding schemes.

**Source for failure mode:** `OWASP-ASVS V11.3.1` (prohibit weak padding schemes PKCS#1 v1.5); `CWE-780` (Use of RSA Algorithm without OAEP); cross-ref Bleichenbacher 1998, ROBOT 2017.

### Canonical Pattern

```python
# Python — RSA-OAEP for encryption
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes

def encrypt(plaintext: bytes, public_key) -> bytes:
    return public_key.encrypt(
        plaintext,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None,
        ),
    )

def sign(message: bytes, private_key) -> bytes:
    return private_key.sign(
        message,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH,
        ),
        hashes.SHA256(),
    )
```

```java
// Java — RSA-OAEP with SHA-256
Cipher cipher = Cipher.getInstance("RSA/ECB/OAEPWithSHA-256AndMGF1Padding");
OAEPParameterSpec oaepParams = new OAEPParameterSpec(
  "SHA-256", "MGF1", MGF1ParameterSpec.SHA256, PSource.PSpecified.DEFAULT
);
cipher.init(Cipher.ENCRYPT_MODE, publicKey, oaepParams);
byte[] ciphertext = cipher.doFinal(plaintext);
```

### Why It Works

RSA-OAEP introduces additional randomization and a hash-based structure that makes the padding either valid or unambiguously invalid in ways that don't reveal information about the plaintext. The MGF1 mask generation function (with SHA-256 as the hash) ensures the padding bytes are uniformly distributed; the OAEP construction includes an integrity check that fails cleanly on tamper. Practical Bleichenbacher-style attacks don't apply.

**Additional considerations:** *Use ECC over RSA when possible.* Modern systems increasingly prefer Curve25519 / X25519 for key agreement and Ed25519 for signatures — smaller keys (32 bytes), faster operations, no padding-mode complexity. RSA remains relevant for interoperability with older systems. *Hybrid encryption.* For encrypting data larger than the RSA key size minus padding overhead (which is most data), use hybrid: generate a fresh AES key per message, encrypt the data with AES-GCM, encrypt the AES key with RSA-OAEP, send both. *Signature schemes.* RSA-PSS over RSA-PKCS#1 v1.5 for new code. ECDSA on P-256 / P-384 for FIPS contexts. Ed25519 for new non-FIPS code (smaller signatures, deterministic, side-channel resistant).

---

## AP-7: Same Key Reused Across Cryptographic Purposes

### Anti-Pattern

```python
# Python — one key for AES encryption AND HMAC signing
import os
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import hmac
import hashlib

MASTER_KEY = os.environ['MASTER_KEY'].encode()  # single 32-byte key for everything

def encrypt(plaintext: bytes) -> bytes:
    aesgcm = AESGCM(MASTER_KEY)
    nonce = os.urandom(12)
    return nonce + aesgcm.encrypt(nonce, plaintext, None)

def sign(message: bytes) -> bytes:
    # Same key — if an HMAC oracle leaks anything, encryption is also at risk
    return hmac.new(MASTER_KEY, message, hashlib.sha256).digest()
```

```python
# Python — same RSA keypair for encryption AND signing
def encrypt_for_user(plaintext: bytes, user_public_key) -> bytes:
    return user_public_key.encrypt(plaintext, padding.OAEP(...))

def sign_for_user(message: bytes, user_private_key) -> bytes:
    # Same keypair — attacks on signing can compromise encryption and vice versa
    return user_private_key.sign(message, padding.PSS(...), hashes.SHA256())
```

### Why It Fails

Key purpose separation is a foundational discipline. Each cryptographic primitive has an associated threat model and attack surface. When one key serves multiple purposes:

1. **Attacks on one purpose compromise the other.** An attacker with a signing oracle (server signs arbitrary messages on request) can sometimes use the structure of the signing operation to learn about the encryption key. Cross-purpose attacks are documented in RSA (signing-as-decryption oracle) and in some hash-based constructions.

2. **Key-leakage scope is amplified.** If the key leaks via one path (e.g., debug logging of an HMAC operation), every operation under that key is compromised — including operations the leak path didn't touch.

3. **Rotation becomes impossible.** Rotating a key requires re-doing every operation that used it — if the key serves multiple purposes, the operational coordination becomes brittle.

The fix is purpose-specific keys: separate keys for encryption, signing, MAC, KEK, DEK. NIST SP 800-57 §5.2 explicitly mandates key separation.

**Source for failure mode:** `OWASP-ASVS V11.1.1` (prevent key oversharing); `NIST SP 800-57 §5.2` (key types and separation); cross-ref `OWASP-CHEAT-CS §Key Management`.

### Canonical Pattern

```python
# Python — separate keys for each purpose, derived from a master via HKDF
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import hashes
import os

MASTER = os.environ['MASTER_KEY'].encode()  # the master secret

def derive_key(purpose: str, length: int = 32) -> bytes:
    """Derive a purpose-specific key from the master via HKDF."""
    hkdf = HKDF(
        algorithm=hashes.SHA256(),
        length=length,
        salt=None,
        info=purpose.encode('utf-8'),  # 'info' parameter binds the derived key to its purpose
    )
    return hkdf.derive(MASTER)

ENCRYPTION_KEY = derive_key('aes-gcm-encryption', length=32)
SIGNING_KEY = derive_key('hmac-sha256-signing', length=32)
SESSION_TOKEN_KEY = derive_key('session-token-mac', length=32)

def encrypt(plaintext: bytes) -> bytes:
    aesgcm = AESGCM(ENCRYPTION_KEY)
    nonce = os.urandom(12)
    return nonce + aesgcm.encrypt(nonce, plaintext, None)

def sign(message: bytes) -> bytes:
    return hmac.new(SIGNING_KEY, message, hashlib.sha256).digest()
```

```python
# Python — separate RSA keypairs for encryption vs signing
encryption_keypair = rsa.generate_private_key(public_exponent=65537, key_size=3072)
signing_keypair = rsa.generate_private_key(public_exponent=65537, key_size=3072)

# Encryption uses encryption_keypair.public_key() to encrypt; encryption_keypair to decrypt
# Signing uses signing_keypair to sign; signing_keypair.public_key() to verify
```

### Why It Works

HKDF (HMAC-based Key Derivation Function, RFC 5869) takes a master secret and a context string and produces a purpose-specific key. The derived keys are cryptographically independent — leaking the encryption key doesn't reveal the signing key (or the master). Rotation of the master rotates all derived keys simultaneously; rotation of a single purpose requires only that purpose's HKDF context to change.

For asymmetric crypto, generating separate keypairs per purpose is the equivalent — the operational complexity is slightly higher (two keypairs to manage instead of one) but the discipline is sound.

**Additional considerations:** *KEK/DEK pattern.* Per Rule 5.6, large data sets use a Key Encryption Key (KEK) to encrypt per-record Data Encryption Keys (DEK). The KEK is the long-lived master; DEKs are short-lived per-record. Rotating the KEK re-encrypts (small) DEKs; rotating DEKs re-encrypts only that record's data. *Envelope encryption in cloud KMS.* AWS KMS, GCP Cloud KMS, Azure Key Vault all support the envelope-encryption pattern natively — the application calls "encrypt with master key X"; the KMS generates a DEK, encrypts the data with the DEK, encrypts the DEK with the KEK, returns both. Decryption reverses. The application never sees the master key directly. *Cross-reference to secrets-management.* `security-secrets-management` (Phase 6 commit 5/12) handles the operational side of key storage and rotation; this rule handles the cryptographic discipline of key separation.

---

## AP-8: TLS 1.0 / 1.1 Still Enabled

### Anti-Pattern

```nginx
# nginx — explicit TLS 1.0 + 1.1 allowed (still seen in legacy configs)
server {
  listen 443 ssl;
  ssl_protocols TLSv1 TLSv1.1 TLSv1.2 TLSv1.3;  # TLSv1 and TLSv1.1 should NOT be here
  ssl_ciphers HIGH:!aNULL:!MD5:!RC4;
  # ...
}
```

```python
# Python — explicit minimum TLS 1.0 in client code
import ssl

context = ssl.create_default_context()
context.minimum_version = ssl.TLSVersion.TLSv1  # too low; should be TLSv1_2 or TLSv1_3
```

```java
// Java — SSLContext with insecure protocol
SSLContext sslContext = SSLContext.getInstance("TLS");  // ambiguous; may include TLSv1.0
sslContext.init(null, null, null);
// Should use SSLContext.getInstance("TLSv1.2") or "TLSv1.3"
```

### Why It Fails

TLS 1.0 (1999) and TLS 1.1 (2006) have been formally deprecated by RFC 8996 (2021). They were already discouraged before then due to:

- **BEAST (2011):** TLS 1.0 CBC-mode vulnerability allowing plaintext recovery
- **POODLE (2014):** SSLv3 protocol issue with downgrade-attack implications for TLS 1.0
- **FREAK (2015):** Forced downgrade to export-grade ciphers
- **Logjam (2015):** Diffie-Hellman parameter weakness affecting TLS 1.0
- **Lucky 13 (2013):** CBC mode timing attack
- **CRIME / BREACH:** Compression-based attacks (TLS 1.0 specifically)

With both endpoints supporting TLS 1.2+, modern clients automatically negotiate the higher version — but an attacker performing a downgrade attack can force renegotiation to the weakest mutually-supported protocol. As long as TLS 1.0/1.1 is in the server's allowed list, the downgrade is possible.

ASVS V12.1.1 mandates current TLS versions (1.2, 1.3) only.

**Source for failure mode:** `OWASP-ASVS V12.1.1`; `RFC-8996` (deprecating TLS 1.0/1.1).

### Canonical Pattern

```nginx
# nginx — TLS 1.2 + 1.3 only; modern cipher suites
server {
  listen 443 ssl http2;
  ssl_protocols TLSv1.2 TLSv1.3;
  
  # Mozilla "Modern" profile (Mozilla SSL Configuration Generator)
  # TLS 1.3 cipher suites are non-configurable in nginx; TLS 1.2 list below
  ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305;
  ssl_prefer_server_ciphers off;
  
  # HSTS for browser clients
  add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload" always;
  
  # ... cert config
}
```

```python
# Python — minimum TLS 1.2; prefer 1.3
import ssl

context = ssl.create_default_context()
context.minimum_version = ssl.TLSVersion.TLSv1_2
context.maximum_version = ssl.TLSVersion.TLSv1_3
# Optional: restrict cipher suites (Python's defaults from OpenSSL are typically modern)
# context.set_ciphers('ECDHE+AESGCM:ECDHE+CHACHA20:DHE+AESGCM')
```

```java
// Java — explicit TLS 1.2 (TLS 1.3 available in JDK 11+)
SSLContext sslContext = SSLContext.getInstance("TLSv1.3");  // or "TLSv1.2" for broader compatibility
sslContext.init(null, null, SecureRandom.getInstanceStrong());

// For server-side, configure SSLEngine to disable older protocols
SSLEngine engine = sslContext.createSSLEngine();
engine.setEnabledProtocols(new String[] { "TLSv1.2", "TLSv1.3" });
```

### Why It Works

Restricting to TLS 1.2 minimum (1.3 preferred) eliminates the downgrade-attack surface. The modern cipher-suite list prioritizes forward-secrecy AEAD combinations (ECDHE + AES-GCM or ChaCha20-Poly1305) and excludes the legacy options that had known weaknesses. HSTS prevents browser-side protocol downgrade for browser clients. The configuration matches Mozilla's "Modern" SSL profile, the industry standard for high-security deployments.

**Additional considerations:** *Mozilla SSL Configuration Generator.* `ssl-config.mozilla.org` produces ready-to-use configurations for nginx, Apache, HAProxy, etc., at three profile levels (Modern, Intermediate, Old). Use Modern for new deployments; Intermediate for compatibility with older clients (drops TLS 1.0/1.1 but adds some TLS 1.2 compat). *SSL Labs / Mozilla Observatory.* External scanning tools verify the deployed configuration matches intent. Run after every TLS-config change. *Certificate types.* For new deployments, prefer ECDSA certificates (smaller, faster); RSA-2048+ is the broadly-compatible fallback. Let's Encrypt issues both. *OCSP Stapling.* Per V12.1.4 (L3), enable OCSP stapling to communicate certificate revocation status without requiring client-side OCSP lookup. nginx: `ssl_stapling on; ssl_stapling_verify on;`.

---

## AP-9: Plaintext Fallback / "Internal" Traffic Unencrypted

### Anti-Pattern

```python
# Python — HTTP allowed alongside HTTPS for the same service
@app.route('/api/users')  # listens on both 80 and 443
def get_users():
    return jsonify(users)

# Service-to-service call without TLS
def fetch_internal_data():
    # Internal service mesh — "we're behind the firewall, plaintext is fine"
    response = requests.get('http://internal-service.local:8080/data')
    return response.json()
```

```yaml
# Kubernetes manifest — service ports without TLS termination
apiVersion: v1
kind: Service
metadata:
  name: orders-service
spec:
  ports:
    - name: http
      port: 8080  # plain HTTP for service-to-service; should be TLS-encrypted
      targetPort: 8080
```

```nginx
# nginx — HTTP not redirected to HTTPS
server {
  listen 80;
  server_name api.example.com;
  # No redirect to HTTPS; serves content directly over HTTP
  location / {
    proxy_pass http://backend;
  }
}
```

### Why It Fails

Plaintext fallback creates a downgrade attack surface — even if HTTPS is the intended protocol, an attacker who can intercept the network connection (compromised pod, MITM on shared infrastructure, malicious cloud-provider activity) can:

1. **Intercept HTTP traffic directly** when the client uses HTTP first (auth tokens, session cookies, sensitive data all exposed).
2. **Force-downgrade HTTPS to HTTP** via SSL-stripping attacks (the attacker proxies the connection, presenting HTTP to the client while talking HTTPS to the server — without HSTS the client never knows).
3. **Read internal-mesh traffic** when service-to-service calls assume the network is safe — proven false repeatedly (compromised pod → all inter-pod traffic readable; cloud-provider mistake; insider).

The "internal is safe" assumption is the zero-trust failure mode that V12.3.1 explicitly addresses: encrypted protocols for all inbound/outbound connections including internal service-to-service traffic, without fallback.

**Source for failure mode:** `OWASP-ASVS V12.2.1` (TLS encrypts all HTTP traffic to external services without fallback); `V12.3.1` (encrypted protocols secure all inbound/outbound including internal); `V12.3.3` (internal HTTP-based service connections TLS-protected without fallback).

### Canonical Pattern

```nginx
# nginx — port 80 redirects to 443; HSTS preload-eligible
server {
  listen 80;
  server_name api.example.com;
  return 301 https://$host$request_uri;
}

server {
  listen 443 ssl http2;
  server_name api.example.com;
  
  ssl_protocols TLSv1.2 TLSv1.3;
  # ... cipher suites and cert config from AP-8 canonical pattern
  
  add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload" always;
  
  location / {
    proxy_pass https://backend;  # backend ALSO over HTTPS, not HTTP
    proxy_ssl_verify on;
    proxy_ssl_trusted_certificate /etc/ssl/certs/internal-ca.pem;
  }
}
```

```python
# Python — service-to-service via TLS (mTLS preferred for sensitive paths)
import requests

def fetch_internal_data():
    response = requests.get(
        'https://internal-service.local:8443/data',
        verify='/etc/ssl/certs/internal-ca.pem',  # internal CA bundle for self-signed verification
        cert=('/etc/ssl/client.crt', '/etc/ssl/client.key'),  # mTLS client cert
        timeout=5,
    )
    response.raise_for_status()
    return response.json()
```

```yaml
# Kubernetes with service mesh (Linkerd / Istio) — automatic mTLS for pod-to-pod
# Service mesh injects sidecar proxies that handle TLS termination + mTLS transparently
apiVersion: v1
kind: Service
metadata:
  name: orders-service
  annotations:
    # Linkerd: automatic mTLS via control plane
    linkerd.io/inject: enabled
spec:
  ports:
    - name: http  # appears as HTTP to the application; sidecar handles mTLS in the mesh
      port: 8080
      targetPort: 8080
```

### Why It Works

The port 80 → 443 redirect eliminates the HTTP-first-then-upgrade window. HSTS commits the browser to HTTPS for the configured max-age period (`includeSubDomains; preload` extends to subdomains and registers with the browser's preload list). Internal service-to-service calls use HTTPS explicitly (`https://...`) with internal-CA verification or mTLS for sensitive paths. Service meshes (Linkerd, Istio, Cilium-mesh, Consul Connect) provide automatic mTLS for pod-to-pod traffic — the application code uses plain HTTP within the pod, the sidecar proxy handles TLS in the mesh. This is the operationally-cleanest pattern at scale.

**Additional considerations:** *HSTS preload registration.* For browser-facing sites, register at `hstspreload.org` to be included in browsers' built-in HSTS list — protects first-visit users from SSL stripping. Requires `max-age >= 31536000` (1 year), `includeSubDomains`, `preload` directives. *Internal CA management.* For internal mTLS, run a private CA (HashiCorp Vault PKI, AWS Private CA, cert-manager in Kubernetes) that issues short-lived certificates to internal services. Automation prevents the "expired internal cert outage" problem. *Service mesh tradeoffs.* Service meshes add infrastructure complexity and per-hop latency overhead. For small deployments, explicit per-service TLS configuration is simpler. For mid-to-large deployments (10+ services), the mesh's automation is worth it. *Zero-trust framing.* "Internal" is not a security boundary — the threat model in modern architectures treats all networks as potentially hostile (compromised pod, malicious sidecar, cloud-provider issue). TLS-everywhere with mTLS for sensitive paths is the zero-trust equivalent of the firewall-perimeter model.

---

## Summary

| AP | Title | Primary Rule | Severity |
|----|-------|--------------|----------|
| AP-1 | AES-ECB mode for confidentiality | Rule 5.1 | High |
| AP-2 | IV/nonce reuse with AES-GCM | Rule 5.3 | Critical |
| AP-3 | Non-CSPRNG (`Math.random`, `rand`, `Random`) for security values | Rule 5.4 | Critical |
| AP-4 | Password hashed with general hash (SHA-256) | Rule 5.5 | Critical |
| AP-5 | PBKDF2 / bcrypt / scrypt with insufficient parameters | Rule 5.5 | High |
| AP-6 | PKCS#1 v1.5 padding for RSA | Rule 5.1 | High |
| AP-7 | Same key reused across cryptographic purposes | Rule 5.6 | High |
| AP-8 | TLS 1.0 / 1.1 still enabled | Rule 5.7 | High |
| AP-9 | Plaintext fallback / "internal" traffic unencrypted | Rule 5.7 | High |

Severity is the typical range; actual severity depends on the change context. DISAGREEMENT Rule 5.2 routes severity for findings raised here. AP-2 (IV reuse — auth key recovery), AP-3 (predictable tokens), and AP-4 (fast-hash passwords) are close to hard-refusal territory per `CLAUDE.md` §5 — strong advocacy. Cross-reference SECURITY-CORE for hard-refusal cases (AP-1 hardcoded credentials, AP-2 custom crypto, AP-3 disabled TLS, AP-4 MD5/SHA-1 broken-algo).
