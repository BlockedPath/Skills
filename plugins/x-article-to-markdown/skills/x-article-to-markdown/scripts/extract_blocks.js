// Browser-side extractor for X (Twitter) long-form Articles.
//
// Returns raw, ordered content items with their MEASURED computed styles. We
// deliberately read getComputedStyle (font-size/weight/style/family/decoration)
// instead of trusting tag names or CSS classes, because X encodes headings/
// bold/italic with auto-generated utility classes (r-1ttztb7 ...) that rotate
// between deploys. Computed style is what the reader actually sees, so it is the
// stable signal. All semantic classification (heading levels, list grouping,
// captions) happens in Python from this raw data — keep this file dumb.
() => {
  const read = document.querySelector('[data-testid="twitterArticleReadView"]');
  const body =
    document.querySelector('[data-testid="twitterArticleRichTextView"]') || read;
  if (!body) return { error: 'no-article-body' };

  // ---------- metadata (author chrome lives in the header, not the body) ----------
  const titleEl = document.querySelector('[data-testid="twitter-article-title"]');
  const title = titleEl ? titleEl.innerText.trim() : '';

  let author = '', handle = '';
  const uc = read && read.querySelector('[data-testid="UserCell"]');
  if (uc) {
    const lines = uc.innerText.split('\n').map(s => s.trim()).filter(Boolean);
    author = lines[0] || '';
    handle = lines.find(l => l.startsWith('@')) || '';
  }
  if (!handle) {
    const av = read && read.querySelector('[data-testid^="UserAvatar-Container-"]');
    const m = av && av.getAttribute('data-testid').match(/UserAvatar-Container-(.+)/);
    if (m) handle = '@' + m[1];
  }
  const timeEl = read && read.querySelector('time');
  const date = timeEl ? (timeEl.getAttribute('datetime') || timeEl.innerText.trim()) : '';

  // ---------- helpers ----------
  const BLOCK_DISP = new Set(['block', 'flex', 'list-item', 'grid', 'table']);
  const isBlock = el => {
    if (!el || el === body) return el === body;
    if (el.tagName === 'LI') return true;
    return BLOCK_DISP.has(getComputedStyle(el).display);
  };
  const nearestBlock = el => {
    while (el && el !== body) {
      if (isBlock(el)) return el;
      el = el.parentElement;
    }
    return body;
  };
  const listDepth = el => {
    let d = 0, p = el;
    while (p && p !== body) {
      if (p.tagName === 'UL' || p.tagName === 'OL') d++;
      p = p.parentElement;
    }
    return d;
  };
  const mediaId = u => {
    const m = (u || '').match(/\/media\/([^?/.]+)/);
    return m ? m[1] : (u || null);
  };
  const isContentImg = im =>
    im && im.tagName === 'IMG' &&
    im.closest('[data-testid="tweetPhoto"]') &&
    !im.closest('[data-testid^="UserAvatar"]');

  const seenImg = new Set();
  const seenCode = new Set();

  // ---------- cover image(s): tweetPhoto in the read view but OUTSIDE the body ----------
  const cover = [];
  if (read) {
    read.querySelectorAll('[data-testid="tweetPhoto"] img').forEach(im => {
      if (body.contains(im) || im.closest('[data-testid^="UserAvatar"]')) return;
      const id = mediaId(im.currentSrc || im.src);
      if (seenImg.has(id)) return;
      seenImg.add(id);
      cover.push({ kind: 'image', src: im.src, alt: im.alt || '' });
    });
  }

  // ---------- ordered walk of body: text nodes + inline images in document order ----------
  const items = [];
  let curEl = null, cur = null;
  const walker = document.createTreeWalker(
    body, NodeFilter.SHOW_ELEMENT | NodeFilter.SHOW_TEXT);
  let node;
  while ((node = walker.nextNode())) {
    if (node.nodeType === Node.ELEMENT_NODE) {
      // Code block: <div data-testid="markdown-code-block"> [lang label] <pre>code</pre>
      // The <pre> innerText preserves whitespace/newlines — grab it as one unit and
      // skip walking inside (otherwise each token becomes a mangled inline-code run).
      if (node.matches && node.matches('[data-testid="markdown-code-block"]') && !seenCode.has(node)) {
        seenCode.add(node);
        const pre = node.querySelector('pre');
        const code = (pre ? pre.innerText : node.innerText).replace(/\s+$/, '');
        let lang = '';
        const first = node.firstElementChild;
        if (first && first.tagName !== 'PRE') lang = (first.innerText || '').trim().split('\n')[0];
        items.push({ kind: 'code', lang, text: code });
        curEl = null; cur = null;
        continue;
      }
      if (isContentImg(node)) {
        const id = mediaId(node.currentSrc || node.src);
        if (!seenImg.has(id)) {
          seenImg.add(id);
          items.push({ kind: 'image', src: node.src, alt: node.alt || '' });
        }
        curEl = null; cur = null;
      }
      continue;
    }
    const raw = node.textContent;
    if (!raw || !raw.trim()) continue;
    if (node.parentElement.closest('[data-testid="markdown-code-block"]')) continue;
    const blockEl = nearestBlock(node.parentElement);
    if (blockEl !== curEl) {
      const cs = getComputedStyle(blockEl);
      curEl = blockEl;
      cur = {
        kind: 'block',
        tag: blockEl.tagName,
        li: blockEl.tagName === 'LI' || !!node.parentElement.closest('li'),
        ordered: !!node.parentElement.closest('ol'),
        depth: listDepth(node.parentElement),
        size: parseFloat(cs.fontSize) || 0,
        runs: [],
      };
      items.push(cur);
    }
    const p = node.parentElement;
    const cs = getComputedStyle(p);
    const a = p.closest('a[href]');
    cur.runs.push({
      text: raw,
      bold: (parseInt(cs.fontWeight) || 400) >= 600,
      italic: cs.fontStyle === 'italic',
      strike: /line-through/.test(cs.textDecorationLine || ''),
      code: /\bmono\b|monospace/i.test(cs.fontFamily || ''),
      href: a ? a.href : null,
      size: parseFloat(cs.fontSize) || 0,
    });
  }

  return { url: location.href, meta: { title, author, handle, date }, cover, items };
}
