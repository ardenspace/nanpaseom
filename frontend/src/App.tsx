// 스캐폴드 검증용 최소 셸 — 실제 화면(타이틀/채팅)은 다음 스텝.
// "Still Here" 는 게임 타이틀 (NPC 대사 아님). 한글 시스템 문구는 tone.ts 에만.

export default function App() {
  return (
    <main className="shell">
      <h1 className="shell__title">Still Here</h1>
      <p className="shell__hint">nanpaseom frontend scaffold</p>
    </main>
  );
}
