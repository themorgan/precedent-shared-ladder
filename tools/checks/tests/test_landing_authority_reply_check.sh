#!/usr/bin/env bash
# practice: prompt-please-on-the-ladder -- claims this test, so a consuming repository receives it
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
# it is the BestPractice clone precedent.json declares, found the engine's
# way (beside this checkout, or beside its main checkout from a worktree).
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
TOOLS="$HERE/../.."
# This set's own reply_check.json: where the push check says this set is
# (a consumer that declares it, PRECEDENT_SOURCE_DIR_PRECEDENT_SHARED_LADDER),
# else this checkout's root, which is right inside the set itself. A
# consumer receives this test since 2026-10-31, and the root there is the
# consumer's, so the old default read a file that is not there and the
# test crashed on main (2026-11-01, a voice repository's Produce).
if [ -z "${REPLY_CHECK:-}" ] && [ -n "${PRECEDENT_SOURCE_DIR_PRECEDENT_SHARED_LADDER:-}" ] \
        && [ -f "$PRECEDENT_SOURCE_DIR_PRECEDENT_SHARED_LADDER/reply_check.json" ]; then
    REPLY_CHECK="$PRECEDENT_SOURCE_DIR_PRECEDENT_SHARED_LADDER/reply_check.json"
fi
REPLY_CHECK="${REPLY_CHECK:-$TOOLS/../reply_check.json}"
if [ ! -f "$REPLY_CHECK" ]; then
    echo "SKIPPED: no copy of this set's reply_check.json here (looked at $REPLY_CHECK"
    echo "  and \$PRECEDENT_SOURCE_DIR_PRECEDENT_SHARED_LADDER), so there is no"
    echo "  landing-authority pair to judge; the set's own run judges it"
    exit 0
fi
# The push check exports where universal really is, resolved the engine's
# way, a throwaway worktree in /tmp included (BestPractice PR #1440,
# 2026-10-30). The sibling path is the default when it does not, which is
# a run by hand from a clone beside BestPractice.
if [ -z "${UNIVERSAL_REPLY_CHECK:-}" ] && [ -n "${PRECEDENT_SOURCE_DIR_PRECEDENT:-}" ]; then
    UNIVERSAL_REPLY_CHECK="$PRECEDENT_SOURCE_DIR_PRECEDENT/reply_check.json"
fi
# Otherwise the universal path precedent.json declares, resolved by the
# engine's own _declared_path: beside this checkout, or beside its main
# checkout when this is a linked worktree that has no BestPractice next to
# it (2026-10-31: the test failed in a worktree under another directory).
if [ -z "${UNIVERSAL_REPLY_CHECK:-}" ]; then
    UNIVERSAL_DIR="$(PYTHONDONTWRITEBYTECODE=1 python3 - "$TOOLS" <<'PY' 2>/dev/null
import json, pathlib, sys
sys.path.insert(0, sys.argv[1])
import precedent_resolve as pr
root = pathlib.Path(sys.argv[1]).resolve().parent
raw = next(s['path'] for s in json.load(open(root / 'precedent.json', encoding='utf-8'))['sources']
           if s.get('level') == 'universal')
print(pr._declared_path(root, raw))
PY
)"
    if [ -n "$UNIVERSAL_DIR" ] && [ -f "$UNIVERSAL_DIR/reply_check.json" ]; then
        UNIVERSAL_REPLY_CHECK="$UNIVERSAL_DIR/reply_check.json"
    fi
fi
UNIVERSAL_REPLY_CHECK="${UNIVERSAL_REPLY_CHECK:-$TOOLS/../../BestPractice/reply_check.json}"
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
