#!/usr/bin/env python3
"""Phase 0 enforcement: 모든 yaml 파일이 파싱 OK인지 확인.

Authority: ADR 0018, docs/superpowers/specs/2026-05-11-...
Run: python3 scripts/check_yaml.py
Exit code: 0 = all green, 1 = parse failure
"""
import os
import sys
import yaml

TARGET_DIRS = ["rules", "npcs"]


def main() -> int:
    errors = []
    for d in TARGET_DIRS:
        if not os.path.isdir(d):
            errors.append(f"missing dir: {d}/")
            continue
        for f in sorted(os.listdir(d)):
            if not f.endswith(".yaml"):
                continue
            path = os.path.join(d, f)
            try:
                with open(path, encoding="utf-8") as fh:
                    yaml.safe_load(fh)
                print(f"OK  {path}")
            except yaml.YAMLError as exc:
                errors.append(f"PARSE FAIL  {path}: {exc}")

    if errors:
        print("\n--- ERRORS ---")
        for e in errors:
            print(e)
        return 1

    print("\nAll yaml parsed OK.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
