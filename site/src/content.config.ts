import { defineCollection, z } from 'astro:content';
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

const installSection = z.object({
  heading: z.string(),
  body: z.string(), // markdown-ish plain text, rendered with line breaks
  bullets: z.array(z.string()).optional(),
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
  summary: z.string().optional(), // short sub-label shown next to the heading, e.g. "8 configurations"
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
      productImageBackground: z.enum(['dark', 'light']).default('light'),
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
      assemblyDiagram: image().optional(),
      assemblyDiagramAlt: z.string().optional(),
      assemblyDiagramCaption: z.string().optional(),
      installationSections: z.array(installSection).default([]),
      standards: z.array(standard).default([]),
      faqs: z.array(faqItem).default([]),
      downloads: z.array(download).default([]),
      seoTitle: z.string().optional(),
      seoDescription: z.string().optional(),
    }),
});

export const collections = { products };
