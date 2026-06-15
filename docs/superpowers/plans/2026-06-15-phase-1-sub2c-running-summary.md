# Phase 1.0 Sub-2c — Running Summary 슬라이스 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 수리공 `POST /turn` 에 running NPC memory summary 를 채운다 — 10 exchange 마다 rolling 요약(이전 summary + 직전 10 exchange)을 생성해 `npc_state.summary` 에 저장하고 이후 매 턴 시스템 프롬프트에 주입하되, 요약 실패가 대화를 절대 깨뜨리지 않는다.

**Architecture:** 8턴 verbatim 윈도우와 memory_tags injection 은 이미 구현됨 — 이 슬라이스는 비어 있던 세 번째 기둥(running summary)만 채운다. 요약은 `run_turn` 맨 끝 post-step 으로 돌려(턴 반환에 무영향), `count_exchanges % 10 == 0` 일 때만 동기 호출한다. 요약 프롬프트는 `rules/summary.yaml`(코드 하드코딩 금지), LLM 콜은 의존성 주입(gate=stub, prod=평문 completion).

**Tech Stack:** Python 3.11+, FastAPI, psycopg3 (sync), Postgres 16, pydantic v2, Jinja2, pytest, pyyaml, httpx, 로컬 llama-server(Gemma 4).

**Authority docs (audit trail 우선 — Task 1):** `docs/mechanic-spec.md` "Context Window Management" (lines 185–195), ADR 0023 (결정적 게이트 + live off-gate), 0027 (로컬 Gemma), 0028 (forward-compat 스키마 — `npc_state.summary` 이미 존재). 신규 ADR 0032.

**Design spec:** `docs/superpowers/specs/2026-06-15-phase-1-sub2c-running-summary-design.md`

**Prerequisite:** `docker compose up -d db` (Postgres). live 테스트만 llama-server 필요 (게이트는 stub).

---

## File Structure

| 파일 | 책임 |
|---|---|
| `docs/adr/0032-running-summary-rolling-defer-budget-cap.md` | rolling 전략 + 역할 분담 + 프롬프트 YAML + 동기 생성 + 4k cap defer 결정 기록 |
| `rules/summary.yaml` | 요약 system 프롬프트 + user 템플릿 (데이터, 튜닝 지점) |
| `app/turn/summarizer.py` | `SummaryRules` 스키마 + `load_summary_rules()` + `summarize(prior, exchanges, *, llm_call)` |
| `app/llm/client.py` (수정) | `summarize_call(system, user) -> str` 평문 completion (json_schema 없음) |
| `app/store/repo.py` (수정) | `count_exchanges` + `save_summary` |
| `app/prompt_builder/schemas.py` (수정) | `RuntimeState.summary` 필드 |
| `app/prompt_builder/renderer.py` (수정) | `build_prompt(..., summary=None)` |
| `rules/prompt_skeleton.yaml` (수정) | summary 주입 슬롯 (snapshot-safe: 전체 섹션을 `{% if summary %}` 안에) |
| `app/turn/loop.py` (수정) | summary 주입 + 턴-끝 trigger (`_maybe_summarize`) + `summarize_call` 주입 |
| `docs/mechanic-spec.md` / `docs/mapping-spec.md` (수정) | Sub-2c 갱신 노트 + 미매핑 라인 |
| `CLAUDE.md` (수정) | Sub-2c enforcement |
| `tests/turn/test_summarizer.py`, `tests/turn/test_summary.py`, `tests/live/test_summary_live.py` | 테스트 |

---

## Task 1: ADR 0032 + spec 갱신 (audit trail 우선)

**Files:**
- Create: `docs/adr/0032-running-summary-rolling-defer-budget-cap.md`
- Modify: `docs/mechanic-spec.md` ("Context Window Management" 섹션)
- Modify: `docs/mapping-spec.md` ("미매핑 항목" 리스트)

- [ ] **Step 1: ADR 0032 작성**

Create `docs/adr/0032-running-summary-rolling-defer-budget-cap.md`:

```markdown
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
```

- [ ] **Step 2: mechanic-spec Sub-2c 노트 추가**

