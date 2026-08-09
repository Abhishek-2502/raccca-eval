"""LLM provider protocol."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, TypeVar

from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


@dataclass(frozen=True, slots=True)
class LLMCompletion:
    """Normalized LLM completion response."""

    content: str
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    latency_ms: float = 0.0
    model: str = ""


class LLMProvider(Protocol):
    """Protocol for LLM backends used by the judge engine."""

    async def acomplete_structured(
        self,
        *,
        system: str,
        user: str,
        output_model: type[T],
    ) -> tuple[T, LLMCompletion]:
        """Async structured completion."""
        ...

    def complete_structured(
        self,
        *,
        system: str,
        user: str,
        output_model: type[T],
    ) -> tuple[T, LLMCompletion]:
        """Sync structured completion."""
        ...
