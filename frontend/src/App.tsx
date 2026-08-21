// 타이틀 + 채팅 + 차단 화면 — Phase 1 step 4.
// 규약: 한글 시스템 문구는 전부 tone.ts 상수. NPC 텍스트는 전부 서버에서 온다.
// "Still Here" 는 게임 타이틀(영문)이라 마크업에 둔다.

import { Fragment, useEffect, useRef, useState } from "react";
import { postJson, type ApiResult } from "./api";
import CopyCodeButton from "./CopyCodeButton";
import { markPlayedHint, readPlayedHint } from "./playedHint";
import type {
  BootstrapData,
  Choice,
  RedeemData,
  SaveCodeIssueData,
} from "./protocol";
import {
  clearNudgeDismissed,
  markNudgeDismissed,
  readNudgeDismissed,
  shouldShowSaveCodeNudge,
} from "./saveCodeNudge";
import { useTurn, type Msg } from "./useTurn";
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
  REPLACE_RESCUE_CODE,
  REPLACE_RESCUE_FAILED,
  RESUME_DIVIDER,
  RETURNING_NOTE,
  SAVE_CODE_BANNED_NOTE,
  SAVE_CODE_BUTTON,
  SAVE_CODE_CANCEL,
  SAVE_CODE_CLOSE,
  SAVE_CODE_ENTRY,
  SAVE_CODE_ERROR_FALLBACK,
  SAVE_CODE_INPUT_PLACEHOLDER,
  SAVE_CODE_ISSUED_NOTE,
  SAVE_CODE_ISSUED_TITLE,
  SAVE_CODE_NUDGE_ACTION,
  SAVE_CODE_NUDGE_AFTER_TURNS,
  SAVE_CODE_NUDGE_BODY,
  SAVE_CODE_NUDGE_DISMISS,
  SAVE_CODE_ROTATE,
  SAVE_CODE_ROTATE_WARNING,
  SAVE_CODE_SUBMIT,
  SEND_BUTTON,
  SERVER_UNREACHABLE,
  START_BUTTON,
} from "./tone";

// Msg (채팅 로그 엔트리) 는 useTurn.ts 소유 — 로그를 append 하는 쪽이 shape 의 홈.
// 여기서는 렌더와 재방문 복원(past 부여)만 한다.

type Screen = "title" | "chat" | "banned";

// 클라이언트측 여유 상한 — 실제 제한은 서버(Layer 1)가 소유.
const MAX_INPUT_LEN = 500;

// 세이브 코드 XXXX-XXXX (9자) — 형식 권한은 서버(app/save_code.py).
// 여기서는 입력 필드 상한만 맞춘다 (malformed 는 서버 404 가 처리).
const SAVE_CODE_LEN = 9;

/** 세이브 코드 응답(발급 · 회전 공용 wire shape) → 새 코드 또는 사용자 노출 오류 문구.
 *  두 경로가 같은 분기(unreachable / ok / banned / 401·503)를 쓰므로 판독만 여기 모으고,
 *  오류를 *어디에* 띄울지(채팅 로그 vs 패널)는 호출측이 정한다. */
type SaveCodeResult =
  | { ok: true; code: string }
  | { ok: false; error: string };

function readSaveCodeResult(r: ApiResult<SaveCodeIssueData>): SaveCodeResult {
  if (r.unreachable) return { ok: false, error: SERVER_UNREACHABLE };
  const data = r.data;
  if (data.status === "ok" && data.save_code) {
    return { ok: true, code: data.save_code };
  }
  if (data.status === "banned") {
    return { ok: false, error: data.ban_reason || GENERIC_ERROR };
  }
  // 401 무신원 등 — 서버 문구 우선.
  return { ok: false, error: data.message || GENERIC_ERROR };
}

/** 오버레이 백드롭의 클래스. 요청 중에는 백드롭이 닫는 표면이 아니라 클릭이
 *  삼켜지므로(위 onClick 가드), 삼킨다는 사실을 커서/농도로 보인다 — 문구 없이.
 *  두 오버레이(대체 확인 · 세이브 코드 패널)가 같은 표면을 쓰므로 여기 한 곳에서. */
function backdropClass(busy: boolean): string {
  const base = "overlay__backdrop";
  return busy ? `${base} ${base}--busy` : base;
}

/** 대체 확인 탈출구의 진행 상태. "pending" 은 요청 중 — 결과가 나오면 판독 결과로
 *  대체된다. null 은 아직 탈출구를 누르지 않은 상태(다이얼로그를 닫으면 되돌아간다). */
