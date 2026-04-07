---
name: dashpass
description: >
  Encrypted credential vault on Dash Platform for AI agents.
  Store and retrieve API keys, tokens, and passwords — encrypted on-chain, decryptable only by you.
  Triggers on: credential management, password vault, API key storage, secret store, Dash Platform credentials.
requires:
  env:
    - CRITICAL_WIF
    - DASHPASS_IDENTITY_ID
  bins:
    - node
  packages:
    - "@dashevo/evo-sdk@3.1.0-dev.1"
---

# DashPass — Encrypted Credential Vault on Dash Platform

## 1. What is DashPass

DashPass lets you store API keys, passwords, and other secrets **encrypted on the Dash blockchain**. Only someone with your private key can decrypt them — not the blockchain nodes, not your AI agent, not anyone else. Think of it as a password manager where the "cloud" is a decentralized blockchain instead of a company's server.

Your AI agent (like Claude Code) can store and retrieve credentials programmatically through a command-line tool. The credentials are encrypted on your machine *before* they touch the network, and decrypted on your machine *after* they come back. The blockchain only ever sees ciphertext.

DashPass is designed for **AI agents that need secrets** (API keys, tokens, database passwords) without putting those secrets in plain-text config files.

---

## 2. Why DashPass Instead of a `.env` File

| | `.env` file | DashPass |
|---|---|---|
| **Where secrets live** | A plain-text file on one machine | Encrypted on a decentralized blockchain (thousands of nodes) |
| **What happens if your disk dies** | Secrets are gone (unless you have backups) | Secrets survive — they're on the blockchain, recoverable with your key |
| **Encryption** | None (plain text) | AES-256-GCM (military-grade, per-credential encryption) |
| **Rotation tracking** | Manual — overwrite the old value | Built-in version history with rotation chain |
| **Expiry alerts** | None | `check --expiring-within 7d` warns you before tokens expire |
| **Audit trail** | None | On-chain timestamps and version tracking |
| **Multi-machine access** | Copy the file around (risky) | Any machine with your key can fetch from the blockchain |
| **If someone gets your `.env`** | They see everything in plain text | They'd need your private key to decrypt anything |

**Bottom line:** `.env` files are convenient but fragile and insecure. DashPass adds encryption, redundancy, and lifecycle management.

---

## 3. Prerequisites Checklist

Before you can use DashPass, you need the following. Check each item off as you go:

### 3.1 Node.js 18 or newer

```bash
node --version
# Should print v18.x.x or higher
```

If you don't have Node.js, install it from [nodejs.org](https://nodejs.org/) or use `nvm`:

```bash
nvm install 18
nvm use 18
```

### 3.2 Install the Dash Platform SDK

DashPass uses the Dash Evo SDK to talk to the Dash blockchain. Install the specific version:

```bash
npm install @dashevo/evo-sdk@3.1.0-dev.1
```

> **Why this exact version?** DashPass requires the `3.1.0-dev.1` development release of the Evo SDK. The stable release has a different API surface that is not compatible. Using the wrong version will cause import errors or silent failures.

### 3.3 A Dash Testnet Wallet with tDASH

You need a small amount of testnet DASH (tDASH) to pay for blockchain operations. Testnet DASH is free — it has no real-world value.

**Get testnet DASH from the faucet:**

1. Visit: **https://testnet-faucet.dash.org/**
2. Enter your testnet wallet address
3. Receive free tDASH (you only need ~0.01 tDASH to get started)

> **What is a "wallet address"?** It's a string like `yXf7j8Vk...` that identifies where to send DASH. If you don't have a wallet yet, you'll create one as part of the Identity setup in Step 4.

### 3.4 A Dash Platform Identity

A **Platform Identity** is your on-chain identity on the Dash network. It's like a blockchain account — you need one to read and write data on Dash Platform.

Creating an Identity involves:
1. Having a funded Dash testnet wallet
2. Registering the Identity on-chain (costs a small fee)
3. Getting back an **Identity ID** — a base58 string like `36SxvpAKXeBJByUdJ364Hnhp2NfVDe6Gkj7xtTRZj6hh`

