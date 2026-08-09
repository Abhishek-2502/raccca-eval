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
