# Getting Started

## Install

```bash
pip install raccca-eval
```

For development:

```bash
pip install -e ".[dev]"
```

## Quickstart

```python
from raccca_eval import RacccaEvaluator, EvaluationRequest, RacccaCriterion

evaluator = RacccaEvaluator(model="gpt-4o-mini")

result = evaluator.evaluate(
    EvaluationRequest(
        query="What is the capital of France?",
        response="The capital of France is Paris.",
        criteria_to_evaluate=[RacccaCriterion.RELEVANCE, RacccaCriterion.ACCURACY],
        reference_answer="Paris is the capital of France.",
        audience="general audience",
    )
)

print(result.overall_score)
print(result.scores["relevance"].rationale)
```

## RACCCA Criteria

| Criterion | Description |
|-----------|-------------|
| `relevance` | Does the response address the query? |
| `accuracy` | Is the information factually correct? |
| `completeness` | Are all essential points covered? |
| `clarity` | Is it understandable for the audience? |
| `coherence` | Is it logically structured? |
| `appropriateness` | Is tone and content suitable? |

See [configuration.md](configuration.md) and [providers.md](providers.md) for advanced setup.
