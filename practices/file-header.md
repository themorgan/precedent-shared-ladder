---
slug:        file-header
title:       A last-updated timestamp, author, and version at the top of files
tier:        on-demand
severity:    default
applies_to:  ["**/*.md"]
occasion:    "editing a markdown file that carries this header"
gates:       []
index_clause: "markdown files get a last-updated/by-me/version header"
checked_by:  tools/checks/check_file_header.py
defines:     []
status:      active
in_force_at: null
supersedes:  []
overrides:   null
added:       "2026-10-19"
approved_by: "Morgan F, 2026-10-19, moved from an individual set (there: Morgan F, migrated from RepoPersonalPreferences by the private-set migration session; `N` made monotonic and `--fix` added 2026-09-22, Morgan F -- \"the number bumping rule should be updated so you auto-fix these errors when found, for example, just not updating it if not content changes, and/or skipping numbers if needed - this is a minor feature so I don't collide different versions, it just needs the higher number for the more recent one, no precision\")"
strength:    decided
---
## Rule
A markdown file I maintain gets `<!-- Last updated: YYYY-MM-DD HH:MM:SS (Buenos Aires) by Morgan F, to version N -->` as its first line -- a full timestamp (hour, minute, second), not just a calendar date, since a bare date can't tell two same-day edits apart. `N` is a plain integer counter private to that one file: 1 the first time the header is added, and higher every time the file's content changes. Update the line whenever the file's content changes, not its formatting alone.

**`N` only has to RISE. It is not a successor function.** A change must push it up, by any amount; it may never go down; and bumping it without a content change is fine -- that is how a bump somebody missed earlier gets caught up. Gaps in the sequence mean nothing. All the number has to do is be higher on the more recent version, so I never have two copies I can't order.

**A copy of somebody else's file is not a file I maintain.** A vendored
tree -- Precedent's catalogue, a voice pack, anything a
`process/manifest*.json` records as coming from another repository -- keeps
its upstream's header as it is; neither the commit nor `--fix` stamps it, and
an edit there goes to its source. On 2026-10-10 a stamp the commit put on a
voice pack's README made each next pack sync refuse it as local drift, in
three repositories. **The same goes for a single file kept in step with
upstream** -- one a manifest records with status `synced`, such as a
rendered `GETTING_STARTED.md`: the audit holds it to its recorded hash, so a
stamp is drift. On 2026-10-15 the commit stamped one on an edit and again on
a byte-for-byte restore, and its landing was refused both times.

**Nobody has to remember the bump: the commit makes it.** `bootstrap/pre-commit-fix`, which the commit backstop runs before every commit in every repository, bumps the header of each staged markdown file whose content changed, in the commit being made -- only a header already in the exact format above, and never an unstaged edit. **Found a file whose header is behind anyway** -- a web edit, a rebase, a commit made with `--no-verify`? `python3 tools/checks/check_file_header.py --fix` catches it up in the working tree; commit that like any other edit.

## Detail
The "to version N" phrasing names that one file's own version, not a repo-wide release number, so bumping it is a one-file edit. This also means the rule doesn't mean retrofitting a header onto every existing file at once -- a file only picks up (or bumps) its header when it's actually being edited for some other reason, never a repo-wide sweep. A script or config format with comments gets the equivalent in that syntax; skip it where a leading comment would break the file (JSON has none) or where the file is a byte-for-byte mirror of something else and must never be hand-edited.

## Why
`NAME` here is always "Morgan F" when I'm the one making the edit -- the same name every commit is already authored as -- so the header settles who last touched the file without a reader needing to go check `git blame`.

## Story
Migrated here from RepoPersonalPreferences by the phase-3 private-set
migration. No incident was recorded; the details each carry their own stated
reason, and those are what this Story keeps.

The full timestamp rather than a calendar date is the load-bearing choice: a
bare date cannot tell two same-day edits apart, and same-day edits are the
common case on an actively-worked file. The zone is the same one every other
date in this set uses, so there is one clock rather than two.

The author field exists so the header settles who last touched the file
without a reader going to `git blame` -- the same name every commit is
already authored as, read from the one place that name lives rather than
restated here.

The version counter is deliberately per-file and private to that file, not a
repo-wide release number, which is what makes bumping it a one-file edit
rather than a coordination problem. That is also why installing the rule
never means a repo-wide sweep: a file picks up or bumps its header when it
is already being edited for some other reason, so the cost is always
attached to work already happening.


2026-09-07: a consuming repo renamed its whole content directory in one `git mv`, and this check reported all twelve versioned documents under it as *"header is new in this commit but starts at version N, expected 1"* -- twelve false positives on a commit that created no file at all. The cause was the parent lookup: it asked `git show HEAD~1:<current path>`, which is the right question only for a file that had that path at `HEAD~1`. A renamed file did not, git exited non-zero, and "no parent" was read as "new file." Both fixes available to that repo were wrong -- reset twelve real counters to 1, or leave the check red -- because nothing here could tell a rename from a creation. `git diff -M --name-status` can, so the check now asks it and reads the parent side at the path the file actually had. Copies are deliberately not followed: a copy really is a new file, and its counter really should start at 1.

**2026-09-22: the rule made a missed bump permanently unfixable, and Morgan cut that arm out.** PR #191 changed `README.md` and did not bump `N`. The next commit tried to catch it up and was refused -- *"version changed from 24 to 25 but the file's content didn't change -- only bump N when content changes"* -- because by then the content change was in an earlier commit. Both arms were individually reasonable and together they left no commit shape that could repair the file: the only ways out were to leave the check red or to invent a content change to carry the bump. The cause of the original miss is worth keeping too, because it is not laziness: the pre-push sweep ran BEFORE the commit existed, and this check can only compare `HEAD` against `HEAD~1`, so there was nothing yet to find.

