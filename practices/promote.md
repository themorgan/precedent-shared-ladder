---
slug:        promote
title:       "\"Promote\" does the next stage the work needs and says which first; \"Promote N\" does stage N of the five-stage ladder"
tier:        on-demand
severity:    default
applies_to:  ["**"]
applies_to_why: "A phrase in a MESSAGE, like go-update's and push-directly's entries -- no file path reaches it. Routed by the `merge` gate. Decided: 2026-09-25, when the practice landed."
occasion:    "a person says \"Promote\", \"Promote N\" or a stage word (\"Consider\", \"Act\", \"Debut\", \"Run tests\", \"Produce\", \"Make live\"), or asks to plan, build, test or move work up a tier"
gates:       ["merge"]
gates_why:   "Promote is a merge between branch tiers -- staging into main, or pre-staging into staging for anyone still on it -- the moment that gate exists for."
index_clause: "the next tier up, chosen from the work and said first; \"Promote N\" does stage N"
checked_by:  null
defines:     ["Promote", "pre-staging", "Promote N", "Graduate", "the five stages"]
command:     {"Promote": "Do the next stage this work needs, saying which before it starts: land this session's unsaved work on your landing branch first (staging, for anyone on the ladder), then move staging into main with the quick checks, merge at once, and watch GitHub's test after the merge. Where pre-staging still holds work, it moves that into staging first. \"Promote N\" does stage N of the five-stage ladder: 1 Consider, 2 Act, 3 Booked, 4 Run tests (Debut), 5 Produce."}
status:      active
in_force_at: null
supersedes:  []
overrides:   null
added:       "2026-10-02"
approved_by: "Morgan F, 2026-10-02, withdrawn from the universal set BestPractice, which keeps no copy (there: Morgan, 2026-09-27 (decided) -- never recommend a Promote another window is already running; Morgan, 2026-09-25 -- the three branch tiers are his own design (\"to prestaging only the most minimal test; to staging/precedent-beta-v01 all local tests; and then to main, you get all those local tests AND the most important GitHub test\", strength: decided), with promotion by a person rather than a schedule (\"I think that it should not be on a cron\", decided). The word itself was the session's recommendation, approved with the plan as a whole: \"Otherwise, this looks great, let's do it, go ahead, go update\". Not re-running the suite on files that already passed it is his rule too (Morgan, 2026-09-25: \"staging will not run the full suite of tests if it's being promoted from pre-staging to staging and the full suite of tests ran on pre-staging and nothing has changed\", strength: decided). Saving the session's own work with Go update before promoting is his rule too (Morgan, 2026-09-25, strength: decided). An ambiguous Promote -- both steps with work waiting -- moves pre-staging into staging (Morgan, 2026-09-26: \"if my 'promote' is ambiguous and you don't know which of the two types of promotion it should refer to - then choose to do pre-staging to staging\", strength: decided). \"Graduate\" as a second word for the same command is his too (Morgan, 2026-09-26: \"Let's add a new vocab word 'graduate' to be used as a synonym for 'promote'\", strength: decided); \"Promote N\" and the five stages, 2026-09-27/28 (spec/FIVE_STAGES_AND_OUR_LANGUAGE_PLAN.md, strength: decided).) Rewritten 2026-10-09 to the ladder redesign plan, Morgan: \"Act on the ladder plan\" -- Booked lands on staging, stage 4 becomes the optional Run tests (\"Debut\" kept as another word for it), Produce is fast with GitHub's test after the merge, the numbering stays, and reconciling with main stays as it was (\"make sure that staging doesn't change what it does now, in reconciling the versions sent directly to main with our staging\"; spec/LADDER_REDESIGN_PLAN.md)."
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
| 3 | **Booked** | Shared Save | Land it from the feature branch on the landing branch, staging, with the quick checks. Also **Go update**, **Book it**. | [go-update](go-update.md) |
| 4 | **Run tests** | Debut, Test Readiness | Optional: the full local suite on staging, moving nothing. | [debut](debut.md) |
| 5 | **Produce** | Make live | Staging into main -- production -- with the quick checks, merged at once; GitHub's full test runs right after, and a red main is fixed in the same sitting. | [produce](produce.md) |

