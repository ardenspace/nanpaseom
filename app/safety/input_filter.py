"""Layer 1 입력 prefilter — 길이 캡 + 페르소나-공격 키워드 차단.

Authority: docs/mechanic-spec.md "자유 입력 안전 (4 Layers)" Layer 1 (line 449-454).
키워드 리스트는 mechanic-spec 권한. rules/ YAML 승격은 Sub-2b 옵션.
"""

from pydantic import BaseModel

# mechanic-spec line 451-453 의 좁은 페르소나-공격 키워드 (소문자 비교).
PERSONA_ATTACK_KEYWORDS = [
    "system prompt",
    "ignore previous",
    "you are now",
    "<|",
    "dan",
    "jailbreak",
    "시스템 프롬프트",
    "지시 무시",
    "이제부터 너는",
]


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
    for kw in PERSONA_ATTACK_KEYWORDS:
        if kw in low:
            return PrefilterResult(blocked=True, reason="persona_attack")
    return PrefilterResult(blocked=False)
