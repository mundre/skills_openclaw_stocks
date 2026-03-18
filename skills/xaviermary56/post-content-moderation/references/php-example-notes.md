# PHP Example Notes

Use this reference when the user wants to adapt the bundled PHP example to their own backend.

## Bundled files

- `scripts/config.php`
- `scripts/moderation_support.php`
- `scripts/php_xai_client_example.php`

## Style direction

This demo intentionally uses:
- PHP 7.3 compatible syntax
- short array syntax `[]`
- object-oriented structure
- small command entry files
- separated config and support classes
- a migration-friendly engineering skeleton
- DTO-style wrappers for post/comment/result data

## Structure

### `config.php`

Keep configuration in one place:
- x.ai endpoint
- api key
- model name
- pull interface url
- callback url
- timeout settings
- whitelist
- custom rules

### `moderation_support.php`

Keep shared support code in classes:
- constants
- custom exceptions
- logger interface + implementation
- trace id builder
- retry and callback retry policy
- config loader
- rule provider interface + loader
- HTTP client
- stdin input reader
- media inspector interface + placeholder
- DTO classes
- result builder and formatter
- app context

### `php_xai_client_example.php`

Keep moderation responsibilities in one class:
- post moderation request
- comment moderation request
- callback request
- model response parsing

## Production advice

- do not store real API keys in git
- keep `temperature = 0`
- log raw model failures separately from content rejections
- if full-auto strict mode is enabled, fail closed on model/network/media errors
- if callback fails, retry with backoff instead of dropping the result silently
- replace placeholder media inspection with real image/video preprocessing
- if moving into Yaf, split current support file into constants, dto, contracts, client, formatter, and provider directories
