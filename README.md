# raccca-eval

Enterprise-grade Python SDK for evaluating LLM responses using the **RACCCA** framework:

**R**elevance · **A**ccuracy · **C**ompleteness · **C**larity · **C**oherence · **A**ppropriateness

[![PyPI version](https://img.shields.io/pypi/v/raccca-eval.svg)](https://pypi.org/project/raccca-eval/)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Use a judge LLM to score any model output on six quality dimensions — with typed results, multi-provider support, and sync or async batch evaluation.

## Install

```bash
pip install raccca-eval
```

Requires Python 3.11+. Set an API key for your judge provider (e.g. `OPENAI_API_KEY`).

## Quickstart

```python
from raccca_eval import EvaluationRequest, RacccaCriterion, RacccaEvaluator

evaluator = RacccaEvaluator(model="gpt-4o-mini")

result = evaluator.evaluate(
    EvaluationRequest(
        query="What causes Type 2 diabetes?",
        response=(
            "Type 2 diabetes is caused by insulin resistance and impaired beta-cell function, "
            "often linked to obesity and sedentary lifestyle."
        ),
        criteria_to_evaluate=[
            RacccaCriterion.RELEVANCE,
            RacccaCriterion.ACCURACY,
            RacccaCriterion.COMPLETENESS,
        ],
        reference_answer=(
            "Insulin resistance and beta-cell dysfunction are primary causes of Type 2 diabetes."
        ),
        audience="medical students",
    )
)

print(f"Overall: {result.overall_score}/5")
print(f"Summary: {result.summary}")

for name, score in result.scores.items():
    print(f"  {name}: {score.score}/5 — {score.rationale}")

# Token usage from the judge call
print(f"Judge tokens: {result.usage.total_tokens}, latency: {result.usage.latency_ms:.0f}ms")
```

**Example output:**

```
Overall: 4.33/5
Summary: Accurate and relevant explanation with good coverage of core mechanisms.
  relevance: 5/5 — Directly addresses the question about Type 2 diabetes causes.
  accuracy: 4/5 — Core mechanisms are correct; minor details omitted.
  completeness: 4/5 — Covers insulin resistance and lifestyle factors well.
Judge tokens: 842, latency: 1200ms
```

## RACCCA criteria

| Criterion | `RacccaCriterion` | What it measures |
|-----------|---------------------|------------------|
| Relevance | `RELEVANCE` | Does the response address the query? |
| Accuracy | `ACCURACY` | Is the information factually correct? |
| Completeness | `COMPLETENESS` | Are all essential points covered? |
| Clarity | `CLARITY` | Is it understandable for the audience? |
| Coherence | `COHERENCE` | Is it logically structured? |
| Appropriateness | `APPROPRIATENESS` | Is tone and content suitable? |

Each criterion is scored **1–5** with a written rationale. Pass `audience` when evaluating clarity or appropriateness; provide `reference_answer` or `context` for stronger accuracy and completeness checks.

## Evaluation request

```python
EvaluationRequest(
    query="...",                        # Original user prompt
    response="...",                     # LLM output to evaluate
    criteria_to_evaluate=[...],         # Defaults to all six RACCCA criteria
    reference_answer="...",             # Optional gold-standard answer
    context="...",                      # Optional grounding document
    audience="...",                     # Required for clarity / appropriateness
    external_prompt="...",              # Extra instructions for the judge
)
```

## Features

- **Typed Pydantic API** — `EvaluationRequest`, `EvaluationResult`, `CriterionScore`
- **Multi-provider judges** — OpenAI, Anthropic, Gemini, Azure, Ollama, vLLM via LiteLLM
- **Flexible config** — environment variables, `.env`, or `raccca.yaml`
- **Sync & async** — `evaluate()`, `aevaluate()`, `aevaluate_batch()`, `evaluate_batch()`
- **Two strategies** — `single` (one judge call) or `per_criterion` (one call per dimension)
- **Production-ready** — retries, optional fallback judge, JSON recovery, usage metadata

## Configuration

Environment variables (all prefixed with `RACCCA_`):

```bash
export OPENAI_API_KEY=sk-...
export RACCCA_JUDGE_MODEL=gpt-4o-mini
export RACCCA_STRATEGY=single
export RACCCA_FALLBACK_MODEL=anthropic/claude-3-5-haiku-20241022
export RACCCA_MAX_RETRIES=3
```

Or use a YAML config file (`raccca.yaml`):

```yaml
judge_model: gpt-4o-mini
strategy: single
temperature: 0.0
weights:
  relevance: 0.3
  accuracy: 0.4
  completeness: 0.3
```

```python
evaluator = RacccaEvaluator.from_settings()
```

See [docs/configuration.md](docs/configuration.md) for all options.

### Evaluation strategies

| Strategy | Behavior | Best for |
|----------|----------|----------|
| `single` (default) | One LLM call scores all selected criteria | Cost-efficient production use |
| `per_criterion` | Separate LLM call per criterion | Audits and maximum granularity |

```python
from raccca_eval.config import RacccaSettings

evaluator = RacccaEvaluator(settings=RacccaSettings(strategy="per_criterion"))
```

## Providers

| Provider | Model string example | Env vars |
|----------|---------------------|----------|
| OpenAI | `gpt-4o-mini` | `OPENAI_API_KEY` |
| Anthropic | `anthropic/claude-3-5-haiku-20241022` | `ANTHROPIC_API_KEY` |
| Google | `gemini/gemini-2.0-flash` | `GEMINI_API_KEY` |
| Azure | `azure/gpt-4o` | `AZURE_API_KEY`, `AZURE_API_BASE` |
| Ollama | `ollama/llama3.2` | `OLLAMA_API_BASE` |

See [docs/providers.md](docs/providers.md) for setup details.

## Async batch evaluation

Evaluate many responses concurrently with bounded parallelism:

```python
import asyncio

from raccca_eval import EvaluationRequest, RacccaCriterion, RacccaEvaluator

async def main() -> None:
    evaluator = RacccaEvaluator.from_settings()

    requests = [
        EvaluationRequest(
            query="What is RACCCA?",
            response="RACCCA is a framework for evaluating AI responses.",
            criteria_to_evaluate=[RacccaCriterion.RELEVANCE, RacccaCriterion.CLARITY],
            audience="developers",
        ),
        EvaluationRequest(
            query="What is 2+2?",
            response="2+2 equals 4.",
            criteria_to_evaluate=[RacccaCriterion.ACCURACY, RacccaCriterion.RELEVANCE],
            reference_answer="4",
        ),
    ]

    results = await evaluator.aevaluate_batch(requests, concurrency=5)

    for i, result in enumerate(results, start=1):
        print(f"Request {i}: {result.overall_score}/5 — {result.summary}")

asyncio.run(main())
```

Sync equivalent: `evaluator.evaluate_batch(requests, concurrency=5)`.

## Examples

Runnable scripts in [`examples/`](examples/):

| Script | Description |
|--------|-------------|
| [`basic_eval.py`](examples/basic_eval.py) | Single evaluation with score breakdown |
| [`batch_eval.py`](examples/batch_eval.py) | Async batch evaluation |
| [`azure_and_ollama.py`](examples/azure_and_ollama.py) | Azure OpenAI and Ollama judges |

```bash
export OPENAI_API_KEY=sk-...
python examples/basic_eval.py
```

## Development

```bash
git clone https://github.com/Abhishek-2502/raccca-eval.git
cd raccca-eval
pip install -e ".[dev]"
pytest
ruff check .
mypy raccca_eval
```

Integration tests (require live API keys) are skipped by default:

```bash
pytest -m integration
```

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for version history.

## License

MIT — see [LICENSE](LICENSE).
