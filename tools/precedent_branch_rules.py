#!/usr/bin/env python3
"""Reports whether each repository has the GitHub ruleset that refuses creating a harness-named branch (claude/**, session/**), and applies it only when asked, repository by repository

precedent_branch_rules.py -- act's rule, held by GitHub itself.

    python3 tools/precedent_branch_rules.py                 this repository
    python3 tools/precedent_branch_rules.py OWNER/REPO ...  those repositories
    python3 tools/precedent_branch_rules.py --apply OWNER/REPO ...

WHY (2026-10-16). Every other guard on act's naming rule runs inside the
session -- the pre-push guard, this set's check -- and each one can be
missing in some new session shape nobody tested. A repository ruleset is
the one guard nothing in the session can skip: GitHub refuses the push
that would create `claude/<anything>` or `session/<anything>`, whatever
loaded and whatever the session was told. A session that hits it renames
its branch (`git branch -m`, every commit kept) and pushes that.

OPT-IN, PER PERSON (Morgan, 2026-10-16, strength: decided: "this convention
should be something that is explicitly opted in to ... I can opt in, but
Alex (by default) won't be opted in so nothing would change for him" --
"it isn't just for my accounts but anyone else including Alex who may opt
in"). Anyone opts in by writing

    "github_branch_rules": true

in their own identity.json (their individual set's), or in their user-level
config (~/.config/precedent/config.json). Nobody who has not opted in is
touched: --apply refuses, and the report only says how to opt in.

ONLY ON THE PERSON'S OWN REPOSITORIES. Once opted in, --apply adds the
ruleset to the repositories named on the command line that the person's
own GitHub account owns (identity.json's "github"), and refuses any other:
a ruleset binds everyone who pushes there, so it is the owner's call. It
never applies to all of them at once, and reporting reads and changes
nothing.

How it reaches GitHub: the `gh` command where it works, else the REST API
with $GH_TOKEN or $GITHUB_TOKEN. Rulesets on a private repository need a
paid GitHub plan; where the plan lacks them GitHub says so and this
reports it. Where neither route can change the settings, it prints the
page where the person adds the ruleset by hand, and what to enter.

Exit 0 when every repository named has the ruleset (or it was applied);
1 when one lacks it; 2 when one could not be checked.
"""
import json
import os
import pathlib
import re
import subprocess
import sys
import urllib.error
import urllib.request

OPT_IN_KEY = 'github_branch_rules'
RULESET_NAME = 'No harness-named branches (act)'
PATTERNS = ['refs/heads/claude/**', 'refs/heads/session/**']
RULESET = {
    'name': RULESET_NAME,
    'target': 'branch',
    'enforcement': 'active',
    'conditions': {'ref_name': {'include': PATTERNS, 'exclude': []}},
    'rules': [{'type': 'creation'}],
}



def _tools():
    here = pathlib.Path(__file__).resolve().parent
    if str(here) not in sys.path:
        sys.path.insert(0, str(here))


def opted_in():
    """-> (True, where) when this person has opted in, else (False, why)."""
    _tools()
    places = []
    try:
        import precedent_branch_name as pbn
        f = pbn.identity_file('.')
        if f:
            places.append(f)
    except Exception:                                        # noqa: BLE001
        pass
    places.append(pathlib.Path(os.environ.get('PRECEDENT_USER_CONFIG',
                                              '~/.config/precedent/config.json')).expanduser())
    for f in places:
        try:
            data = json.loads(pathlib.Path(f).read_text(encoding='utf-8'))
        except (OSError, ValueError):
            continue
        if isinstance(data, dict) and data.get(OPT_IN_KEY) is True:
            return True, str(f)
    return False, (f'not opted in: write "{OPT_IN_KEY}": true in your '
                   f'identity.json or ~/.config/precedent/config.json to opt in')


def person_login():
    _tools()
    try:
        import precedent_branch_name as pbn
        return (pbn.github_user('.') or '').lower()
    except Exception:                                        # noqa: BLE001
        return (os.environ.get('PRECEDENT_GITHUB_USER') or '').lower()


class CannotReach(Exception):
    pass


def _gh(method, path, body=None):
    """-> (status, parsed body) through `gh api`, or None where gh is not
    usable here."""
    cmd = ['gh', 'api', '-X', method, path, '-H', 'Accept: application/vnd.github+json',
           '--include']
    if body is not None:
        cmd += ['--input', '-']
    try:
        r = subprocess.run(cmd, input=json.dumps(body) if body is not None else None,
                           capture_output=True, text=True, timeout=60)
    except (OSError, subprocess.TimeoutExpired):
        return None
    parts = re.split(r'\r?\n\r?\n', r.stdout, maxsplit=1)
    head, rest = parts[0], (parts[1] if len(parts) > 1 else '')
    m = re.match(r'HTTP/\S+ (\d+)', head)
    if not m:
        text = (r.stderr or r.stdout).strip()
        return 0, {'message': text}
    try:
        data = json.loads(rest) if rest.strip() else {}
    except ValueError:
        data = {'message': rest.strip()}
    return int(m.group(1)), data


