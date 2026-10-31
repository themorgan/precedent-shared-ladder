#!/bin/bash

# A fixture commit is not a person's commit: the global commit backstop
# (commit-identity.sh, 2026-09-07) reaches the throwaway repositories
# this test builds and would refuse them.
export PRECEDENT_ALLOW_ANY_AUTHOR=1
# The same backstop runs bootstrap/pre-commit-fix, which would bump the very
# headers these cases leave unbumped on purpose.
export PRECEDENT_SKIP_COMMIT_FIX=1
# Two-direction test for check_file_header.py, both planted violations it's
# meant to catch:
#   A. content changed but the version wasn't bumped;
#   B. the header line is malformed.
# Plus a planted NON-violation it must NOT catch:
#   C. vendored third-party content with its own, different, complete
#      attribution convention that happens to start "<!-- Last updated:"
#      too -- not this practice's business (real incident: this check used
#      to flag every such file as a malformed attempt at the person's header).
# Then: the real, current, unplanted repo must stay clean.
set -euo pipefail
cd "$(dirname "$0")/../../.."
ROOT="$(pwd)"

# The check under test is THIS checkout's working-tree copy, run against each
# scratch clone -- never the clone's own copy. `git clone` carries committed
# state only, so a clone's tools/checks/check_file_header.py is whatever HEAD
# has, and an uncommitted change to the check was tested against the new
# cases with the old script. Seen 2026-09-28 in a consumer's Update Vendors,
# which runs the changed-files check before its commit: "a merge bringing in
# a file added and bumped on the other side stays clean" failed, and passed
# the moment the update was committed. PRECEDENT_CHECK_ROOT is the check's own
# way of auditing a directory other than the one it sits in.
CHECK_UNDER_TEST="$ROOT/tools/checks/check_file_header.py"

# WHOSE header: the person comes from their own identity.json, never from a
# constant in the check (2026-10-31). Every case below runs as a fictional
# person whose individual set is a fixture this test writes, so the result
# never depends on whoever runs the suite -- the container's own user config
# would otherwise name a real person. No PRECEDENT_COMMIT_* override either:
# it outranks identity.json and would hide the path under test.
unset PRECEDENT_COMMIT_EMAIL PRECEDENT_COMMIT_NAME PRECEDENT_COMMIT_TZ
IDENTITIES="$(mktemp -d)"
make_person() {   # make_person DIR NAME ZONE -> a user config naming that set
  mkdir -p "$IDENTITIES/$1"
  printf '{"format_version": 1, "name": "%s", "email": "%s@example.invalid", "timezone": "%s"}\n' \
    "$2" "$1" "$3" > "$IDENTITIES/$1/identity.json"
  printf '{"format_version": 1, "individual": {"name": "%s", "path": "%s"}}\n' \
    "$1" "$IDENTITIES/$1" > "$IDENTITIES/$1.config.json"
  echo "$IDENTITIES/$1.config.json"
}
PAT_CONFIG="$(make_person pat "Pat Example" "Europe/Lisbon")"
SAM_CONFIG="$(make_person sam "Sam Sample" "Asia/Tokyo")"
NOBODY_CONFIG="$IDENTITIES/nobody.config.json"   # never written: no identity
export PRECEDENT_USER_CONFIG="$PAT_CONFIG"
check_under_test() {
  PRECEDENT_CHECK_ROOT="$PWD" python3 "$CHECK_UNDER_TEST" "$@"
}

# Every case plants into a document THIS TEST commits first, never into the
# host repo's README.md. The test is materialized into consuming repos, and it
# used to assume their README.md carried this header, as one set's did.
# One consumer's did not (2026-09-27): the "content changed, version not
# bumped" edit landed in a file the check has no business judging, the check
# rightly stayed silent, and the case failed with nothing wrong in the check.
# Called inside a scratch clone, after its identity is configured. `add -f`
# for the same reason as the vendor/ case below.
plant_doc() {
  printf '<!-- Last updated: 2026-09-27 10:00:00 (Lisbon) by Pat Example, to version 1 -->\n\nA versioned document this test plants and owns.\n' > PLANTED_DOC.md
  git add -f PLANTED_DOC.md
  TZ="Europe/Lisbon" git commit -q -m "plant a versioned document for the test"
}

