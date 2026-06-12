#!/usr/bin/env bash
# Launch (or reuse) a Chrome with remote debugging enabled, using a dedicated
# persistent profile, so the X article scraper can drive a logged-in session.
#
# First run: a Chrome window opens — log into x.com once. The login persists in
# the profile dir, so future runs reuse it (no re-login). This is a SEPARATE
# Chrome instance from your everyday browser; it won't disturb your normal tabs.
#
#   ./launch_chrome.sh                 # launch/reuse, open x.com
#   X_SCRAPE_PORT=9333 ./launch_chrome.sh
#
# Env: X_SCRAPE_PORT (default 9222), X_SCRAPE_PROFILE (default ~/.cache/x-scrape-chrome)
set -euo pipefail
PORT="${X_SCRAPE_PORT:-9222}"
PROFILE="${X_SCRAPE_PROFILE:-$HOME/.cache/x-scrape-chrome}"
URL="${1:-https://x.com/home}"

if curl -s --max-time 2 "http://localhost:${PORT}/json/version" >/dev/null 2>&1; then
  echo "✓ Chrome already listening on :${PORT} — reusing it."
  echo "  (If it's not logged into X, log in in that window, then re-run the scraper.)"
  exit 0
fi

CHROME=""
for c in \
  "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
  "/Applications/Google Chrome Canary.app/Contents/MacOS/Google Chrome Canary" \
  "/Applications/Chromium.app/Contents/MacOS/Chromium" \
  "$(command -v google-chrome 2>/dev/null || true)" \
  "$(command -v chromium 2>/dev/null || true)" \
  "$(command -v chromium-browser 2>/dev/null || true)"; do
  if [ -n "$c" ] && [ -x "$c" ]; then CHROME="$c"; break; fi
done
if [ -z "$CHROME" ]; then
  echo "ERROR: Could not find Google Chrome / Chromium." >&2
  echo "Install Chrome, or set CHROME to its path and edit this script." >&2
  exit 1
fi

mkdir -p "$PROFILE"
echo "Launching Chrome on :${PORT}"
echo "  binary : $CHROME"
echo "  profile: $PROFILE"
echo "  → If this is the first run, LOG INTO x.com in the window that opens."
"$CHROME" \
  --remote-debugging-port="${PORT}" \
  --user-data-dir="${PROFILE}" \
  --no-first-run --no-default-browser-check \
  "$URL" >/dev/null 2>&1 &

for _ in $(seq 1 20); do
  if curl -s --max-time 1 "http://localhost:${PORT}/json/version" >/dev/null 2>&1; then
    echo "✓ Debug port ready on :${PORT} (pid $!)."
    exit 0
  fi
  sleep 0.5
done
echo "Chrome launched (pid $!) but :${PORT} isn't responding yet — give it a moment." >&2
