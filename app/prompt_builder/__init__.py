"""Sub-1 — 시스템 프롬프트 빌더 (offline pure function).

Public API:
    from app.prompt_builder import build_prompt

Authority:
    - docs/superpowers/specs/2026-05-14-phase-1-sub1-prompt-builder-design.md
    - rules/prompt_skeleton.yaml (template + 메타-게임 instruction)
"""

from app.prompt_builder.renderer import build_prompt

__all__ = ["build_prompt"]
