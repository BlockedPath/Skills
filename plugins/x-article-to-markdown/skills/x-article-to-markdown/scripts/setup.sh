#!/usr/bin/env bash
# One-time setup: create a dedicated venv and install Playwright (the only
# dependency). No browser download is needed — the scraper attaches to your
# existing Chrome over CDP. `markdown` is included for the optional preview.
set -euo pipefail
VENV="${X_SCRAPE_VENV:-$HOME/.cache/x-scrape-venv}"

if [ ! -x "$VENV/bin/python" ]; then
  echo "Creating venv at $VENV"
  python3 -m venv "$VENV"
fi
"$VENV/bin/python" -m pip install --quiet --upgrade pip
"$VENV/bin/python" -m pip install --quiet playwright markdown
echo "✓ Setup complete."
"$VENV/bin/python" -c "import importlib.metadata as m; print('  playwright', m.version('playwright'), 'at $VENV')"
echo "Next: bash scripts/launch_chrome.sh   (log into X once), then run scrape_x_article.py"
