// tone — frontend-local 사용자 노출 시스템 문구의 *단일 홈*.
// scripts/check_no_hardcoded_dialogue.py 의 한글 리터럴 스캔에서 유일한 예외 파일.
//
// 원칙 (mapping-spec 시스템 톤):
// - 정직한 인프라 언어. NPC 디제틱 말투(세계 안 목소리) 절대 금지 —
//   NPC 텍스트는 전부 서버(yaml → 빌더)에서 온다.
// - 시스템 문구 추가는 반드시 이 파일에 named constant 로.

/** 서버 연결 실패 (fetch 자체가 실패했을 때). */
export const SERVER_UNREACHABLE =
  "서버에 연결할 수 없습니다. 네트워크를 확인하고 잠시 후 다시 시도해 주세요.";

/** 그 외 예상 못 한 오류의 공용 폴백. */
export const GENERIC_ERROR =
  "오류가 발생했습니다. 잠시 후 다시 시도해 주세요.";

/** 타이틀 — 시작 버튼. */
export const START_BUTTON = "시작하기";

/** 타이틀 — 연결(bootstrap) 진행 중 버튼 라벨. */
export const CONNECTING = "연결 중…";

/** 타이틀 — 세이브 코드 진입점 (Phase 3 예정, 지금은 비활성 자리표시). */
export const SAVE_CODE_ENTRY_DISABLED = "세이브 코드로 이어하기 (준비 중)";

/** 채팅 — 자유 입력 placeholder. 정직한 인프라 언어 (디제틱 문구 금지). */
export const FREE_INPUT_PLACEHOLDER = "메시지를 입력하세요";

/** 채팅 — 자유 입력 전송 버튼. */
export const SEND_BUTTON = "보내기";

/** 차단 화면 헤딩 — 상세 사유(ban_reason)는 서버가 준다. */
export const BANNED_TITLE = "접속이 차단되었습니다";
