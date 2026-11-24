# Arlos

Worldbuilding bible for Arlos, a secondary world centred on the Circle Sea (Circuleana), developed by Jan toward a novel. The repo is the single source of truth: lorebooks, conlang, structured canon data, and later the manuscript.

## Layout

The repo root is Jan's Obsidian vault. Lorebooks live in content folders grouped by subject:

```text
Cosmology/          elements, aetheric arts, ineffable forces
Flora & Fauna/      gryphoids
Geography/          regions, settlements, water features
Languages/          conlang and naming (Remean, Suurese, others)
Material Reality/   engineering, metallurgy, measurements, currencies
Media/              in-world documents, crests, portraits
Organisations/      polities, houses, Lurist churches and orders
Peoples/            Alvai, Dvergr, humankind, beastkin
Timekeeping/        calendars, events, timelines
canon/              lorebooks from the scaffold not yet placed in the folders above
manuscript/         empty until the novel starts
```

Working and tooling folders sit beside them and are not content:

```text
data/               structured canon (timeline.yaml first)
sources/            converted source documents (older versions, catechism table, measurements)
maps/               map images
notes/              decisions from chat sessions not yet folded into a lorebook
tools/              lint, link and timeline checks
.obsidian/          vault settings, plugins and themes
```

The checks treat every Markdown file outside the working folders as content (`tools/corpus.py`), so content folders can be added or renamed freely. Links resolve by file name, not path.

`sources/` holds older or raw material. When a source and a lorebook disagree, the lorebook wins.

## Hard canon constraints

These are never violated, in lorebooks, notes, or conversation about the setting.

- No God or monotheistic deity, and no allusion to one. Quasi-divine entities (the Noble Elements, the Animal Spirits) are embodied in the world, often extremely powerful and cunning, never omnipotent or omniscient.
- Nothing below Newtonian physics: no atoms, molecules, electromagnetism, or other modern forces. Reality runs on six elements (Fire, Air, Water, Ice, Stone, Soil) arranged on a hexagon, with Antagonistic, Abeyant and Adjacent relations. Fulminance and Tension are the in-world Charges; lodestone, current, and the Charge of Air and Ice are the vocabulary.
- "Aether" is not air. It is the prevailing field theory of how the six elements' interactions give rise to reality. Aetheric modulation means provable, repeatable, precisely applied changes to that field.
- There are no birds. Every avian niche is filled by a gryph (a heraldic griffin made real, one per niche).
- The sprite rule: no prepared explosive mixtures, no steam engines, no internal combustion. Gunpowder does not exist as a word or concept; steam stays at kitchen and bath-house scale.
- No coal or petroleum. Fuel is charcoal and turpentine ("sprit" in common speech), later palmit; every furnace is bound to the woodlot.
- Iron is scarce (Varngard bog iron, the volcanic sands of Ertra and the Eastern Gyre coasts). Bronze is the tooling metal; abrasives and lapidary work compensate.
- Shaping was lost entirely at the Fall of Reme (0 AR), is religiously proscribed, and never appears as extant after the Fall.
- Terminology: the Hierophant's staff is the foculier, never a crozier. "Purified zinc" and "true brass", never "Remean-grade". Remeans are never "men"; Harmonized Remeans are ambigen. A moling is a sprite bond of any element; an adaling is a courtier bond.
- Damnatio memoriae: the theocracy never names recovered techniques after Reme.
- Writer-level mysteries stay open even where in-world theories exist. Do not flatten them into resolved mechanics.
- Staging matters: no anachronisms, every innovation traceable to prior conditions, no material or technology as a free lunch.

Dates use the civil count: years before the Fall of Reme are BR, after it AR, the Fall itself 0 AR.

## How we work

- Drafting loop: Claude proposes, Jan corrects, then the corrections are integrated as targeted edits. Never rewrite a whole file to apply a correction.
- Before drafting anything, search the content folders, `notes/` and `data/` for what is already established, and cross-reference before introducing new material.
- Earth-historical shorthand (Charlemagne, the Rhine, a Viking analogue) is fine in conversation and in `notes/`, never in lorebook prose.
- Do not flag open threads or pending decisions in replies. Jan tracks them separately.
- Prose conventions for lorebooks are in `.claude/rules/lorebook-prose.md`; conlang conventions in `.claude/rules/conlang.md`.
- Decisions Jan makes in conversation that are not yet in a lorebook go into `notes/canon_decisions.md`. When one is folded into a lorebook, remove it from the notes in the same branch.

## Git workflow

- `main` holds settled canon. Never commit to `main` directly.
- One topic per branch, named `lore/...`, `conlang/...`, `data/...` or `tools/...`, and a pull request for Jan to review.
- Commit messages name the file and the change in one line, for example `Svenu: move clinker riveting to the Remean Era`.
- If a change touches a date, update `data/timeline.yaml` in the same branch.

## Checks

- A PostToolUse hook runs `tools/lint.py --hook` after every edit and reports house-style or canon-constraint errors in the lines just changed. Fix them before moving on.
- Before opening a pull request, run all three and report the results in the PR:
  - `python3 tools/lint.py` (style and constraints across the corpus; `--summary` for counts)
  - `python3 tools/links.py` (unresolved `[[wikilinks]]`)
  - `python3 tools/check_timeline.py` (timeline schema, and dates in lorebooks that disagree with it)
- The linter's word lists live in `tools/lint_rules.py`. Extend them when Jan names a new forbidden term.
