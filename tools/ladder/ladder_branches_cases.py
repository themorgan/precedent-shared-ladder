#!/usr/bin/env python3
"""Tests for tools/ladder/ladder_branches.py, this set's branch_moves: Promote, Produce and the wait on main's GitHub test after a Produce

Moved with the moves themselves from BestPractice's tools/verify_harness.py
on 2026-10-19 (BestPractice spec/ENFORCEMENT_LIVES_WITH_ITS_PRACTICE_PLAN.md,
pieces 5b and 5c). Run by tools/checks/tests/test_ladder_branches.sh;
shipped beside the moves, because a consumer receives a set's test
scripts and the tools its practices ship, and nothing else.

THE ENGINE THEY RUN AGAINST. The moves are built on the engine core, so
these tests run against an engine beside them: the one in this checkout's
tools/ (a consumer's, or this set's own copy), or the one
PRECEDENT_ENGINE_ROOT names (a BestPractice checkout, to test a change to
both at once). Each test sees ONE module, `precedent_branches`, that is that
engine with this set's moves added -- the shape the code had before the
move -- so a test can stand in for any part of it, engine or moves, and the
moves see the stand-in. The scratch repositories the tests build get the
same assembled file. How the engine FINDS this file (set_tool, the
`branch_moves` key) is tested in BestPractice with a made-up set, and here
by one case against this set's own precedent-source.json.
"""
import collections, hashlib, importlib.util, json, os, pathlib, re, shutil, subprocess, sys, tempfile, time
import tempfile as _tempfile_for_env

# THE HARNESS'S OWN SETTINGS, as BestPractice's tools/verify_harness.py sets
# them before any case runs: these cases were written under them.
# A FIXTURE COMMIT IS NOT A PERSON'S COMMIT. Since 2026-09-07 the commit
# identity hook installs a backstop at core.hooksPath -- global, because that
# is the only hook location reaching a repository attached mid-session, which
# is where three wrong-author incidents came from. It therefore also reaches
# the throwaway repos this harness builds by the dozen, and refused them for
# a +0000 offset, taking the whole run down with a RuntimeError on the first
# `git commit -qm base`.
#
# Set here, once, for every subprocess: the override the backstop itself
# documents. It is the right answer rather than a workaround -- nothing in a
# temporary directory is anybody's authorship. The two checks that exercise
# the backstop's own refusals pop this back out of their fixture env, so the
# coverage is not weakened by it.
os.environ.setdefault('PRECEDENT_ALLOW_ANY_AUTHOR', '1')

# EVERY UPDATE VENDORS RUN HERE TESTS THIS CHECKOUT'S CODE. Run from a clone
# behind origin/main, precedent_update.py would otherwise run origin's
# newest green commit from a worktree (precedent_update_driver.py) -- and a
# case would quietly test that instead of the change in front of it. Set
# once, for every subprocess; the one check of the driver itself clears it.
os.environ.setdefault('PRECEDENT_UPDATE_RUN_IN_PLACE', '1')

# THE SAME BUG, ON THE CLOCK INSTEAD OF THE AUTHOR, and it escaped the fix
# above by one field. commit-identity.sh repoints `/etc/localtime` so a
# session's commits carry the declared offset without a `TZ=` prefix. In a
# FIXTURE there is no declared identity to resolve, so the hook falls to the
# last rung -- precedent.json's `fallback_timezone`, America/New_York -- and
# repoints the REAL container's system clock to it. Two call sites already
# pass PRECEDENT_LOCALTIME to redirect that write; anything reaching the hook
# by another path did not, and silently reset the machine.
#
# Measured 2026-09-11, before/after on a controlled run: `/etc/localtime` went
# from America/Argentina/Buenos_Aires to America/New_York across one
# `verify_harness.py` invocation, with the session's own clock left wrong
# afterwards. The cost is not the harness's -- it is the NEXT commit in the
# session, refused by the backstop for `author-date offset is '-0400'` with
# the author already correct, which reads as a fresh identity problem and is
# really this. It cost a day of re-fixing git config that was never wrong.
#
# Set here for the same reason and in the same way: nothing in a temporary
# directory owns the machine's clock. The two checks that exercise the hook's
# own timezone behaviour set their own PRECEDENT_LOCALTIME and are unaffected.
# (practice: fixture-owns-its-state -- one level further out, since the state
# the fixture was mutating belonged to the container rather than to git.)
os.environ.setdefault(
    'PRECEDENT_LOCALTIME', '/tmp/precedent-harness-localtime')

# Same problem, opposite direction: the harness must OWN the identity its
# fixtures assert on, instead of inheriting whatever the session exports.
#
# check_identity_reaches_a_repo_that_did_not_exist_yet builds a fixture in a
# temporary HOME, sets a global identity inside it, and asserts that commits
# made there used it. But GIT_AUTHOR_* outrank `git config --global user.*`,
# so a session that exports them -- the individual practice set's
# .claude/settings.json does -- authored every fixture commit as the real
# person, and 4 of that check's 11 stated cases failed, none of them real.
# Three failed in the confusing direction: a bot identity the fixture plants
# in LOCAL config was never the author any more, so the refusal the case
# waits for correctly did not fire, and a working backstop read as broken.
#
# Measured 2026-09-07, same tree, no code change: `1 failed` with the two
# variables exported, `0 failed` under `env -u`. Dropped here, once, rather
# than in the single fixture that happened to notice -- a fixture written
# later would inherit the same invisible dependency and the same hour of
# misdiagnosis. GIT_AUTHOR_DATE goes with them because the same check
# asserts on the author-date offset, which that variable equally overrides.
#
# The GIT_COMMITTER_* trio is deliberately NOT dropped: nothing in this
# harness or in commit-identity.sh reads the committer (the hook resolves
# `git var GIT_AUTHOR_IDENT`), so removing them would be a guess at a
# problem nobody has had.
for _var in ('GIT_AUTHOR_NAME', 'GIT_AUTHOR_EMAIL', 'GIT_AUTHOR_DATE'):
    os.environ.pop(_var, None)

# THE SAME SHAPE AGAIN, on the private-source credential, and this one made
# the harness's own result depend on which container it ran in. Two fixtures
# build a scenario where NO credential is available -- "with no base url the
# shared source is named on stderr as NOT in force", and "--write-session-hook
# with NO --repo-url ... degrades quietly" -- and then spawn a subprocess
# carrying the container's own environment. Where PRECEDENT_GIT_TOKEN and
# PRECEDENT_SOURCE_BASE_URL are set (INSTALL.md section 8, and every session
# since the credential route was verified on 2026-09-10), the subprocess
# picks them up, finds a URL after all, and does the thing the case says it
# must not do. The fixture never established the state it asserted on.
#
# Measured 2026-09-11, same tree, no code change: `4 failed` with the two
# variables in the environment, `2 failed` under `env -u` -- so a harness
# whose credentials happened to be missing reported two checks green that a
# credentialed one reported red, and neither run was wrong about itself.
#
# The first fix popped both variables inside the two fixtures that noticed,
# and those pops are still there -- they document the hazard where a reader
# meets it, and they hold if anything ever re-adds a credential in a
# narrower scope. They are not the whole fix, because a fixture written next
# month inherits the same invisible dependency and will not have read them.
# So the scrub is dropped here as well, once, for the same reason as the
# block above. (practice: fixture-owns-its-state, whose Rule says exactly
# this: clear the ambient inputs at the top, not in the fixture that
# happened to notice.)
#
# A fixture that genuinely wants a credential sets it explicitly, and still
# gets it -- check_source_credentials plants its own token and its own
# file:// base URL, and is unaffected.
# check_fixtures_own_the_credential_environment asserts this block did its
# job, planted variables and all.
CREDENTIAL_ENV_VARS = ('PRECEDENT_GIT_TOKEN', 'PRECEDENT_SOURCE_BASE_URL')
for _var in CREDENTIAL_ENV_VARS:
    os.environ.pop(_var, None)

# A THIRD INSTANCE, three days later, and it turned the whole branch red on
# any machine that has the also-list set. PRECEDENT_FRESHNESS_ALSO names
# OTHER repositories the freshness guard should check
# (.claude/hooks/freshness-guard.sh), and a fixture that runs the guard
# against its own temporary clone inherits it -- so the guard walked out of
# the fixture into this container's real attached practice sets, could not
# fetch one of them (no credential for a private remote), and blocked. The
# check reported "pre-write does not block a branch absent from origin
# (exit 2)" in both copies: a correct guard, a correct absent-branch
# NOTE printed just above it, and a block belonging to a repository the
# fixture had never heard of.
#
# Measured 2026-09-11, same tree, no code change: `2 failed` with the
# variable set, and exit 0 from the same guard call under `env -u
# PRECEDENT_FRESHNESS_ALSO`. A fixture exercising the guard owns which
# repositories it checks exactly as much as it owns the clone it built
# (practice: fixture-owns-its-state) -- and the only thing that can own an
# ambient list for every fixture, including the ones written next month, is
# this block.
os.environ.pop('PRECEDENT_FRESHNESS_ALSO', None)

# GIT'S OWN REPOSITORY VARIABLES (2026-10-06, traced from
# gotchas/gotcha-2026-10-01-a-harness-check-run-in-a-linked-worktree-turns-the-main-clone-bare.md).
# `git bisect run` exports GIT_DIR to the command it runs, and a git hook
# gets GIT_DIR and GIT_INDEX_FILE. Every fixture here builds its env from
# os.environ, so under either one a fixture's `git init`, `git add` and
# `git commit` all went to the repository the harness was started in, not
# the temporary one in front of them. Run from a linked worktree, GIT_DIR is
# `.git/worktrees/<name>`, and `git init --bare` re-initialised it as bare,
# which writes `core.bare = true` into the config the main clone shares.
# That is the 2026-10-01 bisect: fixture commits on the worktree's HEAD, and
# a main clone git called bare. Reproduced the same way on 2026-10-06 in a
# throwaway repository. Nothing in the harness locates a repository through
# these: ROOT is this file's own location, and every git call names its
# directory or runs in one. So they are dropped here, once, for every fixture
# (check_harness_drops_inherited_git_repository_variables).
GIT_REPOSITORY_ENV_VARS = (
    'GIT_DIR', 'GIT_WORK_TREE', 'GIT_COMMON_DIR', 'GIT_INDEX_FILE',
    'GIT_OBJECT_DIRECTORY', 'GIT_ALTERNATE_OBJECT_DIRECTORIES',
    'GIT_NAMESPACE', 'GIT_PREFIX')
for _var in GIT_REPOSITORY_ENV_VARS:
    os.environ.pop(_var, None)

# GIT'S BACKGROUND MAINTENANCE (2026-10-18, issue #1207). A commit ends by
# starting `git maintenance run --auto` detached, and that run holds
# .git/objects/maintenance.lock for a moment. check_precedent_check_fires
# copies its pristine fixture with shutil.copytree right after committing
# into it, listed the lock, found it gone by the time it went to copy it, and
# turned GitHub's test on pull request #1206 red with nothing wrong in the
# tree. No fixture wants git tidying its throwaway repository behind its
# back, so every git this harness or its subprocesses start is told not to,
# appended to any GIT_CONFIG_COUNT entries already in the environment
# (check_harness_fixtures_run_no_background_maintenance).
HARNESS_GIT_CONFIG = (('maintenance.auto', 'false'), ('gc.auto', '0'))
_n = int(os.environ.get('GIT_CONFIG_COUNT') or 0)
for _key, _value in HARNESS_GIT_CONFIG:
    os.environ[f'GIT_CONFIG_KEY_{_n}'] = _key
    os.environ[f'GIT_CONFIG_VALUE_{_n}'] = _value
    _n += 1
os.environ['GIT_CONFIG_COUNT'] = str(_n)

# THE SAME, FOR THE GITHUB ACCOUNT (2026-09-30). The account a session's
# token belongs to now fills in the private sets' location and the commit
# identity when nothing declares them, and a cloud container's proxy answers
# api.github.com/user for ANY caller -- so a fixture meaning "nobody is known
# here" was answered with the real person's account and walked off to clone
# their real individual set. Every fixture starts with GitHub knowing nobody;
# one that tests the account rung points PRECEDENT_GITHUB_USER_URL at its own
# answer, as the commit-identity and base-URL checks do.
import tempfile as _tempfile_for_env  # noqa: E402
os.environ['PRECEDENT_GITHUB_USER_URL'] = (
    pathlib.Path(_tempfile_for_env.gettempdir()) / 'harness-github-knows-nobody.json').as_uri()

# AND WHAT A FAILED CLONE LEAVES BEHIND (2026-10-09). The source bootstrap
# keeps git's output for a clone that failed beside the user config, so the
# credentials check can quote it later. Fixtures fail clones on purpose, and
# without this every one of them would write a note into the real
# ~/.config/precedent that a real session would then quote.
os.environ['PRECEDENT_CLONE_NOTES'] = str(
    pathlib.Path(_tempfile_for_env.mkdtemp(prefix='harness-clone-notes-'))
    / 'clone-failures.json')

os.environ.setdefault('PRECEDENT_ASSUME_LADDER', '1')
os.environ.setdefault('PRECEDENT_LOCAL_SESSION', '0')
os.environ.setdefault('PRECEDENT_SEED_OFF_MAIN', '1')


HERE = pathlib.Path(__file__).resolve().parent
SET_ROOT = HERE.parents[1]
ENGINE_ROOT = pathlib.Path(os.environ.get('PRECEDENT_ENGINE_ROOT') or SET_ROOT).resolve()
LADDER = SET_ROOT / 'tools' / 'ladder' / 'ladder_branches.py'
_ASM = pathlib.Path(tempfile.mkdtemp(prefix='ladder-branches-test-'))
_SCRIPT_GUARD = '\nif __name__ == ' + repr('__main__') + ':'


def _assemble():
    """-> a root whose tools/ is ENGINE_ROOT's, file for file, except
    precedent_branches.py, which is the engine with this set's moves added
    and its branch_moves() answering with itself."""
    (_ASM / 'tools').mkdir()
    for p in ENGINE_ROOT.iterdir():
        if p.name not in ('tools', '.git'):
            (_ASM / p.name).symlink_to(p)
    for p in (ENGINE_ROOT / 'tools').iterdir():
        if p.name != 'precedent_branches.py':
            (_ASM / 'tools' / p.name).symlink_to(p)
    if not (_ASM / 'tools' / 'ladder').exists():
        (_ASM / 'tools' / 'ladder').symlink_to(LADDER.parent)
    engine = (ENGINE_ROOT / 'tools' / 'precedent_branches.py').read_text(encoding='utf-8')
    moves = LADDER.read_text(encoding='utf-8')
    tail = ('\n\n# ---- this set\'s moves, added by its test (ladder_branches_cases.py) ----\n'
            + moves
            + '\n\nclass _ThisModule:\n'
              '    def __getattr__(self, name):\n'
              '        return globals()[name]\n\n\n'
              'core = _ThisModule()\n\n\n'
              'def branch_moves(root, user_config=None):\n'
              '    return sys.modules.get(__name__)\n')
    at = engine.rfind(_SCRIPT_GUARD)
    text = engine[:at] + tail + engine[at:] if at >= 0 else engine + tail
    (_ASM / 'tools' / 'precedent_branches.py').write_text(text, encoding='utf-8')
    return _ASM


ROOT = _assemble()
sys.path.insert(0, str(ROOT / 'tools'))
sys.modules.pop('precedent_branches', None)


_n = int(os.environ.get('GIT_CONFIG_COUNT') or 0)


FAILED = []


PASSED = []


NA = []


_CHECK_ALREADY_REPORTED = object()


_CHECK_FILTERED_OUT = object()


def check(name, ok, detail='', failure=''):
    """Record one verdict.

    The fourth argument exists for the verdict-returning family, which ends
    in `return (not bad, detail, failure)` and is wired up as
    `check('<name>', *check_foo())`. Those carry TWO strings: a detail worth
    printing when the check passes ("11 stated cases"), and the failure text
    naming what broke. Collapsing them at the call site would have meant
    every one of those sites choosing, and choosing differently; taking both
    here keeps the family's own return shape intact.

    A failing check prints its failure text when it has one, because that is
    the string that says what to go and look at."""
    if ok is _CHECK_ALREADY_REPORTED:
        return
    if ok is _CHECK_FILTERED_OUT:
        not_applicable(name, 'filtered out by PRECEDENT_CHECK_ONLY/SKIP')
        return
    shown = failure if (not ok and failure) else detail
    (PASSED if ok else FAILED).append((name, shown))
    print(f"{'PASS' if ok else 'FAIL'}: {name}" + (f" -- {shown}" if shown and not ok else ""))


_CURRENT_CHECK = []


NA_FUNCTIONS = set()


def not_applicable(name, reason):
    NA.append((name, reason))
    if _CURRENT_CHECK:
        NA_FUNCTIONS.add(_CURRENT_CHECK[-1])
    print(f"N/A:  {name} -- {reason}")


def _without_session_id(fn):
    """Run a check with no CLAUDE_CODE_REMOTE_SESSION_ID in the environment.
    precedent_gate._unlanded_work reports only commits carrying this
    session's trailer when that id is set, so a fixture whose commits carry
    none must not inherit the id of the session running the harness
    (practice: fixture-owns-its-state)."""
    import functools

    @functools.wraps(fn)
    def run(*a, **k):
        saved = os.environ.pop('CLAUDE_CODE_REMOTE_SESSION_ID', None)
        try:
            return fn(*a, **k)
        finally:
            if saved is not None:
                os.environ['CLAUDE_CODE_REMOTE_SESSION_ID'] = saved
    return run


@_without_session_id
def _engine_commit_fixture(tmp, name, kind, git_env):
    """A repository with an origin, the REAL engine files the engine-commit
    checks exercise, and stubs for the gates they do not. -> (work, bare).
    The stubs pass; test_in_copy.sh leaves a marker naming the checkout it
    ran in when CS_MARK is set, so a caller can prove consumer_shape ran."""
    import json as _json, shutil as _shutil
    bare, work = tmp / f'{name}.git', tmp / name
    subprocess.run(['git', 'init', '-q', '--bare', '-b', 'beta', str(bare)],
                   env=git_env, capture_output=True)
    (work / 'tools' / 'checks' / 'tests').mkdir(parents=True)
    subprocess.run(['git', 'init', '-q', '-b', 'beta', str(work)],
                   env=git_env, capture_output=True)
    real = ['precedent_branches.py', 'precedent_push_check.py',
            'precedent_identity.py', 'precedent_time.py',
            'precedent_consumer_shape.py']
    for f in real:
        _shutil.copy2(ROOT / 'tools' / f, work / 'tools' / f)
    stubs = {
        'precedent_check.py': (
            'import sys\n'
            'CHECKS = {"x": {"binds_publishers": True}}\n'
            'if __name__ == "__main__":\n'
            '    print("precedent_check: 3 passed, 0 violated")\n'),
        'leak_gate.py': '',
        'doc_lint.py': '',
        # consumer_shape imports these two for what a consumer receives.
        'build_views.py': ('def _engine_tool_paths(): return set()\n'
                           'def _json_str(v): return v\n'
                           'def ships_paths(fm): return []\n'),
        'split_practices.py': 'def _read_practice_file(p): return {}, {}\n',
    }
    for f, body in stubs.items():
        (work / 'tools' / f).write_text(body, encoding='utf-8')
    (work / 'tools' / 'ENGINE_MANIFEST.json').write_text(_json.dumps(
        {'kind': kind, 'files': real + list(stubs)}), encoding='utf-8')
    tests = work / 'tools' / 'checks' / 'tests'
    (tests / 'run_all.sh').write_text('exit 0\n', encoding='utf-8')
    (tests / 'test_in_copy.sh').write_text(
        'top="$(git rev-parse --show-toplevel)" || exit 1\n'
        'git rev-parse -q --verify HEAD >/dev/null || exit 1\n'
        '[ -z "$(git status --porcelain --untracked-files=no)" ] || '
        '{ git status --porcelain; exit 1; }\n'
        '[ -n "${CS_MARK:-}" ] && echo "ran in $(basename "$top")" >> "$CS_MARK"\n'
        'exit 0\n', encoding='utf-8')
    (work / 'precedent.json').write_text(_json.dumps({'base_branch': 'beta'}),
                                         encoding='utf-8')
    (work / 'list.txt').write_text('a\n', encoding='utf-8')
    for args in (['add', '-A'], ['commit', '-q', '-m', 'init'],
                 ['remote', 'add', 'origin', f'file://{bare}'],
                 ['push', '-q', 'origin', 'beta']):
        subprocess.run(['git', '-C', str(work), *args], env=git_env,
                       capture_output=True, text=True)
    return work, bare


