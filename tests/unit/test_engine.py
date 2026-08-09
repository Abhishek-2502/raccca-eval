"""Unit tests for JudgeEngine."""

from raccca_eval.config.settings import RacccaSettings
from raccca_eval.judge.engine import JudgeEngine
from raccca_eval.models.criteria import RacccaCriterion
from raccca_eval.models.judge_output import JudgeCriterionOutput, JudgeEvaluationOutput
from raccca_eval.models.request import EvaluationRequest
from tests.helpers import MockLLMProvider


def test_single_strategy_evaluation(sample_request, sample_judge_output) -> None:
    settings = RacccaSettings(strategy="single")
    provider = MockLLMProvider(sample_judge_output)
    engine = JudgeEngine(provider=provider, settings=settings)

    result = engine.evaluate(sample_request)

    assert result.overall_score >= 1.0
    assert "relevance" in result.scores
    assert result.scores["relevance"].score == 5
    assert result.usage.num_calls == 1


def test_per_criterion_strategy() -> None:
    request = EvaluationRequest(
        query="Q",
        response="A",
        criteria_to_evaluate=[RacccaCriterion.RELEVANCE, RacccaCriterion.ACCURACY],
        reference_answer="A",
    )
    output = JudgeEvaluationOutput(
        scores=[
            JudgeCriterionOutput(
                criterion=RacccaCriterion.RELEVANCE,
                score=4,
                rationale="Relevant.",
            )
        ],
        summary="Good.",
    )
    settings = RacccaSettings(strategy="per_criterion")
    provider = MockLLMProvider(output)
    engine = JudgeEngine(provider=provider, settings=settings)

    result = engine.evaluate(request)

    assert result.usage.num_calls == 2
    assert len(result.scores) == 2


async def test_async_evaluation(sample_request, sample_judge_output) -> None:
    settings = RacccaSettings(strategy="single")
    provider = MockLLMProvider(sample_judge_output)
    engine = JudgeEngine(provider=provider, settings=settings)

    result = await engine.aevaluate(sample_request)

    assert result.overall_score >= 1.0


async def test_async_per_criterion_strategy() -> None:
    request = EvaluationRequest(
        query="Q",
        response="A",
        criteria_to_evaluate=[RacccaCriterion.RELEVANCE, RacccaCriterion.ACCURACY],
        reference_answer="A",
    )
    output = JudgeEvaluationOutput(
        scores=[
            JudgeCriterionOutput(
                criterion=RacccaCriterion.RELEVANCE,
                score=4,
                rationale="Relevant.",
            )
        ],
        summary="Good.",
    )
    settings = RacccaSettings(strategy="per_criterion")
    provider = MockLLMProvider(output)
    engine = JudgeEngine(provider=provider, settings=settings)

    result = await engine.aevaluate(request)

    assert result.usage.num_calls == 2
    assert len(result.scores) == 2


class _FailingProvider:
    def complete_structured(self, **kwargs: object) -> tuple[JudgeEvaluationOutput, object]:
        raise RuntimeError("primary failed")

    async def acomplete_structured(self, **kwargs: object) -> tuple[JudgeEvaluationOutput, object]:
        raise RuntimeError("primary failed")


def test_fallback_provider_used_on_sync_failure(
    sample_request, sample_judge_output
) -> None:
    settings = RacccaSettings(strategy="single")
    fallback = MockLLMProvider(sample_judge_output)
    engine = JudgeEngine(
        provider=_FailingProvider(),
        settings=settings,
        fallback_provider=fallback,
    )

    result = engine.evaluate(sample_request)

    assert result.overall_score >= 1.0
    assert len(fallback.calls) == 1


async def test_fallback_provider_used_on_async_failure(
    sample_request, sample_judge_output
) -> None:
    settings = RacccaSettings(strategy="single")
    fallback = MockLLMProvider(sample_judge_output)
    engine = JudgeEngine(
        provider=_FailingProvider(),
        settings=settings,
        fallback_provider=fallback,
    )

    result = await engine.aevaluate(sample_request)

    assert result.overall_score >= 1.0
    assert len(fallback.calls) == 1


def test_ground_truth_warning_in_result(sample_judge_output) -> None:
    request = EvaluationRequest(
        query="Q",
        response="A",
        criteria_to_evaluate=[RacccaCriterion.ACCURACY],
    )
    settings = RacccaSettings(strategy="single")
    engine = JudgeEngine(provider=MockLLMProvider(sample_judge_output), settings=settings)

    result = engine.evaluate(request)

    assert result.warnings
    assert "reference_answer" in result.warnings[0]


def test_on_eval_complete_callback(sample_request, sample_judge_output) -> None:
    completed = []
    settings = RacccaSettings(strategy="single")
    engine = JudgeEngine(
        provider=MockLLMProvider(sample_judge_output),
        settings=settings,
        on_eval_complete=completed.append,
    )

    engine.evaluate(sample_request)

    assert len(completed) == 1
    assert completed[0].overall_score >= 1.0


def test_debug_includes_raw_response(sample_request, sample_judge_output) -> None:
    settings = RacccaSettings(strategy="single", debug=True)
    engine = JudgeEngine(
        provider=MockLLMProvider(sample_judge_output),
        settings=settings,
    )

    result = engine.evaluate(sample_request)

    assert result.raw_response is not None


def test_clamps_out_of_range_scores() -> None:
    output = JudgeEvaluationOutput(
        scores=[
            JudgeCriterionOutput(
                criterion=RacccaCriterion.RELEVANCE,
                score=99,
                rationale="Too high.",
            ),
        ],
        summary="Test.",
    )
    request = EvaluationRequest(
        query="Q",
        response="A",
        criteria_to_evaluate=[RacccaCriterion.RELEVANCE],
        reference_answer="A",
    )
    settings = RacccaSettings(strategy="single", scoring_scale_min=1, scoring_scale_max=5)
    engine = JudgeEngine(provider=MockLLMProvider(output), settings=settings)

    result = engine.evaluate(request)

    assert result.scores["relevance"].score == 5
