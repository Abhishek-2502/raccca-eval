"""Unit tests for RacccaEvaluator."""

from raccca_eval.config.settings import RacccaSettings
from raccca_eval.evaluator import RacccaEvaluator
from raccca_eval.judge.engine import JudgeEngine
from raccca_eval.models.request import EvaluationRequest
from tests.helpers import MockLLMProvider


def test_evaluator_from_settings(monkeypatch, sample_judge_output) -> None:
    monkeypatch.setenv("RACCCA_JUDGE_MODEL", "mock-model")

    evaluator = RacccaEvaluator.from_settings()
    assert evaluator.model == "mock-model"


def test_evaluate_batch_with_mock(monkeypatch, sample_request, sample_judge_output) -> None:
    settings = RacccaSettings(judge_model="mock-model", max_retries=1)
    evaluator = RacccaEvaluator(settings=settings)

    mock_provider = MockLLMProvider(sample_judge_output)
    evaluator._engine = JudgeEngine(provider=mock_provider, settings=settings)

    results = evaluator.evaluate_batch([sample_request, sample_request], concurrency=2)
    assert len(results) == 2
    assert results[0].overall_score >= 1.0
