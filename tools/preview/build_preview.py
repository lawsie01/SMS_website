"""Bundle the built site into one self-contained HTML file for an Artifact.

The artifact CSP has no connect-src and no external hosts, so every asset has
to be inlined as a data: URI and every fetch answered from memory.

Navigation is a DOM swap rather than a document load. Each page's HTML is held
in __PAGES__ and written into #app on a route change; the page's own scripts
are rewritten as classic scripts and run again each time, because a module
only ever executes once.
"""
import base64, json, mimetypes, os, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DIST = Path(os.environ.get('PREVIEW_DIST', ROOT / 'site' / 'dist'))
OUT = Path(sys.argv[1] if len(sys.argv) > 1
           else os.environ.get('PREVIEW_OUT', ROOT / 'sms-site-preview.html'))


def js(value):
    """JSON safe to embed inside a <script> element."""
    return json.dumps(value).replace('</', '<\\/').replace('<!--', '<\\!--')


# ---------------------------------------------------------------- routes
html = {}
for f in sorted(DIST.rglob('*.html')):
    rel = f.relative_to(DIST)
    if f.name == 'index.html':
        route = '/' + str(rel.parent).replace('.', '').strip('/')
        route = (route + '/').replace('//', '/')
    else:
        # 404.html has no directory of its own; give it the route the host
        # maps it to so the router can reach it.
        route = '/' + rel.stem + '/'
    html[route] = f.read_text()
routes = sorted(html)

# The bundle inlines every srcset variant as base64, so the 2x variants cost
# roughly a third more than their file size and buy nothing: the preview is
# read in an artifact frame, not on a retina hero. Cap the widths, and move
# any src that pointed at a dropped variant down to the largest kept one.
SRCSET_CAP = 1600
SRCSET = re.compile(r'srcset="([^"]+)"')

def cap_srcset(text):
    def one(m):
        kept, dropped = [], []
        for part in m.group(1).split(','):
            bits = part.strip().rsplit(' ', 1)
            if len(bits) != 2 or not bits[1].endswith('w'):
                return m.group(0)
            (kept if int(bits[1][:-1]) <= SRCSET_CAP else dropped).append(
                (bits[0], int(bits[1][:-1])))
        if not kept:
            kept = [min(dropped, key=lambda d: d[1])]
            dropped = [d for d in dropped if d not in kept]
        text_out = ', '.join(f'{u} {w}w' for u, w in kept)
        for u, _ in dropped:
            cap_srcset.swaps[u] = max(kept, key=lambda k: k[1])[0]
        return f'srcset="{text_out}"'
    cap_srcset.swaps = getattr(cap_srcset, 'swaps', {})
    return SRCSET.sub(one, text)

for r in routes:
    html[r] = cap_srcset(html[r])
for r in routes:
    for dropped, keep in getattr(cap_srcset, 'swaps', {}).items():
        html[r] = html[r].replace(f'src="{dropped}"', f'src="{keep}"')


# ---------------------------------------------------------------- assets
REF = re.compile(r'/(?:_astro|models|fonts|images)/[A-Za-z0-9._\-]+')
assets, stubbed, missing = {}, [], []


def data_uri(path):
    p = DIST / path.lstrip('/')
    if not p.exists():
        missing.append(path)
        return None
    mime = mimetypes.guess_type(p.name)[0] or 'application/octet-stream'
    if p.suffix == '.glb':
        mime = 'model/gltf-binary'
    if p.suffix == '.woff2':
        mime = 'font/woff2'
    return f'data:{mime};base64,' + base64.b64encode(p.read_bytes()).decode()


def refs(text):
    return set(REF.findall(text))


# CSS first: it carries the font faces and background images.
css_hrefs = []
for r in routes:
    for h in re.findall(r'<link rel="stylesheet" href="([^"]+)"', html[r]):
        if h not in css_hrefs:
            css_hrefs.append(h)