run_case() {
  local label="$1"
  local mutate="$2"
  local scratch
  scratch="$(mktemp -d)"
  git clone -q "$ROOT" "$scratch"
  (
    cd "$scratch"
    # NEVER mutate the repo under test. On 2026-09-22 a case added here ran
    # its `eval "$mutate"` against the real working tree and rewrote this
    # repo's own README.md header; `git status` caught it, nothing in the
    # suite did. A wrong cwd is now a loud failure instead of a silent edit.
    if [[ "$PWD" == "$ROOT" ]]; then
      echo "FAIL: mutation for '"'"'$label'"'"' would run in the real repo" >&2
      exit 1
    fi
    git config user.name "Pat Example"
    git config user.email "pat@example.invalid"
    plant_doc
    eval "$mutate"
    TZ="Europe/Lisbon" git commit -q -am "planted violation: $label"
    if check_under_test > /dev/null; then
      echo "FAIL: check_file_header.py did not fire on: $label" >&2
      exit 1
    fi
    echo "ok: fires on planted violation ($label)"
  )
  local status=$?
  rm -rf "$scratch"
  return $status
}

run_clean_case() {
  local label="$1"
  local mutate="$2"
  local scratch
  scratch="$(mktemp -d)"
  git clone -q "$ROOT" "$scratch"
  (
    cd "$scratch"
    # NEVER mutate the repo under test. On 2026-09-22 a case added here ran
    # its `eval "$mutate"` against the real working tree and rewrote this
    # repo's own README.md header; `git status` caught it, nothing in the
    # suite did. A wrong cwd is now a loud failure instead of a silent edit.
    if [[ "$PWD" == "$ROOT" ]]; then
      echo "FAIL: mutation for '"'"'$label'"'"' would run in the real repo" >&2
      exit 1
    fi
    git config user.name "Pat Example"
    git config user.email "pat@example.invalid"
    plant_doc
    eval "$mutate"
    TZ="Europe/Lisbon" git commit -q -am "planted non-violation: $label"
    if ! check_under_test > /dev/null; then
      echo "FAIL: check_file_header.py fired on a non-violation: $label (false positive)" >&2
      exit 1
    fi
    echo "ok: stays clean on planted non-violation ($label)"
  )
  local status=$?
  rm -rf "$scratch"
  return $status
}

run_case "content changed, version not bumped" '
python3 - <<PY
import pathlib
p = pathlib.Path("PLANTED_DOC.md")
lines = p.read_text().splitlines()
lines.append("Planted content change without a version bump.")
p.write_text("\n".join(lines) + "\n")
PY
'

run_case "malformed header line" '
python3 - <<PY
import pathlib
p = pathlib.Path("PLANTED_DOC.md")
lines = p.read_text().splitlines()
lines[0] = "<!-- Last updated: 2026-08-31 by Pat Example, to version 2 -->"
p.write_text("\n".join(lines) + "\n")
PY
'

# `git add -f`, not `git add`: this test is materialized into consuming repos,
# and a PHP one ignores /vendor/ (Composer's folder), so a plain add is refused
# there and the test died before it reached the check (2026-09-25). It passed
# in this repo only because nothing here ignores vendor/.
run_clean_case "vendored file with its own, different, complete attribution" '
mkdir -p vendor
cat > vendor/THIRD_PARTY.md <<EOF
<!-- Last updated: 2026-01-01 10:00:00 (Some Other Zone) by Someone Else, to version 1 -->

Vendored content with its own header convention, not this person'"'"'s.
EOF
git add -f vendor/THIRD_PARTY.md
'

# A rename is not a creation. `git show HEAD~1:<new path>` fails for a
# renamed file, which used to read as "no parent" and demand the version
# counter restart at 1 -- twelve false positives in one consuming repo's
# single `git mv` of its content directory (2026-09-07).
run_clean_case "a versioned document renamed, not created" '
git mv PLANTED_DOC.md RENAMED_DOC.md
'

