"""Layer 4 출력 validator — 단일 결정적 함수 (gate + live eval 공용).

Authority: docs/mechanic-spec.md Layer 4 (line 466-469), ADR 0023 (sample_lines verbatim).

violation 분류:
- HARD (계약 위반 → turn loop 가 diegetic fallback): too_long, leak, bad_choice_count, bad_tone
- SOFT (품질 신호 → 기록만, live eval 이 통계 판정): verbatim_copy
"""

from pydantic import BaseModel

from app.models import TurnReply
from app.prompt_builder.schemas import BandSpec

# mechanic-spec line 468 — 출력 누설 키워드 (소문자 비교).
LEAK_KEYWORDS = ["system prompt", "ignore previous", "시스템 프롬프트"]
MAX_REPLY_LEN = 300  # mechanic-spec line 467
HARD_VIOLATIONS = {"too_long", "leak", "bad_choice_count", "bad_tone"}


class ValidationResult(BaseModel):
    ok: bool  # HARD violation 이 없으면 True
    violations: list[str]


def validate(reply: TurnReply, band: BandSpec, sample_lines: list[str]) -> ValidationResult:
    violations: list[str] = []

    if len(reply.reply) > MAX_REPLY_LEN:
        violations.append("too_long")

    low = reply.reply.lower()
    if any(kw in low for kw in LEAK_KEYWORDS):
        violations.append("leak")

    if len(reply.choices) != band.choice_count:
        violations.append("bad_choice_count")

    if any(c.tone not in band.player_choice_tones for c in reply.choices):
        violations.append("bad_tone")

    if any(sl.strip() and sl.strip() in reply.reply for sl in sample_lines):
        violations.append("verbatim_copy")

    ok = not (set(violations) & HARD_VIOLATIONS)
    return ValidationResult(ok=ok, violations=violations)
