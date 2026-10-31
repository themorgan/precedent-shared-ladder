---
slug:        ladder-required
title:       Work climbs the five stages -- a plan first, each stage read back, nothing left on a feature branch
tier:        on-demand
severity:    default
applies_to:  ["**"]
occasion:    "starting to build anything, landing it, or ending a session that built something"
gates:       ["reply"]
index_clause: "plan first, read back each stage, never leave work on a branch"
index_required: true
checked_by:  null
defines:     []
status:      active
in_force_at: null
requires:    ["ladder"]
supersedes:  []
overrides:   null
added:       "2026-10-19"
approved_by: "Morgan F, 2026-10-19, moved from an individual set (there: Morgan F, 2026-09-27/28 -- the five stages are optional for everyone and required for me (BestPractice spec/FIVE_STAGES_AND_OUR_LANGUAGE_PLAN.md); the archive guard assented, 'Okay, I like these ideas'); reworded 2026-10-31 to speak of the person who brings this set rather than in one person's voice, meaning unchanged, by the session under Morgan F's approval of that day (\"do your recommendations for all\", strength: assented)"
strength:    decided
---
## Rule
The five stages (the ladder set's `promote` practice, in
precedent-shared-ladder: Consider, Act, Booked, Debut, Produce) are optional
in Precedent. **For a person who brings this set they are the
way work goes:**

1. **Consider before Act, every time.** Before building anything, say the
   plan -- and for most work that is one sentence: what will change and
   where. A bigger plan only when the work needs it. Never a document the
   work didn't need.
2. **Read back every stage before it runs**, with its number, word and
   synonym, and the repo and branches: "Now Promote 3: Booked, the Shared
   Save -- moving `2026-10-17-<user>-...` onto staging (BestPractice)." That goes
   for "Go update" too: for them it is Booked.
3. **Before Booked, judge whether the work is ready** -- finished, checks
   passing, nothing half-edited. If you think it isn't, say so and ask what
   the person meant instead of booking it; they may have meant a higher step, like
   moving work booked earlier up to staging. This is the one stage that may
   stop to ask.
4. **Never end a session with work sitting on a feature branch.** If this
   session's work reached Act but not Booked, don't tell the person they can archive:
   say where the work is and recommend Booked -- or name the branch and say
   plainly that it is meant to be dropped.

## Why
Work kept getting built without a plan anyone could see, and finished work
kept getting stranded on feature branches: `claude/graduate-synonym` held
two finished commits for days, with a warning printed the whole time. The
ladder makes the plan and the landing steps the person can see, and read-backs mean they
always know where the work is and where it is going.

## Story
2026-09-27: Morgan proposed the five stages in a brainstorm, "all optional
(except for me)", because he couldn't force Alex into it. The session pushed
back on a few details -- the one-line plan so small fixes stay cheap, the
feature branch instead of the local clone, the archive guard after the
graduate-synonym branch was found stranded -- and he took them. Built
2026-09-29.

2026-10-31: the rule still spoke in the first person ("For me", "ask what I meant")
twelve days after it moved here from an individual set. The very
deep check of 2026-10-30 found it, and the session reworded it to
speak of the person who brings this set, under Morgan's approval of
2026-10-31 ("do your recommendations for all", strength:
assented). The meaning is unchanged; quoted words stay as they
were said.

## Install
Resident through the reply gate. Point 4 is also enforced where the person's own set declares it: the
individual set this rule came from declares `require_landed_if_says` in its
`reply_check.json` (this set does not, as of 2026-10-31), so the reply check
refuses "You can archive this session" while work sits on a feature
branch, unless each branch is given up with a **Branch disposition:**
line.
