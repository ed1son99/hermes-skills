---
name: obsidian
description: Read, search, create, and edit notes in the Obsidian vault.
platforms: [linux, macos, windows]
---

# Obsidian Vault

Use this skill for filesystem-first Obsidian vault work: reading notes, listing notes, searching note files, creating notes, appending content, and adding wikilinks. For the specific pattern of exporting an agent's skill library as interlinked MOC notes, see `references/hermes-skill-catalog-pattern.md`.

## Vault path

Use a known or resolved vault path before calling file tools.

The documented vault-path convention is the `OBSIDIAN_VAULT_PATH` environment variable, for example from `${HERMES_HOME:-~/.hermes}/.env`. If it is unset, use `~/Documents/Obsidian Vault`.

File tools do not expand shell variables. Do not pass paths containing `$OBSIDIAN_VAULT_PATH` to `read_file`, `write_file`, `patch`, or `search_files`; resolve the vault path first and pass a concrete absolute path. Vault paths may contain spaces, which is another reason to prefer file tools over shell commands.

If the vault path is unknown, `terminal` is acceptable for resolving `OBSIDIAN_VAULT_PATH` or checking whether the fallback path exists. Once the path is known, switch back to file tools.

## Read a note

Use `read_file` with the resolved absolute path to the note. Prefer this over `cat` because it provides line numbers and pagination.

## List notes

Use `search_files` with `target: "files"` and the resolved vault path. Prefer this over `find` or `ls`.

- To list all markdown notes, use `pattern: "*.md"` under the vault path.
- To list a subfolder, search under that subfolder's absolute path.

## Search

Use `search_files` for both filename and content searches. Prefer this over `grep`, `find`, or `ls`.

- For filenames, use `search_files` with `target: "files"` and a filename `pattern`.
- For note contents, use `search_files` with `target: "content"`, the content regex as `pattern`, and `file_glob: "*.md"` when you want to restrict matches to markdown notes.

## Create a note

Use `write_file` with the resolved absolute path and the full markdown content. Prefer this over shell heredocs or `echo` because it avoids shell quoting issues and returns structured results.

## Append to a note

Prefer a native file-tool workflow when it is not awkward:

- Read the target note with `read_file`.
- Use `patch` for an anchored append when there is stable context, such as adding a section after an existing heading or appending before a known trailing block.
- Use `write_file` when rewriting the whole note is clearer than constructing a fragile patch.

For an anchored append with `patch`, replace the anchor with the anchor plus the new content.

For a simple append with no stable context, `terminal` is acceptable if it is the clearest safe option.

## Targeted edits

Use `patch` for focused note changes when the current content gives you stable context. Prefer this over shell text rewriting.

## Wikilinks

Obsidian links notes with `[[Note Name]]` syntax. When creating notes, use these to link related content.

When deleting or renaming notes, always search for remaining wikilinks pointing to the old name and fix them. Use `search_files` with `target: "content"` and a regex like `\[\[Old Name(\||\]\])` to find all references, then patch each one.

## Vault cleanup

When asked to clean up, deduplicate, or reorganize the vault:

1. **Full inventory** — `search_files(target="files", pattern="*.md")` to list every note.
2. **Find empties** — `read_file` each file; 0-byte files get deleted. Use `terminal` with `rm` for deletion (no dedicated delete tool).
3. **Spot duplicates** — read every file. Notes covering the same topic with overlapping content are candidates for merge. Two skill catalogs that list the same items in different formats → keep the newer/richer one, delete the other.
4. **Merge thin notes** — if a standalone note has ≤5 lines of unique content and that content already exists in a larger canonical note, merge the unique bits into the canonical note and delete the thin one.
5. **Fix wikilinks** — after any deletion, search for `[[Deleted Name` across all `.md` files and update to the new canonical target.
6. **Use redirect stubs** — when a deleted file still has incoming wikilinks you can't or shouldn't rewrite (e.g. thin MOC pages that many notes link to), replace the full content with a 3-5 line redirect note pointing to the canonical file. Include yaml frontmatter with the original `name` and `aliases` so Obsidian search/completion still works. This shrinks the file from hundreds of bytes to ~250B while keeping all links intact.
7. **Verify** — re-run `search_files(target="files", pattern="*.md")` to confirm the final count and structure.

### Pitfalls

- **Byte-level dedup misses semantic duplicates.** Two files can have different content yet cover the same topic with 80% overlap (e.g. two skill catalogs in different formats, or a user profile spread across multiple files). `execute_code` with `os.walk` + `hashlib.md5` finds exact duplicates; semantic duplicates require reading and comparing actual content.
- **Thin MOC files aren't empty but are noise.** A vault with 11 MOC pages each at 300-900B of link-only content creates visual clutter without adding value. Merge them into one consolidated page or redirect them all to a single canonical catalog.
- **Archives should be respected.** If a vault has a documented archive policy (e.g. `AGENTS.md` says "do not flatten or delete archive contents"), skip the Archive directories entirely during cleanup.

## Batch operations

When creating or editing many notes at once (e.g. generating a set of MOC pages per category), use `execute_code` to batch `write_file` / `patch` calls. This is faster than individual tool calls and keeps the workflow atomic.

When using `execute_code` for vault work, set `vault = "/path/to/vault"` once at the top and reference it in every call. Paths with spaces must be handled with string concatenation, not shell expansion.
