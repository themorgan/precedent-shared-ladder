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

WHAT COUNTS (go-update's first bullet, the mechanical half of it):
  - any file under .github/workflows/
  - tools/precedent_check.py, tools/precedent_push_check.py,
    tools/leak_gate.py, tools/verify_harness.py, and anything under
    tools/checks/ -- the checks other work is judged against
EXCEPT an engine file that is byte for byte what the engine's own manifest
(tools/ENGINE_MANIFEST.json) recorded when Update Vendors vendored it from
BestPractice's main: that code already passed BestPractice's own review and
checks, and a vendor update would otherwise take a pull request every time
(Morgan, 2026-10-16: "since they are all checked that is fine"). A workflow
file never takes that exemption: it runs on the consuming repository's own
Actions, with its minutes and permissions, and only a run there shows it
works there. The rest of go-update's high-risk test -- a governance
practice, something hard to reverse, "not sure" -- stays the session's
judgment.

Runs only where the push check says the push goes to this repository's
landing branch (PRECEDENT_PUSH_DESTINATION, which it sets for the checks it
runs), and only on the ladder. Exit 0 and print nothing when clean; exit 1
with the finding on a violation; exit 2, SKIPPED, when it does not apply.
"""
import hashlib
import json
import os
import pathlib
import re
import subprocess
import sys

SOURCE_ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
ROOT = pathlib.Path(os.environ.get("PRECEDENT_CHECK_ROOT") or SOURCE_ROOT)
PRACTICE_FILE = SOURCE_ROOT / "practices" / "go-update.md"

GATING = ("tools/precedent_check.py", "tools/precedent_push_check.py",
          "tools/leak_gate.py", "tools/verify_harness.py")


class Skip(Exception):
    pass


def _git(*args):
    r = subprocess.run(["git", "-C", str(ROOT), *args], capture_output=True, text=True)
    return r.stdout.strip() if r.returncode == 0 else None


def landing_branch():
    tools = ROOT / "tools"
    sys.path.insert(0, str(tools))
    try:
        import precedent_branches
        return precedent_branches.landing_branch(str(ROOT))[0]
    except Exception:                                        # noqa: BLE001
        try:
            cfg = json.loads((ROOT / "precedent.json").read_text(encoding="utf-8"))
        except (OSError, ValueError):
            cfg = {}
        return cfg.get("landing_branch") or cfg.get("base_branch") or "main"
    finally:
        sys.path.pop(0)


def high_risk(path):
    return (path.startswith(".github/workflows/") or path in GATING
            or path.startswith("tools/checks/"))


def vendored_unchanged(path, manifest):
    """True for an engine file whose bytes are exactly what the manifest
    recorded vendoring from BestPractice's main."""
    if not path.startswith("tools/") or not isinstance(manifest, dict):
        return False
    if manifest.get("source_branch") not in (None, "main"):
        return False
    name = path[len("tools/"):]
    want = (manifest.get("sha256") or {}).get(name)
    f = ROOT / path
    if not want or not f.is_file():
        return False
    return hashlib.sha256(f.read_bytes()).hexdigest() == want


def changed_files(dest):
    since = os.environ.get("PRECEDENT_CHANGED_SINCE") or f"origin/{dest}"
    out = _git("diff", "--name-only", f"{since}...HEAD")
    if out is None:
        raise Skip(f"could not read what changed since {since}")
    return [p for p in out.splitlines() if p.strip()]


def findings():
    if os.environ.get("PRECEDENT_NO_LADDERS") == "1":
        raise Skip("off the ladder (PRECEDENT_NO_LADDERS=1)")
    dest = os.environ.get("PRECEDENT_PUSH_DESTINATION")
    if not dest:
        raise Skip("not run by a push check, so no push to judge")
    landing = landing_branch()
    if dest != landing:
        raise Skip(f"this push goes to {dest}, not the landing branch {landing}")
    try:
        manifest = json.loads((ROOT / "tools" / "ENGINE_MANIFEST.json")
                              .read_text(encoding="utf-8"))
    except (OSError, ValueError):
        manifest = None
    bad = [p for p in changed_files(dest)
           if high_risk(p) and not vendored_unchanged(p, manifest)]
    return landing, bad


def rule_text():
    text = PRACTICE_FILE.read_text(encoding="utf-8")
    m = re.search(r"## Rule\n(.*?)\n## ", text, re.S)
    return m.group(1).strip() if m else "(no Rule found)"


def main():
    try:
        landing, bad = findings()
    except Skip as e:
        print(f"SKIPPED: check_landing_takes_a_pr: {e}")
        return 2
    if not bad:
        return 0
    print("VIOLATION: go-update -- a high-risk change takes a pull request")
    print(rule_text())
    print()
    print(f"  This push lands straight on {landing} and changes "
          f"{', '.join(bad)} -- a CI workflow or code other work is judged "
          f"by. This one takes a pull request: push the branch, open a pull "
          f"request into {landing}, and merge it once its checks pass.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
