---
name: gcp
description: Git commit and push using microcommits with conventional commits. No co-authoring. Use /gcp to commit staged or unstaged changes with a well-structured conventional commit message and push. Pass `simple` to commit everything as one big commit instead of splitting.
---

# Git Commit & Push (microcommit workflow)

Commit and push the current changes using microcommits and conventional commits. No co-authored-by lines ever.

## Modes

- **Default** (`/gcp`): microcommit workflow — split unrelated changes into separate commits.
- **Simple** (`/gcp simple`): one big commit for everything. Skip the splitting, don't overthink it — just stage all changes, write one good conventional-commit message covering them, commit, and push. **All other rules still apply** (conventional format, no co-authoring, no `--no-verify`, sensible message, push at the end).

## Rules

- **Never** add `Co-authored-by` or any trailer lines to commits.
- One logical change per commit (microcommit). If there are multiple unrelated changes staged, split them.
- Commit message must follow Conventional Commits: `<type>(<optional scope>): <short description>`
- Subject line ≤ 72 characters, imperative mood ("add" not "adds").
- Body is optional — include it only when the *why* isn't obvious from the diff.
- Never use `--no-verify`.

## Commit types

| Type | When to use |
|------|-------------|
| `feat` | New feature or behaviour |
| `fix` | Bug fix |
| `refactor` | Code change that isn't a fix or feature |
| `style` | Formatting, whitespace, no logic change |
| `test` | Adding or updating tests |
| `docs` | Documentation only |
| `chore` | Tooling, deps, config, CI |
| `perf` | Performance improvement |
| `revert` | Reverts a previous commit |

## Workflow

1. Run `git status` and `git diff` (staged + unstaged) to understand what changed.
2. Check `git log --oneline -5` to match the existing message style.
3. If unstaged changes exist and belong to the same logical unit, stage them. If they belong to a different concern, stage only the relevant files.
4. Draft the commit message:
   - Pick the right type.
   - Add a scope if it improves clarity (e.g. `fix(auth):`, `feat(notes):`).
   - Write a concise subject that answers "what does this commit do?".
   - Add a body only when the motivation isn't clear from the diff.
5. Commit using a heredoc to preserve formatting:
   ```bash
   git commit -m "$(cat <<'EOF'
   type(scope): short description

   Optional body explaining why, not what.
   EOF
   )"
   ```
6. Push to the current branch's upstream: `git push`.
7. If no upstream is set: `git push -u origin <branch>`.

## What NOT to do

- Do not add `Co-authored-by:` or any other trailer.
- Do not squash multiple unrelated changes into one commit (default mode only; `simple` intentionally combines them).
- Do not use vague messages like "fix", "update", "misc", "wip".
- Do not amend published commits.
- Do not force-push unless explicitly asked.
