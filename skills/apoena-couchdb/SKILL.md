---
name: apoena-couchdb
description: Use when an app on platform.apoena.dev needs its own CouchDB server (PouchDB sync, offline-first data, a db.<domain> host) — or when someone proposes putting a second app on an existing CouchDB instance. Covers Traefik router names that collide across Coolify stacks, the Authentik issuer and keys CouchDB pins, the Fauxton basic-auth hash, the Coolify compose quirks, and the 400-not-401 answers CouchDB gives for bad JWTs.
---

<what-to-do>

## Rule: one CouchDB instance per app

Do not add a second app to an existing instance. The admin account, `[jwt_auth] required_claims` (one issuer), `[jwt_keys]` and the CORS origins are server-wide. A shared instance lets one app's backend (which holds the admin login) read the other app's data, and the second app's tokens would need the first app's issuer.

A new **database** inside the app's own instance needs no skill: something with the admin login does `PUT /<db>` and `PUT /<db>/_security`. Browser tokens cannot create databases (`default_security = admin_only`).

## Inputs

| Value | Example | Notes |
| --- | --- | --- |
| `APP` | `bluebin` | kebab-case. Repo and Coolify app: `<APP>-couchdb` |
| `DB_HOST` | `db.bluebin.app` | `db.<domain>` for a custom domain, `<APP>-db.apoena.dev` for an `*.apoena.dev` app |
| `ORIGINS` | see below | every origin that serves the SPA, plus the dev server |
| `AUTH_HOST`, `SLUG` | `auth.bluebin.app`, `bluebin` | the Authentik host the app logs in on, and its OIDC provider slug |

`ORIGINS` is a regex body, alternatives separated by a plain pipe, dots written `[.]`:

```bash
ORIGINS='https://(www[.])?bluebin[.]app|http://localhost:5173'
```

The Coolify steps need `$COOLIFY_API_TOKEN` (exported from `~/.dotfiles/zsh/private.zsh`). Without it, stop after Step 4 and hand the user the Step 5 values.

## Step 0 — Preconditions (stop if one fails)

```bash
[ "$(dig +short "$DB_HOST" | head -1)" = "$(dig +short platform.apoena.dev | head -1)" ] || echo "STOP: DNS"
ISS=$(curl -fsS "https://$AUTH_HOST/application/o/$SLUG/.well-known/openid-configuration" | jq -r .issuer)
curl -fsS "https://$AUTH_HOST/application/o/$SLUG/jwks/" | jq -e '[.keys[]? | select(.kty=="RSA")] | length > 0'   # must print true
```

- DNS fails on a custom domain → run the **marque-dns** skill (its zone has a `*` record that covers `db.`).
- No provider (404 on openid-configuration) → the app needs an Authentik OIDC provider first. There is no Authentik API token: the user imports a blueprint in the Authentik UI (Flows and Stages > Flows > Import). Do not continue without it.
- JWKS is `{}` (the `jq -e` prints `false`) and openid-configuration lists only `HS256` → the provider has no signing key, so it signs with the client secret and CouchDB cannot verify it. Ask the user to set **Signing Key** on the provider in the Authentik UI (Applications > Providers > edit, an RSA certificate such as the default self-signed one), then re-run Step 0. In a blueprint this is `signing_key` on the provider.
- `ISS` is exact, trailing slash included. Authentik puts the request host in it, so the app must always log in on `AUTH_HOST`.

## Step 1 — Copy the template

The template is the Vaquant instance, `julien/couchdb` (public). Clone it fresh, files only. Do not copy `~/projects/couchdb`: that is the live Vaquant checkout and may hold uncommitted work.

```bash
git clone --depth 1 https://git.apoena.dev/julien/couchdb.git ~/projects/$APP-couchdb
cd ~/projects/$APP-couchdb && rm -rf .git .env
```

## Step 2 — Make it the app's instance

