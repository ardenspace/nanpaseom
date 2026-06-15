"""rules/safety.yaml 의 pydantic 스키마 (fail-fast, extra=forbid)."""

from pydantic import BaseModel, ConfigDict


class SafetyMessages(BaseModel):
    model_config = ConfigDict(extra="forbid")
    warning: str
    ban: str


class SafetyRules(BaseModel):
    model_config = ConfigDict(extra="forbid")
    harassment_denylist: list[str]
    persona_attack: list[str]
    messages: SafetyMessages
