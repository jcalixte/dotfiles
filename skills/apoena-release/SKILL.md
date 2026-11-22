---
name: apoena-release
description: Use when the user wants to release, ship, deploy or tag a new version of one of their Android Store Apps (a repo with `.gitea/workflows/release.yml` triggered on `v*` tags). Commits and pushes pending work, picks the next semver version from the conventional commits since the last tag, tags and pushes it, watches the Gitea Actions run, checks the signed APK landed on the Gitea release, confirms the workflow pinned the version in the Store's `apps.yaml` and the Store (store.apoena.dev) lists it (pinning by hand, retrying or unblocking the Store rebuild on Coolify), then deletes the App's Gitea releases older than the last five and checks the server disk usage.
---

<what-to-do>

Ship one **Release** of a Store App. A Release is an annotated git tag `vX.Y.Z` pushed to git.apoena.dev; the repo's release workflow builds the signed APK, attaches it to a Gitea release, then pins that version in the Store's `apps.yaml` as `store-bot`; that commit fires the Store's push webhook (a cached build, ~40 s). The Store lists only the pinned Release of each App, and old Gitea releases are deleted (the server disk is small). Report each check's outcome as you go; never claim a step passed without seeing it.

`$TEA_TOKEN` and `$COOLIFY_API_TOKEN` come from `~/.dotfiles/zsh/private.zsh`. If one is missing, tell the user to `source` it; don't hunt for tokens on disk.

## Step 1 — Commit and push pending work

If `git status --porcelain` lists changes or `git fetch -q && git status -sb` shows `main` ahead of origin, commit them as conventional microcommits and push. Use the `gcp` skill if it is in the skill list; else commit by hand (one commit per change, docs apart, no `Co-Authored-By` trailer). Those commit messages feed the version bump in Step 3, so they matter. Skip this step when the tree is clean and `main` is pushed.

## Step 2 — Preconditions

Stop and tell the user if any fails:

- `.gitea/workflows/release.yml` exists and triggers on `tags: ["v*"]`.
- Its last step runs `pin-release.mjs` (`grep -q pin-release.mjs .gitea/workflows/release.yml`). An older workflow calls Coolify with `force=true` and a Coolify token that is gone: replace that step with the one in `apoena-android-app/templates/release.yml` (App ID in place of `{{APP_ID}}`), commit `ci(release): pin the Release in the Store's apps.yaml` and push before you tag.
- On `main`, working tree clean, and `main` is pushed (`git fetch -q && git status -sb` shows no ahead/behind). If `main` is behind origin, stop: don't pull or rebase on the user's behalf.
- There are commits since the last tag (`git describe --tags --abbrev=0`). Nothing new → nothing to release.
- Unit tests pass: `flutter test` when `pubspec.yaml` exists (a Flutter App), else `./gradlew -q :app:testDebugUnitTest`.

## Step 3 — Pick the version (semver)

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

Bump from the highest tag, not from `git describe`: another session can push a tag at any time, so always fetch tags first. The same rule applies below 1.0 (a `feat` on `v0.1.4` gives `v0.2.0`). If the user named a version, use theirs. Minor and patch must stay below 100, because `versionCode = X*10000 + Y*100 + Z`. Show the commit list and the chosen version in one line, then proceed.

## Step 4 — Tag and push

```bash
git tag -a "vX.Y.Z" -m "vX.Y.Z"
git push origin "vX.Y.Z"
```

Never move, delete or re-push an existing tag: a published version is final. To fix a bad release, ship the next patch.

## Step 5 — Watch the release workflow

Owner/repo comes from `git remote get-url origin` (`ssh://git.apoena.dev:22222/<owner>/<repo>.git`). Call the Gitea API with `curl` and `$TEA_TOKEN` (the installed `tea` has no `api` subcommand). A build takes about **10 minutes** (Flutter install, tests, signed APK).

