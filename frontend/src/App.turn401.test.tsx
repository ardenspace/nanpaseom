// /turn 401 자동 복구 경로 회귀 pin — 클라이언트가 *새 세션에 진입하는 유일한 경로*라
// 이후 페이즈(넛지 재노출)가 여기에 물린다. 지금 배포된 동작을 그대로 고정한다
// (개선 금지 — 개선은 spec/계약 경유).
//
// 규약: 테스트 이름/주석 밖 리터럴은 영어. 사용자 노출 문구 단언은 tone.ts import 로만
// (scripts/check_no_hardcoded_dialogue.py 가 이 파일도 스캔한다).
//
// 서버는 stub fetch — 경로별 응답 큐를 미리 넣고, 실제 호출 시퀀스를 정확히 단언한다.
// 시퀀스 단언이 곧 무한 루프 금지의 pin 이다 (재bootstrap 은 정확히 1회).

import { afterEach, describe, expect, it, vi } from "vitest";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import App from "./App";
import {
  BANNED_TITLE,
  FREE_INPUT_PLACEHOLDER,
  SEND_BUTTON,
  SERVER_UNREACHABLE,
  SESSION_RESTORE_FAILED,
  START_BUTTON,
} from "./tone";

const BOOTSTRAP = "/session/bootstrap";
const TURN = "/turn";

const OPENING = "npc opening (stub)";
const SECOND_OPENING = "npc opening after new session (stub)";
const RECOVERED_REPLY = "npc reply after recovery (stub)";
const STALE_HISTORY = "stale resumed history line (stub)";
const PLAYER_INPUT = "player input (stub)";
const SERVER_ERROR_MESSAGE = "server side error message (stub)";
const BAN_REASON = "ban reason from bootstrap (stub)";

/** 큐 항목: JSON 응답이거나 네트워크 단절(fetch reject). */
type Reply = { status: number; body: unknown } | "unreachable";

const json = (status: number, body: unknown): Reply => ({ status, body });

/** 큐가 비었을 때 돌려주는 응답. 클라이언트가 계약보다 더 호출하면 이게 나가고,
 *  호출 시퀀스 단언이 어긋나 테스트가 깨진다 (조용한 통과 방지). */
const OVERFLOW: Reply = {
  status: 401,
  body: { status: "error", message: "unexpected extra call (stub)" },
};

function stubServer(queues: Record<string, Reply[]>) {
  const calls: string[] = [];
  const fetchMock = vi.fn(async (input: RequestInfo | URL) => {
    const path = String(input);
    calls.push(path);
    const queue = queues[path];
    if (!queue) throw new Error(`unstubbed request path: ${path}`);
    const next = queue.shift() ?? OVERFLOW;
    if (next === "unreachable") throw new Error("network down (stub)");
    return {
      ok: next.status >= 200 && next.status < 300,
      status: next.status,
      json: async () => next.body,
    } as Response;
  });
  vi.stubGlobal("fetch", fetchMock);
  return calls;
}

const openingBootstrap = json(200, {
  status: "new",
  npc_id: "surigong",
  reply: OPENING,
  choices: [],
});

const unauthorizedTurn = json(401, {
  status: "error",
  message: "no session (stub)",
});

/** 타이틀 → 채팅 진입 → 자유 입력으로 한 턴 전송. */
async function sendOneTurn() {
  render(<App />);
  fireEvent.click(screen.getByRole("button", { name: START_BUTTON }));
  const field = await screen.findByPlaceholderText(FREE_INPUT_PLACEHOLDER);
  fireEvent.change(field, { target: { value: PLAYER_INPUT } });
  fireEvent.click(screen.getByRole("button", { name: SEND_BUTTON }));
}