# A merge is judged against the side a file came from, both directions
# (2026-09-26). A Promote is one merge commit of a whole batch onto staging,
# so a document added on the branch below and bumped there is absent from the
# first parent; reading only HEAD~1 called it "new at version 2, expected 1"
# and refused the Promote. A file that NEITHER parent has is still new, and
# still has to start at 1.
merge_case() {
  local label="$1" expect="$2" newfile_version="$3" add_on_side="$4"
  local scratch
  scratch="$(mktemp -d)"
  git clone -q "$ROOT" "$scratch"
  (
    cd "$scratch"
    if [[ "$PWD" == "$ROOT" ]]; then
      echo "FAIL: merge case '$label' would run in the real repo" >&2
      exit 1
    fi
    git config user.name "Pat Example"
    git config user.email "pat@example.invalid"
    export TZ="Europe/Lisbon"
    base="$(git rev-parse HEAD)"
    git checkout -q -b side
    if [[ "$add_on_side" == yes ]]; then
      printf '<!-- Last updated: 2026-09-26 10:00:00 (Lisbon) by Pat Example, to version 1 -->\n\nFirst draft.\n' > MERGED_NOTES.md
      git add MERGED_NOTES.md
      git commit -q -m "add notes at version 1"
      printf '<!-- Last updated: 2026-09-26 11:00:00 (Lisbon) by Pat Example, to version 2 -->\n\nSecond draft.\n' > MERGED_NOTES.md
      git commit -q -am "notes to version 2"
    else
      printf 'side-only change\n' > SIDE_ONLY.txt
      git add SIDE_ONLY.txt
      git commit -q -m "side change"
    fi
    git checkout -q -B trunk "$base"
    printf 'trunk-only change\n' > TRUNK_ONLY.txt
    git add TRUNK_ONLY.txt
    git commit -q -m "trunk change"
    git merge -q --no-ff --no-commit side
    if [[ "$add_on_side" != yes ]]; then
      printf '<!-- Last updated: 2026-09-26 12:00:00 (Lisbon) by Pat Example, to version %s -->\n\nBorn in the merge.\n' "$newfile_version" > MERGED_NOTES.md
      git add MERGED_NOTES.md
    fi
    git commit -q -m "merge side into trunk"
    if check_under_test > out.txt; then result=clean; else result=fired; fi
    if [[ "$expect" == clean && "$result" != clean ]]; then
      echo "FAIL: check_file_header.py fired on a merge that only brought in a versioned file (false positive): $label" >&2
      cat out.txt >&2
      exit 1
    fi
    if [[ "$expect" == fired ]] && ! grep -q "MERGED_NOTES.md: header is new in this commit but starts at version $newfile_version, expected 1" out.txt; then
      echo "FAIL: check_file_header.py did not report a file new in the merge itself: $label" >&2
      cat out.txt >&2
      exit 1
    fi
    echo "ok: $label"
  )
  local status=$?
  rm -rf "$scratch"
  return $status
}
merge_case "a merge bringing in a file added and bumped on the other side stays clean" clean 2 yes
merge_case "a file new in the merge itself still has to start at version 1" fired 4 no

# THE 2026-09-22 CHANGE, both directions. `N` is monotonic, not a successor
# function: a bump with no content change is how a MISSED bump gets caught up,
# and refusing it left PR #191's README.md permanently unfixable -- the content
# change was already in an earlier commit, so no later commit could carry the
# bump. What must still fire is a version going DOWN, and (above) a content
# change with no bump at all.
#
# THESE THREE BUILD THEIR OWN SCRATCH CLONES rather than calling run_case /
# run_clean_case, and that is deliberate. On 2026-09-22 a first draft of them
# went through those helpers and their `eval "$mutate"` ran against the REAL
# working tree instead of the clone -- it rewrote this repo's own README.md
# header to version 1 and appended a test line to it. Caught by `git status`
# before the commit. The helpers now refuse to run a mutation outside a
# scratch clone (see the guard in each), but a test that does its own cd,
# inline and visible, cannot have that class of accident at all.
assert_scratch() {
  # Belt and braces: never mutate the repository the suite is testing.
  if [[ "$PWD" == "$ROOT" ]]; then
    echo "FAIL: a test case is about to mutate the real repo at $ROOT" >&2
    exit 1
  fi
}

