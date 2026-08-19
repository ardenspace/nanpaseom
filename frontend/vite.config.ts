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
});
