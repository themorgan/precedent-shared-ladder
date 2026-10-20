#!/usr/bin/env bash
# Test for tools/ladder/branch_page_note.py: it prints the note for every reply
# that says the session can be archived only when the engine's branch page has something on it, says nothing
# otherwise, and never fails -- not even with no engine beside it.
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
NOTE="$HERE/../../ladder/branch_page_note.py"
fail=0
tmp="$(mktemp -d)"; trap 'rm -rf "$tmp"' EXIT
mkdir -p "$tmp/tools/ladder"
cp "$NOTE" "$tmp/tools/ladder/"
stub() {  # $1 deletable branches, $2 staging waiting
  cat > "$tmp/tools/precedent_stale_branches.py" <<PY
PAGE_FILENAME = 'branch-cleanup.html'
def collect():
    return [('o', 'r', 'x', ['b'] * $1)], None
def collect_waiting():
    return ['r'] * $2
PY
}
# No bytecode cache: each stub is rewritten within the same second at the
# same size, and a cached copy of the last one would be read instead.
run() { PYTHONDONTWRITEBYTECODE=1 python3 "$tmp/tools/ladder/branch_page_note.py"; echo "rc=$?"; }
stub 0 0; out="$(run)"
[ "$out" = "rc=0" ] || { echo "FAIL: nothing to clean, yet it printed: $out"; fail=1; }
stub 2 0; out="$(run)"
case "$out" in *"some branches can be deleted (the page"*"rc=0") ;; *) echo "FAIL: deletable branches not said: $out"; fail=1;; esac
case "$out" in *"waiting to go into main"*) echo "FAIL: named a waiting staging that is not there"; fail=1;; esac
case "$out" in *'In EVERY reply that says "You can archive this session"'*) ;; *) echo "FAIL: the note no longer rides with every archive line: $out"; fail=1;; esac
stub 0 1; out="$(run)"
case "$out" in *"a repository's staging is waiting to go into main"*"--fetch --html <scratchpad>/branch-cleanup.html"*"rc=0") ;; *) echo "FAIL: waiting staging not said: $out"; fail=1;; esac
rm "$tmp/tools/precedent_stale_branches.py"; out="$(run)"
[ "$out" = "rc=0" ] || { echo "FAIL: with no engine it should say nothing and exit 0: $out"; fail=1; }
[ "$fail" = 0 ] && echo "PASS: branch_page_note"
exit "$fail"
