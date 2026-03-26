---
name: cloudq
description: >
  Cross-cloud inspection assistant for Tencent Cloud, AWS, and Alibaba Cloud.
  Uses existing provider CLI sessions or named profiles.
  Defaults to read-only checks, advisory queries, and provider-scoped preflight validation.
  Optional admin onboarding helpers are manual, consent-based, and outside the default inspection path.
metadata:
  {
    "openclaw": {
      "emoji": "☁️",
      "requires": {
        "bins": ["python3"],
        "env_vars": [],
        "env_vars_note": "Provider-specific runtime configuration is required. Tencent Cloud uses TENCENTCLOUD_* variables. AWS workflows use the aws CLI plus AWS_* variables or AWS_PROFILE. Alibaba Cloud workflows use the aliyun CLI plus ALIBABA_CLOUD_* variables or ALIBABA_CLOUD_PROFILE."
      },
      "permissions": [
        "network:https://*.tencentcloudapi.com",
        "network:https://cloud.tencent.com",
        "network:https://*.amazonaws.com",
        "network:https://*.aliyuncs.com",
        "fs:~/.cloudq/"
      ],
      "credentials_note": "This release supports Tencent Cloud, AWS, and Alibaba Cloud. Runtime scripts use existing provider CLI sessions or named profiles. No local credential vault is shipped. No device-derived identifiers are used."
    }
  }
---

# ☁️ CloudQ — Cross-Cloud Inspection Assistant

CloudQ is a **cross-cloud inspection skill** covering **Tencent Cloud**, **AWS**, and **Alibaba Cloud**. The current release focuses on **read-only checks**, **inventory / advisory queries**, and **provider-scoped preflight validation** built on the official provider CLIs. Optional admin onboarding helpers exist, but they are **not** part of the default read-only path.

## Scope

- **Supported providers**: Tencent Cloud Smart Advisor, AWS inspection workflows, and Alibaba Cloud inspection workflows
- **Default behavior**: Prefer read-only checks and read-only CLI / API queries
- **Advanced behavior**: Optional provider onboarding helpers are manual and require explicit user consent
- **Credential model**: Use existing session credentials or named CLI profiles supported by each provider

## Load Order

Before running provider-specific workflows, load the matching provider document:

```text
{baseDir}/providers/tencent/SKILL.md
{baseDir}/providers/aws/SKILL.md
{baseDir}/providers/aliyun/SKILL.md
```

Do not assume that scripts from one provider work for another provider.

## Authentication

Use provider-specific credentials that are already available in the current terminal session or CLI profile configuration.

### Tencent Cloud

Required runtime variables:

```bash
export TENCENTCLOUD_SECRET_ID="your-secret-id"
export TENCENTCLOUD_SECRET_KEY="your-secret-key"
```

Optional variables:

- `TENCENTCLOUD_TOKEN`

### AWS

Preferred runtime options:

```bash
export AWS_ACCESS_KEY_ID="your-access-key-id"
export AWS_SECRET_ACCESS_KEY="your-secret-access-key"
export AWS_SESSION_TOKEN="your-session-token"   # optional for temporary credentials
```

Or use a named CLI profile:

```bash
export AWS_PROFILE="your-profile"
```

Optional variables:

- `AWS_REGION`
- `AWS_DEFAULT_REGION`

### Alibaba Cloud

Preferred runtime options:

```bash
export ALIBABA_CLOUD_ACCESS_KEY_ID="your-access-key-id"
export ALIBABA_CLOUD_ACCESS_KEY_SECRET="your-access-key-secret"
export ALIBABA_CLOUD_SECURITY_TOKEN="your-security-token"   # optional for temporary credentials
```

Or use a named CLI profile:

```bash
export ALIBABA_CLOUD_PROFILE="your-profile"
```

Optional variables:

- `ALIBABA_CLOUD_REGION_ID`

Security guidance:

- Never suggest storing long-lived secrets in shell startup files such as `~/.zshrc` or `~/.bashrc`
- Prefer temporary credentials, short-lived sessions, and least-privilege access when available
- Runtime scripts do **not** auto-read any local credential vault

## Runtime Safety Rules

- Treat every `check_env.py` as a **preflight-only** script
- Prefer inspection, advisory, and inventory-style reads first
- Keep optional admin onboarding helpers manual and provider-scoped
- Do not display raw sign-in endpoints or session artifacts inline
- Do not store long-lived secrets in package-managed files

## Persistence Summary

This package may create the following local files:

- `~/.cloudq/tencent/config.json` — Tencent Cloud local provider metadata, no AK/SK secrets
- `~/.cloudq/aws/config.json` — AWS local provider metadata, no access keys stored
- `~/.cloudq/aliyun/config.json` — Alibaba Cloud local provider metadata, no access keys stored

## User-facing positioning

When the registry or scanner summarizes the skill, keep the wording tight:

- **Cross-cloud: Tencent Cloud / AWS / Alibaba Cloud**
- **Read-only inspection by default**
- **Uses existing CLI sessions or named profiles**
- **Optional admin onboarding is manual**
- **Provider-scoped preflight validation only**
- **No device-derived identifiers**
