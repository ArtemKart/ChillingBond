#!/bin/sh
set -e

echo "🚀 Starting Nginx..."
echo "BACKEND_HOST: ${BACKEND_HOST:-not set}"
echo "BACKEND_PORT: ${BACKEND_PORT:-not set}"
echo "FRONTEND_HOST: ${FRONTEND_HOST:-not set}"
echo "FRONTEND_PORT: ${FRONTEND_PORT:-not set}"

envsubst '${BACKEND_HOST} ${BACKEND_PORT} ${FRONTEND_HOST} ${FRONTEND_PORT}' \
  < /etc/nginx/nginx.conf.template \
  > /etc/nginx/nginx.conf

echo "✅ Generated nginx.conf"

exec nginx -g 'daemon off;'
