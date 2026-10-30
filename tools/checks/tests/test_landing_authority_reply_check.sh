#!/usr/bin/env bash
# Test for this set's landing-authority pair in reply_check.json
# (id "prompt-please-landing-authority"): a paste block that orders a landing
# needs the person's quoted Booked; one that only reports a landing, or lists
# it as one example in a bracketed list, does not. Run through the engine's
# violations() in tools/ beside this set. REPLY_CHECK names another copy of
# the file to judge, so the old one can be shown failing.
#
# JUDGED WITH UNIVERSAL'S RULE (2026-10-29). The pair states only what it
# adds and inherits universal's triggers (the engine's _inherit_pair), so it
# is judged as a session sees it: universal's rule and this one through the
# engine's _settle. UNIVERSAL_REPLY_CHECK names universal's file; by default
# it is the BestPractice clone beside this set, which precedent.json declares.
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
TOOLS="$HERE/../.."
REPLY_CHECK="${REPLY_CHECK:-$TOOLS/../reply_check.json}"
# The push check exports where universal really is, resolved the engine's
# way, a throwaway worktree in /tmp included (BestPractice PR #1440,
# 2026-10-30). The sibling path is the default when it does not.
if [ -z "${UNIVERSAL_REPLY_CHECK:-}" ] && [ -n "${PRECEDENT_SOURCE_DIR_PRECEDENT:-}" ]; then
    UNIVERSAL_REPLY_CHECK="$PRECEDENT_SOURCE_DIR_PRECEDENT/reply_check.json"
fi
UNIVERSAL_REPLY_CHECK="${UNIVERSAL_REPLY_CHECK:-$TOOLS/../../BestPractice/reply_check.json}"
# --run-tests judges a throwaway worktree in /tmp, where nothing sits beside
# the tree (2026-10-30: main went red on that alone). There, look beside the
# clone the worktree belongs to, which git's common dir names. RETIRE this
# once this set's tools/ENGINE_MANIFEST.json records a BestPractice main
# carrying precedent_resolve.source_dir_env: the variable above covers it.
if [ ! -f "$UNIVERSAL_REPLY_CHECK" ]; then
    _common="$(git -C "$HERE" rev-parse --path-format=absolute --git-common-dir 2>/dev/null || true)"
    if [ -n "$_common" ] && [ -f "$(dirname "$_common")/../BestPractice/reply_check.json" ]; then
        UNIVERSAL_REPLY_CHECK="$(dirname "$_common")/../BestPractice/reply_check.json"
    fi
fi
PYTHONDONTWRITEBYTECODE=1 python3 - "$TOOLS" "$REPLY_CHECK" "$UNIVERSAL_REPLY_CHECK" <<'PY'
import json, pathlib, sys
sys.path.insert(0, sys.argv[1])
import precedent_reply_check as rc

RID = 'prompt-please-landing-authority'
if not pathlib.Path(sys.argv[3]).is_file():
    print(f'FAIL: universal\'s reply_check.json is not at {sys.argv[3]}; this '
          f'set\'s pair inherits its triggers, so it cannot be judged without it '
          f'(set UNIVERSAL_REPLY_CHECK, or attach BestPractice beside this set)')
    sys.exit(1)
universal = [r for r in json.load(open(sys.argv[3], encoding='utf-8'))
             if r.get('id') == RID]
own = [r for r in json.load(open(sys.argv[2], encoding='utf-8'))
       if r.get('id') == RID]
assert len(own) == 1, 'the landing-authority pair is not in reply_check.json'
assert len(universal) == 1, 'universal has no landing-authority rule to inherit'
settled = [r for r in rc._settle(universal + own, pathlib.Path(sys.argv[1]).parent)
           if r.get('id') == RID]
assert len(settled) == 1, 'the two rules did not settle into one'
req = {'id': RID, 'practice': settled[0].get('practice'),
       'require_in_fence_paired_with': settled[0]['require_in_fence_paired_with'][:1]}

def refused(body):
    text = 'Paste into: a new session.\n\n```\n' + body + '\n```\n'
    return [v['message'] for v in rc.violations(text, [req])
            if v['kind'] == 'in_fence_paired']

BOOKED = 'Morgan, 2026-10-20: "Booked."\n'
passes = [
    'On 2026-10-20 precedent_branches.py --land refused a direct push to staging.',
    'Then narrow it to orders to land (land it, merge the PR, Booked as an instruction).',
    'A direct push to staging was refused.',
]
orders = [
    'Then merge the PR into main.',
    'You can push it to staging.',
    'Merge the PR, then stop.',
    'Land it on staging.',
    'Open a PR into staging.',
    'Booked.',
    'Run precedent_branches.py --promote.',
    'git push origin staging',
]
fail = 0
for body in passes:
    got = refused(body)
    if got:
        print(f'FAIL: refused, though it orders nothing: {body!r}\n  {got[0][:160]}'); fail = 1
for body in orders:
    if not refused(body):
        print(f'FAIL: an order to land passed with no quoted Booked: {body!r}'); fail = 1
    got = refused(BOOKED + body)
    if got:
        print(f'FAIL: refused even with the quoted Booked: {body!r}\n  {got[0][:160]}'); fail = 1
print('PASS: landing-authority reply check' if not fail else
      'FAIL: landing-authority reply check')
sys.exit(fail)
PY
