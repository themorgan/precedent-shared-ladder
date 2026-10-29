---
slug:        vendor-update-on-the-ladder
title:       "Adds to vendor-update-runbook, with the ladder: the update lands on staging by Booked, then goes live by Produce"
tier:        on-demand
severity:    default
applies_to:  ["**"]
applies_to_why: "Fires with the rule it adds to: an update being taken, a moment rather than a file class. Reached through the occasion index and the merge gate, as that rule is."
occasion:    "a person says \"Update Vendors\" or \"Update All Vendors\" in a repo on the five-stage ladder"
gates:       ["merge"]
gates_why:   "The same moment as universal's vendor-update-runbook, so the two load together at the merge gate."
index_clause: "Update Vendors lands on staging by Booked, then goes live by Produce"
checked_by:  null
defines:     []
status:      active
in_force_at: null
expires:     null
visible_to:  code-owners
supersedes:  []
overrides:   null
adds_to:     vendor-update-runbook
added:       "2026-10-06"
approved_by: "Morgan, 2026-10-06 (strength: decided): \"rules should not be repeated, but supporting repos can have additions for them\" -- this holds what the ladder set's full copy of vendor-update-runbook changed, split out the same day. Its parts were decided earlier: missing tiers made by the update, 2026-09-27; the full check at staging, not pre-staging, 2026-09-27; every repo gets all three branches, 2026-09-25. Going live by Produce: Morgan, 2026-10-28 (strength: decided), choosing it over landing the update straight on main: \"I just want to run a command and have it update and go live\", then \"Go with option 1, build it\"."
---
## Rule
**Adds to universal's [vendor-update-runbook](https://github.com/alex137/BestPractice/blob/staging/practices/vendor-update-runbook.md), for people who bring the ladder.** Everything there holds; this says how the update meets the five stages.

**Step 12 is [go-update](go-update.md)'s chain.** "Update Vendors" carries Booked for what it produced: say the landing branch out loud (`python3 tools/precedent_branches.py --landing`), commit, push, and land it on staging: `python3 tools/precedent_branches.py --land BRANCH`, with no pull request. When auto mode refuses that step, ask for it in words that name it: "Booked: land `<branch>` on staging" (a consumer, 2026-10-13: "Merge PR #N" had no pull request to name, and the person's "booked" cleared it). When the merge goes through and auto mode then refuses the check after it, the merge tool's result (`merged: true`, the merge SHA) stands for this turn and the branch check opens the next one ([go-update](go-update.md)). **Booked runs the update for you when anything is behind**: `python3 tools/precedent_merge_vendors.py` commits a finished update as a commit of its own before Booked lands the rest.

**Then it goes live: the phrase carries Produce too** (Morgan, 2026-10-28, strength: decided). Once Booked has put the update on staging, run [Produce](produce.md) right after it, the short way, without asking again, and read it back first like any stage ("Now Promote 5: Produce, staging into main (<repo>)"). **Produce moves everything waiting on staging, not only the update.** So before it runs, list what else staging holds that main does not (`git log --oneline origin/main..origin/staging`, less the update's own commits), and the report names each as having gone live with the update. That is the cost Morgan chose over landing the update straight on main. Produce's own stops still hold: the one question when the last Debut failed on that staging, a red `main` fixed in the same sitting. Where the landing branch is `main`, the update is live once it lands, and there is nothing to Produce. **In [Update All Vendors](https://github.com/alex137/BestPractice/blob/staging/practices/update-all-vendors.md) it holds for every repository the run updates:** once a repository's update has merged into its staging, Produce that repository.

**Best said "Update Vendors and make live"** ("Update All Vendors and make them live"): auto mode lets a move into `main` through only on words that name it. As of 2026-10-28 that is expected, not yet seen working. When it refuses anyway, say so in one line and ask for the move by name: "Produce: staging into main in <repo>".

**Step 6 runs the landing's check, and the full check waits.** `--land` runs the quick checks on what the update changed; the full suite runs when a Debut is asked for, and around Produce ([checks-follow-the-tier](checks-follow-the-tier.md)).

**The update gives the repo its `staging` branch.** It makes `staging` on origin when it is missing, and reports what it made. `python3 tools/precedent_branches.py --ensure-tiers` does the same on its own (`--apply` to make it); in a repo whose staging tier was `main`, it writes `"staging_branch": "staging"` into `precedent.json` for the update to commit. `base_branch` stays as it is, because it also pins where a practice source's session clone sits. **A repository still on a retired branch tier is moved onto staging by the update**, which merges the work waiting there into staging and offers the old branch for deletion as a link. From then on work lands on staging, and main takes staging by Produce.

## Detail
**Your base branch takes the update by Produce, later**, so its committed tree is often one sync behind the manifest. That is why the update's loss check reads only lines this repo changed, never lines upstream deleted in between.

## Why
Taking an update is routine work, and routine work lands on staging fast and earns the slow checks later, in a Debut or around Produce. A repo missing staging cannot take the ladder at all, and an update is the one moment someone is already looking at how it is set up.

## Story
Morgan, 2026-09-25: *"make sure that all repos with precedent vendored-in have staging and pre-staging branches? That should be part of the migration!"* And 2026-09-27 (strength: decided), on making missing tiers in the update itself, and on the check: *"The point of pre-staging is to move fast, so I want the 10 minute checks to happen at the staging level, not pre-staging."*

**2026-10-06: split out of a full copy.** From 2026-10-02 the ladder set carried its own full copy of the runbook, nearly a thousand lines, overriding universal's to say these points in the ladder's words. Every change to the runbook had to be made twice, and the copies drifted. Morgan: *"rules should not be repeated, but supporting repos can have additions for them."* This file holds only the additions; the set's copy of vendor-update-runbook is deduplicated.

**2026-10-28: the update goes live, not just onto staging.** Asked twice in one conversation whether Update Vendors and Update All Vendors put the update on main or only on staging -- only on staging, until a Produce -- Morgan said: *"I just want to run a command and have it update and go live."* Of three options (the phrase runs Produce after Booked; the update skips staging and lands straight on main; keep it and say "Update Vendors and Produce"), the session recommended landing straight on main, so that no other work waiting on staging went live with it. Morgan chose the first: *"Go with option 1, build it"* (strength: decided). The report naming what else went live is that choice's cost made visible.

**2026-10-14: pre-staging retired for everyone** (Morgan: *"Only me, go ahead and plan it. Retire pre-staging."*, strength: decided). Until then the update landed by a pull request into pre-staging wherever a repository still had three tiers ("Merge PR #N into pre-staging" when auto mode refused it), ran the fast checks there with the full check at the Promote, and made every missing tier -- `staging` from `pre-staging`, `pre-staging` from `staging`, both from `main` when neither existed. From 2026-10-09 repositories moved onto staging one at a time (ladder-in-a-repo-on-staging, now retired), and landed by `--land`; now every one does.

## Install
Nothing to install. The engine's [tools/precedent_update.py](https://github.com/alex137/BestPractice/blob/staging/tools/precedent_update.py) already makes the missing tiers when the ladder is in force (`ensure_tiers` in [tools/precedent_branches.py](https://github.com/alex137/BestPractice/blob/staging/tools/precedent_branches.py)), and says nothing about tiers to anyone else; [tools/precedent_merge_vendors.py](https://github.com/alex137/BestPractice/blob/staging/tools/precedent_merge_vendors.py) is what Booked runs.
