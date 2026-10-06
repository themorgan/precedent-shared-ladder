---
slug:        vendor-update-runbook
title:       "Deduplicated: vendor-update-runbook is universal's, with this set's addition in vendor-update-on-the-ladder"
tier:        on-demand
severity:    default
applies_to:  []
applies_to_why: "DEDUPLICATED 2026-10-06 -- universal's vendor-update-runbook is the rule, and vendor-update-on-the-ladder holds what this set adds to it. Kept so links to vendor-update-runbook.md in this set resolve; it routes nothing."
occasion:    "a link or a reference still names this set's copy of vendor-update-runbook"
gates:       []
index_clause: "deduplicated 2026-10-06; universal's rule, plus vendor-update-on-the-ladder"
checked_by:  null
defines:     []
status:      deduplicated
in_force_at: vendor-update-runbook
visible_to:  code-owners
supersedes:  []
overrides:   null
added:       "2026-10-02"
approved_by: "Morgan, 2026-10-06 (strength: decided): \"rules should not be repeated, but supporting repos can have additions for them\""
strength:    decided
---
## Rule
**Deduplicated.** The rule is universal's [vendor-update-runbook](https://github.com/alex137/BestPractice/blob/staging/practices/vendor-update-runbook.md), and what this set adds to it -- landing by Booked, the full check at the Promote, and the missing tiers -- is in [vendor-update-on-the-ladder](vendor-update-on-the-ladder.md). Read those two; nothing here is in force.

## Detail

## Why
A full copy overriding universal's meant every change to the rule had to be made twice, and the copies drifted.

## Story
Copied into this set on 2026-10-02 under the same slug, when the ladder became a set a person brings, so people who bring it read the rule in the ladder's words. Split on 2026-10-06 into universal's rule plus [vendor-update-on-the-ladder](vendor-update-on-the-ladder.md), which holds only the additions. The full copy is in this file's git history.

## Install
Nothing. Link [vendor-update-on-the-ladder](vendor-update-on-the-ladder.md), or universal's vendor-update-runbook, instead.
