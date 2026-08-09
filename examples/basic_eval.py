"""Basic RACCCA evaluation example."""

from raccca_eval import EvaluationRequest, RacccaEvaluator, RacccaCriterion


def main() -> None:
    evaluator = RacccaEvaluator(model="gpt-4o-mini")

    request = EvaluationRequest(
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

    result = evaluator.evaluate(request)

    print(f"Overall score: {result.overall_score}")
    for name, score in result.scores.items():
        print(f"  {name}: {score.score} — {score.rationale}")
    print(f"Summary: {result.summary}")


if __name__ == "__main__":
    main()
