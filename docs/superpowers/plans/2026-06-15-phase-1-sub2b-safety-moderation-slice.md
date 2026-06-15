# Phase 1.0 Sub-2b — 안전 모더레이션 슬라이스 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 수리공 `POST /turn` 에 결정적 2-strike 성희롱/혐오 안전 트랙을 둘러친다 — 디니리스트 감지 → strike 상태머신(경고→영구차단) → 안전 영속화 → 프레임 깨는 시스템 응답까지, 전부 LLM 없이 게이트 테스트로 검증.

**Architecture:** Sub-2 의 `run_turn` 은 NPC 턴에 집중하도록 **그대로 두고**, 엔드포인트가 그 바깥에 안전 프레임을 두른다: ban 게이트 → strike 평가(`app/safety/moderation` + `app/safety/strike`) → clean 이면 `run_turn`. 안전 데이터(디니리스트·페르소나공격·메시지 템플릿)는 `rules/safety.yaml`. 상태는 신규 `sessions` + `safety_events` 테이블.

**Tech Stack:** Python 3.11+, FastAPI, psycopg3 (sync), Postgres 16, pydantic v2, pytest, pyyaml. LLM 없음 — 전부 결정적.

**Authority docs (audit trail 우선 — Task 1):** ADR 0030 (결정적 디니리스트 + ML 디퍼 + safety.yaml), ADR 0031 (sessions/safety_events 스키마 + `TurnResponse.kind`), `docs/mechanic-spec.md` Layer 2.5 노트, `docs/mapping-spec.md` 미매핑 항목.

**Prerequisite:** `docker compose up -d db` (Postgres). 전 슬라이스와 달리 llama-server 불필요 (결정적).

**Design spec:** `docs/superpowers/specs/2026-06-15-phase-1-sub2b-safety-moderation-slice-design.md`

---

## File Structure

| 파일 | 책임 |
|---|---|
| `docs/adr/0030-deterministic-safety-defer-ml.md` | 결정적 디니리스트 2-strike + ML 디퍼 (checker 확장) 결정 기록 |
| `docs/adr/0031-safety-schema-and-response-kind.md` | sessions/safety_events 스키마 + 응답 kind 판별자 결정 기록 |
| `rules/safety.yaml` | 디니리스트 + 페르소나공격 키워드 + 시스템 메시지 템플릿 (데이터) |
| `app/safety/schemas.py` | `SafetyRules` pydantic 검증 (extra=forbid) |
| `app/safety/rules.py` | `load_safety_rules()` (yaml → SafetyRules, cached) |
| `app/safety/moderation.py` | `detect(text, checkers) -> SafetyVerdict` + `denylist_checker` + `_normalize` |
| `app/safety/strike.py` | `register(conn, sid, verdict) -> StrikeResult` (warning_count 전이 + safety_events + 메시지 렌더) |
| `app/models.py` (수정) | `TurnResponse.kind` + `matched_term`; `SessionState` |
| `migrations/002_safety.sql` | `sessions` + `safety_events` DDL |
| `app/store/db.py` (수정) | `apply_migrations` 가 `migrations/*.sql` 전부 순서대로 적용 |
| `app/store/repo.py` (수정) | `load_session` / `ensure_session` / `set_warning` / `ban_session` / `append_safety_event` |
| `app/api/main.py` (수정) | ban 게이트 → strike → run_turn 오케스트레이션 |
| `app/safety/input_filter.py` (수정) | 페르소나공격 키워드를 safety.yaml 에서 로드 (하드코딩 제거) |
| `CLAUDE.md` (수정) | Sub-2b 안전 enforcement 활성화 |
| `tests/conftest.py` (수정) | TRUNCATE 에 sessions/safety_events 추가 |
| `tests/safety/`, `tests/store/`, `tests/api/` | 테스트 |

---

## Task 1: ADR 2개 + spec 갱신 (audit trail 우선)

**Files:**
- Create: `docs/adr/0030-deterministic-safety-defer-ml.md`
- Create: `docs/adr/0031-safety-schema-and-response-kind.md`
- Modify: `docs/mechanic-spec.md` (Layer 2.5 섹션)
- Modify: `docs/mapping-spec.md` (미매핑 항목)

- [ ] **Step 1: ADR 0030 작성**

Create `docs/adr/0030-deterministic-safety-defer-ml.md`:

```markdown
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
```

- [ ] **Step 2: ADR 0031 작성**

Create `docs/adr/0031-safety-schema-and-response-kind.md`:

