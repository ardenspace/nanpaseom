"""Sub-2 도메인 모델. LLM 구조화 출력 + 영속 상태 + 엔드포인트 응답."""

from typing import Optional

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
    """`POST /turn` 응답. awareness 정수는 노출 안 함 (mechanic-spec: 숫자 비노출)."""
    model_config = ConfigDict(extra="forbid")
    reply: str
    choices: list[Choice]
    session_uuid: str
