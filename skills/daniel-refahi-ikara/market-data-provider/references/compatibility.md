# Compatibility policy

## Stability target
This foundation skill should keep installation and factory usage stable across minor releases.

## Stable surface
The following should remain stable unless a major release is made:
- skill name: `market-data-provider`
- environment variable `MARKET_DATA_PROVIDER`
- EODHD credential env variables
- import path: `market_data_provider.factory`
- factory function: `create_market_data_provider()`

## Allowed changes in minor releases
- add new providers
- add optional model fields
- add new helper scripts
- improve documentation and release process

## Breaking changes
Any of the following requires a major version bump:
- renaming package/import paths
- removing provider support
- changing required env variable names
- changing smoke test invocation path
