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