SCRATCH_MONO="$(mktemp -d)"
git clone -q "$ROOT" "$SCRATCH_MONO"
(
  cd "$SCRATCH_MONO"
  assert_scratch
  git config user.name "Pat Example"
  git config user.email "pat@example.invalid"
  plant_doc

  # (1) catch-up bump, no content change -- must be CLEAN.
  python3 - <<'PYMONO'
import pathlib, re
p = pathlib.Path("PLANTED_DOC.md")
lines = p.read_text().splitlines()
n = int(re.search(r"version (\d+)", lines[0]).group(1))
lines[0] = re.sub(r"version \d+", "version %d" % (n + 1), lines[0])
p.write_text("\n".join(lines) + "\n")
PYMONO
  TZ="Europe/Lisbon" git commit -q -am "catch-up bump, no content change"
  if ! check_under_test > /dev/null; then
    echo "FAIL: check_file_header.py fired on a catch-up bump, which is how a missed bump is repaired" >&2
    exit 1
  fi
  echo "ok: stays clean on a catch-up bump with no content change"

  # (2) version going DOWN -- must FIRE, content change or not.
  python3 - <<'PYBACK'
import pathlib, re
p = pathlib.Path("PLANTED_DOC.md")
lines = p.read_text().splitlines()
lines[0] = re.sub(r"version \d+", "version 1", lines[0])
lines.append("A content change, so only the DIRECTION of N is under test.")
p.write_text("\n".join(lines) + "\n")
PYBACK
  TZ="Europe/Lisbon" git commit -q -am "version goes backwards"
  if check_under_test > /dev/null; then
    echo "FAIL: check_file_header.py did not fire on a version going backwards" >&2
    exit 1
  fi
  echo "ok: fires on planted violation (version going backwards)"
)
rm -rf "$SCRATCH_MONO"

# (3) --fix repairs the WORKING TREE before the commit, which is the only
# moment a repair is possible.
SCRATCH_FIX="$(mktemp -d)"
git clone -q "$ROOT" "$SCRATCH_FIX"
(
  cd "$SCRATCH_FIX"
  assert_scratch
  git config user.name "Pat Example"
  git config user.email "pat@example.invalid"
  plant_doc
  before="$(head -1 PLANTED_DOC.md)"
  printf 'A real edit, with no hand-written version bump.\n' >> PLANTED_DOC.md
  check_under_test --fix > /dev/null
  if [[ "$before" == "$(head -1 PLANTED_DOC.md)" ]]; then
    echo "FAIL: --fix did not stamp a file whose body changed" >&2
    exit 1
  fi
  TZ="Europe/Lisbon" git commit -q -am "edit stamped by --fix"
  if ! check_under_test > /dev/null; then
    echo "FAIL: a commit stamped by --fix is not clean" >&2
    exit 1
  fi
  check_under_test --fix > /dev/null
  if [[ -n "$(git status --porcelain)" ]]; then
    echo "FAIL: --fix touched a file whose body had not changed" >&2
    exit 1
  fi
  echo "ok: --fix stamps a changed file, and is a no-op on a clean tree"
)
rm -rf "$SCRATCH_FIX"

