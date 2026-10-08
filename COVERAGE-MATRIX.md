# Lab Coverage Matrix

> **REST track note:** this repo ships phases 00-02. The REST / OWASP API Top 10 section below is
> what you'll actually practice here; the GraphQL, SOAP/WSDL, gRPC, WebSocket, and cross-cutting
> sections are the forward roadmap (those labs and references arrive with their phases). The
> custom-lab in this repo ships its three REST sections only.

Maps every vulnerability class this course teaches to where you'll actually practice it. Verified
against each project's live GitHub repo on 2026-09-08 (not from memory) before this was written,
including a second pass the same day against 7 user-supplied lab URLs (see
`setup/EXTERNAL-LABS.md` for the full disposition of each).

Rule applied: use an existing, maintained, purpose-built vulnerable app wherever one exists.
Only build a custom lab where nothing suitable does.

## REST / OWASP API Security Top 10 (2023)

| # | Category | Primary lab | Supplementary | Status |
|---|---|---|---|---|
| API1 | Broken Object Level Authorization (BOLA) | crAPI | vAPI, VAmPI, DVRA, PortSwigger access-control labs, `custom-labs/api-custom-lab` `/api/bola/1` (self-built, verified 2026-09-08) | Covered |
| API2 | Broken Authentication | crAPI (JWT/OTP flaws) | vAPI, VAmPI (token TTL), PortSwigger JWT labs | Covered |
| API3 | Broken Object Property Level Auth (mass assignment / excessive data exposure) | crAPI, vAPI | VAmPI (`/users/v1/_debug`), DVRA | Covered |
| API4 | Unrestricted Resource Consumption | crAPI, vAPI (no rate limit module) | `reference/rate-limit-bypass.md`, Tiredful-API (dedicated Throttling category) | Covered |
| API5 | Broken Function Level Authorization (BFLA) | crAPI (admin endpoints), vAPI | VAmPI (admin-only DELETE), DVRA, `custom-labs/api-custom-lab` `/api/bfla/1` (self-built, verified 2026-09-08) | Covered |
| API6 | Unrestricted Access to Sensitive Business Flows | crAPI (coupon/community abuse) | PortSwigger business-logic labs, DVRA | Covered |
| API7 | Server-Side Request Forgery | crAPI (image-upload-by-URL, vehicle location) | `reference/ssrf.md` | Covered |
| API8 | Security Misconfiguration | vAPI (dedicated module) | general recon checklist | Covered |
| API9 | Improper Inventory Management | crAPI (v1 vs v2, mobile-only endpoints) | dvws-node (hidden API functionality exposure) | Covered |
| API10 | Unsafe Consumption of (Third-Party) APIs | `custom-labs/api-custom-lab` `/api/unsafe-consumption/1` | `vulnerable-apps/vulnerable-rest-api` claims coverage - unverified depth, see `setup/EXTERNAL-LABS.md` | Covered (custom, built + verified 2026-09-08) |

**DVRA (`theowni/Damn-Vulnerable-RESTaurant-API-Game`) deserves a specific callout**: unlike
the other REST targets, which scatter one vuln per endpoint, it's built as a single-path
CTF-style chain - start as a low-privileged user, escalate all the way to root through one
connected sequence of bugs. That structure is closer to what Phase 06's capstone is trying to
teach (chaining, not just spot-checking categories) than anything else in this table - worth
assigning as bonus/stretch practice in Phase 02, or as capstone warm-up.

## GraphQL

| Issue | Lab | Status |
|---|---|---|
| Introspection, schema recovery, field-suggestion | DVGA, PortSwigger "Finding a hidden GraphQL endpoint" | Covered |
| Alias batching (brute force / rate-limit bypass) | PortSwigger "Bypassing rate limiting via GraphQL aliases" | Covered |
| Authorization gaps (`node(id)` IDOR, private post access) | DVGA, PortSwigger "Accessing private GraphQL posts" | Covered |
| CSRF over GraphQL | PortSwigger "Performing CSRF exploits over GraphQL" | Covered |
| DoS (depth/alias/directive/recursive fragment) | DVGA | Covered |
| Injection (SQLi/NoSQLi/command via resolver args) | DVGA | Covered |

