---
slug:        prompt-please-on-the-ladder
title:       "Adds to prompt-please, with the ladder: a handed-off prompt says nothing about landing; the receiving session lands it by risk"
tier:        on-demand
severity:    default
applies_to:  ["**"]
applies_to_why: "Fires with the rule it adds to: a phrase in a message, reached through the occasion index and the reply gate. No path locus."
occasion:    "a person says \"Prompt Please\" while the five-stage ladder is in force"
gates:       ["reply"]
gates_why:   "The same moment as universal's prompt-please: the reply is the whole artifact, so the two load together at the reply gate."
index_clause: "prompt is silent on landing; small work to main, big stops at Act"
checked_by:  null
defines:     []
status:      active
in_force_at: null
expires:     null
supersedes:  []
overrides:   null
adds_to:     prompt-please
added:       "2026-10-06"
approved_by: "Morgan, 2026-10-06 (strength: decided): \"rules should not be repeated, but supporting repos can have additions for them\" -- this holds what the ladder set's full copy of prompt-please changed, split out the same day. Its parts were decided earlier: a prompt without Booked ends at Act, 2026-10-01; the copy into this set, 2026-10-02."
---
## Rule
**Adds to universal's [prompt-please](https://github.com/alex137/BestPractice/blob/staging/practices/prompt-please.md), for people who bring the ladder.** Everything there holds; this says where the handed-off work stops in the ladder's words.

**The prompt says nothing about how far the work goes.** No "stop at Act",
no "land it", and no tier branch named as somewhere to land, merge or open a
pull request. The person says which they want, when they want to, in the
note they paste above it (Morgan, 2026-10-09: "Sometimes it's one sometimes
it's the other ... in the preface comment I paste above when I paste it in,
I can say which I prefer").

**Where the note says nothing, the receiving session decides by risk.**
Small or low-risk work it takes all the way to `main` -- Booked, then
Produce -- with that repository's checks, and GitHub's test or the full
local check after, as the ladder requires. Big, complex or high-risk work
(go-update's high-risk: an install, a migration, a shared file other repos
read, anything hard to undo, or anything it is unsure is none of those) it
builds and pushes on its feature branch, stops at Act, and gives the person
its read: what it built, what worries it, and what it recommends. Unsure
which? Big.

**A landing word in a prompt is only ever the person's own, quoted and dated in the block** -- `Prompt Please` said together with Booked (`Go update`, `Approved`), or anything that plainly gives both in the same breath -- and it is bounded exactly as [go-update](go-update.md) bounds it: the handed-off work only, and conditional on that repository's own checks passing. A session never writes one of its own.

## Why
Landing is the person's step on the ladder, and the person decides how much
of it to hand over; a prompt written by another session cannot. A prompt that tells another session to merge into pre-staging, or to open a pull request into staging, hands that step to a session the person never spoke to, and the receiving session has no way to tell it apart from the person's word.

## Story
Morgan, 2026-10-01 (strength: decided), after two prompts a session wrote told the receiving session to open pull requests into tier branches nobody had authorized: *"No, we always want to do it in the local container (\"Act\") and then I'll authorize it to go to pre-staging via \"Promote\" etc."* So a prompt without his Booked ends at Act.

**2026-10-09: by risk, and in his own note.** A handoff that stopped at Act
kept a small fix waiting on a second word from him after he had asked for it
to reach main ("I told you twice"). Morgan: *"I'd say nothing in the prompt
about that ... on low risk or small stuff, go right through to main but on
big or complex or high risk stuff you should not yet do it but give me
feedback."*

**2026-10-06: split out of a full copy.** From 2026-10-02 the ladder set carried its own full copy of prompt-please, overriding universal's, to say this in the ladder's words. Every change to the rule had to be made twice; the 2026-10-06 change to its opening line was. Morgan: *"rules should not be repeated, but supporting repos can have additions for them."* This file holds only the addition; the set's copy of prompt-please is deduplicated.

## Install
Nothing to install. The reply gate prints it with prompt-please. One mechanical check: `prompt-please-landing-authority` in this set's `reply_check.json` refuses a paste block that tells another session to land, merge, push or open a pull request onto `pre-staging`, `staging` or `main` without the person's own Booked (or `Approved`, `Go update`) for this handoff quoted in it.
