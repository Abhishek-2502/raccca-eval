# Provider Setup

`raccca-eval` uses [LiteLLM](https://docs.litellm.ai/) as a unified provider adapter.

## OpenAI

```bash
export OPENAI_API_KEY=sk-...
```

```python
evaluator = RacccaEvaluator(model="gpt-4o-mini")
```

## Anthropic

```bash
export ANTHROPIC_API_KEY=sk-ant-...
```

```python
evaluator = RacccaEvaluator(model="anthropic/claude-3-5-haiku-20241022")
```

## Google Gemini

```bash
export GEMINI_API_KEY=...
```

```python
evaluator = RacccaEvaluator(model="gemini/gemini-2.0-flash")
```

## Azure OpenAI

```bash
export AZURE_API_KEY=...
export AZURE_API_BASE=https://your-resource.openai.azure.com
```

```python
from raccca_eval.config import RacccaSettings

settings = RacccaSettings(
    judge_model="azure/gpt-4o",
    api_base="https://your-resource.openai.azure.com",
)
evaluator = RacccaEvaluator(settings=settings)
```

## Ollama (Local)

```bash
export OLLAMA_API_BASE=http://localhost:11434
```

```python
evaluator = RacccaEvaluator(model="ollama/llama3.2")
```

For weaker local models, consider `strategy="per_criterion"` in settings.

## vLLM / OpenAI-Compatible Endpoints

```python
from raccca_eval.config import RacccaSettings

settings = RacccaSettings(
    judge_model="openai/your-model-name",
    api_base="http://localhost:8000/v1",
    api_key="dummy",
)
evaluator = RacccaEvaluator(settings=settings)
```

## Fallback Model

Configure a fallback judge model for resilience:

```yaml
judge_model: gpt-4o-mini
fallback_model: anthropic/claude-3-5-haiku-20241022
```
