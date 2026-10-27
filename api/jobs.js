// 新加坡职位查询：凭查询码返回全部职位。职位数据 _jobs.json 由 tools/build.py 生成，不放在公开静态文件里。
// 查询码只存哈希（_codes.json），用 tools/job_codes.py 生成和作废。同一 IP 15 分钟内输错 10 次就暂停（单实例内存计数，尽力而为）。
const crypto = require('crypto');
const JOBS = require('./_jobs.json');
const CODES = require('./_codes.json');
const ALLOWED_HOSTS = ['visas.run', 'www.visas.run', 'alpaca-overseas.vercel.app'];
const WINDOW_MS = 15 * 60 * 1000, MAX_FAILS = 10;
const fails = new Map();

const allowedOrigin = (origin) => {
  try {
    const h = new URL(origin).hostname;
    return ALLOWED_HOSTS.includes(h) || /^alpaca-overseas-[a-z0-9-]+\.vercel\.app$/.test(h);
  } catch { return false; }
};

const recent = (ip) => (fails.get(ip) || []).filter((t) => Date.now() - t < WINDOW_MS);

// 忽略大小写、空格和横线：yt abcd-2345 和 YT-ABCD-2345 是同一个码
const hash = (code) => crypto.createHash('sha256').update(String(code).toUpperCase().replace(/[\s-]+/g, '')).digest('hex');

module.exports = async (req, res) => {
  res.setHeader('Cache-Control', 'no-store');
  if (req.method !== 'POST') { res.setHeader('Allow', 'POST'); return res.status(405).json({ error: 'method not allowed' }); }
  if (!String(req.headers['content-type'] || '').startsWith('application/json')) return res.status(415).json({ error: 'unsupported' });
  const origin = req.headers.origin;
  if (origin && !allowedOrigin(origin)) return res.status(403).json({ error: 'forbidden' });
  const ip = String(req.headers['x-forwarded-for'] || '').split(',')[0].trim() || 'unknown';
  if (recent(ip).length >= MAX_FAILS) return res.status(429).json({ error: '输错次数太多，请 15 分钟后再试' });

  const code = req.body && typeof req.body === 'object' ? String(req.body.code || '').slice(0, 40) : '';
  if (!code || !Object.prototype.hasOwnProperty.call(CODES, hash(code))) {
    const list = recent(ip);
    list.push(Date.now());
    fails.set(ip, list);
    if (fails.size > 5000) for (const [k, v] of fails) if (Date.now() - v[v.length - 1] >= WINDOW_MS) fails.delete(k);
    return res.status(401).json({ error: '查询码不对，请检查后再输入' });
  }
  res.status(200).json({ jobs: JOBS });
};