def _engine_commit_env(tmp):
    """-> (ambient, person, person_git). `ambient` is what a hookless session
    had on 2026-09-26: git's global identity is the container's bot, no
    ~/.config/precedent/config.json, and a TZ that is not the person's --
    and nothing else from this machine (practice: fixture-owns-its-state).
    `person` is the PRECEDENT_COMMIT_* declaration on top of it;
    `person_git` authors the fixture's OWN commits as the person, so the
    only commits that can come out as the bot are the ones the engine made."""
    gcfg = tmp / 'gitconfig'
    gcfg.write_text('[user]\n\tname = Claude\n\temail = noreply@anthropic.com\n',
                    encoding='utf-8')
    ambient = {k: v for k, v in os.environ.items()
               if not k.startswith(('GIT_', 'PRECEDENT_', 'CLAUDE_'))
               and k != 'TZ'}
    ambient.update(GIT_CONFIG_GLOBAL=str(gcfg), GIT_CONFIG_NOSYSTEM='1',
                   PRECEDENT_USER_CONFIG=str(tmp / 'no-such-config.json'),
                   PRECEDENT_ALLOW_ANY_AUTHOR='1', TZ='America/New_York')
    person = dict(ambient, PRECEDENT_COMMIT_NAME='Pat Person',
                  PRECEDENT_COMMIT_EMAIL='pat@example.com',
                  PRECEDENT_COMMIT_TZ='Asia/Kolkata')
    person_git = dict(ambient, GIT_AUTHOR_NAME='Pat Person',
                      GIT_AUTHOR_EMAIL='pat@example.com',
                      GIT_COMMITTER_NAME='Pat Person',
                      GIT_COMMITTER_EMAIL='pat@example.com')
    return ambient, person, person_git


def _gh_if(expr, event_name, private, head_ref=''):
    """Evaluate a GitHub Actions job `if:` the way GitHub does, for the few
    operators the light check uses (&&, ||, !, ==, !=, startsWith, contains,
    true),
    against one event. Strict on purpose: anything else in the expression
    raises, so a template edit this cannot read fails loudly, never reads as
    "skips"."""
    import types
    e = expr.replace('!=', ' __NE__ ').replace('==', ' __EQ__ ')
    e = e.replace('&&', ' and ').replace('||', ' or ').replace('!', ' not ')
    e = e.replace('__NE__', '!=').replace('__EQ__', '==')
    e = re.sub(r'\btrue\b', 'True', re.sub(r'\bfalse\b', 'False', e))
    left = re.sub(r"'[^']*'", '', e)
    names = set(re.findall(r'[A-Za-z_][\w.]*', left)) - {
        'and', 'or', 'not', 'True', 'False', 'startsWith', 'contains',
        'github.event_name',
        'github.head_ref', 'github.event.repository.private'}
    if names:
        raise ValueError(f'the job if: uses {sorted(names)}, which this evaluator does not model')
    ns = types.SimpleNamespace
    github = ns(event_name=event_name, head_ref=head_ref,
                event=ns(repository=ns(private=private)))
    return bool(eval(e, {'__builtins__': {}}, {
        'github': github,
        'startsWith': lambda a, b: str(a or '').lower().startswith(str(b).lower()),
        'contains': lambda a, b: str(b).lower() in str(a or '').lower()}))


def _fixture_git_env():
    return dict(os.environ, GIT_AUTHOR_NAME='F', GIT_AUTHOR_EMAIL='f@x',
                GIT_COMMITTER_NAME='F', GIT_COMMITTER_EMAIL='f@x',
                GIT_CONFIG_GLOBAL=os.devnull, PRECEDENT_ALLOW_ANY_AUTHOR='1')


def _stale_ref_fixture_env(tmp):
    """The environment every throwaway repo in the stale-ref checks below
    runs git under: a fixed author, no global or system config, and no
    personal Precedent config, so nothing on the machine leaks in."""
    return dict(os.environ, PRECEDENT_ALLOW_ANY_AUTHOR='1',
                GIT_AUTHOR_NAME='T', GIT_AUTHOR_EMAIL='t' + chr(64) + 'example.com',
                GIT_COMMITTER_NAME='T',
                GIT_COMMITTER_EMAIL='t' + chr(64) + 'example.com',
                GIT_CONFIG_GLOBAL=str(tmp / 'gitconfig'),
                GIT_CONFIG_NOSYSTEM='1', GIT_TERMINAL_PROMPT='0',
                PRECEDENT_USER_CONFIG=str(tmp / 'config.json'))


def _promote_fixture(tmp, env, base_branch, tiers):
    """-> (work, git, branches, tip): a throwaway repo with a bare origin
    carrying `tiers`, stub checks that always pass, and the real
    precedent_branches.py and precedent_push_check.py. Same shape as
    check_promote_picks_its_step's fixture."""
    import json as _json, shutil as _shutil

    def git(cwd, *a):
        return subprocess.run(['git', '-C', str(cwd), *a],
                              capture_output=True, text=True, env=env)

    bare = tmp / 'origin.git'
    git(tmp, 'init', '-q', '--bare', '-b', 'main', str(bare))
    work = tmp / 'work'
    (work / 'tools').mkdir(parents=True)
    git(tmp, 'init', '-q', '-b', 'main', str(work))
    for f in ('precedent_push_check.py', 'precedent_branches.py', 'precedent_time.py'):
        _shutil.copy2(ROOT / 'tools' / f, work / 'tools' / f)
    (work / 'tools' / 'ENGINE_MANIFEST.json').write_text(
        _json.dumps({'kind': 'consumer'}), encoding='utf-8')
    for t in ('precedent_check', 'leak_gate', 'doc_lint'):
        (work / 'tools' / f'{t}.py').write_text(
            'import sys\n'
            + ('print("precedent_check: 3 passed, 0 violated")\n'
               if t == 'precedent_check' else '')
            + 'sys.exit(0)\n', encoding='utf-8')
    (work / 'precedent.json').write_text(
        _json.dumps({'base_branch': base_branch}), encoding='utf-8')
    (work / 'list.txt').write_text('a\n', encoding='utf-8')
    git(work, 'add', '-A')
    git(work, 'commit', '-q', '-m', 'init')
    git(work, 'remote', 'add', 'origin', f'file://{bare}')
    for b in tiers:
        git(work, 'push', '-q', 'origin', f'HEAD:refs/heads/{b}')

    def branches(*a):
        p = subprocess.run([sys.executable, 'tools/precedent_branches.py', *a],
                           cwd=work, capture_output=True, text=True, env=env)
        return p.returncode, p.stdout + p.stderr

    def tip(b):
        return git(work, 'ls-remote', 'origin',
                   f'refs/heads/{b}').stdout.split('\t')[0]
    return work, git, branches, tip


def check_killed_promote_releases_its_lock():
    """A Promote killed by SIGTERM still releases its lock.

    2026-09-28: a Promote run under a 590-second command limit was killed
    mid-check, and its claim on precedent-promote-lock sat on origin for the
    full stale window, so the same session's retry did nothing. try/finally
    never runs on SIGTERM unless something turns the signal into an
    exception. The fixture stubs everything around the lock: the step, the
    claim, and a run that blocks, so the only thing under test is whether
    the release still happens when the process is killed.
    """
    import tempfile
    tmp = pathlib.Path(tempfile.mkdtemp(prefix='precedent-lock-kill-'))
    cases = []
    try:
        marker = tmp / 'released'
        started = tmp / 'started'
        script = tmp / 'run.py'
        script.write_text(f"""
import sys, time, pathlib
sys.path.insert(0, {str(ROOT / 'tools')!r})
import precedent_branches as pb
pb.promotion_step = lambda root, to, work: (pb.MAIN, 'fixture')
pb.staging_branch = lambda root: pb.STAGING
pb.repo_has_tiers = lambda root: True
pb._lock_claim = lambda root, say: ('held', 'fixture-commit')
pb._lock_release = lambda root, held, say: pathlib.Path({str(marker)!r}).write_text(held)
def _run(root, say):
    pathlib.Path({str(started)!r}).write_text('1')
    time.sleep(60)
    return 0
pb._promote_to_main = _run
sys.exit(pb.promote('.', say=lambda *a: None))
""", encoding='utf-8')
        for sig_name in ('SIGTERM', 'SIGHUP'):
            import signal as _signal
            for f in (marker, started):
                f.unlink(missing_ok=True)
            proc = subprocess.Popen([sys.executable, str(script)], cwd=str(tmp))
            deadline = time.time() + 20
            while not started.exists() and time.time() < deadline:
                time.sleep(0.05)
            proc.send_signal(getattr(_signal, sig_name))
            try:
                proc.wait(timeout=20)
            except subprocess.TimeoutExpired:
                proc.kill()
            cases.append((f'a Promote killed by {sig_name} mid-run releases '
                          f'the lock it holds',
                          marker.exists() and marker.read_text() == 'fixture-commit',
                          f'exit {proc.returncode}, released={marker.exists()}'))
            cases.append((f'...and exits non-zero, so nothing reads the kill '
                          f'as a finished Promote ({sig_name})',
                          proc.returncode not in (0, None), f'exit {proc.returncode}'))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    bad = [(n, d) for n, ok, d in cases if not ok]
    check(f'a killed Promote releases its lock ({len(cases)} stated cases)',
          not bad, '; '.join(f'{n} ({d})' for n, d in bad))


def check_produce_sees_main_changes_staging_carries():
    """A red main whose tip changes nothing staging lacks does not hold Produce.

    2026-10-05: main's GitHub test went red on a Produce's own merge commit
    because its jobs never got a runner. main_test_holds_produce asked
    whether staging descends from main's tip, said "Debut first", and the
    Debut had nothing to take down -- a merge commit changes no file -- so
    the session went round in a circle. The hold now also lifts when
    staging already carries every change main's tip brings (and its tree
    passed the full local check). The control keeps the hold for a main
    tip that changes a file staging lacks.
    """
    import tempfile
    tmp = pathlib.Path(tempfile.mkdtemp(prefix='precedent-produce-carried-'))
    cases = []
    try:
        origin, r = tmp / 'origin.git', tmp / 'r'
        def git(*a, cwd=None):
            return subprocess.run(['git', *a], cwd=str(cwd or r),
                                  capture_output=True, text=True)
        git('init', '-q', '--bare', str(origin), cwd=tmp)
        git('clone', '-q', str(origin), str(r), cwd=tmp)
        git('config', 'user.email', 'fixture@example.com')
        git('config', 'user.name', 'fixture')
        (r / 'a.txt').write_text('one\n')
        git('add', '.')
        git('commit', '-qm', 'base')
        git('branch', '-M', 'main')
        git('checkout', '-qb', 'staging')
        (r / 'a.txt').write_text('two\n')
        git('commit', '-qam', 'work on staging')
        git('checkout', '-q', 'main')
        git('merge', '-q', '--no-ff', '-m', 'Merge pull request: Produce', 'staging')
        git('push', '-q', 'origin', 'main', 'staging')
        script = tmp / 'run.py'
        script.write_text(f"""
import sys
sys.path.insert(0, {str(ROOT / 'tools')!r})
import precedent_branches as pb
pb._gets_github_test = lambda root, b: True
pb.github_tests = lambda root, sha: ['deep-check.yml']
pb.github_test_state = lambda root, sha, tests, gh=None: ('failed', 'fixture')
pb.staging_branch = lambda root: 'staging'
pb._receipt = lambda root, sha: True
print(repr(pb.main_test_holds_produce({str(r)!r}, say=lambda *a: None)))
""", encoding='utf-8')
        def run():
            out = subprocess.run([sys.executable, str(script)], capture_output=True,
                                 text=True)
            return out.stdout.strip(), out.stderr[-400:]
        got, err = run()
        cases.append(("a main tip that is a no-change merge of staging does not "
                      "hold Produce", got == 'None', got or err))
        (r / 'b.txt').write_text('a change only main has\n')
        git('add', '.')
        git('commit', '-qm', 'direct push to main')
        git('push', '-q', 'origin', 'main')
        got, err = run()
        cases.append(("...and a main tip with a file change staging lacks still "
                      "holds it, naming Debut", 'Debut first' in got, got or err))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    bad = [(n, d) for n, ok, d in cases if not ok]
    check(f'Produce sees main changes staging already carries ({len(cases)} '
          f'stated cases)', not bad, '; '.join(f'{n} ({d})' for n, d in bad))


def check_engine_commits_state_their_author():
    """Every commit the engine makes states its author (2026-09-26).

    A session rooted above four attached practice sets ran no SessionStart
    hook, so git kept the container's global identity, and no
    ~/.config/precedent/config.json existed. PRECEDENT_COMMIT_NAME/EMAIL were
    in the environment and nothing turned them into git's author: every
    merge and lock commit Promote made came out as the bot, in all four
    sets. `git merge` and `git commit-tree` run no `pre-commit`, so the
    global backstop never saw them. And Promote's full check refused every
    real run in a source, because consumer_shape would not run in the linked
    worktree Promote always checks in.

    Since 2026-10-17 the commits are the ones the move into main makes: the copy of staging merged with main that its pull
    request comes from, and the Promote lock's.

    The fixture reproduces that session exactly -- bot global identity, no
    user config, a TZ that is not the person's -- and asserts on the commits
    Promote actually pushed. THE CONTROL: the same Promote with nobody
    declared still authors as the bot (a shared repo has no person to be
    wrong about), which proves the fixture's ambient identity really is the
    bot, so the declared case is not passing by accident. And a repository
    that IS somebody's individual source, with an identity.json nobody can
    be read out of, refuses the commit in the tool's own words rather than
    making it (practice: control-asserts-which-failure)."""
    import tempfile
    name = ('Engine commits state their author: Promote in a hookless '
            'session authors as the declared person, in their zone')
    need = ['precedent_branches.py', 'precedent_identity.py',
            'precedent_time.py', 'precedent_consumer_shape.py']
    absent = [f for f in need if not (ROOT / 'tools' / f).exists()]
    if absent:
        not_applicable(name, f'not in this tree: {absent}')
        return
    cases = []
    with tempfile.TemporaryDirectory() as td:
        tmp = pathlib.Path(td)
        ambient, person, person_git = _engine_commit_env(tmp)

        def run_in(work, env, *args):
            p = subprocess.run([sys.executable, 'tools/precedent_branches.py',
                                *args], cwd=work, capture_output=True,
                               text=True, env=env)
            return p.returncode, p.stdout + p.stderr

        def git(work, *args):
            return subprocess.run(['git', '-C', str(work), *args],
                                  capture_output=True, text=True,
                                  env=person_git).stdout.strip()

        def to_staging(work, path, text, msg):
            # main holds what beta had, then beta gains an edit and a commit
            # main also gained, so the copy is a real merge the engine makes.
            git(work, 'fetch', '-q', 'origin')
            git(work, 'push', '-q', 'origin', 'origin/beta:refs/heads/main')
            git(work, 'checkout', '-q', '-B', 'm', 'origin/beta')
            (work / 'main-only.txt').write_text('m\n', encoding='utf-8')
            git(work, 'add', 'main-only.txt')
            git(work, 'commit', '-q', '-m', 'a change made on main')
            git(work, 'push', '-q', 'origin', 'HEAD:refs/heads/main')
            git(work, 'checkout', '-q', '-B', 'w', 'origin/beta')
            (work / path).write_text(text, encoding='utf-8')
            git(work, 'add', path)
            git(work, 'commit', '-q', '-m', msg)
            git(work, 'push', '-q', 'origin', 'HEAD:refs/heads/beta')

        def copy_head(work):
            git(work, 'fetch', '-q', 'origin')
            # The copy's name: the session-branch format, or the dated
            # to-main- name where no workflow knows the new one (a fixture).
            refs = [r for r in git(work, 'for-each-ref', '--format=%(refname:short)',
                                   'refs/remotes/origin/').split()
                    if 'promote-to-main' in r or '/to-main-' in r]
            return git(work, 'log', '-1', '--format=%an|%ae|%ad|%s',
                       '--date=format:%z', refs[-1]) if refs else ''

        def head_of(work, branch):
            git(work, 'fetch', '-q', 'origin')
            return git(work, 'log', '-1', '--format=%an|%ae|%ad|%s',
                       '--date=format:%z', f'origin/{branch}')

        # 1. Declared by PRECEDENT_COMMIT_* alone, in a practice SOURCE --
        #    so the full check includes consumer_shape.
        work, _ = _engine_commit_fixture(tmp, 'work', 'source', person_git)
        to_staging(work, 'list.txt', 'b\n', 'an edit to promote')
        rc, out = run_in(work, person, '--promote', '--to', 'main')
        cases.append((f'the move into main in a hookless session gets as far as '
                      f'its pull request (rc={rc}, '
                      f'{out.strip().splitlines()[-1][:160] if out.strip() else ""!r})',
                      'READY FOR MAIN' in out))
        got = copy_head(work)
        cases.append((f'the merge commit it makes is authored by the declared '
                      f'person, not git\'s global bot identity (got {got!r})',
                      got.startswith('Pat Person|pat@example.com|')
                      and '|Promote beta into main' in got))
        cases.append((f'and dated in the declared zone (+0530), not the '
                      f'ambient TZ (got {got!r})', '|+0530|Promote' in got))
        lock = head_of(work, 'precedent-promote-lock')
        cases.append((f'the Promote lock commits are authored the same way '
                      f'(got {lock!r})',
                      lock.startswith('Pat Person|pat@example.com|')))

        # 2. THE CONTROL: nobody declared, a shared repository.
        work2, _ = _engine_commit_fixture(tmp, 'shared', 'consumer', person_git)
        to_staging(work2, 'list.txt', 'c\n', 'another edit')
        rc, out = run_in(work2, ambient, '--promote', '--to', 'main')
        got = copy_head(work2)
        cases.append((f'control: with nobody declared, the same Promote still '
                      f'authors as git\'s global identity -- the bot this '
                      f'fixture set, so case 1 is not passing by accident '
                      f'(rc={rc}, got {got!r})',
                      got.startswith('Claude|noreply@anthropic.com|')))

        # 3. An individual source nobody can be read out of: refused.
        work3, _ = _engine_commit_fixture(tmp, 'indiv', 'source', person_git)
        (work3 / 'identity.json').write_text('{"name": "no email here"}\n',
                                             encoding='utf-8')
        git(work3, 'add', 'identity.json')
        git(work3, 'commit', '-q', '-m', 'an unreadable declaration')
        git(work3, 'push', '-q', 'origin', 'beta')
        to_staging(work3, 'list.txt', 'd\n', 'an edit')
        before = head_of(work3, 'main')
        rc, out = run_in(work3, ambient, '--promote', '--to', 'main')
        cases.append((f'an individual source with no resolvable author '
                      f'REFUSES the commit and moves nothing (rc={rc}, '
                      f'{out.strip()[-160:]!r})',
                      rc == 1 and 'REFUSED: no commit was made' in out
                      and 'identity.json' in out
                      and head_of(work3, 'main') == before and not copy_head(work3)))
    failed = [n for n, ok in cases if not ok]
    check(f'{name} ({len(cases)} stated cases)', not failed, '; '.join(failed))


def check_to_main_copy_name_is_never_taken():
    """The copy a Promote into main pushes never reuses a name origin has,
    however many Promotes fall in one second.

    2026-10-19: the fallback name was the current second, so a third
    Promote within it named the same copy and its push was refused as
    non-fast-forward. "the work just done, on staging, goes into main"
    failed only on GitHub's faster runner (run 39259090526), once its
    output was printed (#1221). Negative control: the old fallback returns
    a taken name and fails the first case."""
    sys.path.insert(0, str(ROOT / 'tools'))
    import precedent_branches as pb
    saved = (pb._workflows_know_new_copy_names, pb._day_and_moment, pb._remote_tip)
    taken = {'to-main-2026-10-19', 'to-main-1792416365', 'to-main-1792416365-2'}
    try:
        pb._workflows_know_new_copy_names = lambda root: False
        pb._day_and_moment = lambda root: ('2026-10-19', '1792416365')
        pb._remote_tip = lambda root, name: 'abc' if name in taken else None
        got = pb._to_main_copy('.')
        taken.discard('to-main-2026-10-19')
        first = pb._to_main_copy('.')
    finally:
        pb._workflows_know_new_copy_names, pb._day_and_moment, pb._remote_tip = saved
    cases = [('a name origin already has, at the same second twice over, is '
              'never returned', got == 'to-main-1792416365-3', got),
             ('...and the dated name is still the first choice when free',
              first == 'to-main-2026-10-19', first)]
    bad = [(n, d) for n, ok, d in cases if not ok]
    check(f'a Promote copy\'s name is never one origin has ({len(cases)} stated '
          f'cases)', not bad, '; '.join(f'{n} ({d})' for n, d in bad))


