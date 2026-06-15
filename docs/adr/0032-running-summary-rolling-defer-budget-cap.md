# ADR 0032: Running summary — rolling 전략 + 역할 분담 + 4k budget cap defer

- Status: Accepted
- Date: 2026-06-15
- Deciders: Arden, Claude (Sub-2c brainstorming)

## Context

`mechanic-spec.md` "Context Window Management" 는 3요소를 명세한다: (a) 8턴 verbatim
윈도우, (b) memory_tags injection, (c) 10턴마다 running summary. (a)/(b) 는 Sub-1/Sub-2
에서 구현됐고 `npc_state.summary` 컬럼도 이미 존재(ADR 0028)하나, (c) running summary 의
생성·주입 로직만 비어 있다. spec 은 "single summarization call, running summary" 라고만
해서 요약 *입력 전략*(rolling vs full)과 budget cap 의 슬라이스 포함 여부가 열려 있었다.

## Decision

1. **Rolling 전략**: 요약 입력 = `이전 summary + 직전 10 exchanges` (상수 크기). full
   재요약(전체 히스토리, 선형 증가) 아님. 이유: (i) 로컬 단일-GPU + TTFT<3s 목표 —
   full 은 세션 후반 지연 spike, rolling 은 상수, (ii) 4k cap 과 정합(입력 상수),
   (iii) spec 용어 자체가 "running".
2. **역할 분담**: memory_tags = 변하지 않는 구조적 앵커(드러난 사실, drift 0),
   summary = 부드러운 서사 흐름/뉘앙스 recap(drift 허용). 이 분담이 rolling 의 drift
   약점을 무해화한다 — 중요 사실은 memory_tags 에 박혀 안 잃는다.
3. **턴-끝 동기 생성**: 요약은 `run_turn` 맨 끝 post-step. 요약 콜 실패해도 플레이어
   턴은 이미 끝나 무영향(기존 summary 유지, 비노출). 핵심 안전 속성.
4. **요약 프롬프트는 `rules/summary.yaml`** (새 파일) — 코드 아닌 데이터. NPC 대사가
   아니므로 check_no_hardcoded_dialogue 대상 아님.
5. **4k token budget cap (drop-oldest verbatim) 은 defer** — 8턴 윈도우 + 상수 rolling
   summary + 200자 입력 cap 이 payload 를 실질 bound. 명시적 cap 은 Gemma 토크나이저
   연동 + drop 로직이 필요해 별 infra. 실측에서 4k 근접 시 후속 하드닝 슬라이스로.

## Alternatives Considered

- A. ★ chosen — rolling + 동기 + cap defer.
- B. Full 재요약 — drift 없으나 입력 선형 증가, 후반 지연 spike, cap 역행, memory_tags 와 중복.
- C. 비동기/백그라운드 요약 잡 — 슬라이스엔 YAGNI (인프라 추가). 후속.

## Consequences

- `npc_state.summary` 가 비로소 쓰임(ADR 0028 forward-compat 실현).
- `build_prompt` 가 `summary` 인자를 받음 — None 일 때 렌더 무변(Sub-1 oracle 회귀 없음).
- 요약 모델 = dialogue 와 동일 tier(별도 infra 없음), `summarize_call` 은 평문 completion.
- 4k cap 은 mechanic-spec 에 deferred 로 명시.

## Related

- ADR 0023 (결정적 게이트 + live off-gate), 0027 (로컬 Gemma), 0028 (스키마 forward-compat),
  0029 (thinking 비활성화 — summarize_call 도 동일).
