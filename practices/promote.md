---
slug:        promote
title:       "\"Promote\" moves the work one tier up -- the feature branch onto staging, or staging into main -- and says which first; \"Promote N\" does stage N of the five-stage ladder"
tier:        on-demand
severity:    default
applies_to:  ["**"]
applies_to_why: "A phrase in a MESSAGE, like go-update's and push-directly's entries -- no file path reaches it. Routed by the `merge` gate. Decided: 2026-09-25, when the practice landed."
occasion:    "a person says \"Promote\", \"Promote N\" or a stage word (\"Consider\", \"Act\", \"Debut\", \"Produce\", \"Make live\"), or asks to plan, build or move work up a tier"
gates:       ["merge"]
gates_why:   "Promote is a move between branch tiers -- onto staging, or staging into main -- the moment that gate exists for."
index_clause: "the next tier up, chosen from the work and said first; \"Promote N\" does stage N"
checked_by:  null
ships:       ["tools/ladder/ladder_branches.py"]
defines:     ["Promote", "Promote N", "Graduate", "the five stages"]
command:     {"Promote": "Move the work one tier up, whichever it needs, saying which before it starts: work still on this session's feature branch lands on staging first (Booked), and work on staging that main lacks moves into main (Produce). Each move gets its own checks -- the quick checks landing on staging, the quick checks into main with GitHub's test after the merge -- and nothing moves unless they pass. The full local tests on staging (Debut) are optional and move nothing. \"Promote N\" does stage N of the five-stage ladder: 1 Consider, 2 Act, 3 Booked, 4 Debut, 5 Produce."}
status:      active
in_force_at: null
supersedes:  []
overrides:   null
added:       "2026-10-02"
approved_by: "Morgan F, 2026-10-02, withdrawn from the universal set BestPractice, which keeps no copy (there: Morgan, 2026-09-27 (decided) -- never recommend a Promote another window is already running; Morgan, 2026-09-25 -- the three branch tiers are his own design (\"to prestaging only the most minimal test; to staging/precedent-beta-v01 all local tests; and then to main, you get all those local tests AND the most important GitHub test\", strength: decided), with promotion by a person rather than a schedule (\"I think that it should not be on a cron\", decided). The word itself was the session's recommendation, approved with the plan as a whole: \"Otherwise, this looks great, let's do it, go ahead, go update\". Not re-running the suite on files that already passed it is his rule too (Morgan, 2026-09-25: \"staging will not run the full suite of tests if it's being promoted from pre-staging to staging and the full suite of tests ran on pre-staging and nothing has changed\", strength: decided). Saving the session's own work with Go update before promoting is his rule too (Morgan, 2026-09-25, strength: decided). An ambiguous Promote -- both steps with work waiting -- moves pre-staging into staging (Morgan, 2026-09-26: \"if my 'promote' is ambiguous and you don't know which of the two types of promotion it should refer to - then choose to do pre-staging to staging\", strength: decided). \"Graduate\" as a second word for the same command is his too (Morgan, 2026-09-26: \"Let's add a new vocab word 'graduate' to be used as a synonym for 'promote'\", strength: decided); \"Promote N\" and the five stages, 2026-09-27/28 (spec/FIVE_STAGES_AND_OUR_LANGUAGE_PLAN.md, strength: decided). Debut is optional, and staging into main is always Produce (Morgan, 2026-10-11, strength: decided).)"
strength:    assented
---
## Rule
**The five stages.** Promote is also the one word for the whole ladder a
piece of work climbs, from idea to production -- **"Promote N" does stage
N**, and each stage has its own word and a synonym:

| # | Stage | Synonym | What happens | Practice |
|---|---|---|---|---|
| 1 | **Consider** | Plan | Decide how much plan the work needs, and make that much. | [consider](consider.md) |
| 2 | **Act** | Build | Build it on this session's feature branch, pushed so it survives. | [act](act.md) |
| 3 | **Booked** | Shared Save | Land it from the feature branch on `staging`, with the quick checks: `--land BRANCH`. Also **Go update**, **Book it**. | [go-update](go-update.md) |
| 4 | **Debut** | Test Readiness | Optional: run the full local tests on `staging`, and move nothing: `--run-tests`. Also **Run tests**. | [debut](debut.md) |
| 5 | **Produce** | Make live | Promote staging into main -- production -- quick checks, GitHub's test after the merge. | [produce](produce.md) |

