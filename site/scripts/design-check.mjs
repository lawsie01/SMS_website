// Runs the design detector against the built site rather than the source
// tree. The static scan over src/ returns zero on this project because the
// rules that actually fire here — line length, undersized text, cramped
// padding — need a rendered box to measure, and Astro components don't have
// one until they're built. This builds, serves dist on a spare port, points
// the detector at every route, and tears the server down again.
//
// Usage: npm run design:check            (builds first)
//        npm run design:check -- --no-build
//
// The detector drives headless Chrome, which refuses to start as root. In a
// container that runs as root, run it as an unprivileged user:
//   su <user> -s /bin/bash -c 'cd site && node scripts/design-check.mjs'
import { spawn, spawnSync } from 'node:child_process';
import { createServer } from 'node:http';
import { readFile, stat } from 'node:fs/promises';
import { join, extname } from 'node:path';

const PORT = 4399;
const DIST = new URL('../dist/', import.meta.url).pathname;

const ROUTES = [
  '/',
  '/products/',
  '/products/dn375-maintenance-shaft/',
  '/products/dn600-maintenance-chamber/',
  '/products/dn1000-maintenance-hole/',
  '/why-plastic-vs-concrete/',
  '/applications/',
  '/approvals/',
  '/technical-resources/',
  '/technical-resources/request-access/',
  '/about/',
  '/contact/',
];

const TYPES = {
  '.html': 'text/html; charset=utf-8',
  '.css': 'text/css; charset=utf-8',
  '.js': 'text/javascript; charset=utf-8',
  '.json': 'application/json',
  '.svg': 'image/svg+xml',
  '.webp': 'image/webp',
  '.png': 'image/png',
  '.jpg': 'image/jpeg',
  '.woff2': 'font/woff2',
  '.glb': 'model/gltf-binary',
  '.pdf': 'application/pdf',
};

if (!process.argv.includes('--no-build')) {
  const build = spawnSync('npm', ['run', 'build'], { stdio: 'inherit', shell: false });
  if (build.status !== 0) process.exit(build.status ?? 1);
}

// Astro's build emits directory-style routes, so /about/ has to resolve to
// /about/index.html the way Netlify does it in production.
async function resolve(urlPath) {
  let p = decodeURIComponent(urlPath.split('?')[0]);
  if (p.endsWith('/')) p += 'index.html';
  let file = join(DIST, p);
  try {
    if ((await stat(file)).isDirectory()) file = join(file, 'index.html');
  } catch {
    try {
      await stat(join(DIST, p + '/index.html'));
      file = join(DIST, p + '/index.html');
    } catch {
      return null;
    }
  }
  return file;
}

const server = createServer(async (req, res) => {
  const file = await resolve(req.url ?? '/');
  if (!file) {
    res.writeHead(404).end('not found');
    return;
  }
  try {
    const body = await readFile(file);
    res.writeHead(200, { 'content-type': TYPES[extname(file)] ?? 'application/octet-stream' });
    res.end(body);
  } catch {
    res.writeHead(404).end('not found');
  }
});

await new Promise((r) => server.listen(PORT, '127.0.0.1', r));

const urls = ROUTES.map((r) => `http://127.0.0.1:${PORT}${r}`);
console.log(`Scanning ${urls.length} routes on 127.0.0.1:${PORT}\n`);

// The detector prints findings and nothing else, so a clean run is silent —
// indistinguishable from a run that never started. Count what it printed and
// say so either way.
const detect = spawn('npx', ['--yes', 'impeccable@latest', 'detect', ...urls], {
  stdio: ['inherit', 'pipe', 'inherit'],
  shell: false,
});

let out = '';
detect.stdout.on('data', (d) => {
  out += d;
  process.stdout.write(d);
});

const code = await new Promise((r) => detect.on('close', r));
server.close();
// Silence only means clean if the detector actually ran. A failed npx fetch or
// a missing browser also prints nothing to stdout, and reporting that as a
// pass is worse than reporting nothing at all.
if (code !== 0) {
  console.error(`\nDetector exited ${code} without producing findings. This is not a pass.`);
  process.exit(code ?? 1);
}
if (!out.trim()) console.log(`Clean — no anti-patterns across ${urls.length} routes.`);
process.exit(0);