`docs/mechanic-spec.md` 의 "## Context Window Management" 섹션에서 `**Summarization call model:**` 로 시작하는 bullet 을 찾고, 그 bullet 바로 아래에 추가:

```markdown

> **Sub-2c 갱신 (ADR 0032, 2026-06-15):** running summary 구현됨 — rolling 전략(이전 summary
> + 직전 10 exchange), 턴-끝 동기 생성, 실패 시 기존 summary 유지(대화 무영향). 요약 프롬프트는
> `rules/summary.yaml`. **4k budget cap(drop-oldest)은 defer** — 8턴 윈도우 + 상수 rolling
> summary + 200자 입력 cap 이 payload 를 실질 bound. 실측에서 4k 근접 시 후속 하드닝.
```

- [ ] **Step 3: mapping-spec 미매핑 라인 추가**

`docs/mapping-spec.md` 의 `## 미매핑 항목 (의도적)` 리스트에 1줄 추가:

```markdown
- Running summary 의 rolling 입력 전략 + 4k budget cap defer — 컨텍스트 관리 제작 결정 (ADR 0032)
```

- [ ] **Step 4: 검증 + commit**

Run: `python3 scripts/check_yaml.py`
Expected: 모든 yaml parse OK (이 task 는 yaml 변경 없음 — sanity).

```bash
git add docs/adr/0032-running-summary-rolling-defer-budget-cap.md docs/mechanic-spec.md docs/mapping-spec.md
git commit -m "ADR 0032 + spec 갱신 — running summary rolling 전략, 4k cap defer"
```

---

## Task 2: rules/summary.yaml + summarizer 스키마/로더/순수함수

**Files:**
- Create: `rules/summary.yaml`
- Create: `app/turn/summarizer.py`
- Test: `tests/turn/test_summarizer.py`

- [ ] **Step 1: rules/summary.yaml 작성**

Create `rules/summary.yaml`:

```yaml
# 요약 콜 프롬프트 — Context Window Management (running summary), ADR 0032.
# Authority: docs/mechanic-spec.md "Context Window Management". 튜닝은 코드 아닌 여기서.
system_prompt: |-
  너는 대화 기록을 압축하는 메모리 보조다. 아래는 한 NPC와 플레이어의 대화다.
  "이 NPC가 플레이어에 대해 기억하는 것"을 한국어 bullet 목록으로 요약하라.
  규칙:
  - 300 토큰 이내. 핵심 사실과 감정 흐름만.
  - 이전 요약이 있으면 거기에 새 대화를 통합해 갱신하라(중복 제거).
  - NPC 대사를 그대로 베끼지 말고 3인칭 사실로 적어라.
  - 출력은 bullet 목록만. 머리말/맺음말 금지.
user_template: |-
  [이전 요약]
  {prior}

  [새 대화]
  {conversation}
```

- [ ] **Step 2: 실패 테스트 작성**

Create `tests/turn/test_summarizer.py`:

```python
from app.turn.summarizer import load_summary_rules, summarize


def test_summary_rules_load_and_validate():
    rules = load_summary_rules()
    assert "{prior}" in rules.user_template
    assert "{conversation}" in rules.user_template
    assert rules.system_prompt.strip()


def test_summarize_passes_prior_and_conversation_to_llm():
    captured = {}

    def stub(system, user):
        captured["system"] = system
        captured["user"] = user
        return "- 요약 결과"

    out = summarize(
        "이전 기억",
        [{"role": "user", "content": "안녕"}, {"role": "assistant", "content": "어"}],
        llm_call=stub,
    )
    assert out == "- 요약 결과"
    assert "이전 기억" in captured["user"]
    assert "안녕" in captured["user"] and "어" in captured["user"]
    assert captured["system"] == load_summary_rules().system_prompt


def test_summarize_first_time_marks_no_prior():
    captured = {}

    def stub(system, user):
        captured["user"] = user
        return "x"

    summarize(None, [{"role": "user", "content": "hi"}], llm_call=stub)
    assert "첫 요약" in captured["user"]
```

- [ ] **Step 3: 실패 확인**

