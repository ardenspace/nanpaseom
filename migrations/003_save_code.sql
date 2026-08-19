-- B5: 세이브 코드 — sessions 에 save_code 컬럼 *하나만* 추가.
--
-- - VARCHAR(9): XXXX-XXXX (하이픈 포함 9자, app/save_code.py 형식 정의와 일치)
-- - UNIQUE: 코드 → 세션 1:1 (NULL 은 다중 허용 — 코드 미발급 세션)
-- - NULL 허용 + 기본값 없음: 기존 row 무손실 적용 (001/002 불변)
-- - choices 복원은 기존 chat_logs.reply_json_raw 로 충분 — 신규 테이블/추가 컬럼 없음
-- - idempotent (IF NOT EXISTS) — 테스트 fixture 가 매번 재적용
ALTER TABLE sessions ADD COLUMN IF NOT EXISTS save_code VARCHAR(9);
CREATE UNIQUE INDEX IF NOT EXISTS idx_sessions_save_code ON sessions (save_code);
