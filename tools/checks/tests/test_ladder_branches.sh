#!/usr/bin/env bash
# Test for tools/ladder/ladder_branches.py, this set's branch_moves: Promote,
# Produce and the wait on main's GitHub test. Moved from BestPractice's
# verify_harness.py with the moves on 2026-10-19; the cases are in
# ladder_branches_cases.py beside this file, which travels with it
# (2026-10-20: a test's <name>_cases.py helper ships with the test).
#
# Runs against the engine in tools/ beside it, or the one PRECEDENT_ENGINE_ROOT
# names. An engine older than the move still does these moves itself and never
# loads this file, so the cases wait for one that hands --promote to a set.
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
SET_ROOT="$(cd "$HERE/../../.." && pwd)"
ENGINE_ROOT="${PRECEDENT_ENGINE_ROOT:-$SET_ROOT}"
if ! grep -q "^MOVES_KEY = 'branch_moves'" "$ENGINE_ROOT/tools/precedent_branches.py" 2>/dev/null; then
  echo "N/A: ladder_branches -- the engine in $ENGINE_ROOT/tools still does Promote and Produce itself; these cases run once it hands them to this set"
  exit 0
fi
python3 "$HERE/ladder_branches_cases.py" || { echo "FAIL: ladder_branches"; exit 1; }
echo "PASS: ladder_branches"
