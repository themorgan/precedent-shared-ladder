#!/bin/bash

# A fixture commit is not a person's commit: the global commit backstop
# (commit-identity.sh, 2026-09-07) reaches the throwaway repositories
# this test builds and would refuse them.
export PRECEDENT_ALLOW_ANY_AUTHOR=1
# Fixture commits skip the machine's global commit hooks too: they are
# throwaway repositories, and running every hook on each of their commits
# was most of this test's time (2026-10-31 test review).
export GIT_CONFIG_COUNT=1 GIT_CONFIG_KEY_0=core.hooksPath GIT_CONFIG_VALUE_0=/dev/null
# Two-direction test for check_assorted_notes_is_deleted.py:
#   1. plant a link to ASSORTED_NOTES.md in an ordinary page -- it must fire;
#   2. plant links to files that merely END the same way (MARKETING_IDEAS.md,
#      RANDOM_NOTES.md) -- it must stay clean;
#   3. plant a README.md and a MAP.md listing ASSORTED_NOTES.md -- clean: a
#      plain list of files may name it;
#   4. a "## See also" link to it -- must FIRE now (strict, 2026-11-18: the
#      writing set's older check passed it, and a planning repo's session
#      moved links into See also because of that);
#   later cases, each with its own comment: the migration once
#   ASSORTED_NOTES.md exists, a catch-all outside content/, a headline-cased
#   See Also (fires), a link whose text is the file's own name (fires), a
#   link with a #fragment (fires), a map's source (clean), and the real,
#   current repo (clean).
set -euo pipefail
cd "$(dirname "$0")/../../.."
ROOT="$(pwd)"
SCRATCH="$(mktemp -d)"
trap 'rm -rf "$SCRATCH"' EXIT

git clone -q "$ROOT" "$SCRATCH"
cd "$SCRATCH"
git config user.name "Fixture Author"
git config user.email "fixture@example.com"
mkdir -p content
echo "whatever is on my mind" > content/ASSORTED_NOTES.md
mkdir -p docs
echo "See [the notes](../content/ASSORTED_NOTES.md) for why." > docs/planted-reference.md
git add content/ASSORTED_NOTES.md docs/planted-reference.md
git commit -q -m "planted violation: a doc links to ASSORTED_NOTES.md"

# Exit 1 exactly: a missing or crashing script (2) is not "fired".
if [ "$(python3 tools/checks/check_assorted_notes_is_deleted.py > /dev/null 2>&1; echo $?)" != 1 ]; then
  echo "FAIL: check_assorted_notes_is_deleted.py did not fire on a planted reference" >&2
  exit 1
fi
echo "ok: fires on planted violation"

cd "$ROOT"
SCRATCH2="$(mktemp -d)"
git clone -q "$ROOT" "$SCRATCH2"
(
  cd "$SCRATCH2"
  git config user.name "Fixture Author"
  git config user.email "fixture@example.com"
  mkdir -p content
  echo "marketing copy" > content/MARKETING_IDEAS.md
  echo "loose thoughts" > content/RANDOM_NOTES.md
  mkdir -p docs
  cat > docs/planted-non-reference.md <<'EOF'
Real links, to real files that just happen to end the same way:
[marketing](../content/MARKETING_IDEAS.md) and [notes](../content/RANDOM_NOTES.md).
EOF
  git add content/MARKETING_IDEAS.md content/RANDOM_NOTES.md docs/planted-non-reference.md
  git commit -q -m "planted non-violation: links to MARKETING_IDEAS.md and RANDOM_NOTES.md"
  if ! python3 tools/checks/check_assorted_notes_is_deleted.py > /dev/null; then
    echo "FAIL: check_assorted_notes_is_deleted.py fired on links to MARKETING_IDEAS.md/RANDOM_NOTES.md (false positive)" >&2
    exit 1
  fi
  echo "ok: stays clean on planted non-violation (MARKETING_IDEAS.md, RANDOM_NOTES.md)"
)
status=$?
rm -rf "$SCRATCH2"
if [ "$status" -ne 0 ]; then
  exit "$status"
fi