**Never block on it.** A foreground Bash loop of several minutes gets cut off when the session ends, and its outcome is lost. Instead:

1. Find the run ID once, right after the tag push. The newest push run is the tag's (`head_branch` is null in this Gitea, so don't filter on it); check that its `created_at` is after the push:

   ```bash
   G=https://git.apoena.dev/api/v1; H="Authorization: token $TEA_TOKEN"
   curl -fsS -H "$H" "$G/repos/$OWNER/$REPO/actions/runs?limit=1" | jq -r '.workflow_runs[0] | "\(.id) \(.created_at) \(.status)"'
   ```

   If it prints an error or nothing, stop and fix the call.

2. Watch it with the **Monitor** tool (load it with ToolSearch `select:Monitor`), `timeout_ms` 1200000. The script prints only when the run ends, then exits:

   ```bash
   G=https://git.apoena.dev/api/v1; H="Authorization: token $TEA_TOKEN"; RUN=<id>
   while true; do
     R=$(curl -fsS -H "$H" "$G/repos/$OWNER/$REPO/actions/runs/$RUN" || echo '{}')
     S=$(jq -r '.status // "curl-error"' <<<"$R")
     if [ "$S" = completed ]; then
       echo "run $(jq -r .conclusion <<<"$R")"
       curl -fsS -H "$H" "$G/repos/$OWNER/$REPO/actions/runs/$RUN/jobs" \
         | jq -r '.jobs[].steps[] | select(.conclusion != "success" and .conclusion != "skipped") | "step \(.name): \(.conclusion)"'
       exit 0
     fi
     sleep 30
   done
   ```

   Keep working (or end the turn) while it runs; the notification brings you back. If the Monitor expires, re-arm it once; a run past 25 minutes is stuck: link the run and stop.

Use `actions/runs/<id>` (`status` + `conclusion`) and `actions/runs/<id>/jobs` (one line per step). Don't use `actions/tasks`: its `status` lags and says `running` after the run has ended.

`success` → go on. `failure` → name the failed step (from the jobs call), link `https://git.apoena.dev/$OWNER/$REPO/actions/runs/<id>` and stop. The usual causes are a compile error or a missing App key secret. Only exception: when the one failed step is "Pin the Release in the Store", the release itself is fine: confirm the APK below, then pin by hand in Step 6. Don't re-run the job: `POST /releases` on an existing tag returns 409. A 401 there means `STORE_GITEA_TOKEN` is missing or revoked (see `apoena-android-app` to make a new one).

Then confirm the APK is attached:

```bash
curl -fsS -H "$H" "$G/repos/$OWNER/$REPO/releases/tags/vX.Y.Z" | jq -r '.html_url, .assets[].name'
```

The APK lands before the last step ("Pin the Release in the Store"), so an attached APK alone doesn't mean the run is done.

## Step 6 — Confirm the Store lists it

The app ID is `applicationId` in `app/build.gradle.kts` (`android/app/build.gradle.kts` in a Flutter App). The workflow's last step commits `version: vX.Y.Z` to the Store's `apps.yaml`; the Store rebuild takes about 40 s after the run ends.

```bash
curl -fsS https://store.apoena.dev/fdroid/repo/index-v2.json \
  | jq -c --arg id "$APP_ID" '.packages[$id].versions | to_entries | map(.value.manifest.versionName)'
```

Done when it prints `["X.Y.Z"]`: the Store build keeps only the pinned APK of each App, so the old version goes away.

If the new version isn't there, first check the pin: `curl -fsS https://git.apoena.dev/julien/store/raw/branch/main/apps.yaml | grep -A3 "id: $APP_ID"`. No `version: vX.Y.Z` there means the pin step did not write it: read its log. If it says the App is pinned higher, the Store is right as it is. Otherwise add the line by hand in `~/projects/store` (`git pull --rebase` first), commit `chore(apps): pin $APP_ID vX.Y.Z` and push. With the pin in place, find the Store's latest Coolify deployment (Store app UUID `urzae6uwh0lzk352gqvuug6n`):

