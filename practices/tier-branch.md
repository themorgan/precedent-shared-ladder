---
slug:        tier-branch
title:       "\"Tier branch\" names one rung of the staging -> main ladder (pre-staging too, while anyone still uses it)"
tier:        on-demand
severity:    default
applies_to:  ["**"]
applies_to_why: "A word, not an action -- no file path reaches it. Since 2026-09-30 it is out of the occasion index (Morgan: a definition, not a trigger; its meaning is in Our language) and reached through the merge gate, the moment a tier branch matters: where work lands, and what is never offered for deletion. Decided: 2026-09-30."
occasion:    null
gates:       ["merge"]
gates_why:   "A merge is where a tier branch matters: which one the work targets, and that none of them is ever deleted."
index_clause: "staging or main, plus staging's old name and the lock; pre-staging if used"
checked_by:  null
defines:     ["Tier branch", "Landing branch"]
command:     null
status:      active
in_force_at: null
visible_to:  code-owners
supersedes:  []
overrides:   null
added:       "2026-10-02"
approved_by: "Morgan F, 2026-10-02, withdrawn from the universal set BestPractice, which keeps no copy (there: Morgan, 2026-09-28 -- after asking what \"a tier branch for deletion\" meant: 'Add \"Tier branch\" to the list of non-actionable vocabulary words.'). Updated 2026-10-09, Morgan: \"Act on the ladder plan\" retired pre-staging from the ladder, and \"When we roll this out to repos into which [BestPractice] is vendored in, make sure we have a smooth upgrade process for each. Merging the branches, telling he can delete pre-staging ...\" -- so a retired pre-staging that holds nothing staging lacks may be offered for deletion"
strength:    decided
---
## Rule
**"Tier branch" is this project's word for one rung of the branch ladder**
([spec/BRANCH_TIERS_PLAN.md](https://github.com/alex137/BestPractice/blob/staging/spec/BRANCH_TIERS_PLAN.md)):
`staging`, where work lands and waits for Produce; and `main`, the top,
production. **`pre-staging`**, where work landed until 2026-10-09, is no
longer used on the ladder; it stays a tier branch in any repository where
someone still lands on it or where it still holds work staging lacks. Two
more branches count as tier branches because they exist only to serve the
ladder: `precedent-beta-v01`, staging's name before 2026-09-25, kept so an
install still pinned to it takes its updates; and
`precedent-promote-lock`, which a Promote holds so two sessions never
promote at once. `tier_branches()` and `LOCK_BRANCH` in
[tools/precedent_branches.py](https://github.com/alex137/BestPractice/blob/staging/tools/precedent_branches.py)
are the list.

**Saying it does not itself trigger an action.** It is a word to look up,
like [primary-branch](primary-branch.md). What it carries is one standing
consequence stated elsewhere: a tier branch is never offered for deletion,
by any route ([branch-delete-links](https://github.com/alex137/BestPractice/blob/staging/practices/branch-delete-links.md#never-a-tier-branch) rule 4, and
[very-deep-check-on-the-ladder](very-deep-check-on-the-ladder.md), for the very deep check's branch sweep).

**The one exception is a retired pre-staging.** Once a repository is off
pre-staging -- nobody lands there, and it holds nothing staging lacks --
it may be offered for deletion as a one-click link, saying it is no longer
used. A session never deletes it, and never offers it while it holds work
staging lacks; that work is brought into staging first. `staging` and
`main` are never offered, ever.

## Why
The word reached a person before it had a definition: a reply said the very
deep check "never offers a tier branch for deletion", and the next message
had to ask what that meant. Writing it down once, with a `command:` entry,
puts it in the [vocabulary](https://github.com/alex137/BestPractice/blob/staging/practices/vocabulary.md) listing, so the next reply that
uses it points at an answer instead of a question.

## Story
Coined 2026-09-28. Fixing the very deep check for the branch tiers, a
session used "tier branch" as shorthand for the branches the sweep must
never offer to delete. Morgan asked what it meant, got the answer, and asked
for it to join "Primary branch" as a vocabulary word that defines rather
than acts.

**2026-10-09: pre-staging retired from the ladder.** Morgan approved the
ladder redesign ("Act on the ladder plan",
`spec/LADDER_REDESIGN_PLAN.md`), and asked
the same day that rolling it out tell him he can delete pre-staging. So a
pre-staging that holds nothing staging lacks stopped being protected, and
may now be offered for deletion as a link; staging and main stay protected
without exception.

## Install
No check on the answer, for the reason [vocabulary](https://github.com/alex137/BestPractice/blob/staging/practices/vocabulary.md) gives:
this defines a word, it does not check that a session used it. The listing
is generated from the `command:` field (`python3 tools/precedent_vocabulary.py`),
and `python3 tools/build_views.py` regenerates the glossary row.
