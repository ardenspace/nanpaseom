/// <reference types="vitest/config" />
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// dev 프록시 타깃 — 백엔드 dev 포트 8765 (머신 포트 점유표와 안 겹치는 값).
// 백엔드 dev 실행: .venv/bin/uvicorn app.api.main:app --port 8765
// prod 에서는 FastAPI 가 frontend/dist 를 same-origin 서빙하므로 프록시 불필요.
const BACKEND = "http://127.0.0.1:8765";

export default defineConfig({
  plugins: [react()],
  server: {
    // Vite 기본 포트 5173 (머신 점유표와 충돌 없음).
    // 쿠키(session_uuid)는 same-origin 프록시 경유라 그대로 전달된다.
    proxy: {
      "/session": BACKEND,
      "/turn": BACKEND,
      "/save-code": BACKEND,
    },
  },
  build: {
    outDir: "dist",
  },
  // 프론트 테스트 러너 — vitest. 별도 config 파일을 두지 않는 이유는
  // 프로덕션 빌드와 *같은* vite 파이프라인(alias/plugin/tsconfig)에서 돌아야
  // 테스트가 실제 번들과 어긋나지 않기 때문.
  test: {
    // jsdom — React 19 + testing-library 조합에서 가장 호환이 검증된 DOM 구현.
    // playedHint 의 localStorage, 이후 페이즈의 다이얼로그 렌더가 모두 필요로 한다.
    environment: "jsdom",
    // 테스트는 소스 옆에 colocate (src 안이라 tsc 타입체크도 같이 받는다).
    include: ["src/**/*.test.ts", "src/**/*.test.tsx"],
    setupFiles: ["src/test/setup.ts"],
    // globals 미사용 — describe/it/expect 는 각 파일에서 명시 import.
    globals: false,
  },
});
