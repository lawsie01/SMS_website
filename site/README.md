# SMS Website

The SMS (Sewer Maintenance Shaft Pty Ltd) marketing and product website — built with
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
- The enquiry form on `/contact/` uses **Netlify Forms** (`data-netlify="true"`) — no serverless
  function or third-party form service needed. Submissions appear in the Netlify dashboard under
  Forms, and can be forwarded to `sales@sewerms.com.au` via a Netlify notification/webhook.

To deploy elsewhere (Vercel, Cloudflare Pages), point the platform at `npm run build` with output
directory `dist`, and replace the Netlify Forms `data-netlify` attribute in
`src/pages/contact/index.astro` with whatever form backend you use instead.

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
    restricted: false     # false = public download link; true = "available on request" (routes to /contact/)
```

Full engineering drawings are treated as commercial-in-confidence by default (`restricted: true`) —
they show as "available on request" and link to the contact form rather than a public URL. Only
flip a drawing to `restricted: false` if it has been cleared for public distribution.

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
  `src/data/company.json` and `reference-materials/EXTRACTED_SPECS_NOTES.md` for the full list
  (exact street address/ABN, whether WaterMark/ISO 9001 certification still applies to the current
  range, and the two sales contacts whose exact titles couldn't be independently verified).
- **Brand colours were extracted directly from the SMS logo**, not guessed — see
  `src/styles/global.css` (`--color-sms-green-400: #63b447`, `--color-sms-green-900: #191717`). If
  the client provides an official brand guideline later, update the `@theme` block in that one file.
