---
name: clone-repo
description: Use when the user asks to clone / fetch / pull down a repository, especially terse asks like "clone into ." where the host, owner, or URL is not spelled out. Resolves the clone target from host-scoping keywords and per-host owner defaults, handles git.apoena.dev's non-standard SSH port, sets up dual-host mirror remotes (GitHub + Gitea) so one push writes both, treats repos as private-by-default (failing clearly on auth), and clones non-destructively into a non-empty directory.
---

<what-to-do>

Resolve and clone a repository even when the ask is terse (e.g. "clone into ."). Never guess silently — infer with the rules below, state the resolved target, then act. Prefer non-destructive operations. Stop and report clearly on any auth failure rather than falling back or inventing credentials.

## 1. Resolve the host

- If the user says **"github only"** → use GitHub, do NOT probe apoena.dev.
- If the user says **"apoena.dev only"** / **"git.apoena.dev only"** → use Gitea at `git.apoena.dev`, do NOT probe GitHub.
- If a full URL is given, use it verbatim (skip host/owner inference).
- If neither a scope nor a URL is given, ask which host (short numbered choice), or infer from context (a `git.apoena.dev` project → Gitea; a GitHub issue/PR context → GitHub).

## 2. Resolve owner + repo

Default owner **per host** (only when the user gives a bare repo name or nothing):

- **GitHub** → owner `jcalixte`
- **git.apoena.dev (Gitea)** → owner `julien`

The repo *name* is rarely inferable — do not carry a name from one host's context into another (a name seen in a GitHub issue file is a GitHub name, not an apoena.dev slug). If the name is unknown, ask for `owner/repo` or the full URL.

## 3. Build the URL

- **GitHub HTTPS:** `https://github.com/<owner>/<repo>`
- **GitHub SSH:** `git@github.com:<owner>/<repo>.git`
- **git.apoena.dev (Gitea) SSH:** `ssh://git@git.apoena.dev:22222/<owner>/<repo>.git`
  - ⚠️ Port is **22222** and the `ssh://` scheme is REQUIRED. The scp-style `git@git.apoena.dev:owner/repo.git` silently hits port 22 (a different SSH service) and fails with `Permission denied (publickey)` even when the key is valid.
  - Local key `~/.ssh/id_ed25519` (no passphrase) is authorized on Gitea over port 22222.
- **git.apoena.dev HTTPS:** `https://git.apoena.dev/<owner>/<repo>` (private → needs token; prefer SSH).

## 4. Clone into the target directory

- **Empty dir:** `git clone <url> <dir>` normally.
- **Non-empty dir (has a `.git` already, e.g. a Jean project seeded with `.gitkeep`):** default to the **non-destructive** path — do NOT wipe:
  1. `git remote add origin <url>` (or `git remote set-url origin <url>` if it exists)
  2. `GIT_SSH_COMMAND="ssh -o StrictHostKeyChecking=accept-new -o BatchMode=yes" git fetch origin --verbose`
  3. `git reset --hard origin/<default-branch>` (usually `main`) to bring the working tree to the remote content
  4. `git branch --set-upstream-to=origin/<default-branch> <branch>`
  - Only wipe-and-clean-clone if the user explicitly asks.

## 5. Dual-host mirror remotes (GitHub + Gitea)

Some repos live on **both** GitHub and `git.apoena.dev` (Gitea mirror). Do NOT set up a single `origin` with a fetch URL on one host and a push URL on the other — that split silently breaks `git push`:

- `git push` uses `remote.origin.pushurl` only; `git fetch` uses `remote.origin.url` only.
- If fetch→Gitea and push→GitHub, `git push` writes GitHub while `git status` reports ahead/behind vs Gitea. A commit looks "unpushed" forever, and `git push` says `Everything up-to-date` because its real target (GitHub) already has it. The Gitea mirror silently never receives the commit.

**Correct setup — one `origin`, push writes BOTH hosts:**

```
git remote set-url origin ssh://git@git.apoena.dev:22222/<owner>/<repo>.git
git remote set-url --add --push origin ssh://git@git.apoena.dev:22222/<owner>/<repo>.git
git remote set-url --add --push origin https://github.com/<gh-owner>/<repo>
```

- First line: fetch URL (pick the primary host — Gitea here).
- The first `--add --push` re-declares the fetch host as a push target (adding any push URL clears the implicit default, so the primary must be listed explicitly).
- Second `--add --push` adds the mirror. After this, one `git push` updates both; `git remote -v` shows one fetch + two push lines.

**To repair an already-split remote** (fetch and push on different hosts): run the three commands above to reset it. Then `git push` once to sync whichever mirror lagged.

Only wire dual push when the user wants both hosts kept in sync; a single-host repo needs none of this.

## 6. Auth: private by default, fail clearly

- Assume the repo is **private**. Attempt the fetch; if auth fails, **STOP and report the exact error** — never fall back to another method or fabricate credentials on your own.
- Distinguish the failure clearly:
  - `Not found` (Gitea, unauthenticated) → wrong path OR private (Gitea hides existence). Re-check owner/repo.
  - `could not read Username` → private, needs auth.
  - `Permission denied (publickey)` on apoena.dev → almost always the **wrong SSH port** (used 22 instead of 22222); fix the URL first before assuming the key is unregistered.
  - `Cannot find repository: X` after successful SSH auth → auth is fine, repo path is wrong.
- When credentials are genuinely needed, offer: SSH (preferred, no secret in transcript) / HTTPS token / `credential.helper store`. Warn that pasting a token lands it in the transcript.

## 7. Verify

Run `git status` (clean, tracking origin), `git remote -v` (correct URL — and for a mirror, one fetch + two push lines), and list top-level contents. Report the HEAD commit and what kind of project it is.

Keep bash commands simple (avoid chained `&&`/`;` with `echo "$?"` that trip permission prompts). Prefer `GIT_TERMINAL_PROMPT=0` / `BatchMode=yes` so a missing credential fails fast instead of hanging on a prompt.

</what-to-do>
