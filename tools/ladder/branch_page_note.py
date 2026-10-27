#!/usr/bin/env python3
"""Prints the reply gate's note about the branch cleanup page -- only when some branches can be deleted or a staging waits to go into main -- for the archive-line reply and the closing reply, the moments the-boildown names (practices/stale-branch-cleanup.md); run by the gate through this set's reply_check.json `note_from_tool`

branch_page_note.py -- what the archive-line reply and the closing reply
(the moments the-boildown names) owe the branch cleanup page.

The page itself is the engine's (tools/precedent_stale_branches.py): its
delete button runs on GitHub, where nothing a set ships is present. What
is this set's is the rule that those two replies link the page (rebuilding
it, after the answer, only when the person asks), and only when there is something on it ("Don't do that if
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
    # REBUILD ONLY WHEN ASKED (Morgan, 2026-10-20, strength: decided: "Sure
    # let's rebuild the page only when I ask"): the page's delete-all button
    # needs a GitHub tool, so every publish asks him to approve it, and a
    # rebuild after every landing put that prompt in nearly every session.
    # The answer still goes first; BestPractice's answer-first gate holds
    # the build and publish. 2026-10-27: "Branch cleanup" names the ask.
    return (f"In the archive-line reply and the closing reply (the moments "
            f"the-boildown names): {what} (the page "
            f"counts them, after a fetch), so link the branch cleanup "
            f"page{where} in one Boildown line, and nothing else on that line. "
            f"Link it as it stands: rebuild and republish it only when the "
            f"person asks for a fresh list in this conversation (\"Branch "
            f"cleanup\", the page's name), never because "
            f"this session made, landed or merged a branch -- each publish asks "
            f"them to approve the page's GitHub tool -- and only after the "
            f"reply's answer is written. When asked and this engine is too old "
            f"to build it, link it as it stands and say it was not refreshed. "
            f"To rebuild: read the "
            f"saved page's url with the Artifact tool, WITHOUT a path, "
            f"IMMEDIATELY before building, and run `python3 tools/"
            f"precedent_stale_branches.py --fetch --html "
            f"<scratchpad>/{sb.PAGE_FILENAME} --merge FILE` with the file that "
            f"read says the full HTML was saved to (only a page that came back "
            f"inline needs a second read, with path index.html, for the file). "
            f"Never merge a copy from earlier in the session. Before the first "
            f"publish, Read every line of that saved file in ranges of about 100 "
            f"lines and change "
            f"nothing: the Artifact tool refuses a republish over a page "
            f"another session published until it has been read through. Then "
            f"publish it the way the build's last line says. In any other "
            f"reply, say nothing about it (practice: stale-branch-cleanup).")


if __name__ == '__main__':
    text = note()
    if text:
        print(text)
    sys.exit(0)
