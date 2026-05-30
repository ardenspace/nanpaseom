"""CLI — `python -m app.prompt_builder --npc surigong --awareness 70 ...`.

용도: 디버그 / oracle 회귀 검증 / 디자이너 가 시스템 프롬프트 모양 손쉽게 확인.
LLM 호출 없음 — 순수 yaml→string.
"""

import argparse
import json
import sys
import traceback

from app.prompt_builder import build_prompt


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Sub-1 — 시스템 프롬프트 빌더 (offline)",
    )
    parser.add_argument(
        "--npc",
        required=True,
        choices=["surigong", "eobu", "halmoni", "hyean"],
        help="NPC name",
    )
    parser.add_argument(
        "--awareness",
        required=True,
        type=int,
        help="awareness int 0-100",
    )
    parser.add_argument(
        "--memory-tags",
        default="[]",
        help="JSON list of memory tag strings (default: '[]')",
    )
    parser.add_argument(
        "--hooks-runtime",
        default="{}",
        help="JSON dict of hook runtime variables (default: '{}')",
    )
    args = parser.parse_args(argv)

    try:
        memory_tags = json.loads(args.memory_tags)
        hooks_runtime = json.loads(args.hooks_runtime)
        output = build_prompt(
            npc_name=args.npc,
            awareness=args.awareness,
            memory_tags=memory_tags,
            hooks_runtime=hooks_runtime,
        )
        print(output)
        return 0
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
