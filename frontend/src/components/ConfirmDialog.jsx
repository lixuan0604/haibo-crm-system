import { useEffect } from "react";

export default function ConfirmDialog({
  title,
  message,
  confirmText = "确定",
  cancelText = "取消",
  danger = false,
  busy = false,
  onConfirm,
  onCancel,
}) {
  useEffect(() => {
    function onKey(event) {
      if (event.key === "Escape" && !busy) onCancel();
    }
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [busy, onCancel]);

  return (
    <div className="mask" onMouseDown={busy ? undefined : onCancel}>
      <div
        className="modal confirm"
        role="dialog"
        aria-modal="true"
        aria-label={title}
        onMouseDown={(event) => event.stopPropagation()}
      >
        <h2>{title}</h2>
        <p>{message}</p>
        <div className="modal-actions">
          <button type="button" className="btn" onClick={onCancel} disabled={busy}>
            {cancelText}
          </button>
          <button type="button" className={danger ? "btn danger" : "btn primary"} onClick={onConfirm} disabled={busy}>
            {busy ? "正在处理…" : confirmText}
          </button>
        </div>
      </div>
    </div>
  );
}
