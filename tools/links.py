#!/usr/bin/env python3
"""Report [[wikilinks]] that resolve to no file name or frontmatter alias.

Usage: python3 tools/links.py
Exit code 1 if any link is unresolved.
"""
import re
import sys
from collections import defaultdict
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import corpus  # noqa: E402
LINK = re.compile(r"!?\[\[([^\]|#^]+)(?:[#^][^\]|]*)?(?:\|[^\]]*)?\]\]")


def norm(s):
    s = re.sub(r"[\s_]+", " ", s.strip()).lower()
    return s[4:] if s.startswith("the ") else s


def frontmatter(text):
    if not text.startswith("---\n"):
        return {}
    end = text.find("\n---", 4)
    if end == -1:
        return {}
    try:
        return yaml.safe_load(text[4:end]) or {}
    except yaml.YAMLError:
        return {}


def main():
    files = corpus.content_files(extra_top=("notes",))
    targets = {}
    for f in files:
        text = f.read_text(encoding="utf-8")
        targets[norm(f.stem)] = f
        for alias in frontmatter(text).get("aliases", []) or []:
            targets[norm(str(alias))] = f
        h1 = re.search(r"^# (.+)$", text, re.MULTILINE)
        if h1:
            targets[norm(h1.group(1))] = f
    missing = defaultdict(list)
    for f in files:
        for lineno, line in enumerate(f.read_text(encoding="utf-8").split("\n"), start=1):
            for m in LINK.finditer(line):
                name = m.group(1)
                if norm(name) not in targets:
                    missing[name].append(f"{f.relative_to(ROOT).as_posix()}:{lineno}")
    for name in sorted(missing, key=str.lower):
        where = ", ".join(missing[name])
        print(f"[[{name}]] unresolved ({len(missing[name])}x): {where}")
    print(f"{len(missing)} unresolved link targets across {len(files)} files")
    return 1 if missing else 0


if __name__ == "__main__":
    sys.exit(main())
