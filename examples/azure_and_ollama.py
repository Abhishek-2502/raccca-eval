"""Examples for Azure OpenAI and Ollama providers."""

import os

from raccca_eval import EvaluationRequest, RacccaEvaluator, RacccaCriterion
from raccca_eval.config import RacccaSettings


def evaluate_with_azure() -> None:
    """Evaluate using Azure OpenAI via LiteLLM."""
    settings = RacccaSettings(
        judge_model="azure/gpt-4o",
        api_base=os.environ.get("AZURE_API_BASE", "https://your-resource.openai.azure.com"),
    )
    evaluator = RacccaEvaluator(settings=settings)

    request = EvaluationRequest(
        query="Summarize RACCCA in one sentence.",
        response="RACCCA is a six-criteria framework for evaluating LLM responses.",
        criteria_to_evaluate=[RacccaCriterion.RELEVANCE, RacccaCriterion.ACCURACY],
        reference_answer=(
            "RACCCA evaluates Relevance, Accuracy, Completeness, Clarity, Coherence, "
            "and Appropriateness."
        ),
        audience="developers",
    )

    result = evaluator.evaluate(request)
    print("Azure result:", result.overall_score)


def evaluate_with_ollama() -> None:
    """Evaluate using a local Ollama model."""
    os.environ.setdefault("OLLAMA_API_BASE", "http://localhost:11434")

    evaluator = RacccaEvaluator(model="ollama/llama3.2")

    request = EvaluationRequest(
        query="What is Python?",
        response="Python is a popular programming language.",
        criteria_to_evaluate=[RacccaCriterion.RELEVANCE, RacccaCriterion.CLARITY],
        audience="beginners",
    )

    result = evaluator.evaluate(request)
    print("Ollama result:", result.overall_score)


if __name__ == "__main__":
    print("Uncomment the provider you want to test:")
    # evaluate_with_azure()
    # evaluate_with_ollama()
