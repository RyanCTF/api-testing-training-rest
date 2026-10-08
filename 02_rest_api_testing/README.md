# Phase 02 - REST API Testing (OWASP API Top 10)

## Objectives

Hunt all ten OWASP API Security Top 10 (2023) categories end-to-end against a realistic,
purpose-built vulnerable REST target. By the end you should be able to look at any REST endpoint
and immediately generate hypotheses across all ten categories, not just the ones you happen to
remember.

## Read first

`reference/rest-api.md` (full), then for each category below, follow the cross-reference into
`reference/rate-limit-bypass.md` where noted.

## The ten categories, and where to hunt them on crAPI

| # | Category | What it actually looks like | Hunt it on |
|---|---|---|---|
| API1 | BOLA | `GET/PUT /orders/{id}`-style endpoints where ownership of `{id}` is never verified against the caller's identity | crAPI order/vehicle-location endpoints, or `custom-labs/api-custom-lab` `/api/bola/1` for a smaller isolated instance |
| API2 | Broken Authentication | Weak JWT implementation, OTP with no attempt limit, password-reset token predictability | crAPI login/OTP/reset flows - decode the JWT (`reference/jwt-attacks.md`) |
| API3 | Broken Object Property Level Auth | Response includes fields the caller shouldn't see (excessive exposure) or request accepts fields the caller shouldn't set (mass assignment - e.g. a `role` or `is_admin` field the client can just include) | crAPI community/profile endpoints |
| API4 | Unrestricted Resource Consumption | No rate limit on OTP/coupon/reset endpoints; no pagination limit | crAPI coupon/OTP endpoints - see `reference/rate-limit-bypass.md` for the counter-key vs counted-unit bypass framing before you conclude "not exploitable" |
| API5 | BFLA | An endpoint meant for one role (e.g. mechanic/admin) reachable by a lower-privileged authenticated user because the check is missing or client-side only | crAPI admin/mechanic-only endpoints, or `custom-labs/api-custom-lab` `/api/bfla/1` for a smaller isolated instance |
| API6 | Unrestricted Sensitive Business Flows | No abuse-protection on flows like coupon redemption or bulk actions, even if individually "authorized" | crAPI coupon/community post flow |
| API7 | SSRF | Any parameter that makes the server fetch a URL you control (image-by-URL, webhook registration, PDF/link preview) | crAPI's vehicle image-by-URL / video upload feature - see `reference/ssrf.md` for the full bypass taxonomy once you've confirmed the primitive |
| API8 | Security Misconfiguration | Verbose errors, debug endpoints left on, permissive CORS, default creds | vAPI's dedicated module, general recon of both apps |
| API9 | Improper Inventory Management | Old API versions (`v1` still live and less protected than `v2`) or mobile-only endpoints the web client never uses | crAPI ships a mobile app specifically to demonstrate this - pull it apart (Phase 01 section 4 discovery techniques apply directly here) |
| API10 | Unsafe Consumption of APIs | The server trusts data/redirects from an upstream API it calls without revalidating | `custom-labs/api-custom-lab` `/api/unsafe-consumption/1` - built specifically for this category, no public lab covered it |

## Lab

- **Primary:** crAPI (`setup/SETUP.md`) - realistic combined app, most categories present
  together the way they'd show up on a real engagement.
- **Supplementary:** vAPI and VAmPI - each isolates categories into small independent
  endpoints, useful for drilling one specific category without crAPI's other noise in the way.
  VAmPI additionally has a vulnerable on/off switch, worth toggling if you also want to see what
  a *fixed* version of the same endpoint looks like.
- **Stretch/bonus:** DVRA (Damn Vulnerable RESTaurant) - unlike the other three, it's one
  connected privilege-escalation chain (low-priv user to root) rather than independent per-vuln
  endpoints. Do this once the ten categories feel routine individually - it's closer to what a
  real engagement (and the later capstone phase) actually rewards: chaining, not category-spotting.
- Lower-priority extras (Tiredful-API, `vulnerable-apps/vulnerable-rest-api`, `dvws-node`) are
  documented in `setup/EXTERNAL-LABS.md` if you want more reps on a specific category.

## Milestone (see `workshop.md`)

Full BOLA/BFLA/mass-assignment hunt across crAPI, written up as if it were a real engagement
finding set (repro steps, impact, affected endpoints).
