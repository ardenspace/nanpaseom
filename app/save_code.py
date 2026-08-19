"""세이브 코드 — 형식 단일 정의 + 생성 + 시스템 문구 로더 (B3 계약, Phase 3).

- 형식: ``XXXX-XXXX`` — 4자-하이픈-4자, 총 9자 (``sessions.save_code VARCHAR(9)`` 와 일치).
- 알파벳: A-Z + 2-9 에서 혼동 문자 O/I/L/0/1 제외 (31자).
- 생성: ``<단어>-<랜덤4자>`` — 프리픽스는 섬/바다 테마 4자 단어 목록(전 글자가
  허용 알파벳 내 — 인간 재판정 2026-08-19, 가독 프리픽스 채택), 뒤 4자는
  알파벳 uniform random. UNIQUE 충돌 처리(재시도)는 발급 엔드포인트 몫.
- 사용자 노출 문구는 ``rules/save_code.yaml`` (코드 하드코딩 금지, opening.yaml 패턴).

형식(상수/regex)은 발급과 검증(redeem)이 공유하는 단일 정의 — 테스트
``tests/api/test_save_code.py`` 가 이 정의에서 형식을 pin 한다.
"""

import re
import secrets
from functools import lru_cache
from pathlib import Path

import yaml
from pydantic import BaseModel, ConfigDict

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


class SaveCodeRules(BaseModel):
    model_config = ConfigDict(extra="forbid")
    issue_no_session_message: str
    redeem_not_found_message: str


@lru_cache(maxsize=1)
def load_save_code_rules() -> SaveCodeRules:
    raw = yaml.safe_load((RULES_DIR / "save_code.yaml").read_text())
    return SaveCodeRules.model_validate(raw)
