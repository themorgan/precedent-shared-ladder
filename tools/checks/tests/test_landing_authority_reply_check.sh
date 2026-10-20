#!/usr/bin/env bash
# Test for this set's landing-authority pair in reply_check.json
# (id "prompt-please-landing-authority"): a paste block that orders a landing
# needs the person's quoted Booked; one that only reports a landing, or lists
# it as one example in a bracketed list, does not. Run through the engine's
# violations() in tools/ beside this set. REPLY_CHECK names another copy of
# the file to judge, so the old one can be shown failing.
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
TOOLS="$HERE/../.."
REPLY_CHECK="${REPLY_CHECK:-$TOOLS/../reply_check.json}"
PYTHONDONTWRITEBYTECODE=1 python3 - "$TOOLS" "$REPLY_CHECK" <<'PY'
import json, sys
sys.path.insert(0, sys.argv[1])
import precedent_reply_check as rc

reqs = [r for r in json.load(open(sys.argv[2], encoding='utf-8'))
        if r.get('id') == 'prompt-please-landing-authority']
assert len(reqs) == 1, 'the landing-authority pair is not in reply_check.json'
req = {'id': reqs[0]['id'], 'practice': reqs[0].get('practice'),
       'require_in_fence_paired_with': reqs[0]['require_in_fence_paired_with'][:1]}

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
