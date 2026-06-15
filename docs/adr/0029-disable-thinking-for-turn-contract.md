# ADR 0029: thinking 모델의 reasoning 비활성화 — turn JSON 계약이 빈 content 로 깨지는 것 차단

- Status: Accepted
- Date: 2026-06-15
- Deciders: Arden, Claude (Sub-2b 진입 전 스파이크 중 발견)

## Context

`gemma-4-26B-A4B-it` (및 비교 후보 `qwen3.6-35B-A3B`) 는 **thinking 모델**이다. 현재 llama.cpp 빌드 (`--jinja`) 는 모델의 추론을 `message.reasoning_content` 로 분리하고 실제 답은 `message.content` 에 둔다. 그런데 이 모델들은 답하기 전에 길게 "생각" 하므로, turn 호출의 `max_tokens=1024` 예산을 reasoning 이 전부 소진하고 `content` 는 **빈 문자열** 로 끝난다 (`finish_reason=length`).

`app/llm/client.py` 는 `content` 를 읽어 JSON 파싱한다. content 가 비면 파싱 실패 → `LLMError` → turn loop 이 **매 턴 diegetic fallback** ("머리가 띵하네"). 즉 수리공 vertical slice 가 실제 모델에선 한 번도 작동하지 않았다.

이 버그가 그동안 안 잡힌 이유:
- gate 테스트는 `llm_call` 을 stub → 실제 모델 디코딩을 안 거침.
- off-gate live eval (`tests/live`, ADR 0023) 은 *verbatim 복사 ≤ 임계* 만 검사 → 전부 fallback 이면 verbatim=0 으로 **trivial 하게 통과**.

llama-server 는 요청에 `chat_template_kwargs: {"enable_thinking": false}` 를 주면 chat-template 의 thinking 분기를 끈다. 실측: 이 플래그로 수리공이 정상 in-character JSON (reply + 3 choices) 을 즉시 반환, Layer 4 통과.

## Decision

1. **turn 호출은 thinking 을 끈다.** `app/llm/client.py` 의 `/v1/chat/completions` 페이로드에 `chat_template_kwargs: {"enable_thinking": false}` 를 항상 포함. 모델 선택 (Gemma / Qwen) 과 무관 — 둘 다 thinking 모델이라 동일하게 필요.
2. **live eval 강화.** `tests/live` 가 diegetic fallback 횟수를 세고 `MAX_FALLBACKS` 초과 시 FAIL. trivial 통과 (전부 fallback → verbatim=0) 재발 차단.
3. **gate 회귀 가드.** `tests/llm/test_client.py` 가 페이로드에 `enable_thinking=false` 가 들어가는지 결정적으로 검증 (네트워크 stub).

## Alternatives Considered

- **A. ★ chosen** — 요청 단위 `enable_thinking=false`. 서버 설정 무관, 모델 무관, 게임에 reasoning 불필요.
- **B. 서버 기동 플래그 (`--reasoning-format none`)** — reasoning 을 content 에 inline 으로 남김 → JSON 앞에 `<|channel>thought...` 섞여 파싱 실패 (실측). 부적합.
- **C. `max_tokens` 대폭 증가 + reasoning 후 content 파싱** — 지연·비용 증가, content 가 reasoning 뒤에 온다는 보장 약함. slice 에 reasoning 가치 없음.
- **D. client 가 content 빈 경우 `reasoning_content` 폴백 파싱** — reasoning 은 JSON 이 아니라 산문 → 무의미.

## Consequences

- `docs/mapping-spec.md` 미매핑 항목에 1줄 추가 (lore 무관 디코딩 결정, ADR 0027 과 동급).
- 향후 비-thinking 모델 tier 추가 시 이 플래그는 무시돼도 무해 (알 수 없는 kwarg 는 template 이 무시).
- live eval 이 이제 실제 신호 — `pytest -m live` 가 계약이 닫히는지 검증 (fallback 폭주 시 FAIL).
- (운영 메모) 이 Mac Mini(48GB)는 llama.cpp 모델을 한 번에 하나만 GPU 오프로드 가능 — 모델 A/B 비교 시 동시 로드 금지 (Metal OOM).

## Related

- ADR 0027 (local Gemma json_schema 디코딩 — 같은 LLM 백엔드 계약 영역).
- ADR 0023 (sample_lines verbatim invariant — 이번에 강화된 live eval 이 운반).
- `app/llm/client.py`, `tests/llm/test_client.py`, `tests/live/test_verbatim_eval.py`.
