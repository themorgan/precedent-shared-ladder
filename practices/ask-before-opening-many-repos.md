---
slug:        ask-before-opening-many-repos
title:       Ask me before opening more than three repositories in one session
tier:        on-demand
severity:    default
applies_to:  ["**"]
occasion:    "about to open more than three more repos in one session"
index_clause: "ask first, naming each repo and why"
index_required: true
checked_by:  null
defines:     []
status:      active
in_force_at: null
supersedes:  []
overrides:   null
added:       "2026-10-19"
approved_by: "Morgan F, 2026-10-19, moved from an individual set (there: Morgan F, 2026-10-17)"
strength: decided
---
## Rule
**Before a session attaches, clones or works across more than three
repositories beyond the ones it started with, it asks me**, naming each
one and what it needs there. It never does it as a step inside other
work, and never because a request said "everywhere"
(`everywhere-means-the-sources`).

The repositories a session starts with -- its own, and the practice
sources its setup attaches -- are not counted.

## Detail
Every repository in a session costs tokens on every turn: its
instructions, its hooks, its files in every search. A dozen of them is
most of a session's budget gone before any work, and it rarely buys
anything Update Vendors would not bring later on its own.

## Why
Morgan, 2026-10-17: "I REALLY NEED YOU TO ASK ME BEFORE YOU OPEN DOZENS OF
REPOS IN THE FUTURE IN ONE SESSSION", and "ANYTHING TO OPEN ALL THE REPOS
MUST GET SESSION USER APPROVAL, IT IS A HUGE TOKEN ORDEAL PLUS MAKES NO
SENSE TO DO THIS BEFORE A VENDOR UPDATE".

## Story
2026-10-17: a session working on BestPractice and the ladder set attached
read access to one repository after another, which BestPractice's
reach-or-ask then allowed with no limit, until 21 were attached and every
turn paid for all of them (that session's own report of what went wrong).
Morgan's words under Why followed. The same day reach-or-ask took the same
limit, so it binds people who don't bring this set too, and Morgan set the
number at three: "let's say three."
