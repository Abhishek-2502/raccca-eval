"""Built-in RACCCA rubric definitions."""

from __future__ import annotations

from dataclasses import dataclass

from raccca_eval.models.criteria import RacccaCriterion


@dataclass(frozen=True, slots=True)
class RubricDefinition:
    """Definition and scoring anchors for one RACCCA criterion."""

    criterion: RacccaCriterion
    name: str
    definition: str
    score_1: str
    score_3: str
    score_5: str


RUBRIC_DEFINITIONS: dict[RacccaCriterion, RubricDefinition] = {
    RacccaCriterion.RELEVANCE: RubricDefinition(
        criterion=RacccaCriterion.RELEVANCE,
        name="Relevance",
        definition="The extent to which the response directly addresses the issue or question.",
        score_1="Completely off-topic or ignores the query.",
        score_3="Partially addresses the query but misses key aspects.",
        score_5="Fully and directly addresses every part of the query.",
    ),
    RacccaCriterion.ACCURACY: RubricDefinition(
        criterion=RacccaCriterion.ACCURACY,
        name="Accuracy",
        definition=(
            "The degree to which the response provides correct, reliable, "
            "and fact-based information."
        ),
        score_1="Contains major factual errors or misleading claims.",
        score_3="Mostly accurate with minor errors or unsupported claims.",
        score_5="Fully accurate, reliable, and consistent with provided ground truth.",
    ),
    RacccaCriterion.COMPLETENESS: RubricDefinition(
        criterion=RacccaCriterion.COMPLETENESS,
        name="Completeness",
        definition=(
            "The degree to which the response covers all essential aspects "
            "of the topic or question."
        ),
        score_1="Misses most essential points.",
        score_3="Covers main points but omits important details.",
        score_5="Comprehensively covers all essential aspects.",
    ),
    RacccaCriterion.CLARITY: RubricDefinition(
        criterion=RacccaCriterion.CLARITY,
        name="Clarity",
        definition="How easily the response can be understood by the intended audience.",
        score_1="Confusing, ambiguous, or unreadable for the audience.",
        score_3="Understandable but could be clearer or better organized.",
        score_5="Crystal clear and perfectly suited to the audience.",
    ),
    RacccaCriterion.COHERENCE: RubricDefinition(
        criterion=RacccaCriterion.COHERENCE,
        name="Coherence",
        definition=(
            "The extent to which the response is logically structured, well-organized, "
            "and flows smoothly from one point to another."
        ),
        score_1="Disorganized, contradictory, or hard to follow.",
        score_3="Generally logical with some awkward transitions.",
        score_5="Logically structured with smooth, natural flow throughout.",
    ),
    RacccaCriterion.APPROPRIATENESS: RubricDefinition(
        criterion=RacccaCriterion.APPROPRIATENESS,
        name="Appropriateness",
        definition=(
            "How well the response aligns with the intended audience and context, "
            "and is suitable and respectful in tone and content."
        ),
        score_1="Inappropriate tone, content, or level for the audience.",
        score_3="Generally appropriate with minor tone or context mismatches.",
        score_5="Perfectly aligned with audience, context, and tone expectations.",
    ),
}


def get_rubric(criterion: RacccaCriterion) -> RubricDefinition:
    return RUBRIC_DEFINITIONS[criterion]
