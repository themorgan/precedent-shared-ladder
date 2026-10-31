#!/usr/bin/env bash
# practice: act -- claims this test, so a consuming repository receives it
# tools/precedent_branch_rules.py changes nothing for a person who has not
# opted in, and once opted in applies only to repositories that person's
# own GitHub account owns. GitHub is stubbed: nothing here reaches it.
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
TOOLS="$HERE/../.."
tmp="$(mktemp -d)"; trap 'rm -rf "$tmp"' EXIT
run() {  # $1 = user config JSON, rest = arguments
  printf '%s' "$1" > "$tmp/cfg.json"; shift
  ( cd "$tmp" && PRECEDENT_USER_CONFIG="$tmp/cfg.json" PRECEDENT_GITHUB_USER=octo python3 - "$TOOLS" "$@" <<'PY'
import sys
sys.path.insert(0, sys.argv[1])
import precedent_branch_rules as r
applied = []
r.status = lambda repo: ('missing', '')
r.apply = lambda repo: (applied.append(repo) or True, 'ok')
r.person_login = lambda: 'octo'
rc = r.main(sys.argv[2:])
print('APPLIED=' + ','.join(applied))
sys.exit(rc)
PY
  ) 2>&1; }
fail=0
out="$(run '{}' octo/a)"; rc=$?
[ "$rc" = 0 ] && grep -q "nothing is changed" <<<"$out" || { echo "FAIL: not opted in, the report should change nothing and exit 0: $out"; fail=1; }
out="$(run '{}' --apply octo/a)"; rc=$?
[ "$rc" = 2 ] || { echo "FAIL: not opted in, --apply should be refused (exit 2): $out"; fail=1; }
grep -q "APPLIED=octo" <<<"$out" && { echo "FAIL: applied without opting in"; fail=1; }
on='{"github_branch_rules": true}'
out="$(run "$on" --apply octo/a)"
grep -q "APPLIED=octo/a" <<<"$out" || { echo "FAIL: opted in, own repository not applied: $out"; fail=1; }
out="$(run "$on" --apply someone-else/b)"
grep -q "APPLIED=someone-else" <<<"$out" && { echo "FAIL: applied to a repository the person does not own"; fail=1; }
grep -q "not owned by octo" <<<"$out" || { echo "FAIL: refusal for another owner's repository not said: $out"; fail=1; }
[ "$fail" = 0 ] && echo "PASS: precedent_branch_rules opt-in"
exit "$fail"