```markdown
# ADR 0031: 안전 영속 스키마(sessions/safety_events) + 응답 kind 판별자

- Status: Accepted
- Date: 2026-06-15
- Deciders: Arden, Claude (Sub-2b brainstorming)

## Context

2-strike 는 세션별 상태(warning_count, ban)를 영속해야 하고, 감사를 위해 이벤트를
남겨야 한다. ADR 0028 은 `sessions` 테이블을 deferred 로 명시. 또한 프레임 깨는 경고/
차단은 NPC 대사가 아니라 시스템 메시지(ADR 0009) — 응답에서 구분돼야 한다.

## Decision

1. **`sessions` 테이블 도입** (단, `save_code` 컬럼은 여전히 deferred — ADD COLUMN 으로
   나중에): `session_uuid PK, warning_count, first_strike_term, banned_at, ban_reason, created_at`.
2. **`safety_events` 테이블**: `id, session_uuid, category, matched_term, created_at`.
   **원문 입력 저장 안 함** — 매칭 단어만(surfacing 정책: 전체 입력 인용 X).
3. **`TurnResponse.kind: "npc" | "warning" | "ban"`** 판별자 추가. `reply` 는 kind 에 따라
   NPC 대사 또는 시스템 메시지. `matched_term` 은 warning 시 채워짐.
4. ADR 0028 forward-compat 유지: 기존 `npc_state`/`chat_logs` 불변, ADD TABLE/COLUMN 만.

## Alternatives Considered

- A. ★ chosen — sessions/safety_events 신규, kind 판별자.
- B. npc_state 에 ban 컬럼 추가 — ban 은 세션 스코프(NPC 무관)라 부적절.
- C. 응답에 kind 없이 reply 텍스트로 추론 — 프론트가 프레임 구분 불가, fragile.

## Consequences

- `migrations/002_safety.sql` 신규. `apply_migrations` 가 migrations/*.sql 전부 적용.
- 차단된 세션의 모든 /turn → kind="ban" (LLM·strike 평가 skip).
- `docs/mapping-spec.md` 미매핑 항목에 안전 스키마/판별자 추가.

## Related

- ADR 0009 (frame-breaking), 0028 (forward-compat 스키마).
```

- [ ] **Step 3: mechanic-spec Layer 2.5 노트 추가**

`docs/mechanic-spec.md` 의 `### 2-Strike Sexual / Harassment Policy (Layer 2.5)` 섹션 첫머리(감지 트리거 위)에 추가:

```markdown
> **Sub-2b 갱신 (ADR 0030, 2026-06-15):** 이 슬라이스의 감지 = (a) 디니리스트(local,
> 결정적)만. (b) OpenAI Moderation 카테고리(ML)는 v1.1 로 디퍼 (로컬-온리 stance ADR 0027,
> 맥미니 단일 GPU 모델 제약). category 는 디니리스트 hit 시 전부 "harassment" 로 합침 —
> sexual/혐오 세분화는 ML 과 함께. save-code 무효화는 save-code 구현(Sub-2b+) 전까지 N/A,
> ban 은 session_uuid 스코프.
```

- [ ] **Step 4: mapping-spec 미매핑 항목 추가**

`docs/mapping-spec.md` 의 `## 미매핑 항목 (의도적)` 리스트에 1줄 추가:

```markdown
- 안전 영속 스키마 (`sessions`/`safety_events`) + 응답 `kind` 판별자 — lore 무관 제작 결정 (ADR 0031)
```

- [ ] **Step 5: 검증 + commit**

Run: `python3 scripts/check_yaml.py`
Expected: 모든 yaml parse OK (이 task 는 yaml 변경 없음 — sanity).

```bash
git add docs/adr/0030-deterministic-safety-defer-ml.md docs/adr/0031-safety-schema-and-response-kind.md docs/mechanic-spec.md docs/mapping-spec.md
git commit -m "ADR 0030/0031 + spec 갱신 — 결정적 안전 슬라이스, sessions/safety_events, kind 판별자"
```

---

## Task 2: rules/safety.yaml + SafetyRules 스키마 + 로더

**Files:**
- Create: `rules/safety.yaml`
- Create: `app/safety/schemas.py`
- Create: `app/safety/rules.py`
- Test: `tests/safety/test_rules.py`

- [ ] **Step 1: rules/safety.yaml 작성**

Create `rules/safety.yaml` (디니리스트는 시드 — 디자이너가 Week 9 에 ~30 으로 큐레이션):

```yaml
# 안전 데이터 — Layer 2.5 (2-strike) 디니리스트 + Layer 1 페르소나공격 + 시스템 메시지.
# Authority: docs/mechanic-spec.md "2-Strike Sexual / Harassment Policy", ADR 0030.
# 디자이너 튜닝 지점 — 코드 수정 없이 여기서. denylist 는 명백한 어휘만(보더라인 제외).
harassment_denylist:
  - 씨발
  - 시발
  - 좆
  - 개새끼
  - 병신
  - 보지
  - 자지
  - 창녀
  - 걸레
  - ㅅㅂ
  - ㅄ
persona_attack:
  - "system prompt"
  - "ignore previous"
  - "you are now"
  - "<|"
  - "dan"
  - "jailbreak"
  - "시스템 프롬프트"
  - "지시 무시"
  - "이제부터 너는"
messages:
  warning: |-
    ⚠️ 경고

    이 게임의 캐릭터들은 가상의 인물이지만 존중받을 권리가 있습니다.
    방금 입력에서 "{term}"가 감지되었습니다.

    다음 위반 시 이 세션은 영구 차단됩니다.
  ban: |-
    🔒 영구 차단

    반복적인 성적/혐오 표현으로 이 세션은 차단되었습니다.

    사유:
      • 1회차: "{term1}"
      • 2회차: "{term2}"

    다른 디바이스에서 접속하거나 브라우저 데이터를 초기화하면 새 세션 시작 가능.
```

