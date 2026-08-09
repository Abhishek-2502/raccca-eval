"""Unit tests for EvaluationRequest validation."""

import pytest
from pydantic import ValidationError

from raccca_eval.models.criteria import RacccaCriterion
from raccca_eval.models.request import EvaluationRequest


def test_request_defaults_to_all_criteria() -> None:
    request = EvaluationRequest(
        query="Hello?",
        response="Hi there.",
        audience="general audience",
    )
    assert len(request.criteria_to_evaluate) == 6


def test_request_requires_audience_for_clarity() -> None:
    with pytest.raises(ValidationError, match="audience is required"):
        EvaluationRequest(
            query="Explain quantum computing.",
            response="Quantum computing uses qubits.",
            criteria_to_evaluate=[RacccaCriterion.CLARITY],
        )


def test_ground_truth_warning_without_reference() -> None:
    request = EvaluationRequest(
        query="What is RACCCA?",
        response="A framework for evaluation.",
        criteria_to_evaluate=[RacccaCriterion.ACCURACY],
    )
    assert request.ground_truth_warning is not None
    assert "without context or reference_answer" in request.ground_truth_warning


def test_deduplicates_criteria() -> None:
    request = EvaluationRequest(
        query="Q",
        response="A",
        criteria_to_evaluate=[
            RacccaCriterion.RELEVANCE,
            RacccaCriterion.RELEVANCE,
            RacccaCriterion.ACCURACY,
        ],
        reference_answer="A",
    )
    assert request.criteria_to_evaluate.count(RacccaCriterion.RELEVANCE) == 1
