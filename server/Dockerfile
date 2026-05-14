# Multi-stage: pull bgweb-api binary, run via Caddy for CORS support
FROM foochu/bgweb-api:latest as bgweb

FROM caddy:2-alpine

# Copy bgweb-api binary and gnubg data files
COPY --from=bgweb /usr/bin/bgweb-api /usr/bin/bgweb-api
COPY --from=bgweb /var/lib/bgweb-api /var/lib/bgweb-api

# Caddy reverse-proxy config (handles CORS + proxies to bgweb-api)
COPY Caddyfile /etc/caddy/Caddyfile

# Startup script: run bgweb-api on :8081 in background, Caddy on :8080 in foreground
COPY start.sh /start.sh
RUN chmod +x /start.sh

EXPOSE 8080

CMD ["/start.sh"]
