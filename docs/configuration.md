# Configuration

## Environment Variables

All settings use the `RACCCA_` prefix:

| Variable | Default | Description |
|----------|---------|-------------|
| `RACCCA_JUDGE_MODEL` | `gpt-4o-mini` | Primary judge LLM model string |
| `RACCCA_FALLBACK_MODEL` | — | Fallback model if primary fails |
| `RACCCA_API_BASE` | — | Custom API base (Azure, Ollama, vLLM) |
| `RACCCA_API_KEY` | — | Optional explicit API key |
| `RACCCA_TEMPERATURE` | `0.0` | Judge temperature |
| `RACCCA_MAX_RETRIES` | `3` | Retry attempts on transient errors |
| `RACCCA_TIMEOUT_SECONDS` | `60` | Request timeout |
| `RACCCA_STRATEGY` | `single` | `single` or `per_criterion` |
| `RACCCA_DEBUG` | `false` | Include raw judge response in results |
| `RACCCA_CONFIG_PATH` | — | Path to YAML config file |

Provider API keys (`OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, etc.) are read by LiteLLM automatically.

## YAML Config

Create `raccca.yaml` in your project root:

```yaml
judge_model: gpt-4o-mini
fallback_model: anthropic/claude-3-5-haiku-20241022
strategy: single
temperature: 0.0
weights:
  relevance: 0.3
  accuracy: 0.4
  completeness: 0.3
```

Load via:

```python
evaluator = RacccaEvaluator.from_settings()
```

## Evaluation Strategies

- **`single`** (default): One LLM call scores all selected criteria. Lower cost.
- **`per_criterion`**: One LLM call per criterion. Higher accuracy for audits.

## Weights

Set per-criterion weights to customize the overall score:

```python
from raccca_eval.config import RacccaSettings

settings = RacccaSettings(
    weights={"relevance": 2, "accuracy": 3, "completeness": 1},
)
evaluator = RacccaEvaluator(settings=settings)
```
