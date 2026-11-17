---
slug:        offer-only-what-you-recommend
title:       "Adds to the-boildown: never offer what you'd advise against, except a close call or a choice that is the person's to weigh"
tier:        on-demand
severity:    default
applies_to:  ["**"]
applies_to_why: "Fires on every reply that ends a turn, reached by the reply gate with the-boildown. No path locus."
occasion:    ""
gates:       ["reply"]
gates_why:   "The moment a reply is written is when a question gets asked; it loads with the-boildown, whose item 1 is where most asks sit."
index_clause: "never offer what you would advise against, save a close call or theirs to weigh"
checked_by:  null
defines:     []
status:      active
in_force_at: null
expires:     null
supersedes:  []
overrides:   null
adds_to:     the-boildown
added:       "2026-11-17"
approved_by: "Morgan F, 2026-11-17 (strength: decided): \"you don't need to tell me things you recommend *NOT* doing, it's a waste of conversation/time/tokens\" -- first written into his individual set's so-what-test, then moved here at his word the same day: \"maybe this rule should be moved from [my individual set] to precedent ladders since it's the sort of rule that applies to everything. Also, there feels like there would be common cases that are exceptions, what are they? We should put them into the rule. (For example a very close call)\". The close call is his example; the other exceptions were proposed to him in another session and merged or dropped here where another practice already covers them."
---
## Rule
**Never offer what you'd advise against.** Ask the person only about what
you'd recommend doing. A question whose answer you'd pick as "no" stays out
of the reply: not asked, not listed as an option, not raised as "we could
also".

**Ask it anyway when your "no" is not the deciding one:**

- **A close call.** The options are nearly even: ask, say it's close, give
  your lean and what would tip it.
- **Theirs to weigh.** The choice turns on money, people, a client
  relationship, or something hard to undo, and what decides it is what they
  value or know, not your judgment: name the option and why you wouldn't.

**It cuts what you'd raise, never what you're asked or warned of.** A
question they put to you ("should I X?") gets its answer, "no" included.
"My options" still lists every real option, the rejected ones marked
([my-options](https://github.com/alex137/BestPractice/blob/staging/practices/my-options.md)). And something they are about to do, or asked for,
that you'd advise against is a warning, said plainly -- that is a risk, not
an offer.

## Detail
**Why the exceptions stop at two.** Each of the others proposed on
2026-11-17 is a case the rule never reached, already ruled elsewhere:
answering a direct question and listing every option for "My options" are
answers, not offers; a warning is a risk, which a reply never cuts; and not
doing what was asked is said in the reply's first line, with why, by
universal's [current-rule-governs](https://github.com/alex137/BestPractice/blob/staging/practices/current-rule-governs.md). They stay in the Rule as one
sentence so nobody reads the cut as reaching them.

**The close call still gives a pick.** "It's close" is not a way to hand
the comparing back. The lean and what would change it are the part asked
for, as my-options says of a close pair.

**"Theirs to weigh" is narrow.** It is not every decision the person makes;
it is one where a reasonable person who saw what you saw could still choose
the other way, because the deciding input is theirs. A technical choice
where you know the answer is not one of them, however consequential.

**What the reply gate checks.** Universal's `boildown-ask-states-its-question`
already refuses an ask in Your next steps without the session's pick, and a
close call carries one, so nothing there conflicts. The gate does not refuse
an ask whose pick is "no": whether "no" means "don't" depends on how the
question is worded ("keep it as is?" -- "no" is the change), and a warning
or a close call reads the same to a pattern. This rule is judgment, printed
at the reply gate with the-boildown.

**Relation to "A suggestion is asked once"** (the-boildown item 1): that
rule limits how often an idea you'd recommend is raised. This one decides
whether it is raised at all.

## Why
A question whose answer the session already knows is "no" makes the person
read it, weigh it, and answer it, to arrive where the session already was.
It costs their attention and the conversation's length, and it buries the
questions that do need them.

## Story
Morgan, 2026-11-17 (strength: decided), after a reply asked whether to
change something it recommended leaving alone: *"you don't need to tell me
things you recommend *NOT* doing, it's a waste of conversation/time/tokens"*.
It went into his individual set's so-what-test the same day.
He then asked for it to move to the
ladder set, *"since it's the sort of rule that applies to everything"*, and
for its common exceptions to go into the rule, naming *"a very close call"*.
Six were proposed; two survived as exceptions, and the other four, already
covered elsewhere, became the Rule's last paragraph.

## Install
Nothing to install. The reply gate prints it with the-boildown on every
reply.
