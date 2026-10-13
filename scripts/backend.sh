#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
BACKEND="$ROOT/backend"
RUN_DIR="$BACKEND/run"
PID_FILE="$RUN_DIR/app.pid"
LOG_FILE="$RUN_DIR/app.log"
PORT=26284
ACTION="${1:-start}"

mkdir -p "$RUN_DIR"

listening_pids() {
  netstat -ano | tr -d '\r' | awk -v port=":$PORT" '
    $4 == "LISTENING" && index($2, port) {
      colon = match($2, /:[0-9]+$/)
      if (colon && substr($2, colon) == port) print $5
    }
  ' | sort -u
}

stop_backend() {
  if [[ -f "$PID_FILE" ]]; then
    old_pid="$(tr -d '\r' < "$PID_FILE")"
    if [[ -n "$old_pid" ]]; then
      taskkill //PID "$old_pid" //F >/dev/null 2>&1 || true
    fi
    rm -f "$PID_FILE"
  fi
  local pid
  for pid in $(listening_pids); do
    taskkill //PID "$pid" //F >/dev/null 2>&1 || true
  done
}

start_backend() {
  if listening_pids | grep -q .; then
    echo "后端已在端口 ${PORT} 运行"
    return 0
  fi
  cd "$BACKEND"
  nohup python app.py >>"$LOG_FILE" 2>&1 &
  echo $! >"$PID_FILE"
  local i
  for i in 1 2 3 4 5 6 7 8 9 10; do
    if listening_pids | grep -q .; then
      echo "后端已启动，端口 ${PORT}，日志 ${LOG_FILE}"
      return 0
    fi
    sleep 0.5
  done
  echo "后端启动失败，请查看 ${LOG_FILE}" >&2
  return 1
}

case "$ACTION" in
  start)
    start_backend
    ;;
  stop)
    stop_backend
    echo "后端已停止"
    ;;
  restart)
    stop_backend
    sleep 0.5
    start_backend
    ;;
  *)
    echo "用法: bash scripts/backend.sh start|stop|restart" >&2
    exit 1
    ;;
esac
