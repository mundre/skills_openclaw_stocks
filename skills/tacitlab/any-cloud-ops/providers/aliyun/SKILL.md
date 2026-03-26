# ☁️ CloudQ — Alibaba Cloud Provider

This provider handles **Alibaba Cloud inspection workflows** inside the CloudQ multi-cloud package. It focuses on read-only identity checks, inventory-style queries, and optional local onboarding helpers for advanced browser access.

## 1. Authentication

Use current-session Alibaba Cloud credentials or a named Alibaba Cloud CLI profile.

### 1.1 Required

One of the following credential modes is required:

- `ALIBABA_CLOUD_ACCESS_KEY_ID` + `ALIBABA_CLOUD_ACCESS_KEY_SECRET`
- `ALIBABA_CLOUD_PROFILE`

### 1.2 Optional

- `ALIBABA_CLOUD_SECURITY_TOKEN`
- `ALIBABA_CLOUD_REGION_ID`
- `ALIBABA_CLOUD_ROLE_ARN`
- `ALIBABA_CLOUD_ROLE_SESSION_NAME`
- `ALIBABA_CLOUD_ROLE_SESSION_DURATION`
- `ALIBABA_CLOUD_SSO_SIGN_IN_URL`

Security guidance:

- Prefer **STS temporary credentials** or short-lived sessions when possible
- Prefer least-privilege RAM users or roles instead of long-lived administrator credentials
- Never suggest storing long-lived secrets in shell startup files such as `~/.zshrc` or `~/.bashrc`
- Runtime scripts do **not** auto-read any local credential vault

## 2. Detection Workflow

Run the environment detection script before Alibaba Cloud operations:

```bash
python3 {baseDir}/providers/aliyun/scripts/check_env.py
```

Optional quiet mode:

```bash
python3 {baseDir}/providers/aliyun/scripts/check_env.py --quiet
```

Return codes:

- `0`: Alibaba Cloud credentials are valid and local provider setup already exists
- `1`: Python / CLI / network problem
- `2`: Alibaba Cloud credentials are missing or invalid
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
python3 {baseDir}/providers/aliyun/scripts/setup_role.py
```

The wizard may, after explicit user confirmation:

- Read the current Alibaba Cloud identity with `sts GetCallerIdentity`
- Inspect existing access targets with `ram ListRoles`
- Let the user choose an existing access target
- Optionally prepare a dedicated read-only access path
- Save local Alibaba Cloud provider metadata to `~/.cloudq/aliyun/config.json`

### 3.2 Direct admin setup

```bash
python3 {baseDir}/providers/aliyun/scripts/create_role.py
```

Only run this after explicit user consent. It is an optional cloud-side admin action.

## 4. Read-only CLI calls

The main read-only entrypoint is:

```bash
python3 {baseDir}/providers/aliyun/scripts/aliyun_cli.py <product> <Action> [payload-json] [region] [profile]
```

Examples:

```bash
python3 {baseDir}/providers/aliyun/scripts/aliyun_cli.py sts GetCallerIdentity
python3 {baseDir}/providers/aliyun/scripts/aliyun_cli.py ram ListRoles '{"MaxItems": 20}'
```

## 5. Optional admin changes

Cloud-side setup changes are **not** part of the default inspection path. If the user does not explicitly consent, do not run onboarding scripts.

## 6. Optional browser handoff

A browser entry helper exists for environments that have already completed advanced setup:

```bash
python3 {baseDir}/providers/aliyun/scripts/login_url.py "https://home.console.aliyun.com/"
```

This helper depends on `ALIBABA_CLOUD_SSO_SIGN_IN_URL` or a previously saved sign-in entry in `~/.cloudq/aliyun/config.json`.

Display rule:

- Never print the raw URL inline
- Always render it as a hyperlink such as `[打开阿里云登录入口](...)`

## 7. Persistence summary

Local files that may exist:

- `~/.cloudq/aliyun/config.json` — Alibaba Cloud local provider metadata, no access keys stored

## 8. Provider boundary

If the user asks for Tencent Cloud or AWS, load the matching provider skill instead of reusing Alibaba Cloud scripts.