```bash
API=https://platform.apoena.dev/api/v1; AUTH="Authorization: Bearer $COOLIFY_API_TOKEN"
curl -fsS -H "$AUTH" "$API/deployments/applications/urzae6uwh0lzk352gqvuug6n?take=2" | jq -c '.deployments[] | {deployment_uuid, status, created_at}'
```

- `queued` behind an older `in_progress` deployment: Coolify runs one deployment at a time. If the older one's last log line is `Gracefully shutting down build container` and it has not moved for 10 minutes, it is stuck (its new container is already live). Cancel it with `curl -fsS -X POST -H "$AUTH" "$API/deployments/<old uuid>/cancel"`; yours then starts.

- `in_progress` / `queued`: watch it with a Monitor, the same way as Step 5 (`timeout_ms` 900000). The script polls `$API/deployments/$D` every 30 s, and on `finished` prints the index versions and exits; on `failed`/`cancelled*` prints the status plus `.logs | fromjson | .[] | select(.hidden|not) | .output | tail -15` and exits.
- `failed` on a transient Coolify error (e.g. `container name ... is already in use`): trigger one rebuild with `curl -fsS -X POST -H "$AUTH" "$API/deploy?uuid=urzae6uwh0lzk352gqvuug6n&force=false"` (no image exists for a failed commit, so Coolify builds it, with cache), watch the new deployment the same way, then re-check the index. A rebuild only regenerates the Repo from `apps.yaml`, so it is safe to repeat.
- Fails for any other reason, or fails again: show the log lines and stop. The Gitea release is still fine. Skip Step 7: the older releases stay until the Store lists the new one.

## Step 7 — Keep the last five releases, check the disk

Only after the Store index lists the new version.

1. Keep this App's five newest releases that have an APK (the new tag is one of them) and delete the others. A release with no APK (a failed run) goes too. Keep every git tag: `DELETE /releases/{id}` removes the release and its APK, not the tag.

   ```bash
   curl -fsS -H "$H" "$G/repos/$OWNER/$REPO/releases?limit=50" \
     | jq -r '(map(select(any(.assets[]; .name | endswith(".apk")))) | sort_by(.created_at) | reverse | .[:5] | map(.id)) as $keep
         | .[] | select(.id as $i | $keep | index($i) | not) | "\(.id) \(.tag_name)"'
   # for each id: curl -fsS -X DELETE -H "$H" "$G/repos/$OWNER/$REPO/releases/<id>"   (204 = deleted)
   ```

   Then list the releases again: at most five remain, each with its APK, and `vX.Y.Z` is the newest.

2. Check the server disk (read-only). Don't run a cleanup here: Coolify runs a forced Docker cleanup every night at midnight, a Store image holds one APK per App, and a cleanup removes unused images of every app on the server. The last cleanup run on the server (UUID `adnwww057yrh5a1b1nfo5o26`) gives the disk usage; the API returns a bare array:

   ```bash
   curl -fsS -H "$AUTH" "$API/servers/adnwww057yrh5a1b1nfo5o26/docker-cleanup/executions" \
     | jq -r '.[0] | "\(.created_at) \(.message)"'
   ```

   The message reads `Disk usage before: N%, Disk usage after: M%`. If N or M is 90 or more, warn the user and give the time of that run. They decide whether to run a manual cleanup (`POST $API/servers/<uuid>/docker-cleanup/run`) or look on the server (`du`): about 83% of the disk is data that Docker cleanup cannot free.

## Step 8 — Report

One short summary: version and why (the bump rule that applied), release URL, APK name, whether the Store index lists it, how many old releases were deleted, and the disk usage from the last cleanup run (with a warning at 90% or more). Mention that Neo Store picks it up on its next repo sync (pull to refresh).

</what-to-do>
