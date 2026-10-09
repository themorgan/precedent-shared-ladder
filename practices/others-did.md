---
slug:        others-did
title:       "The first reply of the day opens with what other people landed since you were last told"
tier:        on-demand
severity:    default
applies_to:  ["**"]
applies_to_why: "A moment, not a place: the first prompt of a person's day. The session-start hook finds the news and the reply gate hands it over, so no file path reaches it."
occasion:    "the first session of a day, after 07:00 in the person's own timezone, when someone else has landed work since the person was last told"
gates:       ["reply"]
gates_why:   "The reply gate prints the pending report at the top of the first prompt, once, and deletes it; later prompts that day carry nothing."
index_clause: "first reply of the day opens with what others landed since you were last told"
index_required: false
checked_by:  null
defines:     []
status:      active
in_force_at: null
supersedes:  []
overrides:   null
added:       "2026-10-08"
approved_by: "Morgan F, 2026-10-08 -- \"This new practice you define is great, approved\"; in the ladder set because not everyone may want it; the mechanism is part of Precedent so future people in the repository get it; Claude-signed commits attributed by their session (strength: decided)"
strength:    decided
---
## Rule

**When the reply gate hands over a block headed "WHAT OTHERS DID", the
reply opens with it, before answering the question.** A short summary in
What's New style: about three bullets, each opening with its key phrase in
bold, saying who did it and what it changes for the person. **A change to a
rule, or to how sessions behave, is always named**, however small it looks:
that is the change that makes a session act differently from what the
person expects. Then answer the question. Say it once; later replies do
not repeat it.

**It shows only what other people did.** WHATS_NEW.md is the day's most
important changes by anyone; this is the opposite view, for a person whose
own work fills most of that log.

**A commit signed only "Claude" is attributed through its session.** The
block lists any the tool could not settle with its session link. Open each
with `get_session` before writing the summary: one that opens from this
account is the person's own and is left out; one that does not is someone
else's.

## Detail

**What runs it.** `tools/precedent_others_did.py` ships with the engine,
so every repository with Precedent installed has it. It runs at session
start for anyone with this set, and does nothing for anyone without it.
It reads `main`, the staging branch and `pre-staging`, takes every commit
since the last report that is not the person's own, and leaves the block
for the reply gate. Merge commits are left out; the work they merged is
counted on its own.

**When.** At most once a day: nothing before 07:00 in the person's
timezone (`others_did_hour` in their identity.json changes the hour), and
nothing once they have been told since that hour. A day with news only from
the person themself writes nothing and says one line at session start.

**Where it remembers.** On origin's `refs/precedent/others-did`, a ref
outside every branch holding one file, `others_did_watermark.json`, one row
per person, keyed by their declared name. The tool writes it there by name,
never through the working tree, so a session's own work is never swept into
it, and it never shows in a branch list, rides a Promote or lands on a tier.
If that push is refused, the container keeps a note and the worst case is
the same report again in another container, never a missed one.

## Story

On 2026-10-08 Alex changed how merges into `main` work and Morgan found out
only when something confusing happened. The beta-branch check that came
before this had found those commits at that session's start. Its notice sat
past the part of the start-up output the session is shown, and it could
save "told" only into a checkout sitting idle on staging, so it never
reached him. This practice moved the report to the first prompt and the
mark onto the landing branch.

Later the same day that mark showed its own cost: a status check run in a
consuming repository's first reply pushed "Others-did mark ... [skip ci]"
straight onto its pre-staging, and the next Produce carried it up to main.
So the mark moved off every branch, to `refs/precedent/others-did`.
