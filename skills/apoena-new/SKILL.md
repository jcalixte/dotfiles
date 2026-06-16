---
name: apoena-new
description: Use when the user wants to bootstrap a new *.apoena.dev app on Coolify — scaffolds a Vite + Vue + DaisyUI SPA (optionally with a Gleam backend and SQLite), creates a public Gitea repo on git.apoena.dev, and prints the Coolify deploy checklist.
---

<what-to-do>

Walk the user through bootstrapping a new `*.apoena.dev` app end-to-end. Ask the inputs one at a time, waiting for the answer before moving on. Do not assume defaults silently — show the default in the question and let the user override.

Then scaffold the code, create the Gitea repo, push, and print the Coolify checklist. **Do NOT log into or call Coolify.** Hand off the checklist for the user to paste into the UI at `https://platform.apoena.dev`.

## Step 1 — Gather inputs

Ask in this order:

1. **App name** (kebab-case, lowercase). Used for the local folder, the Gitea repo, and the subdomain prefix. Example: `qrcode`.
2. **Backend?** (default: no). If yes, the stack is Gleam (`wisp` + `mist`). Skill does not support other backends — if the user wants something else, stop and ask them to scaffold the backend manually.
3. **SQLite?** Default: yes if backend was chosen, no if SPA-only. (A SPA can still use SQLite via the backend; offering it for SPA-only means "set up the volume now even though there's nothing using it yet" — discourage that.)
4. **Local scaffold path.** Default: `$PWD/<app-name>`.
5. **Subdomain.** Default: `<app-name>.apoena.dev`. Confirm.
6. **Primary color** (hex, e.g. `#570DF8`). Default: `#570DF8` (DaisyUI default). Used both as the Tailwind v4 `--color-primary` and as the favicon stroke color.
7. **Favicon icon name** from Tabler (`https://tabler.io/icons`). Default: `circle`. Use the exact slug shown on the Tabler page (e.g. `bolt`, `paw`, `qrcode`). Outline variant only.

## Step 2 — Verify prerequisites

Run these checks. If any fail, print the missing tool + remediation and STOP.

| Tool | Check | Remediation |
|---|---|---|
| `node` | `node --version` (≥ 20) | `brew install node` |
| `pnpm` | `pnpm --version` | `npm i -g pnpm` (or fall back to `npm` — note the choice and use it everywhere below) |
| `tea` | `tea --version` && `tea login list` contains `git.apoena.dev` | `brew install tea` then `tea login add --name apoena --url https://git.apoena.dev --token <PAT>` (PAT from `https://git.apoena.dev/user/settings/applications`) |
| `docker` (backend only) | `docker --version` | install OrbStack / Docker Desktop |
| `gleam` (backend only) | `gleam --version` (≥ 1.0) | `brew install gleam erlang rebar3` |

## Step 3 — Scaffold the frontend

```bash
cd <local-path-parent>
npm create vite@latest <app-name> -- --template vue-ts
cd <app-name>
pnpm install
pnpm add -D tailwindcss @tailwindcss/vite
pnpm add daisyui@latest
```

Then write/patch these files (templates in `templates/`):

- `vite.config.ts` — add `@tailwindcss/vite` plugin, and (if backend) the `/api` dev proxy to `http://localhost:8000`.
- `src/style.css` — copy `templates/tailwind-style.css` then substitute `{{PRIMARY_COLOR}}` with the user's hex.
- `src/App.vue` — replace boilerplate with a minimal DaisyUI landing card showing the app name. Drop `src/components/HelloWorld.vue`.
- `src/assets/icons/` — create the folder and copy `templates/icons-readme.md` to `src/assets/icons/README.md`. This is the reusable in-app icon folder; the user drops Tabler SVGs here as needed.
- `public/favicon.svg` — fetch `https://raw.githubusercontent.com/tabler/tabler-icons/main/icons/outline/<favicon-icon>.svg`, then `sed` replace `currentColor` with the primary-color hex. Write to `public/favicon.svg`. If the curl 404s, ask the user for a different icon name and retry. Delete `public/vite.svg`.
- `index.html` — replace the `<link rel="icon" ...>` line with `<link rel="icon" type="image/svg+xml" href="/favicon.svg" />`. Update `<title>` to the app name.
- `Dockerfile` — copy `templates/Dockerfile.spa`.
- `nginx.conf` — copy `templates/nginx.conf`.
- `.dockerignore` — at minimum `node_modules`, `dist`, `.git`.

Verify `pnpm dev` boots (start it, curl `http://localhost:5173`, kill it).

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

Write a short `README.md`:

```markdown
# <app-name>

Deployed at https://<subdomain>

## Develop

\`\`\`bash
pnpm dev           # frontend on :5173
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
git commit -m "chore: initial scaffold"
tea repos create --owner julien --name <app-name> --description "<app-name>.apoena.dev" --init=false
git remote add origin ssh://git@git.apoena.dev:22222/julien/<app-name>.git
git push -u origin main
```

