// 러너 확증용 최소 pin — 이미 출하 중인 순수 로직(재방문 힌트) 한 건.
// localStorage 를 쓰므로 이 테스트가 통과하면 vitest 뿐 아니라
// jsdom DOM 환경과 setup 의 테스트 간 격리까지 함께 실증된다.
//
// 규약: describe/it 이름은 영어로 쓴다. 한글 리터럴의 단일 홈은 tone.ts 이고
// scripts/check_no_hardcoded_dialogue.py 가 테스트 파일도 스캔하기 때문.
// 사용자 노출 문구를 단언해야 하는 테스트는 tone.ts 에서 import 해서 쓴다.

import { describe, it, expect } from "vitest";
import { markPlayedHint, readPlayedHint } from "./playedHint";

describe("playedHint", () => {
  it("reads false when no hint is stored", () => {
    expect(readPlayedHint()).toBe(false);
  });

  it("reads true after markPlayedHint", () => {
    markPlayedHint();
    expect(readPlayedHint()).toBe(true);
  });

  it("does not leak the previous test's mark (setup isolation)", () => {
    expect(readPlayedHint()).toBe(false);
  });
});
