// 羊驼出海 · 各页面共用脚本。每段先检查本页有没有对应元素，没有就跳过。
var esc = function (s) { return String(s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); };
var sgd = function (n) { return 'S$' + Math.round(n).toLocaleString('en-US'); };
// 行业 → 配图
var IND_PIC = { '餐饮': 'job-chef', '酒店': 'job-hotel', '建筑': 'job-build', '司机': 'job-driver', '美业': 'job-salon', '工厂': 'job-factory' };
var indPic = function (ind) { var k = Object.keys(IND_PIC).filter(function (x) { return ind.indexOf(x) === 0; })[0]; return '/img/' + (IND_PIC[k] || 'sg-bay') + '-s.jpg'; };
var ph = function (src, alt) { return '<span class="ph"><img src="' + src + '" alt="' + esc(alt || '') + '" loading="lazy" decoding="async"></span>'; };
// 图片加载失败就移除，露出底色（不用 onerror 属性，安全策略禁止内联脚本）
document.addEventListener('error', function (e) { if (e.target.tagName === 'IMG' && e.target.closest('.ph')) e.target.remove(); }, true);
[].forEach.call(document.querySelectorAll('.ph img'), function (img) { if (img.complete && !img.naturalWidth) img.remove(); });
var jobLink = function (j) {
  return '/contact?service=' + encodeURIComponent('新加坡工作签证') + '&msg=' + encodeURIComponent('【咨询职位 ' + j.id + '】' + j.t + (j.co ? '（' + j.co + '）' : '') + '，' + (j.pay || '') + '。');
};

// 手机菜单
(function () {
  var btn = document.getElementById('menu-btn'), nav = document.getElementById('main-nav');
  if (!btn) return;
  btn.addEventListener('click', function () {
    var open = nav.classList.toggle('open');
    btn.setAttribute('aria-expanded', open ? 'true' : 'false');
  });
})();

// 岗位总数
(function () {
  if (!window.__JOBS) return;
  document.querySelectorAll('[data-jobs-count]').forEach(function (el) { el.textContent = window.__JOBS.length; });
})();

// 首页轮播：横向滚动吸附，自动播放，悬停或触摸时暂停
(function () {
  var box = document.getElementById('slides');
  if (!box) return;
  var slides = box.children, dots = document.querySelectorAll('#dots button'), cur = 0, timer;
  var reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  function go(i) {
    cur = (i + slides.length) % slides.length;
    box.scrollTo({ left: cur * box.clientWidth, behavior: reduce ? 'auto' : 'smooth' });
  }
  function mark() {
    cur = Math.round(box.scrollLeft / box.clientWidth);
    dots.forEach(function (d, i) { d.setAttribute('aria-current', i === cur ? 'true' : 'false'); });
  }
  function play() { stop(); if (!reduce) timer = setInterval(function () { go(cur + 1); }, 5500); }
  function stop() { clearInterval(timer); }
  dots.forEach(function (d, i) { d.addEventListener('click', function () { go(i); play(); }); });
  document.getElementById('prev').addEventListener('click', function () { go(cur - 1); play(); });
  document.getElementById('next').addEventListener('click', function () { go(cur + 1); play(); });
  var t;
  box.addEventListener('scroll', function () { clearTimeout(t); t = setTimeout(mark, 60); }, { passive: true });
  var root = box.parentNode;
  root.addEventListener('mouseenter', stop);
  root.addEventListener('mouseleave', play);
  root.addEventListener('focusin', stop);
  root.addEventListener('focusout', play);
  box.addEventListener('touchstart', stop, { passive: true });
  box.addEventListener('touchend', play, { passive: true });
  document.addEventListener('visibilitychange', function () { document.hidden ? stop() : play(); });
  mark();
  play();
})();

// 首页热门岗位
(function () {
  var rail = document.getElementById('jobrail');
  if (!rail || !window.__JOBS) return;
  var seen = {};
  // 每个行业挑最新、有底薪的，凑 8 个，看起来更丰富
  var picks = window.__JOBS.filter(function (j) { return j.b; }).filter(function (j) {
    seen[j.ind] = (seen[j.ind] || 0) + 1;
    return seen[j.ind] <= 2;
  }).slice(0, 8);
  rail.innerHTML = picks.map(function (j) {
    var meta = [j.ind.split('/')[0]].concat(j.p.slice(0, 2));
    if (j.hs) meta.push('包住');
    return '<a class="jcard" href="' + jobLink(j) + '"><span class="ph">' + '<img src="' + indPic(j.ind) + '" alt="" loading="lazy" decoding="async">' +
      '<span class="pay">' + sgd(j.b) + '<small> 起</small></span></span><span class="body"><b>' + esc(j.t) + '</b><span class="meta">' +
      meta.map(function (m) { return '<span>' + esc(m) + '</span>'; }).join('') + '</span></span></a>';
  }).join('');
})();

