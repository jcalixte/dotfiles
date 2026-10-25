---
name: apoena-android-app
description: Use when the user wants to create a new native Android App for their personal Store (the F-Droid repo read by Neo Store), or to make an existing Android repo Store-ready — scaffolds Kotlin + Jetpack Compose with `applicationId dev.apoena.<name>`, generates a launcher icon, derives `versionCode` from the `vX.Y.Z` tag, signs with the shared App key from Gitea user-level secrets, adds the Gitea Actions release workflow (signed APK → Gitea release → Coolify Store rebuild), creates the public Gitea repo, and registers the App in the Store's `apps.yaml`.
---

<what-to-do>

Bootstrap one **App** for the **Store**. The rules come from the Store's design docs (`~/projects/store/CONTEXT.md` and `docs/adr/`); read them if the user questions a rule. Ask the inputs one at a time, showing the default.

## Rules every App follows

- Native Android, Kotlin + Jetpack Compose. No PWA, no cross-platform wrapper.
- `applicationId` = `namespace` = `dev.apoena.<name>`, where `<name>` is the app name with dashes removed (`my-app` → `dev.apoena.myapp`). It never changes after the first Release — Android treats a new ID as a new app.
- A **Release** is a git tag `vX.Y.Z`. CI passes `-PreleaseVersion=X.Y.Z`; Gradle sets `versionName = "X.Y.Z"` and `versionCode = X*10000 + Y*100 + Z`. Y and Z stay below 100. Never set `versionCode` by hand.
- Every App is signed with the **one shared App key** (never a per-App key, never committed). Local builds stay unsigned.
- The Gitea repo is **public**. Security is the App key signature, not secrecy.
- The release workflow publishes the signed APK as a Gitea release asset, then asks Coolify to rebuild the Store. The App never writes to the Store repo.

## Step 1 — Inputs

1. **App name** (kebab-case). Repo name, folder name, Gradle `rootProject.name`.
2. **App label** — the name under the icon on the phone. Default: app name in Title Case.
3. **applicationId** — default `dev.apoena.<name without dashes>`. For an existing App that already shipped a Release, keep its current ID.
4. **Project dir** — default `~/projects/<app-name>`. If the dir already holds an Android project, this is an **adopt** run: skip Step 3 and apply Step 4 to the existing files.
5. **License** — an SPDX short identifier, e.g. `GPL-3.0-only`, `AGPL-3.0-only`, `MIT`. Without one the Store lists the App as license `Unknown`.
6. **Description** — a few lines on what the App does, shown on the App's page in the Client. Basic HTML, no Markdown, 4000 characters at most.

## Step 2 — One-time setup (per user, not per App)