Run: `.venv/bin/pytest tests/turn/test_summarizer.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'app.turn.summarizer'`.

- [ ] **Step 4: summarizer.py 구현**

Create `app/turn/summarizer.py`:

```python
"""Running summary 생성 — 10 exchange 마다 (ADR 0032).

summarize: 이전 summary + 직전 exchanges → rolling 갱신 요약 (≤300토큰 목표).
llm_call 은 의존성 주입 (gate=stub, prod=app.llm.client.summarize_call).
요약 프롬프트는 rules/summary.yaml — 코드 하드코딩 금지.
"""

from functools import lru_cache
from pathlib import Path

import yaml
from pydantic import BaseModel, ConfigDict

RULES_DIR = Path(__file__).resolve().parents[2] / "rules"


class SummaryRules(BaseModel):
    model_config = ConfigDict(extra="forbid")
    system_prompt: str
    user_template: str


@lru_cache(maxsize=1)
def load_summary_rules() -> SummaryRules:
    raw = yaml.safe_load((RULES_DIR / "summary.yaml").read_text())
    return SummaryRules.model_validate(raw)


def summarize(prior: str | None, exchanges: list[dict], *, llm_call) -> str:
    """이전 summary + exchanges → 갱신 요약 (rolling). llm_call(system, user) -> str."""
    rules = load_summary_rules()
    prior_block = prior if prior else "(아직 없음 — 첫 요약)"
    conversation = "\n".join(f"{e['role']}: {e['content']}" for e in exchanges)
    user = rules.user_template.format(prior=prior_block, conversation=conversation)
    return llm_call(rules.system_prompt, user)
```

- [ ] **Step 5: 통과 확인 + yaml 검증**

Run: `.venv/bin/pytest tests/turn/test_summarizer.py -v && python3 scripts/check_yaml.py`
Expected: PASS (3 tests) + summary.yaml parse OK.

- [ ] **Step 6: Commit**

```bash
git add rules/summary.yaml app/turn/summarizer.py tests/turn/test_summarizer.py
git commit -m "Running summary 순수함수 — summary.yaml + SummaryRules + summarize (ADR 0032)"
```

---

## Task 3: 평문 completion 콜 (`summarize_call`)

**Files:**
- Modify: `app/llm/client.py`

- [ ] **Step 1: summarize_call 추가**

`app/llm/client.py` 파일 끝에 추가:

```python
def summarize_call(system: str, user: str) -> str:
    """평문 completion (json_schema 없음) — running summary 용. 실패 = LLMError.

    dialogue 와 동일 tier/서버 (ADR 0027/0032). ADR 0029: thinking 비활성화.
    """
    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        "temperature": 0.3,  # 요약은 낮은 변동
        "max_tokens": 400,   # ≤300토큰 목표 + 여유
        "chat_template_kwargs": {"enable_thinking": False},
    }
    try:
        resp = httpx.post(f"{LLAMA_SERVER_URL}/v1/chat/completions", json=payload, timeout=120)
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"]
    except Exception as e:
        raise LLMError(str(e)) from e
```

- [ ] **Step 2: import 회귀 확인 (게이트는 이 함수를 stub 으로 대체하므로 호출 안 함)**

Run: `.venv/bin/python -c "from app.llm.client import summarize_call; print('ok')"`
Expected: `ok` (import 가능, 시그니처 유효).

- [ ] **Step 3: Commit**

```bash
git add app/llm/client.py
git commit -m "summarize_call — 평문 completion 콜 (running summary 용, ADR 0027/0029)"
```

---

## Task 4: repo — count_exchanges + save_summary

**Files:**
- Modify: `app/store/repo.py`
- Test: `tests/store/test_summary_repo.py`

- [ ] **Step 1: 실패 테스트 작성**

Create `tests/store/test_summary_repo.py`:

