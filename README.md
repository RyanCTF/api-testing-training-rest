# API Security Testing: Zero to Hero

**New here? Read `GETTING-STARTED.md` instead of this file** - it's the literal step-by-step
version. This file is the overview/reference once you're underway.

A self-paced curriculum for experienced web application pentesters who have little or no
structured API-testing background. You already know HTTP, Burp/Caido, and the general OWASP
attack classes (SQLi, XSS, access control, etc). This course is about what's *different* when
the thing you're attacking is an API rather than a rendered web app: no UI to click through,
auth is machine-to-machine, the "spec" is the map, and a huge share of real bugs live in
authorization logic rather than injection.

## How this works

- **Self-paced.** Seven phases (00-06), each roughly 1-2 weeks of part-time effort. No fixed
  schedule - work through them whenever you have time over the next few months.
- **Two files per phase:**
  - `README.md` - concepts, what to read, why it matters.
  - `workshop.md` - the hands-on exercise and the milestone deliverable.
- **Workshops are dual-mode.** Every `workshop.md` is written to be completable entirely solo -
  it has its own target setup steps, a task list, and a spoiler-tagged solution walkthrough at
  the bottom. The same document is also the script for a live group session if we can get
  everyone together. Nobody blocks on scheduling either way.
- **Don't peek at the solution walkthrough** until you've genuinely tried for at least an hour.
  The struggle is most of the learning.

## Prerequisites

- Comfortable with Burp Suite or Caido (proxy, repeater, intercept).
- General web app pentest experience (this course does not re-teach XSS/SQLi/access control
  fundamentals - it teaches how those show up differently in an API context, plus API-native
  issues like BOLA/BFLA and mass assignment).
- Docker + Docker Compose installed locally, or a shared lab VM (see `setup/SETUP.md`).

> **This repository is the REST track (phases 00-02).** It's the first release of a larger
> course; the GraphQL, SOAP/WSDL, gRPC/WebSocket, and capstone phases are released separately as
> you progress. Everything you need for the REST track is in here.

## Repo layout

```
00_orientation/          tooling setup, lab environment, OWASP API Top 10 overview
01_api_fundamentals/     API families, specs, auth schemes, surface discovery
02_rest_api_testing/     OWASP API Top 10 hunted end-to-end on a real REST target
setup/                   tool installs + lab environment bring-up (+ EXTERNAL-LABS.md intake list)
reference/               self-contained technique docs for the REST track
custom-labs/             purpose-built vulnerable services for gaps in public tooling
```

## Reference material

The deep technique references the REST track points to (REST, SSRF, JWT/OAuth attacks,
rate-limit bypass) live in `reference/` in this repo. Nothing in this track depends on any
external repo or system - everything you need is here. (Per-family references for the other
phases ship with those phases.)

## Your work

Keep your workshop writeups and deliverables in a local `my-work/` folder (make it yourself - it
is not part of the repo and you don't push it anywhere). There's no submissions branch and
nothing to commit back here. When you finish a phase, send your writeup to whoever's running the
course however suits them - that's how progress gets tracked, there's no separate dashboard.

## Phase index

Available in this repo (the REST track):

| Phase | Topic | Milestone deliverable |
|---|---|---|
| 00 | Orientation & tooling | Lab stack running, all tools installed |
| 01 | API fundamentals | Full attack-surface map + auth scheme ID from a given spec |
| 02 | REST (OWASP API Top 10) | BOLA/BFLA/mass-assignment hunt on crAPI + writeup |

Released later as you progress: 03 GraphQL, 04 SOAP/WSDL, 05 gRPC & WebSockets, 06 Capstone +
blind final exam (the competency gate).

See `COVERAGE-MATRIX.md` for which lab covers which vulnerability class, and what's custom-built
vs. borrowed from existing public projects.
