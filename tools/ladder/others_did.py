#!/usr/bin/env python3
"""Once a day, from the first session after 07:00 in the person's own timezone, says what OTHER people landed in this repository since that person's own last commit here -- every commit on its shared branches that is not theirs -- and hands the session a block to open its first reply with; nothing is stored on origin, only a note in the container so one session does not say it twice

Say what other people did here since your own last commit, once a day.

WHY IT EXISTS (Morgan, 2026-10-08). Alex changed how merges to `main` work
and Morgan found out only when something confusing happened. WHATS_NEW.md
did not help: it carries the three or four most important things done by
anyone each day, and most days that is mostly Morgan's own work. What he
asked for is the opposite view -- only what OTHERS did -- delivered before
his first question of the day is answered, without him having to ask.

IT REPLACES the beta-branch watermark check, which did a narrower
version of the same job (anyone else pushing to one branch, staging) and,
measured the day this was written, did not deliver it: it found Alex's ten
commits at that session's start, and (1) its notice sat inside a
SessionStart output over the size the harness shows, so the session never
saw it, and (2) it could write its mark only into a checkout sitting idle
on staging, which a session on a feature branch never is, so the mark went
to a per-container note and every new container would have said it again.
This file fixes the first: the notice reaches the session through the
reply gate on the first prompt. WHERE IT STARTS settles the second.

WHERE IT STARTS: the person's own most recent commit on any of the
shared branches (Morgan, 2026-10-10: "Go with option 1"). Everything
others landed after it is the report, headed "since your last commit
here". Nothing is written to origin. From 2026-10-08 the tool kept a mark
of what each person was last told on origin's refs/precedent/others-did,
and before that in a JSON file on the landing branch.
From a cloud session the git proxy refuses a push to refs/precedent/*
with HTTP 403 (measured 2026-10-10), so the mark stayed in the container,
every new container started over, and the daily report could go missing.
The cost of no mark: until the person commits here again, each new
container repeats the same list. Inside one container a note in
.precedent/ stops a repeat, and when that note is newer than the last
commit it is the starting point instead. The options weighed are in
todo/todo-2026-10-10-others-did-mark-cannot-be-pushed-from-a-cloud-session.md.

WHO IT IS FOR. The person who brings the ladder set: the set ships this
file (practices/others-did.md, `ships:`) and wires it with two `hooks:`,
one at SessionStart that finds the news and one at UserPromptSubmit that
hands it over. It moved here from BestPractice's engine on 2026-10-17
(BestPractice spec/ENFORCEMENT_LIVES_WITH_ITS_PRACTICE_PLAN.md part 3);
the commit sorting it shares with Update Vendors stayed in the engine, in
tools/precedent_commit_owners.py. PRECEDENT_NO_LADDERS=1 still silences it.

WHAT COUNTS AS SOMEONE ELSE'S: see the engine's
tools/precedent_commit_owners.py, which both readers use.

WHEN. At most one report a day in a container: none before the person's
hour (07:00 by default, `others_did_hour` in identity.json overrides), and
none once they have been told since that hour today. A report writes the
container's note; a run that finds nothing from anyone else writes
nothing and says one line.

Run:
  python3 tools/ladder/others_did.py              # session start: one status line
  python3 tools/ladder/others_did.py --no-fetch   # compare local refs only
  python3 tools/ladder/others_did.py --remind     # first prompt: the pending report, once

Exit status is always 0 (practice: fail-gracefully): a session start that
a network hiccup could block is worse than the notice it was carrying.
"""
import argparse
import datetime
import json
import pathlib
import re
import subprocess
import sys

# Shipped by the ladder set to tools/ladder/; the engine it runs on is in
# tools/ beside it, in the set's own repository and in every consumer.
# Behind the engine already loaded, never in front of it (2026-10-31): the
# BestPractice engine loads this file into its own process, and putting
# this set's tools/ first there made every later import -- leak_gate
# among them -- this set's older vendored copy for the rest of that run.
_ENGINE = str(pathlib.Path(__file__).resolve().parent.parent)
if _ENGINE not in sys.path:
    sys.path.append(_ENGINE)
import precedent_identity as pi   # noqa: E402
import precedent_time             # noqa: E402
try:
    from precedent_commit_owners import (  # noqa: E402
        git, classify, commit_listing, LOG_FORMAT, records as _records)