describe("turn 401 auto recovery", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("re-bootstraps once and retries the pending turn when the session resumes", async () => {
    const calls = stubServer({
      [BOOTSTRAP]: [
        openingBootstrap,
        json(200, {
          status: "resumed",
          npc_id: "surigong",
          history: [{ role: "npc", content: STALE_HISTORY }],
          choices: [],
        }),
      ],
      [TURN]: [
        unauthorizedTurn,
        json(200, { kind: "npc", reply: RECOVERED_REPLY, choices: [] }),
      ],
    });

    await sendOneTurn();

    await screen.findByText(RECOVERED_REPLY);
    // bootstrap 은 정확히 1회 더, turn 은 정확히 1회 재시도 — 그 이상 없음.
    expect(calls).toEqual([BOOTSTRAP, TURN, BOOTSTRAP, TURN]);
    // resumed 복구는 채팅을 다시 그리지 않는다 — 기존 로그가 그대로 남고
    // bootstrap 이 준 히스토리는 버려진다 (배포된 동작).
    expect(screen.getByText(OPENING)).toBeTruthy();
    expect(screen.getByText(PLAYER_INPUT)).toBeTruthy();
    expect(screen.queryByText(STALE_HISTORY)).toBeNull();
  });

  it("enters the new session and does not resend the pending input when the server has none", async () => {
    const calls = stubServer({
      [BOOTSTRAP]: [
        openingBootstrap,
        json(200, {
          status: "new",
          npc_id: "surigong",
          reply: SECOND_OPENING,
          choices: [],
        }),
      ],
      [TURN]: [unauthorizedTurn],
    });

    await sendOneTurn();

    await screen.findByText(SECOND_OPENING);
    // 두 번째 /turn 이 없다 — 보류된 입력은 사라진 세션 소속이라 재전송하지 않는다.
    expect(calls).toEqual([BOOTSTRAP, TURN, BOOTSTRAP]);
    // 새 세션의 로그로 완전히 교체 — 이전 오프닝도 보낸 입력도 남지 않는다.
    expect(screen.queryByText(OPENING)).toBeNull();
    expect(screen.queryByText(PLAYER_INPUT)).toBeNull();
  });

  it("stops after one retry when the retried turn is rejected again", async () => {
    const calls = stubServer({
      [BOOTSTRAP]: [
        openingBootstrap,
        json(200, { status: "resumed", npc_id: "surigong", choices: [] }),
      ],
      [TURN]: [unauthorizedTurn, unauthorizedTurn],
    });

    await sendOneTurn();

    await screen.findByText(SESSION_RESTORE_FAILED);
    // 재bootstrap 은 다시 일어나지 않는다 (무한 루프 금지).
    expect(calls).toEqual([BOOTSTRAP, TURN, BOOTSTRAP, TURN]);
    // 잠금 해제 — 실패해도 입력은 다시 쓸 수 있어야 한다.
    await waitFor(() => {
      const field = screen.getByPlaceholderText(
        FREE_INPUT_PLACEHOLDER,
      ) as HTMLInputElement;
      expect(field.disabled).toBe(false);
    });
  });

  it("reports an unreachable server when the recovery bootstrap cannot be reached", async () => {
    const calls = stubServer({
      [BOOTSTRAP]: [openingBootstrap, "unreachable"],
      [TURN]: [unauthorizedTurn],
    });

    await sendOneTurn();

    await screen.findByText(SERVER_UNREACHABLE);
    expect(calls).toEqual([BOOTSTRAP, TURN, BOOTSTRAP]);
  });

  it("switches to the banned screen when the recovery bootstrap reports a ban", async () => {
    const calls = stubServer({
      [BOOTSTRAP]: [
        openingBootstrap,
        json(200, { status: "banned", ban_reason: BAN_REASON }),
      ],
      [TURN]: [unauthorizedTurn],
    });

    await sendOneTurn();

    await screen.findByText(BANNED_TITLE);
    expect(screen.getByText(BAN_REASON)).toBeTruthy();
    expect(calls).toEqual([BOOTSTRAP, TURN, BOOTSTRAP]);
  });

  it("shows the server message when the recovery bootstrap itself errors", async () => {
    const calls = stubServer({
      [BOOTSTRAP]: [
        openingBootstrap,
        json(503, { status: "error", message: SERVER_ERROR_MESSAGE }),
      ],
      [TURN]: [unauthorizedTurn],
    });

    await sendOneTurn();

    await screen.findByText(SERVER_ERROR_MESSAGE);
    // 채팅 화면에 남는다 — 차단도 새 세션도 아니다.
    expect(screen.getByText(OPENING)).toBeTruthy();
    expect(calls).toEqual([BOOTSTRAP, TURN, BOOTSTRAP]);
  });
});
