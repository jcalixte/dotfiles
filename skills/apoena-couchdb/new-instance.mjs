// Generates a CouchDB instance repo for one app from ./template.
// Usage: node new-instance.mjs <app> <db-host> <origins> <issuer-url> <out-dir>
// <origins>: exact browser origins, comma-separated; the first one is used by smoke.sh.
// Example: node new-instance.mjs bluebin db.bluebin.app \
//   https://bluebin.app,https://www.bluebin.app,http://localhost:5173 \
//   https://auth.bluebin.app/application/o/bluebin/ ~/projects/bluebin-couchdb
import { createPublicKey, randomBytes } from 'node:crypto'
import { execFileSync } from 'node:child_process'
import { cpSync, existsSync, readFileSync, readdirSync, statSync, writeFileSync } from 'node:fs'
import { dirname, join } from 'node:path'
import { fileURLToPath } from 'node:url'

const [app, dbHost, originList, issuerArg, out] = process.argv.slice(2)
if (!out) {
  console.error('Usage: node new-instance.mjs <app> <db-host> <origins> <issuer-url> <out-dir>')
  process.exit(1)
}
const fail = (message) => {
  console.error(`STOP: ${message}`)
  process.exit(1)
}
if (!/^[a-z0-9-]+$/.test(app)) fail(`app "${app}" must be kebab-case`)
if (existsSync(out)) fail(`${out} already exists`)
if (!/^[a-z0-9.-]+$/.test(dbHost)) fail(`db-host "${dbHost}" must be a bare host name`)
const origins = originList.split(',').map((origin) => origin.trim())
for (const origin of origins)
  if (!/^https?:\/\/[a-z0-9.-]+(:\d+)?$/.test(origin))
    fail(`origin "${origin}" must be exact: scheme://host[:port], no path or trailing slash`)
// Traefik regex: dots escaped as [.] (a `\` would need YAML escaping), anchored by the template.
const originsRegex = origins.map((origin) => origin.replace(/\./g, '[.]')).join('|')

// The issuer must be the one Authentik writes in its tokens, trailing slash included.
const issuerUrl = issuerArg.endsWith('/') ? issuerArg : `${issuerArg}/`
const discovery = await fetch(`${issuerUrl}.well-known/openid-configuration`)
if (!discovery.ok) fail(`no OIDC provider at ${issuerUrl} (HTTP ${discovery.status})`)
const { issuer, jwks_uri: jwksUri } = await discovery.json()
const { keys = [] } = await (await fetch(jwksUri)).json()
const rsaKeys = keys.filter((key) => key.kty === 'RSA')
if (rsaKeys.length === 0)
  fail(`${jwksUri} has no RSA key: set a Signing Key on the Authentik provider first`)
const jwtKeys = rsaKeys
  .map((jwk) => {
    const pem = createPublicKey({ key: jwk, format: 'jwk' }).export({ type: 'spki', format: 'pem' })
    return `rsa:${jwk.kid} = ${pem.trim().replace(/\n/g, '\\n')}`
  })
  .join('\n')

const fauxtonPassword = randomBytes(16).toString('hex')
const fauxtonHash = execFileSync('pnpm', ['--silent', 'dlx', 'bcryptjs@3', fauxtonPassword], {
  encoding: 'utf8',
}).trim().split('\n')[0]
if (!/^\$2[aby]\$\d\d\$.{53}$/.test(fauxtonHash)) fail(`unexpected bcrypt output: ${fauxtonHash}`)

const values = {
  APP: app,
  DB_HOST: dbHost,
  ORIGINS: originsRegex,
  ISS: issuer,
  JWT_KEYS: jwtKeys,
  FAUXTON_HASH: fauxtonHash,
  SMOKE_ORIGIN: origins[0],
}

const template = join(dirname(fileURLToPath(import.meta.url)), 'template')
cpSync(template, out, { recursive: true })
const walk = (dir) =>
  readdirSync(dir).flatMap((name) => {
    const path = join(dir, name)
    return statSync(path).isDirectory() ? walk(path) : [path]
  })
for (const path of walk(out)) {
  const text = readFileSync(path, 'utf8')
  // A function replacement: `$` in values (bcrypt hash, regex) stays literal.
  const filled = text.replace(/\{\{([A-Z_]+)\}\}/g, (match, key) => {
    if (!(key in values)) fail(`unknown placeholder ${match} in ${path}`)
    return values[key]
  })
  writeFileSync(path, filled)
}

const secret = () => randomBytes(16).toString('hex')
writeFileSync(
  join(out, '.env'),
  `COUCHDB_USER=admin\nCOUCHDB_PASSWORD=${secret()}\nCOUCHDB_ERLANG_COOKIE=${secret()}\nCOUCHDB_PORT=5984\n` +
    `# Deployed Fauxton basic-auth password: copy to the Coolify env var FAUXTON_PASSWORD.\nFAUXTON_PASSWORD=${fauxtonPassword}\n`,
  { mode: 0o600 },
)
console.log(`Generated ${out} for ${app} (issuer ${issuer}, ${rsaKeys.length} key(s)).`)
console.log('Fauxton password written to .env (FAUXTON_PASSWORD), not printed.')
