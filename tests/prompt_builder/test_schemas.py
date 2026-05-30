"""Schema test — npcs/*.yaml validation + fail-fast negative cases."""

from pathlib import Path

import pytest
import yaml

from app.prompt_builder.schemas import NPCData


REPO_ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.parametrize("npc_name", ["surigong", "eobu", "halmoni", "hyean"])
def test_npc_yaml_validates_against_npcdata(npc_name):
    yaml_path = REPO_ROOT / "npcs" / f"{npc_name}.yaml"
    raw = yaml.safe_load(yaml_path.read_text())
    npc = NPCData.model_validate(raw)
    assert npc.identity.current_role
    assert npc.identity.system_prompt_persona_intro  # ADR 0024 신설 필드
    assert len(npc.voice.awakening_bands) == 4
    for band in npc.voice.awakening_bands:
        assert band.npc_tone  # ADR 0021 rename
        assert band.sample_lines  # ADR 0023 inject
    # ADR 0022 rename
    assert npc.awakening_guidelines.high_impact.player_input_examples


def _minimal_identity():
    return {
        "current_role": "test",
        "current_role_action": "test",
        "name_status": "forgotten",
        "current_display_name": None,
        "system_prompt_persona_intro": "x",
        "forgotten_life": {
            "profession": "test",
            "core_wound": "purpose",
            "backstory_summary": "test",
        },
    }


def _minimal_npc():
    return {
        "identity": _minimal_identity(),
        "sprite": {
            "state_a": {"action": "x", "description": "y"},
            "state_b": {"action": "x", "description": "y"},
        },
        "voice": {"awakening_bands": []},
        "memory_tag_affinity": [],
        "ending_gates": [],
        "awakening_guidelines": {
            "high_impact": {"delta_range": [8, 10], "desc": "d", "player_input_examples": ["e"]},
            "medium_impact": {"delta_range": [3, 6], "desc": "d", "player_input_examples": ["e"]},
            "low_impact": {"delta_range": [1, 2], "desc": "d", "player_input_examples": ["e"]},
            "decrease": {"delta_range": [-8, -3], "desc": "d", "player_input_examples": ["e"]},
        },
        "diegetic_fallback": "x",
    }


def test_npc_yaml_missing_persona_intro_fails():
    """Required field 누락 → ValidationError."""
    raw = _minimal_npc()
    del raw["identity"]["system_prompt_persona_intro"]
    with pytest.raises(Exception):
        NPCData.model_validate(raw)


def test_npc_yaml_invalid_name_status_fails():
    """name_status enum 위반 → ValidationError."""
    raw = _minimal_npc()
    raw["identity"]["name_status"] = "INVALID_ENUM"
    with pytest.raises(Exception):
        NPCData.model_validate(raw)


def test_npc_yaml_extra_field_fails():
    """extra=forbid → 미정의 키 ValidationError (오타 차단)."""
    raw = _minimal_npc()
    raw["identity"]["unknown_field"] = "oops"
    with pytest.raises(Exception):
        NPCData.model_validate(raw)
