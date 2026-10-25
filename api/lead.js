// 接收官网"预约私人顾问"表单。目前写入 Vercel 运行日志，接入邮箱或企业微信后在这里转发。
// 防滥用：只收本站发来的 JSON；隐藏字段和填写时间挡机器人；同一 IP 10 分钟最多 5 次（单实例内存计数，尽力而为）。
const ALLOWED_HOSTS = ['visas.run', 'www.visas.run', 'alpaca-overseas.vercel.app'];
const WINDOW_MS = 10 * 60 * 1000, MAX_PER_WINDOW = 5;
const hits = new Map();

const allowedOrigin = (origin) => {
  try {
    const h = new URL(origin).hostname;
    return ALLOWED_HOSTS.includes(h) || /^alpaca-overseas-[a-z0-9-]+\.vercel\.app$/.test(h);
  } catch { return false; }
};

const limited = (ip) => {
  const now = Date.now();
  const list = (hits.get(ip) || []).filter((t) => now - t < WINDOW_MS);
  list.push(now);
  hits.set(ip, list);
  if (hits.size > 5000) for (const [k, v] of hits) if (now - v[v.length - 1] >= WINDOW_MS) hits.delete(k);
  return list.length > MAX_PER_WINDOW;
};

module.exports = async (req, res) => {
  res.setHeader('Cache-Control', 'no-store');
  if (req.method !== 'POST') { res.setHeader('Allow', 'POST'); return res.status(405).json({ error: 'method not allowed' }); }
  if (!String(req.headers['content-type'] || '').startsWith('application/json')) return res.status(415).json({ error: 'unsupported' });
  const origin = req.headers.origin;
  if (origin && !allowedOrigin(origin)) return res.status(403).json({ error: 'forbidden' });
  const ip = String(req.headers['x-forwarded-for'] || '').split(',')[0].trim() || 'unknown';
  if (limited(ip)) return res.status(429).json({ error: '提交太频繁，请稍后再试' });

  const b = req.body && typeof req.body === 'object' ? req.body : {};
  // 机器人：隐藏字段被填了，或打开页面不到 1.5 秒就提交。假装成功，不记录。
  if (b.website || (typeof b.t === 'number' && b.t < 1500)) return res.status(200).json({ ok: true });
  // 去掉控制字符
  const clip = (v, n) => String(v == null ? '' : v).replace(/[\u0000-\u001f\u007f\u2028\u2029]+/g, ' ').trim().slice(0, n);
  const lead = {
    name: clip(b.name, 60), contact: clip(b.contact, 100), service: clip(b.service, 40),
    when: clip(b.when, 40), msg: clip(b.msg, 2000), at: new Date().toISOString(),
  };
  if (!lead.name || !lead.contact) return res.status(400).json({ error: '请填写称呼和联系方式' });
  console.log('NEW_LEAD ' + JSON.stringify(lead));
  res.status(200).json({ ok: true });
};
