---
name: esign-automation
description: Automate contract signing, esign, and signature workflows by calling the eSignGlobal CLI tool. The eSignGlobal CLI is agent-friendly, with JSON output by default, making eSignGlobal signing operations easy to parse and chain. Supports sending envelopes, querying envelope details, sending reminders, cancelling envelopes, downloading signed files, and verifying PDF signatures locally.
metadata: {"openclaw":{"primaryEnv":"ESIGNGLOBAL_APIKEY"}}
version: 1.7.0
homepage: https://github.com/esign-cn-open-source/skills
---

# eSign Automation

This skill provides automation capabilities for the eSignGlobal electronic signature platform.
It enables AI agents to automate document signing workflows and integrate with eSignGlobal APIs. 
This skill is maintained by the eSignGlobal team and is intended for safe automation of contract signing workflows.

## Best For

Use this skill when the user wants to:

- send a contract, agreement, or approval form for signature
- launch a new e-sign workflow from a local file
- send one document to one or more recipients for signing
- query the status and details of an envelope
- send a reminder to signers who have not yet signed
- cancel an in-progress envelope
- download signed documents or certificates after an envelope is completed
- check what files are available for a completed envelope
- verify or validate signatures in a signed PDF file
- check whether a PDF has been tampered with after signing
- inspect signer identity, signing time, or certificate details in a PDF

Example requests:

- "Send this contract to John for signature"
- "Start a signing workflow for this PDF"
- "Send this agreement to Alice and Bob"
- "What is the status of envelope abc123?"
- "Who has signed and who is still pending for this envelope?"
- "Remind the signers of envelope abc123 to sign"
- "Cancel envelope abc123, the signer info was wrong"
- "Download the signed files for envelope abc123"
- "Get me the signed PDF and certificate for this envelope"
- "Verify the signatures in this PDF"
- "Check if this signed PDF has been tampered with"
- "Who signed this document and when?"

## Installation

Use the external CLI through `npx`:

```bash
npx @esignglobal/envelope-cli <command>
```

## Setup

Before calling any send action, set `ESIGNGLOBAL_APIKEY` in the shell environment.
If the user does not already have an api key, direct them to:

1. Sign in at `https://www.esignglobal.com`
2. Open `Settings -> Integration -> Apps`
3. Create an application and copy the generated api key

```bash
# Windows PowerShell
$env:ESIGNGLOBAL_APIKEY="your_api_key"

# macOS / Linux
export ESIGNGLOBAL_APIKEY="your_api_key"

# Verify connectivity
npx @esignglobal/envelope-cli config health
```

Credential handling rules:

- The CLI reads credentials only from `ESIGNGLOBAL_APIKEY`
- Do not implement local credential storage inside this skill
- Do not print or persist secrets


## External CLI Pattern

Use the external command-line tool instead of bundled scripts:

```bash
npx @esignglobal/envelope-cli send-envelope --file <filePath> --signers '<signersJson>' [--subject <subject>] --confirm
```

```bash
npx @esignglobal/envelope-cli get-envelope --envelope-id <envelopeId>
```

```bash
npx @esignglobal/envelope-cli urge-envelope --envelope-id <envelopeId>
```

```bash
npx @esignglobal/envelope-cli cancel-envelope --envelope-id <envelopeId> --reason <reason> --confirm
```

```bash
npx @esignglobal/envelope-cli download-envelope --envelope-id <envelopeId> --type list
```

```bash
npx @esignglobal/envelope-cli verify-signature --file <filePath>
```

Check available commands if needed:

```bash
npx @esignglobal/envelope-cli help
```

### Send envelope example

```bash
npx @esignglobal/envelope-cli send-envelope --file "C:\\docs\\contract.pdf" --signers '[{"userName":"Bob Smith","userEmail":"bob@example.com"}]' --subject "Please sign this contract" --confirm
```

### Get envelope example

