"""raccca_eval — Enterprise RACCCA framework for evaluating LLM responses."""

from raccca_eval.evaluator import RacccaEvaluator
from raccca_eval.exceptions import (
    RacccaError,
    RacccaParseError,
    RacccaProviderError,
    RacccaValidationError,
)
from raccca_eval.models import (
    ALL_CRITERIA,
    CriterionScore,
    EvaluationRequest,
    EvaluationResult,
    RacccaCriterion,
    UsageMetadata,
)
from raccca_eval.version import __version__

__all__ = [
    "__version__",
    "ALL_CRITERIA",
    "CriterionScore",
    "EvaluationRequest",
    "EvaluationResult",
    "RacccaCriterion",
    "RacccaError",
    "RacccaEvaluator",
    "RacccaParseError",
    "RacccaProviderError",
    "RacccaValidationError",
    "UsageMetadata",
]
