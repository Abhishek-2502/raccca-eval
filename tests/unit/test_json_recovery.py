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
    with pytest.raises(RacccaParseError) as exc_info:
        extract_json_text("   ")
    assert exc_info.value.raw_response == "   "


def test_extract_json_embedded_object() -> None:
    raw = 'Analysis complete: {"scores": [], "summary": "ok"} — done.'
    assert extract_json_text(raw).startswith("{")


def test_extract_json_raises_when_missing() -> None:
    raw = "plain text without json"
    with pytest.raises(RacccaParseError, match="No JSON object") as exc_info:
        extract_json_text(raw)
    assert exc_info.value.raw_response == raw


def test_parse_model_response_repairs_single_quotes() -> None:
    raw = (
        "{'scores': [{'criterion': 'relevance', 'score': 4, 'rationale': 'Good.'}], "
        "'summary': 'Solid.'}"
    )
    parsed = parse_model_response(raw, JudgeEvaluationOutput)
    assert parsed.summary == "Solid."
    assert parsed.scores[0].score == 4


def test_parse_error_includes_raw_response() -> None:
    raw = "not json at all"
    with pytest.raises(RacccaParseError) as exc_info:
        parse_model_response(raw, JudgeEvaluationOutput)
    assert exc_info.value.raw_response == raw
