// B5 세이브 코드 넛지 — 판정의 순수 함수 + dismiss 플래그 저장소.
//
// 왜 순수 함수인가: 노출 조건은 관측 가능한 세션 상태(누적 턴 수 · 코드 보유 ·
// dismiss)의 함수여야 화면 없이 경계를 pin 할 수 있다. 임계값은 이 파일이 아니라
// tone.ts (프론트 튜닝 값의 단일 홈) 에 산다 — 두 곳 중복 금지.
//
// dismiss 플래그는 localStorage — 기존 재방문 힌트(playedHint.ts)와 같은 저장소,
// 같은 모양이라 가드된 접근 자체는 localFlag.ts 가 소유한다 (중복 금지). 여기 남는
// 것은 이 플래그의 *의미* 뿐. 세션 신원/진행은 절대 여기 두지 않는다 (신원은 쿠키
// 단일 소스).

import { localFlag } from "./localFlag";
import { SAVE_CODE_NUDGE_AFTER_TURNS } from "./tone";

const NUDGE_DISMISSED_KEY = "nanpaseom.saveCodeNudgeDismissed";

const dismissedFlag = localFlag(NUDGE_DISMISSED_KEY);

/** 넛지 판정의 입력 — 전부 관측 가능한 세션 상태.
 *
 *  - hasSaveCode: 이 세션이 유효한 세이브 코드를 갖고 있는가. 진입 응답의
 *    ``has_save_code`` (B2b) 가 그 시점의 진실이고, 세션 도중 발급/회전이
 *    성공하면 클라이언트가 즉시 참으로 갱신한다 (추가 왕복 없음).
 *  - turnCount: 이 세션에서 플레이어가 보낸 누적 턴 수.
 *  - dismissed: 이 기기에서 넛지를 닫은 적이 있는가 (readNudgeDismissed).
 */
export type NudgeState = {
  hasSaveCode: boolean;
  turnCount: number;
  dismissed: boolean;
};

/** 넛지를 지금 노출할 것인가. 순수 — 같은 입력이면 항상 같은 답.
 *
 *  억제가 먼저다: 이미 코드를 가진 세션과 이 기기에서 닫은 적이 있는 플레이어는
 *  턴을 아무리 쌓아도 보지 않는다 (B5). 그 둘을 통과했을 때만 임계값을 잰다. */
export function shouldShowSaveCodeNudge(state: NudgeState): boolean {
  if (state.hasSaveCode) return false;
  if (state.dismissed) return false;
  return state.turnCount >= SAVE_CODE_NUDGE_AFTER_TURNS;
}

/** 이 기기에서 넛지를 닫은 적이 있는가. 저장소를 못 읽으면 false (무해한 재노출). */
export function readNudgeDismissed(): boolean {
  return dismissedFlag.read();
}

/** 넛지를 닫았다고 이 기기에 기록. 저장 실패는 무해 — 다음에 다시 보일 뿐. */
export function markNudgeDismissed(): void {
  dismissedFlag.mark();
}

/** dismiss 기록 해제 — 이 기기에서 *코드 없는 새 세션* 으로 진입했을 때만.
 *  쿠키가 사라져 새 세션이 된 플레이어가 넛지를 영영 못 보는 상태를 막는다. */
export function clearNudgeDismissed(): void {
  dismissedFlag.clear();
}