def check_promote_picks_its_step():
    """Promote moves staging into main, and says so before anything else
    (Morgan, 2026-09-26: print "now promoting staging to main"). It has no
    step into staging (Morgan, 2026-10-17, strength: decided): asked for, it moves nothing and says work reaches
    staging by Booked.

    The cases that matter: staging moves into main only through a throwaway
    copy, main itself untouched by the script; the work the session names
    (--work) must be on staging already; and nothing waiting prints no "Now
    promoting" line at all."""
    sys.path.insert(0, str(ROOT / 'tools'))
    import precedent_branches as pb  # is_fix_branch / is_main_copy: new names and old
    import tempfile, json as _json, shutil as _shutil
    name = 'Promote moves staging into main, and says so first'
    tool = ROOT / 'tools' / 'precedent_branches.py'
    if not tool.exists():
        not_applicable(name, 'tools/precedent_branches.py is absent')
        return
    cases = []
    with tempfile.TemporaryDirectory() as td:
        tmp = pathlib.Path(td)
        env = dict(os.environ, PRECEDENT_ALLOW_ANY_AUTHOR='1',
                   GIT_AUTHOR_NAME='T', GIT_AUTHOR_EMAIL='t@example.com',
                   GIT_COMMITTER_NAME='T', GIT_COMMITTER_EMAIL='t@example.com',
                   GIT_CONFIG_GLOBAL=str(tmp / 'gitconfig'),
                   PRECEDENT_USER_CONFIG=str(tmp / 'config.json'))

        def git(cwd, *a):
            return subprocess.run(['git', '-C', str(cwd), *a],
                                  capture_output=True, text=True, env=env)

        bare = tmp / 'origin.git'
        git(tmp, 'init', '-q', '--bare', '-b', 'main', str(bare))
        work = tmp / 'work'
        (work / 'tools').mkdir(parents=True)
        git(tmp, 'init', '-q', '-b', 'main', str(work))
        for f in ('precedent_push_check.py', 'precedent_branches.py', 'precedent_time.py'):
            _shutil.copy2(ROOT / 'tools' / f, work / 'tools' / f)
        (work / 'tools' / 'ENGINE_MANIFEST.json').write_text(
            _json.dumps({'kind': 'consumer'}), encoding='utf-8')
        for t in ('precedent_check', 'leak_gate', 'doc_lint'):
            (work / 'tools' / f'{t}.py').write_text(
                'import sys\n'
                + ('print("precedent_check: 3 passed, 0 violated")\n'
                   if t == 'precedent_check' else '')
                + 'sys.exit(0)\n', encoding='utf-8')
        (work / 'precedent.json').write_text(
            _json.dumps({'base_branch': 'staging'}), encoding='utf-8')
        (work / 'list.txt').write_text('a\n', encoding='utf-8')
        git(work, 'add', '-A')
        git(work, 'commit', '-q', '-m', 'init')
        git(work, 'remote', 'add', 'origin', f'file://{bare}')
        for b in ('main', 'staging'):
            git(work, 'push', '-q', 'origin', f'HEAD:refs/heads/{b}')

        def branches(*a):
            p = subprocess.run([sys.executable, 'tools/precedent_branches.py', *a],
                               cwd=work, capture_output=True, text=True, env=env)
            return p.returncode, p.stdout + p.stderr

        def tip(b):
            return git(work, 'ls-remote', 'origin', f'refs/heads/{b}').stdout.split('\t')[0]

        def commit_to(branch, path, text):
            git(work, 'fetch', '-q', 'origin')
            git(work, 'checkout', '-q', '-B', f'w-{branch}', f'origin/{branch}')
            (work / path).write_text(text, encoding='utf-8')
            git(work, 'add', path)
            git(work, 'commit', '-q', '-m', f'edit {path} on {branch}')
            git(work, 'push', '-q', 'origin', f'HEAD:refs/heads/{branch}')
            return git(work, 'rev-parse', 'HEAD').stdout.strip()

        rc, out = branches('--promote')
        cases.append(('nothing waiting anywhere: nothing to promote, and no '
                      '"Now promoting" line', rc == 0 and 'nothing to promote' in out
                      and 'Now promoting' not in out))

        rc, out = branches('--promote', '--to', 'nowhere')
        cases.append(('an unknown --to is refused with the usage line',
                      rc == 2 and 'usage:' in out))

        commit_to('staging', 'one.txt', '1\n')
        staging_before = tip('staging')
        rc, out = branches('--promote', '--to', 'staging')
        cases.append(('the retired step into staging moves nothing and says work '
                      'reaches staging by Booked', rc == 0
                      and 'no step into staging' in out and 'Now promoting' not in out
                      and tip('staging') == staging_before))

        main_before = tip('main')
        rc, out = branches('--promote')
        copies = [r for r in (l.split('\t')[1] for l in git(
            work, 'ls-remote', 'origin', 'refs/heads/*').stdout.splitlines())
            if pb.is_main_copy(r[len('refs/heads/'):])]
        sys.path.insert(0, str(ROOT / 'tools'))
        import precedent_time as _pt
        sys.path.pop(0)
        cases.append(('the copy is named for the day, by precedent_time, not its '
                      'quiet fallback', bool(copies) and all(
                          _pt.today(work) in c[len('refs/heads/'):]
                          for c in copies), copies))
        cases.append(('staging goes into main, said in '
                      'those words, exiting 3 since main has not moved yet',
                      rc == 3 and out.startswith(
                          'Now promoting from staging to main')
                      and 'READY FOR MAIN' in out))
        # Since 2026-10-07 the copy is staging merged with main -- the tree
        # the full check judged -- so the pull request's merge has main as an
        # ancestor of its head and main's push test recognises it.
        copy_ref = copies[0].split('refs/heads/', 1)[1] if len(copies) == 1 else ''
        holds = (lambda a, b: git(work, 'merge-base', '--is-ancestor', a, b)
                 .returncode == 0)
        cases.append(('into main by a throwaway copy of staging merged with main, '
                      'main itself untouched',
                      tip('main') == main_before and bool(copy_ref)
                      and holds(tip('staging'), tip(copy_ref))
                      and holds(main_before, tip(copy_ref))))
        cases.append(('it says the pull request comes from the copy, never from '
                      'staging', 'Never open it from staging itself' in out))

        # PROMOTE'S COPY, THEN THE MERGE CHECK, END TO END (2026-10-08). The
        # copy became a merge of staging and main on 2026-10-07 while the
        # merge check still let only staging's own tip into main, so every
        # Produce was refused as "out of date" with staging unmoved. Each copy
        # below goes through merge_refusal with promote_only on, as the merge
        # gate would put it.
        indiv = tmp / 'indiv'
        indiv.mkdir()
        (indiv / 'identity.json').write_text(_json.dumps(
            {'email': 'p@example.com', 'promote_only': True}), encoding='utf-8')
        gate_cfg = tmp / 'gate-config.json'
        gate_cfg.write_text(_json.dumps({'individual': {'path': str(indiv)}}),
                            encoding='utf-8')

        def all_copies():
            return sorted(r[len('refs/heads/'):] for r in (
                l.split('\t')[1] for l in git(work, 'ls-remote', 'origin',
                                               'refs/heads/*').stdout.splitlines())
                if pb.is_main_copy(r[len('refs/heads/'):]))

        def gate(ref):
            sha = tip(ref)
            heads = [l.split('\t')[1][len('refs/heads/'):] for l in git(
                work, 'ls-remote', '--heads', 'origin').stdout.splitlines()
                if l.split('\t')[0] == sha]
            return pb.merge_refusal(work, ['main'], heads, str(gate_cfg),
                                    head_sha=sha)

        first_copy = copy_ref
        why = gate(first_copy) if first_copy else 'no copy'
        cases.append(("main already in staging: the copy is staging's own tip, "
                      'and the merge check lets it into main',
                      bool(first_copy) and tip(first_copy) == tip('staging')
                      and why is None, why))

        # Land the fold-in the way the pull request would.
        git(work, 'fetch', '-q', 'origin')
        git(work, 'checkout', '-q', '-B', 'w-main', 'origin/main')
        git(work, 'merge', '-q', '--no-ff', '-m', 'fold', 'origin/staging')
        git(work, 'push', '-q', 'origin', 'HEAD:refs/heads/main')

        on_staging = commit_to('staging', 'two.txt', '2\n')
        seen = set(all_copies())
        rc, out = branches('--promote', '--to', 'main', '--full', '--because', 'test the long way', '--work', on_staging)
        # The long way's first line names the person's words; the step comes
        # next.
        cases.append(('the step named: --to main, the long way when asked for',
                      rc == 3 and out.startswith('the full route into main, '
                                                 'because the person asked')
                      and out.splitlines()[1].startswith(
                          'Now promoting from staging to main')))
        merge_copy = next(iter(set(all_copies()) - seen), '')
        parents = git(work, 'rev-list', '--parents', '-n', '1',
                      tip(merge_copy)).stdout.split() if merge_copy else []
        why = gate(merge_copy) if merge_copy else 'no copy'
        cases.append(('main not in staging: the copy is a merge of main and '
                      "staging's tip, and the merge check lets it into main "
                      '(it refused every one, 2026-10-08)',
                      len(parents) == 3 and parents[2] == tip('staging')
                      and parents[1] == tip('main') and why is None, why))
        why = gate(first_copy) or ''
        cases.append(('a copy made before staging moved is refused as out of '
                      'date', 'out of date' in why, why))
        # A copy carrying a change of its own beyond the merge is not a copy.
        git(work, 'checkout', '-q', '--detach', tip(merge_copy))
        (work / 'extra.txt').write_text('x\n', encoding='utf-8')
        git(work, 'add', 'extra.txt')
        git(work, 'commit', '-q', '--amend', '--no-edit')
        git(work, 'push', '-q', 'origin', 'HEAD:refs/heads/to-main-20991231T000000-0300')
        why = gate('to-main-20991231T000000-0300') or ''
        cases.append(('a copy whose merge carries a file the merge never made is '
                      'refused', why != '', why))
        git(work, 'push', '-q', 'origin', ':refs/heads/to-main-20991231T000000-0300')
        rc, out = branches('--promote', '--work', on_staging)
        cases.append(('the work just done, on staging, goes into main',
                      rc == 3 and out.startswith('Now promoting from staging to main'),
                      f'rc={rc}: {out[-600:]}'))
        git(work, 'checkout', '-q', '-B', 'w-feature', 'origin/staging')
        (work / 'four.txt').write_text('4\n', encoding='utf-8')
        git(work, 'add', 'four.txt')
        git(work, 'commit', '-q', '-m', 'not landed')
        git(work, 'push', '-q', 'origin', 'HEAD:refs/heads/w-feature')
        rc, out = branches('--promote', '--work', 'w-feature')
        cases.append(('work not on staging yet is not promoted: Book it first',
                      rc == 0 and 'not on staging yet' in out
                      and 'Now promoting' not in out))
        rc, out = branches('--promote', '--work', 'no-such-thing')
        cases.append(('a --work it cannot see chooses nothing and says why',
                      rc == 0 and 'is not a branch or commit' in out
                      and 'Now promoting' not in out))
        wts = git(work, 'worktree', 'list').stdout.strip().splitlines()
        cases.append(('no worktree is left behind', len(wts) == 1))
    failed = [c[0] + (f' ({c[2]})' if len(c) > 2 and c[2] else '')
              for c in cases if not c[1]]
    check(f'{name} ({len(cases)} stated cases)', not failed, '; '.join(failed))


def check_main_test_minutes_rule():
    """Morgan, 2026-10-01: "I really want to make sure that github minutes
    only run if it's main AND (it's a public repo OR (that user's
    precedent-individual has it enabled AND it's been the # of hours or more
    listed in ci_every_hours))".

    Three independent views of the same rule, so one cannot hide a mistake
    in another: (1) the light-check template's own `on:` and job `if:`,
    evaluated against every event that could start it; (2) every combination
    of visibility, switch, hours and time since the last pass, through
    Promote's decision AND the template together, compared with the rule;
    (3) a real Promote into main in a scratch repository, reading the branch
    name it actually pushed. The deliberate exceptions -- where it runs
    although the rule alone would not -- are asserted separately and named,
    so a change to any of them is a visible decision, not drift."""
    import importlib.util, itertools, json as _json, shutil as _shutil, tempfile
    import time as _time
    name = "GitHub minutes run only on main, and in a private repo only when switched on and due"
    src = ROOT / 'tools' / 'precedent_branches.py'
    tpl = ROOT / 'templates' / 'github-actions' / 'light-check.yml.template'
    try:
        import yaml as _yaml
    except ImportError:
        not_applicable(name, 'PyYAML is not installed, and the template is read with it')
        return
    if not src.exists() or not tpl.is_file():
        not_applicable(name, 'tools/precedent_branches.py or the light-check template is absent')
        return
    spec = importlib.util.spec_from_file_location('_pb_minutes', src)
    pb = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(pb)
    cases = []
    doc = _yaml.safe_load(tpl.read_text(encoding='utf-8'))
    on = doc.get('on', doc.get(True)) or {}
    expr = doc['jobs']['light-check']['if']

    def starts(event, branch, private, head_ref=''):
        """-> True when GitHub would start a runner: a trigger matches, then
        the job's if: holds. `branch` is the pushed branch, or the pull
        request's base."""
        trig = on.get(event, None) if isinstance(on, dict) else None
        if event not in on:
            return False
        branches = (trig or {}).get('branches') if isinstance(trig, dict) else None
        if branches is not None and branch not in branches:
            return False
        return _gh_if(expr, event, private, head_ref)

    # (1) Every event shape, against the rule's first half: never off main.
    for private in (False, True):
        kind = 'private' if private else 'public'
        for b in ('staging', 'claude/feature-x'):
            cases.append((f'{kind}: a push to {b} starts no runner',
                          not starts('push', b, private)))
            cases.append((f'{kind}: a pull request into {b} starts no runner',
                          not starts('pull_request', b, private, 'claude/feature-x')))
    cases.append(('public: a push to main runs (a public repo tests every push to main)',
                  starts('push', 'main', False)))
    cases.append(('private: a push to main starts no runner, ever',
                  not starts('push', 'main', True)))
    cases.append(('private: a Promote copy that is NOT DUE starts no runner',
                  not starts('pull_request', 'main', True, pb.NOT_DUE_PREFIX + '2026-10-01')))
    cases.append(('public: a not-due name is ignored, and the test runs',
                  starts('pull_request', 'main', False, pb.NOT_DUE_PREFIX + '2026-10-01')))
    cases.append(('private: a Promote copy that IS due runs',
                  starts('pull_request', 'main', True, 'to-main-2026-10-01')))
    cases.append(('private: a pull request into main from a working branch -- not a '
                  'Promote copy, so nobody judged it -- starts no runner',
                  not starts('pull_request', 'main', True, 'claude/feature-x')))
    cases.append(('...nor one from staging itself',
                  not starts('pull_request', 'main', True, 'staging')))
    cases.append(('...nor "x-to-main-...": the copy name is matched as a prefix',
                  not starts('pull_request', 'main', True, 'x-to-main-2026-10-01')))
    # The session-branch names a Promote's copies carry since 2026-10-06.
    cases.append(('private: a copy named like a session branch that IS due runs',
                  starts('pull_request', 'main', True,
                         'claude/2026-10-06-promote-to-main-y1ktn')))
    cases.append(('private: one that is NOT DUE starts no runner',
                  not starts('pull_request', 'main', True,
                             'claude/2026-10-06-promote-to-main-not-due-y1ktn')))
    cases.append(('...and what Promote names them is what the template reads',
                  pb.is_main_copy('claude/2026-10-06-promote-to-main-y1ktn')
                  and pb.is_not_due_copy('claude/2026-10-06-promote-to-main-not-due-y1ktn')
                  and pb.COPY_NAME_MARKER in tpl.read_text(encoding='utf-8')))
    # A DELIBERATE EXCEPTION, named so it stays a decision: GitHub's if: has
    # no pattern matching, so a hand-named branch whose slug happens to say
    # "promote-to-main" reads as a copy there. It would run one test on a
    # private pull request into main; the engine's own reading is exact.
    cases.append(('EXCEPTION: a branch whose slug says promote-to-main runs there, '
                  'and only there -- the engine does not take it for a copy',
                  starts('pull_request', 'main', True,
                         'claude/2026-10-06-merge-promote-to-main-docs-y1ktn')
                  and not pb.is_main_copy('claude/2026-10-06-merge-promote-to-main-docs-y1ktn')))
    cases.append(('public: a pull request into main from a working branch runs',
                  starts('pull_request', 'main', False, 'claude/feature-x')))
    cases.append(('a run started by hand runs in either kind of repository',
                  starts('workflow_dispatch', 'main', True)
                  and starts('workflow_dispatch', 'main', False)))

    # (2) The whole table, through Promote's decision and the template.
    saved_force = os.environ.pop(pb.FORCE_ENV, None)
    WF = '.github/workflows/light-check.yml'
    now = _time.time()

    class GH:
        def __init__(self, hours_ago):
            self.hours_ago = hours_ago

        def call(self, path, cache=True):
            if self.hours_ago is None:
                return {'workflow_runs': []}, None
            return {'workflow_runs': [{
                'path': WF, 'status': 'completed', 'conclusion': 'success',
                'head_branch': 'to-main-2026-09-20', 'html_url': 'U',
                'created_at': _time.strftime('%Y-%m-%dT%H:%M:%SZ', _time.gmtime(
                    now - self.hours_ago * 3600))}]}, None
    pb._slug = lambda root: 'o/r'
    pb.github_tests = lambda root, sha: [(WF, True)]
    real_git = pb._git
    pb._git = lambda root, *a: (('on: {}\n# ' + pb.NOT_DUE_PREFIX) if a[:1] == ('show',)
                                else '' if a[:2] == ('diff', '--name-only')
                                else real_git(root, *a))
    wrong = []
    rows = 0
    with tempfile.TemporaryDirectory() as td:
        tmp = pathlib.Path(td)
        repo, me = tmp / 'repo', tmp / 'me'
        repo.mkdir()
        me.mkdir()
        cfg = tmp / 'config.json'
        cfg.write_text(_json.dumps({'individual': {'path': str(me)}}), encoding='utf-8')
        visibilities = ('public', 'private', None)
        switches = ('enabled', 'disabled', 'disable', None)      # None = not declared
        hours_set = (0, 24, 168, None, 'weekly')                 # None = not declared
        last_pass = (1, 23, 25, 167, 169, 1000, None)            # hours ago; None = never
        for vis, sw, hrs, ago in itertools.product(visibilities, switches, hours_set, last_pass):
            pj = {'base_branch': 'main'}
            if vis:
                pj['visibility'] = vis
            (repo / 'precedent.json').write_text(_json.dumps(pj), encoding='utf-8')
            ident = {'email': 'me@example.com'}
            if sw is not None:
                ident['ci_workflows'] = sw
            if hrs is not None:
                ident['ci_every_hours'] = hrs
            (me / 'identity.json').write_text(_json.dumps(ident), encoding='utf-8')
            private = vis == 'private'
            due, why = pb.main_test_due(repo, 'TIP', gh=GH(ago), user_config=cfg)
            copy = ('to-main-' if due else pb.NOT_DUE_PREFIX) + '2026-10-01'
            ran = starts('pull_request', 'main', private, copy)
            # The rule, written out as Morgan wrote it. An undeclared or
            # non-numeric hours value is 0 (every Promote); an undeclared
            # switch is on (his "assume yes"); a typo is off.
            on_ = sw in ('enabled', None)
            h = hrs if isinstance(hrs, (int, float)) and not isinstance(hrs, bool) else 0
            elapsed = ago is None or ago >= h
            expected = (not private) or (on_ and elapsed)
            rows += 1
            if ran != expected:
                wrong.append(f'{vis}/{sw}/{hrs}h/last {ago}h ago: ran={ran}, rule says '
                             f'{expected} ({why})')
        cases.append((f'all {rows} combinations of visibility, switch, hours and time '
                      f'since the last pass run exactly when the rule says',
                      not wrong))

        # The deliberate exceptions: each RUNS although the rule alone would
        # not, because its inputs say the window cannot be trusted. Asserted,
        # so dropping one is a decision someone makes in this file.
        (repo / 'precedent.json').write_text(_json.dumps(
            {'base_branch': 'main', 'visibility': 'private'}), encoding='utf-8')
        (me / 'identity.json').write_text(_json.dumps(
            {'email': 'me@example.com', 'ci_workflows': 'enabled', 'ci_every_hours': 168}),
            encoding='utf-8')
        d, _ = pb.main_test_due(repo, 'TIP', gh=GH(10), user_config=cfg)
        cases.append(('baseline for the exceptions: enabled, 168h, passed 10h ago -> not due',
                      d is False))

        class FailGH(GH):
            def call(self, path, cache=True):
                data, _ = super().call(path)
                data['workflow_runs'].insert(0, dict(data['workflow_runs'][0],
                                                     conclusion='failure', created_at=_time.strftime(
                                                         '%Y-%m-%dT%H:%M:%SZ', _time.gmtime(now - 3600))))
                return data, None

        class DownGH:
            def call(self, path, cache=True):
                return None, 'HTTP 503'
        exceptions = [
            ('a failed newest run', lambda: pb.main_test_due(repo, 'TIP', gh=FailGH(10), user_config=cfg)),
            ('GitHub not answering', lambda: pb.main_test_due(repo, 'TIP', gh=DownGH(), user_config=cfg)),
        ]
        for label, fn in exceptions:
            d, why = fn()
            cases.append((f'EXCEPTION, runs inside the window: {label} ({why[:60]})', d is True))
        pb._git = lambda root, *a: ('on: {}\n' if a[:1] == ('show',) else ''
                                    if a[:2] == ('diff', '--name-only') else real_git(root, *a))
        d, why = pb.main_test_due(repo, 'TIP', gh=GH(10), user_config=cfg)
        cases.append(('EXCEPTION, runs inside the window: an installed workflow older '
                      'than the skip (it would run anyway)', d is True))
        pb._git = real_git
        os.environ[pb.FORCE_ENV] = '1'
        d, why = pb.main_test_due(repo, 'TIP', gh=GH(10), user_config=cfg)
        os.environ.pop(pb.FORCE_ENV, None)
        cases.append((f'EXCEPTION, a person asking: {pb.FORCE_ENV}=1 runs it', d is True))

        # (3) A real Promote into main, in a scratch repository with a bare
        # origin: which branch name does it actually push?
        env = dict(os.environ, GIT_AUTHOR_NAME='T', GIT_AUTHOR_EMAIL='t@example.com',
                   GIT_COMMITTER_NAME='T', GIT_COMMITTER_EMAIL='t@example.com',
                   GIT_CONFIG_GLOBAL=str(tmp / 'gitconfig'), PRECEDENT_ALLOW_ANY_AUTHOR='1')

        def git(cwd, *a):
            return subprocess.run(['git', '-C', str(cwd), *a], capture_output=True,
                                  text=True, env=env)
        bare, work = tmp / 'origin.git', tmp / 'work'
        git(tmp, 'init', '-q', '--bare', '-b', 'main', str(bare))
        git(tmp, 'init', '-q', '-b', 'main', str(work))
        (work / '.github' / 'workflows').mkdir(parents=True)
        _shutil.copy2(tpl, work / '.github' / 'workflows' / 'light-check.yml')
        (work / 'precedent.json').write_text(_json.dumps(
            {'base_branch': 'main', pb.STAGING_KEY: 'staging',
             'visibility': 'private'}), encoding='utf-8')
        (work / 'notes.md').write_text('one\n', encoding='utf-8')
        git(work, 'add', '-A')
        git(work, 'commit', '-qm', 'start')
        git(work, 'remote', 'add', 'origin', str(bare))
        git(work, 'push', '-q', 'origin', 'main')
        git(work, 'push', '-q', 'origin', 'main:staging')
        saved_env = {k: os.environ.get(k) for k in env}
        os.environ.update(env)
        pb2 = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(pb2)
        pb2._check = lambda root, wt, tier, dest=None: (True, 'this exact tree already passed')
        pb2._slug = lambda root: 'o/r'
        pb2.USER_CONFIG_ENV = '_PB_TEST_UNUSED'
        pb2.DEFAULT_USER_CONFIG = cfg
        pushed = {}
        try:
            for label, ago in (('passed 10h ago', 10), ('passed 200h ago', 200)):
                git(work, 'checkout', '-q', '-B', 'staging', 'origin/staging')
                (work / 'notes.md').write_text(f'{label}\n', encoding='utf-8')
                git(work, 'commit', '-qam', f'work: {label}')
                git(work, 'push', '-q', 'origin', 'staging')
                before = set(git(work, 'ls-remote', '--heads', 'origin').stdout.split())
                pb2.last_main_test_pass = (lambda a: lambda root, tests, gh=None:
                                           (_time.time() - a * 3600, None))(ago)
                said = []
                rc = pb2._promote_to_main(str(work), said.append)
                after = set(git(work, 'ls-remote', '--heads', 'origin').stdout.split())
                pushed[label] = (rc, sorted(r[len('refs/heads/'):] for r in after - before
                                            if r.startswith('refs/heads/')), said)
            # No GitHub test runs on the pull request at all (2026-10-04):
            # "DUE", then "wait for its GitHub test", read as a wait for a
            # test that would never start.
            git(work, 'checkout', '-q', '-B', 'staging', 'origin/staging')
            (work / 'notes.md').write_text('no test\n', encoding='utf-8')
            git(work, 'commit', '-qam', 'work: no test')
            git(work, 'push', '-q', 'origin', 'staging')
            saved_tests = pb2.github_tests
            pb2.github_tests = lambda root, sha: []
            try:
                said = []
                rc = pb2._promote_to_main(str(work), said.append)
            finally:
                pb2.github_tests = saved_tests
            pushed['none runs'] = (rc, [], said)
        finally:
            for k, v in saved_env.items():
                if v is None:
                    os.environ.pop(k, None)
                else:
                    os.environ[k] = v
        rc, refs, said = pushed['passed 10h ago']
        cases.append(('a real Promote, test passed 10h ago with 168h set: pushes a '
                      'not-due copy and says NOT DUE',
                      rc == pb2.PROMOTE_MAIN_NOT_MOVED and len(refs) == 1
                      and pb2.is_not_due_copy(refs[0])
                      and any('NOT DUE' in x for x in said)
                      and not starts('pull_request', 'main', True, refs[0])))
        rc, refs, said = pushed['passed 200h ago']
        cases.append(('...and with the test 200h old: pushes a plain copy, '
                      'says DUE, and GitHub would run it',
                      rc == pb2.PROMOTE_MAIN_NOT_MOVED and len(refs) == 1
                      and pb2.is_main_copy(refs[0])
                      and not pb2.is_not_due_copy(refs[0])
                      and any('GitHub test: DUE' in x for x in said)
                      and starts('pull_request', 'main', True, refs[0])))
        rc, refs, said = pushed['passed 200h ago']
        carried = refs and git(work, 'merge-base', '--is-ancestor', 'origin/main',
                               f'origin/{refs[0]}').returncode == 0
        tip = refs and git(work, 'rev-parse', f'origin/{refs[0]}').stdout.strip()
        cases.append(('...and the copy is staging merged with main, so the push '
                      'test on main after its merge recognises what passed, and the '
                      'merge instruction pins that commit',
                      bool(carried) and bool(tip)
                      and any(f'at head commit {tip}' in x for x in said)))
        rc, _refs, said = pushed.get('none runs', (None, [], []))
        text = '\n'.join(said)
        cases.append(('...and where no GitHub test runs on the pull request: says '
                      'NONE, never DUE, and gives no wait step',
                      rc == pb2.PROMOTE_MAIN_NOT_MOVED and 'GitHub test: NONE' in text
                      and 'GitHub test: DUE' not in text
                      and '--wait-main-test' not in text))
    if saved_force is not None:
        os.environ[pb.FORCE_ENV] = saved_force
    failed = [n for n, ok in cases if not ok]
    detail = '; '.join(failed) + ((' | ' + ' | '.join(wrong[:5])) if wrong else '')
    check(f'{name} ({len(cases)} stated cases, {rows} table rows)', not failed, detail)


