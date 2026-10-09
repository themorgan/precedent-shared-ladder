---
slug:        the-boildown-on-the-ladder
title:       "Adds to the-boildown, with the ladder: the first line names the stage, and a pending Produce never holds the archive line"
tier:        on-demand
severity:    default
applies_to:  ["**"]
applies_to_why: "Fires with the rule it adds to: every reply that ends a turn, reached by the reply gate. No path locus."
occasion:    ""
gates:       ["reply"]
gates_why:   "The same moment as universal's the-boildown, so the two load together at the reply gate."
index_clause: "first line names the stage; only a red main holds the archive line"
checked_by:  null
defines:     []
status:      active
in_force_at: null
expires:     null
supersedes:  []
overrides:   null
adds_to:     the-boildown
added:       "2026-10-06"
approved_by: "Morgan, 2026-10-06 (strength: decided): \"rules should not be repeated, but supporting repos can have additions for them\" -- this holds what the ladder set's full copy of the-boildown changed, split out the same day. Its parts were each decided earlier: the stage in the first line, 2026-09-29; a Promote never blocks archive, 2026-09-25; never suggest a Promote another window is running, 2026-09-27; Promote lines only for this session's own batch, 2026-09-29. Updated 2026-10-09 for the ladder without pre-staging, Morgan: \"Act on the ladder plan\" (precedent-shared-ladder spec/LADDER_REDESIGN_PLAN.md) -- the session that ran a Produce waits for GitHub's test and fixes a red main before it stops."
---
## Rule
**Adds to universal's [the-boildown](https://github.com/alex137/BestPractice/blob/staging/practices/the-boildown.md), for people who bring the ladder.** Everything there holds; this changes three points of it.

**The first line also names the stage.** After the branch, in parentheses, which of the five stages the work has finished -- or is in:

- **The work of this session is now on:** `staging` in BestPractice (you have finished step 3 of 5, Booked)

| Where the work is | What the parenthesis says |
|---|---|
| Nothing written yet: a plan was said, or a question answered | no branch yet (you have finished step 1 of 5, Consider) |
| A local branch, not pushed | you are in step 2 of 5, Act -- not pushed yet |
| A feature branch, pushed | you have finished step 2 of 5, Act |
| The person's landing branch (`staging`, or `pre-staging` for someone still on it) | you have finished step 3 of 5, Booked |
| `staging`, and Run tests passed on its current commit | you have finished step 4 of 5, Run tests |
| `main`, GitHub's test after the merge still running, or failing and being fixed | you are in step 5 of 5, Produce -- GitHub's test is still running (or: main is red, being fixed) |
| `main`, GitHub's test passed (or none runs here) | you have finished step 5 of 5, Produce |

The stage is read from where the work is, not from what was asked. A stage still under way says "you are in", not "you have finished": a pull request open into the landing branch but not merged is in step 3, and the line names the feature branch the work is actually on. The step goes before the word here, which answers [stage-word-carries-its-step](stage-word-carries-its-step.md) for the reply's first stage word.

**A Produce still to run never holds the archive line.** Work that has landed on staging is on `origin`; moving it to main is the pipeline's next step toward live, whenever the person chooses, and any session can run it later. Neither does a Run tests nobody asked for. It never fails archive condition 1, and it belongs with the things the closed list of blockers names as never holding the line. It gets one plain line in The Boildown -- only when the batch holds this session's own work -- and nothing more: never item 1's next steps, never item 2's blockers, never the reason behind the archive line.

**A Produce already merged does hold it, until GitHub's test passes.** The session that ran it waits on that test and fixes a red `main` before it stops ([produce](produce.md)). When it cannot, the reply says so in item 2, with the `main-test-failed` issue's link, so the next session in that repository picks it up first.

**Never suggest a Promote another window is already running.** Item 1 never asks for a Promote, a Booked (`Go update`) or a merge that another session is already carrying out on the same work -- it says that it is under way instead ([promote](promote.md)). While another window is promoting a repository, that repository gets no Promote line at all, at most a plain statement that a Promote is under way. The reply gate checks the Promote lock and says which a repository gets; a claim older than the lock's 15 minutes is not a Promote running.

## Detail
**Item 3's scope covers the Promote line too.** It reports work this session itself committed -- on a feature branch it worked on, or in a staging batch it booked into. Another session's batch waiting on its own Produce, or a sibling practice source's staging, gets no line, unless this session is blocked on it. Commits are counted the way item 3 counts them, for the Promote line as for every line that says one branch is ahead of another.

**The one exception to "never holds the line"** is a genuinely urgent reason to promote now -- a fix that something live is broken without, say -- and then item 1 names that reason concretely. "It hasn't been fully tested yet" is not one, because that is what every change on staging is until Run tests or GitHub's test.

## Why
The person kept having to work out from the rest of a reply where the work stood; one fixed first line answers it before anything else is read. And a Promote is the pipeline's business, not the session's: holding a window open for it costs the person a session they could have closed, and suggesting one another window is already running starts a race.

## Story
Morgan, 2026-09-29 (strength: decided), on the first line: *"after you say the boil down, the first bullet point should be the work of this session is now on colon and then the name of the branch, regardless of whether it's a local branch, pre-staging, staging, main, and then after that, put the parentheses for the name of the stage we're at"* -- and, on exceptions: *"I think there is no exception. Even if there's planning, then there's no branch. But just say you have finished the stage, consider, stage one of five."*

Morgan, 2026-09-25 (strength: decided): *"promotion should NEVER be a blocker to archive a session (unless there is a very urgent reason to do so). Promotion is about the pipeline to get it to live, and that shouldn't stop us from closing a session."* And 2026-09-27 (strength: decided), after the per-turn line told him "a Promote can move them" twice while another window was promoting: *"NEVER recommend a promote when another session is already doing it!!!"* And 2026-09-29 (strength: decided): *"only tell me about that promotions that I need to do *ONLY* regarding the branch/flow that I edited/worked on in that session window. If that session window didn't touch it, don't tell me I should promote it *UNLESS* our session is blocked on it."*

**2026-10-06: split out of a full copy.** Until this day the ladder set carried its own full copy of the-boildown, overriding universal's, to change the points above. Every change to the rule had to be made twice, and copies drifted. Morgan: *"rules should not be repeated, but supporting repos can have additions for them."* This file holds only the additions; the set's copy of the-boildown is deduplicated.

**2026-10-09: the ladder without pre-staging.** Morgan approved the ladder redesign ("Act on the ladder plan", `spec/LADDER_REDESIGN_PLAN.md`): Booked lands on staging, stage 4 became the optional Run tests, and Produce merges at once with GitHub's test after. The table followed, and a merged Produce whose test has not passed joined the few things that hold the archive line, since its session fixes a red main in the same sitting.

## Install
Nothing to install. The reply gate prints it with the-boildown on every reply. The ladder set's `reply_check.json` entry `boildown-first-bullet` (practice [stage-word-carries-its-step](stage-word-carries-its-step.md)) refuses a first line without the stage, and the reply gate reads the Promote lock for the line it prints per repository.
