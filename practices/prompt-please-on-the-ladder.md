---
slug:        prompt-please-on-the-ladder
title:       "Adds to prompt-please, with the ladder: a handed-off prompt stops at Act unless the person said Booked"
tier:        on-demand
severity:    default
applies_to:  ["**"]
applies_to_why: "Fires with the rule it adds to: a phrase in a message, reached through the occasion index and the reply gate. No path locus."
occasion:    "a person says \"Prompt Please\" while the five-stage ladder is in force"
gates:       ["reply"]
gates_why:   "The same moment as universal's prompt-please: the reply is the whole artifact, so the two load together at the reply gate."
index_clause: "a handed-off prompt stops at Act; with Booked it names the landing branch"
checked_by:  null
defines:     []
status:      active
in_force_at: null
expires:     null
supersedes:  []
overrides:   null
adds_to:     prompt-please
added:       "2026-10-06"
approved_by: "Morgan, 2026-10-06 (strength: decided): \"rules should not be repeated, but supporting repos can have additions for them\" -- this holds what the ladder set's full copy of prompt-please changed, split out the same day. Its parts were decided earlier: a prompt without Booked ends at Act, 2026-10-01; the copy into this set, 2026-10-02. Updated 2026-10-09 for the ladder without pre-staging, Morgan: \"Act on the ladder plan\" (spec/LADDER_REDESIGN_PLAN.md)."
---
## Rule
**Adds to universal's [prompt-please](https://github.com/alex137/BestPractice/blob/staging/practices/prompt-please.md), for people who bring the ladder.** Everything there holds; this says where the handed-off work stops in the ladder's words.

**Without the person's Booked for this handoff, the prompt ends at Act.** The default text says so directly:

> **STOP AT ACT: build it on your feature branch, push it there, and stop.
> Open no pull request and merge nothing; the person lands it with Booked.**

It names no tier branch -- not `staging`, `main` or `pre-staging` -- as somewhere to land, merge or open a pull request, since landing is Booked's and needs the person's word.

**With Booked, it names the person's landing branch** -- what `python3 tools/precedent_branches.py --landing` answers in the seed repo, `staging` for a person on the ladder, landed with `python3 tools/precedent_branches.py --land` -- and never `main`, which only the person's Produce reaches. A repository's declared base branch is not the answer, because it can name a branch the person does not land on. When you cannot run the command, write "your landing branch" and let the receiving session resolve it.

**Booked travels only as the person's own words, quoted and dated in the block** -- `Prompt Please` said together with Booked (`Go update`, `Approved`), or anything that plainly gives both in the same breath. It is bounded exactly as [go-update](go-update.md) bounds it: the handed-off work only, the landing branch, and conditional on that repository's own checks passing.

## Why
Landing is the person's step on the ladder. A prompt that tells another session to land on staging, or to open a pull request into main, hands that step to a session the person never spoke to, and the receiving session has no way to tell it apart from the person's word.

## Story
Morgan, 2026-10-01 (strength: decided), after two prompts a session wrote told the receiving session to open pull requests into tier branches nobody had authorized: *"No, we always want to do it in the local container (\"Act\") and then I'll authorize it to go to pre-staging via \"Promote\" etc."* So a prompt without his Booked ends at Act.

**2026-10-06: split out of a full copy.** From 2026-10-02 the ladder set carried its own full copy of prompt-please, overriding universal's, to say this in the ladder's words. Every change to the rule had to be made twice; the 2026-10-06 change to its opening line was. Morgan: *"rules should not be repeated, but supporting repos can have additions for them."* This file holds only the addition; the set's copy of prompt-please is deduplicated.

**2026-10-09: the landing branch became staging.** With the ladder redesign Morgan approved that day ("Act on the ladder plan", `spec/LADDER_REDESIGN_PLAN.md`), a prompt carrying Booked names staging and `--land`; main is still reached only by the person's Produce.

## Install
Nothing to install. The reply gate prints it with prompt-please. One mechanical check: `prompt-please-landing-authority` in this set's `reply_check.json` refuses a paste block that tells another session to land, merge, push or open a pull request onto `staging`, `main` or `pre-staging` without the person's own Booked (or `Approved`, `Go update`) for this handoff quoted in it.
