#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
RENDERED="$ROOT/deploy/haibo.nginx.conf"

"$ROOT/deploy/frontend.sh"
"$ROOT/deploy/backend.sh" restart

sed "s|__APP_ROOT__|$ROOT|g" "$ROOT/deploy/nginx.conf" > "$RENDERED"

if [[ ! -d /etc/nginx/conf.d ]]; then
  echo "前端和后端已更新。这台机器没有 /etc/nginx/conf.d，Nginx 配置在 $RENDERED"
  exit 0
fi

if [[ "$(id -u)" -ne 0 ]]; then
  echo "前端和后端已更新。安装 Nginx 配置请用 root 执行："
  echo "  sudo cp $RENDERED /etc/nginx/conf.d/haibo.conf"
  echo "  sudo nginx -t && sudo nginx -s reload"
  exit 0
fi

cp "$RENDERED" /etc/nginx/conf.d/haibo.conf
nginx -t
if command -v systemctl >/dev/null 2>&1; then
  systemctl reload nginx
else
  nginx -s reload
fi
echo "Nginx 已加载 $RENDERED"
