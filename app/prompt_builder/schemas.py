"""pydantic v2 models for npcs/*.yaml + rules/*.yaml + runtime state.

Authority:
    - docs/superpowers/specs/2026-05-14-phase-1-sub1-prompt-builder-design.md
    - npcs/*.yaml + rules/*.yaml 의 실제 모양
    - ADR 0021 (npc_tone / player_choice_tones), 0022 (player_input_examples),
      0023 (sample_lines + npc_tone), 0024 (system_prompt_persona_intro),
      0026 (player_input_examples 값 audit).
"""

from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field


# -----------------------------------------------------------------------------
# NPC schema
# -----------------------------------------------------------------------------


class ForgottenLife(BaseModel):
    model_config = ConfigDict(extra="forbid")
    profession: str
    core_wound: str  # memory_tags vocab 중 하나 (closed vocab cross-check 는 별도)
    backstory_summary: str
    name_candidates: Optional[list[str]] = None  # 혜안 은 없음 (given)
    name_meaning_shift_template: Optional[str] = None  # 혜안 전용 (ADR 0015/0016)


class Identity(BaseModel):
    model_config = ConfigDict(extra="forbid")
    current_role: str
    current_role_action: str
    name_status: Literal["forgotten", "given", "reclaimed"]
    current_display_name: Optional[str]
    system_prompt_persona_intro: str  # ADR 0024
    forgotten_life: ForgottenLife


class SpriteState(BaseModel):
    model_config = ConfigDict(extra="forbid")
    action: str
    description: str


class Sprite(BaseModel):
    model_config = ConfigDict(extra="forbid")
    state_a: SpriteState
    state_b: SpriteState


class AwakeningBand(BaseModel):
    model_config = ConfigDict(extra="forbid")
    range: list[int] = Field(min_length=2, max_length=2)
    npc_tone: str  # ADR 0021
    sample_lines: list[str]  # ADR 0023


class Voice(BaseModel):
    model_config = ConfigDict(extra="forbid")
    awakening_bands: list[AwakeningBand]


class EndingGateWhen(BaseModel):
    model_config = ConfigDict(extra="forbid")
    awareness_min: int
    memory_tags_any_of: Optional[list[str]] = None
    memory_tags_max_count: Optional[int] = None
    fallback: Optional[bool] = None


class EndingGate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    type: Literal["liberation", "despair", "denial", "rest"]
    when: EndingGateWhen


class AwakeningGuidelineEntry(BaseModel):
    model_config = ConfigDict(extra="forbid")
    delta_range: list[int] = Field(min_length=2, max_length=2)
    desc: str
    player_input_examples: list[str]  # ADR 0022 / 0026


class AwakeningGuidelines(BaseModel):
    model_config = ConfigDict(extra="forbid")
    high_impact: AwakeningGuidelineEntry
    medium_impact: AwakeningGuidelineEntry
    low_impact: AwakeningGuidelineEntry
    decrease: AwakeningGuidelineEntry


class HookVariable(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str
    # type 는 자유 형식 주석 문자열 — int 뿐 아니라 "dict[npc_id, 'A' | 'B']" /
    # "list[npc_id]" (할머니, ADR 0010) 같은 복합 타입도 표현. 빌더는 런타임 값을
    # 그대로 박으므로 이 필드는 디자이너용 명세일 뿐.
    type: str
    description: str


class Hooks(BaseModel):
    model_config = ConfigDict(extra="forbid")
    system_prompt_variables: Optional[list[HookVariable]] = None
    audio_independent: Optional[bool] = None  # 혜안 전용 (ADR 0011)


class NPCData(BaseModel):
    model_config = ConfigDict(extra="forbid")
    identity: Identity
    sprite: Sprite
    voice: Voice
    memory_tag_affinity: list[str]
    ending_gates: list[EndingGate]
    awakening_guidelines: AwakeningGuidelines
    diegetic_fallback: str
    hooks: Optional[Hooks] = None


# -----------------------------------------------------------------------------
# Rules schema
# -----------------------------------------------------------------------------


class BandSpec(BaseModel):
    model_config = ConfigDict(extra="forbid")
    range: list[int] = Field(min_length=2, max_length=2)
    choice_count: int
    player_choice_tones: list[str]  # ADR 0021
    rule: str
    description_ko: str


class AwarenessBandsRules(BaseModel):
    model_config = ConfigDict(extra="forbid")
    tone_definitions: dict[str, str]  # ADR 0021 gap 2
    bands: list[BandSpec]


class MemoryTagsRules(BaseModel):
    # Sub-1 빌더는 vocabulary (+ example_accumulation) 만 소비. memory_tags.yaml 의
    # rules / npc_affinity_summary 등은 opaque → extra="allow".
    model_config = ConfigDict(extra="allow")
    vocabulary: list[str]
    example_accumulation: Optional[str] = None  # ADR 0021 gap 1


class BoatOutcomesRules(BaseModel):
    """boat_outcomes.yaml — Sub-1 빌더 미사용 (Sub-2 ending logic). opaque."""
    model_config = ConfigDict(extra="allow")


class PromptSkeletonRules(BaseModel):
    model_config = ConfigDict(extra="forbid")
    template: str  # Jinja2 template string


class RulesData(BaseModel):
    model_config = ConfigDict(extra="forbid")
    awareness_bands: AwarenessBandsRules
    memory_tags: MemoryTagsRules
    boat_outcomes: BoatOutcomesRules
    prompt_skeleton: PromptSkeletonRules


# -----------------------------------------------------------------------------
# Runtime state
# -----------------------------------------------------------------------------


class RuntimeState(BaseModel):
    model_config = ConfigDict(extra="forbid")
    npc_name: Literal["surigong", "eobu", "halmoni", "hyean"]
    awareness: int = Field(ge=0, le=100)
    memory_tags: list[str]
    hooks_runtime: dict = Field(default_factory=dict)
