# {{APP}}-couchdb

The CouchDB of {{APP}}, at `https://{{DB_HOST}}`. No other app uses this instance: the admin
account, the JWT issuer and the CORS origins are server-wide, so each app gets its own.
Generated from the `apoena-couchdb` skill template.

## Local

```bash
cp .env.example .env     # set the passwords
make up                  # docker compose up -d --build
make smoke               # scripts/smoke.sh against http://127.0.0.1:5984
```

Fauxton: http://127.0.0.1:5984/_utils, with the user and password from `.env`.

## What the setup does

- Builds from `couchdb:3.5.3` (pinned) and copies `config/local.ini` into the image. A config
  change needs a redeploy (a push to `main` does it).
- `single_node = true`: creates `_users` and `_replicator`. Without it CouchDB stays in
  "setup needed" and many endpoints answer 500.
- Data is admin-only by default (`default_security = admin_only`, `admin_only_all_dbs`).
  Browser users get access through the `_security` of each database.
- Data lives in the named volume `couchdb-data`. The image runs as uid 5984, so a bind
  mount to a root-owned host directory fails.

## Deployed instance

Coolify, Docker Compose build pack, compose file `docker-compose.coolify.yml`. The admin
login is in the Coolify env vars `SERVICE_USER_COUCHDB` / `SERVICE_PASSWORD_COUCHDB`.

```bash
COUCHDB_USER=... COUCHDB_PASSWORD=... FAUXTON_PASSWORD=... ./scripts/smoke.sh https://{{DB_HOST}}
```

### Fauxton

Traefik asks for a basic-auth login (user `fauxton`, password in the Coolify env var
`FAUXTON_PASSWORD`) before it serves `/_utils`, then Fauxton asks for the CouchDB admin.
The bcrypt hash is written in the `basicauth.users` label: Coolify escapes every `$` in
labels, so a `${VAR}` there would reach Traefik as literal text. The hash is public, which
is safe only because the password is 32 random characters. To change it:

```bash
PW=$(openssl rand -hex 16); pnpm --silent dlx bcryptjs@3 "$PW"
```

Put the hash in the label (single `$` signs) and the password in `FAUXTON_PASSWORD`, push.

### CORS

Traefik answers CORS, not CouchDB. Allowed origins: the `accesscontrolalloworiginlistregex`
label. Keep the `^` and `$` anchors, or an origin that only contains a match passes.

### JWT (Authentik)

Browser apps send their Authentik access token as `Authorization: Bearer`. CouchDB checks
the signature with `[jwt_keys]`, the `iss` in `required_claims`, and takes the user name
from `sub`. It does not fetch JWKS: when Authentik changes its signing key, sync fails with
400, then:

```sh
node scripts/jwt-keys.mjs {{ISS}}jwks/
```

Paste the output under `[jwt_keys]` and push. CouchDB answers 400 (not 401) for a bad
signature, a malformed token or a wrong issuer; 401 only for an expired token.

## Backup

```bash
docker compose exec -T couchdb bash -c 'tar -C /opt/couchdb -cf - data' > couchdb-backup.tar
```
