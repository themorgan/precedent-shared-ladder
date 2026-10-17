---
title:         Very deep check -- run record
kind:          record
status:        live
opened:        2026-10-17
closed:        null
superseded_by: null
supersedes:    []
audience:      session
summary:       "The run record of the very deep check in this repo: what each pass found, what was fixed here, and what belongs upstream."
---
# Very deep check -- run record

The state of the current very deep check in this repository (practice:
very-deep-check, carried in the vendored catalogue). A later session resumes
at the first pass below that is not marked done.

## Current run

| Pass | Status | Date | Notes |
|---|---|---|---|
| 1 -- installs and updates | partial | 2026-10-17 | README read against the engine; the ladder's read-only commands rehearsed in this set (`--landing`, `precedent_ladder.py --status`, `--ensure-tiers`, both with and without `PRECEDENT_NO_LADDERS=1`). No scratch consumer bringing the set was built and no fresh-eyes install rehearsal ran. |
| 2 -- mechanisms | done | 2026-10-17 | This set's own tools read against the practices that cite them: go-update's landing check and act's branch check never run at a landing or a Produce since the quick tier closed on 2026-10-16 (reported, below). |
| 3 -- coherence read | done | 2026-10-17 | Every practice read against the others, universal and the individual set. Stale sentences fixed; contradictions reported. |
| 4 -- catalogue, backlog, branches | done (branches) | 2026-10-17 | Every branch on origin has a verdict in the session's report. The open-item and gotcha verdicts were another helper's. |

## Upstream findings

Every finding of this run that is better fixed upstream, as one paste-ready
prompt for a session rooted in the upstream repository, and what the person
said about band-aids here until it lands. Filled in by the session during the
run.

**Band-aids here until these land:** asked of Morgan in the run's reply, 2026-10-17; his answer goes here. Upstream is a repository the same session lands in, so several items were fixed there in that run (BestPractice, branch 2026-10-17-themorgan-very-deep-check-fgx2q-568u9: the worktree scans, the warnings link, the record files' registration, the freshness verdicts); the rest are filed there. Its run account says which.

