---
description: Copy a previous Claude suggestion (code block, command, or text) to the macOS clipboard via `pbcopy`. Triggered by `/clip` with an optional selector argument.
---

# Clip

Copy a relevant prior suggestion from the current conversation into the macOS clipboard.

## When to use

- The user invokes `/clip` (with or without an argument).
- The user says "copy that", "put that in my clipboard", "clip the X".

Only consider **prior assistant turns** in this conversation as the source — never the user's own messages, and never content from files unless the user explicitly asks for that.

## How to pick what to copy

1. **If `/clip` has an argument**, treat it as a selector and pick the matching suggestion (e.g. `/clip the docker command`, `/clip the second function`, `/clip the SQL query`).
2. **If no argument**, default to the most recent concrete suggestion (code block, shell command, config snippet, or short body of advice) in the conversation.
3. **If multiple candidates are plausible** and the choice isn't obvious, list them as a short numbered menu (one line each, summarised) and ask the user to pick. Do not copy a guess.

Strip surrounding prose — copy only the raw payload (the code, the command, the value), not Claude's explanation around it. If the user explicitly wants the prose too, include it.

## How to copy

Use the Bash tool with a quoted heredoc so nothing in the content is expanded by the shell:

```bash
pbcopy <<'CLIP_EOF'
<content goes here verbatim>
CLIP_EOF
```

Use a delimiter unlikely to appear in the content (`CLIP_EOF` is fine for almost everything).

## After copying

Confirm in one short line what was copied — describe it, don't paste it back. Examples:

- "Copied the `docker compose up` command (1 line)."
- "Copied the `parseConfig` function (24 lines)."
- "Copied the migration SQL (3 statements)."

## Safety

- If the content looks like a secret (API key, password, token, private key), ask before copying.
- Never run any other side effects — this skill only writes to the clipboard.

## Platform note

Default to `pbcopy` (macOS). If on Linux, fall back to `xclip -selection clipboard` or `wl-copy`; on Windows, `clip.exe`. Only switch if `pbcopy` isn't available.
