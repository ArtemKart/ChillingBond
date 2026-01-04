#!/bin/sh
set -e

echo "🔍 DEBUG: Raw environment at container start"
env | grep -E "(BACKEND|FRONTEND|PORT)" | sort

echo ""
echo "🔍 DEBUG: Before setting defaults"
echo "BACKEND_PORT from env: [${BACKEND_PORT}]"
echo "FRONTEND_PORT from env: [${FRONTEND_PORT}]"

export BACKEND_HOST=${BACKEND_HOST:-backend.railway.internal}
export BACKEND_PORT=${BACKEND_PORT:-8000}
export FRONTEND_HOST=${FRONTEND_HOST:-frontend.railway.internal}
export FRONTEND_PORT=${FRONTEND_PORT:-3000}
export PORT=${PORT:-80}

echo ""
echo "🚀 Starting Nginx..."
echo "BACKEND_HOST: ${BACKEND_HOST}"
echo "BACKEND_PORT: ${BACKEND_PORT}"
echo "FRONTEND_HOST: ${FRONTEND_HOST}"
echo "FRONTEND_PORT: ${FRONTEND_PORT}"
echo "PORT: ${PORT}"

# Подставляем переменные
envsubst '${BACKEND_HOST} ${BACKEND_PORT} ${FRONTEND_HOST} ${FRONTEND_PORT} ${PORT}' \
  < /etc/nginx/nginx.conf.template \
  > /etc/nginx/nginx.conf

echo "✅ Generated nginx.conf"

# Запускаем nginx
exec nginx -g 'daemon off;'