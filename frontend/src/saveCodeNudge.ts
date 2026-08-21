// B5 세이브 코드 넛지 — 판정의 순수 함수 + dismiss 플래그 저장소.
//
// Phase 4 step 1 (계약 pin) 에서는 *이름/모듈/시그니처만* 고정한다. 본문은 전부
// 미구현이며 호출 즉시 던진다 — saveCodeNudge.test.ts 가 이 시그니처에 대고
// 계약을 pin 하고, 구현은 다음 스텝이 채운다. 여기에 로직을 두는 것이 이 스텝의
// 일이 아니라는 사실을 코드로 남긴다.
//
// 왜 순수 함수인가: 노출 조건은 관측 가능한 세션 상태(누적 턴 수 · 코드 보유 ·
// dismiss)의 함수여야 화면 없이 경계를 pin 할 수 있다. 임계값은 이 파일이 아니라
// tone.ts (프론트 튜닝 값의 단일 홈) 에 산다 — 두 곳 중복 금지.
//
// dismiss 플래그는 localStorage — 기존 재방문 힌트(playedHint.ts)와 같은 저장소,
// 같은 모양. 세션 신원/진행은 절대 여기 두지 않는다 (신원은 쿠키 단일 소스).

const NOT_IMPLEMENTED = "saveCodeNudge: not implemented (Phase 4 step 1 pins the signature only)";

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

/** 넛지를 지금 노출할 것인가. 순수 — 같은 입력이면 항상 같은 답. */
export function shouldShowSaveCodeNudge(_state: NudgeState): boolean {
  throw new Error(NOT_IMPLEMENTED);
}

/** 이 기기에서 넛지를 닫은 적이 있는가. 저장소를 못 읽으면 false (무해한 재노출). */
export function readNudgeDismissed(): boolean {
  throw new Error(NOT_IMPLEMENTED);
}

/** 넛지를 닫았다고 이 기기에 기록. 저장 실패는 무해 — 다음에 다시 보일 뿐. */
export function markNudgeDismissed(): void {
  throw new Error(NOT_IMPLEMENTED);
}

/** dismiss 기록 해제 — 이 기기에서 *코드 없는 새 세션* 으로 진입했을 때만.
 *  쿠키가 사라져 새 세션이 된 플레이어가 넛지를 영영 못 보는 상태를 막는다. */
export function clearNudgeDismissed(): void {
  throw new Error(NOT_IMPLEMENTED);
}
