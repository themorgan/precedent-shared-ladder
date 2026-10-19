---
slug:        small-helpers-run-on-haiku
title:       "A helper that only reads, summarizes or transcribes runs on the cheapest model"
tier:        on-demand
severity:    default
applies_to:  []
occasion:    "spawning a helper agent, or handing a small task to another model"
gates:       []
index_clause: "reading, summarizing, transcribing: Haiku; one helper per job, not per item"
checked_by:  null
defines:     []
status:      active
in_force_at: null
supersedes:  []
overrides:   null
added:       "2026-10-19"
approved_by: "Morgan F, 2026-10-19, moved from an individual set (there: Morgan, 2026-10-11 -- \"Maybe a practice here to use Haiku 5.5 for small tasks like transcription, summarizing internally etc\", then \"Please\" to the proposal)"
strength:    decided
---
## Rule
**A helper whose job is reading, summarizing, transcribing, sorting or
pulling facts out of text runs on the smallest model**: pass `model: "haiku"`
when spawning it (Haiku 5.5 as of 2026-10-11). The helper returns lines; the
session that spawned it does the judging and the writing I will read.

**Small model, not small cost.** Every helper carries a fixed load before it
does anything, about 100,000 tokens for a single tool call (measured
2026-10-11), and each tool call it makes adds to that. So:

- **one helper per job**, never one per item or per system;
- **few calls**: one search per source, filtered at the source, and open an
  item only when its title isn't enough;
- **give me the cost** in the reply when it was a large job: tokens, tool
  calls, minutes, from the helper's own report.

Haiku makes each token cheap. It does not make the fixed load go away.

## Story
The first "Catch me up" in a personal repository, 2026-10-11, ran on one Haiku helper:
191,082 tokens over 24 tool calls, against a hoped-for 100,000. Most of the
difference was calls, not reading. Morgan asked the same day for Haiku on
small internal jobs as a standing rule. The universal
`session-spend-follows-the-task` says the same about whole sessions; this
says it about helpers, which that rule's occasion never reaches.
