# Local CLI Mode Reference

Use this when MCP is unavailable.

## Steps

### 1. Generate swap page

```bash
python3 scripts/trader_cli.py swap-page \
  --from ETH --to USDT --amount 0.001 \
  --wallet 0xUserWalletAddress \
  -o /tmp/swap.html --json
```

### 2. Upload to hosting

```bash
SWAP_URL=$(curl -s -F "reqtype=fileupload" -F "time=72h" \
  -F "fileToUpload=@/tmp/swap.html" \
  https://litterbox.catbox.moe/resources/internals/api.php)
```

### 3. Generate QR code

```python
import qrcode
qr = qrcode.QRCode(box_size=10, border=3)
qr.add_data(SWAP_URL)
qr.make(fit=True)
img = qr.make_image(fill_color='#00ffaa', back_color='#0a0e14')
img.save('/tmp/swap_qr.png')
```

### 4. Send trade preview

Use the same message template as MCP mode.

## Configuration

```yaml
# ~/.web3-trader/config.yaml
api_keys:
  zeroex: "YOUR_API_KEY"
chains:
  default: ethereum
risk:
  max_slippage: 0.5
  max_amount_usdt: 10000
```