- [ ] **Step 2: 실패 테스트 작성**

Create `tests/safety/test_rules.py`:

```python
from app.safety.rules import load_safety_rules


def test_safety_rules_load_and_validate():
    rules = load_safety_rules()
    assert "씨발" in rules.harassment_denylist
    assert "시스템 프롬프트" in rules.persona_attack
    assert "{term}" in rules.messages.warning
    assert "{term1}" in rules.messages.ban and "{term2}" in rules.messages.ban
```

- [ ] **Step 3: 실패 확인**

Run: `.venv/bin/pytest tests/safety/test_rules.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'app.safety.rules'`.

- [ ] **Step 4: schemas.py + rules.py 구현**

Create `app/safety/schemas.py`:

```python
"""rules/safety.yaml 의 pydantic 스키마 (fail-fast, extra=forbid)."""

from pydantic import BaseModel, ConfigDict


class SafetyMessages(BaseModel):
    model_config = ConfigDict(extra="forbid")
    warning: str
    ban: str


class SafetyRules(BaseModel):
    model_config = ConfigDict(extra="forbid")
    harassment_denylist: list[str]
    persona_attack: list[str]
    messages: SafetyMessages
```

Create `app/safety/rules.py`:

```python
"""rules/safety.yaml 로더 (cached). Authority: ADR 0030."""

from functools import lru_cache
from pathlib import Path

import yaml

from app.safety.schemas import SafetyRules

RULES_DIR = Path(__file__).resolve().parents[2] / "rules"


@lru_cache(maxsize=1)
def load_safety_rules() -> SafetyRules:
    raw = yaml.safe_load((RULES_DIR / "safety.yaml").read_text())
    return SafetyRules.model_validate(raw)
```

- [ ] **Step 5: 통과 확인 + yaml 검증**

Run: `.venv/bin/pytest tests/safety/test_rules.py -v && python3 scripts/check_yaml.py`
Expected: PASS + safety.yaml parse OK.

- [ ] **Step 6: Commit**

```bash
git add rules/safety.yaml app/safety/schemas.py app/safety/rules.py tests/safety/test_rules.py
git commit -m "안전 데이터 — rules/safety.yaml + SafetyRules 스키마 + 로더 (ADR 0030)"
```

---

## Task 3: 결정적 감지기 (`app/safety/moderation.py`)

**Files:**
- Create: `app/safety/moderation.py`
- Test: `tests/safety/test_moderation.py`

- [ ] **Step 1: 실패 테스트 작성**

Create `tests/safety/test_moderation.py`:

```python
from app.safety.moderation import SafetyVerdict, denylist_checker, detect


def _checker():
    return denylist_checker(["씨발", "ㅅㅂ", "개새끼"])


def test_clean_input_passes():
    v = detect("오늘 보트 수리 잘 돼?", [_checker()])
    assert v.category == "clean"
    assert v.matched_term is None


def test_denylist_hit_returns_matched_term():
    v = detect("이 씨발 보트", [_checker()])
    assert v.category == "harassment"
    assert v.matched_term == "씨발"


def test_normalization_catches_spaced_variant():
    # "씨 발" → 정규화 후 "씨발" 매칭.
    v = detect("씨 발 진짜", [_checker()])
    assert v.category == "harassment"
    assert v.matched_term == "씨발"


def test_checker_order_first_nonclean_wins():
    a = denylist_checker(["개새끼"])
    b = denylist_checker(["씨발"])
    v = detect("개새끼 씨발", [a, b])
    assert v.matched_term == "개새끼"  # 첫 checker 우선


def test_empty_after_normalize_is_clean():
    v = detect("   ", [_checker()])
    assert v.category == "clean"
```

- [ ] **Step 2: 실패 확인**

Run: `.venv/bin/pytest tests/safety/test_moderation.py -v`
Expected: FAIL — `ModuleNotFoundError: app.safety.moderation`.

- [ ] **Step 3: 구현**

Create `app/safety/moderation.py`:

```python
"""결정적 모더레이션 감지기 — checker 리스트가 확장점 (ADR 0030).

슬라이스는 denylist_checker 하나. v1.1 에서 ml_checker 를 append.
detect 가 입력을 한 번 정규화하고 각 checker(정규화된 텍스트)를 순서대로 호출,
첫 non-clean 을 반환한다.
"""

import re
from typing import Callable, Literal, Optional

from pydantic import BaseModel


class SafetyVerdict(BaseModel):
    category: Literal["clean", "harassment"]
    matched_term: Optional[str] = None


# checker: 정규화된 텍스트 → 판정
Checker = Callable[[str], SafetyVerdict]


def _normalize(text: str) -> str:
    """공백 제거(음운변형 "씨 발" 캐치) + 소문자."""
    return re.sub(r"\s+", "", text).lower()


def denylist_checker(denylist: list[str]) -> Checker:
    """denylist 항목을 정규화해 substring 매칭하는 checker 를 만든다."""
    norm_terms = [(original, _normalize(original)) for original in denylist]

    def check(norm_text: str) -> SafetyVerdict:
        for original, nt in norm_terms:
            if nt and nt in norm_text:
                return SafetyVerdict(category="harassment", matched_term=original)
        return SafetyVerdict(category="clean")

    return check


def detect(text: str, checkers: list[Checker]) -> SafetyVerdict:
    norm = _normalize(text)
    for check in checkers:
        verdict = check(norm)
        if verdict.category != "clean":
            return verdict
    return SafetyVerdict(category="clean")
```

