"""Batch async evaluation example."""

import asyncio

from raccca_eval import EvaluationRequest, RacccaEvaluator, RacccaCriterion


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

    results = await evaluator.aevaluate_batch(requests, concurrency=2)

    for index, result in enumerate(results, start=1):
        print(f"Request {index}: overall={result.overall_score}")


if __name__ == "__main__":
    asyncio.run(main())
