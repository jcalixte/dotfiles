---
name: apoena-new
description: Use when the user wants to bootstrap a new *.apoena.dev app (or an app on a custom marque domain) on Coolify — orchestrates the apoena skills end-to-end: DNS (marque-dns), SPA scaffold with a real first screen (apoena-spa-scaffold), optional Gleam backend (apoena-gleam-backend), Gitea repo (apoena-gitea-repo), Coolify provisioning + first deploy (apoena-coolify-deploy), then hands off to the feature-build skills to flesh out the rest.
---

<what-to-do>

Walk the user through bootstrapping a new `*.apoena.dev` app end-to-end. This skill is the **orchestrator**: it gathers the inputs once, then invokes the specific skills in order and passes them along. Read this file for the sequence; read each sub-skill when you reach its step.

| Step | Skill | When |
|---|---|---|
| 2b | **marque-dns** | custom apex only (skip for `*.apoena.dev`) |
| 3 | **apoena-spa-scaffold** | always |
| 4 | **apoena-gleam-backend** | backend selected |
| 6 | **apoena-gitea-repo** | always |
| 7 | **apoena-coolify-deploy** | always |
| 9 | **walk-with-me** → **incremental-implementation** | always |

The scaffold is **not** a placeholder. Step 3 builds a real first screen of the app the user asked for, and once that's deployed, Step 9 designs the rest with `/walk-with-me` and then hands off to the feature-build skills. Do not stop at the first screen and wait to be told to continue — proceed into Step 9.

## Step 1 — Gather inputs

Ask the inputs one at a time, waiting for the answer before moving on. Do not assume defaults silently — show the default in the question and let the user override.

**First, establish what the app is.** Before the infra questions below, make sure you understand the app's purpose and core features — from the user's request in this conversation and any design docs / spec already in the target directory (read them; don't re-ask what's already written down). If the concept is thin or missing, ask the user for a one-paragraph description before continuing. You use this in three places: to theme the scaffold, to build a real first screen (Step 3), and to drive the feature build (Step 9). Then gather the infra inputs.

Ask in this order:

1. **App name** (kebab-case, lowercase). Used for the local folder, the Gitea repo, and the subdomain prefix. Example: `qrcode`.
2. **Backend?** (default: no). If yes, the stack is Gleam (`wisp` + `mist`). Not supported: anything else — if the user wants something else, stop and ask them to scaffold the backend manually.
3. **SQLite?** Default: yes if backend was chosen, no if SPA-only. (A SPA can still use SQLite via the backend; offering it for SPA-only means "set up the volume now even though there's nothing using it yet" — discourage that.)
4. **Local scaffold path.** Default: `$PWD/<app-name>`. **If the current directory is already named `<app-name>` (or already holds the project's design docs), scaffold into the current directory instead of a nested `<app-name>/<app-name>` — confirm this with the user.**
5. **Subdomain / domain.** Default: `<app-name>.apoena.dev`. Confirm. If the user gives a **custom apex bought via marque** (not under `apoena.dev`, e.g. `typoena.app`), flag it — Step 2b provisions its DNS, and it must already be registered in marque.
6. **Primary color** (hex, e.g. `#570DF8`). Default: `#570DF8` (DaisyUI default). Used both as the Tailwind v4 `--color-primary` and as the favicon stroke color.
7. **Favicon icon name** from Tabler (`https://tabler.io/icons`). Default: `circle`. Use the exact slug shown on the Tabler page (e.g. `bolt`, `paw`, `qrcode`). Outline variant only. Pre-verify it resolves (HTTP 200) before scaffolding so you don't discover a 404 late.

## Step 2 — Verify prerequisites

Run these checks. If any fail, print the missing tool + remediation and STOP.

| Tool | Check | Remediation |
|---|---|---|
| `node` | `node --version` (≥ 20) | `brew install node` |
| `pnpm` | `pnpm --version` | `npm i -g pnpm` (or fall back to `npm` — note the choice and use it everywhere below) |
| `tea` | `tea --version` && `tea login list` contains `git.apoena.dev` | `brew install tea` then `tea login add --name apoena --url https://git.apoena.dev --token <PAT>` (PAT from `https://git.apoena.dev/user/settings/applications`) |

> **The Gitea login may be named anything** (not necessarily `apoena`) and need not be tea's default. Identify it by URL in `tea login list`; capture its **NAME** (for `--login` in Step 6) and confirm the SSH host/port is `git.apoena.dev:22222`. Do not assume the login name is `apoena` anywhere downstream.

Backend-only tools (`docker`, `gleam`) are checked by **apoena-gleam-backend** in Step 4.

## Step 2b — DNS for a custom domain

Only when the domain is not under `apoena.dev`. `*.apoena.dev` is covered by a wildcard — skip. Do it here, not at deploy, so DNS propagates while you scaffold.

→ Run the **marque-dns** skill with the domain. It writes the A/`*`/`www` records into the apoena PDS and verifies them against marque's nameservers.

## Step 3 — Scaffold the frontend

→ Run the **apoena-spa-scaffold** skill, passing: app name, project dir, primary color, favicon icon name, whether there's a backend (for the `/api` dev proxy), and the app's purpose + core features from Step 1 (it builds the real first screen from that).

It returns having verified `pnpm build` / `pnpm lint` / `pnpm fmt` and having checked the screen in both colour schemes. If it reports that an informative `README.md` already existed, skip Step 5.

## Step 4 — Backend (if selected)

→ Run the **apoena-gleam-backend** skill with the app name, project root, and the SQLite choice. It scaffolds `backend/`, its Dockerfile, and the root `docker-compose.yml`.

If no backend, do NOT create a `docker-compose.yml` — Coolify uses the Dockerfile build pack directly.

## Step 5 — README

Skip if an informative `README.md` already exists (see Step 3). Otherwise write a short `README.md`:

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

## Step 6 — Git + Gitea

→ Run the **apoena-gitea-repo** skill with the app name, project dir, and the login NAME from Step 2. It commits, creates the public repo, and pushes `main`.

## Step 7 — Provision in Coolify

→ Run the **apoena-coolify-deploy** skill with the app name, the domain from Step 1, and the project dir (it reads it to pick the build pack). It creates the app via the API, wires the push webhook, triggers the first deploy and polls it to a terminal state — or prints the manual UI checklist if `$COOLIFY_API_TOKEN` is unavailable.

## Step 8 — Bootstrap summary

The infra is live. Summarise the bootstrap in two lines:
- Local path: `<absolute-path>`
- Repo: `https://git.apoena.dev/julien/<app-name>`

If it deployed, also give the live URL `https://<subdomain>` (the first screen is now live) and note any pending manual step (e.g. the Gitea webhook if the `$TEA_TOKEN` sub-step was skipped). Then continue to Step 9 — do not stop here.

## Step 9 — Build out the app

The bootstrap is done and the first screen is deployed; now build the rest of the app the user asked for (Step 1). Don't wait to be told to start (no "say the word and I'll start on it") — begin immediately with the design interview below.

- **Design first with `/walk-with-me`.** Before writing any feature code, run the **walk-with-me** skill to reach shared understanding of the deep feature set: it interviews the user one decision at a time and writes the design docs (`CONTEXT.md`, `DESIGN.md`, any ADRs) into the project dir, escalating to `/qfd` for a goal→function→component decomposition when the change warrants it. This **is** the design step — do not also run `spec-driven-development`, it would be redundant ceremony.
- **Then build from those docs with `incremental-implementation`**, slice by slice — use **frontend-ui-engineering** for the UI slices, and **daisyui-contrast** for any new colour you introduce.
- Build the features that go beyond the first screen — the remaining screens, search/filtering, detail views, persistence, whatever Step 1 and walk-with-me settled on.
- Commit and push each working slice. Pushes to `main` auto-deploy via the Coolify webhook, so every slice ships to `https://<subdomain>` — verify the live site after pushes that matter.
- Keep the deploy green: run `pnpm build` (clean, no warnings) + `pnpm lint` + `pnpm fmt` before each push, the same gates as Step 3.

</what-to-do>

<supporting-info>

## The skills this orchestrates

Each stands alone and can be run directly against an existing project; this skill only sequences them and threads the Step 1 answers through.

- **marque-dns** — `at.marque.dns` record into the apoena PDS for a custom apex. Marque's nameservers serve it directly, so the `putRecord` is live DNS.
- **apoena-spa-scaffold** — Vite + Vue 3 + TS, Tailwind v4, DaisyUI, oxc lint/format, Tabler favicon, `Dockerfile` + `nginx.conf`. Builds the real first screen. Owns the SPA templates.
- **daisyui-contrast** — measures WCAG contrast for `--color-primary` / `--color-primary-content` and any hand-written pair. Used by the scaffold and again during the feature build.
- **apoena-gleam-backend** — Gleam `wisp` + `mist` in `backend/`, optional `sqlight`, Gleam Dockerfile, root `docker-compose.yml`.
- **apoena-gitea-repo** — public repo on `git.apoena.dev` via `tea`, SSH remote on port `22222`, initial commit + push.
- **apoena-coolify-deploy** — Coolify application via the API on `platform.apoena.dev`, the git-URL PATCH self-hosted Gitea needs, push webhook, first deploy polled to completion. Owns the manual fallback checklist.

## When the user wants a different stack

The chain is opinionated for Vite/Vue/DaisyUI ± Gleam. If the user says "actually I want Svelte" or "Rust backend": stop, name what's different, and ask whether to (a) adapt manually after the Gitea + Coolify skills run, or (b) abort the bootstrap entirely and do it by hand.

</supporting-info>