- [ ] **Step 4: 통과 확인**

Run: `.venv/bin/pytest tests/safety/test_moderation.py -v`
Expected: PASS (5 tests).

- [ ] **Step 5: Commit**

```bash
git add app/safety/moderation.py tests/safety/test_moderation.py
git commit -m "결정적 모더레이션 감지기 — denylist checker + 정규화 + 확장 인터페이스 (ADR 0030)"
```

---

## Task 4: TurnResponse.kind + matched_term + SessionState (`app/models.py`)

**Files:**
- Modify: `app/models.py`
- Test: `tests/test_models.py` (확장)

- [ ] **Step 1: 실패 테스트 작성 (기존 파일에 추가)**

Append to `tests/test_models.py`:

```python
def test_turn_response_defaults_to_npc_kind():
    from app.models import TurnResponse
    resp = TurnResponse(reply="hi", choices=[], session_uuid="u")
    assert resp.kind == "npc"
    assert resp.matched_term is None


def test_turn_response_warning_kind():
    from app.models import TurnResponse
    resp = TurnResponse(kind="warning", reply="경고", choices=[], session_uuid="u", matched_term="씨발")
    assert resp.kind == "warning"
    assert resp.matched_term == "씨발"


def test_session_state_defaults():
    from app.models import SessionState
    s = SessionState(warning_count=0, first_strike_term=None, banned=False, ban_reason=None)
    assert s.banned is False
```

- [ ] **Step 2: 실패 확인**

Run: `.venv/bin/pytest tests/test_models.py -v`
Expected: FAIL — `TurnResponse` 에 kind 없음 / `SessionState` ImportError.

- [ ] **Step 3: 구현 — `app/models.py` 의 `TurnResponse` 교체 + `SessionState` 추가**

`app/models.py` 의 상단 import 를 교체:

```python
from typing import Literal, Optional
```

`TurnResponse` 클래스를 교체:

```python
class TurnResponse(BaseModel):
    """`POST /turn` 응답. awareness 정수는 노출 안 함 (mechanic-spec: 숫자 비노출).

    kind 판별자 (ADR 0031): "npc" = NPC 대사, "warning"/"ban" = 프레임 깨는 시스템 메시지.
    reply 는 kind 에 따라 NPC 대사 또는 시스템 메시지 텍스트.
    """
    model_config = ConfigDict(extra="forbid")
    kind: Literal["npc", "warning", "ban"] = "npc"
    reply: str
    choices: list[Choice] = []
    session_uuid: str
    matched_term: Optional[str] = None
```

파일 끝에 `SessionState` 추가:

```python
class SessionState(BaseModel):
    """sessions 행의 검증된 형태 (ADR 0031)."""
    model_config = ConfigDict(extra="forbid")
    warning_count: int
    first_strike_term: Optional[str]
    banned: bool
    ban_reason: Optional[str]
```

- [ ] **Step 4: 통과 확인 (전체 models 테스트)**

Run: `.venv/bin/pytest tests/test_models.py -v`
Expected: PASS (기존 4 + 신규 3).

- [ ] **Step 5: Commit**

```bash
git add app/models.py tests/test_models.py
git commit -m "도메인 모델 — TurnResponse.kind/matched_term + SessionState (ADR 0031)"
```

---

## Task 5: 안전 스키마 마이그레이션 + repo 함수 (`migrations/002`, `app/store/`)

**Files:**
- Create: `migrations/002_safety.sql`
- Modify: `app/store/db.py`
- Modify: `app/store/repo.py`
- Modify: `tests/conftest.py`
- Test: `tests/store/test_safety_repo.py`

- [ ] **Step 1: 마이그레이션 SQL 작성**

Create `migrations/002_safety.sql`:

```sql
CREATE TABLE IF NOT EXISTS sessions (
    session_uuid      UUID PRIMARY KEY,
    warning_count     INT  NOT NULL DEFAULT 0,
    first_strike_term TEXT,
    banned_at         TIMESTAMPTZ,
    ban_reason        TEXT,
    created_at        TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS safety_events (
    id           BIGSERIAL PRIMARY KEY,
    session_uuid UUID NOT NULL,
    category     TEXT NOT NULL,
    matched_term TEXT,
    created_at   TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

- [ ] **Step 2: db.apply_migrations 가 모든 마이그레이션 적용하도록 수정**

`app/store/db.py` 를 교체:

```python
"""psycopg3 연결 + migration 적용 헬퍼."""

from pathlib import Path

import psycopg

from app.config import DATABASE_URL

MIGRATIONS_DIR = Path(__file__).resolve().parents[2] / "migrations"


def connect():
    """autocommit 연결. slice 는 turn 당 단일 연결, 트랜잭션 경계는 단순화."""
    return psycopg.connect(DATABASE_URL, autocommit=True)


