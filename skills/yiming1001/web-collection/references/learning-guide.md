# Web Collection Learning Guide

Use one unified rule set:

1. Never ask for configuration that is already present in environment variables.
2. Local and cloud share the same recommended defaults and overall collection flow.
3. Cloud only adds two extra required values: `id` and `token`.
4. Local mode may only call `scripts/collect_and_export_loop.sh`.
5. Cloud mode may only call `scripts/cloud_dispatch_loop.sh`.

## Asking Rules

Ask only for user-facing defaults that are still missing after checking:

- `defaultExportMode`
- `defaultMaxItems`
- `defaultFetchDetail`
- `defaultDetailSpeed`
- `defaultCloudDeviceId` in cloud mode only
- `defaultCloudToken` in cloud mode only

Do not ask for:

- `WEB_COLLECTION_CONNECTION_MODE`
- `WEB_COLLECTION_BRIDGE_URL`
- `WEB_COLLECTION_CLOUD_BASE_URL`
- `WEB_COLLECTION_CLOUD_DEVICE_ID` when already present
- `WEB_COLLECTION_CLOUD_TOKEN` when already present
- `WEB_COLLECTION_BRIDGE_CMD`

## Shared Flow

1. Run `scripts/preflight_check.sh`
2. Persist any user-provided defaults if this turn supplies them
3. Ask only for missing user-facing values
4. Build the payload
5. Dispatch through the mode-specific script only