```python
import uuid

from app.store import repo


def test_count_exchanges_counts_pairs(conn):
    sid = str(uuid.uuid4())
    assert repo.count_exchanges(conn, sid, "surigong") == 0
    # 1 exchange = user(turn 0) + assistant(turn 1)
    repo.append_chat_log(conn, sid, "surigong", 0, "user", "a")
    repo.append_chat_log(conn, sid, "surigong", 1, "assistant", "b")
    assert repo.count_exchanges(conn, sid, "surigong") == 1
    repo.append_chat_log(conn, sid, "surigong", 2, "user", "c")
    repo.append_chat_log(conn, sid, "surigong", 3, "assistant", "d")
    assert repo.count_exchanges(conn, sid, "surigong") == 2


def test_save_summary_updates_npc_state(conn):
    sid = str(uuid.uuid4())
    repo.save_npc_state(conn, sid, "surigong", 10, [])  # 행 생성
    repo.save_summary(conn, sid, "surigong", "- 플레이어는 보트를 물었다")
    state = repo.load_npc_state(conn, sid, "surigong")
    assert state.summary == "- 플레이어는 보트를 물었다"
    assert state.awareness == 10  # 다른 필드 불변
```

- [ ] **Step 2: 실패 확인**

Run: `.venv/bin/pytest tests/store/test_summary_repo.py -v`
Expected: FAIL — `AttributeError: module 'app.store.repo' has no attribute 'count_exchanges'`.

- [ ] **Step 3: repo.py 에 함수 추가**

`app/store/repo.py` 파일 끝에 추가:

```python
def count_exchanges(conn, session_uuid: str, npc_id: str) -> int:
    """완료된 exchange 수. 1 exchange = user+assistant 2행 → (MAX(turn_index)+1)//2."""
    row = conn.execute(
        "SELECT (COALESCE(MAX(turn_index), -1) + 1) / 2 FROM chat_logs "
        "WHERE session_uuid = %s AND npc_id = %s",
        (session_uuid, npc_id),
    ).fetchone()
    return int(row[0])


def save_summary(conn, session_uuid: str, npc_id: str, summary: str) -> None:
    """npc_state.summary 갱신 (행은 save_npc_state 후 존재 가정)."""
    conn.execute(
        "UPDATE npc_state SET summary = %s, updated_at = now() "
        "WHERE session_uuid = %s AND npc_id = %s",
        (summary, session_uuid, npc_id),
    )
```

- [ ] **Step 4: 통과 확인**

Run: `.venv/bin/pytest tests/store/ -v`
Expected: PASS (기존 store 테스트 + 신규 2).

- [ ] **Step 5: Commit**

```bash
git add app/store/repo.py tests/store/test_summary_repo.py
git commit -m "repo — count_exchanges + save_summary (ADR 0032)"
```

---

## Task 5: build_prompt summary 주입 (snapshot-safe)

**Files:**
- Modify: `app/prompt_builder/schemas.py:172-179` (`RuntimeState`)
- Modify: `app/prompt_builder/renderer.py:38-106` (`build_prompt`)
- Modify: `rules/prompt_skeleton.yaml` (template)
- Test: `tests/prompt_builder/test_summary_injection.py`

핵심 불변식: `summary=None` 일 때 렌더 출력이 **기존과 100% 동일** (Sub-1 4-cell oracle / 16-cell property 회귀 없음). 따라서 summary 섹션 전체를 `{% if summary %}` 안에 둔다.

- [ ] **Step 1: 실패 테스트 작성**

Create `tests/prompt_builder/test_summary_injection.py`:

```python
from app.prompt_builder.renderer import build_prompt
from app.turn.loop import RUBY_HOOK_STUB


def test_summary_none_renders_unchanged():
    # summary 미전달 == summary=None == 기존 출력
    assert build_prompt("surigong", 10, [], RUBY_HOOK_STUB) == build_prompt(
        "surigong", 10, [], RUBY_HOOK_STUB, summary=None
    )


def test_summary_present_is_injected():
    out = build_prompt("surigong", 10, [], RUBY_HOOK_STUB, summary="- 플레이어는 떠남을 물었다")
    assert "- 플레이어는 떠남을 물었다" in out
    assert "기억 요약" in out


def test_summary_present_adds_lines_over_none():
    none_out = build_prompt("surigong", 10, [], RUBY_HOOK_STUB, summary=None)
    sum_out = build_prompt("surigong", 10, [], RUBY_HOOK_STUB, summary="- x")
    assert len(sum_out) > len(none_out)
```