sheets = {}
for h in css_hrefs:
    p = DIST / h.lstrip('/')
    sheets[h] = p.read_text() if p.exists() else ''

# Per-page inline <style> blocks live in <head>, which the router never
# swaps, so hoist them into the one shared stylesheet.
HEADSTYLE = re.compile(r'<style>(.*?)</style>', re.S)
head_styles = []

# Page scripts.
EXT_SCRIPT = re.compile(r'<script type="module" src="([^"]+)"></script>')
INLINE_SCRIPT = re.compile(r'<script type="module">(.*?)</script>', re.S)
LDJSON = re.compile(r'<script type="application/ld\+json">.*?</script>', re.S)
TITLE = re.compile(r'<title>(.*?)</title>', re.S)
BODYTAG = re.compile(r'<body[^>]*class="([^"]*)"')
BODY = re.compile(r'<body[^>]*>(.*)</body>', re.S)

script_srcs = []
for r in routes:
    for s in EXT_SCRIPT.findall(html[r]):
        if s not in script_srcs:
            script_srcs.append(s)

page_scripts = {}
for s in script_srcs:
    p = DIST / s.lstrip('/')
    page_scripts[s] = p.read_text() if p.exists() else ''

# Collect every asset reference from HTML, CSS and JS.
wanted = set()
for r in routes:
    # Structured data carries absolute sewerms.com.au URLs whose paths look
    # like local assets. The router strips ld+json, so don't chase them.
    wanted |= refs(LDJSON.sub('', html[r]))
for h, t in sheets.items():
    wanted |= refs(t)
for s, t in page_scripts.items():
    wanted |= refs(t)

for a in sorted(wanted):
    if a in css_hrefs or a in script_srcs:
        continue                      # inlined as text, not as a data URI
    if a.endswith('.glb'):
        continue                      # handed to the viewer separately
    if a.endswith('.html') or a.endswith('.json'):
        stubbed.append(a)
        continue
    u = data_uri(a)
    if u:
        assets[a] = u


def rewrite(text):
    for a, u in assets.items():
        text = text.replace(a, u)
    return text


# GLB models: the viewer fetches them, which the CSP forbids, so hand them
# over as base64 and let it parse them in place.
models = {}
for m in sorted((DIST / 'models').glob('*.glb')):
    models['/models/' + m.name] = base64.b64encode(m.read_bytes()).decode()

search_index_file = DIST / 'search-index.json'
search_index = search_index_file.read_text() if search_index_file.exists() else 'null'

pages = {}
for r in routes:
    t = html[r]
    for m in HEADSTYLE.finditer(t):
        if m.group(1) not in head_styles:
            head_styles.append(m.group(1))
    t = rewrite(t)
    body = BODY.search(t)
    inner = body.group(1) if body else ''
    ext = EXT_SCRIPT.findall(inner)
    inner = EXT_SCRIPT.sub('', inner)
    inline = INLINE_SCRIPT.findall(inner)
    inner = LDJSON.sub('', INLINE_SCRIPT.sub('', inner))
    inner = HEADSTYLE.sub('', inner)
    pages[r] = {
        'title': (TITLE.search(t).group(1).strip() if TITLE.search(t) else 'SMS'),
        'bodyClass': (BODYTAG.search(t).group(1).strip() if BODYTAG.search(t) else ''),
        'html': inner,
        'ext': ext,
        'inline': inline,
    }

css = rewrite('\n'.join([sheets[h] for h in css_hrefs] + head_styles))
page_scripts = {k: rewrite(v) for k, v in page_scripts.items()}

