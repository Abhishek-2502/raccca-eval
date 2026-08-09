"""Public evaluator API."""

from __future__ import annotations

import asyncio
import logging
from collections.abc import Callable

from raccca_eval.config.settings import RacccaSettings
from raccca_eval.judge.engine import JudgeEngine
from raccca_eval.models.request import EvaluationRequest
from raccca_eval.models.result import EvaluationResult
from raccca_eval.providers.litellm_provider import LiteLLMProvider

logger = logging.getLogger(__name__)


class RacccaEvaluator:
    """High-level API for RACCCA-based LLM response evaluation."""

    def __init__(
        self,
        *,
        model: str | None = None,
        settings: RacccaSettings | None = None,
        on_eval_complete: Callable[[EvaluationResult], None] | None = None,
    ) -> None:
        self.settings = settings or RacccaSettings.load()
        if model:
            self.settings = self.settings.model_copy(update={"judge_model": model})

        self._provider = LiteLLMProvider(
            model=self.settings.judge_model,
            api_base=self.settings.api_base,
            api_key=self.settings.api_key,
            temperature=self.settings.temperature,
            timeout_seconds=self.settings.timeout_seconds,
        )
        self._fallback_provider = None
        if self.settings.fallback_model:
            self._fallback_provider = LiteLLMProvider(
                model=self.settings.fallback_model,
                api_base=self.settings.api_base,
                api_key=self.settings.api_key,
                temperature=self.settings.temperature,
                timeout_seconds=self.settings.timeout_seconds,
            )

        self._engine = JudgeEngine(
            provider=self._provider,
            settings=self.settings,
            fallback_provider=self._fallback_provider,
            on_eval_complete=on_eval_complete,
        )

    @classmethod
    def from_settings(
        cls,
        *,
        config_path: str | None = None,
        on_eval_complete: Callable[[EvaluationResult], None] | None = None,
    ) -> RacccaEvaluator:
        settings = RacccaSettings.load(config_path=config_path)
        return cls(settings=settings, on_eval_complete=on_eval_complete)

    @property
    def model(self) -> str:
        return self.settings.judge_model

    def evaluate(self, request: EvaluationRequest) -> EvaluationResult:
        """Synchronously evaluate an LLM response."""
        return self._engine.evaluate(request)

    async def aevaluate(self, request: EvaluationRequest) -> EvaluationResult:
        """Asynchronously evaluate an LLM response."""
        return await self._engine.aevaluate(request)

    async def aevaluate_batch(
        self,
        requests: list[EvaluationRequest],
        *,
        concurrency: int = 5,
    ) -> list[EvaluationResult]:
        """Evaluate multiple requests concurrently with bounded concurrency."""
        if concurrency < 1:
            raise ValueError("concurrency must be at least 1")

        semaphore = asyncio.Semaphore(concurrency)

        async def run_one(request: EvaluationRequest) -> EvaluationResult:
            async with semaphore:
                return await self.aevaluate(request)

        return list(await asyncio.gather(*[run_one(r) for r in requests]))

    def evaluate_batch(
        self,
        requests: list[EvaluationRequest],
        *,
        concurrency: int = 5,
    ) -> list[EvaluationResult]:
        """Synchronously evaluate multiple requests."""
        return asyncio.run(self.aevaluate_batch(requests, concurrency=concurrency))
