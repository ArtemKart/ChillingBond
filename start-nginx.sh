#!/bin/sh
set -e

echo "🚀 Starting Nginx..."
echo "=== RAW ENVIRONMENT VARIABLES ==="
env | sort
echo "================================="

# Устанавливаем значения по умолчанию
export BACKEND_HOST=${BACKEND_HOST:-backend.railway.internal}
export BACKEND_PORT=${BACKEND_PORT:-8000}
export FRONTEND_HOST=${FRONTEND_HOST:-frontend.railway.internal}
export FRONTEND_PORT=${FRONTEND_PORT:-3000}

echo "=== AFTER DEFAULTS ==="
echo "BACKEND_HOST: [${BACKEND_HOST}]"
echo "BACKEND_PORT: [${BACKEND_PORT}]"
echo "FRONTEND_HOST: [${FRONTEND_HOST}]"
echo "FRONTEND_PORT: [${FRONTEND_PORT}]"
echo "======================"

# Подставляем переменные
envsubst '${BACKEND_HOST} ${BACKEND_PORT} ${FRONTEND_HOST} ${FRONTEND_PORT}' \
  < /etc/nginx/nginx.conf.template \
  > /etc/nginx/nginx.conf

echo "✅ Generated nginx.conf (relevant lines):"
grep -A 2 "upstream backend" /etc/nginx/nginx.conf
grep -A 2 "upstream frontend" /etc/nginx/nginx.conf

# Запускаем nginx
exec nginx -g 'daemon off;'