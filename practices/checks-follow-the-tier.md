---
slug:        checks-follow-the-tier
title:       "Checks follow the tier: a landing judges the change; the full suite judges everything, on request and after the merge into main"
tier:        on-demand
severity:    default
applies_to:  ["tools/precedent_push_check.py", "tools/precedent_merge_check.py", "tools/precedent_branches.py"]
applies_to_why: "It governs which branch tier a check runs at, so it binds the three files that decide that: the push check, the merge gate and the tier resolver. Editing any of them is the moment a check's tier is set. Decided: 2026-09-27, when the practice landed."
occasion:    "adding a check, or deciding which branch tier a check runs at"
gates:       []
index_clause: "landing: changed files only; full suite on request; main: GitHub after merge"
checked_by:  null
defines:     []
status:      active
in_force_at: null
visible_to:  code-owners
supersedes:  []
overrides:   null
added:       "2026-10-02"
approved_by: "Morgan F, 2026-10-02, withdrawn from the universal set BestPractice, which keeps no copy (there: Morgan, 2026-09-27 (strength: decided): \"for pre-staging, we should not check every file ... the pre-staging checks need to be the fast, immediate checks ... we have staging precisely to do the full suite ... That has to be our articulated philosophy.\"). Moved up a tier on 2026-10-09, Morgan: \"Act on the ladder plan\" -- the quick checks now judge a landing on staging, the full local suite runs on request (Run tests), and GitHub's full test runs right after the merge into main (spec/LADDER_REDESIGN_PLAN.md)."
---
## Rule
**Each kind of check has one job, and a check goes where that job is done.**

- **A landing: fast, and only about the change.** A push or pull request
  onto the landing branch -- `staging` for anyone on the ladder since
  2026-10-09, `pre-staging` for anyone still on it -- is judged on the
  files it creates or changes, and on the generated files a changed
  practice feeds -- **nothing more**, in seconds. A problem in a file the
  change did not touch is named and left for the full suite, never held
  against this landing.
- **The full suite: thorough, on every file.** It runs when the person
  asks for it -- Run tests (`--run-tests`) on staging -- and on the move
  from pre-staging into staging for anyone still on it.
- **Into `main`: GitHub's full test.** On the ladder the move into main
  takes the quick checks and merges at once; GitHub's full test runs right
  after the merge, and a red `main` is fixed in the same sitting. Without
  `--fast`, the move takes the full local suite and the GitHub test before
  the merge.

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

**No session runs the full check before landing.** It runs when the person
says Run tests, and on GitHub after the merge into main (Morgan,
2026-09-27, strength: decided: *"The point of pre-staging is to move fast,
so I want the 10 minute checks to happen at the staging level, not
pre-staging"*; carried to staging itself on 2026-10-09).

**A new check states its tier when it is added**, and a check that reads
the whole repository runs on a landing only in a form limited to the
change (`precedent_check.py --changed-files-only`), or not there at all.

## Detail
**Why the split is this one.** The landing branch is where every
session's work lands, often and in small pieces; a slow or unrelated
refusal there stops work that did nothing wrong. The full suite still runs
on every batch, on GitHub after the merge into main, and Update Vendors
takes only a `main` that passed it, so a failure the quick checks miss
never reaches another repository.

**"Only about the change" is exact.** The change is what the push adds on
top of the branch it lands on (`origin/staging...HEAD`, or
`origin/pre-staging...HEAD` for anyone still landing there), so it covers
the files a session created or edited and nothing a different session put
there. A check may still READ the rest of the repository to answer, for
instance to compare one document against another, but it only REPORTS on
the changed files.
**A deletion is part of the change too.** A file the change deleted or
renamed away strands its mentions in files the change never touched, so
those mentions are reported at the landing all the same, and only for
paths this change removed (2026-09-30: an Update Vendors passed Booked, and
the Debut into staging then refused on about 15 files no earlier run had
named).
A practice file sync wrote into a consuming repository -- one its
`MANIFEST.json` names -- is not the change's own writing even when the
change is the update that wrote it, so it is not judged there: its source
judges it, and a repair here would be overwritten by the next sync
(2026-09-28, an Update Vendors refused over an acronym in a vendored
practice).

**What a landing runs today** (the quick checks; pre-staging's until
2026-10-09, and staging's for a ladder person since). The lint, the leak gate and the author
checks, as before -- the leak gate still scans the whole tree, since a
secret anywhere is this push's to stop. Added on 2026-09-27, and on the
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
the full suite.

**What moves a check to the landing:** it is fast (seconds, not minutes)
and its finding can be pinned to a file. A check that cannot name a file,
or needs the test suite, belongs in the full suite. On 2026-09-29 seven test-suite
checks that each judge one practice file moved on that rule into
`precedent_check.py`'s `practice-file-shape`, and the routing reason's check
moved with the reason into the practice file (`routing-reason`) -- so a
broken practice file is refused at the landing, not twenty minutes into
the full suite (Morgan, 2026-09-29: "make those per-file checks thorough at
pre-staging, much moreso than rolling it out to test unrelated files").

**A landing never reads the full history.** The author, date and
session-trailer checks read only commits not yet on any remote (the
trailer check since 2026-09-29, where a repository declares the set that
carries it), and a practice check given the
push's range reads only that range: the harness-adapter ledger check walked
four folders' whole history there until 2026-09-29, and pinned its finding
to a file the push had not changed, so it read everything and could never
refuse. The whole history is the very deep check's to read (Morgan,
2026-09-29: "pre-staging should never do any check of a full history").

**Where it is built.** `tools/precedent_push_check.py` decides the tier from
the branch a push writes (`precedent_branches.tier_for_push`) and adds the
changed-files practice run for a landing (`pre-staging`, or staging for a
person who lands there: `changed_since_for`);
`tools/precedent_merge_check.py` does the same for a pull request merged
through GitHub; [spec/BRANCH_TIERS_PLAN.md](https://github.com/alex137/BestPractice/blob/staging/spec/BRANCH_TIERS_PLAN.md)
holds the tier design.

## Why
Stated by Morgan on 2026-09-27, when the practice checks were added to
pushes into `pre-staging`: the checks there have to stay the fast,
immediate ones, and every file is checked at `staging` and `main`, where
there is time for it.

## Story
A plan document whose title and first heading disagreed reached
`pre-staging` on 2026-09-27: a push there ran only the lint, the leak gate
and the author check, and the practice check that knows about headings ran
only at `staging`. It surfaced as a red full check on an unrelated change a
few hours later. The fix put the practice checks at `pre-staging`, and
Morgan set the condition this practice records: only for the files the
change touches.

**2026-10-09: the quick checks move up to staging.** With the ladder
redesign Morgan approved that day ("Act on the ladder plan",
`spec/LADDER_REDESIGN_PLAN.md`), a person
on the ladder lands on staging, and staging takes the quick checks that
pre-staging took. The full local suite became Run tests, asked for when
wanted, and GitHub's full test, run once right after the merge into main,
became the gate every batch passes.

## Install
Nothing to install. A repository that vendors the engine gets the tiered
push check with it; this practice is what a session reads before adding a
check to it.
