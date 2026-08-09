# raccca-eval Features

**raccca-eval** is a Python SDK that uses a judge LLM to score any model response across six quality dimensions — with structured results, multi-provider support, and production-ready reliability.

---

## RACCCA Evaluation Framework

Evaluate LLM outputs on six research-backed quality dimensions:

| Dimension | What it measures |
|-----------|------------------|
| **Relevance** | Does the response address the query? |
| **Accuracy** | Is the information factually correct? |
| **Completeness** | Are all essential points covered? |
| **Clarity** | Is it understandable for the target audience? |
| **Coherence** | Is it logically structured and consistent? |
| **Appropriateness** | Is the tone and content suitable for the context? |

Each dimension receives an integer score with a written rationale, so every evaluation is explainable and auditable.

---

## Core Capabilities

### Structured, typed evaluation results
Every evaluation returns a fully typed result object with per-criterion scores, rationales, a weighted overall score, and a summary — ready to store, log, or display in dashboards.

### Configurable scoring scales
Scoring scales are not locked to 1–5. Define custom min and max bounds, and the SDK adapts prompts, validation, and rubric midpoints automatically.

### Custom rubric definitions
Override built-in rubric text for any criterion to tailor evaluation to your domain, use case, or compliance requirements.

### Weighted overall scores
Assign custom weights per criterion so the final score reflects what matters most for your application.

---

## Judge LLM Support

### Multi-provider, model-agnostic
Works with any judge model supported by LiteLLM, including:

- OpenAI (GPT-4o, GPT-4o-mini, and others)
- Anthropic (Claude)
- Google (Gemini)
- Azure OpenAI
- Ollama (local models)
- vLLM

Switch providers or models without changing your evaluation logic.

### Two evaluation strategies

| Strategy | Description | Best for |
|----------|-------------|----------|
| **Single** | One judge call scores all selected criteria | Cost-efficient production workloads |
| **Per-criterion** | Separate judge call per dimension | Audits, research, and maximum granularity |

### Optional fallback judge
If the primary judge model fails, an automatic fallback model takes over — keeping evaluations resilient in production.

---

## Input Flexibility

Provide the context your evaluation needs:

- **Query** — the original user prompt
- **Response** — the LLM output to evaluate
- **Reference answer** — a gold-standard answer for accuracy and completeness checks
- **Context document** — external grounding material for fact-checking
- **Target audience** — required for clarity and appropriateness scoring
- **External prompt** — additional instructions injected into the judge

Select any subset of the six RACCCA criteria per evaluation.

---

## Production Readiness

### Sync and async evaluation
Run evaluations synchronously, asynchronously, or in concurrent batches with configurable parallelism — suited for both interactive apps and high-throughput pipelines.

### Automatic retries
Transient judge LLM failures are retried with configurable backoff, reducing noise from flaky API responses.

### Robust JSON recovery
Judge outputs that are malformed or use non-standard formatting are recovered automatically, with optional support for the `json-repair` library for harder cases.

### Parse error debuggability
When parsing fails, the raw judge response is attached to the error — so you can inspect exactly what went wrong without guesswork.

### Usage metadata
Every evaluation reports token counts (prompt, completion, total), latency, and number of judge calls — for cost tracking and performance monitoring.

### Evaluation callbacks
Hook into the evaluation lifecycle to log, persist, or stream results as soon as each evaluation completes.

---

## Configuration

Configure the SDK your way:

- **Environment variables** — all settings available via `RACCCA_*` prefixed vars
- **`.env` file** — load secrets and settings from a local dotenv file
- **YAML config** — declarative configuration via `raccca.yaml` for teams and CI

Settings include judge model, strategy, temperature, retry limits, scoring scale bounds, criterion weights, and more.

---

## Developer Experience

- **Python 3.11+** with full type hints and Pydantic validation
- **MIT licensed** — free for commercial and open-source use
- **Published on PyPI** — install with a single pip command
- **Runnable examples** — basic evaluation, batch evaluation, and multi-provider setups included
- **CI-tested** — linting, type checking, and unit tests on every push and release

---

## Use Cases

- **LLM quality monitoring** — score production responses against RACCCA dimensions on every request
- **Prompt and model comparison** — evaluate the same query across models or prompt variants with consistent rubrics
- **RAG pipeline evaluation** — check accuracy and completeness against retrieved context and reference answers
- **Content moderation and safety** — assess appropriateness and clarity for specific audiences
- **Research and benchmarking** — run per-criterion evaluations for detailed, auditable score breakdowns
- **CI/CD quality gates** — fail builds or deployments when response quality drops below a threshold