The ladder is **optional for everyone**: anyone may use its words, nobody
has to, and a repository whose only branch is main simply has fewer stages.
**Since 2026-10-09 the ladder has no pre-staging** (Morgan, "Act on the
ladder plan", `spec/LADDER_REDESIGN_PLAN.md`):
Booked lands on staging, and staging is where finished work waits for
Produce. pre-staging stays a tier branch for anyone still on it, and is
never deleted by a session. A
person's own individual set may require it for them.

- **Read back every stage before it runs**, with its number, word and
  synonym and the repository and branches: *"Now Promote 5: Produce, Make
  live -- moving staging into main (BestPractice)."* A request
  covering several stages names them all: *"Now Promote 3 then 4: ..."*.
- **Read the request, never scan it for a word.** Every stage word is
  ordinary English. The same step can be asked for many ways -- "Debut",
  "Promote 5", "make it live", "move BestPractice staging to main" -- and a
  named step wins over any guess. Stage 5, which changes
  production, is read most strictly.
- **A bare Promote means the next step this work has not done, and never
  skips one** -- except Run tests, which is optional and never run unasked.
  Between possible moves, take the lowest: work on the feature branch means
  Booked first; work on staging that main lacks means Produce; work still
  on pre-staging means moving it into staging first (below). Asking for a
  higher stage runs the lower moves first, and a bare Promote never sends
  finished work back to Consider.
- **"Graduate" is another word for Promote.**

The rest of this Rule is the moves between branch tiers.

When a message says **"Promote"** about the branch tiers, **first check this
session's own branch for work that is not on the landing branch yet**:
anything uncommitted, or committed but not yet landed. **If there is any,
run [Booked](go-update.md) on it first** -- for anyone on the ladder that is

    python3 tools/precedent_branches.py --land BRANCH

which lands it on staging -- and confirm `origin/staging` carries it.
Promote carries that authorization itself: nobody is asked a second time
(Morgan, 2026-09-25: *"If there is anything in that session's branch that
is not yet committed, to first do a 'go update' ... before starting the
'promote'"*, strength: decided). Nothing to save means nothing to do here.

**Then the move into main is [Produce](produce.md):**

    python3 tools/precedent_branches.py --promote --to main --fast

quick checks, a throwaway copy of staging merged with main, a pull request
merged at once at the printed head, then GitHub's test watched with
`--wait-main-test COPY` and a red main fixed in the same sitting. The
reply opens with the line the tool prints first, *"Now promoting from
staging to main"*. A Promote that resolves to staging into main is the
named go-ahead
[BestPractice's AGENTS.md](https://github.com/alex137/BestPractice/blob/staging/AGENTS.md)
asks for before main moves, since the person asked for exactly this; nobody
is asked again.

**Reconciling with main never changes** (Morgan, 2026-10-09: *"make sure
that staging doesn't change what it does now, in reconciling the versions
sent directly to main with our staging"*). People off the ladder push
straight to main, and that goes on. Wherever work enters staging -- a
Booked by `--land`, a Run tests, the move from pre-staging -- the tool
builds staging, then main's direct commits, then the new work, each by a
merge commit, rebuilds the generated files main left stale, and checks
them together; and the copy for the pull request into main is staging
merged into main. Nothing that reached main directly is ever dropped or
overwritten. When that composition conflicts in hand-written text, nothing
moves, and the tool says what to merge and where.

**Where pre-staging still holds work** -- a person still landing there, or
a repository Update Vendors has not yet converted -- a bare Promote moves
it into staging first, the full-checked move this ladder used until
2026-10-09:

    python3 tools/precedent_branches.py --promote --to staging --work BRANCH

It takes the Promote lock, copies down what reached staging another way
once checked, composes staging, any `DATE-promote-fix-ID` branch handed in
with `--work`, main's direct work and pre-staging into one tree, runs the
full push check on it once (standing on an earlier pass of exactly the
same files, whichever window ran it), and only on a pass moves staging and
pre-staging to that commit in one push. A failure or conflict moves
neither and leaves the tree on a local `DATE-promote-fix-ID` branch; the
session fixes it there in the same turn, whoever's commit broke it, and
promotes again with `--work` that branch. **When both pre-staging and
staging have work waiting, a Promote with no step named moves pre-staging
into staging** (Morgan, 2026-09-26: *"if my 'promote' is ambiguous and you
don't know which of the two types of promotion it should refer to - then
choose to do pre-staging to staging"*, strength: decided).

**Without `--fast`, the move into main is the full one**, for anyone not on
the fast route: the full local check on staging merged into main, held
while main's own GitHub test is failing, then the copy, and the pull
request merged only after its GitHub test passes
(`--wait-main-test COPY`, exit 0 only on a pass). Both moves exit 3, not 0,
until main has moved, and their block opens with *"MAIN HAS NOT MOVED
YET"*: exit 0 means the branch moved (2026-09-28: a session read the old
exit 0 as done while main had not moved).

**The Promote lock.** Only one window moves a tier at a time. The lock is
the branch `precedent-promote-lock` on origin, which only ever moves
forward: one empty `[skip ci]` commit per claim or release, the newest one
saying who holds it. **If another window holds it, this Promote does
nothing** and says so -- *"another window is promoting right now"* -- and
that is the whole report. A claim left by a window that died frees itself
after 15 minutes. The branch is never deleted, and it is not unlanded work.
**The merge gate takes the same lock** while it checks a pull request into
staging or main (`hold_for_landing`; Alex, 2026-09-30: *"Do all three
recs"*, strength: decided), so a Promote and a landing never move a tier
under each other's check.

**When Claude Code's own safety check stops the move into main, say so and
ask for "Produce".** Its auto mode can refuse `--promote --to main` as a
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
another session is already doing it!!!"*). The same goes for Booked or a
merge of the same pull request or the same work: two windows doing one job
race, and the loser throws its work away (Morgan, 2026-09-25: *"you should
NEVER suggest to \"promote\" or \"go update\" or \"merge\" when another
session is already doing that with the same PR/thing"*, strength: decided).

**Waiting for a Produce never keeps a session open.** Work on staging is
already on `origin`, and any later session can move it, so a pending
Produce is never a reason for "Don't archive this session" unless there is
a genuinely urgent reason to move it now
([the-boildown-on-the-ladder](the-boildown-on-the-ladder.md)). A Produce
already merged is different: its session watches GitHub's test and fixes a
red main before it stops ([produce](produce.md)).

**In a private repository the GitHub test runs at most once every
`github_ci_every_hours`** (since 2026-10-01,
[spec/CI_CADENCE_PLAN.md](https://github.com/alex137/BestPractice/blob/staging/spec/CI_CADENCE_PLAN.md), "Promote decides").
When the test passed more recently than that, Promote names the copy
`DATE-promote-to-main-not-due-ID`: the light check skips that pull request
before a runner starts, and `--wait-main-test` says **NOT DUE** and exits 0.
**The repository's own `github_ci_main_test` has the final say**
("individual", "never", "always" or a number of hours); under "always"
GitHub tests the push to main after the merge, never the pull request, and
Promote says so. Say which it was, and the line Promote printed for why.

**Main takes staging by a pull request from a throwaway copy, never from
staging itself.** A merged pull request's page offers to delete its
source branch, and on 2026-09-26 staging, the source of the pull request
into main, was deleted right after that merge -- by what, is not
established ([the gotcha](https://github.com/alex137/BestPractice/blob/staging/gotchas/gotcha-2026-09-26-a-pull-request-from-staging-deletes-staging.md)).
Promote makes that copy itself; the merge gate refuses a pull request
from a tier branch.

**Report what it printed, plainly**: the commits moved and which checks
ran, or -- on `PROMOTE REFUSED` -- the failing check and the batch it was
run on. A refusal is fixed on a feature branch, landed with Booked, and
promoted again; never by pushing the batch onward some other way. When
another window moved the same batch meanwhile, Promote says so and exits
cleanly, and that is the whole report. Every Promote ends with one line,
`PROMOTE RESULT: <to> <- <from>: <verdict>`, and that line is what to read.

**Not practice promotion.** Moving a practice *candidate* into the
catalogue is also called promotion, and a message about a candidate or a
practice means that step, which has its own tool. This command is about
branches, never a practice.

## Why
Many windows land work in seconds because a landing gets only the quick
checks. Since 2026-10-09 the full check every batch gets is GitHub's, once,
right after the merge into main; the local one is Run tests, asked for when
wanted. That trade is safe because Update Vendors takes only a main whose
GitHub test passed, so a red main never reaches another repository, and
because the session that ran the Produce fixes it at once. The command
still checks the exact commit it pushes, and pushes by itself.

## Story
Morgan, 2026-09-25, in a brainstorm about why saving had gone from a second
to twenty minutes once the local checks came back: work from eight windows
at once into one branch with only the fastest check, and pay for the full
suite once, from a background window, when the batch moves on. He ruled out
a scheduled promotion in favour of a push a person starts. The plan, with
the decisions and how firmly each was made, is
[spec/BRANCH_TIERS_PLAN.md](https://github.com/alex137/BestPractice/blob/staging/spec/BRANCH_TIERS_PLAN.md).

**The one-line summary named the check loosely until 2026-09-26.** It said
"the full check", and Morgan asked whether that meant the check of the
branch the work enters. It always did -- the Rule above runs staging's
checks into staging and main's into main -- so only the summary changed, to
say so.

**2026-10-06: a Promote's branches named like a session's.** Morgan, reading a fix branch named `promote-fix-20261006T165108-0300` in a reply: *"isn't our URL format for temporary GitHub repo URLs to start with the timestamps then the slug then a few random characters? ... let's do that"*. The fix branch and the copy of staging are named by [tools/precedent_branch_name.py](../tools/precedent_branch_name.py) now, like every temporary branch; the old `promote-fix-DATE` and `to-main-DATE` names are still recognized, and a repository whose GitHub test knows only those keeps getting them until Update Vendors brings the new workflow. strength: decided.

**2026-10-09: the ladder loses pre-staging.** Two small urgent fixes were
quoted 90 minutes to reach main by the ladder, and the same fixes sent the
way Alex lands work reached main about two minutes after they were ready.
The ladder ran the same full suite two or three times for one batch.
Morgan approved the redesign that day ("Act on the ladder plan",
`spec/LADDER_REDESIGN_PLAN.md`): Booked
lands on staging, stage 4 becomes the optional Run tests, Produce merges
fast with GitHub's test after, and reconciling with main stays exactly as
it was. The move from pre-staging into staging stays in the Rule for
whoever is still on it.

## Install
Nothing to install beyond the engine: [precedent_branches.py](../tools/precedent_branches.py) ships in
every kind's engine files. Its behaviour is pinned by [verify_harness.py](https://github.com/alex137/BestPractice/blob/staging/tools/verify_harness.py)'s
`check_promote_pre_staging` -- a failing batch leaves staging where it was,
a passing one lands as a merge commit whose second parent is pre-staging,
and a conflicting direct push to staging stops the sync without pushing;
and by `check_sync_copies_work_from_above_once_checked` -- work from main or
staging is copied down only once checked, a failure is reported and never
copied, and merge commits that change no file are left alone.

`checked_by` is null because the only thing left to check is whether a
session ran the command when it was asked to, and nothing in a tree
records that; what the command does once run is the harness case above.