cd "$ROOT"
SCRATCH3="$(mktemp -d)"
git clone -q "$ROOT" "$SCRATCH3"
(
  cd "$SCRATCH3"
  git config user.name "Fixture Author"
  git config user.email "fixture@example.com"
  mkdir -p content
  echo "whatever is on my mind" > content/ASSORTED_NOTES.md
  cat > README.md <<'EOF'
# Scratch repo

- [content/ASSORTED_NOTES.md](content/ASSORTED_NOTES.md) -- notes with no obvious home elsewhere.
EOF
  cat > MAP.md <<'EOF'
# Map

| content/ASSORTED_NOTES.md | General notes, listed here for discoverability. |
|---|---|
| [content/ASSORTED_NOTES.md](content/ASSORTED_NOTES.md) | as above |
EOF
  git add content/ASSORTED_NOTES.md README.md MAP.md
  git commit -q -m "planted non-violation: README.md and MAP.md link to ASSORTED_NOTES.md"
  if ! python3 tools/checks/check_assorted_notes_is_deleted.py > /dev/null; then
    echo "FAIL: check_assorted_notes_is_deleted.py fired on a README.md/MAP.md listing link (false positive)" >&2
    exit 1
  fi
  echo "ok: stays clean on a README.md/MAP.md listing link"
)
status=$?
rm -rf "$SCRATCH3"
if [ "$status" -ne 0 ]; then
  exit "$status"
fi

cd "$ROOT"
SCRATCH4="$(mktemp -d)"
git clone -q "$ROOT" "$SCRATCH4"
(
  cd "$SCRATCH4"
  git config user.name "Fixture Author"
  git config user.email "fixture@example.com"
  mkdir -p content
  echo "whatever is on my mind" > content/ASSORTED_NOTES.md
  cat > docs-page.md <<'EOF'
# An ordinary page

See [the notes](content/ASSORTED_NOTES.md) for background on this claim.

## See also

- [content/ASSORTED_NOTES.md](content/ASSORTED_NOTES.md) -- related notes.
EOF
  git add content/ASSORTED_NOTES.md docs-page.md
  git commit -q -m "planted: an ordinary citation plus a See also link in one file"
  out="$(python3 tools/checks/check_assorted_notes_is_deleted.py || true)"
  if ! echo "$out" | grep -q "docs-page.md:3:"; then
    echo "FAIL: did not fire on the ordinary link" >&2
    echo "$out" >&2
    exit 1
  fi
  if ! echo "$out" | grep -q "docs-page.md:7:"; then
    echo "FAIL: did not fire on a See also link (See also is no longer exempt)" >&2
    echo "$out" >&2
    exit 1
  fi
  echo "ok: fires on both the ordinary link and the See also link"
)
status=$?
rm -rf "$SCRATCH4"
if [ "$status" -ne 0 ]; then
  exit "$status"
fi

# Once content/ASSORTED_NOTES.md exists the consolidation this practice
# describes has happened, and a legacy NAME is just a filename again. A repo
# with a real ASSORTED_NOTES.md was flagged for linking book-moses/NOTES.md,
# a manuscript brainstorm that is not its catch-all (2026-09-06).
SCRATCH5="$(mktemp -d)"
(
  set -e
  git clone -q "$ROOT" "$SCRATCH5"
  cd "$SCRATCH5"
  mkdir -p content book-moses
  echo "# Assorted notes" > content/ASSORTED_NOTES.md
  echo "# Moses notes" > book-moses/NOTES.md
  echo "See [the Moses notes](book-moses/NOTES.md) for that draft." > TODO.md
  git add -A
  git -c user.name="Test" -c user.email="test@example.com" commit -q -m "migrated repo, unrelated NOTES.md"
  if ! python3 tools/checks/check_assorted_notes_is_deleted.py > /dev/null; then
    echo "FAIL: fired on a legacy-named file in a repo that already has content/ASSORTED_NOTES.md" >&2
    exit 1
  fi
  echo "ok: legacy names stop counting once the migration is done"

  # ...and the canonical file is still guarded in that same repo, so the
  # case above cannot be met by a check that simply stopped running.
  echo "Per [the notes](content/ASSORTED_NOTES.md), we should ship it." > TODO.md
  git add -A
  git -c user.name="Test" -c user.email="test@example.com" commit -q -m "citation of the real notes file"
  # Exit 1 exactly: a missing or crashing script (2) is not "fired".
  if [ "$(python3 tools/checks/check_assorted_notes_is_deleted.py > /dev/null 2>&1; echo $?)" != 1 ]; then
    echo "FAIL: stopped guarding content/ASSORTED_NOTES.md itself" >&2
    exit 1
  fi
  echo "ok: still fires on a citation of the canonical notes file"
)
status=$?
rm -rf "$SCRATCH5"
if [ "$status" -ne 0 ]; then
  exit "$status"
