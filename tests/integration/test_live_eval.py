"""Integration tests requiring live LLM API keys."""

import pytest

from raccca_eval import EvaluationRequest, RacccaCriterion, RacccaEvaluator


@pytest.mark.integration
def test_live_openai_evaluation() -> None:
    evaluator = RacccaEvaluator(model="gpt-4o-mini")
    request = EvaluationRequest(
        query="What is the capital of France?",
        response="The capital of France is Paris.",
        criteria_to_evaluate=[
            RacccaCriterion.RELEVANCE,
            RacccaCriterion.ACCURACY,
            RacccaCriterion.COMPLETENESS,
        ],
        reference_answer="Paris is the capital of France.",
        audience="general audience",
    )

    result = evaluator.evaluate(request)

    assert result.overall_score >= 4.0
    assert result.scores["relevance"].score >= 4
    assert result.usage.total_tokens > 0
