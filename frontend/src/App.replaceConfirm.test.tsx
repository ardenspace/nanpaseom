// B4 계약 pin — 대체 확인 다이얼로그. (Phase 3 step 1 — 탈출구 절반은 실패 상태로 커밋.)
//
// 두 절반이 섞여 있다:
//  (1) 회귀 pin (지금 통과해야 정상) — 타이틀의 상시 코드 입구, 그리고 진행 유무와
//      무관한 *무조건* 대체 확인. 무조건인 이유는 HttpOnly 쿠키를 클라이언트가
//      읽을 수 없어 진행 없음 판정이 신뢰 불가이기 때문 (지난 런의 의식적 설계).
//      여기가 깨지면 그건 실제 회귀다.
//  (2) 신규 pin (지금 실패해야 정상) — 다이얼로그 안의 탈출구. 갈아타기 전에
//      이 기기 세션의 세이브 코드를 받아 두는 경로와 그 실패 분기.
//
// 규약: 테스트 이름/주석 밖 리터럴은 영어. 사용자 노출 문구 단언은 tone.ts import 로만
// (scripts/check_no_hardcoded_dialogue.py 가 이 파일도 스캔한다).
//
// 서버는 stub fetch (공유 헬퍼 src/test/stubServer) — 경로별 응답 큐. 호출 시퀀스 단언이
// 곧 확인 전에는 아무 요청도 안 나간다 / 탈출구 실패 뒤에도 redeem 이 실제로 나간다 의 pin 이다.
//
// 미pin: 서버측 계약(B2 /save-code, B3 /save-code/redeem)은 python 테스트 소유.
// 여기서는 화면 어포던스와 클라이언트 가드만 본다.

import { afterEach, describe, expect, it, vi } from "vitest";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import App from "./App";
import { markPlayedHint } from "./playedHint";
import { backdropShowsBusy, clickBackdrop } from "./test/overlay";
import { json, stubServer, type StubReply } from "./test/stubServer";
import {
  REPLACE_CONFIRM_CANCEL,
  REPLACE_CONFIRM_OK,
  REPLACE_CONFIRM_TITLE,
  REPLACE_RESCUE_CODE,
  REPLACE_RESCUE_FAILED,
  SAVE_CODE_COPY,
  SAVE_CODE_ENTRY,
  SAVE_CODE_INPUT_PLACEHOLDER,
  SAVE_CODE_SUBMIT,
} from "./tone";

const SAVE_CODE = "/save-code";
const REDEEM = "/save-code/redeem";

const TYPED_CODE = "MAST-2345";
const RESCUED_CODE = "REEF-6789";
const OPENING = "npc opening after redeem (stub)";
const BAN_REASON = "ban reason from save code (stub)";
const SERVER_ERROR_MESSAGE = "server side error message (stub)";

// 이 파일은 공유 stubServer 의 기본 정책을 쓴다 — 큐에 없는 경로도, 큐를 넘어선
// 여분 호출도 던진다 (조용히 통과하지 못하게).

/** jsdom 에는 실제 클립보드가 없다 — 성공/실패를 시험이 정한다. */
function stubClipboard(writeText: (text: string) => Promise<void>) {
  Object.defineProperty(navigator, "clipboard", {
    value: { writeText },
    configurable: true,
  });
}

/** 타이틀 → 코드 입력 열기 → 코드 타이핑. 아직 제출하지 않는다. */
function typeCode() {
  render(<App />);
  fireEvent.click(screen.getByRole("button", { name: SAVE_CODE_ENTRY }));
  fireEvent.change(screen.getByPlaceholderText(SAVE_CODE_INPUT_PLACEHOLDER), {
    target: { value: TYPED_CODE },
  });
}

/** 코드 제출 → 대체 확인 다이얼로그가 뜰 때까지. */
async function openReplaceConfirm() {
  typeCode();
  fireEvent.click(screen.getByRole("button", { name: SAVE_CODE_SUBMIT }));
  await screen.findByText(REPLACE_CONFIRM_TITLE);
}

afterEach(() => {
  vi.unstubAllGlobals();
  Reflect.deleteProperty(navigator, "clipboard");
});

describe("title save code entry", () => {
  it("offers the save code entry on the title screen of a fresh device", () => {
    stubServer({});
    render(<App />);

    expect(screen.getByRole("button", { name: SAVE_CODE_ENTRY })).toBeTruthy();
  });

  it("still offers the save code entry when the device has a played hint", () => {
    stubServer({});
    markPlayedHint();
    render(<App />);

    expect(screen.getByRole("button", { name: SAVE_CODE_ENTRY })).toBeTruthy();
  });
});

