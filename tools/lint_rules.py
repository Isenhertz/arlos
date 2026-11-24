"""Lint rules for tools/lint.py.

Each rule has a severity ("error" or "warning"), a message, and either a regex
`pattern` or a `words` list (matched as whole words, case-insensitive unless
ignore_case is False). `paths` and `exclude` are glob lists relative to the
repo root. Rules marked in_world_only are skipped for the files listed in
OUT_OF_WORLD (design notes written from outside the setting).

The PostToolUse hook only blocks on errors; warnings show up in full runs.
Kept as plain Python so the hook needs nothing beyond the standard library.
"""

PROSE = ["canon/**", "manuscript/**"]
ALL_TEXT = ["canon/**", "conlang/**", "manuscript/**"]

OUT_OF_WORLD = [
    "canon/science/Gunpowder_and_Steam.md",
]

# Deliberate in-world notation (dozenal shorthand), not reported as special characters.
ALLOWED_SPECIAL_CHARS = "⨳※⨝⁂"

RULES = {
    "em_dash": {
        "severity": "error",
        "pattern": "—",
        "message": "Em-dash; use ' -- ' instead",
        "paths": ALL_TEXT,
    },
    "en_dash": {
        "severity": "error",
        "pattern": "–",
        "message": "En-dash; use a plain hyphen for ranges (1117-1121) or ' -- ' for asides",
        "paths": ALL_TEXT,
    },
    "spaced_range": {
        "severity": "warning",
        "pattern": r"\b\d{1,4}\s+-{1,2}\s+\d{1,4}\b",
        "message": "Numeric range with spaces; write it as 1117-1121",
        "paths": PROSE,
    },
    "special_chars": {
        "severity": "warning",
        "kind": "special_chars",
        "message": "Special character outside letters and diacritics",
        "paths": PROSE,
    },
    "earth_shorthand": {
        "severity": "error",
        "in_world_only": True,
        "message": "Earth-historical shorthand in in-world prose",
        "paths": PROSE,
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
        "pattern": r"\bEarth\b|\bour own history\b|\bour world\b",
        "message": "Out-of-world reference to our own world",
        "paths": PROSE,
    },
    "sub_newtonian_physics": {
        "severity": "error",
        "message": "Physics below the Newtonian level; Arlos runs on the six elements and the Aether",
        "paths": ALL_TEXT,
        "words": [
            "atom", "atoms", "atomic", "subatomic", "molecule", "molecules", "molecular",
            "electron", "electrons", "proton", "protons", "neutron", "neutrons",
            "photon", "photons", "quantum", "electromagnetism", "electromagnetic",
            "electricity", "electric", "electrical", "magnetism", "magnetic", "nuclear",
            "isotope", "isotopes", "radioactive", "radioactivity", "relativity",
            "oxygen", "hydrogen", "nitrogen", "helium",
        ],
    },
    "monotheistic_deity": {
        "severity": "error",
        "pattern": r"\bGods?\b|\bAlmighty\b|\bthe Creator\b|[Mm]onothe",
        "message": "Monotheistic deity language; quasi-divine beings in Arlos are embodied, never omnipotent",
        "paths": ALL_TEXT,
    },
    "birds": {
        "severity": "error",
        "pattern": r"\w*birds?\b",
        "ignore_case": True,
        "message": "Birds do not exist on Arlos; every avian niche is a gryph",
        "paths": ALL_TEXT,
    },
    "forbidden_tech": {
        "severity": "error",
        "in_world_only": True,
        "message": "Gunpowder, explosives and steam power do not exist in-world",
        "paths": PROSE,
        "words": ["gunpowder", "black powder", "dynamite", "steam engine", "steam engines", "steam-engine"],
    },
    "terminology": {
        "severity": "error",
        "pattern": r"\b[Cc]rozier\b|Remean-grade",
        "message": "Retired term (foculier, not crozier; purified zinc and true brass, never Remean-grade)",
        "paths": PROSE,
    },
    "filename_reference": {
        "severity": "error",
        "pattern": r"\b[\w-]+\.(?:md|pdf|xlsx|csv)\b",
        "message": "Lorebooks are standalone; do not cite source filenames",
        "paths": PROSE,
    },
    "bullets_in_prose": {
        "severity": "warning",
        "pattern": r"^\s*[-*+]\s",
        "message": "Bullet point in lorebook prose",
        "paths": ["canon/**"],
        "exclude": ["canon/reference/**", "canon/history/Timeline_of_the_Circle_Sea.md"],
    },
    "open_threads_section": {
        "severity": "warning",
        "pattern": r"^#+\s*Open Threads",
        "message": "Open threads belong in Jan's own tracking, not in lorebooks",
        "paths": ["canon/**"],
    },
}
