#!/bin/sh
set -e

export BACKEND_HOST=${BACKEND_HOST:-backend.railway.internal}
export BACKEND_PORT=${BACKEND_PORT:-8080}
export FRONTEND_HOST=${FRONTEND_HOST:-frontend.railway.internal}
export FRONTEND_PORT=${FRONTEND_PORT:-8080}
export PORT=${PORT:-80}

envsubst '${BACKEND_HOST} ${BACKEND_PORT} ${FRONTEND_HOST} ${FRONTEND_PORT} ${PORT}' \
  < /etc/nginx/nginx.conf.template \
  > /etc/nginx/nginx.conf

echo "✅ Generated nginx.conf"

exec nginx -g 'daemon off;'
