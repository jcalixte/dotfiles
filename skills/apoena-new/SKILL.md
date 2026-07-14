---
name: apoena-new
description: Use when the user wants to bootstrap a new *.apoena.dev app (or an app on a custom marque domain) on Coolify — scaffolds a Vite + Vue + DaisyUI SPA (optionally with a Gleam backend and SQLite), creates a public Gitea repo on git.apoena.dev, provisions the Coolify app via API (falling back to a printable deploy checklist), builds a real first screen of the app the user asked for, and then hands off to the feature-build skills to flesh out the rest.
---

<what-to-do>

Walk the user through bootstrapping a new `*.apoena.dev` app end-to-end. Ask the inputs one at a time, waiting for the answer before moving on. Do not assume defaults silently — show the default in the question and let the user override.

Then scaffold the code, create the Gitea repo, push, and provision the Coolify app via its API (Step 8) when `$COOLIFY_API_TOKEN` is available — otherwise print the checklist (Step 9) for the user to paste into the UI. Calling the Coolify **API** is expected and fine; do NOT try to drive the Coolify **web UI** / a browser.

The scaffold is **not** a placeholder. Step 3 builds a real first screen of the app the user asked for, and once that's deployed, Step 11 designs the rest of the app with `/walk-with-me` and then hands off to the feature-build skills. Do not stop at the first screen and wait to be told to continue — proceed into Step 11.

## Step 1 — Gather inputs

**First, establish what the app is.** Before the infra questions below, make sure you understand the app's purpose and core features — from the user's request in this conversation and any design docs / spec already in the target directory (read them; don't re-ask what's already written down). If the concept is thin or missing, ask the user for a one-paragraph description before continuing. You use this in three places: to theme the scaffold, to build a real first screen (Step 3), and to drive the feature build (Step 11). Then gather the infra inputs.

Ask in this order:

