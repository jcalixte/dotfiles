---
name: crosslink
description: Crosslink markdown files in a folder so related notes reference each other. With an entrypoint argument (e.g. `/crosslink README.md`), only adds links from that entrypoint to the other files — one level of linking. Without an argument, crosslinks across all files in the folder (every file may link to others); ask the user before starting this fuller pass, and default the entrypoint to README.md if one exists.
---

# Crosslink markdown files

Add wiki-style or markdown links between related notes in a folder so the knowledge base navigates as a graph instead of a flat list.

## Input

The argument is either:

- **An entrypoint file** (e.g. `README.md`, `index.md`, `notes/overview.md`) — work in the folder that contains this file. Only ONE level of linking is required: add links *from the entrypoint* to other relevant files in the same folder. Do not touch the other files.
- **Nothing** — before doing anything, ask the user:
  1. Which folder to crosslink (default: current working directory).
  2. Confirm they want the full pass (every file may be modified to link to others), not just an entrypoint pass. If they want the lighter pass, ask for the entrypoint (default: `README.md` if it exists in the folder).

Resolve relative dates and folders against the current working directory.

## Process

1. **Read first.** Use Glob to list every `*.md` file in the target folder (non-recursive by default; ask if the user wants subfolders included when relevant). Read all of them — you cannot judge relevance without knowing what each note says. For large folders (>15 files), read titles + first ~30 lines of each, then deep-read on demand.

2. **Build a mental index.** For each file, note its main topic, key terms, and concepts that might be referenced elsewhere. Identify natural connections: shared terminology, prerequisite relationships, parent/child topics, contrasting ideas.

3. **Detect existing link style.** Scan a few files to determine which convention the folder already uses:
   - Markdown links: `[label](relative/path.md)`
   - Wiki links: `[[note-name]]`
   - Both / mixed
   
   Match the existing style. If the folder has no links yet, prefer markdown links (`[label](file.md)`) unless the user specifies otherwise.

4. **Add links.**
   - **Entrypoint mode:** edit ONLY the entrypoint. Add a links section (or weave links into existing prose) pointing to the other files in a sensible order — usually grouped by topic, or in reading order if a learning path is implied. Each link should have a one-line description of *why* a reader would follow it, not just the filename.
   - **Full mode:** for each file, add links to the 2–5 most strongly related other files. Place the link inline where the related concept first appears in the text, OR add a "See also" / "Related" section at the bottom — match the existing convention in the folder.

5. **Avoid noise.**
   - Do not link a file to itself.
   - Do not add a link unless there is a real conceptual connection — orphans are better than fake links.
   - Do not link the same target twice in the same file unless the second mention is in a meaningfully different context.
   - Preserve existing links; do not rewrite them unless they are broken.

6. **Report.** When done, output a short summary:
   - Files touched.
   - Number of links added per file.
   - Any files you deliberately left as orphans (and why — usually: no real connections found).

## Language

Match the language of the notes. If the notes are in French, link labels and any "Voir aussi" / "Related" headings should be in French too.

## Do not

- Do not rewrite or reformat the prose. This skill adds links; it does not edit content.
- Do not create new files.
- Do not modify frontmatter.
- Do not add links to external URLs — this skill is for internal crosslinking only.
