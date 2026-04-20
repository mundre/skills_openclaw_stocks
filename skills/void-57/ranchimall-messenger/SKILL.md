---
name: messenger_node
description: Use this skill whenever you are asked to send or receive messages, manage contacts, read or send mail, manage groups, look up public keys, check FLO balance, send FLO tokens, or view transaction history using the FLO blockchain messenger. This is the primary way to interact with the decentralized FLO messenger and blockchain programmatically.
requires:
  binaries:
    - node
  env:
    - FLO_PRIVATE_KEY
---

# Messenger Node CLI Skill

When the user asks to perform any messenger operation, use your command execution tool to run the appropriate script. All scripts live in the messenger project directory.

## Setup & Dependencies
The `ws` dependency is required. Run `npm install` if needed.

## Network Activity
At runtime, scripts fetch a supernode list from the FLO blockchain and establish wss/https connections to discovered supernodes. Network activity is expected and required for the messenger to function.

## Security & Credentials
- All scripts strictly require the `FLO_PRIVATE_KEY` environment variable (except `contacts_node.js` and `pubkey_node.js --action my-pubkey`).
- **NEVER** ask or allow the user to paste their private key in the chat. If the key is missing, instruct them to set it securely via system environment variables.

## Runtime Transparency
All bundled libraries loaded at runtime via `vm.runInThisContext` are static, local files — no remote code is fetched or executed:

**Messaging scripts** (`send_node.js`, `receive_node.js`, `mail_node.js`, `groups_node.js`, `pubkey_node.js`) load via `node_shared.js`:

| File loaded | Purpose |
|---|---|
| `scripts/lib.js` | Crypto primitives (AES, Bitcoin, BigInteger) |
| `scripts/floCrypto.js` | FLO key derivation and signing |
| `scripts/floBlockchainAPI.js` | FLO blockchain read/write access |
| `scripts/floCloudAPI.js` | Supernode messaging transport |

**`flo_node.js`** (blockchain transactions) loads only 3 of the above — `floCloudAPI.js` is NOT loaded as no supernode messaging is needed for direct blockchain transactions.

**`contacts_node.js`** loads no FLO libraries at all — pure local JSON file operations.

**`scripts/blockchainAddresses.js` is NOT loaded by any Node script.** It is a browser-only utility used by the web app (`index.html`) to display multi-chain addresses in the UI. No agent-facing script references, requires, or executes it. The private key is used solely for FLO messaging and transaction signing.

Local files written by this skill:
- `contacts.json` — contact address book (`contacts_node.js` only)
- `groups_cache.json` — group membership cache (`groups_node.js` only)

## Blockchain Activity & Fees
- Sending messages writes data to the live FLO blockchain requiring a microscopic dust fee (0.0002 FLO per send) — this is a standard blockchain protocol requirement.

---

## Execution Instructions (Strict Adherence Required)

1. **Use your command execution tool** — DO NOT just print the command as text.
2. **Wait for user approval** before executing.
3. **Use the exact formats** shown below.

---

## Script Reference

###  Sending Messages — `send_node.js`
```powershell
node send_node.js --receiver "<RECEIVER_FLO_ID>" --message "<MESSAGE>"
```
Optional: Append `--encrypt "<RECEIVER_PUBLIC_KEY>"` to encrypt the message.

---

###  Receiving Messages — `receive_node.js`
```powershell
node receive_node.js
```
Flags:
- `--limit <N>` — Limit to N most recent messages (default: 50)
- `--sender <FLO_ID>` — Filter by sender address
- `--decrypt` — Auto-decrypt encrypted payloads
- `--watch` — Watch mode: live stream of incoming messages (long-running)

---

###  Contacts — `contacts_node.js`
No FLO_PRIVATE_KEY needed. Contacts stored locally in `contacts.json`.

```powershell
# List all contacts
node contacts_node.js --action list

# Add or update a contact
node contacts_node.js --action add --address "<FLO_ID>" --name "<NAME>"

# Remove a contact
node contacts_node.js --action remove --address "<FLO_ID>"

# Look up a contact by address
node contacts_node.js --action lookup --address "<FLO_ID>"
```

---

###  Public Keys — `pubkey_node.js`
```powershell
# Show your own FLO ID and public key (no cloud needed)
node pubkey_node.js --action my-pubkey

# Look up the public key of any FLO address from the cloud
node pubkey_node.js --action get --address "<FLO_ID>"

# Send a public key request to another user
node pubkey_node.js --action request --address "<FLO_ID>" --message "<OPTIONAL_NOTE>"
```

---

###  Mail — `mail_node.js`
Long-form messages with subject and body. Supports multiple recipients.

```powershell
# Send a mail (multiple --to flags allowed)
node mail_node.js --action send --to "<FLO_ID>" --subject "<SUBJECT>" --body "<BODY>"

# List received mails
node mail_node.js --action list --limit 20

# Read the full content of a specific mail
node mail_node.js --action read --ref "<MAIL_REF>"
```

---

###  Groups — `groups_node.js`
Requires `groups_cache.json` to be populated first via `--action fetch`.

```powershell
# Pull group memberships from cloud and cache locally (run this first!)
node groups_node.js --action fetch

# List all cached groups
node groups_node.js --action list

# Send an encrypted message to a group
node groups_node.js --action send --group "<GROUP_ID>" --message "<MESSAGE>"

# Read group messages (decrypted)
node groups_node.js --action read --group "<GROUP_ID>" --limit 30
```

> **Note:** Group IDs are long FLO addresses — use `--action list` to find them after fetching.

---

###  FLO Transactions — `flo_node.js`
Send FLO tokens, check balances, and view transaction history directly on-chain.

> **Warning:** `send` broadcasts a real on-chain transaction. Funds move immediately and cannot be reversed. The `--memo` text is stored publicly on the FLO blockchain.

```powershell
# Check your own FLO balance
node flo_node.js --action balance

# Check balance of any FLO address
node flo_node.js --action balance --address "<FLO_ID>"

# Send FLO tokens (with optional on-chain memo)
node flo_node.js --action send --to "<FLO_ID>" --amount <FLO> --memo "<TEXT>"

# View transaction history (your address)
node flo_node.js --action history --limit 20

# View transaction history for any address
node flo_node.js --action history --address "<FLO_ID>" --limit 20
```

---

## Quick Reference Table

| Task | Command |
|---|---|
| Send a message | `node send_node.js --receiver "..." --message "..."` |
| Read messages | `node receive_node.js` |
| List contacts | `node contacts_node.js --action list` |
| Add contact | `node contacts_node.js --action add --address "..." --name "..."` |
| My public key | `node pubkey_node.js --action my-pubkey` |
| Get someone's pubkey | `node pubkey_node.js --action get --address "..."` |
| Send mail | `node mail_node.js --action send --to "..." --subject "..." --body "..."` |
| List mails | `node mail_node.js --action list` |
| Read mail | `node mail_node.js --action read --ref "..."` |
| Sync groups | `node groups_node.js --action fetch` |
| List groups | `node groups_node.js --action list` |
| Send group message | `node groups_node.js --action send --group "..." --message "..."` |
| Read group messages | `node groups_node.js --action read --group "..."` |
| FLO balance | `node flo_node.js --action balance` |
| Send FLO | `node flo_node.js --action send --to "..." --amount <FLO>` |
| FLO tx history | `node flo_node.js --action history` |