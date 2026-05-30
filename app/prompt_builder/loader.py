"""yaml → pydantic. fail-fast.

Authority:
    - docs/superpowers/specs/2026-05-14-phase-1-sub1-prompt-builder-design.md
    - app/prompt_builder/schemas.py
"""

from functools import lru_cache
from pathlib import Path

import yaml

from app.prompt_builder.schemas import NPCData, RulesData


REPO_ROOT = Path(__file__).resolve().parents[2]
NPCS_DIR = REPO_ROOT / "npcs"
RULES_DIR = REPO_ROOT / "rules"


def load_npc(npc_name: str) -> NPCData:
    """Load + validate npcs/<name>.yaml. fail-fast: 파일 없으면 FileNotFoundError,
    스키마 위반이면 pydantic ValidationError."""
    path = NPCS_DIR / f"{npc_name}.yaml"
    if not path.exists():
        raise FileNotFoundError(f"NPC yaml not found: {path}")
    raw = yaml.safe_load(path.read_text())
    return NPCData.model_validate(raw)


@lru_cache(maxsize=1)
def load_rules() -> RulesData:
    """Load + validate all rules/*.yaml. Cached — rules 는 NPC 별 안 변함
    (Sub-2 turn loop 의 reload 회피)."""
    awareness_bands_raw = yaml.safe_load((RULES_DIR / "awareness_bands.yaml").read_text())
    memory_tags_raw = yaml.safe_load((RULES_DIR / "memory_tags.yaml").read_text())
    boat_outcomes_raw = yaml.safe_load((RULES_DIR / "boat_outcomes.yaml").read_text())
    prompt_skeleton_raw = yaml.safe_load((RULES_DIR / "prompt_skeleton.yaml").read_text())
    return RulesData.model_validate(
        {
            "awareness_bands": awareness_bands_raw,
            "memory_tags": memory_tags_raw,
            "boat_outcomes": boat_outcomes_raw,
            "prompt_skeleton": prompt_skeleton_raw,
        }
    )
