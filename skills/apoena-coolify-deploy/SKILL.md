---
name: apoena-coolify-deploy
description: Use when a Gitea repo needs a Coolify application on platform.apoena.dev — creates it via the API, fixes the git URL Coolify truncates for self-hosted Gitea, wires the push webhook, triggers the first deploy and polls it to a terminal state. Falls back to a printable UI checklist when the API token is missing. Called by apoena-new, or on its own for an existing repo.
---

<what-to-do>

## Inputs

- **App name** (kebab-case) — the Coolify resource name and the Gitea repo name under `julien/`.
- **Domain** — `<app-name>.apoena.dev`, or a custom apex already provisioned via the **marque-dns** skill.
- **Project dir** — read to decide the build pack (`docker-compose.yml` present or not).

Call the Coolify **API**. Do NOT try to drive the Coolify **web UI** / a browser.

## Step 1 — Provision via API (automated)

If `$COOLIFY_API_TOKEN` is unset, skip to Step 2. Both `$COOLIFY_API_TOKEN` and `$TEA_TOKEN` (the Gitea PAT) are exported from the user's `~/.dotfiles/zsh/private.zsh`; if either isn't loaded in the current shell (e.g. it was added after the session started), tell the user to `source ~/.dotfiles/zsh/private.zsh` (or open a new terminal) and re-run — do NOT prompt for either inline.

The Gitea PAT is the env var **`$TEA_TOKEN`**. Do NOT parse the tea config file or search the filesystem for a token — the sandbox blocks credential hunting, and the env var is simpler and authoritative. If `$TEA_TOKEN` is unavailable, that's fine: still do 1a–1c and 1e, **skip only 1d**, and hand the user the manual webhook URL + secret to paste (see 1d).

**Coolify API base:** `https://platform.apoena.dev/api/v1`. Auth: `Authorization: Bearer $COOLIFY_API_TOKEN`.

### 1a. Discover project + server UUIDs

```bash
curl -fsSL -H "Authorization: Bearer $COOLIFY_API_TOKEN" https://platform.apoena.dev/api/v1/projects   | jq '.[] | {uuid, name}'
curl -fsSL -H "Authorization: Bearer $COOLIFY_API_TOKEN" https://platform.apoena.dev/api/v1/servers   | jq '.[] | {uuid, name}'
```

If exactly one project and one server exist → use them. If multiple → print the lists and ask the user to pick one of each. Cache the chosen UUIDs to `~/.config/apoena/coolify.env` (`PROJECT_UUID=…\nSERVER_UUID=…`) so future runs skip the prompt; source the file first if it exists.

### 1b. Create the application — then FIX the git URL

```bash
WEBHOOK_SECRET=$(openssl rand -hex 32)
BUILD_PACK=$([ -f docker-compose.yml ] && echo dockercompose || echo dockerfile)

APP_UUID=$(curl -sS -X POST https://platform.apoena.dev/api/v1/applications/public   -H "Authorization: Bearer $COOLIFY_API_TOKEN"   -H "Content-Type: application/json"   -d "$(jq -n --arg p "$PROJECT_UUID" --arg s "$SERVER_UUID"           --arg name "<app-name>" --arg repo "https://git.apoena.dev/julien/<app-name>"           --arg domain "https://<subdomain>" --arg bp "$BUILD_PACK"           '{project_uuid:$p, server_uuid:$s, environment_name:"production",            git_repository:$repo, git_branch:"main",            build_pack:$bp, ports_exposes:"80",            name:$name, domains:$domain, instant_deploy:false}')"   | jq -r '.uuid')
```

