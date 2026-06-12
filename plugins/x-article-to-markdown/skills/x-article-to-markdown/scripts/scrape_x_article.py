#!/usr/bin/env python3
"""Scrape an X (Twitter) long-form Article into faithful local Markdown.

Connects to a Chrome you're already logged into via the DevTools protocol
(CDP), renders the article, extracts content by MEASURED computed style
(robust to X's rotating CSS classes), downloads images at full resolution,
and writes a Markdown file that mirrors the article's structure.

Usage:
    python scrape_x_article.py <article_url> [--out DIR] [--cdp-url URL]

Prereq: a Chrome started with remote debugging, logged into X, e.g.
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \\
        --remote-debugging-port=9222 --user-data-dir="$HOME/.x-scrape-chrome"
See SKILL.md for the full setup.
"""
from __future__ import annotations
import argparse, json, os, re, sys
from pathlib import Path


def _bootstrap():
    """Make `python3 scripts/scrape_x_article.py` 'just work'. If Playwright
    isn't importable, re-exec under the dedicated venv created by setup.sh
    (avoids fighting Homebrew/system 'externally-managed' Python)."""
    try:
        import playwright  # noqa: F401
        return
    except ImportError:
        pass
    venv = os.environ.get("X_SCRAPE_VENV", os.path.expanduser("~/.cache/x-scrape-venv"))
    venv_py = os.path.join(venv, "bin", "python")
    # Guard with an env flag (not a realpath check): a venv's python is a symlink
    # to the same base interpreter, so realpath equality is unreliable. The flag
    # also guarantees we re-exec at most once.
    if os.path.exists(venv_py) and os.environ.get("X_SCRAPE_REEXEC") != "1":
        os.environ["X_SCRAPE_REEXEC"] = "1"
        os.execv(venv_py, [venv_py, *sys.argv])
    sys.stderr.write(
        "ERROR: the 'playwright' package isn't installed.\n"
        "Run this once:  bash scripts/setup.sh\n"
        "(creates a small venv and installs Playwright — no browser download needed).\n")
    sys.exit(2)


_bootstrap()
from playwright.sync_api import sync_playwright  # noqa: E402
import x_render  # noqa: E402

DEFAULT_CDP = "http://localhost:9222"
HERE = Path(__file__).parent
EXTRACT_JS = (HERE / "extract_blocks.js").read_text(encoding="utf-8")


def slugify(text: str, fallback: str) -> str:
    s = re.sub(r"[^\w\s-]", "", (text or "").lower()).strip()
    s = re.sub(r"[\s_-]+", "-", s)
    return s[:80].strip("-") or fallback


def hires(url: str) -> str:
    """Ask X's media CDN for the original resolution."""
    if "pbs.twimg.com/media/" not in url:
        return url
    url = re.sub(r"([?&])name=\w+", r"\1name=orig", url)
    if "name=" not in url:
        url += ("&" if "?" in url else "?") + "name=orig"
    return url


def media_filename(url: str) -> str:
    # Use the URL path's basename so distinct assets get distinct names. Handles
    # /media/<id> (photos) and /amplify_video_thumb/<id>/img/<name>.jpg (video
    # poster frames), which otherwise both collapsed to "image".
    from urllib.parse import urlsplit
    path = urlsplit(url).path
    base = path.rstrip("/").rsplit("/", 1)[-1]
    stem = re.sub(r"\.\w+$", "", base) or "image"
    fmt = re.search(r"format=(\w+)", url)
    path_ext = re.search(r"\.(\w+)$", base)
    ext = (fmt.group(1) if fmt else (path_ext.group(1) if path_ext else "jpg"))
    return f"{stem}.{ext.replace('jpeg', 'jpg')}"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("url")
    ap.add_argument("--out", default=None, help="output directory (default: ./<slug>)")
    ap.add_argument("--cdp-url", default=DEFAULT_CDP)
    ap.add_argument("--no-images", action="store_true")
    ap.add_argument("--dump-blocks", action="store_true",
                    help="also write blocks.json (handy for debugging/tests)")
    args = ap.parse_args()

    with sync_playwright() as p:
        try:
            browser = p.chromium.connect_over_cdp(args.cdp_url)
        except Exception as e:
            print(f"ERROR: could not connect to Chrome at {args.cdp_url}\n  {e}\n\n"
                  "Start Chrome (logged into X) with remote debugging — see SKILL.md.",
                  file=sys.stderr)
            return 3
        ctx = browser.contexts[0] if browser.contexts else browser.new_context()
        page = ctx.new_page()
        # An Article is addressable as /status/<id> or /article/<id> (same id).
        # The /article/ reader is more stable to scrape than the /status/ tweet
        # page (which can load a reply thread), so normalize to it.
        target = re.sub(r"/status/(\d+)", r"/article/\1", args.url)
        page.goto(target, wait_until="domcontentloaded")
        try:
            page.wait_for_selector('[data-testid="twitterArticleRichTextView"]', timeout=20000)
        except Exception:
            if re.search(r"/i/(flow/login|jf/onboarding)", page.url) or "login" in page.url:
                print("ERROR: Chrome is not logged into X (redirected to login).\n"
                      "Log into x.com in that Chrome window, then re-run.", file=sys.stderr)
                return 4
            print("ERROR: article body did not render. Is the URL an X Article "
                  "(x.com/<user>/article/<id>)?", file=sys.stderr)
            page.close(); return 5

        # trigger lazy-loaded images
        for _ in range(14):
            page.mouse.wheel(0, 1600)
            page.wait_for_timeout(300)
        page.wait_for_timeout(800)

        data = page.evaluate(EXTRACT_JS)
        if data.get("error"):
            print(f"ERROR: extraction failed ({data['error']})", file=sys.stderr)
            page.close(); return 6

        title = data.get("meta", {}).get("title", "")
        art_id = re.search(r"/article/(\d+)", args.url)
        slug = slugify(title, art_id.group(1) if art_id else "x-article")
        out_dir = Path(args.out) if args.out else Path.cwd() / slug
        out_dir.mkdir(parents=True, exist_ok=True)

        # download images
        image_map = {}
        imgs = data.get("cover", []) + [it for it in data["items"] if it.get("kind") == "image"]
        if imgs and not args.no_images:
            img_dir = out_dir / "images"
            img_dir.mkdir(exist_ok=True)
            used = set()
            for it in imgs:
                src = it["src"]
                if src in image_map:        # same asset referenced twice
                    continue
                try:
                    resp = ctx.request.get(hires(src))
                    if resp.ok:
                        fn = media_filename(src)
                        while fn in used:   # guarantee uniqueness on disk
                            stem, _, ext = fn.rpartition(".")
                            n = sum(1 for u in used if u.startswith(stem)) + 1
                            fn = f"{stem}-{n}.{ext}"
                        used.add(fn)
                        (img_dir / fn).write_bytes(resp.body())
                        image_map[src] = f"images/{fn}"
                        print(f"  image -> images/{fn}")
                    else:
                        print(f"  WARN image {resp.status}: {src}", file=sys.stderr)
                except Exception as e:
                    print(f"  WARN image failed ({e}): {src}", file=sys.stderr)

        md = x_render.render_markdown(data, image_map=image_map)
        md_path = out_dir / f"{slug}.md"
        md_path.write_text(md, encoding="utf-8")
        if args.dump_blocks:
            (out_dir / "blocks.json").write_text(json.dumps(data, indent=2), encoding="utf-8")

        page.close()
        print(f"\nSaved: {md_path}  ({len(md)} chars, {len(image_map)} images)")
        return 0


if __name__ == "__main__":
    sys.exit(main())
