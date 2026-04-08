class DataSourceError(Exception):
    """Base market data provider error."""


class AuthenticationError(DataSourceError):
    """Missing or invalid credentials."""


class RateLimitError(DataSourceError):
    """Provider rate limit reached."""


class SymbolNotFoundError(DataSourceError):
    """Requested symbol was not found."""


class TemporaryProviderError(DataSourceError):
    """Transient upstream/provider error."""


class SchemaMappingError(DataSourceError):
    """Unexpected provider payload shape."""
