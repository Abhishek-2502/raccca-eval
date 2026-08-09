"""Configuration loading for raccca_eval."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Literal

import yaml
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from raccca_eval.models.criteria import RacccaCriterion


def _default_config_paths() -> list[Path]:
    candidates = []
    if env_path := os.getenv("RACCCA_CONFIG_PATH"):
        candidates.append(Path(env_path))
    candidates.extend([Path("raccca.yaml"), Path("raccca.yml")])
    return candidates


def load_yaml_config(path: Path | None = None) -> dict[str, Any]:
    """Load optional YAML configuration overlay."""
    paths = [path] if path else _default_config_paths()
    for candidate in paths:
        if candidate.is_file():
            with candidate.open(encoding="utf-8") as handle:
                data = yaml.safe_load(handle)
                return data if isinstance(data, dict) else {}
    return {}


class RacccaSettings(BaseSettings):
    """Application settings loaded from environment and optional YAML."""

    model_config = SettingsConfigDict(
        env_prefix="RACCCA_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    judge_model: str = "gpt-4o-mini"
    fallback_model: str | None = None
    api_base: str | None = None
    api_key: str | None = None
    temperature: float = 0.0
    max_retries: int = 3
    timeout_seconds: int = 60
    strategy: Literal["single", "per_criterion"] = "single"
    scoring_scale_min: int = 1
    scoring_scale_max: int = 5
    weights: dict[str, float] | None = None
    debug: bool = False
    config_path: str | None = None

    @field_validator("weights")
    @classmethod
    def validate_weights(cls, value: dict[str, float] | None) -> dict[str, float] | None:
        if value is None:
            return None
        for key in value:
            RacccaCriterion(key)
        return value

    @classmethod
    def load(cls, *, config_path: Path | str | None = None) -> RacccaSettings:
        """Load settings from YAML overlay merged with environment variables."""
        yaml_path = Path(config_path) if config_path else None
        if yaml_path is None and os.getenv("RACCCA_CONFIG_PATH"):
            yaml_path = Path(os.environ["RACCCA_CONFIG_PATH"])

        yaml_data = load_yaml_config(yaml_path)
        return cls(**yaml_data)

    def get_weights(self, criteria: list[RacccaCriterion]) -> dict[RacccaCriterion, float]:
        """Return normalized weights for the given criteria."""
        if self.weights:
            raw = {RacccaCriterion(k): float(v) for k, v in self.weights.items()}
            selected = {c: raw.get(c, 1.0) for c in criteria}
        else:
            selected = dict.fromkeys(criteria, 1.0)

        total = sum(selected.values())
        if total <= 0:
            equal = 1.0 / len(criteria)
            return dict.fromkeys(criteria, equal)
        return {c: w / total for c, w in selected.items()}
