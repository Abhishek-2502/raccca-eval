"""Shared pytest fixtures."""

from __future__ import annotations

import json
import os
from pathlib import Path

import pytest

from raccca_eval.config.settings import RacccaSettings
from raccca_eval.models.criteria import RacccaCriterion
from raccca_eval.models.judge_output import JudgeCriterionOutput, JudgeEvaluationOutput
from raccca_eval.models.request import EvaluationRequest

FIXTURES_DIR = Path(__file__).resolve().parent / "fixtures"


@pytest.fixture
def sample_request() -> EvaluationRequest:
    return EvaluationRequest(
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


@pytest.fixture
def sample_judge_output() -> JudgeEvaluationOutput:
    return JudgeEvaluationOutput(
        scores=[
            JudgeCriterionOutput(
                criterion=RacccaCriterion.RELEVANCE,
                score=5,
                rationale="Directly answers the question.",
            ),
            JudgeCriterionOutput(
                criterion=RacccaCriterion.ACCURACY,
                score=5,
                rationale="Factually correct.",
            ),
            JudgeCriterionOutput(
                criterion=RacccaCriterion.COMPLETENESS,
                score=4,
                rationale="Covers the main point but lacks extra context.",
            ),
        ],
        summary="Strong, accurate, concise answer.",
    )


@pytest.fixture
def sample_requests_from_file() -> list[dict]:
    with (FIXTURES_DIR / "sample_requests.json").open(encoding="utf-8") as handle:
        return json.load(handle)


@pytest.fixture
def test_settings() -> RacccaSettings:
    return RacccaSettings(
        judge_model="gpt-4o-mini",
        temperature=0.0,
        max_retries=1,
        strategy="single",
    )


def pytest_configure(config: pytest.Config) -> None:
    config.addinivalue_line(
        "markers",
        "integration: marks tests that require live LLM API keys",
    )


def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:
    if os.getenv("OPENAI_API_KEY"):
        return
    skip_integration = pytest.mark.skip(reason="OPENAI_API_KEY not set")
    for item in items:
        if "integration" in item.keywords:
            item.add_marker(skip_integration)

