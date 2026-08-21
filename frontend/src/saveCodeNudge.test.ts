// B5 계약 pin (1/2) — 넛지 판정의 순수 함수와 dismiss 플래그 저장소.
// (Phase 4 step 1 — 실패 상태로 커밋. 구현은 다음 스텝.)
//
// 이 파일이 확정하는 것: 모듈 ./saveCodeNudge, 함수 shouldShowSaveCodeNudge(state)
// 와 read/mark/clearNudgeDismissed(), 입력 shape NudgeState.
// 화면에 붙은 계약(진입 응답 반영 · 발급/회전 즉시 참 · 재노출)은
// App.saveCodeNudge.test.tsx 소유 — 여기서는 화면 없이 재는 것만 잰다.
//
// 임계값은 tone.ts 에서 읽는다. 숫자를 여기 인라인하면 튜닝이 테스트를 거짓으로
// 만든다 — 계약은 설정된 임계값의 경계 양쪽이지 특정 숫자가 아니다.
//
// 규약: 테스트 이름/주석 밖 리터럴은 영어 (scripts/check_no_hardcoded_dialogue.py).

import { afterEach, describe, expect, it, vi } from "vitest";
import {
  clearNudgeDismissed,
  markNudgeDismissed,
  readNudgeDismissed,
  shouldShowSaveCodeNudge,
  type NudgeState,
} from "./saveCodeNudge";
import { SAVE_CODE_NUDGE_AFTER_TURNS } from "./tone";

const T = SAVE_CODE_NUDGE_AFTER_TURNS;

/** 넛지가 보여야 하는 기본 상태 — 각 테스트는 한 축만 바꾼다. */
function state(over: Partial<NudgeState> = {}): NudgeState {
  return { hasSaveCode: false, turnCount: T, dismissed: false, ...over };
}

describe("save code nudge threshold", () => {
  it("has a threshold of at least one turn (boundary is meaningful)", () => {
    expect(Number.isInteger(T)).toBe(true);
    expect(T).toBeGreaterThanOrEqual(1);
  });

  it("stays hidden one turn below the configured threshold", () => {
    expect(shouldShowSaveCodeNudge(state({ turnCount: T - 1 }))).toBe(false);
  });

  it("shows at exactly the configured threshold", () => {
    expect(shouldShowSaveCodeNudge(state({ turnCount: T }))).toBe(true);
  });

  it("stays shown above the threshold", () => {
    expect(shouldShowSaveCodeNudge(state({ turnCount: T + 1 }))).toBe(true);
  });

  it("stays hidden at zero turns", () => {
    expect(shouldShowSaveCodeNudge(state({ turnCount: 0 }))).toBe(false);
  });
});

describe("save code nudge suppression", () => {
  it("never shows to a session that already holds a code", () => {
    expect(shouldShowSaveCodeNudge(state({ hasSaveCode: true }))).toBe(false);
    expect(
      shouldShowSaveCodeNudge(state({ hasSaveCode: true, turnCount: T * 10 })),
    ).toBe(false);
  });

  it("never shows once dismissed on this device", () => {
    expect(shouldShowSaveCodeNudge(state({ dismissed: true }))).toBe(false);
    expect(
      shouldShowSaveCodeNudge(state({ dismissed: true, turnCount: T * 10 })),
    ).toBe(false);
  });
});

describe("nudge dismiss flag storage", () => {
  afterEach(() => {
    vi.restoreAllMocks();
  });

  it("reads false when nothing is stored", () => {
    expect(readNudgeDismissed()).toBe(false);
  });

  it("reads true after marking dismissed", () => {
    markNudgeDismissed();
    expect(readNudgeDismissed()).toBe(true);
  });

  it("reads false again after clearing (code-less new session re-entry)", () => {
    markNudgeDismissed();
    clearNudgeDismissed();
    expect(readNudgeDismissed()).toBe(false);
  });

  it("does not leak the previous test's mark (setup isolation)", () => {
    expect(readNudgeDismissed()).toBe(false);
  });

  it("degrades to not-dismissed when storage is unavailable", () => {
    // 프라이버시 모드 등 — 저장이 불가능하면 재노출될 수 있다 (기록된 한계).
    // 던지지 않는 것이 계약: 넛지 하나 때문에 화면이 깨지면 안 된다.
    vi.spyOn(Storage.prototype, "setItem").mockImplementation(() => {
      throw new Error("storage unavailable (stub)");
    });
    vi.spyOn(Storage.prototype, "getItem").mockImplementation(() => {
      throw new Error("storage unavailable (stub)");
    });

    expect(() => markNudgeDismissed()).not.toThrow();
    expect(readNudgeDismissed()).toBe(false);
  });
});
