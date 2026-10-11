---
slug:        upstream-review
title:       "After an update or a ladder stage lands, review what it ran into and hand the fixable part upstream"
tier:        on-demand
severity:    default
applies_to:  ["**"]
applies_to_why: "A moment, not a place: Update Vendors finishing, and Booked, Debut and Produce landing, touch any file, so no path narrows it. Routed by the `merge` gate, the moment each of them ends in, and by the review block the tools print themselves."
occasion:    "Update Vendors finishes, or a Booked, Debut or Produce lands"
gates:       ["merge"]
gates_why:   "Each of these ends in a merge into a branch tier -- Update Vendors carries its own Booked -- so the merge gate is where the review is due."
index_clause: "after an update or a stage lands, hand fixable warnings upstream"
index_required: false
checked_by:  null
defines:     ["Upstream review", "Upstream-seen"]
status:      active
in_force_at: null
visible_to:  code-owners
supersedes:  []
overrides:   null
added:       "2026-10-11"
approved_by: "Morgan F, 2026-09-30 -- asked for it (\"What if every time an update vendors or migration update or upgrade finishes, explicitly review the warnings, errors, bugs you found, whether you fix them or not ... and you write a prompt for it\") and chose the record (\"I like the ledger idea, I'm sold. Let's do it with C. Act\"); rebuilt 2026-10-11 -- \"yes let's rebuild it but only in ladders and also only when the user is a code owner\" (strength: decided)"
---

## Rule

**When Update Vendors finishes, and when a Booked, Debut or Produce lands,
review everything that step ran into** -- every warning, error, note, new
exemption, kept local edit and workaround, **fixed or not** -- and ask of
each: **could it be fixed upstream**, in BestPractice or a precedent-* set,
so nobody meets it again?

**Only what is within reach counts.** An item is a candidate when the cause
lives somewhere we own or pin, and the fix is a bounded change a session
could make without a design call from the person. A third-party library's
deprecation, a platform notice, a network blip or a lost runner is not: say
so in one line. **A warning our own tool prints every time with nothing to
do is a candidate**: the fix is to stop it printing.

**Hand each candidate off in the Boildown, one
[Prompt Please](https://github.com/alex137/BestPractice/blob/staging/practices/prompt-please.md)
block per upstream repository**, not one per warning, after checking that no
live session is already on it. When nothing is worth it, one line: "Reviewed
N items, nothing worth fixing upstream".

**Only on the ladder, and only for a code owner.** Anyone else is never
shown the review, the block, or a line saying it was skipped.

## Detail

The tools print the review themselves, from
`tools/precedent_upstream_review.py` in the vendored engine, and only where
both conditions hold -- the ladder in force for the person, and the person
named as one of the repository's code owners:

- **Update Vendors** prints it at DONE, with `Upstream-seen:` lines to put at
  the end of the update's commit message.
- **Booked** prints it after the quick checks pass, and writes the lines into
  the commit it lands on staging.
- **Debut** prints it after the full check, and writes the lines into its
  merge commit.
- **Produce** prints it last and records nothing: main moves by a pull
  request.

**Each stage raises only what is new since the stage before.** The record is
the commits themselves: a stage reads the `Upstream-seen: <fingerprint>
<line>` lines on exactly the batch it moves and skips those items. A
fingerprint ignores what changes from run to run -- numbers, commit hashes,
temporary paths -- so the same warning at Booked and again at Produce is one
item. For something no tool printed, `python3
tools/precedent_upstream_review.py --stage booked --note "what you met"`
adds it.

## Why

[upstream-fix](https://github.com/alex137/BestPractice/blob/staging/practices/upstream-fix.md)
asks about a fix somebody made. The warnings nobody acted on -- passed over,
exempted, worked around locally -- had no moment where anyone asked whether
they could be fixed at the source, and an update or a landing is exactly
where they pile up. The record rides the commits so that stages run from
different sessions on different days raise each item once, and nothing grows
beyond the git history that is kept anyway.

It lives in the ladder set and is for code owners because both are where it
belongs: the stages are the ladder's, and the warnings are about running the
repository, which a person who only works in it never needs to see.

**No check enforces it, and that is considered.** Whether a reply carried
the block is the part that does not matter; whether each item was judged
fairly is judgment. The mechanical half is the tool, which prints the review
at the moment it is due.

## Story

Morgan, 2026-09-30: updates and promotions kept surfacing small bugs and
warnings that were fixed locally, exempted or ignored, and he wanted each
treated as a chance to fix it upstream, only for what is new since the stage
before. Of three places for the record -- a committed file, a side branch,
lines on the commits -- he chose the commits. That build never landed: the
session ended with it on its own branch, and the 2026-10-05 and 2026-10-11
very deep checks both found it there. On 2026-10-11 he asked for it again,
on today's ladder, in the ladder set, and for code owners only.

## Install

Nothing to install: declaring the ladder set brings the practice, and Update
Vendors brings the engine module that prints the review.
