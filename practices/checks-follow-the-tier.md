---
slug:        checks-follow-the-tier
title:       "Checks follow the tier: landing on staging judges the change; the full suite runs on request and around the move into main"
tier:        on-demand
severity:    default
applies_to:  ["tools/precedent_push_check.py", "tools/precedent_merge_check.py", "tools/precedent_branches.py"]
applies_to_why: "It governs which branch tier a check runs at, so it binds the three files that decide that: the push check, the merge gate and the tier resolver. Editing any of them is the moment a check's tier is set. Decided: 2026-09-27, when the practice landed."
occasion:    "adding a check, or deciding which branch tier a check runs at"
gates:       []
index_clause: "landing on staging: changed files only; Debut: every file; main: per Produce"
checked_by:  null
defines:     []
status:      active
in_force_at: null
visible_to:  code-owners
supersedes:  []
overrides:   null
added:       "2026-10-02"
approved_by: "Morgan F, 2026-10-02, withdrawn from the universal set BestPractice, which keeps no copy (there: Morgan, 2026-09-27 (strength: decided): \"for pre-staging, we should not check every file ... the pre-staging checks need to be the fast, immediate checks ... we have staging precisely to do the full suite ... That has to be our articulated philosophy.\")"
---
## Rule
**Each step has one job, and a check goes to the step whose job it is.**

- **A working (feature) branch: the basic checks.** The markdown lint, the
  leak gate and the commit-author checks, and nothing more.