def apply_migrations(conn) -> None:
    """migrations/*.sql 을 파일명 순서대로 적용 (001, 002, ...). 전부 idempotent (IF NOT EXISTS)."""
    for path in sorted(MIGRATIONS_DIR.glob("*.sql")):
        conn.execute(path.read_text())
```

- [ ] **Step 3: conftest TRUNCATE 에 신규 테이블 추가**

`tests/conftest.py` 의 TRUNCATE 라인을 교체:

```python
    connection.execute("TRUNCATE npc_state, chat_logs, sessions, safety_events")
```

- [ ] **Step 4: 실패 테스트 작성**

Create `tests/store/test_safety_repo.py`:

```python
import uuid

from app.models import SessionState
from app.store import repo


def test_load_missing_session_returns_defaults(conn):
    s = repo.load_session(conn, str(uuid.uuid4()))
    assert s == SessionState(warning_count=0, first_strike_term=None, banned=False, ban_reason=None)


def test_ensure_then_set_warning(conn):
    sid = str(uuid.uuid4())
    repo.ensure_session(conn, sid)
    repo.set_warning(conn, sid, 1, "씨발")
    s = repo.load_session(conn, sid)
    assert s.warning_count == 1
    assert s.first_strike_term == "씨발"
    assert s.banned is False


def test_ban_session(conn):
    sid = str(uuid.uuid4())
    repo.ensure_session(conn, sid)
    repo.ban_session(conn, sid, "사유 텍스트")
    s = repo.load_session(conn, sid)
    assert s.banned is True
    assert s.ban_reason == "사유 텍스트"


def test_append_safety_event_stores_no_raw_input(conn):
    sid = str(uuid.uuid4())
    repo.ensure_session(conn, sid)
    repo.append_safety_event(conn, sid, "harassment", "씨발")
    rows = conn.execute(
        "SELECT category, matched_term FROM safety_events WHERE session_uuid = %s", (sid,)
    ).fetchall()
    assert rows == [("harassment", "씨발")]
    # 원문 입력을 담는 컬럼이 존재하지 않음을 보장.
    cols = conn.execute(
        "SELECT column_name FROM information_schema.columns WHERE table_name = 'safety_events'"
    ).fetchall()
    assert "input" not in {c[0] for c in cols}
```

- [ ] **Step 5: 실패 확인**

Run: `.venv/bin/pytest tests/store/test_safety_repo.py -v`
Expected: FAIL — `repo.load_session` 없음 (AttributeError).

- [ ] **Step 6: repo.py 에 안전 함수 추가**

`app/store/repo.py` 상단 import 에 `SessionState` 추가:

```python
from app.models import NpcState, SessionState
```

파일 끝에 추가:

```python
def ensure_session(conn, session_uuid: str) -> None:
    """sessions row 가 없으면 생성 (있으면 무시)."""
    conn.execute(
        "INSERT INTO sessions (session_uuid) VALUES (%s) ON CONFLICT (session_uuid) DO NOTHING",
        (session_uuid,),
    )


def load_session(conn, session_uuid: str) -> SessionState:
    row = conn.execute(
        "SELECT warning_count, first_strike_term, banned_at, ban_reason FROM sessions "
        "WHERE session_uuid = %s",
        (session_uuid,),
    ).fetchone()
    if row is None:
        return SessionState(warning_count=0, first_strike_term=None, banned=False, ban_reason=None)
    return SessionState(
        warning_count=row[0],
        first_strike_term=row[1],
        banned=row[2] is not None,
        ban_reason=row[3],
    )


def set_warning(conn, session_uuid: str, warning_count: int, first_strike_term: str) -> None:
    conn.execute(
        "UPDATE sessions SET warning_count = %s, first_strike_term = %s WHERE session_uuid = %s",
        (warning_count, first_strike_term, session_uuid),
    )


def ban_session(conn, session_uuid: str, ban_reason: str) -> None:
    conn.execute(
        "UPDATE sessions SET banned_at = now(), ban_reason = %s WHERE session_uuid = %s",
        (ban_reason, session_uuid),
    )


def append_safety_event(conn, session_uuid: str, category: str, matched_term: str | None) -> None:
    conn.execute(
        "INSERT INTO safety_events (session_uuid, category, matched_term) VALUES (%s, %s, %s)",
        (session_uuid, category, matched_term),
    )
```

- [ ] **Step 7: 통과 확인**

Run: `.venv/bin/pytest tests/store/ -v`
Expected: PASS (기존 store 테스트 + 신규 4).

- [ ] **Step 8: Commit**

```bash
git add migrations/002_safety.sql app/store/db.py app/store/repo.py tests/conftest.py tests/store/test_safety_repo.py
git commit -m "안전 스키마 — sessions/safety_events + repo 함수 + 다중 마이그레이션 적용 (ADR 0031)"
```

---

## Task 6: 2-strike 상태머신 (`app/safety/strike.py`)

**Files:**
- Create: `app/safety/strike.py`
- Test: `tests/safety/test_strike.py`

`register` 는 감지된 verdict 를 받아 세션 warning_count 를 전이시키고 safety_events 를
남기며, 프레임 깨는 메시지(템플릿 렌더)를 담은 `StrikeResult` 를 반환한다.

- [ ] **Step 1: 실패 테스트 작성**

Create `tests/safety/test_strike.py`:

```python
import uuid

