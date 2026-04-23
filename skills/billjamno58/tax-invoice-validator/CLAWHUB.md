# InvoiceGuard — ClawHub Listing

AI-powered invoice duplicate detection, tax compliance verification, and batch processing. Upload invoice images or text → get instant duplicate alerts and tax verification status.

## Features

- **Duplicate Detection**: Cross-check against historical records, flag potential duplicates
- **Tax Verification**: Verify invoice authenticity via tax authority databases (where supported)
- **Batch Processing**: Handle multiple invoices in one run
- **Summary Report**: JSON + markdown export

## Usage

```bash
openclaw run invoice-guard --file invoice.jpg --user-id sp_usr_xxx
```

## Pricing

Pay-per-call: **$0.01 USDT** per invoice batch run.

Credits purchased at [skillpay.me/tax-invoice-validator](https://skillpay.me/tax-invoice-validator)

## Technical Stack

- Parser: Python, Pillow, pdf2image
- AI: OpenAI GPT-4o / Anthropic Claude (user-configured API key)
- Output: JSON, Markdown

## Support

For issues or feature requests, contact the developer.
