#!/usr/bin/env bash
# Two-direction test for tools/checks/check_landing_takes_a_pr.py: a push to
# the landing branch changing a workflow or a gating file is refused; an
# engine file matching its manifest is exempt, a workflow never is; a push
# elsewhere, and one with no push check behind it, is not judged.
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
CHECK="$HERE/../check_landing_takes_a_pr.py"
fail=0
tmp="$(mktemp -d)"; trap 'rm -rf "$tmp"' EXIT
g() { PRECEDENT_ALLOW_ANY_AUTHOR=1 git -C "$tmp" -c user.name=t -c user.email=t@t "$@"; }
g init -q -b staging
echo '{"landing_branch": "staging"}' > "$tmp/precedent.json"
mkdir -p "$tmp/tools" "$tmp/.github/workflows"
echo 'a' > "$tmp/tools/precedent_check.py"
g add -A; g commit -qm base; base="$(g rev-parse HEAD)"
run() { PRECEDENT_CHECK_ROOT="$tmp" PRECEDENT_PUSH_DESTINATION="$1" PRECEDENT_CHANGED_SINCE="$base" \
  python3 "$CHECK" >/dev/null 2>&1; echo $?; }
echo 'b' > "$tmp/tools/precedent_check.py"; g commit -qam gate
[ "$(run staging)" = 1 ] || { echo "FAIL: a changed gating file landing on staging was not refused"; fail=1; }
[ "$(run 2026-10-16-x-y-abcde-fghij)" = 2 ] || { echo "FAIL: a push to a work branch was judged"; fail=1; }
[ "$(PRECEDENT_CHECK_ROOT="$tmp" python3 "$CHECK" >/dev/null 2>&1; echo $?)" = 2 ] || { echo "FAIL: judged with no push check behind it"; fail=1; }
sha="$(sha256sum "$tmp/tools/precedent_check.py" | cut -d' ' -f1)"
printf '{"source_branch": "main", "sha256": {"precedent_check.py": "%s"}}\n' "$sha" > "$tmp/tools/ENGINE_MANIFEST.json"
g add -A; g commit -qm manifest
[ "$(run staging)" = 0 ] || { echo "FAIL: an engine file matching its manifest was refused"; fail=1; }
echo 'on: push' > "$tmp/.github/workflows/x.yml"; g add -A; g commit -qm wf
[ "$(run staging)" = 1 ] || { echo "FAIL: a new workflow landing on staging was not refused"; fail=1; }
[ "$(PRECEDENT_NO_LADDERS=1 run staging)" = 2 ] || { echo "FAIL: judged off the ladder"; fail=1; }
[ "$fail" = 0 ] && echo "PASS: check_landing_takes_a_pr"
exit "$fail"
