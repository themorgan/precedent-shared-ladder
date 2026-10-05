# Repository notes for agents

This repo IS `precedent-shared-ladder` -- a **shared** source, named for its subject; any repository whose work includes that subject declares it alongside its own -- for [Precedent](https://github.com/alex137/BestPractice). [README.md](README.md) says what is here and how a practice lands.

<!-- BEGIN GENERATED: precedent-loader -->

<!-- Regenerate with: python3 tools/build_views.py -- do not hand-edit this block; `python3 tools/build_views.py --check` exits non-zero on drift. Source: practices/ -- edit the practice file, never this block. -->

## Resident block (~114 of 250 token budget, 1 of 20 practices)

**brainstorm-holds-commits.** When a conversation is a **Brainstorm** -- the person says the word, or the
thread is plainly exploratory ("I'm wondering", "what are my options", "do
you have ideas") -- **hold the edit, not just the commit: write nothing to
the repository until they authorize the work.** Research, argue the case,
propose the design; do not create, edit, commit, push, open a pull request
or merge. Answering a question inside it is not authorization, and neither
is enthusiasm for the idea. **When in doubt, it is a brainstorm.**

## Occasion index

```
When a message says "Booked", "Approved", "Book it" or "Promote 3", or plainly authorizes a merge:
  go-update — stage 3, Booked: land it on the landing branch; high-risk: PR and merge
When a message says "Update Vendors", or an upstream update is taken into a vendoring repo:
  vendor-update-runbook — source clone first, both layers move separately, then merge
When a person explicitly asks for a "very deep check" or a "full practice audit":
  very-deep-check — read every repo in force against itself, pass by pass; never routine
When a person says "Chief of Staff":
  chief-of-staff — on request only; name the window read, link each session; Promotion Reviews last
When a person says "No ladders", or asks to see what somebody who does not use the ladder sees:
  no-ladders — a new session with PRECEDENT_NO_LADDERS=1; never this one; it pushes nothing
When a person says "Promote", "Promote N" or a stage word ("Consider", "Act", "Debut", "Produce", "Make live"), or asks to plan, build or move work up a tier:
  act — stage 2: build on the session's feature branch, pushed so it survives
  consider — stage 1: pick the plan size -- one line, Brainstorm, Plan it, Write it up
  debut — stage 4: pre-staging into staging, full checks
  produce — stage 5: staging into main (production); read strictly
  promote — the next tier up, chosen from the work and said first; "Promote N" does stage N
When a person says "Prompt Please", or work belongs in a new session or needs a repo this one cannot reach:
  prompt-please — one paste-ready prompt for a new session; never a session-creating tool
When a person says "Write it up", or asks for a write-up:
  write-it-up — commit a full report: issue, options attacked, the fix that survived; link it
When building a document from a repository's content -- a Word file, a web page, a PDF, a deck -- or finding one that sits beside its sources:
  generated-docs-in-output — a document built from a folder's content goes in that folder's output/

(More on-demand practices are not listed here: one whose applies_to names real paths, or which declares a gate, is reached by those channels instead -- `precedent_paths.py FILE` and `precedent_gate.py MOMENT`. A trigger a PERSON SAYS cannot be reached that way and is always listed above. `precedent_show.py --index-omitted` names the omitted ones.)
```

## Standing instruction

Before starting work of a kind named in the occasion index above, run `python3 tools/precedent_show.py SLUG` for each listed slug to load its Rule. When editing a file, `python3 tools/precedent_paths.py FILE` prints any on-demand practice whose `applies_to` matches it, without needing the index at all. At a named moment — merging a branch, before pushing, ending a turn and writing the reply — run `python3 tools/precedent_gate.py merge|push|reply`: some practices fire at a moment rather than in a file, and no path glob reaches those. If `.precedent/SESSION_PRACTICES.md` exists, read it too: it carries the practices in force from the other sources this repo declares, which are NOT in this block and bind work here exactly as these do. It is regenerated at session start and is deliberately untracked — never commit it or quote it into a pull request.

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
