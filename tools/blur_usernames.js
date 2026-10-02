// Blur every username and avatar on the page BEFORE taking the screenshot (Reddit and Letterboxd).
// Run it in the tab with Claude in Chrome's javascript_tool, after the page has loaded and after scrolling to load
// the comments/reviews you need. Run it again after any scroll that loads new content (it skips what is already blurred).
//
//   optional, set before running:  window.__blurNames = ['known_author', ...];   // e.g. the `author` fields from the thread's .json
//                                  window.__blurMode  = 'blur' (default) | 'black';
//
// Why in the page and not on the picture: the screenshot then contains only blurred pixels (nothing to un-blur later), and no
// coordinates have to be mapped from the page to the pinned screenshot frame.
//
// How: (1) walk the document and every open shadow root (Reddit's comments live in shadow DOM); (2) collect author names from
// `author` / `data-author` attributes, Letterboxd display names and profile links, plus window.__blurNames; (3) blur profile links,
// avatar images and name elements by selector; (4) blur the author name wherever it appears in short text (meta lines), a distinctive name anywhere,
// and any `u/name` or `@name` mention in long text; (5) audit: re-scan for any known name still visible and report it (`leftover`), and list plain-word names (`check_by_eye_plain_word_names`) that were blurred only in short text or with u/: look for those by eye in the screenshot.
// The subreddit name and icon (`a[href^="/r/"]`) are left alone: the caption's `Source: r/<subreddit>` needs them.
// Returns a short JSON string (javascript_tool truncates long output). `leftover` must be empty before you screenshot.
(() => {
  const host = location.hostname;
  const site = host.includes('letterboxd') ? 'letterboxd' : 'reddit';
  const mode = window.__blurMode || 'blur';
  const TEXT_STYLE = mode === 'black'
    ? 'background:#000!important;color:#000!important;border-radius:3px!important;user-select:none!important;'
    : 'filter:blur(8px)!important;user-select:none!important;';
  const IMG_STYLE = mode === 'black' ? 'filter:brightness(0)!important;' : 'filter:blur(9px)!important;';
  const roots = [];
  const collect = (root) => {
    roots.push(root);
    root.querySelectorAll('*').forEach((el) => { if (el.shadowRoot) collect(el.shadowRoot); });
  };
  collect(document);
  const all = (sel) => roots.flatMap((r) => Array.from(r.querySelectorAll(sel)));
  const parentOf = (n) => n.parentNode ? (n.parentNode.host && n.parentNode.nodeType === 11 ? n.parentNode.host : n.parentNode) : null;
  const up = (n, test) => { for (let e = n; e; e = parentOf(e)) { if (e.nodeType === 1 && test(e)) return e; } return null; };
  const isSubreddit = (el) => !!up(el, (e) => e.tagName === 'A' && /^\/r\/[^/]+\/?$/.test(e.getAttribute('href') || ''));
  const isBlurred = (n) => !!up(n, (e) => e.hasAttribute && e.hasAttribute('data-blurred'));
  const count = { profile_links: 0, avatars: 0, names: 0, mentions: 0 };
  const blur = (el, kind) => {
    if (!el || el.hasAttribute('data-blurred') || isSubreddit(el)) return;
    const img = /^(IMG|SVG|CANVAS|PICTURE|FACEPLATE-IMG)$/i.test(el.tagName);
    el.setAttribute('style', (el.getAttribute('style') || '') + ';' + (img ? IMG_STYLE : TEXT_STYLE));
    el.setAttribute('data-blurred', kind);
    count[kind]++;
  };

  // 1. names
  const names = new Set((window.__blurNames || []).map(String));
  all('[author], [data-author]').forEach((el) => names.add(el.getAttribute('author') || el.getAttribute('data-author')));
  if (site === 'letterboxd') {
    all('.attribution .name, .displayname, .person-summary .name').forEach((el) => names.add(el.textContent.trim()));
    all('a.avatar[href], .attribution a[href^="/"]').forEach((a) => {
      const seg = (a.getAttribute('href') || '').split('/').filter(Boolean)[0];
      if (seg && !['film', 'films', 'list', 'lists', 'reviews', 'members', 'journal'].includes(seg)) names.add(decodeURIComponent(seg));
    });
  }
  all('a[href^="/user/"], a[href*="reddit.com/user/"]').forEach((a) => {
    const m = (a.getAttribute('href') || '').match(/\/user\/([^/?#]+)/);
    if (m) names.add(decodeURIComponent(m[1]));
  });
  const nameList = [...names].filter((n) => n && n.length >= 3 && !/\s/.test(n));

  // 2. selectors
  const profile = site === 'letterboxd'
    ? '.attribution .name, .displayname, .person-summary .name, a.avatar, .avatar, .attribution-detail .name'
    : 'a[href^="/user/"], a[href*="reddit.com/user/"], [slot="authorName"], [slot="commentAvatar"], [slot="avatar"]';
  all(profile).forEach((el) => blur(el, 'profile_links'));
  all('img[alt*="avatar" i], img[src*="avatar" i], img[src*="snoo" i], img[src*="/avatars/"], [class*="avatar" i] img, [class*="avatar" i], [id*="avatar" i], faceplate-img[src*="avatar" i]')
    .forEach((el) => { if (!el.closest || !el.closest('[data-keep]')) blur(el, 'avatars'); });

  // 3. text: names in short text nodes, u/name and @name mentions anywhere
  const esc = (s) => s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  const mk = (list) => list.length ? new RegExp('(?<![\\w-])(?:u/)?(' + list.map(esc).join('|') + ')(?![\\w-])', 'g') : null;
  // a name that is an ordinary word ("Trust", "gut") is only blurred in short text (meta lines) or with a u/ prefix, so comment
  // bodies are not damaged; a distinctive name (digit, underscore, hyphen or mixed case) is blurred anywhere.
  const distinctive = (n) => /[0-9_-]/.test(n) || /[a-z][A-Z]/.test(n);
  const namePat = mk(nameList);
  const namePatLong = mk(nameList.filter(distinctive));
  const plainWords = nameList.filter((n) => !distinctive(n));
  const mentionPat = /(?<![\w/])(u\/[A-Za-z0-9_-]{3,20}|@[A-Za-z0-9_.]{3,30})(?![\w-])/g;
  const wrapMatches = (tn, pat, kind, shortOnly) => {
    const text = tn.nodeValue;
    if (shortOnly && text.trim().length > 60) return;
    pat.lastIndex = 0;
    const parts = []; let last = 0, m;
    while ((m = pat.exec(text))) { parts.push([last, m.index, false], [m.index, m.index + m[0].length, true]); last = m.index + m[0].length; }
    if (!parts.length) return;
    parts.push([last, text.length, false]);
    const frag = document.createDocumentFragment();
    parts.forEach(([a, b, hit]) => {
      if (a === b) return;
      if (hit) { const s = document.createElement('span'); s.textContent = text.slice(a, b); s.style.display = 'inline-block'; frag.appendChild(s); blur(s, kind); }
      else frag.appendChild(document.createTextNode(text.slice(a, b)));
    });
    tn.parentNode.replaceChild(frag, tn);
  };
  roots.forEach((root) => {
    const w = document.createTreeWalker(root, NodeFilter.SHOW_TEXT, { acceptNode: (n) => /^(SCRIPT|STYLE|NOSCRIPT)$/i.test(n.parentNode && n.parentNode.tagName) || !n.nodeValue.trim() || isBlurred(n) ? NodeFilter.FILTER_REJECT : NodeFilter.FILTER_ACCEPT });
    const nodes = []; while (w.nextNode()) nodes.push(w.currentNode);
    nodes.forEach((tn) => {
      if (isSubreddit(tn)) return;
      if (namePat) wrapMatches(tn, tn.nodeValue.trim().length <= 60 ? namePat : namePatLong, 'names', false);
      if (tn.parentNode && tn.isConnected) wrapMatches(tn, mentionPat, 'mentions', false);
    });
  });

  // 4. audit: any known name still visible in a short text node, or any u/ mention left
  const leftover = [];
  roots.forEach((root) => {
    const w = document.createTreeWalker(root, NodeFilter.SHOW_TEXT);
    while (w.nextNode()) {
      const n = w.currentNode; const t = n.nodeValue;
      if (!t.trim() || isBlurred(n) || isSubreddit(n) || /^(SCRIPT|STYLE|NOSCRIPT)$/i.test(n.parentNode && n.parentNode.tagName)) continue;
      const np = t.trim().length <= 60 ? namePat : namePatLong;
      if (np) { np.lastIndex = 0; if (np.test(t)) leftover.push(t.trim().slice(0, 40)); }
      mentionPat.lastIndex = 0; if (mentionPat.test(t)) leftover.push(t.trim().slice(0, 40));
    }
  });
  return JSON.stringify({ site, mode, names_known: nameList.length, blurred: count, leftover: leftover.slice(0, 8), check_by_eye_plain_word_names: plainWords.slice(0, 8) });
})();
