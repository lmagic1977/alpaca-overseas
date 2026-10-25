// Vercel 构建时运行：把 site/ 复制到 public/，再下载 Unsplash 图片到 public/img/，网站不依赖外部图床。
import { readFile, writeFile, mkdir, cp, rm } from 'node:fs/promises';

const root = new URL('..', import.meta.url);
const out = new URL('public/', root);
await rm(out, { recursive: true, force: true });
await cp(new URL('site/', root), out, { recursive: true });
await mkdir(new URL('img/', out), { recursive: true });
const images = JSON.parse(await readFile(new URL('tools/images.json', root), 'utf8'));

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

let failed = 0;
await Promise.all(Object.entries(images).map(async ([name, id]) => {
  for (const [suffix, w] of [['', 1800], ['-s', 800]]) {
    const url = `https://images.unsplash.com/photo-${id}?w=${w}&q=72&fm=jpg&fit=crop`;
    try {
      const buf = await get(url);
      await writeFile(new URL(`img/${name}${suffix}.jpg`, out), buf);
      console.log('img ok', name + suffix, buf.length);
    } catch (e) {
      failed++;
      console.log('IMG FAILED', name + suffix, id, e.message);
    }
  }
}));
console.log('done, failed:', failed);
