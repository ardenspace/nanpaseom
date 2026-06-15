# ADR 0030: 결정적 디니리스트 2-strike 우선, ML 모더레이션 디퍼

- Status: Accepted
- Date: 2026-06-15
- Deciders: Arden, Claude (Sub-2b brainstorming)

## Context

ADR 0009 는 안전 Layer 2 를 OpenAI Moderation API 로 명세했다. 그러나 ADR 0027 에서
로컬-온리로 피벗했고(클라우드 키 없음), 이 Mac Mini(48GB)는 llama.cpp 모델을 한 번에
하나만 GPU 오프로드 가능(가드 모델 상시 GPU 부담). Layer 2.5(2-strike)의 감지 트리거 중
(a) 한국어 디니리스트는 *이미 키워드 매칭이라 로컬·결정적*, (b) ML 카테고리만 대체 필요.

## Decision

1. 이 슬라이스의 모더레이션 = **결정적 디니리스트(키워드) 트랙만**. 이유: (i) 게이트
   테스트 가능(ADR 0029 의 테스트 불가 live 경로 교훈의 반대), (ii) 하드웨어 경합 0,
   (iii) 2-strike 윤리 stance 를 end-to-end 출하.
2. ML 분류기(violence/self-harm/hate + 카테고리 성적 감지)는 **v1.1 로 디퍼** —
   `moderation.detect(text, checkers)` 의 두 번째 checker 로 끼울 인터페이스만 연다.
3. 안전 데이터(디니리스트·페르소나공격·메시지)는 `rules/safety.yaml` — 코드 아닌 데이터
   (튜닝은 YAML). Layer 1 의 페르소나공격 키워드도 여기로 승격.

## Alternatives Considered

- A. ★ chosen — 결정적 디니리스트, ML 디퍼.
- B. Gemma 를 모더레이션 판정에 재사용 — 입력당 LLM 콜(+지연), 비결정적, 자체 eval 필요.
- C. 전용 가드 모델(Llama Guard) CPU — 한국어 약함 + 모델/인프라 추가.

## Consequences

- ADR 0009 Layer 2 의 ML 부분은 v1.1. Layer 2.5 의 디니리스트 트랙만 이번에.
- `docs/mechanic-spec.md` Layer 2.5 섹션에 Sub-2b 노트.
- `moderation.detect` 의 checker 리스트가 확장점 (v1.1 ml_checker append).

## Related

- ADR 0009 (4-layer 안전), 0027 (로컬-온리), 0028 (스키마 deferral), 0029 (결정적 테스트 교훈).
- 메모리: macmini-gpu-single-model-offload.
