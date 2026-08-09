"""Unit tests for custom exceptions."""

from raccca_eval.exceptions import RacccaProviderError


def test_provider_error_stores_metadata() -> None:
    err = RacccaProviderError("request failed", provider="openai", status_code=503)
    assert str(err) == "request failed"
    assert err.provider == "openai"
    assert err.status_code == 503
