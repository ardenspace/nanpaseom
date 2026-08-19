// 타이틀 + 채팅 + 차단 화면 — Phase 1 step 4.
// 규약: 한글 시스템 문구는 전부 tone.ts 상수. NPC 텍스트는 전부 서버에서 온다.
// "Still Here" 는 게임 타이틀(영문)이라 마크업에 둔다.

import { Fragment, useEffect, useRef, useState } from "react";
import { postJson } from "./api";
import { markPlayedHint, readPlayedHint } from "./playedHint";
import type { BootstrapData, Choice, TurnData } from "./protocol";
import {
  BANNED_TITLE,
  CONNECTING,
  CONTINUE_BUTTON,
  FREE_INPUT_PLACEHOLDER,
  GENERIC_ERROR,
  RESUME_DIVIDER,
  RETURNING_NOTE,
  SAVE_CODE_ENTRY_DISABLED,
  SEND_BUTTON,
  SERVER_UNREACHABLE,
  START_BUTTON,
} from "./tone";

// warning/error 는 프레임 깨는 시스템 블록 — NPC 말풍선과 시각적으로 분리 렌더.
// past = 재방문 복원된 지난 대화 (히스토리 prefix 에만 붙는다) — 흐리게 렌더.
type Msg = {
  kind: "npc" | "user" | "warning" | "error";
  text: string;
  past?: boolean;
};

type Screen = "title" | "chat" | "banned";

// 클라이언트측 여유 상한 — 실제 제한은 서버(Layer 1)가 소유.
const MAX_INPUT_LEN = 500;

