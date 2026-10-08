# Phase 01 - API Fundamentals

## Objectives

By the end of this phase you can, for any API you're handed:
1. Identify which "family" it belongs to (REST, SOAP, GraphQL, gRPC, WebSocket) and why that
   changes your approach.
2. Read its spec format well enough to extract every operation, parameter, and data type.
3. Identify the auth scheme in use and what that implies about attack surface.
4. Reconstruct a surface map for an API that has *no* published spec at all.

## 1. The four families, conceptually

| | REST | SOAP | GraphQL | gRPC |
|---|---|---|---|---|
| Transport | HTTP verbs + JSON | HTTP POST + XML envelope | HTTP POST (usually) + JSON | HTTP/2 + binary protobuf |
| Spec format | OpenAPI/Swagger | WSDL + XSD | SDL (schema), introspection | `.proto` files |
| Typical auth | API key, Bearer JWT, OAuth2 | WS-Security, SAML, Basic | Bearer JWT, cookies | mTLS, metadata tokens |
| Proxy-friendliness | Native | Native | Native (single endpoint) | Needs proxy support for HTTP/2 + binary decode |
| Where it shows up | Public APIs, mobile backends, microservices | Enterprise/legacy, banking, government, B2B integrations | Modern SPAs, mobile backends wanting flexible queries | Internal microservice-to-microservice traffic |

WebSockets aren't a separate "API style" so much as a transport that any of the above can run
over for bidirectional/streaming use cases (live chat, notifications, real-time location) - it
gets its own phase (05) because the attack surface (handshake, message-level authz, CSWSH) is
genuinely distinct.

Read now: `reference/rest-api.md` (all). The deep-dive reference docs for the other families
(SOAP/WSDL, GraphQL, gRPC, WebSockets) ship with their respective phases in the full course -
for this REST track you only need the conceptual awareness in the table above, not the
per-family technique docs yet.

## 2. Spec formats - what to actually extract

Whatever the format, you're always pulling the same four things out of it: **operations**
(endpoints/queries/mutations/RPCs), **parameters and their types**, **auth requirements per
operation**, and **anything marked internal/deprecated/admin** (these are the highest-signal
places to start testing - deprecated and admin-only paths are chronically under-tested).

- **OpenAPI/Swagger** (`.json`/`.yaml`): `paths` = operations, `components.schemas` = types,
  `security` blocks = auth per-operation (can override globally). Import into Bruno to get a
  working collection instantly.
- **WSDL + XSD**: `wsdl:operation` = operations, referenced XSD files = types. No single index
  file is a common real-world pattern (many services ship one WSDL+XSD set per "part" with no
  top-level file tying them together) - full methodology and tooling arrive with the SOAP phase
  in the full course.
- **GraphQL SDL**: query/mutation/subscription root types define everything reachable. If
  introspection is disabled, field-suggestion/error-based recovery can often rebuild most of the
  schema anyway (the GraphQL phase of the full course covers the field-suggestion/error-based recovery bypasses).
- **protobuf `.proto`**: `service` blocks define RPCs, `message` blocks define types. If server
  reflection is enabled, `grpcurl -plaintext <host> list` gets you the whole surface without the
  `.proto` file at all - if it's not, you need the file from somewhere (app binary, leaked repo,
  intercepted traffic + a decoder).

## 3. Auth schemes and what they imply

| Scheme | What to check first |
|---|---|
| API key (header/query param) | Is it a static long-lived value tied to a specific caller, or session-like? Query-param keys leak into logs/referrers/history. |
| Bearer JWT | Decode it immediately (never assume it's opaque). Check `alg`, check for a `kid` header, check what claims drive authorization decisions server-side (see `reference/jwt-attacks.md`). |
| OAuth2 / OIDC | Which grant type? Client credentials (machine-to-machine, no user in the loop) behaves very differently from authorization code (redirect_uri, PKCE, token leakage via referrer). See `reference/oauth-oidc.md`. |
| Basic / WS-Security (SOAP) | Often paired with legacy systems that skip modern protections entirely - check for missing rate limiting, verbose SOAP faults leaking stack traces. |
| mTLS (common in gRPC) | Is client cert validation actually enforced, or just requested? (You'll practice this directly in the later gRPC phase.) |

## 4. Discovering surface that isn't documented

Real engagements rarely hand you a clean spec. Sources, roughly in order of yield:
1. JS bundles (grep for fetch/axios calls, base URLs, endpoint string literals).
2. Mobile app APK/IPA - decompile, pull hardcoded API hosts and endpoint paths, look for
   endpoints the mobile client uses that the web client never calls (this is precisely OWASP
   API9's "improper inventory management" - crAPI's own mobile app is a real example of this,
   you'll use it in Phase 02).
3. Wayback Machine / historical JS for now-undocumented but still-live old endpoints.
4. Common spec-file paths (`/swagger.json`, `/openapi.yaml`, `/graphql` with introspection,
   `/api-docs`) - full list in `reference/rest-api.md` section 1.
5. Brute force with `ffuf`/`kiterunner` against a wordlist derived from what you already know
   about the API's naming conventions (versioned prefixes, resource-noun patterns) - generic
   wordlists are low-yield here, a tailored one from step 1-2 is much better.

## Milestone (see `workshop.md`)

Given a real public OpenAPI spec you haven't seen before, produce a complete attack-surface map
and auth-scheme identification with no traffic sent to the actual API - this phase is about
reading specs correctly, not exploitation (that starts in Phase 02).
