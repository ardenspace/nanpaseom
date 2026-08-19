// 서버 응답 wire shape 의 단일 홈 — B2 bootstrap / B1 turn.
// 전송 메커니즘은 api.ts, 화면/상태 로직은 App.tsx 소유.

export type Choice = { tone: string; text: string };

// B2 bootstrap 응답 — 분기는 status 로 (new / resumed / banned / error).
export type BootstrapData = {
  status: string;
  session_uuid?: string;
  npc_id?: string;
  reply?: string;
  choices?: Choice[];
  history?: { role: string; content: string }[];
  ban_reason?: string;
  message?: string;
};

// B1 turn 응답 — 분기는 kind 로 (npc / warning / ban).
export type TurnData = {
  kind: string;
  reply?: string;
  choices?: Choice[];
};
