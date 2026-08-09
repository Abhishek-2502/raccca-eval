"""Retry helpers for LLM provider calls."""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import TypeVar

from tenacity import (
    AsyncRetrying,
    Retrying,
    retry_if_exception,
    stop_after_attempt,
    wait_exponential,
)

from raccca_eval.exceptions import RacccaProviderError

T = TypeVar("T")


def _is_retryable(exc: BaseException) -> bool:
    if isinstance(exc, RacccaProviderError):
        if exc.status_code is None:
            return True
        return exc.status_code in {408, 429, 500, 502, 503, 504}
    return False


def run_with_retry(
    func: Callable[[], T],
    *,
    max_retries: int,
    min_wait: float = 1.0,
    max_wait: float = 10.0,
) -> T:
    retryer = Retrying(
        retry=retry_if_exception(_is_retryable),
        stop=stop_after_attempt(max_retries),
        wait=wait_exponential(multiplier=min_wait, min=min_wait, max=max_wait),
        reraise=True,
    )
    return retryer(func)


async def run_with_retry_async(
    func: Callable[[], Awaitable[T]],
    *,
    max_retries: int,
    min_wait: float = 1.0,
    max_wait: float = 10.0,
) -> T:
    retryer = AsyncRetrying(
        retry=retry_if_exception(_is_retryable),
        stop=stop_after_attempt(max_retries),
        wait=wait_exponential(multiplier=min_wait, min=min_wait, max=max_wait),
        reraise=True,
    )
    return await retryer(func)
