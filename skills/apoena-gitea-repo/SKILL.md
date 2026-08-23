---
name: apoena-gitea-repo
description: Use when a local project needs a Gitea repo (public by default) on git.apoena.dev and a first push — creates it with `tea`, wires the SSH remote on port 22222, and commits. Covers the `--owner`/`--login` traps and the stale-token error that make `tea repos create` fail, that push-to-create is disabled server-side, and why deployed repos must stay public. Called by apoena-new, or on its own for an existing directory.
---

<what-to-do>

## Inputs

- **App name** (kebab-case) — the repo name.
- **Project dir** — must already contain the code to push.
- **Description** — defaults to `<app-name>.apoena.dev`.
- **Visibility** — defaults to **public**. See [Visibility](#visibility) before choosing private.

## Prerequisite — the tea login

`tea --version` must work and `tea login list` must contain an entry for `git.apoena.dev`. If not:
`brew install tea` then `tea login add --name apoena --url https://git.apoena.dev --token <PAT>` (PAT from `https://git.apoena.dev/user/settings/applications`).

> **The Gitea login may be named anything** (not necessarily `apoena`) and need not be tea's default. Identify it by URL in `tea login list`; capture its **NAME** for `--login` below, and confirm the SSH host/port is `git.apoena.dev:22222`. Do not assume the login name is `apoena`.

> **`tea login list` showing an entry does not mean the token can create repos.** The PAT behind it may be read-only. There is no cheap non-destructive way to check the scope, so treat `tea repos create` itself as the test and read [Failure modes](#failure-modes) before interpreting its error.

> **Do not conclude tea is unconfigured from a missing `~/.config/tea/config.yml`.** On macOS the config lives under `~/Library/Application Support/tea/`. `tea login list` is the check; the file path is not.

## Create + push

```bash
git init -b main
git add -A
git status --short    # sanity-check node_modules/dist are NOT staged before committing
git commit -m "chore: initial scaffold"
tea repos create --login <login-name> --name <app-name> --description "<app-name>.apoena.dev" --init=false
# private instead: add --private (see Visibility)
git remote add origin ssh://git@git.apoena.dev:22222/julien/<app-name>.git
git push -u origin main
```

**Do not pass `--owner julien` to `tea repos create`** — `--owner` is for *organizations*, and passing a user account fails with `Error: GetOrgByName`. Omitting `--owner` creates the repo under the authenticated user. Pass `--login <login-name>` (the NAME from the prerequisite check) since the git.apoena.dev login may not be tea's default.

**Do not add `Co-authored-by` to the commit** (per `~/CLAUDE.md`).

## Visibility

`tea repos create --private` works, given a token that is allowed to create repos at all.

**Default to public, and keep it public whenever the app will be deployed.** `apoena-coolify-deploy` clones over HTTPS with no credentials and no deploy key, so a private repo fails at the git-clone step of the first deploy. Private is only safe for a repo that stays off Coolify.

When called from **apoena-new**, the answer is always public — that chain ends in a Coolify deploy. Standalone, ask if it is not obvious.

## Failure modes

`tea repos create` fails in three distinguishable ways. Match the message before reacting.

**`Error: this endpoint is not available for public-only tokens`**
The PAT tea is using cannot create repositories. Nothing you pass on the command line fixes it.

Read this one carefully: "public-only" describes the *token*, not the repo's visibility. It is **not** telling you the repo must be public — the call fails identically with and without `--private`. Do not respond by dropping `--private`, and do not ask the user to choose a visibility; the question is moot until the token is fixed.

**Try this first — it is cheap and needs nothing from the browser:**

```bash
tea login delete <login-name>
tea login add --name <login-name> --url https://git.apoena.dev --token $TEA_TOKEN
```

tea's stored login drifts from `$TEA_TOKEN`. The config can hold an old, weaker token while the env var has a good one, and nothing surfaces the difference — `tea login list` shows a healthy-looking row either way, with the same NAME, URL and USER.

**Delete before adding.** Whether `tea login add` overwrites an existing `--name` in place is untested; the one time this was fixed, the entry was deleted first. Do not skip the delete on the assumption that add replaces it.

**Only if that fails**, the token itself is wrong. Gitea's token form has a **"Public only" checkbox separate from the scope checkboxes**; while it is ticked Gitea rejects `POST /user/repos` outright, and granting `write:repository` changes nothing. Ask the user for a new PAT from `https://git.apoena.dev/user/settings/applications` with **"Public only" unchecked** and `write:repository` granted, then re-run the command above.

You cannot tell these two apart yourself — inspecting the stored credential is blocked by the sandbox. Run the re-add, then say which cause it pointed to.

**`Error: GetOrgByName`**
You passed `--owner julien`. `--owner` is for *organizations*. Omit it — the repo is created under the authenticated user.

**The repo already exists**
Ask the user whether to push to the existing one or pick a new name.

### Push-to-create is not a fallback

`ENABLE_PUSH_CREATE_USER` is off on this Gitea, so pushing to a URL for a repo that does not exist fails with `Push to create is not enabled for users.` The repo must exist before `git push`. If repo creation is blocked on token scope, the only route is the user creating it in the web UI (`https://git.apoena.dev/repo/create?name=<app-name>`, no README or .gitignore) and you pushing into it after.

## Hand back

Report the visibility you created it with, and both URLs:

- Browse / clone (HTTPS, what Coolify uses): `https://git.apoena.dev/julien/<app-name>` — sanity-check with `git ls-remote https://git.apoena.dev/julien/<app-name>.git refs/heads/main`.
- Push remote (SSH): `ssh://git@git.apoena.dev:22222/julien/<app-name>.git`.

</what-to-do>

<supporting-info>

The Gitea PAT is also available as the env var **`$TEA_TOKEN`**, exported from `~/.dotfiles/zsh/private.zsh` — that's what downstream webhook creation uses. Do NOT parse the tea config file or search the filesystem for a token; the sandbox blocks credential hunting and the env var is authoritative.

</supporting-info>
