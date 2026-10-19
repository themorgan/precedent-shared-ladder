#!/usr/bin/env python3
"""The ladder's own moves: Promote, Produce, and the wait on main's GitHub test after a Produce; this set's branch_moves, which BestPractice's engine hands `--promote` and `--wait-main-test`

Shipped as tools/ladder/ladder_branches.py by this set's promote practice
and named `branch_moves` in its precedent-source.json, which is how the
engine finds it (precedent_resolve.set_tool). It moved here from
BestPractice's tools/precedent_branches.py on 2026-10-19 (BestPractice
spec/ENFORCEMENT_LIVES_WITH_ITS_PRACTICE_PLAN.md, piece 5b; Morgan: "Let's
do 5b and 5c", strength: decided).

BUILT ON THE ENGINE CORE. Landing, the lock, composing a merge in a
worktree, the checks and pushing stay in the engine, which every
repository needs; this file only decides the moves up the ladder and calls
the engine for the rest, as `core.<name>`. The engine binds itself before
calling (bind), so this file always runs against the engine that called
it, never a second copy.

The engine's `python3 tools/precedent_branches.py --promote ...` and
`--wait-main-test ...` hand their arguments to main() here unchanged, so
every instruction that names those commands keeps working.
"""
import json
import sys
import time

core = None


def bind(engine):
    """Use `engine` (BestPractice's precedent_branches, as loaded by the
    caller) for everything this file does not decide itself."""
    global core
    core = engine


def main(root, argv):
    """-> the exit status for `--promote ...` or `--wait-main-test X`, the
    arguments exactly as the engine's command line received them."""
    if argv[:1] == ['--promote']:
        kw = promote_args(argv[1:])
        if kw is None:
            print('usage: precedent_branches.py --promote [--to main] '
                  '[--work BRANCH-OR-COMMIT] [--full --because \'<their words>\' '
                  '| [--despite-failed-tests] [--no-full-after]]  (the move into '
                  'main is the fast one unless the person asks for --full)',
                  file=sys.stderr)
            return 2
        refused = full_route_refusal(kw)
        if refused:
            print(refused, file=sys.stderr)
            return 2
        because = kw.pop('because')
        if because:
            print(f'the full route into {core.MAIN}, because the person asked: '
                  f'{because.strip()!r}', flush=True)
        return promote(root, **kw)
    if argv[:1] == ['--wait-main-test'] and len(argv) == 2:
        sha, copy = core.resolve_main_test_target(root, argv[1])
        if not sha:
            print(f'precedent_branches: {argv[1]} names no pull request, branch or '
                  f'commit here.', file=sys.stderr)
            return 2
        return wait_for_main_test(root, sha, copy=copy)
    print(f'ladder_branches: no move named {" ".join(argv)!r}', file=sys.stderr)
    return 2


# ONE DEFINITION OF A CURRENT COPY FOR MAIN (2026-10-08). Since 2026-10-07
# Produce's copy is staging merged with main, so main's push test can skip
# what the pull request already passed. The merge check went on allowing a
# head into main only at staging's own tip, so it refused every such copy
# as "out of date: staging has moved" while staging had not moved -- every
# Produce, in every repository on that engine, found by a consumer on
# 2026-10-08. Promote now makes its copy with this function's rule and the
# merge check judges it by the same function, so the two cannot drift
# apart again.
def main_copy_tip(root, mtip, stip, message):
    """-> the commit Produce's copy should be, given main's tip `mtip` and
    staging's `stip`, made and checked out in `root` (a worktree at mtip),
    or None when staging does not merge cleanly into main. Staging's own tip
    when main is already in staging: GitHub's merge of it then has no
    parent the tested head lacks. Otherwise staging merged into main, which
    contains both."""
    if core._run(root, 'merge-base', '--is-ancestor', mtip, stip).returncode == 0:
        core._run(root, 'checkout', '-q', '--detach', stip)
        return stip
    m = core._run(root, 'merge', '--no-ff', '-q', '-m', message, stip,
             env=core._merge_env(root))
    if m.returncode != 0:
        core._run(root, 'merge', '--abort')
        return None
    return core._run(root, 'rev-parse', 'HEAD').stdout.strip()


# A pull request's run shows up on GitHub within a minute or two of the
# pull request opening. One that has not appeared by this long is never
# going to, and waiting the full half hour for it would only hide that.
GITHUB_START_WAIT_SECONDS = 5 * 60


