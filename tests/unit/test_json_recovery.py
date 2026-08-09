"""Unit tests for JSON recovery utilities."""

import pytest

from raccca_eval.exceptions import RacccaParseError
from raccca_eval.models.criteria import RacccaCriterion
from raccca_eval.models.judge_output import JudgeCriterionOutput, JudgeEvaluationOutput
from raccca_eval.utils.json_recovery import extract_json_text, parse_model_response


def test_extract_json_from_markdown_fence() -> None:
    raw = 'Here is the result:\n```json\n{"scores": [], "summary": "ok"}\n```'
    assert extract_json_text(raw).startswith("{")


def test_parse_model_response_valid() -> None:
    output = JudgeEvaluationOutput(
        scores=[
            JudgeCriterionOutput(
                criterion=RacccaCriterion.RELEVANCE,
                score=4,
                rationale="Good answer.",
            )
        ],
        summary="Solid response.",
    )
    parsed = parse_model_response(output.model_dump_json(), JudgeEvaluationOutput)
    assert parsed.summary == "Solid response."


def test_extract_json_raises_on_empty() -> None:
    with pytest.raises(RacccaParseError):
        extract_json_text("   ")