1. **App name** (kebab-case, lowercase). Used for the local folder, the Gitea repo, and the subdomain prefix. Example: `qrcode`.
2. **Backend?** (default: no). If yes, the stack is Gleam (`wisp` + `mist`). Skill does not support other backends — if the user wants something else, stop and ask them to scaffold the backend manually.
3. **SQLite?** Default: yes if backend was chosen, no if SPA-only. (A SPA can still use SQLite via the backend; offering it for SPA-only means "set up the volume now even though there's nothing using it yet" — discourage that.)
4. **Local scaffold path.** Default: `$PWD/<app-name>`. **If the current directory is already named `<app-name>` (or already holds the project's design docs), scaffold into the current directory instead of a nested `<app-name>/<app-name>` — confirm this with the user.**
5. **Subdomain / domain.** Default: `<app-name>.apoena.dev`. Confirm. If the user gives a **custom apex bought via marque** (not under `apoena.dev`, e.g. `typoena.app`), flag it — Step 2b provisions its DNS in the PDS, and it must already be registered in marque.
6. **Primary color** (hex, e.g. `#570DF8`). Default: `#570DF8` (DaisyUI default). Used both as the Tailwind v4 `--color-primary` and as the favicon stroke color.
7. **Favicon icon name** from Tabler (`https://tabler.io/icons`). Default: `circle`. Use the exact slug shown on the Tabler page (e.g. `bolt`, `paw`, `qrcode`). Outline variant only. Pre-verify it resolves (HTTP 200) before scaffolding so you don't discover a 404 late.

## Step 2 — Verify prerequisites

Run these checks. If any fail, print the missing tool + remediation and STOP.

| Tool | Check | Remediation |
|---|---|---|
| `node` | `node --version` (≥ 20) | `brew install node` |
| `pnpm` | `pnpm --version` | `npm i -g pnpm` (or fall back to `npm` — note the choice and use it everywhere below) |
| `tea` | `tea --version` && `tea login list` contains `git.apoena.dev` | `brew install tea` then `tea login add --name apoena --url https://git.apoena.dev --token <PAT>` (PAT from `https://git.apoena.dev/user/settings/applications`) |
| `docker` (backend only) | `docker --version` | install OrbStack / Docker Desktop |
| `gleam` (backend only) | `gleam --version` (≥ 1.0) | `brew install gleam erlang rebar3` |

> **The Gitea login may be named anything** (not necessarily `apoena`) and need not be tea's default. Identify it by URL in `tea login list`; capture its **NAME** (for `--login` in Step 7) and confirm the SSH host/port is `git.apoena.dev:22222`. Do not assume the login name is `apoena` anywhere downstream.

## Step 2b — DNS for a custom domain (marque; skip for `*.apoena.dev`)

Run this **only** when the domain is not under `apoena.dev` (a separate apex bought via marque). `*.apoena.dev` is covered by a wildcard — skip. Do it here, not at deploy, so DNS propagates while you scaffold.

marque is atproto-native: a domain's DNS lives as an `at.marque.dns` record in the apoena PDS (`https://eurosky.social`, repo `did:plc:4m3kouplb7s7xozjd3whinvl` = `apoena.dev`), and marque's nameservers (`stratus`/`cirrus.ns.marque.network`) serve it directly — a `putRecord` **is** live DNS. `$MARQUE_APP_PASSWORD` is exported from `~/.dotfiles/zsh/private.zsh` (source it if not loaded; never prompt inline).

```bash
DID=did:plc:4m3kouplb7s7xozjd3whinvl; PDS=https://eurosky.social; DOMAIN=<domain>
# 1) Domain must already be registered in marque (paid flow — the skill can't buy it). Grab its cid for the subject link.
DOMAIN_CID=$(curl -fsSL "$PDS/xrpc/com.atproto.repo.getRecord?repo=$DID&collection=at.marque.domain&rkey=$DOMAIN" | jq -r '.cid // empty')
[ -z "$DOMAIN_CID" ] && { echo "STOP: $DOMAIN not registered in marque — ask the user to buy it first"; exit 1; }
# 2) Point @/* (A) and www (CNAME→apex) at the Coolify host. Derive the IP — never hardcode it.
IP=$(dig +short platform.apoena.dev | head -1)
JWT=$(curl -sS -X POST "$PDS/xrpc/com.atproto.server.createSession" -H "Content-Type: application/json" \
  -d "$(jq -n --arg id "$DID" --arg pw "$MARQUE_APP_PASSWORD" '{identifier:$id,password:$pw}')" | jq -r '.accessJwt // empty')
REC=$(jq -n --arg d "$DOMAIN" --arg cid "$DOMAIN_CID" --arg did "$DID" --arg ip "$IP" --arg now "$(date -u +%Y-%m-%dT%H:%M:%SZ)" '{
  "$type":"at.marque.dns", domain:$d,
  records:[{ttl:3600,name:"@",value:$ip,recordType:"A"},
           {ttl:3600,name:"*",value:$ip,recordType:"A"},
           {ttl:3600,name:"www",value:$d,recordType:"CNAME"}],
  subject:{uri:("at://"+$did+"/at.marque.domain/"+$d), cid:$cid}, createdAt:$now}')
curl -fsSL -X POST "$PDS/xrpc/com.atproto.repo.putRecord" -H "Authorization: Bearer $JWT" -H "Content-Type: application/json" \
  -d "$(jq -n --arg did "$DID" --arg d "$DOMAIN" --argjson rec "$REC" '{repo:$did,collection:"at.marque.dns",rkey:$d,record:$rec,validate:false}')" | jq '{uri,error}'
# 3) Verify it's live on marque's NS (both should return the IP):
dig +short @stratus.ns.marque.network "$DOMAIN"; dig +short @stratus.ns.marque.network "www.$DOMAIN"
```

**`www` CNAME must target the apex hostname, never an IP** (a CNAME→IP is malformed). `putRecord` replaces on re-run, so it's idempotent. Then continue — in Step 8 the Coolify domain is `https://<domain>` and Let's Encrypt issues once DNS resolves.

## Step 3 — Scaffold the frontend

```bash
cd <local-path-parent>
npm create vite@latest <app-name> -- --template vue-ts
cd <app-name>
pnpm install
pnpm add -D tailwindcss @tailwindcss/vite
pnpm add daisyui@latest
pnpm add -D oxlint oxfmt    # oxc linter + formatter (https://oxc.rs)
```

**If the target directory already exists and is non-empty** (e.g. it already holds design docs, or the chosen path equals the current folder), `npm create vite` becomes interactive and would clobber files. Instead scaffold into a scratch dir and copy in, preserving everything that already exists:

```bash
npm create vite@latest /tmp/<app-name>-scaffold -- --template vue-ts
rm -f /tmp/<app-name>-scaffold/README.md      # never clobber an existing README
cp -R /tmp/<app-name>-scaffold/. <project-dir>/   # trailing /. includes dotfiles; only README would collide
cd <project-dir> && pnpm install && pnpm add -D tailwindcss @tailwindcss/vite && pnpm add daisyui@latest && pnpm add -D oxlint oxfmt
```
Set `"name"` in `package.json` to `<app-name>` (the scaffold names it after the temp dir). If an informative `README.md` already exists, keep it and **skip Step 6**.

Then write/patch these files (templates in `templates/`):

- `vite.config.ts` — add `@tailwindcss/vite` plugin, and (if backend) the `/api` dev proxy to `http://localhost:8000`.
- `src/style.css` — copy `templates/tailwind-style.css` then substitute `{{PRIMARY_COLOR}}` with the user's hex. **Keep the font `@import url(...)` as the first line** (the template already orders it correctly — do not move it below `@import "tailwindcss"` or the font silently won't load in the build).
- `src/App.vue` + supporting files — build the **real first screen of the app** established in Step 1, not a generic landing card. This is the genuine entry point the user would land on, themed with DaisyUI: for a data-driven app that means the primary screen actually wired up (fetching and rendering real data), not a mockup. Keep it to that one screen — secondary screens and the full feature set come in Step 11 — but it must be recognizably *this* app. Add only the components / composables / types that this one screen needs. Delete `src/components/HelloWorld.vue` (and the now-empty `src/components/` if nothing replaces it).
- `src/assets/icons/` — create the folder and copy `templates/icons-readme.md` to `src/assets/icons/README.md`. This is the reusable in-app icon folder; the user drops Tabler SVGs here as needed.
- `public/favicon.svg` — fetch `https://raw.githubusercontent.com/tabler/tabler-icons/main/icons/outline/<favicon-icon>.svg`, then `sed` replace `currentColor` with the primary-color hex, and **overwrite** `public/favicon.svg` (the modern `vue-ts` template already ships one). If the curl 404s, ask the user for a different icon name and retry.
- **Remove the modern template's demo cruft** — recent `vue-ts` ships `src/assets/{vite.svg,vue.svg,hero.png}` and `public/icons.svg` (there is no longer a `public/vite.svg`). `rm -f` them since the new `App.vue` doesn't reference them.
- `index.html` — the modern template **already** has `<link rel="icon" type="image/svg+xml" href="/favicon.svg" />`, so usually only the `<title>` needs updating to the app name (fix the icon link only if it differs).
- `Dockerfile` — copy `templates/Dockerfile.spa`.
- `nginx.conf` — copy `templates/nginx.conf`.
- `.dockerignore` — at minimum `node_modules`, `dist`, `.git`.
- **oxc linter + formatter** ([oxc.rs](https://oxc.rs)) — run `pnpm exec oxlint --init` to generate `.oxlintrc.json` (a valid starter for the installed version; don't hand-write it). For oxfmt, write `.oxfmtrc.json` with `semi: false` (no trailing semicolons) and `singleQuote: false` (double quotes — also oxfmt's default, set explicitly):
  ```json
  {
    "$schema": "./node_modules/oxfmt/configuration_schema.json",
    "semi": false,
    "singleQuote": false
  }
  ```
  Add four scripts to `package.json`: `"lint": "oxlint"`, `"lint:fix": "oxlint --fix"`, `"fmt": "oxfmt"`, `"fmt:check": "oxfmt --check"`. **Coverage caveat:** oxlint lints the `<script>` blocks of `.vue` files but not `<template>`, and oxfmt's `.vue` support is partial — so the Vue markup layer isn't checked. oxfmt does **not** touch `src/style.css` (it formats JS/TS/Vue, not CSS), so the font `@import` ordering there is unaffected.
- **Zed format-on-save** — copy `templates/zed-settings.json` to `.zed/settings.json`. Without it, Zed formats `.ts`/`.vue` on save with its built-in (Prettier-style) formatter, which **adds semicolons** and fights the `semi: false` in `.oxfmtrc.json`. The config points Zed's on-save formatter at the project-local `./node_modules/.bin/oxfmt` (via `--stdin-filepath`, so it honours `.oxfmtrc.json`), for TypeScript/JavaScript/Vue only — CSS/JSON/Markdown keep Zed's defaults. Use the direct binary path, not `pnpm exec oxfmt`: both need cwd at the project root, but the wrapper adds ~300ms on every save. `.zed/` is committed (not git-ignored) so any Zed user on the repo gets consistent saves.

Verify it builds, lints, and is formatted: (1) `pnpm dev` boots — start it, curl `http://localhost:5173` (use `curl --retry … --retry-connrefused` instead of a foreground `sleep` to wait for boot), then kill it; (2) **`pnpm build` succeeds with no warnings** — this is exactly what Coolify runs (`vue-tsc -b && vite build`) and catches type errors the dev server won't. A `@import must precede all rules` warning means the font import in `src/style.css` is misordered; (3) run `pnpm fmt` to format the generated code, then `pnpm lint` — both should pass clean on a fresh scaffold (fix anything oxlint flags before committing); (4) since the scaffold is now a real screen, not a static card, sanity-check that it actually renders — load it in a browser (the **browser-testing-with-devtools** skill) and confirm the first screen shows real content, not an error or empty state.

## Step 4 — Scaffold the backend (if selected)

From the project root:

```bash
mkdir backend && cd backend
gleam new . --name <app_name_snake>
gleam add wisp mist gleam_erlang gleam_http
```

If SQLite was selected: `gleam add sqlight` and create `src/<app_name_snake>/db.gleam` opening `data/app.db`.

Replace `src/<app_name_snake>.gleam` with a minimal wisp app exposing `GET /api/health` returning `200 ok`. Bind `mist` to port `8000`.

Copy `templates/Dockerfile.gleam` to `backend/Dockerfile`.

## Step 5 — docker-compose (if backend)

Copy `templates/docker-compose.yml` to the project root. Substitute `<APP_NAME>`. If no SQLite, remove the `volumes:` block and the `data/` mount from `api`.

If no backend, do NOT create a `docker-compose.yml` — Coolify will use the Dockerfile build pack directly.

## Step 6 — README

Skip this step if an informative `README.md` already exists (see Step 3). Otherwise write a short `README.md`:

```markdown
# <app-name>

Deployed at https://<subdomain>

## Develop

\`\`\`bash
pnpm dev           # frontend on :5173
pnpm lint          # oxlint  (pnpm lint:fix to autofix)
pnpm fmt           # oxfmt   (pnpm fmt:check to verify only)
# (backend only) cd backend && gleam run    # api on :8000
# (compose) docker compose up
\`\`\`

## Deploy

Pushes to `main` are picked up by Coolify at https://platform.apoena.dev.
```

## Step 7 — Git + Gitea

```bash
git init -b main
git add -A
git status --short    # sanity-check node_modules/dist are NOT staged before committing
git commit -m "chore: initial scaffold"
tea repos create --login <login-name> --name <app-name> --description "<app-name>.apoena.dev" --init=false
git remote add origin ssh://git@git.apoena.dev:22222/julien/<app-name>.git
git push -u origin main
```

**Do not pass `--owner julien` to `tea repos create`** — `--owner` is for *organizations*, and passing a user account fails with `Error: GetOrgByName`. Omitting `--owner` creates the repo under the authenticated user. Pass `--login <login-name>` (the NAME from Step 2) since the git.apoena.dev login may not be tea's default.

**Do not add `Co-authored-by` to the commit** (per `~/CLAUDE.md`).

If `tea repos create` fails because the repo already exists, ask the user whether to push to the existing one or pick a new name.

## Step 8 — Provision in Coolify (automated)

If `$COOLIFY_API_TOKEN` is unset, skip this step and jump to Step 9. Both `$COOLIFY_API_TOKEN` and `$TEA_TOKEN` (the Gitea PAT) are exported from the user's `~/.dotfiles/zsh/private.zsh`; if either isn't loaded in the current shell (e.g. it was added after the session started), tell the user to `source ~/.dotfiles/zsh/private.zsh` (or open a new terminal) and re-run the skill — do NOT prompt for either inline.

The Gitea PAT is the env var **`$TEA_TOKEN`** (see above). Do NOT parse the tea config file or search the filesystem for a token — the sandbox blocks credential hunting, and the env var is simpler and authoritative. If `$TEA_TOKEN` is unavailable, that's fine: still do 8a–8c and 8e, **skip only 8d**, and hand the user the manual webhook URL + secret to paste (see 8d).

**Coolify API base:** `https://platform.apoena.dev/api/v1`. Auth: `Authorization: Bearer $COOLIFY_API_TOKEN`.

### 8a. Discover project + server UUIDs

```bash
curl -fsSL -H "Authorization: Bearer $COOLIFY_API_TOKEN" https://platform.apoena.dev/api/v1/projects   | jq '.[] | {uuid, name}'
curl -fsSL -H "Authorization: Bearer $COOLIFY_API_TOKEN" https://platform.apoena.dev/api/v1/servers   | jq '.[] | {uuid, name}'
```

If exactly one project and one server exist → use them. If multiple → print the lists and ask the user to pick one of each. Cache the chosen UUIDs to `~/.config/apoena/coolify.env` (`PROJECT_UUID=…\nSERVER_UUID=…`) so future runs skip the prompt; source the file first if it exists.

### 8b. Create the application — then FIX the git URL

```bash
WEBHOOK_SECRET=$(openssl rand -hex 32)
BUILD_PACK=$([ -f docker-compose.yml ] && echo dockercompose || echo dockerfile)

APP_UUID=$(curl -sS -X POST https://platform.apoena.dev/api/v1/applications/public   -H "Authorization: Bearer $COOLIFY_API_TOKEN"   -H "Content-Type: application/json"   -d "$(jq -n --arg p "$PROJECT_UUID" --arg s "$SERVER_UUID"           --arg name "<app-name>" --arg repo "https://git.apoena.dev/julien/<app-name>"           --arg domain "https://<subdomain>" --arg bp "$BUILD_PACK"           '{project_uuid:$p, server_uuid:$s, environment_name:"production",            git_repository:$repo, git_branch:"main",            build_pack:$bp, ports_exposes:"80",            name:$name, domains:$domain, instant_deploy:false}')"   | jq -r '.uuid')
```

**Custom domain → include `www`.** For a `*.apoena.dev` subdomain, `domains` is just `https://<subdomain>`. For a **custom apex from Step 2b**, set it to `https://<domain>,https://www.<domain>` (comma-separated) — Step 2b creates a `www` CNAME, so registering only the apex leaves `www.<domain>` resolving to a **certless endpoint** (Let's Encrypt never issues for `www`, TLS fails). Both domains share the one app.

If the response has no `uuid` or curl fails → print the error body, then fall through to Step 9.

**CRITICAL — fix `git_repository` after create.** The `applications/public` endpoint only fully parses github.com / gitlab.com / bitbucket URLs. For a self-hosted **Gitea** host it stores `git_repository` as the bare `julien/<app-name>`, and the deploy then fails instantly with `'julien/<app-name>' does not appear to be a git repository` (git treats it as a local path). PATCH it to the full clone URL and verify it persisted:

```bash
curl -fsSL -X PATCH https://platform.apoena.dev/api/v1/applications/$APP_UUID   -H "Authorization: Bearer $COOLIFY_API_TOKEN" -H "Content-Type: application/json"   -d "$(jq -n '{git_repository:"https://git.apoena.dev/julien/<app-name>.git", git_branch:"main"}')"
# verify — must print the full URL, not "julien/<app-name>":
curl -fsSL -H "Authorization: Bearer $COOLIFY_API_TOKEN" https://platform.apoena.dev/api/v1/applications/$APP_UUID | jq '.git_repository'
```

The repo is public, so the HTTPS clone needs no key — sanity-check with `git ls-remote https://git.apoena.dev/julien/<app-name>.git refs/heads/main`.

### 8c. Set the Gitea webhook secret on the Coolify app

```bash
curl -fsSL -X PATCH https://platform.apoena.dev/api/v1/applications/$APP_UUID   -H "Authorization: Bearer $COOLIFY_API_TOKEN"   -H "Content-Type: application/json"   -d "$(jq -n --arg s "$WEBHOOK_SECRET" '{manual_webhook_secret_gitea:$s}')"
```

### 8d. Create the Gitea webhook

**Only if `$TEA_TOKEN` is available.** If it's empty, skip this and tell the user to add the webhook manually — give them the target URL and the `$WEBHOOK_SECRET` (the Coolify side is already configured by 8c), pointing them at `https://git.apoena.dev/julien/<app-name>/settings/hooks`.

Coolify routes Gitea webhooks via a single shared endpoint: `https://platform.apoena.dev/webhooks/source/gitea/events/manual`. The app is matched by the repository URL in the payload, so no per-app UUID is needed in the webhook URL.

```bash
curl -fsSL -X POST https://git.apoena.dev/api/v1/repos/julien/<app-name>/hooks   -H "Authorization: token $TEA_TOKEN"   -H "Content-Type: application/json"   -d "$(jq -n --arg secret "$WEBHOOK_SECRET"           '{type:"gitea", active:true, events:["push"],            config:{url:"https://platform.apoena.dev/webhooks/source/gitea/events/manual",                    content_type:"json", secret:$secret}}')"
```

If non-2xx → print the response and tell the user the app exists in Coolify but the webhook needs to be added manually (give them the URL + secret to paste).

### 8e. Trigger initial deploy — and verify it succeeds

```bash
DUUID=$(curl -fsSL -X POST "https://platform.apoena.dev/api/v1/deploy?uuid=$APP_UUID&force=false"   -H "Authorization: Bearer $COOLIFY_API_TOKEN" | jq -r '.deployments[0].deployment_uuid')
```

Don't just fire-and-forget — **poll the deployment to a terminal state** (run the poll loop as a background command so its `sleep` is allowed), then confirm the live site:

```bash
for i in $(seq 1 90); do
  ST=$(curl -sS -H "Authorization: Bearer $COOLIFY_API_TOKEN" "https://platform.apoena.dev/api/v1/deployments/$DUUID" | jq -r '.status')
  case "$ST" in finished|failed|error|cancelled) break ;; esac
  sleep 5
done
echo "deploy: $ST"
# on failure, decode logs to diagnose (git-URL truncation from 8b is the most common cause):
#   curl ... /deployments/$DUUID | jq -r '.logs | fromjson | .[] | "[\(.type)] \(.output)"' | tail -20
# on success, verify HTTPS + cert:
curl -sS -o /dev/null -w "HTTP %{http_code} TLS %{ssl_verify_result}\n" --retry 6 --retry-all-errors https://<subdomain>/
```

Tell the user the result and: "Tail logs at https://platform.apoena.dev/project/$PROJECT_UUID/application/$APP_UUID."

Skip to Step 10.

## Step 9 — Print the Coolify checklist (fallback)

Reached only if Step 8 was skipped or any sub-step failed. Read `coolify-checklist.md` and substitute the placeholders, then print it to the user. Tell them: "Open https://platform.apoena.dev and paste these values into a new Application. I'll wait — let me know if any field is unclear."

## Step 10 — Bootstrap summary

The infra is live. Summarise the bootstrap in two lines:
- Local path: `<absolute-path>`
- Repo: `https://git.apoena.dev/julien/<app-name>`

If deployed via Step 8, also give the live URL `https://<subdomain>` (the first screen is now live) and note any pending manual step (e.g. the Gitea webhook if 8d was skipped). Then continue to Step 11 — do not stop here.

## Step 11 — Build out the app

The bootstrap is done and the first screen is deployed; now build the rest of the app the user asked for (Step 1). Don't wait to be told to start (no "say the word and I'll start on it") — begin immediately with the design interview below.

- **Design first with `/walk-with-me`.** Before writing any feature code, run the **walk-with-me** skill to reach shared understanding of the deep feature set: it interviews the user one decision at a time and writes the design docs (`CONTEXT.md`, `DESIGN.md`, any ADRs) into the project dir, escalating to `/qfd` for a goal→function→component decomposition when the change warrants it. This **is** the design step — do not also run `spec-driven-development`, it would be redundant ceremony.
- **Then build from those docs with `incremental-implementation`**, slice by slice — use **frontend-ui-engineering** for the UI slices.
- Build the features that go beyond the first screen — the remaining screens, search/filtering, detail views, persistence, whatever Step 1 and walk-with-me settled on.
- Commit and push each working slice. Pushes to `main` auto-deploy via the Coolify webhook (Step 8d), so every slice ships to `https://<subdomain>` — verify the live site after pushes that matter.
- Keep the deploy green: run `pnpm build` (clean, no warnings) + `pnpm lint` + `pnpm fmt` before each push, the same gates as Step 3.

</what-to-do>

<supporting-info>

## Stack rationale

- **Vite + Vue 3 + TypeScript** — matches `skills/web-dev/SKILL.md` ("Always use the most modern HTML, CSS, and JS"). `--template vue-ts` is the official Vite scaffold. Note: the modern `vue-ts` template ships demo assets (`src/assets/{vite.svg,vue.svg,hero.png}`, `public/icons.svg`, and its own `public/favicon.svg`) — clear the unused ones during scaffold.
- **Tailwind v4 via `@tailwindcss/vite`** — v4 dropped the `postcss` + `tailwind.config.js` ceremony; everything is configured in CSS via `@import "tailwindcss"` and `@plugin "daisyui"`.
- **DaisyUI** — Tailwind component library, registered as a Tailwind v4 plugin in the stylesheet (no JS import).
- **Fonts via `api.fonts.coollabs.io`** — privacy-friendly Google Fonts mirror (run by the Coolify team). The CSS `@import`s the font from `https://api.fonts.coollabs.io/css2?...` and sets it as `--font-sans` in the Tailwind v4 `@theme` block. **Note the `api.` subdomain** — the bare `fonts.coollabs.io` host serves the marketing homepage (HTML), not CSS, so the `@font-face` rules never load and the font silently falls back to system fonts. **The font `@import url(...)` MUST be the first line, before `@import "tailwindcss"`** — Tailwind inlines its own import into real rules, and per the CSS spec `@import` must precede all other rules, so a font import placed second is dropped by the build (with a warning) and never loads. To swap fonts, edit `src/style.css` — change the `@import url(...)` family and the `--font-sans` value (and `--font-mono` if you want a mono font like Fira Code applied app-wide).
- **oxc for lint + format** ([oxc.rs](https://oxc.rs)) — `oxlint` (Rust, ESLint-compatible, stable) and `oxfmt` (Prettier-compatible, Beta) replace the ESLint + Prettier stack with one fast toolchain and near-zero config. Chosen over ESLint/Prettier for speed and simplicity. **Limitation to be aware of:** as of mid-2026 oxlint lints only the `<script>` of `.vue` files (no `<template>` linting) and oxfmt's `.vue` support is partial — so the Vue markup layer is unchecked. Acceptable here because the type-checked `pnpm build` (`vue-tsc`) already catches template type errors, and most logic lives in `<script setup lang="ts">`. `.oxlintrc.json` is generated by `oxlint --init`; `.oxfmtrc.json` pins `semi: false` + `singleQuote: false` (no semicolons, double quotes).
- **Nginx-alpine for SPA serving** — tiny image, SPA fallback via `try_files`. Coolify expects port 80 by default for SPAs.
- **Gleam wisp + mist** — wisp is the request framework, mist the HTTP server. Standard combo.
- **SQLite via `sqlight`** — Gleam binding to SQLite. File lives in `data/app.db`, mounted as a Coolify persistent volume.

## Coolify conventions on platform.apoena.dev

- Apps deploy from public Gitea repos. **The `applications/public` API truncates non-GitHub git URLs to `owner/repo`** — you must PATCH `git_repository` to the full `https://git.apoena.dev/julien/<app>.git` URL after create, or the first deploy fails at the git-clone step (see Step 8b).
- The "Dockerfile" build pack is used for SPA-only apps (single `Dockerfile` at the repo root).
- The "Docker Compose" build pack is used when `docker-compose.yml` exists.
- Domains are configured per-resource as `https://<subdomain>` — Coolify provisions Let's Encrypt automatically as long as the DNS A/AAAA record for `<subdomain>.apoena.dev` already points at the Coolify host.
- Persistent storage paths must match what the container writes to (e.g. `/app/data` for SQLite).

## DNS

Whatever the domain, it must resolve to the Coolify host before Step 8 or Coolify's Let's Encrypt step fails.

- **`*.apoena.dev` subdomains** are covered by a wildcard — nothing to do. Sanity-check with `dig +short <subdomain>.apoena.dev` against `dig +short platform.apoena.dev` before deploying.
- **Custom marque domains** (separate apex, e.g. `typoena.app`) are provisioned by **Step 2b** — a `putRecord` of an `at.marque.dns` record into the apoena PDS, which marque's nameservers serve directly. Point `@`/`*` (A) and `www` (CNAME→apex) at `dig +short platform.apoena.dev`. The domain must already be registered in marque (`at.marque.domain/<domain>` record exists); the skill can't buy it. Auth uses `$MARQUE_APP_PASSWORD` from `~/.dotfiles/zsh/private.zsh`.

## When the user wants a different stack

Skill is opinionated for Vite/Vue/DaisyUI ± Gleam. If the user says "actually I want Svelte" or "Rust backend": stop, name what's different, and ask whether to (a) adapt manually after this skill runs the Gitea+Coolify parts, or (b) abort the skill entirely and do it by hand.

## Tabler icons + favicon

- The favicon is fetched from `https://raw.githubusercontent.com/tabler/tabler-icons/main/icons/outline/<name>.svg` at scaffold time, recoloured to the user's primary hex (Tabler outline icons use `stroke="currentColor"` → `sed` replace), and written to `public/favicon.svg` (overwriting the template's default).
- In-app icons live in `src/assets/icons/` — the user drops more Tabler SVGs there as needed. Pattern in Vue: `<img src="@/assets/icons/foo.svg" alt="" class="size-5" />` for static colour, or paste the SVG inline as a Vue component if it needs to follow `currentColor`.
- Primary color is wired into `src/style.css` via `@plugin "daisyui/theme" { name: "light"; default: true; --color-primary: <hex>; }`. This overrides only `--color-primary` on DaisyUI's built-in light theme — all other colors inherit — and the override propagates to both Tailwind utilities (`bg-primary`, `text-primary`) and DaisyUI components (`btn-primary`, `badge-primary`, etc.). Setting it in `@theme` alone would only cover Tailwind utilities, not DaisyUI components.

## Coolify automation requirements

Step 8 runs only if `$COOLIFY_API_TOKEN` is set. Both `$COOLIFY_API_TOKEN` and `$TEA_TOKEN` (the Gitea PAT used for webhook creation in 8d) are exported from `~/.dotfiles/zsh/private.zsh`. Use the env vars directly — do **not** parse the tea config file or run a recursive filesystem `find` for a token (the sandbox blocks credential hunting). If `$TEA_TOKEN` is missing from the current shell, have the user `source ~/.dotfiles/zsh/private.zsh` (or open a new terminal) and re-run; if it stays unavailable, skip the webhook (8d) and hand off manual instructions. The Gitea webhook URL is the same for every Coolify app on this instance — `https://platform.apoena.dev/webhooks/source/gitea/events/manual` — and is hardcoded in the skill; Coolify matches the app by repo URL in the payload.

Cached state lives in `~/.config/apoena/coolify.env` — `PROJECT_UUID` and `SERVER_UUID` after the one-time discovery prompt.

If anything in Step 8 fails (missing token, API error, repo URL mismatch in Coolify), the skill falls through to Step 9 — the original manual checklist — and the user finishes in the Coolify UI.

## Files in this skill

- `templates/Dockerfile.spa` — Vite build → nginx serve, port 80.
- `templates/Dockerfile.gleam` — Gleam build → erlang runtime, port 8000.
- `templates/nginx.conf` — SPA fallback.
- `templates/docker-compose.yml` — web + api + sqlite-volume template.
- `templates/tailwind-style.css` — Tailwind v4 + DaisyUI import (font import ordered first), with `{{PRIMARY_COLOR}}` placeholder.
- `templates/icons-readme.md` — README dropped into `src/assets/icons/` to document the icon folder.
- `templates/zed-settings.json` — copied verbatim to `.zed/settings.json`; points Zed's format-on-save at project-local oxfmt for TS/JS/Vue so editor saves match `.oxfmtrc.json` (no semicolons).
- `coolify-checklist.md` — printable per-app checklist with `{{PLACEHOLDERS}}`.

</supporting-info>
