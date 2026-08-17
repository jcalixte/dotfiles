---
name: apoena-gleam-backend
description: Use when an apoena app needs a backend — scaffolds a Gleam (wisp + mist) API in `backend/`, optionally with SQLite via sqlight, plus the Gleam Dockerfile and the web+api docker-compose.yml Coolify deploys from. Called by apoena-new, or on its own to add an API to an existing SPA.
---

<what-to-do>

## Inputs

- **App name** (kebab-case) — the Gleam project uses its snake_case form, `<app_name_snake>`.
- **Project root** — the repo root; the backend lands in `<root>/backend`.
- **SQLite?** — default yes for a backend. Adds `sqlight`, a `data/app.db`, and the compose volume.

## Prerequisites

Check both. If either fails, print the remediation and STOP.

| Tool | Check | Remediation |
|---|---|---|
| `docker` | `docker --version` | install OrbStack / Docker Desktop |
| `gleam` | `gleam --version` (≥ 1.0) | `brew install gleam erlang rebar3` |

## Step 1 — Scaffold the backend

From the project root:

```bash
mkdir backend && cd backend
gleam new . --name <app_name_snake>
gleam add wisp mist gleam_erlang gleam_http
```

If SQLite was selected: `gleam add sqlight` and create `src/<app_name_snake>/db.gleam` opening `data/app.db`.

Replace `src/<app_name_snake>.gleam` with a minimal wisp app exposing `GET /api/health` returning `200 ok`. Bind `mist` to port `8000`.

Copy `templates/Dockerfile.gleam` to `backend/Dockerfile`.

## Step 2 — docker-compose

Copy `templates/docker-compose.yml` to the project root. Substitute `<APP_NAME>`. If no SQLite, remove the `volumes:` block and the `data/` mount from `api`.

The compose file's presence is what makes Coolify pick the **Docker Compose** build pack instead of the plain Dockerfile one — so only create it when there really is a backend.

## Step 3 — Verify

`cd backend && gleam run` boots on `:8000`; curl `http://localhost:8000/api/health` returns `ok`, then kill it. If the frontend was scaffolded with the `/api` dev proxy, `pnpm dev` on `:5173` should reach the same endpoint through `/api/health`.

</what-to-do>

<supporting-info>

## Stack rationale

- **Gleam wisp + mist** — wisp is the request framework, mist the HTTP server. Standard combo.
- **SQLite via `sqlight`** — Gleam binding to SQLite. File lives in `data/app.db`, mounted as a Coolify persistent volume. Persistent storage paths must match what the container writes to (e.g. `/app/data`).

## When the user wants a different backend

This skill only supports Gleam. If the user wants Rust/Node/Go: stop, name what's different, and ask whether to (a) scaffold the backend by hand after the repo + Coolify parts run, or (b) skip the automated bootstrap entirely.

## Files in this skill

- `templates/Dockerfile.gleam` — Gleam build → erlang runtime, port 8000.
- `templates/docker-compose.yml` — web + api + sqlite-volume template.

</supporting-info>
