"""JSON recovery utilities for malformed LLM outputs."""

from __future__ import annotations

import json
import re
from typing import TypeVar

from pydantic import BaseModel, ValidationError

from raccca_eval.exceptions import RacccaParseError

T = TypeVar("T", bound=BaseModel)

_JSON_BLOCK_PATTERN = re.compile(r"```(?:json)?\s*(.*?)\s*```", re.DOTALL | re.IGNORECASE)
_JSON_OBJECT_PATTERN = re.compile(r"\{.*\}", re.DOTALL)


def extract_json_text(raw: str) -> str:
    """Extract JSON string from raw LLM output."""
    text = raw.strip()
    if not text:
        raise RacccaParseError("Empty response from judge LLM.")

    block_match = _JSON_BLOCK_PATTERN.search(text)
    if block_match:
        return block_match.group(1).strip()

    if text.startswith("{") and text.endswith("}"):
        return text

    object_match = _JSON_OBJECT_PATTERN.search(text)
    if object_match:
        return object_match.group(0)

    raise RacccaParseError("No JSON object found in judge LLM response.")


def parse_model_response(raw: str, model: type[T]) -> T:
    """Parse raw LLM text into a Pydantic model with recovery fallbacks."""
    json_text = extract_json_text(raw)
    try:
        return model.model_validate_json(json_text)
    except (ValidationError, json.JSONDecodeError):
        repaired = json_text.replace("'", '"')
        try:
            return model.model_validate_json(repaired)
        except (ValidationError, json.JSONDecodeError) as exc:
            raise RacccaParseError(
                f"Failed to parse judge output as {model.__name__}: {exc}"
            ) from exc
