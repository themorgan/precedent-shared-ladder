---
slug:        actions-minutes-are-scarce
title:       GitHub Actions minutes are scarce -- every job is a cost, designed down from the start
tier:        on-demand
severity:    default
applies_to:  []
occasion:    "GitHub Actions comes up -- its minutes, billing or spend, or a workflow written, reviewed or pushed to"
gates:       []
index_clause: "count jobs: one per trigger, none without a change, checks run in the session"
checked_by:  null
defines:     []
status:      active
in_force_at: null
supersedes:  []
overrides:   null
added:       "2026-10-19"
approved_by: "Morgan F, 2026-10-19, moved from an individual set (there: Morgan F, 2026-09-25); reworded 2026-10-31 to speak of the person who brings this set rather than in one person's voice, meaning unchanged, by the session under Morgan F's approval of that day (\"do your recommendations for all\", strength: assented)"
strength:    decided
---
## Rule
**GitHub Actions minutes are scarce, and the person pays for every one of them.** A
workflow that runs when it did not need to is a defect, the same as a bug.
It is never a harmless convenience. **Every workflow, and every piece of
work that will push to a repo that has workflows, is designed to minimize
minutes from the first commit.** Don't retrofit it after the bill arrives.
How to answer the person when they raise the cost is
`cost-concern-face-value`. This rule is about
not giving them the reason to raise it.

**Count jobs, not seconds.** GitHub bills each job rounded **up to a whole
minute** (as of 2026-09). A job that runs for one second costs a minute. So
does a job that runs for fifty-nine. Ten one-second jobs cost ten minutes.
Making a job faster saves nothing. Running fewer jobs is the only saving.

**Before adding or changing a workflow, say what it will cost:** how many
jobs each trigger starts, how often each trigger fires, and what that comes
to in a normal week and on a heavy build day. If you can't say, you haven't
designed it yet.

**The models, to use from the start:**

1. **One job, many steps.** Tasks that run at the same time go in **one
   job** as separate steps: steps are free, jobs are not. Several jobs in
   one workflow still bill as several minutes, and several `cron:` lines
   in one workflow still start several runs. **So "can several crons or
   actions be one?" means: can they be steps of one job on one trigger?**
   Usually yes. A scheduling repository's weekly sync and its UPCOMING_HOLIDAYS.md
   regeneration were two Monday jobs; they are now one.
2. **Nothing runs without a change.** If a run would have nothing to do,
   it must not start. Narrow `paths:` to the files the job actually reads.
   Trigger on the change itself, never on a clock that checks for one.
   Never regenerate an output on pushes that can't change it. A job that
   starts, finds nothing to do and exits has already cost a minute.
3. **Checks run in the session, not in Actions.** Unit tests, lint and doc
   checks run in the working session before it pushes (the deep check).
   Repeating them on every push and pull request pays twice for one answer.
   Actions runs a check only when Actions is the only place it can run: it
   needs a secret the session doesn't hold, or a runtime the session can't
   reproduce. Even then it is **button-only**.
4. **Probes and live tests are button-only.** A workflow that tests against
   a real service is `workflow_dispatch` and nothing else, never `push` on
   working branches. The session whose change needs it starts it by hand,
   from the Actions tab or the workflow-dispatch API, once, when the
   change is ready.

**And during the work itself:**

- **A pull request can double the bill**: its `pull_request` run, then the
  `push` run on `main` after the merge. Where the repo's merge rule allows
  a direct push, that is the cheaper path.
- **Batch pushes on a build day.** Don't push every small fix mid-iteration
  to a branch whose pushes start workflows. Push when a piece is done.
- **Look after a burst.** After a day of heavy pushing, read the repo's run
  list and count the jobs. Don't estimate. A trigger firing more than you
  expected is a bug to fix the same day.

## Story
A scheduling repository's build day, 2026-09-24, ran **about ninety Actions jobs in
one day**. None of the ones checked ran longer than 34 seconds, and every
one of them billed a full minute. Almost none were the product doing its
job:

- Unit tests on every push and pull request: 30.
- The BestPractice light check: 25.
- Google and Basecamp probes and live tests, starting on every
  working-branch push: 19.
- UPCOMING_HOLIDAYS.md regeneration on every code push: 9.
- The sync itself, mostly manual test runs: 7.

The next day, four cuts went in (the scheduling repository's pull request), and they are the
four models above. The regeneration moved into the sync's own job. The unit
tests and the old regeneration workflow were paused, since the session runs
the tests before every push anyway. The probes and target tests lost their
push triggers. The recurring cost went to **one minute a week**, plus one
for each config change merged to `main`. That is the floor for a weekly job
with no server. Everything above it had been designed in by default and had
to be taken out by hand.

2026-10-31: the rule still spoke in the first person ("I pay", "answer me")
twelve days after it moved here from an individual set. The very
deep check of 2026-10-30 found it, and the session reworded it to
speak of the person who brings this set, under Morgan's approval of
2026-10-31 ("do your recommendations for all", strength:
assented). The meaning is unchanged; quoted words stay as they
were said.
