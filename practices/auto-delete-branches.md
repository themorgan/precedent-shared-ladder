---
slug:        auto-delete-branches
title:       A branch that just merged clean is deleted locally without asking -- and its remote is handed over as a one-click link, never deleted
tier:        on-demand
severity:    default
applies_to:  ["**"]
occasion:    "a branch this session merged finishes a clean merge"
gates:       ["merge"]
index_clause: "delete a just-merged branch locally, unasked; hand over the remote as a link"
index_required: false
checked_by:  null
defines:     []
status:      active
in_force_at: null
supersedes:  []
overrides:   null
added:       "2026-10-19"
approved_by: "Morgan F, 2026-10-19, moved from an individual set (there: Morgan F, 2026-09-19. Amended 2026-09-22, Morgan, in his own words -- \"the right one is to never delete a remote branch but to tell the user to\" -- after this file was found still instructing a session to run `git push origin --delete`, which the universal practice never-delete-a-remote-branch had forbidden by name two days earlier. He named the resolution directly rather than choosing from options; the session proposed only the shape of the edit. The local half, and the no-asking part, are unchanged and were not re-litigated.)"
strength:    decided
---
## Rule
Once a pull request's own head branch completes a clean merge -- the
merge command or the platform's own merge call reports success, no
conflict -- delete that head branch **locally** (`git branch -d`), without
asking first.

**The remote branch is never this session's to delete, by any route.**
[`never-delete-a-remote-branch`](https://github.com/alex137/BestPractice/blob/staging/practices/never-delete-a-remote-branch.md)
(universal) lists the forbidden routes by name -- `git push origin --delete`
and `git push origin :<branch>`, the GitHub Model Context Protocol server,
the REST or GraphQL API by hand, a dispatched Actions workflow, a subagent --
and it is not overridden here. **Hand the remote branch to me instead**, as
the one-click filtered link
[`branch-delete-links`](https://github.com/alex137/BestPractice/blob/staging/practices/branch-delete-links.md)
(universal) specifies, in the same reply that reports the merge. That
practice owns the mechanism -- the `/branches/all?query=` form, the
percent-encoding, the substring caveat, and the fact that the page afterwards
reads *"no branches matched"* -- and it is not restated here.

This reaches exactly one branch: the head branch of the pull request that
just merged -- never the branch it merged *into*, never any other branch
in the repository, and never a branch before its own merge has actually
landed. A branch still under review, still failing its checks, or only
proposed for merge is untouched. Neither is a **sync merge** -- bringing
the base branch's own new commits into a working branch to catch it up,
`go-update`'s own first step -- because that merge's head is the base
branch, not the working branch, and the working branch has not merged
anywhere yet; nothing here fires from it. If what just served as a pull
request's head is a protected branch or the repository's own base branch,
that is not the ordinary case this rule describes, and the session stops
and says so rather than deleting it.

## Detail
`git branch -d` refuses a branch whose commits are not literally reachable
from the branch it points at -- exactly what happens after a squash or a
rebase merge, the two GitHub itself offers alongside an ordinary merge
commit. The PR reports **Merged**, and `-d` still fails, because the
squashed commit on the base branch has a different SHA than anything on
the source branch ever had. That refusal is not the branch being unmerged;
it is `-d`'s ancestry check not recognizing a squash. Confirm the merge
actually happened through the platform itself -- the PR's own merged
state, not a guess from the failed `-d` -- before deleting that one branch
with `-D` instead. `-D` is never the default: reached for only after that
confirmation, on the one branch just confirmed, never as a routine
substitute for `-d`.

## Why
A branch that already merged clean has nothing left to protect, and keeping
it costs a small, constant tax of clutter and future confusion about which
branches are still live. **Locally, a session doing the deleting itself,
right when it already knows the merge succeeded, is strictly better
information than a person clicking a button minutes or days later on trust
alone** -- and a local delete touches no remote, is reversible from the
reflog, and is ordinary housekeeping that the universal practice permits
outright. That half is the call this file exists to make:
BestPractice's own default is to leave the whole thing to a person, and
here it is automatic and unasked-for.

**The remote half went the other way, and this file argued the wrong side of
it for three days.** Until 2026-09-22 the text above told a session to run
`git push origin --delete` as the same reflex. The case against that is not
that deleting the wrong remote branch is expensive -- it is that a session
running in Claude Code on the web *cannot remove a remote ref at all*, so
every attempt is a refusal, and the failure mode observed is a session
working through the forbidden routes one at a time looking for one that
sticks. What I get out of the deletion is one click on a row that is already
on screen; what the attempt costs is a session burning a turn rediscovering
a settled fact. So the remote is mine to click and the link is the session's
to produce.

Not universal: this binds only sessions that bring this set, so it changes
nothing about how anyone else's repository, or a session working there
without this set, handles its own branches. (It was written for one
person's individual set and moved here on 2026-10-19; until the very deep
check of 2026-10-30 this paragraph still said it bound only that set's
sessions.)

## Story
Raised in a BestPractice session (`session_0176kGXXBqRt9oUeqTFPSDGz`,
"Automatic branch deletion configuration") asking about automating branch
deletion there. Recognized in that conversation as a personal habit rather
than a rule for the shared repository -- a practice only binds a session
that resolves its source, and `precedent-individual` is a source only my
own sessions attach, so writing it here reaches every project I work in
without touching BestPractice's own default for anyone else. Handed off
to a session on `precedent-individual` itself to write and land.

**Amended 2026-09-22, and the way it was found is the part worth keeping.**
Nothing mechanical caught it. `never-delete-a-remote-branch` landed universal
on 2026-09-21 -- asked for in my own words, after a session tried several
routes to delete a remote branch in succession -- and this file, in a
different repository and never re-read, went on saying the opposite. Both
carried `strength: decided`; both were in force in the same session; neither
declared `overrides` against the other. The contradiction surfaced only
because a session hit the merge gate, read both, and stopped to ask which one
governed instead of picking the one that told it to act. **A newer practice
in one source does not reach back and amend an older one in another**, and
[`precedent_check.py`](https://github.com/alex137/BestPractice/blob/staging/tools/precedent_check.py)
has no check for two sources instructing opposite actions at the same moment -- which is why this sat for three days in a
catalogue that passes its own full sweep.

While the file was open, its `## Why` was also repointed: it had credited the
one-click closing link to `next-steps-after-commit`, which was deduplicated
into [`the-boildown`](https://github.com/alex137/BestPractice/blob/staging/practices/the-boildown.md)
on 2026-09-15 and no longer carries that rule.

## Install
No mechanical check. This governs a step a session takes right after a
merge it just performed -- there is no artifact afterward that
distinguishes "the session deleted this because the rule said to" from
"the branch is just gone for some other reason", the same gap
`go-update`'s own Install names for the phrase that triggers
it. A check that only confirms the branch is absent could not tell a
correct, timely deletion from one that happened some other way, or flag
the one failure mode that would actually matter -- the wrong branch
deleted.

**The remote half is not checkable here either, but it is checkable
somewhere.** A session that tries `git push origin --delete` is running a
forbidden command rather than leaving an absent artifact, which is a
PreToolUse-shaped problem, not a catalogue-shaped one --
`never-delete-a-remote-branch` is where any such gate belongs, since it binds
every adopter and not only my own sessions.
