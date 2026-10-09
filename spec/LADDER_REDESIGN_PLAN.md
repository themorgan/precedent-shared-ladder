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

**Reconciling with `main` does not change** (Morgan, 2026-10-09: "make
sure that staging doesn't change what it does now, in reconciling the
versions sent directly to main with our staging"). Today a Debut takes in
whatever reached `main` without the ladder: it builds `staging`, then
`main`'s direct commits, then the new work, checks them together, and
leaves `staging` holding everything `main` has. That same step, done the
same way, now runs wherever work enters `staging` (Booked) and at "Run
tests"; and Produce still builds its copy on top of `main`, so nothing that
reached `main` directly is ever dropped or overwritten.

**1. No more `pre-staging`.** Booked lands work on `staging`, which becomes
where your finished work waits until you say Produce. The quick checks stay
what they are today on `pre-staging`: only the files the change touches, in
seconds.

**2. "Run tests", when you want it.** It runs what Debut runs today, the
full local suite, on `staging`, and moves nothing: about 11 minutes. (A
per-test record that would have re-run only changed tests was tried on
2026-10-09 and taken back out: recording what each test reads cost more
than it saved.) **"Debut" stays as another word for it** (Morgan,
2026-10-09), so Debut becomes the optional stage: test the batch fully
before production when you want to.

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

**B. A red `main` is fixed at once, in three layers** (Morgan asked
how this works when he is offline, 2026-10-09):

1. **Usually, in the same sitting.** The session that ran Produce waits
   for GitHub's test, about 10 minutes, and fixes any failure itself before
   it stops. Produce is the authorization for that fix. This is what
   happened twice on 2026-10-09: a test that no longer fit was found and
   fixed within the hour, with nothing asked of Morgan.
2. **If the session ends first or cannot fix it, the failure is written
   down where it cannot be missed:**
   - **A GitHub issue opens by itself.** One small step in GitHub's test
     files an issue in the repository when the test on `main` fails, or
     adds to the open one. GitHub also emails the person whose push it
     tested, by default.
   - **The next session in that repository starts with it.** BestPractice's
     [open_failures.py](https://github.com/alex137/BestPractice/blob/main/tools/open_failures.py)
     already files a failure into the repository's open items and lists it
     at session start. That session raises it in its first reply and fixes
     it before other work, unless Morgan says otherwise.
   - **Morgan's other repositories say so too.** With piece A, Update
     Vendors anywhere reports "BestPractice's `main` is red, so I took the
     last green version", so he hears about it wherever he works next.
3. **Meanwhile nothing breaks for anyone.** Piece A keeps every repository
   on the last `main` that passed until the fix lands.

**Not done: an unattended fix on a timer.** A fix to the engine every
repository takes has a session, and Morgan, behind it; a scheduled job
fixing it alone is the pattern Morgan's own rules
(`crons-are-a-last-resort`) keep for when nothing else can work.

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

**In Morgan's individual set:** `landing_branch` comes out of
`identity.json` and `"retire_pre_staging": true` goes in, so each
repository's own `precedent.json` decides where work lands, one repository
at a time (Morgan, 2026-10-09: "I want to fully complete one repo at a
time"). The `stage-words` rule names both readings until the last
repository has moved.

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

## Decisions (Morgan, 2026-10-09)

1. **Piece A applies to everyone, Alex included.** And when Update Vendors
   takes a version that is not the newest `main`, it says so: which commit
   it took, how far behind the newest it is, and why (that commit's GitHub
   test is still running, or failed), so the person knows they do not have
   the latest.
2. **"Debut" is kept as another word for "Run tests"**, which makes Debut
   the optional stage.
3. **Produce never refuses after a failed "Run tests"; it shows the
   failures and asks once** (proposed below, agreed). Morgan: "often these
   tests fail for trivial reasons, and sometimes I really just need to push
   something to live quickly."
4. **Numbering stays:** Booked is step 3, "Run tests" (Debut) step 4,
   Produce step 5.

### Question 3, the answer

**Produce never refuses on a failed "Run tests"; it shows the failures and
asks once.** Telling a critical failure from a trivial one by machine would
mean sorting more than 600 tests by hand, and the sorting would go stale.
The person is the better judge, and the question costs seconds: *"Run tests
found 2 failures: <each test, one line on what it covers>. Produce
anyway?"* A yes goes straight on.

**What a yes costs, said plainly at that moment:** GitHub runs the same
tests after the merge, so a failure that is real there turns `main` red, and
under piece A your other repositories keep the previous version until it is
fixed. On 2026-10-09 that is what happened to two urgent fixes: they reached
`main` in minutes, a test that no longer fit turned it red, and fixing the
test took about 45 minutes. So shipping past a failure gets the change onto
`main` fast, while getting it into the other repositories still needs the
failure fixed. The session that ran Produce fixes it at once (piece B,
layer 1).

**For a true emergency, one override:** Update Vendors can take a specific
red `main` commit when the person names it in their own words ("take
<commit> anyway"), and records that it did.

## Order of work, once approved

1. BestPractice: piece A (Update Vendors takes a green `main`), the GitHub
   issue on a failed `main` test (piece B, layer 2), the fast Produce mode,
   and the "Run tests" entry point, landed and live first, so the safety is
   in place before anything goes faster.
2. This set: the rule changes above.
3. Morgan's individual set: `retire_pre_staging` in place of
   `landing_branch`, and `stage-words`.
4. **One repository at a time** (Morgan, 2026-10-09), starting with
   HavrutaPlanning: Update Vendors, landed all the way to `main`, brings the
   engine and changes nothing else; a second Update Vendors switches that
   repository's `landing_branch` to `staging`, brings in what was left on
   `pre-staging`, rewords its instructions and prints the delete link.
   Only once that repository works smoothly does the next one start. Until
   the last has moved, [ladder-in-a-repo-on-staging](../practices/ladder-in-a-repo-on-staging.md)
   says how the stage words work in a repository already on `staging`, and
   the rest of this set's rules keep describing `pre-staging`.
