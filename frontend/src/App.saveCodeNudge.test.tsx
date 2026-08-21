// B5 계약 pin (2/2) — 화면에 붙은 넛지 계약. (Phase 4 step 1 — 실패 상태로 커밋.)
//
// 여기서 재는 것: 진입 응답의 has_save_code(B2b) 가 넛지 노출의 권위라는 것,
// 세션 도중 발급/회전 성공이 *추가 왕복 없이* 즉시 코드 보유로 반영된다는 것,
// 한 번 닫으면 이 기기에서 반복 노출되지 않는다는 것, 그리고 그 예외 —
// 코드 없는 새 세션 진입에서는 다시 보인다는 것.
//
// 임계값 경계 자체와 판정 함수의 시그니처는 saveCodeNudge.test.ts 소유.
// 서버측 has_save_code 계약은 tests/api/test_has_save_code.py 소유.
//
// 규약: 테스트 이름/주석 밖 리터럴은 영어. 사용자 노출 문구 단언은 tone.ts import 로만
// (scripts/check_no_hardcoded_dialogue.py 가 이 파일도 스캔한다).
//
// 미pin: 넛지의 마크업 구조/위치/애니메이션 — 구현 재량. 문구가 화면에 있는가,
// 닫을 수 있는가만 본다.

import { afterEach, describe, expect, it, vi } from "vitest";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import App from "./App";
import {
  CONTINUE_BUTTON,
  FREE_INPUT_PLACEHOLDER,
  SAVE_CODE_BUTTON,
  SAVE_CODE_CLOSE,
  SAVE_CODE_NUDGE_AFTER_TURNS,
  SAVE_CODE_NUDGE_BODY,
  SAVE_CODE_NUDGE_DISMISS,
  SAVE_CODE_ROTATE,
  SEND_BUTTON,
  START_BUTTON,
} from "./tone";

const BOOTSTRAP = "/session/bootstrap";
const TURN = "/turn";
const ISSUE = "/save-code";
const ROTATE = "/save-code/rotate";

const T = SAVE_CODE_NUDGE_AFTER_TURNS;

const OPENING = "npc opening (stub)";
const PAST_LINE = "past history line (stub)";
const NPC_REPLY = "npc reply to";
const ISSUED_CODE = "MAST-2345";
const ROTATED_CODE = "REEF-6789";

type Json = Record<string, unknown>;

/** 진입 응답 — 계약상 new/resumed 둘 다 has_save_code 를 싣는다 (B2b). */
const newEntry = (hasSaveCode: boolean): Json => ({
  status: "new",
  npc_id: "surigong",
  reply: OPENING,
  choices: [],
  has_save_code: hasSaveCode,
});

const resumedEntry = (hasSaveCode: boolean): Json => ({
  status: "resumed",
  npc_id: "surigong",
  history: [{ role: "assistant", content: PAST_LINE }],
  choices: [],
  has_save_code: hasSaveCode,
});

function jsonOk(body: unknown): Response {
  return { ok: true, status: 200, json: async () => body } as Response;
}

/** stub 서버. bootstrap 은 주어진 진입 응답을 순서대로 소비하고 마지막 것이
 *  이후에도 계속 나온다 (한 테스트 안에서 재진입을 흉내내기 위함).
 *  /turn 은 보낸 입력을 그대로 되울려 턴마다 고유한 텍스트를 만든다. */
function stubServer(entries: Json[]) {
  const calls: string[] = [];
  const queue = [...entries];
  const fetchMock = vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
    const path = String(input);
    calls.push(path);
    if (path === BOOTSTRAP) {
      return jsonOk(queue.length > 1 ? queue.shift() : queue[0]);
    }
    if (path === TURN) {
      const sent = JSON.parse(String(init?.body ?? "{}")) as {
        player_input?: string;
      };
      return jsonOk({
        kind: "npc",
        reply: `${NPC_REPLY} ${sent.player_input ?? ""}`,
        choices: [],
      });
    }
    if (path === ISSUE) return jsonOk({ status: "ok", save_code: ISSUED_CODE });
    if (path === ROTATE) return jsonOk({ status: "ok", save_code: ROTATED_CODE });
    throw new Error(`unstubbed request path: ${path}`);
  });
  vi.stubGlobal("fetch", fetchMock);
  return calls;
}

/** 타이틀의 진입 버튼 — 재방문 힌트가 붙으면 라벨이 바뀌므로 둘 다 받는다. */
function startButton(): HTMLElement {
  return screen.getByRole("button", {
    name: (name: string) => name === START_BUTTON || name === CONTINUE_BUTTON,
  });
}

async function enterChat() {
  fireEvent.click(startButton());
  await screen.findByPlaceholderText(FREE_INPUT_PLACEHOLDER);
}

/** 자유 입력으로 count 턴을 보낸다. tag 는 턴 텍스트를 고유하게 만드는 접두사. */
async function driveTurns(count: number, tag: string) {
  for (let i = 0; i < count; i++) {
    const text = `${tag}/${i}`;
    const field = await screen.findByPlaceholderText(FREE_INPUT_PLACEHOLDER);
    fireEvent.change(field, { target: { value: text } });
    fireEvent.click(screen.getByRole("button", { name: SEND_BUTTON }));
    await screen.findByText(`${NPC_REPLY} ${text}`);
  }
}

