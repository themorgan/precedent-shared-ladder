---
slug:        act
title:       "\"Act\" is stage 2: build the change on the session's feature branch"
tier:        on-demand
severity:    default
applies_to:  ["**"]
applies_to_why: "A phrase in a MESSAGE (\"Act\", \"Promote 2\") -- stage 2 of the five-stage ladder; no file path reaches it. Reached through the occasion index; no gate, since building is every moment rather than one. Decided: 2026-09-29, when the practice landed."
occasion:    "a person says \"Promote\", \"Promote N\" or a stage word (\"Consider\", \"Act\", \"Debut\", \"Run tests\", \"Produce\", \"Make live\"), or asks to plan, build, test or move work up a tier"
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
approved_by: "Morgan F, 2026-10-02, withdrawn from the universal set BestPractice, which keeps no copy (there: Morgan, 2026-09-27 -- Act lives on the session's temporary (feature) branch and \"booked is all about moving it from there to pre-staging so ... it won't get lost\"). Amended 2026-10-06, Morgan, \"Please evaluate and act\" on a session's finding that this rule and Claude Code on the web's designated branch contradicted each other (strength: assented; the wording is the session's). Updated 2026-10-09 for the ladder without pre-staging, Morgan: \"Act on the ladder plan\" (spec/LADDER_REDESIGN_PLAN.md)."
strength:    decided
---
## Rule
**Act is step 2 of the five-stage ladder ([promote](promote.md)): make the
change.** The work lives on this session's own **feature branch** -- the
short-lived branch named like `<date>-<slug>-<id>` -- and is **pushed
there**, so a reclaimed container loses nothing. It is not shared yet:
nothing reaches staging, the landing branch, until [Booked](go-update.md).

**The branch is named when Act starts, by
[tools/precedent_branch_name.py](../tools/precedent_branch_name.py), never
by hand**: `git switch -c "$(python3 tools/precedent_branch_name.py <a few
words>)"` gives `2026-10-01-feature-branch-naming-awpkv` -- the day,
what the work is, and the last five characters of the session's ID,
lowercased, so the name leads back to the session. With no session ID, or
the name already on GitHub, the tool puts five random characters there
instead and says so. A branch the harness named when the session opened,
before the task was known (`claude/hopeful-carson-yy42sb`), is left alone:
the session makes its named branch at Act and works there. **Claude Code
on the web tells a session to develop on that harness branch and not to
push to another without explicit permission: this rule is that
permission**, so the session makes its named branch without stopping to
ask. **The push check refuses a session branch named by hand**, printing
the rename command, so a hand-typed name never reaches GitHub; it lets the
harness's own name through, so a session that kept it is never left with
work it cannot push (Morgan, 2026-10-06, strength: decided: "how can we
make sure that you always use the new format for temporary branches?").

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

**2026-10-09: Booked lands on staging.** With the ladder redesign Morgan approved that day ("Act on the ladder plan", `spec/LADDER_REDESIGN_PLAN.md`), the shared branch Act stops short of is staging; pre-staging is no longer used.

## Install
The naming tool ships with the engine ([precedent_branch_name.py](../tools/precedent_branch_name.py) in
[tools/precedent_vendor_engine.py](../tools/precedent_vendor_engine.py)'s
`ENGINE_FILES`); it reads the session ID through
`precedent_detect.this_session_id()` and the date through
`precedent_time`. The reply gate already says when a feature branch holds
work that has not landed.
