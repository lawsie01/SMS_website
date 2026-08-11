# SMS Website

The SMS (Sewer Maintenance Solutions) marketing and product website — built with
[Astro](https://astro.build) as a static site, styled with Tailwind CSS, with all product data,
spec tables and FAQs stored as structured content files rather than hard-coded in components.

## Why Astro

- **Static output, near-zero client-side JavaScript.** This is a content/spec-driven B2B site, not
  an app — Astro ships plain HTML/CSS by default, which is the best starting point for Core Web
  Vitals and crawlability.
- **Content Collections.** Product specs, part codes, configurations, FAQs and downloads live in
  `src/content/products/*.md` as structured frontmatter, validated against a schema
  (`src/content.config.ts`). Adding a product or editing a spec is a content change, not a code
  change — see [Editing content](#editing-content-the-important-bit) below.
- **Built-in image optimisation** (`astro:assets`) automatically resizes and converts product photos
  to WebP at build time.
- **Static export** deploys to any static host — this project is configured for Netlify, but the
  `dist/` output works equally well on Vercel or Cloudflare Pages.

## Requirements

- Node.js 20+ (Node 22 recommended, matches `netlify.toml`)

## Running locally

```bash
npm install
npm run dev       # http://localhost:4321, hot-reloading
```

## Building & previewing a production build

```bash
npm run build     # runs astro check (type/content validation) + astro build -> dist/
npm run preview   # serves the built dist/ locally to sanity-check the production output
```

## Deploying

This repo is configured for **Netlify** (`netlify.toml`):

- Build command: `npm run build`
- Publish directory: `dist`
- The enquiry form on `/contact/`, the gated download form on `/technical-resources/request-access/`,
  and the quote builder on `/quote/` each use a separate **Netlify Forms** instance
  (`data-netlify="true"`, forms named `contact`, `download-request` and `quote-request`) — no
  serverless function or third-party form service needed. Submissions appear in the Netlify
  dashboard under Forms, and can be forwarded to `sales@sewerms.com.au` via a Netlify
  notification/webhook. Set up a **2-business-day SLA reminder** on the `quote-request` form
  notification so quote requests don't sit unreviewed.

To deploy elsewhere (Vercel, Cloudflare Pages), point the platform at `npm run build` with output
directory `dist`, and replace the Netlify Forms `data-netlify` attribute in
`src/pages/contact/index.astro` with whatever form backend you use instead.

## Design checks (Impeccable)

The site is checked against [Impeccable](https://github.com/pbakaus/impeccable), a UI
anti-pattern detector. It needs no API key and isn't a project dependency — it runs via `npx`:

```bash
npx --yes impeccable detect src/          # static pass over source
npm run preview                           # then, in a second terminal:
npx --yes impeccable detect http://localhost:4321/ http://localhost:4321/quote/
```

The URL pass renders in a real browser and is the one worth trusting — it catches computed
contrast, heading order and line length that static analysis misses. All pages currently report
zero failures at both 1280x800 and 390x844.

Two things to know before acting on its output:

- **`cramped-padding` is ignored** via `.impeccable/config.json`. It fires on the bordered data
  tables, which fill their container edge-to-edge by design — adding inset would put a white
  gutter around each table's dark header row. Genuine false positive for this pattern.
- **`em-dash-overuse` is advisory** and never fails a run. What remains is mostly the `MS8 — RRJ
  180° Straight` style separators in configuration dropdowns, which are UI labels rather than prose.

Note that Impeccable's `overused-font` rule does **not** see Tailwind v4 `@theme` custom
properties — it only matches real `font-family` declarations. A bad font named in
`src/styles/global.css` will pass the static pass and only be caught by the URL pass.

---

## Editing content (the important bit)

**You should never need to touch a `.astro` component file to add a product, change a spec, fix a
part code, or swap a brochure PDF.** All of that lives in plain content files.

### Where everything lives

```
src/content/products/*.md      ← one file per product (spec tables, FAQs, downloads, etc.)
src/content.config.ts          ← the schema those files are validated against
src/data/company.json          ← phone, email, address, coverage areas, sales contacts
public/downloads/*.pdf         ← the actual brochure/certificate PDFs served for download
src/assets/images/*            ← product photos and hero images
```

### Editing an existing product's specs

Open the relevant file in `src/content/products/`, e.g. `dn600-maintenance-chamber.md`. The top of
the file (between the `---` lines) is YAML frontmatter — structured fields that render into the
page automatically. For example, to change a spec value, find the row under `specSections` and
edit the `value`:

```yaml
specSections:
  - heading: "Product overview"
    rows:
      - label: "Base socket tolerance"
        value: "±7.5° horizontal angle and ±7.5° gradient"   # <- edit this
```

Each `atAGlance` row can optionally carry an `icon` (one of the names in `src/components/Icon.astro`
— `chemical`, `service-life`, `depth`, `ladder`, `load`, `diameter`, `feather`, `joint`, `shield`,
`wsaa`) to show a small line-icon above the value. Omit it and the tile just renders as text, same as
before:

```yaml
atAGlance:
  - label: "Chemical resistance"
    value: "pH 1–13"
    icon: "chemical"   # optional — leave out for a text-only tile
```

Every section on the product page maps to a field in this file:

| Page section | Frontmatter field |
|---|---|
| At-a-glance stat blocks | `atAGlance` |
| Full specification table | `specSections` |
| Configurations & part codes table | `configurations` / `configurationsIntro` |
| Installation & depth | `installationSections` |
| Standards & approvals | `standards` |
| FAQ accordion (+ FAQPage schema) | `faqs` |
| Downloads panel | `downloads` |
| Product render photo | `productImage`, `productImageAlt`, `productImageBackground` |

The short paragraph below the closing `---` is the intro copy shown at the bottom of the page — edit
it like any normal text.

### Adding a brand new product

1. Copy an existing file in `src/content/products/` as a starting point (pick a DN-family page like
   `dn375-maintenance-shaft.md` for a full product, or an accessory page like `bends.md` for a
   simpler fittings-style page).
2. Rename the file — the filename becomes the page's URL, e.g. `dn800-maintenance-chamber.md` →
   `/products/dn800-maintenance-chamber/`.
3. Fill in the frontmatter fields. Required fields are `title`, `brand`, `category`,
   `shortDescription` and `cardUseCase` — everything else defaults to empty and simply won't render
   that section (e.g. leave `configurations: []` out entirely if it doesn't apply).
4. Set `category` to `maintenance-shaft`, `maintenance-chamber` or `maintenance-hole` for a full
   DN-family template (with configurations table), or `accessory` for the lighter fittings template.
5. Set `order` to control where it appears among other cards on the homepage and `/products/` hub.
6. Save the file — `npm run dev` will pick it up immediately; no other file needs to change. The
   product automatically appears on the homepage, the `/products/` hub, and gets its own page with
   Product/FAQPage/BreadcrumbList schema.org markup.

### Swapping or adding a downloadable brochure/drawing

1. Put the new PDF in `public/downloads/`.
2. In the product's content file, update the `downloads` list:

```yaml
downloads:
  - label: "SMS Maintenance Chamber Brochure (March 2027)"
    file: "/downloads/SMS-Maintenance-Chamber-Brochure-Mar2027.pdf"
    fileType: "PDF"
    restricted: false     # false = public download link; true = gated behind /technical-resources/request-access/
```

Full engineering drawings and CAD/BIM files are treated as commercial-in-confidence by default
(`restricted: true`) — they show as "request access" and link to the dedicated
`/technical-resources/request-access/` lead-capture form (a separate Netlify form,
`download-request`, from the general enquiry form) rather than a public URL. That form pre-fills
the product and asset type from the link's query string. Only flip a drawing to
`restricted: false` if it has been cleared for public distribution.

### How the quote builder (`/quote/`) works

`/quote/` lets a visitor pick products and quantities into a quote list, then submit it as one
request — it does **not** calculate pricing. The product picker (configurations, quantities) and the
running quote list are entirely client-side (vanilla JS + `localStorage`, no framework), so the list
persists across page loads without a backend. Each product page also has an "Add to quote" link
(`/quote/?add=<product-slug>`) that pre-adds that product when the quote page loads.

On submit, a hidden field builds a human-readable itemised summary (product, quantity, configuration)
from the quote list and sends it to the `quote-request` Netlify form alongside the requester's contact
and project details — so whoever reviews it in the Netlify Forms dashboard (or a forwarded
notification email) can read the list without parsing JSON. **The 2-business-day turnaround promised
on the page and thank-you screen is a process commitment, not something the site enforces** — someone
on the SMS team needs to actually check the Forms dashboard (or notification inbox) regularly and send
the reviewed quote back manually within that window.

### Editing company-wide details (phone, email, address, sales contacts, coverage areas)

Edit `src/data/company.json`. This single file feeds the header, footer, contact page, About page,
and the Organization schema.org markup — change it once, it updates everywhere.

### Editing the standards/approvals shown site-wide

Each product's own standards list lives in that product's `standards` field. The dedicated
`/approvals/` page content (the fuller descriptions and FAQ) is in
`src/pages/approvals/index.astro` — it's plain arrays at the top of the file rather than a content
collection, since it's page-specific narrative content rather than per-product data.

---

## Notes for whoever picks this up next

- **Engineering drawings are not published publicly.** The three product families' full engineering
  drawings are marked commercial-in-confidence by the client and are not included as public
  downloads on this site (see `reference-materials/` in the repo root for the originals, supplied
  for content-authoring reference only — do not publish them as-is). Only the marketing brochures and
  the WSAA certificate are wired up as public downloads in `public/downloads/`.
- **A few facts are flagged for client confirmation** rather than asserted outright, because they
  couldn't be verified from the supplied brochures/drawings alone — search `CONFIRM` in
  `reference-materials/EXTRACTED_SPECS_NOTES.md` for the full list (exact street address, whether
  WaterMark/ISO 9001 certification still applies to the current range, and the two sales contacts
  whose exact titles couldn't be independently verified). Legal name and ABN in
  `src/data/company.json` are confirmed as of August 2026 (Sewer Maintenance Solutions (SMS), ABN
  71 672 987 067).
- **Brand colours were extracted directly from the SMS logo**, not guessed — see
  `src/styles/global.css` (`--color-sms-green-400: #63b447`, `--color-sms-green-900: #191717`). If
  the client provides an official brand guideline later, update the `@theme` block in that one file.
- **Typefaces are self-hosted via Fontsource, not a CDN** — Archivo for headings, IBM Plex Sans for
  body and tables, both installed as npm packages and served from `/_astro/`. Nothing is fetched
  from Google Fonts at runtime, so there's no third-party dependency and no silent fallback. Only
  the `wght` axis and the latin subset ship (~36kB + ~48kB). If the client supplies an official
  brand typeface, swap `--font-display` / `--font-sans` in `global.css` and drop the two
  `@fontsource-variable` imports above them.