- **Landing on `staging` (Booked, `--land`): fast, and only about the
  change.** A landing is judged on the files it creates or changes, and on
  the generated files a changed practice feeds -- **nothing more**, in
  seconds. A problem in a file the change did not touch is named and left
  for a full run, never held against this landing. **No test runs here**,
  nor the practice checks: both are Debut's and Produce's. The checks that
  do run are a closed list, and adding one takes the person's own words
  and its time, after being urged to leave it to the Debut
  ([quick-tier-is-closed](https://github.com/alex137/BestPractice/blob/staging/practices/quick-tier-is-closed.md)).
- **Debut (`--run-tests`): thorough, and it moves nothing.** The full
  suite, on every file, on staging, when the person asks for it.
- **Into `main` (Produce): what [produce](produce.md) says.** The quick
  checks on what moves, then GitHub's test after the merge, or the full
  local suite on `main` when that test is not due; the full suite before
  the merge only on the person's own words.

**Every tier checks one version: the one landing.** Its own files, plus
the current copy of each practice set in force, read and never fixed. **No
tier's check lints, checks or fixes any other branch**, and none reads a
clone the session's sources do not declare. The one other branch a tier
check reads is the push check's receipt branch, which holds records of
earlier passes and no work. Reading every branch
belongs to the [very deep check](https://github.com/alex137/BestPractice/blob/staging/practices/very-deep-check.md) alone, run on request,
and even there only to say whether a branch's work landed and whether the
branch should go (Morgan, 2026-09-29, strength: decided: *"I don't want
'everything, ever' on the deep check we do upon every promote to
staging"*; the doc checks ran on every branch from 2026-09-14 to
2026-09-19, which is the case this rules out).

**No session runs the full check before landing on `staging`.** It runs
when asked, as a Debut, and around the move into `main`; a failure there is
fixed on a feature branch and landed again by Booked (Morgan, 2026-09-27,
strength: decided; his words are in the Story).

**A new check states its tier when it is added**, and a check that reads
the whole repository runs at landing only in a form limited to the change
(`precedent_check.py --changed-files-only`), or not there at all.

## Detail
**Why the split is this one.** `staging` is where every session's work
lands, often and in small pieces; a slow or unrelated refusal there stops
work that did nothing wrong. The full suite runs on request as a Debut,
and around every move into `main`, so thoroughness at landing buys nothing
the later steps do not already buy.

**"Only about the change" is exact.** The change is what the landing adds
on top of the branch it lands on (`origin/staging...HEAD`), so it covers
the files a session created or edited and nothing a different session put
there. A check may still READ the rest of the repository to answer, for
instance to compare one document against another, but it only REPORTS on
the changed files.
**A deletion is part of the change too.** A file the change deleted or
renamed away strands its mentions in files the change never touched, so
those mentions are reported at landing all the same, and only for paths
this change removed (2026-09-30; the Story has the case).
A practice file sync wrote into a consuming repository -- one its
`MANIFEST.json` names -- is not the change's own writing even when the
change is the update that wrote it, so it is not judged there: its source
judges it, and a repair here would be overwritten by the next sync
(2026-09-28, an Update Vendors refused over an acronym in a vendored
practice).

**What landing runs today.** The lint, the leak gate and the author
checks -- the leak gate still scans the whole tree, since a secret
anywhere is this landing's to stop. Added on 2026-09-27, and on the
changed files only: the practice checks
(`precedent_check.py --changed-files-only`), a compile of each changed
Python file, a parse of each changed shell script (`bash -n`) and of each
changed JSON file, the own test of each changed check
(`tools/checks/check_x.py` runs `tools/checks/tests/test_x.sh`; a
repo-local test and its materialized copy run once, as the materialized
copy), and -- since 2026-09-28 -- a refusal of a new check that arrives
without that test or without `SOURCE_ROOT`, naming the file and lines to
add, and -- when
a practice file changed -- a check that its generated views (`AGENTS.md`,
`MAP.md`, `GLOSSARY.md`) were regenerated with it
(`precedent_push_check.py --changed-files-check`). A push sends commits that
already exist, so that last one refuses and names the command that
regenerates; it never rewrites anything itself. Everything else waits for
a full run.

**What moves a check to landing:** it is fast (seconds, not minutes) and
its finding can be pinned to a file. A check that cannot name a file, or
needs the test suite, belongs to the full run. On 2026-09-29 seven
test-suite checks that each judge one practice file moved on that rule
into `precedent_check.py`'s `practice-file-shape`, and the routing
reason's check moved with the reason into the practice file
(`routing-reason`) -- so a broken practice file is refused at landing, not
twenty minutes into a full run (Morgan, 2026-09-29, strength: decided; his
words are in the Story).

**Landing never reads the full history.** The author, date and
session-trailer checks read only commits not yet on any remote (the
trailer check since 2026-09-29, where a repository declares the set that
carries it), and a practice check given the
push's range reads only that range: the harness-adapter ledger check walked
four folders' whole history there until 2026-09-29, and pinned its finding
to a file the push had not changed, so it read everything and could never
refuse. The whole history is the very deep check's to read (Morgan,
2026-09-29; his words are in the Story).

**Where it is built.** `tools/precedent_push_check.py` decides the tier from
the branch a push writes (`precedent_branches.tier_for_push`) and adds the
changed-files practice run for a landing on staging;
`tools/precedent_merge_check.py` does the same for a pull request merged
through GitHub; `--land` and `--run-tests` in [tools/precedent_branches.py](../tools/precedent_branches.py)
run the quick and the full checks on the tree they compose;
[spec/BRANCH_TIERS_PLAN.md](https://github.com/alex137/BestPractice/blob/staging/spec/BRANCH_TIERS_PLAN.md)
holds the tier design.

## Why
Landing has to stay fast and immediate, because every session's work goes
through it, many times a day. Every file is still checked, where there is
time for it: in a Debut on request, and around the move into `main`.

## Story
A plan document whose title and first heading disagreed reached
`pre-staging` on 2026-09-27: a push there ran only the lint, the leak gate
and the author check, and the practice check that knows about headings ran
only at `staging`. It surfaced as a red full check on an unrelated change a
few hours later. The fix put the practice checks at `pre-staging`, and
Morgan set the condition this practice records: only for the files the
change touches.

Stated by Morgan on 2026-09-27, when the practice checks were added to
pushes into `pre-staging`: the checks there have to stay the fast,
immediate ones, and every file is checked at `staging` and `main`, where
there is time for it. The same day: *"The point of pre-staging is to move
fast, so I want the 10 minute checks to happen at the staging level, not
pre-staging"* (strength: decided); his own promote-only rule, in his
individual set, already had the Promote carry the full check. A failure at
the Promote was fixed on `pre-staging` and promoted again.

**2026-09-29**, on the per-file checks: *"make those per-file checks
thorough at pre-staging, much moreso than rolling it out to test unrelated
files"*; and on history: *"pre-staging should never do any check of a full
history"*.

**2026-09-30: a deletion left for the next tier.** An Update Vendors
passed Booked, and the Debut into staging then refused on about 15 files
no earlier run had named: mentions of paths the update had removed. Since
then a deletion's stranded mentions are reported at landing.

**2026-10-14: pre-staging retired for everyone** (Morgan: *"Only me, go
ahead and plan it. Retire pre-staging."*, strength: decided). The three
tiers this practice named -- `pre-staging` fast and about the change,
`staging` thorough, `main` thorough plus GitHub -- became the steps above:
the fast, change-only checks moved with Booked onto staging (`--land`, which
had run them there since 2026-10-09), the full suite became Debut's, on
request, and `main` takes what Produce says.

**2026-10-16: no test before a push.** A landing took 218 seconds of
quick checks: the harness tests a change reaches, added at landing on
2026-10-11, and the practice checks on the changed files. Morgan: *"all
the testing EXCEPT THE BARE ESSENTIAL AND LEAK GATES SHOULD GO INTO DEBUT,
AND THE GITHUB TEST AFTER THE NEXT PRODUCE"*, and *"LET'S BAN ALL NEW TESTS
BEFOREHAND EXCEPT WHEN EXPLICITLY DIRECTLY VERBALLY AUTHORIZED"* (strength:
decided). Both moved to the Debut, and the engine closed the list.

## Install
Nothing to install. A repository that vendors the engine gets the tiered
push check with it; this practice is what a session reads before adding a
check to it.