| File | Change |
| --- | --- |
| `docker-compose.coolify.yml` | Prefix every Traefik router, middleware and service name (see below) |
| `docker-compose.coolify.yml` | Both `rule=` labels: replace the `Host(...)` part with `Host(\`$DB_HOST\`)` and drop the Vaquant hosts. The Fauxton rule keeps `&& PathPrefix(\`/_utils\`)` |
| `docker-compose.coolify.yml` | `accesscontrolalloworiginlistregex=^($ORIGINS)$`. Keep `^` and `$`: without them `https://bluebin.app.evil.com` passes |
| `docker-compose.coolify.yml` | `basicauth.users=fauxton:<new hash>` (Step 3) |
| `config/local.ini` | `required_claims = exp, {iss, "$ISS"}` |
| `config/local.ini` | Replace every `rsa:` line under `[jwt_keys]` with the output of `node scripts/jwt-keys.mjs https://$AUTH_HOST/application/o/$SLUG/jwks/` |
| `config/local.ini` | Delete `roles_claim_path` unless the provider adds a `couchdb_roles` claim |
| `README.md`, comments | First paragraph: "The CouchDB of <App>, at `https://$DB_HOST`". Replace Vaquant names, hosts and origins |
| `scripts/smoke.sh` | The allowed-origin CORS check (3 lines, `https://vaquant.at`): use one of the app's origins. Nothing else in the script is app-specific |

**Traefik names are global.** Every compose stack on the server shares one Traefik. Two stacks that both define `couchdb-api` or `couchdb-cors` overwrite each other, and the other app's CouchDB loses its CORS or its Fauxton login. Prefix them:

```bash
# also renames couchdb-fauxton-auth: \b matches between "fauxton" and "-auth"
sed -i "s/\bcouchdb-\(api\|fauxton\|cors\|svc\)\b/$APP-couchdb-\1/g" docker-compose.coolify.yml
grep -o 'traefik\.http\.[a-z]*\.[a-z0-9-]*' docker-compose.coolify.yml | sort -u   # every name starts with $APP-couchdb-
grep -rniE 'vaquant|apoena\.dev' --exclude-dir=.git .                              # only hits you meant to keep
```

## Step 3 — Fauxton password

```bash
FAUXTON_PASSWORD=$(openssl rand -hex 16)
pnpm --silent dlx bcryptjs@3 "$FAUXTON_PASSWORD"   # prints $2b$10$...
```

Paste the hash in the label with single `$` signs. Coolify escapes every `$` in labels, so a `${VAR}` there reaches Traefik as literal text. The hash is public in the repo, which is safe only because the password is 32 random hex characters. Keep `FAUXTON_PASSWORD` for Step 5. No Docker daemon is needed (`htpasswd` via `docker run` fails in the container).

## Step 4 — Repo

Commit (`feat: CouchDB instance for <APP>`) and run the **apoena-gitea-repo** skill for `<APP>-couchdb`. Public is fine: the repo holds no secret (`.env` is ignored, admin password comes from Coolify, JWT keys are public keys).

## Step 5 — Coolify

Run the **apoena-coolify-deploy** skill for `<APP>-couchdb` with these values:

- `build_pack: "dockercompose"`, `ports_exposes: "5984"`
- PATCH `docker_compose_location: "/docker-compose.coolify.yml"`
- `docker_compose_domains: [{name:"couchdb", domain:"https://$DB_HOST"}]` (the compose service is `couchdb`)

Before the first deploy, check that Coolify generated the admin secrets:

```bash
curl -fsS -H "Authorization: Bearer $COOLIFY_API_TOKEN" https://platform.apoena.dev/api/v1/applications/$APP_UUID/envs \
  | jq -r '.[].key' | grep -E '^SERVICE_(USER|PASSWORD)_COUCHDB$'
```

If they are missing, Coolify has not parsed the compose file yet: ask the user to click **Reload Compose** on the app in the Coolify UI (no API endpoint does it), then set `docker_compose_domains` again and re-check. A deploy without them crash-loops (CouchDB 3 refuses to start without an admin).

Add `FAUXTON_PASSWORD` as an env var (reference only, nothing reads it), then deploy.

