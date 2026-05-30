#!/usr/bin/env python3
"""enforcement — app/ 안에 NPC 대사 (sample_lines / diegetic_fallback) 하드코딩 금지.

빌더가 yaml 에서 생성하는 텍스트가 코드에 박히면 spec-driven 권한 경계 위반 (CLAUDE.md).
pre-commit 또는 CI 에서 실행. 비-zero exit = 위반.
"""

import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
NPC_DIR = ROOT / "npcs"
APP_DIR = ROOT / "app"
MIN_LEN = 6  # 너무 짧은 문자열의 우발적 매칭 회피


def collect_dialogue() -> set[str]:
    strings: set[str] = set()
    for f in NPC_DIR.glob("*.yaml"):
        data = yaml.safe_load(f.read_text(encoding="utf-8"))
        strings.add(data["diegetic_fallback"].strip())
        for band in data["voice"]["awakening_bands"]:
            for line in band["sample_lines"]:
                strings.add(line.strip())
    return {s for s in strings if len(s) >= MIN_LEN}


def scan_paths(paths: list[Path], dialogue: set[str]) -> list[tuple[Path, str]]:
    hits: list[tuple[Path, str]] = []
    for py in paths:
        text = py.read_text(encoding="utf-8")
        for line in dialogue:
            if line in text:
                hits.append((py, line))
    return hits


def scan_app() -> list[tuple[Path, str]]:
    return scan_paths(list(APP_DIR.rglob("*.py")), collect_dialogue())


def main() -> int:
    hits = scan_app()
    for py, line in hits:
        print(f"HARDCODED NPC DIALOGUE in {py.relative_to(ROOT)}: {line!r}", file=sys.stderr)
    if hits:
        print("\nNPC 대사는 npcs/*.yaml 에만. 빌더가 생성합니다 (CLAUDE.md).", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