# (3b) --fix-staged is what bootstrap/pre-commit-fix runs before every commit:
# it bumps a changed file IN THE INDEX, never sweeps an unstaged edit into the
# commit, and leaves a header it did not write in the exact format alone.
SCRATCH_STAGED="$(mktemp -d)"
git clone -q "$ROOT" "$SCRATCH_STAGED"
(
  cd "$SCRATCH_STAGED"
  assert_scratch
  git config user.name "Pat Example"
  git config user.email "pat@example.invalid"
  plant_doc
  printf '<!-- Last updated: 2026-09-04 (an older format) Pat Example -->\n\nold\n' > OLD_FORMAT.md
  git add -f OLD_FORMAT.md
  TZ="Europe/Lisbon" git commit -q -m "plant an older-format header"
  printf 'A staged edit.\n' >> PLANTED_DOC.md
  printf 'Also staged.\n' >> OLD_FORMAT.md
  git add -f PLANTED_DOC.md OLD_FORMAT.md
  printf 'An unstaged edit.\n' >> PLANTED_DOC.md
  PRECEDENT_CHECK_ROOT="$PWD" check_under_test --fix-staged 2> /dev/null
  if ! git show :PLANTED_DOC.md | head -1 | grep -q 'to version 2 -->'; then
    echo "FAIL: --fix-staged did not bump a staged, changed file in the index" >&2
    exit 1
  fi
  if git show :PLANTED_DOC.md | grep -q 'An unstaged edit'; then
    echo "FAIL: --fix-staged swept an unstaged edit into the commit" >&2
    exit 1
  fi
  if [[ "$(head -1 PLANTED_DOC.md)" != "$(git show :PLANTED_DOC.md | head -1)" ]]; then
    echo "FAIL: --fix-staged left the working tree showing the bump undone" >&2
    exit 1
  fi
  if ! git show :OLD_FORMAT.md | head -1 | grep -q 'an older format'; then
    echo "FAIL: --fix-staged rewrote a header that was not in the exact format" >&2
    exit 1
  fi
  # The check rightly calls an older-format header malformed; that fixture
  # has done its job, so it leaves before the commit is judged.
  git rm -q -f OLD_FORMAT.md
  TZ="Europe/Lisbon" git commit -q -m "edit stamped by --fix-staged"
  if ! check_under_test > /dev/null; then
    echo "FAIL: a commit stamped by --fix-staged is not clean" >&2
    exit 1
  fi
  echo "ok: --fix-staged bumps only what is staged, in the index, and only exact-format headers"
)
rm -rf "$SCRATCH_STAGED"

# (3c) --fix-staged leaves a SYNCED COPY alone: a file a process/manifest*.json
# records as kept in step with upstream (status "synced", whole file).
# practice_audit.py holds it to its recorded hash, so a stamp is DRIFT and the
# landing is refused (a consumer's GETTING_STARTED.md, 2026-10-15). Its own
# manifest file, so a consumer's real process/manifest.json is never touched.
SCRATCH_SYNCED="$(mktemp -d)"
git clone -q "$ROOT" "$SCRATCH_SYNCED"
(
  cd "$SCRATCH_SYNCED"
  assert_scratch
  git config user.name "Pat Example"
  git config user.email "pat@example.invalid"
  plant_doc
  mkdir -p process
  printf '{"upstream": {}, "entries": [{"practice": "t", "local_path": "PLANTED_DOC.md", "granularity": "file", "status": "synced"}]}\n' \
    > process/manifest_header_test.json
  git add -f process/manifest_header_test.json
  TZ="Europe/Lisbon" git commit -q -m "record the planted document as a synced copy"
  printf 'A staged edit to a synced copy.\n' >> PLANTED_DOC.md
  git add -f PLANTED_DOC.md
  PRECEDENT_CHECK_ROOT="$PWD" check_under_test --fix-staged 2> /dev/null
  if ! git show :PLANTED_DOC.md | head -1 | grep -q 'to version 1 -->'; then
    echo "FAIL: --fix-staged stamped a file a manifest records as a synced copy" >&2
    exit 1
  fi
  TZ="Europe/Lisbon" git commit -q -m "edit a synced copy"
  if ! check_under_test > /dev/null; then
    echo "FAIL: the check judged a synced copy's header, which upstream owns" >&2
    exit 1
  fi
  echo "ok: a synced copy is neither stamped nor judged"
)
rm -rf "$SCRATCH_SYNCED"

