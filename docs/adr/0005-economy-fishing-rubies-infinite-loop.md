# ADR 0005: Economy — Light Fishing + Single Currency 루비 + Infinite Repair Loop

- Status: Accepted
- Date: 2026-05-09
- Deciders: Arden, `grill-me` skill

## Context

순수 대화만 있으면 *잔류 ending*의 emotional weight가 약함. 플레이어가 "남는다"를 *진짜로 선택할 수 있는* 컴포트 활동 필요.

동시에 *트로프 collapse*의 시그니처 모먼트가 경제 메커니즘으로부터 자연 출현하면 narrative ecology가 강해짐.

## Decision

**라이트 1-tap 낚시 + 단일 통화 "루비".**

- 풍경 부두 영역 탭 → 낚시 모드. 찌가 가라앉는 순간 탭 → "잡았다!" 5-15초 단발 비트, 무한 반복.
- 어부 [물고기 줄게] → 🔴 +1. 수리공 [루비 줄게 (현재 N개)] → 🔴 -1 + "더 필요해…"
- **수리공 무한 루프**: 절대 충족 X. 보트 수리는 루비로 트리거되지 않음 (≥1 NPC ending에서 등장 — ADR 0002).
- 루비를 어디에도 못 씀. 그냥 *쌓임*.
- **트로프 collapse 시그니처**: 어부 각성 모먼트 = "이 루비들… 너한테서 받아왔어. *어디서* 가져왔지?"
- **카운터 글리치 사라짐**: boat moment 진입 직후 1초 비트 (stutter 200ms → 흐려짐 500ms → 사라짐 300ms). *결정 순간에 화폐의 환각이 무너짐.*

LLM 시스템 프롬프트 hint: 어부/수리공 system prompt에 `player_total_rubies_given_to_this_npc: N` 변수 주입. LLM이 누적량 보고 자연스럽게 awareness_delta 가중.

## Alternatives Considered

- 컴포트 활동 없음 — 잔류 ending 무게 부족.
- 복수 통화 (낚시 + 농사 + 채광) — solo dev scope 폭주.
- 루비로 보트 수리 게이트 — narrative ecology 깨짐 (보트는 *의지의 회복*이지 *재화의 축적*이 아님).

## Consequences

- NPC YAML에 `hooks.system_prompt_variables` (player_total_rubies_*) 필드.
- 카운터 글리치는 boat moment 진입의 *시각 시그니처* (ADR 0002와 정합).
- 게임 내내 루비 카운터 *안정적*으로 보임 = "있는 척"이 *결정 순간에만 무너짐*.

## Related

- ADR 0002 (boat moment as ending — 보트 트리거는 루비와 무관).
- `docs/mechanic-spec.md` "Fishing & 루비 Economy" 섹션.
