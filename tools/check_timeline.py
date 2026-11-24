#!/usr/bin/env python3
"""Validate data/timeline.yaml and compare it against dates stated in the lorebooks.

1. Schema: required fields, unique ids, integer years, end >= year, known eras,
   year inside its era, source files that exist, events in chronological order.
2. Cross-check: for every event with a `match` pattern, find sentences in the content files
   that match it and contain explicit years ("336 AR", "177 BR", "-355 AR",
   "the 360s AR", "(1117-1121)"). A sentence is reported when none of its years
   falls on the event's year or inside its span (circa events get +/-25 years).

Usage: python3 tools/check_timeline.py
Exit code 1 on schema errors; date disagreements are reported for review.
"""
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import corpus  # noqa: E402
TIMELINE = ROOT / "data" / "timeline.yaml"
CIRCA_SLACK = 25

YEAR_PATTERNS = [
    # decades: "360s AR"
    (re.compile(r"(\d{1,4})s\s*(AR|BR)\b"), "decade"),
    # ranges with an era: "1117-1121 AR", "0-8 AR", "-213 to -177 AR"
    (re.compile(r"([−-]?\d{1,4})\s*(?:-|–|to)\s*([−-]?\d{1,4})\s*(AR|BR)\b"), "range"),
    # single years: "336 AR", "177 BR", "-355 AR"
    (re.compile(r"([−-]?\d{1,4})\s*(AR|BR)\b"), "single"),
    # bare four-digit years in the AR range, as the later lorebooks write them: "in 1574", "(1561-1574)"
    (re.compile(r"(?<![\d-])(1[0-6]\d\d)(?!\d)"), "bare"),
]


def to_int(num, era):
    n = int(num.replace("−", "-"))
    if era == "BR":
        n = -abs(n)
    return n


def years_in(sentence):
    """Return (lo, hi, position) for every year mention in the sentence."""
    found = []
    taken = []
    for pat, kind in YEAR_PATTERNS:
        for m in pat.finditer(sentence):
            if any(m.start() < e and m.end() > s for s, e in taken):
                continue
            taken.append((m.start(), m.end()))
            if kind == "decade":
                start = to_int(m.group(1), m.group(2))
                found.append((start, start + 9, m.start()))
            elif kind == "range":
                a, b = to_int(m.group(1), m.group(3)), to_int(m.group(2), m.group(3))
                found.append((min(a, b), max(a, b), m.start()))
            elif kind == "single":
                y = to_int(m.group(1), m.group(2))
                found.append((y, y, m.start()))
            else:
                y = int(m.group(1))
                found.append((y, y, m.start()))
    return found


WINDOW = 80  # only years this close to the event's name count as dating it


def sentences(text):
    # blank out frontmatter so line numbers stay true to the file
    fm = re.match(r"^---\n.*?\n---\n", text, flags=re.DOTALL)
    if fm:
        text = "\n" * fm.group(0).count("\n") + text[fm.end():]
    # [[Target|Shown]] -> Shown, [[Target]] -> Target
    text = re.sub(r"\[\[[^\]|]*\|([^\]]*)\]\]", r"\1", text)
    text = re.sub(r"\[\[([^\]]*)\]\]", r"\1", text)
    for lineno, line in enumerate(text.split("\n"), start=1):
        for s in re.split(r"(?<=[.;!?])\s+(?=[A-Z\"*(])", line):
            if s.strip():
                yield lineno, s.strip()


def validate(data):
    errors = []
    eras = {e["id"]: e for e in data.get("eras", [])}
    seen = set()
    prev = None
    for ev in data.get("events", []):
        eid = ev.get("id", "?")
        for field in ("id", "year", "era", "title"):
            if field not in ev:
                errors.append(f"{eid}: missing {field}")
        if eid in seen:
            errors.append(f"{eid}: duplicate id")
        seen.add(eid)
        year = ev.get("year")
        if not isinstance(year, int):
            errors.append(f"{eid}: year must be an integer")
            continue
        end = ev.get("end", year)
        if not isinstance(end, int) or end < year:
            errors.append(f"{eid}: end must be an integer >= year")
        era = eras.get(ev.get("era"))
        if era is None:
            errors.append(f"{eid}: unknown era {ev.get('era')}")
        else:
            lo, hi = era.get("start", -10**6), era.get("end", 10**6)
            if not (lo <= year <= hi):
                errors.append(f"{eid}: year {year} outside era {era['id']} ({lo} to {hi})")
        for src in ev.get("sources", []):
            if not (ROOT / src).exists():
                errors.append(f"{eid}: source {src} does not exist")
        if prev is not None and year < prev:
            errors.append(f"{eid}: out of chronological order")
        prev = year
        if "match" in ev:
            try:
                re.compile(ev["match"])
            except re.error as exc:
                errors.append(f"{eid}: bad match pattern ({exc})")
    return errors


def fmt(y):
    return f"{-y} BR" if y < 0 else f"{y} AR"


def cross_check(data):
    docs = corpus.content_files()
    texts = {d: list(sentences(d.read_text(encoding="utf-8"))) for d in docs}
    reports = []
    for ev in data["events"]:
        if "match" not in ev:
            continue
        pat = re.compile(ev["match"])
        lo, hi = ev["year"], ev.get("end", ev["year"])
        if ev.get("circa"):
            lo, hi = lo - CIRCA_SLACK, hi + CIRCA_SLACK
        for doc, sents in texts.items():
            for lineno, s in sents:
                m = pat.search(s)
                if not m:
                    continue
                found = years_in(s)
                if any(a <= hi and b >= lo for a, b, _ in found):
                    continue  # the sentence states the timeline's date somewhere
                ys = [(a, b) for a, b, pos in found
                      if m.start() - WINDOW <= pos <= m.end() + WINDOW]
                if not ys:
                    continue  # no year close enough to the name to be dating it
                stated = ", ".join(fmt(a) if a == b else f"{fmt(a)}-{fmt(b)}" for a, b in ys)
                span = fmt(ev["year"]) if "end" not in ev else f"{fmt(ev['year'])}-{fmt(ev['end'])}"
                reports.append(
                    f"{ev['id']} (timeline {span}{', circa' if ev.get('circa') else ''}): "
                    f"{doc.relative_to(ROOT).as_posix()}:{lineno} states {stated}\n    \"{s[:160]}\""
                )
    return reports


def main():
    data = yaml.safe_load(TIMELINE.read_text(encoding="utf-8"))
    errors = validate(data)
    for e in errors:
        print(f"schema: {e}")
    reports = cross_check(data) if not errors else []
    for r in reports:
        print(f"review: {r}")
    print(f"{len(data.get('events', []))} events, {len(errors)} schema errors, {len(reports)} date disagreements to review")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
