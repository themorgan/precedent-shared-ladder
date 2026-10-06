---
slug:        debut
title:       "\"Debut\" is stage 4: move pre-staging into staging, with the full checks"
tier:        on-demand
severity:    default
applies_to:  ["**"]
applies_to_why: "A phrase in a MESSAGE (\"Debut\", \"Promote 4\") -- stage 4, a Promote with the step named, like promote's entry. Routed by the `merge` gate. Decided: 2026-09-29, when the practice landed."
occasion:    "a person says \"Promote\", \"Promote N\" or a stage word (\"Consider\", \"Act\", \"Debut\", \"Produce\", \"Make live\"), or asks to plan, build or move work up a tier"
gates:       ["merge"]
gates_why:   "Debut and Produce are merges between branch tiers -- the moment that gate exists for, as for promote."
index_clause: "stage 4: pre-staging into staging, full checks"
checked_by:  null
defines:     ["Debut", "Test Readiness"]
command:     {"Debut": "Stage 4 (Promote 4), also called Test Readiness: move pre-staging into staging, with the full local checks, saying so first -- saving this session's own work to pre-staging first if it is not there yet. It takes in whatever reached main without the ladder, checks that and pre-staging together once, and moves staging and pre-staging level; when that check fails, whoever's commit broke it, the session fixes it in the same turn on the fix branch the Debut names and runs it again."}
status:      active
in_force_at: null
visible_to:  code-owners
supersedes:  []
overrides:   null
added:       "2026-10-02"
approved_by: "Morgan F, 2026-10-02, withdrawn from the universal set BestPractice, which keeps no copy (there: Morgan, 2026-09-27 -- stage 4 of the five stages, \"Debut (Test Readiness: To Staging)\")"
strength:    decided
---
## Rule
**Debut is step 4 of the five-stage ladder ([promote](promote.md)): a
Promote from pre-staging into staging.** It runs exactly what
[Promote](promote.md) runs with the step named:

    python3 tools/precedent_branches.py --promote --to staging --work BRANCH

([tools/precedent_branches.py](https://github.com/alex137/BestPractice/blob/staging/tools/precedent_branches.py)), and everything Promote says holds:
the lock, the full local check on the batch, nothing moving unless it
passes. Work still on this session's feature branch goes through
[Booked](go-update.md) first, and the read-back names both stages.

**A Debut takes in what reached main without the ladder, and moves both
tiers.** People off the ladder push straight to main, and that goes on. So
a Debut builds one tree -- staging, then main's new work, then
pre-staging -- rebuilds the generated files main left stale, runs the full
check on it once, and only then moves staging and pre-staging to that same
commit (Morgan, 2026-10-03, strength: decided).

**When that check fails or the merge conflicts, nothing moves, and the
session finishes it in the same turn, whoever's commit broke it** -- main's
included, never "main is not mine" and never deferred (Morgan, 2026-10-03:
*"if it fails because of a problem on main (caused by someone not using
this process) -- then you have to fix it as part of this process"*,
strength: decided). The Debut leaves the tree it checked on a
local `promote-fix-DATE` branch (pushed only with a fix, since 2026-10-06) and says what failed, naming main's commits as
the place to look first. Run what failed on each tip to see which side
brought it, fix it on that branch, run every step once (`## Detail`),
push, and Debut again with `--work promote-fix-DATE`: that takes the fix in
first and finishes. A fix to the session's own booked work may go through
Booked instead, as before (Morgan, 2026-10-01, strength: assented).

**Where a repository has no pre-staging** -- a person who lands on staging
-- Debut has nothing to do, and says so.

## Detail
A refusal shows only part of what is wrong: the push check stops at its
first failing step, and a test that crashes takes the rest of its batch
down with it. So after fixing what it named, on the fix branch, run:

    PRECEDENT_PUSH_CHECK_ALL=1 python3 tools/precedent_push_check.py --tier full --because "a Debut was refused"

Fix all of what that finds, push it to the fix branch, and Debut again:

    python3 tools/precedent_branches.py --promote --to staging --work promote-fix-DATE

The next Debut reuses that pass for the same files rather than running it
a second time. A conflict in hand-written text is the same route: the
Debut names the merge to make on the fix branch (`git merge SHA`), and the
session resolves it there. Only a `promote-fix-` branch is taken in this
way; any other `--work` that is not on pre-staging is named and left for
Booked.

The fix branch has done its job once the Debut takes it in; it is never
deleted by a session, and the Debut's last lines link its branches page.

## Why
"Debut" names the step for what it means: the work's first appearance where
it is fully checked, ready to be judged for production.

## Story
Named 2026-09-27 with the rest of the ladder.

**2026-10-01: five Debuts for one batch.** A change booked earlier that
day broke tests only the full suite runs, and the refused Debuts turned
them up a few at a time: every refusal stopped at its first failing step,
and in the third a crashing test fixture took the rest of its batch down
with it. Each fix cost a booking and a Debut of about eight minutes. After
the fourth, a single run of every step came back clean, and the fifth Debut
reused it and passed. Run after the first refusal, it would have saved most
of those rounds.

**2026-10-03: main went red off the ladder.** Two commits pushed straight
to main left a generated page stale there, so main's own test failed. The
Debut of that day held main's work out until main passed, which waited on
someone who was not on the ladder, while pre-staging drifted further from
main and the next Produce was set to meet the conflict. Morgan's answer
was to compose main's work into every Debut, check it with the ladder's
own, fix any failure there and then, and move both tiers level.

## Install
Nothing new: the promotion tool and its checks are
[promote](promote.md)'s.