- [ ] **Step 2: 실패 확인**

Run: `.venv/bin/pytest tests/prompt_builder/test_summary_injection.py -v`
Expected: FAIL — `build_prompt() got an unexpected keyword argument 'summary'`.

- [ ] **Step 3: RuntimeState 에 summary 필드 추가**

`app/prompt_builder/schemas.py` 의 `RuntimeState` (172-179행) 에 `summary` 필드 추가 — `memory_tags` 줄 아래:

```python
class RuntimeState(BaseModel):
    model_config = ConfigDict(extra="forbid")
    npc_name: Literal["surigong", "eobu", "halmoni", "hyean"]
    # strict=True → bool/float/str coercion 거부. awareness 는 진짜 int 여야 함
    # (bool True 가 1 로 조용히 통과하던 gap 차단, code-review followup).
    awareness: int = Field(strict=True, ge=0, le=100)
    memory_tags: list[str]
    summary: Optional[str] = None
    hooks_runtime: dict = Field(default_factory=dict)
```

(`Optional` 은 schemas.py 에 이미 import 됨 — 67행 등에서 사용 중.)

- [ ] **Step 4: build_prompt 에 summary 인자 추가**

`app/prompt_builder/renderer.py` 의 `build_prompt` 시그니처 + RuntimeState 생성 + render 호출 수정:

시그니처 (38-43행) 를 교체:

```python
def build_prompt(
    npc_name: str,
    awareness: int,
    memory_tags: list[str],
    hooks_runtime: dict | None = None,
    summary: str | None = None,
) -> str:
```

RuntimeState 생성 (49-58행) 을 교체:

```python
    state = RuntimeState(
        npc_name=npc_name,
        awareness=awareness,
        memory_tags=memory_tags,
        summary=summary,
        hooks_runtime=hooks_runtime or {},
    )
    npc_name = state.npc_name
    awareness = state.awareness
    memory_tags = state.memory_tags
    summary = state.summary
    hooks_runtime = state.hooks_runtime
```

`template.render(...)` 호출 (98-106행) 에 `summary=summary` 추가:

```python
    return template.render(
        npc=npc,
        rules=rules,
        band=band,
        band_npc=band_npc,
        awareness=awareness,
        memory_tags=memory_tags,
        summary=summary,
        hooks_runtime=hooks_runtime,
    )
```

- [ ] **Step 5: skeleton 에 summary 슬롯 추가 (snapshot-safe)**

`rules/prompt_skeleton.yaml` 의 `[Memory tags 누적]` 블록 끝(`{% endif %}`, 20행) 과 `[awakening_guidelines]`(22행) 사이에 삽입. **전체 섹션을 `{% if summary %}` 안에** 둬서 None 이면 0줄 렌더:

```
  {% if summary %}
  [NPC 기억 요약]
  {{ summary }}
  {% endif %}
```

삽입 후 해당 구간이 다음과 같아야 함:

```
  [Memory tags 누적]
  {% if memory_tags %}
  [{{ memory_tags | join(", ") }}]
  {% else %}
  (none)
  {% endif %}
  {% if summary %}
  [NPC 기억 요약]
  {{ summary }}
  {% endif %}

  [awakening_guidelines]
```

- [ ] **Step 6: 통과 확인 + Sub-1 oracle 회귀 확인**

Run: `.venv/bin/pytest tests/prompt_builder/ -v`
Expected: PASS — 신규 3 + 기존 oracle/property 테스트 전부 green (summary=None 이 출력 불변).

- [ ] **Step 7: yaml 검증 + Commit**

Run: `python3 scripts/check_yaml.py`
Expected: parse OK.

```bash
git add app/prompt_builder/schemas.py app/prompt_builder/renderer.py rules/prompt_skeleton.yaml tests/prompt_builder/test_summary_injection.py
git commit -m "build_prompt summary 주입 — snapshot-safe (summary=None 시 출력 불변, ADR 0032)"
```

