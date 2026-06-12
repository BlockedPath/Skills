---
name: x-article-to-markdown
description: >-
  Scrape an X.com (Twitter) long-form Article into a local Markdown file that
  faithfully preserves its on-page structure — title, author byline, headings,
  bold/italic, ordered & bulleted lists, blockquotes, dividers, links, and
  images (downloaded locally so it renders offline). Use this whenever the user
  wants to save, scrape, download, archive, convert, back up, or "make a local
  copy" of an X.com / Twitter Article — especially when they paste a URL like
  x.com/USERNAME/article/ID (or twitter.com/.../article/...) and ask to grab,
  read offline, or turn it into Markdown. X Articles are login-gated and rendered
  in-browser, so this skill drives the user's already-logged-in Chrome via the
  DevTools protocol (CDP). Trigger even if the user only says "save this X
  article" or "convert this thread/article to markdown" with a link.
---

# X Article → Markdown

Convert an X (Twitter) long-form **Article** into a faithful local Markdown file
plus a folder of downloaded images.

## Why this needs a browser (read once)

X Articles are a Premium feature that is **login-gated and 100% client-rendered**.
The raw HTML is an empty app shell (a plain fetch returns nothing; a logged-out
visit redirects to the login page). So there is no API or `curl` shortcut — the
only reliable way to read an Article is a **real browser that is logged into X**.

This skill attaches to a Chrome you control over the **DevTools protocol (CDP)**
and reads the rendered page. Crucially, it classifies formatting by the text's
**computed style** (`getComputedStyle` font-size/weight/style) rather than X's CSS
class names, which are auto-generated and rotate between deploys. That makes the
converter resilient to X's frequent markup churn.

## One-time setup

1. **Install the dependency** into a dedicated venv (no browser download needed —
   we attach to your existing Chrome). This sidesteps Homebrew/system
   "externally-managed Python" errors:
   ```bash
   bash scripts/setup.sh
   ```
   (The scraper auto-uses this venv at `~/.cache/x-scrape-venv`, so you keep
   calling it with plain `python3` — it re-execs itself into the venv.)
2. **Start a logged-in debug Chrome.** Run the helper, which opens a *separate*
   Chrome window using a dedicated profile (it won't disturb your normal browser):
   ```bash
   bash scripts/launch_chrome.sh
   ```
   The first time, **log into x.com** in that window. The session persists in the
   profile dir (`~/.cache/x-scrape-chrome`), so you won't need to log in again.
   If a debug Chrome is already running on the port, the helper just reuses it.

> Already have a Chrome running with `--remote-debugging-port=9222` and logged
> into X? You can skip the helper and point the scraper at it with `--cdp-url`.

## Usage

```bash
python3 scripts/scrape_x_article.py "<article_url>" [--out DIR]
```

Example:
```bash
python3 scripts/scrape_x_article.py \
  "https://x.com/karpathy/article/2002118205729562949"
```

With no `--out`, it creates a folder named from the article's title slug in the
current directory:
```
2025-llm-year-in-review/                # ← the slug folder (default only)
├── 2025-llm-year-in-review.md          # YAML frontmatter + faithful body
└── images/
    ├── G8jw86Fa8AAixGt.jpg             # cover + inline images, full resolution
    └── G8jxfzSWQAAqhII.jpg
```
With `--out DIR`, the `.md` and `images/` are written **directly into DIR** (no
extra slug subfolder): `DIR/<slug>.md` + `DIR/images/`.

The `.md` opens cleanly in any Markdown viewer (VS Code, Obsidian, GitHub) and
mirrors the article: title as `#`, author/date byline, paragraphs, **bold**,
*italics*, lists, `> quotes`, `---` dividers, `[links](…)`, and `![images](…)`
pointing at the local files.

### Useful flags
- `--out DIR` — write to a specific directory.
- `--cdp-url URL` — attach to a different debug Chrome (default `http://localhost:9222`).
- `--no-images` — skip downloading images (keep remote URLs).
- `--dump-blocks` — also emit `blocks.json` (the raw extracted structure; handy
  for debugging or when adapting to an X markup change).

## How it works (pipeline)

1. **Attach** to the logged-in Chrome via CDP (`scrape_x_article.py`).
2. **Render & extract** — navigate, scroll to trigger lazy images, then run
   `scripts/extract_blocks.js` in the page. That returns the title, author/handle/
   date, cover image(s), and an ordered list of body items, each annotated with
   its measured computed style. (Lists, links, and images are read from semantic
   tags; headings/bold/italic are inferred from computed font metrics.)
3. **Render** — `scripts/x_render.py` (pure, no browser) turns that structure into
   Markdown. Heading detection is **self-calibrating**: it finds the body's
   dominant font-size and treats only meaningfully larger text as a heading, so it
   adapts across articles without hardcoded pixel values.
4. **Download images** at full resolution (`name=orig`) into `images/` and rewrite
   the Markdown to relative paths, so the file is self-contained and renders offline.

## Verifying fidelity (optional)

To eyeball the result against the live page, render the Markdown to a styled
preview and screenshot it:
```bash
python3 -m pip install markdown        # only needed for the preview
# see references/preview.md for a ready-to-use preview snippet
```

## Troubleshooting

- **"could not connect to Chrome at http://localhost:9222"** — the debug Chrome
  isn't running. Run `bash scripts/launch_chrome.sh`.
- **"Chrome is not logged into X (redirected to login)"** — log into x.com in the
  debug Chrome window, then re-run.
- **"article body did not render"** — confirm the URL is an *Article*
  (`x.com/<user>/article/<id>`), not a regular tweet/status. Regular tweets have a
  different structure this skill doesn't target.
- **Output looks wrong after an X update** — X changed its DOM. Re-run with
  `--dump-blocks` and inspect `blocks.json`; the stable anchors and how to adapt
  are documented in `references/dom-structure.md`.

## Reference files
- `references/dom-structure.md` — the X Article DOM map (stable `data-testid`
  anchors, how formatting is encoded, what to update if X changes its markup).
- `references/preview.md` — snippet to render the Markdown to a styled HTML
  preview for side-by-side comparison with the live article.
