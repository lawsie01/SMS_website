import type { APIRoute } from 'astro';
import { getCollection } from 'astro:content';

export const prerender = true;

export const GET: APIRoute = async () => {
  const products = await getCollection('products');
  // Fittings & accessories aren't ready for launch — excluded so search
  // never surfaces a result for a page that [slug].astro's getStaticPaths
  // won't build. Re-enable together with that filter.
  const searchable = products.filter((p) => p.data.category !== 'accessory');

  const entries = searchable.map((p) => ({
    id: p.id,
    url: `/products/${p.id}/`,
    title: p.data.title,
    brand: p.data.brand,
    dnSize: p.data.dnSize ?? '',
    description: p.data.shortDescription,
    // code is optional on a configuration — riser pipe and a few other parts
    // are not coded separately — so mapping it straight through puts nulls in
    // the index, and the client normalises every code with toLowerCase.
    partCodes: p.data.configurations.map((c) => c.code).filter((c): c is string => Boolean(c)),
    standardCodes: p.data.standards.map((s) => s.code),
    faqText: p.data.faqs.map((f) => `${f.question} ${f.answer}`).join(' '),
  }));

  return new Response(JSON.stringify(entries), {
    headers: { 'Content-Type': 'application/json' },
  });
};
