"""Test helpers and mocks."""

from __future__ import annotations

from raccca_eval.models.judge_output import JudgeEvaluationOutput
from raccca_eval.providers.base import LLMCompletion


class MockLLMProvider:
    """In-memory mock provider for unit tests."""

    def __init__(self, output: JudgeEvaluationOutput, *, model: str = "mock-model") -> None:
        self.output = output
        self.model = model
        self.calls: list[tuple[str, str]] = []

    def complete_structured(self, *, system: str, user: str, output_model: type):
        self.calls.append((system, user))
        completion = LLMCompletion(
            content=output_model.model_validate(self.output.model_dump()).model_dump_json(),
            prompt_tokens=100,
            completion_tokens=50,
            total_tokens=150,
            latency_ms=10.0,
            model=self.model,
        )
        return self.output, completion

    async def acomplete_structured(self, *, system: str, user: str, output_model: type):
        return self.complete_structured(system=system, user=user, output_model=output_model)
