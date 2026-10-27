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
case "$out" in *"In the archive-line reply and the closing reply"*) ;; *) echo "FAIL: the note no longer rides with every archive line: $out"; fail=1;; esac
# 2026-10-20: a refresh only when the person asks, never for a landing alone
# and never before the answer, and the line bare.
case "$out" in *"only when the person asks for a fresh list"*"never because this session made, landed or merged a branch"*"only after the reply's answer is written"*) ;; *) echo "FAIL: the note no longer limits the rebuild to the person's ask: $out"; fail=1;; esac
case "$out" in *'"Branch cleanup"'*) ;; *) echo "FAIL: the note no longer names the word that asks for a refresh: $out"; fail=1;; esac
case "$out" in *"nothing else on that line"*) ;; *) echo "FAIL: the note no longer keeps the line bare: $out"; fail=1;; esac
# 2026-10-27: the rows live in the page's database. A refresh lists them,
# runs the tool and sends its batch; it never republishes the page, so it
# never asks for the page to be read through.
case "$out" in *"ArtifactData list of collection repos"*"--db-docs <scratchpad>/branch-db --versions"*"ArtifactData batch"*) ;; *) echo "FAIL: the note no longer gives the database refresh: $out"; fail=1;; esac
case "$out" in *"Never publish to the page's address for a refresh"*) ;; *) echo "FAIL: the note no longer forbids a republish for a refresh: $out"; fail=1;; esac
case "$out" in *"Read every line"*|*"--merge"*|*"--html"*) echo "FAIL: the note still describes the old read-through and merge: $out"; fail=1;; esac
stub 0 1; out="$(run)"
case "$out" in *"a repository's staging is waiting to go into main"*"--db-docs <scratchpad>/branch-db"*"rc=0") ;; *) echo "FAIL: waiting staging not said: $out"; fail=1;; esac
rm "$tmp/tools/precedent_stale_branches.py"; out="$(run)"
[ "$out" = "rc=0" ] || { echo "FAIL: with no engine it should say nothing and exit 0: $out"; fail=1; }
[ "$fail" = 0 ] && echo "PASS: branch_page_note"
exit "$fail"