---

## Task 6: loop 와이어링 — summary 주입 + 턴-끝 trigger

**Files:**
- Modify: `app/turn/loop.py`
- Test: `tests/turn/test_summary.py`

- [ ] **Step 1: 실패 테스트 작성**

Create `tests/turn/test_summary.py`:

```python
import uuid

from app.llm.client import LLMError
from app.models import Choice, TurnReply
from app.store import repo
from app.turn.loop import run_turn


def _reply():
    return TurnReply(
        reply="망치질은 멈추지 않아.", awareness_delta=1, reason="r", memory_tags=[],
        choices=[Choice(tone="empathetic", text="a"), Choice(tone="provocative", text="b"),
                 Choice(tone="deflecting", text="c")],
    )


def _llm(system, messages):
    return _reply()


def _drive(conn, sid, n, summarize_call):
    for i in range(n):
        run_turn(conn, sid, "surigong", f"입력 {i}", llm_call=_llm, summarize_call=summarize_call)


def test_summary_triggers_on_10th_exchange(conn):
    sid = str(uuid.uuid4())
    calls = []

    def stub(system, user):
        calls.append(user)
        return "- 플레이어는 보트에 관심이 있다"

    _drive(conn, sid, 10, stub)
    assert len(calls) == 1
    assert repo.load_npc_state(conn, sid, "surigong").summary == "- 플레이어는 보트에 관심이 있다"


def test_no_summary_before_10th(conn):
    sid = str(uuid.uuid4())

    def stub(system, user):
        raise AssertionError("10 exchange 전엔 요약 안 함")

    _drive(conn, sid, 9, stub)
    assert repo.load_npc_state(conn, sid, "surigong").summary is None


def test_summary_injected_into_next_prompt(conn):
    sid = str(uuid.uuid4())

    def stub(system, user):
        return "- 기억된 사실"

    _drive(conn, sid, 10, stub)

    captured = {}

    def capturing(system, messages):
        captured["system"] = system
        return _reply()

    run_turn(conn, sid, "surigong", "다음", llm_call=capturing, summarize_call=stub)
    assert "- 기억된 사실" in captured["system"]


def test_summary_failure_keeps_old_and_turn_succeeds(conn):
    sid = str(uuid.uuid4())

    def failing(system, user):
        raise LLMError("summary timeout")

    resp = None
    for i in range(10):
        resp = run_turn(conn, sid, "surigong", f"x{i}", llm_call=_llm, summarize_call=failing)
    assert resp.reply  # 턴 정상 반환
    assert repo.load_npc_state(conn, sid, "surigong").summary is None  # 갱신 안 됨


def test_rolling_passes_prior_summary_on_20th(conn):
    sid = str(uuid.uuid4())
    seen = []

    def stub(system, user):
        seen.append(user)
        return f"summary-{len(seen)}"

    _drive(conn, sid, 20, stub)
    assert len(seen) == 2
    # 2번째 요약 입력에 1번째 요약(prior)이 통합됨 (rolling)
    assert "summary-1" in seen[1]
```

- [ ] **Step 2: 실패 확인**

Run: `.venv/bin/pytest tests/turn/test_summary.py -v`
Expected: FAIL — `run_turn() got an unexpected keyword argument 'summarize_call'`.

- [ ] **Step 3: loop.py 수정**

`app/turn/loop.py` 상단 import 에 summarizer 추가 (`from app.store import repo` 줄 아래):

```python
from app.turn import summarizer
```

`RUBY_HOOK_STUB` 정의 아래에 상수 + 헬퍼 추가:

```python
SUMMARIZE_EVERY = 10  # exchanges (mechanic-spec "Context Window Management")


def _maybe_summarize(conn, sid, npc_id, prior_summary, summarize_call) -> None:
    """10 exchange 마다 rolling 요약. 실패해도 turn 무영향 (기존 summary 유지). ADR 0032."""
    if repo.count_exchanges(conn, sid, npc_id) % SUMMARIZE_EVERY != 0:
        return
    delta = repo.load_recent_turns(conn, sid, npc_id, limit=SUMMARIZE_EVERY * 2)
    try:
        new_summary = summarizer.summarize(prior_summary, delta, llm_call=summarize_call)
    except llm_client.LLMError:
        return  # 기존 summary 유지 — 대화 무영향
    repo.save_summary(conn, sid, npc_id, new_summary)
```

