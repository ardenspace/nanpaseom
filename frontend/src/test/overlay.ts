// 공유 테스트 헬퍼 — 오버레이 백드롭 클릭.
//
// 백드롭은 접근 가능한 이름도 role 도 없는 표면이라 RTL 질의로 잡을 수 없다.
// 두 오버레이(타이틀의 대체 확인, 채팅의 세이브 코드 패널)가 같은 클래스를 쓰고
// 같은 계약(요청 중에는 닫히지 않는다)을 pin 하므로 여기 한 곳에 둔다.

import { fireEvent } from "@testing-library/react";

/** 화면에 떠 있는 오버레이의 백드롭을 클릭한다. 없으면 즉시 실패. */
export function clickBackdrop() {
  const backdrop = document.querySelector(".overlay__backdrop");
  if (!backdrop) throw new Error("no overlay backdrop on screen");
  fireEvent.click(backdrop);
}
