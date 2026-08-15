---
name: concise-doc
description: Use when documentation has gone stale or bloated — dated status stamps ("as of 2026-08-04"), "previously X, now Y" passages, History/Background sections, finished migration diaries, "we decided/we refactored" narration, flags and commands that no longer exist, dead links, or padded AI prose. Also use when the user asks to prune, de-historicise, shorten, or make a README/CLAUDE.md/wiki page state only what is true now. Covers ADRs, which keep their decision history but get compressed.
---

# Concise doc

Documentation describes the present. Git holds the past. Any sentence that exists to record when something changed, what it used to be, or who decided it is spending the reader's attention on a state they will never meet.

Three things come out in one pass:

1. Outdated. The doc claims something the code no longer does.
2. Historic. The doc narrates change instead of describing state.
3. Bloated. The doc says in six paragraphs what fits in a table.

A passage survives only if a reader acting today would do the wrong thing without it.

**REQUIRED SUB-SKILL:** run ai-writing-tropes over every file you touch, in the same pass. Pruning history and leaving padded AI prose behind is half a job.

## Outdated: verify against the code, don't guess

Every concrete noun in a doc is a claim you can check. Grep before you trust it.

| Doc claims | Check |
|---|---|
| a CLI flag, subcommand, env var | grep the parser / config loader |
| a file or directory path | does the path exist |
| a script (`pnpm run build:legacy`) | is it still in `package.json` |
| an endpoint, a table, a config key | grep the route table / schema |
| a version floor (`requires Node >= 18`) | `engines`, CI matrix, lockfile |
| a URL | fetch it, or at least check the domain still resolves |
| a screenshot of the UI | does the current UI look like that |

What fails the check:

- Delete it, if it documents something that no longer exists.
- Correct it, if the section is load-bearing (install, build, run) and today's answer is obvious from the code. Correcting is not licence to rewrite the section's shape.
- Ask, if the section is load-bearing and the current answer is not obvious. Do not invent an instruction you have not run.

Duplicate pages count as outdated. When two files document the same thing and one is stale, delete the stale one and link the survivor, rather than merging both into a longer page.

## Historic: keep the fact, drop the frame

Most historic sentences carry a live fact inside a dead frame.

| Historic | Present |
|---|---|
| `As of 2026-08-04 the token has push access everywhere.` | `The token has push access everywhere.` |
| `Fixed 2026-08-08. Two guards now protect this.` | `Two guards protect this:` |
| `We migrated from Webpack to Vite in v3.` | `Build runs on Vite.` |
| `Previously this read from env; it now reads config.toml.` | `Reads config.toml.` |
| `After discussion we chose a queue here for backpressure.` | delete, the queue is in the code |
| `Note: since 2.1, retries are automatic.` | `Retries are automatic.` (unless 2.0 is still supported) |
| `NEW! Dark mode support.` | `Supports dark mode.` |
| `Currently no CLI, but one is planned.` | delete, or open an issue |

Delete outright:

- Dated status stamps: `As of <date>`, `At the time of writing`, `Updated <date>`, `Verified <date>`.
- History, Background, Previously, Legacy notes, Old behaviour, `(pre-<date>)` blocks describing unreachable state.
- Before/after pairs where only "after" is reachable.
- Session and PR narration: "we refactored this to...", "this broke in #412", "after the auth cleanup".
- Migration diaries for migrations nobody is still running. The result stays, the steps go.
- Decision justification with no operational consequence. If it constrains future edits ("must stay O(1), called per frame"), it is a constraint: rewrite it as one.
- Relative time words: recently, new, now supports, finally, no longer, still, coming soon for things that shipped.
- Stale future tense: "will be replaced by X" where X already replaced it.
- Changelog fragments pasted into reference docs. Link the CHANGELOG.

Keep, rewritten to present tense:

