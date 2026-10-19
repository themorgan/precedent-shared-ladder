---
slug:        handoff-only-when-blocked
title:       Hand off to a new session only what this session cannot do
tier:        on-demand
severity:    default
applies_to:  ["**"]
occasion:    "handing work to another session, or spawning one"
gates:       ["reply"]
index_clause: "hand off only what this session cannot do; check list_sessions first"
index_required: true
checked_by:  null
defines:     []
status:      active
in_force_at: null
supersedes:  []
overrides:   null
added:       "2026-10-19"
approved_by: "Morgan F, 2026-10-19, moved from an individual set (there: Morgan F, 2026-09-11; revised 2026-09-13, Morgan F, to require checking for a session that already covers the work BEFORE spawning one)"
strength: decided
---
## Rule
When I say **"give me the instructions to copy paste into a new session"** — or anything that means it — I am asking you for the residue: the part of the work *this* session genuinely cannot perform. I am not handing you permission to package up everything that is still open. Anything you can do from where you are, you do now, in this window, and the handoff does not mention it.

Universal [`prompt-please`](https://github.com/alex137/BestPractice/blob/staging/practices/prompt-please.md) owns the handoff's form -- a paste block, never a session this one creates; this rule decides what goes in it.

Two things qualify an item for a handoff, and nothing else does:

1. **The work needs a session rooted somewhere this one cannot write**, and you have *established* that rather than assumed it. Established means you tried and were refused: `git push --dry-run` to that repository came back with a denial, `add_repo` with `access: "push"` refused, a tool call returned a scope error naming the repository. A refusal you can quote is a fact; "I am probably not allowed" is not.
2. **I explicitly said I want a new session** — to clear the context, to start from a clean slate, whatever the reason. My saying so ends the question; you do not have to establish anything.

Never open a handoff because you inferred this session was ending. *"I will then close you"* describes what I do afterwards. It does not convert work you could have finished into work for somebody else, and a session that treats it that way hands me back a job I asked it to do.

**Establishing that THIS session cannot do the work is necessary and not sufficient. Before a session is spawned, check whether one already covers it.** Run `list_sessions` and match on the target repository. If a live session is already on that work, do not spawn: name it and tell me to continue there, which is [`dont-race-another-window`](https://github.com/alex137/BestPractice/blob/staging/practices/dont-race-another-window.md) applied to a window that does not exist yet. **A BLOCKED session is the sharpest case and the easiest to get wrong** -- one waiting on an answer from me needs the answer, not a sibling, and spawning beside it buys a second branch on the same files while the first sits unanswered. Send me to it instead.

The check has to happen here, at the moment of spawning, because there is no later point where it is possible: a session spawned into a repository this one could not attach cannot enumerate that repository's other sessions either, so the burden cannot be passed downstream. This is the same move as the capability check above -- measure rather than assume -- asked about a different question. That one asks whether I CAN do it; this one asks whether it is ALREADY being done, and satisfying the first says nothing about the second.

A handoff is normally **partial**, and that is the point. Three open items, one of which is in a file you already have open in the repository you are already rooted in: you fix that one, and the handoff document carries the other two. Sorting them is the work; a document listing all three is the work not done.

## Detail
**Say what you tried, next to each item you hand off.** One clause per item, naming the command or tool call and what it said back — *"`git push --dry-run` to this repository returns 403, `not in this session's authorized repository set`"*. That clause is what makes the item checkable by me at a glance, and writing it is also the check on you: an item you cannot write that clause for is an item you have not established, which means it is not a handoff item yet. Go and find out first.

**The forbidden move is the plausible one.** Nothing about a handoff looks wrong from the inside. Every item in it is real, every item is still open, and the document reads as thorough — which is exactly why the over-wide handoff survives being written and reaches me. The failure is invisible in the artifact and visible only to me, a window later, when I paste instructions into a fresh session for a fix that was two minutes' work in the window I just closed.

**The cost is asymmetric, and it lands entirely on me.** Attempting something you turn out not to be able to do costs one refused command and ten seconds. Handing me something you could have done costs me a window, a paste, a fresh session's ramp-up, and — the part I actually object to — the routing. I have on the order of a hundred tabs open. Working out which of them is rooted in what, so I can decide where your instructions should go, is the specific chore this rule exists to stop generating.

This is the same shape as [`fresh-before-write`](https://github.com/alex137/BestPractice/blob/staging/practices/fresh-before-write.md)'s core move, applied to capability instead of freshness: **measure the thing rather than assume it**, because the assumption fails silently and the measurement is cheap. There, a session assumed its checkout was current; here, a session assumes it is fenced out. Both are one command away from knowing.

## Why
Morgan, 2026-09-11, raising this himself and framing it as standing — "now and always":

```text
I am going crazy because 1000 times in the last days (it seems) You haven't been able to do things because your session wasn't 'rooted' in the right repo. And I don't want to spend half my life just checking which of the 100 tabs is rooted in what, It is confusing and frustrating. So when I say to you - now and always - 'give me the instructions to copy paste into a new session' it means *when you need to be 'rooted' in something different for some reason, if you can't do it yourself (unless explicitly I tell you I want a new session to clear the context or something).
```

"1000 times in the last days (it seems)" is his own count and carries his own hedge; the point does not rest on the figure.

## Story
2026-09-11, in a session working on `precedent-beta-v01` (alex137/BestPractice). Morgan asked for "instructions for a new session… I will then close you", covering three open failures. The session put all three into the handoff document. One of them had its fix in a file the session already had open, in the repository it was already rooted in.

He came back with:

```text
I don't understand why you told me to give that to another session if you could fix it yourself.
```

He was right. The session did that item itself, in about twenty minutes, and it merged as [#207](https://github.com/alex137/BestPractice/pull/207).

The other two items genuinely were behind the cross-owner wall, and this is the half of the story that keeps the rule from becoming "never hand off". They were **measured, not assumed**: `git push --dry-run` to that repository returned 403 — `not in this session's authorized repository set` — and `add_repo` with `access: "push"` refused with `cross-tier adds are not supported in v1`. Two refusals, quotable, on the record. Those two belonged in the handoff. The third never did.

Recorded here because the instruction existed only in that thread. Nothing wrote it down, so nothing carried it into the next session — the `repo-is-memory` failure, named in Precedent's own catalogue on `precedent-beta-v01` (alex137/BestPractice).

## Install
No mechanical check, same class as `the-boildown` and `audience-register`: the artifact is the text of a chat reply, which this repository does not hold and a repo-scoped check script cannot read. Nothing distinguishes, after the fact, a handoff that correctly carried two blocked items from one that should have carried one — both leave the same absence of a commit behind.

What stands in for it is the per-item clause the Detail section requires. A handoff item that names the refusal it is based on is auditable by me in the reply itself, which is the only place the evidence ever exists; an item with no such clause is the tell.

`gates: ["reply"]` for the moment the rule actually fires. A handoff is something you write at the end of a turn, so the reply gate reaches it — but note the rule's real demand comes earlier, when you decide to do the work instead. By the time the reply is being written the fix is either in or it is not.