shell = f"""<title>SMS site preview</title>
<style>{css}</style>
<style>
  #preview-bar {{
    position: fixed; bottom: 0; left: 0; right: 0; z-index: 9999;
    background: #1f1925; color: #fff; font: 12px/1.4 system-ui, sans-serif;
    padding: 6px 12px; display: flex; gap: 10px; align-items: center;
    justify-content: space-between;
  }}
  #preview-bar code {{ color: #38e33a; font-family: ui-monospace, monospace; }}
  #preview-bar > span {{ opacity: .65; }}
  #preview-edit-wrap {{ opacity: 1 !important; display: flex; gap: 6px; flex: none; }}
  #preview-bar button {{
    font: inherit; color: #fff; background: #3a323f; border: 1px solid #5f5768;
    border-radius: 4px; padding: 3px 9px; cursor: pointer;
  }}
  #preview-bar button:hover {{ background: #5f5768; }}
  #preview-bar button[data-on] {{ background: #38e33a; border-color: #38e33a; color: #1f1925; font-weight: 600; }}
  body {{ padding-bottom: 30px; }}

  /* Inline editing. Only text-only elements are made editable, so the caret
     can never land inside markup the store cannot round-trip. */
  body[data-editing] [data-ek] {{
    outline: 1px dashed rgba(56,227,58,.55); outline-offset: 3px; cursor: text;
  }}
  body[data-editing] [data-ek]:hover {{ outline-style: solid; }}
  body[data-editing] [data-ek]:focus {{
    outline: 2px solid #1abc1c; outline-offset: 3px; background: rgba(56,227,58,.07);
  }}
  [data-ek][data-edited] {{ box-shadow: inset 3px 0 0 -1px #38e33a; }}
  #preview-edits {{
    position: fixed; right: 12px; bottom: 38px; z-index: 10000;
    width: min(460px, calc(100vw - 24px)); max-height: 60vh; overflow: auto;
    background: #fff; color: #1f1925; border: 1px solid #c5c1c9; border-radius: 8px;
    box-shadow: 0 10px 30px rgba(0,0,0,.25); font: 12px/1.5 system-ui, sans-serif;
    padding: 10px 12px;
  }}
  #preview-edits h4 {{ margin: 0 0 8px; font: 600 12px/1.4 system-ui, sans-serif; }}
  #preview-edits .row {{ border-top: 1px solid #e8e7ea; padding: 8px 0; }}
  #preview-edits .row:first-of-type {{ border-top: 0; }}
  #preview-edits .rt {{ font-family: ui-monospace, monospace; color: #505d68; font-size: 11px; }}
  #preview-edits del {{ color: #9a2436; text-decoration: line-through; }}
  #preview-edits ins {{ color: #0f6b10; text-decoration: none; }}
  #preview-edits button {{
    font: inherit; border: 1px solid #c5c1c9; background: #f7f7f7; border-radius: 4px;
    padding: 1px 7px; cursor: pointer; margin-top: 4px;
  }}
</style>
<div id="app"></div>
<div id="preview-bar">
  <span>Static preview. Route <code id="preview-route">/</code></span>
  <span id="preview-note">Forms and PDF downloads are inert. Everything else is the real build.</span>
  <span id="preview-edit-wrap">
    <button type="button" id="preview-edit">Edit copy</button>
    <button type="button" id="preview-count" hidden>0 edits</button>
  </span>
</div>
<div id="preview-edits" hidden></div>
<script>window.__PAGES__ = {js(pages)};
window.__SCRIPTS__ = {js(page_scripts)};
window.__MODEL_B64__ = {js(models)};
window.__SEARCH_INDEX__ = {search_index};</script>
"""

