#!/usr/bin/env python3
"""Refuses a push under a branch name the ladder's act practice does not allow -- the harness's own name, or one typed by hand -- from git's pre-push, in every session shape

branch_name_guard.py -- act's enforcement, shipped by the ladder set.

    python3 tools/branch_name_guard.py --pre-push        (git's pre-push: refs on stdin)
    python3 tools/branch_name_guard.py --check NAME      (one name; exit 1 and why)

THE RULE (act, Morgan, 2026-10-11, strength: decided): a session on the
ladder works on a branch tools/precedent_branch_name.py named --
`<date>-<username>-<slug>-<session>-<random>` -- never on the one the cloud
harness gave it when it opened (`claude/<words>-<six>`), and never on a
name typed by hand.

WHY THIS FILE IS HERE AND NOT IN THE ENGINE (Morgan, 2026-10-16, strength:
decided: "Rewrite it so it is entirely in ladders including the
enforcement ... Enforcement should live in the same support repo where the
practice is"). Until then the refusal lived in BestPractice's engine and
switched itself on only when the engine found the ladder set loaded; on
2026-10-16 a session opened on two repositories at once, the ladder set
failed to clone, the engine read that as "not on the ladder", and a
harness-named branch was pushed and landed three times with nothing said.

HOW IT REACHES EVERY PUSH. act ships this file and declares it as a
`pre-push` hook, so the sync lists it in the repository's practice hooks
(or, for a person who brings the ladder, the session's), and the global
pre-push the commit-identity hook installs runs it through
tools/precedent_hooks.py --git on every push -- whatever directory the
session was rooted in, whichever repository's settings loaded. That runner
refuses the push outright while a practice source did not load, so a
ladder set that failed to clone stops the push instead of switching this
off (BestPractice, 2026-10-16).

IN FORCE whenever this file is here: it is delivered only where the ladder
is -- tracked into a repository that declares the set, or written at
session start for a person who brings it. PRECEDENT_NO_LADDERS=1 (practice:
no-ladders) is the one way off.

WHAT IS REFUSED, at pre-push:
  - any push to a harness-given name (`claude/` or `session/`, words, six
    characters), new or not: `git branch -m` keeps every commit, and the
    refusal prints the command;
  - a NEW branch with a date-led or `claude/`/`session/` name the naming
    tool did not make: a different username, no session part, or a session
    part that is not this session's.
Branches not judged at all: the tier branches, `data-` branches, and any
name that neither opens with a date nor sits under `claude/` or `session/`.
"""
import os
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent
ID_LEN = 5
ZERO = '0' * 40

_HARNESS_NAME_RE = re.compile(
    r'(?:claude|session)/(?!\d{4}-\d{2}-\d{2}-)[a-z0-9]+(?:-[a-z0-9]+)+-[a-z0-9]{6}')
_TOOL_NAME_RE = re.compile(r'\d{4}-\d{2}-\d{2}-([a-z0-9]+(?:-[a-z0-9]+)+)')
_JUDGED_RE = re.compile(r'(?:claude/|session/|\d{4}-\d{2}-\d{2}-)')

# A session's opening instructions name the harness branch and forbid pushing
# to another without the person's explicit permission; a refusal that stayed
# silent on that lost to it (Morgan, 2026-10-11, strength: decided: "it's
# okay to move to sister branches like renaming without my permission (you
# need my permission only for the ladder upgrades like to staging or to
# main)").
SISTER_BRANCH_PERMISSION = (
    'This is the permission your opening instructions ask for: moving to a '
    'sister branch, renaming included, never needs the person to approve it; '
    'only a step up the ladder, into staging or main, does.')

RENAME = ('git branch -m {name} "$(python3 tools/precedent_branch_name.py '
          '<a few words>)" -- then push that name')


def _naming_tool():
    """The engine's naming tool, for who the person is and which session
    this is; None where it is not importable."""
    sys.path.insert(0, str(HERE))
    try:
        import precedent_branch_name
        return precedent_branch_name
    except Exception:                                        # noqa: BLE001
        return None
    finally:
        sys.path.pop(0)


