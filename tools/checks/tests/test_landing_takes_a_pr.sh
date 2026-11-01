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
# A check the sync materialized, byte for byte what MANIFEST.json recorded,
# is exempt; a hand-edited one is not, and neither is a repo's own check
# (2026-10-17: in a consumer tools/checks/ is the materialized catalogue, so
# counting all of it refused every sync).
g rm -q -r .github; g commit -qm "no workflow"; base="$(g rev-parse HEAD)"
mkdir -p "$tmp/tools/checks" "$tmp/local/tools/checks"
echo 'print(1)' > "$tmp/tools/checks/check_x.py"
s16="$(sha256sum "$tmp/tools/checks/check_x.py" | cut -c1-16)"
printf '{"checks": [{"path": "tools/checks/check_x.py", "sha256_16": "%s", "source": "some-set"}]}\n' "$s16" > "$tmp/MANIFEST.json"
g add -A; g commit -qm sync; synced="$(g rev-parse HEAD)"
[ "$(run staging)" = 0 ] || { echo "FAIL: a materialized check matching MANIFEST.json was refused"; fail=1; }
echo 'print(2)' > "$tmp/tools/checks/check_x.py"; g commit -qam "hand edit"; edited="$(g rev-parse HEAD)"
[ "$(run staging)" = 1 ] || { echo "FAIL: a hand-edited materialized check was not refused"; fail=1; }
g reset -q --hard "$synced"; echo 'x' > "$tmp/local/tools/checks/check_own.py"; g add -A; g commit -qm own; own="$(g rev-parse HEAD)"
[ "$(run staging)" = 1 ] || { echo "FAIL: a repo's own check landing on staging was not refused"; fail=1; }
# The same judgment at git's pre-push, which is where a landing meets it:
# the shipped guard reads the pushed commit, not the working tree.
GUARD="$HERE/../../landing_pr_guard.py"
hook() { printf 'refs/heads/w %s refs/heads/%s %s\n' "$1" "$2" "$base" \
  | (cd "$tmp" && PRECEDENT_USER_CONFIG="$tmp/none.json" PRECEDENT_ASSUME_LADDER=1 python3 "$GUARD" --pre-push >/dev/null 2>&1); echo $?; }
[ "$(hook "$synced" staging)" = 0 ] || { echo "FAIL: pre-push refused a sync's materialized check"; fail=1; }
[ "$(hook "$edited" staging)" = 1 ] || { echo "FAIL: pre-push let a hand-edited check onto staging"; fail=1; }
[ "$(hook "$own" staging)" = 1 ] || { echo "FAIL: pre-push let a repo's own check onto staging"; fail=1; }
[ "$(hook "$own" 2026-10-16-x-y-abcde-fghij)" = 0 ] || { echo "FAIL: pre-push judged a push to a work branch"; fail=1; }
[ "$(PRECEDENT_NO_LADDERS=1 hook "$own" staging)" = 0 ] || { echo "FAIL: pre-push judged off the ladder"; fail=1; }
# What the refusal says comes after the pull request (2026-10-18): never a
# bare "once its checks pass", since a repo may run no check on one. With
# the engine's pull_request_route_note it says what that reads from the
# workflows; without it, not to wait when none is listed.
said() { printf 'refs/heads/w %s refs/heads/staging %s\n' "$own" "$base" \
  | (cd "$tmp" && PRECEDENT_LANDING_SOURCE="${PRECEDENT_LANDING_SOURCE:-}" PRECEDENT_USER_CONFIG="$tmp/none.json" PRECEDENT_ASSUME_LADDER=1 python3 "$GUARD" --pre-push 2>&1 >/dev/null); }
# "Without the engine" is planted, not assumed: the guard's own folder may
# hold a vendored engine, which Python finds first (2026-10-19: this case
# failed wherever the engine sat beside the guard).
printf 'raise ImportError("no engine here")\n' > "$tmp/tools/precedent_branches.py"
said | grep -q 'straight away if the pull' || { echo "FAIL: without the engine, the refusal promised checks that may never start"; fail=1; }
printf 'def pull_request_route_note(root, base):\n    return "ROUTE NOTE FOR " + base\n' > "$tmp/tools/precedent_branches.py"
said | grep -q 'ROUTE NOTE FOR staging' || { echo "FAIL: the refusal did not use the engine's pull_request_route_note"; fail=1; }
# A push the land tool makes gets no note of the guard's own: the tool ran
# the quick checks and says what follows itself (2026-10-19: the guard said
# "Nothing has run the quick checks" right above the tool's "passed").
landed="$(PRECEDENT_LANDING_SOURCE=w said)"
echo "$landed" | grep -q 'ROUTE NOTE' && { echo "FAIL: a push from the land tool got the guard's own route note"; fail=1; }
echo "$landed" | grep -q 'land tool that made this push' || { echo "FAIL: a push from the land tool was not pointed at its note"; fail=1; }
# A file already on main, byte for byte, came through main's pull request
# (2026-10-30: a red-main fix merged into main went red again on this check
# at `--run-tests main` until it also reached staging). A workflow is still
# refused, and a file that differs from main's is still judged.
g update-ref refs/remotes/origin/main "$own"
[ "$(hook "$own" staging)" = 0 ] || { echo "FAIL: pre-push refused a check already on main by its pull request"; fail=1; }
[ "$(PRECEDENT_CHANGED_SINCE="$synced" run staging)" = 0 ] || { echo "FAIL: the check refused a check already on main by its pull request"; fail=1; }
echo 'y' > "$tmp/local/tools/checks/check_own.py"; g commit -qam "differs from main"; differs="$(g rev-parse HEAD)"
[ "$(hook "$differs" staging)" = 1 ] || { echo "FAIL: pre-push let through a check that differs from main's"; fail=1; }
mkdir -p "$tmp/.github/workflows"; echo 'on: push' > "$tmp/.github/workflows/y.yml"
g add -A; g commit -qm wf-main; wfm="$(g rev-parse HEAD)"; g update-ref refs/remotes/origin/main "$wfm"
[ "$(hook "$wfm" staging)" = 1 ] || { echo "FAIL: pre-push let a workflow through because main has it"; fail=1; }
g update-ref -d refs/remotes/origin/main
# The harness's area files are the code other work is judged by too
# (2026-10-31: BestPractice's verify_harness.py split into tools/harness/).
g reset -q --hard "$synced"; mkdir -p "$tmp/tools/harness"
echo 'def check_x(): pass' > "$tmp/tools/harness/vh_area.py"; g add -A; g commit -qm area; area="$(g rev-parse HEAD)"
[ "$(hook "$area" staging)" = 1 ] || { echo "FAIL: pre-push let a harness area file onto staging"; fail=1; }
g reset -q --hard "$synced"; echo 'PARTS = []' > "$tmp/tools/harness_parts.py"; g add -A; g commit -qm parts; parts="$(g rev-parse HEAD)"
[ "$(hook "$parts" staging)" = 1 ] || { echo "FAIL: pre-push let tools/harness_parts.py onto staging"; fail=1; }
[ "$fail" = 0 ] && echo "PASS: check_landing_takes_a_pr"
exit "$fail"
