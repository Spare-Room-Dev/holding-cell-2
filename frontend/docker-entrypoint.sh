#!/bin/sh
# Copy static files to the shared volume
cp -r /usr/share/nginx/html/* /static/ 2>/dev/null || true

# Start nginx (original entrypoint)
exec nginx -g "daemon off;"