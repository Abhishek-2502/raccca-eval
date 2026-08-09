# Changelog

All notable changes to this project are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-08-09

Initial public release of **raccca-eval** — a Python SDK for evaluating LLM responses using the **RACCCA** framework:

**R**elevance · **A**ccuracy · **C**ompleteness · **C**larity · **C**oherence · **A**ppropriateness

### Added

- Typed Pydantic API: `EvaluationRequest`, `EvaluationResult`, `CriterionScore`, and `RacccaCriterion`
- Six RACCCA evaluation criteria on a configurable 1–5 scoring scale
- `RacccaEvaluator` with sync (`evaluate`), async (`aevaluate`), and batch (`aevaluate_batch`) evaluation
- Multi-provider LLM support via LiteLLM (OpenAI, Anthropic, Gemini, Azure, Ollama, vLLM)
- Configuration via environment variables (`RACCCA_*`), `.env`, or YAML (`raccca.yaml`)
- Two evaluation strategies: `single` (one judge call) and `per_criterion` (one call per dimension)
- Retry logic, optional fallback judge model, and JSON recovery for malformed LLM output
- Configurable criterion weights for weighted overall scores
- Usage metadata: token counts, latency, and call count per evaluation
- Examples: basic eval, batch async eval, Azure + Ollama setup
- Documentation: getting started, configuration, and provider guides
- Unit tests and optional integration tests with live LLM API keys

### Requirements

- Python 3.11, 3.12, or 3.13
- An API key for your chosen LLM provider

[0.1.0]: https://github.com/Abhishek-2502/raccca-eval/releases/tag/v0.1.0

