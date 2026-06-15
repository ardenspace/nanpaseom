from app.safety.moderation import SafetyVerdict, denylist_checker, detect


def _checker():
    return denylist_checker(["씨발", "ㅅㅂ", "개새끼"])


def test_clean_input_passes():
    v = detect("오늘 보트 수리 잘 돼?", [_checker()])
    assert v.category == "clean"
    assert v.matched_term is None


def test_denylist_hit_returns_matched_term():
    v = detect("이 씨발 보트", [_checker()])
    assert v.category == "harassment"
    assert v.matched_term == "씨발"


def test_normalization_catches_spaced_variant():
    # "씨 발" → 정규화 후 "씨발" 매칭.
    v = detect("씨 발 진짜", [_checker()])
    assert v.category == "harassment"
    assert v.matched_term == "씨발"


def test_checker_order_first_nonclean_wins():
    a = denylist_checker(["개새끼"])
    b = denylist_checker(["씨발"])
    v = detect("개새끼 씨발", [a, b])
    assert v.matched_term == "개새끼"  # 첫 checker 우선


def test_empty_after_normalize_is_clean():
    v = detect("   ", [_checker()])
    assert v.category == "clean"


def test_second_checker_consulted_when_first_clean():
    # 확장점 계약: 첫 checker 가 clean 이면 다음 checker 가 호출된다 (v1.1 ml_checker).
    clean = denylist_checker(["없는단어"])
    hit = denylist_checker(["씨발"])
    v = detect("이 씨발", [clean, hit])
    assert v.category == "harassment"
    assert v.matched_term == "씨발"