def check_private_repo_skipped_gate_is_not_main_test():
    """A workflow GitHub never runs in this repository is not one of main's
    GitHub tests, and nothing else changes (2026-10-09).

    THE INCIDENT. In a private consuming repository the pull request into
    main showed the light check passed and leak-gate.yml "skipped": its
    template gates its only job on `github.event.repository.private != true`.
    A skipped run never counts as a pass, so --wait-main-test said
    "leak-gate.yml never ran on it. Do not merge" on every pull request,
    for good, and the Promote blamed an Update Vendors that would bring the
    same file. One definition, precedent_branches.skipped_by_design, read by
    github_tests and precedent_ci_verified alike.

    THE NEGATIVE CASES ARE THE POINT: the same skipped run in a public
    repository, and a skipped workflow that is NOT gated on privacy in a
    private one, still never read as passed."""
    import importlib.util, json as _json, subprocess as _sp, tempfile
    name = 'a workflow skipped by design in a private repository is not main\'s GitHub test'
    src = ROOT / 'tools' / 'precedent_branches.py'
    tpl_dir = ROOT / 'templates' / 'github-actions'
    leak_tpl, light_tpl = (tpl_dir / 'leak-gate.yml.template',
                           tpl_dir / 'light-check.yml.template')
    if not (src.exists() and leak_tpl.is_file() and light_tpl.is_file()):
        not_applicable(name, 'precedent_branches.py or a workflow template is absent')
        return
    spec = importlib.util.spec_from_file_location('_pb_skipped_by_design', src)
    pb = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(pb)
    sys.path.insert(0, str(ROOT / 'tools'))
    try:
        import precedent_ci_verified as pciv
    finally:
        sys.path.pop(0)
    cases = []
    for t in sorted(tpl_dir.glob('*.yml.template')):
        wf = t.name[:-len('.template')]
        cases.append((f'NOT_DUE_SKIP_TEMPLATES names {wf} exactly when its template '
                      f'carries the not-due skip',
                      (pb.NOT_DUE_PREFIX in t.read_text(encoding='utf-8'))
                      == (wf in pb.NOT_DUE_SKIP_TEMPLATES)))
    LEAK, LIGHT, OTHER = ('.github/workflows/leak-gate.yml',
                          '.github/workflows/light-check.yml',
                          '.github/workflows/other.yml')
    env = _fixture_git_env()
    with tempfile.TemporaryDirectory() as td:
        repo = pathlib.Path(td) / 'repo'
        wfd = repo / '.github' / 'workflows'
        wfd.mkdir(parents=True)

        def git(*a):
            return _sp.run(['git', *a], cwd=repo, env=env, capture_output=True,
                           text=True, check=True).stdout.strip()

        def commit(visibility, files):
            pj = {'base_branch': 'main', 'github_ci_main_test': 168}
            if visibility:
                pj['visibility'] = visibility
            (repo / 'precedent.json').write_text(_json.dumps(pj), encoding='utf-8')
            for p in list(wfd.iterdir()):
                p.unlink()
            for path, text in files.items():
                (repo / path).write_text(text, encoding='utf-8')
            git('add', '-A')
            git('commit', '-q', '--allow-empty', '-m', 'fixture')
            return git('rev-parse', 'HEAD')

        git('init', '-q', '-b', 'main')
        # Named, as this repository's own leak-gate.yml is:
        # precedent_ci_verified expects only a workflow with a `name:`.
        real = {LEAK: 'name: Leak gate\n' + leak_tpl.read_text(encoding='utf-8'),
                LIGHT: light_tpl.read_text(encoding='utf-8')}
        # Gated, but not on privacy: skipped for its own reason.
        other = ('name: Other\non:\n  pull_request:\n    branches: [main]\n'
                 'jobs:\n  other:\n    if: github.event_name == \'push\'\n'
                 '    runs-on: ubuntu-latest\n    steps:\n      - run: "true"\n')
        # Two jobs, only one gated on privacy: the other still runs.
        half = ('name: Half\non:\n  pull_request:\njobs:\n  a:\n'
                '    if: ${{ github.event.repository.private != true }}\n'
                '    runs-on: ubuntu-latest\n    steps:\n      - run: "true"\n'
                '  b:\n    runs-on: ubuntu-latest\n    steps:\n      - run: "true"\n')
        # The negated form, and a privacy gate that is one `&&` part.
        negated = ('name: Neg\non:\n  pull_request:\njobs:\n  n:\n'
                   '    if: >-\n      (!github.event.repository.private)\n'
                   '      && github.actor != \'bot\'\n'
                   '    runs-on: ubuntu-latest\n    steps:\n      - run: "true"\n')

        def run(path, conclusion):
            return {'path': path, 'status': 'completed', 'conclusion': conclusion,
                    'created_at': '2026-10-09T12:00:00Z', 'html_url': 'U'}

        class GH:
            def __init__(self, runs):
                self.runs = runs

            def call(self, path, cache=True):
                if path == 'repos/o/r':
                    return {'full_name': 'o/r'}, None
                if '/pulls' in path:
                    return [], None
                if '/actions/workflows/' in path:
                    wf = path.split('/actions/workflows/')[1].split('/')[0]
                    return {'workflow_runs': [
                        dict(r, head_branch='main', created_at='2026-10-09T12:00:00Z')
                        for r in self.runs if r['path'].endswith('/' + wf)
                        and r['conclusion'] == 'success']}, None
                return {'workflow_runs': self.runs}, None

        pb._slug = lambda root: 'o/r'
        pb.GITHUB_POLL_SECONDS = 0
        pb.GITHUB_START_WAIT_SECONDS = 0
        pb.GITHUB_TEST_WAIT_SECONDS = 0
        incident = [run(LIGHT, 'success'), run(LEAK, 'skipped')]

        def wait(sha, runs):
            said = []
            return pb.wait_for_main_test(repo, sha, said.append, GH(runs)), said[-1]

        sha = commit('private', real)
        rc, said = wait(sha, incident)
        cases.append(('(a) private repo, light check passed and leak-gate skipped: '
                      'the wait says PASSED', rc == 0 and 'PASSED' in said))
        cases.append(('...because leak-gate.yml is not one of main\'s GitHub tests '
                      'there, and the light check still is',
                      [p for p, _ in pb.github_tests(repo, sha)] == [LIGHT]))
        cases.append(('...and precedent_ci_verified does not expect it either',
                      'Leak gate' not in ' '.join(pciv.expected_workflows(repo, 'x', 'main'))
                      and pciv.expected_workflows(repo, 'x', 'main')))
        due, why = pb.main_test_due(repo, sha, gh=GH(incident))
        cases.append(('(d) the due check no longer sends a private repo to Update '
                      'Vendors over leak-gate.yml', 'Update Vendors' not in why
                      and 'leak-gate' not in why))
        sha = commit('public', real)
        rc, said = wait(sha, incident)
        cases.append(('(b) the same runs in a public repository: NOT passed, '
                      'leak-gate.yml never ran', rc == 1 and 'NONE' in said
                      and 'leak-gate.yml' in said))
        cases.append(('...and precedent_ci_verified still expects it there',
                      'Leak gate' in pciv.expected_workflows(repo, 'x', 'main')))
        sha = commit(None, real)
        cases.append(('...and in a repository that declares no visibility',
                      LEAK in [p for p, _ in pb.github_tests(repo, sha)]))
        sha = commit('private', dict(real, **{OTHER: other}))
        rc, said = wait(sha, incident + [run(OTHER, 'skipped')])
        cases.append(('(c) private repo, a workflow NOT gated on privacy skipped: '
                      'NOT passed', rc == 1 and 'other.yml' in said))
        sha = commit('private', {LIGHT: real[LIGHT],
                                 '.github/workflows/half.yml': half})
        cases.append(('...nor one with a job the privacy gate does not reach',
                      '.github/workflows/half.yml' in [p for p, _ in pb.github_tests(repo, sha)]))
        sha = commit('private', {LIGHT: real[LIGHT],
                                 '.github/workflows/neg.yml': negated})
        cases.append(('the negated form, as one && part of a folded if:, is the '
                      'same gate', [p for p, _ in pb.github_tests(repo, sha)] == [LIGHT]))
        cases.append(('the light check\'s own if:, privacy only inside an ||, is '
                      'never read as skipped by design',
                      not pb.skipped_by_design(repo, real[LIGHT])))
        sha = commit('private', {LIGHT: real[LIGHT], OTHER: other})
        due, why = pb.main_test_due(repo, sha, gh=GH([run(LIGHT, 'success')]))
        cases.append(('(d) a workflow no shipped template gives the not-due skip is '
                      'due, and the advice does not name Update Vendors',
                      due is True and 'other.yml' in why and 'Update Vendors' not in why))
        sha = commit('private', {LIGHT: 'on:\n  pull_request:\n    branches: [main]\n'
                                        'jobs:\n  x:\n    runs-on: ubuntu-latest\n'})
        due, why = pb.main_test_due(repo, sha, gh=GH([]))
        cases.append(('...while an old light-check.yml, whose template does carry it, '
                      'is still sent to Update Vendors',
                      due is True and 'Update Vendors' in why))
    failed = [n for n, ok in cases if not ok]
    check(f'{name} ({len(cases)} stated cases)', not failed, '; '.join(failed))