Check these once; skip the step when they exist. Variables can be listed: `curl -fsS -H "Authorization: token $TEA_TOKEN" https://git.apoena.dev/api/v1/user/actions/variables`. **Secrets cannot be listed by the API** — ask the user whether they exist (UI: https://git.apoena.dev/user/settings/actions/secrets).

| Name | Kind | Value |
|---|---|---|
| `APP_KEYSTORE_BASE64` | secret | `base64 -w0 app-key.jks` |
| `APP_KEYSTORE_PASSWORD` | secret | keystore password |
| `APP_KEY_ALIAS` | secret | key alias (e.g. `app`) |
| `APP_KEY_PASSWORD` | secret | key password (PKCS12: same as keystore password) |
| `STORE_DEPLOY_TOKEN` | secret | Coolify API token with the **`deploy` permission only** |
| `STORE_COOLIFY_UUID` | variable | UUID of the Store's Coolify application — set: `urzae6uwh0lzk352gqvuug6n` |

**Creating the App key** — only if it does not exist anywhere yet. Creating a second one silently would split the Apps across two keys.

```bash
keytool -genkeypair -keystore app-key.jks -storetype PKCS12 -alias app \
  -keyalg RSA -keysize 4096 -validity 36500 -dname "CN=Julien Calixte, O=apoena"
```

Then STOP and have the user store `app-key.jks` and its password in their password manager. **A lost App key means no App can ever be updated again** (uninstall, data lost). Do not continue to the first Release until the user confirms the backup.

Upload secrets with `curl -fsS -X PUT -H "Authorization: token $TEA_TOKEN" -H "Content-Type: application/json" -d '{"data":"<value>"}' https://git.apoena.dev/api/v1/user/actions/secrets/<NAME>`, and the variable with `POST .../user/actions/variables/STORE_COOLIFY_UUID` and `{"value":"<uuid>"}`. Delete the local `app-key.jks` only after the user confirms the backup. Never echo secret values into the conversation.

**`STORE_DEPLOY_TOKEN`** cannot be made by API: the user creates it in Coolify (https://platform.apoena.dev → Keys & Tokens → API tokens) with only the `deploy` permission, then it is uploaded like the other secrets. Without it the release still publishes, but the last step (Store rebuild) fails with HTTP 401.

## Step 3 — Scaffold (new App only)

Copy the templates from this skill's `templates/` and replace `{{APP_NAME}}`, `{{APP_LABEL}}`, `{{APP_ID}}`, `{{GRADLE_VERSION}}`:

| Template | Destination |
|---|---|
| `settings.gradle.kts` | `settings.gradle.kts` |
| `build.gradle.kts` | `build.gradle.kts` |
| `gradle.properties` | `gradle.properties` |
| `libs.versions.toml` | `gradle/libs.versions.toml` |
| `gradle-wrapper.properties` | `gradle/wrapper/gradle-wrapper.properties` |
| `app.build.gradle.kts` | `app/build.gradle.kts` |
| `AndroidManifest.xml` | `app/src/main/AndroidManifest.xml` |
| `strings.xml` | `app/src/main/res/values/strings.xml` |
| `MainActivity.kt` | `app/src/main/java/<applicationId as path>/MainActivity.kt` |
| `gitignore` | `.gitignore` |
| `release.yml` | `.gitea/workflows/release.yml` |

**Launcher icon** — generate it, never hand-write it:

```bash
python3 ~/.claude/skills/apoena-android-app/scripts/make-icon.py \
  --id dev.apoena.<name> --res app/src/main/res
```

It writes `mipmap-<density>/ic_launcher.png` at all five densities: a grid mark on a solid
colour, both derived from the applicationId, so each App looks different and white on the
colour clears WCAG AA. `templates/AndroidManifest.xml` already points `android:icon` at it.
Plain PNGs on purpose — fdroidserver cannot rasterise an adaptive XML icon, so an adaptive
icon would leave the App with no icon in the Repo index. When the App gets real artwork,
replace these files and keep the format.

**Versions.** The templates pin the versions that were last verified to build. Before scaffolding, check for newer stable AGP / Gradle / Kotlin / Compose BOM (see [Versions](#versions)); bump only if the new set builds.

**Gradle wrapper** — no local Gradle needed. Download the three wrapper files from the Gradle tag and verify the jar checksum:

```bash
V=9.8.2
B=https://raw.githubusercontent.com/gradle/gradle/v$V
curl -fsSL -o gradlew $B/gradlew && chmod +x gradlew
curl -fsSL -o gradlew.bat $B/gradlew.bat
curl -fsSL -o gradle/wrapper/gradle-wrapper.jar $B/gradle/wrapper/gradle-wrapper.jar
echo "$(curl -fsSL https://services.gradle.org/distributions/gradle-$V-wrapper.jar.sha256)  gradle/wrapper/gradle-wrapper.jar" | sha256sum -c
```

## Step 4 — Adopt (existing App only)

Bring the existing files in line with the rules, keeping the App's own code and dependencies:

- `app/build.gradle.kts`: replace the hard-coded `versionCode`/`versionName` with the `releaseVersion` block, and add the `signingConfigs` block and `signingConfig` line, both exactly as in `templates/app.build.gradle.kts`.
- Add `.gitea/workflows/release.yml` from the template. If one already exists, replace it with the template: older copies trigger the Store with `force=false`, which serves a stale Repo.
- Add `*.jks` and `*.keystore` to `.gitignore`.
- If the project is still on AGP 8, leave it there unless the user asks to upgrade — the release rules work on AGP 8 too. On AGP 8, keep the `kotlin-android` plugin; on AGP 9 it must be removed (built-in Kotlin).

## Step 5 — Verify locally

A local build needs a JDK and the Android SDK. If they are missing, say so and rely on the first CI run instead.

```bash
./gradlew assembleDebug                                    # unsigned dev build, versionName 0.0.0-dev
./gradlew assembleRelease -PreleaseVersion=1.4.2           # versionCode must come out as 10402
aapt2 dump badging app/build/outputs/apk/release/*.apk | head -1
```

## Step 6 — Gitea repo

New App: run the **apoena-gitea-repo** skill (public repo, SSH remote on port 22222, first push). Adopt run: commit and push to the existing remote.

## Step 7 — Register in the Store

Run `git -C ~/projects/store pull --rebase` first (other sessions push there too). Add the App to `~/projects/store/apps.yaml`, commit `feat(apps): add <app-name>`, and push. The push redeploys the Store; an App with no Release yet is listed in `apps.yaml` but not shown.

```yaml
apps:
  - id: dev.apoena.<name>
    repo: julien/<app-name>
    license: <SPDX id>
    description: |
      <what the App does, basic HTML>
```

`license` and `description` feed the Repo index. The App's summary is not here: it follows
the Gitea repo description, so change it on the repo.

## Step 8 — First Release

Only after Step 2 is complete and the App key backup is confirmed:

```bash
git tag v0.1.0 && git push origin v0.1.0
```

Watch the run at `https://git.apoena.dev/julien/<app-name>/actions`, then confirm the release has the asset `dev.apoena.<name>-v0.1.0.apk`. After the Store rebuild finishes (a few minutes), confirm the App is in the Repo:

```bash
curl -fsS https://store.apoena.dev/fdroid/repo/index-v2.json | jq '.packages | keys'
```

Neo Store shows the App after its next repo sync (pull to refresh). If the Store rebuild step failed, the release is still fine: fix the token and re-run only that job, or trigger `POST /api/v1/deploy?uuid=$STORE_COOLIFY_UUID&force=true`.

</what-to-do>

<supporting-info>

## Versions

Last verified to build (2026-10-24): AGP 9.4.0, Gradle 9.8.2, Kotlin 2.4.21, Compose BOM 2026.09.00, compileSdk/targetSdk 37, JDK 17+ (CI uses 21).

- AGP 9 has built-in Kotlin: do **not** apply `org.jetbrains.kotlin.android`, and `kotlinOptions` is gone. The Compose compiler plugin `org.jetbrains.kotlin.plugin.compose` is still required and must equal the Kotlin version — hence the `buildscript` classpath in the root `build.gradle.kts`, which lifts AGP's bundled Kotlin to the catalog's.
- Release notes: https://developer.android.com/build/releases/gradle-plugin, https://developer.android.com/build/migrate-to-built-in-kotlin

## Release workflow

- Runs on `git.apoena.dev`'s act_runner (`ubuntu-latest` = `docker.gitea.com/runner-images:ubuntu-latest`: Node, no Java), hence `setup-java` + `setup-android`. AGP downloads missing platforms and build-tools itself once licenses are accepted.
- The job token creates the release because of `permissions: contents: write` (Gitea 1.26 supports `permissions:`; a user or admin "restricted" default would otherwise make releases read-only).
- Gitea sets `GITHUB_REF_NAME`, `GITHUB_SERVER_URL`, `GITHUB_REPOSITORY`; it does **not** set `GITEA_REF_NAME` (use `gitea.ref_name` in expressions).
- Coolify `/api/v1/deploy` is **POST** only since v4.5 (`GET` returns 405). It uses `force=true` (rebuild without Docker cache): a new Release changes nothing in the Store's build inputs, so a cached build would serve the old Repo.
- `STORE_DEPLOY_TOKEN` must be a `deploy`-scoped Coolify token: it sits in every App's CI, so a `write`/`root` token there would expose the whole Coolify instance.

## App metadata in the Repo

`~/projects/store/fdroid/build-repo.py` writes one `metadata/<id>.yml` per App for
`fdroid update`: `Summary` from the Gitea repo description, `License` and `Description`
from `apps.yaml`. Field names are CamelCase and `License` takes an SPDX short identifier —
see the [Build Metadata Reference](https://f-droid.org/en/docs/Build_Metadata_Reference/).
The build prints a warning for each missing field instead of failing.

## Why these rules

The Store design is recorded in `~/projects/store`: ADR 0001 (F-Droid repo + Neo Store), ADR 0002 (one App key), ADR 0003 (the Store pulls Releases from Gitea releases). The Store is live at https://store.apoena.dev; its README explains how to add it to Neo Store.

</supporting-info>