except ImportError:
    # An engine from before 2026-10-17 carries the same functions in the
    # file this one replaced; Update Vendors takes the two halves in either
    # order, so either engine works.
    from precedent_others_did import (  # noqa: E402
        git, classify, commit_listing, LOG_FORMAT, _records)

REPO = pathlib.Path(__file__).resolve().parents[2]

LOCAL_NOTE = '.precedent/others-did-local.json'
PENDING = '.precedent/others-did-pending.md'
DEFAULT_HOUR = 7
HOUR_SETTING = 'others_did_hour'
def identity_key(identity):
    """A slug of the declared NAME, never the email: the leak gate refuses an
    email anywhere in a tracked file, and this one is public."""
    slug = re.sub(r'[^a-z0-9]+', '-',
                  (identity.get('name') or identity.get('email') or '').lower())
    return slug.strip('-') or 'unknown'


# ---------------------------------------------------------------- branches

def watched_branches(repo):
    """The tier branches this repository has: main, its staging branch and
    whatever precedent.json names as base_branch."""
    names = ['main', 'staging']
    try:
        import precedent_branches as pb
        for extra in (pb.base_branch(repo), pb.staging_branch(repo)):
            if extra and extra not in names:
                names.append(extra)
    except Exception:                                             # noqa: BLE001
        pass
    return names


def landing(repo, user_config=None):
    try:
        import precedent_branches as pb
        return pb.landing_branch(repo, user_config)[0]
    except Exception:                                             # noqa: BLE001
        return 'main'


def _fetch(repo, branches):
    """Fetch the branches origin actually has. -> the ones that resolve."""
    code, out = git(repo, 'ls-remote', '--heads', 'origin')
    if code != 0:
        return None
    present = {ln.split('refs/heads/', 1)[1] for ln in out.splitlines()
               if 'refs/heads/' in ln}
    wanted = [b for b in branches if b in present]
    if not wanted:
        return []
    _, shallow = git(repo, 'rev-parse', '--is-shallow-repository')
    depth = ['--depth=200'] if shallow == 'true' else []
    refspecs = [f'+refs/heads/{b}:refs/remotes/origin/{b}' for b in wanted]
    code, _ = git(repo, 'fetch', '-q', *depth, 'origin', *refspecs)
    return wanted if code == 0 else None


def _heads(repo, branches):
    heads = {}
    for b in branches:
        code, sha = git(repo, 'rev-parse', '--verify', '--quiet', f'origin/{b}^{{commit}}')
        if code == 0 and sha:
            heads[b] = sha
    return heads


# ---------------------------------------------------------------- where it starts

def my_last_commit(repo, heads, me_email):
    """-> (sha, when) of the person's own most recent commit reachable from
    any watched branch, by author email, or (None, None) when they have none
    here. Merge commits count: landing one is the person's own act."""
    me_email = (me_email or '').lower()
    if not me_email or not heads:
        return None, None
    code, out = git(repo, 'log', '--date-order', '-n', '4000',
                    '--format=%H%x1f%ae%x1f%cI', *sorted(set(heads.values())))
    if code != 0:
        return None, None
    for line in out.splitlines():
        sha, _, rest = line.partition('\x1f')
        email, _, when = rest.partition('\x1f')
        if email.lower() == me_email:
            return sha, _parse_time(when)
    return None, None


def _read_local(repo):
    try:
        data = json.loads((pathlib.Path(repo) / LOCAL_NOTE).read_text(encoding='utf-8'))
    except (OSError, ValueError):
        return {}
    return data if isinstance(data, dict) else {}


def _ignored(repo, rel):
    """Only write under .precedent/ where git can be SHOWN to ignore it: an
    untracked file elsewhere is dirt that reads as work existing nowhere."""
    return git(repo, 'check-ignore', '--quiet', rel)[0] == 0


def _write_local(repo, rel, text):
    if not _ignored(repo, rel):
        return False
    path = pathlib.Path(repo) / rel
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding='utf-8')
    except OSError:
        return False
    return True


def _parse_time(value):
    try:
        return datetime.datetime.fromisoformat(value)
    except (TypeError, ValueError):
        return None


def _new_commits(repo, heads, tips, told_at):
    """Every non-merge commit on a watched branch that no tip the person was
    told about (in this container) already reaches."""
    known = [t for t in tips.values()
             if t and git(repo, 'cat-file', '-e', f'{t}^{{commit}}')[0] == 0]
    args = ['log', '--no-merges', LOG_FORMAT, *sorted(set(heads.values()))]
    if known:
        args += ['--not', *known]
    if len(known) < len([t for t in tips.values() if t]) and told_at:
        # A tip this clone does not hold (a shallow clone, a rewritten
        # branch): bound the window by time instead of reading all history.
        args.insert(1, f'--since={told_at}')
    code, out = git(repo, *args)
    return None if code != 0 else _records(out)


