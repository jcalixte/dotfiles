# Coolify deploy checklist — {{APP_NAME}}

Open https://platform.apoena.dev and create a new Application with these values.

## 1. DNS (do this first, outside Coolify)

Verify `{{SUBDOMAIN}}` already resolves to the Coolify host:

```bash
dig +short {{SUBDOMAIN}}
```

If empty, add an A/CNAME record before continuing — Let's Encrypt issuance will fail otherwise. If the wildcard `*.apoena.dev` is already in place, you're covered.

## 2. New resource

- **Project**: existing project, or create one named `{{APP_NAME}}`.
- **Resource type**: Application → **Public Repository**.
- **Repository URL**: `https://git.apoena.dev/julien/{{APP_NAME}}`
- **Branch**: `main`
- **Build pack**: `{{BUILD_PACK}}`  *(Dockerfile for SPA-only, Docker Compose if `docker-compose.yml` is present)*

## 3. Network

- **Ports exposed**: `{{PORTS}}`  *(`80` for SPA, or your compose-published ports)*
- **Domains**: `https://{{SUBDOMAIN}}`  *(Coolify provisions Let's Encrypt automatically)*

## 4. Persistent storage *(only if SQLite was selected)*

- **Source**: `{{APP_NAME}}-data`  *(Coolify-managed named volume)*
- **Destination**: `/app/data`
- **Mount on**: the `api` service

## 5. Environment variables

| Key | Value | Notes |
|---|---|---|
| *(none required by default)* | | Add app-specific secrets here |

## 6. Deploy

Click **Deploy**. First build pulls images and may take 2–5 min. Subsequent pushes to `main` trigger automatic rebuilds.

## 7. Verify

```bash
curl -I https://{{SUBDOMAIN}}
# expect: HTTP/2 200
```

If 502/504: check the Coolify container logs — usually port mismatch or missing env var.
