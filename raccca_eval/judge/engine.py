"""Judge engine orchestrating RACCCA evaluation LLM calls."""

from __future__ import annotations

import asyncio
import logging
from collections.abc import Callable

from raccca_eval.config.settings import RacccaSettings
from raccca_eval.judge.prompt_builder import RubricPromptBuilder
from raccca_eval.models.criteria import RacccaCriterion
from raccca_eval.models.judge_output import JudgeCriterionOutput, JudgeEvaluationOutput
from raccca_eval.models.request import EvaluationRequest
from raccca_eval.models.result import CriterionScore, EvaluationResult, UsageMetadata
from raccca_eval.providers.base import LLMCompletion, LLMProvider
from raccca_eval.utils.retry import run_with_retry, run_with_retry_async

logger = logging.getLogger(__name__)


class JudgeEngine:
    """Orchestrates judge LLM calls and aggregates RACCCA scores."""

    def __init__(
        self,
        provider: LLMProvider,
        settings: RacccaSettings,
        *,
        fallback_provider: LLMProvider | None = None,
        on_eval_complete: Callable[[EvaluationResult], None] | None = None,
    ) -> None:
        self.provider = provider
        self.fallback_provider = fallback_provider
        self.settings = settings
        self.on_eval_complete = on_eval_complete
        self.prompt_builder = RubricPromptBuilder(
            scale_min=settings.scoring_scale_min,
            scale_max=settings.scoring_scale_max,
        )

    def evaluate(self, request: EvaluationRequest) -> EvaluationResult:
        if self.settings.strategy == "per_criterion":
            return run_with_retry(
                lambda: self._evaluate_per_criterion(request),
                max_retries=self.settings.max_retries,
            )
        return run_with_retry(
            lambda: self._evaluate_single(request),
            max_retries=self.settings.max_retries,
        )

    async def aevaluate(self, request: EvaluationRequest) -> EvaluationResult:
        if self.settings.strategy == "per_criterion":
            return await run_with_retry_async(
                lambda: self._aevaluate_per_criterion(request),
                max_retries=self.settings.max_retries,
            )
        return await run_with_retry_async(
            lambda: self._aevaluate_single(request),
            max_retries=self.settings.max_retries,
        )

    def _evaluate_single(self, request: EvaluationRequest) -> EvaluationResult:
        prompt = self.prompt_builder.build(request)
        output, completion = self._call_with_fallback(
            system=prompt.system,
            user=prompt.user,
            output_model=JudgeEvaluationOutput,
        )
        return self._build_result(request, output.scores, output.summary, [completion])

    async def _aevaluate_single(self, request: EvaluationRequest) -> EvaluationResult:
        prompt = self.prompt_builder.build(request)
        output, completion = await self._acall_with_fallback(
            system=prompt.system,
            user=prompt.user,
            output_model=JudgeEvaluationOutput,
        )
        return self._build_result(request, output.scores, output.summary, [completion])

    def _evaluate_per_criterion(self, request: EvaluationRequest) -> EvaluationResult:
        scores: list[JudgeCriterionOutput] = []
        completions: list[LLMCompletion] = []
        summaries: list[str] = []

        for criterion in request.criteria_to_evaluate:
            prompt = self.prompt_builder.build_single_criterion(request, criterion)
            output, completion = self._call_with_fallback(
                system=prompt.system,
                user=prompt.user,
                output_model=JudgeEvaluationOutput,
            )
            criterion_scores = [s for s in output.scores if s.criterion == criterion]
            if not criterion_scores and output.scores:
                criterion_scores = [output.scores[0]]
            scores.extend(criterion_scores)
            completions.append(completion)
            summaries.append(output.summary)

        summary = " ".join(summaries) if summaries else "Per-criterion evaluation complete."
        return self._build_result(request, scores, summary, completions)

    async def _aevaluate_per_criterion(self, request: EvaluationRequest) -> EvaluationResult:
        async def evaluate_one(
            criterion: RacccaCriterion,
        ) -> tuple[list[JudgeCriterionOutput], LLMCompletion, str]:
            prompt = self.prompt_builder.build_single_criterion(request, criterion)
            output, completion = await self._acall_with_fallback(
                system=prompt.system,
                user=prompt.user,
                output_model=JudgeEvaluationOutput,
            )
            criterion_scores = [s for s in output.scores if s.criterion == criterion]
            if not criterion_scores and output.scores:
                criterion_scores = [output.scores[0]]
            return criterion_scores, completion, output.summary

        results = await asyncio.gather(
            *[evaluate_one(c) for c in request.criteria_to_evaluate]
        )

        scores: list[JudgeCriterionOutput] = []
        completions: list[LLMCompletion] = []
        summaries: list[str] = []
        for criterion_scores, completion, summary in results:
            scores.extend(criterion_scores)
            completions.append(completion)
            summaries.append(summary)

        summary = " ".join(summaries) if summaries else "Per-criterion evaluation complete."
        return self._build_result(request, scores, summary, completions)

    def _call_with_fallback(
        self,
        *,
        system: str,
        user: str,
        output_model: type[JudgeEvaluationOutput],
    ) -> tuple[JudgeEvaluationOutput, LLMCompletion]:
        try:
            return self.provider.complete_structured(
                system=system,
                user=user,
                output_model=output_model,
            )
        except Exception:
            if self.fallback_provider is None:
                raise
            logger.warning("Primary judge model failed; using fallback model.")
            return self.fallback_provider.complete_structured(
                system=system,
                user=user,
                output_model=output_model,
            )

    async def _acall_with_fallback(
        self,
        *,
        system: str,
        user: str,
        output_model: type[JudgeEvaluationOutput],
    ) -> tuple[JudgeEvaluationOutput, LLMCompletion]:
        try:
            return await self.provider.acomplete_structured(
                system=system,
                user=user,
                output_model=output_model,
            )
        except Exception:
            if self.fallback_provider is None:
                raise
            logger.warning("Primary judge model failed; using fallback model.")
            return await self.fallback_provider.acomplete_structured(
                system=system,
                user=user,
                output_model=output_model,
            )

    def _build_result(
        self,
        request: EvaluationRequest,
        judge_scores: list[JudgeCriterionOutput],
        summary: str,
        completions: list[LLMCompletion],
    ) -> EvaluationResult:
        expected = set(request.criteria_to_evaluate)
        score_map: dict[str, CriterionScore] = {}

        for item in judge_scores:
            if item.criterion not in expected:
                continue

            clamped_score = self._clamp_score(item.score, item.criterion.value)

            score_map[item.criterion.value] = CriterionScore(
                criterion=item.criterion,
                score=clamped_score,
                rationale=item.rationale,
                confidence=item.confidence,
            )

        for criterion in request.criteria_to_evaluate:
            if criterion.value not in score_map:
                score_map[criterion.value] = CriterionScore(
                    criterion=criterion,
                    score=self.settings.scoring_scale_min,
                    rationale="Judge did not return a score for this criterion.",
                )

        weights = self.settings.get_weights(request.criteria_to_evaluate)
        overall = sum(
            score_map[c.value].score * weights[c] for c in request.criteria_to_evaluate
        )

        usage = UsageMetadata(
            prompt_tokens=sum(c.prompt_tokens for c in completions),
            completion_tokens=sum(c.completion_tokens for c in completions),
            total_tokens=sum(c.total_tokens for c in completions),
            latency_ms=sum(c.latency_ms for c in completions),
            num_calls=len(completions),
        )

        warnings: list[str] = []
        if request.ground_truth_warning:
            warnings.append(request.ground_truth_warning)

        raw_response = completions[-1].content if self.settings.debug and completions else None
        model = completions[-1].model if completions else self.settings.judge_model

        result = EvaluationResult(
            scores=score_map,
            overall_score=round(overall, 2),
            summary=summary,
            model=model,
            usage=usage,
            warnings=warnings,
            raw_response=raw_response,
        )

        if self.on_eval_complete:
            self.on_eval_complete(result)

        return result

    def _clamp_score(self, score: int | float, label: str) -> int:
        scale_min = self.settings.scoring_scale_min
        scale_max = self.settings.scoring_scale_max
        if scale_min <= score <= scale_max:
            return int(round(score))
        logger.warning(
            "Judge returned score %s outside the configured scale bounds "
            "[%s, %s] for '%s'. Clamping score.",
            score,
            scale_min,
            scale_max,
            label,
        )
        return max(scale_min, min(int(round(score)), scale_max))
