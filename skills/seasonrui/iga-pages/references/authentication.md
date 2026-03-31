# Authentication

## Obtaining AK/SK

Get your Access Key (AK) and Secret Key (SK) from the Volcengine IAM console: <https://console.volcengine.com/iam/keymanage>

## Commands

```bash
iga login                                        # interactive prompt for AK/SK
iga login --accessKey <ak> --secretKey <sk>      # non-interactive
iga logout                                       # remove stored credentials
```

## Credential Resolution

Credentials are resolved in priority order: **flags → env vars → `~/.iga/auth.json`**.

- **TTY** (no credentials found): interactive prompt for Access Key and Secret Key
- **Non-TTY** (no credentials found): exits with error

## Credential File

```json
// ~/.iga/auth.json
{
  "type": "aksk",
  "accessKey": "<AK>",
  "secretKey": "<SK>"
}
```

## Logout

`iga logout` deletes `~/.iga/auth.json`.

## Validate Without Saving

```bash
iga login --accessKey <ak> --secretKey <sk> --check
```

Useful for credential rotation testing. Exits 0 if valid, 1 if invalid.
