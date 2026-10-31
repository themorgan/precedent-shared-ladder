# Repository notes for agents

This repo IS `precedent-shared-ladder` -- a **shared** source, named for its subject; any repository whose work includes that subject declares it alongside its own -- for [Precedent](https://github.com/alex137/BestPractice). [README.md](README.md) says what is here and how a practice lands.

<!-- BEGIN GENERATED: precedent-loader -->

<!-- Regenerate with: python3 tools/build_views.py -- do not hand-edit this block; `python3 tools/build_views.py --check` exits non-zero on drift. Source: practices/ -- edit the practice file, never this block. -->

## Resident block (~154 of 250 token budget, 2 of 27 practices)

**brainstorm-holds-commits.** When a conversation is a **Brainstorm** -- the person says the word, or the
thread is plainly exploratory ("I'm wondering", "what are my options", "do
you have ideas") -- **hold the edit, not just the commit: write nothing to
the repository until they authorize the work.** Research, argue the case,
propose the design; do not create, edit, commit, push, open a pull request
or merge. Answering a question inside it is not authorization, and neither
is enthusiasm for the idea. **When in doubt, it is a brainstorm.**

**stage-words.** **3 Booked = branch -> staging; 4 Debut = only the full tests on
staging, moving nothing; 5 Produce = staging -> main.** The rest is the ladder set's `promote`.

## Occasion index

```
When GitHub Actions comes up -- its minutes, billing or spend, or a workflow written, reviewed or pushed to:
  actions-minutes-are-scarce — count jobs: one per trigger, none without a change, checks run in the session
  cost-concern-face-value — take it at face value; never answer with a free tier or unused minutes
When a message says "Booked", "Approved", "Book it" or "Promote 3", or plainly authorizes a merge:
  go-update — stage 3, Booked: land it on the landing branch; high-risk: PR and merge
When a person says "No ladders", or asks to see what somebody who does not use the ladder sees:
  no-ladders — a new session with PRECEDENT_NO_LADDERS=1; never this one; it pushes nothing
When a person says "Promote", "Promote N" or a stage word ("Consider", "Act", "Debut", "Produce", "Make live"), or asks to plan, build or move work up a tier:
  act — stage 2: build on the session's feature branch, pushed so it survives
  consider — stage 1: pick the plan size -- one line, Brainstorm, Plan it, Write it up
  promote — the next tier up, chosen from the work and said first; "Promote N" does stage N
When a person says "Write it up", or asks for a write-up:
  write-it-up — commit a full report: issue, options attacked, the fix that survived; link it
When about to open more than three more repos in one session:
  ask-before-opening-many-repos — ask first, naming each repo and why
When adding or keeping anything on a schedule -- an Actions cron, a Claude routine, any timer:
  crons-are-a-last-resort — no cron or Routine a person could trigger instead; register any essential one
When building a document from a repository's content -- a Word file, a web page, a PDF, a deck -- or finding one that sits beside its sources:
  generated-docs-in-output — a document built from a folder's content goes in that folder's output/
When handing work to another session, or spawning one:
  handoff-only-when-blocked — hand off only what this session cannot do; check list_sessions first
When pushing to staging or main, or merging a pull request into either, in any repository the person works in:
  promote-only — staging and main only by Promote or a staging-to-main PR; never a direct push
When spawning a helper agent, or handing a small task to another model:
  small-helpers-run-on-haiku — reading, summarizing, transcribing: Haiku; one helper per job, not per item
When starting to build anything, landing it, or ending a session that built something:
  ladder-required — plan first, read back each stage, never leave work on a branch
When telling the person something will be lost, discarded, or go away with the container, clone or session:
  loss-comes-with-a-verdict — never just 'it goes away': say it's fine to lose and why, or how they keep it
When the person says a change goes "everywhere":
  everywhere-means-the-sources — BestPractice and precedent-* only; other repos get it by Update Vendors

(More on-demand practices are not listed here: one whose applies_to names real paths, or which declares a gate, is reached by those channels instead -- `precedent_paths.py FILE` and `precedent_gate.py MOMENT`. A trigger a PERSON SAYS cannot be reached that way and is always listed above. `precedent_show.py --index-omitted` names the omitted ones.)
```

## Standing instruction

Before starting work of a kind named in the occasion index above, run `python3 tools/precedent_show.py SLUG` for each listed slug to load its Rule. When editing a file, `python3 tools/precedent_paths.py FILE` prints any on-demand practice whose `applies_to` matches it, without needing the index at all. At a named moment — merging a branch, before pushing, ending a turn and writing the reply — run `python3 tools/precedent_gate.py merge|push|reply`: some practices fire at a moment rather than in a file, and no path glob reaches those. If .precedent/SESSION_PRACTICES.md exists, read it too: it carries the practices in force from the other sources this repo declares, which are NOT in this block and bind work here exactly as these do. It is regenerated at session start and is deliberately untracked — never commit it or quote it into a pull request.

<!-- END GENERATED -->

## Working in this repo

- **Practices are in [practices/](practices/)**, one file per practice,
  in Precedent's practice-file format -- frontmatter plus `## Rule` /
  `## Detail` / `## Why` / `## Story` / `## Install`.
- **The loader block above is generated, and so are MAP.md and
  GLOSSARY.md** -- regenerate all three with the full
  `python3 tools/build_views.py` after any practice change, never
  `--agents-only`, and commit what it rewrites.
- **Before committing:** `python3 tools/precedent_check.py --full-sweep`
  -- `0 violated` is what matters. The bare command runs only a
  rotation slice, and a practice source runs no CI
  (universal `source-sets-run-no-ci`), so nothing else catches what
  it misses.
- **This file describes the MECHANISM, never the INVENTORY.** A rule
  goes in a practice file, where the loader dedupes it and precedence
  ranks it; restated here as prose it is invisible to both.
- **Approval** is a listed approver's own yes, in
  [approvers.json](approvers.json).