def wait_for_main_test(root, sha, say=print, gh=None, copy=None):
    """Wait for main's GitHub test on `sha` -- the to-main copy's tip, once
    its pull request into main is open -- and -> 0 passed, 1 anything else.

    The last step of a Promote into main is "wait for its GitHub test, then
    merge", and until 2026-09-27 nothing here did the waiting, so each
    session wrote its own poller; one crashed mid-wait that day on a Python
    version quirk and was read by eye instead. This is that wait, once:
    `--wait-main-test COPY` after opening the pull request. A run that has
    not appeared within GITHUB_START_WAIT_SECONDS is reported as never
    started rather than waited on for the full half hour."""
    tests = core.github_tests(root, sha)
    if not tests:
        say(f'no GitHub test is installed here, so there is nothing to wait for '
            f'on {sha[:12]}: the full local check at the Promote was the whole check.')
        return 0
    if copy and is_not_due_copy(copy):
        say(f'GitHub test NOT DUE on {sha[:12]}: Promote named this copy {copy} '
            f'because main\'s GitHub test is not due on its pull request (the '
            f'Promote printed why), so the pull request shows the test as skipped '
            f'and no runner started. The full local check at the Promote stands; '
            f'in a repo set to github_ci_main_test "always", GitHub tests the push '
            f'to {core.MAIN} once this merges. Merge the pull request into {core.MAIN} with '
            f'a merge commit{core._at_head(sha)}.')
        return 0
    say(f'waiting for the GitHub test on {sha[:12]} (up to '
        f'{core.GITHUB_TEST_WAIT_SECONDS // 60} minutes): ' + ', '.join(p for p, _ in tests))
    t0 = time.monotonic()
    state, detail = core.github_test_state(root, sha, tests, gh)
    while state in ('running', 'none'):
        waited = time.monotonic() - t0
        if waited >= core.GITHUB_TEST_WAIT_SECONDS or (
                state == 'none' and waited >= GITHUB_START_WAIT_SECONDS):
            break
        time.sleep(core.GITHUB_POLL_SECONDS)
        state, detail = core.github_test_state(root, sha, tests, gh)
    # A fast move merges first and waits after, so by now main may already
    # carry the commit (2026-10-10: a passed test still said "Merge the pull
    # request" twice, over a pull request merged half an hour before).
    merged = _on_main_already(root, sha)
    if state == 'passed':
        if merged:
            say(f'GitHub test PASSED on {sha[:12]}: {detail}. {core.MAIN} already '
                f'carries it -- the pull request is merged; nothing is left to do.')
        else:
            say(f'GitHub test PASSED on {sha[:12]}: {detail}. Merge the pull request '
                f'into {core.MAIN} with a merge commit{core._at_head(sha)}.')
        return 0
    if merged:
        say(f'GitHub test {state.upper()} on {sha[:12]}: {detail}. {core.MAIN} already '
            f'carries it, so fix {core.MAIN} now, straight into it: cut a branch '
            f'from {core.MAIN}\'s tip named by `python3 tools/precedent_branch_name.py '
            f'fix main WORDS`, open its pull request into {core.MAIN} (red_main_fix '
            f'lets that one through), then land the same branch on '
            f'{core.staging_branch(root)} (`{core.LAND_COMMAND} BRANCH`).')
    else:
        say(f'GitHub test {state.upper()} on {sha[:12]}: {detail}. Do not merge.')
    return 1


def _on_main_already(root, sha):
    """-> True when origin's main already holds `sha` (after a fresh fetch).
    False when it does not, or git cannot say."""
    core._run(root, 'fetch', '-q', 'origin', core.MAIN)
    return core._run(root, 'merge-base', '--is-ancestor', sha,
                f'origin/{core.MAIN}').returncode == 0


def promotion_step(root, to=None, work=None):
    """-> (step, why): which Promote to run -- MAIN (staging into main) or
    None (nothing waiting, or nothing a Promote may do here).

    Work reaches staging by Booked (--land); a Promote only moves staging
    into main (Morgan, 2026-10-17, strength: decided). Asked for a step
    into staging, it says so and moves nothing. `work`, the branch the session was just on, still decides:
    not on staging yet means it must be Booked first."""
    staging = core.staging_branch(root)
    if staging == core.MAIN:
        return None, f'{core.MAIN} is the staging tier here, so work lands there directly'
    if to == core.STAGING:
        return None, (f'there is no step into {staging} any more: work reaches '
                      f'{staging} by Booked (--land), and a Promote moves '
                      f'{staging} into {core.MAIN}')
    core._run(root, 'fetch', '-q', 'origin', staging, core.MAIN)
    stip, mtip = core._remote_tip(root, staging), core._remote_tip(root, core.MAIN)
    if work:
        core._run(root, 'fetch', '-q', 'origin', work)
        sha = core._git(root, 'rev-parse', '--verify', '--quiet', f'{work}^{{commit}}') \
            or core._git(root, 'rev-parse', '--verify', '--quiet', f'origin/{work}^{{commit}}')
        if not sha:
            return None, (f'{work!r} is not a branch or commit this checkout can '
                          f'see, so nothing was chosen from it')
        if not (stip and core._run(root, 'merge-base', '--is-ancestor', sha,
                              stip).returncode == 0):
            return None, (f'the work just done ({work}) is not on {staging} yet: '
                          f'Book it there first (--land), then Promote')
    if to == core.MAIN or (stip and mtip and core._new_commits(root, mtip, stip)):
        return core.MAIN, ('asked for by name (--to main)' if to == core.MAIN else
                      f'{staging} has work {core.MAIN} lacks')
    if not mtip:
        return None, f'origin has no {core.MAIN}'
    return None, f'{staging} and {core.MAIN} carry the same work'


# What the run that is under way decided, for promote_result_line: set by
# _verdict at the point each path knows it, read once the run is over.
_RESULT = {}


def _verdict(text, move=None):
    """Record this Promote's verdict, one line, for its closing result line."""
    _RESULT['verdict'] = ' '.join(str(text).split())
    if move:
        _RESULT['move'] = move


# A failure never carries its success word (2026-10-11: a script searching
# "LANDED" read "NOT LANDED" as a landing): LAND REFUSED and PROMOTE REFUSED,
# never NOT LANDED or NOT PROMOTED. The old prefix stays readable here.
_REASON_PREFIXES = ('PROMOTE REFUSED: ', 'NOT PROMOTED: ', 'PROMOTE NOT FINISHED, ')


