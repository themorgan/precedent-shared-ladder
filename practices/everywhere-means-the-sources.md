---
slug:        everywhere-means-the-sources
title:       '"Everywhere" means BestPractice and the precedent-* sources'
tier:        on-demand
severity:    default
applies_to:  ["**"]
occasion:    "I say a change goes \"everywhere\""
index_clause: "BestPractice and precedent-* only; other repos get it by Update Vendors"
index_required: true
checked_by:  null
defines:     []
status:      active
in_force_at: null
supersedes:  []
overrides:   null
added:       "2026-10-19"
approved_by: "Morgan F, 2026-10-19, moved from an individual set (there: Morgan F, 2026-10-17)"
strength: decided
---
## Rule
**When I say a change goes "everywhere", I mean BestPractice and the
precedent-* sources** -- the places Update Vendors copies from. It does
not mean every repository I own. The repositories that use Precedent pick
the change up at their next Update Vendors, and that is the only way it
should reach them: changing them by hand now only makes a conflict in
each one at the next update.

**Every repository is meant only when I say so in those words** -- "every
repo", or the repositories named one by one. Even then, opening them is
`ask-before-opening-many-repos`'s
question first.

## Detail
A repository that has not had its vendors updated yet still carries the
old thing; that is expected, not a gap to chase. "Gone everywhere" is
true of a repository once its vendors are updated.

## Why
Morgan, 2026-10-17, after asking for pre-staging to be deleted
"EVERYWHERE": "I DID NOT MEAN IN EVERY REPO, I MEANT EVERYWHERE IN BP AND
PRECEDENT-* SO IT WOULD BE VENDORED IN IN THE UPDATES. PLEASE NOTE THAT
THIS IS WHAT \"EVERYWHERE\" MEANS UNLESS THE USER SPECIFIES EVERY SINGLE
REPO". And: "there is no pre-staging IN REPOS WHERE WE HAVE UPDATED THE
VENDORS that is the goal!!! Of course there still is in repos that are not
updated."

## Story
2026-10-17: Morgan asked for pre-staging to be deleted "EVERYWHERE", and
the request was read as every repository he has. He corrected it in the
words under Why: everywhere means BestPractice and the precedent-* sources,
and every other repository gets the change through its next Update
Vendors.
