---
slug:        crons-are-a-last-resort
title:       Crons and scheduled Routines are a last resort -- a person-triggered path wins when there is a reasonable one
tier:        on-demand
severity:    default
applies_to:  []
occasion:    "adding or keeping anything on a schedule -- an Actions cron, a Claude routine, any timer"
gates:       []
index_clause: "no cron or Routine a person could trigger instead; register any essential one"
checked_by:  null
defines:     []
status:      active
in_force_at: null
supersedes:  []
overrides:   null
added:       "2026-10-19"
approved_by: "Morgan F, 2026-10-19, moved from an individual set (there: Morgan F, 2026-09-25; Routines made explicit the same day, Morgan: \"remember we are limiting scheduled routines\" and \"make clear [we] are minimizing the number of scheduled routines\"); reworded 2026-10-31 to speak of the person who brings this set rather than in one person's voice, meaning unchanged, by the session under Morgan F's approval of that day (\"do your recommendations for all\", strength: assented)"
strength:    decided
---
## Rule
**Crons are unwelcome.** A cron (anything that runs on a clock: a GitHub
Actions `schedule:`, a Claude routine, a recurring timer anywhere) runs
whether or not there is anything to do. Every run costs something. Once
it's set up, nobody looks at it again. **The default answer to "should this
be a cron?" is no.**

**Scheduled Claude Routines count, and their number is kept down just
as hard.** That means every Routine a session could create: a recurring
one, a one-shot, a `send_later` reminder, a self check-in scheduled to come
back and look at a pull request. Each one fires into a session whether or
not anything changed, and each one also keeps its session from being
archived. **The default answer to "should I schedule a Routine for this?"
is no** too. Before creating one, look for something that already fires:
a pull request's own events, a Routine already in place that could take
the work on, or the person's next message. A Routine that is kept goes
through the same bar as a cron below, and gets the same ask first.

**Prefer a person-triggered path whenever there is a reasonable one**, in
this order:

1. **Hang it on something the person already does.** Examples: a push, a
   merge, a config change, the start of a session.
2. **A button**, such as `workflow_dispatch` or a command they run.
3. **A reminder**: a todo item with `disposition: ask` and a `remind_on`
   date ([todo-reminder](https://github.com/alex137/BestPractice/blob/staging/practices/todo-reminder.md)),
   or Claude raising it at the right moment.

"Reasonable" means the task can wait until someone gets to it, and missing
it for a while does no harm. If that's true, it is not a cron.

**A cron is justified only when the job is essential and has to happen
without anyone remembering.** A scheduling repository's weekly sync qualifies: the
holidays have to reach the calendar whether or not anyone thinks of it. When one
qualifies:

- **Fold it in.** Every scheduled task in a repo that can share a time
  shares **one job on one schedule**
  (`actions-minutes-are-scarce`). Never add
  a second cron beside an existing one when the first could take on the
  work as a step.
- **Document it where it lives.** The workflow's header comment says why
  it has to be a cron, which person-triggered alternative was considered
  and why it lost, what each run costs, and who decided it and when.
- **Register it.** The repo's instructions file or its map carries one
  list of every schedule in force: what fires, when, and why. It is updated
  in the same commit that adds, changes, pauses or removes a cron. One
  place to see them all is what keeps them from multiplying unnoticed.
- **Watch it.** A cron that fails or stops firing without anyone noticing
  is worse than none. An essential cron is essential enough to alert on,
  the way a scheduling repository's opens an issue and pings a dead man's switch.

**Before adding any cron or scheduled Routine, ask the person.** Name the person-triggered alternative
and your recommendation in the same breath. A cron added without asking is
the failure this rule exists to prevent.

## Story
By 2026-09-16 Morgan had already paused the BestPractice sync crons ("no more
crons for now"). On 2026-09-24, a scheduling repository's build day added two
more: a weekly sync and, an hour before it, a weekly regeneration of
UPCOMING_HOLIDAYS.md. The regeneration only ever needed to run when the
sync did, so it became a step of the sync's job the next day. The one cron
left is the one that can't be a button: a job whose whole point is that
nobody has to remember it. That is the bar.

2026-10-31: the rule still spoke in the first person ("I don't like crons", "ask me")
twelve days after it moved here from an individual set. The very
deep check of 2026-10-30 found it, and the session reworded it to
speak of the person who brings this set, under Morgan's approval of
2026-10-31 ("do your recommendations for all", strength:
assented). The meaning is unchanged; quoted words stay as they
were said.
