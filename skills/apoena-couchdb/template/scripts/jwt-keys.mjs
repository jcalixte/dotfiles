// Prints `[jwt_keys]` lines for config/local.ini from an OIDC JWKS URL.
// Usage: node scripts/jwt-keys.mjs https://auth.example.com/application/o/<slug>/jwks/
import { createPublicKey } from 'node:crypto'

const url = process.argv[2]
if (!url) {
  console.error('Usage: node scripts/jwt-keys.mjs <jwks-url>')
  process.exit(1)
}

const { keys } = await (await fetch(url)).json()
for (const jwk of keys.filter((key) => key.kty === 'RSA')) {
  const pem = createPublicKey({ key: jwk, format: 'jwk' }).export({ type: 'spki', format: 'pem' })
  console.log(`rsa:${jwk.kid} = ${pem.trim().replace(/\n/g, '\\n')}`)
}
