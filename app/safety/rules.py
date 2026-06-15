"""rules/safety.yaml 로더 (cached). Authority: ADR 0030."""

from functools import lru_cache
from pathlib import Path

import yaml

from app.safety.schemas import SafetyRules

RULES_DIR = Path(__file__).resolve().parents[2] / "rules"


@lru_cache(maxsize=1)
def load_safety_rules() -> SafetyRules:
    raw = yaml.safe_load((RULES_DIR / "safety.yaml").read_text())
    return SafetyRules.model_validate(raw)