// 咨询表单：从链接参数预填服务和留言
(function () {
  var form = document.getElementById('lead');
  if (!form) return;
  var $ = function (id) { return document.getElementById(id); };
  var sel = $('f-service');
  var qs = new URLSearchParams(location.search);
  if (qs.get('service')) {
    var v = qs.get('service');
    if (![].some.call(sel.options, function (o) { return o.value === v; })) { var o = document.createElement('option'); o.textContent = v; sel.appendChild(o); }
    sel.value = v;
  }
  if (qs.get('msg')) $('f-msg').value = qs.get('msg');
  var started = Date.now();
  form.addEventListener('submit', function (e) {
    e.preventDefault();
    var name = $('f-name').value.trim(), contact = $('f-contact').value.trim(), err = $('f-err');
    if (!name || !contact) { err.textContent = '请填写称呼和联系方式，顾问才能联系到你。'; err.hidden = false; return; }
    err.hidden = true;
    var btn = form.querySelector('button[type=submit]');
    btn.disabled = true;
    var done = function () {
      $('f-ok-txt').textContent = name + '，关于「' + sel.value + '」的咨询已记录，顾问会通过 ' + contact + ' 联系你。';
      $('f-ok').hidden = false;
      btn.disabled = false;
    };
    var payload = { name: name, contact: contact, service: sel.value, when: $('f-when').value, msg: $('f-msg').value.trim(), website: $('f-site') ? $('f-site').value : '', t: Date.now() - started };
    var endpoint = document.querySelector('meta[name="lead-endpoint"]');
    if (!endpoint || !window.fetch) { done(); return; }
    fetch(endpoint.content, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) })
      .then(function (r) { if (!r.ok) throw new Error(r.status); done(); })
      .catch(function () { btn.disabled = false; err.textContent = '提交没有成功，请稍后再试。'; err.hidden = false; });
  });
})();