def promote_result_line(root, rc, to=None, last=''):
    """-> the single line a Promote ends on: which move, and what became of
    it. `rc` is the run's exit status (None when an error stopped it) and
    `last` the last thing it said, the reason when no path recorded one."""
    try:
        staging = core.staging_branch(root)
    except Exception:
        staging = core.STAGING
    move = _RESULT.get('move') or (
        f'{core.MAIN} <- {staging}')
    verdict = _RESULT.get('verdict')
    if not verdict:
        reason = ' '.join((str(last or '').strip().splitlines() or [''])[0].split())
        for prefix in _REASON_PREFIXES:
            if reason.startswith(prefix):
                reason = reason[len(prefix):]
        reason = reason[:240] or 'see the lines above'
        if rc is None:
            verdict = f'PROMOTE REFUSED: the run stopped on an error ({reason})'
        elif rc == 0:
            verdict = f'NOTHING TO PROMOTE: {reason}'
        else:
            verdict = f'PROMOTE REFUSED: {reason}'
    return f'PROMOTE RESULT: {move}: {verdict}'


def promote(root, say=print, to=None, work=None, fast=False,
            despite_failed_tests=False, no_full_after=False):
    """Run a Promote (_promote_run) and end it, on every path -- an error and
    a refusal included -- with promote_result_line as the last thing said.
    `fast` and `despite_failed_tests` are the fast move into main's
    (_promote_to_main). -> _promote_run's exit status."""
    _RESULT.clear()
    last = ['']

    def heard(msg=''):
        last[0] = msg
        say(msg)
    rc = None
    try:
        rc = _promote_run(root, heard, to, work, fast, despite_failed_tests,
                          no_full_after)
        return rc
    finally:
        say(promote_result_line(root, rc, to, last[0]))
        _RESULT.clear()


def _promote_run(root, say=print, to=None, work=None, fast=False,
                 despite_failed_tests=False, no_full_after=False):
    """Pick the step (promotion_step), SAY it, then run it, one window at a
    time. -> 0 promoted, nothing to promote, or another window already
    promoting; 1 refused (a failing check, a conflict, a race);
    PROMOTE_MAIN_NOT_MOVED when staging into main is ready for its pull
    request and main has not moved yet."""
    if not core.repo_has_tiers(root) and not core._git(
            root, 'rev-parse', '--verify', '--quiet',
            f'refs/remotes/origin/{core.staging_branch(root)}'):
        # Nothing ever creates tiers in a repository that did not ask for
        # them (spec/LADDER_OPT_IN_PLAN.md, Morgan 2026-10-02: "Yes"). Before
        # this, a Promote here announced a move, failed on the missing
        # staging branch, and left its lock branch behind on origin.
        say(f'this repository has only {core.MAIN}, and work lands there '
            f'directly, so there is nothing to promote.')
        _verdict(f'NOTHING TO PROMOTE: this repository has only {core.MAIN}')
        return 0
    step, why = promotion_step(root, to, work)
    staging = core.staging_branch(root)
    if step is None:
        say(f'nothing to promote: {why}.')
        _verdict(f'NOTHING TO PROMOTE: {why}')
        return 0
    # The one line a person reads first: which move this is, in these words.
    say(f'Now promoting from {staging} to {core.MAIN} ({why}).')
    run = _promote_to_main
    kw = {'work': work} if work else {}
    if fast and run is _promote_to_main:
        kw.update(fast=True, despite_failed_tests=despite_failed_tests,
                  no_full_after=no_full_after)
    if kw:
        run = (lambda r, s, f=run, kw=kw: f(r, s, **kw))
    state, info = core._lock_claim(root, say)
    if state == 'busy':
        say(f'another window is promoting or landing right now ({info}), so this one did '
            f'nothing. Do not Promote again while it runs.')
        _verdict(f'PROMOTE REFUSED: another window is promoting or landing right now ({info}); '
                 f'do not Promote again while it runs')
        return 0
    if state == 'none':
        say(f'NOTE: could not take the Promote lock ({info}); going ahead '
            f'without it.')
        return run(root, say)
    old_handlers = core._exit_cleanly_on_signal()
    try:
        return run(root, say)
    finally:
        core._ignore_signals(old_handlers)
        try:
            core._lock_release(root, info, say)
        finally:
            core._restore_signals(old_handlers)


def is_not_due_copy(name):
    """True for a copy whose pull request main's GitHub test skips."""
    return str(name or '').startswith(core.NOT_DUE_PREFIX) or \
        core._promote_made(name) == core.NOT_DUE_SLUG


def _workflows_know_new_copy_names(root):
    """True when every GitHub test at staging's tip recognizes the new copy
    names, or does not look at copy names at all (or none is installed). A
    repository that has not taken the workflow carrying them would run its
    test on a not-due copy, so its copies keep the old names until Update
    Vendors brings it. A workflow that never names a copy (BestPractice's
    own deep check runs on every pull request into main) is indifferent, so
    it no longer holds the copies to the old names (Morgan, 2026-10-09:
    "those should be aligned with the format I like: 2026-12-31-slug-abcdef")."""
    tip = core._remote_tip(root, core.staging_branch(root))
    if not tip:
        return False

    def knows(p):
        body = core._git(root, 'show', f'{tip}:{p}') or ''
        return core.COPY_NAME_MARKER in body or 'to-main-' not in body
    return all(knows(p) for p, _d in core.github_tests(root, tip))