export default function App() {
  const [screen, setScreen] = useState<Screen>("title");
  const [titleError, setTitleError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [messages, setMessages] = useState<Msg[]>([]);
  const [choices, setChoices] = useState<Choice[]>([]);
  const [sessionUuid, setSessionUuid] = useState("");
  const [npcId, setNpcId] = useState("");
  const [banReason, setBanReason] = useState("");
  const [draft, setDraft] = useState("");
  const [spriteVisible, setSpriteVisible] = useState(true);
  // 재방문 힌트는 타이틀 첫 렌더 시점에 한 번만 읽는다 (라벨 용도).
  const [playedHint] = useState(readPlayedHint);
  const logEndRef = useRef<HTMLDivElement>(null);
  const firstScrollRef = useRef(true);

  useEffect(() => {
    if (messages.length === 0) return;
    // 첫 진입(특히 resumed 히스토리)은 즉시 점프 — 이후 새 메시지만 부드럽게.
    logEndRef.current?.scrollIntoView({
      behavior: firstScrollRef.current ? "auto" : "smooth",
    });
    firstScrollRef.current = false;
  }, [messages, busy]);

  function pushMsg(kind: Msg["kind"], text: string) {
    setMessages((prev) => [...prev, { kind, text }]);
  }

  async function start() {
    if (busy) return;
    setBusy(true);
    setTitleError(null);
    const r = await postJson<BootstrapData>("/session/bootstrap");
    if (r.unreachable) {
      setTitleError(SERVER_UNREACHABLE);
    } else {
      const data = r.data;
      if (data.status === "banned") {
        markPlayedHint(); // 밴 세션도 플레이 이력 — 재방문 라벨 유지.
        setBanReason(data.ban_reason ?? "");
        setScreen("banned");
      } else if (data.status === "new") {
        markPlayedHint();
        setSessionUuid(data.session_uuid ?? "");
        setNpcId(data.npc_id ?? "");
        setMessages([{ kind: "npc", text: data.reply ?? "" }]);
        setChoices(data.choices ?? []);
        setScreen("chat");
      } else if (data.status === "resumed") {
        markPlayedHint();
        setSessionUuid(data.session_uuid ?? "");
        setNpcId(data.npc_id ?? "");
        setMessages(
          (data.history ?? []).map(
            (h): Msg => ({
              kind: h.role === "user" ? "user" : "npc",
              text: h.content,
              past: true, // 지난 대화 — 새 턴과 시각적으로 구분.
            }),
          ),
        );
        setChoices(data.choices ?? []);
        setScreen("chat");
      } else {
        // 503 {status:"error", message} — 타이틀에 남아 재시도 가능.
        setTitleError(data.message || GENERIC_ERROR);
      }
    }
    setBusy(false);
  }

  async function sendTurn(text: string) {
    if (busy) return;
    setBusy(true);
    pushMsg("user", text);
    const r = await postJson<TurnData>("/turn", {
      session_uuid: sessionUuid,
      npc_id: npcId,
      player_input: text,
    });
    if (r.unreachable) {
      pushMsg("error", SERVER_UNREACHABLE);
    } else if (!r.ok) {
      pushMsg("error", GENERIC_ERROR);
    } else {
      const data = r.data;
      if (data.kind === "ban") {
        // 즉시 차단 화면 — 입력/선택지 전부 봉인.
        setBanReason(data.reply ?? "");
        setChoices([]);
        setScreen("banned");
      } else if (data.kind === "warning") {
        // pinned 규칙: warning 은 UI 모드 불변 — 이전 npc choices 유지.
        pushMsg("warning", data.reply ?? "");
      } else {
        pushMsg("npc", data.reply ?? "");
        // 빈 choices → 자유 입력 모드 (렌더가 choices.length 로 분기).
        setChoices(data.choices ?? []);
      }
    }
    setBusy(false);
  }

  function submitFreeInput(e: React.FormEvent) {
    e.preventDefault();
    const text = draft.trim();
    if (!text || busy) return;
    setDraft("");
    void sendTurn(text);
  }

  if (screen === "banned") {
    return (
      <main className="banned">
        <div className="banned__panel">
          <h1 className="banned__title">{BANNED_TITLE}</h1>
          {banReason && <p className="banned__reason">{banReason}</p>}
        </div>
      </main>
    );
  }

  if (screen === "title") {
    return (
      <main className="title">
        <div className="title__mist" aria-hidden="true" />
        <div className="title__inner">
          <h1 className="title__name">Still Here</h1>
          <div className="title__actions">
            <button
              className="btn btn--primary"
              onClick={() => void start()}
              disabled={busy}
            >
              {busy ? CONNECTING : playedHint ? CONTINUE_BUTTON : START_BUTTON}
            </button>
            {/* Phase 3 자리표시 — 세이브 코드 입력은 아직 미배선. */}
            <button className="btn btn--ghost" disabled>
              {SAVE_CODE_ENTRY_DISABLED}
            </button>
          </div>
          {playedHint && !titleError && (
            <p className="title__note">{RETURNING_NOTE}</p>
          )}
          {titleError && <p className="title__error">{titleError}</p>}
        </div>
      </main>
    );
  }

  const freeInputMode = choices.length === 0;

  return (
    <main className="chat">
      <header className="chat__header">
        {spriteVisible && (
          <img
            className="chat__sprite"
            src="/assets/surigong.png"
            alt=""
            onError={() => setSpriteVisible(false)}
          />
        )}
        <span className="chat__header-title">Still Here</span>
      </header>

      <div className="chat__log">
        {messages.map((m, i) => {
          const block =
            m.kind === "warning" || m.kind === "error" ? (
              <div key={i} className={`system-msg system-msg--${m.kind}`}>
                {m.text}
              </div>
            ) : (
              <div
                key={i}
                className={`bubble bubble--${m.kind}${m.past ? " bubble--past" : ""}`}
              >
                {m.text}
              </div>
            );
          // 지난 대화 블록 끝 — 새 턴과의 경계 구분선 (past 는 항상 prefix).
          const pastBoundary = m.past && !messages[i + 1]?.past;
          return pastBoundary ? (
            <Fragment key={i}>
              {block}
              <div className="resume-divider" role="separator">
                {RESUME_DIVIDER}
              </div>
            </Fragment>
          ) : (
            block
          );
        })}
        {busy && (
          <div className="bubble bubble--npc typing" aria-hidden="true">
            <span className="typing__dot" />
            <span className="typing__dot" />
            <span className="typing__dot" />
          </div>
        )}
        <div ref={logEndRef} />
      </div>

      <footer className="chat__controls">
        {freeInputMode ? (
          <form className="free-input" onSubmit={submitFreeInput}>
            <input
              className="free-input__field"
              type="text"
              value={draft}
              maxLength={MAX_INPUT_LEN}
              placeholder={FREE_INPUT_PLACEHOLDER}
              onChange={(e) => setDraft(e.target.value)}
              disabled={busy}
            />
            <button
              className="btn btn--primary"
              type="submit"
              disabled={busy || draft.trim().length === 0}
            >
              {SEND_BUTTON}
            </button>
          </form>
        ) : (
          <div className="choices">
            {choices.map((c, i) => (
              <button
                key={i}
                className="choice-btn"
                onClick={() => void sendTurn(c.text)}
                disabled={busy}
              >
                {c.text}
              </button>
            ))}
          </div>
        )}
      </footer>
    </main>
  );
}
