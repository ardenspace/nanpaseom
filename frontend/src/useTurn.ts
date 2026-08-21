// /turn 요청 1건의 수명 전체 — 전송, 401 자동 복구, 응답의 화면 반영.
// App.tsx 에서 잘라 온 *동작 보존* 추출 (Phase 2 step 5): 분기/문구/상태 전이는
// 원본과 동일하다. 새 동작을 여기서 추가하지 말 것 — 추가는 spec/계약 경유.
//
// 상태는 여전히 App 이 소유한다. 이 훅은 넘겨받은 setter/콜백으로만 화면을 만지고,
// 자체 state 를 갖지 않는다 (busy 는 start/redeem/발급과 공유되는 App 소유 플래그).

import { postJson, type ApiResult } from "./api";
import type { BootstrapData, Choice, TurnData } from "./protocol";
import {
  GENERIC_ERROR,
  SERVER_UNREACHABLE,
  SESSION_RESTORE_FAILED,
} from "./tone";

// 채팅 로그 엔트리 shape 의 단일 홈. 이 훅이 npc/user/warning/error 를 append 하고,
// App 은 렌더 + 재방문 복원 히스토리에만 past 를 붙인다 (훅은 past 를 쓰지 않는다).
// warning/error 는 프레임 깨는 시스템 블록 — NPC 말풍선과 시각적으로 분리 렌더.
export type Msg = {
  kind: "npc" | "user" | "warning" | "error";
  text: string;
  past?: boolean;
};

/** 훅이 App 의 상태를 만지는 유일한 통로. 여기 없는 상태는 훅이 모른다. */
export type TurnDeps = {
  /** 진행 중 요청 잠금 — App 소유 (타이틀/발급 경로와 공유). */
  busy: boolean;
  setBusy: (busy: boolean) => void;
  /** 현재 대화 중인 NPC. 401 재시도도 이 값을 그대로 쓴다 (원본 동작). */
  npcId: string;
  pushMsg: (kind: Msg["kind"], text: string) => void;
  /** 플레이어 턴 1건이 나갔다 — 이 세션의 누적 턴 수를 세는 쪽에 알린다 (B5 넛지).
   *  401 복구의 *재시도* 는 같은 턴이므로 다시 세지 않는다. 새 세션으로 갈아탄
   *  경우의 리셋은 enterChat 소유 (진입이 카운터의 홈). */
  onTurnSent: () => void;
  /** 진입 응답이 알려준 코드 보유 상태 (B2b) — 그 시점의 진실이므로 그대로 반영한다.
   *  401 복구가 화면을 유지하는 resumed 분기에서도 이 값만은 서버 권한이다: 쿠키가
   *  가리키는 세션이 바뀌었을 수 있고(다른 탭의 코드 사용 등), 코드를 가진 세션에
   *  넛지를 노출하는 것은 B5 위반이다. 히스토리(표시 상태)는 계속 버린다. */
  onEntrySaveCode: (hasSaveCode: boolean) => void;
  setChoices: (choices: Choice[]) => void;
  /** 차단 화면 전환 — 사유 표시 + 선택지 봉인 + 화면 교체. */
  showBanned: (reason: string) => void;
  /** new/resumed bootstrap 응답 → 채팅 진입 (App 소유, redeem 과 공유). */
  enterChat: (data: BootstrapData) => void;
};

export function useTurn(deps: TurnDeps): {
  sendTurn: (text: string) => Promise<void>;
} {
  const {
    busy,
    setBusy,
    npcId,
    pushMsg,
    onTurnSent,
    onEntrySaveCode,
    setChoices,
    showBanned,
    enterChat,
  } = deps;

  /** turn 응답을 화면에 반영. 401 처리(자동 재bootstrap)는 sendTurn 소유 —
   *  여기 도달한 !ok 는 그 외 오류다. */
  function applyTurn(r: ApiResult<TurnData>) {
    if (r.unreachable) {
      pushMsg("error", SERVER_UNREACHABLE);
      return;
    }
    if (!r.ok) {
      pushMsg("error", GENERIC_ERROR);
      return;
    }
    const data = r.data;
    if (data.kind === "ban") {
      // 즉시 차단 화면 — 입력/선택지 전부 봉인.
      showBanned(data.reply ?? "");
    } else if (data.kind === "warning") {
      // pinned 규칙: warning 은 UI 모드 불변 — 이전 npc choices 유지.
      pushMsg("warning", data.reply ?? "");
    } else {
      pushMsg("npc", data.reply ?? "");
      // 빈 choices → 자유 입력 모드 (렌더가 choices.length 로 분기).
      setChoices(data.choices ?? []);
    }
  }

  async function sendTurn(text: string) {
    if (busy) return;
    setBusy(true);
    pushMsg("user", text);
    onTurnSent();
    // 신원은 쿠키가 전담 — 본문은 {npc_id, player_input} 뿐 (B1/B6).
    const r = await postJson<TurnData>("/turn", {
      npc_id: npcId,
      player_input: text,
    });
    if (!r.unreachable && r.status === 401) {
      // 서버가 세션을 모름(쿠키 소멸 등) — recoverable. 자동 재bootstrap 1회.
      // 쿠키는 편의, 코드가 열쇠 — 세션이 없으면 새로 시작이 맞다.
      const b = await postJson<BootstrapData>("/session/bootstrap");
      if (b.unreachable) {
        pushMsg("error", SERVER_UNREACHABLE);
      } else if (b.data.status === "banned") {
        showBanned(b.data.ban_reason ?? "");
      } else if (b.data.status === "resumed") {
        // 화면은 그대로 두지만(히스토리는 버린다) 코드 보유 상태만은 이 응답이
        // 권한이다 — 쿠키가 코드를 가진 세션으로 재바인딩됐을 수 있다 (B2b/B5).
        onEntrySaveCode(b.data.has_save_code === true);
        // 세션 복구됨 — 보류된 턴을 정확히 1회 재시도. 또 401 이면
        // 재bootstrap 없이 정직하게 알리고 멈춘다 (무한 루프 금지).
        const retry = await postJson<TurnData>("/turn", {
          npc_id: npcId,
          player_input: text,
        });
        if (!retry.unreachable && retry.status === 401) {
          pushMsg("error", SESSION_RESTORE_FAILED);
        } else {
          applyTurn(retry);
        }
      } else if (b.data.status === "new") {
        // 서버에 이 기기의 세션이 없었음 — 새 세션의 오프닝으로 진입.
        // 보내려던 입력은 사라진 세션 소속이라 재전송하지 않는다.
        enterChat(b.data);
      } else {
        // 503 {status:"error", message} — 서버 문구 우선.
        pushMsg("error", b.data.message || GENERIC_ERROR);
      }
    } else {
      applyTurn(r);
    }
    setBusy(false);
  }

  return { sendTurn };
}