// 新加坡 EP / S Pass 自测
(function () {
  var $ = function (id) { return document.getElementById(id); };
  var form = $('sgc');
  if (!form) return;
  form.addEventListener('submit', function (e) { e.preventDefault(); });
  var radio = function (name) { var el = form.querySelector('input[name="' + name + '"]:checked'); return el ? el.value : 'u'; };
  // 23 岁为起点、45 岁封顶，中间按线性估算
  var floor = function (age, lo, hi) {
    var a = Math.min(45, Math.max(23, age));
    return Math.round((lo + (hi - lo) * (a - 23) / 22) / 50) * 50;
  };
  var pts = function (v) { return v === 'u' ? [0, 20] : [Number(v), Number(v)]; };

  function render() {
    var age = Number($('sg-age').value) || 0;
    var sal = Number($('sg-salary').value) || 0;
    var fin = radio('sg-sector') === 'fin';
    var small = radio('sg-size') === 'small';
    $('sg-c3-set').hidden = small;
    $('sg-c4-set').hidden = small;

    var epMin = fin ? floor(age, 6200, 11800) : floor(age, 5600, 10700);
    var spMin = fin ? floor(age, 3800, 5650) : floor(age, 3300, 4800);

    var rows = [
      ['C1 薪资水平', pts(radio('sg-c1'))],
      ['C2 学历', pts(radio('sg-c2'))],
      ['C3 多元化' + (small ? '（小公司默认）' : ''), small ? [10, 10] : pts(radio('sg-c3'))],
      ['C4 本地雇佣' + (small ? '（小公司默认）' : ''), small ? [10, 10] : pts(radio('sg-c4'))]
    ];
    if ($('sg-c5').checked) { var c5 = $('sg-c5-third').checked ? 10 : 20; rows.push(['C5 紧缺职业加分', [c5, c5]]); }
    if ($('sg-c6').checked) rows.push(['C6 战略项目加分', [10, 10]]);
    var lo = 0, hi = 0;
    rows.forEach(function (r) { lo += r[1][0]; hi += r[1][1]; });

    var exempt = sal >= 22500;
    var epSalaryOk = sal >= epMin;
    var spOk = sal >= spMin;
    var v = '', sub = '', good = false;
    if (exempt) {
      v = '月薪达到 S$22,500，EP 免 COMPASS 评估'; good = true;
      sub = '只需满足最低薪资和常规审核要求。';
    } else if (epSalaryOk && lo >= 40) {
      v = '符合 EP 申请条件'; good = true;
      sub = '月薪高于 ' + age + ' 岁的 EP 最低要求 ' + sgd(epMin) + '，COMPASS 预计 ' + lo + (hi > lo ? '–' + hi : '') + ' 分。';
    } else if (epSalaryOk && hi >= 40) {
      v = 'EP 有机会，取决于未确定的几项';
      sub = '月薪达到 EP 最低要求 ' + sgd(epMin) + '，COMPASS 在 ' + lo + '–' + hi + ' 分之间。把“不确定”的项目弄清楚就能判断。';
    } else if (epSalaryOk) {
      v = 'EP 积分不足 40 分';
      sub = '月薪达到 EP 最低要求，但 COMPASS 只有 ' + hi + ' 分。' + (spOk ? '可以考虑 S Pass，或调整薪资结构后再评估。' : '');
    } else if (spOk) {
      v = '更适合申请 S Pass';
      sub = '月薪低于 ' + age + ' 岁的 EP 最低要求 ' + sgd(epMin) + '，但高于 S Pass 最低要求 ' + sgd(spMin) + '。S Pass 受雇主配额限制，不看 COMPASS。';
    } else {
      v = '目前月薪未达到工作准证要求';
      sub = age + ' 岁的 S Pass 最低月薪约 ' + sgd(spMin) + '，EP 约 ' + sgd(epMin) + '。可以和顾问聊聊其他路径。';
    }
    $('sg-verdict').textContent = v;
    $('sg-verdict').classList.toggle('good', good);
    $('sg-sub').textContent = sub;

    var showMeter = !exempt && epSalaryOk;
    $('sg-meter').hidden = !showMeter;
    $('sg-score').innerHTML = lo + (hi > lo ? '<small>–' + hi + '</small>' : '') + '<small> 分</small>';
    $('sg-fill').style.width = Math.min(100, lo / 80 * 100) + '%';
    $('sg-range').style.left = Math.min(100, lo / 80 * 100) + '%';
    $('sg-range').style.width = Math.max(0, Math.min(100, hi / 80 * 100) - Math.min(100, lo / 80 * 100)) + '%';

    var ledger = '<div><span>EP 最低月薪（' + age + ' 岁，' + (fin ? '金融业' : '非金融') + '）</span><span>' + sgd(epMin) + '</span></div>' +
      '<div><span>S Pass 最低月薪</span><span>' + sgd(spMin) + '</span></div>';
    if (showMeter) rows.forEach(function (r) {
      var unk = r[1][0] !== r[1][1];
      ledger += '<div' + (unk ? ' class="na"' : '') + '><span>' + r[0] + '</span><span>' + (unk ? '0–20' : r[1][0]) + '</span></div>';
    });
    $('sg-ledger').innerHTML = ledger;

    form.dataset.summary = '【EP/S Pass 自测】' + age + ' 岁，月薪 ' + sgd(sal) + '，' + (fin ? '金融业' : '非金融行业') + '。结果：' + v + (showMeter ? '（COMPASS ' + lo + (hi > lo ? '–' + hi : '') + ' 分）' : '') + '。';
  }

  form.addEventListener('input', render);
  form.addEventListener('change', render);
  $('sg-cta').addEventListener('click', function () {
    this.href = '/contact?service=' + encodeURIComponent('新加坡工作签证') + '&msg=' + encodeURIComponent(form.dataset.summary || '');
  });
  render();
})();

