#!/usr/bin/env python3
"""check_session_branch_name.py -- the mechanical check for practices/act.md.

# practice: act

A session on the ladder works on its own named branch, never on the one the
cloud harness named when the session opened (`claude/<words>-<six>`), and
never on one typed by hand. tools/branch_name_guard.py, which this set
ships and runs at every push, refuses pushing either; this check covers the
rest: the checkout's current branch is read every time the practice checks
run -- at a landing, a Produce, a deep check -- so such work can never be
Booked or Produced until it is renamed. `git branch -m` keeps every commit,
so the fix loses nothing. A name the naming tool made in another session
passes here: only its shape is judged, not whose session it was.

Off the ladder (PRECEDENT_NO_LADDERS=1) nothing is judged.

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

class CannotRun(Exception):
    pass


def guard():
    """This set's branch_name_guard: beside this check's tools/ when run in
    place, else the copy shipped into the audited repository."""
    for tools in (SOURCE_ROOT / "tools", ROOT / "tools"):
        if (tools / "branch_name_guard.py").is_file():
            sys.path.insert(0, str(tools))
            try:
                import branch_name_guard
                return branch_name_guard
            finally:
                sys.path.pop(0)
    raise CannotRun("tools/branch_name_guard.py is not here")


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
    g = guard()
    name = current_branch()
    why = g.name_refusal(name, tail="", user="")
    if why is None:
        return None
    return (f"This checkout is on {name}. Work on it is never Booked or "
            f"Produced until it is renamed: {why}")


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