def _rest(method, path, body=None):
    token = os.environ.get('GH_TOKEN') or os.environ.get('GITHUB_TOKEN')
    if not token:
        return None
    req = urllib.request.Request(
        'https://api.github.com' + path, method=method,
        data=json.dumps(body).encode() if body is not None else None,
        headers={'Authorization': f'Bearer {token}',
                 'Accept': 'application/vnd.github+json'})
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            return resp.status, json.loads(resp.read() or b'{}')
    except urllib.error.HTTPError as e:
        try:
            return e.code, json.loads(e.read() or b'{}')
        except ValueError:
            return e.code, {}
    except (urllib.error.URLError, OSError) as e:
        return 0, {'message': str(e)}


def call(method, path, body=None):
    for route in (_gh, _rest):
        got = route(method, path, body)
        if got is not None and got[0]:
            return got
    raise CannotReach('neither gh nor a GitHub token reached the API from here')


def this_repo():
    r = subprocess.run(['git', 'remote', 'get-url', 'origin'],
                       capture_output=True, text=True)
    m = re.search(r'github\.com[/:]([^/]+)/([^/]+?)(?:\.git)?/?$', r.stdout.strip())
    return f'{m.group(1)}/{m.group(2)}' if m else None


def manual_steps(repo):
    return (f'add it by hand at https://github.com/{repo}/settings/rules/new?target=branch'
            f' -- name "{RULESET_NAME}", enforcement Active, target branches '
            f'by pattern {" and ".join(p[len("refs/heads/"):] for p in PATTERNS)}, '
            f'rule "Restrict creations", no bypass list')


def status(repo):
    """-> ('present'|'missing'|'unavailable'|'unknown', detail)"""
    try:
        code, data = call('GET', f'/repos/{repo}/rulesets')
    except CannotReach as e:
        return 'unknown', str(e)
    if code == 200 and isinstance(data, list):
        for rs in data:
            if isinstance(rs, dict) and rs.get('name') == RULESET_NAME:
                return 'present', f'ruleset {rs.get("id")}'
        return 'missing', ''
    msg = str((data or {}).get('message', '')) if isinstance(data, dict) else ''
    if code == 403 and re.search(r'upgrade|plan|not available', msg, re.I):
        return 'unavailable', msg
    return 'unknown', f'HTTP {code}: {msg}'


def apply(repo):
    try:
        code, data = call('POST', f'/repos/{repo}/rulesets', RULESET)
    except CannotReach as e:
        return False, str(e)
    if code in (200, 201):
        return True, f'ruleset {data.get("id")} created'
    msg = str((data or {}).get('message', '')) if isinstance(data, dict) else ''
    return False, f'HTTP {code}: {msg}'


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    if any(a in ('-h', '--help') for a in argv):
        print((__doc__ or '').strip())
        return 0
    do_apply = '--apply' in argv
    repos = [a for a in argv if not a.startswith('--')]
    if do_apply and not repos:
        print('--apply changes a repository\'s settings: name each repository '
              '(OWNER/REPO) it is for.', file=sys.stderr)
        return 2
    repos = repos or [r for r in [this_repo()] if r]
    if not repos:
        print('no repository named, and this checkout has no GitHub origin', file=sys.stderr)
        return 2
    on, where = opted_in()
    login = person_login()
    if do_apply and not on:
        print(f'--apply refused: {where}.', file=sys.stderr)
        return 2
    if do_apply and not login:
        print('--apply refused: no GitHub username is declared ("github" in '
              'identity.json), so whose repositories these are is not known.',
              file=sys.stderr)
        return 2
    worst = 0
    for repo in repos:
        state, detail = status(repo)
        if state == 'missing' and do_apply:
            if repo.split('/')[0].lower() != login:
                print(f'{repo}: --apply refused -- it is not owned by {login}, '
                      f'and a ruleset binds everyone who pushes there, so it is '
                      f'its owner\'s call', file=sys.stderr)
                worst = max(worst, 1)
                continue
            ok, detail = apply(repo)
            state = 'applied' if ok else 'missing'
        line = {
            'present': 'has the ruleset',
            'applied': 'ruleset applied',
            'missing': 'LACKS the ruleset -- GitHub will let a harness-named branch be created',
            'unavailable': 'cannot have it: rulesets are not available on this repository\'s plan',
            'unknown': 'could not be checked',
        }[state]
        print(f'{repo}: {line}' + (f' ({detail})' if detail else ''))
        if state == 'missing':
            if on and repo.split('/')[0].lower() == login:
                print(f'  {manual_steps(repo)}, or run: python3 tools/precedent_branch_rules.py --apply {repo}')
            elif not on:
                print(f'  ({where}; nothing is changed until you do)')
            worst = max(worst, 1)
        elif state in ('unknown', 'unavailable'):
            worst = max(worst, 2 if state == 'unknown' else 1)
    if not on:
        worst = min(worst, 0) if worst == 1 else worst
    return worst


if __name__ == '__main__':
    sys.exit(main())
