// 세이브 코드 복사 버튼 — 채팅의 발급 패널과 타이틀의 대체 확인 탈출구가 공유한다.
// (conventions: 같은 로직이 두 번째로 나타나면 공용 홈으로 승격.)
//
// 복사 여부는 이 버튼이 스스로 소유한다 — 복사했다는 사실은 화면에 뜬 코드
// 하나에만 붙기 때문. 코드가 바뀌면(회전 등) 호출측이 key={code} 로 리셋한다.

import { useState } from "react";
import { SAVE_CODE_COPIED, SAVE_CODE_COPY } from "./tone";

export default function CopyCodeButton({ code }: { code: string }) {
  const [copied, setCopied] = useState(false);

  function copy() {
    // clipboard API 는 비보안 컨텍스트에 없을 수 있다 — 실패해도 무해
    // (코드 텍스트는 user-select: all 로 직접 복사 가능).
    void navigator.clipboard?.writeText(code).then(
      () => setCopied(true),
      () => {},
    );
  }

  return (
    <button className="btn btn--primary" type="button" onClick={copy}>
      {copied ? SAVE_CODE_COPIED : SAVE_CODE_COPY}
    </button>
  );
}
