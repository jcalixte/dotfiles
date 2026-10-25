---
name: apoena-release
description: Use when the user wants to release, ship, deploy or tag a new version of one of their Android Store Apps (a repo with `.gitea/workflows/release.yml` triggered on `v*` tags). Picks the next semver version from the conventional commits since the last tag, tags and pushes it, watches the Gitea Actions run, checks the signed APK landed on the Gitea release, and confirms the Store (store.apoena.dev) lists the new version, retrying the Store rebuild when Coolify fails on a transient error.
---

<what-to-do>

Ship one **Release** of a Store App. A Release is an annotated git tag `vX.Y.Z` pushed to git.apoena.dev; the repo's release workflow builds the signed APK, attaches it to a Gitea release, then asks Coolify to rebuild the Store. Report each check's outcome as you go; never claim a step passed without seeing it.

`$TEA_TOKEN` and `$COOLIFY_API_TOKEN` come from `~/.dotfiles/zsh/private.zsh`. If one is missing, tell the user to `source` it; don't hunt for tokens on disk.

## Step 1 — Preconditions

Stop and tell the user if any fails:

- `.gitea/workflows/release.yml` exists and triggers on `tags: ["v*"]`.
- On `main`, working tree clean, and `main` is pushed (`git fetch -q && git status -sb` shows no ahead/behind).
- There are commits since the last tag (`git describe --tags --abbrev=0`). Nothing new → nothing to release.
- Unit tests pass: `./gradlew -q :app:testDebugUnitTest`.

## Step 2 — Pick the version (semver)

```bash
git fetch --tags -q
LAST=$(git tag --sort=-v:refname | grep -E '^v[0-9]+\.[0-9]+\.[0-9]+$' | head -1)
git log --format='%s%n%b' "$LAST"..HEAD
```

Bump from the conventional commits since `$LAST`:

| Commits contain | Bump |
|---|---|
| `!` after the type (`feat!:`) or a `BREAKING CHANGE:` footer | major |
| any `feat` | minor (reset patch) |
| only `fix`, `perf`, `refactor`, `chore`, `docs`, … | patch |

The same rule applies below 1.0 (a `feat` on `v0.1.4` gives `v0.2.0`). If the user named a version, use theirs. Minor and patch must stay below 100, because `versionCode = X*10000 + Y*100 + Z`. Show the commit list and the chosen version in one line, then proceed.

## Step 3 — Tag and push

```bash
git tag -a "vX.Y.Z" -m "vX.Y.Z"
git push origin "vX.Y.Z"
```

Never move, delete or re-push an existing tag: a published version is final. To fix a bad release, ship the next patch.

## Step 4 — Watch the release workflow

Owner/repo comes from `git remote get-url origin` (`ssh://git.apoena.dev:22222/<owner>/<repo>.git`). Poll every 15 s until the run for the tag ends (a build takes about 2–3 minutes):

```bash
tea api "/repos/$OWNER/$REPO/actions/tasks?limit=5" \
  | jq -r --arg t "vX.Y.Z" '[.workflow_runs[] | select(.head_branch == $t)][0].status'
```

`success` → go on. `failure` → link `https://git.apoena.dev/$OWNER/$REPO/actions` and stop. The usual causes are a compile error or a missing App key secret.

Then confirm the APK is attached:

```bash
tea api "/repos/$OWNER/$REPO/releases/tags/vX.Y.Z" | jq -r '.html_url, .assets[].name'
```

## Step 5 — Confirm the Store lists it

The app ID is `applicationId` in `app/build.gradle.kts`.

```bash
curl -fsS https://store.apoena.dev/fdroid/repo/index-v2.json \
  | jq -c --arg id "$APP_ID" '.packages[$id].versions | to_entries | map(.value.manifest.versionName)'
```

If the new version isn't there, look at the Store's latest Coolify deployment (Store app UUID `urzae6uwh0lzk352gqvuug6n`):

```bash
API=https://platform.apoena.dev/api/v1; AUTH="Authorization: Bearer $COOLIFY_API_TOKEN"
D=$(curl -fsS -H "$AUTH" "$API/deployments/applications/urzae6uwh0lzk352gqvuug6n?take=1" | jq -r '.deployments[0].deployment_uuid')
curl -fsS -H "$AUTH" "$API/deployments/$D" | jq -r '.status, (.logs | fromjson | .[] | select(.hidden|not) | .output)' | tail -20
```

- `in_progress` / `queued`: wait for it.
- `failed` on a transient Coolify error (e.g. `container name ... is already in use`): trigger one rebuild with `curl -fsS -X POST -H "$AUTH" "$API/deploy?uuid=urzae6uwh0lzk352gqvuug6n&force=true"`, poll `$API/deployments/<uuid>` to `finished`, then re-check the index. A rebuild only regenerates the index from Gitea releases, so it is safe to repeat.
- Fails for any other reason, or fails again: show the log lines and stop. The Gitea release is still fine.

## Step 6 — Report

One short summary: version and why (the bump rule that applied), release URL, APK name, and whether the Store index lists it. Mention that Neo Store picks it up on its next repo sync (pull to refresh).

</what-to-do>
