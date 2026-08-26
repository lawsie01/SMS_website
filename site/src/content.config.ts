import { defineCollection, z, type ImageFunction } from 'astro:content';
import { glob } from 'astro/loaders';

const specRow = z.object({
  label: z.string(),
  value: z.string(),
});

const iconName = z.enum([
  'chemical',
  'service-life',
  'depth',
  'ladder',
  'load',
  'diameter',
  'feather',
  'joint',
  'shield',
  'wsaa',
]);

const atAGlanceRow = specRow.extend({
  icon: iconName.optional(), // matches an Icon.astro name — omit to render text-only
});

const specSection = z.object({
  heading: z.string(),
  rows: z.array(specRow),
});

// installSection and photoItem need the image() helper, which astro:content
// only exposes inside the collection's own schema factory — so both are
// factories themselves, called with that same `image` inside products'
// schema below, rather than plain top-level z.object() like their siblings.
// A numbered indicator on an assembly render. x/y are percentages of the
// image box: y positions the badge in the left gutter, x is where its lead
// line stops, on the left edge of the part being called out.
const callout = z.object({
  n: z.number().int().positive(),
  x: z.number().min(0).max(100),
  y: z.number().min(0).max(100),
});

const assemblyRender = (image: ImageFunction) =>
  z.object({
    image: image(),
    alt: z.string(),
    caption: z.string().optional(),
    callouts: z.array(callout).default([]),
  });

const photoItem = (image: ImageFunction) =>
  z.object({
    image: image(),
    alt: z.string(),
    caption: z.string().optional(),
  });

const installSection = (image: ImageFunction) =>
  z.object({
    heading: z.string(),
    body: z.string(), // markdown-ish plain text, rendered with line breaks
    bullets: z.array(z.string()).optional(),
    images: z.array(photoItem(image)).default([]), // real product photos illustrating this step
  });

const configRow = z.object({
  // Number of the matching indicator on the assembly render above.
  ref: z.number().int().positive().optional(),
  // Omitted for parts SMS does not code separately, such as riser pipe and
  // seals, which still need a row so every indicator on the render resolves.
  code: z.string().optional(),
  configuration: z.string(),
  size: z.string().optional(),
  notes: z.string().optional(),
});

// A size-grouped bank of part codes for an accordion — e.g. all 8 RRJ angle
// codes for one inlet/outlet size, so every code in a large matrix (like the
// DN1000 Hole's 32 base configurations) is individually present in the page
// and findable, without a 32-row table dominating the section by default.
const configGroup = z.object({
  heading: z.string(),
  rows: z.array(configRow),
});

const faqItem = z.object({
  question: z.string(),
  answer: z.string(),
});

const download = z.object({
  label: z.string(),
  file: z.string(), // path under /public/downloads/
  fileType: z.string().default('PDF'),
  restricted: z.boolean().default(false), // true = available on request, not a public link
});

const standard = z.object({
  code: z.string(),
  description: z.string(),
});

const products = defineCollection({
  loader: glob({ pattern: '**/*.md', base: './src/content/products' }),
  schema: ({ image }) =>
    z.object({
      title: z.string(),
      brand: z.enum(['AXEDO', 'ROMOLD', 'SMS']),
      dnSize: z.string().optional(),
      category: z.enum([
        'maintenance-shaft',
        'maintenance-chamber',
        'maintenance-hole',
        'accessory',
      ]),
      order: z.number().default(99),
      shortDescription: z.string(),
      cardUseCase: z.string(),
      // Supplied product-overview paragraph, set above At a glance. Distinct
      // from shortDescription (the hero line) and from the markdown body
      // (the sidebar caption).
      overview: z.string().optional(),
      heroImage: image().optional(),
      heroImageAlt: z.string().optional(),
      productImage: image().optional(),
      productImageAlt: z.string().optional(),
      // 'light' = the exact backdrop colour baked into the "-clover" 3D
      // renders (see --color-render-bg); 'white' = real photography shot on
      // true white. Picking the wrong one leaves a visible seam around the
      // image — match whatever colour is actually in the image file's own
      // background, not a stylistic preference.
      productImageBackground: z.enum(['dark', 'light', 'white']).default('light'),
      // Larger, more detailed shot for the product page's own sidebar — e.g.
      // a cutaway revealing an internal feature — falls back to productImage
      // (used for every card thumbnail sitewide) when omitted.
      productImageDetail: image().optional(),
      productImageDetailAlt: z.string().optional(),
      // A cutaway/detail shot is very often a different asset type (real
      // photography) to the card thumbnail (a 3D render) — needs its own
      // background colour rather than inheriting productImageBackground,
      // or a real-white detail photo shows the same seam bug against a
      // container tinted for a render. Defaults to productImageBackground's
      // own default rather than assuming white, since most products don't
      // set a productImageDetail at all.
      productImageDetailBackground: z.enum(['dark', 'light', 'white']).default('light'),
      countryOfManufacture: z.string().optional(),
      // Named separately from manufacturerNote so the About page can list
      // it as one of a uniform set of facts across every product.
      manufacturer: z.string().optional(),
      manufacturerNote: z.string().optional(),
      atAGlance: z.array(atAGlanceRow).default([]),
      specSections: z.array(specSection).default([]),
      configurationsIntro: z.string().optional(),
      configurations: z.array(configRow).default([]),
      configDiagram: image().optional(),
      configDiagramAlt: z.string().optional(),
      configDiagramCaption: z.string().optional(),
      configGroupsIntro: z.string().optional(),
      configGroups: z.array(configGroup).default([]),
      // Real product photos placed alongside the schematic config diagram —
      // photographic proof next to the plan-view icons, not a replacement.
      configPhotos: z.array(photoItem(image)).default([]),
      // Manufacturer assembly renders. Every render in the supplied set
      // includes the lateral connection, which is an optional on-site
      // addition rather than part of the base — assemblyRendersIntro says so
      // once for the whole set instead of repeating it in every caption.
      assemblyRenders: z.array(assemblyRender(image)).default([]),
      assemblyRendersIntro: z.string().optional(),
      // Real photos of the individual parts (cone, riser, ...) to sit beside
      // the parts table, rather than only the schematic renders.
      componentPhotos: z.array(photoItem(image)).default([]),
      installationSections: z.array(installSection(image)).default([]),
      standards: z.array(standard).default([]),
      faqs: z.array(faqItem).default([]),
      downloads: z.array(download).default([]),
      seoTitle: z.string().optional(),
      seoDescription: z.string().optional(),
    }),
});

export const collections = { products };