describe("unconditional replace confirmation", () => {
  it("asks for confirmation even when this device has no recorded progress", async () => {
    const calls = stubServer({});

    await openReplaceConfirm();

    // 확인 전에는 어떤 요청도 나가지 않는다 — redeem 은 확인 뒤에만.
    expect(calls).toEqual([]);
  });

  it("asks for confirmation when this device has a played hint", async () => {
    const calls = stubServer({});
    markPlayedHint();

    await openReplaceConfirm();

    expect(calls).toEqual([]);
  });

  it("keeps the typed code and sends nothing when the confirmation is cancelled", async () => {
    const calls = stubServer({});

    await openReplaceConfirm();
    fireEvent.click(screen.getByRole("button", { name: REPLACE_CONFIRM_CANCEL }));

    await waitFor(() => {
      expect(screen.queryByText(REPLACE_CONFIRM_TITLE)).toBeNull();
    });
    const field = screen.getByPlaceholderText(
      SAVE_CODE_INPUT_PLACEHOLDER,
    ) as HTMLInputElement;
    expect(field.value).toBe(TYPED_CODE);
    expect(calls).toEqual([]);
  });
});

describe("replace confirmation escape hatch", () => {
  it("offers a path to this session's save code from inside the dialog", async () => {
    stubServer({});

    await openReplaceConfirm();

    expect(
      screen.getByRole("button", { name: REPLACE_RESCUE_CODE }),
    ).toBeTruthy();
  });

  it("shows the code and offers a copy control when the server issues one", async () => {
    const calls = stubServer({
      [SAVE_CODE]: [json(200, { status: "ok", save_code: RESCUED_CODE })],
    });

    await openReplaceConfirm();
    fireEvent.click(screen.getByRole("button", { name: REPLACE_RESCUE_CODE }));

    await screen.findByText(RESCUED_CODE);
    expect(screen.getByRole("button", { name: SAVE_CODE_COPY })).toBeTruthy();
    expect(calls).toEqual([SAVE_CODE]);
  });

  it("keeps the code on screen when the clipboard write rejects", async () => {
    const writeText = vi.fn<(text: string) => Promise<void>>(() =>
      Promise.reject(new Error("clipboard denied (stub)")),
    );
    stubClipboard(writeText);
    stubServer({
      [SAVE_CODE]: [json(200, { status: "ok", save_code: RESCUED_CODE })],
    });

    await openReplaceConfirm();
    fireEvent.click(screen.getByRole("button", { name: REPLACE_RESCUE_CODE }));
    await screen.findByText(RESCUED_CODE);
    fireEvent.click(screen.getByRole("button", { name: SAVE_CODE_COPY }));

    await waitFor(() => {
      expect(writeText).toHaveBeenCalledWith(RESCUED_CODE);
    });
    // 복사 실패는 코드 표시를 막지 않는다 — 손으로 옮겨 적을 수 있어야 한다.
    expect(screen.getByText(RESCUED_CODE)).toBeTruthy();
  });
});

/** 탈출구가 코드를 못 주는 경우의 공통 계약: 코드 대신 정직한 실패 문구가 뜨고,
 *  갈아타기(redeem)는 그대로 계속 가능하다 — 탈출구 실패가 redeem 을 막지 않는다. */
async function rescueFailureKeepsRedeemUsable(saveCodeReply: StubReply) {
  const calls = stubServer({
    [SAVE_CODE]: [saveCodeReply],
    [REDEEM]: [
      json(200, {
        status: "new",
        npc_id: "surigong",
        reply: OPENING,
        choices: [],
      }),
    ],
  });

  await openReplaceConfirm();
  fireEvent.click(screen.getByRole("button", { name: REPLACE_RESCUE_CODE }));

  // (a) 원인이 무엇이든 사용자에게 남는 사실은 하나 — 코드를 못 받았다.
  await waitFor(() => {
    expect(document.body.textContent).toContain(REPLACE_RESCUE_FAILED);
  });
  expect(screen.queryByRole("button", { name: SAVE_CODE_COPY })).toBeNull();

  // (b) 여기가 계약의 하중을 받는 절반 — 확인 버튼이 살아 있고, 누르면 실제로
  //     redeem 요청이 나가 채팅까지 들어간다.
  const confirm = screen.getByRole("button", {
    name: REPLACE_CONFIRM_OK,
  }) as HTMLButtonElement;
  expect(confirm.disabled).toBe(false);
  fireEvent.click(confirm);

  await screen.findByText(OPENING);
  expect(calls).toEqual([SAVE_CODE, REDEEM]);
}