**Do not add `Co-authored-by` to the commit** (per `~/CLAUDE.md`).

If `tea repos create` fails because the repo already exists, ask the user whether to push to the existing one or pick a new name.

## Step 8 — Print the Coolify checklist

Read `coolify-checklist.md` and substitute the placeholders, then print it to the user. Tell them: "Open https://platform.apoena.dev and paste these values into a new Application. I'll wait — let me know if any field is unclear."

## Step 9 — Done

Summarise in two lines:
- Local path: `<absolute-path>`
- Repo: `https://git.apoena.dev/julien/<app-name>`

</what-to-do>

<supporting-info>

## Stack rationale

- **Vite + Vue 3 + TypeScript** — matches `skills/web-dev/SKILL.md` ("Always use the most modern HTML, CSS, and JS"). `--template vue-ts` is the official Vite scaffold.
- **Tailwind v4 via `@tailwindcss/vite`** — v4 dropped the `postcss` + `tailwind.config.js` ceremony; everything is configured in CSS via `@import "tailwindcss"` and `@plugin "daisyui"`.
- **DaisyUI** — Tailwind component library, registered as a Tailwind v4 plugin in the stylesheet (no JS import).
- **Fonts via `fonts.coollabs.io`** — privacy-friendly Google Fonts mirror (run by the Coolify team). The CSS `@import`s `Inter` from `https://fonts.coollabs.io/css2?...` and sets it as `--font-sans` in the Tailwind v4 `@theme` block. To swap fonts, edit `src/style.css` — change the `@import url(...)` family and the `--font-sans` value.
- **Nginx-alpine for SPA serving** — tiny image, SPA fallback via `try_files`. Coolify expects port 80 by default for SPAs.
- **Gleam wisp + mist** — wisp is the request framework, mist the HTTP server. Standard combo.
- **SQLite via `sqlight`** — Gleam binding to SQLite. File lives in `data/app.db`, mounted as a Coolify persistent volume.

## Coolify conventions on platform.apoena.dev

- Apps deploy from public Gitea repos (Coolify polls the branch).
- The "Dockerfile" build pack is used for SPA-only apps (single `Dockerfile` at the repo root).
- The "Docker Compose" build pack is used when `docker-compose.yml` exists.
- Domains are configured per-resource as `https://<subdomain>` — Coolify provisions Let's Encrypt automatically as long as the DNS A/AAAA record for `<subdomain>.apoena.dev` already points at the Coolify host.
- Persistent storage paths must match what the container writes to (e.g. `/app/data` for SQLite).

## DNS reminder

The skill does NOT configure DNS. If `<subdomain>.apoena.dev` does not already resolve to the Coolify host, the Let's Encrypt step inside Coolify will fail. Tell the user to add the record (wildcard `*.apoena.dev` may already cover it — check `dig +short <subdomain>.apoena.dev` before deploying).

## When the user wants a different stack

Skill is opinionated for Vite/Vue/DaisyUI ± Gleam. If the user says "actually I want Svelte" or "Rust backend": stop, name what's different, and ask whether to (a) adapt manually after this skill runs the Gitea+Coolify parts, or (b) abort the skill entirely and do it by hand.

## Tabler icons + favicon

- The favicon is fetched from `https://raw.githubusercontent.com/tabler/tabler-icons/main/icons/outline/<name>.svg` at scaffold time, recoloured to the user's primary hex (Tabler outline icons use `stroke="currentColor"` → `sed` replace), and written to `public/favicon.svg`.
- In-app icons live in `src/assets/icons/` — the user drops more Tabler SVGs there as needed. Pattern in Vue: `<img src="@/assets/icons/foo.svg" alt="" class="size-5" />` for static colour, or paste the SVG inline as a Vue component if it needs to follow `currentColor`.
- Primary color is wired into `src/style.css` as `--color-primary` inside the Tailwind v4 `@theme` block, so DaisyUI's `bg-primary`, `text-primary`, etc. pick it up automatically.

## Files in this skill

- `templates/Dockerfile.spa` — Vite build → nginx serve, port 80.
- `templates/Dockerfile.gleam` — Gleam build → erlang runtime, port 8000.
- `templates/nginx.conf` — SPA fallback.
- `templates/docker-compose.yml` — web + api + sqlite-volume template.
- `templates/tailwind-style.css` — Tailwind v4 + DaisyUI import, with `{{PRIMARY_COLOR}}` placeholder.
- `templates/icons-readme.md` — README dropped into `src/assets/icons/` to document the icon folder.
- `coolify-checklist.md` — printable per-app checklist with `{{PLACEHOLDERS}}`.

</supporting-info>