fi

# The same migration test, in a repo whose catch-all is NOT under content/.
# `content/` is this practice's default directory, not its definition, and
# content-directory says an established layout wins over the default. A repo
# that renamed content/ (2026-09-07: one renamed it to business-modeling/ so
# every content directory said what it held) still has a migrated catch-all,
# and its unrelated NOTES.md is still just a filename.
SCRATCH6="$(mktemp -d)"
(
  set -e
  git clone -q "$ROOT" "$SCRATCH6"
  cd "$SCRATCH6"
  mkdir -p business-modeling book-moses
  echo "# Assorted notes" > business-modeling/ASSORTED_NOTES.md
  echo "# Moses notes" > book-moses/NOTES.md
  echo "See [the Moses notes](book-moses/NOTES.md) for that draft." > TODO.md
  git add -A
  git -c user.name="Test" -c user.email="test@example.com" commit -q -m "migrated repo, catch-all outside content/"
  if ! python3 tools/checks/check_assorted_notes_is_deleted.py > /dev/null; then
    echo "FAIL: fired on a legacy-named file in a repo whose ASSORTED_NOTES.md is outside content/" >&2
    exit 1
  fi
  echo "ok: the migration counts wherever the catch-all lives, not only under content/"

  # ...and the canonical file is still guarded at its new location, so the
  # case above cannot be met by a check that simply stopped running.
  echo "Per [the notes](business-modeling/ASSORTED_NOTES.md), we should ship it." > TODO.md
  git add -A
  git -c user.name="Test" -c user.email="test@example.com" commit -q -m "citation of the real notes file, outside content/"
  # Exit 1 exactly: a missing or crashing script (2) is not "fired".
  if [ "$(python3 tools/checks/check_assorted_notes_is_deleted.py > /dev/null 2>&1; echo $?)" != 1 ]; then
    echo "FAIL: stopped guarding ASSORTED_NOTES.md once it moved out of content/" >&2
    exit 1
  fi
  echo "ok: still fires on a citation of the catch-all at its new location"
)
status=$?
rm -rf "$SCRATCH6"
if [ "$status" -ne 0 ]; then
  exit "$status"
fi

# A headline-cased "## See Also" is no shelter either: the older check
# matched the heading case-insensitively to exempt it, and the strict check
# must not have kept that exemption by another spelling.
SCRATCH7="$(mktemp -d)"
(
  set -e
  git clone -q "$ROOT" "$SCRATCH7"
  cd "$SCRATCH7"
  mkdir -p content
  echo "# Assorted notes" > content/ASSORTED_NOTES.md
  cat > a-page.md <<'EOF'
# An ordinary page

## See Also

- [content/ASSORTED_NOTES.md](content/ASSORTED_NOTES.md) -- related notes.
EOF
  git add -A
  git -c user.name="Test" -c user.email="test@example.com" commit -q -m "See Also in headline case"
  # Exit 1 exactly: a missing or crashing script (2) is not "fired".
  if [ "$(python3 tools/checks/check_assorted_notes_is_deleted.py > /dev/null 2>&1; echo $?)" != 1 ]; then
    echo "FAIL: did not fire on a link in a headline-cased See Also footer" >&2
    exit 1
  fi
  echo "ok: fires on a See Also footer in headline case"
)
status=$?
rm -rf "$SCRATCH7"
if [ "$status" -ne 0 ]; then
  exit "$status"
fi

