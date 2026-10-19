#!/usr/bin/env python3
"""check_file_header.py -- the mechanical check for practices/file-header.md.

# practice: file-header

Scope: change, over every markdown file tracked in the repo (applies_to
"**/*.md"). A file "carries this header" (the practice's own occasion
clause) once its first line matches the format below -- untouched files
that never had one are not required to grow one; that's a per-edit choice,
not a repo-wide sweep, per the practice's own Detail section. A line has
to both start "<!-- Last updated:" *and* name Morgan to count as an
attempt at this header -- vendored third-party content (e.g. a consuming
repo's process/upstream/ tree) can have its own, different, complete
attribution convention that happens to share the prefix; that's not this
practice's business and isn't flagged as malformed.

Two things are checked mechanically for every file that does carry it:

1. Format -- the first line must match the header exactly:
   <!-- Last updated: YYYY-MM-DD HH:MM:SS (Buenos Aires) by Morgan F, to version N -->
   with N a plain positive integer.

2. Version continuity, against this file's own content in the parent
   commit (HEAD~1) where available. **N is MONOTONIC, not a successor
   function** (Morgan, 2026-09-22):
   - if the file's body (everything after the header line) changed,
     N must have INCREASED from the parent commit's N -- by any amount;
   - N may never DECREASE, whether or not the body changed;
   - a bump with no body change is fine. It is how a missed earlier bump
     is caught up, and gaps in the sequence carry no meaning.
   A file with no parent version (newly added, or the header is new in
   this commit) is exempt from continuity -- there is nothing to compare
   against -- but a freshly added header must start at version 1.

   WHY THE "no touch-up without a real edit" ARM CAME OUT, 2026-09-22.
   It made a missed bump PERMANENTLY unfixable. PR #191 changed README.md
   without bumping N; the next commit tried to bump it and was refused --
   "version changed from 24 to 25 but the file's content didn't change" --
   because by then the content change was in an earlier commit. There was
   no commit shape that repaired it. Morgan's ruling: *"this is a minor
   feature so I don't collide different versions, it just needs the higher
   number for the more recent one, no precision"*. A gratuitous bump costs
   nothing; an unfixable red costs a real check.

3. `--fix` repairs the WORKING TREE before the commit is made, which is the
   only moment a repair is possible: for every tracked markdown file whose
   body differs from HEAD and whose first line carries this header, the line
   is rewritten with the current Buenos Aires timestamp and N set past the
   HEAD version. Where the zone cannot be resolved -- `precedent_time.py`
   not importable -- it stamps NOTHING and exits non-zero rather than
   guessing; see `_stamp()` for why guessing is the worse of the two. It stamps a malformed header into the right format too, and
   forces a brand-new file's header to version 1. It also catches up a file
   whose body has NOT changed if HEAD's own commit is itself the violation
   -- content changed with no bump, or a backwards version -- which is what
   an edit made outside any session (e.g. straight from the GitHub web UI)
   leaves behind with nothing pending to trigger the ordinary path; see
   `_head_catchup_target()`. It never touches anything else, and never
   touches a mirrored or generated tree. Run it before `git add`; see
   `practices/file-header.md`.

Exit 0 and print nothing when clean. Exit 1 and print the practice's own
Rule text (never a paraphrase) plus the specific finding(s) on a violation.
"""
import json
import os
import pathlib
import re
import subprocess
import sys

# TWO different questions, which used to share one name -- and that is exactly
# how a practice file went missing. SOURCE_ROOT is the practice set this script
# ships in; ROOT is the repository it AUDITS.
#
# They are the same directory in both normal cases: run in place inside its own
# set, and materialized into a consuming repo (where precedent_materialize.py
# has written practices/ and tools/checks/ side by side). They differ in the
# third case -- a repo that DECLARES this source but never materializes it, and
# runs the script in place against itself. Precedent's own repo is exactly
# that: its practices/ is the universal catalogue, so `parents[2]/practices/`
# resolved to a directory this practice was never in, and rule_text() raised
# FileNotFoundError from inside the violation printer (2026-09-06). The rule
# text always ships beside the script, so it is looked up against SOURCE_ROOT
# and can no longer be absent; only what to audit is overridable.
SOURCE_ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
ROOT = pathlib.Path(os.environ.get("PRECEDENT_CHECK_ROOT") or SOURCE_ROOT)
PRACTICE_FILE = SOURCE_ROOT / "practices" / "file-header.md"

