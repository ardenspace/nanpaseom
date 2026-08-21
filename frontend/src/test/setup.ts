// vitest 전역 setup — 모든 테스트 파일이 자동으로 통과하는 지점.
// vite.config.ts 의 test.setupFiles 가 이 파일을 가리킨다.
//
// 여기서 하는 일은 두 가지: (1) 런타임 환경 보정, (2) 테스트 간 격리.
// 헬퍼/픽스처는 각 테스트가 필요할 때 명시 import 하는 쪽이 추적 가능하므로
// 여기에 두지 않는다.

import { afterEach } from "vitest";
import { cleanup } from "@testing-library/react";

// --- (1) 환경 보정: jsdom 스토리지 되찾기 ---------------------------------
// Node 22+ 부터 globalThis 에 내장 web storage(localStorage/sessionStorage)가
// 이미 존재한다. vitest 의 jsdom 환경은 *이미 global 에 있는 키* 를 덮어쓰지
// 않으므로(populateGlobal 의 키 필터), 테스트 안에서 참조되는 localStorage 가
// jsdom 것이 아니라 동작하지 않는 node 쪽 껍데기로 잡힌다 — setItem 은 조용히
// 실패하고 clear 는 아예 없다. 그러면 브라우저에서 도는 프로덕션 코드와
// 테스트가 어긋난다.
// vitest 는 jsdom 인스턴스를 globalThis.jsdom 으로 노출하므로 거기서 되돌린다.
// vitest 가 이 갭을 메우면 아래 블록은 no-op 이 되고, 그때 지우면 된다.
type JsdomHandle = { window: Window & typeof globalThis };
const jsdomHandle = (globalThis as { jsdom?: JsdomHandle }).jsdom;
if (jsdomHandle) {
  for (const key of ["localStorage", "sessionStorage"] as const) {
    if (globalThis[key] !== jsdomHandle.window[key]) {
      Object.defineProperty(globalThis, key, {
        value: jsdomHandle.window[key],
        configurable: true,
        writable: true,
      });
    }
  }
}

// --- (2) 테스트 간 격리 ---------------------------------------------------
afterEach(() => {
  // globals:false 라 testing-library 의 auto-cleanup 이 스스로 등록되지 않는다.
  // 렌더된 컴포넌트가 다음 테스트로 새지 않도록 여기서 명시 해제.
  cleanup();
  // 스토리지는 한 파일 안의 모든 테스트가 공유한다 — 힌트류 상태가 테스트
  // 순서에 따라 결과를 바꾸지 않게 매 테스트 후 비운다.
  localStorage.clear();
  sessionStorage.clear();
});
