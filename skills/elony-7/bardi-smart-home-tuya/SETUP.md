# Setup — Bardi-Tuya Smart Home

## Install Dependencies

```bash
# Debian/Ubuntu/Kali
pip install --break-system-packages tinytuya

# macOS
pip install tinytuya
```

## Configure Credentials

Set these environment variables (add to `~/.bashrc` or `~/.zshrc`):

```bash
export TUYA_ACCESS_ID="your-access-id"
export TUYA_ACCESS_SECRET="your-access-secret"
export TUYA_API_REGION="sg"  # Options: sg, cn, us, eu, in
```

### Where to Get Credentials

1. Go to [https://iot.tuya.com](https://iot.tuya.com) (international) or [https://tuyasmart.com](https://tuyasmart.com) (China)
2. Create a cloud project
3. Copy the **Access ID** and **Access Secret** from the project overview
4. Enable the "Smart Home Devices" API group

### Region Selection

| Region Code | Data Center | Where |
|-------------|-------------|-------|
| `sg` | Singapore | Southeast Asia, default |
| `us` | US West | Americas |
| `eu` | Central Europe | Europe |
| `cn` | China | China mainland |
| `in` | India | India |

## Verify Installation

```bash
python3 scripts/tuya_control.py discover
```

Should list all devices linked to your Tuya account.

## Local Network Discovery

To find devices on your local network:

```bash
python3 scripts/tuya_scan.py
```

Requires devices to be on the same network. Shows IP addresses, device IDs, and protocol versions.

## Notes

- Cloud API requires internet connection
- Local scan works without cloud credentials
- Device must be linked to your Tuya account for cloud control
- Some devices require specific API groups to be enabled in your Tuya project