HEADER_RE = re.compile(
    r"^<!-- Last updated: (\d{4}-\d{2}-\d{2}) (\d{2}):(\d{2}):(\d{2}) "
    r"\(Buenos Aires\) by Morgan F, to version (\d+) -->$"
)
HEADER_FMT = ("<!-- Last updated: {stamp} (Buenos Aires) "
              "by Morgan F, to version {n} -->")
# How the violation messages tell a session to repair this. Written as the
# path a session actually types, not as __file__, which in a materialized
# consumer is an absolute path nobody would paste.
REL_SELF = "tools/checks/check_file_header.py"
# A line that's clearly *trying* to be the header but doesn't match exactly
# -- used to flag malformed headers, not just missing ones.
HEADER_ATTEMPT_RE = re.compile(r"^<!--\s*Last updated:", re.IGNORECASE)


def is_header_attempt(line: str) -> bool:
    # A "Last updated:" prefix alone isn't enough to call a line an attempt
    # at *this* header format -- vendored third-party content (e.g. a
    # consuming repo's process/upstream/ tree) can carry its own, different,
    # complete attribution convention that happens to start the same way.
    # That's not this practice's business and shouldn't be flagged as
    # malformed just for not saying "Morgan F". Require the name too.
    return bool(HEADER_ATTEMPT_RE.match(line)) and "morgan" in line.lower()



# --- Findings this repo cannot act on where they are reported -------------
#
# A consuming repo mirrors trees it must NOT hand-edit: the vendored
# universal catalogue (byte-identical to upstream, re-mirrored wholesale)
# and any generated or re-synced copy of another repo's files. A finding
# inside one of those is real, but it is not actionable HERE -- the fix
# belongs in the repo that owns the text, and editing the mirror is
# forbidden and would be overwritten by the next sync anyway. Reporting
# them buries the findings that ARE actionable: one consuming repo's run
# showed dozens of violations, every single one inside its vendored copy
# of upstream's own prose (2026-09-06).
#
# Nothing is hardcoded. All three signals already exist and are already
# authoritative in any repo that has them:
#   1. process/manifest.json's upstream.vendored_at -- the mirror's own
#      declared path.
#   2. A "GENERATED FILE" / "do not hand-edit" / "DERIVED" marker in the
#      file's opening lines (practice: derived-file-marker).
#   3. MANIFEST.json's per-practice `level` -- practices/ is materialized
#      output, so a practice from any source but repo-local is owned
#      elsewhere. Attributing by the COMMITTED manifest rather than by
#      live source resolution is deliberate: a bare CI checkout cannot
#      reach a team sibling clone or a private user-level config, and
#      "did not resolve here" is not "owned here".
# A repo with none of these files loses nothing -- every part fails open.
_GENERATED_RE = re.compile(
    r"generated file|do not hand[- ]edit|DERIVED from", re.I)


def _mirrored_prefixes_without_the_engine() -> tuple:
    """The manifest-only reading this check has always done, kept as the
    fallback for a repo with no precedent_resolve.py."""
    manifest = ROOT / "process" / "manifest.json"
    if not manifest.is_file():
        return ()
    try:
        upstream = json.loads(manifest.read_text(encoding="utf-8")).get("upstream", {})
    except (ValueError, OSError):
        return ()
    at = str(upstream.get("vendored_at") or "").strip("/")
    return (at + "/",) if at else ()


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


# Resolved once: it is a property of the repository, not of the file being
# examined, and not_actionable_here() is called per file.
_MIRRORED = _mirrored_prefixes()


