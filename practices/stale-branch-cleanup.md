---
slug:        stale-branch-cleanup
title:       "Every reply that says the session can be archived links the person's one pinned page of every branch they can delete and every staging waiting to go live"
tier:        on-demand
severity:    default
applies_to:  ["**"]
applies_to_why: "A moment, not a place: a reply that says the session can be archived. Routed by the `reply` gate."
occasion:    "a reply that says \"You can archive this session\", or answers \"Archive\" or \"Archive?\""
gates:       ["reply"]
gates_why:   "This set's tools/ladder/branch_page_note.py counts the stale branches, and the repositories whose staging waits for main, at the start of every turn; the reply gate prints what it says (this set's reply_check.json, note_from_tool) only when there are any, so a reply that says the session can be archived is the one that can still carry the link."
index_clause: "with every archive line: link the pinned branch and staging page, only if any"
index_required: false
checked_by:  null
ships:       ["tools/ladder/branch_page_note.py"]
defines:     []
status:      active
in_force_at: null
visible_to:  code-owners
supersedes:  []
overrides:   null
added:       "2026-10-05"
approved_by: "Morgan F, 2026-10-20 -- the page with every archive line, not only the closing reply: \"That page should be given. Anytime you do tell me that I can archive the page. Booked.\" (strength: decided). Morgan F, 2026-10-16 -- the page also lists each repository whose staging waits to go into main, taken over from the retired chief-of-staff: \"Let's implement your three suggestion\" (strength: decided). Morgan F, 2026-10-11 -- one pinned page updated in place, its address in his identity.json, instead of a new page every session: \"Let's do this\" (strength: decided). Earlier, Morgan F, 2026-10-05 -- \"in the Boildown, give the user an artifact with a list of all stale temp github repos that can be deleted, from all repos that are open in that session. Don't do that if there aren't any. If in doubt, do NOT include it\"; the closing reply only, and for code owners only (strength: decided)"
---

## Rule

**In every reply that says "You can archive this session", and in one
that answers "Archive" or "Archive?", when any branch can be deleted or any
staging is waiting to go into main, link the page listing them in one
Boildown line.** The list covers every
repository open in the session where the person is a code owner. A branch
is on it only when it is already in `main`, so deleting it loses nothing;
`main`, `staging` and the engine's own branches never are.

**Above the branches, the page lists each repository whose staging carries
a change `main` lacks**: how many commits, the oldest one's date, and a link
to GitHub's comparison. A repository where `main` is staging has no row. The
tool builds this list too; nothing extra to run.

