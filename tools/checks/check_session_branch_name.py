#!/usr/bin/env python3
"""check_session_branch_name.py -- the mechanical check for practices/act.md.

# practice: act

A session on the ladder works on its own named branch, never on the one the
cloud harness named when the session opened (`claude/<words>-<six>`). The
engine's push check refuses a push that would CREATE such a branch on
origin; this check covers the rest: the checkout's current branch is read
every time the practice checks run -- at a landing, a Produce, a deep check
-- so work on a harness-named branch can never be Booked or Produced until
it is renamed. `git branch -m` keeps every commit, so the fix loses nothing.

Off the ladder (PRECEDENT_NO_LADDERS=1, or the engine's own
conventions_in_force saying so) nothing is judged.

Exit 0 and print nothing when clean. Exit 1 and print the practice's own
Rule text plus the finding on a violation. Exit 2, with a reason, when the
check COULD NOT RUN (not a git checkout, a detached HEAD) -- reported as
SKIPPED, and a skip is not a pass.
"""
import os
import pathlib
import re
import subprocess
import sys

# SOURCE_ROOT is the practice set this script ships in; ROOT is the
# repository it audits. The same directory when run in place or
# materialized into a consumer; PRECEDENT_CHECK_ROOT overrides the second.
SOURCE_ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
ROOT = pathlib.Path(os.environ.get("PRECEDENT_CHECK_ROOT") or SOURCE_ROOT)
PRACTICE_FILE = SOURCE_ROOT / "practices" / "act.md"

# The engine's own pattern, used when its naming tool is not importable.
HARNESS_NAME_RE = re.compile(
    r"(?:claude|session)/(?!\d{4}-\d{2}-\d{2}-)[a-z0-9]+(?:-[a-z0-9]+)+-[a-z0-9]{6}")


class CannotRun(Exception):
    pass


def naming_tool():
    tools = ROOT / "tools"
    if not (tools / "precedent_branch_name.py").is_file():
        return None
    sys.path.insert(0, str(tools))
    try:
        import precedent_branch_name
        return precedent_branch_name
    except Exception:                                        # noqa: BLE001
        return None
    finally:
        sys.path.pop(0)


def current_branch():
    r = subprocess.run(["git", "-C", str(ROOT), "symbolic-ref", "--short",
                        "-q", "HEAD"], capture_output=True, text=True)
    if r.returncode != 0 or not r.stdout.strip():
        top = subprocess.run(["git", "-C", str(ROOT), "rev-parse",
                              "--show-toplevel"], capture_output=True)
        raise CannotRun("not a git checkout" if top.returncode
                        else "HEAD is detached, so there is no branch to judge")
    return r.stdout.strip()


def rule_text():
    text = PRACTICE_FILE.read_text(encoding="utf-8")
    m = re.search(r"## Rule\n(.*?)\n## ", text, re.S)
    return m.group(1).strip() if m else "(no Rule found)"


def finding():
    if os.environ.get("PRECEDENT_NO_LADDERS") == "1":
        return None
    tool = naming_tool()
    if tool is not None and not getattr(tool, "conventions_in_force",
                                        lambda r: True)(str(ROOT)):
        return None
    name = current_branch()
    judge = getattr(tool, "is_harness_name", None) if tool else None
    harness = judge(name) if judge else bool(HARNESS_NAME_RE.fullmatch(name))
    if not harness:
        return None
    return (f"This checkout is on {name}, the name the harness gave the "
            f"session when it opened. Work on it is never Booked or "
            f"Produced: rename it first -- every commit comes with it -- "
            f"git branch -m {name} "
            f"\"$(python3 tools/precedent_branch_name.py <a few words>)\" "
            f"-- then push and land that name. Moving to a sister branch "
            f"needs nobody's permission (Morgan, 2026-10-11).")


def main():
    try:
        why = finding()
    except CannotRun as e:
        print(f"SKIPPED: check_session_branch_name: {e}")
        return 2
    if why is None:
        return 0
    print("VIOLATION: act -- a session works on its own named branch")
    print(rule_text())
    print()
    print(f"  {why}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
