---
slug:        no-ladders
title:       "\"No ladders\" starts a test session that sees what a person off the ladder sees"
tier:        on-demand
severity:    default
applies_to:  ["**"]
applies_to_why: "A phrase in a message; no file path reaches it. Routed by the `reply` gate."
occasion:    "a person says \"No ladders\", or asks to see what somebody who does not use the ladder sees"
gates:       ["reply"]
gates_why:   "The obligation is what the reply says: how to start the session, and that this one cannot become it."
index_clause: "a new session with PRECEDENT_NO_LADDERS=1; never this one; it pushes nothing"
checked_by:  null
defines:     ["No ladders"]
command:     {"No ladders": "Tell you how to start a new session that sees exactly what a person off the ladder sees -- no ladder rules, words or branches -- and that pushes and merges nothing. This session cannot switch over: it has already read the rules."}
status:      active
in_force_at: null
supersedes:  []
overrides:   null
added:       "2026-10-02"
approved_by: "Morgan F, 2026-10-02 -- the test mode is named \"No ladders\", never after a person (BestPractice spec/LADDER_OPT_IN_PLAN.md D13, strength: decided)"
---

## Rule

**When the person says "No ladders", tell them how to start a new session
that sees what a person off the ladder sees, and do not pretend this one
can become it.** A running session has already read the ladder's rules, and
nothing unloads text already read.

The new session needs the environment variable `PRECEDENT_NO_LADDERS=1`
from its start:

- **In the cloud:** a second environment that sets the variable, and a new
  session started in it.
- **On their own computer:** the variable set in the shell before the
  session starts.

That session loads none of the ladder: no set that provides it, and none
of the person's own rules that require it. Its work lands where a person
off the ladder lands it, and **its push and merge gates refuse everything**,
since it exists only to look. Say that too, so a refused push there is not
a surprise.

To check that a session is one, run `python3 tools/precedent_ladder.py
--status`; it says when the variable is set.

## Why

The ladder is opt-in so that people who never chose it meet none of it.
The only way to know that holds is to look through their eyes, and the
person who brings the ladder cannot do that from a session already
carrying it.

## Story

Decided 2026-10-02, while the ladder was being moved out of the universal
set into this one: the person who uses it wanted a reliable way to see the
system as a colleague who does not, without naming that colleague anywhere.
A switch inside a running session was considered and dropped: it cannot
unload rules already read, and a switch committed to the individual set
would only take effect after a Promote.
