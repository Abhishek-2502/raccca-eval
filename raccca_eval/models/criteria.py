"""RACCCA evaluation criteria definitions."""

from __future__ import annotations

from enum import StrEnum


class RacccaCriterion(StrEnum):
    """The six RACCCA evaluation dimensions."""

    RELEVANCE = "relevance"
    ACCURACY = "accuracy"
    COMPLETENESS = "completeness"
    CLARITY = "clarity"
    COHERENCE = "coherence"
    APPROPRIATENESS = "appropriateness"


ALL_CRITERIA: tuple[RacccaCriterion, ...] = tuple(RacccaCriterion)

CRITERIA_REQUIRING_AUDIENCE: frozenset[RacccaCriterion] = frozenset(
    {RacccaCriterion.CLARITY, RacccaCriterion.APPROPRIATENESS}
)

CRITERIA_BENEFITING_GROUND_TRUTH: frozenset[RacccaCriterion] = frozenset(
    {RacccaCriterion.ACCURACY, RacccaCriterion.COMPLETENESS}
)
