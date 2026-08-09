# raccca-eval

Enterprise-grade Python SDK for evaluating LLM responses using the **RACCCA** framework:

**R**elevance · **A**ccuracy · **C**ompleteness · **C**larity · **C**oherence · **A**ppropriateness

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## Features

- Typed Pydantic API for evaluation requests and results
- Multi-provider LLM support via LiteLLM (OpenAI, Anthropic, Gemini, Azure, Ollama, vLLM)
- Configurable via environment variables and YAML
- Sync and async evaluation with batch support
- Single-call and per-criterion evaluation strategies
- Retry logic with optional fallback judge model

## Install

```bash
pip install raccca-eval
```

## Quickstart

```python
from raccca_eval import RacccaEvaluator, EvaluationRequest, RacccaCriterion

evaluator = RacccaEvaluator(model="gpt-4o-mini")

result = evaluator.evaluate(
    EvaluationRequest(
        query="What causes Type 2 diabetes?",
        response="Type 2 diabetes is caused by insulin resistance...",
        criteria_to_evaluate=[
            RacccaCriterion.RELEVANCE,
            RacccaCriterion.ACCURACY,
            RacccaCriterion.COMPLETENESS,
        ],
        reference_answer="Insulin resistance and beta-cell dysfunction...",
        audience="medical students",
    )
)

print(result.overall_score)       # e.g. 4.33
print(result.scores["accuracy"])  # CriterionScore(score=4, rationale="...")
```

## Configuration

Set `OPENAI_API_KEY` (or your provider's key), then optionally configure via environment:

```bash
export RACCCA_JUDGE_MODEL=gpt-4o-mini
export RACCCA_STRATEGY=single
export RACCCA_FALLBACK_MODEL=anthropic/claude-3-5-haiku-20241022
```

Or use a YAML config file (`raccca.yaml`):

```yaml
judge_model: gpt-4o-mini
strategy: single
temperature: 0.0
```

```python
evaluator = RacccaEvaluator.from_settings()
```

See [docs/configuration.md](docs/configuration.md) for all options.

## Providers

| Provider | Model string example | Env vars |
|----------|---------------------|----------|
| OpenAI | `gpt-4o-mini` | `OPENAI_API_KEY` |
| Anthropic | `anthropic/claude-3-5-haiku-20241022` | `ANTHROPIC_API_KEY` |
| Google | `gemini/gemini-2.0-flash` | `GEMINI_API_KEY` |
| Azure | `azure/gpt-4o` | `AZURE_API_KEY`, `AZURE_API_BASE` |
| Ollama | `ollama/llama3.2` | `OLLAMA_API_BASE` |

See [docs/providers.md](docs/providers.md) for setup details.

## Async Batch Evaluation

```python
import asyncio
from raccca_eval import RacccaEvaluator, EvaluationRequest

evaluator = RacccaEvaluator.from_settings()
results = asyncio.run(evaluator.aevaluate_batch(requests, concurrency=5))
```

## Development

```bash
git clone https://github.com/raccca-eval/raccca-eval.git
cd raccca-eval
pip install -e ".[dev]"
pytest
ruff check .
mypy raccca_eval
```

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for version history.

## License

MIT — see [LICENSE](LICENSE).
