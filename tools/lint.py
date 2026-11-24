#!/usr/bin/env python3
"""House-style and canon-constraint linter for the Arlos bible.

Modes
  python3 tools/lint.py                 lint every content Markdown file (see tools/corpus.py)
  python3 tools/lint.py PATH [PATH...]  lint the given files
  python3 tools/lint.py --summary       per-rule counts per file (baseline report)
  python3 tools/lint.py --hook          Claude Code PostToolUse hook: reads the hook JSON on
                                        stdin, lints only the lines changed since the last
                                        commit in the edited file, exits 2 on errors so the
                                        findings are shown to Claude

Rules and word lists live in tools/lint_rules.py so they can be edited without
touching this script. Standard library only, so the hook runs anywhere.
"""
import json
import re
import subprocess
import sys
import unicodedata
from collections import Counter, defaultdict
from fnmatch import fnmatch
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import corpus  # noqa: E402
import lint_rules  # noqa: E402


def load_rules():
    return {
        "rules": lint_rules.RULES,
        "out_of_world": lint_rules.OUT_OF_WORLD,
        "allowed_special_chars": lint_rules.ALLOWED_SPECIAL_CHARS,
    }


def rel(path):
    try:
        return Path(path).resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return Path(path).as_posix()


def applies(rule, relpath):
    if rule.get("scope") == "prose" and any(fnmatch(relpath, p) for p in corpus.CONLANG):
        return False
    include = rule.get("paths", ["*"])
    exclude = rule.get("exclude", [])
    return any(fnmatch(relpath, p) for p in include) and not any(fnmatch(relpath, p) for p in exclude)


def compile_rules(cfg):
    compiled = []
    for name, rule in cfg["rules"].items():
        r = dict(rule)
        r["name"] = name
        if "pattern" in r:
            r["regex"] = re.compile(r["pattern"], re.IGNORECASE if r.get("ignore_case") else 0)
        elif "words" in r:
            words = sorted(r["words"], key=len, reverse=True)
            alt = "|".join(re.escape(w) for w in words)
            flags = re.IGNORECASE if r.get("ignore_case", True) else 0
            r["regex"] = re.compile(r"(?<![\w-])(?:" + alt + r")(?![\w-])", flags)
        compiled.append(r)
    return compiled


def special_chars(line, allowed):
    hits = []
    for ch in line:
        if ch in allowed or ch.isascii():
            continue
        cat = unicodedata.category(ch)
        if cat.startswith("L") or cat.startswith("M"):
            continue  # letters with diacritics, thorn, eth etc.
        hits.append(ch)
    return hits


def lint_lines(relpath, numbered_lines, rules, cfg):
    """numbered_lines: iterable of (lineno, text). Returns list of findings."""
    findings = []
    out_of_world = any(fnmatch(relpath, g) for g in cfg.get("out_of_world", []))
    allowed = set(cfg.get("allowed_special_chars", ""))
    in_frontmatter = False
    in_code = False
    for lineno, text in numbered_lines:
        stripped = text.strip()
        if lineno == 1 and stripped == "---":
            in_frontmatter = True
            continue
        if in_frontmatter:
            if stripped == "---":
                in_frontmatter = False
            continue
        if stripped.startswith("```"):
            in_code = not in_code
            continue
        if in_code:
            continue
        for r in rules:
            if not applies(r, relpath):
                continue
            if out_of_world and r.get("in_world_only"):
                continue
            kind = r.get("kind", "regex")
            if kind == "special_chars":
                hits = special_chars(text, allowed)
                if hits:
                    shown = " ".join(sorted({f"{c} (U+{ord(c):04X})" for c in hits}))
                    findings.append((relpath, lineno, r["severity"], r["name"], f"{r['message']}: {shown}"))
                continue
            for m in r["regex"].finditer(text):
                findings.append((relpath, lineno, r["severity"], r["name"], f"{r['message']}: \"{m.group(0)}\""))
    return findings


def lint_file(path, rules, cfg, only_lines=None):
    relpath = rel(path)
    with open(path, encoding="utf-8") as fh:
        lines = fh.read().split("\n")
    numbered = list(enumerate(lines, start=1))
    findings = lint_lines(relpath, numbered, rules, cfg)
    if only_lines is not None:
        findings = [f for f in findings if f[1] in only_lines]
    return findings


def changed_lines(path):
    """Line numbers added or modified relative to HEAD. None means 'whole file' (untracked)."""
    relpath = rel(path)
    tracked = subprocess.run(
        ["git", "-C", str(ROOT), "ls-files", "--error-unmatch", relpath],
        capture_output=True,
    ).returncode == 0
    if not tracked:
        return None
    diff = subprocess.run(
        ["git", "-C", str(ROOT), "diff", "--unified=0", "HEAD", "--", relpath],
        capture_output=True, text=True,
    ).stdout
    lines = set()
    for m in re.finditer(r"^@@ -\d+(?:,\d+)? \+(\d+)(?:,(\d+))? @@", diff, re.MULTILINE):
        start, count = int(m.group(1)), int(m.group(2) or "1")
        lines.update(range(start, start + count))
    return lines


def default_files():
    return corpus.content_files()


def print_findings(findings, stream):
    for relpath, lineno, sev, name, msg in findings:
        print(f"{relpath}:{lineno}: {sev}: [{name}] {msg}", file=stream)


def run_hook(rules, cfg):
    try:
        payload = json.load(sys.stdin)
    except json.JSONDecodeError:
        return 0
    path = (payload.get("tool_input") or {}).get("file_path")
    if not path or not path.endswith(".md"):
        return 0
    relpath = rel(path)
    if not corpus.is_content(relpath):
        return 0
    if not Path(path).exists():
        return 0
    findings = lint_file(path, rules, cfg, only_lines=changed_lines(path))
    errors = [f for f in findings if f[2] == "error"]
    if errors:
        print("House-style or canon-constraint problems in the lines you just changed:", file=sys.stderr)
        print_findings(errors, sys.stderr)
        print("Fix these before moving on (see CLAUDE.md for the rules).", file=sys.stderr)
        return 2
    return 0


def main(argv):
    cfg = load_rules()
    rules = compile_rules(cfg)
    if "--hook" in argv:
        return run_hook(rules, cfg)
    summary = "--summary" in argv
    paths = [a for a in argv if not a.startswith("--")]
    files = [Path(p) for p in paths] if paths else default_files()
    all_findings = []
    for f in files:
        all_findings.extend(lint_file(f, rules, cfg))
    if summary:
        per_file = defaultdict(Counter)
        for relpath, _, sev, name, _ in all_findings:
            per_file[relpath][f"{sev}:{name}"] += 1
        totals = Counter()
        for relpath in sorted(per_file):
            counts = ", ".join(f"{k} {v}" for k, v in sorted(per_file[relpath].items()))
            print(f"{relpath}: {counts}")
            totals.update(per_file[relpath])
        print("TOTAL: " + ", ".join(f"{k} {v}" for k, v in sorted(totals.items())))
    else:
        print_findings(all_findings, sys.stdout)
    return 1 if any(f[2] == "error" for f in all_findings) else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
