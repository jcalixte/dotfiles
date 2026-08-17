---
name: nuke-comments
description: Use when the user wants every comment gone from code they just generated — "nuke the comments", "strip all comments", "remove comments from the files you created", "delete the AI comment noise" — or after an agent-heavy session that sprayed narration across new files. Measures the blast radius first, gets a decision, then strips mechanically.
---

# Nuke comments

Mechanical total strip, not editorial judgment. Every comment in the target files goes, except a
short protected list the toolchain actually reads. Nothing is deleted before the user picks.

For comment-by-comment judgment (keep the magic number, promote the rest into code), use
**prune-comments** instead. This skill is the blunt instrument: default target is the code files
*created in this repo*, and the default answer is "all of it".

## The script

`~/.claude/skills/nuke-comments/nuke_comments.py` — stdlib Python 3, no install.

```bash
python3 ~/.claude/skills/nuke-comments/nuke_comments.py            # impact report, created files
python3 ~/.claude/skills/nuke-comments/nuke_comments.py --json     # same, machine-readable
python3 ~/.claude/skills/nuke-comments/nuke_comments.py --only everything --apply
```

| Flag | Effect |
|---|---|
| *(no paths)* | files git reports as new — untracked + added. The default target. |
| `--changed` / `--tracked` | dirty files / every tracked code file |
| `PATH...` | explicit files or directories |
| `--only everything` | every non-protected comment |
| `--only file:src/a.ts` `--only kind:doc-block` `--only id:42` | narrower selection, repeatable |
| `--include-protected` | also strip directives, shebangs, TODOs, JSDoc types |
| `--apply` | write; originals copied to `.nuke-comments-backup/` first |
| `--self-test` | run the scanner fixtures |

It is string-aware per language, so `"# not a comment"` and `/https:\/\//` survive:

| Language | What the scanner knows |
|---|---|
| JS/TS/Vue/Svelte | regex literals, template `${…}` nesting, `<template>`/`<script>`/`<style>` regions |
| Rust | `'a` lifetime vs `'x'` char literal, raw/byte strings `r#"…"#` `b"…"`, nested `/* /* */ */` |
| Gleam | `////` module docs and `///` doc runs merged into one comment each |
| Go | backtick raw strings (no escape processing) |
| Python / shell / SQL | triple quotes, `$#` and `${#var}`, `--` only after whitespace |
| CSS/SCSS, HTML, Lua, Haskell, C-like | own scanners |

Unknown file types are skipped and listed, never guessed at.

Protected by default, reported separately: shebangs, toolchain directives (`eslint-disable`,
`@ts-expect-error`, `# noqa`, `//go:build`, `# shellcheck`, `/// <reference>`, `SPDX`…), JSDoc blocks
carrying types in untyped files, `TODO`/`FIXME`/`HACK` markers, **doctests** (a fenced ``` block in a
`///` / `//!` / `/**` comment compiles and runs as a test) and **`SAFETY:` / `PANICS:` invariants** on
unsafe blocks.

## Workflow

1. **Report.** Run the script with no `--apply`. Never guess the blast radius by reading files.
2. **Recap, then ask.** Post the recap in the shape below and put the choice to the user —
   AskUserQuestion when it is available, otherwise a numbered list. **"Everything" is always
   option 1**, whatever else you offer.
3. **Apply** exactly what was chosen: `--only everything`, or the `--only file:` / `kind:` / `id:`
   selectors matching the answer.
4. **Verify.** In order:
   - **Formatter first** — `cargo fmt`, `gleam format`, `oxfmt`/`prettier`. Deleting the only line
     inside a block leaves `fn() {\n  []\n}` that the formatter collapses; that drift is expected, and
     running the formatter is what keeps the diff honest.
   - `git diff -U0` — every added line must be the same code minus its comment.
   - The project's typecheck / lint / tests. Stripped directives fail here, not in review.
5. **Report back**: comments removed per file, lines removed, what stayed protected, backup path.

## Recap shape

The recap has four parts, in order:

1. One line of totals: `N comments, M lines, across K files`.
2. The per-file table from the script — file, count, lines, share of the file.
3. The protected list, with the reason each entry survives. If it's empty, say so in one line.
4. The choice: numbered options, **1 = everything**, then the narrower cuts that actually fit
   this report (a noisy file, `commented-code`, `doc-block`, `banner`), then abort.

No preamble, no per-comment quoting, no verdict on whether the comments were good.

## Red flags

| Thought | Reality |
|---|---|
| "The user said nuke, so just apply it" | The report and the choice come first. Always. |
| "I'll read the files and count comments myself" | You will miss comments inside strings and invent counts. Run the script. |
| "Only offer the safe subset" | "Everything" is option 1 in every recap, even a 900-comment one. |
| "Backups are overkill for new files" | New files have no git baseline — the backup dir is the only undo. |
| "Comment-only diff can't break the build" | `@ts-expect-error`, `//go:build`, `eslint-disable` are code. Run the checks. |
| "This file type isn't in the map, I'll strip it by hand" | Hand-stripping corrupts strings. Leave it, report it as skipped. |
