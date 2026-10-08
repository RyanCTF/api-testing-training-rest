# Reference

Self-contained technical reference for the REST track - REST, SSRF, JWT, OAuth/OIDC, and
rate-limit bypass. Everything phases 00-02 point you to lives here. (The full course adds
per-family references - GraphQL, gRPC, WebSockets, SOAP/WSDL - and a report-writing guide with
their respective phases.)

| File | Covers |
|---|---|
| `rest-api.md` | REST discovery, mass assignment, BOLA, method/version tampering, CORS, parameter pollution, batch-endpoint auth bypass |
| `ssrf.md` | SSRF bypass techniques (blocklist/allowlist bypass, cloud metadata, gopher, SSRF-to-RCE), quick-paste payload set |
| `jwt-attacks.md` | alg:none, RS256->HS256 confusion, kid/jku/jwk injection, secret cracking |
| `oauth-oidc.md` | state/redirect_uri manipulation, PKCE bypass, token leakage, IdP mixup |
| `rate-limit-bypass.md` | Counter-key vs. counted-unit bypass framework (array-stuffing, alias batching, HPP) |

These are working references, not one-time reading - come back to them mid-lab when you hit
something you don't recognize.