def check_main_test_cadence():
    """Main's GitHub test runs at most once every github_ci_every_hours in a
    private repository, decided by Promote before GitHub starts anything
    (spec/CI_CADENCE_PLAN.md, "Promote decides", 2026-10-01).

    THE NEGATIVE CASES ARE THE POINT: a skip that fires wrongly is main
    going untested. Each "not due" is paired with the shape where it must
    run -- a public repo, an expired window, a failed newest run, GitHub not
    answering, a workflow that cannot skip yet, a batch that changes a
    workflow, PRECEDENT_CI_NOW=1. And a skipped run must never read as a
    failure: GitHub records one, free, on every private push to main."""
    import importlib.util, json as _json, tempfile, time as _time
    name = "main's GitHub test runs at most once every github_ci_every_hours"
    src = ROOT / 'tools' / 'precedent_branches.py'
    if not src.exists():
        not_applicable(name, 'tools/precedent_branches.py is absent')
        return
    spec = importlib.util.spec_from_file_location('_pb_cadence', src)
    pb = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(pb)
    cases = []
    tpl = (ROOT / 'templates' / 'github-actions' / 'light-check.yml.template')
    tpl_text = tpl.read_text(encoding='utf-8') if tpl.is_file() else ''
    cases.append(('the light-check template names the very branch prefix Promote '
                  'gives a not-due copy',
                  f"startsWith(github.head_ref, '{pb.NOT_DUE_PREFIX}')" in tpl_text))
    saved_env = os.environ.get(pb.FORCE_ENV)
    os.environ.pop(pb.FORCE_ENV, None)
    with tempfile.TemporaryDirectory() as td:
        tmp = pathlib.Path(td)
        repo, me = tmp / 'repo', tmp / 'me'
        repo.mkdir()
        me.mkdir()
        cfg = tmp / 'config.json'
        cfg.write_text(_json.dumps({'individual': {'path': str(me)}}), encoding='utf-8')

        def setup(visibility='private', mine=None, theirs=None):
            pj = {'base_branch': 'main'}
            if visibility:
                pj['visibility'] = visibility
            if theirs is not None:
                pj['github_ci_every_hours'] = theirs
            (repo / 'precedent.json').write_text(_json.dumps(pj), encoding='utf-8')
            ident = {'email': 'me@example.com'}
            if mine is not None:
                ident['ci_every_hours'] = mine
            (me / 'identity.json').write_text(_json.dumps(ident), encoding='utf-8')

        setup('public', mine=168)
        cases.append(('a public repository is tested on every Promote, whatever '
                      'the person sets', pb.main_test_cadence(repo, cfg)[0] == 0))
        setup(None, mine=168)
        cases.append(('...and so is one that declares no visibility',
                      pb.main_test_cadence(repo, cfg)[0] == 0))
        setup(mine=168, theirs=0)
        h, where = pb.main_test_cadence(repo, cfg)
        cases.append(("in Promote the person's value wins over the repository's 0 "
                      '(Morgan: "if it conflicts, and I run promote, it still skips it")',
                      h == 168 and str(me) in where))
        setup(theirs=6)
        cases.append(("with no personal value, the repository's own applies",
                      pb.main_test_cadence(repo, cfg)[0] == 6))
        setup(mine='weekly')
        cases.append(('a value that is not a number means every Promote',
                      pb.main_test_cadence(repo, cfg)[0] == 0))
        setup(mine=True)
        cases.append(('...and so does true', pb.main_test_cadence(repo, cfg)[0] == 0))

        WF = '.github/workflows/light-check.yml'
        now = _time.time()

        def iso(hours_ago):
            return _time.strftime('%Y-%m-%dT%H:%M:%SZ', _time.gmtime(now - hours_ago * 3600))

        def run(hours_ago, conclusion='success', branch='to-main-2026-09-30'):
            return {'path': WF, 'status': 'completed', 'conclusion': conclusion,
                    'head_branch': branch, 'created_at': iso(hours_ago),
                    'html_url': 'U'}

        class GH:
            def __init__(self, runs, fail=None):
                self.runs, self.fail = runs, fail

            def call(self, path, cache=True):
                if self.fail:
                    return None, self.fail
                return {'workflow_runs': self.runs}, None

        pb._slug = lambda root: 'o/r'
        skipping = 'on: {}\n# ' + pb.NOT_DUE_PREFIX + '\n'
        shown = {'text': skipping, 'diff': ''}
        real_git = pb._git

        def fake_git(root, *args):
            if args[:1] == ('show',):
                return shown['text']
            if args[:2] == ('diff', '--name-only'):
                return shown['diff']
            return real_git(root, *args)
        pb._git = fake_git
        pb.github_tests = lambda root, sha: [(WF, True)]
        setup(mine=168)

        def due(runs, **kw):
            return pb.main_test_due(repo, 'TIP', gh=GH(runs, kw.get('fail')),
                                    user_config=cfg)
        d, why = due([run(10), run(1, 'skipped', 'main')])
        cases.append(('a pass 10 hours ago with a 168-hour window is NOT DUE, says when '
                      'the next one is, and a newer skipped run changes nothing',
                      d is False and 'next one is due' in why))
        d, why = due([run(200)])
        cases.append(('a pass 200 hours ago is due', d is True and '200h ago' in why))
        d, why = due([run(1, 'failure', 'main'), run(10)])
        cases.append(('a failed newest run keeps it due inside the window, with its link',
                      d is True and 'failure' in why and 'U' in why))
        d, why = due([run(10, branch='claude/some-feature')])
        cases.append(('a pass on a working branch does not count for main',
                      d is True and 'no passing run' in why))
        d, why = due([], fail='HTTP 403')
        cases.append(('GitHub not answering means it runs', d is True and '403' in why))
        shown['text'] = 'on: {}\n'
        d, why = due([run(10)])
        cases.append(('a workflow installed before the not-due skip existed is always '
                      'due, so a "not due" wait never merges under a running test',
                      d is True and 'predates' in why))
        shown['text'] = skipping
        shown['diff'] = '.github/workflows/light-check.yml\ntools/ENGINE_MANIFEST.json\n'
        d, why = due([run(10)])
        cases.append(('a batch changing a workflow or the vendored engine is NOT forced '
                      '(Morgan: "I might update the vendored engines a lot")', d is False))
        shown['diff'] = ''
        os.environ[pb.FORCE_ENV] = '1'
        d, why = due([run(10)])
        os.environ.pop(pb.FORCE_ENV, None)
        cases.append((f'{pb.FORCE_ENV}=1 makes it due', d is True))
        setup(mine=168)
        pj = _json.loads((repo / 'precedent.json').read_text(encoding='utf-8'))
        (repo / 'precedent.json').write_text(_json.dumps(
            dict(pj, github_ci_workflows='disabled')), encoding='utf-8')
        d, why = due([run(1000)])
        cases.append(("with no personal switch, the repository's own \"disabled\" "
                      'means no test, however long ago it passed',
                      d is False and "this repo's precedent.json" in why))
        (me / 'identity.json').write_text(_json.dumps(
            {'email': 'me@example.com', 'ci_every_hours': 168,
             'ci_workflows': 'enabled'}), encoding='utf-8')
        d, why = due([run(1000)])
        cases.append(("...and the person's \"enabled\" wins over it", d is True))
        setup(mine=0)
        d, why = due([run(10)])
        cases.append(('a value of 0 is every Promote', d is True))

        said = []
        rc = pb.wait_for_main_test(repo, 'TIP', said.append, GH([]),
                                   copy=pb.NOT_DUE_PREFIX + '2026-10-01')
        cases.append(('--wait-main-test on a not-due copy exits 0 at once and says '
                      'NOT DUE', rc == 0 and said and 'NOT DUE' in said[-1]))
        pb._remote_tip = lambda root, branch: None
        cases.append(('a not-due copy is named with the name the template skips on',
                      pb.is_not_due_copy(pb._to_main_copy(repo, due=False))
                      and not pb.is_not_due_copy(pb._to_main_copy(repo))))
        ok_run = {'path': WF, 'status': 'completed', 'conclusion': 'success',
                  'created_at': '2026-09-30T10:00:00Z', 'head_sha': 'SHA'}
        skipped = dict(ok_run, conclusion='skipped', created_at='2026-09-30T11:00:00Z')

        class RunsGH:
            def call(self, path, cache=True):
                if '/pulls' in path:
                    return [], None
                return {'workflow_runs': [ok_run, skipped]}, None
        st, _why = pb.github_test_state(repo, 'SHA', [(WF, True)], RunsGH())
        cases.append(('a skipped run newer than a pass reads "passed", never "failed" '
                      '(every private push to main records one)', st == 'passed'))

        # 2026-10-19: the push run on main skipped its test while the pull
        # request's run was still going, finished `success`, and was read as
        # main's verdict; the pull request's run failed (issue #1242).
        pr_fail = {'id': 1, 'path': WF, 'status': 'completed', 'conclusion': 'failure',
                   'created_at': '2026-10-19T14:24:40Z', 'head_sha': 'HEAD',
                   'html_url': 'U'}
        push_ok = {'id': 2, 'path': WF, 'status': 'completed', 'conclusion': 'success',
                   'created_at': '2026-10-19T14:25:34Z', 'head_sha': 'SHA'}

        def runs_gh(on_sha, jobs_of):
            class G:
                def call(self, path, cache=True):
                    if path.endswith('/pulls'):
                        return [{'head': {'sha': 'HEAD'}, 'base': {'ref': 'main'},
                                 'number': 1240}], None
                    if '/jobs' in path:
                        return {'jobs': jobs_of}, None
                    if 'head_sha=HEAD' in path:
                        return {'workflow_runs': [pr_fail]}, None
                    return {'workflow_runs': on_sha}, None
            return G()
        hollow_jobs = [{'name': pb.DECISION_JOB, 'conclusion': 'success'},
                       {'name': 'test', 'conclusion': 'skipped'}]
        st, why = pb.github_test_state(repo, 'SHA', [(WF, True)],
                                       runs_gh([push_ok], hollow_jobs))
        cases.append(('a push run that tested nothing, newer than its pull '
                      'request\'s failed run, reads "failed" (2026-10-19)',
                      st == 'failed' and 'U' in why))
        st, _why = pb.github_test_state(
            repo, 'SHA', [(WF, True)],
            runs_gh([push_ok], [dict(j, conclusion='success') for j in hollow_jobs]))
        cases.append(('CONTROL: a push run that did run its test, and passed, '
                      'still decides', st == 'passed'))
        pr_fail_saved, pr_fail = pr_fail, dict(pr_fail, path='other.yml')
        st, _why = pb.github_test_state(repo, 'SHA', [(WF, True)],
                                        runs_gh([push_ok], hollow_jobs))
        pr_fail = pr_fail_saved
        cases.append(('a run that tested nothing and is the only run is kept: '
                      'it reads "passed", never "never ran"', st == 'passed'))
        wf_text = (ROOT / '.github' / 'workflows' / 'deep-check.yml').read_text(
            encoding='utf-8')
        cases.append(("precedent_branches.DECISION_JOB is deep-check.yml's "
                      'already-tested job name',
                      f'name: {pb.DECISION_JOB}\n' in wf_text))
    if saved_env is not None:
        os.environ[pb.FORCE_ENV] = saved_env
    failed = [n for n, ok in cases if not ok]
    check(f'{name} ({len(cases)} stated cases)', not failed, '; '.join(failed))


def check_main_test_wait_does_not_ask_to_merge_what_is_merged():
    """After a fast move, --wait-main-test does not ask for a merge main
    already carries.

    2026-10-10: a fast move merges first and waits on GitHub's test after,
    and twice the passed wait ended "Merge the pull request into main" over
    a pull request merged half an hour before. The wait now looks at
    origin's main first.
    """
    import tempfile
    sys.path.insert(0, str(ROOT / 'tools'))
    try:
        import precedent_branches as pb
    finally:
        sys.path.pop(0)
    cases = []
    saved = (pb.github_tests, pb.github_test_state)
    try:
        pb.github_tests = lambda root, sha: [('.github/workflows/t.yml', None)]
        with tempfile.TemporaryDirectory() as td:
            tmp = pathlib.Path(td)
            env = _fixture_git_env()
            g = lambda cwd, *a: subprocess.run(['git', '-C', str(cwd), *a], env=env,
                                               capture_output=True, text=True)
            g(tmp, 'init', '-q', '--bare', '-b', 'main', str(tmp / 'o.git'))
            g(tmp, 'clone', '-q', str(tmp / 'o.git'), str(tmp / 'w'))
            w = tmp / 'w'
            g(w, 'checkout', '-q', '-B', 'main')
            (w / 'a').write_text('a'); g(w, 'add', '-A'); g(w, 'commit', '-qm', 'a')
            g(w, 'push', '-q', 'origin', 'main')
            merged = g(w, 'rev-parse', 'HEAD').stdout.strip()
            g(w, 'checkout', '-q', '-b', 'copy')
            (w / 'b').write_text('b'); g(w, 'add', '-A'); g(w, 'commit', '-qm', 'b')
            g(w, 'push', '-q', 'origin', 'copy')
            open_ = g(w, 'rev-parse', 'HEAD').stdout.strip()
            for state, rc_want in (('passed', 0), ('failure', 1)):
                pb.github_test_state = lambda *a, s=state, **k: (s, 'fixture run')
                said = []
                rc = pb.wait_for_main_test(w, merged, said.append)
                cases.append((f'{state}, already on main: no merge is asked for',
                              rc == rc_want and 'already carries it' in said[-1]
                              and 'Merge the pull request' not in said[-1]
                              and 'Do not merge' not in said[-1], said[-1]))
                if state != 'passed':
                    # 2026-10-17: "fix main now" named no route, and the fix
                    # took the long way through staging and a second Produce.
                    cases.append(('failure, already on main: the red-main route is named',
                                  'precedent_branch_name.py' in said[-1]
                                  and 'red_main_fix' in said[-1], said[-1]))
                said = []
                rc = pb.wait_for_main_test(w, open_, said.append)
                cases.append((f'{state}, not on main yet: as before',
                              rc == rc_want and ('Merge the pull request' in said[-1]
                                                 if state == 'passed'
                                                 else 'Do not merge' in said[-1]),
                              said[-1]))
    finally:
        pb.github_tests, pb.github_test_state = saved
    bad = [(n, d) for n, ok, d in cases if not ok]
    check(f'the main-test wait does not ask to merge what is merged ({len(cases)} stated cases)',
          not bad, '; '.join(f'{n} ({d})' for n, d in bad))


def check_main_test_wait_says_what_it_waits_on():
    """--wait-main-test agrees with Update Vendors on what passed, says at
    once when no run will start, and is never silent for long.

    2026-10-19: after a fast Produce a consumer's session ran the wait on a
    commit and it said nothing for over an hour. Update Vendors took a main
    whose files carried the passed marker; the wait read GitHub's runs only.
    """
    import tempfile
    sys.path.insert(0, str(ROOT / 'tools'))
    try:
        import precedent_branches as pb
    finally:
        sys.path.pop(0)
    cases = []
    saved = (pb.github_tests, pb.github_test_state, pb.passed_markers, pb._slug,
             pb.GITHUB_POLL_SECONDS, pb.GITHUB_TEST_WAIT_SECONDS,
             pb.GITHUB_START_WAIT_SECONDS, pb.PROGRESS_SECONDS, time.sleep)

    class GH:
        def __init__(self, pulls):
            self.pulls = pulls

        def call(self, path, cache=True):
            return self.pulls, None
    try:
        pb.github_tests = lambda root, sha: [('.github/workflows/t.yml', None)]
        pb._slug = lambda root: 'o/r'
        with tempfile.TemporaryDirectory() as td:
            tmp = pathlib.Path(td)
            env = _fixture_git_env()
            g = lambda cwd, *a: subprocess.run(['git', '-C', str(cwd), *a], env=env,
                                               capture_output=True, text=True)
            g(tmp, 'init', '-q', '--bare', '-b', 'main', str(tmp / 'o.git'))
            g(tmp, 'clone', '-q', str(tmp / 'o.git'), str(tmp / 'w'))
            w = tmp / 'w'
            g(w, 'checkout', '-q', '-B', 'main')
            (w / 'a').write_text('a'); g(w, 'add', '-A'); g(w, 'commit', '-qm', 'a')
            g(w, 'push', '-q', 'origin', 'main')
            g(w, 'checkout', '-q', '-b', 'side')
            (w / 'b').write_text('b'); g(w, 'add', '-A'); g(w, 'commit', '-qm', 'b')
            side = g(w, 'rev-parse', 'HEAD').stdout.strip()
            tree = g(w, 'rev-parse', 'HEAD^{tree}').stdout.strip()

            # (a) The marker answers first, as it does for Update Vendors.
            pb.passed_markers = lambda root: {tree}
            pb.github_test_state = lambda *a, **k: ('failed', 'a push run that tested nothing')
            said = []
            rc = pb.wait_for_main_test(w, side, said.append, GH([]))
            cases.append(('files carrying the passed marker read PASSED, as Update '
                          'Vendors reads them', rc == 0 and 'PASSED' in said[-1]
                          and 'passed marker' in said[-1], said[-1]))

            # (b) No run will ever start: said at once, no polling.
            pb.passed_markers = lambda root: set()
            pb.github_test_state = lambda *a, **k: ('none', 't.yml never ran on it')
            pb.GITHUB_START_WAIT_SECONDS = 3600

            def no_sleep(_s):
                raise AssertionError('slept')
            time.sleep = no_sleep
            said = []
            try:
                rc = pb.wait_for_main_test(w, side, said.append, GH([]))
                ok = rc == 1 and 'no run of it will start' in said[-1]
            except AssertionError:
                ok = False
            cases.append(("a commit that is neither main's tip nor an open pull "
                          "request's head is refused at once, not waited on",
                          ok, said[-1] if said else ''))
            open_pr = [{'base': {'ref': 'main'}, 'state': 'open', 'number': 7,
                        'head': {'sha': side}}]
            pb.GITHUB_START_WAIT_SECONDS = 0
            time.sleep = lambda _s: None
            said = []
            rc = pb.wait_for_main_test(w, side, said.append, GH(open_pr))
            cases.append(("...but an open pull request's head is waited on as before",
                          rc == 1 and 'no run of it will start' not in said[-1],
                          said[-1]))

            # (c) A run that never finishes: progress lines, then a timeout
            # that says so.
            pb.github_test_state = lambda *a, **k: ('running', 't.yml has not finished')
            pb.GITHUB_POLL_SECONDS = 0
            pb.GITHUB_TEST_WAIT_SECONDS = 0.05
            pb.PROGRESS_SECONDS = 0
            said = []
            rc = pb.wait_for_main_test(w, side, said.append, GH(open_pr))
            cases.append(('a long wait prints a line as it goes',
                          any('still waiting' in s for s in said), said[:3]))
            cases.append(('...and ends saying it stopped waiting, and how to wait more',
                          rc == 1 and 'stopped waiting after' in said[-1]
                          and '--wait-main-test again' in said[-1], said[-1]))
    finally:
        (pb.github_tests, pb.github_test_state, pb.passed_markers, pb._slug,
         pb.GITHUB_POLL_SECONDS, pb.GITHUB_TEST_WAIT_SECONDS,
         pb.GITHUB_START_WAIT_SECONDS, pb.PROGRESS_SECONDS, time.sleep) = saved
    bad = [(n, d) for n, ok, d in cases if not ok]
    check(f'the main-test wait says what it waits on ({len(cases)} stated cases)',
          not bad, '; '.join(f'{n} ({d})' for n, d in bad))


def check_a_failed_result_never_carries_its_success_word():
    """A LAND RESULT or PROMOTE RESULT line that reports a failure never
    contains LANDED or PROMOTED.

    2026-10-11: a rollout script looked for "LANDED" in the land result to
    decide it could go on, and "NOT LANDED" matched, so it promoted on top
    of a landing that never happened. The failure verdicts are now LAND
    REFUSED and PROMOTE REFUSED, and a run that did nothing says NOTHING TO
    PROMOTE. The check builds every verdict the result line can end on from
    the module's own text, and runs the result line for each exit status.
    """
    import re as _re
    sys.path.insert(0, str(ROOT / 'tools'))
    try:
        import precedent_branches as pb
    finally:
        sys.path.pop(0)
    src = (ROOT / 'tools' / 'precedent_branches.py').read_text(encoding='utf-8')
    code = '\n'.join(ln for ln in src.splitlines() if not ln.lstrip().startswith('#'))
    verdicts = _re.findall(r"""(?:return \d, |_verdict\(|verdict = )f?['"]([A-Z][A-Z ]+[A-Z])\b""", code)
    words = sorted(set(verdicts))
    bad = [w for w in words if _re.search(r'\b(LANDED|PROMOTED)\b', w)
           and w not in ('LANDED', 'PROMOTED')]
    check('the verdicts the module can end a result line on were found',
          {'LANDED', 'LAND REFUSED', 'PROMOTE REFUSED'} <= set(words), words)
    check('THE DISCRIMINATING CASE: no failure verdict contains LANDED or PROMOTED',
          not bad, bad)
    lines = []
    for rc in (None, 0, 1):
        pb._RESULT.clear()
        lines.append(pb.promote_result_line(ROOT, rc, last='a reason'))
    pb._RESULT.clear()
    check('the result line a Promote falls back on says PROMOTED only for a move',
          not any(_re.search(r'\bPROMOTED\b', ln) for ln in lines), lines)


def check_promote_branches_are_named_like_session_branches():
    """A Promote's fix branch and its copy of staging are named
    <date>-<slug>-<session ID's end>, like every temporary branch --
    except a copy in a repository whose GitHub test knows only the old
    names, which keeps them until Update Vendors brings the new workflow.

    WHY. Morgan, 2026-10-06, reading `promote-fix-20261006T165108-0300` in a
    reply: "isn't our URL format for temporary GitHub repo URLs to start with
    the timestamps then the slug then a few random characters?" The
    Promote's own branches had never been brought into the format."""
    import tempfile
    sys.path.insert(0, str(ROOT / 'tools'))
    import precedent_branches as pb
    import precedent_branch_name as pbn
    env = _fixture_git_env()
    saved = {k: os.environ.get(k) for k in ('CLAUDE_CODE_REMOTE_SESSION_ID', 'CLAUDECODE',
                                            'PRECEDENT_USER_CONFIG',
                                            'PRECEDENT_GITHUB_USER')}
    os.environ['CLAUDE_CODE_REMOTE_SESSION_ID'] = 'session_01FixtureSessionIdAbcde'
    os.environ['CLAUDECODE'] = '1'
    # No person: the names are asserted without a username prefix, so the
    # machine's own identity must not reach them (2026-10-14: in a session
    # whose identity.json declares a GitHub username every name here
    # carried it, and the check failed there while passing on GitHub).
    os.environ['PRECEDENT_USER_CONFIG'] = os.devnull
    os.environ['PRECEDENT_GITHUB_USER'] = ''
    tpl = (ROOT / 'templates' / 'github-actions' / 'light-check.yml.template').read_text(
        encoding='utf-8')
    try:
        with tempfile.TemporaryDirectory() as td:
            td = pathlib.Path(td)
            origin, repo = td / 'origin.git', td / 'work'
            run = lambda *a, cwd=td: subprocess.run(list(a), cwd=str(cwd), env=env,
                                                    capture_output=True, text=True)
            run('git', 'init', '-q', '--bare', str(origin))
            run('git', 'init', '-q', '-b', 'staging', str(repo))
            (repo / '.github' / 'workflows').mkdir(parents=True)
            wf = repo / '.github' / 'workflows' / 'light-check.yml'
            wf.write_text(tpl, encoding='utf-8')
            run('git', 'add', '-A', cwd=repo); run('git', 'commit', '-qm', 'base', cwd=repo)
            run('git', 'remote', 'add', 'origin', str(origin), cwd=repo)
            run('git', 'push', '-q', 'origin', 'staging', cwd=repo)
            run('git', 'fetch', '-q', 'origin', cwd=repo)
            day, _m = pb._day_and_moment(repo)
            have_tests = bool(pb.github_tests(repo, pb._remote_tip(repo, pb.staging_branch(repo))))
            copy, not_due = pb._to_main_copy(repo), pb._to_main_copy(repo, due=False)
            check('its copies of staging too, where the GitHub test knows the new names',
                  re.fullmatch(f'{day}-promote-to-main-abcde-[a-z0-9]{{5}}', copy)
                  and re.fullmatch(f'{day}-promote-to-main-not-due-abcde-[a-z0-9]{{5}}',
                                   not_due)
                  and pb.is_main_copy(copy) and pb.is_not_due_copy(not_due),
                  f'{copy} {not_due} tests={have_tests}')
            wf.write_text(tpl.replace(pb.COPY_NAME_MARKER, '-x-'), encoding='utf-8')
            run('git', 'commit', '-qam', 'an older workflow', cwd=repo)
            run('git', 'push', '-q', 'origin', 'staging', cwd=repo)
            run('git', 'fetch', '-q', 'origin', cwd=repo)
            old = pb._to_main_copy(repo, due=False)
            check('CONTROL: where the GitHub test knows only the old names, a copy '
                  'keeps one, so a not-due copy is still skipped',
                  have_tests and old.startswith(pb.NOT_DUE_PREFIX), f'{old} tests={have_tests}')
            # A GitHub test that never names a copy (BestPractice's own deep
            # check runs on every pull request into main) does not care what
            # the copy is called, so it gets the session-branch format too
            # (Morgan, 2026-10-09).
            wf.write_text('name: Deep check\non:\n  pull_request:\n    branches: [main]\n'
                          'jobs:\n  check:\n    runs-on: ubuntu-latest\n'
                          '    steps:\n      - run: echo ok\n', encoding='utf-8')
            run('git', 'commit', '-qam', 'a workflow that names no copy', cwd=repo)
            run('git', 'push', '-q', 'origin', 'staging', cwd=repo)
            run('git', 'fetch', '-q', 'origin', cwd=repo)
            plain = pb._to_main_copy(repo)
            check('where the GitHub test names no copy at all, a copy is named '
                  '<date>-promote-to-main-<id>-<random>',
                  re.fullmatch(f'{day}-promote-to-main-abcde-[a-z0-9]{{5}}', plain)
                  is not None, plain)
    finally:
        for k, v in saved.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v