Morgan's ruling, in his own words: *"this is a minor feature so I don't collide different versions, it just needs the higher number for the more recent one, no precision"* -- and, on what a session should do about it, *"the number bumping rule should be updated so you auto-fix these errors when found"*. So the "no touch-up without a real edit" arm is gone, `N` became monotonic, and `--fix` exists so the repair happens at the one moment it can. What did NOT change: a content change with no bump is still a violation, and that is the arm the whole practice is for.

**Later the same day, the `--fix` that change shipped had a fallback of its own, and it came out for the same reason.** Where [`precedent_time.py`](https://github.com/alex137/BestPractice/blob/staging/tools/precedent_time.py) was missing, `_stamp()` fell through to a bare `datetime.now()` -- the container's clock, UTC on a hosted runner -- on the argument that a wrong-zone stamp still satisfies the check while writing nothing does not. `timestamps-carry-offset` reported it and was right twice over. The header spells `(Buenos Aires)` as a literal, so a guessed stamp is wrong AND indistinguishable from a correct one by reading the file; and the "writing nothing is worse" half had just expired, because monotonic `N` is exactly what makes an unstamped header recoverable later. The two halves of one change had not been read against each other. `--fix` now refuses, says why, and stamps nothing.

**2026-09-22, later still: `--fix` covered a missed bump only when something else was already pending.** Monotonic `N` and `--fix` together were built to make a missed bump cheap to catch up -- but `--fix` only ever compared the WORKING TREE against `HEAD`, so a file with no pending edit read as clean even when `HEAD`'s own commit was the very one that skipped the bump. That is exactly the shape an edit made outside any session leaves: a commit lands (from the GitHub web UI, say) that changes a file's body without bumping its header, and nothing local runs `--fix` against it because nothing local made it. The violation then sits there, live, for as long as that commit remains `HEAD` -- every run of the check reports it, with no pending edit for the ordinary repair path to catch, until some unrelated later commit happens to move `HEAD` past it. Morgan raised this as a recurring cost, the same shape as the exemption list `commit-author`/`buenos-aires-dates` share for out-of-session commits (`identity.json`'s `grandfathered_commit_shas`) -- but this practice's own counter needs no such list: `N` was already built to tolerate a gap-filling bump with no content change, so `--fix` was extended to also check whether `HEAD` itself already violates against ITS parent (`_head_catchup_target()`) and, if so, stamp the catch-up bump even with nothing else pending. A session's ordinary `--fix` habit now clears this the same way it clears any other missed bump, and no exemption entry is ever written for it.

## Install
Checked mechanically by [`tools/checks/check_file_header.py`](../tools/checks/check_file_header.py) against every tracked `*.md` file. A file only carries an obligation once its first line already looks like the header -- files that never had one aren't flagged, matching the Detail section's "only when actually being edited" rule. For a file that does carry it: the header line must match the exact format; `N` must have risen when the body changed; and `N` must never fall. Scope is `change` (compares each commit against its parent). Tested in [`tools/checks/tests/test_file_header.sh`](../tools/checks/tests/test_file_header.sh) in both directions, including the three cases the 2026-09-22 changes turn on -- a catch-up bump with no content change must stay clean, a version going backwards must fire, and `--fix` in a checkout with no [`precedent_time.py`](https://github.com/alex137/BestPractice/blob/staging/tools/precedent_time.py) must refuse by name and leave every header alone.

**`--fix` is the same script, run on the working tree instead of on a commit.** It rewrites the header of every tracked markdown file whose body differs from `HEAD`, setting `N` to `max(what the file says, HEAD's N + 1)` and the timestamp to now. It also catches up a file whose body has NOT changed if `HEAD`'s own commit already violates against ITS parent -- content changed there with no bump, or a version that went backwards -- which is what an edit made outside any session leaves behind with nothing else pending. It never adds a header to a file that did not carry one, and never touches a mirrored or generated tree -- the same exclusions the check itself uses. The zone comes from [`tools/precedent_time.py`](https://github.com/alex137/BestPractice/blob/staging/tools/precedent_time.py), not from a constant in the script: hardcoding `America/Argentina/Buenos_Aires` here would be a second copy of a decision `buenos-aires-dates` already owns.

**Where it cannot resolve the zone, `--fix` refuses and stamps nothing.** No [`precedent_time.py`](https://github.com/alex137/BestPractice/blob/staging/tools/precedent_time.py) on the path -- a repo that materializes `tools/checks/` without `tools/` -- and it prints why and exits non-zero, rather than writing the container's clock. It has to be that way round because the zone is not part of what gets written: the header spells `(Buenos Aires)` literally, so a guessed stamp is wrong and reads as correct at the same time, and nobody looking at the file can catch it. An unstamped header can be caught up by any later commit now that `N` only has to rise; a wrong timestamp never gets caught at all.

**2026-09-10: the mirrored-tree exclusion comes from the engine.** The check skips files inside a tree this repo mirrors from somewhere else -- a hand-edit there is forbidden and the next sync overwrites it -- and it worked that list out itself, from `process/manifest.json`'s `upstream.vendored_at` alone. That file is one install layout's bookkeeping: Precedent's own INSTALL.md section 0 says to skip writing it, so in a section 0 install the exclusion silently evaporated and the vendored catalogue came back into scope. `precedent_resolve.mirrored_prefixes(repo)` answers it now, reading `precedent.json`'s declared source paths as well -- and precedent.json is the file that exists in exactly the repos the manifest is missing from. It fails open: where the engine module is absent (a practice-set repo does not vendor it) the old manifest-only reading is the fallback, because an exclusion that comes back short costs extra findings, never a missed one.

