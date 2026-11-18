---
slug:        assorted-notes-is-deleted
title:       What goes into ASSORTED_NOTES.md counts as deleted -- never read, searched, cited or mentioned unless asked for
tier:        resident
severity:    default
applies_to:  ["**"]
occasion:    "moving anything into ASSORTED_NOTES.md, starting a catch-all notes file or renaming a legacy BRAINSTORM, NOTES or IDEAS file, or writing a reply, a page or a plan that could draw on it"
gates:       []
index_clause: "ASSORTED_NOTES.md counts as deleted: never read, search, cite or mention it unasked"
index_required: true
checked_by:  tools/checks/check_assorted_notes_is_deleted.py
defines:     ["ASSORTED_NOTES.md"]
status:      active
in_force_at: null
requires:    ["ladder"]
supersedes:  ["assorted-notes"]
overrides:   null
added:       "2026-11-18"
approved_by: "Morgan F, 2026-11-18: \"That is where 'cut' things go, instead of being deleted, in case we want to reference it in the future, but we should treat it like they're deleted and you should never reference or search or remind me or mention them unless I explicitly ask.\" Then, on where it lives: \"I think that should be in precedent ladders because that is commonly how we use ladders, so add it there.\" Then, superseding the writing set's assorted-notes: \"I think we should deprecate the older rule and keep the new one. We should be strict but also this isn't just for 'writing' but generally about how I work.\""
strength:    decided
---
## Rule
**What is in `ASSORTED_NOTES.md` counts as deleted.** Never read, search,
cite, link or mention it unless the person asks for it; confirm a move
there in a word, with no recap. One per repo, by that name; only a
`README.md` or `MAP.md` may link it.

## Detail
- **Why the file exists at all:** it is where cut things go instead of
  being deleted, so nothing cut is lost, and nothing cut comes back on its
  own.
- **Out of search, too.** A repository declaring this set lists
  `ASSORTED_NOTES.md` in a root `.rgignore`, so a search cannot surface it
  by accident; a session told to open it reads it directly.
- **One file, one name.** A repo keeps a single `ASSORTED_NOTES.md` for
  what was cut and for notes not ready to be relied on. The filename is
  fixed; the directory is not: it sits with the repo's other content, in
  the directory that holds it, or at the root when there is none (older
  repos keep theirs in `content/`). A legacy equivalent -- `BRAINSTORM.md`,
  `NOTES.md`, `IDEAS.md` or similar -- is renamed to it, content kept.
- **A plain list of files** is a `README.md` or `MAP.md` whose job is
  saying what exists and where, or the hand-written source of a map
  (`MAP.source.md`, a row under `MAP.source/`). It may link the file;
  nothing else does -- not a page's own `## See also`, and not a link
  whose text is the file's own name. The moment something in the file is
  needed as support, it moves out to where it belongs, and the link points
  there.
- **The check.**
  [`tools/checks/check_assorted_notes_is_deleted.py`](../tools/checks/check_assorted_notes_is_deleted.py)
  fails a markdown link to `ASSORTED_NOTES.md` -- or, until one exists at
  any depth, to a legacy name -- anywhere but the file itself and a plain
  list of files. Matching is by basename, so `MARKETING_IDEAS.md` is not
  `IDEAS.md`; a vendored copy of somebody else's catalogue is skipped.
  It cannot see a bare mention with no link. Two-direction tested in
  [`tools/checks/tests/test_assorted_notes_is_deleted.sh`](../tools/checks/tests/test_assorted_notes_is_deleted.sh).
- **It replaces the shared writing set's `assorted-notes`**, which allowed
  a See also link and a link naming the file. That rule is deduplicated
  to this one; the parts of it that still hold are the two items above.
- **Asked for means the file, or what is in it, by name.** "Show me the
  scenes we set aside" is asking; "what else could we try?" is not.

## Why
The file exists so that cutting something never loses it, and so that
nothing cut comes back on its own. A session that recaps what it moved, or
links to it from the page it left, or checks it before proposing something
new, turns a deleted item back into a live one, which is exactly what
moving it there was meant to stop.

## Story
2026-11-18, a planning repository: a session moved set-aside video scenes
into `ASSORTED_NOTES.md` as asked, then named every one of them in its
reply, wrote "kept in Assorted Notes" onto the page they left and linked
the file from that page's See also. The repository already had a local
rule treating the file as deleted, but it loaded only when the file itself
was edited, and it spoke of documents, not of replies. It moved here,
resident and widened to replies and search, the same day.

Later the same day, Morgan settled the two rules into one: "I think we
should deprecate the older rule and keep the new one. We should be strict
but also this isn't just for 'writing' but generally about how I work."
The writing set's rule had let a session in the same repository move links
into a See also section, because its check passed them there. Its filename
and renaming parts came here, its check came here without the See also and
names-the-file exemptions, and its copy was deduplicated to this one.
