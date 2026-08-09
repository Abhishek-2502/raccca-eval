"""LiteLLM-backed provider implementation."""

from __future__ import annotations

import asyncio
import time
from typing import Any, TypeVar

import litellm
from pydantic import BaseModel

from raccca_eval.exceptions import RacccaProviderError
from raccca_eval.providers.base import LLMCompletion
from raccca_eval.utils.json_recovery import parse_model_response

T = TypeVar("T", bound=BaseModel)


class LiteLLMProvider:
    """Unified LLM provider using LiteLLM."""

    def __init__(
        self,
        *,
        model: str,
        api_base: str | None = None,
        api_key: str | None = None,
        temperature: float = 0.0,
        timeout_seconds: int = 60,
    ) -> None:
        self.model = model
        self.api_base = api_base
        self.api_key = api_key
        self.temperature = temperature
        self.timeout_seconds = timeout_seconds

    def _build_kwargs(self) -> dict[str, Any]:
        kwargs: dict[str, Any] = {
            "model": self.model,
            "temperature": self.temperature,
            "timeout": self.timeout_seconds,
        }
        if self.api_base:
            kwargs["api_base"] = self.api_base
        if self.api_key:
            kwargs["api_key"] = self.api_key
        return kwargs

    def _build_messages(self, *, system: str, user: str) -> list[dict[str, str]]:
        return [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ]

    def _to_completion(self, response: Any, *, latency_ms: float) -> LLMCompletion:
        try:
            content = response.choices[0].message.content or ""
            usage = getattr(response, "usage", None)
            prompt_tokens = int(getattr(usage, "prompt_tokens", 0) or 0)
            completion_tokens = int(getattr(usage, "completion_tokens", 0) or 0)
            total_tokens = int(getattr(usage, "total_tokens", 0) or 0)
            model = str(getattr(response, "model", self.model) or self.model)
        except (AttributeError, IndexError, TypeError) as exc:
            raise RacccaProviderError(
                "Unexpected response format from LLM provider.",
                provider=self.model,
            ) from exc

        return LLMCompletion(
            content=content,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total_tokens,
            latency_ms=latency_ms,
            model=model,
        )

    def _raise_provider_error(self, exc: Exception) -> None:
        status_code = getattr(exc, "status_code", None)
        raise RacccaProviderError(
            str(exc),
            provider=self.model,
            status_code=int(status_code) if status_code is not None else None,
        ) from exc

    def complete_structured(
        self,
        *,
        system: str,
        user: str,
        output_model: type[T],
    ) -> tuple[T, LLMCompletion]:
        kwargs = self._build_kwargs()
        messages = self._build_messages(system=system, user=user)
        schema = output_model.model_json_schema()
        response_format = {
            "type": "json_schema",
            "json_schema": {
                "name": output_model.__name__,
                "schema": schema,
                "strict": True,
            },
        }

        started = time.perf_counter()
        try:
            response = litellm.completion(
                **kwargs,
                messages=messages,
                response_format=response_format,
            )
        except Exception as exc:
            self._raise_provider_error(exc)

        latency_ms = (time.perf_counter() - started) * 1000
        completion = self._to_completion(response, latency_ms=latency_ms)

        try:
            parsed = output_model.model_validate_json(completion.content)
        except Exception:
            parsed = parse_model_response(completion.content, output_model)

        return parsed, completion

    async def acomplete_structured(
        self,
        *,
        system: str,
        user: str,
        output_model: type[T],
    ) -> tuple[T, LLMCompletion]:
        return await asyncio.to_thread(
            self.complete_structured,
            system=system,
            user=user,
            output_model=output_model,
        )
