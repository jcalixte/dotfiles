---
name: marque-dns
description: Use when a custom apex domain bought via marque needs DNS pointed at a host — writes an `at.marque.dns` record into the apoena PDS, which marque's nameservers serve directly, so the putRecord is live DNS. Skip for `*.apoena.dev` subdomains (wildcard already covers them).
---

<what-to-do>

Run this **only** when the domain is not under `apoena.dev` (a separate apex bought via marque). `*.apoena.dev` is covered by a wildcard — skip. When bootstrapping an app, do this *before* scaffolding so DNS propagates while you work, not at deploy time.

marque is atproto-native: a domain's DNS lives as an `at.marque.dns` record in the apoena PDS (`https://eurosky.social`, repo `did:plc:4m3kouplb7s7xozjd3whinvl` = `apoena.dev`), and marque's nameservers (`stratus`/`cirrus.ns.marque.network`) serve it directly — a `putRecord` **is** live DNS. `$MARQUE_APP_PASSWORD` is exported from `~/.dotfiles/zsh/private.zsh` (source it if not loaded; never prompt inline).

```bash
DID=did:plc:4m3kouplb7s7xozjd3whinvl; PDS=https://eurosky.social; DOMAIN=<domain>
# 1) Domain must already be registered in marque (paid flow — the skill can't buy it). Grab its cid for the subject link.
DOMAIN_CID=$(curl -fsSL "$PDS/xrpc/com.atproto.repo.getRecord?repo=$DID&collection=at.marque.domain&rkey=$DOMAIN" | jq -r '.cid // empty')
[ -z "$DOMAIN_CID" ] && { echo "STOP: $DOMAIN not registered in marque — ask the user to buy it first"; exit 1; }
# 2) Point @/* (A) and www (CNAME→apex) at the Coolify host. Derive the IP — never hardcode it.
IP=$(dig +short platform.apoena.dev | head -1)
JWT=$(curl -sS -X POST "$PDS/xrpc/com.atproto.server.createSession" -H "Content-Type: application/json" \
  -d "$(jq -n --arg id "$DID" --arg pw "$MARQUE_APP_PASSWORD" '{identifier:$id,password:$pw}')" | jq -r '.accessJwt // empty')
REC=$(jq -n --arg d "$DOMAIN" --arg cid "$DOMAIN_CID" --arg did "$DID" --arg ip "$IP" --arg now "$(date -u +%Y-%m-%dT%H:%M:%SZ)" '{
  "$type":"at.marque.dns", domain:$d,
  records:[{ttl:3600,name:"@",value:$ip,recordType:"A"},
           {ttl:3600,name:"*",value:$ip,recordType:"A"},
           {ttl:3600,name:"www",value:$d,recordType:"CNAME"}],
  subject:{uri:("at://"+$did+"/at.marque.domain/"+$d), cid:$cid}, createdAt:$now}')
curl -fsSL -X POST "$PDS/xrpc/com.atproto.repo.putRecord" -H "Authorization: Bearer $JWT" -H "Content-Type: application/json" \
  -d "$(jq -n --arg did "$DID" --arg d "$DOMAIN" --argjson rec "$REC" '{repo:$did,collection:"at.marque.dns",rkey:$d,record:$rec,validate:false}')" | jq '{uri,error}'
# 3) Verify it's live on marque's NS (both should return the IP):
dig +short @stratus.ns.marque.network "$DOMAIN"; dig +short @stratus.ns.marque.network "www.$DOMAIN"
```

**`www` CNAME must target the apex hostname, never an IP** (a CNAME→IP is malformed). `putRecord` replaces on re-run, so it's idempotent.

**Tell the caller the `www` record exists.** Downstream, the Coolify app must register `https://<domain>,https://www.<domain>` — registering only the apex leaves `www.<domain>` resolving to a certless endpoint (Let's Encrypt never issues for `www`, TLS fails).

</what-to-do>

<supporting-info>

Whatever the domain, it must resolve to the target host before a Coolify app is created, or Coolify's Let's Encrypt step fails.

- **`*.apoena.dev` subdomains** are covered by a wildcard — nothing to do here. Sanity-check with `dig +short <subdomain>.apoena.dev` against `dig +short platform.apoena.dev` before deploying.
- **Custom marque domains** (separate apex, e.g. `typoena.app`) are what this skill provisions. The domain must already be registered in marque (`at.marque.domain/<domain>` record exists); the skill can't buy it.

</supporting-info>
