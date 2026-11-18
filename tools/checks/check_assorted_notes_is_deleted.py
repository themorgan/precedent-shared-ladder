#!/usr/bin/env python3
"""check_assorted_notes_is_deleted.py -- the mechanical check for
practices/assorted-notes-is-deleted.md.

# practice: assorted-notes-is-deleted

Scope: tree, over every file tracked in the repo. What is in
`ASSORTED_NOTES.md` counts as deleted, so nothing links to it: a markdown
link whose target's basename is `ASSORTED_NOTES.md` (or, before the
migration has happened, a legacy BRAINSTORM.md / NOTES.md / IDEAS.md) fails
anywhere outside the file itself and a plain list of files -- a `README.md`
or `MAP.md` at any depth, or the hand-written source of a map
(`MAP.source.md`, a row under `MAP.source/`).

STRICT, ON PURPOSE (Morgan, 2026-11-18, strength: decided: "We should be
strict"). This replaces the writing set's `check_assorted_notes.py`, which
also passed a link inside any `## See also` section and a link whose text
was the file's own name. Both exemptions are gone: a See also footer is a
page pointing at the file it left, which is how a deleted item comes back,
and in a planning repository a session moved links INTO See also because
that check passed them there.

Kept from that check, with its reasons: the basename-exact match (a link to
MARKETING_IDEAS.md is not a link to IDEAS.md), legacy names counting only
until an ASSORTED_NOTES.md exists at any depth, and the mirrored-prefix
exclusion, which skips a vendored copy of somebody else's catalogue.

It cannot see a bare prose mention with no link; that is the Rule's to
carry, and the reply gate's, not this script's.

Exit 0 and print nothing when clean. Exit 1 and print the practice's own
Rule text (never a paraphrase) plus the specific finding(s) on a violation.
"""
import functools
import os
import pathlib
import re
import subprocess
import sys

# SOURCE_ROOT is the practice set this script ships in; ROOT is the
# repository it AUDITS. They differ when a repo declares this set without
# materializing it and runs the script in place against itself.
SOURCE_ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
ROOT = pathlib.Path(os.environ.get("PRECEDENT_CHECK_ROOT") or SOURCE_ROOT)
PRACTICE_FILE = SOURCE_ROOT / "practices" / "assorted-notes-is-deleted.md"

# Legacy names the practice says to rename to ASSORTED_NOTES.md -- a link to
# any of these, in an unrenamed legacy repo, is the same violation.
LEGACY_FILENAMES = ("BRAINSTORM.md", "NOTES.md", "IDEAS.md")
CANONICAL_FILENAME = "ASSORTED_NOTES.md"


