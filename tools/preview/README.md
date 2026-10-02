# Single-file site preview

Bundles the built site into one self-contained HTML file that can be published
as a Claude Artifact and clicked through like the real thing.

```sh
tools/preview/make_preview.sh [output.html]   # default: ./sms-site-preview.html
```

The script builds the site, bundles it, and restores anything it touched on
the way out. Nothing it changes is left in the working tree.

## Why it is not just `dist/index.html`

The artifact viewer serves one HTML file with no connect-src and no external
hosts, so the bundle has to carry everything and answer every request itself.

- **Every asset is inlined** as a `data:` URI: images, the font faces that the
  stylesheet references, and the stylesheet itself. Absolute URLs inside
  JSON-LD look like local paths but are not chased.
- **Navigation is a DOM swap.** Each page's body HTML sits in `__PAGES__`, and
  a click on an internal link writes the new body into `#app`.
- **Page scripts are re-run as classic scripts** on every route change. A
  module only ever executes once, so the site's own scripts would stop working
  after the first navigation.
- **three.js is statically linked for this build only.** The viewer normally
  lazy-loads it through `import()`, which a classic script cannot do, so the
  loader is rewritten to static imports before the build and restored after.
  Vite then folds three.js into the viewer chunk and leaves no import behind.
- **`fetch` is shimmed** to answer the search index and the GLB models from
  memory, and form submits are blocked in the capture phase so the contact
  form never hangs on a request that cannot be made.

## Inline copy editing

The bundle ships an editor: the Edit copy button in the preview bar makes
text-only elements `contenteditable` and writes each change to the artifact's
`db` store, so edits persist on the link and can be read back and ported into
the Astro source.

Only elements whose children are all text nodes are editable, so an edit can
never swallow a link or a nested span and the store only ever holds plain
strings. Each edit is keyed by a hash of the route plus the element's pristine
text, which means the key survives a rebuild as long as the sentence itself is
unchanged, and doubles as the search string for finding it in the source.

Publishing needs `capabilities: {db: {}}`, which makes the artifact
organisation-internal.
