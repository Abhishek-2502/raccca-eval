"""Custom exceptions for raccca_eval."""


class RacccaError(Exception):
    """Base exception for all RACCCA evaluation errors."""


class RacccaValidationError(RacccaError):
    """Raised when evaluation input fails validation."""


class RacccaProviderError(RacccaError):
    """Raised when the LLM provider returns an error."""

    def __init__(
        self,
        message: str,
        *,
        provider: str | None = None,
        status_code: int | None = None,
    ):
        super().__init__(message)
        self.provider = provider
        self.status_code = status_code


class RacccaParseError(RacccaError):
    """Raised when judge output cannot be parsed into structured scores."""

    def __init__(self, message: str, *, raw_response: str | None = None) -> None:
        super().__init__(message)
        self.raw_response = raw_response
