#!/bin/sh
# Run bgweb-api in background on internal port 8081
/usr/bin/bgweb-api --datadir /var/lib/bgweb-api/data --port 8081 &
BGWEB_PID=$!

# Trap signals to cleanly shut down both processes
trap "kill $BGWEB_PID 2>/dev/null; exit 0" TERM INT

# Run Caddy in foreground on public port 8080
caddy run --config /etc/caddy/Caddyfile --adapter caddyfile
