---
slug:        very-deep-check-on-the-ladder
title:       "Adds to very-deep-check, with the ladder: fixes land by Booked, tier branches are never offered for deletion, and every Promote merge is rehearsed"
tier:        on-demand
severity:    advisory
scope:       any-adopter
applies_to:  ["**"]
applies_to_why: "Fires with the rule it adds to: a person asking for the check, not a file being touched. Reached through the occasion index, as that rule is."
occasion:    "running a very deep check where the five-stage ladder is in force"
gates:       []
index_clause: "fixes land by Booked; never offer a tier branch for deletion; rehearse Promotes"
checked_by:  null
defines:     []
status:      active
in_force_at: null
expires:     null
visible_to:  code-owners
supersedes:  []
overrides:   null
adds_to:     very-deep-check
added:       "2026-10-06"
approved_by: "Morgan, 2026-10-06 (strength: decided): \"rules should not be repeated, but supporting repos can have additions for them\" -- this holds what the ladder set's full copy of very-deep-check changed, split out the same day. Its parts were each decided on 2026-09-28: read main and write by Booked then Promote; never offer pre-staging or staging for deletion; drift and rehearsal on every tier pair."
---
## Rule
**Adds to universal's [very-deep-check](https://github.com/alex137/BestPractice/blob/staging/practices/very-deep-check.md), for people who bring the ladder.** Everything there holds; this says how the check meets the five stages.

**Read `main`, write through Booked.** Every fix the check makes is committed on its working branch and lands the ordinary way: Booked (`Go update`) onto the person's landing branch, and a Promote from there, never pushed to `main`. A retired set's `drop-retired` is Booked onto its landing branch like any other change. Before fixing a finding in a file the `LIVE VERSUS LANDING` section names, check whether pre-staging already fixed it and is only waiting to be promoted.

**A tier branch is never offered for deletion**, by any list the check prints or writes: `pre-staging`, `staging`, `main`, staging's old name `precedent-beta-v01`, and Promote's lock branch, in every repo in force, merged or not. Every Promote fast-forwards the lower tiers, so an ancestor test calls them "merged" right after one.

**Drift is asked of every tier pair**: what `staging` and `main` carry that `pre-staging` never took, and what `main` carries that `staging` never took. A row on a pair into `pre-staging` is not a choice to put to the person: everything above belongs below, and `python3 tools/precedent_branches.py --sync-pre-staging` (which a Promote runs first anyway) brings it down. A row nobody wants is a revert owed on the upper branch.

**Every merge a Promote makes is rehearsed**, in order: `pre-staging` into `staging`, then `staging` into `main`.

## Detail
The fleet version of the branch sweep, across every repo the person owns, is [chief-of-staff](chief-of-staff.md)'s; this check stays inside the repos it already reads.

## Why
The check reads what people run, which is `main`; a fix pushed straight there skips every check the ladder puts between a change and production. And the tier branches are the ladder itself: a one-click delete link on one of them, after a Promote made it look merged, would take the pipeline down with a click.

## Story
Morgan, 2026-09-28 (strength: decided): *"it's better to do a deep check on the live version (main), but we don't want to edit it, to edit it we should use the normal process."* Until then a run read whatever the harness checked out -- `main` in one repo and `pre-staging` in four others, the same afternoon. The same day: *"it needs to never never offer to delete pre-staging nor staging"* -- until then the sweep protected only the declared base and the default branch, and would have handed both `pre-staging` and `precedent-beta-v01` over with a delete link. Also the same day, the drift question moved down a tier and the rehearsal took both Promote merges, since the first is the one that happens every day.

**2026-10-06: split out of a full copy.** From 2026-10-02 the ladder set carried its own full copy of very-deep-check, nearly three thousand lines, overriding universal's to say these points in the ladder's words. Every change had to be made twice, and the copies drifted. Morgan: *"rules should not be repeated, but supporting repos can have additions for them."* This file holds only the additions; the set's copy of very-deep-check is deduplicated.

## Install
Nothing to install. Universal's `tools/very_deep_check.py` already does each of these when the ladder is in force (`ladder_in_force()` in `tools/precedent_branches.py`): the tier-branch guard in the one function that mints every delete link, the drift rows per tier pair, and both rehearsals.
