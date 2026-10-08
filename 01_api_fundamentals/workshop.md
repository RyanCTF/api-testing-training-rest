# Phase 01 Workshop - Surface Mapping From a Spec

**Mode:** Solo or live. If live: everyone maps the same spec independently for 30-40 min, then
compare notes - differences in what people flagged as "interesting" are usually the most useful
part of the discussion.

## Setup

Pick one public, real OpenAPI spec you have not already looked at. Two good options depending on
how much time you want to spend:

- **Quick pass (~30 min):** the classic Swagger Petstore spec -
  `https://petstore3.swagger.io/api/v3/openapi.json` - small enough to fully map in one sitting.
- **Full pass (~90 min):** a large real-world public API spec, e.g. GitHub's REST API OpenAPI
  description or Stripe's public API spec (both published by the vendor for integration
  purposes - you're only reading the document, not sending it any traffic, so this is fine to do
  against the real published spec).

This exercise never sends a single request to the live API - it's entirely about extracting
information correctly from the spec document.

## Task

Import the spec into Bruno (or just read the raw JSON/YAML, your call), then produce:

1. **Full operation inventory** - every path + method, grouped by resource.
2. **Auth scheme map** - which operations require auth, which are public, and what scheme
   (global `security` block vs. per-operation overrides - check for operations that override the
   global scheme to something weaker, that's a real, common misconfiguration pattern).
3. **Highest-priority test targets, ranked**, with a one-line reason each. You're looking for:
   - Any operation whose path or description implies elevated privilege (admin, internal,
     batch, export).
   - Any operation that takes an ID as a path/query param where a sibling "list mine" operation
     also exists (classic BOLA setup - if there's a `GET /orders/{id}`, is there also a
     `GET /orders` scoped to "my" orders? if both exist, that's your first BOLA hypothesis).
   - Any operation whose request schema has more writable fields than its corresponding read
     schema exposes (mass-assignment hypothesis).
   - Anything marked deprecated - deprecated rarely means removed.
4. **Data model summary** - what object types exist and how they relate (helps spot IDOR chains
   later: if a `Ticket` references a `UserID`, does any operation let you read/write a `Ticket`
   without proving ownership of that `UserID`?).

## Deliverable

`my-work/01-surface-map.md` containing the four sections above for the spec you
picked. This is a real artifact you'd actually produce at the start of a real API engagement -
treat it that way, not as busywork.

## Solution notes

<details>
<summary>What "good" looks like</summary>

There's no single correct answer since this is a mapping exercise, not an exploit. The bar is:
could someone who has never seen this spec read your document and immediately know where to
start testing, and why? If your ranked list is just "test everything" with no reasoning, redo it -
the ranking and the *reasoning* is the actual skill being practiced here, not the inventory
itself (that part is closer to clerical work).
</details>
