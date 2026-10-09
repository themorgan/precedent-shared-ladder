---
slug:        debut
title:       "\"Debut\" (\"Run tests\") is stage 4, optional: the full local suite on staging, moving nothing"
tier:        on-demand
severity:    default
applies_to:  ["**"]
applies_to_why: "A phrase in a MESSAGE (\"Run tests\", \"Debut\", \"Promote 4\") -- stage 4, named like promote's entry. Routed by the `merge` gate, beside the moves it can come before. Decided: 2026-09-29, when the practice landed; kept on 2026-10-09, when stage 4 stopped being a move."
occasion:    "a person says \"Promote\", \"Promote N\" or a stage word (\"Consider\", \"Act\", \"Debut\", \"Run tests\", \"Produce\", \"Make live\"), or asks to plan, build, test or move work up a tier"
gates:       ["merge"]
gates_why:   "Run tests is the full check a person can ask for before Produce, the merge into main; it loads with the moves it can come before."
index_clause: "stage 4, optional: Run tests -- the full local suite on staging, moving nothing"
checked_by:  null
defines:     ["Run tests", "Debut", "Test Readiness"]
command:     {"Run tests": "Stage 4 (Promote 4), optional: run the full local test suite on staging, with whatever reached main directly brought in the same way a landing brings it, and move nothing. About ten minutes. It tells you what failed, if anything; a Produce afterwards shows those failures and asks once before going on.", "Debut": "The same as **Run tests** (stage 4). Until 2026-10-09 it moved pre-staging into staging; it no longer moves anything.", "Test Readiness": "The same as **Run tests**."}
status:      active
in_force_at: null
visible_to:  code-owners
supersedes:  []
overrides:   null
added:       "2026-10-02"
approved_by: "Morgan F, 2026-10-02, withdrawn from the universal set BestPractice, which keeps no copy (there: Morgan, 2026-09-27 -- stage 4 of the five stages, \"Debut (Test Readiness: To Staging)\"). Rewritten 2026-10-09 to the ladder redesign plan, Morgan: \"Act on the ladder plan\", with its decisions -- \"Debut\" kept as another word for \"Run tests\", which makes Debut the optional stage, and the numbering kept (spec/LADDER_REDESIGN_PLAN.md)"
strength:    decided
---
## Rule
**Run tests is step 4 of the five-stage ladder ([promote](promote.md)), and
it is optional. "Debut", "Test Readiness" and "Promote 4" mean the same.**
It runs the full local test suite on staging and moves nothing:

    python3 tools/precedent_branches.py --run-tests

([tools/precedent_branches.py](https://github.com/alex137/BestPractice/blob/staging/tools/precedent_branches.py)).
With no branch named it tests the person's landing branch, staging. It
builds the same tree a landing builds -- staging, then whatever reached
main directly -- in a throwaway worktree, runs the full push check on it
once, and records the result for the move into main. Its last line is
`RUN TESTS RESULT: ...`; it exits 0 on a pass and 1 on a failure. About ten
minutes.

**Nothing waits for it.** Booked lands work on staging with the quick
checks, and [Produce](produce.md) moves staging into main with the quick
checks too; GitHub's full test runs right after that merge. Run tests is
the slow, careful version a person asks for when they want the batch fully
tested on their machine before it goes live. A bare Promote never runs it
on its own, and nothing refuses for want of it.

**A failure is reported, never fixed into a refusal.** Say what failed, in
plain words, one line per failing check. When the person goes on to
Produce, the move shows those failures again and asks once (see
[produce](produce.md)); a failed Run tests never blocks it. A failure the
session can fix is fixed the ordinary way: on a feature branch, then
Booked.

**Read it back like any stage**: *"Now Promote 4: Run tests (Debut) -- the
full local suite on staging, moving nothing (BestPractice)."*

**Where a person still lands on pre-staging**, the old Debut, the move from
pre-staging into staging with the full check, is still what
`python3 tools/precedent_branches.py --promote --to staging` does
([promote](promote.md)). It is the way an unconverted repository empties
pre-staging before Update Vendors retires it.

## Detail
The full check stops at its first failing step, so one run can hide a
second failure behind the first. To see all of them at once on a fix
branch:

    PRECEDENT_PUSH_CHECK_ALL=1 python3 tools/precedent_push_check.py --tier full --because "Run tests failed"

The result Run tests records is for staging's commit at the time. Once
staging moves, a Produce reports the old result as stale and does not ask
about it.

## Why
"Debut" named the work's first appearance where it was fully checked.
Since 2026-10-09 the full check is something a person asks for rather than
a gate every batch waits on, so the word stays and names that check.

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

**2026-10-09: Debut stops being a move.** Two small urgent fixes were
quoted 90 minutes to reach main by the ladder, about half of it the full
suite run locally at Debut and again on GitHub at Produce. Morgan approved
the ladder redesign plan the same day ("Act on the ladder plan"): Booked
lands on staging, Produce is fast and GitHub's test runs after the merge,
and "Debut" is kept as another word for "Run tests", which makes it the
optional stage. pre-staging is no longer used
(`spec/LADDER_REDESIGN_PLAN.md`).

## Install
Nothing new: `--run-tests` ships in the engine's
[precedent_branches.py](../tools/precedent_branches.py), with
[promote](promote.md)'s tool.
