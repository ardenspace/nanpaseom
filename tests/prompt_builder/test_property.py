"""Property test — 16 cell (NPC × band) cross-product invariant.

verbatim 검증(4 cell snapshot)보다 약하나, 12 cell 의 covering check.
6 invariant × 16 cell = 96 assertions.
"""

import pytest

from app.prompt_builder import build_prompt
from app.prompt_builder.loader import load_npc, load_rules


NPC_NAMES = ["surigong", "eobu", "halmoni", "hyean"]
BAND_INDICES = [0, 1, 2, 3]  # 0=0-30, 1=30-60, 2=60-85, 3=85-100


def _awareness_for(band_idx: int) -> int:
    """Band 중간 값."""
    return {0: 15, 1: 45, 2: 72, 3: 92}[band_idx]


def _memory_tags_for(band_idx: int) -> list[str]:
    return {
        0: [],
        1: ["purpose"],
        2: ["pattern", "fear", "loss"],
        3: ["pattern", "loss", "home"],
    }[band_idx]


def _hooks_for(npc_name: str) -> dict:
    """NPC hooks 명세 따라 minimum-required input. 명세 없으면 빈 dict."""
    npc = load_npc(npc_name)
    if not (npc.hooks and npc.hooks.system_prompt_variables):
        return {}
    return {hv.name: 0 for hv in npc.hooks.system_prompt_variables}


def _build(npc_name, band_idx):
    return build_prompt(
        npc_name=npc_name,
        awareness=_awareness_for(band_idx),
        memory_tags=_memory_tags_for(band_idx),
        hooks_runtime=_hooks_for(npc_name),
    )


@pytest.mark.parametrize("npc_name", NPC_NAMES)
@pytest.mark.parametrize("band_idx", BAND_INDICES)
def test_layer3_meta_defense_always_present(npc_name, band_idx):
    assert "[Layer 3 메타-디펜스]" in _build(npc_name, band_idx)


@pytest.mark.parametrize("npc_name", NPC_NAMES)
@pytest.mark.parametrize("band_idx", BAND_INDICES)
def test_npc_tone_verbatim_in_output(npc_name, band_idx):
    npc = load_npc(npc_name)
    out = _build(npc_name, band_idx)
    assert npc.voice.awakening_bands[band_idx].npc_tone in out


@pytest.mark.parametrize("npc_name", NPC_NAMES)
@pytest.mark.parametrize("band_idx", BAND_INDICES)
def test_sample_lines_verbatim_in_output(npc_name, band_idx):
    npc = load_npc(npc_name)
    out = _build(npc_name, band_idx)
    for line in npc.voice.awakening_bands[band_idx].sample_lines:
        assert line in out, f"sample_line missing: {line!r}"


@pytest.mark.parametrize("npc_name", NPC_NAMES)
@pytest.mark.parametrize("band_idx", BAND_INDICES)
def test_persona_intro_verbatim_in_output(npc_name, band_idx):
    npc = load_npc(npc_name)
    out = _build(npc_name, band_idx)
    assert npc.identity.system_prompt_persona_intro.strip() in out


@pytest.mark.parametrize("npc_name", NPC_NAMES)
@pytest.mark.parametrize("band_idx", BAND_INDICES)
def test_choice_rule_in_output(npc_name, band_idx):
    rules = load_rules()
    out = _build(npc_name, band_idx)
    assert rules.awareness_bands.bands[band_idx].rule in out


@pytest.mark.parametrize("npc_name", NPC_NAMES)
@pytest.mark.parametrize("band_idx", BAND_INDICES)
def test_injected_memory_tags_in_vocab_and_output(npc_name, band_idx):
    rules = load_rules()
    out = _build(npc_name, band_idx)
    vocab = set(rules.memory_tags.vocabulary)
    for tag in _memory_tags_for(band_idx):
        assert tag in vocab, f"tag {tag} not in closed vocab"
        assert tag in out
