## 변경 요약

<!-- 무엇을, 왜 -->

## spec-driven 체크리스트

- [ ] 메커니즘 변경 시 `docs/mechanic-spec.md` **+** `docs/mapping-spec.md` 둘 다 갱신 (drift 없음)
- [ ] 새 디자인 결정 → ADR 작성 (`docs/adr/NNNN-*.md`, 시퀀셜) + 영향 spec/YAML 갱신
- [ ] NPC 대사/톤/forgotten_life 변경은 `npcs/*.yaml` 에만 (코드 하드코딩 금지)
- [ ] `python3 scripts/check_yaml.py` green
- [ ] `python scripts/check_no_hardcoded_dialogue.py` exit 0
- [ ] `pytest` green (live 마커 제외 gate)
