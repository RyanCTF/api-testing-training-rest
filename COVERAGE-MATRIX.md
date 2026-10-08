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
connected sequence of bugs. That structure is closer to what the later capstone phase is trying
to teach (chaining, not just spot-checking categories) than anything else in this table - worth
assigning as bonus/stretch practice in Phase 02, or as capstone warm-up.

## Cross-cutting (JWT / OAuth / rate limiting) - in scope for this track

| Issue | Where you practice it here | Reference |
|---|---|---|
| JWT alg confusion / none-alg / kid injection / jku SSRF | crAPI (custom JWT impl) | `reference/jwt-attacks.md` |
| OAuth/OIDC flow attacks | crAPI auth flows (conceptual) | `reference/oauth-oidc.md` |
| Rate-limit bypass (counter-key and counted-unit axes) | crAPI coupon/OTP, vAPI | `reference/rate-limit-bypass.md` |

## Later phases (roadmap - not in this repo)

The full course also covers **GraphQL**, **SOAP/WSDL**, **gRPC** and **WebSockets**, plus a
multi-service **capstone** and a blind **final exam** (the competency gate). Those labs, their
reference docs, and their own coverage detail ship with their phases - none of it is part of this
REST track, so don't go looking for it here. The custom-lab in this repo ships its three REST
sections (BOLA, BFLA, unsafe-consumption) only; its SOAP sections belong to the SOAP phase.
