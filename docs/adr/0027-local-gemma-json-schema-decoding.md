# ADR 0027: local Gemma 4 (llama-server) + json_schema 제약 디코딩이 prompt-parse-retry 전제를 대체

- Status: Accepted
- Date: 2026-05-30
- Deciders: Arden, Claude (Sub-2 brainstorming session)

## Context

mechanic-spec Approach C (line 92, 232) 는 *llama-server + local Gemma 26-27B Q4 on Mac Mini* 를 Tier-1 로 명세. 이 서버에 `gemma-4-26B-A4B-it` (MoE ~4B active, unsloth Q4_K_M GGUF, `/Users/arden/gemma-4-26B/`) 가 `llama-server` (llama.cpp, homebrew) 로 서빙 준비됨 — Approach C 의 원래 가정과 정합. Error-Handling 섹션 (line 199-212) 전체가 *prompt-for-JSON → parse → retry once → diegetic fallback* 로 쓰임 — 로컬 모델이 clean JSON 을 못 내는 전제.

llama-server 는 `--json-schema` / per-request `response_format: {type: "json_schema"}` 로 **GBNF 제약 디코딩** 을 제공 — 출력이 schema-valid JSON 임을 보장. 즉 "malformed JSON 거의 불가" 속성이 클라우드 tool-use 없이 로컬에서 확보됨. 이는 error-handling 전제 대체 라는 authority-touching 사실.

(이전 라운드 brainstorming 은 Anthropic Claude tool-use 를 택했으나, API 키 부재 + 로컬 추론 선호로 폐기. 로컬 Gemma 가 Approach C 의 원래 tier 였으므로 이 결정은 tier deviation 이 아니라 *복귀*.)

## Decision

1. **Model tier = local Gemma 4 26B-A4B via llama-server** (Approach C Tier-1 확정). failover tier 추상화는 Sub-2b.
2. **턴 JSON 계약 = `json_schema` 제약 디코딩.** turn 스키마 (`reply` / `awareness_delta` / `reason` / `memory_tags` / `choices`) 를 JSON schema 로 정의, llama-server `/v1/chat/completions` 의 `response_format: {type: "json_schema", json_schema: {...}}` 에 주입해 출력 강제.
3. **diegetic fallback 재정의** = parse 실패가 아니라 *llama-server 에러/timeout + Layer 4 위반* 전용.
4. prompt caching: llama.cpp 의 서버-측 prefix KV cache (정적 system 접두 자동 재사용). 코드 측 제어 불필요.
5. `system` 전달: OpenAI-호환 system 메시지 + `--jinja` (Gemma chat-template). Gemma 가 system role 미지원 시 첫 user 메시지에 prepend (구현 검증 포인트, Task 7).

## Alternatives Considered

- **A. ★ chosen** — local Gemma 4 + json_schema 제약 디코딩, error-handling 재정의.
- **B. prompt-for-JSON + retry (spec 원래 경로)** — 그래마 없이 프롬프트 의존. 단순·endpoint무관하나 4B-active 모델엔 fragile → fallback 노이즈.
- **C. OpenAI tool/function calling on llama-server** — Gemma template/모델 의존적, 4B-active 에서 shape 강제는 json_schema 그래마가 더 견고.
- **D. Anthropic Claude tool-use (이전 라운드)** — API 키 부재 + 로컬 선호로 폐기.

## Consequences

- `docs/mechanic-spec.md` Error-Handling 섹션 갱신: JSON parse-failure 경로 near-dead (json_schema 제약), fallback = 서버에러/Layer4-위반.
- `docs/mapping-spec.md` "미매핑 항목 (의도적)" 에 json_schema 계약 추가 (lore 무관 implementation detail; 기존 "LLM 백엔드 tiered failover" 와 동급).
- live eval 은 클라우드 비용/키 없이 로컬 llama-server 로 실행 — 결정성 gate 외부의 real-model signal 이 무료·재현가능.
- Sub-2b 에서 비-llama 모델 tier 추가 시 이 ADR 재방문.

## Related

- `docs/superpowers/specs/2026-05-30-phase-1-sub2-surigong-vertical-slice-design.md` Decision 3.
- ADR 0023 (sample_lines verbatim ≤ N invariant — 디코딩 방식과 무관하게 live eval 로 검증).
- mechanic-spec line 92/232 (llama-server + Gemma Tier-1), line 199-212 (Error-Handling, 갱신 대상).