router = r"""
<script>
(function () {
  var DEFAULT_NOTE = 'Forms and PDF downloads are inert. Everything else is the real build.';
  var app = document.getElementById('app');
  var label = document.getElementById('preview-route');

  function note(msg) {
    var n = document.getElementById('preview-note');
    if (n) n.textContent = msg || DEFAULT_NOTE;
  }

  // GLB models: decode once into ArrayBuffers. The viewer reads them from
  // here and parses in place, because the artifact CSP has no connect-src
  // and any fetch for a .glb would be refused.
  var MODELS = {};
  Object.keys(window.__MODEL_B64__ || {}).forEach(function (k) {
    var bin = atob(window.__MODEL_B64__[k]);
    var buf = new Uint8Array(bin.length);
    for (var i = 0; i < bin.length; i++) buf[i] = bin.charCodeAt(i);
    MODELS[k] = buf.buffer;
  });

  function norm(href) {
    if (!href || href.charAt(0) !== '/') return null;
    var path = href.split('#')[0].split('?')[0];
    if (!/\/$/.test(path)) path += '/';
    return window.__PAGES__[path] ? path : null;
  }

  function run(page) {
    // Each page's scripts are re-executed on every route change. A module
    // would only ever run once, so they go in as classic scripts.
    (page.ext || []).forEach(function (src) {
      var code = window.__SCRIPTS__[src];
      if (!code) return;
      var s = document.createElement('script');
      s.textContent = '(function(){' + code + '})();';
      document.body.appendChild(s);
      s.remove();
    });
    (page.inline || []).forEach(function (code) {
      var s = document.createElement('script');
      s.textContent = '(function(){' + code + '})();';
      document.body.appendChild(s);
      s.remove();
    });
  }

  function render(route, push) {
    var page = window.__PAGES__[route];
    if (!page) return;
    app.innerHTML = page.html;
    document.title = page.title;
    label.textContent = route;
    note(null);
    if (push) history.pushState({ route: route }, '', '#' + route);
    window.scrollTo(0, 0);
    run(page);
    if (window.__onRender__) window.__onRender__(route);
  }

  document.addEventListener('click', function (e) {
    if (document.body.hasAttribute('data-editing') &&
        e.target.closest && e.target.closest('[data-ek]')) {
      e.preventDefault();
      return;
    }
    var a = e.target.closest && e.target.closest('a[href]');
    if (!a || a.target === '_blank') return;
    // The enquiry CTAs are links to /contact/ that the site upgrades into a
    // modal. Routing them would replace the DOM mid-dispatch, so the
    // element's own listener never runs and the modal never opens.
    if (a.hasAttribute('data-enquiry-cta')) return;
    var route = norm(a.getAttribute('href'));
    var hash = (a.getAttribute('href') || '').split('#')[1];
    if (!route) return;
    e.preventDefault();
    render(route, true);
    if (hash) {
      var t = document.getElementById(hash);
      if (t) t.scrollIntoView();
    }
  }, true);

  // Search reads its index over fetch, and the viewer fetches a .glb. There
  // is no connect-src in the artifact CSP, so answer both from memory.
  var realFetch = window.fetch.bind(window);
  window.fetch = function (input, init) {
    var url = typeof input === 'string' ? input : (input && input.url) || '';
    if (url.indexOf('/search-index.json') === 0 && window.__SEARCH_INDEX__) {
      return Promise.resolve(new Response(JSON.stringify(window.__SEARCH_INDEX__), {
        status: 200, headers: { 'Content-Type': 'application/json' },
      }));
    }
    for (var k in MODELS) {
      if (url.indexOf(k) !== -1) {
        return Promise.resolve(new Response(MODELS[k], {
          status: 200, headers: { 'Content-Type': 'model/gltf-binary' },
        }));
      }
    }
    return realFetch(input, init);
  };

  // Forms post to Netlify, which nothing here can reach. Stop the event in
  // the capture phase so the site's own handler never starts a request that
  // would fail and leave the form stuck on "Sending".
  document.addEventListener('submit', function (e) {
    e.preventDefault();
    e.stopPropagation();
    note('Form submission is disabled in the preview.');
  }, true);

  window.addEventListener('popstate', function (e) {
    render((e.state && e.state.route) || '/', false);
  });

  var start = location.hash.slice(1);
  render(window.__PAGES__[start] ? start : '/', false);
})();
</script>
"""

