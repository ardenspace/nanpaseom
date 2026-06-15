"""Layer 1 입력 prefilter — 길이 캡 + 페르소나-공격 키워드 차단.

Authority: docs/mechanic-spec.md Layer 1. 키워드는 rules/safety.yaml (ADR 0030).
"""

from pydantic import BaseModel

from app.safety.rules import load_safety_rules


class PrefilterResult(BaseModel):
    blocked: bool
    reason: str | None = None


def _contains_hangul(text: str) -> bool:
    return any("가" <= ch <= "힣" for ch in text)


def check(player_input: str) -> PrefilterResult:
    """입력을 검사. 차단 시 blocked=True + reason."""
    limit = 200 if _contains_hangul(player_input) else 500
    if len(player_input) > limit:
        return PrefilterResult(blocked=True, reason="too_long")
    low = player_input.lower()
    for kw in load_safety_rules().persona_attack:
        if kw.lower() in low:
            return PrefilterResult(blocked=True, reason="persona_attack")
    return PrefilterResult(blocked=False)