function nudgeVisible(): boolean {
  return (document.body.textContent ?? "").includes(SAVE_CODE_NUDGE_BODY);
}

/** 채팅 헤더에서 세이브 코드를 발급받고 패널을 닫는다 (세션 도중 코드 보유 전환). */
async function issueCodeAndClose() {
  fireEvent.click(screen.getByRole("button", { name: SAVE_CODE_BUTTON }));
  await screen.findByText(ISSUED_CODE);
  fireEvent.click(screen.getByRole("button", { name: SAVE_CODE_CLOSE }));
}

describe("save code nudge exposure", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("stays hidden before the threshold turn", async () => {
    stubServer([newEntry(false)]);
    render(<App />);
    await enterChat();

    await driveTurns(T - 1, "below");

    expect(nudgeVisible()).toBe(false);
  });

  it("appears at the threshold turn with a dismiss control", async () => {
    stubServer([newEntry(false)]);
    render(<App />);
    await enterChat();

    await driveTurns(T, "at");

    await waitFor(() => {
      expect(nudgeVisible()).toBe(true);
    });
    expect(
      screen.getByRole("button", { name: SAVE_CODE_NUDGE_DISMISS }),
    ).toBeTruthy();
  });

  it("never appears when the entry response reports an existing save code", async () => {
    stubServer([resumedEntry(true)]);
    render(<App />);
    await enterChat();

    await driveTurns(T, "hascode");

    expect(nudgeVisible()).toBe(false);
  });
});

describe("save code nudge after in-session code changes", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("stays hidden after issuing a code mid-session, without re-entering", async () => {
    // 진입 응답은 코드 없음이었지만 발급이 성공했다 — 발급 응답이 코드를 돌려주므로
    // 클라이언트는 추가 왕복 없이 즉시 참으로 간주한다.
    const calls = stubServer([newEntry(false)]);
    render(<App />);
    await enterChat();

    await issueCodeAndClose();
    await driveTurns(T, "issued");

    expect(nudgeVisible()).toBe(false);
    expect(calls.filter((p) => p === BOOTSTRAP)).toHaveLength(1);
  });

  it("stays hidden after rotating a code mid-session, without re-entering", async () => {
    // 회전은 코드를 갈아끼울 뿐 — 보유 상태를 되돌리지 않는다.
    const calls = stubServer([newEntry(false)]);
    render(<App />);
    await enterChat();

    fireEvent.click(screen.getByRole("button", { name: SAVE_CODE_BUTTON }));
    await screen.findByText(ISSUED_CODE);
    fireEvent.click(screen.getByRole("button", { name: SAVE_CODE_ROTATE }));
    fireEvent.click(screen.getByRole("button", { name: SAVE_CODE_ROTATE }));
    await screen.findByText(ROTATED_CODE);
    fireEvent.click(screen.getByRole("button", { name: SAVE_CODE_CLOSE }));

    await driveTurns(T, "rotated");

    expect(nudgeVisible()).toBe(false);
    expect(calls.filter((p) => p === BOOTSTRAP)).toHaveLength(1);
  });
});

describe("save code nudge dismissal", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  /** 임계값까지 몰고 가 넛지를 띄운 뒤 닫는다. */
  async function reachAndDismiss(tag: string) {
    await driveTurns(T, tag);
    await waitFor(() => {
      expect(nudgeVisible()).toBe(true);
    });
    fireEvent.click(
      screen.getByRole("button", { name: SAVE_CODE_NUDGE_DISMISS }),
    );
    await waitFor(() => {
      expect(nudgeVisible()).toBe(false);
    });
  }

  it("does not come back later in the same session", async () => {
    stubServer([newEntry(false)]);
    render(<App />);
    await enterChat();

    await reachAndDismiss("dismiss");
    await driveTurns(2, "after-dismiss");

    expect(nudgeVisible()).toBe(false);
  });

  it("stays dismissed when the same device resumes the session later", async () => {
    stubServer([newEntry(false), resumedEntry(false)]);
    const first = render(<App />);
    await enterChat();
    await reachAndDismiss("dismiss");
    first.unmount();

    render(<App />); // 같은 기기 재방문 — 이어지는 세션 (코드 없음)
    await enterChat();
    await driveTurns(T, "resumed-again");

    expect(nudgeVisible()).toBe(false);
  });

  it("shows again when the same device enters a code-less new session", async () => {
    // 쿠키가 사라져 새 세션이 된 플레이어 — 코드가 없는데 넛지를 영영 못 보면 안 된다.
    stubServer([newEntry(false), newEntry(false)]);
    const first = render(<App />);
    await enterChat();
    await reachAndDismiss("dismiss");
    first.unmount();

    render(<App />);
    await enterChat();
    await driveTurns(T, "new-again");

    await waitFor(() => {
      expect(nudgeVisible()).toBe(true);
    });
  });
});
