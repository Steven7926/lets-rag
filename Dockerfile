# ./Dockerfile
FROM ollama/ollama:latest

# Listen on all interfaces and keep models warm
ENV OLLAMA_HOST=0.0.0.0:11434 \
    OLLAMA_KEEP_ALIVE=24h \
    OLLAMA_MODELS=""

# Simple entrypoint that starts the server, waits until ready, then pulls models
# Usage: set OLLAMA_MODELS="llama3.1:8b,nomic-embed-text,mistral:7b" (comma/space separated)
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl jq ca-certificates && \
    rm -rf /var/lib/apt/lists/*

COPY docker-entrypoint.sh /usr/local/bin/docker-entrypoint.sh
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

EXPOSE 11434

# Healthcheck hits /api/tags
HEALTHCHECK --interval=30s --timeout=5s --retries=10 \
  CMD curl -fsS http://127.0.0.1:11434/api/tags >/dev/null || exit 1

ENTRYPOINT ["docker-entrypoint.sh"]
