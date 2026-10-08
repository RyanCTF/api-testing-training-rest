# api-custom-lab (REST track)

One deployable app, path-namespaced sections per issue - see `../README.md` for why this exists
and what's covered where. This is the REST-track build: the three REST sections only. (The full
course adds SOAP sections to this same lab in a later phase.)

## Run it

```bash
cd custom-labs/api-custom-lab
docker compose up --build      # or: docker-compose up --build  (see ../../setup/SETUP.md)
```
- `main-app`: `http://localhost:5000` (lab index at `/`)
- `partner-api`: `http://localhost:5001` (used by the unsafe-consumption section)
- `internal-service`: not published - only reachable from inside the compose network

## Labs

| Path | Issue |
|---|---|
| `/api/bola/1` | OWASP API1:2023 - a valid token from one user reaches another user's resource |
| `/api/bfla/1` | OWASP API5:2023 - a valid token is checked, but not its owner's role |
| `/api/unsafe-consumption/1` | OWASP API10:2023 - unsafe consumption of a trusted upstream API's response |

BOLA and BFLA are already well covered by the public labs (crAPI, vAPI, VAmPI, DVRA) - these two
exist so at least one instance of each lives in something fully self-built and self-verified,
not dependent on an external project. Both use a deliberately trivial login (`POST
<path>/login` with just a `username`, no password - these two labs are about authorization, not
authentication) to get a genuine token, then misuse that genuine token against another user's
data (`bola`) or an admin-only function (`bfla`).

`unsafe-consumption` (OWASP API10) is the one no public lab covered well: `main-app` trusts the
response of a "partner" API it calls, so a partner-controlled value flows into a server-side
fetch without revalidation.

Each solved lab returns a `FLAG{...}` string in its response body once the actual
vulnerability - not just the endpoint - has been exploited (state genuinely changed, or data
genuinely leaked). Getting a normal-looking response back is not the same as solving it;
if you don't see a flag, you haven't finished it yet.

## Notes for whoever runs this

- All state is in-memory (`ACCOUNTS`/`USERS` dicts) - restarting `main-app` resets everything.
- `unsafe-consumption`'s exploit path requires reaching `internal-service`, which has no
  published port - confirming a fetch actually landed there (rather than just crafting a
  plausible-looking request) is the whole point.
