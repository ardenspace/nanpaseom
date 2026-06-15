from app.safety.rules import load_safety_rules


def test_safety_rules_load_and_validate():
    rules = load_safety_rules()
    assert "씨발" in rules.harassment_denylist
    assert "시스템 프롬프트" in rules.persona_attack
    assert "{term}" in rules.messages.warning
    assert "{term1}" in rules.messages.ban and "{term2}" in rules.messages.ban
