// 타이틀 + 채팅 + 차단 화면 — Phase 1 step 4.
// 규약: 한글 시스템 문구는 전부 tone.ts 상수. NPC 텍스트는 전부 서버에서 온다.
// "Still Here" 는 게임 타이틀(영문)이라 마크업에 둔다.

import { Fragment, useEffect, useRef, useState } from "react";
import { postJson, type ApiResult } from "./api";
import { markPlayedHint, readPlayedHint } from "./playedHint";
import type {
  BootstrapData,
  Choice,
  RedeemData,
  SaveCodeIssueData,
  TurnData,
} from "./protocol";
import {
  BANNED_TITLE,
  CONNECTING,
  CONTINUE_BUTTON,
  FREE_INPUT_PLACEHOLDER,
  GENERIC_ERROR,
  REPLACE_CONFIRM_BODY,
  REPLACE_CONFIRM_CANCEL,
  REPLACE_CONFIRM_OK,
  REPLACE_CONFIRM_TITLE,
  RESUME_DIVIDER,
  RETURNING_NOTE,
  SAVE_CODE_BANNED_NOTE,
  SAVE_CODE_BUTTON,
  SAVE_CODE_CANCEL,
  SAVE_CODE_CLOSE,
  SAVE_CODE_COPIED,
  SAVE_CODE_COPY,
  SAVE_CODE_ENTRY,
  SAVE_CODE_ERROR_FALLBACK,
  SAVE_CODE_INPUT_PLACEHOLDER,
  SAVE_CODE_ISSUED_NOTE,
  SAVE_CODE_ISSUED_TITLE,
  SAVE_CODE_SUBMIT,
  SEND_BUTTON,
  SERVER_UNREACHABLE,
  SESSION_RESTORE_FAILED,
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

// 세이브 코드 XXXX-XXXX (9자) — 형식 권한은 서버(app/save_code.py).
// 여기서는 입력 필드 상한만 맞춘다 (malformed 는 서버 404 가 처리).
const SAVE_CODE_LEN = 9;

export default function App() {
  const [screen, setScreen] = useState<Screen>("title");
  const [titleError, setTitleError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [messages, setMessages] = useState<Msg[]>([]);
  const [choices, setChoices] = useState<Choice[]>([]);
  const [npcId, setNpcId] = useState("");
  const [banReason, setBanReason] = useState("");
  const [draft, setDraft] = useState("");
  const [spriteVisible, setSpriteVisible] = useState(true);
  // 세이브 코드 — 발급(채팅 오버레이) / 입력(타이틀) / 대체 확인 다이얼로그.
  const [saveCode, setSaveCode] = useState<string | null>(null);
  const [saveCodeOpen, setSaveCodeOpen] = useState(false);
  const [saveCodeCopied, setSaveCodeCopied] = useState(false);
  const [codeEntryOpen, setCodeEntryOpen] = useState(false);
  const [codeDraft, setCodeDraft] = useState("");
  const [codeError, setCodeError] = useState<string | null>(null);
  const [confirmOpen, setConfirmOpen] = useState(false);
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

  /** new/resumed 성공 응답 → 채팅 진입. bootstrap 과 redeem 이 같은
   *  wire shape 를 쓰는 이유가 이 공유다 (RedeemData = BootstrapData). */
  function enterChat(data: BootstrapData) {
    markPlayedHint();
    setNpcId(data.npc_id ?? "");
    if (data.status === "new") {
      setMessages([{ kind: "npc", text: data.reply ?? "" }]);
    } else {
      setMessages(
        (data.history ?? []).map(
          (h): Msg => ({
            kind: h.role === "user" ? "user" : "npc",
            text: h.content,
            past: true, // 지난 대화 — 새 턴과 시각적으로 구분.
          }),
        ),
      );
    }
    setChoices(data.choices ?? []);
    setSaveCode(null); // 세션이 바뀌었을 수 있으니 캐시된 코드 무효화.
    setScreen("chat");
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
      } else if (data.status === "new" || data.status === "resumed") {
        enterChat(data);
      } else {
        // 503 {status:"error", message} — 타이틀에 남아 재시도 가능.
        setTitleError(data.message || GENERIC_ERROR);
      }
    }
    setBusy(false);
  }

  /** 타이틀 — 세이브 코드 redeem. 성공(new/resumed)만 쿠키가 재바인딩되어
   *  채팅 진입. banned/404/503 은 재바인딩 없음 — 이 기기 세션은 무사하므로
   *  차단 화면으로 갈아타지 않고 입력 아래 시스템 톤 안내로만 알린다. */
  async function redeemCode() {
    if (busy) return;
    setBusy(true);
    setCodeError(null);
    const r = await postJson<RedeemData>("/save-code/redeem", {
      code: codeDraft.trim(),
    });
    if (r.unreachable) {
      setCodeError(SERVER_UNREACHABLE);
    } else {
      const data = r.data;
      if (data.status === "new" || data.status === "resumed") {
        enterChat(data);
      } else if (data.status === "banned") {
        setCodeError(
          data.ban_reason
            ? `${SAVE_CODE_BANNED_NOTE}\n${data.ban_reason}`
            : SAVE_CODE_BANNED_NOTE,
        );
      } else {
        // 404(미지/형식 위반) / 503(오프닝 실패) — 입력은 보존, 재시도 가능.
        setCodeError(data.message || SAVE_CODE_ERROR_FALLBACK);
      }
    }
    setConfirmOpen(false);
    setBusy(false);
  }

  function submitCode(e: React.FormEvent) {
    e.preventDefault();
    if (busy || codeDraft.trim().length === 0) return;
    // 대체 확인은 무조건 — HttpOnly 쿠키는 클라이언트가 못 읽고 localStorage
    // 힌트보다 오래 살 수 있어, 힌트 게이팅은 조용한 세션 상실을 못 막는다.
    setConfirmOpen(true);
  }

  function closeCodeEntry() {
    setCodeEntryOpen(false);
    setCodeDraft("");
    setCodeError(null);
  }

  /** 채팅 — 세이브 코드 발급. 서버가 idempotent 라 재요청도 안전하지만,
   *  이미 받아 둔 코드는 재호출 없이 다시 보여준다. */
  async function issueSaveCode() {
    if (busy) return;
    if (saveCode) {
      setSaveCodeOpen(true);
      return;
    }
    setBusy(true);
    const r = await postJson<SaveCodeIssueData>("/save-code");
    if (r.unreachable) {
      pushMsg("error", SERVER_UNREACHABLE);
    } else {
      const data = r.data;
      if (data.status === "ok" && data.save_code) {
        setSaveCode(data.save_code);
        setSaveCodeOpen(true);
      } else if (data.status === "banned") {
        pushMsg("error", data.ban_reason || GENERIC_ERROR);
      } else {
        // 401 무신원 등 — 서버 문구 우선.
        pushMsg("error", data.message || GENERIC_ERROR);
      }
    }
    setBusy(false);
  }

  function copySaveCode() {
    if (!saveCode) return;
    // clipboard API 는 비보안 컨텍스트에 없을 수 있다 — 실패해도 무해
    // (코드 텍스트는 user-select: all 로 직접 복사 가능).
    void navigator.clipboard?.writeText(saveCode).then(
      () => setSaveCodeCopied(true),
      () => {},
    );
  }

  function closeSaveCode() {
    setSaveCodeOpen(false);
    setSaveCodeCopied(false);
  }

  /** turn 응답을 화면에 반영. 401 처리(자동 재bootstrap)는 sendTurn 소유 —
   *  여기 도달한 !ok 는 그 외 오류다. */
  function applyTurn(r: ApiResult<TurnData>) {
    if (r.unreachable) {
      pushMsg("error", SERVER_UNREACHABLE);
      return;
    }
    if (!r.ok) {
      pushMsg("error", GENERIC_ERROR);
      return;
    }
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

  async function sendTurn(text: string) {
    if (busy) return;
    setBusy(true);
    pushMsg("user", text);
    // 신원은 쿠키가 전담 — 본문은 {npc_id, player_input} 뿐 (B1/B6).
    const r = await postJson<TurnData>("/turn", {
      npc_id: npcId,
      player_input: text,
    });
    if (!r.unreachable && r.status === 401) {
      // 서버가 세션을 모름(쿠키 소멸 등) — recoverable. 자동 재bootstrap 1회.
      // 쿠키는 편의, 코드가 열쇠 — 세션이 없으면 새로 시작이 맞다.
      const b = await postJson<BootstrapData>("/session/bootstrap");
      if (b.unreachable) {
        pushMsg("error", SERVER_UNREACHABLE);
      } else if (b.data.status === "banned") {
        setBanReason(b.data.ban_reason ?? "");
        setChoices([]);
        setScreen("banned");
      } else if (b.data.status === "resumed") {
        // 세션 복구됨 — 보류된 턴을 정확히 1회 재시도. 또 401 이면
        // 재bootstrap 없이 정직하게 알리고 멈춘다 (무한 루프 금지).
        const retry = await postJson<TurnData>("/turn", {
          npc_id: npcId,
          player_input: text,
        });
        if (!retry.unreachable && retry.status === 401) {
          pushMsg("error", SESSION_RESTORE_FAILED);
        } else {
          applyTurn(retry);
        }
      } else if (b.data.status === "new") {
        // 서버에 이 기기의 세션이 없었음 — 새 세션의 오프닝으로 진입.
        // 보내려던 입력은 사라진 세션 소속이라 재전송하지 않는다.
        enterChat(b.data);
      } else {
        // 503 {status:"error", message} — 서버 문구 우선.
        pushMsg("error", b.data.message || GENERIC_ERROR);
      }
    } else {
      applyTurn(r);
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
          {codeEntryOpen ? (
            <form className="code-entry" onSubmit={submitCode}>
              <input
                className="free-input__field code-entry__field"
                type="text"
                value={codeDraft}
                maxLength={SAVE_CODE_LEN}
                placeholder={SAVE_CODE_INPUT_PLACEHOLDER}
                // 소문자 타이핑 허용 — 표시/전송은 대문자 정규화.
                onChange={(e) => setCodeDraft(e.target.value.toUpperCase())}
                disabled={busy}
                autoFocus
              />
              <div className="code-entry__actions">
                <button
                  className="btn btn--primary"
                  type="submit"
                  disabled={busy || codeDraft.trim().length === 0}
                >
                  {busy ? CONNECTING : SAVE_CODE_SUBMIT}
                </button>
                <button
                  className="btn btn--ghost"
                  type="button"
                  onClick={closeCodeEntry}
                  disabled={busy}
                >
                  {SAVE_CODE_CANCEL}
                </button>
              </div>
              {codeError && <p className="code-entry__error">{codeError}</p>}
            </form>
          ) : (
            <div className="title__actions">
              <button
                className="btn btn--primary"
                onClick={() => void start()}
                disabled={busy}
              >
                {busy ? CONNECTING : playedHint ? CONTINUE_BUTTON : START_BUTTON}
              </button>
              <button
                className="btn btn--ghost"
                onClick={() => setCodeEntryOpen(true)}
                disabled={busy}
              >
                {SAVE_CODE_ENTRY}
              </button>
            </div>
          )}
          {playedHint && !titleError && !codeEntryOpen && (
            <p className="title__note">{RETURNING_NOTE}</p>
          )}
          {titleError && <p className="title__error">{titleError}</p>}
        </div>
        {confirmOpen && (
          <div className="overlay" role="dialog" aria-modal="true">
            <div
              className="overlay__backdrop"
              onClick={() => setConfirmOpen(false)}
            />
            <div className="overlay__panel">
              <h2 className="overlay__title overlay__title--warning">
                {REPLACE_CONFIRM_TITLE}
              </h2>
              <p className="overlay__body">{REPLACE_CONFIRM_BODY}</p>
              <div className="overlay__actions">
                <button
                  className="btn btn--primary"
                  onClick={() => void redeemCode()}
                  disabled={busy}
                >
                  {busy ? CONNECTING : REPLACE_CONFIRM_OK}
                </button>
                <button
                  className="btn btn--ghost"
                  onClick={() => setConfirmOpen(false)}
                  disabled={busy}
                >
                  {REPLACE_CONFIRM_CANCEL}
                </button>
              </div>
            </div>
          </div>
        )}
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
        <button
          className="btn btn--ghost chat__save-btn"
          onClick={() => void issueSaveCode()}
          disabled={busy}
        >
          {SAVE_CODE_BUTTON}
        </button>
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

      {saveCodeOpen && saveCode && (
        <div className="overlay" role="dialog" aria-modal="true">
          <div className="overlay__backdrop" onClick={closeSaveCode} />
          <div className="overlay__panel">
            <h2 className="overlay__title">{SAVE_CODE_ISSUED_TITLE}</h2>
            <p className="savecode__code">{saveCode}</p>
            <p className="overlay__body">{SAVE_CODE_ISSUED_NOTE}</p>
            <div className="overlay__actions">
              <button className="btn btn--primary" onClick={copySaveCode}>
                {saveCodeCopied ? SAVE_CODE_COPIED : SAVE_CODE_COPY}
              </button>
              <button className="btn btn--ghost" onClick={closeSaveCode}>
                {SAVE_CODE_CLOSE}
              </button>
            </div>
          </div>
        </div>
      )}
    </main>
  );
}