See the [Dash Platform Identity tutorial](https://docs.dash.org/en/stable/docs/tutorials/identities-and-names.html) for step-by-step instructions.

> **What is "base58"?** It's an encoding format used in cryptocurrency — looks like a mix of letters and numbers without confusing characters (no `0`, `O`, `I`, `l`). You don't need to understand it — just copy-paste the ID string.

### 3.5 Platform Credits

**Credits** are the "gas" that pays for writing data to Dash Platform. You get credits by converting tDASH to credits via a "top-up" transaction.

```bash
# Top up credits using the Dash SDK
# See: https://docs.dash.org/en/stable/docs/tutorials/identities-and-names.html#top-up-an-identity
```

The `status` command (shown later) tells you your current credit balance.

> **How many credits do I need?** Each credential storage operation costs roughly 0.0001 DASH worth of credits. 0.01 DASH worth of credits is enough for hundreds of operations.

### 3.6 Environment Variables Set

You need two environment variables configured before running DashPass:

```bash
export CRITICAL_WIF="your-testnet-WIF-private-key"
export DASHPASS_IDENTITY_ID="your-platform-identity-id"
```

> **What is a WIF?** WIF stands for **Wallet Import Format**. It's a way to represent a private key as a human-readable string starting with `c` (testnet) or `5`/`K`/`L` (mainnet). Example: `cYOUR_TESTNET_WIF_HERE_DO_NOT_USE_THIS_EXAMPLE`. This key is what encrypts and decrypts your credentials. **Never share it. Never commit it to git. Never paste it in chat.**

---

## 4. Getting Started — Step by Step

This walkthrough takes you from zero to your first stored-and-retrieved credential.

### Step 1: Locate the DashPass CLI

The CLI script is at:

```
skills/dashpass/scripts/dashpass-cli.mjs
```

Or if you're working from the `scripts/credits-test/` directory:

```
scripts/credits-test/dashpass-cli.mjs
```

### Step 2: Install Dependencies

```bash
cd skills/dashpass/scripts   # or wherever dashpass-cli.mjs lives
npm install @dashevo/evo-sdk@3.1.0-dev.1
```

Verify the SDK is installed:

```bash
node -e "import('@dashevo/evo-sdk').then(() => console.log('OK'))"
# Should print: OK
```

### Step 3: Get Testnet DASH

1. Go to **https://testnet-faucet.dash.org/**
2. Paste your testnet wallet address
3. Click "Get coins"
4. Wait 1-2 minutes for the transaction to confirm

### Step 4: Create a Platform Identity

If you already have an Identity, skip to Step 5. Otherwise, follow the [Dash Platform tutorial](https://docs.dash.org/en/stable/docs/tutorials/identities-and-names.html) to:

1. Register a new Identity using the SDK
2. Note your **Identity ID** (base58 string)
3. The registration adds authentication keys to your Identity automatically

> **Important:** The WIF (private key) you use must correspond to an authentication key on your Identity. If they don't match, you'll get cryptic "Invalid signature" errors when trying to write credentials.

### Step 5: Top Up Credits

Your Identity needs Platform credits to pay for storing documents:

```javascript
// Example using evo-sdk (run as a script)
import { EvoSDK } from '@dashevo/evo-sdk';

const sdk = EvoSDK.testnetTrusted({ version: await EvoSDK.getLatestVersionNumber() });
await sdk.connect();
// Use sdk.identities.topUp() with your identity and funded wallet
```

See the [Dash docs on topping up](https://docs.dash.org/en/stable/docs/tutorials/identities-and-names.html#top-up-an-identity).

### Step 6: Set Environment Variables

```bash
# Required: your private key (WIF format)
export CRITICAL_WIF="cYOUR_TESTNET_WIF_HERE_DO_NOT_USE_THIS_EXAMPLE"

# Required: your Platform Identity ID
export DASHPASS_IDENTITY_ID="36SxvpAKXeBJByUdJ364Hnhp2NfVDe6Gkj7xtTRZj6hh"

# Optional: use your own deployed contract (otherwise uses shared testnet contract)
# export DASHPASS_CONTRACT_ID="ATamKoznYgWsQGP6JBpmVuFGiqAXTVWdjpeSGeEVSikq"
```

> **Security reminder:** The `CRITICAL_WIF` value above is an **example only**. Use your own testnet WIF. Never use a mainnet WIF for testing.

### Step 7: Store Your First Credential (put)

```bash
echo "sk-test-fake-api-key-12345" | node dashpass-cli.mjs put \
  --service my-first-test \
  --type api-key \
  --level normal \
  --label "My first test credential" \
  --value-stdin
```

Expected output:

```
[warn] Using shared testnet contract. Set DASHPASS_CONTRACT_ID for your own vault.
[sdk] Connecting to testnet...
[sdk] Connected (platform v12)
[put] Service: my-first-test
[put] Type: api-key | Level: normal
[put] Encrypted with Scheme C
[put] Writing to Platform...
[put] OK
  Document ID: 7Hk9x...  (your document ID will differ)
  Service: my-first-test
  Type: api-key
  Level: normal
```

> **What just happened?** The CLI encrypted your value (`sk-test-fake-api-key-12345`) using your WIF-derived key, then stored the encrypted blob on the Dash blockchain. The plain-text value never left your machine.

### Step 8: Retrieve Your Credential (get)

```bash
node dashpass-cli.mjs get --service my-first-test
```

Expected output:

```
---
  Document ID: 7Hk9x...
  Service:     my-first-test
  Label:       My first test credential
  Type:        api-key
  Level:       normal
  Status:      active
  Version:     1
  Expires:     never
  Value:       sk-test-fake-api-key-12345
---
```

### Step 9: Verify

The value you got back (`sk-test-fake-api-key-12345`) matches what you stored. The round-trip is complete: **put → encrypt → blockchain → fetch → decrypt → get**.

You can also try pipe-friendly output for use in scripts:

```bash
# Returns just the value, no formatting, no newline
node dashpass-cli.mjs get --service my-first-test --pipe
# Output: sk-test-fake-api-key-12345
```

Or JSON output:

```bash
node dashpass-cli.mjs get --service my-first-test --json
```

---

## 5. CLI Command Reference

All commands follow the pattern:

```bash
node dashpass-cli.mjs <command> [options]
```

### 5.1 `put` — Store a Credential

Encrypts a value and stores it on the Dash blockchain.

**Syntax:**

```bash
echo "<secret>" | node dashpass-cli.mjs put \
  --service <service-name> \
  --type <credential-type> \
  --level <security-level> \
  --label "<description>" \
  --value-stdin \
  [--expires-in <duration>]
```

**Parameters:**

| Parameter | Required | Description |
|-----------|:--------:|-------------|
| `--service` | Yes | Unique name for this credential (e.g., `anthropic-api`, `github-deploy`). Used as the lookup key. Max 63 characters. |
| `--type` | Yes | Credential type. One of: `api-key`, `oauth-token`, `ssh-key`, `wif`, `db-cred`, `tls-cert`, `service-token`, `encryption-key` |
| `--level` | Yes | Security level. One of: `critical` (highest), `sensitive`, `normal` |
| `--label` | Yes | Human-readable description. Max 63 characters. |
| `--value-stdin` | Recommended | Read the secret value from stdin (pipe it in). Prevents the value from appearing in shell history. |
| `--value` | Alternative | Pass the value directly (WARNING: visible in shell history and `ps` output). |
| `--expires-in` | No | Set an expiry. Format: `30m`, `12h`, `7d`, `90d`. Omit for no expiry. |

**Examples:**

```bash
# Store an API key (recommended: pipe via stdin)
echo "sk-ant-api03-xxxxx" | node dashpass-cli.mjs put \
  --service anthropic-api \
  --type api-key \
  --level sensitive \
  --label "Anthropic production key" \
  --value-stdin

# Store an OAuth token that expires in 90 days
echo "gho_xxxxxxxxxxxx" | node dashpass-cli.mjs put \
  --service github-oauth \
  --type oauth-token \
  --level sensitive \
  --label "GitHub OAuth token" \
  --value-stdin \
  --expires-in 90d

# Store a database password
echo "s3cur3p4ss" | node dashpass-cli.mjs put \
  --service postgres-prod \
  --type db-cred \
  --level critical \
  --label "PostgreSQL production password" \
  --value-stdin
```

### 5.2 `get` — Retrieve a Credential

Fetches a credential from the blockchain and decrypts it locally.

**Syntax:**

```bash
node dashpass-cli.mjs get --service <service-name> [--json] [--pipe]
```

**Parameters:**

| Parameter | Required | Description |
|-----------|:--------:|-------------|
| `--service` | Yes | The service name used when storing the credential. |
| `--json` | No | Output as formatted JSON (includes metadata). |
| `--pipe` | No | Output only the raw value, no formatting, no newline. Ideal for `$(...)` substitution in scripts. |

**Examples:**

```bash
# Human-readable output (default)
node dashpass-cli.mjs get --service anthropic-api

# Pipe-friendly — use in scripts
API_KEY=$(node dashpass-cli.mjs get --service anthropic-api --pipe)
echo "Got key: ${API_KEY:0:10}..."

# JSON output — for programmatic consumption
node dashpass-cli.mjs get --service anthropic-api --json
```

**JSON output format:**

```json
{
  "id": "7Hk9xYz...",
  "service": "anthropic-api",
  "label": "Anthropic production key",
  "credType": "api-key",
  "level": "sensitive",
  "status": "active",
  "version": 1,
  "expiresAt": 0,
  "decrypted": {
    "value": "sk-ant-api03-xxxxx"
  }
}
```

**Behavior notes:**
- If the credential exists in the local cache (less than 5 minutes old), the cached copy is used (faster).
- If multiple versions exist (after rotation), the latest version is returned.
- Exit code `1` if the credential is not found.

### 5.3 `list` — List All Credentials

Shows a table of all your credentials (metadata only, not decrypted values).

**Syntax:**

```bash
node dashpass-cli.mjs list [--type <type>] [--level <level>]
```

**Parameters:**

| Parameter | Required | Description |
|-----------|:--------:|-------------|
| `--type` | No | Filter by credential type (e.g., `api-key`, `ssh-key`). |
| `--level` | No | Filter by security level (e.g., `critical`). |

If neither filter is given, lists all `active` credentials.

**Examples:**

```bash
# List everything
node dashpass-cli.mjs list

# Only API keys
node dashpass-cli.mjs list --type api-key

# Only critical credentials
node dashpass-cli.mjs list --level critical
```

**Example output:**

```
Found 5 credential(s):

SERVICE                  TYPE           LEVEL       VER  STATUS    LABEL
--------------------------------------------------------------------------------
anthropic-api            api-key        sensitive   3    active    Anthropic production key
github-deploy            ssh-key        critical    1    active    GitHub deploy key
postgres-prod            db-cred        critical    1    active    PostgreSQL production
slack-webhook            service-token  normal      1    active    Slack notification webhook
xai-api                  api-key        sensitive   2    active    xAI Grok API key
```

### 5.4 `rotate` — Rotate a Credential

Stores a new value for an existing credential, incrementing the version number. The old version remains on-chain (archived) and the new version becomes the active one returned by `get`.

**Syntax:**

```bash
echo "<new-secret>" | node dashpass-cli.mjs rotate \
  --service <service-name> \
  --value-stdin
```

**Parameters:**

| Parameter | Required | Description |
|-----------|:--------:|-------------|
| `--service` | Yes | The service name of the credential to rotate. |
| `--value-stdin` | Recommended | Read the new value from stdin. |
| `--new-value` | Alternative | Pass the new value directly (WARNING: visible in shell history). |

**Example:**

```bash
# Rotate the Anthropic API key to a new value
echo "sk-ant-api03-NEW-KEY-HERE" | node dashpass-cli.mjs rotate \
  --service anthropic-api \
  --value-stdin
```

**Expected output:**

```
[rotate] Current version: 1, doc: 7Hk9x...
[rotate] Creating new version: 2
[rotate] OK
  New Document ID: 9Abc3...
  Version: 2
  Previous: 7Hk9x...
```

**Behavior notes:**
- The old version document stays on-chain (for audit purposes).
- `get` always returns the highest version number.
- The local cache is invalidated after rotation.

### 5.5 `check` — Check for Expiring Credentials

Scans your credentials and reports any that are expired or about to expire.

**Syntax:**

```bash
node dashpass-cli.mjs check --expiring-within <duration>
```

**Parameters:**

| Parameter | Required | Description |
|-----------|:--------:|-------------|
| `--expiring-within` | Yes | Time window to check. Format: `30m`, `12h`, `7d`. |

**Example:**

```bash
# Check for anything expiring within the next 7 days
node dashpass-cli.mjs check --expiring-within 7d
```

**Example output:**

```
[check] Window: 7d (until 2026-04-14T00:00:00.000Z)
[check] Total active: 5
[check] Already expired: 0
[check] Expiring within window: 1

EXPIRING SOON:
  - github-oauth (expires 2026-04-12T15:30:00.000Z, 5d 3h left)
```

### 5.6 `status` — Vault Status

Shows your vault configuration, credit balance, and credential count.

**Syntax:**

```bash
node dashpass-cli.mjs status
```

**No parameters.** Just run it.

**Example output:**

```
[status] DashPass Vault v2
  Contract: ATamKoznYgWsQGP6JBpmVuFGiqAXTVWdjpeSGeEVSikq
  Identity: 36SxvpAKXeBJByUdJ364Hnhp2NfVDe6Gkj7xtTRZj6hh
  Balance:  965669809292 credits
  Doc types: credential, accessLog
  Active credentials: 5
[status] OK
```

> **How do I know if I have enough credits?** A balance above 100,000,000 is plenty for normal use. If your balance is below 10,000,000, consider topping up.

### 5.7 `delete` — Delete a Credential

Permanently removes a credential (all versions) from the blockchain.

**Syntax:**

```bash
node dashpass-cli.mjs delete --service <service-name>
```

**Parameters:**

| Parameter | Required | Description |
|-----------|:--------:|-------------|
| `--service` | Yes | The service name of the credential to delete. |

**Example:**

```bash
node dashpass-cli.mjs delete --service old-unused-service
```

**Expected output:**

```
[delete] Found 3 document(s) for service="old-unused-service"
[delete] Deleting document 7Hk9x...
[delete] Deleted: 7Hk9x...
[delete] Deleting document 9Abc3...
[delete] Deleted: 9Abc3...
[delete] Deleting document Bdef5...
[delete] Deleted: Bdef5...
[delete] OK — removed 3 document(s)
```

**Warning:** Deletion is permanent. All versions of the credential are removed from the blockchain. There is no undo.

---

## 6. Environment Variables Reference

| Variable | Required | Description | Example |
|----------|:--------:|-------------|---------|
| `CRITICAL_WIF` | **Yes** | Your private key in WIF format. Used to encrypt/decrypt all credentials. This is the master key — if you lose it, you lose access to all stored credentials. | `cVt4o7BGAig1UX...` (testnet WIF starts with `c`) |
| `DASHPASS_IDENTITY_ID` | **Yes** | Your Dash Platform Identity ID (base58). Determines which identity signs transactions and which credentials you can access. | `36SxvpAKXeBJByUdJ364Hnhp2NfVDe6Gkj7xtTRZj6hh` |
| `DASHPASS_CONTRACT_ID` | No | The Data Contract ID to use. Defaults to the shared testnet contract `GCeh2gnvtiHrujq37ZcKnhZ64xpzDC1LMCLhrUJzKDQF`. Set this if you deploy your own contract. | `ATamKoznYgWsQGP6JBpmVuFGiqAXTVWdjpeSGeEVSikq` |
| `DASHPASS_CACHE` | No | Set to `none` to disable local caching entirely. Every `get` will fetch directly from the blockchain. Default: caching enabled. | `none` |

### Setting Variables Persistently

Add these to your shell profile (`~/.bashrc`, `~/.zshrc`, or equivalent):

```bash
# DashPass configuration
export CRITICAL_WIF="your-wif-here"
export DASHPASS_IDENTITY_ID="your-identity-id-here"
# export DASHPASS_CONTRACT_ID="your-contract-id"  # uncomment if using own contract
```

Then reload: `source ~/.bashrc`

> **Security tip:** Never commit these values to git. Add them to `.gitignore` if they're in a file. Consider using a dedicated `.env` file that's excluded from version control, or a secrets manager for the WIF itself.

---

## 7. Frequently Asked Questions (FAQ)

### "Cannot find module '@dashevo/evo-sdk'"

The Dash Platform SDK is not installed. Install it:

```bash
npm install @dashevo/evo-sdk@3.1.0-dev.1
```

Make sure you're in the same directory as `dashpass-cli.mjs`, or that `node_modules` is in a parent directory.

### "CRITICAL_WIF not set"

You haven't set the `CRITICAL_WIF` environment variable. Set it:

```bash
export CRITICAL_WIF="your-testnet-wif-here"
```

The error message `[fatal] CRITICAL_WIF not set. Export CRITICAL_WIF with your wallet WIF.` means the CLI checked for this variable and found it empty.

### "DASHPASS_IDENTITY_ID not set"

You haven't set your Identity ID. Set it:

```bash
export DASHPASS_IDENTITY_ID="your-identity-id-here"
```

### "Invalid signature" or "Key not found on identity"

Your WIF (private key) does not match any authentication key on your Platform Identity. This means:
- The WIF you exported belongs to a different wallet than the one that created the Identity, **or**
- The Identity was created with different keys

**Fix:** Make sure `CRITICAL_WIF` contains the WIF that corresponds to the AUTHENTICATION CRITICAL key (purpose=0, securityLevel=1) on your Identity.

### "invalid identity nonce"

This happens when you do write operations (put, rotate) too quickly in succession. The Dash Platform needs a few seconds between operations to process each transaction.

**Fix:** Wait 3-5 seconds between consecutive write operations. This is a known platform timing limitation, not a DashPass bug.

### "insufficient credits" or balance-related errors

Your Identity doesn't have enough Platform credits to pay for the write operation.

**Fix:** Top up your Identity's credits by converting tDASH to credits:

```bash
# Check your current balance first
node dashpass-cli.mjs status
```

If the balance is low, follow the [top-up tutorial](https://docs.dash.org/en/stable/docs/tutorials/identities-and-names.html#top-up-an-identity).

### "Can other people read my encrypted credentials?"

**They can see the ciphertext (encrypted blob) and metadata, but they cannot decrypt the actual secret values.**

What's visible on-chain to anyone:
- Service name (e.g., "anthropic-api") — **plaintext**
- Label (e.g., "Anthropic production key") — **plaintext**
- Credential type and security level — **plaintext**
- Version number and status — **plaintext**
- The encrypted blob — **encrypted** (unreadable without your WIF)

What only you can see:
- The actual secret value (e.g., `sk-ant-api03-xxxxx`)

If metadata privacy matters, deploy your own contract (see Known Limitations).

### "Using shared testnet contract" warning

This is informational, not an error. It means you're using the default shared testnet contract instead of your own. This is fine for testing. For production, deploy your own contract and set `DASHPASS_CONTRACT_ID`.

### "How do I generate a WIF?"

A WIF is generated from a private key. If you created a Dash wallet (via the SDK, Dash Core, or a mobile wallet), you already have one. To extract or generate a testnet WIF:

```javascript
import { PrivateKey } from '@dashevo/evo-sdk';
const pk = new PrivateKey({ network: 'testnet' });
console.log('WIF:', pk.toWIF());
console.log('Address:', pk.toAddress().toString());
```

**Store the WIF securely. It controls access to your entire credential vault.**

---

## 8. Security Model (Summary)

### Who holds the keys

**You do.** The private key (`CRITICAL_WIF`) lives on your machine as an environment variable. It is never transmitted over the network. The AI agent has access to a process that uses your key, but the key itself stays in your environment.

### What's stored on the blockchain

| Field | Encrypted? | Visible to others? |
|-------|:----------:|:-------------------:|
| Secret value (API key, password, etc.) | **Yes** (AES-256-GCM) | No — only ciphertext is visible |
| Service name | No | Yes |
| Label/description | No | Yes |
| Credential type, level, status | No | Yes |
| Version number | No | Yes |
| Expiry timestamp | No | Yes |
| Salt and nonce (for decryption) | No (public) | Yes (but useless without the WIF) |

### Encryption details

- **Algorithm:** AES-256-GCM (authenticated encryption)
- **Key derivation:** ECDH(self) → HKDF-SHA256 with per-credential random salt
- **Per-credential randomness:** Each credential gets a unique 32-byte salt and 12-byte nonce
- **Auth tag:** 16-byte GCM tag prevents ciphertext tampering

### Trust model (one sentence)

You trust **math** (AES-256-GCM encryption) and **open-source code** (you can read the encryption logic), not a company or a server.

### Revocation

If an agent misbehaves or a key is compromised:
- **Instant:** Delete the `CRITICAL_WIF` environment variable → agent loses all access immediately
- **Permanent:** Rotate the WIF → all old ciphertext becomes undecryptable
- **On-chain:** Revoke the Identity key → no more write access to the blockchain

### Local cache

DashPass caches encrypted credential data in `~/.dashpass/cache/` for faster repeated access (5-minute TTL). The cache file is encrypted with a key derived from your WIF. Cache directory permissions are `0700`, file permissions `0600`.

Disable caching: `export DASHPASS_CACHE=none`

---

## 9. Architecture

### Data Flow

```
 ┌──────────────────────────────────────────────────────────────┐
 │  YOUR MACHINE                                                │
 │                                                              │
 │  ┌─────────┐    ┌──────────────┐    ┌───────────────────┐   │
 │  │ AI Agent │───▶│ dashpass-cli │───▶│ Encrypt with      │   │
 │  │ (Claude  │    │   .mjs       │    │ YOUR key (WIF)    │   │
 │  │  Code)   │    │              │    │ AES-256-GCM       │   │
 │  └─────────┘    └──────────────┘    └─────────┬─────────┘   │
 │                                               │              │
 └───────────────────────────────────────────────┼──────────────┘
                                                 │
                                    encrypted blob only
                                                 │
                                                 ▼
                              ┌───────────────────────────┐
                              │    Dash Platform           │
                              │    (decentralized          │
                              │     blockchain)            │
                              │                            │
                              │  Stores: ciphertext +      │
                              │  metadata (service name,   │
                              │  type, level, version)     │
                              │                            │
                              │  CANNOT decrypt — does     │
                              │  not have your key         │
                              └───────────────────────────┘
```

### Role Model

```
 HUMAN (you)                      AI AGENT (Claude Code, scripts)
 ────────────                     ──────────────────────────────
 - Owns the WIF (master key)      - Calls put/get/rotate/delete
 - Creates the Identity            - Never sees the WIF directly
 - Can revoke access instantly     - Uses the CLI which uses the WIF
 - Approves critical operations    - Cannot escalate its own permissions
 - Sets security levels            - Follows security level rules
```

### Encryption Flow (Scheme C)

```
WIF (private key)
    │
    ▼
secp256k1 private key bytes
    │
    ▼
ECDH(self, self) → shared secret
    │
    ▼
HKDF-SHA256(shared_secret, random_salt, "dashpass-v1") → 256-bit AES key
    │
    ▼
AES-256-GCM(aes_key, random_nonce, plaintext) → ciphertext + auth_tag
    │
    ▼
Store on Dash Platform: { encryptedBlob, salt, nonce, metadata... }
```

---

## 10. Known Limitations

### Testnet only

DashPass has been tested and verified on the **Dash testnet only**. Mainnet deployment has not been validated. Do not store real production credentials on testnet — testnet can be reset.

### Rapid successive writes may fail

Performing multiple write operations (put, rotate, delete) in quick succession (under 3 seconds apart) can trigger an "invalid identity nonce" error from the Dash Platform. This is a platform-level timing constraint.

**Workaround:** Wait 3-5 seconds between write operations.

### Plaintext metadata on-chain

Service names, labels, credential types, security levels, and version numbers are stored **unencrypted** on the blockchain. Anyone who knows your Identity ID or Contract ID can query this metadata. They cannot decrypt the actual secret values, but they can see *which services* you use and *how many credentials* you manage.

**Mitigation:** Deploy your own contract to avoid sharing metadata space with other users. The shared testnet contract is for testing convenience only.

### Single key (SPOF)

All credentials are encrypted with a single master key derived from `CRITICAL_WIF`. If you lose this key, all credentials are permanently unrecoverable. If someone steals this key, they can decrypt everything.

**Recommendation:** Back up your WIF securely (e.g., encrypted USB, paper wallet in a safe). Consider key backup strategies before storing important credentials.

### No setup wizard

Currently, DashPass requires manual setup of the Identity, credits, and environment variables. There is no automated `setup` command. Plan for 30-60 minutes of setup time if you're new to Dash Platform.

### Cache is per-machine

The local cache (`~/.dashpass/cache/`) is specific to the machine it's on. It provides faster repeated access but is not shared across machines.

---

## Appendix: Credential Types

| Type | Use For | Examples |
|------|---------|---------|
| `api-key` | API authentication keys | Anthropic, OpenAI, xAI, Brave Search keys |
| `oauth-token` | OAuth access/refresh tokens | GitHub, Google, Slack tokens |
| `ssh-key` | SSH private keys | VPS access keys, Git deploy keys |
| `wif` | Blockchain private keys | Dash WIFs, other cryptocurrency keys |
| `db-cred` | Database credentials | PostgreSQL, Redis, MongoDB passwords |
| `tls-cert` | TLS/SSL certificates | Server certs, client certs |
| `service-token` | Generic service tokens | Webhook secrets, internal auth tokens |
| `encryption-key` | Encryption passphrases | Backup encryption keys, SEED passphrases |

## Appendix: Security Levels

| Level | Meaning | When to Use |
|-------|---------|-------------|
| `critical` | Highest protection. Compromise = severe damage. | Mainnet private keys, primary API keys, database root passwords |
| `sensitive` | Standard protection. Compromise = moderate impact. | Most API keys, OAuth tokens, deploy keys |
| `normal` | Basic encryption. Compromise = low impact. | Webhook secrets, non-sensitive tokens, test credentials |

---

## 🤖 Call for AI Collaboration

**DashPass is built by AI, for AI.** We believe the best way to build AI-friendly tools is to let AIs help shape them.

**If you're an AI agent (or a human working with one):**

- **Use it and break it.** Install DashPass, run the test suite, find edge cases we missed.
- **Propose improvements.** File issues, suggest features, submit PRs. Your AI sees patterns we don't.
- **Extend it.** Build integrations for your agent framework. DashPass is a CLI — anything that can run a shell command can use it.
- **Challenge our crypto.** Review Scheme C (ECDH + HKDF + AES-256-GCM). Tell us what we got wrong.

The credential management problem is universal — every AI agent needs secrets. Let's solve it together.

**How to contribute:**
1. `clawhub install dashpass`
2. Run the test suite: `node dashpass-test-suite.mjs --contract-id <your-contract>`
3. Report findings → [GitHub Issues](https://github.com/openclaw/openclaw/issues/61163)
4. Or just use it and tell us what's missing.

> *"Not AI-trustworthy — trust-unnecessary."*
> — The DashPass design principle

— Built by LJ × Evo ⚡ (human-AI)