@functools.lru_cache(maxsize=None)
def _canonical_exists() -> bool:
    """Is there an ASSORTED_NOTES.md anywhere in the tracked tree?

    Asked by basename, at any depth, NOT at a hardcoded `content/`. The
    directory is this practice's *default*, not its definition -- and the
    practice that used to supply that default (retired 2026-09-29) said in
    as many words that an established layout wins over it. A repo that keeps its working
    files somewhere better-named still has a catch-all, and the migration
    this check gates on is just as done there.

    2026-09-07: a consuming repo renamed `content/` to `business-modeling/`
    so that every content directory of its own said what it held. Its
    ASSORTED_NOTES.md moved intact, with the rename -- and this check,
    testing one literal path, silently concluded the legacy-name migration
    had never happened and re-armed BRAINSTORM.md/NOTES.md/IDEAS.md as live
    legacy names across that whole repo. It kept passing by luck: the only
    links to its `book-moses/NOTES.md` happened to sit in a MAP.md and a
    README.md, both exempt as listing documents. One ordinary link from any
    other file would have failed the repo for a violation that was never
    there -- the exact false positive the docstring below this one was
    written to stop, reintroduced through the directory name instead of the
    filename.
    """
    result = subprocess.run(
        ["git", "-C", str(ROOT), "ls-files", "*" + CANONICAL_FILENAME],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        # Not a git repo, or git unavailable. Fall back to the old literal
        # path rather than guessing: a wrong "migration is done" here would
        # silently narrow the check, and failing open is the worse direction
        # for a rule about not citing unformed notes.
        return (ROOT / "content" / CANONICAL_FILENAME).is_file()
    return any(pathlib.PurePosixPath(line).name == CANONICAL_FILENAME
               for line in result.stdout.splitlines() if line.strip())


def notes_filenames() -> tuple:
    """The canonical name always; the legacy names only until the migration
    this practice describes has actually happened.

    "In an unrenamed legacy repo" is the condition the comment above states
    and the check did not test: it matched any file named NOTES.md, anywhere,
    forever. Once an ASSORTED_NOTES.md exists the consolidation is
    done, and a file that merely shares a legacy name is an ordinary file
    with its own subject -- 2026-09-06, a repo with a perfectly good
    content/ASSORTED_NOTES.md was flagged for linking `book-moses/NOTES.md`,
    a manuscript-scoped brainstorm about Moses that is not this repo's
    catch-all and was never meant to become it. Reading the legacy names as
    permanent turns a one-time migration rule into a standing ban on a
    common filename."""
    if _canonical_exists():
        return (CANONICAL_FILENAME,)
    return (CANONICAL_FILENAME,) + LEGACY_FILENAMES


def _mirrored_prefixes_without_the_engine() -> tuple:
    """Exclude nothing, which is exactly what this check did before it asked
    the question at all -- so a repo with no precedent_resolve.py behaves as
    it always has, and the gain is confined to the repos that have one."""
    return ()


# --- what this repo MIRRORS from elsewhere, and may not edit -------------
#
# THE ENGINE ANSWERS THIS NOW (2026-09-10). Several source-supplied checks
# need the same list -- anything that scans prose and would otherwise report
# findings inside a vendored copy of somebody else's catalogue -- and each
# derived it privately, from whichever single file it happened to know
# about. That is how a real defect got in: a check reading only
# `process/manifest.json`'s `upstream.vendored_at` loses its exclusion
# entirely in an INSTALL.md section 0 install, because section 0 step 5 says
# outright to SKIP that file, and a section 0 install puts the engine at
# `tools/` instead. A real section 0 install's run reported dozens of
# findings inside Precedent's own historical prose, none of them actionable:
# editing a mirror is forbidden and the next sync would overwrite it anyway.
#
# precedent_resolve.mirrored_prefixes(ROOT) reads `precedent.json`'s declared
# source paths as well as the manifest -- and precedent.json is the file that
# EXISTS in exactly the repos process/manifest.json is missing from. It never
# raises; an empty tuple is a valid answer (it is what a source set and a
# fresh repo return).
#
# FAILS OPEN, deliberately, where the two identity checks report SKIPPED for
# the same missing module. precedent_resolve.py is in upstream's
# CONSUMER_ENGINE_FILES but not its ENGINE_FILES, so a practice-set repo does
# not vendor it -- and an exclusion that comes back empty costs extra
# findings, never a missed one, while an identity that cannot be resolved
# would make every verdict wrong. Different failure, different degrade.
@functools.lru_cache(maxsize=None)
def _mirrored_prefixes() -> tuple:
    for _d in (ROOT / "tools", ROOT / "process" / "upstream" / "tools",
               pathlib.Path(__file__).resolve().parent.parent,
               SOURCE_ROOT / "tools"):
        if (_d / "precedent_resolve.py").is_file():
            sys.path.insert(0, str(_d))
            break
    try:
        import precedent_resolve
        return tuple(precedent_resolve.mirrored_prefixes(ROOT))
    except Exception:
        return _mirrored_prefixes_without_the_engine()


_MIRRORED = _mirrored_prefixes()

# Matches any markdown link's target; the target is then compared against
# notes_filenames() by basename, so a filename that merely ends the same way
# (MARKETING_IDEAS.md, RANDOM_NOTES.md) doesn't match.
LINK_RE = re.compile(r"\]\(([^)]+)\)")

# Any Markdown file can add a link to the notes file, so any change to one
# selects this check (Precedent's precedent_check reads SELECTS_ON without
# running this script).
SELECTS_ON = ("*.md", "**/*.md")

# A plain list of files -- any README.md or MAP.md, at any depth -- may name
# the file; so may the notes file itself (a self-link) and the practice file
# that documents the rule. Nothing else.
EXEMPT_BASENAMES = (
    {"assorted-notes-is-deleted.md", "readme.md", "map.md"}
    | {n.lower() for n in notes_filenames()}
)

# A view's source is the view, written by hand: MAP.source.md (or one row
# file under MAP.source/) is copied word for word into MAP.md by Precedent's
# build_views, so a link there is a link in the map. Until 2026-10-19 the
# source was judged as an ordinary page, a consumer's map listing its notes
# file was flagged in MAP.source.md, and main went red after a Produce.
SOURCE_SUFFIX = ".source"


def _listing_view(path: str) -> bool:
    """True when `path` is an exempt listing document, directly or as the
    hand-written source of one: X.source.md, or any file under X.source/,
    whose view X.md is exempt."""
    parts = pathlib.PurePosixPath(path).parts
    name = parts[-1].lower()
    if name in EXEMPT_BASENAMES:
        return True
    if name.endswith(SOURCE_SUFFIX + ".md") and \
            name[:-len(SOURCE_SUFFIX + ".md")] + ".md" in EXEMPT_BASENAMES:
        return True
    return any(d.lower().endswith(SOURCE_SUFFIX)
               and d.lower()[:-len(SOURCE_SUFFIX)] + ".md" in EXEMPT_BASENAMES
               for d in parts[:-1])


# This check's own machinery: its docstring describes the link pattern it
# looks for, and its test plants that pattern as a fixture -- neither is a
# real link to real notes.
EXEMPT_PATHS = {
    "tools/checks/check_assorted_notes_is_deleted.py",
    "tools/checks/tests/test_assorted_notes_is_deleted.sh",
}


def rule_text() -> str:
    # A materialized check runs in whatever repo its source was resolved
    # into, and the practice file it quotes is not guaranteed to be there:
    # a repo that declares the source but never materializes it, or a
    # practice retired out of the tree, both leave PRACTICE_FILE absent.
    # Unguarded, this raised FileNotFoundError from inside the violation
    # PRINTER -- so the finding was correctly detected, correctly printed,
    # and then buried under a traceback. Found 2026-09-06 running every
    # source-supplied check against BestPractice; 14 of the 16 shared this
    # exact body. The Rule text being unavailable is not the check failing.
    if not PRACTICE_FILE.is_file():
        return "(practice file not found at %s)" % PRACTICE_FILE
    text = PRACTICE_FILE.read_text(encoding="utf-8")
    m = re.search(r"## Rule\n(.*?)\n## ", text, re.S)
    return m.group(1).strip() if m else "(no Rule found)"


def tracked_files() -> list[str]:
    result = subprocess.run(
        ["git", "-C", str(ROOT), "ls-files"],
        capture_output=True,
        text=True,
        check=True,
    )
    return [line for line in result.stdout.splitlines() if line.strip()]


def find_violations() -> list[str]:
    findings = []
    for path in tracked_files():
        # A link inside a vendored copy of somebody else's catalogue is not
        # this repo's to fix: the fix belongs in the source, and the next
        # sync overwrites a hand-edit here.
        if _MIRRORED and path.startswith(_MIRRORED):
            continue
        if _listing_view(path):
            continue
        if path in EXEMPT_PATHS:
            continue
        full = ROOT / path
        try:
            text = full.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        for lineno, line in enumerate(text.splitlines(), start=1):
            for m in LINK_RE.finditer(line):
                target = m.group(1)
                bare = target.split()[0] if target.split() else target
                bare = bare.split("#", 1)[0]
                if pathlib.PurePosixPath(bare).name in notes_filenames():
                    findings.append(f"{path}:{lineno}: links to {target!r}")
    return findings


if __name__ == "__main__":
    findings = find_violations()
    if findings:
        print(f"VIOLATION: {PRACTICE_FILE.stem}")
        for f in findings:
            print(f"  {f}")
        print("\nthe rule:")
        print("  " + rule_text().replace("\n", "\n  "))
        sys.exit(1)
    sys.exit(0)