`run_turn` 시그니처를 교체 (`summarize_call` 주입 추가):

```python
def run_turn(conn, session_uuid: str, npc_id: str, player_input: str, *, llm_call=None, summarize_call=None) -> TurnResponse:
    if llm_call is None:
        llm_call = llm_client.call
    if summarize_call is None:
        summarize_call = llm_client.summarize_call
```

`build_prompt(...)` 호출 (현 51행) 에 `summary=state.summary` 추가:

```python
    system = build_prompt(npc_id, state.awareness, state.memory_tags, RUBY_HOOK_STUB, summary=state.summary)
```

happy-path 끝 (`_log_exchange(...)` 호출 직후, `return TurnResponse(...)` 바로 위) 에 post-step 추가:

```python
    repo.save_npc_state(conn, session_uuid, npc_id, new_awareness, new_tags)
    _log_exchange(conn, session_uuid, npc_id, player_input, reply.reply, reply.model_dump())
    _maybe_summarize(conn, session_uuid, npc_id, state.summary, summarize_call)

    return TurnResponse(reply=reply.reply, choices=reply.choices, session_uuid=session_uuid)
```

(주의: `_maybe_summarize` 는 **happy path 에만** 호출. Layer1/LLMError/Layer4 분기는 그 전에 return 하므로 요약 안 함 — 의도된 동작.)

- [ ] **Step 4: 통과 확인 + 기존 loop 회귀 확인**

Run: `.venv/bin/pytest tests/turn/ -v`
Expected: PASS — 신규 5 + 기존 test_loop.py 전부 green.

(기존 `test_loop.py` 는 `summarize_call` 미전달 → 기본값 `llm_client.summarize_call`. 단 이 테스트들은 1턴만 돌려 `count_exchanges`=1 → trigger 안 됨 → summarize_call 호출 안 됨 → 실서버 접속 없음.)

- [ ] **Step 5: Commit**

```bash
git add app/turn/loop.py tests/turn/test_summary.py
git commit -m "loop 와이어링 — summary 주입 + 턴-끝 rolling 요약 trigger (ADR 0032)"
```

---

## Task 7: live 테스트 (off-gate, 실제 Gemma)

**Files:**
- Test: `tests/live/test_summary_live.py`

- [ ] **Step 1: live 테스트 작성**

Create `tests/live/test_summary_live.py`:

```python
"""Off-gate live — 실제 llama-server (Gemma 4). `pytest -m live` 로만 실행.

ADR 0032: running summary 가 비어있지 않고 대략 ≤300토큰. 요약은 비결정적이라
verbatim 임계가 아니라 구조(비어있지 않음 + 상한)만 검증.
"""

import httpx
import pytest

from app.config import LLAMA_SERVER_URL
from app.llm.client import summarize_call
from app.turn.summarizer import summarize


def _server_up() -> bool:
    try:
        return httpx.get(f"{LLAMA_SERVER_URL}/health", timeout=2).status_code == 200
    except Exception:
        return False


@pytest.mark.live
def test_summary_real_call_nonempty_and_bounded():
    if not _server_up():
        pytest.skip("llama-server 미기동 — live 스킵")
    exchanges = [
        {"role": "user", "content": "보트는 언제 다 고쳐져?"},
        {"role": "assistant", "content": "글쎄, 끝이 보이질 않아."},
        {"role": "user", "content": "넌 원래 누구였어?"},
        {"role": "assistant", "content": "...그건 잘 기억나지 않는군."},
    ]
    out = summarize(None, exchanges, llm_call=summarize_call)
    assert out.strip()  # 비어있지 않음
    # ≤300토큰 목표의 느슨한 프록시 (한국어 대략, 안전하게 2000자 상한)
    assert len(out) < 2000
```

- [ ] **Step 2: 게이트에서 제외됨 확인 (수집되지만 실행 skip)**