def _to_main_copy(root, due=True):
    """The throwaway branch a pull request into main comes FROM: never
    staging itself, whose pull request page offers to delete it (gotchas/
    gotcha-2026-09-26-a-pull-request-from-staging-deletes-staging.md). Named
    as precedent_merge_check.py's refusal names it, with a suffix when that
    name is taken -- and the not-due name instead when main's GitHub test is
    not due, which is the name the light check's job skips on. In the
    session-branch format (promote_branch_name), unless a GitHub test here
    still knows only the old names."""
    if _workflows_know_new_copy_names(root):
        name = core.promote_branch_name(root, core.COPY_SLUG if due else core.NOT_DUE_SLUG,
                                   lambda n: bool(core._remote_tip(root, n)))
        if name:
            return name
    day, moment = core._day_and_moment(root)
    prefix = 'to-main-' if due else core.NOT_DUE_PREFIX
    base = f'{prefix}{day}'
    if not core._remote_tip(root, base):
        return base
    # The moment is a second: two Promotes in one second named the same
    # copy and the second push was refused as non-fast-forward (2026-10-19:
    # "the work just done, on staging, goes into main" failed only on
    # GitHub's faster runner, run 39259090526). Count up until one is free.
    name, n = f'{prefix}{moment}', 1
    while core._remote_tip(root, name):
        n += 1
        name = f'{prefix}{moment}-{n}'
    return name


# Exit 0 from a Promote means the branch it names has moved. Into main it
# stops short -- the pull request, its GitHub test and the merge are the
# session's -- and until 2026-09-28 it still exited 0 there: a session read
# the 0 as done while main had not moved. That state has its own code now,
# distinct from a refusal (1) and a usage error (2).
PROMOTE_MAIN_NOT_MOVED = 3


def _carries_changes_of(root, tip, other):
    """True when `tip` already has every file change `other` brings: merging
    `other` into `tip` would leave `tip`'s tree as it is. A Produce's own
    merge commit on main is the common case -- it changes no file, so a
    Debut has nothing to take down and never makes staging its descendant.
    Until 2026-10-05 main_test_holds_produce asked for ancestry alone, so a
    main whose GitHub test went red without running (no runner) held every
    Produce while telling the session to Debut, and the Debut had nothing to
    do. Needs `git merge-tree --write-tree` (git 2.38); where that is
    missing, or the merge conflicts, this answers False, the old reading."""
    r = core._run(root, 'merge-tree', '--write-tree', tip, other)
    if r.returncode != 0:
        return False
    merged = r.stdout.split('\n', 1)[0].strip()
    return bool(merged) and merged == core._git(root, 'rev-parse', f'{tip}^{{tree}}')


def main_test_holds_produce(root, say=print, gh=None):
    """-> None when a move into main may go ahead, else why not. Main's
    GitHub test on its own tip: failing holds it, still running is waited
    for (spec/LADDER_OPT_IN_PLAN.md D10, Morgan 2026-10-02, strength:
    decided: "Produce waits until main's test passes"). No test installed,
    none on this tip, or one GitHub cannot be asked about holds nothing:
    the pull request's own test is still the last gate."""
    if not core._gets_github_test(root, core.MAIN):
        return None
    mtip = core._remote_tip(root, core.MAIN)
    tests = core.github_tests(root, mtip) if mtip else []
    if not tests:
        return None
    state, detail = core.github_test_state(root, mtip, tests, gh)
    if state == 'running':
        say(f'the GitHub test on {core.MAIN} ({mtip[:12]}) is still running; a move '
            f'into {core.MAIN} waits for it...')
        deadline = time.monotonic() + core.GITHUB_TEST_WAIT_SECONDS
        while state == 'running' and time.monotonic() < deadline:
            time.sleep(core.GITHUB_POLL_SECONDS)
            state, detail = core.github_test_state(root, mtip, tests, gh)
    if state == 'failed':
        # Staging already carries main's tip: this Produce is what repairs
        # main, and its own pull request's GitHub test is the last gate.
        # Holding it waited for a fix from someone off the ladder, who does
        # not make one (Morgan, 2026-10-03, strength: decided; narrows D10).
        staging = core.staging_branch(root)
        core._run(root, 'fetch', '-q', 'origin', staging)
        stip = core._remote_tip(root, staging)
        carried = bool(stip) and (
            core._run(root, 'merge-base', '--is-ancestor', mtip, stip).returncode == 0
            or _carries_changes_of(root, stip, mtip))
        # ...checked first, never taken on trust: carrying main's commit says
        # nothing about whether the tree it makes with the ladder's work
        # passes, so the hold lifts only for a staging tip whose exact tree
        # has passed the full local check (Morgan, 2026-10-03: "Should it
        # check this first?"). The pull request's GitHub test is still the
        # last gate before the merge.
        if carried and core._receipt(root, stip):
            say(f'{core.MAIN}\'s own GitHub test is failing on its tip ({mtip[:12]}: '
                f'{detail}). {staging} already carries that commit, and its tip '
                f'({stip[:12]}) has passed the full local check, so this Produce '
                f'goes ahead: it is what brings {core.MAIN} back to green, and its pull '
                f'request\'s own GitHub test is the last gate.')
            return None
        if carried:
            return (f'{core.MAIN}\'s own GitHub test is failing on its tip ({mtip[:12]}: '
                    f'{detail}). {staging} carries that commit, but its tip '
                    f'({stip[:12]}) has no full local check on record, so it is '
                    f'not known to repair {core.MAIN}. Debut first: its full check '
                    f'judges that tree, then Produce again.')
        return (f'{core.MAIN}\'s own GitHub test is failing on its tip ({mtip[:12]}: '
                f'{detail}), and {staging} does not carry that commit yet. Debut '
                f'first: the Promote takes {core.MAIN}\'s work down and checks it with '
                f'yours, then Produce again.')
    if state == 'running':
        return (f'{core.MAIN}\'s GitHub test on {mtip[:12]} was still running after '
                f'{core.GITHUB_TEST_WAIT_SECONDS // 60} minutes ({detail}); Promote '
                f'again once it finishes.')
    return None


