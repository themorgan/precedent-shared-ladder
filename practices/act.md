---
slug:        act
title:       "\"Act\" is stage 2: build the change on the session's feature branch"
tier:        on-demand
severity:    default
applies_to:  ["**"]
applies_to_why: "A phrase in a MESSAGE (\"Act\", \"Promote 2\") -- stage 2 of the five-stage ladder; no file path reaches it. Reached through the occasion index; no gate, since building is every moment rather than one. Decided: 2026-09-29, when the practice landed."
occasion:    "a person says \"Promote\", \"Promote N\" or a stage word (\"Consider\", \"Act\", \"Debut\", \"Produce\", \"Make live\"), or asks to plan, build or move work up a tier"
gates:       []
index_clause: "stage 2: build on the session's feature branch, pushed so it survives"
checked_by:  null
defines:     ["Act"]
command:     {"Act": "Stage 2 (Promote 2): build the change, on this session's own feature branch, pushed to GitHub so a lost session does not lose it -- not yet shared.", "Build": "The same as **Act**."}
status:      active
in_force_at: null
supersedes:  []
overrides:   null
added:       "2026-10-02"
approved_by: "Morgan F, 2026-10-02, withdrawn from the universal set BestPractice, which keeps no copy (there: Morgan, 2026-09-27 -- Act lives on the session's temporary (feature) branch and \"booked is all about moving it from there to pre-staging so ... it won't get lost\"). Amended 2026-10-06, Morgan, \"Please evaluate and act\" on a session's finding that this rule and Claude Code on the web's designated branch contradicted each other (strength: assented; the wording is the session's). Amended 2026-10-11, Morgan: the username in every branch name, right after the date, and the rule and its checks only for people on the ladder (strength: decided)"
strength:    decided
---
## Rule
**Act is step 2 of the five-stage ladder ([promote](promote.md)): make the
change.** The work lives on this session's own **feature branch** -- the
short-lived branch named like `<date>-<username>-<slug>-<session>-<random>` -- and is **pushed
there**, so a reclaimed container loses nothing. It is not shared yet:
nothing reaches pre-staging until [Booked](go-update.md).

**The branch is named when Act starts, by
[tools/precedent_branch_name.py](../tools/precedent_branch_name.py), never
by hand**: `git switch -c "$(python3 tools/precedent_branch_name.py <a few
words>)"` gives `2026-10-11-themorgan-branch-naming-awpkv-q7m2x` -- the
day; whose branch it is, the person's GitHub username; what the work is;
the last five characters of the session's ID, lowercased, so the name
leads back to the session; and five random characters on every name, so a
session's second branch of the day with the same slug never needs a longer
name than its first (Morgan, 2026-10-11, strength: decided). **Every
branch a session on the ladder creates takes this shape**, except a
`data-` branch and the tier branches (Morgan, 2026-10-11, strength:
decided). The username is the `github` field of the person's
`identity.json`; git never knows it. With none declared the name leaves
it out, and the tool asks GitHub who the session is signed in as and
prints the command that records it (`--set-github <username>`): the
session offers that to the person and runs it only on their yes. With no
session ID the session part is random too, and the tool says so.

**This rule, and every check that enforces it, binds only a person on the
ladder** (Morgan, 2026-10-11, strength: decided: "Our branch naming
conventions should be in force for people who use ladders, not everyone
else"). Off it, nothing below refuses or warns.

A branch the harness named when the session opened, before the task was
known -- two random words (`claude/hopeful-carson-yy42sb`) or a few words
of the task (`claude/branch-naming-enforcement-cjm44t`), then six
characters -- is left alone: the session makes its named branch at Act and
works there. **Claude Code on the web tells a session to develop on that
harness branch and not to push to another without explicit permission:
this rule is that permission**, so the session makes its named branch
without stopping to ask. **The push check refuses a session branch named
by hand**, printing the rename command, so a hand-typed name never reaches
GitHub; it lets the harness's own name through, so a session that kept it
is never left with work it cannot push (Morgan, 2026-10-06, strength:
decided: "how can we make sure that you always use the new format for
temporary branches?"). **Let through is not unsaid:** the first commit on
the harness's name hands the session a note with the command, once per
branch, whatever word started the building (branch-name-commit-note.sh,
2026-10-11), and every push to it hands the same note again
(precedent_branch_name.harness_name_note).

**Act comes after [Consider](consider.md)**, even if the plan is one line.
A request to build with no plan yet gets the one-line plan first, in the
same reply.

**A feature branch is easy to forget**, which is why Act never ends a
session on its own. Work that reached Act but not Booked is said plainly
at the end of the reply, with Booked recommended
([the-boildown](https://github.com/alex137/BestPractice/blob/staging/practices/the-boildown.md)).

## Why
Building straight onto a shared branch skips the checks and the chance to
change course; building only in the container loses the work when the
session ends. The feature branch is the one place that is both private and
safe.

## Story
Named 2026-09-27. Morgan first wrote "local clone" for this stage, then
corrected it: he meant the session's feature branch on GitHub, and Booked
is the step that moves it somewhere it will not be forgotten.

**Branch names**, 2026-10-01. Morgan pointed out that the branches sessions
leave behind are hard to connect to what they did: the harness names a
session's branch when it opens, before anyone knows the task
(`claude/hopeful-carson-yy42sb`), and sessions that made up their own
"random" ending repeated it -- three branches in BestPractice ended in
`-7qk2`. He asked for date, slug and an identifier, then chose the
session ID's ending over random characters ("I love the idea to use the
session ID"), with random characters only where there is no ID or the name
is taken. "Yes, let's do it. Act and Booked" (strength: decided).

**The harness's branch**, 2026-10-06. A session in a consumer found this
rule and Claude Code on the web's own instruction pulling opposite ways:
the harness says to develop on the branch it named and push nowhere else
without explicit permission, and this rule says to make a named branch. It
followed the harness, and noticed that the push check let it, though this
rule then said any branch the tool did not name was refused. The rule now
says it is the permission the harness asks for, and says what the push
check actually refuses.

2026-10-07: Morgan, on the temporary branches sessions leave on GitHub: "many
of your temp github [branches] you create start with 'claude/' - I think
update the rule to eliminate that prefix". The tool's names now open with
the date (strength: decided); a harness-given name keeps its own.

**The username, and the ladder only**, 2026-10-11. In a consumer a
session took "Great" as its go-ahead, never loaded this rule, and built,
pushed and landed a whole feature on `claude/eager-volta-hfk5k3`; the push
note could not help, since that consumer's engine predated it. A session
asked to look at the fix found that the push check also refused the
harness's task-word names (this session's own,
`claude/branch-naming-enforcement-cjm44t`), and that nothing in the
engine asked whether the person was on the ladder. Morgan: every branch a
ladder session creates takes the one shape; the conventions are for
people on the ladder, not everyone; and
"what if we add to the branch name convention the name of the user ... I
think the username should be first". Asked where the username comes from
-- git knows a name and an address, never a username -- he asked for the
tool to "look it up with github's 'who am I' and offer to write it into
the identity.json" (strength: decided). The first-commit note came the
same day.

## Install
The naming tool ships with the engine ([precedent_branch_name.py](../tools/precedent_branch_name.py) in
[tools/precedent_vendor_engine.py](../tools/precedent_vendor_engine.py)'s
`ENGINE_FILES`); it reads the session ID through
`precedent_detect.this_session_id()` and the date through
`precedent_time`. The reply gate already says when a feature branch holds
work that has not landed.
