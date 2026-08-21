// 서버 응답 wire shape 의 단일 홈 — B2 bootstrap / B1 turn.
// 전송 메커니즘은 api.ts, 화면/상태 로직은 App.tsx 소유.

export type Choice = { tone: string; text: string };

// B2 bootstrap 응답 — 분기는 status 로 (new / resumed / banned / error).
// 신원(세션)은 본문에 없다 — HttpOnly 쿠키로만 오간다 (B6).
export type BootstrapData = {
  status: string;
  npc_id?: string;
  reply?: string;
  choices?: Choice[];
  history?: { role: string; content: string }[];
  // B2b — 이 세션이 유효한 세이브 코드를 갖고 있는가. 진입 성공(new/resumed)
  // 응답에만 실린다 (banned/503 에는 없음) — 넛지 노출의 권위 (B5).
  has_save_code?: boolean;
  ban_reason?: string;
  message?: string;
};

// B3 세이브 코드 발급 응답 — 분기는 status 로 (ok / banned / error).
// 회전(POST /save-code/rotate) 도 같은 shape 를 쓴다 (새 코드냐 기존 코드냐만 다름).
export type SaveCodeIssueData = {
  status: string;
  save_code?: string;
  ban_reason?: string;
  message?: string;
};

// B3 redeem 응답 — bootstrap 과 wire shape 를 의도적으로 공유한다
// (성공 시 채팅 진입 렌더 로직 재사용). 별칭으로 그 의도를 기록.
export type RedeemData = BootstrapData;

// B1 turn 응답 — 분기는 kind 로 (npc / warning / ban).
export type TurnData = {
  kind: string;
  reply?: string;
  choices?: Choice[];
};
