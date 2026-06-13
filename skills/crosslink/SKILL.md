---
name: crosslink
description: Crosslink markdown files in a folder so related notes reference each other. With an entrypoint argument (e.g. `/crosslink README.md`), adds links from the entrypoint to related files AND backlinks from each of those files to the entrypoint — bidirectional, but only touching files that connect to the entrypoint. Without an argument, crosslinks across all files in the folder (every file may link to others); ask the user before starting this fuller pass, and default the entrypoint to README.md if one exists.
---

# Crosslink markdown files

Add wiki-style or markdown links between related notes in a folder so the knowledge base navigates as a graph instead of a flat list.

## Input

The argument is either:

- **An entrypoint file** (e.g. `README.md`, `index.md`, `notes/overview.md`) — work in the folder that contains this file. Add links *from the entrypoint* to other relevant files in the same folder, AND add a backlink *from each of those linked files back to the entrypoint*. Files that are not connected to the entrypoint are left untouched.
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

4. **Add links — inline blending is the strong default.** A link should *be* a noun phrase the sentence already needs, not a pointer appended to it. The text should still read as a normal sentence if you removed the link syntax. Save "See also" lists for the rare case where no natural anchor exists anywhere in the text.

   **Hierarchy of placement (try in order, stop at the first that works):**
   1. **The concept is already named in the text.** Wrap that noun phrase in the link. Often zero other words change.
      - Bad: `Build a culture of stopping to fix problems (jidoka). See [jidoka](tps/jidoka.pub.md).`
      - Good: `Build a culture of stopping to fix problems ([_jidoka_](tps/jidoka.pub.md)).`
   2. **The concept fits naturally into an existing sentence.** Reword *lightly* so the link sits on a real noun phrase. Light rewording is allowed (and encouraged) when it produces a sentence that reads better than the original — but the meaning must not shift.
      - Bad: `Use visual control so no problems are hidden. Voir [kanban](kanban.md), [andon](andon.md).`
      - Good: `Use visual control — through a [kanban](kanban.md) board or an [andon](andon.md) signal — so no problems are hidden.`
   3. **A short follow-up sentence reads naturally.** If neither of the above fits, add one sentence that genuinely belongs in the prose (a clarification, an example, a contrast), with the link inside it. The sentence must stand on its own as content, not as a pointer.
      - Bad: `... reduce the lead time. See [value stream mapping](value-stream-mapping.md).`
      - Good: `... reduce the lead time. A [value stream map](value-stream-mapping.md) makes the wasted time visible step by step.`
   4. **Appended list — last resort.** Only if the file has no natural anchor anywhere (very short stubs, pure outlines), add to an existing references/see-also section, or create one if none exists.

   **Anti-patterns — do not write these:**
   - `See [X](x.md).` / `Voir [X](x.md).` as a standalone sentence.
   - `→ [X](x.md)` arrows tacked onto the end of a line.
   - "Voir aussi" / "See also" blocks at the bottom when the concept is already named in the body.
   - Parenthetical pointers like `(see [X](x.md))` when the concept itself could carry the link.

   **Entrypoint mode** vs **full mode** affects *which* files get linked, not *how* you link. Both modes follow the placement hierarchy above.

   - **Entrypoint mode:** weave links from the entrypoint to related files into the existing prose using the hierarchy above. The link goes on the natural concept name; if the entrypoint is a structured list (e.g. principles, glossary, table of contents), the link goes on a key noun in each item rather than on a "see X" suffix. Then add backlinks the same way in each linked file. Files you did not link to from the entrypoint stay untouched.
   - **Full mode:** for each file, add links to the 2–5 most strongly related other files, placed by the same hierarchy.

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

- Do not restructure or rewrite content. Light rewording in service of natural link placement is allowed (see step 4); broader edits to prose, structure, or argument are not.
- Do not create new files.
- Do not modify frontmatter.
- Do not add links to external URLs — this skill is for internal crosslinking only.
- Do not introduce "Voir [X]" / "See [X]" sentences. The link belongs on the concept name, not on a meta-pointer.
