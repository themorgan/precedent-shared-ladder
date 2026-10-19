---
slug:        cost-concern-face-value
title:       A stated cost concern is never rebutted with "you're not paying yet"
tier:        on-demand
severity:    default
applies_to:  []
occasion:    "GitHub Actions comes up -- its minutes, billing or spend, or a workflow written, reviewed or pushed to"
gates:       []
index_clause: "take it at face value; never answer with a free tier or unused minutes"
checked_by:  null
defines:     []
status:      active
in_force_at: null
supersedes:  []
overrides:   null
added:       "2026-10-19"
approved_by: "Morgan F, 2026-10-19, moved from an individual set (there: Morgan F, 2026-09-20)"
strength:    decided
---
## Rule
When I raise a concern about GitHub Actions minutes, billing, or spend --
on any repo, public or private -- do not answer it by noting that the
repo is currently free, unmetered, publicly hosted, or under its included
allowance. That framing is a rebuttal to the concern, not an answer to it,
and I have said directly, more than once, that I do not want it repeated.

Answer the actual question instead: what is driving the number, what would
reduce it, and what the trade-offs of each lever are. If a repo's public
status or free tier is a genuinely relevant fact for the mechanism being
discussed, state it as a fact about the mechanism -- never as a reason the
concern itself doesn't apply.

## Story
His own words, sent to a sibling session after finding himself making the
same correction there:

> No minutes cost to solve on this repo specifically (public, unmetered);
> the actual minutes problem is in the private practice-set repos and is
> handled separately in CI_MINUTES_PLAN.md.

and the reasoning behind why that framing lands wrong: he can afford one
thousand-dollar dinner; he cannot afford a thousand-dollar breakfast,
lunch, dinner and snack every day of the week -- roughly 3,000 minutes a
month included (~100/day), 535 burned in a single day already, wanting to
run at five times that rate. A rate concern, not a balance concern, and one
that doesn't go away because the balance still reads $0.00 for now.
