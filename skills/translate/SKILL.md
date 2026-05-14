---
description: Translate into English
---

# Translate into English

Reading the file in parameter. Translate the markdown file.

Look after mistakes and weird expression as the author is French. Keep the same tone.

Directly modify the file.

Do NOT modify the frontmatter and reference part (only `## Références` into `## References`).

The file may be partially translated already (e.g. body in English but title/filename in French, or some headings already translated). Translate only what's still in French — for already-English parts, run them through the `/enhance` skill instead of leaving them as-is.

Translate the filename as well and modify its references in every other markdown files (ignore `node_modules`). When updating references, only translate the link text if it is a standalone title; leave it alone if it's embedded in a sentence in another language (only update the path in that case).

Summarize in the console the changes you've made so I can improve.
