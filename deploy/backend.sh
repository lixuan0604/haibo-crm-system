#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
BACKEND="$ROOT/backend"
RUN_DIR="$BACKEND/run"
PID_FILE="$RUN_DIR/haibo.pid"
LOG_FILE="$RUN_DIR/haibo.log"

mkdir -p "$RUN_DIR"

if [[ -x "$BACKEND/.venv/bin/gunicorn" ]]; then
  GUNICORN="$BACKEND/.venv/bin/gunicorn"
elif command -v gunicorn >/dev/null 2>&1; then
  GUNICORN="$(command -v gunicorn)"
else
  echo "未找到 gunicorn。请在 backend 目录执行: pip install -r requirements.txt"
  exit 1
fi

is_running() {
  [[ -f "$PID_FILE" ]] && kill -0 "$(cat "$PID_FILE")" 2>/dev/null
}

start() {
  if is_running; then
    echo "后端已在运行，pid=$(cat "$PID_FILE")"
    return 0
  fi
  rm -f "$PID_FILE"
  cd "$BACKEND"
  "$GUNICORN" \
    --workers 2 \
    --bind 127.0.0.1:26284 \
    --pid "$PID_FILE" \
    --daemon \
    --access-logfile "$LOG_FILE" \
    --error-logfile "$LOG_FILE" \
    --capture-output \
    app:app
  echo "后端已启动，pid=$(cat "$PID_FILE")，日志 $LOG_FILE"
}

stop() {
  if ! [[ -f "$PID_FILE" ]]; then
    echo "后端没有在运行"
    return 0
  fi
  local pid
  pid="$(cat "$PID_FILE")"
  if kill -0 "$pid" 2>/dev/null; then
    kill "$pid"
    for _ in 1 2 3 4 5 6 7 8 9 10; do
      kill -0 "$pid" 2>/dev/null || break
      sleep 0.3
    done
    if kill -0 "$pid" 2>/dev/null; then
      kill -9 "$pid" 2>/dev/null || true
    fi
  fi
  rm -f "$PID_FILE"
  echo "后端已停止"
}

restart() {
  stop
  start
}

status() {
  if is_running; then
    echo "后端正在运行，pid=$(cat "$PID_FILE")"
  else
    echo "后端没有在运行"
    return 1
  fi
}

case "${1:-}" in
  start) start ;;
  stop) stop ;;
  restart) restart ;;
  status) status ;;
  *)
    echo "用法: $0 start|stop|restart|status"
    exit 1
    ;;
esac
