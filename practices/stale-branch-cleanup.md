---
slug:        stale-branch-cleanup
title:       "Every archive-line reply and closing reply links the person's one pinned page of every branch they can delete and every staging waiting to go live"
tier:        on-demand
severity:    default
applies_to:  ["**"]
applies_to_why: "A moment, not a place: the archive-line reply and the closing reply, both named by the-boildown. Routed by the `reply` gate."
occasion:    "a person says \"Branch cleanup\", or the archive-line reply or the closing reply (the-boildown)"
gates:       ["reply"]
gates_why:   "This set's tools/ladder/branch_page_note.py counts the stale branches, and the repositories whose staging waits for main, at the start of every turn; the reply gate prints what it says (this set's reply_check.json, note_from_tool) only when there are any, so the archive-line reply or the closing reply (the-boildown) can still carry the link."
index_clause: "\"Branch cleanup\" refreshes the branch page; archive lines only link it"
index_required: true
checked_by:  null
ships:       ["tools/ladder/branch_page_note.py"]
defines:     ["Branch cleanup"]
command:     {"Branch cleanup": "Refresh your pinned Branch cleanup page now, from every repository this session can see; at the close of any other session it is only linked as it stands."}
status:      active
in_force_at: null
visible_to:  code-owners
supersedes:  []
overrides:   null
added:       "2026-10-05"
approved_by: "Morgan F, 2026-10-27 -- the rows in the page's own database, so a refresh needs no read-through and no republish: \"Both, A first. ... Act, Book.\" (strength: decided). Morgan F, 2026-10-27 -- \"Branch cleanup\", the page's name, as the word that asks for a rebuild, since a rebuild's read-through cost about 98,000 tokens: \"Both, A first. ... Act, Book.\" (strength: decided). Morgan F, 2026-10-20 -- the page rebuilt only when he asks, since every publish asked him to approve the page's GitHub tool: \"Sure let's rebuild the page only when I ask. Act and staging.\" (strength: decided). Morgan F, 2026-10-20 -- a rebuild only after a branch this session changed, never before the answer, and the page and its Boildown line bare: \"Can you make the enforcement of that stronger? ... when you give me the branches to delete now, you give me paragraphs about it's checkmarks etc - ... just give it to me and say nothing else. Do these and booked.\" (strength: decided). Morgan F, 2026-10-20 -- the page with every archive line, not only the closing reply: \"That page should be given. Anytime you do tell me that I can archive the page. Booked.\" (strength: decided). Morgan F, 2026-10-16 -- the page also lists each repository whose staging waits to go into main, taken over from the retired chief-of-staff: \"Let's implement your three suggestion\" (strength: decided). Morgan F, 2026-10-11 -- one pinned page updated in place, its address in his identity.json, instead of a new page every session: \"Let's do this\" (strength: decided). Earlier, Morgan F, 2026-10-05 -- \"in the Boildown, give the user an artifact with a list of all stale temp github repos that can be deleted, from all repos that are open in that session. Don't do that if there aren't any. If in doubt, do NOT include it\"; the closing reply only, and for code owners only (strength: decided)"
---

## Rule

