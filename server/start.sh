#!/bin/sh
# Run bgweb-api in background on internal port 8081
/usr/bin/bgweb-api --datadir /var/lib/bgweb-api/data --port 8081 &
BGWEB_PID=$!

# Trap signals to cleanly shut down both processes
trap "kill $BGWEB_PID 2>/dev/null; exit 0" TERM INT

# Wait for bgweb-api to actually accept connections on :8081 before bringing
# Caddy up. Without this, Caddy starts proxying immediately and every request
# during the first ~2s of a cold start returns 502 (dial: connection refused).
# This was caught via Fly logs after a load test produced sporadic 502s.
for i in 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20; do
  if nc -z localhost 8081 2>/dev/null; then
    echo "bgweb-api ready after ${i}s, starting Caddy"
    break
  fi
  sleep 1
done

# Run Caddy in foreground on public port 8080
caddy run --config /etc/caddy/Caddyfile --adapter caddyfile
