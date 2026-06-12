#!/usr/bin/env python3
"""Offline self-test for the Markdown renderer (no browser/network).

Exercises the formatting paths a thin article may not cover — headings (by
computed size), italic/strike/code, links, nested lists, image captions, and
dividers — so regressions surface without needing a live scrape.

Run:  python3 scripts/selftest.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import x_render

DATA = {
    "url": "https://x.com/test/article/123",
    "meta": {"title": "Test Article", "author": "Jane Doe",
             "handle": "@jane", "date": "2025-06-01T12:00:00.000Z"},
    "cover": [{"kind": "image", "src": "https://pbs.twimg.com/media/COVER?format=jpg&name=medium", "alt": ""}],
    "items": [
        {"kind": "block", "li": False, "ordered": False, "depth": 0, "size": 28,
         "runs": [{"text": "A Real Heading", "bold": True, "size": 28}]},
        {"kind": "block", "li": False, "ordered": False, "depth": 0, "size": 17, "runs": [
            {"text": "Plain then ", "size": 17},
            {"text": "bold", "bold": True, "size": 17},
            {"text": ", ", "size": 17},
            {"text": "italic", "italic": True, "size": 17},
            {"text": ", ", "size": 17},
            {"text": "struck", "strike": True, "size": 17},
            {"text": ", ", "size": 17},
            {"text": "mono", "code": True, "size": 17},
            {"text": " and a ", "size": 17},
            {"text": "link", "href": "https://example.com", "size": 17},
            {"text": ".", "size": 17},
        ]},
        {"kind": "block", "li": True, "ordered": True, "depth": 1, "size": 17, "runs": [{"text": "First", "size": 17}]},
        {"kind": "block", "li": True, "ordered": True, "depth": 1, "size": 17, "runs": [{"text": "Second", "size": 17}]},
        {"kind": "block", "li": True, "ordered": False, "depth": 2, "size": 17, "runs": [{"text": "Nested bullet", "size": 17}]},
        {"kind": "block", "li": True, "ordered": True, "depth": 1, "size": 17, "runs": [{"text": "Third", "size": 17}]},
        {"kind": "code", "lang": "python", "text": "def hi():\n    return 1"},
        {"kind": "image", "src": "https://pbs.twimg.com/media/INLINE?format=jpg&name=medium", "alt": "Image"},
        {"kind": "block", "li": False, "ordered": False, "depth": 0, "size": 13, "runs": [{"text": "a caption", "size": 13}]},
        {"kind": "block", "li": False, "ordered": False, "depth": 0, "size": 17, "runs": [{"text": "---", "size": 17}]},
        {"kind": "block", "li": False, "ordered": False, "depth": 0, "size": 17, "runs": [{"text": "Final paragraph.", "size": 17}]},
    ],
}

md = x_render.render_markdown(DATA, image_map={
    "https://pbs.twimg.com/media/COVER?format=jpg&name=medium": "images/COVER.jpg"})

CHECKS = [
    ("heading by size -> ##", "## A Real Heading" in md),
    ("bold run", "**bold**" in md),
    ("italic run", "*italic*" in md),
    ("strikethrough run", "~~struck~~" in md),
    ("inline code run", "`mono`" in md),
    ("link run", "[link](https://example.com)" in md),
    ("ordered item 1", "1. First" in md),
    ("ordered item 2", "2. Second" in md),
    ("nested bullet indented", "    - Nested bullet" in md),
    ("ordered numbering resumes after nest", "3. Third" in md),
    ("inline image rendered", "](https://pbs.twimg.com/media/INLINE" in md or "INLINE" in md),
    ("image caption italicised", "*a caption*" in md),
    ("divider", "\n---\n" in md),
    ("fenced code block w/ lang", "```python\ndef hi():\n    return 1\n```" in md),
    ("cover image before title", md.index("COVER.jpg") < md.index("# Test Article")),
    ("title h1", "# Test Article" in md),
    ("pretty byline date", "Jun 1, 2025" in md),
]

fails = [name for name, ok in CHECKS if not ok]
for name, ok in CHECKS:
    print(f"  {'PASS' if ok else 'FAIL'}  {name}")
if fails:
    print(f"\n{len(fails)} FAILED\n\n--- rendered markdown ---\n{md}")
    sys.exit(1)
print(f"\nAll {len(CHECKS)} checks passed.")
