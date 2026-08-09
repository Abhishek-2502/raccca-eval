"""Unit tests for RacccaSettings."""

from pathlib import Path

import pytest

from raccca_eval.config.settings import RacccaSettings, load_yaml_config
from raccca_eval.models.criteria import RacccaCriterion


def test_settings_default_model() -> None:
    settings = RacccaSettings()
    assert settings.judge_model == "gpt-4o-mini"


def test_get_weights_normalizes() -> None:
    settings = RacccaSettings(
        weights={"relevance": 2.0, "accuracy": 2.0},
    )
    criteria = [RacccaCriterion.RELEVANCE, RacccaCriterion.ACCURACY]
    weights = settings.get_weights(criteria)
    assert weights[RacccaCriterion.RELEVANCE] == pytest.approx(0.5)
    assert weights[RacccaCriterion.ACCURACY] == pytest.approx(0.5)


def test_load_yaml_config(tmp_path: Path) -> None:
    config_file = tmp_path / "raccca.yaml"
    config_file.write_text("judge_model: test-model\nstrategy: per_criterion\n", encoding="utf-8")
    data = load_yaml_config(config_file)
    assert data["judge_model"] == "test-model"

    settings = RacccaSettings.load(config_path=config_file)
    assert settings.judge_model == "test-model"
    assert settings.strategy == "per_criterion"
