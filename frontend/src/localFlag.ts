// 기기 로컬 *불리언 플래그* 한 벌 — localStorage 접근을 가드로 감싸 절대 던지지 않는다.
//
// 프라이버시 모드 / 저장소 차단 브라우저에서 localStorage 접근은 throw 한다. 화면이
// 플래그 하나 때문에 깨지면 안 되므로 읽기 실패는 false(=기록 없음), 쓰기/삭제 실패는
// 무시가 계약이다 — 최악의 결과는 힌트/넛지가 한 번 더 보이는 무해한 재노출뿐이다.
//
// 이 파일은 저장 *메커니즘* 만 안다. 어떤 키가 무엇을 뜻하는지는 각 플래그 모듈이
// 소유한다 (playedHint.ts, saveCodeNudge.ts). 세션 신원/진행은 절대 여기 두지 않는다
// — 신원은 쿠키 단일 소스.

/** 키 하나에 묶인 가드된 불리언 플래그. */
export type LocalFlag = {
  /** 이 기기에 플래그가 켜져 있는가. 읽지 못하면 false. */
  read: () => boolean;
  /** 플래그를 켠다. 저장 실패는 무해 — 던지지 않는다. */
  mark: () => void;
  /** 플래그를 지운다. 삭제 실패는 무해 — 던지지 않는다. */
  clear: () => void;
};

export function localFlag(key: string): LocalFlag {
  return {
    read() {
      try {
        return localStorage.getItem(key) === "1";
      } catch {
        return false;
      }
    },
    mark() {
      try {
        localStorage.setItem(key, "1");
      } catch {
        // 무시 — 기록되지 않았을 뿐 진행에는 영향이 없다.
      }
    },
    clear() {
      try {
        localStorage.removeItem(key);
      } catch {
        // 무시 — 플래그가 남아 있을 뿐 진행에는 영향이 없다.
      }
    },
  };
}
