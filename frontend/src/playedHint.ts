// 재방문 *힌트* — 신원 권한은 어디까지나 서버 쿠키. localStorage 는
// 타이틀 버튼 라벨/카피만 바꾼다 (bootstrap 결과가 항상 진실).
//
// 저장소 접근의 가드는 localFlag.ts 소유 (넛지 dismiss 플래그와 같은 메커니즘).
// 여기 남는 것은 이 플래그의 *의미* — 어떤 키가 무엇을 뜻하는가뿐이다.

import { localFlag } from "./localFlag";

const PLAYED_HINT_KEY = "nanpaseom.played";

const playedFlag = localFlag(PLAYED_HINT_KEY);

/** 이 기기에서 플레이한 적이 있는가. 저장소를 못 읽으면 false (힌트 없음으로 취급). */
export function readPlayedHint(): boolean {
  return playedFlag.read();
}

/** 플레이 이력을 이 기기에 기록. 실패는 무해 — 다음 방문에 [시작하기] 로 보일 뿐. */
export function markPlayedHint() {
  playedFlag.mark();
}