def check_merge_instructions_give_the_full_head():
    """Every "merge it" line a Promote into main prints names the head commit
    in full.

    WHY. 2026-10-06, a session in a consumer: the Promote and the wait
    printed twelve characters of the copy's tip, and GitHub's merge API
    takes the expected head in full, so the session had to look the rest up
    before it could merge."""
    import tempfile
    sys.path.insert(0, str(ROOT / 'tools'))
    import precedent_branches as pb
    sha = 'a' * 40
    cases = [('_at_head carries all 40 characters', sha in pb._at_head(sha)),
             ('...and says nothing without a head', pb._at_head('') == '')]
    saved = (pb.github_tests, pb.github_test_state)
    try:
        pb.github_tests = lambda root, s: [('.github/workflows/x.yml', 'x')]
        pb.github_test_state = lambda root, s, tests, gh=None: ('passed', 'x passed')
        with tempfile.TemporaryDirectory() as td:
            said = []
            rc = pb.wait_for_main_test(td, sha, said.append)
            cases.append(('a PASSED wait names the full head to merge at',
                          rc == 0 and sha in said[-1]))
            said = []
            rc = pb.wait_for_main_test(
                td, sha, said.append,
                copy='claude/2026-10-06-promote-to-main-not-due-abcde')
            cases.append(('...and so does a NOT DUE one', rc == 0 and sha in said[-1]))
    finally:
        pb.github_tests, pb.github_test_state = saved
        sys.path.pop(0)
    src = (ROOT / 'tools' / 'precedent_branches.py').read_text(encoding='utf-8')
    cases.append(('the READY instructions pass the head too -- the copy\'s own '
                  'commit, staging merged with main',
                  src.count('_at_head(copy_tip)') >= 2))
    bad = [n for n, ok in cases if not ok]
    check(f'a Promote\'s merge instructions name the full head commit '
          f'({len(cases)} stated cases)', not bad, '; '.join(bad))


def check_promote_into_main_exits_nonzero_until_main_moves():
    """Exit 0 from a Promote means the branch it names has moved.

    Reported 2026-09-28: `--promote --to main` pushed the to-main copy,
    printed READY FOR MAIN and a "Next, and not by this script" line, and
    exited 0. A session read the 0 as done; main had not moved, because the
    pull request, its GitHub test and the merge were all still to do. That
    state now exits PROMOTE_MAIN_NOT_MOVED, distinct from a refusal (1) and
    a usage error (2), and the block it prints opens by saying main has not
    moved.

    Also pinned here, from the same day's report of a Promote that "moved
    the session's checked-out branch without pushing it": neither kind of
    Promote touches the checkout it is run from -- the branch checked out
    and where it points are the same before and after. Every merge the
    tool makes happens in a throwaway detached worktree."""
    import tempfile
    name = ('a Promote into main exits non-zero until main moves, and no '
            'Promote moves the checked-out branch')
    tool = ROOT / 'tools' / 'precedent_branches.py'
    if not tool.exists():
        not_applicable(name, 'tools/precedent_branches.py is absent')
        return
    cases = []
    with tempfile.TemporaryDirectory() as td:
        tmp = pathlib.Path(td)
        env = _stale_ref_fixture_env(tmp)
        work, git, branches, tip = _promote_fixture(
            tmp, env, 'staging', ('main', 'staging'))
        git(work, 'checkout', '-q', '-b', 'session-work', 'origin/staging')
        (work / 'two.txt').write_text('2\n', encoding='utf-8')
        git(work, 'add', 'two.txt')
        git(work, 'commit', '-q', '-m', 'work')
        git(work, 'push', '-q', 'origin', 'HEAD:refs/heads/staging')
        before = git(work, 'rev-parse', 'HEAD').stdout.strip()
        main_before = tip('main')
        rc, out = branches('--promote', '--to', 'main', '--full', '--because', 'test the long way', '--work', 'session-work')
        ready = [l for l in out.splitlines() if 'NOT MOVED' in l or 'READY FOR' in l]
        cases.append(('staging into main, main not yet moved: exit 3, not 0 '
                      f'(got {rc})', rc == 3))
        cases.append(('main really has not moved', tip('main') == main_before))
        cases.append(('the ready block opens by saying main has NOT moved',
                      bool(ready) and 'MAIN HAS NOT MOVED YET' in ready[0]))
        cases.append(('the checked-out branch is where it was',
                      git(work, 'branch', '--show-current').stdout.strip()
                      == 'session-work'
                      and git(work, 'rev-parse', 'HEAD').stdout.strip() == before))

    # A repository whose staging tier IS main: work lands there directly,
    # so a Promote has nothing to move and says so.
    with tempfile.TemporaryDirectory() as td:
        tmp = pathlib.Path(td)
        env = _stale_ref_fixture_env(tmp)
        work, git, branches, tip = _promote_fixture(
            tmp, env, 'main', ('main',))
        git(work, 'checkout', '-q', '-b', 'session-work', 'origin/main')
        (work / 'three.txt').write_text('3\n', encoding='utf-8')
        git(work, 'add', 'three.txt')
        git(work, 'commit', '-q', '-m', 'work')
        git(work, 'push', '-q', '-u', 'origin', 'session-work')
        before = git(work, 'rev-parse', 'HEAD').stdout.strip()
        main_before = tip('main')
        rc, out = branches('--promote', '--work', 'session-work')
        cases.append(('no staging branch: nothing to promote, exit 0, main '
                      f'untouched (got {rc})',
                      rc == 0 and 'nothing to promote' in out
                      and tip('main') == main_before))
        cases.append(('and the checked-out branch is where it was, pointing at '
                      'what its own remote copy holds',
                      git(work, 'branch', '--show-current').stdout.strip()
                      == 'session-work'
                      and git(work, 'rev-parse', 'HEAD').stdout.strip() == before
                      == tip('session-work')))
    failed = [n for n, ok in cases if not ok]
    check(f'{name} ({len(cases)} stated cases)', not failed, '; '.join(failed))


def check_landing_on_staging_run_tests_and_fast_move_into_main():
    """The approved plan of 2026-10-09 (land straight on staging, make the
    full local suite optional, make the move into main fast),
    as the engine builds it, generically:

    - A person whose landing branch is staging, with promote_only on, lands
      there: the push gate and the merge gate let their own landing branch
      through, while main stays promotion-only. A push there takes the quick
      checks.
    - Staging's reconciliation with main does not change (Morgan: "make sure
      that staging doesn't change what it does now, in reconciling the
      versions sent directly to main with our staging"): a landing that
      lacks a commit made directly on main is refused at the gates, and
      --land composes it in, as the Promote into staging does. Nothing on
      main is dropped.
    - --run-tests runs the full local suite, moves nothing, and records
      pass or fail for the commit it tested.
    - --promote --to main --fast runs no full suite, prints the head commit
      in full and the after-merge wait; a failed --run-tests on that very
      commit asks (exit 4) and --despite-failed-tests goes on; a failure on
      an older commit is stale and asks nothing.
    - A landing_branch the engine does not know (neither staging nor main)
      makes --land refuse, naming the value and where it is set.
    - Everyone else's routes are as before."""
    import tempfile, json as _json
    name = ('landing straight on staging, --run-tests and the fast move into '
            'main')
    tool = ROOT / 'tools' / 'precedent_branches.py'
    if not tool.exists():
        not_applicable(name, 'tools/precedent_branches.py is absent')
        return
    sys.path.insert(0, str(ROOT / 'tools'))
    try:
        import precedent_branches as pb
    finally:
        sys.path.pop(0)
    cases = []
    with tempfile.TemporaryDirectory() as td:
        tmp = pathlib.Path(td)
        runs = tmp / 'runs'
        runs.write_text('')
        env = dict(_stale_ref_fixture_env(tmp), RUNS=str(runs))
        work, git, branches, tip = _promote_fixture(
            tmp, env, 'staging', ('main', 'staging'))
        cfg = tmp / 'config.json'
        indiv = tmp / 'indiv'
        indiv.mkdir()
        cfg.write_text(_json.dumps({'individual': {'path': str(indiv)}}),
                       encoding='utf-8')

        def person(**settings):
            (indiv / 'identity.json').write_text(_json.dumps(
                {'email': 'p' + chr(64) + 'example.com', **settings}),
                encoding='utf-8')

        # The full suite's stub counts its runs and fails while FAIL is in
        # the tree; the quick checks never run it. A GitHub test is
        # installed, so the move into main has one to name.
        (work / 'tools' / 'precedent_check.py').write_text(
            'import os, pathlib, sys\n'
            'if not {"--changed-files-only", "--only", "--base-dependent"}'
            ' & set(sys.argv):\n'
            '    open(os.environ["RUNS"], "a").write("run\\n")\n'
            '    if pathlib.Path("FAIL").exists():\n'
            '        print("precedent_check: 1 violated")\n'
            '        sys.exit(1)\n'
            'print("precedent_check: 3 passed, 0 violated")\n', encoding='utf-8')
        (work / '.github' / 'workflows').mkdir(parents=True)
        (work / '.github' / 'workflows' / 'test.yml').write_text(
            'on:\n  pull_request:\n    branches: [main]\njobs: {}\n',
            encoding='utf-8')
        git(work, 'add', '-A')
        git(work, 'commit', '-q', '-m', 'stubs')
        git(work, 'push', '-q', 'origin', 'HEAD:main', 'HEAD:staging')

        def full_runs():
            n = runs.read_text().count('run')
            runs.write_text('')
            return n

        def commit_on(base, branch, path, text, push_to=None):
            git(work, 'fetch', '-q', 'origin')
            git(work, 'checkout', '-q', '-B', branch, f'origin/{base}')
            (work / path).write_text(text, encoding='utf-8')
            git(work, 'add', '-A')
            git(work, 'commit', '-q', '-m', f'{path} on {branch}')
            git(work, 'push', '-q', 'origin', f'HEAD:refs/heads/{push_to or branch}')
            return git(work, 'rev-parse', 'HEAD').stdout.strip()

        def on(sha, branch):
            git(work, 'fetch', '-q', 'origin')
            return git(work, 'merge-base', '--is-ancestor', sha,
                       f'origin/{branch}').returncode == 0

        def run(*a):
            p = subprocess.run([sys.executable, 'tools/precedent_branches.py', *a],
                               cwd=work, capture_output=True, text=True, env=env)
            return p.returncode, p.stdout + p.stderr

        refusal = getattr(pb, 'direct_push_refusal', None)
        merge_refusal = getattr(pb, 'merge_refusal', None)

        def push_why(args):
            return refusal(work, args, str(cfg))

        def merge_why(bases, heads, sha=None):
            return merge_refusal(work, bases, heads, str(cfg), head_sha=sha)

        # --- a landing branch this engine does not know: --land refuses,
        # naming it, so work never goes somewhere the setting did not mean.
        person(landing_branch='nightly', promote_only=True)
        rc, out = run('--land')
        cases.append(('an unknown landing_branch: --land refuses (exit 2), '
                      'naming the value and where it is set, and lands nothing',
                      rc == 2 and "LAND REFUSED: landing_branch is 'nightly' in "
                      f"{indiv / 'identity.json'}, a branch this engine does not "
                      'know. Run Update Vendors, which moves it' in out
                      and 'Nothing was landed.' in out, out[-400:]))
        person(landing_branch='staging')
        cases.append(('default: landing on staging without promote_only takes '
                      'the quick checks too',
                      pb.tier_for_branch(work, 'staging', str(cfg))[0] == 'basic'))

        # --- landing straight on staging ---
        person(landing_branch='staging', promote_only=True)
        git(work, 'checkout', '-q', '-B', 'level', 'origin/staging')
        cases.append(('a push to their own landing branch, staging, goes through',
                      push_why('origin HEAD:staging') is None,
                      str(push_why('origin HEAD:staging'))[:200]))
        why = push_why('origin HEAD:main') or ''
        cases.append(('main still takes work only by promotion, and the refusal '
                      'names --land and the move into main, which is the fast '
                      'one with no flag',
                      'promote_only is on' in why and '--land' in why
                      and '--promote --to main`' in why
                      and '--full' not in why, why[:200]))
        cases.append(('a push to staging or main takes the quick checks',
                      pb.tier_for_branch(work, 'staging', str(cfg))[0] == 'basic'
                      and pb.tier_for_branch(work, 'main', str(cfg))[0] == 'basic'))
        cases.append(('a pull request into staging carrying main is merged',
                      merge_why(['staging'], ['level'],
                                git(work, 'rev-parse', 'HEAD').stdout.strip()) is None))
        why = merge_why(['main'], ['level']) or ''
        cases.append(('a working branch into main is still refused, saying to '
                      'land it on staging, their landing branch',
                      'Land the branch on staging' in why, why[:200]))

        # A commit made directly on main, then work cut from staging.
        direct = commit_on('main', 'hotfix', 'direct.txt', 'd\n', push_to='main')
        feat = commit_on('staging', 'feat', 'feat.txt', 'f\n')
        why = push_why('origin HEAD:staging') or ''
        cases.append(('a push to staging lacking main\'s direct commit is refused, '
                      'naming the commit and --land',
                      '--land' in why and 'direct.txt' in why, why[:300]))
        why = merge_why(['staging'], ['feat'], feat) or ''
        cases.append(('so is a pull request into staging that lacks it',
                      '--land' in why, why[:200]))
        main_before = tip('main')
        full_runs()
        rc, out = run('--land', 'feat')
        cases.append(('--land composes and lands: exit 0, one LAND RESULT line '
                      'last', rc == 0 and out.strip().splitlines()[-1].startswith(
                          'LAND RESULT: staging <- feat: LANDED at '), out[-400:]))
        cases.append(('staging now carries the commit made directly on main, and '
                      'the work', on(direct, 'staging') and on(feat, 'staging')))
        cases.append(('main did not move, and kept its own commit',
                      tip('main') == main_before and on(direct, 'main')))
        cases.append(('it ran the quick checks only', full_runs() == 0))
        cases.append(('it said what it brought in from main',
                      'BROUGHT IN 1 commit(s) made directly on main' in out))
        rc, out = run('--land', 'feat')
        cases.append(('landing it again: nothing to land, exit 0',
                      rc == 0 and 'NOTHING TO LAND' in out, out[-200:]))

        # --- --run-tests ---
        before = (tip('main'), tip('staging'))
        rc, out = run('--run-tests')
        rec = (pb.run_tests_record(work, 'staging')
               if hasattr(pb, 'run_tests_record') else None) or {}
        cases.append(('--run-tests passes: exit 0, the full suite ran once',
                      rc == 0 and full_runs() == 1, out[-300:]))
        cases.append(('it recorded a pass for staging\'s commit',
                      rec.get('result') == 'passed'
                      and rec.get('commit') == tip('staging')))
        cases.append(('it moved nothing', (tip('main'), tip('staging')) == before))

        # --- the fast move into main ---
        def copies():
            return sorted(l.split('refs/heads/')[-1] for l in git(
                work, 'ls-remote', 'origin', 'refs/heads/*').stdout.splitlines()
                if 'to-main' in l)

        rc, out = run('--promote', '--to', 'main', '--fast')
        last = out.strip().splitlines()[-1] if out.strip() else ''
        made = copies()
        head = git(work, 'rev-parse', f'origin/{made[-1]}').stdout.strip() if made else ''
        cases.append(('the fast move: exit 3 (main has not moved), no full suite',
                      rc == 3 and full_runs() == 0, out[-400:]))
        cases.append(('it prints the copy\'s head commit in all 40 characters',
                      len(head) == 40 and f'at head commit {head}' in out))
        cases.append(('its result line says GitHub\'s test runs after the merge '
                      'and names --wait-main-test',
                      last.startswith('PROMOTE RESULT: main <- staging: ')
                      and 'runs after the merge' in last
                      and '--wait-main-test' in last, last))
        cases.append(('the copy contains main, so nothing that reached main '
                      'directly is dropped', bool(head) and on(direct, made[-1])))
        cases.append(('the merge gate can tell the copy is a fast one',
                      bool(getattr(pb, 'fast_main_copy', lambda *a: None)(work, head))))

        # A failed --run-tests on staging's current commit asks.
        commit_on('staging', 'breaks', 'FAIL', 'x\n')
        run('--land', 'breaks')
        full_runs()
        rc, out = run('--run-tests')
        rec = (pb.run_tests_record(work, 'staging')
               if hasattr(pb, 'run_tests_record') else None) or {}
        cases.append(('--run-tests fails: exit 1, recorded as failed with the '
                      'check named, for staging\'s commit',
                      rc == 1 and rec.get('result') == 'failed'
                      and rec.get('commit') == tip('staging')
                      and any(f.get('check') == 'precedent_check'
                              for f in rec.get('failed') or []), out[-300:]))
        full_runs()
        before = copies()
        rc, out = run('--promote', '--to', 'main', '--fast')
        cases.append(('after it, the fast move asks: exit 4, the failing check '
                      'on its own line, the question in the person\'s words, '
                      'nothing pushed',
                      rc == 4 and '  precedent_check: ' in out
                      and 'Run the move anyway? Say yes to continue' in out
                      and copies() == before, out[-400:]))
        rc, out = run('--promote', '--to', 'main', '--fast',
                      '--despite-failed-tests')
        cases.append(('--despite-failed-tests goes on: exit 3, a copy made, still '
                      'no full suite', rc == 3 and copies() != before
                      and full_runs() == 0, out[-300:]))

        # A failure recorded on an older commit is stale.
        commit_on('staging', 'more', 'more.txt', 'm\n')
        run('--land', 'more')
        rc, out = run('--promote', '--to', 'main', '--fast')
        cases.append(('a failure on an older commit is reported stale and asks '
                      'nothing: exit 3', rc == 3 and 'STALE' in out
                      and 'Say yes to continue' not in out, out[-300:]))

        # A private repository whose GitHub test is not due (Morgan,
        # 2026-10-09): the full suite runs on main here after the merge,
        # unless Debut passed on exactly this, only prose changed, or the
        # person asked for a fast one -- and the end-of-turn check holds
        # the turn until it has started.
        pj_path = work / 'precedent.json'
        pj_before = pj_path.read_text(encoding='utf-8')
        bare = tmp / 'origin.git'

        def private(on):
            pj_path.write_text(_json.dumps(dict(_json.loads(pj_before),
                                                visibility='private',
                                                github_ci_main_test='never'),
                                           indent=2) + '\n' if on else pj_before,
                               encoding='utf-8')

        def merged(out):
            m = re.search(r'expectedHeadSha ([0-9a-f]{40})', out)
            if m:
                git(bare, 'update-ref', 'refs/heads/main', m.group(1))
                git(work, 'fetch', '-q', 'origin')
            return m.group(1) if m else ''

        def fast(*extra):
            private(True)
            try:
                rc, out = run('--promote', '--to', 'main', '--fast', *extra)
            finally:
                private(False)
            return rc, out, (out.strip().splitlines()[-1] if out.strip() else '')

        # The earlier failing check's FAIL file comes off staging first, so a
        # full run on main can pass.
        git(work, 'fetch', '-q', 'origin')
        git(work, 'checkout', '-q', '-B', 'unbreak', 'origin/staging')
        if (work / 'FAIL').exists():
            git(work, 'rm', '-q', 'FAIL')
            git(work, 'commit', '-q', '-m', 'FAIL off staging')
        git(work, 'push', '-q', 'origin', 'HEAD:refs/heads/unbreak')
        run('--land', 'unbreak')
        commit_on('staging', 'quiet', 'quiet.json', '{}\n')
        run('--land', 'quiet')
        rc, out, last = fast()
        cases.append(('not due, code changed: no one waits on GitHub, and the '
                      'full suite on main is asked for after the merge',
                      rc == 3 and 'not due on this one' in out
                      and '--wait-main-test' not in last
                      and '--run-tests main' in last, out[-500:]))
        sha = merged(out)
        owed = pb.full_check_owed(work) if hasattr(pb, 'full_check_owed') else None
        cases.append(('once merged, the end-of-turn check says the full check '
                      'is owed and not started',
                      bool(owed) and owed[0][0] == sha and owed[0][1] == 'none',
                      str(owed)))
        rc, out = run('--run-tests', 'main')
        owed = pb.full_check_owed(work) if hasattr(pb, 'full_check_owed') else None
        cases.append(('after --run-tests main passes, nothing is owed',
                      rc == 0 and owed == [], f'exit {rc}: {owed} {out[-200:]}'))

        commit_on('staging', 'prose', 'notes.md', '# Notes\n\nA line.\n')
        run('--land', 'prose')
        rc, out, last = fast()
        cases.append(('only prose changed: no full check after, and it says why',
                      rc == 3 and 'only prose changed' in out
                      and '--run-tests main' not in last, out[-400:]))
        merged(out)

        commit_on('staging', 'tested', 'tested.json', '{}\n')
        run('--land', 'tested')
        run('--run-tests')
        rc, out, last = fast()
        cases.append(('Debut (Run tests) passed on exactly this: no full check '
                      'after', rc == 3 and 'already passed on exactly this' in out
                      and '--run-tests main' not in last, out[-400:]))
        merged(out)

        commit_on('staging', 'hurry', 'hurry.json', '{}\n')
        run('--land', 'hurry')
        rc, out, last = fast('--no-full-after')
        marked = git(work, 'ls-remote', 'origin',
                     'refs/precedent/main-unchecked').stdout.strip()
        cases.append(('asked for fast: no full check after, it says so, and '
                      'main is marked as moved without one, on origin',
                      rc == 3 and 'asked for a fast one' in out
                      and '--run-tests main' not in last and bool(marked),
                      out[-400:]))
        merged(out)
        state = pb.main_unchecked(work) if hasattr(pb, 'main_unchecked') else None
        cases.append(('the mark counts the moves made without a full check',
                      bool(state) and state[1] >= 1, str(state)))
        rc, out = run('--run-tests', 'main')
        cleared = not git(work, 'ls-remote', 'origin',
                          'refs/precedent/main-unchecked').stdout.strip()
        cases.append(('the next full run on main clears the mark',
                      rc == 0 and cleared, out[-300:]))
        commit_on('staging', 'last', 'last.json', '{}\n')
        run('--land', 'last')

        # --- the full move into main, only when asked for by name ---
        # The long way is taken only on the person's own words (Morgan,
        # 2026-10-11: "only do the long way when explicitly authorized"):
        # --full alone is refused before anything runs or is pushed.
        full_runs()
        rc, out = run('--promote', '--to', 'main', '--full')
        cases.append(('--full without the person\'s words is refused, and '
                      'nothing runs', rc == 2 and 'PROMOTE REFUSED' in out
                      and '--because' in out and full_runs() == 0,
                      f'exit {rc}: {out[-300:]}'))
        rc, out = run('--promote', '--to', 'main', '--full', '--because', '  ')
        cases.append(('...and blank words are no words', rc == 2
                      and 'PROMOTE REFUSED' in out and full_runs() == 0,
                      f'exit {rc}: {out[-300:]}'))
        rc, out = run('--promote', '--to', 'main', '--full', '--because',
                      'Produce the long way')
        cases.append(('with --full and their words, the move into main runs '
                      'the full suite, and says whose words',
                      full_runs() >= 1 and 'full push check' in out
                      and "because the person asked: 'Produce the long way'" in out,
                      f'exit {rc}: {out[-300:]}'))
        # The fast move is the default (Morgan, 2026-10-11: "default to the
        # fast route unless I explicitly agree to or request the slow
        # route"): a bare --promote --to main asks for it, --full is the one
        # way to the old route, and a flag meant for the fast move refuses
        # beside --full rather than being dropped.
        pa = pb.promote_args
        cases += [
            ('a bare --promote --to main is the fast move',
             (pa(['--to', 'main']) or {}).get('fast') is True),
            ('a bare --promote is the fast move if its step is main',
             (pa([]) or {}).get('fast') is True),
            ('--full asks for the old route', (pa(['--to', 'main', '--full'])
                                              or {}).get('fast') is False),
            ('--fast is still taken and changes nothing',
             pa(['--fast']) == pa(['--to', 'main'])),
            ('--full beside a fast-move flag is a usage error',
             pa(['--to', 'main', '--full', '--despite-failed-tests']) is None
             and pa(['--full', '--fast']) is None),
            ('--because without --full is a usage error',
             pa(['--to', 'main', '--because', 'x']) is None),
            ('the refusal: --full with no words is refused, with words passes',
             bool(pb.full_route_refusal(pa(['--to', 'main', '--full'])))
             and pb.full_route_refusal(pa(['--to', 'main', '--full',
                                           '--because', 'yes, the long way'])) is None
             and pb.full_route_refusal(pa(['--to', 'main'])) is None),
            ('a fast-move flag on the move into staging is a usage error',
             pa(['--to', 'staging', '--full']) is None
             and pa(['--to', 'staging', '--no-full-after']) is None)]
    bad = [(c[0], c[2] if len(c) > 2 else '') for c in cases if not c[1]]
    check(f'{name} ({len(cases)} stated cases)', not bad,
          '; '.join(f"{n}{' (' + d + ')' if d else ''}" for n, d in bad))


