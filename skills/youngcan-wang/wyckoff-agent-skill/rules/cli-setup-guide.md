# CLI Setup Guide

## Installation

Recommended:
```bash
pip install youngcan-wyckoff-analysis
```

Alternative (one-line):
```bash
curl -fsSL https://raw.githubusercontent.com/YoungCan-Wang/Wyckoff-Analysis/main/install.sh | bash
```

Verify: `wyckoff --version`

## Account Registration

1. Open https://wyckoff-analysis-youngcanphoenix.streamlit.app/
2. Register with email and password.
3. Login via CLI:
   ```bash
   wyckoff auth login <email> <password>
   ```
4. Verify: `wyckoff auth status`

Note: Credentials are automatically saved to `~/.wyckoff/wyckoff.json`. When the login token expires, the CLI will re-login automatically — no need to enter credentials again.

## Data Sources

At least one data source is required. Both recommended for best coverage.

### Tushare (free)

1. Register at https://tushare.pro/ and copy your token.
2. Configure:
   ```bash
   wyckoff config tushare <your_token>
   ```

### TickFlow (paid, real-time + historical)

1. Purchase at https://tickflow.org/auth/register?ref=5N4NKTCPL4
2. Copy your API key from the dashboard.
3. Configure:
   ```bash
   wyckoff config tickflow <your_api_key>
   ```

## AI Model Setup

Interactive:
```bash
wyckoff model add
```

Non-interactive:
```bash
wyckoff model set <alias> <provider> <api_key> --model <model_name>
```

Supported providers: `gemini`, `openai`, `claude`.

## CLI Command Reference

### Auth

| Command | Description |
|---|---|
| `wyckoff auth login <email> <password>` | Login |
| `wyckoff auth logout` | Logout |
| `wyckoff auth status` | Check login status |

### Model

| Command | Description |
|---|---|
| `wyckoff model list` | List configured models |
| `wyckoff model add` | Add model (interactive) |
| `wyckoff model set <name> <provider> <api_key>` | Add/update model (non-interactive) |
| `wyckoff model rm <name>` | Remove model |
| `wyckoff model default <name>` | Set default model |

### Config

| Command | Description |
|---|---|
| `wyckoff config show` | Show current config (masked) |
| `wyckoff config tushare <token>` | Set Tushare token |
| `wyckoff config tickflow <api_key>` | Set TickFlow API key |

### Portfolio

| Command | Description |
|---|---|
| `wyckoff portfolio list` | View positions and cash |
| `wyckoff portfolio add <code> <shares> <cost>` | Add/update a position |
| `wyckoff portfolio rm <code>` | Remove a position |
| `wyckoff portfolio cash <amount>` | Set available cash |

### Signal

| Command | Description |
|---|---|
| `wyckoff signal` | View today's triggered signals |
| `wyckoff signal pending` | Pending signals only |
| `wyckoff signal confirmed` | Confirmed signals only |
| `wyckoff signal --json` | JSON output |
| `wyckoff signal -n 50` | Limit results |

### Recommend

| Command | Description |
|---|---|
| `wyckoff recommend` | View today's AI recommendations |
| `wyckoff recommend --json` | JSON output |
| `wyckoff recommend -n 10` | Limit results |

### Misc

| Command | Description |
|---|---|
| `wyckoff update` | Upgrade to latest version |
| `wyckoff --version` | Print version |
| `wyckoff` | Launch interactive TUI |

## Guided Setup Flow

When guiding a new user, follow this exact order:

1. **Install** → `pip install youngcan-wyckoff-analysis`
2. **Register** → open web app to create account
3. **Login** → `wyckoff auth login`
4. **Data source** → configure at least tushare or tickflow
5. **Model** → `wyckoff model add`
6. **Ready** → user can now run `wyckoff` for TUI or use any CLI subcommand

Each step depends on the previous one. Do not skip ahead.
