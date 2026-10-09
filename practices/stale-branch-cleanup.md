---
slug:        stale-branch-cleanup
title:       "The closing Boildown links a page of every branch the person can delete"
tier:        on-demand
severity:    default
applies_to:  ["**"]
applies_to_why: "A moment, not a place: the reply that closes a session. Routed by the `reply` gate."
occasion:    "the reply that says the session can be archived"
gates:       ["reply"]
gates_why:   "The reply gate counts the stale branches at the start of every turn and prints the line only when there are any, so the closing reply is the one that can still carry the link."
index_clause: "closing Boildown: link a page of deletable branches, only if any"
index_required: false
checked_by:  null
defines:     []
status:      active
in_force_at: null
visible_to:  code-owners
supersedes:  []
overrides:   null
added:       "2026-10-05"
approved_by: "Morgan F, 2026-10-05 -- \"in the Boildown, give the user an artifact with a list of all stale temp github repos that can be deleted, from all repos that are open in that session. Don't do that if there aren't any. If in doubt, do NOT include it\"; the closing reply only, and for code owners only (strength: decided). Extended 2026-10-09, Morgan, rolling out the ladder without pre-staging: \"telling he can delete pre-staging\" -- a retired pre-staging that holds nothing staging lacks may be listed"
---

## Rule

**In the reply that says "You can archive this session", when any branch
can be deleted, publish a page listing them and link it in one Boildown
line.** The list covers every repository open in the session where the
person is a code owner. A branch is on it only when it is already in
`main`, so deleting it loses nothing; `main`, `staging` and the engine's
own branches never are. **`pre-staging` is listed only once it is
retired** -- the ladder stopped using it on 2026-10-09, nobody in that
repository lands there, and it holds nothing staging lacks -- marked as no
longer used. While it holds work staging lacks, it is never listed.

**No branches, no page. In doubt, no page.** Not in any other reply either:
it rides with the archive line, so it does not come back every message.

Build it with `python3 tools/precedent_stale_branches.py --fetch --html
<scratchpad>/branch-cleanup.html`, publish that file as an artifact, unedited
and within the hour, and write the line as: *"Branches you can delete: Branch cleanup, N across M
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

2026-10-09: the ladder stopped using pre-staging (Morgan, "Act on the
ladder plan", `spec/LADDER_REDESIGN_PLAN.md`),
and asked that rolling it out tell him he can delete it. A pre-staging that
holds nothing staging lacks joined what this page may list.
