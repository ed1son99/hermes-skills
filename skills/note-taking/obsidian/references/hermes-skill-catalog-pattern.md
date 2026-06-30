# Hermes Skill Catalog in Obsidian

Pattern for exporting the agent's skill library into an Obsidian vault as interlinked MOC notes.

## Structure

```
Skills/
├── Hermes 技能总览.md       ← Main catalog: table of all N skills by category
├── Skill 统一目录.md         ← Optional: merged view (Hermes + other agent skills)
├── <Category Name>.md        ← One MOC per category, each skill gets a ### heading
└── ...
```

## Main catalog (Hermes 技能总览)

- Frontmatter with `tags: [skill, MOC, hermes]`
- One table per category: skill name | description
- Each category row links to its MOC note: `[[Skills/<Category>|<Category> MOC]]`
- Bottom: summary table with counts
- Bottom: cross-links to related notes

## Category MOC

- Frontmatter with `tags: [skill, MOC, <category>, hermes]`
- Each skill as `### skill-name` with one-line description
- Footer: `> 上级：[[Hermes 技能总览]]`

## Memory bank

Single canonical note (e.g. `阿蒙的记忆库.md`) covering:
- User profile (identity, goals, pain points)
- Communication rules (tone, forbidden phrases, shortcuts)
- Tech environment (model, OS, tools, paths)
- Core work (projects, workflows, toolchains)
- Agent self-description (name, role, configuration)
- Cross-links to skill catalog and external memory (Claude Memory)

## Cleanup checklist

1. List all `.md` with `search_files(target="files", pattern="*.md")`
2. `read_file` every file to find: empties (0 bytes), duplicates, thin notes
3. Delete empties with `terminal` + `rm`
4. Merge thin notes into canonical note, then delete
5. Delete duplicate catalogs (keep newest/richest)
6. Search dead wikilinks: `search_files(target="content", pattern="\[\[Deleted Name")`
7. Patch all dead links to new targets
8. Re-list to verify final count
