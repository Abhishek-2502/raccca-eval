# Changelog

All notable changes to this project are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.2] - 2026-08-09

### Added

- Dynamic score clamping in `JudgeEngine` — out-of-range judge scores are clamped to the configured scale bounds with a warning log
- `RubricPromptBuilder.rubric_overrides` for injecting custom rubric definitions per criterion
- `RacccaParseError.raw_response` — unparseable judge output is attached to the exception for easier debugging
- Optional `json-repair` fallback in JSON recovery (used when the package is installed)

### Changed

- Removed hardcoded `1–5` score bounds from Pydantic models so structured output schemas respect custom scoring scales
- Rubric midpoint is computed dynamically from `scale_min` and `scale_max` instead of being hardcoded to `3`

## [0.1.1] - 2026-08-09

First public release of **raccca-eval** — a Python SDK for evaluating LLM responses using the **RACCCA** framework:

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
- Examples, documentation, and unit tests

### Requirements

- Python 3.11, 3.12, or 3.13
- An API key for your chosen LLM provider

[0.1.2]: https://github.com/Abhishek-2502/raccca-eval/releases/tag/v0.1.2
[0.1.1]: https://github.com/Abhishek-2502/raccca-eval/releases/tag/v0.1.1
