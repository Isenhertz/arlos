# Arlos

Worldbuilding bible for Arlos, a secondary world centred on the Circle Sea, written toward a novel.

## What lives where

| Folder | Contents |
|---|---|
| `Cosmology/`, `Flora & Fauna/`, `Geography/`, `Languages/`, `Material Reality/`, `Media/`, `Organisations/`, `Peoples/`, `Timekeeping/` | Lorebooks, grouped by subject |
| `canon/` | Lorebooks from the original scaffold not yet placed in the subject folders |
| `data/` | Structured canon; `timeline.yaml` holds the dated events the lorebooks are checked against |
| `notes/` | Decisions from conversation that are not yet folded into a lorebook |
| `sources/` | Converted source documents: older drafts, the comparative catechism table, the measurement tables |
| `maps/` | Map images |
| `tools/` | Checks for house style, canon constraints, links and dates |
| `manuscript/` | Empty until the novel starts |

Everything outside `data/`, `notes/`, `sources/`, `maps/` and `tools/` counts as content for the checks, so subject folders can be added or renamed without touching the tools.

The repo root is an Obsidian vault: `[[wikilinks]]` and the `aliases:` frontmatter resolve there.

## Working on it

`CLAUDE.md` holds the hard canon constraints, prose conventions and workflow that every Claude Code session follows. In short: `main` is settled canon, every change arrives on a branch as a pull request, and corrections are applied as targeted edits.

## Checks

```bash
python3 tools/lint.py            # house style and canon constraints (add --summary for counts)
python3 tools/links.py           # [[wikilinks]] that resolve to nothing
python3 tools/check_timeline.py  # timeline schema, and lorebook dates that disagree with it
```

`tools/lint.py` also runs automatically as a Claude Code hook after every edit, on the changed lines only. The timeline check needs PyYAML (`pip install pyyaml`); the linter needs nothing beyond Python 3.