# A link whose own text is the notes file's name or path was exempt in the
# older check, as "naming the file, not citing it". The rule now forbids
# linking it at all, so every one of these fires -- and a #fragment link too,
# which the older check missed by reading "X.md#part" as a different name.
SCRATCH8="$(mktemp -d)"
(
  set -e
  git clone -q "$ROOT" "$SCRATCH8"
  cd "$SCRATCH8"
  mkdir -p content docs
  echo "# Assorted notes" > content/ASSORTED_NOTES.md
  cat > docs/names-the-file.md <<'EOF'
# A page that names the notes file

The one document this rule does not reach is [ASSORTED_NOTES.md](../content/ASSORTED_NOTES.md).
It lives at [content/ASSORTED_NOTES.md](../content/ASSORTED_NOTES.md), spelled from the root,
or at [`../content/ASSORTED_NOTES.md`](../content/ASSORTED_NOTES.md), spelled from here.
EOF
  git add -A
  git -c user.name="Test" -c user.email="test@example.com" commit -q -m "links that name the notes file"
  out="$(python3 tools/checks/check_assorted_notes_is_deleted.py || true)"
  for n in 3 4 5; do
    if ! grep -q "docs/names-the-file.md:$n:" <<<"$out"; then
      echo "FAIL: did not fire on line $n, a link whose text names the notes file" >&2
      echo "$out" >&2
      exit 1
    fi
  done
  echo "ok: a link naming the notes file itself fires"

  echo "Details are in [part two](../content/ASSORTED_NOTES.md#part-two)." >> docs/names-the-file.md
  git add -A
  git -c user.name="Test" -c user.email="test@example.com" commit -q -m "a link into the notes file with a fragment"
  out="$(python3 tools/checks/check_assorted_notes_is_deleted.py || true)"
  if ! grep -q "docs/names-the-file.md:6:" <<<"$out"; then
    echo "FAIL: did not fire on a #fragment link into the notes file" >&2
    echo "$out" >&2
    exit 1
  fi
  echo "ok: fires on a #fragment link into the notes file"
)
status=$?
rm -rf "$SCRATCH8"
if [ "$status" -ne 0 ]; then
  exit "$status"
fi

# A map written in its source: MAP.source.md, or a row file under
# MAP.source/, is copied word for word into MAP.md, so a listing link there
# is a listing link in the map. A consumer's link in MAP.source.md was
# flagged and main went red after a Produce (2026-10-19). Any other
# *.source.md is an ordinary page, and still fires.
cd "$ROOT"
SCRATCH9="$(mktemp -d)"
git clone -q "$ROOT" "$SCRATCH9"
(
  cd "$SCRATCH9"
  mkdir -p content MAP.source/0010-layout
  echo "whatever is on my mind" > content/ASSORTED_NOTES.md
  printf '# Map\n\nThe notes: [the notes](content/ASSORTED_NOTES.md).\n' > MAP.source.md
  echo "| [the notes](../../content/ASSORTED_NOTES.md) | notes |" > MAP.source/0010-layout/0010-notes.md
  git add content MAP.source.md MAP.source
  git -c user.name="Test" -c user.email="test@example.com" commit -q -m "a map's source lists the notes file"
  if ! python3 tools/checks/check_assorted_notes_is_deleted.py > /dev/null; then
    echo "FAIL: fired on a link in MAP.source.md or a MAP.source/ row (false positive)" >&2
    python3 tools/checks/check_assorted_notes_is_deleted.py >&2 || true
    exit 1
  fi
  echo "ok: stays clean on a map's source, file or directory form"
  printf 'See [the notes](content/ASSORTED_NOTES.md).\n' > PLAN.source.md
  git add PLAN.source.md
  git -c user.name="Test" -c user.email="test@example.com" commit -q -m "an ordinary page named .source.md cites the notes"
  out="$(python3 tools/checks/check_assorted_notes_is_deleted.py || true)"
  if ! grep -q "PLAN.source.md:1:" <<<"$out"; then
    echo "FAIL: stopped firing on a .source.md page that is no listing's source" >&2
    exit 1
  fi
  echo "ok: still fires on a .source.md page whose view is no listing"
)
status=$?
rm -rf "$SCRATCH9"
if [ "$status" -ne 0 ]; then
  exit "$status"
fi

if ! python3 tools/checks/check_assorted_notes_is_deleted.py > /dev/null; then
  echo "FAIL: check_assorted_notes_is_deleted.py is not clean on the real, current repo" >&2
  exit 1
fi
echo "ok: clean on real content"
