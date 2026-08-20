# 난파섬 — Mapping Spec (Mechanic ↔ Lore)

이 문서는 *정렬 권한* spec. `mechanic-spec.md` (시스템)와 `world-spec.md` (서사)의 정합을 보장한다.

## Mapping Table

| Mechanic (PRD) | Lore (망각의 섬) |
|---|---|
| Shipwreck frame (플레이어가 난파선으로 도착) | 반포기 상태로 떠밀려옴 (자발 X) |
| NPC가 트로프에 갇힘 | 망각의 의식(ritual)이 자아의 빈자리를 채움 |
| Awareness gauge 0-100 | 잃어버린 자아의 복원도 |
| memory_tags 10종 | 도망쳐 온 원래 삶의 파편 |
| 3→2→1→0 UI 축소 | 주어진 선택지가 줄고 *자기 언어*가 회복됨 |
| 보트 5분기 엔딩 | "떠나고 싶은 의지"의 회복 양상 |
| 보트는 ≥1 NPC awareness 85+에 등장 | 보트는 *의지가 있는 자에게만 보임* |
| 루비 무한 루프 (수리공 "더 필요해") | 결핍감으로 망각을 유지하는 자가-기제 |
| 카운터 글리치 사라짐 (boat moment) | 결정 순간에 환각이 무너짐 |
| 글로벌 awareness ≥40 mutter | 망각 시스템이 *흔들리기 시작*하는 신호 |
| Sprite state A → B 전환 (awareness 60+) | 망각의 의식이 멈춤. *처음으로 정면을 본다* |
| 할머니의 시각적 hint (다른 NPC state A↔B 관찰) | 가장 오래 머문 자가 *루프의 가장자리*를 본다 |
| 혜안의 4-band escalation | 사람을 안 보려 했던 자가 *처음으로 동행을 발견*하는 과정 |
| Boat moment 이름 beat (3 회수 + 1 의미 전환) | 망각된 자의 이름 복원 vs 못 잊은 자의 의미 전환 (ADR 0015, 0016) |
| 자유 입력 안전 4-layer + 2-strike | 섬의 *유한한 인내심* — 의지 회복하러 온 자에게는 응답, 파괴하러 온 자에게는 차단 |
| 회차 (playthrough) 모델 | 섬은 끝없이 다른 사람을 받아들임. *플레이어*는 회차마다 새 인격 |
| 할머니의 시그니처 "나… 이 대화 수백 번 했어" | 가장 오래 머문 자만이 *루프 자체*를 감지함 |

## Drift 방지 룰

이 매핑은 *살아있다*. 변경 룰:

1. 메커니즘 신규 추가 / 변경 → 이 표에 행 추가 / 갱신
2. lore 신규 추가 / 변경 → 이 표에 행 추가 / 갱신
3. 표에 *없는 메커니즘이 발견되면* → drift. 둘 중 하나:
   - 메커니즘이 lore 없이도 정당화되면 → 아래 "미매핑 항목"으로 명시 추가
   - 그렇지 않으면 → lore 추가 or 메커니즘 제거
4. PR에서 `mechanic-spec.md` / `world-spec.md` 변경이 있는데 `mapping-spec.md`가 변경되지 않았다면 → 리뷰 reject

이 룰은 *암묵적 표류 금지*가 목적.

## 미매핑 항목 (의도적)

다음은 *lore 의미 없이* 메커니즘 자체의 implementation detail:

- LLM 백엔드 tiered failover (PRD Premise 4)
- Postgres 스키마
- Mac Mini / Cloudflare Tunnel 인프라
- Mobile responsive layout
- CC0 픽셀 아트 sourcing
- 턴 출력 JSON 계약 (`json_schema` 제약 디코딩, `emit_turn`) — llama.cpp 구조화 출력, lore 무관 제작 결정 (ADR 0027)
- thinking 모델 reasoning 비활성화 (`chat_template_kwargs.enable_thinking=false`) — gemma-4/qwen3 추론 토큰이 `content` 를 비우는 것 차단, lore 무관 디코딩 결정 (ADR 0029)
- 안전 영속 스키마 (`sessions`/`safety_events`) + 응답 `kind` 판별자 — lore 무관 제작 결정 (ADR 0031)
- Running summary 의 rolling 입력 전략 + 4k budget cap defer — 컨텍스트 관리 제작 결정 (ADR 0032)
- 세션 신원/쿠키/공개 표면 위생 — 쿠키 단일 신원 + 서버 민팅, 쿠키 속성 4종 + bearer 수용, assets 화이트리스트 + 자동 문서 봉인, 세이브 코드 단어 프리픽스 형식, 180일 영속 쿠키 — lore 무관 배포 준비 결정 (ADR 0033–0037)

이들은 망각의 섬 lore와 무관한 *제작 결정*. mapping table은 *게임 안에서 플레이어가 경험하는 메커니즘*에 한정.
