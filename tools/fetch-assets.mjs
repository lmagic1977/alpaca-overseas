// Vercel 构建时运行：下载 Unsplash 图片和图标库到站点目录，网站不依赖外部图床和 CDN。
import { readFile, writeFile, mkdir } from 'node:fs/promises';

const root = new URL('..', import.meta.url);
const images = JSON.parse(await readFile(new URL('tools/images.json', root), 'utf8'));
await mkdir(new URL('img/', root), { recursive: true });
await mkdir(new URL('vendor/', root), { recursive: true });

async function get(url, tries = 3) {
  for (let i = 1; i <= tries; i++) {
    try {
      const r = await fetch(url);
      if (!r.ok) throw new Error('HTTP ' + r.status);
      return Buffer.from(await r.arrayBuffer());
    } catch (e) {
      if (i === tries) throw e;
      await new Promise((ok) => setTimeout(ok, 800 * i));
    }
  }
}

const lucide = await get('https://unpkg.com/lucide@0.469.0/dist/umd/lucide.min.js');
await writeFile(new URL('vendor/lucide.min.js', root), lucide);
console.log('lucide ok', lucide.length);

let failed = 0;
await Promise.all(Object.entries(images).map(async ([name, id]) => {
  for (const [suffix, w] of [['', 1800], ['-s', 800]]) {
    const url = `https://images.unsplash.com/photo-${id}?w=${w}&q=72&fm=jpg&fit=crop`;
    try {
      const buf = await get(url);
      await writeFile(new URL(`img/${name}${suffix}.jpg`, root), buf);
      console.log('img ok', name + suffix, buf.length);
    } catch (e) {
      failed++;
      console.log('IMG FAILED', name + suffix, id, e.message);
    }
  }
}));
console.log('done, failed:', failed);
