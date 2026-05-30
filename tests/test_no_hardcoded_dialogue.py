from scripts.check_no_hardcoded_dialogue import collect_dialogue, scan_app


def test_collect_dialogue_includes_sample_lines_and_fallback():
    d = collect_dialogue()
    # 수리공 diegetic_fallback (mechanic-spec line 204) 가 수집돼야 함.
    assert any("머리가 띵하" in s for s in d)


def test_app_tree_has_no_hardcoded_dialogue():
    # 현 app/ 트리는 깨끗해야 함.
    assert scan_app() == []


def test_scanner_detects_injected_line(tmp_path):
    d = collect_dialogue()
    sample = next(iter(d))
    f = tmp_path / "bad.py"
    f.write_text(f'NPC_LINE = "{sample}"\n', encoding="utf-8")
    from scripts.check_no_hardcoded_dialogue import scan_paths
    hits = scan_paths([f], d)
    assert hits, "주입된 NPC 대사를 잡아야 함"
