# Additional Test Labs

Supplementary REST targets, all verified live against GitHub (stars, archive status, README)
before being slotted in - one turned out to be archived with a maintained successor, and one
claims coverage of the exact OWASP category (API10) this course had to build a custom lab for.
(A GraphQL-only lab that was also reviewed belongs to the later GraphQL phase, not this REST
track, so it's not listed here.) Full disposition below; see `COVERAGE-MATRIX.md` for where each lands in the
curriculum and `SETUP.md` for bring-up commands.

## Disposition

| Repo | Status | Verdict |
|---|---|---|
| `OWASP/crAPI` | Already in use | No change - Phase 02 primary |
| `erev0s/VAmPI` | 1316 stars, actively maintained, OpenAPI3 | **Added** - Phase 02 supplementary |
| `theowni/Damn-Vulnerable-RESTaurant-API-Game` | 935 stars, actively maintained | **Added** - Phase 02 supplementary, promoted for its single-path privilege-escalation chain |
| `payatu/Tiredful-API` | 584 stars, older/manual setup | **Added** - Phase 02 minor supplementary (has a dedicated "Throttling" category) |
| `vulnerable-apps/vulnerable-rest-api` | 0 stars, low traction | **Added with caveat** - claims API10:2023 coverage (the category we built a custom lab for), unverified depth on our end |
| `snoopysecurity/dvws` | **Archived** - maintainer's own README says "out of date, please use dvws-node" | **Substituted** with `snoopysecurity/dvws-node` (519 stars, updated this week) |

## Notes worth flagging back

- **`dvws` is archived.** The link supplied points at the old repo; its own README redirects to
  `snoopysecurity/dvws-node`, which is what got added instead. If you had the old one bookmarked
  elsewhere, update it.
- **`vulnerable-apps/vulnerable-rest-api` claims to cover API10:2023 (Unsafe Consumption of
  APIs)** - the one category `COVERAGE-MATRIX.md` originally said had no existing lab anywhere,
  which is why `custom-labs/api-custom-lab` got built. This repo's own README lists API10 as a
  covered vulnerability class, but at 0 stars and with no deep-dive done on our end into its
  actual implementation, it's not trusted as a replacement for the custom lab (which has been
  built and verified live) - it's listed as a second data point worth trying, not a substitute.
  If a trainee tries it and it's solid, worth a follow-up to promote it or fold findings back
  into the answer key.
- `dvws-node` spans REST, GraphQL, *and* XML-RPC (user enumeration) - XML-RPC doesn't map to any
  existing phase in this course and isn't getting its own phase for one repo's coverage of it;
  treat it as bonus/stretch material if a trainee gets curious, not a required checkpoint.
