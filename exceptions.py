"""
Custom exceptions for the Pexels SDK.
"""


class PexelsError(Exception):
    """Base exception for all Pexels SDK errors."""

    def __init__(self, message: str, status_code: int | None = None, response_body: dict | None = None):
        super().__init__(message)
        self.status_code = status_code
        self.response_body = response_body or {}


class PexelsAuthenticationError(PexelsError):
    """Raised when the API key is invalid or missing (HTTP 401)."""


class PexelsRateLimitError(PexelsError):
    """
    Raised when the rate limit has been exceeded (HTTP 429).

    Attributes:
        retry_after: Seconds to wait before retrying (from Retry-After header).
        limit: The rate limit ceiling for this period.
        remaining: Remaining requests in this period.
        reset: Unix timestamp when the limit resets.
    """

    def __init__(
        self,
        message: str,
        status_code: int | None = None,
        response_body: dict | None = None,
        retry_after: int | None = None,
        limit: int | None = None,
        remaining: int | None = None,
        reset: int | None = None,
    ):
        super().__init__(message, status_code, response_body)
        self.retry_after = retry_after
        self.limit = limit
        self.remaining = remaining
        self.reset = reset


class PexelsNotFoundError(PexelsError):
    """Raised when a resource is not found (HTTP 404)."""


class PexelsServerError(PexelsError):
    """Raised when the Pexels API returns a 5xx error."""
