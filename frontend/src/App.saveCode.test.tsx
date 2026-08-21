// B1 프론트 어포던스 계약 pin — 세이브 코드 패널에서 회전에 도달할 수 있고,
// 회전 UI 가 이전 코드는 더 이상 쓸 수 없다는 사실을 명시한다. (Phase 2 step 2 — 실패 상태로 커밋.)
//
// 규약: 테스트 이름/주석 밖 리터럴은 영어. 사용자 노출 문구 단언은 tone.ts import 로만
// (scripts/check_no_hardcoded_dialogue.py 가 이 파일도 스캔한다).
//
// 서버는 stub fetch — 이 파일은 화면 어포던스만 pin 한다. 회전의 서버 계약은
// tests/api/test_save_code_rotate.py 소유.
//
// 미pin: 다른 기기/탭에 떠 있는 옛 코드의 스테일 표시 — 계약이 명시적으로 감수한다.

import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import App from "./App";
import {
  RETIRED_IMMUTABLE_CODE_CLAIM,
  SAVE_CODE_BUTTON,
  SAVE_CODE_ISSUED_NOTE,
  SAVE_CODE_ROTATE,
  SAVE_CODE_ROTATE_WARNING,
  START_BUTTON,
} from "./tone";

const ISSUED_CODE = "MAST-2345";
const ROTATED_CODE = "REEF-6789";

function jsonOk(body: unknown): Response {
  return {
    ok: true,
    status: 200,
    json: async () => body,
  } as Response;
}

/** 최소 stub 서버 — bootstrap(new) / 발급 / 회전만 안다. 그 외 경로는 즉시 실패시켜
 *  테스트가 모르는 요청을 조용히 통과시키지 않는다. */
function stubServer() {
  const fetchMock = vi.fn(async (input: RequestInfo | URL) => {
    const path = String(input);
    if (path === "/session/bootstrap") {
      return jsonOk({
        status: "new",
        npc_id: "surigong",
        reply: "npc opening (stub)",
        choices: [],
      });
    }
    if (path === "/save-code") {
      return jsonOk({ status: "ok", save_code: ISSUED_CODE });
    }
    if (path === "/save-code/rotate") {
      return jsonOk({ status: "ok", save_code: ROTATED_CODE });
    }
    throw new Error(`unstubbed request path: ${path}`);
  });
  vi.stubGlobal("fetch", fetchMock);
  return fetchMock;
}

/** 타이틀 → 채팅 → 세이브 코드 패널까지 연다 (발급된 코드가 화면에 뜬 상태). */
async function openSaveCodePanel() {
  render(<App />);
  fireEvent.click(screen.getByRole("button", { name: START_BUTTON }));
  fireEvent.click(await screen.findByRole("button", { name: SAVE_CODE_BUTTON }));
  await screen.findByText(ISSUED_CODE);
}

describe("save code panel rotation affordance", () => {
  beforeEach(() => {
    stubServer();
  });
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("reaches a rotation control from the chat save-code panel", async () => {
    await openSaveCodePanel();

    expect(screen.getByRole("button", { name: SAVE_CODE_ROTATE })).toBeTruthy();
  });

  it("states that the previous code stops working", async () => {
    await openSaveCodePanel();

    fireEvent.click(screen.getByRole("button", { name: SAVE_CODE_ROTATE }));

    // 마크업 구조는 구현 재량 — 문구가 화면에 있다는 사실만 pin.
    await waitFor(() => {
      expect(document.body.textContent).toContain(SAVE_CODE_ROTATE_WARNING);
    });
  });
});

describe("save code panel copy", () => {
  it("no longer claims that the code never changes", () => {
    // 회전이 생긴 이상 코드가 바뀌지 않는다는 옛 주장은 거짓이다 — 같은 화면의
    // 안내가 회전 계약과 모순되면 안 된다.
    expect(SAVE_CODE_ISSUED_NOTE).not.toContain(RETIRED_IMMUTABLE_CODE_CLAIM);
  });
});
