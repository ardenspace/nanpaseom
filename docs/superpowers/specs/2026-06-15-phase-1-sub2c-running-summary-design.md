# Phase 1.0 Sub-2c — Running Summary 슬라이스 Design Spec

- Date: 2026-06-15
- Deciders: Arden, Claude (brainstorming session)
- Status: Approved (design) → 다음 단계는 implementation plan (writing-plans)

## 목표 (Goal)

수리공 `POST /turn` 의 컨텍스트 윈도우 전략에서 **마지막 비어 있는 기둥**을 채운다 — **running NPC memory summary**. `mechanic-spec.md` "Context Window Management" (lines 185–195) 의 3요소 중 verbatim 8턴 윈도우와 memory_tags injection 은 Sub-1/Sub-2 에서 이미 구현됐고, **10턴마다의 running summary 만 비어 있다**. `npc_state.summary` 컬럼은 이미 존재하지만(migration 001) 아무도 쓰지 않고 프롬프트에 주입도 안 된다 — 이 슬라이스가 그 로직을 채운다.

Sub-2 가 "턴 루프가 닫힌다", Sub-2b 가 "자유 입력이 안전하게 처리된다" 를 증명했다면, Sub-2c 는 **"긴 대화에서 NPC 가 윈도우 밖 과거를 기억한다"** 를 증명한다.

## 범위 (Scope)

**In:**
- `rules/summary.yaml` — 요약 system 프롬프트 템플릿 (코드 아닌 YAML — 레포 철학 일관).
- `app/turn/summarizer.py` — `summarize(prior, exchanges, *, llm_call) -> str` 순수 오케스트레이션 (LLM 의존성 주입).
- `app/store/repo.py` — `count_exchanges`, `load_turns_since`, `save_summary` 추가.
- `app/prompt_builder/renderer.py` + `rules/prompt_skeleton.yaml` — `summary` 주입 슬롯.
- `app/turn/loop.py` — ① `state.summary` 프롬프트 주입, ② 턴 끝 trigger 시 summarizer 호출.
- ADR 0032 — rolling 전략 + 역할 분담 + 프롬프트 YAML 거주 + 동기 생성 + 4k cap defer.

**Out (의도적 defer):**
- **4k token budget cap (drop-oldest verbatim)** — 8턴 윈도우 + 상수 rolling summary + 입력 200자 cap(input_filter) 이 이미 payload 를 실질 bound. 명시적 cap 은 Gemma 토크나이저 연동 + drop 로직이 필요해 별 infra. 실측에서 4k 근접 시 후속 하드닝 슬라이스로 (ADR 0032 에 명시).
- 비동기/백그라운드 요약 잡 — 동기(턴 끝) 로 충분. 백그라운드는 후속.
- 나머지 3 NPC, 프론트엔드, save-code.

## 핵심 결정 (Key Decisions)

### D1. Rolling 요약 전략 (vs full re-summarize)
입력 = **`이전 summary + 직전 10 exchanges`** (상수 크기), full 재요약(전체 히스토리, 선형 증가) 아님.

근거:
1. **memory_tags 가 drift 를 이미 막는다** — 드러난 하드 팩트는 memory_tags 에 append-only 로 영구 고정(drift 0). rolling summary 가 산문을 흘려도 중요 사실은 안 잃는다. full 의 "원본 기반 정확도" 는 이 게임에선 memory_tags 가 이미 담당 → 중복 투자.
2. **로컬 단일-GPU + TTFT <3s 목표** — full 은 세션 후반일수록 요약 콜 입력이 커져 지연 spike. rolling 은 상수 입력 → 지연 예측 가능.
3. **4k budget cap 과 정합** — rolling 은 입력이 상수라 cap 을 설계상 자동 준수.
4. spec 용어 자체가 "**Running** summary".

### D2. 역할 분담 (summary ↔ memory_tags)
- **memory_tags** = 변하지 않는 구조적 앵커 (드러난 사실: family, loss, regret …). drift 0.
- **summary** = 부드러운 **서사 흐름/뉘앙스** recap ("what this NPC remembers about the player"). drift 허용.

두 메커니즘은 상보적이며, 이 분담이 D1(rolling) 의 drift 약점을 무해화한다.

### D3. 턴-끝 동기 생성, 다음 턴부터 사용
요약은 `run_turn` **맨 끝**(exchange 영속화 후) post-step. 이유:
- "이후 매 턴 주입" = generate-at-end / use-next-turn 과 정확히 일치.
- **요약 콜이 실패해도 플레이어 턴은 이미 끝나 무영향** — 실패 시 기존 summary 유지, 조용히 넘어감 (내부 메모리라 플레이어 비노출, diegetic fallback 불필요).

→ **이 슬라이스의 핵심 안전 속성: 요약 실패가 대화를 절대 깨뜨리지 않는다.**

