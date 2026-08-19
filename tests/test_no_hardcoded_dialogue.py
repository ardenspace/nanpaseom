from scripts.check_no_hardcoded_dialogue import (
    STRING_LIT_RE,
    collect_dialogue,
    scan_dialogue,
    scan_frontend_korean,
    scan_paths,
)


def test_collect_dialogue_includes_sample_lines_and_fallback():
    d = collect_dialogue()
    # 수리공 diegetic_fallback (mechanic-spec line 204) 가 수집돼야 함.
    assert any("머리가 띵하" in s for s in d)


def test_app_and_frontend_trees_have_no_hardcoded_dialogue():
    # 현 app/ + frontend/src 트리는 깨끗해야 함.
    assert scan_dialogue() == []


def test_scanner_detects_injected_line(tmp_path):
    d = collect_dialogue()
    sample = next(iter(d))
    f = tmp_path / "bad.py"
    f.write_text(f'NPC_LINE = "{sample}"\n', encoding="utf-8")
    hits = scan_paths([f], d)
    assert hits, "주입된 NPC 대사를 잡아야 함"


def test_frontend_tree_has_no_korean_outside_tone_module():
    # tone.ts 외의 frontend/src 파일에 한글 리터럴이 없어야 함.
    assert scan_frontend_korean() == []


def test_js_string_literal_regex_finds_korean_but_ignores_comments():
    src = '// 한글 주석은 자유\nconst x = "한글 리터럴";\n'
    lits = STRING_LIT_RE.findall(src)
    assert any("한글 리터럴" in lit for lit in lits)
    assert not any("주석" in lit for lit in lits)