# (3b) --fix ALSO catches up a file whose current HEAD already violates
# against ITS parent, even with nothing pending in the working tree -- the
# shape an edit made outside any session (a GitHub-web commit, say) leaves
# behind: content changed, header never bumped, and nobody has touched the
# file since to trip the ordinary "body differs from HEAD" path above.
SCRATCH_CATCHUP="$(mktemp -d)"
git clone -q "$ROOT" "$SCRATCH_CATCHUP"
(
  cd "$SCRATCH_CATCHUP"
  assert_scratch
  git config user.name "Pat Example"
  git config user.email "pat@example.invalid"
  plant_doc

  # Simulate the outside edit: content changes, header untouched -- exactly
  # what a GitHub web-UI commit looks like, since nothing there runs --fix.
  printf 'An edit made outside any session, header left unbumped.\n' >> PLANTED_DOC.md
  TZ="Europe/Lisbon" git commit -q -am "outside edit, no bump"
  if check_under_test > /dev/null; then
    echo "FAIL: setup did not actually plant a violation" >&2
    exit 1
  fi
  if [[ -n "$(git status --porcelain)" ]]; then
    echo "FAIL: test setup left the working tree dirty" >&2
    exit 1
  fi

  check_under_test --fix > /dev/null
  if [[ -z "$(git status --porcelain)" ]]; then
    echo "FAIL: --fix did not catch up a HEAD-only violation with nothing pending" >&2
    exit 1
  fi
  TZ="Europe/Lisbon" git commit -q -am "catch-up bump for the outside edit"
  if ! check_under_test > /dev/null; then
    echo "FAIL: the catch-up commit is not clean" >&2
    exit 1
  fi
  echo "ok: --fix catches up a HEAD-only violation left by an edit outside a session"
)
rm -rf "$SCRATCH_CATCHUP"

# (4) --fix REFUSES where it cannot resolve the person, rather than stamping
# the container's clock under a place label the header spells literally.
# Morgan, 2026-09-22: the label is literal, so a guessed stamp is wrong and
# unfalsifiable at the same time, and a header left unstamped is now
# recoverable because N is monotonic. Since 2026-10-31 name and zone come
# through precedent_identity.py, so that is the module this checkout lacks.
SCRATCH_TZ="$(mktemp -d)"
git clone -q "$ROOT" "$SCRATCH_TZ"
(
  cd "$SCRATCH_TZ"
  assert_scratch
  git config user.name "Pat Example"
  git config user.email "pat@example.invalid"
  plant_doc
  rm -f tools/precedent_identity.py      # what a consumer that vendors
  git add -A                             # tools/checks/ without tools/ has
  git -c user.name="Test" -c user.email="test@example.com" \
    commit -q -m "a checkout with no precedent_identity.py"

  before="$(head -1 PLANTED_DOC.md)"
  printf 'An edit in a checkout that cannot resolve a zone.\n' >> PLANTED_DOC.md

  # This case is about what sits BESIDE the check, so the working-tree copy
  # runs from inside the clone, where precedent_time.py is missing.
  cp "$CHECK_UNDER_TEST" tools/checks/check_file_header.py
  OUT="$(python3 tools/checks/check_file_header.py --fix 2>&1)" && RC=0 || RC=$?
  if [[ "$RC" -eq 0 ]]; then
    echo "FAIL: --fix exited 0 in a checkout with no precedent_identity.py" >&2
    echo "$OUT" >&2
    exit 1
  fi
  if ! grep -q "REFUSED" <<<"$OUT" \
     || ! grep -q "precedent_identity.py is not importable" <<<"$OUT"; then
    echo "FAIL: --fix did not say WHY it refused -- a bare non-zero exit reads as a crash" >&2
    echo "$OUT" >&2
    exit 1
  fi
  if [[ "$before" != "$(head -1 PLANTED_DOC.md)" ]]; then
    echo "FAIL: --fix stamped a header anyway after refusing" >&2
    exit 1
  fi
  echo "ok: --fix refuses, says why, and stamps nothing when the person is unresolvable"
)
rm -rf "$SCRATCH_TZ"