### D4. 요약 프롬프트는 `rules/summary.yaml` (새 파일)
NPC 프롬프트 빌드(`prompt_skeleton.yaml`) 와 책임이 다른 infra meta-prompt → 별도 파일. 코드 하드코딩 금지 원칙 일관. (NPC 대사가 아니므로 `check_no_hardcoded_dialogue.py` 대상 아님.)

## 트리거 / 카운팅 (Trigger semantics)

- 1 **exchange** = player input(1) + NPC reply(1). 현재 `chat_logs` 는 exchange 당 turn_index 2개(ti, ti+1) 기록.
- `count_exchanges` = 완료된 exchange 수 = `(MAX(turn_index)+1) / 2`.
- **trigger: exchange 영속화 직후 `count % 10 == 0`** → summarize.
- rolling delta `load_turns_since` = 직전 요약 이후의 exchanges (trigger 주기상 마지막 10 exchanges).
- 첫 요약(10턴): `prior = None` → 입력은 exchanges 1–10.

## 데이터 흐름 (Data Flow)

```
run_turn(...)
  ├─ Layer 1 / state load / build_prompt(..., summary=state.summary)  ← 주입 (신규)
  ├─ window = load_recent_turns(8)
  ├─ llm_call(system, messages) → Layer 4 → clamp → save_npc_state → _log_exchange
  └─ [POST-STEP, 신규] if count_exchanges % 10 == 0:
         prior = state.summary
         delta = load_turns_since(...)
         try: new = summarizer.summarize(prior, delta, llm_call=...)
              repo.save_summary(...)            # 성공 시에만 갱신
         except LLMError: pass                  # 기존 summary 유지, 턴은 이미 정상 반환
```

요약 생성은 `TurnResponse` 반환에 영향을 주지 않는다 (반환은 post-step 전에 확정).

## 컴포넌트 (Components — 단일 책임)

| 파일 | 책임 | 의존 |
|---|---|---|
| `rules/summary.yaml` (신규) | 요약 system 프롬프트 템플릿 (데이터) | — |
| `app/turn/summarizer.py` (신규) | `summarize(prior, exchanges, *, llm_call) -> str` | summary.yaml, llm_call(주입) |
| `app/store/repo.py` (수정) | `count_exchanges` / `load_turns_since` / `save_summary` | chat_logs, npc_state |
| `app/prompt_builder/renderer.py` (수정) | `build_prompt(..., summary)` 주입 | prompt_skeleton.yaml |
| `rules/prompt_skeleton.yaml` (수정) | summary 주입 슬롯 (memory_tags 인근) | — |
| `app/turn/loop.py` (수정) | summary 주입 + 턴-끝 trigger | summarizer, repo, renderer |

## 에러 처리 (Error Handling)

- 요약 LLM 콜 실패(`LLMError`) → 기존 `npc_state.summary` 유지, 턴은 정상 반환 (D3). 플레이어 비노출.
- `prior=None` (첫 요약) → 템플릿이 "신규 메모리 생성" 모드. summarizer 내부 분기.
- summary 미존재 시 `build_prompt` 는 summary 슬롯을 비워서 렌더 (기존 동작 불변 — Sub-2 회귀 없음).

## 테스트 전략 (Testing — ADR 0023/0029 패턴)

**결정적 게이트 (stub summarizer / stub llm_call):**
- trigger 정확성: 10/20 exchange 에만 호출, 9/11 엔 호출 안 됨.
- `npc_state.summary` 갱신 확인.
- `build_prompt` 가 summary 를 주입함 (렌더 문자열에 포함).
- **요약 콜 실패 시 기존 summary 유지 + 턴 정상 반환** (핵심 안전 속성).
- rolling 입력 구성: prior + delta exchanges 가 summarizer 에 전달됨.

**`pytest -m live` (실제 Gemma):**
- 요약 출력 비어있지 않음 + ≤300토큰 (verbatim 임계 X — 요약은 비결정적, 구조만 검증).

## 핵심 회귀 (이 슬라이스가 증명하는 단 하나)

10 exchange 를 진행한 세션의 11번째 턴에서, 시스템 프롬프트에 윈도우(마지막 8턴) **밖**의 과거를 담은 `summary` 가 주입된다. 그리고 요약 콜이 실패해도 그 턴은 정상 응답한다 — **긴 대화의 기억이 닫히되, 기억 생성 실패가 대화를 깨지 않는다.**

## Authority / Related

- `docs/mechanic-spec.md` "Context Window Management" (lines 185–195) — 권한.
- ADR 0023/0029 (결정적 게이트 + live off-gate), 0027 (로컬 Gemma), 0028 (forward-compat 스키마 — `npc_state.summary` 이미 존재).
- 신규 ADR 0032 (이 슬라이스 결정 기록).
