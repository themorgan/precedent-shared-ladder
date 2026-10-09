# Ladder redesign plan

**Status: a proposal for Morgan's review, 2026-10-09. Nothing here is in
force yet.** It changes only the ladder this set carries, for the people who
bring it. Anyone landing straight on `main`, Alex included, works exactly as
before.

## Why

**On 2026-10-09, two small urgent fixes were quoted 90 minutes to reach
`main` by the ladder.** About half of that was building and proving the
fixes. The rest was the ladder itself: the full local test suite at Debut
(about 10 minutes), then GitHub's full test at Produce (about 10 more), plus
a hop for each tier. The same fixes, sent the way Alex lands work, reached
`main` about 2 minutes after they were ready.

The ladder runs the same full suite two or three times for one batch:
locally at Debut, sometimes again locally at Produce, then on GitHub. The
redesign keeps one full run, GitHub's, as the gate for everyone, and makes
the local one something you ask for.

## The new shape

| Step | Today | Proposed |
|---|---|---|
| 1 Consider, 2 Act | Unchanged | Unchanged |
| **Booked** | Feature branch into `pre-staging`, quick checks | Feature branch into **`staging`**, the same quick checks |
| **Debut** | `pre-staging` into `staging`, full local suite | **Retired as a move.** "Run tests" replaces it |
| **Run tests** | (none) | Optional, on request: the full local suite on `staging` |
| **Produce** | `staging` into `main`, full local suite plus GitHub's test, before the merge | `staging` into `main` with the quick checks; **GitHub's full test runs right after the merge** |

**1. No more `pre-staging`.** Booked lands work on `staging`, which becomes
where your finished work waits until you say Produce. The quick checks stay
what they are today on `pre-staging`: only the files the change touches, in
seconds.

**2. "Run tests", when you want it.** It runs what Debut runs today, the
full local suite, on `staging`, and moves nothing. With the change being
built on 2026-10-09 (a test re-runs only when a file it reads has changed),
it should usually take a minute or two.

**3. Produce is always fast.** Quick checks, a pull request into `main`,
merged at once. GitHub's full test runs on it straight after, and the
session that did the Produce watches it. There is no fast or slow Produce:
saying "Run tests" first is the slow version.

## The two pieces that make this safe

**A. Update Vendors takes only a `main` that passed GitHub's test.** The
real risk of a fast Produce is not `main` being red for half an hour. It is
another repository running Update Vendors in that half hour and taking a
broken engine into itself. On 2026-10-09 a test that no longer fit sat on
`main` for about an hour; had it been a real bug, any repository updated in
that hour would have taken it. So Update Vendors would take the newest
`main` commit whose GitHub test passed, skip anything pending or red, and say
which commit it took and why. `main` can then move fast while every
repository only ever receives a confirmed version.

**B. A red `main` is fixed at once.** The session that ran Produce waits
for GitHub's test and fixes any failure in the same sitting, as was done on
2026-10-09. If it cannot finish, the failure is filed where the next session
sees it at session start (BestPractice's
[open_failures.py](https://github.com/alex137/BestPractice/blob/main/tools/open_failures.py)
already does this for failures found after a push).

## What it costs and what changes

**In this set (the ladder's rules):** [go-update](../practices/go-update.md)
(Booked lands on `staging`), [debut](../practices/debut.md) (retired as a
move, or kept as another word for "Run tests"),
[produce](../practices/produce.md) (quick checks, merge, then watch),
[promote](../practices/promote.md) (the stage table),
[checks-follow-the-tier](../practices/checks-follow-the-tier.md),
[tier-branch](../practices/tier-branch.md),
[stage-word-carries-its-step](../practices/stage-word-carries-its-step.md)
and [vendor-update-on-the-ladder](../practices/vendor-update-on-the-ladder.md).

**In Morgan's individual set:** `landing_branch` in `identity.json` moves
from `pre-staging` to `staging`, a setting rather than code, and the
`stage-words` rule reads "3 Booked = branch -> staging; 5 Produce = staging
-> main".

**In BestPractice's engine, written generically (no ladder words there):**
the Promote into `main` gains a mode that runs the quick checks, merges and
then waits on GitHub's test; Update Vendors learns to pick the newest
`main` commit whose test passed (piece A); and a "Run tests" entry point runs
the full local suite on a branch without moving it.

**In every repository on the ladder:** `pre-staging` stops being used. Before
the switch, one last Debut moves anything still on it into `staging`. The
branch itself is left in place and offered for deletion as a link, never
deleted by a session.

## What we give up

- **`staging` is no longer always fully tested on your machine.** It is
  tested when you say "Run tests", and by GitHub once it reaches `main`. A
  problem the quick checks miss is found after the merge, not before.
- **`main` can be red for a short time.** Piece A keeps your other
  repositories from taking it; piece B fixes it.
- **One shared landing place fewer.** Several sessions now land on `staging`
  directly, as they land on `pre-staging` today, so nothing changes in how
  they share it.
- **If GitHub's test is down or stalls,** Produce still lands, and piece A
  holds every repository at the last confirmed `main` until the test runs.

## Open questions for Morgan

1. **Should piece A apply to everyone, Alex included,** or only to people
   who bring the ladder? Recommended: everyone, since it also protects
   repositories from a direct push to `main` that breaks something. That
   changes Alex's Update Vendors too, so it needs his yes as well.
2. **What becomes of the word "Debut"?** Retire it, or keep it as another
   word for "Run tests". Recommended: keep it, so the habit still works.
3. **Should Produce refuse when the last "Run tests" on `staging` failed?**
   Recommended: yes, since a known failure should not go to `main`.
4. **Numbering.** Booked stays step 3 and Produce step 5, with "Run tests"
   as step 4, so "Promote N" and every reply's "step N of 5" keep their
   meaning.

## Order of work, once approved

1. BestPractice: piece A (Update Vendors takes a green `main`), the fast
   Produce mode, and the "Run tests" entry point, landed and live first, so
   the safety is in place before anything goes faster.
2. This set: the rule changes above.
3. Morgan's individual set: `landing_branch` and `stage-words`.
4. Each repository on the ladder: one last Debut, then Update Vendors.
