# ☁️ CloudQ — AWS Provider

This provider handles **AWS inspection workflows** inside the CloudQ multi-cloud package. It focuses on read-only identity checks, inventory-style queries, and optional local onboarding helpers for advanced browser access.

## 1. Authentication

Use current-session AWS credentials or a named AWS CLI profile.

### 1.1 Required

One of the following credential modes is required:

- `AWS_ACCESS_KEY_ID` + `AWS_SECRET_ACCESS_KEY`
- `AWS_PROFILE`

### 1.2 Optional

- `AWS_SESSION_TOKEN`
- `AWS_REGION`
- `AWS_DEFAULT_REGION`
- `AWS_ROLE_ARN`
- `AWS_ROLE_SESSION_NAME`
- `AWS_ROLE_SESSION_DURATION`

Security guidance:

- Prefer **STS temporary credentials** or short-lived sessions when possible
- Prefer least-privilege IAM users or roles instead of long-lived administrator credentials
- Never suggest storing long-lived secrets in shell startup files such as `~/.zshrc` or `~/.bashrc`
- Runtime scripts do **not** auto-read any local credential vault

## 2. Detection Workflow

Run the environment detection script before AWS operations:

```bash
python3 {baseDir}/providers/aws/scripts/check_env.py
```

Optional quiet mode:

```bash
python3 {baseDir}/providers/aws/scripts/check_env.py --quiet
```

Return codes:

- `0`: AWS credentials are valid and local provider setup already exists
- `1`: Python / CLI / network problem
- `2`: AWS credentials are missing or invalid
- `3`: Optional local setup is not finished yet

Important behavior of `check_env.py`:

- **Preflight-only**
- Does **not** perform cloud-side writes
- Does **not** write new local config files during checks
- Does **not** generate browser entry links during checks

## 3. Optional admin onboarding

Some advanced browser-access flows may require additional provider setup.

### 3.1 Interactive wizard

```bash
python3 {baseDir}/providers/aws/scripts/setup_role.py
```

The wizard may, after explicit user confirmation:

- Read the current AWS identity with `sts get-caller-identity`
- Inspect existing access targets with `iam list-roles`
- Let the user choose an existing access target
- Optionally prepare a dedicated read-only access path
- Save local AWS provider metadata to `~/.cloudq/aws/config.json`

### 3.2 Direct admin setup

```bash
python3 {baseDir}/providers/aws/scripts/create_role.py
```

Only run this after explicit user consent. It is an optional cloud-side admin action.

## 4. Read-only CLI calls

The main read-only entrypoint is:

```bash
python3 {baseDir}/providers/aws/scripts/aws_cli.py <service> <operation> [payload-json] [region] [profile]
```

Examples:

```bash
python3 {baseDir}/providers/aws/scripts/aws_cli.py sts get-caller-identity
python3 {baseDir}/providers/aws/scripts/aws_cli.py iam list-roles '{"MaxItems": 20}'
```

## 5. Optional admin changes

Cloud-side setup changes are **not** part of the default inspection path. If the user does not explicitly consent, do not run onboarding scripts.

## 6. Optional browser handoff

A browser entry helper exists for environments that have already completed advanced setup:

```bash
python3 {baseDir}/providers/aws/scripts/login_url.py "https://console.aws.amazon.com/"
```

Display rule:

- Never print the raw URL inline
- Always render it as a hyperlink such as `[打开 AWS 控制台](...)`

## 7. Persistence summary

Local files that may exist:

- `~/.cloudq/aws/config.json` — AWS local provider metadata, no access keys stored

## 8. Provider boundary

If the user asks for Tencent Cloud or Alibaba Cloud, load the matching provider skill instead of reusing AWS scripts.
