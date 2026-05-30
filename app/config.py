"""환경 설정 — env override 가능. slice 는 비밀값을 코드에 박지 않음."""

import os

DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql://nanpaseom:nanpaseom@localhost:5432/nanpaseom",
)
# 로컬 llama-server (llama.cpp). API 키 불필요.
LLAMA_SERVER_URL = os.environ.get("LLAMA_SERVER_URL", "http://localhost:8080")
# llama-server alias — 미설정/무시돼도 무방 (단일 모델 서빙).
MODEL = os.environ.get("NANPASEOM_MODEL", "gemma-4-26b")
