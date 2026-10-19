#!/usr/bin/env python3
"""Refuses a push straight to the landing branch that changes a CI workflow or the code other work is judged by, from git's pre-push, and prints the pull-request route -- go-update's high-risk line, enforced where landings happen

landing_pr_guard.py -- go-update's enforcement, shipped by the ladder set.

    python3 tools/landing_pr_guard.py --pre-push     (git's pre-push: refs on stdin)
    python3 tools/landing_pr_guard.py --range BASE TIP   (what a push of TIP over BASE would be told)

THE RULE (go-update): Booked lands most work straight on the landing branch,
with no pull request; a high-risk change takes one. This file holds the part
of that line a script can see.

WHY A PRE-PUSH HOOK (2026-10-17). Until then the only enforcement was
tools/checks/check_landing_takes_a_pr.py, a practice check, and a landing
runs the quick tier, which runs no practice check: the rule said "checked at
the push" and nothing checked it. go-update ships this file and declares it
as a `pre-push` hook, the way act ships its branch guard, so the global
pre-push the commit-identity hook installs runs it on every push, a
`precedent_branches.py --land` included (which pushes from the person's
checkout since the same day). Morgan, 2026-10-17: "Fix the other issues you
found including the checks that never run".

WHAT COUNTS (go-update's first bullet, the mechanical half of it):
  - any file under .github/workflows/
  - tools/precedent_check.py, tools/precedent_push_check.py,
    tools/leak_gate.py, tools/verify_harness.py, and any check under
    tools/checks/ or local/tools/checks/ -- the code other work is judged by
EXCEPT, never for a workflow file:
  - an engine file byte for byte what tools/ENGINE_MANIFEST.json recorded
    vendoring from BestPractice's main (Morgan, 2026-10-16: "since they are
    all checked that is fine");
  - a check the sync materialized from a practice source, byte for byte
    what MANIFEST.json recorded writing (2026-10-17): it passed its own
    source's checks, and in a consumer tools/checks/ is that catalogue, so
    counting it refused every sync.
Both are read at the commit being pushed, never from the working tree.

IN FORCE whenever this file is here; PRECEDENT_NO_LADDERS=1 (practice:
no-ladders) is the one way off. At --pre-push: exit 0 to let the push
through (a push elsewhere included), 1 to refuse it, with the reason on
stderr.
"""
import hashlib
import json
import os
import pathlib
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent
ZERO = '0' * 40
GATING = ('tools/precedent_check.py', 'tools/precedent_push_check.py',
          'tools/leak_gate.py', 'tools/verify_harness.py')
CHECK_DIRS = ('tools/checks/', 'local/tools/checks/')
WORKFLOWS = '.github/workflows/'


def in_force():
    return os.environ.get('PRECEDENT_NO_LADDERS') != '1'


def _git(root, *args, binary=False):
    try:
        r = subprocess.run(['git', '-C', str(root), *args], capture_output=True,
                           text=not binary, timeout=60)
    except (OSError, subprocess.TimeoutExpired):
        return None
    if r.returncode != 0:
        return None
    return r.stdout if binary else r.stdout.strip()


def high_risk(path):
    return (path.startswith(WORKFLOWS) or path in GATING
            or path.startswith(CHECK_DIRS))


def _blob(root, rev, path):
    return _git(root, 'cat-file', 'blob', f'{rev}:{path}', binary=True)


def _json_at(root, rev, path):
    raw = _blob(root, rev, path)
    try:
        return json.loads(raw.decode('utf-8')) if raw else None
    except (UnicodeDecodeError, ValueError):
        return None


def exempt(root, rev, path, engine=None, manifest=None):
    """True for a high-risk path whose bytes at `rev` are exactly what was
    vendored or materialized (the module docstring). `engine` and `manifest`
    are the two manifests at `rev`, read once by the caller."""
    if path.startswith(WORKFLOWS):
        return False
    data = _blob(root, rev, path)
    if data is None:
        return False
    full = hashlib.sha256(data).hexdigest()
    if (path.startswith('tools/') and isinstance(engine, dict)
            and engine.get('source_branch') in (None, 'main')
            and (engine.get('sha256') or {}).get(path[len('tools/'):]) == full):
        return True
    if path.startswith('tools/checks/') and isinstance(manifest, dict):
        for row in manifest.get('checks') or []:
            if isinstance(row, dict) and row.get('path') == path:
                return bool(row.get('sha256_16')) and full[:16] == row['sha256_16']
    return False


def risky(root, paths, rev):
    """-> the paths in `paths` that make a push of `rev` take a pull request."""
    engine = _json_at(root, rev, 'tools/ENGINE_MANIFEST.json')
    manifest = _json_at(root, rev, 'MANIFEST.json')
    return [p for p in paths if high_risk(p)
            and not exempt(root, rev, p, engine, manifest)]


def changed(root, base, tip):
    out = _git(root, 'diff', '--name-only', f'{base}...{tip}')
    return None if out is None else [p for p in out.splitlines() if p.strip()]