def _landed_since(repo, heads, mine, when):
    """Every non-merge commit that LANDED on a watched branch after the
    person's own commit `mine` (made at `when`) and that `mine` does not
    already contain.

    By landing, not by each commit's own date: a colleague's pull request
    holds commits made days before the person's last one, and they reach
    the branch only when it is merged. So each branch's first-parent line
    since `when` is read -- the merges and direct commits that moved it --
    and a merge contributes everything it brought in."""
    found = set()
    for head in sorted(set(heads.values())):
        code, out = git(repo, 'log', '--first-parent', f'--since={when.isoformat()}',
                        '--format=%H %P', head)
        if code != 0:
            return None
        for line in out.splitlines():
            sha, *parents = line.split()
            if len(parents) > 1:
                code, brought = git(repo, 'rev-list', '--no-merges',
                                    f'{parents[0]}..{sha}', '--not', mine)
                if code != 0:
                    return None
                found.update(brought.split())
            elif git(repo, 'merge-base', '--is-ancestor', sha, mine)[0] != 0:
                found.add(sha)
    if not found:
        return []
    code, out = git(repo, 'log', '--no-walk=sorted', LOG_FORMAT, *sorted(found))
    return None if code != 0 else _records(out)


# ---------------------------------------------------------------- the report

def _block(repo_name, since_text, others, unsure):
    """The text the reply gate hands the session on its first prompt."""
    return '\n'.join([
        f'WHAT OTHERS DID IN {repo_name} {since_text} '
        f'-- {len(others) + len(unsure)} commit(s) by people other than you.',
        '',
        'OPEN YOUR FIRST REPLY WITH THE THREE OR FOUR MOST IMPORTANT THINGS '
        'HERE, NEVER THE WHOLE LIST, before answering the question: three '
        "or four bullets in What's New style, each opening with its key phrase "
        'in bold, saying who did it and what it changes for the person. '
        'Pick by what changes for them; a change to a rule or to how '
        'sessions behave always makes the cut. Leave the rest out: the '
        'person can ask for more. Then answer. Say it once; it is not '
        'repeated in later replies (the others-did practice, in the ladder '
        'set; Morgan, 2026-10-10: "It should not list EVERYTHING, just the '
        'three or four most important things").',
        '']) + '\n' + commit_listing(others, unsure)


def _when(moment):
    return moment.strftime('%A %Y-%m-%d %H:%M')