def _promote_to_main(root, say=print, work=None, fast=False,
                     despite_failed_tests=False, no_full_after=False):
    """Staging into main: the full check on exactly what main would hold,
    then a throwaway copy of staging for the pull request into main, whose
    GitHub test is the last gate (spec/BRANCH_TIERS_PLAN.md: main gets "all
    those local tests AND the most important GitHub test"). Main is moved by
    that pull request, never by this script. -> PROMOTE_MAIN_NOT_MOVED when
    the copy is ready and main has not moved yet; 0 nothing to promote; 1
    refused. `fast` is _promote_to_main_fast instead."""
    if fast:
        return _promote_to_main_fast(root, say, work, despite_failed_tests,
                                     no_full_after)
    staging = core.staging_branch(root)
    held = main_test_holds_produce(root, say)
    if held:
        say(f'PROMOTE REFUSED: {held}')
        return 1
    core._run(root, 'fetch', '-q', 'origin', staging, core.MAIN)
    stip, mtip = core._remote_tip(root, staging), core._remote_tip(root, core.MAIN)
    if not stip or not mtip:
        say(f'origin lacks {staging if not stip else core.MAIN}, so there is nothing '
            f'to promote into {core.MAIN}.')
        return 1
    batch = core._new_commits(root, mtip, stip)
    if not batch:
        say(f'nothing to promote: {core.MAIN} already has everything on {staging}.')
        _verdict(f'NOTHING TO PROMOTE: {core.MAIN} already has everything on '
                 f'{staging} ({stip})', move=f'{core.MAIN} <- {staging}')
        return 0
    with core._Worktree(root, mtip) as wt:
        copy_tip = main_copy_tip(
            wt, mtip, stip,
            f'Promote {staging} into {core.MAIN} ({len(batch)} commit(s))')
        if not copy_tip:
            say(f'{staging} does not merge cleanly into {core.MAIN}; nothing was pushed. '
                f'{core.MAIN} has changes of its own on the same lines -- merge {core.MAIN} '
                f'into a branch, resolve it there, land it on {staging} '
                f'(`{core.LAND_COMMAND} BRANCH`), and Promote again.')
            return 1
        # THE COPY IS THIS MERGE, NOT STAGING'S TIP (2026-10-07). Pushed as
        # staging's tip, the pull request's merge into main had main's last
        # commit as a parent the tested head did not contain -- after any
        # earlier Produce, GitHub's own merge commit -- so the push test on
        # main could not tell it had just passed, re-ran the whole suite
        # (30 minutes that night) and the next Produce waited on it
        # (todo-2026-10-07-main-push-test-reruns-a-tree-its-pull-request-passed).
        # This commit contains main, is exactly what the full check below
        # judges, and is what the pull request's GitHub test then runs.
        # Where main is already in staging it is staging's tip itself, and
        # main_copy_current is what the merge check accepts (2026-10-08).
        say(f'checking {len(batch)} commit(s) from {staging} with the full push check...')
        t0 = time.monotonic()
        ok, out = core._check(root, wt, core.FULL, dest=core.MAIN)
        if ok:
            # What GitHub's test of the pull request into main will judge
            # against main, judged here first (a few seconds; 2026-10-17).
            against = core._against_main(root, wt, staging, mtip, say)
            if against:
                ok = False
                out += '\n' + '\n'.join(f'  {f["check"]}: {f["line"]}'
                                         for f in against)
        took = time.monotonic() - t0
    review = core._upstream_review(root, None, 'produce', out, f'{mtip}..{stip}')[0] \
        if ok else []
    if not ok:
        say(f'PROMOTE REFUSED: the full check failed on {staging} merged into '
            f'{core.MAIN}, so nothing was pushed. The batch was:\n  '
            + '\n  '.join(batch) + f'\n\n{out}\n\nFix it on a branch, land it on '
            f'{staging} (`{core.LAND_COMMAND} BRANCH`), and Promote again.')
        return 1
    reused = next((l for l in out.splitlines() if 'already passed' in l), None)
    if reused:
        say('the full check was NOT re-run: ' + reused.split(': ', 1)[-1]
            + ' Same files, so the earlier run stands.')
    else:
        say(f'the full check ran on the batch and passed, in {took:.0f}s.')
    due, why = core.main_test_due(root, stip)
    # No GitHub test runs on this pull request at all -- none is installed,
    # or every one is path-filtered off this change. "DUE", then "wait for
    # it", read as a test to wait on where none would ever start (2026-10-04,
    # all four shared sets and a consumer); --wait-main-test said the same.
    none_runs = not core.github_tests(root, stip)
    copy = _to_main_copy(root, due)
    p = core._run(root, 'push', '-q', 'origin', f'{copy_tip}:refs/heads/{copy}')
    if p.returncode != 0:
        say(f'could not push the copy {copy}: {p.stderr.strip()[:200]}')
        return 1
    shown, others = core.mark_other_work(root, batch, work)
    say(f'{core.MAIN.upper()} HAS NOT MOVED YET: this Promote exits '
        f'{PROMOTE_MAIN_NOT_MOVED}, not 0, until the pull request below is merged.\n'
        f'READY FOR {core.MAIN.upper()}: {len(batch)} commit(s) from {staging} '
        f'({stip[:12]}), '
        + ('which already contains ' + core.MAIN if copy_tip == stip else
           f'merged with {core.MAIN} as {copy_tip[:12]}')
        + f' and pushed as {copy}:\n  ' + '\n  '.join(shown)
        + core._other_work_note(others, work) + '\n\n'
        + (f'GitHub test: NONE -- no GitHub test runs on this pull request '
           f'(none is installed here, or its path filter does not reach this '
           f'change), so the full local check above is the whole check.\n\n'
           if none_runs else
           f'GitHub test: DUE -- {why}.\n\n' if due else
           f'GitHub test: ON THE PUSH TO {core.MAIN.upper()} -- {why}. Its pull request '
           f'shows the test as skipped, which starts no runner and costs nothing.\n\n'
           if 'never the pull request' in why else
           f'GitHub test: NOT DUE -- {why}. Its pull request shows the test as '
           f'skipped, which starts no runner and costs nothing.\n\n') +
        f'Next, and not by this script: open a pull request from {copy} into '
        f'{core.MAIN}, titled "Promote {staging} into {core.MAIN} ({len(batch)} '
        f'commit(s))", '
        + (f'and merge it with a merge commit{core._at_head(copy_tip)}' if none_runs else
           f'wait for its GitHub test with\n'
           f'  python3 tools/precedent_branches.py --wait-main-test {copy}\n'
           f'and merge it with a merge commit once that says PASSED'
           + ('' if due else ' (or, for this not-due copy, NOT DUE)')
           + core._at_head(copy_tip)) +
        f'. Never open it from {staging} itself.')
    _verdict(f'READY FOR {core.MAIN.upper()}: open a pull request from {copy} into '
             f'{core.MAIN}, then merge with expectedHeadSha {copy_tip}'
             + ('' if none_runs else ' once its GitHub test says PASSED'
                + ('' if due else ' (or NOT DUE)'))
             + f'; {core.MAIN} has not moved yet', move=f'{core.MAIN} <- {staging}')
    for line in review:
        say(line)
    return PROMOTE_MAIN_NOT_MOVED


