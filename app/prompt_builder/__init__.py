"""Sub-1 — 시스템 프롬프트 빌더 (offline pure function).

Public API:
    from app.prompt_builder import build_prompt

Authority:
    - docs/superpowers/specs/2026-05-14-phase-1-sub1-prompt-builder-design.md
    - rules/prompt_skeleton.yaml (template + 메타-게임 instruction)
"""

# build_prompt 은 renderer.py 가 구현 후 노출됨 (Task 19). 현재 는 placeholder.
__all__ = ["build_prompt"]
