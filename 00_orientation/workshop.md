# Phase 00 Workshop - Environment Check

**Mode:** Solo or live, doesn't matter - this is just a smoke test, not a teaching exercise.

## Task

1. Confirm crAPI is up: `curl -s -o /dev/null -w "%{http_code}\n" http://localhost:8888` should
   return something other than a connection error (crAPI's web UI, not necessarily 200 - a
   redirect is fine).
2. Register an account through crAPI's UI and log in. Capture the login request in your proxy.
   Identify: what does the auth token look like (JWT? opaque?), where does the client send it on
   subsequent requests (header? cookie?), and what claims does it carry if it's a JWT (decode it
   at jwt.io or with `jwt_tool`, don't guess).
3. Confirm Bruno is installed and you can import an OpenAPI spec - crAPI exposes one,
   find it (hint: check `reference/rest-api.md` section 1's discovery-path list, or just look around
   the app).
4. Confirm `jwt_tool` runs: `jwt_tool -h`.

## Deliverable

A short note in `submissions/<your-name>/00-orientation.md`:
- crAPI reachable: yes/no
- Auth token type and where it's carried
- The OpenAPI spec URL you found
- Anything that didn't install cleanly (so it can get fixed before Phase 02, not during it)

## Solution notes (if you get stuck)

<details>
<summary>crAPI auth token</summary>

crAPI issues a JWT on login, sent as `Authorization: Bearer <token>` on subsequent API calls
(not a cookie). Decode it - the claims are a preview of Phase 02's JWT-related BOLA/broken-auth
work, no need to attack it yet.
</details>

<details>
<summary>Finding the spec</summary>

crAPI's OpenAPI/spec surface is discoverable from the app itself and from the identity/community
service routes - if `curl`-ing the common paths from `reference/rest-api.md` section 1 doesn't turn it
up immediately, check the community service's own docs endpoint. This is deliberately a "go
find it" exercise, not a "here's the URL" one - that's the actual skill.
</details>
