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
| `ORIGINS` | `https://bluebin.app,https://www.bluebin.app,http://localhost:5173` | exact origins that serve the SPA, plus the dev server, comma-separated. The first one is the one `smoke.sh` tests |
| `ISS` | `https://auth.bluebin.app/application/o/bluebin/` | the app's **own** Authentik provider: `https://<auth host>/application/o/<provider slug>/`. Another app's provider makes the two apps' tokens valid on both instances |

The Coolify steps need `$COOLIFY_API_TOKEN` (exported from `~/.dotfiles/zsh/private.zsh`). Without it, stop after Step 3 and hand the user the Step 4 values.

## Step 1 — DNS

```bash
[ "$(dig +short "$DB_HOST" | head -1)" = "$(dig +short platform.apoena.dev | head -1)" ] || echo "STOP: DNS"
```

Fails on a custom domain → run the **marque-dns** skill (its zone has a `*` record that covers `db.`).

## Step 2 — Generate the repo from the template

`template/` in this skill is a complete instance repo with `{{PLACEHOLDERS}}`. `new-instance.mjs` fills them, so do not edit the generated files by hand:

```bash
node ~/.claude/skills/apoena-couchdb/new-instance.mjs "$APP" "$DB_HOST" "$ORIGINS" "$ISS" ~/projects/$APP-couchdb
```

It reads the issuer and the RSA keys from the provider, builds the anchored CORS regex, prefixes every Traefik name with `<APP>-couchdb-` (all stacks share one Traefik: a name used twice overwrites the other app's CORS or Fauxton login), hashes a new Fauxton password with `bcryptjs`, and writes `.env` (mode 600, git-ignored) with local passwords and `FAUXTON_PASSWORD`. It never prints a secret.

It stops (`STOP: …`, exit 1, nothing written) when:

| Message | Fix |
| --- | --- |
| `no OIDC provider at …` (404) | The app needs an Authentik OIDC provider. No Authentik API token exists: the user imports a blueprint in the Authentik UI (Flows and Stages > Flows > Import) |
| `… has no RSA key` | The provider signs with HS256 (client secret), CouchDB cannot verify that. The user sets **Signing Key** on the provider (Applications > Providers > edit, an RSA certificate such as the default self-signed one). Blueprint: `signing_key`. It applies to new tokens at once; logged-in users get an RSA token at their next refresh |
| `origin "…" must be exact` | Give `scheme://host[:port]` only: no path, no trailing slash, no regex |
| `… already exists` | Pick another output dir; the script never overwrites |

The app's OIDC client must always use the auth host in `ISS`: a token from another host of the shared Authentik has another `iss` and gets 400 `Invalid iss claim`.

To change the template itself (a CouchDB upgrade, a new label), edit `template/` and run it with Vaquant's values (`vaquant db.vaquant.at https://vaquant.at,https://vaquant.space,http://localhost:8080 https://auth.vaquant.at/application/o/vaquant/`) into `/tmp` and diff with `julien/couchdb`. Expected differences only: the prefixed Traefik names, the CORS regex written as a flat list, the old `couchdb.apoena.dev` host, and `roles_claim_path` (Vaquant still has it). Running instances do not follow the template; port a change to each repo.

## Step 3 — Repo

```bash
cd ~/projects/$APP-couchdb && git init -b main && git add -A && git commit -m "feat: CouchDB instance for $APP"
```

Then run the **apoena-gitea-repo** skill for `<APP>-couchdb`. Public is fine: the repo holds no secret (`.env` is ignored, the admin password comes from Coolify, `[jwt_keys]` are public keys, the Fauxton hash is of a 32-character random password).

## Step 4 — Coolify

Run the **apoena-coolify-deploy** skill for `<APP>-couchdb` with these values:

- `build_pack: "dockercompose"`, `ports_exposes: "5984"`
- PATCH `docker_compose_location: "/docker-compose.coolify.yml"`
- `docker_compose_domains: [{name:"couchdb", domain:"https://$DB_HOST"}]` (the compose service is `couchdb`)

Before the first deploy, check that Coolify generated the admin secrets:

```bash
curl -fsS -H "Authorization: Bearer $COOLIFY_API_TOKEN" https://platform.apoena.dev/api/v1/applications/$APP_UUID/envs \
  | jq -r '.[].key' | sort -u | grep -E '^SERVICE_(USER_COUCHDB|PASSWORD_COUCHDB|PASSWORD_COUCHDBCOOKIE)$'   # 3 lines
```

If they are missing, Coolify has not parsed the compose file yet: ask the user to click **Reload Compose** on the app in the Coolify UI (no API endpoint does it), then set `docker_compose_domains` again and re-check. A deploy without them crash-loops (CouchDB 3 refuses to start without an admin).

Add `FAUXTON_PASSWORD` from the generated `.env` as an env var (reference only, nothing reads it), then deploy:

```bash
FP=$(grep '^FAUXTON_PASSWORD=' ~/projects/$APP-couchdb/.env | cut -d= -f2)
curl -fsS -X POST -H "Authorization: Bearer $COOLIFY_API_TOKEN" -H "Content-Type: application/json" \
  https://platform.apoena.dev/api/v1/applications/$APP_UUID/envs -d "$(jq -n --arg v "$FP" '{key:"FAUXTON_PASSWORD", value:$v}')" >/dev/null
```

## Step 5 — Verify

Read the admin login from the envs (`real_value` of `SERVICE_USER_COUCHDB` / `SERVICE_PASSWORD_COUCHDB`, production row) into variables; never print them. Tell the user you used the admin login.

```bash
cd ~/projects/$APP-couchdb
COUCHDB_USER=… COUCHDB_PASSWORD=… FAUXTON_PASSWORD=… bash scripts/smoke.sh https://$DB_HOST   # ends "All checks passed"
curl -s -w ' %{http_code}\n' -H 'Authorization: Bearer abc.def.ghi' https://$DB_HOST/_session   # 400 Malformed authentication token
```

Then check that every **other** CouchDB instance still answers its CORS preflight with its own origin (a Traefik name collision breaks them, not the new one). List them, then send each a preflight from one of its app's origins:

```bash
curl -fsS -H "Authorization: Bearer $COOLIFY_API_TOKEN" https://platform.apoena.dev/api/v1/applications \
  | jq -r '.[] | select(.name | test("couchdb")) | "\(.name) \(.docker_compose_domains)"'
curl -s -o /dev/null -D - -X OPTIONS -H 'Origin: https://vaquant.at' -H 'Access-Control-Request-Method: GET' \
  https://db.vaquant.at/_session | grep -i '^access-control-allow-origin'   # Vaquant's instance (app "couchdb")
```

## Step 6 — Wire the app

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
| Generated files edited by hand to rename or re-host | Traefik names or hosts drift; regenerate instead |
| `ports: 5984` in compose | Database exposed on the host, bypassing Traefik. Keep `expose:` |
| Bind-mounted `local.ini` | Coolify mounts an empty directory; the Dockerfile copies it instead |
| Bind mount for data | `eacces`: the image runs as uid 5984. Keep the named volume |

</supporting-info>
