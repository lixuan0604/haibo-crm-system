#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
FRONTEND="$ROOT/frontend"
RUNTIME="$ROOT/deploy/runtime"
NGINX_HOME="$RUNTIME/nginx"
NGINX_VERSION="1.28.0"
NGINX_URL="https://nginx.org/download/nginx-${NGINX_VERSION}.zip"
LISTEN_PORT=26285

to_win_path() {
  cygpath -m "$1"
}

ensure_nginx() {
  if [[ -x "$NGINX_HOME/nginx.exe" ]]; then
    return 0
  fi
  mkdir -p "$RUNTIME"
  local archive="$RUNTIME/nginx.zip"
  echo "正在下载 Nginx ${NGINX_VERSION}"
  curl -fsSL "$NGINX_URL" -o "$archive"
  unzip -q -o "$archive" -d "$RUNTIME"
  rm -rf "$NGINX_HOME"
  mv "$RUNTIME/nginx-${NGINX_VERSION}" "$NGINX_HOME"
  rm -f "$archive"
}

write_conf() {
  local dist
  dist="$(to_win_path "$FRONTEND/dist")"
  cat >"$NGINX_HOME/conf/nginx.conf" <<EOF
worker_processes  1;

error_log  logs/error.log;
pid        logs/nginx.pid;

events {
    worker_connections  1024;
}

http {
    include       mime.types;
    default_type  application/octet-stream;
    sendfile      on;

    server {
        listen       ${LISTEN_PORT};
        server_name  localhost;

        root   ${dist};
        index  index.html;

        location /api/ {
            proxy_pass http://127.0.0.1:26284;
            proxy_http_version 1.1;
            proxy_set_header Host \$host;
            proxy_set_header X-Real-IP \$remote_addr;
            proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        }

        location / {
            try_files \$uri \$uri/ /index.html;
        }
    }
}
EOF
}

nginx_running() {
  [[ -f "$NGINX_HOME/logs/nginx.pid" ]] || return 1
  local pid
  pid="$(tr -d '\r' < "$NGINX_HOME/logs/nginx.pid")"
  [[ -n "$pid" ]] || return 1
  tasklist //FI "PID eq $pid" | grep -q "$pid"
}

reload_nginx() {
  local prefix
  prefix="$(to_win_path "$NGINX_HOME")"
  if nginx_running; then
    "$NGINX_HOME/nginx.exe" -p "$prefix" -s reload
    echo "Nginx 已重新加载"
  else
    "$NGINX_HOME/nginx.exe" -p "$prefix"
    echo "Nginx 已启动：http://127.0.0.1:${LISTEN_PORT}"
  fi
}

cd "$FRONTEND"
npm run build
ensure_nginx
write_conf
reload_nginx