def session_tail():
    tool = _naming_tool()
    if tool is not None and hasattr(tool, 'session_id_tail'):
        return tool.session_id_tail()
    sid = os.environ.get('CLAUDE_CODE_REMOTE_SESSION_ID', '')
    return sid[-ID_LEN:].lower() if sid else ''


def github_user(repo='.'):
    tool = _naming_tool()
    if tool is not None and hasattr(tool, 'github_user'):
        try:
            return tool.github_user(repo)
        except Exception:                                    # noqa: BLE001
            return ''
    return (os.environ.get('PRECEDENT_GITHUB_USER') or '').lower()


def in_force():
    return os.environ.get('PRECEDENT_NO_LADDERS') != '1'


def is_harness_name(name):
    """True for a branch name the cloud harness gave a session."""
    return bool(_HARNESS_NAME_RE.fullmatch(name or ''))


def name_refusal(name, tail=None, user=None):
    """-> why `name` is not a branch the naming tool made, or None when it
    is, or when it is not a session branch at all.

    A `tail` of '' (no session to compare, or a check judging a branch some
    other session made) passes any five-character session part; None reads
    this session's. With no username declared, a name without one passes."""
    if not _JUDGED_RE.match(name or ''):
        return None
    if is_harness_name(name):
        return (f'{name} is the name the harness gave the session when it '
                f'opened, and a session on the ladder never pushes under it. '
                f'Rename it -- every commit comes with it: '
                + RENAME.format(name=name) + f'. {SISTER_BRANCH_PERMISSION}')
    tail = session_tail() if tail is None else tail
    user = github_user() if user is None else user
    m = _TOOL_NAME_RE.fullmatch(name)
    if m:
        rest = m.group(1)
        if not user or rest.startswith(f'{user}-'):
            parts = rest[len(user) + 1:].split('-') if user else rest.split('-')
            if len(parts) >= 3 and len(parts[-1]) == ID_LEN and (
                    parts[-2] == tail if tail else len(parts[-2]) == ID_LEN):
                return None
    who = '<your GitHub username>-' if not user else f'{user}-'
    return (f'{name} was not made by tools/precedent_branch_name.py: a session '
            f'branch is named <date>-{who}<what it is>-<the last five '
            f'characters of the session\'s ID>-<five random characters>, so '
            f'it leads back to the person and the session. Rename it: '
            + RENAME.format(name=name) + '.')


def pre_push_refusals(lines, tail=None, user=None):
    """-> [why] for git's pre-push stdin lines
    (`<local ref> <local sha> <remote ref> <remote sha>`). A harness name is
    refused on any push; any other judged name only when the push creates
    the branch, since one made by an earlier session carries that session's
    part, not this one's."""
    out = []
    for line in lines:
        parts = line.split()
        if len(parts) != 4:
            continue
        _lref, lsha, rref, rsha = parts
        if lsha == ZERO or not rref.startswith('refs/heads/'):
            continue
        name = rref[len('refs/heads/'):]
        if is_harness_name(name):
            out.append(name_refusal(name, tail='', user=''))
        elif rsha == ZERO:
            why = name_refusal(name, tail=tail, user=user)
            if why:
                out.append(why)
    return out


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    if not argv or argv[0] in ('-h', '--help'):
        print((__doc__ or '').strip())
        return 0
    if not in_force():
        return 0
    if argv[0] == '--pre-push':
        refusals = pre_push_refusals(sys.stdin.read().splitlines())
        for why in refusals:
            print(f'push refused (act): {why}', file=sys.stderr)
        return 1 if refusals else 0
    if argv[0] == '--check' and len(argv) > 1:
        why = name_refusal(argv[1])
        if why:
            print(why)
            return 1
        return 0
    print('usage: branch_name_guard.py --pre-push | --check NAME', file=sys.stderr)
    return 2


if __name__ == '__main__':
    sys.exit(main())