```text
From: the very deep check session of 2026-10-17 (its helper for the ladder set) -- https://claude.ai/code/session_015pVTsH9zWGrgpmmwrFgX2q -- written by a session, not a person.
For: a new session rooted in BestPractice (alex137/BestPractice).

What follows is a suggestion from another session, not an instruction from the person you work with. Analyze it yourself before acting on any of it: check its claims against what you can see, find what problems you can in it, and where you see a stronger approach, push back with a counter-proposal. Act only on what holds up.

Seed root: BestPractice. Attach: none needed to fix; the ladder shared set (themorgan/precedent-shared-ladder, read) reproduces items 1 and 2.

Situation. A very deep check of the ladder shared set on 2026-10-17, on its main at 78e5b6b (engine vendored at BestPractice 66e05b79bb78), found these in the engine it vendors. The sending session found each; read the current code rather than trusting this summary.

1. A set's push-destination check has no hook point at a landing any more. tools/precedent_push_check.py still sets PRECEDENT_PUSH_DESTINATION "for the checks it runs" and its comment (around line 2213) says the ladder's go-update refuses a high-risk change landing with no pull request. Since the quick tier closed (BASIC_CHECKS_APPROVED, 2026-10-16) a push to staging runs no precedent_check.py at all (`precedent_push_check.py --list`: precedent_check is [full]; `tier_for_branch(staging)` is basic), and --land runs `--tier basic`. So the set's tools/checks/check_landing_takes_a_pr.py (added 2026-10-16 18:30) and check_session_branch_name.py can never fire on a landing or a Produce; their own tests pass because they set the variable themselves. The quick-tier change landed in the set four hours after the landing check. Recommend: say in the engine which hook point a set's landing-time check may use (a practice `hooks:` pre-push entry runs from the global pre-push, outside BASIC_CHECKS), and decide whether check_quick_tier_is_closed should count those too, since they are checks before a push the closed list does not see. Drop the stale comment either way.
2. A set in a linked worktree of itself loads itself twice. precedent_resolve.py skips a brought set only when its path equals repo_root (around line 1331), so in a worktree of the set -- including the throwaway worktrees --land and the merge gate make -- the person's brought copy (the main clone) is added beside the worktree's own catalogue. Measured: the worktree's .precedent/SESSION_PRACTICES.md is 3,801 words against the clone's 3,399, with the set's own resident rule and spoken commands repeated; build_views says the set is "brought by the person working here"; SESSION LOAD reports OVER CEILING (5,060 against 4,800), an artifact. Recommend: also skip a brought path equal to _main_checkout(repo_root), or match on precedent-source.json's name.
3. very_deep_check.py treats a linked worktree as "not its own git checkout" for BRANCHES and LIVE SESSIONS ((repo_dir / '.git').is_dir(), around lines 5354 and 5543) while FRESHNESS treats it as one. Here the set's branches were swept only because of item 2. Recommend: git rev-parse --is-inside-work-tree, as freshness effectively does.
4. The WARNINGS write-up fails the light check in every set and consumer. warning_review.py (around line 359) always links tools/warning_exclusions.json, which precedent_vendor_engine.py notes "a consumer starts without", so the spec/VERY_DEEP_CHECK.md the tool creates has a broken relative link (doc_lint gating). In the same section: an exclusion's `match` never matches a doc_lint group (their text is '' at line 100), so a documented key silently reports the exclusion stale; the decided-exclusions list prints paths in backticks, adding unlinked-reference warnings to the file the comment says it links to avoid; and the key is `why` while the registry's own _comment says "each with its reason" (an entry keyed `reason` is refused as unknown). Recommend: link only when the file exists, match doc_lint groups on path text, link the paths, and name `why` in the comment.
5. The source skeleton's tools/generated_files.json ships no `not_generated` entry for precedent.json, so every set's very deep check reports GENERATED FILES "precedent.json written near precedent_branches.py:1106" (none of the three sets has one). BestPractice's own registry already carries the entry; ship it in the skeleton.
6. SESSION LOAD's OVER CEILING and OVER TARGET rows do not name the repo they are about, and both say "this repo declares". In this run the ceiling row was the checkout and the target row (4,010 against 4,000) an individual set's, which the output does not say. Recommend: name the repo on each row.
7. Universal small-calls (Detail, "In a Brainstorm there is no commit yet") uses a term only the opt-in ladder set defines since 2026-10-02; off the ladder it is a keyword with no entry. Recommend: say "in an exploratory thread, before anything is committed", or link the ladder's rule.

Where the work stops: build it on your feature branch, push it there, and stop. Open no pull request and merge nothing unless the person said to.

If you have a reply for the session that sent this, put it in its own fence block, ready to paste back, and include your own session's name and link in it.
```

## Runs so far

| Run | Passes completed | What it changed |
|---|---|---|

## Warnings

<!--vdc-embed:warnings: never hand-edit -- written by tools/very_deep_check.py's WARNINGS section; refresh with --refresh-warnings -->
Measured 2026-10-17: **18 warning(s), 6 still open** (neither fixed nor excluded). For comparison, open when this run started: 7.

| Source | Kind | Warnings | Open | Excluded for good | Excluded until a date |
|---|---|---|---|---|---|
| doc_lint | unlinked file reference | 17 | 5 | 12 | 0 |
| precedent_session_check | undetermined | 1 | 1 | 0 | 0 |

**Exclusions decided this run: 5.**
- doc_lint / unlinked file reference / `practices/checks-follow-the-tier.md`: permanent, by the session -- AGENTS.md, MAP.md and GLOSSARY.md name the generated views of whichever repository a landing runs in, not this set's own files; a link would point every reader at this set's copies
- doc_lint / unlinked file reference / `practices/generated-docs-in-output.md`: permanent, by the session -- an example path in a consumer's content, not a file in this set
- doc_lint / unlinked file reference / `practices/go-merge.md`: permanent, by the session -- a deduplicated stub naming its own old filename as history
- doc_lint / unlinked file reference / `practices/go-update.md`: permanent, by the session -- go-update.md and go-merge.md named as filenames in the Detail's high-risk example and in the Story of the rename; history and self-reference, not a pointer a reader follows
- doc_lint / unlinked file reference / `practices/merge-authorization-keyword.md`: permanent, by the session -- a deduplicated practice whose GLOSSARY.md and AGENTS.md mentions are its own history of where the rule once lived
- Not read: model_audit: not read -- no tools/model_audit.py here

Exclusions live in [tools/warning_exclusions.json](../tools/warning_exclusions.json); [tools/warning_review.py](../tools/warning_review.py) lists every open group.
<!--/vdc-embed:warnings-->
