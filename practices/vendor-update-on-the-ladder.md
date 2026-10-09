---
slug:        vendor-update-on-the-ladder
title:       "Adds to vendor-update-runbook, with the ladder: the update lands on staging by Booked, takes only a main that passed, and retires pre-staging"
tier:        on-demand
severity:    default
applies_to:  ["**"]
applies_to_why: "Fires with the rule it adds to: an update being taken, a moment rather than a file class. Reached through the occasion index and the merge gate, as that rule is."
occasion:    "a person says \"Update Vendors\" in a repo on the five-stage ladder"
gates:       ["merge"]
gates_why:   "The same moment as universal's vendor-update-runbook, so the two load together at the merge gate."
index_clause: "lands on staging by Booked; takes a green main; retires pre-staging"
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
approved_by: "Morgan, 2026-10-06 (strength: decided): \"rules should not be repeated, but supporting repos can have additions for them\" -- this holds what the ladder set's full copy of vendor-update-runbook changed, split out the same day. Its parts were decided earlier: missing tiers made by the update, 2026-09-27; the full check at staging, not pre-staging, 2026-09-27; every repo gets all three branches, 2026-09-25. Rewritten 2026-10-09, Morgan: \"Act on the ladder plan\" (spec/LADDER_REDESIGN_PLAN.md) -- the update lands on staging and takes only a main whose GitHub test passed -- and, for the rollout, \"make sure we have a smooth upgrade process for each. Merging the branches, telling he can delete pre-staging, updating previous mentions/links within each repo\"."
---
## Rule
**Adds to universal's [vendor-update-runbook](https://github.com/alex137/BestPractice/blob/staging/practices/vendor-update-runbook.md), for people who bring the ladder.** Everything there holds; this says how the update meets the five stages.

**Step 12 is [go-update](go-update.md)'s chain.** "Update Vendors" carries Booked for what it produced: say the landing branch out loud (staging), commit, and land it with `python3 tools/precedent_branches.py --land`, or, for a high-risk update, open the pull request into staging and merge it. When auto mode refuses that merge, ask for it in words that name it: "Merge PR #N into staging". When the merge goes through and auto mode then refuses the check after it, the merge tool's result (`merged: true`, the merge SHA) stands for this turn and the branch check opens the next one ([go-update](go-update.md)). **Booked runs the update for you when anything is behind**: `python3 tools/precedent_merge_vendors.py` commits a finished update as a commit of its own before Booked lands the rest.

**Step 6 runs the landing's quick checks.** On staging that is the fast checks on what the update changed ([checks-follow-the-tier](checks-follow-the-tier.md)); the full suite is Run tests, when asked for, and GitHub's test after the next Produce.

**The update takes only a `main` that passed GitHub's test.** It takes the newest `main` commit whose GitHub test passed, skips anything pending or red, and when that is not the newest it says which commit it took, how far behind it is, and why. Pass that line on in the reply: it is how the person hears that BestPractice's `main` is red. In an emergency, `--take-anyway <commit>` takes a named commit on the person's own words, and the report and commit message say so. This is what makes a fast Produce safe: a red `main` never reaches another repository.

**The update retires pre-staging**, in the repository's next Update Vendors after the engine carries the step (spec/LADDER_REDESIGN_PLAN.md, "Rolling it out to each repository"):

1. Work on pre-staging that staging lacks is brought into staging the same way a landing brings work in -- composed with main's direct commits, nothing dropped. A conflict stops the step and says what to merge and where.
2. Once pre-staging holds nothing staging lacks, the update says it is no longer used and gives its one-click delete link. It never deletes it, and never offers it while it holds work.
3. Wording in the repository's own files that tells a reader work lands on pre-staging, and links to pre-staging, are repointed to staging. Dated history -- Stories, gotchas, closed items, dated decisions -- is left alone and listed.
4. The generated views are refreshed.
5. One short report block says what moved, what was reworded, and the delete link.

Put that block in the reply as the update printed it. `staging` and `main` are never offered for deletion. A repository with no separate staging tier yet gets one from `python3 tools/precedent_branches.py --ensure-tiers` (`--apply` to make it); in a repo whose staging tier was `main`, it writes `"staging_branch": "staging"` into `precedent.json` for the update to commit. `base_branch` stays as it is, because it also pins where a practice source's session clone sits. From then on work lands on staging, and main takes staging by pull request.

## Why
Taking an update is routine work, and routine work lands fast and earns the slow checks later: on request, and on GitHub after the merge into main. A repo missing a tier cannot take the ladder at all, and an update is the one moment someone is already looking at how it is set up.

## Story
Morgan, 2026-09-25: *"make sure that all repos with precedent vendored-in have staging and pre-staging branches? That should be part of the migration!"* And 2026-09-27 (strength: decided), on making missing tiers in the update itself, and on the check: *"The point of pre-staging is to move fast, so I want the 10 minute checks to happen at the staging level, not pre-staging."*

**2026-10-06: split out of a full copy.** From 2026-10-02 the ladder set carried its own full copy of the runbook, nearly a thousand lines, overriding universal's to say these points in the ladder's words. Every change to the runbook had to be made twice, and the copies drifted. Morgan: *"rules should not be repeated, but supporting repos can have additions for them."* This file holds only the additions; the set's copy of vendor-update-runbook is deduplicated.

**2026-10-09: the ladder without pre-staging.** Morgan approved the ladder redesign ("Act on the ladder plan", `spec/LADDER_REDESIGN_PLAN.md`), and asked the same day for the rollout to be smooth in every repository that vendors BestPractice: *"Merging the branches, telling he can delete pre-staging, updating previous mentions/links within each repo, etc etc"*. So the update lands on staging, takes only a green `main`, and retires pre-staging in five steps.

## Install
Nothing to install. The engine's `tools/precedent_update.py` makes a missing staging tier when the ladder is in force (`ensure_tiers` in `tools/precedent_branches.py`), says nothing about tiers to anyone else, and picks the newest `main` that passed (`source_commit`, with `--take-anyway`); `tools/precedent_merge_vendors.py` is what Booked runs. The step that retires pre-staging is engine work in BestPractice, approved 2026-10-09; until a repository's engine carries it, the person empties pre-staging with a Promote into staging and deletes it by hand.
