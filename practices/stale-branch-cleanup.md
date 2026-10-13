---
slug:        stale-branch-cleanup
title:       "The closing Boildown links the person's one pinned page of every branch they can delete"
tier:        on-demand
severity:    default
applies_to:  ["**"]
applies_to_why: "A moment, not a place: the reply that closes a session. Routed by the `reply` gate."
occasion:    "the reply that says the session can be archived"
gates:       ["reply"]
gates_why:   "The reply gate counts the stale branches at the start of every turn and prints the line only when there are any, so the closing reply is the one that can still carry the link."
index_clause: "closing Boildown: refresh the pinned page of deletable branches, only if any"
index_required: false
checked_by:  null
defines:     []
status:      active
in_force_at: null
visible_to:  code-owners
supersedes:  []
overrides:   null
added:       "2026-10-05"
approved_by: "Morgan F, 2026-10-11 -- one pinned page updated in place, its address in his identity.json, instead of a new page every session: \"Let's do this\" (strength: decided). Earlier, Morgan F, 2026-10-05 -- \"in the Boildown, give the user an artifact with a list of all stale temp github repos that can be deleted, from all repos that are open in that session. Don't do that if there aren't any. If in doubt, do NOT include it\"; the closing reply only, and for code owners only (strength: decided)"
---

## Rule

**In the reply that says "You can archive this session", when any branch
can be deleted, publish a page listing them and link it in one Boildown
line.** The list covers every repository open in the session where the
person is a code owner. A branch is on it only when it is already in
`main`, so deleting it loses nothing; `main`, `staging`, `pre-staging` and
the engine's own branches never are.

**No branches, no page. In doubt, no page.** Not in any other reply either:
it rides with the archive line, so it does not come back every message.

**It is one page, updated in place.** Build it with `python3
tools/precedent_stale_branches.py --fetch --html
<scratchpad>/branch-cleanup.html`. **With a saved page it first asks for
that page as it stands, and writes nothing until it has it:** save it to a
file (the Artifact tool's read of that address, with path `index.html`) and
run the command again adding `--merge <that file>`. The page then keeps the
rows of every repository this session cannot see, under the date they were
last checked, and replaces the rest; `--replace` is only for a saved page
that is gone or unreadable. Then publish the file to that address (the
Artifact tool's `url`), so the person keeps the one page pinned in their
sidebar. When it says none is saved,
publish it as a new page, pin it, and save its address as
`branch_cleanup_page` in the person's individual `identity.json` -- the
next close then updates it. Either way, unedited and within the hour.

**An engine too old for this skips the page.** If the tool here does not
accept `--merge`, or session start reported the engine behind upstream
(ENGINE BEHIND UPSTREAM), do not publish: an older tool writes only the
repositories this session can see, and publishing it over the saved page
erases every other repository's rows and the page's saved ticks. Say in
the Boildown line that the page was skipped and that Update Vendors here
fixes it (2026-10-13: a to-do repository's older tool would have erased
42 branches across seven repositories). Write the line as: *"Branches you can delete: Branch cleanup, N across M
repositories"*, with the page's name linked to it. The reply gate prints the count at the start of a
turn when there is one, so the session knows before it writes the close.

## Detail

**What the page is.** One section per repository, one row per branch: a
link to GitHub's branch list filtered to that one branch, where the trash
icon deletes it, and the branch's last commit date. A tick per row keeps
the person's place, in their browser only. The page deletes nothing, and the
session never does either: a remote branch is the person's to delete
([never-delete-a-remote-branch](https://github.com/alex137/BestPractice/blob/staging/practices/never-delete-a-remote-branch.md),
universal).

**Why one page.** A new page every session left a pile of snapshots, each
showing branches already deleted. The pinned page is where the person looks,
any time. It says when it was refreshed, in their own timezone, because
between closes it shows the last close's list. Its ticks belong to that
build: a refreshed list starts unticked, since a branch still on it was not
deleted. A page the person owns cannot be updated from somebody else's
account, which is why the address is theirs, in their individual source,
and never in a shared one.

**It passes the publish gate.** Universal's
[docs-track-models](https://github.com/alex137/BestPractice/blob/staging/practices/docs-track-models.md)
lets only a fresh render reach a link, and the engine registers this tool
as one of its page generators: the gate passes the page it writes, as it
wrote it, for an hour. Edit the file and the gate refuses it as hand-made;
run the tool again instead.

**What counts as stale.** The tool lists a remote branch whose tip is
already in `origin/main`, or that carries no change `main` lacks -- a
Promote fix branch or copy of staging (`DATE-promote-fix-ID`, `DATE-promote-to-main-ID`, the `claude/` forms of those from before 2026-10-07, or the older `promote-fix-*` and `to-main-*`) whose only commits are merges that
changed nothing. It reads the remote-tracking refs, so `--fetch` first
makes the page match GitHub; the turn-start count skips the fetch to stay
fast.

**Who sees it.** This practice is `visible_to: code-owners`: branch
management belongs to the people who run the repository, and a repository
where the person is not a code owner is left off the page.

## Why

Morgan asked for this list by hand, session after session. On 2026-10-05 a
session built it once, as a page with 80 links across four repositories,
and he asked for it to come every time there is something to clean up --
but only then, and only at the close.

## Story

2026-10-05: after a day of Update Vendors, Debuts and Produces across
BestPractice and three practice sets, Morgan asked for "a list of branches
from the 3 sets as well as bestpractice that I can delete", then "As an
artifact please with clickable links". The page that session built is the
one `tools/precedent_stale_branches.py --html` now writes.

2026-10-07: a consuming repository's session built the page as this rule
says, and the Artifact publish gate refused it as "not a render of any
registered document". Two rules in force contradicted each other, and the
session fell back to linking branches in chat. The engine now registers the
tool as a page generator, so the page passes, and this rule says so.

2026-10-11: Morgan asked whether a template or a living file in each repo
would be cheaper. Neither: the page already comes from a program, and a
committed file goes stale the moment a branch is deleted. What his question
did point at was the new link every session, so the page became one pinned
page with a "Refreshed" line, updated in place.

2026-10-12: a consuming repository's Update Vendors pointed out that the
tool only sees the clones on disk, so a session with fewer repositories
open than the last one published over the page and wiped the rows the
wider session had listed: "Merge them, or only replace when the repo set
is the same." Merging keeps more, so `--html` now merges the saved page
and refuses to write without it.
