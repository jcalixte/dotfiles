---
name: nuke-docs
description: Use when docs have outgrown their usefulness and the user wants only the essentials left — "nuke the docs", "strip the docs down", "keep only what's true", "delete the doc noise", "these READMEs are bloated" — or after an agent-heavy session that left specs, plans, worklogs and status sections behind. Measures what would go, gets a decision, then deletes.
---

# Nuke docs

Two questions decide what survives:

- **Product essence** — what this is, who it is for, what it does.
- **Tech essence** — how to run it, build it, deploy it, and reason about it.

A section that answers neither is not documentation, it is sediment. Diaries, status stamps, dated
snapshots, "previously we…", padded prose, duplicated passages, tables of contents nobody follows.

For section-by-section rewriting (compress the ADR, keep the decision, de-historicise the prose) use
**concise-doc**. This skill is the blunt instrument: it measures, you choose, whole sections and whole
files go. Same shape as **nuke-comments**, one difference — docs need judgment, so the script flags
what it is sure about and hands you the rest.

## The script

`~/.claude/skills/nuke-docs/nuke_docs.py` — stdlib Python 3, no install.

```bash
python3 ~/.claude/skills/nuke-docs/nuke_docs.py               # impact report, docs created in the repo
python3 ~/.claude/skills/nuke-docs/nuke_docs.py --tracked      # every tracked doc
python3 ~/.claude/skills/nuke-docs/nuke_docs.py --json         # machine-readable
python3 ~/.claude/skills/nuke-docs/nuke_docs.py --only everything --apply
```

| Flag | Effect |
|---|---|
| *(no paths)* | docs git reports as new — untracked + added. The default target. |
| `--changed` / `--tracked` | dirty docs / every tracked doc |
| `PATH...` | explicit files or directories |
| `--only everything` | every **flagged** section (not the unclassified ones) |
| `--only file:README.md` `--only kind:status` `--only id:42` | narrower, repeatable |
| `--include-instructions` | also touch CLAUDE.md / AGENTS.md / SKILL.md |
| `--apply` | write; originals copied to `.nuke-docs-backup/` first |
| `--self-test` | run the classifier fixtures |

It splits each doc into heading sections, then reports words, share of the file, and a verdict per
section. A file left with nothing but headings is deleted outright.

**Flagged** (what `everything` covers): `diary` (worklogs, dated headings), `history` (Background,
Changelog, "previously we…"), `status` (Status, Roadmap, Next steps, "as of 2026-08-04"),
`dated-doc` (a `2026-08-01-*.md` snapshot), `meta` (TOC, "about this document"), `padding` (AI filler
with no actionable fact), `duplicate` (>60% shingle overlap with a section already seen),
`dead-reference`, `empty`.

**Protected**, reported with a reason: front matter, document titles, parent headings, `product` and
`tech` sections, `reference` (term/option tables), sections carrying a fenced example, normative rule
sections, LICENSE/SECURITY text, instruction files, a heading another doc links to, and anything
marked `<!-- keep -->`. Force one with `--only id:<n>`.

It also surfaces signals without acting on them: dead links (file *and* anchor), stale
`pnpm run <script>` / `make <target>` references checked against `package.json` and the `Makefile`,
date stamps, past-state phrases.

## Workflow

1. **Report.** Run the script with no `--apply`.
2. **Judge the leftovers.** Every `JUDGE unknown` section: read it, decide product-essential,
   tech-essential, or sediment. Note the ids of the sediment — the script will not guess for you.
3. **Recap, then ask.** Post the recap in the shape below and put the choice to the user —
   AskUserQuestion when available, otherwise a numbered list. **"Everything" is always option 1**:
   `--only everything` plus the `id:`s you judged out.
4. **Apply** exactly what was chosen.
5. **Verify.**
   - Read the script's dangling-link report and fix or drop every link it names.
   - `git diff --stat` — deletions only, plus any link fix you made.
   - Re-read each surviving doc against the two questions. A README that no longer says what the
     thing is went too far — restore that section from `.nuke-docs-backup/`.
6. **Report back**: sections and files removed, words dropped, what stayed protected, backup path.

## Recap shape

Four parts, in order:

1. One line of totals: `N words in K docs, X% flagged, Y% needed judgment`.
2. The per-file table — file, words, flagged share, and the verdict per section.
3. What stays and why: the protected list, plus the essentials each doc will still carry.
4. The choice: numbered options, **1 = everything flagged + the ids you judged out**, then the
   narrower cuts this report actually supports (one bloated file, `kind:diary`, `kind:status`,
   dated snapshots only), then abort.

No preamble, no rewriting sections in the recap, no verdict on whether the docs were good.

## Red flags

| Thought | Reality |
|---|---|
| "The user said nuke, so just apply it" | The report and the choice come first. Always. |
| "I'll skim the docs and judge from memory" | Word counts and duplication are measured, not felt. Run the script. |
| "Unknown means safe to delete" | Unknown means unread. Read it, then decide — that is step 2. |
| "This spec is dated, so it is worthless" | Dated snapshots are the biggest single win *and* the easiest thing to regret. Flag it, let the user choose. |
| "CLAUDE.md is bloated too, take it with everything" | Instruction files are prompts; deleting a rule changes agent behavior. Needs `--include-instructions` and its own decision. |
| "The ADR repeats the design doc, so it is a duplicate" | An ADR's job is to hold the decision. Duplication is a signal, not a verdict. |
| "I'll rewrite these sections while I'm here" | That is concise-doc. This skill deletes; mixing the two makes the diff unreviewable. |
| "Deleting docs can't break anything" | It breaks every link pointing at them. Read the dangling report. |