**In the archive-line reply and the closing reply -- the two moments
[the-boildown](https://github.com/alex137/BestPractice/blob/staging/practices/the-boildown.md)
names and owns -- when any branch can be deleted or any
staging is waiting to go into main, link the page listing them in one
Boildown line.** The list covers every
repository open in the session where the person is a code owner. A branch
is on it only when it is already in `main`, so deleting it loses nothing;
`main`, `staging` and the engine's own branches never are.

Above the branches, the page lists each repository whose staging carries a
change `main` lacks ("What the page lists").

**Write the line as** *"Branches you can delete: Branch cleanup, N across M
repositories"*, with the page's name linked to it, and, when anything is
waiting, add *"; waiting to go live: <repository>, <repository>"*.
**Nothing else on that line, and nothing about the page anywhere else in
the reply** ("The line, and an older engine").

**Nothing to delete and nothing waiting, no page.** Not in any reply
but those two.

**Link the saved page as it stands. Refresh it only when the person says
"Branch cleanup"**, or plainly asks for a fresh list, **and only after the
reply's answer is written** ("Refreshing in full"). A refresh never rebuilds
or republishes the page; it is three steps ("The page and its database"):

1. ArtifactData `list` of collection `repos` on the page's url, with
   `out_dir` `<scratchpad>/branch-db`;
2. `python3 tools/precedent_stale_branches.py --fetch --db-docs
   <scratchpad>/branch-db --versions "<the listing's lines>"`;
3. ArtifactData `batch` with the `writes` line the tool prints.

A write refused for its version: list again and run the tool again. With
no page saved yet, `--db-page` writes one to publish once.

**An engine too old for this skips the refresh**: when the tool here does
not accept `--db-docs`, or session start reported ENGINE BEHIND UPSTREAM,
never publish anything to the page's address. Link it as it stands, and say
in the line that it was not refreshed and that Update Vendors here fixes it.

## Detail

**What the page is.** One section per repository, one row per branch: a
link to GitHub's branch list filtered to that one branch, where the trash
icon deletes it, and the branch's last commit date. A tick per row keeps
the person's place, saved in the page's database (`ticks`), and counts only
for the check it was made on. The session never deletes a
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
shows the date it comes back. A click hides that button at once and is
saved in the page's database (`clicks`). Every row stays as it was, for counting, reading the
names, and deleting one at a time instead. A repository whose `main` lacks
the workflow has no button, and the page says nothing about why; Update
Vendors installs it. **One more button, above
the repositories, starts the workflow in every public repository at once**
(2026-10-16): one click, through the person's own GitHub connector, so the
page is published with the capabilities the builder prints, which add that
one GitHub tool to the page's database. A private repository, or one whose
visibility is unknown, is never in it. **Any of these clicks checks off
every row of the repositories it covers** (Morgan: "it should check the box
and cross it off if it doesn't already", strength: decided). The page's builder,
[precedent_stale_branches.py](https://github.com/alex137/BestPractice/blob/staging/tools/precedent_stale_branches.py),
says how it decides.

**Why one page.** A new page every session left a pile of snapshots, each
showing branches already deleted. The pinned page is where the person looks,
any time. It says when it was refreshed, in their own timezone, and each
repository checked before that says when it was, because between refreshes
it shows the last list. A repository's ticks belong to its check: a
refreshed list starts unticked, since a branch still on it was not deleted. A page the person owns cannot be updated from somebody else's
account, which is why the address is theirs, in their individual source,
and never in a shared one.

**It passes the publish gate.** Universal's
[docs-track-models](https://github.com/alex137/BestPractice/blob/staging/practices/docs-track-models.md)
lets only a fresh render reach a link, and the engine registers this tool
as one of its page generators: the gate passes the page `--db-page` writes,
as it wrote it, for an hour. Edit the file and the gate refuses it as hand-made;
run the tool again instead.

**What counts as stale.** The tool lists a remote branch whose tip is
already in `origin/main`, or that carries no change `main` lacks -- a
Promote fix branch or copy of staging (`DATE-promote-fix-ID`, `DATE-promote-to-main-ID`, the `claude/` forms of those from before 2026-10-07, or the older `promote-fix-*` and `to-main-*`) whose only commits are merges that
changed nothing. It reads the remote-tracking refs, so `--fetch` first
makes the page match GitHub; the turn-start count skips the fetch to stay
fast.

**Waiting to go live, kept like the branches.** A repository this session
checked gets its fresh row, or none once staging and `main` are level; one
it could not see keeps its last row, with the date it was checked.
So the page covers, over a few closes, every repository the person works
in, and no single session has to read them all. A repository nobody opens
is the gap: its row only ages. A staging that merged `main` back in after a
Produce, and changes nothing `main` lacks, counts as level.

**Who sees it.** This practice is `visible_to: code-owners`: branch
management belongs to the people who run the repository, and a repository
where the person is not a code owner is left off the page.

### What the page lists

**Above the branches, the page lists each repository whose staging carries
a change `main` lacks**: how many commits, the oldest one's date, and a link
to GitHub's comparison. A repository where `main` is staging has no row. The
tool builds this list too; nothing extra to run.

### Refreshing in full

**Refresh it only when the person says "Branch cleanup"**,
the page's name, or anything else that plainly asks for a fresh list, **and
only after the reply's answer is written; every other time, link the saved
page as it stands.** A branch this session made, landed or merged does not
earn a refresh on its own (Morgan, 2026-10-20). Until 2026-10-27 a refresh
republished the page, and each publish asked the person to approve the
page's GitHub tool, so a rebuild after every landing put that prompt in
nearly every session: "I keep in getting asked for permission ... it is
very frustrating". It was also dear: the read-through a republish needed
came to about 98,000 tokens on 2026-10-27, for a page of about 1,100
lines, which is why the rows then moved into the page's database (below).
A link asks for nothing and costs one line.
**The answer always goes first**
([answer-first-ask-before-long-work](https://github.com/alex137/BestPractice/blob/staging/practices/answer-first-ask-before-long-work.md)):
BestPractice's answer-first gate holds the build and the publish while the
person's question has no answer (2026-10-20: a session spent minutes
rebuilding this page for its archive line before writing a word of the
answer). The archive sentence can end any reply with nothing running and
nothing off its landing branch (BestPractice's the-boildown, since
2026-10-18), and the link goes with each one; between refreshes the page
shows the date of its last build, so a stale row is easy to spot.

### The page and its database

**It is one page, and its rows live in its own database** (since
2026-10-27): one document a repository, which a refresh writes for the
repositories this session can see and leaves alone for every other. The
page itself is never rebuilt or republished for a refresh, so nothing has to
be read first or merged. **A refresh is three steps:**

1. ArtifactData `list` of collection `repos` on the page's url, with
   `out_dir` `<scratchpad>/branch-db` -- it saves the files and prints each
   document's version, and nothing of the rows comes into the conversation;
2. `python3 tools/precedent_stale_branches.py --fetch --db-docs
   <scratchpad>/branch-db --versions "<the listing's lines, or id=version
   pairs>"` -- the listing's files hold each document but not its version,
   and every write over a document is pinned to the version it was listed
   at, so the tool refuses until it has one for each;
3. ArtifactData `batch` with the `writes` line the tool prints.

A write refused for its version means another session wrote that
repository in between: list again and run the tool again. The page reads
the documents live, so the refresh shows the moment the batch lands. When
no page is saved, `--db-page <scratchpad>/branch-cleanup.html` writes the
page: publish it as a new page with the capabilities it prints, pin it,
save its address as `branch_cleanup_page` in the person's individual
`identity.json`, and fill it with the three steps. The page is published
again only when its code changes, never for its rows.

### The line, and an older engine

**An engine too old for this skips the refresh.** If the tool here does not
accept `--db-docs`, or session start reported the engine behind upstream
(ENGINE BEHIND UPSTREAM), do not refresh, and never publish anything to the
page's address: an older tool builds a whole page of only the repositories
this session can see, and publishing it over the saved page would replace
its database-backed page. **Still link the saved page as it stands**: a
link overwrites nothing. Say in the Boildown line that it was not refreshed
and that Update Vendors here fixes it (2026-10-13: a to-do repository's
older tool would have erased 42 branches across seven repositories). Write the line as: *"Branches you can delete: Branch cleanup, N across M
repositories"*, with the page's name linked to it, and, when anything is
waiting, add *"; waiting to go live: <repository>, <repository>"*.
**Nothing else on that line, and nothing about the page anywhere else in
the reply**: not its ticks, its buttons, or whether a button was tried
(Morgan, 2026-10-20: "just give it to me and say nothing else"). The page
says nothing about itself either: no intro and no notes on how a button
works, only the list. The reply gate prints the count at the start of a
turn when there is one, so the session knows before it writes the close.

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

Later the same day, Morgan: "I keep in getting asked for permission to
access the branch and it is very frustrating - how do we stop it
constantly asking for authorization". A session read its own log: the one
prompt it had raised was the republish of this page, whose delete-all
button needs a GitHub tool, and every session that landed a branch
republished it. He weighed a new page each time (it would most likely ask
the same way, lose his ticks and change the link) and chose a rebuild only
when he asks.

2026-10-27: a session in another repository measured the read-through a
rebuild needs at about 98,000 tokens, for a page of 1,097 lines, and found
sessions still rebuilding after every landing: the 2026-10-20 change above
had reached this set's staging but not `main`, which is what every
repository reads. Morgan named the word that asks for a rebuild, "Branch
cleanup", the page's name, so it is in the vocabulary, and chose to move the
page's rows into the page's own database next, so a refresh needs no
read-through and can be cheap enough to come back on its own.

The same day, the page moved into its own database. The last read-through
of the old page, to republish it in place one final time, found its script
broken: an unescaped apostrophe in one string, so nothing on it had run --
no ticks, no buttons, no Open next. BestPractice's harness now parses the
page's script. A refresh since is a listing, one tool run and one batch of
writes, a few thousand tokens, and touches only the repositories the
session can see.

**2026-10-31: the Rule cut to what a session does.** It had grown to
844 words; it now holds 333 (both counted with `wc -w` over the
`## Rule` section), and every paragraph it no longer holds moved word for
word into Detail, under the heading the Rule names. Morgan: *"maybe we add
to very deep check to always review like the 25% of all the rules that are
the longest in that repo and shorten them like you did?"*, then *"use your
judgment, and act booked produce"* (strength: assented).
