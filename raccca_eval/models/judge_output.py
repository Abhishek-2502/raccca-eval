"""Judge LLM structured output schemas."""

from __future__ import annotations

from pydantic import BaseModel, Field

from raccca_eval.models.criteria import RacccaCriterion


class JudgeCriterionOutput(BaseModel):
    """Single criterion score returned by the judge LLM."""

    criterion: RacccaCriterion
    score: int = Field(..., description="Score awarded by the judge model.")
    rationale: str = Field(..., min_length=1)
    confidence: float | None = Field(default=None, ge=0.0, le=1.0)


class JudgeEvaluationOutput(BaseModel):
    """Full structured output from a single judge LLM call."""

    scores: list[JudgeCriterionOutput] = Field(..., min_length=1)
    summary: str = Field(..., min_length=1)
