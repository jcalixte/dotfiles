---
name: apoena-gitea-repo
description: Use when a local project needs a public Gitea repo on git.apoena.dev and a first push — creates it with `tea`, wires the SSH remote on port 22222, and commits. Covers the `--owner`/`--login` traps that make `tea repos create` fail. Called by apoena-new, or on its own for an existing directory.
---

<what-to-do>

## Inputs

- **App name** (kebab-case) — the repo name.
- **Project dir** — must already contain the code to push.
- **Description** — defaults to `<app-name>.apoena.dev`.

## Prerequisite — the tea login

`tea --version` must work and `tea login list` must contain an entry for `git.apoena.dev`. If not:
`brew install tea` then `tea login add --name apoena --url https://git.apoena.dev --token <PAT>` (PAT from `https://git.apoena.dev/user/settings/applications`).

> **The Gitea login may be named anything** (not necessarily `apoena`) and need not be tea's default. Identify it by URL in `tea login list`; capture its **NAME** for `--login` below, and confirm the SSH host/port is `git.apoena.dev:22222`. Do not assume the login name is `apoena`.

## Create + push

```bash
git init -b main
git add -A
git status --short    # sanity-check node_modules/dist are NOT staged before committing
git commit -m "chore: initial scaffold"
tea repos create --login <login-name> --name <app-name> --description "<app-name>.apoena.dev" --init=false
git remote add origin ssh://git@git.apoena.dev:22222/julien/<app-name>.git
git push -u origin main
```

**Do not pass `--owner julien` to `tea repos create`** — `--owner` is for *organizations*, and passing a user account fails with `Error: GetOrgByName`. Omitting `--owner` creates the repo under the authenticated user. Pass `--login <login-name>` (the NAME from the prerequisite check) since the git.apoena.dev login may not be tea's default.

**Do not add `Co-authored-by` to the commit** (per `~/CLAUDE.md`).

If `tea repos create` fails because the repo already exists, ask the user whether to push to the existing one or pick a new name.

## Hand back

The repo is public. Report both URLs to the caller:

- Browse / clone (HTTPS, what Coolify uses): `https://git.apoena.dev/julien/<app-name>` — sanity-check with `git ls-remote https://git.apoena.dev/julien/<app-name>.git refs/heads/main`.
- Push remote (SSH): `ssh://git@git.apoena.dev:22222/julien/<app-name>.git`.

</what-to-do>

<supporting-info>

The Gitea PAT is also available as the env var **`$TEA_TOKEN`**, exported from `~/.dotfiles/zsh/private.zsh` — that's what downstream webhook creation uses. Do NOT parse the tea config file or search the filesystem for a token; the sandbox blocks credential hunting and the env var is authoritative.

</supporting-info>
