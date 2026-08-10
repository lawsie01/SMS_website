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
  code: z.string(),
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
      countryOfManufacture: z.string().optional(),
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
      assemblyDiagram: image().optional(),
      assemblyDiagramAlt: z.string().optional(),
      assemblyDiagramCaption: z.string().optional(),
      // Same idea for the "Other components" table — real photos of the
      // individual parts (cone, riser, ...) rather than only the schematic.
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
