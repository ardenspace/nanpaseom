// 재방문 *힌트* — 신원 권한은 어디까지나 서버 쿠키. localStorage 는
// 타이틀 버튼 라벨/카피만 바꾼다 (bootstrap 결과가 항상 진실).

const PLAYED_HINT_KEY = "nanpaseom.played";

export function readPlayedHint(): boolean {
  try {
    return localStorage.getItem(PLAYED_HINT_KEY) === "1";
  } catch {
    return false; // 프라이버시 모드 등 — 힌트 없음으로 취급.
  }
}

export function markPlayedHint() {
  try {
    localStorage.setItem(PLAYED_HINT_KEY, "1");
  } catch {
    // 힌트 저장 실패는 무해 — 다음 방문에 [시작하기] 로 보일 뿐.
  }
}