**Build and publish it the first time a session gives it, and again only
when this session has made, landed or merged a branch since it last
published; otherwise link the saved page as it stands.** The archive
sentence can end any reply with nothing running and nothing off its landing
branch (BestPractice's the-boildown, since 2026-10-18), so a page rebuilt
at each one would be rebuilt every message. From 2026-10-18 to 2026-10-20
this rule solved that by giving the page only in the closing reply, and
since Morgan rarely types "Archive", the page stopped appearing at all.
The link costs one line; the rebuild is what only a change earns.

**Nothing to delete and nothing waiting, no page.** Not in a reply that
does not say the session can be archived.

**It is one page, updated in place.** Build it with `python3
tools/precedent_stale_branches.py --fetch --html
<scratchpad>/branch-cleanup.html`. **With a saved page it first asks for
that page as it stands, and writes nothing until it has it:** read that
address once with the Artifact tool, **without a path** -- the read a
republish needs -- and run the command again adding `--merge <the file that
read says the full HTML was saved to>`. Only a page small enough to come
back inline needs a second read, with path `index.html`, for the file; a
read with the path alone does not count for the republish. **Hand the tool
the file that read saved, with `--merge`, and never rebuild the page from
your own copy of it. Read the page immediately before building, every time,
and merge that file: never a copy from earlier in the session, and never the
page this session built last.** **Before the first publish, Read every
line of that saved file**, in two or three ranges with offset and limit
(one Read of the whole page is over the tool's size cap), and change
nothing in it. When another session, or the page itself, published the
version last -- the usual case for this shared page -- the Artifact tool
refuses a publish until the file has been read through, and after one
refusal it refuses the same content once more before letting it through
(measured 2026-10-17: refused unread; read through; refused as "identical
content already refused"; published on the third try). Reading first
costs one publish. When this session published the last version itself,
the tool counts it as viewed and the read is not needed. Another session may
have republished it in between, and a merge against an older copy drops
that session's rows and every tick saved since; the tool warns when the
file it is handed is not a fresh read. The page then keeps the
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
erases every other repository's rows and the page's saved ticks. **Still
link the saved page as it stands**: a link overwrites nothing. Say in the
Boildown line that it was not refreshed and that Update Vendors here
fixes it (2026-10-13: a to-do repository's older tool would have erased
42 branches across seven repositories). Write the line as: *"Branches you can delete: Branch cleanup, N across M
repositories"*, with the page's name linked to it, and, when anything is
waiting, add *"; waiting to go live: <repository>, <repository>"*. The reply gate prints the count at the start of a
turn when there is one, so the session knows before it writes the close.

## Detail

**What the page is.** One section per repository, one row per branch: a
link to GitHub's branch list filtered to that one branch, where the trash
icon deletes it, and the branch's last commit date. A tick per row keeps
the person's place, in their browser only. The session never deletes a
branch: a remote branch is the person's to delete
([never-delete-a-remote-branch](https://github.com/alex137/BestPractice/blob/staging/practices/never-delete-a-remote-branch.md),
universal).

**The delete-all button (2026-10-16).** Each repository's section opens
with one more line: a link to that repository's
`precedent-branch-cleanup.yml` workflow on GitHub, where the person clicks
Run workflow and it deletes every branch already in `main`. Nothing ever
starts it but that click (Morgan: "on both [private] and public, NEVER run
the cleanup automatically", strength: decided). **In a public repository
the button is always there.** **In a private one it shows only once
`github_branch_cleanup_every_hours` (in the person's `identity.json`; 336
for Morgan) has passed since that repository's last cleanup run**, one
tracker per repository, apart from the main test's; otherwise the line
says the date it comes back. A click hides that button at once and is
saved into the page. Every row stays as it was, for counting, reading the
names, and deleting one at a time instead. A repository whose `main` lacks
the workflow says so; Update Vendors installs it. **One more button, above
the repositories, starts the workflow in every public repository at once**
(2026-10-16): one click, through the person's own GitHub connector, so the
page is published with the capabilities the builder prints, which add that
one GitHub tool to the page's own saves. A private repository, or one whose
visibility is unknown, is never in it. **Any of these clicks checks off
every row of the repositories it covers** (Morgan: "it should check the box
and cross it off if it doesn't already", strength: decided). The page's builder,
[precedent_stale_branches.py](https://github.com/alex137/BestPractice/blob/staging/tools/precedent_stale_branches.py),
says how it decides.

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

**Waiting to go live, merged like the branches.** A repository this session
checked gets its fresh row, or none once staging and `main` are level; one
it could not see keeps its last row, dated and marked as possibly moved.
So the page covers, over a few closes, every repository the person works
in, and no single session has to read them all. A repository nobody opens
is the gap: its row only ages. A staging that merged `main` back in after a
Produce, and changes nothing `main` lacks, counts as level.

**Who sees it.** This practice is `visible_to: code-owners`: branch
management belongs to the people who run the repository, and a repository
where the person is not a code owner is left off the page.

## Why

Morgan asked for this list by hand, session after session. On 2026-10-05 a
session built it once, as a page with 80 links across four repositories,
and he asked for it to come every time there is something to clean up --
but only then, and only at the close. On 2026-10-20 he asked for it with
every reply that says the session can be archived, since that is when he
decides whether to archive it.

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

2026-10-14: pre-staging retired for everyone (Morgan: *"Only me, go ahead and plan it. Retire pre-staging."*, strength: decided). It had been
on the never-listed tier branches beside `main` and `staging`; a leftover
one is now Update Vendors' to offer for deletion, once its work is on
staging.

2026-10-15: a consuming repository's session closed by following only the
reply gate's line, which said to merge "the page as it stands" without
saying how to get it. It read the address without a path, which saved no
file, then merged against its own copy from earlier in the session.
Another session had republished the page in between, so that merge would
have dropped that session's rows and the ticks saved since; the artifact
service's conflict refusal is what caught it. The rule and the gate line
now say to read the page with path `index.html` immediately before
building, and the tool warns when the file it is handed is not a fresh
read.

2026-10-16: Morgan retired chief-of-staff, which he rarely used and whose
name a new system of his will take. Its one check nothing else did --
which repositories have staging waiting for main -- moved here, onto the
page he already keeps pinned, so it comes at every close instead of on
request. The old practice read every repository at once; this page gets
there across sessions, by the same merge that keeps the branches.

2026-10-16, the same evening: a consuming repository's close read the page
twice, first with path `index.html` as this said, then without one, because
the first read's own result says its copy does not count for a republish.
The second read had saved the full page to a file anyway, and the session
then opened that file and read it through, about 50KB nobody needed. One
read without a path now serves both the merge and the publish.

2026-10-17, evening: a session fixing root issues from a consuming repo's
Update Vendors tested the republish the way this rule then read, with no
read of the saved file, because one session had read all 70KB of it for
about 31,000 tokens and nobody had tried without. The Artifact tool refused
the publish, since another session had published last. After the read it
also refused the same content once more, and the third publish went
through. The read cannot be skipped while the Artifact tool asks for it, so
the rule now says to do it before the first publish, in ranges.

2026-10-20: a session fixing how a shared set came to hold copies of every
other source's rules closed with four separate branch delete links and no
page. Since 2026-10-18 the page rode only with a reply that answers
"Archive", and that session's archive line was not one, so the rule said
"In doubt, no page." Morgan: "how come recently you are no longer giving me
the link to the artifact with all the branches to delete from the
session?", then "That page should be given. Anytime you do tell me that I
can archive the page. Booked." The page now comes with every archive line,
rebuilt only when the session's branches changed.
