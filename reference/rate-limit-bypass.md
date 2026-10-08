# Rate-Limit Bypass Techniques

## Core Mental Model

A rate limiter has two independent, separately-attackable parts:

1. **The counter key** - what identity does the limiter bucket attempts under? (session ID,
   account, IP, device fingerprint, some combination)
2. **The counted unit** - what does the limiter increment on? (usually "one HTTP request,"
   almost never "one logical guess actually evaluated by the business logic")

Every bypass in this class exploits a mismatch between what the limiter *thinks* it's counting
and what the backend *actually* evaluates. Two orthogonal attack axes:

- **Axis A - cheapen the key.** Get a fresh counter-key for less cost than the limiter's
  attempt budget. If logging in/registering/requesting a new OTP is free (or cheaper than one
  real attempt) and resets the counter, you have unlimited retries at the cost of N extra
  requests.
- **Axis B - inflate the unit.** Get the backend to evaluate more than one guess per counted
  request. If the comparison logic accepts a collection (array, aliased batch, polluted
  param) and loops/`.includes()`s over it, one request = many real attempts, and the limiter
  never sees the difference.

Both axes are worth testing independently and *combined* - session-reset (axis A) stacked with
batch-stuffing (axis B) multiplies effective throughput.

## Axis A - Cheapen/Rotate the Counter Key

| Technique | Mechanism | Detection |
|---|---|---|
| Session/token reset | Login or "resend code" mints a fresh session/token; the attempt counter lives on that session, not the account | Hit the lockout, re-authenticate (or hit "resend"), retry the same guess - does "attempts remaining" reset? |
| Resend-OTP reset | Requesting a new OTP resets the attempt counter for the OLD code too, or the counter is keyed to OTP-generation-id, not account | Trigger resend right before lockout; check if the counter resets even while testing the still-valid prior code |
| IP/header rotation | Limiter keys on `X-Forwarded-For`/`X-Real-IP`/`CF-Connecting-IP` instead of the real peer | Rotate the header value per request |
| Race condition on counter write | Counter increment is read-then-write, not atomic | Fire concurrent requests before the first response lands - counter under-increments |

## Axis B - Inflate What One Request Evaluates

| Technique | Mechanism | Detection |
|---|---|---|
| **Array/batch value-stuffing** | Endpoint expects `{"field": "value"}`; comparison logic (often `Array.isArray(x) ? x.includes(target) : x === target`, or a naive loop, or a query built directly from the field) evaluates a whole array of candidates in one pass. Rate limiter only sees "1 request, 1 attempt charged" | Send `{"field": ["a","b"]}` instead of a string. If the response differs from either single-value response, the array is being iterated server-side |
| HTTP Parameter Pollution (HPP) | Duplicate the parameter (`?otp=1111&otp=2222`); the framework may use the LAST value for the real check but the FIRST for the rate-limit key (or vice versa) | Send duplicate params with different values, observe whether the app processes a different value than the one the limiter appears to have charged |
| GraphQL aliased batching | Alias the same mutation N times in one query - the server executes every alias, but naive rate limiters count the HTTP request, not the resolver invocations | Send 2 aliased copies of a login/OTP mutation with different guesses; check if both actually execute against a limiter believed to allow only 1/request |
| NoSQL/operator injection | `{"otp": {"$ne": null}}` (Mongo) or `{"otp": {"$regex": "^"}}` match-anything operators - same "one request, unbounded logical matches" shape as batch-stuffing | Try Mongo-style operators as the field value even on SQL-looking apps that might have a NoSQL layer somewhere in the auth path |
| Loose-equality falsy match | Send a JS-falsy value (`0`, `false`, `""`, `null`) against a comparison target that has an uninitialized/lazy default | Always try non-string types for any "expected string" field, not just batch-stuffing |

## Combined Checklist (run in this order on any OTP/PIN/token verify endpoint)

1. **Baseline**: submit one wrong guess as a plain string. Note the exact "attempts remaining"
   language and lockout response shape.
2. **Type-probe**: resend the identical wrong guess as `0`, `false`, `null`, `""`, `[]`, and a
   single-element array `["wrong"]`. Any divergent response (different error text, different
   HTTP code, no counter decrement) signals the backend branches on type - worth deeper poking.
3. **Batch-stuff**: if the keyspace is small enough to enumerate (4-6 digit numeric OTP, low-
   entropy PIN), submit the FULL candidate space as an array in one request. Check body-size
   limits first (10,000 codes at ~7 bytes each is well under most default body-parser limits) -
   if it doesn't fit, chunk into a handful of large arrays rather than one request per
   candidate, so each chunk still only burns one counted request.
4. **Reset-probe**: deliberately burn the attempt budget to lockout, then re-authenticate (or
   hit resend/forgot-password/register) and retry - check if the counter resets to full.
5. **Stack A+B**: if reset works, wrap it in a loop - reset session, fire max-allowed batch,
   repeat until the correct code is found or the keyspace is exhausted. Compute required
   throughput against any rotation window (`keyspace / window_seconds`) before committing to a
   long-running sweep.
6. **Header rotation** as a last resort if 1-5 all fail and the limiter is confirmed IP-keyed.

## Why This Keeps Happening

Rate limiting and input validation are implemented as two separate concerns, often literally
different middleware layers, and neither is told what the other assumes. The limiter assumes
"each request is one attempt." The comparison logic assumes "the field is always a string, one
value." Neither assumption is enforced by a shared schema. Any framework that parses JSON
permissively (accepts arrays/objects wherever a scalar is expected, with no strict schema
validation at the boundary) is structurally exposed to axis B; any session/account model where
re-authentication is cheap and un-throttled is structurally exposed to axis A.

**Prevention (for write-ups / pre-answering triage pushback):** strict schema validation
(reject non-string types for OTP/PIN fields outright) closes axis B; keying the limiter on the
account identity itself (not the session) and throttling authentication/resend endpoints
closes axis A.
