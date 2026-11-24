"""Which Markdown files count as canon content, independent of folder layout.

Content is every .md file in the repo except the working and tooling folders
below and the repo's own README and CLAUDE.md. Folders can be added, renamed
or reorganised freely; only a new non-content folder needs adding here.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Top-level folders that hold tooling, raw material or working notes, not canon.
NON_CONTENT = {"tools", "data", "sources", "notes", "maps"}

# Top-level files that describe the repo itself.
NON_CONTENT_FILES = {"README.md", "CLAUDE.md"}

# Folders whose files follow the conlang conventions instead of lorebook prose.
CONLANG = ["Languages/*"]


def is_content(relpath):
    """relpath: POSIX path relative to the repo root."""
    parts = relpath.split("/")
    if not relpath.endswith(".md"):
        return False
    if any(p.startswith(".") for p in parts):  # .git, .obsidian, .claude, .trash
        return False
    if len(parts) > 1 and parts[0] in NON_CONTENT:
        return False
    if len(parts) == 1 and parts[0] in NON_CONTENT_FILES:
        return False
    return "sync-conflict" not in parts[-1]


def content_files(extra_top=()):
    """All content files, plus any files under the top-level folders in extra_top."""
    out = []
    for p in ROOT.rglob("*.md"):
        relpath = p.relative_to(ROOT).as_posix()
        if is_content(relpath) or relpath.split("/")[0] in extra_top:
            out.append(p)
    return sorted(out)