def check_debut_judges_the_change_against_main_too():
    """A Debut judges what depends on the base against main as well as
    staging, so a green Debut cannot be followed by a red main (2026-10-17).

    That day a Debut passed on staging and Produce turned main red: staging
    had deleted a file a page still named, the full suite measured the
    change from staging (where nothing was deleted), and GitHub's test of
    the pull request into main measured it from main. Three pieces:

    - precedent_check.py takes the base from PRECEDENT_CHANGED_SINCE first,
      when it names a commit (the push check already set it, and nothing
      read it), and falls back as before when it does not;
    - --base-dependent selects only the checks a base can change -- every
      change-scope check and each tree check reaching the resolver -- so the
      second pass is seconds, never a second suite (Morgan: "It should
      NOT");
    - --run-tests runs that pass with main's tip as the base, and fails,
      naming the check, when it finds what main would; so does Produce,
      before it pushes the copy, since a Debut is optional and the quick
      tier of an upstream repository runs no rename check."""
    import tempfile, importlib.util as _u
    name = 'the Debut judges the change against main too'
    pc_path = ROOT / 'tools' / 'precedent_check.py'
    if not (ROOT / 'tools' / 'precedent_branches.py').exists() or not pc_path.exists():
        not_applicable(name, 'precedent_branches.py or precedent_check.py is absent')
        return
    cases = []
    with tempfile.TemporaryDirectory() as td:
        tmp = pathlib.Path(td)
        env = _stale_ref_fixture_env(tmp)
        work, git, branches, tip = _promote_fixture(
            tmp, env, 'staging', ('main', 'staging'))
        # The stub judges the way rename-updates-links does: a file the
        # change deleted, measured from the base it is given.
        (work / 'tools' / 'precedent_check.py').write_text(
            'import os, subprocess, sys\n'
            'if "--base-dependent" in sys.argv:\n'
            '    base = os.environ.get("PRECEDENT_CHANGED_SINCE") or "origin/staging"\n'
            '    d = subprocess.run(["git", "diff", "--name-status", base, "HEAD"],\n'
            '                       capture_output=True, text=True).stdout\n'
            '    if "D\\tgone.py" in d:\n'
            '        print("VIOLATION  rename-updates-links")\n'
            '        print("    doc.md:1: still references \'gone.py\', which this branch deleted")\n'
            '        print("precedent_check: 0 passed, 1 violated")\n'
            '        sys.exit(1)\n'
            'print("precedent_check: 3 passed, 0 violated")\n', encoding='utf-8')
        (work / 'gone.py').write_text('x = 1\n', encoding='utf-8')
        (work / 'doc.md').write_text('See gone.py.\n', encoding='utf-8')
        git(work, 'add', '-A')
        git(work, 'commit', '-q', '-m', 'stub, a file and a page naming it')
        git(work, 'push', '-q', 'origin', 'HEAD:main', 'HEAD:staging')
        # Staging deletes the file and leaves the page, already landed.
        git(work, 'rm', '-q', 'gone.py')
        git(work, 'commit', '-q', '-m', 'delete gone.py')
        git(work, 'push', '-q', 'origin', 'HEAD:staging')
        rc, out = branches('--run-tests')
        cases.append(('a Debut of staging that deleted a file main still has '
                      'fails, naming the check and main',
                      rc == 1 and 'rename-updates-links (against main)' in out,
                      out[-300:]))
        cases.append(('...and the RUN TESTS RESULT line names it',
                      'RUN TESTS RESULT: staging: FAILED' in out
                      and 'against main' in out.split('RUN TESTS RESULT')[-1],
                      out[-200:]))
        before = tip('main')
        rc, out = branches('--promote', '--to', 'main')
        cases.append(('a Produce right after that failed Debut asks first '
                      '(exit 4)', rc == 4, out[-200:]))
        # Past the question, Produce's own pass refuses it too, as it would
        # with no Debut at all.
        rc, out = branches('--promote', '--to', 'main', '--despite-failed-tests')
        cases.append(('a Produce of the same staging is refused before it '
                      'pushes anything, naming the check and main',
                      rc == 1 and 'PROMOTE REFUSED' in out
                      and 'rename-updates-links (against main)' in out,
                      out[-300:]))
        cases.append(('...and main did not move', tip('main') == before))
        # Main catches up: the same tree now passes.
        git(work, 'push', '-q', 'origin', 'HEAD:main')
        rc, out = branches('--run-tests')
        cases.append(('once main has the deletion too, the Debut passes',
                      rc == 0 and 'against main)' not in out, out[-300:]))
        rc, out = branches('--run-tests', 'main')
        cases.append(('a Debut of main itself takes no second pass',
                      rc == 0 and 'judging the change against main' not in out,
                      out[-300:]))
    bad = [(c[0], c[2] if len(c) > 2 else '') for c in cases if not c[1]]
    check(f'{name} ({len(cases)} stated cases)', not bad,
          '; '.join(f"{n}{' (' + d + ')' if d else ''}" for n, d in bad))


def check_promote_ends_with_its_result_line():
    """A Promote's last line of output is its verdict, on every path.

    Reported 2026-10-08 from a consuming repository: a session ran a Debut
    with its output written to a log file, and Claude Code's auto mode
    refused the `tail` that would have read the log back, so the session
    could not say whether the Debut had worked. The verdict now comes last
    on stdout whatever happens -- moved, nothing to move, refused, ready
    for main's pull request, or an error -- as one line opening
    "PROMOTE RESULT:", any commit in it written in full, so the command's
    own output answers without a second read.

    Asserted on stdout alone: a line that only reached stderr would not be
    the last line a session reads from a redirected run."""
    import re as _re
    import tempfile
    name = 'a Promote ends with one PROMOTE RESULT line, on every path'
    tool = ROOT / 'tools' / 'precedent_branches.py'
    if not tool.exists():
        not_applicable(name, 'tools/precedent_branches.py is absent')
        return
    sha40 = _re.compile(r'\b[0-9a-f]{40}\b')
    cases = []

    def run(work, env, *a):
        p = subprocess.run([sys.executable, 'tools/precedent_branches.py', *a],
                           cwd=work, capture_output=True, text=True, env=env)
        lines = p.stdout.rstrip('\n').splitlines()
        return p.returncode, (lines[-1] if lines else ''), p.stdout

    def one_result(out):
        return sum(1 for l in out.splitlines() if l.startswith('PROMOTE RESULT:')) == 1

    with tempfile.TemporaryDirectory() as td:
        tmp = pathlib.Path(td)
        # Who is running it comes from identity.json alone, never this
        # machine's own PRECEDENT_GITHUB_USER.
        env = dict(_stale_ref_fixture_env(tmp), PRECEDENT_GITHUB_USER='')
        work, git, _branches, tip = _promote_fixture(
            tmp, env, 'staging', ('main', 'staging'))
        git(work, 'checkout', '-q', '-b', 'session-work', 'origin/staging')
        (work / 'two.txt').write_text('2\n', encoding='utf-8')
        git(work, 'add', 'two.txt')
        git(work, 'commit', '-q', '-m', 'work')
        git(work, 'push', '-q', 'origin', 'HEAD:refs/heads/staging')

        # There is no step into staging (2026-10-17): asked
        # for, it moves nothing and says why, still on its result line.
        before = tip('staging')
        rc, last, out = run(work, env, '--promote', '--to', 'staging')
        cases.append((f'the retired step into staging ends NOTHING TO PROMOTE and '
                      f'says why (rc={rc}, last: {last!r})',
                      rc == 0 and last.startswith('PROMOTE RESULT:')
                      and 'NOTHING TO PROMOTE' in last and 'no step into staging' in last
                      and tip('staging') == before and one_result(out)))

        rc, last, out = run(work, env, '--promote', '--to', 'main', '--full', '--because', 'test the long way')
        copy = next((l.split('pull request from ', 1)[1].split()[0]
                     for l in [last] if 'pull request from ' in l), '')
        cases.append((f'a Produce ready for its pull request ends READY FOR MAIN '
                      f'with the copy and its full head (rc={rc}, last: {last!r})',
                      rc == 3 and last.startswith(
                          'PROMOTE RESULT: main <- staging: READY FOR MAIN: open a '
                          'pull request from ')
                      and bool(copy) and tip(copy) != ''
                      and f'expectedHeadSha {tip(copy)}' in last
                      and one_result(out)))

    with tempfile.TemporaryDirectory() as td:
        tmp = pathlib.Path(td)
        # Who is running it comes from identity.json alone, never this
        # machine's own PRECEDENT_GITHUB_USER.
        env = dict(_stale_ref_fixture_env(tmp), PRECEDENT_GITHUB_USER='')
        work, git, _branches, tip = _promote_fixture(
            tmp, env, 'staging', ('main', 'staging'))
        git(work, 'checkout', '-q', '-b', 'session-work', 'origin/staging')
        (work / 'tools' / 'precedent_check.py').write_text(
            'import sys\nprint("precedent_check: 0 passed, 1 violated")\n'
            'sys.exit(1)\n', encoding='utf-8')
        git(work, 'commit', '-q', '-am', 'a check that fails')
        git(work, 'push', '-q', 'origin', 'HEAD:refs/heads/staging')
        before = tip('main')
        rc, last, out = run(work, env, '--promote', '--to', 'main', '--full',
                            '--because', 'test the long way')
        cases.append((f'a refused Produce ends PROMOTE REFUSED, with a reason, '
                      f'and main does not move (rc={rc}, last: {last!r})',
                      rc == 1 and tip('main') == before
                      and last.startswith('PROMOTE RESULT: main <- staging: PROMOTE REFUSED: ')
                      and one_result(out)))

        # An error mid-run still ends on the line, after the run's own output.
        sys.path.insert(0, str(work / 'tools'))
        try:
            import importlib
            spec = importlib.util.spec_from_file_location(
                '_pb_result_line', work / 'tools' / 'precedent_branches.py')
            pb = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(pb)
        finally:
            sys.path.pop(0)

        def boom(*_a, **_k):
            raise RuntimeError('planted failure')
        pb.promotion_step = boom
        said, raised = [], None
        saved = {k: os.environ.get(k) for k in env}
        os.environ.update(env)
        try:
            pb.promote(str(work), say=said.append, to='main')
        except RuntimeError as exc:
            raised = exc
        finally:
            for k, v in saved.items():
                if v is None:
                    os.environ.pop(k, None)
                else:
                    os.environ[k] = v
        cases.append((f'an error still ends on the result line, and is not '
                      f'swallowed (last: {said[-1] if said else None!r})',
                      raised is not None and bool(said)
                      and said[-1].startswith('PROMOTE RESULT: main <- staging: '
                                              'PROMOTE REFUSED: the run stopped on an error')))
    failed = [n for n, ok in cases if not ok]
    check(f'{name} ({len(cases)} stated cases)', not failed, '; '.join(failed))


