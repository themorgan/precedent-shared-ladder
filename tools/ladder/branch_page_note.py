#!/usr/bin/env python3
"""Prints the reply gate's note about the branch cleanup page -- only when some branches can be deleted or a staging waits to go into main -- for every Boildown that says the session can be archived (practices/stale-branch-cleanup.md); run by the gate through this set's reply_check.json `note_from_tool`

branch_page_note.py -- what a reply that says the session can be archived
owes the branch cleanup page.

The page itself is the engine's (tools/precedent_stale_branches.py): its
delete button runs on GitHub, where nothing a set ships is present. What
is this set's is the rule that a Boildown saying the session can be
archived links the page (building and publishing it when this session's
branches changed), and only when there is something on it ("Don't do that if
there aren't any", Morgan, 2026-10-05). That rule lived in BestPractice's
reply gate until 2026-10-17 (BestPractice
spec/ENFORCEMENT_LIVES_WITH_ITS_PRACTICE_PLAN.md part 3); the gate now runs
this file and prints what it says.

Prints nothing, exit 0, when there is nothing to clean or the engine
cannot say; never fails the gate.
"""
import pathlib
import sys

# Shipped to tools/ladder/; the engine is in tools/ beside it.
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))


def note():
    try:
        import precedent_stale_branches as sb
    except Exception:                                         # noqa: BLE001
        return ''
    try:
        groups, _ = sb.collect()
        n = sum(len(r) for *_x, r in groups)
    except Exception:                                         # noqa: BLE001
        n = 0
    try:
        w = len(sb.collect_waiting())
    except Exception:                                         # noqa: BLE001
        w = 0
    if not (n or w):
        return ''
    # NO COUNT HERE (2026-10-10, a consumer): this reads the remote-tracking
    # refs as they stand, without a fetch -- a fetch per repository at every
    # turn costs too much -- while the page fetches first, so "13 branch(es)
    # across 4" here met 16 on the page. The page's number is the one to give.
    what = (("some branches can be deleted" + (" and " if w else "") if n else "")
            + ("a repository's staging is waiting to go into main" if w else ""))
    try:
        url = sb.saved_page() or ''
    except Exception:                                         # noqa: BLE001
        url = ''
    where = f" ({url})" if url else ''
    return (f"In EVERY reply that says \"You can archive this session\", and "
            f"one that answers \"Archive\" or \"Archive?\": {what} (the page "
            f"counts them, after a fetch), so link the branch cleanup "
            f"page{where} in one Boildown line. Build and publish it the first "
            f"time this session gives it, and again only when this session has "
            f"made, landed or merged a branch since it last published; "
            f"otherwise link it as it stands -- and link it as it stands, "
            f"saying it was not refreshed, when this engine is too old to "
            f"build it. Build the page with `python3 tools/"
            f"precedent_stale_branches.py --fetch --html "
            f"<scratchpad>/{sb.PAGE_FILENAME}` -- with a saved page it asks for "
            f"that page as it stands: read the saved page's url with the "
            f"Artifact tool, WITHOUT a path, IMMEDIATELY before building -- the "
            f"read a republish needs -- and pass the file it says the full HTML "
            f"was saved to as `--merge FILE` (only a page that came back inline "
            f"needs a second read, with path index.html, for the file). Never "
            f"Read that file yourself, and never a copy from earlier in the "
            f"session, so rows from repositories this session cannot see, and "
            f"ticks saved since, are kept -- publish it as an artifact the way "
            f"its last line says (the page saves the person's ticks into "
            f"itself). In a reply that does not say the session can be "
            f"archived, say nothing about it (practice: stale-branch-cleanup).")


if __name__ == '__main__':
    text = note()
    if text:
        print(text)
    sys.exit(0)
