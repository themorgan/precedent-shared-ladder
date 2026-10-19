---
slug:        promote-only
title:       Staging and main take my work by promotion only
tier:        on-demand
severity:    default
applies_to:  []
occasion:    "pushing to staging or main, or merging a pull request into either, in any repository I work in"
gates:       []
index_clause: "staging and main only by Promote or a staging-to-main PR; never a direct push"
checked_by:  null
defines:     []
status:      active
in_force_at: null
requires:    ["ladder"]
supersedes:  []
overrides:   null
added:       "2026-10-19"
approved_by: "Morgan F, 2026-10-19, moved from an individual set (there: Morgan F, 2026-09-25)"
strength:    decided
---
## Rule
**My work reaches staging and main only through the ladder's own tools.**
It lands on `staging`, the landing branch
(`python3 tools/precedent_branches.py --landing`), by `--land`, with the
quick checks. `main` takes `staging` by a pull request from Promote's
throwaway copy of it (`<date>-<me>-promote-to-main-<id>`), never from `staging` itself. A
session working for me never pushes straight to `staging` or `main`, and
never merges a pull request into either unless the gate allows its head:
a `--land` into `staging`, and `staging`'s `promote-to-main` copy into
`main`. (Pre-staging, the tier below staging until 2026-10-14, is retired;
`## Story` keeps how it worked.)

**One exception: a brand-new repository's first install goes straight to
`main`.** With no `main` yet, there is nothing to promote from and nothing
on `main` to protect, so that first push is the one direct push to `main`
a repository ever takes. A repository that already has a `main`, even one
holding only a README, is not this case: its install lands on its
landing branch like anything else. The steps are BestPractice's
[INSTALL.md](https://github.com/alex137/BestPractice/blob/staging/INSTALL.md),
section 0, "The first landing".

**A second exception: a fix for a red `main` goes straight to `main`.**
When `main`'s own GitHub test has failed on its tip, a pull request built
on that tip that fixes it may merge straight into `main`; the session then
brings the same fix into `staging`, so the two stay level. Everything else
still climbs the ladder. The merge gate lets it through only while
`main`'s test is red and only for a branch built on `main` as it stands.

**A third exception: my own content goes straight to `main`.** A change
whose every file is under the repository's `content_paths` (its
`precedent.json`), such as an "Add" to a personal to-do list, may be pushed
or merged straight into `main`; `staging` then takes it from `main` the
usual way, since a landing carries `main`'s direct work. Anything else in
the same change, `precedent.json` included, and the gates refuse it as
before.

This is my rule, not everyone's. Other people may not use the tiers this
way, so it is turned on by `"promote_only": true` in my own
`identity.json` and binds only sessions working for me.

## Detail
The push gate and the merge gate both enforce it. With the setting on,
BestPractice's [`precedent_push_check.py`](https://github.com/alex137/BestPractice/blob/staging/tools/precedent_push_check.py) refuses a `git push` to `staging`
or `main` before running any check, and [`precedent_merge_check.py`](https://github.com/alex137/BestPractice/blob/staging/tools/precedent_merge_check.py) refuses
a pull request into either from any other head. Each refusal names the way
round: land on the repository's landing branch (`--landing` names it),
then say Promote or Produce. A pull request opened against `main` because
that is the repository's default branch gets retargeted at the landing
branch.

`Promote` itself pushes from inside [`precedent_branches.py`](https://github.com/alex137/BestPractice/blob/staging/tools/precedent_branches.py), where no gate
sees it, so it is never refused.

**It outranks `go-update`'s `main` exception for me.** An ask from me to
push or merge straight into `main` lands on the landing branch and is
followed by a Promote; say so in the reply's first line (current-rule-governs)
rather than letting the gate refuse the push.

**A practice source's session clone still sits on `main`.** That pin is
deliberate (BestPractice's [`precedent_source_bootstrap.py`](https://github.com/alex137/BestPractice/blob/staging/tools/precedent_source_bootstrap.py)): the clone is
what a session reads its practices from, and a clone on another branch once
read an older tree and nearly wrote it over newer committed text. When a
session edits one of my sources, it commits on a branch of its own and
lands it on that source's landing branch, then puts the clone back on
`main`; the gate catches a push straight to a tier when it forgets.

## Why
Because a direct push skips the batching that makes `Promote` worth having.
Nothing tells me that work skipped the middle step, and the next Promote
reports "nothing to promote" for a change that never passed through it.

## Story
2026-10-14: pre-staging retired for everyone ("Only me, go ahead and plan
it. Retire pre-staging."). Until then the Rule had two routes: where the
landing branch was `pre-staging`, `Promote` moved work to `staging` with
the full check, and the gate let a pull request from `pre-staging` into
`staging` through.

2026-09-25. I asked how some changes got straight to `main` while I was
trying to run everything through `pre-staging`, then `staging`, then `main`.
In this repository alone, five changes reached `main` that day without
passing `pre-staging`: three commits from one session that had set my
`landing_branch` to `pre-staging` minutes before, a commit adding two
practices, and a pull request opened against `main` because it was the
default branch. The causes were three. This repository has no separate
`staging` branch, so its staging tier was `main`. The session-start clone
sits on `main`, so a session commits there without deciding to. And the
push gate only chose how hard to test by branch: a push to `main` got the
full check, passed, and went through.

Me, the same day: *"Yes do this but please make this an INDIVIDUAL rule for
me, because I believe that Alex and others won't necessarily use this
system."*

2026-10-08. A session installing Precedent into a brand-new repository
had no `main` to open a pull request into and no tier to promote from.
Me: *"Why not install it straight to main?"* (`strength: decided`). That
became the first-install exception.

2026-10-11. A Produce turned `main` red, and the session's fix was refused
straight into `main`; it went through `staging` and a second Produce
instead, one extra pull request. I had forgotten this rule; asked, I
approved letting a fix for a red `main` go straight there
(`strength: assented`). That became the red-main exception.

2026-10-13. Adding items to my personal to-do list went through `staging`
and a Produce like code. Me: *"since the "Add" is just _pure content_, it
shouldn't need to go through staging ... I just want to update lists
quickly and easily"* (`strength: decided`). That became the content
exception, read from `content_paths`.

## Install
Nothing to install beyond the setting: `"promote_only": true` in this
repository's `identity.json`. It takes effect in a repository once that
repository's vendored engine carries the gate, which is BestPractice's
`promote_only` change, reaching each repository through `Update Vendors`.
The gates know all three exceptions: the first install since 2026-10-08,
a red `main` since 2026-10-11, content since 2026-10-13.
No check script: the gate is the enforcement, and its tests live in
BestPractice's [`verify_harness.py`](https://github.com/alex137/BestPractice/blob/staging/tools/verify_harness.py)
(`check_promote_only_and_tier_branches`).