**An approved Booked or Produce covers its own follow-through.** When the
work it moved needs a fix to go green -- a check it trips, a test that
fails after it, a fix in another repository that work depends on -- that
fix is landed and produced as far as the approved move went, in every
repository it needs, without asking again; the reply says what was done.
**New work still waits for the person's own word**, and so does a move
that would carry somebody else's unapproved work along with it (Morgan,
2026-10-18, strength: decided, after one Produce took three approvals: the
third was for a fix to make the approved one pass).

**Two branch tiers: `staging`, then `main`.** Work goes from its feature
branch onto staging (Booked), and from staging into main (Produce). The
ladder is **optional for everyone**: anyone may use its words, nobody has
to, and a repository whose only shared branch is `main` simply has fewer
stages. A person's own individual set may require it for them.

**Debut is optional: a step in the middle to test the work on staging.**
Staging into main is always **Produce**, never Debut, and work on staging
goes there with no Debut at all (Morgan, 2026-10-11, strength: decided:
"the next step is Produce, staging into main. (Debut is an optional step
in the middle to test it.)").

- **Read back every stage before it runs**, with its number, word and
  synonym and the repository and branches: *"Now Promote 3: Booked, the
  Shared Save -- moving `<branch>` onto staging (BestPractice)"*, or *"Now
  Promote 4: Debut, Test Readiness -- running the full tests on staging
  (BestPractice)"*. A request covering several stages names them all:
  *"Now Promote 3 then 5: ..."*.
- **Read the request, never scan it for a word.** Every stage word is
  ordinary English. The same step can be asked for many ways -- "Debut",
  "Promote 4", "run the tests on staging", "move BestPractice staging to
  main" -- and a named step wins over any guess. Stage 5, which changes
  production, is read most strictly.
- **A bare Promote means the next step this work has not done, and never
  skips one.** Work on the feature branch means Booked first. Work on
  staging that main lacks means Produce. Asking for Produce with work still
  on the feature branch runs Booked first. **Debut runs only when asked**,
  so a bare Promote never runs it, and a bare Promote never sends finished
  work back to Consider.
- **"Graduate" is another word for Promote.**

The rest of this Rule is the moves between branch tiers.

When a message says **"Promote"** about the branch tiers -- the whole
message, or a clause like "promote staging" -- **first check this
session's own branch for work that is not on staging yet**: anything
uncommitted, or committed but not yet landed. **If there is any, run
[Booked](go-update.md) on it first**, which lands it on staging, and
confirm `origin/staging` carries it. Promote carries that authorization
itself: nobody is asked a second time. That is the whole Promote when the
work was not on staging yet. When it was already there and main lacks it,
the next step is Produce, run in the repository the work is in:

    python3 tools/precedent_branches.py --promote --to main --work BRANCH

**Promote picks its own step, and says which before anything else.** Its
first line is *"Now landing `<branch>` on staging"* or *"Now promoting from
staging to main"*; the reply opens with that same line. The session decides
from the conversation, and from the branch it was just working on
(Morgan, 2026-09-26, strength: decided; his words are in the Story):

- **This session's feature branch, not on staging yet:** Booked.
- **Already on staging but not on main:** Produce.
- **The person named the step** ("promote staging to main"): the name
  wins.
- **Neither** -- a bare Promote in a session that did no work of its own:
  staging into main when staging carries work main lacks, and otherwise
  nothing to promote, said in one line.

**When both could move, the lower step goes first.** Work still on this
session's feature branch lands on staging before anything moves into main,
even when staging is already ahead of main, unless the person named the
step. A later Promote carries it on into main.

