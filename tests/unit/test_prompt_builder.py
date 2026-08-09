"""Unit tests for RubricPromptBuilder."""

from raccca_eval.judge.prompt_builder import RubricPromptBuilder
from raccca_eval.models.criteria import RacccaCriterion
from raccca_eval.models.request import EvaluationRequest


def test_prompt_includes_query_and_response() -> None:
    request = EvaluationRequest(
        query="What is Python?",
        response="Python is a programming language.",
        criteria_to_evaluate=[RacccaCriterion.RELEVANCE],
        reference_answer="Python is a high-level programming language.",
    )
    prompt = RubricPromptBuilder().build(request)

    assert "What is Python?" in prompt.user
    assert "Python is a programming language." in prompt.user
    assert "Relevance" in prompt.system


def test_prompt_includes_external_prompt() -> None:
    request = EvaluationRequest(
        query="Q",
        response="A",
        criteria_to_evaluate=[RacccaCriterion.RELEVANCE],
        external_prompt="Be strict about factual claims.",
        reference_answer="A",
    )
    prompt = RubricPromptBuilder().build(request)
    assert "Be strict about factual claims." in prompt.system


def test_single_criterion_prompt() -> None:
    request = EvaluationRequest(
        query="Q",
        response="A",
        criteria_to_evaluate=[RacccaCriterion.RELEVANCE, RacccaCriterion.ACCURACY],
        reference_answer="A",
    )
    prompt = RubricPromptBuilder().build_single_criterion(request, RacccaCriterion.ACCURACY)
    assert "Accuracy" in prompt.system
    assert "Relevance" not in prompt.system.split("## RACCCA Rubric")[1]