def check(root=None, no_fetch=False, user_config=None, now=None, land=None):
    """-> (status, lines). status: 'alert' (a report is pending for the
    first prompt), 'ok' (nothing to tell, or not yet), 'unknown'.
    Writes nothing outside this clone's ignored .precedent/ directory."""
    repo = pathlib.Path(root).resolve() if root else REPO
    try:
        me = pi.declared_identity(repo, user_config=user_config)
    except pi.NoDeclaredIdentity:
        return 'unknown', ["no identity is declared, so other people's work "
                           "cannot be told apart from yours"]
    now = now or precedent_time.now(repo)
    del land  # where the mark used to be written; kept for callers
    branches = watched_branches(repo)
    if not no_fetch and _fetch(repo, branches) is None:
        return 'unknown', ['could not reach origin -- what others did is '
                           'unknown this session']
    heads = _heads(repo, branches)
    if not heads:
        return 'unknown', ['none of ' + ', '.join(branches) + ' resolves here']

    key = identity_key(me)
    notes = _read_local(repo)
    row = notes.get(key) if isinstance(notes.get(key), dict) else None

    hour = me.get(HOUR_SETTING, DEFAULT_HOUR)
    try:
        hour = int(hour)
    except (TypeError, ValueError):
        hour = DEFAULT_HOUR
    start = now.replace(hour=hour, minute=0, second=0, microsecond=0)
    told_at = _parse_time((row or {}).get('told_at'))
    if now < start:
        return 'ok', [f'before {hour:02d}:00 -- the day\'s report waits until then']
    if told_at and told_at >= start:
        return 'ok', [f'already told today at {told_at.strftime("%H:%M")}']

    mine, mine_at = my_last_commit(repo, heads, me.get('email'))
    if told_at and (not mine_at or told_at > mine_at):
        commits = _new_commits(repo, heads, row.get('tips') or {}, row.get('told_at'))
        since = f'since you were last told in this container ({_when(told_at)})'
    elif mine:
        commits = _landed_since(repo, heads, mine, mine_at)
        since = f'since your last commit here ({_when(mine_at)})'
    else:
        return 'ok', [f'{me.get("name") or key} has no commit here yet, so '
                      'there is nothing to count from; reports start after '
                      'your first one']
    if commits is None:
        return 'unknown', ['could not read the history since then']
    others, unsure = classify(repo, commits, me.get('email'), heads)
    if not others and not unsure:
        return 'ok', [f'nobody else changed anything {since}']

    _, url = git(repo, 'remote', 'get-url', 'origin')
    repo_name = re.sub(r'\.git$', '', url.rstrip('/').split('github.com/')[-1]) \
        if url else repo.name
    block = _block(repo_name, since, others, unsure)
    if _write_local(repo, PENDING, block):
        notes[key] = {'told_at': now.isoformat(timespec='seconds'),
                      'tips': dict(heads)}
        kept = _write_local(repo, LOCAL_NOTE, json.dumps(notes, indent=2) + '\n')
        outcome = 'noted in this container' if kept else 'not noted, so it may repeat'
    else:
        outcome = 'not noted: .precedent/ is not ignored here'
    who = ', '.join(sorted({w for _, w, _ in others})) or 'unsettled Claude sessions'
    lines = [f'{len(others) + len(unsure)} commit(s) by others {since} '
             f'({who}); the first reply opens with them ({outcome})']
    if outcome.startswith('not noted: '):
        lines.append(block)
    return 'alert', lines


def remind(root=None, user_config=None):
    """For the reply gate: the pending block, once, then gone. Reads one local
    file; never fetches, so a reply costs nothing when there is no news."""
    repo = pathlib.Path(root).resolve() if root else REPO
    if off_ladder(repo, user_config):
        return None
    path = repo / PENDING
    try:
        text = path.read_text(encoding='utf-8')
        path.unlink()
    except OSError:
        return None
    return text.strip() or None


def off_ladder(root, user_config=None):
    """True for a person off the ladder: the ladder set is what turns this on."""
    try:
        import precedent_ladder
        return precedent_ladder.ladder_in_force(root, user_config) is False
    except Exception:                                             # noqa: BLE001
        return False


CHECKED = '.precedent/others-did-checked'


def _today(repo):
    return precedent_time.now(repo).date().isoformat()


def _stamp_due(repo):
    """True when no check has run in this container today."""
    try:
        return (pathlib.Path(repo) / CHECKED).read_text(encoding='utf-8').strip() != _today(repo)
    except OSError:
        return True


def _stamp(repo, result):
    """Note that today's check ran -- unless it ran before the person's hour,
    or could not reach what it needed, so a later prompt tries again."""
    status, lines = result
    if status == 'unknown' or (lines and lines[0].startswith('before ')):
        return
    _write_local(repo, CHECKED, _today(repo) + '\n')


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--no-fetch', action='store_true')
    parser.add_argument('--remind', action='store_true',
                        help='print the pending report once, for the first prompt')
    args = parser.parse_args()
    if args.remind:
        # The first prompt does the day's check itself when nothing has yet
        # in this container today: a set's SessionStart hook is listed by a
        # file the same session start writes, and Claude Code runs one
        # event's hooks side by side, so in a fresh container it can miss
        # its own start (2026-10-17, when this moved into the ladder set).
        try:
            if not off_ladder(REPO) and _stamp_due(REPO):
                _stamp(REPO, check(no_fetch=args.no_fetch))
            report = remind(REPO)
        except Exception:                                         # noqa: BLE001
            report = None
        if report:
            print(report)
        return 0
    if off_ladder(REPO):
        return 0
    try:
        status, lines = check(no_fetch=args.no_fetch)
        _stamp(REPO, (status, lines))
    except Exception as exc:                                      # noqa: BLE001
        status, lines = 'unknown', [f'did not run ({exc})']
    prefix = {'ok': 'others-did', 'alert': 'OTHERS-DID',
              'unknown': 'others-did UNKNOWN'}[status]
    for i, line in enumerate(lines):
        print(f'{prefix}: {line}' if i == 0 else line)
    return 0


if __name__ == '__main__':
    sys.exit(main())
