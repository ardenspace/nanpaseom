# ADR 0016: Boat Moment Name Beats Framework

- Status: Accepted
- Date: 2026-05-11
- Deciders: Arden, `superpowers:brainstorming`, cross-review

## Context

ADR 0015 (혜안 unforgetting)이 *boat moment에서 혜안만 이름 의미 전환*이라는 새 narrative beat을 가져옴. 1차 brainstorming에서 이를 ADR 0004 ("name reclamation asymmetry")로 분리했으나, 교차 리뷰 #3에서 지적 — 0015 reversed면 0004 무의미 = *두 결정이 한 결정의 두 얼굴*.

해결법: 0004를 *framework로 일반화*. 0015는 그 framework의 *혜안 instance*. 두 ADR이 독립적으로 의미 있게 됨.

## Decision

**Boat moment에서 NPC가 자기 이름과 관련된 narrative beat을 가질 수 있다는 framework를 박는다.**

NPC YAML schema:
- `identity.name_status`: `forgotten | given | reclaimed` enum
- `identity.current_display_name`: nullable string
- `identity.forgotten_life.name_candidates`: list of candidate names (forgotten 상태 NPC만)

Boat moment 빌더 (Phase 1.0+) 동작:
- `name_status: forgotten` NPC → LLM 입력에 `name_candidates` pool 주입. LLM이 상황에 어울리는 이름 합성 ("나는… 박OO이었어").
- `name_status: given` NPC (혜안) → LLM 입력에 *의미 전환 template* 주입. ("내 이름이 X인 건 …였어. 근데 이제는…")
- 회차 (playthrough) 마다 풀 유지, LLM이 새 이름 선택 가능.

## Alternatives Considered

- (a) 이름 beat 없음 — 메타 엔딩의 narrative ecology 빈약.
- (b) 모든 NPC 동일 형식 — 3+1 비대칭 (ADR 0015) 손실.
- (c) 0004 (혜안-specific name asymmetry) — 0015와 독립적으로 의미 없음 (cross-review #3).
- (d) ★ chosen — framework 일반화 + NPC별 instance.

## Consequences

- 미래 NPC 추가 (사이비 v1.1) 시 *이미 framework가 있음* — 사이비도 자기 name beat 가능 (예: reclaimed가 *가짜였음을 깨닫는* — "이게 내 이름이 아니었어").
- 빌더에서 NPC별 분기 처리 (name_status 기반).
- `mechanic-spec.md`의 boat moment 섹션은 별도 PR로 본 framework 명시 갱신 필요.

## Related

- ADR 0015 (혜안 instance — 본 framework의 첫 적용).
- ADR 0002 (boat moment as real ending).
- ADR 0017 (사이비 v1.1 — 미래 framework instance 후보).
- ADR 0020 (cross-review #3 followup).
- 모든 `npcs/*.yaml`의 `identity.name_status` + `name_candidates` 필드.