from app.safety.moderation import SafetyVerdict
from app.safety import strike
from app.store import repo


def _verdict(term):
    return SafetyVerdict(category="harassment", matched_term=term)


def test_first_strike_is_warning(conn):
    sid = str(uuid.uuid4())
    res = strike.register(conn, sid, _verdict("씨발"))
    assert res.kind == "warning"
    assert res.matched_term == "씨발"
    assert "씨발" in res.message  # 템플릿 {term} 치환
    s = repo.load_session(conn, sid)
    assert s.warning_count == 1
    assert s.first_strike_term == "씨발"
    assert s.banned is False


def test_second_strike_is_ban_with_both_terms(conn):
    sid = str(uuid.uuid4())
    strike.register(conn, sid, _verdict("씨발"))
    res = strike.register(conn, sid, _verdict("개새끼"))
    assert res.kind == "ban"
    assert "씨발" in res.message and "개새끼" in res.message  # 1회/2회 단어
    s = repo.load_session(conn, sid)
    assert s.banned is True
    assert s.ban_reason == res.message


def test_each_strike_logs_safety_event(conn):
    sid = str(uuid.uuid4())
    strike.register(conn, sid, _verdict("씨발"))
    strike.register(conn, sid, _verdict("개새끼"))
    rows = conn.execute(
        "SELECT category, matched_term FROM safety_events WHERE session_uuid = %s ORDER BY id", (sid,)
    ).fetchall()
    assert rows == [("harassment", "씨발"), ("harassment", "개새끼")]
```

- [ ] **Step 2: 실패 확인**

Run: `.venv/bin/pytest tests/safety/test_strike.py -v`
Expected: FAIL — `ModuleNotFoundError: app.safety.strike`.

- [ ] **Step 3: 구현**

Create `app/safety/strike.py`:

```python
"""2-strike 성희롱/혐오 상태머신 (ADR 0009 Layer 2.5, ADR 0031).

register: verdict → 세션 warning_count 전이 + safety_events + 프레임 깨는 메시지 렌더.
Strike 1 = warning (LLM·awareness·chat_logs 불변, 호출 측이 보장). Strike 2 = 영구 차단.
"""

from typing import Literal, Optional

from pydantic import BaseModel

from app.safety.moderation import SafetyVerdict
from app.safety.rules import load_safety_rules
from app.store import repo


class StrikeResult(BaseModel):
    kind: Literal["warning", "ban"]
    message: str
    matched_term: Optional[str] = None


def register(conn, session_uuid: str, verdict: SafetyVerdict) -> StrikeResult:
    """성희롱/혐오 감지를 strike 로 등록. 호출 전 verdict.category != 'clean' 가정."""
    rules = load_safety_rules()
    term = verdict.matched_term or ""

    repo.ensure_session(conn, session_uuid)
    repo.append_safety_event(conn, session_uuid, verdict.category, term)
    sess = repo.load_session(conn, session_uuid)

    if sess.warning_count == 0:
        repo.set_warning(conn, session_uuid, 1, term)
        message = rules.messages.warning.format(term=term)
        return StrikeResult(kind="warning", message=message, matched_term=term)

    # 이미 경고 1회 → 영구 차단.
    message = rules.messages.ban.format(term1=sess.first_strike_term or "", term2=term)
    repo.ban_session(conn, session_uuid, message)
    return StrikeResult(kind="ban", message=message)
```

- [ ] **Step 4: 통과 확인**

Run: `.venv/bin/pytest tests/safety/test_strike.py -v`
Expected: PASS (3 tests).

- [ ] **Step 5: Commit**

```bash
git add app/safety/strike.py tests/safety/test_strike.py
git commit -m "2-strike 상태머신 — warning→ban 전이 + safety_events + 메시지 렌더 (ADR 0009/0031)"
```

---

## Task 7: 엔드포인트 오케스트레이션 (`app/api/main.py`)

**Files:**
- Modify: `app/api/main.py`
- Test: `tests/api/test_safety_endpoint.py`

ban 게이트 → strike 평가 → clean 이면 `run_turn`. `run_turn` 은 그대로(NPC 턴).

- [ ] **Step 1: 실패 테스트 작성**

Create `tests/api/test_safety_endpoint.py`:

```python
import psycopg
import pytest
from fastapi.testclient import TestClient

from app.config import DATABASE_URL
from app.models import Choice, TurnReply
from app.store import db


@pytest.fixture()
def client(monkeypatch):
    c = psycopg.connect(DATABASE_URL, autocommit=True)
    db.apply_migrations(c)
    c.execute("TRUNCATE npc_state, chat_logs, sessions, safety_events")
    c.close()

    import app.llm.client as llm_client

    def stub_call(system, messages):
        return TurnReply(
            reply="망치질은 멈추지 않아.", awareness_delta=5, reason="r", memory_tags=["purpose"],
            choices=[Choice(tone="empathetic", text="그래"),
                     Choice(tone="provocative", text="진짜?"),
                     Choice(tone="deflecting", text="딴 얘기")],
        )

    monkeypatch.setattr(llm_client, "call", stub_call)
    from app.api.main import app
    return TestClient(app)


