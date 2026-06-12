# X Article DOM map

Read this when output looks wrong and you suspect X changed its markup. The
extractor (`scripts/extract_blocks.js`) anchors on the `data-testid` values below
— these are far more stable than the `css-*` / `r-*` utility classes, which are
auto-generated and rotate between deploys. **Never key off those classes.**

## Stable anchors (`data-testid`)
| testid | role | used for |
|---|---|---|
| `twitterArticleReadView` | full read view (title + author header + body) | metadata + cover-image scope |
| `twitterArticleRichTextView` | the article **body** only | block/text extraction scope |
| `twitter-article-title` | the title | `# H1` + frontmatter |
| `UserCell` | author header (name / @handle / bio) | author + handle metadata |
| `UserAvatar-Container-<handle>` | author avatar; handle is in the testid | handle fallback; EXCLUDE from images |
| `tweetPhoto` | wraps a content image | image detection (vs avatars) |
| `markdown-code-block` | wraps a code block: `[lang label] <pre><code>…` | fenced ``` block |
| `time` (tag) inside read view | publish timestamp | `date` metadata |

## How formatting is encoded
- **Semantic & reliable:** `<ul>/<ol>/<li>` (lists), `<a href>` (links), `<img>`.
- **NOT semantic** — there are no `<h1>/<strong>/<em>/<blockquote>/<hr>` tags.
  Headings, bold, and italics are styled `div`/`span`. We recover them from
  **computed style**:
  - bold ⟸ `font-weight ≥ 600`
  - italic ⟸ `font-style: italic`
  - strikethrough ⟸ `text-decoration-line: line-through`
  - inline code ⟸ `font-family` contains "mono"
  - heading ⟸ block `font-size ≥ ~1.18× the body's dominant font-size`
    (self-calibrating; distinct larger sizes map to `#`, `##`, … by rank)

## Images
- Content images: `pbs.twimg.com/media/<id>?...&name=<size>`. Request `name=orig`
  for full resolution. A `tweetPhoto` may contain a blurred placeholder **and**
  the real image (same `<id>`) — dedupe by the media `<id>`.
- **Cover image**: a `tweetPhoto` that is inside `twitterArticleReadView` but NOT
  inside `twitterArticleRichTextView`. Placed at the top of the output.
- Author avatars (`pbs.twimg.com/profile_images/...`, 96×96, under
  `UserAvatar-*`) are NOT article content — exclude them.
- Captions: a small (≈13px) text block immediately following an image is treated
  as that image's caption and rendered as an italic line beneath it.

## Code blocks
- Wrapped in `[data-testid="markdown-code-block"]` = a language-label div followed
  by a `<pre style="white-space:pre">`. **Take `pre.innerText`** — it preserves
  newlines and indentation. Do NOT walk the inner token `<span>`s: they're
  syntax-highlight fragments and whitespace-collapsing mangles them (e.g.
  "npm install" → "npminstall"). The label div's text is the fence language.

## Videos
- Embedded videos appear as a poster frame `<img>` under `tweetPhoto`, served from
  `pbs.twimg.com/amplify_video_thumb/<id>/img/<name>.jpg`. We save the poster as a
  normal image (Markdown can't embed video). Filenames come from the URL basename,
  so they don't collide with each other or with `/media/` photos.

## Known gaps / TODO
- **Blockquotes** aren't handled yet — none of the sampled articles contained one,
  so X's encoding is unconfirmed (likely a styled `border-left` container). Add it
  against a real sample rather than guessing.

## Layout order (top → bottom)
cover image → title → author byline + date → body (paragraphs, bold section
markers, lists, inline images+captions, dividers).

## If X changes things
1. Re-run the scraper with `--dump-blocks` and open `blocks.json`.
2. If `meta.title`/`author` are empty or the body is missing, the `data-testid`
   names above likely changed — update the selectors in `extract_blocks.js`.
   Find the new names by opening an article in the debug Chrome and inspecting
   `document.querySelectorAll('[data-testid]')`.
3. The computed-style mapping in `x_render.py` rarely needs changing — it keys on
   rendered font metrics, not markup.
