import type { APIRoute } from 'astro';
import { getCollection } from 'astro:content';

export const prerender = true;

export const GET: APIRoute = async () => {
  const products = await getCollection('products');

  const entries = products.map((p) => ({
    id: p.id,
    url: `/products/${p.id}/`,
    title: p.data.title,
    brand: p.data.brand,
    dnSize: p.data.dnSize ?? '',
    description: p.data.shortDescription,
    partCodes: p.data.configurations.map((c) => c.code),
    standardCodes: p.data.standards.map((s) => s.code),
    faqText: p.data.faqs.map((f) => `${f.question} ${f.answer}`).join(' '),
  }));

  return new Response(JSON.stringify(entries), {
    headers: { 'Content-Type': 'application/json' },
  });
};
