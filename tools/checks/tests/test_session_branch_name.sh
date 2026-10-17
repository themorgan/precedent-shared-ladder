#!/usr/bin/env bash
# Two-direction test for tools/checks/check_session_branch_name.py:
# it fires on a checkout sitting on a harness-named branch, stays quiet on
# a tool-made name (anyone's, any session's), fires on a hand-made one, skips
# a detached HEAD, and judges nothing off the ladder; and the shipped guard
# refuses at pre-push what the check flags.
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
CHECK="$HERE/../check_session_branch_name.py"
fail=0
tmp="$(mktemp -d)"; trap 'rm -rf "$tmp"' EXIT
git -C "$tmp" init -q -b main
PRECEDENT_ALLOW_ANY_AUTHOR=1 git -C "$tmp" -c user.name=t -c user.email=t@t commit -q --allow-empty -m x
run() { PRECEDENT_CHECK_ROOT="$tmp" python3 "$CHECK" >/dev/null 2>&1; echo $?; }
git -C "$tmp" checkout -q -b claude/peaceful-ritchie-3u31td
[ "$(run)" = 1 ] || { echo "FAIL: a harness-named branch was not flagged"; fail=1; }
[ "$(PRECEDENT_NO_LADDERS=1 run)" = 0 ] || { echo "FAIL: off the ladder it still judged"; fail=1; }
git -C "$tmp" branch -q -m 2026-10-16-octo-some-work-ab1cd-x9y8z
[ "$(run)" = 0 ] || { echo "FAIL: a tool-made name was flagged"; fail=1; }
git -C "$tmp" branch -q -m 2026-10-16-some-work
[ "$(run)" = 1 ] || { echo "FAIL: a hand-made name was not flagged"; fail=1; }
GUARD="$HERE/../../branch_name_guard.py"
Z=0000000000000000000000000000000000000000; S=1111111111111111111111111111111111111111
push() { printf 'refs/heads/x %s refs/heads/%s %s\n' "$S" "$1" "$2" \
  | CLAUDE_CODE_REMOTE_SESSION_ID=session_0abcde PRECEDENT_GITHUB_USER=octo python3 "$GUARD" --pre-push >/dev/null 2>&1; echo $?; }
[ "$(push claude/peaceful-ritchie-3u31td $Z)" = 1 ] || { echo "FAIL: pre-push let a new harness-named branch through"; fail=1; }
[ "$(push claude/peaceful-ritchie-3u31td $S)" = 1 ] || { echo "FAIL: pre-push let a push to an existing harness-named branch through"; fail=1; }
[ "$(push 2026-10-16-some-work $Z)" = 1 ] || { echo "FAIL: pre-push let a new hand-made name through"; fail=1; }
[ "$(push staging $S)" = 0 ] || { echo "FAIL: pre-push judged a tier branch"; fail=1; }
[ "$(PRECEDENT_NO_LADDERS=1 push claude/peaceful-ritchie-3u31td $Z)" = 0 ] || { echo "FAIL: pre-push judged off the ladder"; fail=1; }
# What is landed, not only where (2026-10-17): a push to staging or main is
# judged by the branch it comes from -- the local ref, or the branch --land
# names in PRECEDENT_LANDING_SOURCE -- so harness-named work is never Booked.
land() { printf '%s %s refs/heads/%s %s\n' "$1" "$S" "$2" "$S" \
  | PRECEDENT_LANDING_SOURCE="${3:-}" CLAUDE_CODE_REMOTE_SESSION_ID=session_0abcde PRECEDENT_GITHUB_USER=octo python3 "$GUARD" --pre-push >/dev/null 2>&1; echo $?; }
[ "$(land refs/heads/claude/peaceful-ritchie-3u31td staging)" = 1 ] || { echo "FAIL: a push of a harness-named branch to staging was let through"; fail=1; }
[ "$(land "$S" staging claude/peaceful-ritchie-3u31td)" = 1 ] || { echo "FAIL: --land of a harness-named branch was let through"; fail=1; }
[ "$(land "$S" main 2026-10-16-some-work)" = 1 ] || { echo "FAIL: a landing of a hand-made name was let through"; fail=1; }
[ "$(land "$S" staging 2026-10-16-alex-some-work-ab1cd-x9y8z)" = 0 ] || { echo "FAIL: --land of a tool-made name, another person's, was refused"; fail=1; }
[ "$(land refs/heads/claude/peaceful-ritchie-3u31td 2026-10-16-octo-some-work-ab1cd-x9y8z)" = 0 ] || { echo "FAIL: a rename on push, to a work branch, was refused"; fail=1; }
[ "$(PRECEDENT_NO_LADDERS=1 land "$S" staging claude/peaceful-ritchie-3u31td)" = 0 ] || { echo "FAIL: a landing was judged off the ladder"; fail=1; }
# Said at session start (2026-10-17): a checkout on a harness name, or one
# a level below where the session is rooted, gets the note; a tool-made name
# and a session with no ID get none.
start() { CLAUDE_PROJECT_DIR="$1" CLAUDE_CODE_REMOTE_SESSION_ID="${2-session_0abcde}" python3 "$GUARD" --session-start 2>/dev/null; }
git -C "$tmp" branch -q -m claude/peaceful-ritchie-3u31td
start "$tmp" | grep -q 'follow this one' || { echo "FAIL: no session-start note on a harness-named branch"; fail=1; }
up="$(mktemp -d)"; ln -s "$tmp" "$up/repo"
start "$up" | grep -q 'claude/peaceful-ritchie-3u31td' || { echo "FAIL: no note for a checkout below the session root"; fail=1; }
rm -rf "$up"
[ -z "$(start "$tmp" '')" ] || { echo "FAIL: a note with no cloud session"; fail=1; }
[ -z "$(PRECEDENT_NO_LADDERS=1 start "$tmp")" ] || { echo "FAIL: a session-start note off the ladder"; fail=1; }
git -C "$tmp" branch -q -m 2026-10-16-octo-some-work-ab1cd-x9y8z
[ -z "$(start "$tmp")" ] || { echo "FAIL: a session-start note on a tool-made name"; fail=1; }
git -C "$tmp" checkout -q --detach
[ "$(run)" = 2 ] || { echo "FAIL: a detached HEAD was not reported as SKIPPED"; fail=1; }
[ "$fail" = 0 ] && echo "PASS: check_session_branch_name"
exit "$fail"
