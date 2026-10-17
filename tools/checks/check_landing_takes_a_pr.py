#!/usr/bin/env python3
"""check_landing_takes_a_pr.py -- the mechanical check for practices/go-update.md.

# practice: go-update

Booked lands most work straight on the landing branch, with no pull
request; a high-risk change takes one. This check holds the part of that
line a script can see: a push straight to the landing branch -- a
`precedent_branches.py --land`, or a plain `git push` to it -- that changes
a CI workflow or the code other work is judged by is refused, with the pull
request route printed instead.

THE INCIDENT (2026-10-16). In a consumer, Update Vendors brought a new
.github/workflows/ file and changes to tools/precedent_push_check.py, its
DONE said "land it on your landing branch", and --land put it on staging.
go-update's own list called both high-risk; the tool and the rule
disagreed, and the tool won.

WHAT COUNTS, AND WHERE IT IS ENFORCED (2026-10-17). The judgment itself --
which paths count, and the engine and materialized-check exemptions -- lives
in tools/landing_pr_guard.py, which go-update ships and declares as a git
pre-push hook: that is what refuses a landing, since a landing runs the quick
tier and the quick tier runs no practice check (Morgan, 2026-10-17: "Fix the
other issues you found including the checks that never run"). This check
asks the same function, so the practice check and the hook cannot disagree,
and runs wherever a push check names the destination
(PRECEDENT_PUSH_DESTINATION, which it sets for the checks it runs), and only
on the ladder. Exit 0 and print nothing when clean; exit 1 with the finding
on a violation; exit 2, SKIPPED, when it does not apply.
"""
import os
import pathlib
import re
import subprocess
import sys

SOURCE_ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
ROOT = pathlib.Path(os.environ.get("PRECEDENT_CHECK_ROOT") or SOURCE_ROOT)
PRACTICE_FILE = SOURCE_ROOT / "practices" / "go-update.md"


class Skip(Exception):
    pass


def guard():
    """go-update's tools/landing_pr_guard.py: beside this check's tools/ when
    run in place, else the copy shipped into the audited repository."""
    for tools in (SOURCE_ROOT / "tools", ROOT / "tools"):
        if (tools / "landing_pr_guard.py").is_file():
            sys.path.insert(0, str(tools))
            try:
                import landing_pr_guard
                return landing_pr_guard
            finally:
                sys.path.pop(0)
    raise Skip("tools/landing_pr_guard.py is not here")


def changed_files(dest):
    since = os.environ.get("PRECEDENT_CHANGED_SINCE") or f"origin/{dest}"
    r = subprocess.run(["git", "-C", str(ROOT), "diff", "--name-only",
                        f"{since}...HEAD"], capture_output=True, text=True)
    if r.returncode != 0:
        raise Skip(f"could not read what changed since {since}")
    return [p for p in r.stdout.splitlines() if p.strip()]


def findings():
    if os.environ.get("PRECEDENT_NO_LADDERS") == "1":
        raise Skip("off the ladder (PRECEDENT_NO_LADDERS=1)")
    dest = os.environ.get("PRECEDENT_PUSH_DESTINATION")
    if not dest:
        raise Skip("not run by a push check, so no push to judge")
    lpg = guard()
    landing = lpg.landing_branch(ROOT)
    if dest != landing:
        raise Skip(f"this push goes to {dest}, not the landing branch {landing}")
    return landing, lpg.risky(ROOT, changed_files(dest), "HEAD"), lpg


def rule_text():
    text = PRACTICE_FILE.read_text(encoding="utf-8")
    m = re.search(r"## Rule\n(.*?)\n## ", text, re.S)
    return m.group(1).strip() if m else "(no Rule found)"


def main():
    try:
        landing, bad, lpg = findings()
    except Skip as e:
        print(f"SKIPPED: check_landing_takes_a_pr: {e}")
        return 2
    if not bad:
        return 0
    print("VIOLATION: go-update -- a high-risk change takes a pull request")
    print(rule_text())
    print()
    print(f"  {lpg.refusal(landing, bad)}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