// 新加坡职位查询
(function () {
  var JOBS = window.__JOBS || [];
  var $ = function (id) { return document.getElementById(id); };
  var list = $('jlist');
  if (!list) return;
  var PAGE = 20, shown = PAGE, sort = 'new';
  var fill = function (sel, values) { values.forEach(function (v) { var o = document.createElement('option'); o.value = o.textContent = v; sel.appendChild(o); }); };
  var tally = function (key) { var m = {}; JOBS.forEach(function (j) { [].concat(j[key]).forEach(function (v) { if (v) m[v] = (m[v] || 0) + 1; }); }); return m; };
  var byCount = function (m) { return Object.keys(m).sort(function (a, b) { return m[b] - m[a]; }); };
  var inds = tally('ind');
  fill($('jind'), byCount(inds));
  fill($('jpass'), byCount(tally('p')));
  fill($('jnt'), byCount(tally('nt')));
  fill($('jrg'), byCount(tally('rg')).filter(function (v) { return v !== '未注明'; }));
  var latest = JOBS.reduce(function (a, j) { return j.d > a ? j.d : a; }, '');
  if ($('jupd')) $('jupd').textContent = '更新于 ' + latest;

  // 行业图片按钮，和“行业”下拉框联动
  var cats = $('jcats');
  cats.innerHTML = '<button type="button" class="cat" data-ind="" aria-pressed="true">' + ph('/img/sg-bay-s.jpg') + '全部<span class="n">' + JOBS.length + '</span></button>' +
    byCount(inds).map(function (k) { return '<button type="button" class="cat" data-ind="' + esc(k) + '" aria-pressed="false">' + ph(indPic(k)) + esc(k.split('/')[0]) + '<span class="n">' + inds[k] + '</span></button>'; }).join('');
  var syncCats = function () { cats.querySelectorAll('.cat').forEach(function (c) { c.setAttribute('aria-pressed', c.dataset.ind === $('jind').value ? 'true' : 'false'); }); };
  cats.addEventListener('click', function (e) {
    var c = e.target.closest('.cat');
    if (!c) return;
    $('jind').value = c.dataset.ind;
    syncCats();
    reset();
  });

  function filtered() {
    var q = $('jq').value.trim().toLowerCase().split(/\s+/).filter(Boolean);
    var nt = $('jnt').value;
    var ind = $('jind').value, pass = $('jpass').value, rg = $('jrg').value, min = Number($('jmin').value);
    var hs = $('jhs').checked, al = $('jal').checked;
    var out = JOBS.filter(function (j) {
      if (ind && j.ind !== ind) return false;
      if (pass && j.p.indexOf(pass) === -1) return false;
      if (rg && j.rg !== rg) return false;
      if (nt && j.nt.length && j.nt.indexOf(nt) === -1) return false;
      if (min && !(j.b >= min)) return false;
      if (hs && !j.hs) return false;
      if (al && !j.al) return false;
      if (q.length) { var hay = (j.t + ' ' + j.co + ' ' + j.pay + ' ' + j.loc + ' ' + j.raw + (j.hs ? ' 包住' : '')).toLowerCase(); if (!q.every(function (w) { return hay.indexOf(w) !== -1; })) return false; }
      return true;
    });
    if (sort === 'pay') out.sort(function (a, b) { return (b.b || 0) - (a.b || 0); });
    return out;
  }

  function row(j) {
    var meta = [];
    if (j.p.length) meta.push('<span class="pp">' + esc(j.p.join(' · ')) + '</span>');
    if (j.nt.length) meta.push('<span>限' + esc(j.nt.join('/')) + '籍</span>');
    if (j.rg !== '未注明') meta.push('<span>' + esc(j.rg) + '</span>');
    if (j.hs) meta.push('<span class="perk">包住</span>');
    if (j.al) meta.push('<span class="perk">住补</span>');
    var dl = [['薪资', j.pay], ['工时与休息', j.h], ['地点 / 编号', j.loc], ['地区', j.rg], ['发布日期', j.d], ['职位编号', j.id]]
      .filter(function (x) { return x[1]; })
      .map(function (x) { return '<div><dt>' + x[0] + '</dt><dd>' + esc(x[1]) + '</dd></div>'; }).join('');
    return '<details class="job"><summary>' + '<span class="th">' + ph(indPic(j.ind)) + '</span>' +
      '<span class="jt">' + esc(j.t) + '<small>' + esc(j.co || j.ind) + '</small><span class="jm">' + meta.join('') + '</span></span>' +
      '<span class="jb">' + (j.b ? sgd(j.b) + '<small>底薪起 / 月</small>' : '<small>薪资面议</small>') + '</span></summary>' +
      '<div class="job-body"><dl>' + dl + '</dl>' + (j.raw ? '<pre>' + esc(j.raw) + '</pre>' : '') +
      '<div class="acts"><a class="btn green sm" href="' + jobLink(j) + '">咨询这个职位</a><span>顾问帮你核实岗位并安排面试</span></div></div></details>';
  }

  function render() {
    var rows = filtered();
    $('jcount').textContent = rows.length;
    list.innerHTML = rows.length ? rows.slice(0, shown).map(row).join('') : '<p class="jobs-empty">没有符合条件的职位，试试放宽筛选条件。</p>';
    $('jmore').hidden = rows.length <= shown;
    $('jmore').textContent = '显示更多职位（还有 ' + Math.max(0, rows.length - shown) + ' 个）';
  }
  function reset() { shown = PAGE; render(); }
  ['jq', 'jind', 'jpass', 'jnt', 'jrg', 'jmin', 'jhs', 'jal'].forEach(function (id) {
    $(id).addEventListener(id === 'jq' ? 'input' : 'change', function () { if (id === 'jind') syncCats(); reset(); });
  });
  document.querySelectorAll('.sortby button').forEach(function (b) {
    b.addEventListener('click', function () {
      sort = b.dataset.sort;
      document.querySelectorAll('.sortby button').forEach(function (x) { x.setAttribute('aria-pressed', x === b ? 'true' : 'false'); });
      reset();
    });
  });
  $('jmore').addEventListener('click', function () { shown += PAGE; render(); });
  render();
})();