# THE FAST MOVE INTO MAIN (2026-10-09, the approved plan that makes the
# move into main fast for whoever asks for it; the default since
# 2026-10-11, promote_args). The full local suite is not run: it is --run-tests, asked
# for when wanted. This runs the quick checks on the change, builds the copy
# for the pull request exactly as the full move does (main_copy_tip: staging
# merged into main, so nothing that reached main directly is dropped), and
# says to merge it at once. GitHub's test still runs -- after the merge --
# and --wait-main-test waits on it.
#
# A FAILED --run-tests ON THIS VERY COMMIT ASKS, NEVER REFUSES (Morgan,
# 2026-10-09: "often these tests fail for trivial reasons, and sometimes I
# really just need to push something to live quickly"). It prints each
# failing check on a line and exits PROMOTE_ASKS; --despite-failed-tests is
# the person's yes. A failure recorded on an older commit says so, as stale,
# and does not ask.
#
# The merge gate reads FAST_MAIN_RECORD to know this copy took the quick
# checks on purpose: it checks the merge at the quick tier, before and after,
# instead of running the full suite the move skipped.
PROMOTE_ASKS = 4


DESPITE_FLAG = '--despite-failed-tests'


FAST_MAIN_KEPT = 20


def _record_fast_main(root, sha, entry):
    path = core._fast_main_path(root)
    if not path:
        return
    data = core._read_json(path) or {}
    data[sha] = entry
    for old in sorted(data, key=lambda k: str(data[k].get('at', '')))[:-FAST_MAIN_KEPT]:
        data.pop(old, None)
    try:
        path.write_text(json.dumps(data, indent=2) + '\n', encoding='utf-8')
    except OSError:
        pass


def failed_tests_ask(root, branch, tip):
    """-> (asks, lines): what the last --run-tests on `branch` says about its
    tip `tip`. `asks` is True only when it FAILED on exactly that commit;
    `lines` is what to print -- the failures, or a stale or passing note."""
    rec = core.run_tests_record(root, branch)
    if not rec:
        return False, [f'no --run-tests result is on record here for {branch}.']
    when = rec.get('at', 'time not recorded')
    if rec.get('commit') != tip:
        state = 'failed' if rec.get('result') == 'failed' else 'passed'
        return False, [f'the last --run-tests on {branch} {state} on an older '
                       f'commit ({str(rec.get("commit"))[:12]}, {when}); it is '
                       f'STALE -- {branch} is at {tip[:12]} now -- so it decides '
                       f'nothing here.']
    if rec.get('result') == 'running':
        return False, [f'--run-tests is still running on this commit, or was '
                       f'stopped before it finished ({tip[:12]}, started {when}); '
                       f'it has passed nothing yet.']
    if rec.get('result') != 'failed':
        return False, [f'--run-tests PASSED on this commit ({tip[:12]}, {when}).']
    failed = rec.get('failed') or []
    return True, ([f'--run-tests FAILED on this commit ({tip[:12]}, {when}), '
                   f'{len(failed)} failing check(s):']
                  + [f'  {f.get("check")}: {f.get("line") or "(no detail)"}'
                     for f in failed])


NO_FULL_AFTER_FLAG = '--no-full-after'


def mark_main_unchecked(root, sha):
    """Record on origin that main moved without a full check, at `sha`, the
    first such move: one ref, kept until a full run clears it, so a run of
    fast moves is seen from any session, not only this container's."""
    if core._git(root, 'ls-remote', 'origin', core.UNCHECKED_REF):
        return
    core._run(root, 'push', '-q', 'origin', f'{sha}:{core.UNCHECKED_REF}')