editor = r"""
<script>
// Inline copy editing for the preview.
//
// Only elements whose children are ALL text nodes are made editable, so an
// edit can never swallow a link, a badge or a nested span - the store keeps
// plain strings and nothing has to round-trip markup.
//
// The key for an edit is a hash of the route plus the element's PRISTINE
// text, taken on each render before any stored edit is applied. That
// survives a rebuild of this bundle as long as the sentence itself is
// unchanged, and it doubles as the search string for porting the edit into
// the Astro source.
(function () {
  var SEL = 'h1,h2,h3,h4,h5,p,li,td,th,dd,dt,figcaption,blockquote,summary';
  var SKIP = 'header,nav,footer,#preview-bar,#preview-edits,script,style';
  var MIN = 2;

  var btn = document.getElementById('preview-edit');
  var countBtn = document.getElementById('preview-count');
  var panel = document.getElementById('preview-edits');
  var edits = Object.create(null);    // key -> {route, original, edited}
  var pristine = Object.create(null); // key -> the bundle's own text
  var db = null;
  var route = '/';
  var timers = Object.create(null);

  function hash(s) {
    var h = 2166136261;
    for (var i = 0; i < s.length; i++) {
      h ^= s.charCodeAt(i);
      h = (h + ((h << 1) + (h << 4) + (h << 7) + (h << 8) + (h << 24))) >>> 0;
    }
    return ('000000' + h.toString(36)).slice(-7);
  }

  function textOnly(el) {
    for (var n = el.firstChild; n; n = n.nextSibling) {
      if (n.nodeType !== 3) return false;
    }
    return true;
  }

  function scan() {
    var nodes = document.querySelectorAll(SEL);
    for (var i = 0; i < nodes.length; i++) {
      var el = nodes[i];
      if (el.closest(SKIP)) continue;
      if (!textOnly(el)) continue;
      var t = el.textContent.trim();
      if (t.length < MIN) continue;
      var key = hash(route + '|' + t);
      el.setAttribute('data-ek', key);
      // Captured BEFORE any stored edit is applied, so the first edit of an
      // element still knows what it is replacing.
      pristine[key] = t;
      var rec = edits[key];
      if (rec && rec.edited !== t) {
        el.textContent = rec.edited;
        el.setAttribute('data-edited', '');
      }
      if (document.body.hasAttribute('data-editing')) {
        el.setAttribute('contenteditable', 'plaintext-only');
      }
    }
  }

  function report(e) {
    var n = document.getElementById('preview-note');
    if (n) n.textContent = 'Could not save that edit (' + (e && e.code ? e.code : 'error') + ').';
  }

  function save(el) {
    var key = el.getAttribute('data-ek');
    if (!key || !db) return;
    var now = el.textContent.trim();
    var rec = edits[key];
    var original = rec ? rec.original : pristine[key];
    if (original === undefined) return;
    if (now === original) {
      delete edits[key];
      el.removeAttribute('data-edited');
      db.doc('edits/' + key).delete().catch(report);
    } else {
      edits[key] = { route: route, original: original, edited: now };
      el.setAttribute('data-edited', '');
      db.doc('edits/' + key).set({
        route: route, original: original, edited: now, at: new Date().toISOString(),
      }).catch(report);
    }
    refresh();
  }

  function refresh() {
    var keys = Object.keys(edits);
    countBtn.hidden = keys.length === 0;
    countBtn.textContent = keys.length + (keys.length === 1 ? ' edit' : ' edits');
    if (!panel.hidden) drawPanel();
  }

  function drawPanel() {
    var keys = Object.keys(edits);
    panel.innerHTML = '';
    var h = document.createElement('h4');
    h.textContent = keys.length + ' pending ' + (keys.length === 1 ? 'edit' : 'edits');
    panel.appendChild(h);
    keys.forEach(function (key) {
      var rec = edits[key];
      var row = document.createElement('div');
      row.className = 'row';
      var r = document.createElement('div');
      r.className = 'rt';
      r.textContent = rec.route;
      var d = document.createElement('div');
      var del = document.createElement('del');
      del.textContent = rec.original;
      var ins = document.createElement('ins');
      ins.textContent = rec.edited;
      d.appendChild(del);
      d.appendChild(document.createElement('br'));
      d.appendChild(ins);
      var b = document.createElement('button');
      b.type = 'button';
      b.textContent = 'Revert';
      b.onclick = function () {
        delete edits[key];
        if (db) db.doc('edits/' + key).delete().catch(report);
        var live = document.querySelector('[data-ek="' + key + '"]');
        if (live) {
          live.textContent = rec.original;
          live.removeAttribute('data-edited');
        }
        refresh();
      };
      row.appendChild(r);
      row.appendChild(d);
      row.appendChild(b);
      panel.appendChild(row);
    });
  }

  window.__onRender__ = function (r) {
    route = r;
    scan();
  };

  btn.addEventListener('click', function () {
    var n = document.getElementById('preview-note');
    if (!db) {
      if (n) n.textContent = 'Editing is unavailable in this view.';
      return;
    }
    var on = document.body.hasAttribute('data-editing');
    if (on) {
      document.body.removeAttribute('data-editing');
      btn.removeAttribute('data-on');
      btn.textContent = 'Edit copy';
      document.querySelectorAll('[contenteditable]').forEach(function (el) {
        if (el.hasAttribute('data-ek')) el.removeAttribute('contenteditable');
      });
      if (n) n.textContent = 'Edits saved. They persist on this link and I can read them back.';
    } else {
      document.body.setAttribute('data-editing', '');
      btn.setAttribute('data-on', '');
      btn.textContent = 'Done';
      scan();
      if (n) n.textContent = 'Click any paragraph or heading and type. Edits save as you go.';
    }
  });

  countBtn.addEventListener('click', function () {
    panel.hidden = !panel.hidden;
    if (!panel.hidden) drawPanel();
  });

  // Save on blur, and on a pause in typing so nothing is lost to a
  // click-away that navigates. One write per element per pause.
  document.addEventListener('focusout', function (e) {
    var el = e.target.closest && e.target.closest('[data-ek][contenteditable]');
    if (el) save(el);
  }, true);

  document.addEventListener('input', function (e) {
    var el = e.target.closest && e.target.closest('[data-ek][contenteditable]');
    if (!el) return;
    var key = el.getAttribute('data-ek');
    clearTimeout(timers[key]);
    timers[key] = setTimeout(function () { save(el); }, 900);
  }, true);

  // Enter ends the edit rather than splitting the block into two nodes the
  // store would then see as one string with a newline in it.
  document.addEventListener('keydown', function (e) {
    if (e.key !== 'Enter' || e.shiftKey) return;
    var el = e.target.closest && e.target.closest('[data-ek][contenteditable]');
    if (!el) return;
    e.preventDefault();
    el.blur();
  }, true);

  if (window.claude && window.claude.use) {
    window.claude.use('db').then(function (store) {
      if (!store) return;
      db = store;
      return store.collection('edits').get().then(function (snap) {
        snap.docs.forEach(function (doc) {
          var d = doc.data();
          if (d && d.original) edits[doc.id] = d;
        });
        refresh();
        scan();
      });
    }).catch(function () { /* editing stays off; the preview still works */ });
  }
})();
</script>
"""

OUT.write_text(shell + router + editor)
size = OUT.stat().st_size
print(f'routes      {len(pages)}')
print(f'assets      {len(assets)} inlined, {len(stubbed)} stubbed, {len(missing)} missing')
print(f'head css    {len(css_hrefs)} linked, {len(head_styles)} inline blocks hoisted')
print(f'models      {len(models)}')
print(f'page js     {len(page_scripts)}')
print(f'output      {OUT}  {size / 1048576:.2f} MB')
if missing:
    print('MISSING:', missing[:10])