**Custom domain → include `www`.** For a `*.apoena.dev` subdomain, `domains` is just `https://<subdomain>`. For a **custom apex provisioned by marque-dns**, set it to `https://<domain>,https://www.<domain>` (comma-separated) — marque-dns creates a `www` CNAME, so registering only the apex leaves `www.<domain>` resolving to a **certless endpoint** (Let's Encrypt never issues for `www`, TLS fails). Both domains share the one app.

If the response has no `uuid` or curl fails → print the error body, then fall through to Step 2.

**CRITICAL — fix `git_repository` after create.** The `applications/public` endpoint only fully parses github.com / gitlab.com / bitbucket URLs. For a self-hosted **Gitea** host it stores `git_repository` as the bare `julien/<app-name>`, and the deploy then fails instantly with `'julien/<app-name>' does not appear to be a git repository` (git treats it as a local path). PATCH it to the full clone URL and verify it persisted:

```bash
curl -fsSL -X PATCH https://platform.apoena.dev/api/v1/applications/$APP_UUID   -H "Authorization: Bearer $COOLIFY_API_TOKEN" -H "Content-Type: application/json"   -d "$(jq -n '{git_repository:"https://git.apoena.dev/julien/<app-name>.git", git_branch:"main"}')"
# verify — must print the full URL, not "julien/<app-name>":
curl -fsSL -H "Authorization: Bearer $COOLIFY_API_TOKEN" https://platform.apoena.dev/api/v1/applications/$APP_UUID | jq '.git_repository'
```

The repo is public, so the HTTPS clone needs no key — sanity-check with `git ls-remote https://git.apoena.dev/julien/<app-name>.git refs/heads/main`.

### 1c. Set the Gitea webhook secret on the Coolify app

```bash
curl -fsSL -X PATCH https://platform.apoena.dev/api/v1/applications/$APP_UUID   -H "Authorization: Bearer $COOLIFY_API_TOKEN"   -H "Content-Type: application/json"   -d "$(jq -n --arg s "$WEBHOOK_SECRET" '{manual_webhook_secret_gitea:$s}')"
```

### 1d. Create the Gitea webhook

**Only if `$TEA_TOKEN` is available.** If it's empty, skip this and tell the user to add the webhook manually — give them the target URL and the `$WEBHOOK_SECRET` (the Coolify side is already configured by 1c), pointing them at `https://git.apoena.dev/julien/<app-name>/settings/hooks`.

Coolify routes Gitea webhooks via a single shared endpoint: `https://platform.apoena.dev/webhooks/source/gitea/events/manual`. The app is matched by the repository URL in the payload, so no per-app UUID is needed in the webhook URL.

```bash
curl -fsSL -X POST https://git.apoena.dev/api/v1/repos/julien/<app-name>/hooks   -H "Authorization: token $TEA_TOKEN"   -H "Content-Type: application/json"   -d "$(jq -n --arg secret "$WEBHOOK_SECRET"           '{type:"gitea", active:true, events:["push"],            config:{url:"https://platform.apoena.dev/webhooks/source/gitea/events/manual",                    content_type:"json", secret:$secret}}')"
```

If non-2xx → print the response and tell the user the app exists in Coolify but the webhook needs to be added manually (give them the URL + secret to paste).

### 1e. Trigger initial deploy — and verify it succeeds

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
# on failure, decode logs to diagnose (git-URL truncation from 1b is the most common cause):
#   curl ... /deployments/$DUUID | jq -r '.logs | fromjson | .[] | "[\(.type)] \(.output)"' | tail -20
# on success, verify HTTPS + cert:
curl -sS -o /dev/null -w "HTTP %{http_code} TLS %{ssl_verify_result}\n" --retry 6 --retry-all-errors https://<subdomain>/
```

Tell the user the result and: "Tail logs at https://platform.apoena.dev/project/$PROJECT_UUID/application/$APP_UUID."

Then hand back to the caller — skip Step 2.

## Step 2 — Print the checklist (fallback)

Reached only if Step 1 was skipped or any sub-step failed. Read `coolify-checklist.md` and substitute the placeholders, then print it to the user. Tell them: "Open https://platform.apoena.dev and paste these values into a new Application. I'll wait — let me know if any field is unclear."

</what-to-do>

<supporting-info>

## Coolify conventions on platform.apoena.dev

- Apps deploy from public Gitea repos. **The `applications/public` API truncates non-GitHub git URLs to `owner/repo`** — you must PATCH `git_repository` to the full `https://git.apoena.dev/julien/<app>.git` URL after create, or the first deploy fails at the git-clone step (see 1b).
- The "Dockerfile" build pack is used for SPA-only apps (single `Dockerfile` at the repo root).
- The "Docker Compose" build pack is used when `docker-compose.yml` exists.
- Domains are configured per-resource as `https://<subdomain>` — Coolify provisions Let's Encrypt automatically as long as the DNS A/AAAA record for `<subdomain>.apoena.dev` already points at the Coolify host.
- Persistent storage paths must match what the container writes to (e.g. `/app/data` for SQLite).

## DNS must already resolve

Whatever the domain, it must resolve to the Coolify host before Step 1 or Coolify's Let's Encrypt step fails.

- **`*.apoena.dev` subdomains** are covered by a wildcard — nothing to do. Sanity-check with `dig +short <subdomain>.apoena.dev` against `dig +short platform.apoena.dev` before deploying.
- **Custom marque domains** (separate apex, e.g. `typoena.app`) are provisioned by the **marque-dns** skill — run it first.

## Automation requirements

Step 1 runs only if `$COOLIFY_API_TOKEN` is set. Both `$COOLIFY_API_TOKEN` and `$TEA_TOKEN` (the Gitea PAT used for webhook creation in 1d) are exported from `~/.dotfiles/zsh/private.zsh`. Use the env vars directly — do **not** parse the tea config file or run a recursive filesystem `find` for a token (the sandbox blocks credential hunting). If `$TEA_TOKEN` is missing from the current shell, have the user `source ~/.dotfiles/zsh/private.zsh` (or open a new terminal) and re-run; if it stays unavailable, skip the webhook (1d) and hand off manual instructions. The Gitea webhook URL is the same for every Coolify app on this instance — `https://platform.apoena.dev/webhooks/source/gitea/events/manual` — and is hardcoded in the skill; Coolify matches the app by repo URL in the payload.

Cached state lives in `~/.config/apoena/coolify.env` — `PROJECT_UUID` and `SERVER_UUID` after the one-time discovery prompt.

If anything in Step 1 fails (missing token, API error, repo URL mismatch in Coolify), fall through to Step 2 — the manual checklist — and the user finishes in the Coolify UI.

## Files in this skill

- `coolify-checklist.md` — printable per-app checklist with `{{PLACEHOLDERS}}`.

</supporting-info>