## Step 6 — Verify

Read the admin login from the envs (`real_value` of `SERVICE_USER_COUCHDB` / `SERVICE_PASSWORD_COUCHDB`, production row) into variables; never print them. Tell the user you used the admin login.

```bash
COUCHDB_USER=… COUCHDB_PASSWORD=… FAUXTON_PASSWORD=… ./scripts/smoke.sh https://$DB_HOST   # ends "All checks passed"
curl -s -w ' %{http_code}\n' -H 'Authorization: Bearer abc.def.ghi' https://$DB_HOST/_session   # 400 Malformed authentication token
```

Then check that every **other** CouchDB instance still answers its CORS preflight with its own origin (a Traefik name collision breaks them, not the new one). List them, then send each a preflight from one of its app's origins:

```bash
curl -fsS -H "Authorization: Bearer $COOLIFY_API_TOKEN" https://platform.apoena.dev/api/v1/applications \
  | jq -r '.[] | select(.name | test("couchdb")) | "\(.name) \(.docker_compose_domains)"'
curl -s -o /dev/null -D - -X OPTIONS -H 'Origin: https://vaquant.at' -H 'Access-Control-Request-Method: GET' \
  https://db.vaquant.at/_session | grep -i '^access-control-allow-origin'   # Vaquant's instance (app "couchdb")
```

## Step 7 — Wire the app

- SPA build env: the CouchDB URL (for example `VITE_COUCHDB=https://$DB_HOST`), in the repo `.env` and in the Coolify envs (production and preview).
- `connect-src` of the app's Content-Security-Policy: add `https://$DB_HOST`.
- The component that creates databases and writes `_security` (`{"members":{"names":["<sub>"]}}`, `sub` = Authentik user uuid) gets the admin login as env vars. The browser never gets it.
- No app prefix on database names: the instance serves one app.
- The app's OIDC client must always use `AUTH_HOST`: a token from another host of the shared Authentik has another `iss` and gets 400 `Invalid iss claim`.

</what-to-do>

<supporting-info>

## CouchDB answers to read correctly

| Request | Answer | Meaning |
| --- | --- | --- |
| `GET /_session`, no token | 200, `userCtx.name: null`, handlers `["jwt","cookie","default"]` | JWT handler is on |
| Bearer token that is not a JWT | 400 `Malformed authentication token` | normal for garbage |
| Bearer token from another issuer | 400 `Invalid iss claim` | `required_claims` works; or `ISS` is wrong |
| Bad signature, unknown `kid` | 400 | Authentik rotated its key: re-run `jwt-keys.mjs`, push |
| Expired token | 401 | the only JWT error that is 401 |
| `GET /_all_dbs` anonymous | 401 | `admin_only_all_dbs` works |

A 400 is never a CORS or network problem. Do not loosen CORS to fix it.

## DevTools noise that is normal

A `_changes?feed=longpoll&heartbeat=…` request shows `JSON.parse: unexpected end of data` in the Firefox response preview while it is open: CouchDB has sent `{"results":[` plus heartbeat newlines. 304 on `_local/…` are PouchDB checkpoints.

## Moving an app's CouchDB URL

PouchDB checkpoints are per remote URL, so a new URL means a slower first sync, no data loss. Installed PWAs keep the old build: serve both hosts from the same instance (two `Host()` in each rule, both domains in Coolify, both in the app's `connect-src`) until clients have updated, then drop the old host.

## Common mistakes

| Mistake | Effect |
| --- | --- |
| Template Traefik names kept | Another app's CouchDB loses CORS or Fauxton login after this deploy |
| `ISS` typed by hand | Every request: 400 `Invalid iss claim` |
| `ports: 5984` in compose | Database exposed on the host, bypassing Traefik. Keep `expose:` |
| Bind-mounted `local.ini` | Coolify mounts an empty directory; the Dockerfile copies it instead |
| Bind mount for data | `eacces`: the image runs as uid 5984. Keep the named volume |

</supporting-info>
