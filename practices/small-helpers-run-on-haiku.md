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
approved_by: "Morgan F, 2026-10-19, moved from an individual set (there: Morgan, 2026-10-11 -- \"Maybe a practice here to use Haiku 5.5 for small tasks like transcription, summarizing internally etc\", then \"Please\" to the proposal); reworded 2026-10-31 to speak of the person who brings this set rather than in one person's voice, meaning unchanged, by the session under Morgan F's approval of that day (\"do your recommendations for all\", strength: assented)"
strength:    decided
---
## Rule
**A helper whose job is reading, summarizing, transcribing, sorting or
pulling facts out of text runs on the smallest model**: pass `model: "haiku"`
when spawning it (Haiku 5.5 as of 2026-10-11). The helper returns lines; the
session that spawned it does the judging and the writing the person will read.

**Small model, not small cost.** Every helper carries a fixed load before it
does anything, about 100,000 tokens for a single tool call (measured
2026-10-11), and each tool call it makes adds to that. So:

- **one helper per job**, never one per item or per system;
- **few calls**: one search per source, filtered at the source, and open an
  item only when its title isn't enough;
- **give the person the cost** in the reply when it was a large job: tokens, tool
  calls, minutes, from the helper's own report.

**A helper's "save it exactly" is a retype, not a copy.** A helper writes
a file by typing what it read, so a long tool result can come back altered
with nothing to say so (2026-10-28: a 40,000-character transcript,
"retyped ... the byte-for-byte match is not verified"). When the harness
already saved the result to a file (a result too large for the context
lands in the session's tool-results folder, byte for byte), copy that file
instead. A brief that asks a helper to save anything verbatim names the
check the copy must pass against the tool's own output (its length, its
line count, or its first and last timestamp), and the helper reports that
check, passed or failed.

Haiku makes each token cheap. It does not make the fixed load go away.

## Story
The first "Catch me up" in a personal repository, 2026-10-11, ran on one Haiku helper:
191,082 tokens over 24 tool calls, against a hoped-for 100,000. Most of the
difference was calls, not reading. Morgan asked the same day for Haiku on
small internal jobs as a standing rule. The universal
`session-spend-follows-the-task` says the same about whole sessions; this
says it about helpers, which that rule's occasion never reaches.

2026-10-28: a helper asked to save a 40,000-character transcript exactly
reported it had "retyped" it and that "the byte-for-byte match is not
verified"; the harness had already saved the same result to a file that a
plain copy would have carried intact.

2026-10-31: the rule still spoke in the first person ("the writing I will read", "give me the cost")
twelve days after it moved here from an individual set. The very
deep check of 2026-10-30 found it, and the session reworded it to
speak of the person who brings this set, under Morgan's approval of
2026-10-31 ("do your recommendations for all", strength:
assented). The meaning is unchanged; quoted words stay as they
were said.
