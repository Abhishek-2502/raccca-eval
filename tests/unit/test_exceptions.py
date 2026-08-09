"""Unit tests for custom exceptions."""

from raccca_eval.exceptions import RacccaParseError, RacccaProviderError


def test_provider_error_stores_metadata() -> None:
    err = RacccaProviderError("request failed", provider="openai", status_code=503)
    assert str(err) == "request failed"
    assert err.provider == "openai"
    assert err.status_code == 503


def test_parse_error_stores_raw_response() -> None:
    err = RacccaParseError("failed", raw_response='{"bad": json}')
    assert str(err) == "failed"
    assert err.raw_response == '{"bad": json}'