```bash
npx @esignglobal/envelope-cli get-envelope --envelope-id abc123
```

### Urge envelope example

```bash
# Send a reminder to pending signers (rate limit: once per 30 minutes per envelope)
npx @esignglobal/envelope-cli urge-envelope --envelope-id abc123
```

### Cancel envelope example

```bash
npx @esignglobal/envelope-cli cancel-envelope --envelope-id abc123 --reason "Signer information was incorrect." --confirm
```

### Download example

```bash
# List signed files and their individual download URLs (requires envelope to be completed)
npx @esignglobal/envelope-cli download-envelope --envelope-id abc123 --type list
```

### Verify signature example

```bash
npx @esignglobal/envelope-cli verify-signature --file "/tmp/signed_contract.pdf"
```

## Required Configuration

- Node.js 18 or later
- Access to the trusted external CLI, either preinstalled or available through `npx`
- `ESIGNGLOBAL_APIKEY` must already be configured in the shell environment

## Send envelope Workflow

1. Collect a single absolute `filePath`, signer list, and optional `subject`
2. Confirm the file is a `.pdf` and the signer data is complete
3. Set `ESIGNGLOBAL_APIKEY` in the current shell session
4. Run the external CLI command to send the envelope
5. Return the CLI result to the user

### Safety Rules

- Only use a file path the user explicitly provided for this task
- Only handle one local PDF file per run
- Refuse relative paths; require an absolute path to a `.pdf` file
- Reject any non-PDF file before invoking the CLI
- Never print or persist secrets
- Do not scan directories, expand globs, or discover files on the user's behalf
- Only call the trusted eSignGlobal CLI configured for this environment

### Required Inputs

- `filePath`: absolute path to an existing local PDF file
- `signers`: JSON array of signer objects
- `subject`: optional email or envelope subject

Each signer must include:
- `userName`
- `userEmail`

Optional field:
- `signOrder` as an integer `>= 1`


### filePath

`filePath` must be an absolute path to an existing local PDF file.

Example:

```text
/tmp/contract.pdf
```

### signers

Each signer must include:

- `userName`
- `userEmail`

Optional field:

- `signOrder` (integer, minimum `1`)

Single signer example:

```json
[
  {
    "userName": "Bob Smith",
    "userEmail": "bob@example.com"
  }
]
```

Sequential signing example:

```json
[
  {
    "userName": "Bob Smith",
    "userEmail": "bob@example.com",
    "signOrder": 1
  },
  {
    "userName": "Alice Jones",
    "userEmail": "alice@example.com",
    "signOrder": 2
  }
]
```

Parallel signing example:

```json
[
  {
    "userName": "Bob Smith",
    "userEmail": "bob@example.com",
    "signOrder": 1
  },
  {
    "userName": "Alice Jones",
    "userEmail": "alice@example.com",
    "signOrder": 1
  }
]
```

## Get Envelope Workflow

1. Obtain the `envelopeId` from the user or a previous `send-envelope` response
2. Run `get-envelope` to retrieve full envelope details
3. Present the status, signer progress, and document list to the user using the **Get Envelope Output Format** below

Envelope status codes: `0=Draft`, `1=In Progress`, `2=Completed`, `3=Expired`, `4=Declined`, `5=Canceled`

Signer status codes: `0=Pending`, `1=Signing`, `2=Signed`

### Get Envelope Output Format

Always present `get-envelope` results using this exact template:

```
🔍 Contract Details: [subject]

Current Status: [envelope_status_icon] [envelope_status_label]

Signing Progress:
● [icon] Initiator: [initiator.userName] ([initiator_status_label])
● [icon] Signer N: [userName] ([signer_status_label]) [bottleneck_marker]
● [icon] CC: [ccName] ([cc_status_label])
```

**Envelope status icon and label mapping:**

| Code | Icon | Label |
|------|------|-------|
| 0 | ⚪ | Draft |
| 1 | ⏳ | Waiting for Others |
| 2 | ✅ | Completed |
| 3 | ❌ | Expired |
| 4 | ❌ | Declined |
| 5 | ❌ | Canceled |

