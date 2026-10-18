#!/usr/bin/env bash
# Test for tools/ladder/upstream_review.py, this set's step_review: it checks
# itself; it is shown only on the ladder and only to a code owner; a line a
# batch's commits already record is skipped. Moved from BestPractice's
# verify_harness.py with the tool on 2026-10-17. Runs against the engine in
# tools/ beside it.
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
SET_ROOT="$(cd "$HERE/../../.." && pwd)"
fail=0
python3 "$SET_ROOT/tools/ladder/upstream_review.py" --self-check >/dev/null 2>&1 \
  || { echo "FAIL: the review's own self-check failed"; fail=1; }
SET_ROOT="$SET_ROOT" python3 - <<'PY' || fail=1
import os, pathlib, subprocess, sys, tempfile
root = pathlib.Path(os.environ['SET_ROOT'])
sys.path.insert(0, str(root / 'tools' / 'ladder'))
sys.path.insert(0, str(root / 'tools'))
import upstream_review as ur
import precedent_ladder as pl, precedent_audience as pa
real = (pl.ladder_in_force, pa.is_code_owner)
bad = []
env = dict(os.environ, GIT_AUTHOR_NAME='H', GIT_AUTHOR_EMAIL='h@example.com',
           GIT_COMMITTER_NAME='H', GIT_COMMITTER_EMAIL='h@example.com',
           PRECEDENT_ALLOW_ANY_AUTHOR='1')
with tempfile.TemporaryDirectory() as td:
    g = lambda *a: subprocess.run(['git', '-C', td, *a], env=env, capture_output=True,
                                  text=True).stdout.strip()
    g('init', '-q', '-b', 'main'); g('commit', '-q', '--allow-empty', '-m', 'base')
    base = g('rev-parse', 'HEAD')
    out = 'ok\nWARN: one thing\n'
    try:
        for name, ladder, owner, shown in (('off the ladder', False, (True, 'x'), False),
                                           ('not a code owner', True, (False, 'no'), False),
                                           ('a code owner on the ladder', True, (True, 'y'), True)):
            pl.ladder_in_force = lambda *a, _v=ladder, **k: _v
            pa.is_code_owner = lambda *a, _v=owner, **k: _v
            new, old = ur.prepare(td, 'booked', out, rev_range=f'{base}..HEAD')
            if shown != (new is not None and any('one thing' in t for _f, t in new)):
                bad.append(f'{name}: shown={new is not None}')
        fp_line = ur.trailer_lines(ur.prepare(td, 'booked', out, rev_range=f'{base}..HEAD')[0])[0]
        g('commit', '-q', '--allow-empty', '-m', f'Land x\n\n{fp_line}')
        new, old = ur.prepare(td, 'produce', out, rev_range=f'{base}..HEAD')
        if new or not old:
            bad.append(f'the next stage did not skip what the commit records: {new} {old}')
    finally:
        pl.ladder_in_force, pa.is_code_owner = real
for b in bad:
    print('FAIL:', b)
sys.exit(1 if bad else 0)
PY
[ "$fail" = 0 ] && echo "PASS: upstream_review"
exit "$fail"
