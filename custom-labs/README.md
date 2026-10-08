# Custom Labs - Build Tracker (REST track)

Per `COVERAGE-MATRIX.md`, some gaps in public tooling needed a custom-built lab. This REST-track
release ships the three REST sections, all **built and verified live** (exploited end-to-end
against a running stack, not just written and assumed to work). BOLA and BFLA are a deliberate
second data point for those two categories - both are already well covered by the public labs,
but at least one instance of each is fully self-built and self-verified here rather than relying
only on external projects. (The full course adds SOAP sections to this same lab in a later
phase.)

## Structure convention

All custom labs live in **one app**, `api-custom-lab/`, with a path-namespaced section per
issue - PortSwigger-style ("one lab, one issue, one URL"), but consolidated into a single
deployable:

```
/api/<issue-slug>/<n>     e.g. /api/unsafe-consumption/1
```

The `<n>` suffix exists so a second instance of the same issue class can be added later without
restructuring anything.

## Sections

| Path | Covers | Status |
|---|---|---|
| `/api/bola/1` | OWASP API1:2023 - a genuine token from one user reaches another user's invoice by ID, no ownership check | **Built, verified** |
| `/api/bfla/1` | OWASP API5:2023 - a genuine token is checked, but not its owner's role, on an admin-only refund endpoint | **Built, verified** |
| `/api/unsafe-consumption/1` | OWASP API10:2023 - main-app blindly fetches a URL sourced from a "trusted" partner API; a partner-registered attacker points it at a docker-network-only internal service and reads its response back through main-app | **Built, verified** |

Every section returns a `FLAG{...}` string in its response only once the actual vulnerability
(not just the endpoint) has been exploited - state genuinely changed, or data genuinely leaked
across a trust boundary that shouldn't have been crossed.

## Layout

```
custom-labs/api-custom-lab/
  README.md              # per-lab index (path, one-line description, no solutions) + run instructions
  docker-compose.yml      # main-app (published :5000), partner-api (published :5001),
                          # internal-service (NOT published - network-internal only)
  main-app/
    app.py                # registers each section's blueprint + lab index page
    sections/
      bola.py
      bfla.py
      unsafe_consumption.py
  partner-api/app.py       # simulated third-party the main app trusts
  internal-service/app.py  # simulated internal-only service, no published port
```

Run it: `cd custom-labs/api-custom-lab && docker compose up --build` (or `docker-compose`, see
`setup/SETUP.md`). Details, exact exploit requests, and per-container notes are in
`api-custom-lab/README.md`.
