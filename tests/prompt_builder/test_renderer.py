"""Renderer test — resolve_band boundary + snapshot (4 cell)."""

from pathlib import Path

import pytest

from app.prompt_builder import build_prompt
from app.prompt_builder.loader import load_rules
from app.prompt_builder.renderer import resolve_band


# -----------------------------------------------------------------------------
# resolve_band — band boundary (spec: low inclusive, high exclusive;
# 마지막 band high inclusive)
# -----------------------------------------------------------------------------


@pytest.mark.parametrize("awareness,expected_range", [
    (0, [0, 30]),
    (15, [0, 30]),
    (29, [0, 30]),
    (30, [30, 60]),
    (45, [30, 60]),
    (59, [30, 60]),
    (60, [60, 85]),
    (84, [60, 85]),
    (85, [85, 100]),
    (92, [85, 100]),
    (100, [85, 100]),  # 마지막 band high inclusive
])
def test_resolve_band(awareness, expected_range):
    rules = load_rules()
    band = resolve_band(awareness, rules.awareness_bands.bands)
    assert band.range == expected_range


@pytest.mark.parametrize("awareness", [-1, 101, 150])
def test_resolve_band_out_of_range_raises(awareness):
    rules = load_rules()
    with pytest.raises(ValueError, match="awareness out of range"):
        resolve_band(awareness, rules.awareness_bands.bands)


# -----------------------------------------------------------------------------
# build_prompt 입력 fail-fast (RuntimeState 검증, code-review followup)
# -----------------------------------------------------------------------------


@pytest.mark.parametrize("bad_awareness", [True, 70.5, -1, 150, "70"])
def test_build_prompt_rejects_bad_awareness(bad_awareness):
    """bool/float/str/범위밖 awareness → ValidationError (strict int)."""
    with pytest.raises(Exception):
        build_prompt(
            npc_name="hyean",
            awareness=bad_awareness,
            memory_tags=["fear"],
            hooks_runtime={},
        )


def test_build_prompt_rejects_unknown_npc():
    """미정의 npc_name → ValidationError (FileNotFoundError 아님)."""
    import pydantic

    with pytest.raises(pydantic.ValidationError):
        build_prompt(npc_name="nonexistent", awareness=70, memory_tags=[], hooks_runtime={})


# -----------------------------------------------------------------------------
# Snapshot — 4 cell verbatim (oracle 추출 .txt 와 정확히 일치)
# -----------------------------------------------------------------------------

SNAPSHOTS_DIR = Path(__file__).parent / "snapshots"

# (npc, awareness, memory_tags, hooks_runtime, snapshot_file)
# scratch hand-synth 의 runtime 가정 과 정확히 일치.
SNAPSHOT_CASES = [
    ("surigong", 15, [], {"player_total_rubies_given_to_this_npc": 0}, "surigong-band-0-30.txt"),
    ("eobu", 45, ["purpose"], {"player_total_rubies_received_from_player": 0}, "eobu-band-30-60.txt"),
    ("halmoni", 92, ["pattern", "loss", "home"],
     {"visible_states_of_other_npcs": {"surigong": "A", "eobu": "B", "hyean": "A"},
      "recent_transitions": ["eobu"]},
     "halmoni-band-85-100.txt"),
    ("hyean", 70, ["pattern", "fear", "loss"], {}, "hyean-band-60-85.txt"),
]


@pytest.mark.parametrize("npc,awareness,memory_tags,hooks,snapshot_file", SNAPSHOT_CASES)
def test_snapshot(npc, awareness, memory_tags, hooks, snapshot_file):
    actual = build_prompt(
        npc_name=npc,
        awareness=awareness,
        memory_tags=memory_tags,
        hooks_runtime=hooks,
    )
    expected = (SNAPSHOTS_DIR / snapshot_file).read_text()
    assert actual == expected, (
        f"Snapshot mismatch for {snapshot_file}.\n"
        f"--- expected ---\n{expected}\n--- actual ---\n{actual}\n"
    )
