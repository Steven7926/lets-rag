#!/bin/sh
set -eu

ollama serve &
PID=$!

echo "Waiting for Ollama..."
for i in $(seq 1 60); do
  if curl -sf http://127.0.0.1:11434/api/tags >/dev/null; then
    echo "Ollama ready."
    break
  fi
  sleep 1
done

if [ -n "${OLLAMA_MODELS:-}" ]; then
  for m in $(echo "$OLLAMA_MODELS" | tr ',;' ' '); do
    [ -z "$m" ] && continue
    echo "Pulling $m..."
    ollama pull "$m"
  done
fi

wait "$PID"
