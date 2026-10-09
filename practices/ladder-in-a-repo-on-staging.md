---
slug:        ladder-in-a-repo-on-staging
title:       "Adds to debut: in a repository that lands on staging, Booked, Debut and Produce work the new way"
tier:        on-demand
severity:    default
applies_to:  ["**"]
applies_to_why: "Fires with the rule it adds to: a stage word said in a repository already moved onto staging, a moment rather than a file class."
occasion:    "a person says \"Booked\", \"Debut\", \"Run tests\" or \"Produce\" in a repository whose landing branch is staging"
gates:       ["merge"]
gates_why:   "The same moment as debut, so the two load together at the merge gate."
index_clause: "on staging: Booked is --land, Debut only tests, Produce is --fast"
checked_by:  null
defines:     []
status:      active
in_force_at: null
expires:     null
visible_to:  code-owners
supersedes:  []
overrides:   null
adds_to:     debut
added:       "2026-10-09"
approved_by: "Morgan, 2026-10-09 (strength: decided): \"I want to fully complete one repo at a time\", and \"Yes, build it\" -- the move off pre-staging goes one repository at a time, so the stages read the repository's own landing branch until the last one has moved (spec/LADDER_REDESIGN_PLAN.md)."
---
## Rule
**Adds to [debut](debut.md), for a repository already moved onto staging.**
`python3 tools/precedent_branches.py --landing` says which: when it names
`staging`, the stages there work the new way, and everything else on the
ladder holds. A repository still landing on `pre-staging` keeps the stages
exactly as the other rules describe them.

- **Booked** lands the branch on `staging`:
  `python3 tools/precedent_branches.py --land BRANCH`. It brings `main`'s
  direct commits in first, runs the quick checks, and ends
  `LAND RESULT: ...`.
- **Debut, or "Run tests"**, runs the full local suite on `staging` and
  moves nothing: `python3 tools/precedent_branches.py --run-tests`. It is
  optional.
- **Produce** moves `staging` into `main` with the quick checks:
  `python3 tools/precedent_branches.py --promote --to main --fast`, then
  the pull request it names is merged at once and GitHub's full test is
  watched after the merge. A red result is fixed in the same sitting.
  After a failed "Run tests" on that commit it shows the failures and asks
  once (exit 4); a yes goes on with `--despite-failed-tests`.

## Why
The move off pre-staging goes one repository at a time, so for a while some
repositories land on staging and some on pre-staging. The person's stage
words stay the same in both; the repository's own landing branch decides
what each one does.

## Story
Morgan, 2026-10-09: *"I want to fully complete one repo at a time ... every
single time I do a vendor updates lately, and so many problems."* The first
plan switched his landing branch in his own settings, which moves every
repository at once; this keeps each repository's stages true to where that
repository lands.