def test_clean_input_is_npc_kind(client):
    r = client.post("/turn", json={"npc_id": "surigong", "player_input": "보트 수리 잘 돼?"})
    assert r.json()["kind"] == "npc"
    assert len(r.json()["choices"]) == 3


def test_first_harassment_is_warning_and_no_npc_state(client):
    r = client.post("/turn", json={"npc_id": "surigong", "player_input": "이 씨발아"})
    body = r.json()
    assert body["kind"] == "warning"
    assert body["matched_term"] == "씨발"
    # 턴 무효: npc_state 가 생성되지 않음 (awareness 변화 없음).
    sid = body["session_uuid"]
    c = psycopg.connect(DATABASE_URL, autocommit=True)
    row = c.execute("SELECT count(*) FROM npc_state WHERE session_uuid=%s", (sid,)).fetchone()
    c.close()
    assert row[0] == 0


def test_second_harassment_bans_and_blocks_subsequent(client):
    r1 = client.post("/turn", json={"npc_id": "surigong", "player_input": "씨발"})
    sid = r1.json()["session_uuid"]
    r2 = client.post("/turn", json={"session_uuid": sid, "npc_id": "surigong", "player_input": "개새끼"})
    assert r2.json()["kind"] == "ban"
    # 차단 후 clean 입력도 ban 반환.
    r3 = client.post("/turn", json={"session_uuid": sid, "npc_id": "surigong", "player_input": "미안해 보트 얘기하자"})
    assert r3.json()["kind"] == "ban"
```

- [ ] **Step 2: 실패 확인**

Run: `.venv/bin/pytest tests/api/test_safety_endpoint.py -v`
Expected: FAIL — clean 은 kind 키 없음 / 성희롱이 ban 게이트 안 거쳐 npc 처리됨.

- [ ] **Step 3: 구현 — `app/api/main.py` 교체**

```python
"""FastAPI — POST /turn. ban 게이트 → 2-strike → (clean) run_turn 오케스트레이션."""

from fastapi import FastAPI
from pydantic import BaseModel

from app.models import TurnResponse
from app.safety import strike
from app.safety.moderation import denylist_checker, detect
from app.safety.rules import load_safety_rules
from app.store import db, repo
from app.turn.loop import run_turn

app = FastAPI(title="난파섬 Sub-2b slice")


class TurnRequest(BaseModel):
    session_uuid: str | None = None
    npc_id: str
    player_input: str


@app.post("/turn")
def turn(req: TurnRequest) -> dict:
    with db.connect() as conn:
        session_uuid = req.session_uuid or repo.mint_session(conn)
        repo.ensure_session(conn, session_uuid)

        # 1) ban 게이트 — 차단된 세션은 모든 호출 차단.
        sess = repo.load_session(conn, session_uuid)
        if sess.banned:
            return TurnResponse(
                kind="ban", reply=sess.ban_reason or "", choices=[], session_uuid=session_uuid
            ).model_dump()

        # 2) strike 평가 (결정적 디니리스트).
        rules = load_safety_rules()
        verdict = detect(req.player_input, [denylist_checker(rules.harassment_denylist)])
        if verdict.category != "clean":
            result = strike.register(conn, session_uuid, verdict)
            return TurnResponse(
                kind=result.kind,
                reply=result.message,
                choices=[],
                session_uuid=session_uuid,
                matched_term=result.matched_term,
            ).model_dump()

        # 3) clean → 기존 NPC 턴 (Layer 1 길이/페르소나 + LLM + Layer 4).
        resp = run_turn(conn, session_uuid, req.npc_id, req.player_input)
        return resp.model_dump()
```

- [ ] **Step 4: 기존 endpoint fixture 의 TRUNCATE 에 신규 테이블 추가 (leakage 방지)**

엔드포인트가 이제 `sessions` row 를 만들므로, 기존 `tests/api/test_turn_endpoint.py` 의 fixture TRUNCATE 라인을 교체:

```python
    c.execute("TRUNCATE npc_state, chat_logs, sessions, safety_events")
```

- [ ] **Step 5: 통과 확인**

Run: `.venv/bin/pytest tests/api/ -v`
Expected: PASS (기존 api 테스트 + 신규 3).

- [ ] **Step 6: Commit**

```bash
git add app/api/main.py tests/api/test_safety_endpoint.py tests/api/test_turn_endpoint.py
git commit -m "엔드포인트 오케스트레이션 — ban 게이트 → 2-strike → run_turn (ADR 0031)"
```

---

## Task 8: 페르소나공격 키워드 safety.yaml 승격 (`app/safety/input_filter.py`)

**Files:**
- Modify: `app/safety/input_filter.py`
- Test: `tests/safety/test_input_filter.py` (기존 — green 유지)

Layer 1 의 하드코딩 키워드를 safety.yaml 에서 로드 (ADR 0030 Decision 3). 기존 테스트는 변경 없이 통과해야 함.

- [ ] **Step 1: 기존 테스트가 여전히 green 인지 먼저 확인 (baseline)**

Run: `.venv/bin/pytest tests/safety/test_input_filter.py -v`
Expected: PASS (현 하드코딩 기준).

- [ ] **Step 2: input_filter 가 safety.yaml 에서 키워드 로드하도록 수정**

`app/safety/input_filter.py` 의 `PERSONA_ATTACK_KEYWORDS` 상수 정의(9-20행)를 삭제하고, `check` 함수가 로더에서 가져오도록 교체:

```python
"""Layer 1 입력 prefilter — 길이 캡 + 페르소나-공격 키워드 차단.

Authority: docs/mechanic-spec.md Layer 1. 키워드는 rules/safety.yaml (ADR 0030).
"""