A Promote that resolves to staging into main is the named go-ahead
[BestPractice's AGENTS.md](https://github.com/alex137/BestPractice/blob/staging/AGENTS.md)
asks for before main moves, since Morgan asked for exactly this; nobody is
asked again.

**When Claude Code's own safety check stops that move, say so and ask for
"Produce".** Its auto mode can refuse `--promote --to main` as a
production deploy (`[Production Deploy]`), because a bare "Promote" does
not name that exact action. The reply says in one line that **Claude
Code's safety check stopped it, not this repository's rules**, and asks
for **"Produce"** (or "Promote 5"). **Never work around the check** --
another command, the GitHub API, or a settings edit of the session's own.
The one durable fix is an `autoMode.allow` entry only the person can add
([gotcha](https://github.com/alex137/BestPractice/blob/staging/gotchas/gotcha-2026-09-30-auto-mode-refuses-a-bare-promote-into-main-as-a-production.md)).

**Never recommend a Promote that another window is already running.**
When a Promote finds the lock held, or the reply gate reports one under way,
no reply suggests promoting that repository again -- not as a next step,
not as a plain line in The Boildown, not as "try again later". It says, at
most, that one is running, and which session holds it when that can be told
(Morgan, 2026-09-27, strength: decided: *"NEVER recommend a promote when
another session is already doing it!!!"*).

**Waiting for a Promote never keeps a session open.** Work on staging is
already on `origin`, and any later session can take it into main, so a
pending Produce is never a reason for "Don't archive this session" unless
there is a genuinely urgent reason to move it now
([the-boildown-on-the-ladder](the-boildown-on-the-ladder.md)).

**Save first, then move.** Work still sitting in the session would
otherwise miss the move the person just asked for (Morgan, 2026-09-25,
strength: decided; his words are in the Story). Nothing to save means
nothing to do there: go straight to the next step.

The commands do the whole move, and a session adds nothing to them:

0. **The Promote lock**, so only one window moves a tier at a time. The
   lock is the branch `data-promote-lock` on origin
   (`precedent-promote-lock` in a repository that has not moved to the
   ladder's data-branch names, [data-branch-names](data-branch-names.md)),
   which only ever
   moves forward: one empty `[skip ci]` commit per claim or release, the
   newest one saying who holds it. **If another window holds it, a Promote
   does nothing** and says so -- *"another window is promoting right
   now"* -- and that is the whole report: don't Promote again while it
   runs, and don't suggest it either. A landing (`--land`) waits its turn
   for the same lock instead, and refuses only if it is still held after
   the wait. A claim left by a window that died frees itself after 15
   minutes. The branch is never deleted (a session can't), and it is not
   unlanded work or a branch to tidy up. **The merge gate takes the same
   lock** while it checks a pull request into staging or main
   (`hold_for_landing`; Alex, 2026-09-30: *"Do all three recs"*, strength:
   decided), so a Promote and a landing never move a tier under each
   other's check: whichever finds it held waits, and a claim naming
   "landing pull request #N" is a landing, not a Promote. The gate frees
   the lock when its check ends, a few seconds before GitHub merges, so it
   checks again after the merge: when the tier moved in those seconds and
   what landed fails, it reverts the merge, putting the tier back to the
   tree the other window landed.
1. **Booked (`--land BRANCH`) composes one tree, by merge commits, in a
   throwaway worktree**: staging, then what reached main directly, then
   the work -- never a fast-forward. People off the ladder push straight to
   main, so every landing brings their work into staging with it. It
   **rebuilds the generated files** (a map, an index, a rendered page) main
   left stale with their own generators, since a source edited off the
   ladder whose render nobody rebuilt is the commonest way main goes red.
   It runs **the quick checks** on the change, and only if they pass pushes
   staging to that commit, never forced, so a staging that moved meanwhile
   refuses the push and nothing is lost. A conflict in hand-written text
   moves nothing: merge `origin/staging` and `origin/main` into the
   branch, resolve it there, push, and land again. Main is never touched.
   It ends `LAND RESULT: ...`.
2. **Debut (`--run-tests`) runs the full local suite on staging**, with
   main's direct work, and moves nothing. Its result is recorded for the
   move into main: 0 passed, 1 failed ([debut](debut.md)).
3. **Produce (`--promote --to main`) moves staging into main**, the short
   way unless the person asks for the long one ([produce](produce.md)).
   **No full run is repeated on files that already passed it.** When the
   full suite already passed on exactly these files, that result stands
   and nothing is re-run, **whichever window ran it**: a pass is shared
   through origin. "Exactly" is the whole condition: one changed character
   anywhere, including a push made straight to staging in between, and the
   suite runs. It is what the files are that decides, never which branch
   they came from. **It says which happened**: "NOT re-run", with when the
   earlier run passed, or how long the run it just did took.

**Staging into main is the fast move unless the person asks for the full
one** ([produce](produce.md), Morgan, 2026-10-11): quick checks, the copy,
merged at once, GitHub's test after. **The long one, only on the person's
own words (`--full --because '<their words>'`), runs the full check** on
staging merged into main (standing on an earlier pass of the same files,
as above). **It waits while main's own GitHub test is running, and is held
while that test is failing** -- unless staging already carries main's
failing tip and staging's tip has passed the full local check, which a
Debut gives it: then this Produce is what brings main back to green, and
goes ahead (Morgan, 2026-10-03, strength: decided). It then pushes a
throwaway copy of staging, `DATE-promote-to-main-ID`, and stops: the tool
never moves main. **That stop exits 3, not 0**, and its block opens with
*"MAIN HAS NOT MOVED YET"*: exit 0 from Promote means the branch it names
has moved, so a 3 means the work below is still owed (2026-09-28: a
session read the old exit 0 as done while main had not moved). The session
opens the pull request from that copy into main, waits for its GitHub test
-- main's last gate -- with
`python3 tools/precedent_branches.py --wait-main-test COPY` (exit 0 only on
a pass; never a poller of the session's own, since one crashed mid-wait on
2026-09-27), and merges it with a merge commit. Report the copy, the pull
request and the merge, and confirm with a fetch that `origin/main` carries
staging's tip.

**In a private repository the GitHub test runs at most once every
`github_ci_every_hours`** (since 2026-10-01,
[spec/CI_CADENCE_PLAN.md](https://github.com/alex137/BestPractice/blob/staging/spec/CI_CADENCE_PLAN.md), "Promote decides").
Promote reads the person's value first, then the repository's, and when the
test passed more recently than that it names the copy
`DATE-promote-to-main-not-due-ID`: the light check skips that pull request before a
runner starts, and `--wait-main-test` says **NOT DUE** and exits 0. On the
short way, the full local suite then runs on `main` after the merge
([produce](produce.md)); on the long way, the full local check before it
stands in. It runs anyway after a failed run until one
passes, when GitHub cannot be asked, and with `PRECEDENT_CI_NOW=1`; a
change to a workflow or the vendored engine is not forced. In a private
repository nothing but a due Promote copy runs the test: a pull request
into main from any other branch is skipped. **The repository's own
`github_ci_main_test` has the final say** ("individual", "never",
"always" or a number of hours); under "always" GitHub tests the push to
main after the merge, never the pull request, and Promote says so. Say which it was -- due or not due, and the line
Promote printed for why -- in the report.

**Main takes staging by a pull request from a throwaway copy, never from
staging itself.** A merged pull request's page offers to delete its
source branch, and on 2026-09-26 staging, the source of the pull request
into main, was deleted right after that merge -- by what, is not
established ([the gotcha](https://github.com/alex137/BestPractice/blob/staging/gotchas/gotcha-2026-09-26-a-pull-request-from-staging-deletes-staging.md)).
Promote makes that copy itself; the merge gate refuses a pull request
from a tier branch.

**Report what it printed, plainly**: what moved and whether a full check
ran or stood from an earlier run, or -- on `LAND REFUSED` or
`PROMOTE REFUSED` -- the failing check and what it was run on. A refusal
is fixed on a feature branch, landed on staging by Booked, and promoted
again; never by pushing the work to a tier some other way. When another
window moved the same work while this one was checking it, the tool says
so and exits cleanly, and that is the whole report: the work has moved,
and there is nothing to run again.

**Never suggest a Promote that another session is already running**, and
the same goes for Booked (`Go update`) or a merge of the same pull request or the
same work: two windows doing one job race, and the loser throws away a full
check run. Before recommending one, look -- the pull request's state, the
branch tips, and any session this one knows is on the same work -- and when
another session has it, say that it does, not that the person should do it
again (Morgan, 2026-09-25, after two sessions promoted the same batch at
once: *"you should NEVER suggest to \"promote\" or \"go update\" or
\"merge\" when another session is already doing that with the same
PR/thing"*, strength: decided).

**A full run takes as long as the suite does** -- minutes in this
repository -- so run a Debut, or Produce's long way, with a long timeout
or in the background, and keep working; nothing moves until it is done,
and nothing else waits on it.

**Not practice promotion.** Moving a practice *candidate* into the
catalogue is also called promotion, and a message about a candidate or a
practice means that step, which has its own tool. This command is about
branches, never a practice.

## Why
Booked lands on staging in seconds, with checks only on what changed, so
many windows can save at once without waiting on one another. The full
suite is still there: on request, as a Debut on staging, and after a
Produce, as GitHub's test on main, or the full local suite when that test
is not due. That trade is only safe because
each command checks the exact commit it pushes, and pushes by itself: a
move that could push without its check, or a check that could pass one
commit and push another, would turn the saving into a hole.

## Story
Morgan, 2026-09-25, in a brainstorm about why saving had gone from a second
to twenty minutes once the local checks came back: work from eight windows
at once into one branch with only the fastest check, and pay for the full
suite once, from a background window, when the batch moves on. He ruled out
a scheduled promotion in favour of a push a person starts. The plan, with
the decisions and how firmly each was made, is
[spec/BRANCH_TIERS_PLAN.md](https://github.com/alex137/BestPractice/blob/staging/spec/BRANCH_TIERS_PLAN.md).
That one branch was `pre-staging`, beneath staging, and the Rule's Why
then read: *"Pre-staging exists so that many windows can save in seconds:
a push there gets only the basic check. That trade is only safe because
every commit still gets the full check before it reaches staging, and this
is where it gets it -- once per batch rather than once per window, which
is the whole saving."*

The same day he set the order of saving and promoting: *"If there is
anything in that session's branch that is not yet committed, to first do a
'go update' [which go into pre-staging] before starting the 'promote'"*
(strength: decided). The save-first rule still holds; Booked now lands on
staging.

**The one-line summary named the check loosely until 2026-09-26.** It said
"the full check", and Morgan asked whether that meant the check of the
branch the work enters. It always did -- the Rule above runs staging's
checks into staging and main's into main -- so only the summary changed, to
say so.

**2026-09-26: Promote picks its own step.** Morgan: *"Promote should
decide based on the context and ... what branch we were just working on.
If the promotion should be pre-staging to staging or staging to main ... it
should print that explicitly on the screen"* (strength: decided). The same
day, on a Promote that could mean either: *"if my 'promote' is ambiguous
and you don't know which of the two types of promotion it should refer to -
then choose to do pre-staging to staging"* (strength: decided). Both moves
were `--promote`: pre-staging into staging with the full local check, then
staging into main. The lower-step-first rule above is what that ambiguity
rule became with two tiers.

**2026-10-03: main's work composed into every move.** Until then a Promote
copied down into pre-staging what had reached staging by another route,
once checked, and held main's own new work out of it; from this day main's
work came down only inside a Promote, composed with everything else and
checked once, so pre-staging only ever received a tree that passed (Morgan,
strength: decided). The Promote then moved staging and pre-staging to the
same commit in one push. Booked's `--land` composes the same way today.

**2026-10-06: a Promote's branches named like a session's.** Morgan, reading a fix branch named `promote-fix-20261006T165108-0300` in a reply: *"isn't our URL format for temporary GitHub repo URLs to start with the timestamps then the slug then a few random characters? ... let's do that"*. The fix branch and the copy of staging are named by [tools/precedent_branch_name.py](../tools/precedent_branch_name.py) now, like every temporary branch; the old `promote-fix-DATE` and `to-main-DATE` names are still recognized, and a repository whose GitHub test knows only those keeps getting them until Update Vendors brings the new workflow. strength: decided.

**Debut is optional**, 2026-10-11. With work landed straight on staging,
a session called the next step "Debut, staging into main". Morgan
corrected it: staging into main is Produce, and Debut is an optional step
in the middle to test it.

**2026-10-14: pre-staging retired for everyone** (Morgan: *"Only me, go
ahead and plan it. Retire pre-staging."*, strength: decided). From
2026-10-09 repositories had moved off it one at a time, and the stages
read each repository's own landing branch until the last had moved
(ladder-in-a-repo-on-staging, now retired). With its only user deciding,
the ladder became two tiers for everyone: Booked lands on staging, Debut
only tests, Produce moves staging into main. "Pre-staging" left this
practice's `defines:`. The engine reads a leftover `pre-staging` setting
as staging, and Update Vendors moves a repository still carrying the
branch onto staging. Until this day the Install also named the harness
cases `check_promote_pre_staging` and
`check_sync_copies_work_from_above_once_checked`, which pinned the move
into staging and the copy down into pre-staging.

## Install
Nothing to install beyond the engine: [precedent_branches.py](../tools/precedent_branches.py) ships in
every kind's engine files. Its behaviour is pinned by [verify_harness.py](https://github.com/alex137/BestPractice/blob/staging/tools/verify_harness.py)'s
`check_landing_on_staging_run_tests_and_fast_move_into_main` -- landing on
staging, the tests that move nothing, and the fast move into main -- and
by `check_landers_wait_their_turn_for_the_lock`.

`checked_by` is null because the only thing left to check is whether a
session ran the command when it was asked to, and nothing in a tree
records that; what the command does once run is the harness cases above.
