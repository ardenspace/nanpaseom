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

/** 타이틀 — 재방문 힌트가 있을 때의 시작 버튼 (서버가 실제 세션 유무를 판정). */
export const CONTINUE_BUTTON = "이어하기";

/** 타이틀 — 재방문 힌트 안내. localStorage 힌트 기반이라 단정하지 않는 문구. */
export const RETURNING_NOTE = "이전 세션이 남아 있으면 이어서 계속됩니다";

/** 타이틀 — 연결(bootstrap) 진행 중 버튼 라벨. */
export const CONNECTING = "연결 중…";

/** 타이틀 — 세이브 코드 입력 진입 버튼. */
export const SAVE_CODE_ENTRY = "세이브 코드로 이어하기";

/** 타이틀 — 세이브 코드 입력 필드 placeholder (형식 안내, A-Z·2-9). */
export const SAVE_CODE_INPUT_PLACEHOLDER = "XXXX-XXXX";

/** 타이틀 — 세이브 코드 제출 버튼. */
export const SAVE_CODE_SUBMIT = "불러오기";

/** 타이틀 — 세이브 코드 입력 취소 버튼. */
export const SAVE_CODE_CANCEL = "취소";

/** 타이틀 — redeem 실패 폴백 (서버 message 가 있으면 그쪽 우선). */
export const SAVE_CODE_ERROR_FALLBACK =
  "세이브 코드를 확인하지 못했습니다. 잠시 후 다시 시도해 주세요.";

/** 타이틀 — 밴된 세션의 코드 redeem 결과 안내. 재바인딩이 없었으므로
 *  이 기기의 진행은 무사하다는 사실을 함께 말한다 (정직한 인프라 언어). */
export const SAVE_CODE_BANNED_NOTE =
  "이 세이브 코드의 세션은 차단된 상태라 불러올 수 없습니다. 이 기기의 진행은 그대로 유지됩니다.";

/** 대체 확인 다이얼로그 — 제목. */
export const REPLACE_CONFIRM_TITLE = "진행 대체 확인";

/** 대체 확인 다이얼로그 — 본문. 항상 표시 (쿠키는 HttpOnly 라 클라이언트가
 *  세션 유무를 알 수 없음). 조건부 어법으로 새 기기에서도 정직하되,
 *  "이 기기의 진행이 대체됩니다" 취지는 분명히 (spec 고정 사항). */
export const REPLACE_CONFIRM_BODY =
  "이 기기에 남아 있는 진행이 있다면, 세이브 코드를 불러올 때 코드의 세션으로 대체됩니다. 계속할까요?";

/** 대체 확인 다이얼로그 — 진행(대체) 버튼. */
export const REPLACE_CONFIRM_OK = "대체하고 이어하기";

/** 대체 확인 다이얼로그 — 취소 버튼 (이 기기의 진행 유지). */
export const REPLACE_CONFIRM_CANCEL = "돌아가기";

/** 채팅 — 헤더의 세이브 코드 발급 버튼. */
export const SAVE_CODE_BUTTON = "세이브 코드";

/** 채팅 — 발급된 코드 표시 패널 제목. */
export const SAVE_CODE_ISSUED_TITLE = "세이브 코드";

/** 채팅 — 발급된 코드 안내. 재발급해도 같은 코드 (idempotent 사실 전달). */
export const SAVE_CODE_ISSUED_NOTE =
  "이 코드를 적어 두면 다른 기기에서 이어할 수 있습니다. 다시 확인해도 코드는 바뀌지 않습니다.";

/** 채팅 — 코드 패널에서 새 코드로 갈아타는(회전) 진입 버튼. */
export const SAVE_CODE_ROTATE = "새 코드로 바꾸기";

/** 채팅 — 회전 UI 경고. 회전의 대가(이전 코드 무효화)를 누르기 전에 명시한다.
 *  정직한 인프라 언어 — 되돌릴 수 없다는 사실을 숨기지 않는다. */
export const SAVE_CODE_ROTATE_WARNING =
  "새 코드를 발급하면 이전 코드는 더 이상 쓸 수 없습니다. 적어 둔 옛 코드는 버려 주세요.";

/** 회전 도입 전 안내에 있던 폐기된 주장 — 회전이 생긴 이상 거짓이므로 어떤
 *  사용자 노출 문구에도 남아 있으면 안 된다. 테스트가 이 상수로 그 부재를 pin 한다
 *  (문구 회귀 가드 — 값 자체는 화면에 렌더되지 않는다). */
export const RETIRED_IMMUTABLE_CODE_CLAIM = "다시 확인해도 코드는 바뀌지 않습니다";

/** 채팅 — 코드 복사 버튼 / 복사 완료 라벨. */
export const SAVE_CODE_COPY = "코드 복사";
export const SAVE_CODE_COPIED = "복사되었습니다";

/** 채팅 — 코드 패널 닫기 버튼. */
export const SAVE_CODE_CLOSE = "닫기";

/** 채팅 — 재방문 복원 시 지난 대화와 새 턴을 가르는 구분선 라벨. */
export const RESUME_DIVIDER = "여기까지 지난 대화";

/** 채팅 — 자유 입력 placeholder. 정직한 인프라 언어 (디제틱 문구 금지). */
export const FREE_INPUT_PLACEHOLDER = "메시지를 입력하세요";

/** 채팅 — 자유 입력 전송 버튼. */
export const SEND_BUTTON = "보내기";

/** 채팅 — /turn 401 후 자동 재bootstrap 까지 했는데도 턴이 다시 거부됐을 때.
 *  재시도는 정확히 1회(무한 루프 금지) — 이후는 정직하게 알리고 멈춘다. */
export const SESSION_RESTORE_FAILED =
  "세션을 복구하지 못했습니다. 페이지를 새로고침한 뒤 다시 시도해 주세요.";

/** 차단 화면 헤딩 — 상세 사유(ban_reason)는 서버가 준다. */
export const BANNED_TITLE = "접속이 차단되었습니다";
