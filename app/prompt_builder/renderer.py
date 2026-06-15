"""Jinja2 + pydantic → system prompt string. verbatim copy only.

Authority:
    - docs/superpowers/specs/2026-05-14-phase-1-sub1-prompt-builder-design.md
    - rules/prompt_skeleton.yaml (template)

Jinja Environment: trim_blocks + lstrip_blocks + keep_trailing_newline.
이 조합이 skeleton 의 block 태그({% for %}/{% if %})를 깔끔히 처리해
oracle 포맷(bulleted/대괄호/빈-band)을 재생산한다.
"""

import warnings

from jinja2 import Environment, StrictUndefined

from app.prompt_builder.loader import load_npc, load_rules
from app.prompt_builder.schemas import BandSpec, RuntimeState


def resolve_band(awareness: int, bands: list[BandSpec]) -> BandSpec:
    """awareness int → BandSpec.

    Boundary 룰: [low, high] 의 low = inclusive, high = exclusive.
    단 마지막 band 의 high = inclusive (awareness=100 도 마지막 band).
    """
    if not (0 <= awareness <= 100):
        raise ValueError(f"awareness out of range: {awareness}")

    for i, band in enumerate(bands):
        low, high = band.range
        is_last = i == len(bands) - 1
        if low <= awareness < high or (is_last and awareness == high):
            return band

    raise ValueError(f"ambiguous band boundary: awareness={awareness} not in any band")


def build_prompt(
    npc_name: str,
    awareness: int,
    memory_tags: list[str],
    hooks_runtime: dict | None = None,
    summary: str | None = None,
) -> str:
    """Public API. yaml + runtime state → system prompt string.

    입력은 RuntimeState 로 fail-fast 검증 (npc_name enum / awareness 0-100 int /
    memory_tags list / hooks_runtime dict). 잘못된 타입·범위는 ValidationError.
    """
    state = RuntimeState(
        npc_name=npc_name,
        awareness=awareness,
        memory_tags=memory_tags,
        summary=summary,
        hooks_runtime=hooks_runtime or {},
    )
    npc_name = state.npc_name
    awareness = state.awareness
    memory_tags = state.memory_tags
    summary = state.summary
    hooks_runtime = state.hooks_runtime

    npc = load_npc(npc_name)
    rules = load_rules()
    band = resolve_band(awareness, rules.awareness_bands.bands)

    # NPC 의 해당 band voice (npc_tone + sample_lines)
    band_npc = next(
        (b for b in npc.voice.awakening_bands if b.range == band.range),
        None,
    )
    if band_npc is None:
        raise ValueError(
            f"NPC {npc_name} 의 voice.awakening_bands 에 band {band.range} 가 없음"
        )

    # hooks_runtime 검증: NPC yaml 명세 대비 키 부족 = ValueError, 잉여 = warning + ignore
    hooks_runtime = hooks_runtime or {}
    if npc.hooks and npc.hooks.system_prompt_variables:
        required = {hv.name for hv in npc.hooks.system_prompt_variables}
        provided = set(hooks_runtime.keys())
        missing = required - provided
        if missing:
            raise ValueError(f"missing hook variable: {missing}")
        extra = provided - required
        if extra:
            warnings.warn(
                f"extra hooks_runtime keys (ignored): {extra}",
                UserWarning,
                stacklevel=2,
            )
            hooks_runtime = {k: v for k, v in hooks_runtime.items() if k in required}

    env = Environment(
        undefined=StrictUndefined,
        trim_blocks=True,
        lstrip_blocks=True,
        keep_trailing_newline=True,
    )
    template = env.from_string(rules.prompt_skeleton.template)
    return template.render(
        npc=npc,
        rules=rules,
        band=band,
        band_npc=band_npc,
        awareness=awareness,
        memory_tags=memory_tags,
        summary=summary,
        hooks_runtime=hooks_runtime,
    )