describe("escape hatch failure branches", () => {
  it("stays honest and keeps redeem usable when there is no session", async () => {
    await rescueFailureKeepsRedeemUsable(
      json(401, { status: "error", message: "no session (stub)" }),
    );
  });

  it("stays honest and keeps redeem usable when the session is banned", async () => {
    await rescueFailureKeepsRedeemUsable(
      json(200, { status: "banned", ban_reason: BAN_REASON }),
    );
  });

  it("stays honest and keeps redeem usable when the server errors", async () => {
    await rescueFailureKeepsRedeemUsable(
      json(503, { status: "error", message: SERVER_ERROR_MESSAGE }),
    );
  });

  it("stays honest and keeps redeem usable when the network is down", async () => {
    await rescueFailureKeepsRedeemUsable("unreachable");
  });
});

describe("dismissing the dialog while the escape hatch is in flight", () => {
  // 회귀: 백드롭에만 가드가 없어서, 탈출구 요청 중에 누르면 다이얼로그는 닫히고
  // busy 만 남았다 — 타이틀 버튼은 이유를 설명하는 화면 없이 죽어 있고, 늦게 온
  // 결과가 다음에 열 때 되살아났다. 취소/백드롭/닫기는 탈출구 상태를 리셋한다는
  // 계약 위반.
  it("keeps the dialog up during the request and starts fresh after it closes", async () => {
    // 응답 큐는 하나뿐 — 두 번째 요청이 나가면 stub 이 던진다.
    const calls = stubServer({
      [SAVE_CODE]: [json(200, { status: "ok", save_code: RESCUED_CODE })],
    });

    await openReplaceConfirm();
    fireEvent.click(screen.getByRole("button", { name: REPLACE_RESCUE_CODE }));
    // 사이에 await 를 두지 않는다 — stub 응답은 마이크로태스크라 아직 오지 않았고,
    // 그래서 이 클릭은 요청이 떠 있는 동안의 백드롭 클릭이다.
    clickBackdrop();

    // (a) 요청 중 백드롭은 취소/확인과 같은 게이트 — 다이얼로그가 남는다.
    expect(screen.getByText(REPLACE_CONFIRM_TITLE)).toBeTruthy();

    // (b) 결과는 여전히 열려 있는 다이얼로그 안에 도착한다.
    await screen.findByText(RESCUED_CODE);

    // (c) 요청이 끝나면 백드롭은 다시 닫는 표면이고, 닫힌 뒤 타이틀은 살아 있다
    //     (죽은 버튼만 남고 이유를 설명할 화면이 없는 상태가 없어야 한다).
    clickBackdrop();
    await waitFor(() => {
      expect(screen.queryByText(REPLACE_CONFIRM_TITLE)).toBeNull();
    });
    const submit = screen.getByRole("button", {
      name: SAVE_CODE_SUBMIT,
    }) as HTMLButtonElement;
    expect(submit.disabled).toBe(false);

    // (d) 다시 열면 처음부터 — 지난 코드가 되살아나지 않고 탈출구는 미실행 상태.
    fireEvent.click(submit);
    await screen.findByText(REPLACE_CONFIRM_TITLE);
    expect(screen.queryByText(RESCUED_CODE)).toBeNull();
    expect(
      screen.getByRole("button", { name: REPLACE_RESCUE_CODE }),
    ).toBeTruthy();
    expect(calls).toEqual([SAVE_CODE]);
  });

  // 위 가드의 뒷면 — 삼켜진 클릭이 아무 반응도 없으면 고장으로 읽힌다.
  // 요청 중 백드롭은 닫는 표면이 아니라는 사실이 화면에도 보여야 한다.
  it("marks the backdrop as busy while the escape hatch is in flight", async () => {
    stubServer({
      [SAVE_CODE]: [json(200, { status: "ok", save_code: RESCUED_CODE })],
    });

    await openReplaceConfirm();
    expect(backdropShowsBusy()).toBe(false);

    // await 없이 — 요청이 아직 떠 있는 시점.
    fireEvent.click(screen.getByRole("button", { name: REPLACE_RESCUE_CODE }));
    expect(backdropShowsBusy()).toBe(true);

    // 요청이 끝나면 표시도 걷힌다 (다시 닫을 수 있는 표면).
    await screen.findByText(RESCUED_CODE);
    expect(backdropShowsBusy()).toBe(false);
  });
});
