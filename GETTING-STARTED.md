# Getting Started - Steps for Trainees

This is the literal step-by-step version of "how do I actually use this repo." `README.md` is
the overview/reference; this is what you actually do, in order, starting from zero.

## Step 0 - Before you touch anything

You should have:
- Read access to this GitHub repo (ask if you don't).
- Docker + Docker Compose installed.
- Comfortable daily use of Burp Suite or Caido - this course assumes that, it doesn't teach it.

(A free PortSwigger Web Security Academy account is used in later phases, not the REST track -
you don't need it yet.)

## Step 1 - Clone it

```bash
git clone <this-repo-url>
cd api-testing-training
```

## Step 2 - Read the two orientation documents, in this order

1. `README.md` - what this course is, how phases, workshops and your writeups work.
2. `COVERAGE-MATRIX.md` - skim it. You don't need to memorize it, just know it exists so that
   later, when you're wondering "is there a lab for X," you check here first instead of asking.

## Step 3 - Set up your tools and lab environment

Follow `setup/SETUP.md` top to bottom for the tooling table, then bring up **only** the lab(s)
Phase 00 needs (crAPI) - don't bring up every lab in the repo on day one, each phase's own
`README.md` tells you what to start when you get there.

## Step 4 - Make a folder for your work

```bash
mkdir my-work
```

Everything you write - workshop deliverables, notes, the final report - goes in your local
`my-work/` folder. It's just for you; it isn't part of the repo and you don't push it anywhere.

## Step 5 - Work Phase 00

Every phase folder (`00_orientation/`, `01_api_fundamentals/`, `02_rest_api_testing/`) has the
same two files, and you always use them the same way:

1. Open `<phase>/README.md`. Read it fully before touching anything - it tells you what to read
   in `reference/` first, and why the phase matters.
2. Do the reading it points you to.
3. Open `<phase>/workshop.md`. This is the actual task. Set up whatever target it names (its own
   `## Setup` section says exactly what), then work the `## Task` section yourself.
4. **Don't open the `## Solution notes` / spoiler-tagged sections until you've genuinely tried
   for at least an hour.** They're hints, not answers - use them to get unstuck, not as the
   first thing you read.
5. Write the deliverable the workshop asks for into
   `my-work/<phase-number>-<topic>.md` (each workshop tells you the exact expected filename and
   content).
6. Send your writeup to whoever's running the course when you finish the phase - whatever's
   lowest friction for them. There's nothing to commit or push back to this repo.
7. Move to the next phase. There's no gate/approval needed between phases - work at your own
   pace, in order (each phase assumes the previous one's skills).

## Step 6 - Repeat Step 5 for phases 01 and 02

Same loop every time: README, reading, workshop setup, task, deliverable, commit, push, next.
Rough pacing is 1-2 weeks each part-time, but there's no clock - this is self-paced.

If you get stuck on something a workshop's own hints don't resolve:
1. `grep -i "<keyword>" reference/*.md` - the answer to "how do I bypass X" is very likely
   already written down.
2. For a public lab (crAPI/vAPI/VAmPI), the project's own official
   walkthrough/Solution toggle is fair game to use after a real attempt - these aren't secret,
   and using them is a normal part of working through Academy-style labs.
3. Only for `custom-labs/api-custom-lab` specifically: there's no public writeup anywhere for
   this one (we built it), so there's no external solution to fall back on if you genuinely get
   stuck for a long time - ask whoever's running this course for a nudge rather than guessing
   indefinitely.

## Step 7 - What's next

That's the REST track. The full course continues with GraphQL, SOAP/WSDL, gRPC & WebSockets, and
a capstone (a multi-service mock engagement plus a blind final exam that acts as the competency
gate). Those phases are released as you progress - ask whoever's running this course when you've
finished Phase 02 and want the next one.

## What "done with the REST track" looks like

You can pick up a REST API you've never seen and know how to start: reconstruct the surface,
identify the auth scheme, generate authorization-bypass hypotheses (BOLA/BFLA/mass assignment)
before injection hypotheses, and know which `reference/` file to go re-read for whatever's in
front of you. That reflex is what the later phases build on.