- Live deprecations. State the old path, the replacement, and the removal version.
- Version-conditional behaviour across supported versions: `Requires Node >= 20; on 18 the parser rejects top-level await.`
- Open upstream workarounds, with the issue link and the trigger condition. Drop when-we-found-it.
- Data left behind by an old system: `Rows created before v4 have a null tenant_id; treat null as the default tenant.` The date is dead, the null is alive.
- Security state a reader must act on: a credential still needing rotation, an advisory hitting versions still deployed.
- Dated facts that are the content: benchmarks, pricing snapshots, survey results. The date is the caveat that keeps the number honest.

## Concise: the file gets shorter

Run the ai-writing-tropes checklist and cut what it flags. The ones that dominate technical docs:

- Fractal summaries. An Overview restating the title, a section preview, then a recap of what was just read. Keep at most one orienting sentence per file.
- One-point dilution. The same instruction rephrased in three registers.
- Listicle in a trench coat. "The first thing... The second thing..." wrapped in prose. Make it a list or a table.
- Bold-first bullets. A wall of `**Thing**: description` reads as generated. Write the sentence.
- Em-dash addiction and unicode arrows.
- "It's worth noting", "Here's the thing", "Let's break this down", "Think of it as".
- Prose that describes a command instead of showing it. Show the command.

Structure beats paragraphs: reference material becomes a table, sequences become numbered steps, options become a list.

Concision has a floor. Do not compress a doc into something only its author can parse, do not drop the one example that makes an API usable, and do not delete an explanation just because it is long. Length is not the target, redundancy is.

## ADRs

An ADR is a decision record, so its history is its content. It stays in scope for this pass, but the pass is compression, not deletion.

Never do:

- Delete an ADR, including superseded ones.
- Edit a past decision to match what the code does now. If reality moved, that is a new ADR superseding the old one.
- Strip the status line or the supersedes/superseded-by links. That chain is the only navigable history.
- Remove the consequences, including the ones that aged badly.

Do:

- Compress context to the few lines that make the decision legible. The full backstory belongs in the linked issue.
- Turn the options considered into a table: option, tradeoff, why rejected. One line each.
- Cut meeting narration: who attended, what was discussed at length, how long it took.
- Cut restated background available in another ADR. Link it.
- Keep the decision itself verbatim in meaning. Compress the wording, never the commitment.

Target shape: status, context, decision, consequences, links. A reader should reconstruct the decision in under a minute.

## Never touch

These files are the historic record, and pruning them destroys their reason to exist: `CHANGELOG.md`, release notes, migration and upgrade guides, RFCs, post-mortems, meeting notes, journals, dated blog posts, `LICENSE` and `NOTICE`, and anything under `history/`, `archive/`, or `_posts/`.

Ambiguous file, like a `NOTES.md` mixing reference and diary: ask before editing. Do not guess.

## What counts as the docs

Scope is a folder: the one the user named, or the working directory. Two sets, unioned, then the never-touch list subtracted.

Every markdown file under that folder, at any depth. In a doc folder, markdown is the product, so all of it is in scope:

```bash
git ls-files '*.md' '*.markdown' -- .        # or, outside a checkout:
find . -name '*.md' -o -name '*.markdown'
```

Every markdown file reachable from that folder's `README.md`, followed transitively. A page linked from a page linked from the README is still the README's responsibility, and it lives anywhere: `CONTRIBUTING.md`, `docs/setup/aws.md`, `packages/api/README.md`.

```bash
# BFS from README.md over relative markdown links
q=(README.md); seen=()
while ((${#q[@]})); do
  f=${q[0]}; q=("${q[@]:1}")
  [[ " ${seen[*]} " == *" $f "* ]] && continue
  seen+=("$f"); [[ -f $f ]] || { echo "BROKEN: $f"; continue; }
  d=$(dirname "$f")
  while read -r t; do
    t=${t%%#*}; t=${t%% *}; [[ -z $t || $t == http* ]] && continue
    q+=("$(realpath -m --relative-to=. "$d/$t")")
  done < <(grep -oE '\]\([^)]+\.(md|markdown)[^)]*\)' "$f" | sed -E 's/^\]\(|\)$//g')
done
for f in "${seen[@]}"; do [[ -f $f ]] && echo "$f"; done
```