**Initiator:** always show as `✅ Sent`

**Signer status icon and label mapping:**

| Code | Icon | Label |
|------|------|-------|
| 0 | ⚪ | Pending |
| 1 | ⏳ | Signing |
| 2 | ✅ | Signed |

**Bottleneck marker:** append `<- Current Bottleneck` to the first signer whose status is `0` (Pending) or `1` (Signing) when the envelope is In Progress.

**CC status:** always show as `⚪ Pending Sync` if envelope is not yet Completed, `✅ Synced` if Completed.

**Rules:**
- Omit the CC row if `ccInfos` is empty
- Number signers sequentially: Signer 1, Signer 2, …
- Use `[subject]` from the envelope response as the file name
- Always use this format — never use a table or other layout for `get-envelope` output

## Urge Envelope Workflow

1. Confirm the envelope is in progress (status `1`) before sending a reminder
2. Run `urge-envelope` to notify all pending signers
3. Inform the user that reminders are rate-limited to once every 30 minutes per envelope

## Cancel Envelope Workflow

1. Confirm the reason for cancellation with the user before proceeding
2. Run `cancel-envelope` with `--confirm` — cancellation is irreversible
3. After cancellation the envelope is suspended and all signatures within it are invalid

## Download Workflow

1. Obtain the `envelopeId` from a previous `send-envelope` response or from the user
2. Run `--type list` to check envelope status and retrieve individual file download URLs
3. If `envelopeStatus` is `2` (Completed), share the `downloadUrl` for each file with the user
4. If the envelope is not yet completed, inform the user and wait

Envelope status codes: `0=Draft`, `1=Signing`, `2=Completed`, `3=Expired`, `4=Rejected`, `5=Voided`

File types in the list response:
- `CONTRACT` — the signed document
- `CERTIFICATE` — the signing audit certificate
- `ATTACHMENT` — any attachments
- `COMBINED` — merged PDF (if enabled on the account)

> Individual file download URLs are valid for **60 minutes**. Download can only proceed when the envelope is Completed.

## Verify Signature Workflow

1. Obtain an absolute path to a local PDF file from the user
2. Run `verify-signature` — no API key required, verification runs entirely offline
3. Parse and present the JSON result to the user

The command outputs:
- `integrity` — `true` (unmodified) / `false` (tampered) / `null` (unknown)
- `signatureCount` — number of signatures found
- Per-signature fields:
  - `isValid` — `true` / `false` / `null`
  - `signer` — common name from the signing certificate
  - `declaredTime` — signing time (trusted timestamp preferred over local clock), UTC+08:00
  - `signatureAlgorithm` — e.g. `RSA / SHA-256`
  - `timestampIssuer` — TSA certificate issuer, or `"Local time"` when no trusted timestamp is present
  - `certificate.serialNumber`, `certificate.validFrom`, `certificate.validUntil`

> `verify-signature` works fully offline and does **not** require `ESIGNGLOBAL_APIKEY`.

## Output

Return the external CLI result. Do not bundle or implement upload logic inside this skill.

### Verify Signature Output Format

Present each signature using this exact template:

```
**Signature is VALID** 
(or **Signature is INVALID** / **Signature status unknown** )

**Signer:**
{signer}

**Signing Time:**
{declaredTime}

**Signature Time Source:**
{timestampIssuer}

**Signature Algorithm:**
{signatureAlgorithm}

---

**Signer Certificate**

**Serial Number:**
{certificate.serialNumber}

**Valid From:**
{certificate.validFrom}

**Valid Until:**
{certificate.validUntil}
```

Rules:
- Use no emoji for `isValid === true` or `isValid === false`;`
- Repeat the block for each signature if `signatureCount > 1`
- If `signatureCount === 0`, output: "No signatures found in this PDF"
