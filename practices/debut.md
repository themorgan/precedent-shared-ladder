---
slug:        debut
title:       "\"Debut\" is stage 4, and optional: run the full local tests on staging, and move nothing"
tier:        on-demand
severity:    default
applies_to:  ["**"]
applies_to_why: "A phrase in a MESSAGE (\"Debut\", \"Promote 4\") -- stage 4, a Promote with the step named, like promote's entry. Routed by the `merge` gate. Decided: 2026-09-29, when the practice landed."
occasion:    "a person says \"Promote\", \"Promote N\" or a stage word (\"Consider\", \"Act\", \"Debut\", \"Produce\", \"Make live\"), or asks to plan, build or move work up a tier"
gates:       ["merge"]
gates_why:   "Debut reads the tier Produce is about to move, and Produce is a merge between branch tiers -- the moment that gate exists for, as for promote."
index_clause: "stage 4, optional: the full local tests on staging; moves nothing"
checked_by:  null
defines:     ["Debut", "Test Readiness", "Run tests"]
command:     {"Debut": "Stage 4 (Promote 4), also called Test Readiness, and optional: run the full local tests on staging, with whatever reached main directly composed in, and move nothing -- saving this session's own work to staging first if it is not there yet. Produce reads the result. When the tests fail, whoever's commit broke them, the session fixes it in the same turn, lands the fix by Booked and runs them again.", "Run tests": "The same as **Debut**."}
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
**Debut is step 4 of the five-stage ladder ([promote](promote.md)), and it
is optional: run the full local tests on `staging`, and move nothing.**
"Run tests" asks for the same thing.

    python3 tools/precedent_branches.py --run-tests

([tools/precedent_branches.py](https://github.com/alex137/BestPractice/blob/staging/tools/precedent_branches.py))
It runs the full local suite on staging, with whatever reached main
directly composed in the way a landing would, records the result, and
ends with one `RUN TESTS RESULT: ...` line: exit 0 passed, 1 failed.
Nothing moves either way. Work still on this session's feature branch
goes through [Booked](go-update.md) first, and the read-back names both
stages: *"Now Promote 3 then 4: ..."*.

**Nobody has to run it.** Staging into main is always
[Produce](produce.md), with or without a Debut before it. What a Debut
buys is read by the Produce that follows: a failure on exactly this
staging commit makes Produce list the failures and ask once before it
moves anything; a pass on exactly this staging and main means nothing
needs to run after the merge; and while main's own GitHub test is
failing, a passing Debut on a staging that carries main's failing tip
lets the Produce go ahead and bring main back to green
([promote](promote.md)).

**When the tests fail, the session fixes them in the same turn, whoever's
commit broke it** -- main's included, never "main is not mine" and never
deferred (Morgan, 2026-10-03: *"if it fails because of a problem on main
(caused by someone not using this process) -- then you have to fix it as
part of this process"*, strength: decided). The run names the failing
checks. Run what failed on each tip to see which side brought it, fix it
on this session's feature branch, run every step once (`## Detail`), land
the fix by Booked, and Debut again.

## Detail
A failing run shows only part of what is wrong: the push check stops at
its first failing step, and a test that crashes takes the rest of its batch
down with it. So after fixing what it named, on the feature branch, run:

    PRECEDENT_PUSH_CHECK_ALL=1 python3 tools/precedent_push_check.py --tier full --because "a Debut failed"

Fix all of what that finds, land it by Booked, and Debut again. A conflict
with main's direct work shows up as a failing check named "merge with
main": merge `origin/main` into the feature branch, resolve it there, and
land it the same way.

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

**Until 2026-10-14 Debut was a move.** It was a Promote from pre-staging
into staging (`--promote --to staging --work BRANCH`): it took the
Promote lock, composed staging, main's new work and pre-staging in one
tree, ran the full check once, and moved staging and pre-staging to the
same commit only if it passed. A failure left the tree on a local
`DATE-promote-fix-ID` branch (an older `promote-fix-DATE` still counted),
fixed there and handed back with `--work`; a fix to the session's own
booked work could go through Booked instead (Morgan, 2026-10-01, strength:
assented). From 2026-10-09, in a repository already moved onto staging,
Debut only ran the tests there (ladder-in-a-repo-on-staging). On
2026-10-14 pre-staging was retired for everyone (Morgan: *"Only me, go
ahead and plan it. Retire pre-staging."*, strength: decided), so that
became Debut everywhere.

## Install
Nothing new: the tool and its checks are [promote](promote.md)'s, and
`--run-tests` is pinned by the engine's
`check_landing_on_staging_run_tests_and_fast_move_into_main`.