def _main_test_note(root):
    """One look, never a wait, at main's own GitHub test: a line to say when
    it is failing or still running, else ''."""
    try:
        mtip = core._remote_tip(root, core.MAIN)
        tests = core.github_tests(root, mtip) if mtip and core._gets_github_test(root, core.MAIN) else []
        if not tests:
            return ''
        state, detail = core.github_test_state(root, mtip, tests)
    except Exception:                                       # noqa: BLE001
        return ''
    if state in ('failed', 'running'):
        return (f'NOTE: {core.MAIN}\'s own GitHub test is {state} on its tip '
                f'({mtip[:12]}: {detail}). This move does not wait on it.')
    return ''


def _promote_to_main_fast(root, say=print, work=None, despite_failed_tests=False,
                          no_full_after=False):
    """The fast move into main: quick checks, the copy, the merge
    instruction, and GitHub's test after the merge. -> PROMOTE_MAIN_NOT_MOVED
    when the copy is ready; PROMOTE_ASKS when --run-tests failed on this
    commit and the person has not said to go on; 0 nothing to promote; 1
    refused."""
    staging = core.staging_branch(root)
    move = f'{core.MAIN} <- {staging}'
    core._run(root, 'fetch', '-q', 'origin', staging, core.MAIN)
    stip, mtip = core._remote_tip(root, staging), core._remote_tip(root, core.MAIN)
    if not stip or not mtip:
        say(f'origin lacks {staging if not stip else core.MAIN}, so there is nothing '
            f'to promote into {core.MAIN}.')
        return 1
    batch = core._new_commits(root, mtip, stip)
    if not batch:
        say(f'nothing to promote: {core.MAIN} already has everything on {staging}.')
        _verdict(f'NOTHING TO PROMOTE: {core.MAIN} already has everything on '
                 f'{staging} ({stip})', move=move)
        return 0
    asks, lines = failed_tests_ask(root, staging, stip)
    if asks and not despite_failed_tests:
        say('\n'.join(lines))
        say(f'ASK THE PERSON, in these words: "Run tests found {len(lines) - 1} '
            f'failure(s) on {staging} (above). GitHub runs the same tests after '
            f'the merge, so a real one turns {core.MAIN} red until it is fixed. Run the '
            f'move anyway? Say yes to continue." On a yes, run this again with '
            f'{DESPITE_FLAG}. Nothing was pushed.')
        _verdict(f'ASKING: --run-tests failed on {staging} at {stip}; ask the '
                 f'person "Run the move anyway? Say yes to continue", and on a '
                 f'yes run again with {DESPITE_FLAG}; nothing was pushed',
                 move=move)
        return PROMOTE_ASKS
    for line in lines:
        say(line)
    if asks:
        say(f'going ahead anyway, as the person said ({DESPITE_FLAG}).')
    note = _main_test_note(root)
    if note:
        say(note)
    with core._Worktree(root, mtip) as wt:
        copy_tip = main_copy_tip(
            wt, mtip, stip,
            f'Promote {staging} into {core.MAIN} ({len(batch)} commit(s))')
        if not copy_tip:
            say(f'{staging} does not merge cleanly into {core.MAIN}; nothing was pushed. '
                f'{core.MAIN} has changes of its own on the same lines -- merge '
                f'origin/{core.MAIN} into your branch, resolve it there, land it on '
                f'{staging}, and promote again.')
            return 1
        say(f'checking {len(batch)} commit(s) from {staging} with the quick '
            f'checks -- the full local suite is not run on a fast move...')
        t0 = time.monotonic()
        ok, out = core._check(root, wt, core.BASIC, dest=core.MAIN, since=mtip)
        if ok:
            # What GitHub's test of the pull request into main will judge
            # against main, judged here first (a few seconds; 2026-10-17).
            against = core._against_main(root, wt, staging, mtip, say)
            if against:
                ok = False
                out += '\n' + '\n'.join(f'  {f["check"]}: {f["line"]}'
                                         for f in against)
        took = time.monotonic() - t0
    review = core._upstream_review(root, None, 'produce', out, f'{mtip}..{stip}')[0] \
        if ok else []
    if not ok:
        say(f'PROMOTE REFUSED: the quick checks failed on {staging} merged into '
            f'{core.MAIN}, so nothing was pushed.\n\n{out}\n\nFix it, land the fix on '
            f'{staging}, and promote again.')
        return 1
    say(f'the quick checks passed, in {took:.0f}s.')
    due, _why = core.main_test_due(root, stip)
    none_runs = not core.github_tests(root, stip)
    copy = _to_main_copy(root, due)
    p = core._run(root, 'push', '-q', 'origin', f'{copy_tip}:refs/heads/{copy}')
    if p.returncode != 0:
        say(f'could not push the copy {copy}: {p.stderr.strip()[:200]}')
        return 1
    shown, others = core.mark_other_work(root, batch, work)
    wait = (f'python3 tools/precedent_branches.py --wait-main-test {copy}')
    # A private repository tests main at most every N hours, and some have
    # no GitHub test at all: then the full suite runs here after the merge,
    # unless one of Morgan's other conditions says it is not needed
    # (full_check_after; 2026-10-09: "I want to make sure there's a full
    # check *somewhere* on the push to main, afterwards").
    test_runs = not none_runs and bool(due)
    skipped = not test_runs
    full_after, full_why = core.full_check_after(root, test_runs, stip, mtip,
                                            asked_fast=no_full_after)
    if skipped and no_full_after and not full_after and 'asked for a fast' in full_why:
        mark_main_unchecked(root, copy_tip)
    gh_line = ('no GitHub test runs here' if none_runs else
               f'GitHub\'s test is not due on this one ({_why})')
    after = (f'{gh_line}, so the full suite runs here instead, after the '
             f'merge: python3 tools/precedent_branches.py --run-tests {core.MAIN}, in '
             f'the background, and fix {core.MAIN} at once if it fails'
             if full_after else
             f'{gh_line}, and no full check is needed after it: {full_why}'
             if skipped else
             f'GitHub\'s test runs after the merge; wait on it with {wait} and '
             f'fix {core.MAIN} at once if it fails')
    _record_fast_main(root, copy_tip, {
        'copy': copy, 'staging': stip, 'main': mtip,
        'despite_failed_tests': bool(asks),
        'full_after': bool(full_after), 'full_after_why': full_why,
        'at': time.strftime('%Y-%m-%dT%H:%M:%S%z')})
    say(f'{core.MAIN.upper()} HAS NOT MOVED YET: this Promote exits '
        f'{PROMOTE_MAIN_NOT_MOVED}, not 0, until the pull request below is merged.\n'
        f'READY FOR {core.MAIN.upper()} (FAST): {len(batch)} commit(s) from {staging} '
        f'({stip[:12]}), '
        + ('which already contains ' + core.MAIN if copy_tip == stip else
           f'merged with {core.MAIN} as {copy_tip[:12]}')
        + f' and pushed as {copy}:\n  ' + '\n  '.join(shown)
        + core._other_work_note(others, work) + '\n\n'
        f'Next, and not by this script: open a pull request from {copy} into '
        f'{core.MAIN}, titled "Promote {staging} into {core.MAIN} ({len(batch)} '
        f'commit(s))", and merge it now with a merge commit{core._at_head(copy_tip)}; '
        f'do not wait for GitHub\'s test first. Then: {after}. Never open it '
        f'from {staging} itself.')
    _verdict(f'READY FOR {core.MAIN.upper()} (FAST): open a pull request from {copy} '
             f'into {core.MAIN} and merge it now with expectedHeadSha {copy_tip}; '
             + (f'no GitHub test runs on this one, so do not wait for one; after '
                f'the merge run the full suite here with --run-tests {core.MAIN}'
                if full_after else
                f'no GitHub test runs on this one and no full check is needed '
                f'after it ({full_why})' if skipped else
                f'the GitHub test runs after the merge -- wait on it with '
                f'--wait-main-test {copy}')
             + f'; {core.MAIN} has not moved yet', move=move)
    for line in review:
        say(line)
    return PROMOTE_MAIN_NOT_MOVED


