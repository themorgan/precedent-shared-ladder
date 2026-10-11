---
slug:        data-branch-names
title:       "A branch that holds a repository's long-lived data is named data-<what>"
tier:        on-demand
severity:    default
applies_to:  ["**"]
applies_to_why: "A moment, not a place: making a branch that keeps data rather than work. Reached through the occasion index and the merge gate, where which branches are records matters."
occasion:    "making a branch that holds a repository's long-lived data rather than work"
gates:       ["merge"]
gates_why:   "A merge is where the branch list matters: what lands, what is finished, and what is a live record that is never deleted."
index_clause: "data-<what>: a live record, never work; old ones are copied, never deleted"
index_required: false
checked_by:  null
defines:     ["Data branch"]
command:     null
status:      active
in_force_at: null
visible_to:  code-owners
supersedes:  []
overrides:   null
added:       "2026-10-11"
approved_by: "Morgan F, 2026-10-11 -- \"'data-' for permanent branches is great and approved (maybe we also rename existing ones?) BUT maybe this should be in 'ladder' only, because Alex might not want this and we don't want to touch his so make sure this 'data-' is only for ones done by people using the ladder\""
strength:    decided
---
## Rule

**A branch that holds a repository's long-lived data, not work, is named
`data-<what>`**, so a branch list shows at a glance which branches are
live records and which are finished or in-flight work. It is never merged
and never offered for deletion.

The engine's own two are named by
[tools/precedent_data_branches.py](https://github.com/alex137/BestPractice/blob/staging/tools/precedent_data_branches.py),
never by hand: `data-check-receipts` (which checks passed on which code)
and `data-promote-lock` (held while a Promote or a landing check runs). A
repository's own data branch -- a coordination board, a result cache, a log
a tool keeps -- takes the same prefix when it is made.

**Existing ones are copied, never deleted.** The first write from a ladder
session in a repository that still has the old branch pushes
`data-<what>` at the old branch's tip and leaves the old branch exactly
where it was. Deleting it is the person's call
([never-delete-a-remote-branch](https://github.com/alex137/BestPractice/blob/staging/practices/never-delete-a-remote-branch.md),
universal).

## Detail

**Only on the ladder.** This is the ladder's convention, not everyone's.
The engine gives a repository `data-` names only when the ladder is in
force for the person working there and the repository has the ladder's
tiers. A repository without the ladder keeps `precedent-check-receipts`
and `precedent-promote-lock` and never gains a `data-` branch.

**Once a repository has moved, everyone in it follows.** When origin has
`data-<what>`, every session there reads and writes it, on the ladder or
not, so the receipts and the lock stay one shared record instead of
splitting in two.

**A window on an older engine** still writes the old name until its
repository takes the new engine. For receipts that costs a re-run at most.
For the lock, the new engine counts a fresh hold on the old name as busy,
so two Promotes never run side by side across the change.

`python3 tools/precedent_data_branches.py` says which name each one has in
a repository, and why; `--migrate` makes the copies at once instead of on
the next write.

## Why

Morgan, 2026-10-11, after noticing that some repositories carry permanent
branches that track information: a naming convention makes it clear those
branches are in use. He approved `data-` the same day, asked whether the
existing ones should be renamed too, and kept it to the ladder so the
repositories of people who do not use it are left as they are.

## Story

2026-10-11: Morgan said he had realized the day before that some
repositories carry permanent branches the engine uses to track
information, and asked whether they should have a naming convention that
says they are in use. Looking at them showed the problem was more than
looks. The engine knew its two such branches, `precedent-check-receipts`
and `precedent-promote-lock`, only from lists typed into each tool that
must leave them alone -- the branch-cleanup page, the very deep check, the
review page -- and the board and cache libraries' default branch names
(`coord`, `result-cache`) were on none of those lists. A prefix lets every
tool recognize a live record by its name instead. He approved `data-` the
same day, asked whether the existing ones should move too, and kept the
convention to the ladder.