# --- single files kept in step with upstream ---------------------------------
#
# A consumer keeps some upstream files beside its own, one at a time: a
# template it rendered and tracks (GETTING_STARTED.md), recorded in a
# process/manifest*.json entry with status "synced". practice_audit.py holds
# each to its recorded hash and reports any change as DRIFT. On 2026-10-15
# --fix-staged stamped such a copy on an edit and again on a byte-for-byte
# restore, and the audit refused the landing each time; the only way through
# was PRECEDENT_SKIP_COMMIT_FIX=1. The engine's synced_copies() answers which
# files these are (after _mirrored_prefixes found precedent_resolve, if it
# could); an engine without it is read the same way, here.
def _synced_copies() -> frozenset:
    try:
        import precedent_resolve
        return frozenset(precedent_resolve.synced_copies(ROOT))
    except Exception:
        pass
    out = set()
    for manifest in sorted((ROOT / "process").glob("manifest*.json")):
        try:
            entries = json.loads(manifest.read_text(encoding="utf-8")).get("entries") or []
        except (ValueError, OSError, AttributeError):
            continue
        for e in entries:
            if isinstance(e, dict) and e.get("local_path") \
                    and e.get("granularity", "file") == "file" \
                    and e.get("status", "synced") == "synced":
                out.add(pathlib.PurePosixPath(e["local_path"]).as_posix())
    return frozenset(out)


_SYNCED = _synced_copies()


def _is_generated(rel: str) -> bool:
    try:
        with (ROOT / rel).open(encoding="utf-8") as fh:
            head = "".join([next(fh, "") for _ in range(3)])
    except (OSError, UnicodeDecodeError):
        return False
    return bool(_GENERATED_RE.search(head))


def _foreign_practice(rel: str) -> bool:
    if not (rel.startswith("practices/") and rel.endswith(".md")):
        return False
    manifest = ROOT / "MANIFEST.json"
    if not manifest.is_file():
        return False
    try:
        entries = json.loads(manifest.read_text(encoding="utf-8")).get("practices", [])
    except (ValueError, OSError):
        return False
    slug = pathlib.PurePath(rel).stem
    for entry in entries:
        if entry.get("slug") == slug:
            return entry.get("level") != "repo-local"
    return False


def not_actionable_here(rel: str) -> bool:
    return (bool(_MIRRORED) and rel.startswith(_MIRRORED)) \
        or rel in _SYNCED or _foreign_practice(rel) or _is_generated(rel)

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


def tracked_md_files() -> list[str]:
    result = subprocess.run(
        ["git", "-C", str(ROOT), "ls-files", "*.md"],
        capture_output=True,
        text=True,
        check=True,
    )
    return [line for line in result.stdout.splitlines()
            if line.strip() and not not_actionable_here(line.strip())]


