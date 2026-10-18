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
approved_by: "Morgan F, 2026-10-02, withdrawn from the universal set BestPractice, which keeps no copy (there: Morgan, 2026-09-28 -- \"the stage 5 word should be \\\"Produce\\\" to make it a verb like the previous ones\", with \"production\" kept as the noun for main; the session must read it in context, \"should not just do a simple grep for that exact word\"); the fast move made the default, Morgan F, 2026-10-11 -- \"I think we should default to the fast route unless I explicitly agree to or request the slow route\", and checked: \"Add in the explicit and strong and checked, only do the long way when explicitly authorized otherwise the short way with the tests after pushing it\""
strength:    decided
---
## Rule
**Produce is step 5 of the five-stage ladder ([promote](promote.md)): a
Promote from staging into main.** `main` is **production** -- what everyone
gets. A Produce is the named go-ahead that merging into `main` needs.

**Take the short way, every time, unless the person asks for the long one:**

    python3 tools/precedent_branches.py --promote --to main --work BRANCH

([tools/precedent_branches.py](https://github.com/alex137/BestPractice/blob/staging/tools/precedent_branches.py))

1. **The quick checks** on what moves. If the last Debut ("Run tests")
   failed on exactly this staging commit, it lists the failures and asks
   once (exit 4); on a yes, run it again with `--despite-failed-tests`.
2. **It pushes a copy** of staging merged with main and stops (exit 3:
   main has not moved). Open the pull request from that copy into main and
   **merge it at once**, at the full head commit it prints. Never wait for
   a test first.
3. **The tests run after the merge**, and the Produce says which:
   - **GitHub's test, when it is due.** Wait on it with
     `--wait-main-test COPY`. A red `main` is fixed in the same sitting,
     **straight into `main`**: a branch named by
     `python3 tools/precedent_branch_name.py fix main WORDS`, cut from
     `main`'s tip, and a pull request from it into `main` -- the one pull
     request into `main` that does not come from staging (Morgan,
     2026-10-11, strength: assented; `red_main_fix` in
     [tools/precedent_branches.py](https://github.com/alex137/BestPractice/blob/staging/tools/precedent_branches.py)).
     Then land the same branch on staging, which refuses a landing that
     lacks it until it does.
   - **When GitHub's test is not due, the full local suite runs on `main`
     after the merge instead**, in the background:
     `--run-tests main`. Do not end the turn while an owed run has not
     started.
   - **Nothing runs after** when Debut already passed on exactly this
     staging and main, when only prose changed, or when the person asked
     for a fast one ("Produce fast": `--no-full-after`, which marks `main`
     as moved without a full check until the next full run).

**When GitHub's test is due.** In a public repository, on every Produce.
In a private one, the repository's `github_ci_main_test` decides first:
`never`, `always` (GitHub tests the push to `main` once, after the merge),
a number of hours, or `individual`, the default, which hands it to the
person: their `github_ci_workflows` switch, then `github_ci_every_hours`
(the person's `identity.json` first, then the repository's) -- 168 means at
most once a week since the last pass. It is due anyway when the last run
failed, until one passes; when no passing run is found or GitHub cannot be
asked; when a workflow predates the not-due skip; and with
`PRECEDENT_CI_NOW=1`. The tool decides this, not the session: read its
line, and never re-derive it.

**The long way is taken only on the person's own words, and that is
checked.** `--full` runs the full local suite before the merge and waits on
GitHub's test before merging. It is for when the person explicitly asks for
it, or agrees to it when asked, in this conversation -- never because a
session judged a change risky, and never on an old instruction. The tool
refuses `--full` unless it carries `--because '<their own words>'`, and
prints those words when it runs. If the long way looks warranted, say why
and ask; until they say yes, take the short way.

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
day, and so did this rule. Later that day he asked for this paragraph to
carry the whole short way, the rules for when GitHub's test runs, and the
long way as an exception that is "explicit and strong and checked": the
tool now refuses `--full` without the person's words.

**2026-10-14: pre-staging retired for everyone** (Morgan: *"Only me, go
ahead and plan it. Retire pre-staging."*, strength: decided). Staging,
where Booked now lands everywhere, is what Produce moves into main. The
reply check that holds a turn until an owed full run on `main` has
started had pointed at ladder-in-a-repo-on-staging, the rule for
repositories already on staging; with that rule retired, it points here.

## Install
Nothing new: the promotion tool and its checks are
[promote](promote.md)'s. The refusal of `--full` without `--because` is in
the engine's `full_route_refusal`
([tools/precedent_branches.py](https://github.com/alex137/BestPractice/blob/staging/tools/precedent_branches.py)),
with its planted cases in
`check_landing_on_staging_run_tests_and_fast_move_into_main`. This set's
`reply_check.json` entry `full-check-after-fast-main` holds the turn while
a merged fast move owes the full local suite on `main` and it has not
started, or has failed.
