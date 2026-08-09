"""Evaluation result models."""

from __future__ import annotations

from pydantic import BaseModel, Field

from raccca_eval.models.criteria import RacccaCriterion


class UsageMetadata(BaseModel):
    """Token usage and timing metadata from the judge LLM call."""

    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    latency_ms: float = 0.0
    num_calls: int = 1


class CriterionScore(BaseModel):
    """Score and rationale for a single RACCCA criterion."""

    criterion: RacccaCriterion
    score: int = Field(..., ge=1, le=5)
    rationale: str
    confidence: float | None = Field(default=None, ge=0.0, le=1.0)


class EvaluationResult(BaseModel):
    """Structured output from a RACCCA evaluation."""

    scores: dict[str, CriterionScore]
    overall_score: float = Field(..., ge=1.0, le=5.0)
    summary: str
    model: str
    usage: UsageMetadata
    warnings: list[str] = Field(default_factory=list)
    raw_response: str | None = None
