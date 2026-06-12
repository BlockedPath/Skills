# Preview: render the Markdown and compare to the live article

Use this to verify structural fidelity. It converts the scraped `.md` to a styled
HTML page (approximating X's reading column) and screenshots it via the same
debug Chrome. Exact fonts/margins will differ from X — that's expected for
"faithful structural markdown"; what you're checking is that all content, order,
and formatting survived.

```bash
python3 -m pip install markdown
python3 - "<path-to>.md" <<'PY'
import sys, re
from pathlib import Path
import markdown
from playwright.sync_api import sync_playwright

md = Path(sys.argv[1])
text = re.sub(r"^---\n.*?\n---\n", "", md.read_text(encoding="utf-8"), count=1, flags=re.S)
body = markdown.markdown(text, extensions=["extra", "sane_lists", "nl2br"])
CSS = """body{background:#fff;color:#0f1419;margin:0;padding:32px 0;
font-family:-apple-system,'Segoe UI',Roboto,Helvetica,Arial,sans-serif}
.col{max-width:680px;margin:0 auto;padding:0 16px;font-size:17px;line-height:1.6}
h1{font-size:34px;font-weight:800;line-height:1.2}img{max-width:100%;height:auto;
border-radius:12px;display:block;margin:16px auto}a{color:#1d9bf0;text-decoration:none}
em{color:#536471}hr{border:none;border-top:1px solid #eee;margin:2em 0}
code{font-family:ui-monospace,Menlo,monospace;background:#f5f8fa;padding:1px 4px;border-radius:4px}"""
html = f"<!doctype html><meta charset=utf-8><style>{CSS}</style><div class=col>{body}</div>"
out = md.parent / "preview.html"; out.write_text(html, encoding="utf-8")
with sync_playwright() as p:
    b = p.chromium.connect_over_cdp("http://localhost:9222")
    pg = b.contexts[0].new_page()
    pg.goto(out.resolve().as_uri(), wait_until="networkidle"); pg.wait_for_timeout(500)
    pg.screenshot(path=str(md.parent / "preview.png"), full_page=True); pg.close()
print("wrote", out, "and preview.png")
PY
```