# (5) THE NAME AND THE PLACE ARE THE PERSON'S, read from their identity.json
# (2026-10-31). Before that the check spelled one person's name and city as
# constants, in a public set any team declares. The same edit, stamped as two
# different people, must carry each one's own name and place -- a constant
# in the script could satisfy one of the two, never both.
stamp_as() {   # stamp_as CONFIG -> the header --fix writes for that person
  local scratch
  scratch="$(mktemp -d)"
  git clone -q "$ROOT" "$scratch"
  (
    cd "$scratch"
    assert_scratch
    git config user.name "Pat Example"
    git config user.email "pat@example.invalid"
    plant_doc
    printf 'An edit to be stamped.\n' >> PLANTED_DOC.md
    PRECEDENT_USER_CONFIG="$1" check_under_test --fix > /dev/null
    head -1 PLANTED_DOC.md
  )
  rm -rf "$scratch"
}
PAT_LINE="$(stamp_as "$PAT_CONFIG")"
SAM_LINE="$(stamp_as "$SAM_CONFIG")"
if [[ "$PAT_LINE" != *"(Lisbon) by Pat Example, to version 2 -->" ]]; then
  echo "FAIL: --fix did not stamp the resolved person's place and name: $PAT_LINE" >&2
  exit 1
fi
if [[ "$SAM_LINE" != *"(Tokyo) by Sam Sample, to version 2 -->" ]]; then
  echo "FAIL: --fix stamped the same name and place for a different person: $SAM_LINE" >&2
  exit 1
fi
echo "ok: --fix stamps each person's own name and place, from their identity.json"

# (6) NOBODY RESOLVES -- a CI runner, a shared repo, a session without its
# individual set. The graceful answer: nothing is stamped (--fix refuses and
# says why; the commit-time --fix-staged skips and exits 0), while the check
# still judges every header already in the exact format, since a rising N
# needs nobody's name. Control: the same commit under a resolved person.
SCRATCH_NOBODY="$(mktemp -d)"
git clone -q "$ROOT" "$SCRATCH_NOBODY"
(
  cd "$SCRATCH_NOBODY"
  assert_scratch
  git config user.name "Pat Example"
  git config user.email "pat@example.invalid"
  plant_doc
  export PRECEDENT_USER_CONFIG="$NOBODY_CONFIG"
  before="$(head -1 PLANTED_DOC.md)"
  printf 'An edit nobody can stamp.\n' >> PLANTED_DOC.md
  OUT="$(check_under_test --fix 2>&1)" && RC=0 || RC=$?
  if [[ "$RC" -eq 0 ]] || ! grep -q "REFUSED" <<<"$OUT" \
     || ! grep -q "no identity resolves" <<<"$OUT"; then
    echo "FAIL: --fix with no identity did not refuse and say why (rc $RC)" >&2
    echo "$OUT" >&2
    exit 1
  fi
  if [[ "$before" != "$(head -1 PLANTED_DOC.md)" ]]; then
    echo "FAIL: --fix stamped a header with no identity resolved" >&2
    exit 1
  fi
  git add -f PLANTED_DOC.md
  check_under_test --fix-staged 2> /dev/null || {
    echo "FAIL: --fix-staged did not exit 0 with no identity -- it runs before every commit" >&2
    exit 1
  }
  if ! git show :PLANTED_DOC.md | head -1 | grep -q 'to version 1 -->'; then
    echo "FAIL: --fix-staged stamped a header with no identity resolved" >&2
    exit 1
  fi
  TZ="Europe/Lisbon" git commit -q -m "content change, no bump, nobody resolved"
  if check_under_test > /dev/null; then
    echo "FAIL: with no identity the check stopped judging a content change with no bump" >&2
    exit 1
  fi
  echo "ok: no identity -- nothing stamped, and a missed bump is still caught"
  # Control: a resolved person stamps the same tree, and the result is clean.
  PRECEDENT_USER_CONFIG="$PAT_CONFIG" check_under_test --fix > /dev/null
  TZ="Europe/Lisbon" git commit -q -am "catch-up bump by a resolved person"
  if ! check_under_test > /dev/null; then
    echo "FAIL: a resolved person's catch-up bump is not clean with no identity" >&2
    exit 1
  fi
  echo "ok: control -- a resolved person's catch-up stamp is clean"
)
rm -rf "$SCRATCH_NOBODY"