Three signals fall out of the traversal, and all three are findings:

- Broken links. A README pointing at a file that no longer exists is outdated content. Fix the path or delete the link, and say which in the report.
- Orphans. Markdown under the folder that nothing reaches, which is where stale docs go to hide. List them with a one-line guess at what they were for and ask. Never delete an orphan unprompted, and never assume a missing README link means the file is dead: `.github/` templates, `LICENSE`-adjacent files, and tool-read files like `CLAUDE.md` are reachable by convention, not by link.
- Escapees. Links that resolve outside the folder (`../shared/api.md`). They belong to the README, so they are in scope, but they are also somebody else's file. List them separately and let the user drop them before the first edit.

Present the resolved set before editing. Big trees get grouped by directory rather than listed file by file.

## How

1. Scope it. Files or folders the user named. With no argument, resolve the set above and confirm it.
2. Read each file whole. A passage is only history if the rest of the file states the current value. Cutting "previously X" when nothing else says what X is now loses the fact.
3. Verify claims against the code, using the table above. Reachability decides version claims: a "fixed upstream" note is dead only once the fix is in the pinned version.
4. Cut and rewrite. Present tense, seams repaired: orphan headings, empty sections, dangling transitions, intros that promise content you deleted.
5. Run ai-writing-tropes over what remains.
6. Repair links. A deleted heading breaks every anchor and TOC entry aimed at it. Grep the folder for the slug, and the wider checkout if there is one, then fix or drop the referrers.
7. Verify, not optional. Read `git diff -- <paths>` hunk by hunk and name where each deleted fact now lives, or restore it. Grep for removed anchors. Run the docs build or link checker if the project has one.
8. Report: deleted, rewritten, corrected against code, kept with reason, moved and where. Include before/after line counts per file. The user can overrule any of it.

When a fact is genuinely historic and genuinely valuable, move it rather than destroy it: append to the CHANGELOG or write the ADR, in the same commit, and say so in the report. Never park it in a comment or a `docs/old/` folder nobody opens.

## Red flags

| Thought | Reality |
|---|---|
| "This explains why the code is like this" | Rationale is not history. A constraint on future edits gets rewritten as a constraint; the rest goes. |
| "Someone might wonder what changed" | They have `git log` and the CHANGELOG. This file answers what is true. |
| "The date makes it more credible" | A date on a claim makes it expire on schedule. Dates stay on measurements and snapshots only. |
| "I'll trim the History section rather than cut it" | The section itself is the artifact. Delete it whole, salvage live facts into the body. |
| "It says 'no longer', so it describes the present" | It describes the past with a present-tense verb. Say what happens, not what stopped. |
| "The flag is probably still there" | Probably is not a check. Grep it. |
| "The install command looks wrong, I'll write the right one" | Only if the code shows it. Otherwise ask. Invented instructions are worse than stale ones. |
| "This link points outside the folder, so it's out of scope" | The README owns it. List it as an escapee and let the user decide. |
| "Both pages have good content, I'll merge them" | Merging grows the doc. Delete the stale one, link the survivor. |
| "This ADR is obsolete, prune it" | Superseded ADRs stay, marked superseded. New reality means a new ADR. |
| "The ADR's context is long but interesting" | Compress to what makes the decision legible, link the issue for the rest. |
| "The doc is shorter, so the pass worked" | Shorter and wrong is a regression. Every deletion needs a surviving home or a reason. |
| "I'll tighten this wording too" | Only under the tropes checklist. Rewriting prose you merely dislike is out of scope. |
| "User said delete everything, so the CHANGELOG too" | Everything means every dead claim in the docs. Record files are the stated exception. |
