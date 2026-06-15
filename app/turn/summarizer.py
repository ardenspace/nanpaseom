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
