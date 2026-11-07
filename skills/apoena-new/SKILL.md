---
name: apoena-new
description: Use when the user wants to bootstrap a new *.apoena.dev app (or an app on a custom marque domain) on Coolify — scaffolds a Vite + Vue + DaisyUI SPA (optionally with a Gleam backend and SQLite), creates a public Gitea repo on git.apoena.dev, provisions the Coolify app via API (falling back to a printable deploy checklist), builds a real first screen of the app the user asked for, and then hands off to the feature-build skills to flesh out the rest.
---

<what-to-do>

Walk the user through bootstrapping a new `*.apoena.dev` app end-to-end. Ask the inputs one at a time, waiting for the answer before moving on. Do not assume defaults silently — show the default in the question and let the user override.

Then scaffold the code, create the Gitea repo, push, and provision the Coolify app via its API (Step 8) when `$COOLIFY_API_TOKEN` is available — otherwise print the checklist for the user to paste into the UI. Calling the Coolify **API** is expected and fine; do NOT try to drive the Coolify **web UI** / a browser.

The scaffold is **not** a placeholder. Step 3 builds a real first screen of the app the user asked for, and once that's deployed, Step 10 designs the rest of the app with `/walk-with-me` and then hands off to the feature-build skills. Do not stop at the first screen and wait to be told to continue — proceed into Step 10.

## Step 1 — Gather inputs

**First, establish what the app is.** Before the infra questions below, make sure you understand the app's purpose and core features — from the user's request in this conversation and any design docs / spec already in the target directory (read them; don't re-ask what's already written down). If the concept is thin or missing, ask the user for a one-paragraph description before continuing. You use this in three places: to theme the scaffold, to build a real first screen (Step 3), and to drive the feature build (Step 10). Then gather the infra inputs.

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

Each sub-skill below repeats its own check before it acts; this table only fails early, before anything is scaffolded.

## Step 2b — DNS for a custom domain (skip for `*.apoena.dev`)

If the domain is a custom apex bought via marque, run the **marque-dns** skill now, not at deploy, so DNS propagates while you scaffold. It also creates the `www` CNAME, so Step 8 registers both `https://<domain>` and `https://www.<domain>`.

## Step 3 — Scaffold the frontend

Run the **apoena-spa-scaffold** skill and follow it to the end. Give it the Step 1 answers: app name, local scaffold path, primary color, favicon icon, what the app is, and whether there is a backend (for the `/api` dev proxy). It builds the real first screen (secondary screens come in Step 10), with the light / dark theme toggle, the Esc-closable modal, the measured contrast pairs for both themes, and the build / lint / format / browser checks.

If it reports that an informative `README.md` already exists, **skip Step 6**.

## Step 4 — Scaffold the backend (if selected)

Run the **apoena-gleam-backend** skill with the app name, the project root and the SQLite answer. It writes `backend/`, the Gleam Dockerfile, the `docker-compose.yml` and the `/api/` proxy block in `nginx.conf`.

## Step 5 — No backend, no compose file

If there is no backend, do NOT create a `docker-compose.yml`: its presence makes Coolify pick the Docker Compose build pack, and the SPA deploys with the plain Dockerfile one.

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

Run the **apoena-gitea-repo** skill with the app name, the project dir and the description `<app-name>.apoena.dev` (or the custom domain). The repo is **public**: Coolify clones it without credentials.

## Step 8 — Deploy on Coolify

Run the **apoena-coolify-deploy** skill with the app name, the domain from Step 1 and the project dir. It creates the app through the API, fixes the Gitea git URL, wires the push webhook, runs the first deploy and polls it. Without `$COOLIFY_API_TOKEN` it prints the manual checklist instead.

## Step 9 — Bootstrap summary

The infra is live. Summarise the bootstrap in two lines:
- Local path: `<absolute-path>`
- Repo: `https://git.apoena.dev/julien/<app-name>`

If Step 8 deployed through the API, also give the live URL `https://<subdomain>` (the first screen is now live) and note any pending manual step (e.g. the Gitea webhook if it was skipped). Then continue to Step 10 — do not stop here.

## Step 10 — Build out the app

The bootstrap is done and the first screen is deployed; now build the rest of the app the user asked for (Step 1). Don't wait to be told to start (no "say the word and I'll start on it") — begin immediately with the design interview below.

- **Design first with `/walk-with-me`.** Before writing any feature code, run the **walk-with-me** skill to reach shared understanding of the deep feature set: it interviews the user one decision at a time and writes the design docs (`CONTEXT.md`, `DESIGN.md`, any ADRs) into the project dir, escalating to `/qfd` for a goal→function→component decomposition when the change warrants it. This **is** the design step — do not also run `spec-driven-development`, it would be redundant ceremony.
- **Then build from those docs with `incremental-implementation`**, slice by slice — use **frontend-ui-engineering** for the UI slices.
- Build the features that go beyond the first screen — the remaining screens, search/filtering, detail views, persistence, whatever Step 1 and walk-with-me settled on.
- Commit and push each working slice. Pushes to `main` auto-deploy via the Coolify webhook (Step 8), so every slice ships to `https://<subdomain>` — verify the live site after pushes that matter.
- Keep the deploy green: run `pnpm build` (clean, no warnings) + `pnpm lint` + `pnpm fmt` before each push, the same gates as apoena-spa-scaffold.

</what-to-do>

<supporting-info>

## Stack rationale

- **Frontend** — Vite + Vue 3 + TypeScript, Tailwind v4, DaisyUI, oxc, nginx. The rationale lives in **apoena-spa-scaffold**.
- **Backend** — Gleam (wisp + mist) and SQLite via `sqlight`. The rationale lives in **apoena-gleam-backend**.

## When the user wants a different stack

Skill is opinionated for Vite/Vue/DaisyUI ± Gleam. If the user says "actually I want Svelte" or "Rust backend": stop, name what's different, and ask whether to (a) adapt manually after this skill runs the Gitea+Coolify parts, or (b) abort the skill entirely and do it by hand.

## Sub-skills

Each step's details, templates and failure modes live in its skill: **marque-dns** (2b), **apoena-spa-scaffold** (3), **apoena-gleam-backend** (4), **apoena-gitea-repo** (7), **apoena-coolify-deploy** (8). Change them there, not here.

</supporting-info>
