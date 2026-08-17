#!/bin/sh
# withEve rewrites /eve/* to the Nitro server on 4274. next start does not
# spawn that process in this image, so start it first.
set -eu

EVE_RUNTIME_PORT="${EVE_NEXT_PRODUCTION_PORT:-4274}"
eve_pid=""

term() {
  if [ -n "$eve_pid" ]; then
    kill "$eve_pid" 2>/dev/null || true
    wait "$eve_pid" 2>/dev/null || true
  fi
}

trap term INT TERM

PORT="$EVE_RUNTIME_PORT" \
  HOST=127.0.0.1 \
  NITRO_PORT="$EVE_RUNTIME_PORT" \
  NITRO_HOST=127.0.0.1 \
  node /app/.output/server/index.mjs &
eve_pid=$!

i=0
while [ "$i" -lt 60 ]; do
  if node -e "fetch('http://127.0.0.1:${EVE_RUNTIME_PORT}/eve/v1/health').then((r) => process.exit(r.ok ? 0 : 1)).catch(() => process.exit(1))"; then
    break
  fi
  i=$((i + 1))
  sleep 0.5
done

pnpm exec next start --hostname 0.0.0.0 --port 3000 &
next_pid=$!
wait "$next_pid"
status=$?
term
exit "$status"
