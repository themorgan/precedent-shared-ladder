---
slug:        vendor-update-on-the-ladder
title:       "Adds to vendor-update-runbook, with the ladder: the update lands by Booked and the full check waits for staging"
tier:        on-demand
severity:    default
applies_to:  ["**"]
applies_to_why: "Fires with the rule it adds to: an update being taken, a moment rather than a file class. Reached through the occasion index and the merge gate, as that rule is."
occasion:    "a person says \"Update Vendors\" in a repo on the five-stage ladder"
gates:       ["merge"]
gates_why:   "The same moment as universal's vendor-update-runbook, so the two load together at the merge gate."
index_clause: "Update Vendors lands by Booked; the full check waits for the Promote"
index_required: true
checked_by:  null
defines:     []
status:      active
in_force_at: null
expires:     null
visible_to:  code-owners
supersedes:  []
overrides:   null
added:       "2026-10-06"
approved_by: "Morgan, 2026-10-06 (strength: decided): \"rules should not be repeated, but supporting repos can have additions for them\" -- this holds what the ladder set's full copy of vendor-update-runbook changed, split out the same day. Its parts were decided earlier: missing tiers made by the update, 2026-09-27; the full check at staging, not pre-staging, 2026-09-27; every repo gets all three branches, 2026-09-25."
---
## Rule
**Adds to universal's [vendor-update-runbook](https://github.com/alex137/BestPractice/blob/staging/practices/vendor-update-runbook.md), for people who bring the ladder.** Everything there holds; this says how the update meets the five stages.

**Step 12 is [go-update](go-update.md)'s chain.** "Update Vendors" carries Booked for what it produced: say the landing branch out loud, commit, push, open the pull request into pre-staging, merge. When auto mode refuses that merge, ask for it in words that name it: "Merge PR #N into pre-staging". **Booked runs the update for you when anything is behind**: `python3 tools/precedent_merge_vendors.py` commits a finished update as a commit of its own before Booked lands the rest.

**Step 6 runs the landing tier's check, and the full check waits for the Promote to staging.** Into pre-staging that is the fast checks on what the update changed ([checks-follow-the-tier](checks-follow-the-tier.md)).

**The update gives the repo all three branches.** It makes any missing tier on origin -- `staging` from `pre-staging`, `pre-staging` from `staging`, both from `main` when neither exists -- and reports what it made. `python3 tools/precedent_branches.py --ensure-tiers` does the same on its own (`--apply` to make them); in a repo whose staging tier was `main`, it writes `"staging_branch": "staging"` into `precedent.json` for the update to commit. `base_branch` stays as it is, because it also pins where a practice source's session clone sits. From then on work lands on pre-staging, Promote moves it to staging, and main takes staging by pull request.

## Detail
**Your base branch takes the update by Promote, later**, so its committed tree is often one sync behind the manifest. That is why the update's loss check reads only lines this repo changed, never lines upstream deleted in between.

## Why
Taking an update is routine work, and routine work lands on pre-staging fast and earns the slow checks on its way to staging. A repo missing a tier cannot take the ladder at all, and an update is the one moment someone is already looking at how it is set up.

## Story
Morgan, 2026-09-25: *"make sure that all repos with precedent vendored-in have staging and pre-staging branches? That should be part of the migration!"* And 2026-09-27 (strength: decided), on making missing tiers in the update itself, and on the check: *"The point of pre-staging is to move fast, so I want the 10 minute checks to happen at the staging level, not pre-staging."*

**2026-10-06: split out of a full copy.** From 2026-10-02 the ladder set carried its own full copy of the runbook, nearly a thousand lines, overriding universal's to say these points in the ladder's words. Every change to the runbook had to be made twice, and the copies drifted. Morgan: *"rules should not be repeated, but supporting repos can have additions for them."* This file holds only the additions; the set's copy of vendor-update-runbook is deduplicated.

## Install
Nothing to install. The engine's `tools/precedent_update.py` already makes the missing tiers when the ladder is in force (`ensure_tiers` in `tools/precedent_branches.py`), and says nothing about tiers to anyone else; `tools/precedent_merge_vendors.py` is what Booked runs.
