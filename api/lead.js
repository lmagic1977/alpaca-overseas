// 接收官网"预约私人顾问"表单。目前写入 Vercel 运行日志，接入邮箱或企业微信后在这里转发。
module.exports = async (req, res) => {
  if (req.method !== 'POST') return res.status(405).json({ error: 'method not allowed' });
  const b = req.body || {};
  const clip = (v, n) => String(v || '').trim().slice(0, n);
  const lead = {
    name: clip(b.name, 60), contact: clip(b.contact, 100), service: clip(b.service, 40),
    when: clip(b.when, 40), msg: clip(b.msg, 2000), at: new Date().toISOString(),
  };
  if (!lead.name || !lead.contact) return res.status(400).json({ error: '请填写称呼和联系方式' });
  console.log('NEW_LEAD ' + JSON.stringify(lead));
  res.status(200).json({ ok: true });
};
