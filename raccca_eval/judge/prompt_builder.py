"""Prompt assembly for RACCCA judge LLM calls."""

from __future__ import annotations

from dataclasses import dataclass

from raccca_eval.judge.rubric import format_rubric_block
from raccca_eval.models.criteria import RacccaCriterion
from raccca_eval.models.request import EvaluationRequest


@dataclass(frozen=True, slots=True)
class JudgePrompt:
    """System and user messages for the judge LLM."""

    system: str
    user: str


class RubricPromptBuilder:
    """Builds judge prompts from an EvaluationRequest."""

    def __init__(self, *, scale_min: int = 1, scale_max: int = 5) -> None:
        self.scale_min = scale_min
        self.scale_max = scale_max

    def build(
        self,
        request: EvaluationRequest,
        *,
        criteria: list[RacccaCriterion] | None = None,
    ) -> JudgePrompt:
        selected = criteria or request.criteria_to_evaluate
        rubric_blocks = [
            format_rubric_block(c, self.scale_min, self.scale_max) for c in selected
        ]
        criteria_list = ", ".join(c.value for c in selected)

        system_parts = [
            "You are an expert evaluator applying the RACCCA framework to assess LLM responses.",
            f"Evaluate the response on these criteria: {criteria_list}.",
            f"Score each criterion on a {self.scale_min}-{self.scale_max} integer scale.",
            "Provide a concise rationale for each score.",
            "Return valid JSON matching the required schema.",
            "",
            "## RACCCA Rubric",
            *rubric_blocks,
        ]

        if request.external_prompt:
            system_parts.extend(["", "## Additional Instructions", request.external_prompt.strip()])

        user_parts = [
            "## Query",
            request.query,
            "",
            "## Response to Evaluate",
            request.response,
        ]

        if request.context:
            user_parts.extend(["", "## Context / External Document", request.context])

        if request.reference_answer:
            user_parts.extend(["", "## Reference Answer", request.reference_answer])

        if request.audience:
            user_parts.extend(["", "## Target Audience", request.audience])

        if not request.context and not request.reference_answer:
            user_parts.extend(
                [
                    "",
                    "## Note",
                    "No context or reference answer was provided. "
                    "For accuracy and completeness, use your best judgment.",
                ]
            )

        return JudgePrompt(system="\n".join(system_parts), user="\n".join(user_parts))

    def build_single_criterion(
        self,
        request: EvaluationRequest,
        criterion: RacccaCriterion,
    ) -> JudgePrompt:
        return self.build(request, criteria=[criterion])
