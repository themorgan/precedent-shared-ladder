#!/usr/bin/env bash
# Test for tools/ladder/others_did.py, the ladder set's daily report of what
# other people landed: it counts from the person's own last commit, writes
# nothing to origin, hands the report over once, and says nothing to a
# person off the ladder. Moved from BestPractice's verify_harness.py with the
# tool on 2026-10-17 (BestPractice spec/ENFORCEMENT_LIVES_WITH_ITS_PRACTICE_PLAN.md
# part 3). Runs against the engine vendored in tools/ beside it.
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
SET_ROOT="$(cd "$HERE/../../.." && pwd)"
SET_ROOT="$SET_ROOT" python3 - <<'PY'
import json, os, pathlib, shutil, subprocess, sys, tempfile
SET_ROOT = pathlib.Path(os.environ['SET_ROOT'])
sys.path.insert(0, str(SET_ROOT / 'tools' / 'ladder'))
sys.path.insert(0, str(SET_ROOT / 'tools'))


def main_cases():
    """tools/ladder/others_did.py (practices/others-did.md), end to end on a
    throwaway origin with main and staging. Moved here from BestPractice's
    verify_harness.py on 2026-10-17 with the tool.

    WHERE IT STARTS (Morgan, 2026-10-10: "Go with option 1"): the report
    counts from the person's own last commit here, and nothing is written to
    origin. Until then a mark of what each person was last told lived on
    origin's refs/precedent/others-did, and a cloud session's push of it was
    refused with HTTP 403, so every new container started over. So:

    - THE DISCRIMINATING CASE: a colleague's commit made BEFORE the
      person's last commit, merged after it, is reported -- it is counted by
      when it landed, not by its own date;
    - nothing the person did is reported, their Claude session's included;
    - origin receives no push of any ref, and the work clone's branch, HEAD
      and staged edit stay exactly as they were;
    - the report reaches the reply gate once; at most one report a day in a
      container, none before 07:00;
    - it asks for the three or four most important things, never the whole
      list (Morgan, 2026-10-10: "It should not list EVERYTHING");
    - a new container repeats the list until the person commits again (the
      cost Morgan accepted), and after that commit says nobody else did
      anything;
    - where this container's note is newer than the last commit, the note's
      tips are the starting point, so what was told is not told again;
    - a person with no commit here is told so, not handed all of history.

    Each case is checked against the tool's own words
    (practice: control-asserts-which-failure)."""
    import datetime, shutil, tempfile
    import others_did as pod

    MINE, THEIRS = 'owner@example.com', 'colleague@example.com'
    BOT = 'noreply@anthropic.com'
    S_MINE = 'https://claude.ai/code/session_01Mine'
    S_THEIRS = 'https://claude.ai/code/session_01Theirs'
    day = datetime.datetime(2026, 10, 8, tzinfo=datetime.timezone.utc)
    cases = []

    def at(days, hour):
        return day + datetime.timedelta(days=days, hours=hour)

    def git(cwd, *args, author=MINE, when=None):
        env = dict(os.environ)
        env['GIT_AUTHOR_EMAIL'] = env['GIT_COMMITTER_EMAIL'] = author
        env['GIT_AUTHOR_NAME'] = env['GIT_COMMITTER_NAME'] = \
            'Claude' if author == BOT else author.split('@')[0]
        if when:
            env['GIT_AUTHOR_DATE'] = env['GIT_COMMITTER_DATE'] = when.isoformat()
        r = subprocess.run(['git', '-C', str(cwd), *args],
                           capture_output=True, text=True, env=env)
        if r.returncode != 0:
            raise RuntimeError(f"git {' '.join(args)}: {r.stderr.strip()}")
        return r.stdout.strip()

    saved = {k: os.environ.get(k) for k in
             ('PRECEDENT_COMMIT_EMAIL', 'PRECEDENT_COMMIT_NAME',
              'PRECEDENT_COMMIT_TIMEZONE', 'PRECEDENT_USER_CONFIG',
              'GIT_CONFIG_GLOBAL')}
    saved_off = pod.off_ladder
    tmp = pathlib.Path(tempfile.mkdtemp(prefix='others-did-'))
    try:
        os.environ['PRECEDENT_COMMIT_EMAIL'] = MINE
        os.environ['PRECEDENT_COMMIT_NAME'] = 'Owner'
        os.environ['PRECEDENT_COMMIT_TIMEZONE'] = 'UTC'
        # A file of the fixture's own, never os.devnull: `git config
        # --global` against /dev/null replaces it with a regular file.
        os.environ['GIT_CONFIG_GLOBAL'] = str(tmp / 'gitconfig')
        (tmp / 'gitconfig').write_text('', encoding='utf-8')
        os.environ.pop('PRECEDENT_USER_CONFIG', None)
        pod.off_ladder = lambda root, user_config=None: False

        origin = tmp / 'origin.git'
        git(tmp, 'init', '-q', '--bare', '-b', 'main', str(origin))
        pushed = tmp / 'pushed.log'
        hook = origin / 'hooks' / 'update'
        hook.write_text(f'#!/bin/sh\necho "$1" >> "{pushed}"\nexit 0\n',
                        encoding='utf-8')
        hook.chmod(0o755)
        seed = tmp / 'seed'
        git(tmp, 'clone', '-q', str(origin), str(seed))
        (seed / 'keep.txt').write_text('x\n', encoding='utf-8')
        (seed / '.gitignore').write_text('.precedent/\n', encoding='utf-8')
        git(seed, 'add', '-A')
        git(seed, 'commit', '-qm', 'c0', when=at(0, 0))
        git(seed, 'push', '-q', 'origin', 'main')
        git(seed, 'push', '-q', 'origin', 'main:staging')

        def land(branch, subject, author, when, trailer=None):
            git(seed, 'fetch', '-q', 'origin', branch)
            git(seed, 'checkout', '-q', '-B', branch, f'origin/{branch}')
            (seed / f'{branch}.txt').write_text(subject, encoding='utf-8')
            git(seed, 'add', '-A')
            msg = ['-m', subject] + (['-m', f'Claude-Session: {trailer}'] if trailer else [])
            git(seed, 'commit', '-q', *msg, author=author, when=when)
            git(seed, 'push', '-q', 'origin', branch)

        def clone(name):
            path = tmp / name
            git(tmp, 'clone', '-q', str(origin), str(path))
            return path

        def run(repo, when):
            return pod.check(root=repo, now=when)

        def pushes():
            return pushed.read_text(encoding='utf-8').split() if pushed.is_file() else []

        work = clone('work')
        git(work, 'checkout', '-q', '-b', 'feature')
        (work / 'draft.txt').write_text('half done\n', encoding='utf-8')
        git(work, 'add', 'draft.txt')
        before = (git(work, 'rev-parse', 'HEAD'), git(work, 'diff', '--cached', '--name-only'))
        baseline = len(pushes())

        status, lines = run(work, at(0, 8))
        cases.append(('CONTROL: with only the person\'s own commit, nobody else '
                      'changed anything since it',
                      status == 'ok' and 'nobody else changed anything since your '
                      'last commit here' in lines[0], f'{status} {lines}'))

        # The person's session commits under their own name, which is what
        # makes a later commit signed only by Claude in it theirs too.
        land('staging', 'my own change', MINE, at(0, 9), trailer=S_MINE)
        # A colleague's pull request: its commit is dated BEFORE the
        # person's last one and lands by a merge after it.
        git(seed, 'fetch', '-q', 'origin', 'main')
        git(seed, 'checkout', '-q', '-B', 'their-pr', 'origin/main')
        (seed / 'pr.txt').write_text('pr\n', encoding='utf-8')
        git(seed, 'add', '-A')
        git(seed, 'commit', '-qm', 'old commit merged late', author=THEIRS, when=at(0, 3))
        git(seed, 'checkout', '-q', '-B', 'main', 'origin/main')
        git(seed, 'merge', '-q', '--no-ff', '-m', 'Merge their pull request',
            'their-pr', author=THEIRS, when=at(0, 10))
        git(seed, 'push', '-q', 'origin', 'main')
        land('main', 'their change', THEIRS, at(0, 11))
        land('staging', 'session signed by Claude, mine', BOT, at(0, 12), trailer=S_MINE)
        land('main', 'their session change', THEIRS, at(0, 13), trailer=S_THEIRS)
        land('main', 'session signed by Claude, theirs', BOT, at(0, 14), trailer=S_THEIRS)

        status, lines = run(work, at(1, 6))
        cases.append(('nothing before 07:00',
                      status == 'ok' and 'before 07:00' in lines[0], f'{status} {lines}'))
        status, lines = run(work, at(1, 8))
        block = pod.remind(work) or ''
        cases.append(('after 07:00 it reports, counted from the last commit',
                      status == 'alert' and 'since your last commit here' in block,
                      f'{status} {lines}'))
        cases.append(('the report asks for the three or four most important things, '
                      'never the whole list (Morgan, 2026-10-10)',
                      'THREE OR FOUR MOST IMPORTANT' in block
                      and 'NEVER THE WHOLE LIST' in block
                      and 'not to copy into the reply' in block, block[:800]))
        cases.append(("THE DISCRIMINATING CASE: a colleague's commit made before the "
                      'last commit and merged after it is reported',
                      'old commit merged late' in block, block[-600:]))
        cases.append(("the report holds the colleague's commits, their Claude session's included",
                      'their change' in block and 'session signed by Claude, theirs' in block,
                      block[-600:]))
        cases.append(("...and none of the person's own, their Claude session's included",
                      'my own change' not in block
                      and 'session signed by Claude, mine' not in block, block[-600:]))
        cases.append(('the reply gate hands it over once',
                      pod.remind(work) is None, 'a second remind() returned text'))
        status, lines = run(work, at(1, 10))
        cases.append(('reported once that day in this container, not again',
                      status == 'ok' and 'already told today' in lines[0], f'{status} {lines}'))
        after = (git(work, 'rev-parse', 'HEAD'), git(work, 'diff', '--cached', '--name-only'))
        cases.append(("the work clone's branch, HEAD and staged edit are untouched",
                      after == before and git(work, 'branch', '--show-current') == 'feature',
                      f'{before} -> {after}'))

        other = clone('other-container')
        status, lines = run(other, at(1, 9))
        block2 = pod.remind(other) or ''
        cases.append(('a new container repeats the list until the person commits '
                      'again (the accepted cost)',
                      status == 'alert' and 'their change' in block2, f'{status} {lines}'))

        land('main', 'after the report', THEIRS, at(1, 12))
        status, lines = run(work, at(2, 8))
        block3 = pod.remind(work) or ''
        cases.append(("where the container's note is newer than the last commit, "
                      'it counts from the note: only what came after',
                      status == 'alert' and 'since you were last told in this '
                      'container' in block3 and 'after the report' in block3
                      and 'their change' not in block3, f'{status} {block3[-500:]}'))

        land('staging', 'more of my own', MINE, at(2, 9))
        status, lines = run(clone('third-container'), at(3, 8))
        cases.append(('after the person commits again, a new container says '
                      'nobody else changed anything',
                      status == 'ok' and 'nobody else changed anything' in lines[0],
                      f'{status} {lines}'))

        cases.append(('origin received no push from the tool: every pushed ref is '
                      "the fixture's own branch, never a refs/precedent/ mark",
                      all(r.startswith('refs/heads/') for r in pushes()[baseline:])
                      and not git(origin, 'for-each-ref', 'refs/precedent'),
                      repr(pushes()[baseline:])))

        os.environ['PRECEDENT_COMMIT_EMAIL'] = 'newcomer@example.com'
        status, lines = run(clone('newcomer'), at(3, 8))
        cases.append(('a person with no commit here is told so, not handed all of history',
                      status == 'ok' and 'no commit here yet' in lines[0], f'{status} {lines}'))
    finally:
        pod.off_ladder = saved_off
        for k, v in saved.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v
        shutil.rmtree(tmp, ignore_errors=True)
    return cases