def check_ladder_test_session_and_the_two_ladder_checks():
    """spec/LADDER_OPT_IN_PLAN.md D7, D13 and the per-person rule.

    - A No ladders session pushes and merges nothing: the push gate and the
      merge check refuse, by name; without the variable neither refuses.
    - set-words-stay-in-their-set finds a made-up set's words planted in
      a practice set that declares that set, passes the owning set itself,
      an individual set whose person brings it, a Story, and a practice
      that requires the owner's capability; and finds a set whose words do
      not match its own examples.
    - ladder-set-is-brought-not-declared finds a precedent.json that
      declares a set providing the ladder, and passes one that declares an
      ordinary set: the ladder is each person's to bring, and a repository
      that declares it puts it on everybody who works there."""
    import shutil, tempfile
    import precedent_check as pc
    import precedent_ladder
    cases = []
    env = {k: v for k, v in os.environ.items()
           if k not in ('PRECEDENT_ASSUME_LADDER',)}
    env['PRECEDENT_NO_LADDERS'] = '1'
    r = subprocess.run([sys.executable, 'tools/precedent_push_check.py', '--gate'],
                       cwd=str(ROOT), env=env, capture_output=True, text=True,
                       timeout=120)
    cases.append(('a No ladders session: the push gate refuses',
                  r.returncode == 1 and 'nothing is pushed' in r.stdout,
                  f'rc={r.returncode} {r.stdout[:200]}'))
    r = subprocess.run([sys.executable, 'tools/precedent_merge_check.py',
                        '--owner', 'o', '--repo', 'r', '--number', '1'],
                       cwd=str(ROOT), env=env, capture_output=True, text=True,
                       timeout=120)
    cases.append(('a No ladders session: the merge check refuses',
                  r.returncode == 1 and 'nothing is pushed' in r.stdout,
                  f'rc={r.returncode} {r.stdout[:200]}'))
    old_env = os.environ.pop('PRECEDENT_NO_LADDERS', None)
    try:
        cases.append(('any other session: no refusal',
                      precedent_ladder.test_session_refusal() is None, ''))
    finally:
        if old_env is not None:
            os.environ['PRECEDENT_NO_LADDERS'] = old_env

    tmp = pathlib.Path(tempfile.mkdtemp(prefix='precedent-ladder-checks-'))
    saved_root = pc.ROOT
    saved_cfg = os.environ.get('PRECEDENT_USER_CONFIG')
    try:
        # set-words-stay-in-their-set, with made-up words: zz-owner owns
        # "Zorpify" and "phase N of 9". Each set below is judged against the
        # sets in force for it -- its precedent.json and its person's config.
        plain, ladder = tmp / 'plain-set', tmp / 'ladder-set'
        owner = tmp / 'zz-owner'
        ind_own, ind_plain, ind_gone = (tmp / 'ind-brings-owner',
                                        tmp / 'ind-brings-plain',
                                        tmp / 'ind-brings-uncloned')
        words = {'patterns': [
            {'kind': 'a zz command', 'regex': r'(?:\*\*|")Zorpify(?:\*\*|")',
             'matches': ['"Zorpify"'], 'never_matches': ['zorpify']},
            {'kind': 'a zz step', 'regex': r'\bphase [1-9] of 9\b'}]}
        declares_owner = {'sources': [{'name': 'zz-owner', 'level': 'shared',
                                       'path': str(owner)}]}
        _genv = dict(os.environ, GIT_AUTHOR_NAME='F', GIT_AUTHOR_EMAIL='f@x',
                     GIT_COMMITTER_NAME='F', GIT_COMMITTER_EMAIL='f@x',
                     GIT_CONFIG_GLOBAL=os.devnull, PRECEDENT_ALLOW_ANY_AUTHOR='1')
        for d, man, cfg in (
                (plain, {'level': 'shared', 'provides': []}, declares_owner),
                (ladder, {'level': 'shared', 'provides': ['ladder']}, None),
                (owner, {'level': 'shared', 'provides': ['zz-cap'],
                         'owned_words': words}, None),
                (ind_own, {'level': 'individual', 'brings': [
                    {'name': 'zz-owner', 'repo_url': 'https://example.com/z.git'}]}, None),
                (ind_plain, {'level': 'individual', 'brings': [
                    {'name': 'plain-set', 'repo_url': 'https://example.com/p.git'}]},
                 declares_owner),
                (ind_gone, {'level': 'individual', 'brings': [
                    {'name': 'not-cloned-set', 'repo_url': 'https://example.com/n.git'}]},
                 declares_owner)):
            (d / 'practices').mkdir(parents=True)
            (d / 'precedent-source.json').write_text(json.dumps(
                dict(name=d.name, **man)))
            if cfg:
                (d / 'precedent.json').write_text(json.dumps(cfg))
            (d / 'practices' / 'x.md').write_text(
                '---\nslug: x\nstatus: active\n---\n\n## Rule\n\n'
                'Say "Zorpify" at phase 3 of 9.\n\n## Story\n\n'
                'On the day, we said "Zorpify" at phase 2 of 9.\n')
            subprocess.run(['git', 'init', '-q', str(d)], env=_genv, check=True)
        # A practice that requires the owner's capability is its own.
        (plain / 'practices' / 'y.md').write_text(
            '---\nslug: y\nstatus: active\nrequires: ["zz-cap"]\n---\n\n'
            '## Rule\n\nSay "Zorpify".\n')
        no_cfg = tmp / 'no-config.json'

        def judge(root, individual=None):
            cfg = tmp / f'cfg-{root.name}.json'
            if individual:
                cfg.write_text(json.dumps({'individual': {'path': str(individual)}}))
            os.environ['PRECEDENT_USER_CONFIG'] = str(cfg if individual else no_cfg)
            pc.ROOT = root
            try:
                got = pc._set_words_stay_in_their_set(None)
                return len(got), got, ''
            except pc.NotApplicable as e:
                return None, [], str(e)

        for root, ind, want, because, what in (
                (plain, None, 2, '', 'a set that declares the owner'),
                (owner, None, None, 'declares words of its own', 'the owning set itself'),
                (ind_own, ind_own, None, 'brought by this set', 'an individual set that brings it'),
                (ind_plain, ind_plain, 2, '', 'an individual set that brings only an ordinary set'),
                (ind_gone, ind_gone, 2, '', 'an individual set whose other brought set is not cloned')):
            n, got, why = judge(root, ind)
            # A skip says why, so a skip for another reason fails here.
            cases.append((f'set words in {what}: '
                          f'{"skipped" if want is None else f"{want} finding(s), none in the Story or a practice that requires the capability"}',
                          (n is None and because in why) if want is None else
                          (n == want and all('x.md:8:' in str(f) for f in got)),
                          f'got {n} {why!r}: {[str(f) for f in got][:4]}'))
        # A set whose declared words do not match their own examples.
        (owner / 'precedent-source.json').write_text(json.dumps(dict(
            name='zz-owner', level='shared', owned_words={'patterns': [
                {'kind': 'a zz command', 'regex': r'\bZorpify\b',
                 'matches': ['Zorpify'], 'never_matches': ['Zorpify!']}]})))
        n, got, why = judge(owner)
        cases.append(('a set whose words match what it says they never should: '
                      'one finding, on its own precedent-source.json',
                      n == 1 and 'precedent-source.json' in str(got[0]),
                      f'got {n} {why!r}: {[str(f) for f in got]}'))
        (owner / 'precedent-source.json').write_text(json.dumps(dict(
            name='zz-owner', level='shared', provides=['zz-cap'], owned_words=words)))
        # The same individual set checked from a linked worktree elsewhere
        # (2026-10-04): a Debut or Produce checks the set in a throwaway
        # worktree under the temp directory, where nothing sits beside it.
        # The set it brings is found beside the main checkout, so the check
        # still stands aside -- before, the set's own Debut was refused.
        subprocess.run(['git', '-C', str(ind_own), 'add', '-A'], env=_genv, check=True)
        subprocess.run(['git', '-C', str(ind_own), 'commit', '-qm', 'x', '--no-verify'],
                       env=_genv, check=True)
        _elsewhere = pathlib.Path(tempfile.mkdtemp(prefix='precedent-ladder-wt-'))
        _wt = _elsewhere / 'wt'
        subprocess.run(['git', '-C', str(ind_own), 'worktree', 'add', '-q', '--detach',
                        str(_wt)], env=_genv, check=True)
        try:
            n, got, why = judge(_wt, ind_own)
            cases.append(('set words in an individual set that brings the owner, '
                          'checked from a linked worktree elsewhere: skipped',
                          n is None and 'brought by this set' in why,
                          f'got {n} {why!r}'))
        finally:
            shutil.rmtree(_elsewhere, ignore_errors=True)
            if saved_cfg is None:
                os.environ.pop('PRECEDENT_USER_CONFIG', None)
            else:
                os.environ['PRECEDENT_USER_CONFIG'] = saved_cfg
        repo = tmp / 'repo'
        repo.mkdir()
        for declared, want, what in (('ladder-set', 1, 'declares the ladder set'),
                                     ('plain-set', 0, 'declares an ordinary set')):
            (repo / 'precedent.json').write_text(json.dumps({'sources': [
                {'name': declared, 'level': 'shared', 'path': f'../{declared}'}]}))
            pc.ROOT = repo
            got = pc._ladder_set_is_brought_not_declared(None)
            cases.append((f'a precedent.json that {what}: {want} finding(s)',
                          len(got) == want, str([str(f) for f in got])[:300]))
        # D18 narrowed (2026-10-19): one code owner's quoted, dated yes in
        # binds_everyone lets a repository declare the ladder.
        ok_by = 'Fx Owner, 2026-10-19: "bind everyone here"'
        for be, owners_file, want, what in (
                ({'sets': ['ladder-set'], 'approved_by': ok_by}, None, 0,
                 'a code owner, by name, binds everyone'),
                ({'sets': ['ladder-set'],
                  'approved_by': 'fxowner, 2026-10-19: "yes"'}, None, 0,
                 'a code owner, by login, binds everyone'),
                ({'sets': ['ladder-set'],
                  'approved_by': 'Someone Else, 2026-10-19: "yes"'}, None, 1,
                 'NEGATIVE CONTROL: a quote from someone who is not a code owner'),
                ({'sets': ['ladder-set'],
                  'approved_by': 'Fx Owner: "bind everyone"'}, None, 1,
                 'NEGATIVE CONTROL: an undated quote'),
                ({'sets': ['ladder-set'],
                  'approved_by': 'Fx Owner, 2026-10-19, said yes'}, None, 1,
                 'NEGATIVE CONTROL: a paraphrase, quoting nobody'),
                ({'sets': ['other-set'], 'approved_by': ok_by}, None, 1,
                 'NEGATIVE CONTROL: an entry that names a different set'),
                ({'sets': ['ladder-set'], 'approved_by': ok_by},
                 '* @someone-else\n', 1,
                 'NEGATIVE CONTROL: a CODEOWNERS file that does not name them'),
                ({'sets': ['ladder-set'],
                  'approved_by': 'someone-else, 2026-10-19: "yes"'},
                 '* @someone-else\n', 0,
                 'the code owner CODEOWNERS names binds everyone')):
            (repo / 'precedent.json').write_text(json.dumps({
                'maintainers': [{'github': 'fxowner', 'name': 'Fx Owner'}],
                'binds_everyone': be,
                'sources': [{'name': 'ladder-set', 'level': 'shared',
                             'path': '../ladder-set'}]}))
            co = repo / 'CODEOWNERS'
            if owners_file:
                co.write_text(owners_file)
            elif co.exists():
                co.unlink()
            pc.ROOT = repo
            got = pc._ladder_set_is_brought_not_declared(None)
            cases.append((f'binds_everyone, {what}: {want} finding(s)',
                          len(got) == want, str([str(f) for f in got])[:300]))
    finally:
        pc.ROOT = saved_root
        shutil.rmtree(tmp, ignore_errors=True)
    # A path rule in a set the person brings fires for them through
    # precedent_paths.py, and for nobody else (2026-10-02: the paths channel
    # read the repository's practices/ alone, so checks-follow-the-tier
    # stopped reaching the person who brings it when it moved).
    tmp = pathlib.Path(tempfile.mkdtemp(prefix='precedent-brought-paths-'))
    try:
        repo, ind, lad = tmp / 'repo', tmp / 'precedent-individual', tmp / 'fx-ladder'
        (repo / 'practices').mkdir(parents=True)
        (repo / 'precedent.json').write_text(json.dumps(
            {'format_version': 1, 'visibility': 'private', 'sources': []}))
        (ind / 'practices').mkdir(parents=True)
        (ind / 'precedent-source.json').write_text(json.dumps(
            {'name': 'precedent-individual', 'level': 'individual',
             'brings': [{'name': 'fx-ladder',
                         'repo_url': 'https://example.com/fx-ladder.git'}]}))
        (lad / 'practices').mkdir(parents=True)
        (lad / 'precedent-source.json').write_text(json.dumps(
            {'name': 'fx-ladder', 'level': 'shared', 'provides': ['ladder']}))
        (lad / 'practices' / 'fx-path-rule.md').write_text(
            '---\nslug:        fx-path-rule\ntitle:       "fx"\n'
            'tier:        on-demand\nseverity:    default\n'
            'applies_to:  ["tools/*.py"]\napplies_to_why: "fx"\n'
            'occasion:    null\nindex_clause: "fx clause"\nstatus:      active\n'
            '---\n\n## Rule\n\nThe brought path rule.\n')
        cfg = tmp / 'config.json'
        cfg.write_text(json.dumps({'format_version': 1, 'individual': {
            'name': 'precedent-individual', 'path': str(ind)}}))
        for what, extra, want in (('the person who brings it', {}, True),
                                  ('a person with no such set',
                                   {'PRECEDENT_USER_CONFIG': str(tmp / 'none.json')}, False),
                                  ('the same person, No ladders',
                                   {'PRECEDENT_NO_LADDERS': '1'}, False)):
            e = {k: v for k, v in os.environ.items()
                 if k not in ('PRECEDENT_ASSUME_LADDER', 'PRECEDENT_NO_LADDERS')}
            e['PRECEDENT_USER_CONFIG'] = str(cfg)
            e.update(extra)
            r = subprocess.run([sys.executable, str(ROOT / 'tools' / 'precedent_paths.py'),
                                '--repo', str(repo), 'tools/x.py'],
                               env=e, capture_output=True, text=True, timeout=120)
            got = 'The brought path rule.' in r.stdout
            cases.append((f'a brought path rule {"fires" if want else "is silent"} '
                          f'for {what}', got == want, (r.stdout + r.stderr)[-300:]))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    # The push check recognises the size-cap warning precedent_check.py
    # prints today (2026-10-02: that wording was made plain and the push
    # check went on looking for the old one, so its closing reminder never
    # fired).
    import precedent_push_check as ppc
    src = (ROOT / 'tools' / 'precedent_check.py').read_text(encoding='utf-8')
    m = re.search(r"WARNING    \{slug\} — (over a size cap\.[^']*)'", src)
    cases.append(("the push check matches precedent_check's size-cap warning "
                  "as it is printed today",
                  bool(m) and any(w in m.group(1) for w in ppc.SIZE_CAP_WARNINGS),
                  m.group(1) if m else 'warning text not found'))

    # A config named outside $HOME is somebody other than the person whose
    # home the bootstrap hook works in, so the self-heal does not run it
    # (2026-10-02: fixtures naming their own config kept putting this
    # machine's individual clone back on its pinned branch). Inside $HOME it
    # still runs.
    import precedent_resolve as _pr_heal
    tmp = pathlib.Path(tempfile.mkdtemp(prefix='precedent-heal-named-'))
    saved = {k: os.environ.get(k) for k in ('CLAUDE_CODE_REMOTE',
                                            'PRECEDENT_USER_CONFIG', 'HOME')}
    try:
        repo, home = tmp / 'repo', tmp / 'home'
        hook = repo / _pr_heal.INDIVIDUAL_BOOTSTRAP_HOOK
        hook.parent.mkdir(parents=True)
        home.mkdir()
        marker = tmp / 'hook-ran'
        hook.write_text(f'#!/bin/bash\ntouch {marker}\n', encoding='utf-8')
        os.environ['CLAUDE_CODE_REMOTE'] = 'true'
        os.environ['HOME'] = str(home)
        os.environ['PRECEDENT_USER_CONFIG'] = str(tmp / 'elsewhere' / 'config.json')
        r1 = _pr_heal._self_heal_individual_source(repo)
        ran1 = marker.exists()
        os.environ['PRECEDENT_USER_CONFIG'] = str(home / 'config.json')
        r2 = _pr_heal._self_heal_individual_source(repo)
        ran2 = marker.exists()
        cases.append(('a config named outside $HOME does not run the bootstrap '
                      'hook; one inside $HOME still does',
                      r1 == 'not-remote' and not ran1 and r2 == 'attempted' and ran2,
                      f'{r1} {ran1} {r2} {ran2}'))
    finally:
        for k, v in saved.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v
        shutil.rmtree(tmp, ignore_errors=True)

    # A rule from a brought set counts as reached through the session file
    # wherever that channel is wired, in a private repository too; with the
    # channel not wired it is reported (2026-10-02: only public repositories
    # counted the channel, so a private one called every brought rule
    # reachable by nothing).
    tmp = pathlib.Path(tempfile.mkdtemp(prefix='precedent-brought-reach-'))
    saved_root, saved_cfg = pc.ROOT, os.environ.get('PRECEDENT_USER_CONFIG')
    try:
        repo, ind, lad = tmp / 'repo', tmp / 'precedent-individual', tmp / 'fx-ladder'
        for d in (repo / 'practices', repo / 'tools', repo / '.claude' / 'hooks',
                  ind / 'practices', lad / 'practices'):
            d.mkdir(parents=True)
        (repo / 'AGENTS.md').write_text('# nothing names it\n')
        (repo / 'precedent.json').write_text(json.dumps(
            {'format_version': 1, 'visibility': 'private', 'sources': []}))
        shutil.copy(ROOT / 'tools' / 'precedent_session_practices.py', repo / 'tools')
        (ind / 'precedent-source.json').write_text(json.dumps(
            {'name': 'precedent-individual', 'level': 'individual',
             'brings': [{'name': 'fx-ladder',
                         'repo_url': 'https://example.com/fx-ladder.git'}]}))
        (lad / 'precedent-source.json').write_text(json.dumps(
            {'name': 'fx-ladder', 'level': 'shared', 'provides': ['ladder']}))
        (lad / 'practices' / 'fx-unrouted.md').write_text(
            '---\nslug:        fx-unrouted\ntitle:       "fx"\n'
            'tier:        on-demand\nseverity:    default\napplies_to:  ["**"]\n'
            'occasion:    null\ngates:       []\nchecked_by:  null\n'
            'status:      active\n---\n\n## Rule\n\nUnrouted.\n')
        cfg = tmp / 'config.json'
        cfg.write_text(json.dumps({'format_version': 1, 'individual': {
            'name': 'precedent-individual', 'path': str(ind)}}))
        os.environ['PRECEDENT_USER_CONFIG'] = str(cfg)
        pc.ROOT = repo
        hook = repo / '.claude' / 'hooks' / 'session-start.sh'
        for wired, want in ((True, False), (False, True)):
            hook.write_text('#!/bin/bash\n' + ('python3 tools/precedent_session_practices.py\n'
                                                if wired else '# no loader here\n'))
            got = any('fx-unrouted' in str(f) for f in (pc._practice_is_reachable(None) or []))
            cases.append((f'in a private repository with the session channel '
                          f'{"wired" if wired else "not wired"}, a brought rule is '
                          f'{"reported unreachable" if want else "reached"}',
                          got == want, f'reported={got}'))
    finally:
        pc.ROOT = saved_root
        if saved_cfg is None:
            os.environ.pop('PRECEDENT_USER_CONFIG', None)
        else:
            os.environ['PRECEDENT_USER_CONFIG'] = saved_cfg
        shutil.rmtree(tmp, ignore_errors=True)

    # A Promote in a repository with only main does nothing and creates no
    # branch (2026-10-02: it announced a move, failed, and left its lock
    # branch on origin).
    tmp = pathlib.Path(tempfile.mkdtemp(prefix='precedent-main-only-'))
    try:
        genv = {k: v for k, v in os.environ.items() if k != 'PRECEDENT_NO_LADDERS'}
        genv.update({'GIT_AUTHOR_NAME': 'x', 'GIT_AUTHOR_EMAIL': 'x@x',
                     'GIT_COMMITTER_NAME': 'x', 'GIT_COMMITTER_EMAIL': 'x@x',
                     'PRECEDENT_ASSUME_LADDER': '1'})
        g = lambda *a, cwd=tmp: subprocess.run(['git', *a], cwd=str(cwd), env=genv,
                                              capture_output=True, text=True)
        g('init', '-q', '--bare', '-b', 'main', 'origin.git')
        g('clone', '-q', str(tmp / 'origin.git'), 'work')
        work = tmp / 'work'
        (work / 'precedent.json').write_text('{"format_version": 1}\n')
        g('add', '-A', cwd=work)
        g('commit', '-qm', 'init', cwd=work)
        g('push', '-q', 'origin', 'HEAD:main', cwd=work)
        r = subprocess.run([sys.executable, str(ROOT / 'tools' / 'precedent_branches.py'),
                            '--promote', '--to', 'staging'], cwd=str(work), env=genv,
                           capture_output=True, text=True, timeout=300)
        heads = g('ls-remote', '--heads', 'origin', cwd=work).stdout
        cases.append(('a Promote in a repository with only main says there is '
                      'nothing to promote and creates no branch',
                      r.returncode == 0 and 'nothing to promote' in r.stdout
                      and heads.count('refs/heads/') == 1,
                      f'rc={r.returncode} {(r.stdout + r.stderr)[-200:]} heads={heads}'))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    bad = [(c[0], c[2]) for c in cases if not c[1]]
    check(f'the No ladders session refuses to push, and the two ladder checks '
          f'find what they name ({len(cases)} stated cases)',
          not bad, '; '.join(f"{n} -- {d}" for n, d in bad))


def check_the_engine_finds_this_sets_moves():
    """The engine finds this file through this set's precedent-source.json
    (`branch_moves`), as set_tool() finds any set's tool."""
    import precedent_resolve as pr
    found = pr.set_tool(SET_ROOT, 'branch_moves')
    check("the engine finds this set's moves by its branch_moves key",
          found is not None and found.resolve() == LADDER.resolve(), repr(found))


def check_cases_pass_whatever_their_order():
    """Two cases that each pass alone pass run together, in file order: a
    case never sees the engine module an earlier one cached (_run_one).

    Negative control, measured 2026-10-20 on the old runner: the pair below
    failed, "module 'precedent_branches' has no attribute
    'wait_for_main_test'"."""
    pair = ('check_private_repo_skipped_gate_is_not_main_test',
            'check_main_test_wait_does_not_ask_to_merge_what_is_merged')
    r = subprocess.run([sys.executable, str(pathlib.Path(__file__).resolve()), *pair],
                       capture_output=True, text=True, timeout=600,
                       env={**os.environ, 'PRECEDENT_ENGINE_ROOT': str(ENGINE_ROOT)})
    out = r.stdout + r.stderr
    name = 'two cases run together pass as each does alone, in file order'
    # Either case is N/A where BestPractice's own templates are absent (a
    # consumer-shaped copy, 2026-10-20): then the pair cannot show the order
    # dependence, which is not a failure.
    if r.returncode == 0 and '2 passed' not in out and 'not applicable' in out:
        not_applicable(name, 'a case of the pair is not applicable here, so '
                             'the two cannot run together')
        return
    check(name, r.returncode == 0 and 'has no attribute' not in out
          and '2 passed, 0 failed' in out, out[-600:])


def _engine_modules():
    """-> the names in sys.modules loaded from the engine's tools/ or the
    assembled one's, symlinks resolved."""
    dirs = {(ROOT / 'tools').resolve(), (ENGINE_ROOT / 'tools').resolve()}
    out = set()
    for name, mod in list(sys.modules.items()):
        f = getattr(mod, '__file__', None)
        try:
            if f and pathlib.Path(f).resolve().parent in dirs:
                out.add(name)
        except (OSError, ValueError):
            pass
    return out


def _run_one(n):
    """Run one case, then drop every engine module it loaded, so the next
    case imports its own.

    WHY (2026-10-20). check_private_repo_skipped_gate_is_not_main_test
    imports a tool whose symlink resolves into the engine's own tools/,
    which puts that directory on sys.path and caches the engine's plain
    precedent_branches, without this set's moves. A later case in the same
    run then failed: "module 'precedent_branches' has no attribute
    'wait_for_main_test'", while each passed alone."""
    before = _engine_modules()
    path = list(sys.path)
    try:
        globals()[n]()
    finally:
        for name in _engine_modules() - before:
            sys.modules.pop(name, None)
        sys.path[:] = path


def _run_all(only):
    names = [n for n in globals() if n.startswith('check_')]
    try:
        for n in names:
            if not only or n in only:
                try:
                    _run_one(n)
                except FileNotFoundError as exc:
                    # A few cases also hold Promote to BestPractice's own
                    # workflow templates, which only BestPractice has: beside
                    # any other engine they cannot run, and say so.
                    missing = pathlib.Path(exc.filename or '')
                    if not str(missing).startswith(str(ROOT)):
                        raise
                    not_applicable(n, f'{missing.relative_to(ROOT)} is not '
                                      f'here; it is BestPractice\'s own, so this '
                                      f'runs beside BestPractice\'s engine')
    finally:
        shutil.rmtree(_ASM, ignore_errors=True)
    print(f'ladder_branches: {len(PASSED)} passed, {len(FAILED)} failed, '
          f'{len(NA)} not applicable')
    for name, why in NA:
        print(f'  N/A: {name} -- {why}')
    return 1 if FAILED else 0


if __name__ == '__main__':
    sys.exit(_run_all(sys.argv[1:]))
