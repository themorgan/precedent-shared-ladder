---
slug:        loss-comes-with-a-verdict
title:       Anything I'm told will be lost comes with a verdict and my action
tier:        on-demand
severity:    default
applies_to:  ["**"]
occasion:    "telling me something will be lost, discarded, or go away with the container, clone or session"
gates:       ["reply"]
index_clause: "never just 'it goes away': say it's fine to lose and why, or how I keep it"
index_required: true
checked_by:  null
defines:     []
command:     null
status:      active
in_force_at: null
supersedes:  []
overrides:   null
added:       "2026-10-19"
approved_by: "Morgan F, 2026-10-19, moved from an individual set (there: Morgan F, 2026-09-26, asked for it outright after a reply said the session's own clones held edits that 'go away with the container': \"update your system to ALWAYS ALWAYS give me a recommendations on what to do whenever you tell me something will go away with the container/clone/session\" -- \"Go update\".)"
strength:    decided
---
## Rule
**Never tell me something will be lost without telling me whether that's
okay.** When a reply says that edits, files, commits, branches or anything
else will go away with the container, the clone or the session -- or are
"not committed or pushed anywhere" -- the same sentence carries one of two
verdicts:

- **Fine to lose, and why.** *"They go away with the container, and that's
  fine: the same change is already on the landing branch in #216."* The reason
  has to be checked, not assumed -- where the copy is, or why nobody needs it.
- **Keep it, and the action.** *"They'll be lost unless we push them -- I'm
  pushing now"*, or, when it's mine to do, *"you need to merge #42 before
  archiving."* Something only I can do is named as my action, in plain words.

**Where you can make it safe yourself, do that instead of reporting it** --
push it, merge it, copy it where it belongs. The verdict is for what is left.

A bare *"they aren't committed anywhere and go away with the container"* is
the failure: it hands me a fact with no decision attached, and I can't tell
whether it's reassurance or a warning.

## Detail
**This is the chat-reply form of a check the archive line already makes.**
Universal `the-boildown` requires every checkout the container holds to be
safe before the archive-line reply (the-boildown), and gives each one a
`**Checkout disposition:** NAME -- discard (reason)` line. That covers the
archive moment only. This covers every other moment a reply mentions a loss
-- mid-task, in a status note, in a caveat -- where no gate is looking.

**"Why it's fine" names the other copy or the reason, concretely.** "It's
regenerated every session" is a reason. "It's probably fine" is not.
Where the answer isn't known, finding it out is part of writing the
sentence: diff the file against the branch that should hold it, or run
[`precedent_container_safe.py`](https://github.com/alex137/BestPractice/blob/staging/tools/precedent_container_safe.py).

## Why
A statement that something will vanish is a warning in form and says
nothing in content until someone judges it. The session is the one holding
the evidence -- it knows what is in the clone and what is already on the
branch -- so leaving the judgment to me leaves it with the person who can
least afford to check. `so-what-test` keeps warnings in a reply; this is
what a warning about loss has to contain to be worth keeping.

## Story
2026-09-26. A session refreshing the vendored engine in two practice sources
closed with: *"Running the refresh also rewrote the session's own copies of
those repos under `~/`. Those edits aren't committed or pushed anywhere, and
they go away with the container."* True, and useless: the edits were
identical to what had just merged into `pre-staging`, so losing them was
fine -- but the reply never said so. Morgan: *"I NEVER understand when you
say 'those edits aren't committed or pushed anywhere, and they go away with
this container' because I DON'T KNOW IF WE WANT THAT OR NOT."*

## Install
No mechanical check. The subject is a sentence in a chat reply, and whether
a loss is acceptable turns on what the lost thing is -- no pattern match can
render that verdict. It is reached two ways: the occasion index, since the
trigger is something the session is about to say, and the `reply` gate, the
moment the sentence gets written.
