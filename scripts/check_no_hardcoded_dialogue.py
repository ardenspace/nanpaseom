#!/usr/bin/env python3
"""enforcement — 하드코딩된 사용자 노출 문구 금지 (CLAUDE.md 권한 경계).

두 가지 스캔. pre-commit 또는 CI 에서 실행. 비-zero exit = 위반.

1. NPC 대사 스캔 — `app/` (*.py) + `frontend/src/` 전체(tone.ts 포함)에
   npcs/*.yaml 의 sample_lines / diegetic_fallback 텍스트가 박히면 위반.
   NPC 텍스트는 빌더가 yaml 에서 생성한다.
2. frontend 한글 리터럴 스캔 — `frontend/src/` 의 사용자 노출 한글 문자열은
   tone 모듈(src/tone.ts)이 단일 홈. 그 외 파일에서 발견되면 위반.
   메커니즘 (단순 유지):
   - .ts/.tsx/.js/.jsx: *문자열 리터럴* ('..', "..", `..`) 만 검사 — 주석은 자유.
   - .css/.html: 주석(/* */, <!-- -->) 제거 후 파일 전체 검사.
   - 그 외 확장자는 스캔 안 함.
"""

import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
NPC_DIR = ROOT / "npcs"
APP_DIR = ROOT / "app"
FRONTEND_SRC = ROOT / "frontend" / "src"
MIN_LEN = 6  # 너무 짧은 문자열의 우발적 매칭 회피

# frontend 한글 리터럴의 유일한 허용 파일 (frontend/src 기준 상대 경로).
TONE_MODULE = "tone.ts"

JS_SUFFIXES = {".ts", ".tsx", ".js", ".jsx"}
MARKUP_SUFFIXES = {".css", ".html"}

HANGUL_RE = re.compile(r"[가-힣]")
# JS/TS 문자열 리터럴 — single/double quote + 템플릿 리터럴(멀티라인).
STRING_LIT_RE = re.compile(
    r"'(?:[^'\\\n]|\\.)*'"
    r'|"(?:[^"\\\n]|\\.)*"'
    r"|`(?:[^`\\]|\\.)*`",
    re.S,
)
CSS_COMMENT_RE = re.compile(r"/\*.*?\*/", re.S)
HTML_COMMENT_RE = re.compile(r"<!--.*?-->", re.S)


def collect_dialogue() -> set[str]:
    strings: set[str] = set()
    for f in NPC_DIR.glob("*.yaml"):
        data = yaml.safe_load(f.read_text(encoding="utf-8"))
        strings.add(data["diegetic_fallback"].strip())
        for band in data["voice"]["awakening_bands"]:
            for line in band["sample_lines"]:
                strings.add(line.strip())
    return {s for s in strings if len(s) >= MIN_LEN}


def frontend_files() -> list[Path]:
    if not FRONTEND_SRC.is_dir():
        return []
    return sorted(
        f for f in FRONTEND_SRC.rglob("*")
        if f.is_file() and f.suffix in JS_SUFFIXES | MARKUP_SUFFIXES
    )


def scan_paths(paths: list[Path], dialogue: set[str]) -> list[tuple[Path, str]]:
    hits: list[tuple[Path, str]] = []
    for py in paths:
        text = py.read_text(encoding="utf-8")
        for line in dialogue:
            if line in text:
                hits.append((py, line))
    return hits


def scan_dialogue() -> list[tuple[Path, str]]:
    """NPC 대사 스캔 — app/*.py + frontend/src (tone.ts 포함: 대사는 거기도 금지)."""
    targets = list(APP_DIR.rglob("*.py")) + frontend_files()
    return scan_paths(targets, collect_dialogue())


def scan_frontend_korean() -> list[tuple[Path, str]]:
    """frontend 한글 리터럴 스캔 — tone 모듈만 예외."""
    hits: list[tuple[Path, str]] = []
    for f in frontend_files():
        if f.relative_to(FRONTEND_SRC).as_posix() == TONE_MODULE:
            continue
        text = f.read_text(encoding="utf-8")
        if f.suffix in JS_SUFFIXES:
            candidates = STRING_LIT_RE.findall(text)
        else:
            candidates = [HTML_COMMENT_RE.sub("", CSS_COMMENT_RE.sub("", text))]
        for c in candidates:
            if HANGUL_RE.search(c):
                snippet = " ".join(c.split())[:60]
                hits.append((f, snippet))
    return hits


def main() -> int:
    bad = False
    for py, line in scan_dialogue():
        bad = True
        print(f"HARDCODED NPC DIALOGUE in {py.relative_to(ROOT)}: {line!r}", file=sys.stderr)
    for f, snippet in scan_frontend_korean():
        bad = True
        print(f"KOREAN LITERAL OUTSIDE TONE MODULE in {f.relative_to(ROOT)}: {snippet!r}", file=sys.stderr)
    if bad:
        print(
            "\nNPC 대사는 npcs/*.yaml 에만 (빌더가 생성). "
            f"frontend 시스템 문구는 frontend/src/{TONE_MODULE} 에만 (CLAUDE.md).",
            file=sys.stderr,
        )
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