type RescueState = SaveCodeResult | "pending" | null;

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
  // 회전은 같은 패널 안의 확인 단계 — 경고를 읽기 전에는 코드가 바뀌지 않는다.
  const [rotateConfirm, setRotateConfirm] = useState(false);
  const [rotateError, setRotateError] = useState<string | null>(null);
  const [codeEntryOpen, setCodeEntryOpen] = useState(false);
  const [codeDraft, setCodeDraft] = useState("");
  const [codeError, setCodeError] = useState<string | null>(null);
  const [confirmOpen, setConfirmOpen] = useState(false);
  // 대체 확인 다이얼로그 안의 탈출구 상태 (null = 아직 안 눌렀음).
  const [rescue, setRescue] = useState<RescueState>(null);
  // 재방문 힌트는 타이틀 첫 렌더 시점에 한 번만 읽는다 (라벨 용도).
  const [playedHint] = useState(readPlayedHint);
  // B5 넛지의 세 입력. hasSaveCode 의 권위는 진입 응답의 has_save_code(B2b) 이고,
  // 세션 도중 발급/회전 성공이 추가 왕복 없이 즉시 참으로 갱신한다.
  const [hasSaveCode, setHasSaveCode] = useState(false);
  // 이 세션에서 플레이어가 보낸 누적 턴 수. 진입이 시드를 정하고 useTurn 이 센다.
  const [turnCount, setTurnCount] = useState(0);
  const [nudgeDismissed, setNudgeDismissed] = useState(readNudgeDismissed);
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
    enterNudgeSession(data);
    setScreen("chat");
  }

  /** 진입 1회당 넛지 상태 시드 (B5). 진입은 세션이 바뀌는 유일한 지점이라
   *  누적 턴 수 · 코드 보유 · dismiss 세 입력이 전부 여기서 정해진다.
   *
   *  턴 수 시드: new 는 0 (임계값만큼 쌓아야 노출). new 가 아닌 진입(resumed)은
   *  임계값에서 시작한다 — resumed 자체가 지킬 진행이 있다는 증거이고, 복원되는
   *  히스토리는 잘려 오므로(limit=8) 거기서 턴을 세면 없는 숫자를 지어내는 꼴이다.
   *
   *  dismiss 해제: *코드 없는 새 세션* 진입에서만. 쿠키가 사라져 새 세션이 된
   *  플레이어가 코드도 없이 넛지를 영영 못 보는 상태를 막는다. resumed 는 해제하지
   *  않고(닫은 결정이 유효), 코드로 복원된 세션은 has_save_code 가 참이라 애초에
   *  이 분기에 오지 않는다. */
  function enterNudgeSession(data: BootstrapData) {
    const isNew = data.status === "new";
    const entryHasCode = data.has_save_code === true;
    setHasSaveCode(entryHasCode);
    setTurnCount(isNew ? 0 : SAVE_CODE_NUDGE_AFTER_TURNS);
    if (isNew && !entryHasCode) {
      clearNudgeDismissed();
      setNudgeDismissed(false);
    } else {
      setNudgeDismissed(readNudgeDismissed());
    }
  }

  function dismissNudge() {
    markNudgeDismissed();
    setNudgeDismissed(true);
  }

  /** 차단 확정 → 사유 표시 + 선택지 봉인 + 화면 교체. turn 경로 전용 —
   *  타이틀 bootstrap 의 banned 는 아직 채팅 상태가 없어 봉인할 선택지도 없다. */
  function showBanned(reason: string) {
    setBanReason(reason);
    setChoices([]);
    setScreen("banned");
  }

  // /turn 전송 + 401 자동 복구 + 응답 반영은 useTurn 소유 (동작 보존 추출).
  // 상태는 여전히 여기 — 훅은 아래 setter 로만 화면을 만진다.
  const { sendTurn } = useTurn({
    busy,
    setBusy,
    npcId,
    pushMsg,
    onTurnSent: () => setTurnCount((n) => n + 1),
    onEntrySaveCode: setHasSaveCode,
    setChoices,
    showBanned,
    enterChat,
  });

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
    closeConfirm();
    setBusy(false);
  }

  /** 대체 확인 다이얼로그의 탈출구 — 갈아타기 전에 *이 기기 세션*의 코드를 받아 둔다.
   *  발급과 같은 endpoint(idempotent) 지만 결과는 이 다이얼로그 안에만 산다:
   *  실패해도 확인 버튼은 그대로 살아 있다 — 돌아올 길을 못 만들었다는 사실만
   *  정직하게 알리고, 계속할지 말지는 사용자가 정한다. */
  async function rescueSaveCode() {
    if (busy) return;
    setBusy(true);
    setRescue("pending");
    setRescue(
      readSaveCodeResult(await postJson<SaveCodeIssueData>("/save-code")),
    );
    setBusy(false);
  }

  /** 다이얼로그를 떠나며 탈출구 상태도 되돌린다 — 다음에 열릴 때는 처음부터. */
  function closeConfirm() {
    setConfirmOpen(false);
    setRescue(null);
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
    const got = readSaveCodeResult(
      await postJson<SaveCodeIssueData>("/save-code"),
    );
    if (got.ok) {
      setSaveCode(got.code);
      setSaveCodeOpen(true);
      // 발급 성공이 곧 코드 보유 — 넛지는 여기서 즉시 꺼진다 (추가 왕복 없음).
      setHasSaveCode(true);
    } else {
      // 패널이 아직 안 열렸으므로 실패는 채팅 로그에 남긴다.
      pushMsg("error", got.error);
    }
    setBusy(false);
  }

  /** 채팅 — 세이브 코드 회전(확인 후). 발급과 달리 idempotent 아님: 성공하면
   *  이전 코드는 그 순간부터 죽는다. 성공해도 패널은 열어 둔 채 새 코드를
   *  같은 자리에 보여준다 — 적어 둘 대상이 방금 바뀐 참이라 숨기면 안 된다. */
  async function rotateSaveCode() {
    if (busy) return;
    setBusy(true);
    setRotateError(null);
    const got = readSaveCodeResult(
      await postJson<SaveCodeIssueData>("/save-code/rotate"),
    );
    if (got.ok) {
      // 복사 라벨은 CopyCodeButton 이 코드별로 소유 — key 가 바뀌며 저절로 되돌아간다.
      setSaveCode(got.code);
      setRotateConfirm(false);
      // 회전은 코드를 갈아끼울 뿐 — 보유 상태를 되돌리지 않는다.
      setHasSaveCode(true);
    } else {
      // 패널이 채팅 로그를 덮고 있으니 실패는 확인 단계 안에서 알린다
      // (코드는 안 바뀐 채로 남는다).
      setRotateError(got.error);
    }
    setBusy(false);
  }

  function closeSaveCode() {
    setSaveCodeOpen(false);
    setRotateConfirm(false);
    setRotateError(null);
  }

  function submitFreeInput(e: React.FormEvent) {
    e.preventDefault();
    const text = draft.trim();
    if (!text || busy) return;
    setDraft("");
    void sendTurn(text);
  }

  // 탈출구의 *해소된* 결과만 — 요청 중("pending")은 아직 보여 줄 사실이 없다.
  const rescued = rescue === "pending" ? null : rescue;

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
            {/* 백드롭도 취소/확인과 같은 게이트 — 요청 중에는 닫는 표면이 아니다.
                닫아 버리면 다이얼로그 없이 busy 만 남아(타이틀 버튼이 이유를
                설명하는 화면 없이 죽는다) 늦게 온 탈출구 결과가 다음에 열 때
                되살아난다. 가드는 closeConfirm 안이 아니라 여기 — redeem 은
                busy 인 채로 closeConfirm 을 호출해 다이얼로그를 걷어낸다. */}
            <div
              className={backdropClass(busy)}
              onClick={busy ? undefined : closeConfirm}
            />
            <div className="overlay__panel">
              <h2 className="overlay__title overlay__title--warning">
                {REPLACE_CONFIRM_TITLE}
              </h2>
              <p className="overlay__body">{REPLACE_CONFIRM_BODY}</p>
              {/* 탈출구 — 파괴적 확인 *앞*에 놓는다. 돌아올 길을 먼저 만들고
                  나서 갈아타는 순서가 화면에도 그대로 보여야 한다. */}
              <div className="replace-rescue">
                {rescued?.ok && (
                  <>
                    <p className="savecode__code">{rescued.code}</p>
                    <CopyCodeButton code={rescued.code} />
                  </>
                )}
                {rescued && !rescued.ok && (
                  <>
                    {/* 원인(401 / 밴 / 503 / 네트워크)이 무엇이든 사용자에게 남는
                        사실은 하나 — 코드를 못 받았다. 서버 문구는 그 아래 부연. */}
                    <p className="overlay__body overlay__body--warning">
                      {REPLACE_RESCUE_FAILED}
                    </p>
                    <p className="overlay__error">{rescued.error}</p>
                  </>
                )}
                {!rescued?.ok && (
                  // 실패 뒤에도 남는다 — 네트워크가 돌아오면 다시 시도할 수 있다.
                  <button
                    className="btn btn--ghost"
                    onClick={() => void rescueSaveCode()}
                    disabled={busy}
                  >
                    {rescue === "pending" ? CONNECTING : REPLACE_RESCUE_CODE}
                  </button>
                )}
              </div>
              <div className="overlay__actions">
                <button
                  className="btn btn--primary"
                  onClick={() => void redeemCode()}
                  disabled={busy}
                >
                  {/* 탈출구 요청 중에는 저쪽이 연결 중 — 확인 라벨은 그대로 둔다. */}
                  {busy && rescue !== "pending"
                    ? CONNECTING
                    : REPLACE_CONFIRM_OK}
                </button>
                <button
                  className="btn btn--ghost"
                  onClick={closeConfirm}
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
  // B5 — 판정은 saveCodeNudge 의 순수 함수 소유. 여기서는 입력을 모으기만 한다.
  const nudgeVisible = shouldShowSaveCodeNudge({
    hasSaveCode,
    turnCount,
    dismissed: nudgeDismissed,
  });

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

      {/* 넛지는 로그가 아니라 입력 바로 위 — 로그에 넣으면 다음 턴에 스크롤로
          밀려 올라가 지금 할 수 있는 일이 아니게 된다. 시스템 목소리이므로
          system 색 계열만 쓴다 (NPC 말풍선 색과 절대 공유 금지). */}
      {nudgeVisible && (
        <div className="nudge" role="status">
          <p className="nudge__body">{SAVE_CODE_NUDGE_BODY}</p>
          <div className="nudge__actions">
            <button
              className="btn btn--primary"
              onClick={() => void issueSaveCode()}
              disabled={busy}
            >
              {SAVE_CODE_NUDGE_ACTION}
            </button>
            <button className="btn btn--ghost" onClick={dismissNudge}>
              {SAVE_CODE_NUDGE_DISMISS}
            </button>
          </div>
        </div>
      )}

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
          {/* 대체 확인 다이얼로그와 같은 이유의 가드 — 회전 요청 중에 닫히면
              busy 만 남아 채팅이 통째로 굳고(있지도 않은 NPC 타이핑 표시까지 뜬다)
              늦게 온 회전 오류가 다음 확인 단계에 되살아난다. */}
          <div
            className={backdropClass(busy)}
            onClick={busy ? undefined : closeSaveCode}
          />
          <div className="overlay__panel">
            <h2 className="overlay__title">{SAVE_CODE_ISSUED_TITLE}</h2>
            {/* 확인 단계에서도 코드는 계속 보인다 — 무엇이 죽는지 보이는 채로 결정. */}
            <p className="savecode__code">{saveCode}</p>
            {rotateConfirm ? (
              <>
                <p className="overlay__body overlay__body--warning">
                  {SAVE_CODE_ROTATE_WARNING}
                </p>
                {rotateError && <p className="overlay__error">{rotateError}</p>}
                <div className="overlay__actions">
                  <button
                    className="btn btn--primary"
                    onClick={() => void rotateSaveCode()}
                    disabled={busy}
                  >
                    {busy ? CONNECTING : SAVE_CODE_ROTATE}
                  </button>
                  <button
                    className="btn btn--ghost"
                    onClick={() => {
                      setRotateConfirm(false);
                      setRotateError(null);
                    }}
                    disabled={busy}
                  >
                    {SAVE_CODE_CANCEL}
                  </button>
                </div>
              </>
            ) : (
              <>
                <p className="overlay__body">{SAVE_CODE_ISSUED_NOTE}</p>
                <div className="overlay__actions">
                  {/* key — 회전으로 코드가 바뀌면 복사 완료 라벨은 옛 코드의
                      사실이므로 함께 리셋된다. */}
                  <CopyCodeButton key={saveCode} code={saveCode} />
                  <button
                    className="btn btn--ghost"
                    onClick={() => setRotateConfirm(true)}
                    disabled={busy}
                  >
                    {SAVE_CODE_ROTATE}
                  </button>
                  <button className="btn btn--ghost" onClick={closeSaveCode}>
                    {SAVE_CODE_CLOSE}
                  </button>
                </div>
              </>
            )}
          </div>
        </div>
      )}
    </main>
  );
}
