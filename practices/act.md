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
checked_by:  tools/checks/check_session_branch_name.py
ships:       ["tools/branch_name_guard.py", "tools/precedent_branch_rules.py"]
hooks:       [{"event": "pre-push", "run": "tools/branch_name_guard.py", "args": ["--pre-push"]}, {"event": "PreToolUse", "matcher": "Bash", "run": "tools/branch_name_guard.py", "args": ["--commit-note"]}]
defines:     ["Act"]
command:     {"Act": "Stage 2 (Promote 2): build the change, on this session's own feature branch, pushed to GitHub so a lost session does not lose it -- not yet shared.", "Build": "The same as **Act**."}
status:      active
in_force_at: null
supersedes:  []
overrides:   null
added:       "2026-10-02"
approved_by: "Morgan F, 2026-10-02, withdrawn from the universal set BestPractice, which keeps no copy (there: Morgan, 2026-09-27 -- Act lives on the session's temporary (feature) branch and \"booked is all about moving it from there to pre-staging so ... it won't get lost\"). Amended 2026-10-06, Morgan, \"Please evaluate and act\" on a session's finding that this rule and Claude Code on the web's designated branch contradicted each other (strength: assented; the wording is the session's). Amended 2026-10-11, Morgan: the username in every branch name, right after the date, and the rule and its checks only for people on the ladder (strength: decided). Amended 2026-10-16, Morgan: the harness's own name is refused, not let through -- \"Both, booked\" to the push refusal and this set's check (strength: decided). Amended 2026-10-16, Morgan: the enforcement lives here with the rule -- \"Rewrite it so it is entirely in ladders including the enforcement\" -- shipped as tools/branch_name_guard.py and run at every push by the engine's pre-push hook point, approved \"just for the branch related check\" (strength: decided)"
strength:    decided
---
## Rule
**Act is step 2 of the five-stage ladder ([promote](promote.md)): make the
change.** The work lives on this session's own **feature branch** -- the
short-lived branch named like `<date>-<username>-<slug>-<session>-<random>` -- and is **pushed
there**, so a reclaimed container loses nothing. It is not shared yet:
nothing reaches staging until [Booked](go-update.md).

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
without stopping to ask. **It covers any sister branch, a rename included;
only a step up the ladder -- into staging or main -- needs the person's
word** (Morgan, 2026-10-11, strength: decided: "it's okay to move to
sister branches like renaming without my permission (you need my
permission only for the ladder upgrades like to staging or to main)"). **Every push is checked, by this set's own
[tools/branch_name_guard.py](../tools/branch_name_guard.py)**, which act
ships and declares as a git `pre-push` hook: it refuses a push to the
harness's own name, new or not, and a new session branch named by hand,
printing the rename command either way (Morgan, 2026-10-15, strength:
decided: "I keep on asking you to do this but again and again you are not
doing it"). It runs from the global pre-push the commit-identity hook
installs, so it holds in a session rooted above its repositories, which
loads no repository's settings; and the engine refuses the push outright
while a practice source did not load, so a ladder set that failed to clone
stops the push instead of switching this off (Morgan, 2026-10-16,
strength: decided: "Enforcement should live in the same support repo where
the practice is"). **Work on a harness-named branch is never Booked or
Produced either:** the same guard judges a push to `staging` or `main` by
the branch it comes from -- the one `--land` was asked to land, which the
landing names to the push, or the local branch of a plain `git push` --
and refuses a harness name or one typed by hand there, pushed before or
not (2026-10-17). A Produce moves only what is already on staging, through
a copy branch the naming tool names. This rule's practice check reads the
checkout's branch in the full check besides. `git branch -m` keeps every
commit, so no refusal loses anything.

**Outside the session, GitHub itself can refuse it.**
[tools/precedent_branch_rules.py](../tools/precedent_branch_rules.py)
reports whether each repository has a ruleset that stops anyone creating a
`claude/**` or `session/**` branch. **It is opt-in, per person:** anyone
-- Morgan, Alex, anyone -- turns it on with `"github_branch_rules": true`
in their own identity.json or user-level config, and nothing changes for
someone who has not (Morgan, 2026-10-16, strength: decided). Opted in,
`--apply` adds the ruleset to the named repositories their own GitHub
account owns, and refuses anyone else's: a ruleset binds everyone who
pushes there.

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

**2026-10-14: pre-staging retired for everyone** (Morgan: *"Only me, go ahead and plan it. Retire pre-staging."*, strength: decided). Until then Booked moved the work from the feature branch to pre-staging, as the approval quotes; now it lands it on staging.

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

Later that day a session got the first-commit note and stayed on the
harness branch anyway: its opening instructions forbade pushing elsewhere
without explicit permission, and the note said "switch" without saying
that this rule is the permission. The rule said it; the note did not, and
the session had not loaded the rule. Morgan asked why, then said moving to
any sister branch needs no permission, only a step up the ladder does
(strength: decided). The sentence above records that, and both of the
naming tool's notes now say it too.

**The harness's name, refused**, 2026-10-16. On 2026-10-15 five sessions
in one consumer worked and pushed under `claude/` names, the session that
noticed among them: it got the note on every commit and every push, and
still followed its opening instructions over it, because the push went
through either way. Morgan, on hearing it was the fourth round since
2026-10-06: "I am very unhappy because I keep on asking you to do this but
again and again you are not doing it and the old branch names keep on
being used." Asked whether a fix would actually enforce it, he chose both
halves and "all in shared ladders, because this is just for people who use
that shared set": the engine's push refusal, which already applies only on
the ladder, and this rule's own check.

**2026-10-17: the landing it never saw.** The very deep check of that day
found the second half above was false: a landing runs the quick tier,
which runs no practice check, and the guard read only the branch a push
goes to, so a bare `--land` put an unpushed `claude/` branch on staging
with nothing refusing it, and a plain push of one to staging went through.
Morgan: *"Fix the other issues you found including the checks that never
run. Tell me what you decide. I will be offline so don't wait for me.
Approved, act, and Booked."* Chosen by the session under that delegation:
the guard judges what a push to staging or main comes from, and `--land`
names that branch to the push's hooks and pushes from the person's own
checkout (an engine change, since the branch is gone by the time git's
hook runs).

## Install
The naming tool ships with the engine ([precedent_branch_name.py](../tools/precedent_branch_name.py) in
[tools/precedent_vendor_engine.py](../tools/precedent_vendor_engine.py)'s
`ENGINE_FILES`); it reads the session ID through
`precedent_detect.this_session_id()` and the date through
`precedent_time`. The reply gate already says when a feature branch holds
work that has not landed.