# THE ENGINE IS THE CHECKED REPOSITORY'S OWN (2026-10-19). A bare
# `import precedent_branches` also searches this script's own directory, so
# in a repository with no engine it found the one beside the guard and
# answered from that: a test of the no-engine case went red the day the
# engine beside it gained pull_request_route_note.
def _engine(root):
    """-> root's own tools/precedent_branches.py as a module, or None."""
    tools = pathlib.Path(root) / 'tools'
    path = tools / 'precedent_branches.py'
    if not path.is_file():
        return None
    import importlib.util
    sys.path.insert(0, str(tools))
    try:
        spec = importlib.util.spec_from_file_location('precedent_branches', path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod
    except Exception:                                        # noqa: BLE001
        return None
    finally:
        sys.path.pop(0)


def landing_branch(root):
    """The landing branch as the engine names it for this person; the
    repository's own declaration where the engine is not importable."""
    try:
        return _engine(root).landing_branch(str(root))[0]
    except Exception:                                        # noqa: BLE001
        try:
            cfg = json.loads((pathlib.Path(root) / 'precedent.json')
                             .read_text(encoding='utf-8'))
        except (OSError, ValueError):
            cfg = {}
        return cfg.get('landing_branch') or cfg.get('base_branch') or 'main'


# WHAT FOLLOWS THE PULL REQUEST (2026-10-18). The refusal said "merge it
# once its checks pass". In BestPractice no workflow runs on a pull request
# into staging, so a session opened one, waited for checks that never
# started, and sat until Morgan asked whether anything was happening. The
# engine's pull_request_route_note reads .github/workflows and says which
# checks, if any, will report; where it is not importable, the refusal says
# not to wait on checks that are not listed.
def route_note(root, landing):
    """-> what to do once the pull request into `landing` is open.

    A push made by the land tool (it sets PRECEDENT_LANDING_SOURCE) gets no
    note here: that tool ran the quick checks and prints its own note right
    after, so this one said "Nothing has run the quick checks" two lines
    above "The quick checks above passed" (2026-10-19)."""
    if os.environ.get('PRECEDENT_LANDING_SOURCE'):
        return 'The land tool that made this push says what follows, below.'
    if root is not None:
        try:
            return _engine(root).pull_request_route_note(str(root), landing)
        except Exception:                                    # noqa: BLE001
            pass
    return ('Merge it once its checks pass, or straight away if the pull '
            'request lists none.')


def refusal(landing, bad, root=None):
    return (f'this push lands straight on {landing} and changes '
            f'{", ".join(bad)} -- a CI workflow or code other work is judged '
            f'by. This one takes a pull request (go-update): push the branch '
            f'and open a pull request into {landing}. '
            f'{route_note(root, landing)}')


def pre_push_refusals(root, lines, landing=None):
    """-> [why] for git's pre-push stdin lines
    (`<local ref> <local sha> <remote ref> <remote sha>`)."""
    landing = landing or landing_branch(root)
    out = []
    for line in lines:
        parts = line.split()
        if len(parts) != 4:
            continue
        _lref, lsha, rref, rsha = parts
        if lsha == ZERO or rref != f'refs/heads/{landing}':
            continue
        base = rsha if rsha != ZERO and _git(root, 'cat-file', '-e', f'{rsha}^{{commit}}') is not None \
            else (f'origin/{landing}' if _git(root, 'rev-parse', '--verify', '-q',
                                              f'origin/{landing}') else None)
        if base is None:
            continue
        paths = changed(root, base, lsha)
        if paths is None:
            out.append(f'could not read what this push to {landing} changes '
                       f'(git diff {base[:12]}...{lsha[:12]} failed), so it is '
                       f'not let through unjudged')
            continue
        bad = risky(root, paths, lsha)
        if bad:
            out.append(refusal(landing, bad, root))
    return out


def _root():
    top = _git(os.environ.get('CLAUDE_PROJECT_DIR') or '.', 'rev-parse', '--show-toplevel')
    return pathlib.Path(top) if top else pathlib.Path('.').resolve()


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    if not argv or argv[0] in ('-h', '--help'):
        print((__doc__ or '').strip())
        return 0
    if not in_force():
        return 0
    root = _root()
    if argv[0] == '--pre-push':
        refusals = pre_push_refusals(root, sys.stdin.read().splitlines())
        for why in refusals:
            print(f'push refused (go-update): {why}', file=sys.stderr)
        return 1 if refusals else 0
    if argv[0] == '--range' and len(argv) == 3:
        paths = changed(root, argv[1], argv[2])
        if paths is None:
            print(f'could not diff {argv[1]}...{argv[2]}', file=sys.stderr)
            return 2
        bad = risky(root, paths, argv[2])
        for p in bad:
            print(p)
        return 1 if bad else 0
    print('usage: landing_pr_guard.py --pre-push | --range BASE TIP', file=sys.stderr)
    return 2


if __name__ == '__main__':
    sys.exit(main())
