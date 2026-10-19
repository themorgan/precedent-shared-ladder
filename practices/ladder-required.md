---
slug:        ladder-required
title:       For me, work climbs the five stages -- a plan first, each stage read back, nothing left on a feature branch
tier:        on-demand
severity:    default
applies_to:  ["**"]
occasion:    "starting to build anything for me, landing it, or ending a session that built something"
gates:       ["reply"]
index_clause: "for me: plan first, read back each stage, never leave work on a branch"
index_required: true
checked_by:  null
defines:     []
status:      active
in_force_at: null
requires:    ["ladder"]
supersedes:  []
overrides:   null
added:       "2026-10-19"
approved_by: "Morgan F, 2026-10-19, moved from an individual set (there: Morgan F, 2026-09-27/28 -- the five stages are optional for everyone and required for me (BestPractice spec/FIVE_STAGES_AND_OUR_LANGUAGE_PLAN.md); the archive guard assented, 'Okay, I like these ideas')"
strength:    decided
---
## Rule
The five stages (the ladder set's `promote` practice, in
precedent-shared-ladder: Consider, Act, Booked, Debut, Produce) are optional
for everyone else. **For me they are the
way work goes:**

1. **Consider before Act, every time.** Before building anything, say the
   plan -- and for most work that is one sentence: what will change and
   where. A bigger plan only when the work needs it. Never a document the
   work didn't need.
2. **Read back every stage before it runs**, with its number, word and
   synonym, and the repo and branches: "Now Promote 3: Booked, the Shared
   Save -- moving `2026-10-17-themorgan-...` onto staging (BestPractice)." That goes
   for "Go update" too: for me it is Booked.
3. **Before Booked, judge whether the work is ready** -- finished, checks
   passing, nothing half-edited. If you think it isn't, say so and ask what
   I meant instead of booking it; I may have meant a higher step, like
   moving work booked earlier up to staging. This is the one stage that may
   stop to ask.
4. **Never end a session with work sitting on a feature branch.** If this
   session's work reached Act but not Booked, don't tell me I can archive:
   say where the work is and recommend Booked -- or name the branch and say
   plainly that it is meant to be dropped.

## Why
Work kept getting built without a plan anyone could see, and finished work
kept getting stranded on feature branches: `claude/graduate-synonym` held
two finished commits for days, with a warning printed the whole time. The
ladder makes the plan and the landing steps I can see, and read-backs mean I
always know where the work is and where it is going.

## Story
2026-09-27: I proposed the five stages in a brainstorm, "all optional
(except for me)", because I can't force Alex into it. The session pushed
back on a few details -- the one-line plan so small fixes stay cheap, the
feature branch instead of the local clone, the archive guard after the
graduate-synonym branch was found stranded -- and I took them. Built
2026-09-29.

## Install
Resident through the reply gate. Point 4 is also enforced: this set's
`reply_check.json` declares `require_landed_if_says`, so the reply check
refuses "You can archive this session" while work sits on a feature
branch, unless each branch is given up with a **Branch disposition:**
line.
