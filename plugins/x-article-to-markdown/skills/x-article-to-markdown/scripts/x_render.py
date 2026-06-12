"""Pure rendering: turn the raw extracted article data into faithful Markdown.

No browser, no network here — that makes it unit-testable on a saved blocks.json.
Classification is self-calibrating: we find the body's dominant font-size and
judge everything relative to it, so the converter works across articles without
hardcoding pixel values or X's rotating CSS class names.
"""
from __future__ import annotations
import re
from collections import Counter
from datetime import datetime

_DASHES = set("-–—_*•· ")


def _pretty_date(s: str) -> str:
    try:
        return datetime.fromisoformat(s.replace("Z", "+00:00")).strftime("%b %-d, %Y")
    except Exception:
        return s

HEADING_RATIO = 1.18   # a block this much larger than body text is a heading
CAPTION_MAX_PX = 14.5   # small text right after an image is treated as a caption


# ---------------------------------------------------------------- inline runs
def _merge_runs(runs):
    """Merge adjacent runs that share identical formatting, so we don't emit
    `**a****b**`. Whitespace-only runs inherit neighbours to avoid breaking
    emphasis spans."""
    out = []
    for r in runs:
        key = (r.get("bold"), r.get("italic"), r.get("strike"),
               r.get("code"), r.get("href"))
        if out and out[-1][0] == key:
            out[-1][1] += r["text"]
        else:
            out.append([key, r["text"]])
    return out


def _esc(t: str) -> str:
    # Light escaping: enough to keep prose from being misread as markdown,
    # without turning the source into backslash soup. The user reads the
    # RENDERED file, so escaped chars still display correctly.
    return (t.replace("\\", "\\\\")
             .replace("`", "\\`")
             .replace("*", "\\*"))


def _wrap(text: str, left: str, right: str) -> str:
    """Wrap, shifting surrounding whitespace OUTSIDE the markers
    (`** bold **` is invalid; ` **bold** ` is what we want)."""
    if not text.strip():
        return text
    lead = text[:len(text) - len(text.lstrip())]
    trail = text[len(text.rstrip()):]
    return f"{lead}{left}{text.strip()}{right}{trail}"


def render_inline(runs, drop_bold: bool = False) -> str:
    # drop_bold: headings are emitted with `#` and are already visually bold on
    # X, so wrapping their text in `**` too would double up (`## **Title**`).
    parts = []
    for (bold, italic, strike, code, href), text in _merge_runs(runs):
        if code:
            t = f"`{text.strip()}`"
            t = (text[:len(text) - len(text.lstrip())] + t +
                 text[len(text.rstrip()):]) if text.strip() else text
        else:
            t = _esc(text)
            if strike:
                t = _wrap(t, "~~", "~~")
            if bold and not drop_bold:
                t = _wrap(t, "**", "**")
            if italic:
                t = _wrap(t, "*", "*")
        if href:
            t = _wrap(t, "[", f"]({href})")
        parts.append(t)
    out = "".join(parts)
    return re.sub(r"[ \t]+", " ", out).strip()


# ------------------------------------------------------------- classification
def _body_size(items) -> float:
    sizes = [round(it["size"]) for it in items
             if it.get("kind") == "block" and not it.get("li") and it.get("size")]
    if not sizes:
        return 17.0
    return float(Counter(sizes).most_common(1)[0][0])


def _heading_levels(items, body):
    """Map the distinct 'large' block sizes to heading levels (largest -> h1)."""
    big = sorted({round(it["size"]) for it in items
                  if it.get("kind") == "block" and not it.get("li")
                  and it["size"] >= body * HEADING_RATIO}, reverse=True)
    return {sz: i + 1 for i, sz in enumerate(big)}  # 1-based; capped later


# ------------------------------------------------------------------ rendering
def _render_list(group) -> str:
    lines, counters = [], {}
    for it in group:
        depth = max(1, it.get("depth", 1))
        for d in list(counters):
            if d > depth:
                del counters[d]
        indent = "    " * (depth - 1)
        text = render_inline(it["runs"])
        if it.get("ordered"):
            counters[depth] = counters.get(depth, 0) + 1
            lines.append(f"{indent}{counters[depth]}. {text}")
        else:
            lines.append(f"{indent}- {text}")
    return "\n".join(lines)


def render_markdown(data: dict, image_map: dict | None = None,
                    frontmatter: bool = True) -> str:
    image_map = image_map or {}
    items = [it for it in data.get("items", []) if not it.get("error")]
    body = _body_size(items)
    hlevels = _heading_levels(items, body)
    meta = data.get("meta", {})

    out = []
    if frontmatter:
        fm = ["---"]
        for k in ("title", "author", "handle", "date"):
            v = (meta.get(k) or "").replace('"', "'")
            if v:
                fm.append(f'{k}: "{v}"')
        if data.get("url"):
            fm.append(f'source: "{data["url"]}"')
        fm.append("---")
        out.append("\n".join(fm))

    for cov in data.get("cover", []):
        src = image_map.get(cov["src"], cov["src"])
        out.append(f"![]({src})")

    if meta.get("title"):
        out.append(f"# {meta['title']}")
        byline = " · ".join(x for x in (meta.get("author"), meta.get("handle"),
                                        _pretty_date(meta.get("date", ""))) if x)
        if byline:
            out.append(f"*{byline}*")

    i, n = 0, len(items)
    while i < n:
        it = items[i]
        if it["kind"] == "code":
            lang = (it.get("lang") or "").strip()
            code = (it.get("text") or "").rstrip("\n")
            fence = "```"
            while fence in code:        # widen the fence if the code contains ```
                fence += "`"
            out.append(f"{fence}{lang}\n{code}\n{fence}")
            i += 1
            continue
        if it["kind"] == "image":
            src = image_map.get(it["src"], it["src"])
            alt = "" if (it.get("alt", "").strip().lower() in ("", "image")) else it["alt"]
            block = f"![{alt}]({src})"
            # absorb a following small text block as the caption
            if i + 1 < n and items[i + 1].get("kind") == "block" \
                    and items[i + 1].get("size", 99) <= CAPTION_MAX_PX \
                    and not items[i + 1].get("li"):
                cap = render_inline(items[i + 1]["runs"])
                if cap:
                    block += f"\n\n*{cap}*"
                i += 1
            out.append(block)
            i += 1
            continue

        if it.get("li"):
            group = []
            while i < n and items[i].get("kind") == "block" and items[i].get("li"):
                group.append(items[i]); i += 1
            out.append(_render_list(group))
            continue

        raw = "".join(r.get("text", "") for r in it["runs"]).strip()
        if len(raw) >= 3 and set(raw) <= _DASHES:
            out.append("---")
            i += 1; continue

        sz = round(it.get("size", body))
        text = render_inline(it["runs"])
        if not text:
            i += 1; continue
        if sz in hlevels:
            level = min(hlevels[sz] + 1, 6)  # +1 because the title is h1
            out.append(f"{'#' * level} {render_inline(it['runs'], drop_bold=True)}")
        else:
            out.append(text)
        i += 1

    md = "\n\n".join(out).rstrip() + "\n"
    return re.sub(r"\n{3,}", "\n\n", md)
