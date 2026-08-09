"""Evaluation request model."""

from __future__ import annotations

from typing import Self

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from raccca_eval.models.criteria import (
    ALL_CRITERIA,
    CRITERIA_BENEFITING_GROUND_TRUTH,
    CRITERIA_REQUIRING_AUDIENCE,
    RacccaCriterion,
)


class EvaluationRequest(BaseModel):
    """Input payload for a RACCCA evaluation."""

    query: str = Field(..., min_length=1, description="The original user query or prompt.")
    response: str = Field(..., min_length=1, description="The LLM response to evaluate.")
    criteria_to_evaluate: list[RacccaCriterion] = Field(
        default_factory=lambda: list(ALL_CRITERIA),
        description="RACCCA criteria to score.",
    )
    context: str | None = Field(
        default=None,
        description="External document or context for grounding accuracy checks.",
    )
    reference_answer: str | None = Field(
        default=None,
        description="Gold-standard answer for comparison.",
    )
    audience: str | None = Field(
        default=None,
        description="Target audience (e.g. 'high school students').",
    )
    external_prompt: str | None = Field(
        default=None,
        description="Additional judge instructions appended to the system prompt.",
    )

    model_config = ConfigDict(str_strip_whitespace=True)

    @field_validator("criteria_to_evaluate")
    @classmethod
    def validate_criteria_not_empty(cls, value: list[RacccaCriterion]) -> list[RacccaCriterion]:
        if not value:
            raise ValueError("criteria_to_evaluate must contain at least one criterion.")
        return list(dict.fromkeys(value))

    @model_validator(mode="after")
    def validate_optional_requirements(self) -> Self:
        criteria_set = set(self.criteria_to_evaluate)

        missing_audience = criteria_set & CRITERIA_REQUIRING_AUDIENCE
        if missing_audience and not self.audience:
            names = ", ".join(sorted(c.value for c in missing_audience))
            raise ValueError(f"audience is required when evaluating: {names}")

        return self

    @property
    def ground_truth_warning(self) -> str | None:
        criteria_set = set(self.criteria_to_evaluate)
        needs_ground_truth = criteria_set & CRITERIA_BENEFITING_GROUND_TRUTH
        if needs_ground_truth and not self.context and not self.reference_answer:
            names = ", ".join(sorted(c.value for c in needs_ground_truth))
            return (
                f"Evaluating {names} without context or reference_answer; "
                "the judge will rely on its own knowledge."
            )
        return None