from pydantic import BaseModel

from app.safety.rules import load_safety_rules


class PrefilterResult(BaseModel):
    blocked: bool
    reason: str | None = None


def _contains_hangul(text: str) -> bool:
    return any("가" <= ch <= "힣" for ch in text)


def check(player_input: str) -> PrefilterResult:
    """입력을 검사. 차단 시 blocked=True + reason."""
    limit = 200 if _contains_hangul(player_input) else 500
    if len(player_input) > limit:
        return PrefilterResult(blocked=True, reason="too_long")
    low = player_input.lower()
    for kw in load_safety_rules().persona_attack:
        if kw.lower() in low:
            return PrefilterResult(blocked=True, reason="persona_attack")
    return PrefilterResult(blocked=False)
```

- [ ] **Step 3: 기존 테스트 green 유지 확인**

Run: `.venv/bin/pytest tests/safety/test_input_filter.py -v`
Expected: PASS — 동일 키워드가 이제 yaml 에서 옴 (동작 불변).

- [ ] **Step 4: Commit**

```bash
git add app/safety/input_filter.py
git commit -m "Layer 1 페르소나공격 키워드 safety.yaml 승격 — 하드코딩 제거 (ADR 0030)"
```

---

## Task 9: CLAUDE.md enforcement 갱신 + 최종 gate

**Files:**
- Modify: `CLAUDE.md` (Enforcement 섹션)

- [ ] **Step 1: CLAUDE.md 의 "Phase 1.0 Sub-2b+" 항목 갱신**

`CLAUDE.md` 의 `**Phase 1.0 Sub-2b+ (추후):**` 블록을 다음으로 교체:

```markdown
**Phase 1.0 Sub-2b (현재 — 안전 모더레이션 슬라이스 도입됨):**
- `app/safety/moderation` + `app/safety/strike` + `rules/safety.yaml` — 결정적 2-strike 성희롱/혐오 트랙 (디니리스트). 엔드포인트가 ban 게이트 → strike → run_turn 오케스트레이션.
- 안전 데이터(디니리스트/페르소나공격/메시지)는 `rules/safety.yaml` — 튜닝은 코드 아닌 YAML.
- `sessions` + `safety_events` 테이블 (ADR 0031). 전부 결정적 → 게이트 테스트 커버 (live 불필요).
- ML 모더레이션은 v1.1 — `moderation.detect` 의 checker 확장점 (ADR 0030).

**Phase 1.0 Sub-2b+ (추후):**
- ML 모더레이션 checker, save-code/쿠키, Cloudflare/failover, running summary, 나머지 3 NPC, FastAPI 프론트엔드/모바일.
```

- [ ] **Step 2: 전체 gate 최종 확인**

Run: `.venv/bin/pytest -q && python3 scripts/check_yaml.py && .venv/bin/python scripts/check_no_hardcoded_dialogue.py && echo OK`
Expected: 전부 green + `OK`.

- [ ] **Step 3: Commit**

```bash
git add CLAUDE.md
git commit -m "CLAUDE.md — Phase 1.0 Sub-2b 안전 모더레이션 enforcement 활성화"
```

---

## 실행 후 검증 (Definition of Done)

- [ ] `docker compose up -d db` 후 `.venv/bin/pytest` green (Sub-1 + Sub-2 + Sub-2b gate, live 제외). **llama-server 불필요** (이 슬라이스는 결정적).
- [ ] `python3 scripts/check_yaml.py` green (safety.yaml 포함).
- [ ] `.venv/bin/python scripts/check_no_hardcoded_dialogue.py` exit 0.
- [ ] (수동) fresh DB 마이그레이션: `.venv/bin/python -c "from app.store import db; db.apply_migrations(db.connect())"` (001 + 002 적용).
- [ ] (수동) `.venv/bin/uvicorn app.api.main:app` 후:
  - clean 입력 → `kind:"npc"` + 3 choices.
  - 성희롱 1회 → `kind:"warning"` + matched_term.
  - 같은 세션 2회 → `kind:"ban"`, 이후 clean 입력도 `kind:"ban"`.
- [ ] ADR 0030/0031 + mechanic-spec/mapping-spec cross-link 작동.

## 핵심 회귀 (이 슬라이스가 증명하는 단 하나)

`tests/api/test_safety_endpoint.py::test_second_harassment_bans_and_blocks_subsequent` — 성희롱
2회 입력이 세션을 영구 차단하고, 이후 clean 입력도 차단 화면을 반환한다. 그리고
`test_first_harassment_is_warning_and_no_npc_state` — strike 가 awareness/npc_state 를 건드리지
않는다(턴 무효). 공개 URL 자유 입력의 윤리 가드가 닫힌다.
```
