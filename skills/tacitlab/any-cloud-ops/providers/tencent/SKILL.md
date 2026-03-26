# ☁️ CloudQ — Tencent Cloud Provider

This provider handles **Tencent Cloud Smart Advisor inspection** workflows inside the CloudQ multi-cloud package. It focuses on read-only architecture inspection, advisory queries, and optional local onboarding helpers for advanced access setup.

## 1. Authentication

Use current-session environment variables.

### 1.1 Required

- `TENCENTCLOUD_SECRET_ID`
- `TENCENTCLOUD_SECRET_KEY`

### 1.2 Optional

- `TENCENTCLOUD_TOKEN`
- `TENCENTCLOUD_ROLE_ARN`
- `TENCENTCLOUD_ROLE_NAME`
- `TENCENTCLOUD_ROLE_SESSION`
- `TENCENTCLOUD_STS_DURATION`

Security guidance:

- Prefer **STS temporary credentials** when available
- Prefer a **least-privilege sub-account** instead of a long-lived root credential
- Never suggest writing secrets to shell startup files such as `~/.zshrc` or `~/.bashrc`
- Runtime scripts do **not** auto-read any locally saved credential file

## 2. Detection Workflow

Run the environment detection script before Tencent Cloud operations:

```bash
python3 {baseDir}/providers/tencent/scripts/check_env.py
```

Optional quiet mode:

```bash
python3 {baseDir}/providers/tencent/scripts/check_env.py --quiet
```

Return codes:

- `0`: Credentials are valid and local provider setup already exists
- `1`: Python/runtime or network problem
- `2`: Credentials are missing or invalid
- `3`: Optional local setup is not finished yet

Important behavior of `check_env.py`:

- **Preflight-only**
- Does **not** contact package, registry, or release services
- Does **not** auto-load locally stored credentials
- Does **not** perform cloud-side writes
- Does **not** generate browser entry links

## 3. Optional admin onboarding

Some advanced console-access flows may require additional provider setup.

### 3.1 Safe default

If `check_env.py` returns `3`, explain that advanced Tencent Cloud access is not configured yet and ask whether the user wants to run optional onboarding.

### 3.2 Interactive wizard

```bash
python3 {baseDir}/providers/tencent/scripts/setup_role.py
```

What the wizard may do after explicit user confirmation:

- Inspect current account context and available access targets
- Let the user choose an existing access target
- Optionally prepare a dedicated read-only access path for Smart Advisor usage
- Save local Tencent Cloud provider metadata to `~/.cloudq/tencent/config.json`

### 3.3 Direct admin setup

```bash
python3 {baseDir}/providers/tencent/scripts/create_role.py
```

Only run this after explicit user consent. It is an optional cloud-side admin action.

## 4. Read-only API calls

The main read-only entrypoint is:

```bash
python3 {baseDir}/providers/tencent/scripts/tcloud_api.py advisor advisor.tencentcloudapi.com <Action> 2020-07-21 '<payload>' [region]
```

Supported Smart Advisor actions documented in `references/api/`:

- `DescribeArch`
- `DescribeArchList`
- `ListDirectoryV2`
- `ListUnorganizedDirectory`
- `DescribeStrategies`
- `DescribeLastEvaluation`

Before using any action, read the corresponding document in:

```text
{baseDir}/providers/tencent/references/api/<Action>.md
```

## 5. Optional admin changes

Cloud-side setup changes are **not** part of the default inspection path. If the user does not explicitly consent, do not run onboarding scripts.

## 6. Optional browser handoff

A browser entry helper exists for environments that have already completed advanced setup:

```bash
python3 {baseDir}/providers/tencent/scripts/login_url.py "https://console.cloud.tencent.com/advisor"
```

Display rule:

- Never print the raw URL inline
- Always render it as a hyperlink such as `[打开控制台](...)`

## 7. Persistence summary

Local files that may exist:

- `~/.cloudq/tencent/config.json` — Tencent Cloud local provider metadata, no AK/SK

## 8. Provider boundary

If the user asks for AWS or Alibaba Cloud, load the matching provider skill instead of reusing Tencent Cloud scripts.
