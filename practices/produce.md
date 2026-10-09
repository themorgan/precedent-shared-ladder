---
slug:        produce
title:       "\"Produce\" is stage 5: move staging into main -- production -- fast, then watch GitHub's test"
tier:        on-demand
severity:    default
applies_to:  ["**"]
applies_to_why: "A phrase in a MESSAGE (\"Produce\", \"Promote 5\") -- stage 5, a Promote with the step named, like promote's entry. Routed by the `merge` gate. Decided: 2026-09-29, when the practice landed."
occasion:    "a person says \"Promote\", \"Promote N\" or a stage word (\"Consider\", \"Act\", \"Debut\", \"Run tests\", \"Produce\", \"Make live\"), or asks to plan, build, test or move work up a tier"
gates:       ["merge"]
gates_why:   "Produce is the merge of staging into main -- the moment that gate exists for, as for promote."
index_clause: "stage 5: staging into main fast, then watch GitHub's test; read strictly"
checked_by:  null
defines:     ["Produce", "Make live", "production"]
command:     {"Produce": "Stage 5 (Promote 5): move staging into main -- production -- saying so first. It runs the quick checks, merges into main at once, and then waits on GitHub's full test, which runs right after the merge; if that test fails, the same session fixes main before it stops. If Run tests last failed on what staging holds now, it shows you those failures and asks once before going on. Here we graduate you from the practice to real-life production!", "Make live": "The same as **Produce**."}
status:      active
in_force_at: null
visible_to:  code-owners
supersedes:  []
overrides:   null
added:       "2026-10-02"
approved_by: "Morgan F, 2026-10-02, withdrawn from the universal set BestPractice, which keeps no copy (there: Morgan, 2026-09-28 -- \"the stage 5 word should be \\\"Produce\\\" to make it a verb like the previous ones\", with \"production\" kept as the noun for main; the session must read it in context, \"should not just do a simple grep for that exact word\"). Made fast on 2026-10-09, Morgan: \"Act on the ladder plan\" (spec/LADDER_REDESIGN_PLAN.md); on a failed Run tests it asks and never refuses -- \"often these tests fail for trivial reasons, and sometimes I really just need to push something to live quickly\""
strength:    decided
---
## Rule
**Produce is step 5 of the five-stage ladder ([promote](promote.md)): staging
into main.** `main` is **production** -- what everyone gets. A Produce is
the named go-ahead that merging into `main` needs, and it carries the fix
of a red `main` that follows it. It is always the fast move:

    python3 tools/precedent_branches.py --promote --to main --fast

([tools/precedent_branches.py](https://github.com/alex137/BestPractice/blob/staging/tools/precedent_branches.py)).
Work still on the session's feature branch goes through
[Booked](go-update.md) first, and the read-back names both stages.

**1. Quick checks, then the copy.** The tool runs the quick checks on
staging merged into main, so nothing that reached main directly is dropped
or overwritten, and pushes a throwaway copy for the pull request. It exits
3 -- *"MAIN HAS NOT MOVED YET"* -- and prints the copy's full 40-character
head commit.

**2. Merge at once.** Open the pull request from that copy into `main`
(never from staging itself), and merge it straight away with a merge
commit, at exactly the printed head (`expectedHeadSha`). Do not wait for
GitHub's test first. Confirm with a fetch that `origin/main` carries it.

**3. Then watch GitHub's test, and fix a red `main` in the same sitting.**

    python3 tools/precedent_branches.py --wait-main-test COPY

waits for GitHub's full test, which runs right after the merge (about ten
minutes). A pass ends the Produce. A failure is this session's to fix
before it stops, whoever's commit caused it: on a feature branch, landed
on staging with Booked, and produced again; the person's Produce is the
authorization for that fix, and nobody is asked again. If the session
cannot finish it, the failure is not lost: GitHub's test opens an issue
labelled `main-test-failed` (or adds to the open one), the next session in
that repository lists it first and fixes it before other work, and Update
Vendors everywhere keeps taking the last `main` that passed until the fix
lands. Say which of these happened, in one line.

**A failed Run tests asks once, and never refuses.** When the last
[Run tests](debut.md) failed on exactly the commit staging is at, the tool
lists the failures, exits 4, and prints a question. Ask the person in those
words: *"Run tests found N failure(s) on staging (above). GitHub runs the
same tests after the merge, so a real one turns main red until it is
fixed. Run the move anyway? Say yes to continue."* On a yes, run it again
with `--despite-failed-tests`. A Run tests result on an older commit is
reported as stale and asks nothing.

**Read it strictly.** "Produce", "production" and "make live" all occur in
ordinary sentences, and this is the step that changes what everyone gets.
It fires only when the message is plainly asking for this step; where the
reading is a genuine judgment call, say it out loud and confirm before
anything moves.

**If Claude Code's own safety check refuses it anyway, stop.** Say in one
line that Claude Code's auto mode stopped the move, not this repository's
rules, and ask for it again in words that name the move ("Produce: staging
into main"). Never route around the check; the durable fix is the person's
([gotcha](https://github.com/alex137/BestPractice/blob/staging/gotchas/gotcha-2026-09-30-auto-mode-refuses-a-bare-promote-into-main-as-a-production.md)).

## Why
The last step needs a word that is a verb like the others and has the "go
live" feel without "launch", which is common in tech and usually means
something much bigger. A theater production fits the ladder's metaphor.

## Story
Named 2026-09-28. The first word was "Picked up", which is ordinary coding
talk ("CI picked up the change"); "Production" followed, and became the
verb "Produce" so every stage reads as something to do.

**2026-10-09: Produce made fast.** Until then a Produce ran the full local
suite and waited on GitHub's test before merging, and with Debut's own run
before it, one batch took the same suite two or three times: two small
urgent fixes were quoted 90 minutes to reach main. Morgan approved the
ladder redesign plan that day ("Act on the ladder plan",
`spec/LADDER_REDESIGN_PLAN.md`): quick
checks, merge at once, GitHub's test straight after, a red main fixed in
the same sitting, and Update Vendors taking only a main that passed. On a
failed Run tests it asks and never refuses, since telling a trivial failure
from a real one by machine would mean sorting more than 600 tests by hand.

## Install
Nothing new: the fast move (`--fast`, `--despite-failed-tests`,
`--wait-main-test`) ships in the engine's
[precedent_branches.py](../tools/precedent_branches.py), with
[promote](promote.md)'s tool.
