"""Unit tests for retry helpers."""

from raccca_eval.exceptions import RacccaProviderError
from raccca_eval.utils.retry import run_with_retry


def test_run_with_retry_on_retryable_provider_error() -> None:
    attempts = 0

    def func() -> str:
        nonlocal attempts
        attempts += 1
        if attempts < 2:
            raise RacccaProviderError("rate limited", status_code=429)
        return "ok"

    assert run_with_retry(func, max_retries=3) == "ok"
    assert attempts == 2
