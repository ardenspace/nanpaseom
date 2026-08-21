"""세이브 코드 — 형식 단일 정의 + 생성 + 시스템 문구 로더 (B3 계약, Phase 3).

- 형식: ``XXXX-XXXX`` — 4자-하이픈-4자, 총 9자 (``sessions.save_code VARCHAR(9)`` 와 일치).
- 알파벳: A-Z + 2-9 에서 혼동 문자 O/I/L/0/1 제외 (31자).
- 생성: ``<단어>-<랜덤4자>`` — 프리픽스는 섬/바다 테마 4자 단어 목록(전 글자가
  허용 알파벳 내 — 인간 재판정 2026-08-19, 가독 프리픽스 채택), 뒤 4자는
  알파벳 uniform random.
- 부여(민팅): ``mint_save_code`` — UNIQUE 충돌 재시도 + 세션 행 갱신. 발급/회전
  두 표면이 공유하는 단일 정의 (엔드포인트에 복사하지 않는다).
- 사용자 노출 문구는 ``rules/save_code.yaml`` (코드 하드코딩 금지, opening.yaml 패턴).

형식(상수/regex)은 발급과 검증(redeem)이 공유하는 단일 정의 — 테스트
``tests/api/test_save_code.py`` 가 이 정의에서 형식을 pin 한다.
"""

import re
import secrets
from functools import lru_cache
from pathlib import Path

import yaml
from psycopg.errors import UniqueViolation
from pydantic import BaseModel, ConfigDict

from app.store import repo

# 혼동 문자 제외 알파벳: A-Z 에서 O/I/L 제거 + 2-9 (0/1 제외).
SAVE_CODE_ALPHABET = "ABCDEFGHJKMNPQRSTUVWXYZ23456789"

SAVE_CODE_GROUP_LEN = 4
SAVE_CODE_LENGTH = 9  # 4 + '-' + 4, VARCHAR(9)

SAVE_CODE_RE = re.compile(
    rf"^[{SAVE_CODE_ALPHABET}]{{{SAVE_CODE_GROUP_LEN}}}"
    rf"-[{SAVE_CODE_ALPHABET}]{{{SAVE_CODE_GROUP_LEN}}}$"
)

# 프리픽스 단어 목록 — 섬/바다 테마 4자 영단어, 전 글자가 SAVE_CODE_ALPHABET 내
# (O/I/L 불가 → MOON/SAIL/ISLE/TIDE/KNOT 류 제외). 형식 정의와 같은 파일이
# 단일 정의 (목록 내용 자체는 구현 재량 — B3 Delegated).
SAVE_CODE_PREFIX_WORDS = (
    "MAST", "REEF", "WAVE", "DUSK", "DAWN",
    "FERN", "SAND", "RUST", "DEEP", "MYTH",
    "HYMN", "DRUM", "STAR", "WEST", "EAST",
)
assert all(
    len(w) == SAVE_CODE_GROUP_LEN and set(w) <= set(SAVE_CODE_ALPHABET)
    for w in SAVE_CODE_PREFIX_WORDS
), "프리픽스 단어는 전 글자가 SAVE_CODE_ALPHABET 내 4자여야 함"

RULES_DIR = Path(__file__).resolve().parents[1] / "rules"


def generate_save_code() -> str:
    """SAVE_CODE_RE 를 만족하는 ``단어-랜덤4자`` 코드 1개 (유일성 보장은 호출자 몫)."""
    word = secrets.choice(SAVE_CODE_PREFIX_WORDS)
    tail = "".join(secrets.choice(SAVE_CODE_ALPHABET) for _ in range(SAVE_CODE_GROUP_LEN))
    return f"{word}-{tail}"


SAVE_CODE_MINT_ATTEMPTS = 20  # 31^8 공간 — 충돌 자체가 희귀, 상한은 안전장치


class SaveCodeMintError(RuntimeError):
    """재시도 상한 내에 유일한 코드를 못 얻음 (실질적으로 발생 불가 — 안전장치)."""


def mint_save_code(conn, session_uuid: str, *, avoid: str | None = None) -> str:
    """세션에 새 코드를 부여하고 그 코드를 돌려준다 (UNIQUE 충돌 시 재시도).

    ``avoid`` 는 결과에서 배제할 코드 — 회전이 현재 코드를 넘기면 "회전 후 이전
    코드는 무효" 계약이 우연한 동일 코드로도 깨지지 않는다. 발급은 넘기지 않는다
    (부여할 코드가 아직 없는 경우에만 호출되므로 배제할 것도 없다).
    """
    for _ in range(SAVE_CODE_MINT_ATTEMPTS):
        code = generate_save_code()
        if code == avoid:
            continue
        try:
            repo.set_save_code(conn, session_uuid, code)
        except UniqueViolation:
            continue
        return code
    raise SaveCodeMintError("save code minting exhausted retries")


class SaveCodeRules(BaseModel):
    """rules/save_code.yaml — redeem 표면의 문구 + 시도 제한 수치 단일 홈.

    제한 수치가 코드가 아닌 YAML 에 사는 이유: 튜닝은 코드 수정이 아니라 YAML
    수정 (CLAUDE.md). 판정 로직은 app/api/rate_limit.py.
    """
    model_config = ConfigDict(extra="forbid")
    redeem_not_found_message: str
    redeem_rate_limit_attempts: int
    redeem_rate_limit_window_seconds: int
    redeem_rate_limited_message: str


@lru_cache(maxsize=1)
def load_save_code_rules() -> SaveCodeRules:
    raw = yaml.safe_load((RULES_DIR / "save_code.yaml").read_text())
    return SaveCodeRules.model_validate(raw)