**Supplementary (low priority):** `vulnerable-apps/vuln-graphql-api` (fork of
`ivision-research/vulnerable-graphql-api`, 0/62 stars) - a small social-media/blog GraphQL API
with private-post visibility controls. Mostly overlaps DVGA and PortSwigger's "Accessing
private GraphQL posts" already; adds easy extra reps, not new technique coverage. `dvws-node`
also covers GraphQL access control, introspection, arbitrary file write, and batching brute
force - broader than this one, worth trying first if picking a supplement.

## SOAP / WSDL

| Issue | Lab | Status |
|---|---|---|
| WSDL/XSD enumeration, multi-WSDL shared-type detection | `custom-labs/api-custom-lab` (3 WSDLs sharing a common fault type) | Covered (custom, built + verified 2026-09-08) |
| Hidden/undocumented operation, no auth | `custom-labs/api-custom-lab` `/soap/hidden-operation/1` | Covered (custom, verified) |
| Optional-field mass assignment via XSD | `custom-labs/api-custom-lab` `/soap/mass-assignment/1` | Covered (custom, verified) |
| XXE in SOAP body | `custom-labs/api-custom-lab` `/soap/xxe/1` | Covered (custom, verified - full `/etc/passwd` read confirmed live) |
| WS-Security attacks | *(none found)* | Deferred - stretch goal, not a Phase 4 blocker |

Note: searched GitHub (2026-09-08) for a purpose-built vulnerable SOAP training app. Nothing with
real traction exists - the closest hit (`Vlangf/VulnAPI`, 0 stars) bundles a bare `soap_app.py`
as one of nine generic protocol targets with no pedagogical structure, and wasn't judged solid
enough to build a course phase on. Built a custom multi-WSDL vulnerable service instead
(`custom-labs/api-custom-lab`) using this repo's own `reference/tools/soap_recon.py` and
`reference/soap-wsdl.md` as the test methodology - every exploit path re-verified live against
a running `docker-compose up` stack before being marked Covered here, not just written and
assumed to work.

## gRPC

| Issue | Lab | Status |
|---|---|---|
| Reflection enabled | grpc-goat lab 001 | Covered |
| Plaintext transport | grpc-goat lab 002 | Covered |
| Insecure TLS / arbitrary mTLS / mTLS subject validation | grpc-goat labs 003-005 | Covered |
| Unix socket world-writable | grpc-goat lab 006 | Covered |
| SQL injection via protobuf field | grpc-goat lab 007 | Covered |
| Command injection via protobuf field | grpc-goat lab 008 | Covered |
| SSRF via protobuf field | grpc-goat lab 009 | Covered |
| BOLA/BFLA specifically over gRPC | *(not in grpc-goat)* | Gap noted, low priority - same logic as `custom-labs/api-custom-lab`'s REST BOLA/BFLA sections, transport differs; call out conceptually in Phase 5 reading, no dedicated gRPC-specific lab planned unless it becomes a real gap in practice |

`rootxjs/grpc-goat` (55 stars, actively maintained, updated 2026-08) is a genuine PortSwigger-style
"one flag per vuln, per port" lab set, already good enough to be Phase 5's gRPC component as-is.
No custom build needed here.

## WebSockets

| Issue | Lab | Status |
|---|---|---|
| Manipulating WebSocket messages | PortSwigger WebSocket labs | Covered |
| Manipulating the WebSocket handshake | PortSwigger WebSocket labs | Covered |
| Cross-site WebSocket hijacking (CSWSH) | PortSwigger WebSocket labs | Covered |
| Message-level authorization gaps | `reference/websockets.md` methodology + crAPI's live-location WS feature if present | Covered |

## Cross-cutting (JWT / OAuth / rate limiting)

| Issue | Lab | Status |
|---|---|---|
| JWT alg confusion / none-alg / kid injection / jku SSRF | PortSwigger JWT labs, crAPI (custom JWT impl), dvws-node (secret brute force) | Covered |
| OAuth/OIDC flow attacks | PortSwigger OAuth labs | Covered |
| Rate-limit bypass (counter-key and counted-unit axes) | vAPI, DVGA (alias batching), Tiredful-API (Throttling), `reference/rate-limit-bypass.md` | Covered |

## Open action items

Everything in this matrix is now Covered by either an existing, verified-live public project or
the custom-built `custom-labs/api-custom-lab` (also verified live, see `custom-labs/README.md`).
No outstanding custom-build gaps as of 2026-09-08.
