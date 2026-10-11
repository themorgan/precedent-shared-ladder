---
slug:        produce
title:       "\"Produce\" is stage 5: move staging into main -- production"
tier:        on-demand
severity:    default
applies_to:  ["**"]
applies_to_why: "A phrase in a MESSAGE (\"Produce\", \"Promote 5\") -- stage 5, a Promote with the step named, like promote's entry. Routed by the `merge` gate. Decided: 2026-09-29, when the practice landed."
occasion:    "a person says \"Promote\", \"Promote N\" or a stage word (\"Consider\", \"Act\", \"Debut\", \"Produce\", \"Make live\"), or asks to plan, build or move work up a tier"
gates:       ["merge"]
gates_why:   "Debut and Produce are merges between branch tiers -- the moment that gate exists for, as for promote."
index_clause: "stage 5: staging into main (production); read strictly"
checked_by:  null
defines:     ["Produce", "Make live", "production"]
command:     {"Produce": "Stage 5 (Promote 5): move staging into main -- production -- with the quick checks, merging at once while GitHub's test runs after, saying so first; the full checks only when the person asks. Here we graduate you from the practice to real-life production!", "Make live": "The same as **Produce**."}
status:      active
in_force_at: null
visible_to:  code-owners
supersedes:  []
overrides:   null
added:       "2026-10-02"
approved_by: "Morgan F, 2026-10-02, withdrawn from the universal set BestPractice, which keeps no copy (there: Morgan, 2026-09-28 -- \"the stage 5 word should be \\\"Produce\\\" to make it a verb like the previous ones\", with \"production\" kept as the noun for main; the session must read it in context, \"should not just do a simple grep for that exact word\"); the fast move made the default, Morgan F, 2026-10-11 -- \"I think we should default to the fast route unless I explicitly agree to or request the slow route\""
strength:    decided
---
## Rule
**Produce is step 5 of the five-stage ladder ([promote](promote.md)): a
Promote from staging into main.** `main` is **production** -- what everyone
gets. It runs Promote with the step named:

    python3 tools/precedent_branches.py --promote --to main --work BRANCH

([tools/precedent_branches.py](https://github.com/alex137/BestPractice/blob/staging/tools/precedent_branches.py)).
**It is the fast move unless the person asks for the slow one**: the quick
checks, then the pull request it names is merged at once, and GitHub's test
runs after the merge (`--wait-main-test COPY`); a red `main` is fixed in
the same sitting. **The full local suite before the merge, with GitHub's
test waited on first, is `--full`, and only when the person agrees to or
asks for it** (Morgan, 2026-10-11). A Produce is the named go-ahead that
merging into `main` needs.

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

**2026-10-11.** The fast move into main had existed since 2026-10-09 but
sat behind a flag, and this rule still said "the full local check plus the
GitHub test". A session followed it word for word: the full suite ran
before the merge, failed on one stale test case, and the whole Produce took
most of an hour for a two-file change. Morgan: *"Why did you take the slow
route? I think we should default to the fast route unless I explicitly
agree to or request the slow route."* The tool's default changed the same
day, and so did this rule.

## Install
Nothing new: the promotion tool and its checks are
[promote](promote.md)'s.
