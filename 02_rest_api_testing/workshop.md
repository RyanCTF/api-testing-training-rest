# Phase 02 Workshop - crAPI BOLA/BFLA/Mass-Assignment Hunt

**Mode:** Solo or live. If live: split into pairs, one drives the proxy, one drives note-taking,
swap halfway.

## Setup

crAPI up and running (`setup/SETUP.md`). Register **two separate accounts** - this phase is
fundamentally about cross-account access, and you can't test BOLA meaningfully with only one
identity. Optionally register a third throwaway account if a feature needs an "attacker" and
"victim" that are both non-admin.

## Task

Work every authenticated feature in crAPI (profile, orders, vehicles, community forum, coupons,
mechanic/admin panel if reachable) as Account A, capturing every request in your proxy. Then, for
each request that references an object by ID (order ID, vehicle ID, post ID, user ID):

1. Replay it authenticated as Account B, same ID -> does it return Account A's data? (BOLA)
2. If there's a role-gated feature (mechanic/admin), try reaching it as a non-privileged account
   by hitting the endpoint directly rather than through the UI. (BFLA)
3. On any endpoint that accepts a JSON body for creating/updating a resource, try adding fields
   that aren't in the documented request schema but that you'd expect the underlying object to
   have (`role`, `is_admin`, `credit`, `verified`, `discount_percent` - whatever's plausible for
   that resource). (Mass assignment)
4. Decode the JWT. Check `alg`, check whether server-side authorization decisions trust any
   client-controllable claim.

Don't stop at the first confirmed bug in each category - crAPI has more than one instance of
several of these by design. Keep going until you've covered every feature area.

## Deliverable

`my-work/02-crapi-findings.md`, one entry per confirmed issue:
- Endpoint + method
- OWASP API Top 10 category
- Repro steps (exact requests, both accounts' tokens where relevant)
- Impact if this were a real target
- Your confidence level and why (did you confirm actual data access, or just a suspicious
  response code? confirm before you write it down as a finding - this is the same discipline
  you'd apply on a real engagement)

## Solution notes

<details>
<summary>If you're stuck on where to even start</summary>

Start from the order-history and vehicle-location features specifically - they're the most
direct BOLA setups in the app (an ID-scoped resource with an obvious "does this belong to me"
question). Get one clean BOLA confirmed first, then use the same "swap the ID, swap the token"
reflex on everything else.
</details>

<details>
<summary>If mass assignment isn't turning up anything</summary>

Check the community/profile update endpoints, not just the obviously security-sensitive ones -
mass assignment bugs are often on features nobody thought to threat-model precisely because they
don't look sensitive at first glance.
</details>
