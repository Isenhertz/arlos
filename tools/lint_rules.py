"""Lint rules for tools/lint.py.

Each rule has a severity ("error" or "warning"), a message, and either a regex
`pattern` or a `words` list (matched as whole words, case-insensitive unless
ignore_case is False). Rules apply to content files only (see tools/corpus.py).
`scope` is "all" (the default) or "prose"; prose rules skip the conlang folders.
`paths` and `exclude` are optional fnmatch globs on the repo-relative path,
where * also matches across folders, so name-based globs survive reorganising. Rules marked in_world_only are skipped for the files listed in
OUT_OF_WORLD (design notes written from outside the setting).

The PostToolUse hook only blocks on errors; warnings show up in full runs.
Kept as plain Python so the hook needs nothing beyond the standard library.
"""


# Globs, matched by file name so they hold wherever the file lives.
OUT_OF_WORLD = [
    "*Gunpowder?and?Steam.md",
    # Notes that carry Jan's real-world design analogues alongside in-world text.
    "*/Kiriya.md",
    "*/Reme.md",
    "*/Virell.md",
    "*/Merhal.md",
    "*/Alchemica.md",
    "*/Remea.md",
    "*/Gryphoids.md",
    "*/Theronga.md",
    "*/Gryphoid?visualisation.md",
]

# Gryphoid design notes that name real birds as the template for each gryph,
# plus Arlosian Material Science until Jan rewrites its "bird's bone" sentence himself.
BIRD_DESIGN_NOTES = [
    "*/Gryphoids.md", "*/Theronga.md", "*/Gryphoid?visualisation.md",
    "*/Arlosian?Material?Science.md",
]

# Content files that are not lorebooks (digests, overviews) and are skipped by every rule.
NOT_LOREBOOK = ["*/Technology?Snapshot?1420s.md"]

# Reference files where lists and tables are expected (bullets allowed).
REFERENCE = ["*Reference*.md", "*Timeline*.md", "*Arlosian?Mathematics.md"]

# Deliberate in-world notation (dozenal shorthand), not reported as special characters.
ALLOWED_SPECIAL_CHARS = "⨳※⨝⁂"

RULES = {
    "em_dash": {
        "severity": "error",
        "pattern": "—",
        "message": "Em-dash; use ' -- ' instead",
        "scope": "all",
    },
    "en_dash": {
        "severity": "error",
        "pattern": "–",
        "message": "En-dash; use a plain hyphen for ranges (1117-1121) or ' -- ' for asides",
        "scope": "all",
    },
    "spaced_range": {
        "severity": "warning",
        "pattern": r"\b\d{1,4}\s+-{1,2}\s+\d{1,4}\b",
        "message": "Numeric range with spaces; write it as 1117-1121",
        "scope": "prose",
    },
    "special_chars": {
        "severity": "warning",
        "kind": "special_chars",
        "message": "Special character outside letters and diacritics",
        "scope": "prose",
    },
    "earth_shorthand": {
        "severity": "error",
        "in_world_only": True,
        "message": "Earth-historical shorthand in in-world prose",
        "scope": "prose",
        "words": [
            "Rome", "Roman", "Romans", "Viking", "Vikings", "Charlemagne", "Rhine",
            "Byzantine", "Byzantium", "Mediterranean", "Inca", "Incan", "Aksum",
            "Achaemenid", "Persia", "Persian", "Islamic", "Amazon", "Andes",
            "Mycenaean", "Hellenistic", "Greek", "Carthage", "Carthaginian", "Venice",
            "Venetian", "Egyptian", "pharaoh", "pharaonic", "Norse", "Celtic",
            "Iberian", "Mongol", "samurai", "Spartan", "medieval", "Renaissance",
            "Victorian", "Napoleonic", "Buddha", "Jesus", "Muhammad", "steampunk",
        ],
    },
    "earth_reference": {
        "severity": "error",
        "in_world_only": True,
        # "Earth" alone is in-world usage for the ground; flag only the planet and our own history.
        "pattern": r"\bEarth's\b|\b(?:on|in) Earth\b|\bEarth (?:terms|birds|history)\b|\bour own history\b|\bour world\b",
        "message": "Out-of-world reference to our own world",
        "scope": "prose",
    },
    "sub_newtonian_physics": {
        "severity": "error",
        "message": "Physics below the Newtonian level; Arlos runs on the six elements and the Aether",
        "scope": "all",
        "words": [
            "atom", "atoms", "atomic", "subatomic", "molecule", "molecules", "molecular",
            "electron", "electrons", "proton", "protons", "neutron", "neutrons",
            "photon", "photons", "quantum", "electromagnetism", "electromagnetic",
            "electricity", "electric", "electrical", "nuclear",
            "isotope", "isotopes", "radioactive", "radioactivity", "relativity",
            "oxygen", "hydrogen", "nitrogen", "helium",
        ],
    },
    "monotheistic_deity": {
        "severity": "error",
        "pattern": r"\bGods?\b|\bAlmighty\b|\bthe Creator\b|[Mm]onothe",
        "message": "Monotheistic deity language; quasi-divine beings in Arlos are embodied, never omnipotent",
        "scope": "all",
    },
    "birds": {
        "severity": "error",
        "pattern": r"\w*birds?\b",
        "ignore_case": True,
        "message": "Birds do not exist on Arlos; every avian niche is a gryph",
        "scope": "all",
        "exclude": BIRD_DESIGN_NOTES,
    },
    "forbidden_tech": {
        "severity": "error",
        "in_world_only": True,
        "message": "Gunpowder, explosives and steam power do not exist in-world",
        "scope": "prose",
        "words": ["gunpowder", "black powder", "dynamite", "steam engine", "steam engines", "steam-engine"],
    },
    "terminology": {
        "severity": "error",
        "pattern": r"\b[Cc]rozier\b|Remean-grade",
        "message": "Retired term (foculier, not crozier; purified zinc and true brass, never Remean-grade)",
        "scope": "prose",
    },
    "filename_reference": {
        "severity": "error",
        "pattern": r"\b[\w-]+\.(?:md|pdf|xlsx|csv)\b",
        "message": "Lorebooks are standalone; do not cite source filenames",
        "scope": "prose",
    },
    "bullets_in_prose": {
        "severity": "warning",
        "pattern": r"^\s*[-*+]\s",
        "message": "Bullet point in lorebook prose",
        "scope": "prose",
        "exclude": REFERENCE,
    },
    "open_threads_section": {
        "severity": "warning",
        "pattern": r"^#+\s*Open Threads",
        "message": "Open threads belong in Jan's own tracking, not in lorebooks",
        "scope": "prose",
    },
}
