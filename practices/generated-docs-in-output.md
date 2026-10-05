---
slug:        generated-docs-in-output
title:       A document generated from a directory's content lives in that directory's output/ subdirectory
tier:        on-demand
severity:    default
applies_to:  ["**"]
occasion:    "building a document from a repository's content -- a Word file, a web page, a PDF, a deck -- or finding one that sits beside its sources"
gates:       []
index_clause: "a document built from a folder's content goes in that folder's output/"
checked_by:  null
defines:     []
status:      active
supersedes:  []
overrides:   null
added:       "2026-10-05"
approved_by: "Morgan F, 2026-10-05: \"Maybe have a standard practice in the 'ladders' repo that each directory has an output subdirectory where content docs that are generated from our content are created in an output subdirectory of the corresponding folder\""
strength:    decided
---
## Rule
**A document generated from a directory's content goes in an `output/`
subdirectory of that same directory.** A Word file built from
`social-media/SOCIAL_MEDIA_IDEAS.md` is
`social-media/output/<name>.docx`; a web page built from the pages in
`business-modeling/` is `business-modeling/output/<name>.html`. Not beside
its sources, and not in one `output/` at the top of the repository.

**`output/` holds generated files only.** Nothing in it is edited by hand:
a correction goes into the source or into the file's recipe, and the file is
rebuilt. Anything a person writes stays out of it, and so do the recipes,
which sit in the directory's own `doc-recipes/`.

**A document built from several directories goes under the directory of its
main source**, the one it is named for or the hub the others hang off.

**A generated file found elsewhere moves into `output/`** in the change that
finds it, with its build script's output path and every link to it updated
in the same commit (`rename-updates-links`).

## Detail
"Generated" means a build writes the file wholesale from sources in the
repository: a script, a recipe, a regeneration. A file someone supplied (a
PDF a partner sent, a logo a designer delivered) is source material, not
output, and stays wherever the repository keeps such things.

The point is that a reader can tell at a glance which files are the content
and which are renderings of it, and that the person maintaining a directory
finds everything built from it in one place, next to what it was built from.

## Why
The generated Word files in one repository had landed in three different
shapes: one in its book's `output/` directory, one loose beside the business
notes it was built from, and a third about to be added for the social media
ideas. Each was a choice a session made on its own. One rule makes the
choice once.

## Story
2026-10-05: asked for a Word file of the social media ideas, Morgan asked for
it in `social-media/output/` and for this to be the standard: every
directory with generated documents keeps them in an `output/` subdirectory of
its own. He asked for it in this set, which follows him into every
repository he works in. The same change moved the business concept's Word
file, which sat loose in `business-modeling/`, into
`business-modeling/output/` beside the web page built from the same notes.
