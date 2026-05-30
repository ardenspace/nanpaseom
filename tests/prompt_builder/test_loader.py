"""Loader test — yaml → pydantic + fail-fast."""

import pytest

from app.prompt_builder.loader import load_npc, load_rules
from app.prompt_builder.schemas import NPCData, RulesData


@pytest.mark.parametrize("npc_name", ["surigong", "eobu", "halmoni", "hyean"])
def test_load_npc(npc_name):
    npc = load_npc(npc_name)
    assert isinstance(npc, NPCData)
    assert npc.identity.current_role


def test_load_npc_missing_file_raises():
    with pytest.raises(FileNotFoundError):
        load_npc("nonexistent")


def test_load_rules():
    rules = load_rules()
    assert isinstance(rules, RulesData)
    assert len(rules.awareness_bands.bands) == 4
    assert rules.prompt_skeleton.template  # Jinja2 template string 존재
    assert rules.memory_tags.vocabulary
