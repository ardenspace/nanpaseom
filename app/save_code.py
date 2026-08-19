"""세이브 코드 형식 — 발급과 검증(redeem)이 공유하는 단일 정의 (B3 계약, Phase 3).

- 형식: ``XXXX-XXXX`` — 4자-하이픈-4자, 총 9자 (``sessions.save_code VARCHAR(9)`` 와 일치).
- 알파벳: A-Z + 2-9 에서 혼동 문자 O/I/L/0/1 제외 (31자).
- PREFIX 단어 목록 등 생성 전략은 구현 재량 — 단, 결과는 반드시 ``SAVE_CODE_RE`` 를 만족.

이 모듈은 **상수 + regex 만** 둔다. 발급/redeem 함수 구현은 별도 스텝
(테스트 ``tests/api/test_save_code.py`` 가 이 정의에서 형식을 pin 한다).
"""

import re

# 혼동 문자 제외 알파벳: A-Z 에서 O/I/L 제거 + 2-9 (0/1 제외).
SAVE_CODE_ALPHABET = "ABCDEFGHJKMNPQRSTUVWXYZ23456789"

SAVE_CODE_GROUP_LEN = 4
SAVE_CODE_LENGTH = 9  # 4 + '-' + 4, VARCHAR(9)

SAVE_CODE_RE = re.compile(
    rf"^[{SAVE_CODE_ALPHABET}]{{{SAVE_CODE_GROUP_LEN}}}"
    rf"-[{SAVE_CODE_ALPHABET}]{{{SAVE_CODE_GROUP_LEN}}}$"
)