FULL_FLAG = '--full'


BECAUSE_FLAG = '--because'


def full_route_refusal(kw):
    """-> why `kw` (from promote_args) is refused, or None. The full route
    into main is refused unless it carries the person's own words asking
    for it or agreeing to it, in --because."""
    if kw.get('fast', True):
        return None
    if (kw.get('because') or '').strip():
        return None
    return ('PROMOTE REFUSED: --full, the long way into main (the full local '
            'suite before the merge, and GitHub\'s test waited on first), is '
            'taken only when the person explicitly asks for it or agrees to it '
            '(Morgan, 2026-10-11). Without that, run the move with no flag: '
            'the quick checks, merge at once, and the tests after. If they '
            'did ask, run again with --because \'<their own words>\'.')


def promote_args(args):
    """-> the keyword arguments --promote's `args` ask promote() for, or None
    for a usage error.

    THE MOVE INTO MAIN IS THE FAST ONE UNLESS THE PERSON ASKS FOR THE FULL
    ONE (Morgan, 2026-10-11, strength: decided: "I think we should default
    to the fast route unless I explicitly agree to or request the slow
    route"). The slow route had stayed the default after the fast one was
    built, so a Produce run as the practice wrote it, with no flag, ran the
    full suite before the merge and waited on GitHub's test as well; that
    day it took most of an hour for a two-file change. --full asks for the
    old route; --fast is still taken, and changes nothing. The flag only
    matters when the step is the move into main: a Promote into staging
    is always fully checked.

    --full takes `--because '<the person's own words>'`, and without it is
    refused by full_route_refusal: the long way is taken only when the
    person agreed to it or asked for it, never on a session's own reading
    (Morgan, 2026-10-11: "only do the long way when explicitly authorized
    otherwise the short way with the tests after pushing it")."""
    rest, opts = list(args), {}
    while rest:
        if len(rest) >= 2 and rest[0] in ('--to', '--work', BECAUSE_FLAG):
            opts[rest[0][2:]] = rest[1]
            rest = rest[2:]
        elif rest[0] in ('--fast', FULL_FLAG, DESPITE_FLAG, NO_FULL_AFTER_FLAG):
            opts[rest[0]] = True
            rest = rest[1:]
        else:
            return None
    full = bool(opts.get(FULL_FLAG))
    if opts.get('--fast') and 'to' not in opts:
        opts['to'] = core.MAIN
    if opts.get('to', core.STAGING) not in (core.STAGING, core.MAIN):
        return None
    if full and (opts.get('--fast') or opts.get(DESPITE_FLAG)
                 or opts.get(NO_FULL_AFTER_FLAG)):
        return None
    if opts.get('because') is not None and not full:
        return None
    if opts.get('to') == core.STAGING and (opts.get('--fast') or full
                                      or opts.get(DESPITE_FLAG)
                                      or opts.get(NO_FULL_AFTER_FLAG)):
        return None
    return {'to': opts.get('to'), 'work': opts.get('work'), 'fast': not full,
            'because': opts.get('because'),
            'despite_failed_tests': bool(opts.get(DESPITE_FLAG)),
            'no_full_after': bool(opts.get(NO_FULL_AFTER_FLAG))}

