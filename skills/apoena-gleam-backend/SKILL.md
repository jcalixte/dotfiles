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

Copy `templates/docker-compose.yml` to the project root. Substitute `<APP_NAME>`. If no SQLite, remove the top-level `volumes:` block and the `volumes:` mount from `api`.

The compose file's presence is what makes Coolify pick the **Docker Compose** build pack instead of the plain Dockerfile one — so only create it when there really is a backend.

The template already follows these rules. Keep them when you edit it:

- **Never publish a host port.** Coolify's Traefik already owns host port 80 and routes to the container by label, so `ports: - "80:80"` fails the deploy with `Bind for 0.0.0.0:80 failed: port is already allocated`. Use `expose`, not `ports`, on both services.
- **Every service has a `healthcheck`.** Without one Coolify reports the app as `running:unknown` and cannot tell a booted container from a crashed one. Both base images are Alpine, so busybox `wget` is available. `web` waits for `api` with `depends_on: {api: {condition: service_healthy}}`. After deploy, the app status must read `running:healthy`.
- **The SQLite volume is named.** A bind mount (`./data:/app/data`) points at the build artifact directory, which Coolify replaces on each deploy, so the data is lost.

The SPA reaches the API inside the compose network, through nginx. Add this block to `nginx.conf` (from **apoena-spa-scaffold**), inside `server { … }`:

```nginx
  location /api/ {
    proxy_pass http://api:8000;
    proxy_set_header Host $host;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
  }
```

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
- `templates/docker-compose.yml` — web + api + named SQLite volume, `expose` only, with healthchecks.

</supporting-info>