# (7) A header naming SOMEBODY ELSE is still this convention. Its N is judged
# whoever it names, and the commit-time stamp writes the person who made the
# edit -- the header says who last touched the file. Control: a line that
# starts the same way but is not in the format and names nobody resolved is
# left alone, as before.
SCRATCH_OTHER="$(mktemp -d)"
git clone -q "$ROOT" "$SCRATCH_OTHER"
(
  cd "$SCRATCH_OTHER"
  assert_scratch
  git config user.name "Pat Example"
  git config user.email "pat@example.invalid"
  printf '<!-- Last updated: 2026-10-01 10:00:00 (Tokyo) by Sam Sample, to version 3 -->\n\nSam wrote this.\n' > SAMS_DOC.md
  printf '<!-- Last updated: last spring, by the vendor -->\n\nNot this convention.\n' > VENDOR_DOC.md
  git add -f SAMS_DOC.md VENDOR_DOC.md
  TZ="Europe/Lisbon" git commit -q -m "a header naming someone else, and a foreign one"
  printf 'Pat edits it.\n' >> SAMS_DOC.md
  printf 'Edited too.\n' >> VENDOR_DOC.md
  git add -f SAMS_DOC.md VENDOR_DOC.md
  check_under_test --fix-staged 2> /dev/null
  if ! git show :SAMS_DOC.md | head -1 | grep -q '(Lisbon) by Pat Example, to version 4 -->'; then
    echo "FAIL: --fix-staged did not stamp the editor over another person's header: $(git show :SAMS_DOC.md | head -1)" >&2
    exit 1
  fi
  if ! git show :VENDOR_DOC.md | head -1 | grep -q 'by the vendor'; then
    echo "FAIL: --fix-staged rewrote a line that is not this header" >&2
    exit 1
  fi
  TZ="Europe/Lisbon" git commit -q -m "edit stamped by the editor"
  if ! check_under_test > /dev/null; then
    echo "FAIL: the editor's stamp over another person's header is not clean" >&2
    exit 1
  fi
  printf 'Edited again, no bump.\n' >> SAMS_DOC.md
  TZ="Europe/Lisbon" git commit -q -am "content change, no bump"
  if check_under_test > /dev/null; then
    echo "FAIL: a missed bump went unjudged because the header names someone else" >&2
    exit 1
  fi
  echo "ok: another person's header is judged and restamped by the editor; a foreign line is left alone"
)
rm -rf "$SCRATCH_OTHER"

if ! check_under_test > /dev/null; then
  echo "FAIL: check_file_header.py is not clean on the real, current repo" >&2
  exit 1
fi
echo "ok: clean on real content"

# A header violation inside a path this repo mirrors and may not hand-edit
# must leave the check SILENT. Added 2026-09-06: in a consuming repo this
# check's only remaining findings were inside the byte-identical vendored
# copy of upstream's own documents -- real, but not fixable there, and the
# next sync overwrites any edit anyway. The mirror is named by
# process/manifest.json's own upstream.vendored_at; nothing is hardcoded.
SCRATCH3="$(mktemp -d)"
trap 'rm -rf "$SCRATCH3" "$IDENTITIES"' EXIT
git clone -q "$ROOT" "$SCRATCH3"
cd "$SCRATCH3"
mkdir -p process/upstream
cat > process/manifest.json <<'JSON'
{"upstream": {"repo": "https://example.invalid/upstream", "vendored_at": "process/upstream", "commit": "0000000000000000000000000000000000000000"}}
JSON
printf 'A mirrored document with no header at all.\n' > process/upstream/MIRRORED.md
git add process/manifest.json process/upstream/MIRRORED.md
git -c user.name="Test" -c user.email="test@example.com" commit -q -m "mirrored file, headerless"
printf 'Changed, still no header, still not ours to fix.\n' >> process/upstream/MIRRORED.md
git add process/upstream/MIRRORED.md
git -c user.name="Test" -c user.email="test@example.com" commit -q -m "mirrored file changed without a version bump"

if ! check_under_test > /dev/null; then
  echo "FAIL: check_file_header.py fired on a file inside the declared vendored mirror, which this repo may not hand-edit" >&2
  exit 1
fi
echo "ok: silent on a violation inside a declared mirror"
