#!/usr/bin/env bash
# Proves the instance works: up, authenticated, system databases present, read/write OK,
# anonymous access refused. On an https URL it also checks Fauxton basic auth and CORS.
# Usage: scripts/smoke.sh [base-url]   (defaults to the local compose instance)
set -euo pipefail

cd "$(dirname "$0")/.."
# Credentials given on the command line win over .env.
if [ -z "${COUCHDB_PASSWORD:-}" ] && [ -f .env ]; then set -a; . ./.env; set +a; fi

BASE="${1:-http://127.0.0.1:${COUCHDB_PORT:-5984}}"
AUTH="${COUCHDB_USER:?}:${COUCHDB_PASSWORD:?}"
DB="smoke-$$"

say() { printf '\n== %s\n' "$1"; }
cleanup_and_fail() { curl -fsS -u "$AUTH" -X DELETE "$BASE/$DB" >/dev/null 2>&1 || true; exit 1; }
req() { curl -fsS -u "$AUTH" "$@"; }

say "waiting for $BASE/_up"
for i in $(seq 1 30); do
  curl -fsS "$BASE/_up" >/dev/null 2>&1 && break
  [ "$i" = 30 ] && { echo "CouchDB did not come up"; exit 1; }
  sleep 2
done
curl -fsS "$BASE/_up"; echo

say "version"
req "$BASE/" | grep -o '"version":"[^"]*"'

say "anonymous access must be refused"
code=$(curl -s -o /dev/null -w '%{http_code}' "$BASE/_all_dbs")
[ "$code" = 401 ] || { echo "expected 401 without credentials, got $code"; exit 1; }
echo "401 OK"

say "system databases"
req "$BASE/_all_dbs"; echo
for d in _users _replicator; do
  req -o /dev/null "$BASE/$d"
  echo "$d present"
done

say "write and read a document"
req -X PUT "$BASE/$DB" >/dev/null
req -X PUT -H 'Content-Type: application/json' -d '{"hello":"couch"}' "$BASE/$DB/doc1" >/dev/null
req "$BASE/$DB/doc1" | grep -q '"hello":"couch"'
echo "document round-trip OK"
code=$(curl -s -o /dev/null -w '%{http_code}' "$BASE/$DB/doc1")
[ "$code" = 401 ] || { echo "anonymous read of a new database: expected 401, got $code"; cleanup_and_fail; }
echo "anonymous read refused (401) OK"

# Proxy checks: only meaningful on the Coolify deployment (Traefik in front).
case "$BASE" in https://*)
  say "Fauxton basic auth"
  code=$(curl -s -o /dev/null -w '%{http_code}' "$BASE/_utils/")
  [ "$code" = 401 ] || { echo "/_utils without proxy login: expected 401, got $code"; cleanup_and_fail; }
  echo "/_utils without login: 401 OK"
  if [ -n "${FAUXTON_PASSWORD:-}" ]; then
    code=$(curl -s -o /dev/null -w '%{http_code}' -u "${FAUXTON_USER:-fauxton}:$FAUXTON_PASSWORD" "$BASE/_utils/")
    [ "$code" = 200 ] || { echo "/_utils with proxy login: expected 200, got $code"; cleanup_and_fail; }
    echo "/_utils with login: 200 OK"
  fi

  say "CORS"
  preflight() { curl -s -o /dev/null -D - -X OPTIONS -H "Origin: $1" -H 'Access-Control-Request-Method: GET' "$BASE/$DB" | tr -d '\r' | tr 'A-Z' 'a-z' | grep '^access-control-allow-origin:' || true; }
  [ "$(preflight {{SMOKE_ORIGIN}})" = "access-control-allow-origin: {{SMOKE_ORIGIN}}" ] \
    || { echo "preflight from {{SMOKE_ORIGIN}} not allowed"; cleanup_and_fail; }
  echo "{{SMOKE_ORIGIN}} allowed"
  [ -z "$(preflight https://evil.example.com)" ] || { echo "preflight from https://evil.example.com was allowed"; cleanup_and_fail; }
  echo "https://evil.example.com refused"
  ;;
esac

say "cleanup"
req -X DELETE "$BASE/$DB" >/dev/null && echo "dropped $DB"

printf '\nAll checks passed. Fauxton: %s/_utils\n' "$BASE"