def read_at_head(path: str, rev: str) -> str | None:
    result = subprocess.run(
        ["git", "-C", str(ROOT), "show", f"{rev}:{path}"],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return None
    return result.stdout


def renamed_from() -> dict[str, str]:
    """{path now: path the same file had at HEAD~1}, for this commit's renames.

    The parent lookup below asks `git show HEAD~1:<path>`, which is the right
    question only for a file that had that path at HEAD~1. A renamed file did
    not, so git exits non-zero, the parent reads as absent, and the check
    concludes the header is new and demands the counter restart at 1 -- for a
    file whose real edit history is untouched and whose version number is
    correct.

    2026-09-07, the incident: a consuming repo renamed its whole content
    directory in one `git mv`, and this check reported all twelve versioned
    documents under it as "header is new in this commit but starts at version
    N, expected 1". Twelve false positives on a commit that added no file at
    all -- and the honest fixes available to that repo were both wrong
    (reset twelve real counters to 1, or leave the check red), because
    nothing here could tell a rename from a creation.

    `git diff -M --name-status` can, so ask it. Copies (`C`) are deliberately
    not followed: a copy really is a new file that happens to share content,
    and its header genuinely should start at 1.
    """
    result = subprocess.run(
        ["git", "-C", str(ROOT), "diff", "-M", "--name-status", "HEAD~1", "HEAD"],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        # No HEAD~1 -- a root commit, or a shallow clone's boundary. The
        # caller's own `parent is None` path already handles that correctly.
        return {}
    out = {}
    for line in result.stdout.splitlines():
        parts = line.split("\t")
        if len(parts) == 3 and parts[0].startswith("R"):
            out[parts[2]] = parts[1]
    return out


def find_violations() -> list[str]:
    findings = []
    renames = renamed_from()
    for path in tracked_md_files():
        current = read_at_head(path, "HEAD")
        if current is None:
            continue
        lines = current.splitlines()
        first = lines[0] if lines else ""

        if not is_header_attempt(first):
            continue  # doesn't carry the header at all -- not required to

        m = HEADER_RE.match(first)
        if not m:
            findings.append(f"{path}: first line looks like the header but doesn't match the required format: {first!r}")
            continue

        version = int(m.group(5))
        body = "\n".join(lines[1:])

        # Read the parent side at the path this file HAD then, not the path
        # it has now -- see renamed_from().
        parent = read_at_head(renames.get(path, path), "HEAD~1")
        if parent is None:
            # A merge brings in files the first parent never had: a Promote
            # merges a whole batch onto staging, and a document added on
            # pre-staging and edited there three times arrives at version 4.
            # Its counter was held to account commit by commit on the branch
            # it came from, so read it against that side. Only a file NEITHER
            # parent has is new here (2026-09-26: a Promote refused over a
            # meeting-notes file added and edited on pre-staging).
            parent = read_at_head(path, "HEAD^2")
        if parent is None:
            if version != 1:
                findings.append(f"{path}: header is new in this commit but starts at version {version}, expected 1")
            continue

        parent_lines = parent.splitlines()
        parent_first = parent_lines[0] if parent_lines else ""
        parent_m = HEADER_RE.match(parent_first)
        if not parent_m:
            # The parent commit may have carried a MALFORMED header attempt
            # (a real published incident: a previous commit's own header
            # dropped its HH:MM:SS component, per this check's own history)
            # rather than no header at all -- "no header in the parent" and
            # "a broken header in the parent" are different situations, and
            # treating the second as the first forces every subsequent
            # correctly-formatted commit to restart numbering at 1, which
            # would misrepresent a file's real edit history for one
            # already-published formatting slip. Recover a version number
            # from the malformed line if one is findable at all, and only
            # fall back to "no header" semantics when it truly isn't.
            if is_header_attempt(parent_first):
                loose = re.search(r"version (\d+)", parent_first)
                if loose:
                    parent_version = int(loose.group(1))
                    parent_body = "\n".join(parent_lines[1:])
                    if body != parent_body and version <= parent_version:
                        findings.append(
                            f"{path}: content changed since the parent commit's "
                            f"(malformed-header) version {parent_version} but "
                            f"version stayed at {version} -- bump it, or run "
                            f"`python3 {REL_SELF} --fix` before committing"
                        )
                    elif version < parent_version:
                        findings.append(
                            f"{path}: version went BACKWARDS, {parent_version} "
                            f"-> {version}. N only ever rises; a bump with no "
                            f"content change is fine, a drop is not"
                        )
                    continue
            if version != 1:
                findings.append(f"{path}: header is new (parent revision carried none) but starts at version {version}, expected 1")
            continue

        parent_version = int(parent_m.group(5))
        parent_body = "\n".join(parent_lines[1:])

        if body != parent_body and version <= parent_version:
            findings.append(
                f"{path}: content changed since the parent commit but version stayed at {version} "
                f"(was {parent_version}) -- bump it, or run "
                f"`python3 {REL_SELF} --fix` before committing"
            )
        elif version < parent_version:
            findings.append(
                f"{path}: version went BACKWARDS, {parent_version} -> {version}. "
                f"N only ever rises; a bump with no content change is fine "
                f"(that is how a missed one is caught up), a drop is not"
            )
    return findings


def _version_of(line: str) -> int | None:
    """N from a header line -- exact format first, then a malformed attempt.

    The loose read is not sloppiness: a published commit once dropped the
    HH:MM:SS component, and treating that line as "no header" would restart
    a real counter at 1. find_violations() has always recovered a number
    that way; this is the same recovery, in one place both callers use.
    """
    m = HEADER_RE.match(line)
    if m:
        return int(m.group(5))
    if is_header_attempt(line):
        loose = re.search(r"version (\d+)", line)
        if loose:
            return int(loose.group(1))
    return None


class ZoneUnresolved(Exception):
    """`precedent_time.py` is not reachable, so `--fix` will not guess."""


def _stamp() -> str:
    """Now, in Buenos Aires, as the header spells it.

    THE ZONE IS NOT HARDCODED HERE and must not be. `precedent_time.py` owns
    the five-rung ladder that decides it (PRECEDENT_COMMIT_TZ, then the
    person's identity.json, then the repo's declared fallback_timezone, and
    so on), and `buenos-aires-dates` is the practice that makes the answer
    Buenos Aires for Morgan. Writing `America/Argentina/Buenos_Aires` into
    this script would be a second copy of that decision -- the exact defect
    `no-hardcoded-git-identity` names -- so this asks the one module that
    knows.

    NO MODULE, NO STAMP (Morgan, 2026-09-22). This used to fall back to a
    bare `datetime.now()` where the module was missing -- a consuming repo
    materializes tools/checks/ without tools/ -- on the reasoning that a
    wrong-zone stamp still satisfies the check and refusing outright would
    be worse. Two things were wrong with that. The zone is NOT part of what
    gets written: HEADER_FMT spells "(Buenos Aires)" literally, so a header
    stamped at container UTC comes out three hours off and labelled
    correctly, and no reader of the file can tell. And "refusing is worse"
    stopped being true in the same change that introduced the fallback --
    once `N` became monotonic, a header this run declines to stamp is
    caught up by any later commit, so the cost of refusing is a bump
    somebody fixes later against the cost of guessing, which is a timestamp
    nobody can ever catch. `timestamps-carry-offset` was reporting exactly
    this, and it was right.
    """
    for _d in (ROOT / "tools", SOURCE_ROOT / "tools",
               pathlib.Path(__file__).resolve().parent.parent):
        if (_d / "precedent_time.py").is_file():
            sys.path.insert(0, str(_d))
            break
    try:
        import precedent_time
    except Exception as exc:
        raise ZoneUnresolved(
            "precedent_time.py is not importable from this checkout, so the "
            "zone the header claims cannot be resolved. Looked in %s. Run "
            "--fix from a checkout that carries tools/precedent_time.py, or "
            "set the header by hand." % ", ".join(
                str(d) for d in (ROOT / "tools", SOURCE_ROOT / "tools",
                                 pathlib.Path(__file__).resolve().parent.parent))
        ) from exc
    # strftime here rather than precedent_time.stamp(): that helper appends
    # the numeric offset ("... 10:58:06 -0300"), which HEADER_RE rejects. The
    # zone still comes from the ladder -- it is what `now()` resolves -- and
    # the offset is simply not part of this header's shape. Caught by the
    # --fix test before this ever ran for real.
    return precedent_time.now(ROOT).strftime("%Y-%m-%d %H:%M:%S")


def _head_catchup_target(path: str, renames: dict[str, str],
                          head_first: str, head_body: str) -> int | None:
    """The N to stamp if HEAD's OWN commit already violates this practice
    against ITS parent (HEAD~1) -- content changed with no bump, or a
    version that went backwards. That is exactly what an edit made outside
    any session (e.g. a commit pushed straight from the GitHub web UI)
    leaves behind, and until something else touches the file, there is no
    pending working-tree edit for the ordinary branch below to catch: the
    violation would otherwise just sit there, live, until some unrelated
    later commit happens to move HEAD past it.

    Returns None when HEAD is clean against its parent -- including when
    the parent's header is missing or unrecoverable, which is a different,
    rarer violation shape (`file-header is new but doesn't start at 1`)
    this does not try to repair, since there is no "catch up to" number.
    """
    parent = read_at_head(renames.get(path, path), "HEAD~1")
    if parent is None:
        return None
    parent_lines = parent.splitlines()
    parent_first = parent_lines[0] if parent_lines else ""
    parent_body = "\n".join(parent_lines[1:])
    parent_n = _version_of(parent_first)
    head_n = _version_of(head_first)
    if parent_n is None or head_n is None:
        return None
    violates = (head_body != parent_body and head_n <= parent_n) or (head_n < parent_n)
    return max(head_n, parent_n) + 1 if violates else None


def fix_working_tree() -> list[str]:
    """Stamp the header of every tracked markdown file whose body has changed
    -- and catch up a file whose current HEAD already violates against ITS
    parent, even with nothing pending, per _head_catchup_target() above.

    WHY THE WORKING TREE AND NOT THE COMMIT. This is the only moment a repair
    is possible. find_violations() compares HEAD against HEAD~1, so by the
    time it reports a missed bump the commit already exists and no later
    commit can carry the fix -- that is the trap Morgan closed on 2026-09-22
    (see the module docstring). Run before `git add` and the header rides the
    same commit as the edit that earned it. The catch-up case is the same
    trap one step further back: an edit made outside any session already
    landed on HEAD unbumped, and nobody has to be the one who notices --
    `--fix` produces the one-line diff, ready to commit like any other.

    N is set to max(what the file says, HEAD's N + 1). That is monotonic and
    nothing more: it catches up a bump missed earlier, it never renumbers
    downward, and gaps are fine -- "no precision", in Morgan's own words.
    """
    # Resolved ONCE, before anything is written. Two reasons: a refusal has
    # to be atomic -- raising partway through would leave half the tree
    # stamped and half not, which is worse than either outcome -- and one
    # run is one moment, so every header it writes carries the same
    # timestamp rather than drifting a second apart down a long tree.
    stamp = _stamp()
    changed = []
    renames = renamed_from()
    for path in tracked_md_files():
        f = ROOT / path
        try:
            text = f.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        lines = text.splitlines()
        first = lines[0] if lines else ""
        if not is_header_attempt(first):
            continue  # never grows a header it didn't already carry

        body = "\n".join(lines[1:])
        head = read_at_head(path, "HEAD")
        if head is None:
            # New file, or one this commit renames. A creation starts at 1;
            # a rename keeps the counter it already had (renamed_from() is
            # the same distinction find_violations() draws, for the same
            # reason -- see its docstring).
            head = read_at_head(renames.get(path, path), "HEAD")
        if head is None:
            target, head_body = 1, None
        else:
            head_lines = head.splitlines()
            head_first = head_lines[0] if head_lines else ""
            head_body = "\n".join(head_lines[1:])
            head_n = _version_of(head_first) or 0
            now_n = _version_of(first)
            target = max(now_n if now_n is not None else head_n, head_n + 1)

        malformed = not HEADER_RE.match(first)
        if head_body is not None and body == head_body and not malformed:
            # Nothing pending for THIS file -- but HEAD's own commit may be
            # the unbumped one (an edit outside a session). Catch it up
            # rather than leaving a live violation for nobody to notice.
            catchup = _head_catchup_target(path, renames, head_first, head_body)
            if catchup is not None:
                new_first = HEADER_FMT.format(stamp=stamp, n=catchup)
                if new_first != first:
                    f.write_text("\n".join([new_first] + lines[1:]) + "\n",
                                 encoding="utf-8")
                    changed.append(
                        f"{path}: version -> {catchup} (catch-up: HEAD's "
                        "own header was left unbumped by the commit that "
                        "made it, likely an edit outside a session)")
            continue

        new_first = HEADER_FMT.format(stamp=stamp, n=target)
        if new_first == first:
            continue
        f.write_text("\n".join([new_first] + lines[1:]) + "\n",
                     encoding="utf-8")
        changed.append(f"{path}: version -> {target}"
                       + (" (header was malformed)" if malformed else ""))
    return changed


def _git(*args: str, data: bytes | None = None) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "-C", str(ROOT), *args], input=data,
                          capture_output=True)


