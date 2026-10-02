# The ladder

This set holds one way of working with Claude: a ladder of **five steps**
that every piece of work climbs, from idea to what everyone gets. You say a
step, Claude does that step and nothing more, and every reply tells you
which step the work has reached.

It is **opt-in, person by person**. Nobody gets the ladder because of the
repository they work in. You get it because you asked for it, and the
people working beside you, in the same repositories, see none of it unless
they ask for it too.

## Contents

- [Who gets it](#who-gets-it)
- [The five steps](#the-five-steps)
- [How much planning: four sizes](#how-much-planning-four-sizes)
- [The three branches work climbs](#the-three-branches-work-climbs)
- [What you will see in replies](#what-you-will-see-in-replies)
- [Everyone else](#everyone-else)
- [Seeing what everyone else sees](#seeing-what-everyone-else-sees)
- [Claude Code's auto mode and Produce](#claude-codes-auto-mode-and-produce)
- [For whoever looks after this set](#for-whoever-looks-after-this-set)

## Who gets it

Anyone who adds this set to their own **individual set** (the collection of
rules that is just for them, usually a repository called
`precedent-individual`). One entry in that repository's
`precedent-source.json` does it:

```json
"brings": [
  {"name": "precedent-shared-ladder",
   "repo_url": "https://github.com/themorgan/precedent-shared-ladder"}
]
```

From the next session on, wherever you work, the ladder is in force for
you. Take the entry out and it is gone again.

**A repository never turns it on for everyone.** A repository's own
settings file (`precedent.json`) lists the rule sets everyone working there
follows, and this set is never listed there: a check refuses it. That is
what lets two people share a repository with one of them on the ladder and
the other not.

## The five steps

| Step | Say | Also | What Claude does |
|---|---|---|---|
| 1 | **Consider** | Plan, Promote 1 | Decides how much planning the work needs, and does that much (the next section). |
| 2 | **Act** | Build, Promote 2 | Makes the change on the session's own working branch, and saves it to GitHub so a lost session loses nothing. Nobody else sees it yet. |
| 3 | **Booked** | Book it, Approved, Go update, Shared Save, Promote 3 | Lands the work on your landing branch (the first of the three branches below), where the rest of the team can see it. |
| 4 | **Debut** | Test Readiness, Promote 4 | Moves everything waiting on pre-staging into staging, after the full checks pass. |
| 5 | **Produce** | Make live, Promote 5 | Moves staging into main, which is production: what everyone gets. The full checks and GitHub's own test must both pass. |

A plain **"Promote"** means "the next step up that the work needs", and
Claude says which one before it starts.

**Every step is read back before it runs**, with its number, its name and
where it goes: *"Now Promote 4: Debut, Test Readiness, moving pre-staging
into staging."* If that is not what you meant, one word stops it.

**Step 5 is read strictly.** "Produce" and "make live" turn up in ordinary
sentences, and this is the step that changes what everyone gets, so where
the meaning is a judgment call Claude asks before anything moves.

**Nothing is shared without your word.** Steps 1 and 2 happen when you ask
for the work; steps 3, 4 and 5 each wait for you to say so. An approval
passed along by another session counts only if your own individual set
says you accept those.

## How much planning: four sizes

Step 1 picks one, lightest first. Claude chooses, and names its choice, so
a wrong pick is fixed in a word.

| Size | Say | What you get |
|---|---|---|
| One-line plan | (the default) | One sentence: what will change and where. Most work needs nothing more. |
| **Brainstorm** | Brainstorm | Thinking it through together. **Nothing is written to any repository** until you say to build it. Exploratory questions ("what are my options", "I'm wondering") count as a Brainstorm too. |
| **Plan it** | Plan it | A written plan in the conversation, handed back as one block you can paste into a new session. |
| **Write it up** | Write it up, Spec it out | A full report committed to the repository: the problem, the options tried and attacked, and the one that survived. |

## The three branches work climbs

Each repository that uses the ladder fully has three shared branches, one
above the other:

- **pre-staging**: where saved work lands (step 3). Quick checks, only on
  what changed.
- **staging**: where it is checked thoroughly (step 4). Every check, on
  every file.
- **main**: production (step 5). Every check, plus GitHub's own test.

A repository with fewer branches simply has fewer steps. In a repository
that has only main, step 3 lands your work on main and steps 4 and 5 have
nothing to do. **Nothing ever creates these branches in a repository that
did not ask for them.**

When main's GitHub test is failing, a Debut still carries your own work up
to staging, and says plainly that the newest work on main was not brought
down and why. Produce waits until main's test passes again.

## What you will see in replies

- **The first time a reply names a step, its number follows**: Booked
  (step 3 of 5). Later mentions in the same reply stay bare.
- **Every reply ends with a short summary**, and its first line says where
  the work is and which step it has finished: *"The work of this session
  is now on: pre-staging (you have finished step 3 of 5, Booked)."*
- **Vocabulary** lists every word you can say, this set's included, each
  marked with the set it comes from.
- **Chief of Staff** stops the work and reports instead: what every open
  session is waiting on, what is colliding, and what waits to move up a
  step in each repository.

## Everyone else

A person who has not added this set sees **none of the above**, in any
repository, including ones you share with them:

- no step names, step numbers or ladder words in any reply, check or
  message;
- their work lands on main, unless they have chosen another branch for
  themselves;
- every check that protects the work (the leak check, the link check, the
  practice checks) runs for them exactly as for you.

The two of you can work in the same repository on the same day. Your
Debut and Produce move what is waiting; their work goes straight to main.
When their work and yours collide, your session sorts it out; they are
never asked.

## Seeing what everyone else sees

To check what a person off the ladder sees, start a **new** session with
the environment variable `PRECEDENT_NO_LADDERS=1` set (in the cloud, a
second environment with that variable; on your own computer, set it before
starting). That session loads none of this set, and it refuses to push or
merge anything, since it exists only to look. A session already running
cannot switch over: it has already read the rules.

## Claude Code's auto mode and Produce

Not a ladder setting, and nothing breaks without it. Claude Code's auto
mode has its own safety check, separate from these rules, and it treats
moving staging into main as a production deploy. It lets that through only
when your message names the move exactly, so **"Produce"** (or "Promote 5")
works and a bare **"Promote"** is stopped. A session that hits this says so
in one line and asks you for "Produce"; it never tries to get around the
check.

To make a plain "Promote" work too, add an **allow rule**. **A session
cannot do this for you**, and a repository cannot carry it. Where it goes
(Claude Code's own documentation, read 2026-09-30):

- **Cloud sessions:** your organization's **managed settings**, at
  [Admin Settings > Claude Code > Managed settings](https://claude.ai/admin-settings/claude-code).
  That needs a Team or Enterprise plan and the Owner or Primary Owner role,
  and it applies to everyone in the organization.
- **Sessions on your own computer:** `~/.claude/settings.json`, or the
  **Auto mode** tab of `/permissions`.

Paste this in, keeping `"$defaults"`: without it, the list replaces every
built-in exception instead of adding one.

```json
{
  "autoMode": {
    "allow": [
      "$defaults",
      "Precedent Promote into main: running tools/precedent_branches.py --promote --to main is allowed when the person asked in this session for Promote, Produce or Promote 5. That tool moves main only through a pull request, after the full local check and the GitHub test pass."
    ]
  }
}
```

The rule is in plain words because the check reads it as prose. Details:
[Configure auto mode](https://code.claude.com/docs/en/auto-mode-config) and
[server-managed settings](https://code.claude.com/docs/en/server-managed-settings).
Without managed settings, keep saying "Produce".

## For whoever looks after this set

This repository is a **shared practice set** for Precedent
([BestPractice](https://github.com/alex137/BestPractice)): one file per
rule under [practices/](practices/), in the format
[PRACTICE_FORMAT.md](https://github.com/alex137/BestPractice/blob/staging/spec/PRACTICE_FORMAT.md)
describes. Its [precedent-source.json](precedent-source.json) says it
**provides the ladder**, which is how the engine knows the ladder is in
force for whoever brings it.

| File | What it is for |
|---|---|
| [practices/](practices/) | The ladder's rules, each moved here whole from the universal set, Story included. Four (the-boildown, prompt-please, very-deep-check, vendor-update-runbook) are fuller copies of a universal rule; a copy here replaces the universal one for the people who bring this set. |
| [reply_check.json](reply_check.json) | The two reply rules only ladder users get: the step in the summary's first line, and a pasted prompt that lands work quoting your "Booked". |
| [our_language.json](our_language.json) | The ladder's own words, merged into Vocabulary for the people who bring it. |
| [approvers.json](approvers.json) | Who may approve a change here. |
| [leak-blocklist.txt](leak-blocklist.txt) | Terms that must never reach a public repository. |
| [tools/](tools/) | The vendored engine. Never edit it by hand; refresh it with "Update Vendors". |

Before pushing, run `python3 tools/precedent_check.py` and read
**0 violated**; a large skipped count is normal in a practice set.

**Approval.** A change is proposed and an approver from
[approvers.json](approvers.json) agrees to it; when the proposer is the
approver, their "yes" in the conversation is the approval. Nobody waits on
a team approval to *use* a rule: put it in your own individual set first.
