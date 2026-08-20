"""Sub-2 도메인 모델. LLM 구조화 출력 + 영속 상태 + 엔드포인트 응답."""

from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict


class Choice(BaseModel):
    model_config = ConfigDict(extra="forbid")
    tone: str
    text: str


class TurnReply(BaseModel):
    """llama-server `emit_turn` json_schema 출력의 검증된 형태."""
    model_config = ConfigDict(extra="forbid")
    reply: str
    awareness_delta: int
    reason: str
    memory_tags: list[str]
    choices: list[Choice]


class NpcState(BaseModel):
    model_config = ConfigDict(extra="forbid")
    awareness: int
    memory_tags: list[str]
    summary: Optional[str] = None


class TurnResponse(BaseModel):
    """`POST /turn` 응답. awareness 정수는 노출 안 함 (mechanic-spec: 숫자 비노출).

    kind 판별자 (ADR 0031): "npc" = NPC 대사, "warning"/"ban" = 프레임 깨는 시스템 메시지.
    reply 는 kind 에 따라 NPC 대사 또는 시스템 메시지 텍스트.

    B1/B6: 자격증명 session_uuid 는 어떤 응답 본문에도 싣지 않는다 — 신원은 쿠키 단일.
    """
    model_config = ConfigDict(extra="forbid")
    kind: Literal["npc", "warning", "ban"] = "npc"
    reply: str
    choices: list[Choice] = []
    matched_term: Optional[str] = None


class SessionState(BaseModel):
    """sessions 행의 검증된 형태 (ADR 0031)."""
    model_config = ConfigDict(extra="forbid")
    warning_count: int
    first_strike_term: Optional[str]
    banned: bool
    ban_reason: Optional[str]
