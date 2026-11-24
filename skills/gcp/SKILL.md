---
name: gcp
description: Git commit and push as conventional microcommits, no co-authoring. `/gcp simple` makes one commit for everything.
---

1. Read `git status`, `git diff HEAD`, `git log --oneline -5`.
2. One commit per logical change, staging only its files (`simple`: one commit, all files).
3. Conventional Commits `type(scope?): subject`, ≤72 chars, imperative, specific (never "fix"/"update"/"wip"). Body only if the why isn't obvious.
4. `git push` (`-u origin <branch>` if no upstream).

Never: `Co-authored-by` or any trailer, `--no-verify`, amending pushed commits, force-push unless asked.
