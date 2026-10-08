# Phase 00 - Orientation

## Why this course exists

You already know how to attack a web app: find the input, follow the data, break the trust
boundary. APIs are the same game with different terrain:

- **No UI to click through.** The "map" is a spec (OpenAPI/WSDL/GraphQL SDL/protobuf) or, often,
  nothing at all - you reconstruct it from JS bundles, mobile app traffic, or brute force.
- **Auth is machine-to-machine.** Sessions/cookies give way to API keys, JWTs, OAuth2 client
  credentials, and mTLS. The attack surface shifts from "steal a session" to "forge or replay a
  token, or find where the server trusts a claim it shouldn't."
- **Authorization bugs dominate.** In web app testing, injection and XSS get a lot of attention.
  In API testing, the single most common and highest-impact class is broken authorization
  (BOLA/BFLA) - the API faithfully does exactly what it's told, for the wrong user. This is why
  OWASP publishes a separate API Security Top 10, and why it leads with authorization, not
  injection.
- **The "front end" is every other engineering team's code.** Mobile apps, partner integrations,
  internal services, and other APIs are all just callers. Assumptions that hold for a browser
  client (can't send arbitrary headers, CSP applies, same-origin policy applies) mostly don't
  hold here.

## OWASP API Security Top 10 (2023) - read this now

Read the official list end to end before Phase 02: https://owasp.org/API-Security/editions/2023/en/0x11-t10/

You don't need to memorize it, but you should recognize all ten category names on sight by the
time you start Phase 02, because that phase is structured directly around them.

## What to do in this phase

1. Work through `setup/SETUP.md` at the repo root - tools, and bring up crAPI (you'll need it
   again in Phase 02, and poking at it now for orientation doesn't hurt).
2. Read the OWASP API Top 10 page above.
3. Skim (don't deep-read yet) `reference/rest-api.md` just to see the shape of what's coming.
4. Do the `workshop.md` in this folder - it's short, just confirms your environment works.

Once your lab stack is up and you've got the Top 10 categories loosely in your head, move to
Phase 01.
