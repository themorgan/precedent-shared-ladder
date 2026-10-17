---
slug:        primary-branch
title:       "\"Primary branch\" names trunk -- base_branch in precedent.json, usually main"
tier:        on-demand
severity:    default
applies_to:  ["**"]
applies_to_why: "A word, not an action -- no file path reaches it. Since 2026-09-30 it is out of the occasion index (Morgan: a definition with nothing to do; its meaning is in Our language) and reached through the merge gate, the moment the branch a pull request targets is decided. Decided: 2026-09-30."
occasion:    null
gates:       ["merge"]
gates_why:   "A merge is where the branch work targets is decided."
index_clause: "trunk: base_branch in precedent.json, usually main; not the landing branch"
checked_by:  null
defines:     ["Primary branch"]
command:     null
status:      active
in_force_at: null
supersedes:  []
overrides:   null
added:       "2026-10-02"
approved_by: "Morgan F, 2026-10-02, withdrawn from the universal set BestPractice, which keeps no copy (there: Morgan, 2026-09-22 -- asked to add \"Primary branch\" to the vocabulary list, wording it with \"trunk\": 'Can you add \"Primary branch\" to the vocabulary list, and in the phrase about it, use the word \"trunk\" there.')"
strength:    decided
---
## Rule
**"Primary branch" is this repo's own word for trunk** -- the branch the
repository's work is measured against and finished work ends up on,
whatever any one repository happens to call it. Saying it does not itself
trigger an action. This practice exists so the word has a definition a
session -- and a person -- can look up, rather than one only ever spelled
out inline inside another rule.

**The repository declares it, as `base_branch` in its `precedent.json`.**
In most repositories that is `main`. Absent a declaration, it is whichever
branch the repository's own routine work is actually developed and
committed against -- never a configured default chosen just because it is
configured that way.

**It is not the landing branch.** Where Booked (`Go update`) lands is the
landing branch, which `python3 tools/precedent_branches.py --landing` names
([go-update](go-update.md)). Off the ladder the two are the same branch. On
the ladder the landing branch is `staging`, and the primary branch, `main`,
is what a Produce promotes it into. Morgan, 2026-09-25: *"we now have a
concept called \"primary branch\" - that should probably be updated in
reference to this"* (strength: decided).

**A branch rule belongs to the repository that made it.** A repository that
stages its work on a branch other than `main` says so in its own files, and
that rule never travels to the repositories that take updates from it: in
each of those, the primary branch is whatever *that* repository declares.
Morgan, 2026-09-24, about the one catalogue repository that does this:
*"this rule doesn't get vendored in anywhere, the primary branch of the
vendored-in repo should be used, often main."* The tiers are the one
exception: `staging` and `main` are the same two names in every
repository, so that part travels like any other practice.

## Why
"Primary branch" and "trunk" name the same thing, but neither had been
written down as this project's own vocabulary before now -- so a question
like "was everything pushed to trunk?" had no guarantee of being read the
same way a bare "push directly" already resolves to that branch. Naming it
once, with a `command:` entry, puts it in the
[vocabulary](https://github.com/alex137/BestPractice/blob/staging/practices/vocabulary.md) listing without a session inferring the mapping
fresh in every conversation.

## Story
Coined 2026-09-22: asked what word developers use for the branch
push-directly (retired 2026-09-30) already called "the primary branch," told
it was "trunk" in general developer usage, Morgan asked for the two to be
tied together in the project's own vocabulary rather than left as a private
mapping I'd have to re-derive each time.

**2026-10-14: pre-staging retired for everyone** (Morgan: *"Only me, go ahead and plan it. Retire pre-staging."*, strength: decided). Until then
new repositories were written with `pre-staging` as their landing branch,
the tiers were three names -- `pre-staging`, `staging` and `main` -- and
staging and main were both what the primary branch was promoted into.

**2026-10-17: one meaning.** The very deep check of that day found this
Rule defining the word twice: `base_branch`, and also the branch Booked
lands on, which on the ladder are `main` and `staging`. Morgan: *"Fix the
other issues you found including the checks that never run. Tell me what
you decide. I will be offline so don't wait for me. Approved, act, and
Booked."* Chosen by the session under that delegation: `base_branch`, the
meaning Precedent's engine gives the words (its CI-cadence report calls
`base_branch` the primary branch), and the branch Booked lands on is called
the landing branch, as go-update and the engine already call it.

## Install
No check on the answer, same reason [vocabulary](https://github.com/alex137/BestPractice/blob/staging/practices/vocabulary.md) gives --
this defines a word, it does not check that a session used it. What's
checked is the generated copy: `python3 tools/build_views.py` regenerates
this row into AGENTS.md's loader block and the reader-facing table, same as
every other command entry (practice: registry-source-of-truth).