def gate_cases():
    cases = []
    # What others did says nothing to a person off the ladder, through the
    # reply gate's own call too (2026-10-02: only its command line asked, so
    # a colleague's reply gate named who had pushed to staging). Off the
    # ladder the pending report is left where it is, not handed over.
    import others_did as pod
    saved_off = pod.off_ladder
    pend_root = pathlib.Path(tempfile.mkdtemp(prefix='others-did-gate-'))
    try:
        (pend_root / '.precedent').mkdir()
        (pend_root / pod.PENDING).write_text('SOMEONE PUSHED\n', encoding='utf-8')
        pod.off_ladder = lambda root, user_config=None: True
        quiet = pod.remind(str(pend_root))
        pod.off_ladder = lambda root, user_config=None: False
        loud = pod.remind(str(pend_root))
    finally:
        pod.off_ladder = saved_off
        shutil.rmtree(pend_root, ignore_errors=True)
    cases.append(('what others did is silent at the reply gate for a person '
                  'off the ladder, and still speaks for one on it',
                  quiet is None and loud == 'SOMEONE PUSHED', f'{quiet!r} {loud!r}'))
    env_off = {k: v for k, v in os.environ.items()
               if k not in ('PRECEDENT_ASSUME_LADDER', 'PRECEDENT_NO_LADDERS')}
    env_off['PRECEDENT_USER_CONFIG'] = str(pathlib.Path(tempfile.gettempdir())
                                           / 'no-such-precedent-config.json')
    # "There" is a repository that binds nobody to the ladder: this set's own
    # when the test runs in it, else a throwaway one. Materialized into a
    # consumer, SET_ROOT is the consumer, whose precedent.json may bind
    # everyone to the ladder, and the case read its real config
    # (2026-10-28: red in the one consumer whose binds_everyone resolved).
    try:
        own = json.loads((SET_ROOT / 'precedent-source.json').read_text(
            encoding='utf-8')).get('name') == 'precedent-shared-ladder'
    except (OSError, ValueError):
        own = False
    there = SET_ROOT if own else pathlib.Path(tempfile.mkdtemp(prefix='others-did-off-'))
    if not own:
        (there / 'precedent.json').write_text('{"sources": []}\n', encoding='utf-8')
    try:
        r = subprocess.run([sys.executable, '-c',
                            'import sys; sys.path.insert(0, sys.argv[1] + "/tools"); '
                            'sys.path.insert(0, sys.argv[1] + "/tools/ladder"); '
                            'import others_did as b; '
                            'print(b.off_ladder(sys.argv[2]))',
                            str(SET_ROOT), str(there)],
                           cwd=str(there), env=env_off, capture_output=True, text=True)
    finally:
        if not own:
            shutil.rmtree(there, ignore_errors=True)
    cases.append(('...and a person with no set of their own is off the ladder there',
                  r.stdout.strip() == 'True', (r.stdout + r.stderr)[-200:]))

    return cases


cases = main_cases() + gate_cases()
bad = [(c[0], c[2]) for c in cases if not c[1]]
for n, d in bad:
    print(f'FAIL: {n} -- {str(d)[:400]}')
if bad:
    sys.exit(1)
print(f'PASS: others_did ({len(cases)} stated cases)')
PY
