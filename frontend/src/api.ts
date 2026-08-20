// 공유 API 클라이언트 — fetch + JSON 파싱 + 실패 정규화의 단일 홈
// (conventions Shared Utilities: 두 번째 endpoint 가 생기면 추출).
// 전송 계층만 소유한다 — 화면/상태 로직은 App.tsx, 한글 문구는 tone.ts.

export type ApiResult<T> =
  // 서버가 JSON 으로 응답 — HTTP 상태와 바디를 그대로 전달.
  // status 는 호출측 분기용 (예: /turn 401 → 재bootstrap) — 전송 계층 사실만.
  | { unreachable: false; ok: boolean; status: number; data: T }
  // 네트워크 단절 or 비-JSON 응답 — 호출측은 SERVER_UNREACHABLE 로 노출.
  | { unreachable: true };

export async function postJson<T>(
  path: string,
  body?: unknown,
): Promise<ApiResult<T>> {
  try {
    const res = await fetch(
      path,
      body === undefined
        ? { method: "POST" }
        : {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(body),
          },
    );
    // 503 {status:"error", message} 도 JSON 바디 — ok=false 로 그대로 넘긴다.
    return {
      unreachable: false,
      ok: res.ok,
      status: res.status,
      data: (await res.json()) as T,
    };
  } catch {
    return { unreachable: true };
  }
}