Run: `.venv/bin/pytest tests/live/test_summary_live.py -v`
Expected: deselected (pyproject `addopts = -m 'not live'`) — 0 실행, 에러 없음.

- [ ] **Step 3: (llama-server 기동 시, 선택) live 실행**

Run: `.venv/bin/pytest -m live tests/live/test_summary_live.py -v`
Expected: PASS (서버 기동 시) 또는 skip (미기동 시).

- [ ] **Step 4: Commit**

```bash
git add tests/live/test_summary_live.py
git commit -m "live 테스트 — running summary 실제 Gemma 콜 비어있지 않음 + 상한 (ADR 0032)"
```

---

## Task 8: CLAUDE.md enforcement + 최종 gate

**Files:**
- Modify: `CLAUDE.md` (Enforcement 섹션)

- [ ] **Step 1: CLAUDE.md 에 Sub-2c 블록 추가**

`CLAUDE.md` 의 `**Phase 1.0 Sub-2b (현재 ...):**` 블록과 `**Phase 1.0 Sub-2b+ (추후):**` 블록 사이에 삽입:

```markdown
**Phase 1.0 Sub-2c (현재 — running summary 도입됨):**
- `app/turn/summarizer` + `rules/summary.yaml` — 10 exchange 마다 rolling 요약(이전 summary + 직전 10 exchange) → `npc_state.summary`, 이후 매 턴 프롬프트 주입. 컨텍스트 윈도우 3요소(8턴 verbatim + memory_tags + summary) 완성.
- 요약은 `run_turn` 턴-끝 동기 post-step — **실패해도 대화 무영향**(기존 summary 유지). 요약 프롬프트는 `rules/summary.yaml`(튜닝은 YAML).
- 4k budget cap(drop-oldest)은 defer (ADR 0032). 게이트=결정적(summarize_call stub), off-gate=`pytest -m live`.

```

그리고 기존 `**Phase 1.0 Sub-2b+ (추후):**` 블록의 내용에서 "running summary" 항목을 제거 (이제 구현됨):

```markdown
**Phase 1.0 Sub-2b+ (추후):**
- ML 모더레이션 checker, save-code/쿠키, Cloudflare/failover, 4k budget cap 하드닝, 나머지 3 NPC, FastAPI 프론트엔드/모바일.
```

- [ ] **Step 2: 전체 gate 최종 확인**

Run: `.venv/bin/pytest -q && python3 scripts/check_yaml.py && .venv/bin/python scripts/check_no_hardcoded_dialogue.py && echo OK`
Expected: 전부 green + `OK`.

- [ ] **Step 3: Commit**

```bash
git add CLAUDE.md
git commit -m "CLAUDE.md — Phase 1.0 Sub-2c running summary enforcement 활성화"
```

---

## 실행 후 검증 (Definition of Done)

- [ ] `docker compose up -d db` 후 `.venv/bin/pytest` green (Sub-1/2/2b/2c gate, live 제외).
- [ ] `python3 scripts/check_yaml.py` green (summary.yaml 포함).
- [ ] `.venv/bin/python scripts/check_no_hardcoded_dialogue.py` exit 0.
- [ ] Sub-1 oracle/property 테스트 회귀 없음 (summary=None 시 build_prompt 출력 불변).
- [ ] (선택, llama-server 기동 시) `.venv/bin/pytest -m live tests/live/test_summary_live.py` PASS.
- [ ] ADR 0032 + mechanic-spec/mapping-spec cross-link 작동.

## 핵심 회귀 (이 슬라이스가 증명하는 단 하나)

`tests/turn/test_summary.py::test_summary_injected_into_next_prompt` — 10 exchange 후 11번째 턴의
시스템 프롬프트에 윈도우 밖 과거를 담은 summary 가 주입된다. 그리고
`test_summary_failure_keeps_old_and_turn_succeeds` — 요약 콜이 실패해도 그 턴은 정상 응답하고
기존 summary 를 유지한다. **긴 대화의 기억이 닫히되, 기억 생성 실패가 대화를 깨지 않는다.**