def fix_staged() -> list[str]:
    """Bump the header of every markdown file IN THE COMMIT BEING MADE whose
    body changed and whose version did not rise -- in the index, so the bump
    rides that same commit. Run by `bootstrap/pre-commit-fix`, which the
    commit-identity backstop calls before every commit, in every repository.

    WHY THIS EXISTS (Morgan, 2026-09-27). `--fix` above is correct and was
    never the problem: it only works if somebody remembers to run it before
    `git add`, and on 2026-09-27 a session did not -- precedent-individual
    94e1c9f changed README.md at version 27, and the miss surfaced only when
    a Promote's full check refused it. Morgan asked for the miss to be
    prevented rather than caught sooner. A step nobody has to remember is
    the only kind that cannot be forgotten.

    Deliberately narrower than `--fix`, because this runs unasked and in
    repositories that are not this one:

    * STAGED FILES ONLY, AND ONLY THEIR STAGED CONTENT. The new blob goes
      into the index; an unstaged edit to the same file is never swept into
      the commit. The working tree's line 1 is updated too when it still
      reads what was staged, so the tree does not show the bump undone.
    * EXACT FORMAT ONLY. A file whose first line is not already a
      well-formed header is left alone -- never grown one, and never
      reformatted. An older, different header naming Morgan is somebody's
      decision to make, not a commit hook's.
    * NO CATCH-UP. A bump somebody missed in an earlier commit is `--fix`'s
      job; this touches nothing the current commit does not change.
    * AN AUTHOR'S OWN BUMP STANDS. A staged version already above HEAD's is
      not rewritten.
    * NEVER REFUSES. Anything it cannot do, it skips; the check itself is
      still the backstop.
    """
    stamp = None
    changed = []
    diff = _git("diff", "--cached", "-M", "--name-status", "--diff-filter=MR",
                "--", "*.md")
    if diff.returncode != 0:
        return changed
    for row in diff.stdout.decode("utf-8", "replace").splitlines():
        parts = row.split("\t")
        if len(parts) < 2:
            continue
        path, before = parts[-1], parts[-2] if parts[0].startswith("R") else parts[-1]
        if not_actionable_here(path):
            continue
        staged = _git("show", f":{path}")
        head = _git("show", f"HEAD:{before}")
        if staged.returncode != 0 or head.returncode != 0:
            continue
        try:
            text = staged.stdout.decode("utf-8")
            head_text = head.stdout.decode("utf-8")
        except UnicodeDecodeError:
            continue
        first, sep, body = text.partition("\n")
        m = HEADER_RE.match(first)
        if not m:
            continue
        head_first, _, head_body = head_text.partition("\n")
        if body == head_body:
            continue
        head_n = _version_of(head_first) or 0
        if int(m.group(5)) > head_n:
            continue
        if stamp is None:
            stamp = _stamp()
        new_first = HEADER_FMT.format(stamp=stamp, n=head_n + 1)
        blob = _git("hash-object", "-w", "--stdin",
                    data=(new_first + sep + body).encode("utf-8"))
        mode = _git("ls-files", "-s", "--", path).stdout.decode().split(" ")[0]
        if blob.returncode != 0 or not mode:
            continue
        info = f"{mode},{blob.stdout.decode().strip()},{path}"
        # `git commit <path>` builds the commit from a TEMPORARY index and
        # holds the real one locked (as index.lock) until the commit lands,
        # then puts that lock in place. Stamping only the temporary index
        # leaves the real one holding the old header, and the NEXT commit
        # would take the version backwards. So in that mode the locked real
        # index is stamped first -- and when it cannot be, nothing is.
        partial = os.path.basename(os.environ.get("GIT_INDEX_FILE", "")
                                   ).startswith("next-index")
        if partial:
            gitdir = _git("rev-parse", "--absolute-git-dir").stdout.decode().strip()
            locked = os.path.join(gitdir, "index.lock")
            if not os.path.isfile(locked):
                continue
            real = subprocess.run(
                ["git", "-C", str(ROOT), "update-index", "--cacheinfo", info],
                capture_output=True, env=dict(os.environ, GIT_INDEX_FILE=locked))
            if real.returncode != 0:
                continue
        if _git("update-index", "--cacheinfo", info).returncode != 0:
            continue
        work = ROOT / path
        try:
            wt = work.read_text(encoding="utf-8")
            wt_first, wt_sep, wt_rest = wt.partition("\n")
            if wt_first == first:
                work.write_text(new_first + wt_sep + wt_rest, encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            pass
        changed.append(f"{path}: version {head_n} -> {head_n + 1}")
    return changed


if __name__ == "__main__":
    if "--fix-staged" in sys.argv[1:]:
        try:
            for line in fix_staged():
                print(f"file-header: stamped {line}", file=sys.stderr)
        except Exception as exc:
            print(f"file-header: nothing stamped ({exc}); the check still "
                  f"catches a missed bump.", file=sys.stderr)
        sys.exit(0)
    if "--fix" in sys.argv[1:]:
        try:
            fixed = fix_working_tree()
        except ZoneUnresolved as exc:
            print("check_file_header --fix: REFUSED, nothing was stamped.")
            print(f"  {exc}")
            sys.exit(1)
        for line in fixed:
            print(f"  fixed {line}")
        print(f"check_file_header --fix: {len(fixed)} header(s) stamped "
              f"in the working tree. Commit them with the edit that "
              f"earned them.")
        sys.exit(0)

    findings = find_violations()
    if findings:
        print(f"VIOLATION: {PRACTICE_FILE.stem}")
        for f in findings:
            print(f"  {f}")
        print("\nthe rule:")
        print("  " + rule_text().replace("\n", "\n  "))
        sys.exit(1)
    sys.exit(0)
