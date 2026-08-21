// 공유 테스트 헬퍼 — 컴포넌트 테스트용 stub 서버 (fetch 대역).
//
// App 컴포넌트 테스트 네 파일이 각자 fetch stub 을 길렀던 것을 하나로 모은 것.
// 여기 있는 것은 배관뿐이다: 무엇을 단언하느냐는 각 테스트 파일이 소유한다.
//
// 공통 성질 (네 파일의 합집합):
//  - 경로별 라우트. 모르는 경로는 던진다 = 테스트가 모르는 요청이 조용히 통과 못 함.
//  - 실제 호출 경로 순서를 calls 배열로 돌려준다 (시퀀스 단언용).
//  - 큐가 비었을 때의 정책을 서버 단위로 고른다 (기본: 던짐).
//  - 네트워크 단절(fetch reject)과 비-2xx 상태를 둘 다 표현한다.
//
// 응답에 헤더는 없다 — 세션 쿠키는 HttpOnly 라 클라이언트가 읽지 않고,
// api.ts 도 res.ok / res.status / res.json() 만 본다.

import { vi } from "vitest";

/** 한 번의 응답: JSON 바디이거나 네트워크 단절. */
export type StubReply = { status: number; body: unknown } | "unreachable";

/** 라우트 구현 — 요청마다 응답 하나를 고른다 (요청 바디를 볼 수 있다). */
export type StubRoute = (init?: RequestInit) => StubReply;

/**
 * 경로 하나에 붙일 수 있는 것:
 *  - StubReply     : 항상 같은 응답
 *  - StubReply[]   : 순서대로 소비되는 큐 (소진 시 whenExhausted 정책)
 *  - StubRoute     : 요청을 보고 직접 고르는 함수
 */
export type StubRouteSpec = StubReply | StubReply[] | StubRoute;

export const json = (status: number, body: unknown): StubReply => ({
  status,
  body,
});

export const jsonOk = (body: unknown): StubReply => json(200, body);

/** 순서대로 소비하되 *마지막 응답이 계속 남는* 큐. 한 테스트 안에서
 *  재진입(언마운트 후 재렌더)을 흉내낼 때 쓴다. */
export function sticky(replies: StubReply[]): StubRoute {
  const queue = [...replies];
  return () => {
    if (queue.length === 0) throw new Error("sticky() needs at least one reply");
    return queue.length > 1 ? (queue.shift() as StubReply) : queue[0];
  };
}

function toRoute(
  path: string,
  spec: StubRouteSpec,
  whenExhausted: StubReply | undefined,
): StubRoute {
  if (typeof spec === "function") return spec;
  if (!Array.isArray(spec)) return () => spec;
  const queue = [...spec];
  return () => {
    const next = queue.shift();
    if (next !== undefined) return next;
    if (whenExhausted !== undefined) return whenExhausted;
    throw new Error(`stub server: reply queue exhausted for ${path}`);
  };
}

export type StubServerOptions = {
  /** 큐가 소진된 뒤의 응답. 생략하면 던진다 (여분 호출 = 즉시 실패).
   *  응답을 주는 쪽을 고르면 클라이언트가 그 응답을 어떻게 다루는지까지
   *  시퀀스 단언으로 잴 수 있다. */
  whenExhausted?: StubReply;
};

/**
 * 전역 fetch 를 경로 라우팅 stub 으로 바꾼다. 해제는 호출측의
 * vi.unstubAllGlobals() (afterEach).
 *
 * @returns 실제로 요청된 경로들 (호출 순서 그대로).
 */
export function stubServer(
  routes: Record<string, StubRouteSpec>,
  options: StubServerOptions = {},
): string[] {
  const calls: string[] = [];
  const compiled = new Map<string, StubRoute>(
    Object.entries(routes).map(([path, spec]) => [
      path,
      toRoute(path, spec, options.whenExhausted),
    ]),
  );

  const fetchMock = vi.fn(
    async (input: RequestInfo | URL, init?: RequestInit) => {
      const path = String(input);
      calls.push(path);
      const route = compiled.get(path);
      if (!route) throw new Error(`stub server: unstubbed request path ${path}`);
      const next = route(init);
      if (next === "unreachable") throw new Error("network down (stub)");
      return {
        ok: next.status >= 200 && next.status < 300,
        status: next.status,
        json: async () => next.body,
      } as Response;
    },
  );
  vi.stubGlobal("fetch", fetchMock);
  return calls;
}
