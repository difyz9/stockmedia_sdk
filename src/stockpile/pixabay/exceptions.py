"""
Custom exceptions for the Pixabay SDK.
"""


class PixabayError(Exception):
    """Base exception for all Pixabay SDK errors."""

    def __init__(
        self,
        message: str,
        status_code: int | None = None,
        response_body: dict | None = None,
    ):
        super().__init__(message)
        self.status_code = status_code
        self.response_body = response_body or {}


class PixabayAuthenticationError(PixabayError):
    """Raised when the API key is invalid or missing (HTTP 401/403)."""


class PixabayRateLimitError(PixabayError):
    """
    Raised when the rate limit has been exceeded (HTTP 429).

    Attributes:
        retry_after: Seconds to wait before retrying (from Retry-After header).
        limit: The rate limit ceiling per 60 second window.
        remaining: Remaining requests in the current window.
        reset: Seconds until the rate limit window resets.
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


class PixabayNotFoundError(PixabayError):
    """Raised when a resource is not found (HTTP 404)."""


class PixabayServerError(PixabayError):
    """Raised when the Pixabay API returns a 5xx error."""
