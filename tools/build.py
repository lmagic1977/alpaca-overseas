# 生成多页面站点到 site/：共用页眉页脚，图标在生成时内联为 SVG（不依赖 CDN）。
# 用法：python3 tools/build.py [lucide-static 的 icons 目录]
# 图标会缓存到 tools/icons.json，之后没有 lucide 目录也能重新生成。
import json, os, re, shutil, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'site')
ICON_CACHE = os.path.join(ROOT, 'tools', 'icons.json')
ICON_DIR = sys.argv[1] if len(sys.argv) > 1 else None
icons = json.load(open(ICON_CACHE)) if os.path.exists(ICON_CACHE) else {}
JOBS = json.loads(open(os.path.join(ROOT, 'src', 'jobs-data.js')).read().split('=', 1)[1].strip().rstrip(';'))
N_JOBS = len(JOBS)
JOBS_UPDATED = max(j['d'] for j in JOBS)
SITE = 'https://visas.run'
BUILD_DATE = __import__('datetime').date.today().isoformat()


def ic(name):
    if name not in icons:
        src = open(os.path.join(ICON_DIR, name + '.svg')).read()
        icons[name] = re.sub(r'\s+', ' ', ''.join(re.findall(r'<(?:path|circle|rect|line|polyline|polygon|ellipse)[^>]*/>', src)))
    return ('<svg class="ico" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
            'stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">' + icons[name] + '</svg>')


ALT = {
    'alpaca-sg': '羊驼拖着行李走过新加坡樟宜机场', 'us-nyc': '美国纽约曼哈顿街景', 'us-gg': '美国旧金山金门大桥',
    'us-esb': '纽约帝国大厦', 'nz-lake': '新西兰湖泊和雪山', 'nz-hills': '新西兰绿色丘陵', 'nz-town': '新西兰小镇街景',
    'sg-mbs': '新加坡滨海湾金沙', 'sg-bay': '新加坡滨海湾', 'sg-merlion': '新加坡鱼尾狮', 'sg-merlion2': '新加坡鱼尾狮公园',
    'mx-gto': '墨西哥瓜纳华托彩色街道', 'mx-angel': '墨西哥城独立天使纪念碑', 'airport': '机场里拖着行李的旅客',
    'airport2': '机场出发大厅', 'meeting': '顾问正在和客户沟通', 'meeting2': '顾问和客户沟通', 'family': '一家人出国旅行',
}


def img(name, alt='', big=False, eager=False):
    """图片放在 .ph 里：加载前/失败时显示渐变底色。"""
    alt = alt or ALT.get(name, '')
    attrs = 'loading="eager" fetchpriority="high"' if eager else 'loading="lazy"'
    if big:
        src = f'src="/img/{name}.jpg" srcset="/img/{name}-s.jpg 800w, /img/{name}.jpg 1800w" sizes="100vw"'
    else:
        src = f'src="/img/{name}-s.jpg"'
    return f'<div class="ph"><img {src} alt="{alt}" {attrs} decoding="async"></div>'


TOP = [('/us', '美国'), ('/nz', '新西兰'), ('/sg', '新加坡'), ('/mx', '墨西哥')]  # 顶部菜单只放四个国家
NAV = [('/', '首页'), ('/us', '美国移民签证'), ('/nz', '新西兰工签'), ('/sg', '新加坡工签'),
       ('/jobs', '新加坡职位'), ('/mx', '墨西哥工签绿卡'), ('/about', '关于我们')]


def page(slug, title, desc, body, scripts=('app.js',), kw='', pic='alpaca-sg', ld=()):
    here = '/sg' if slug == '/jobs' else slug  # 职位查询归在新加坡下
    nav = ''.join(f'<a href="{h}"{" class=\"on\" aria-current=\"page\"" if h == here else ""}>{t}</a>' for h, t in TOP)
    js = ''.join(f'<script src="/{s}"></script>' for s in scripts)
    full_title = title if slug == '/' else f'{title}｜羊驼出海 LLAMA VISA'
    url = SITE + slug
    lds = ''.join(f'<script type="application/ld+json">{json.dumps(x, ensure_ascii=False)}</script>\n' for x in ld_common(slug, title, url) + list(ld))
    return f'''<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{full_title}</title>
<meta name="description" content="{desc}">
<meta name="keywords" content="{kw}">
<meta name="robots" content="index,follow">
<link rel="canonical" href="{url}">
<meta name="applicable-device" content="pc,mobile">
<meta http-equiv="Cache-Control" content="no-transform">
<meta http-equiv="Cache-Control" content="no-siteapp">
<meta name="lead-endpoint" content="/api/lead">
<meta property="og:type" content="website">
<meta property="og:locale" content="zh_CN">
<meta property="og:site_name" content="羊驼出海 LLAMA VISA">
<meta property="og:title" content="{full_title}">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{SITE}/img/{pic}.jpg">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#11866a">
<link rel="icon" href="/favicon.png" type="image/png">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<link rel="stylesheet" href="/styles.css">
{lds}</head>
<body>
<header class="top">
  <div class="wrap">
    <a class="brand" href="/" aria-label="羊驼出海首页"><img class="logo" src="/logo.png" alt="羊驼出海 LLAMA VISA" width="388" height="120"></a>
    <nav class="nav" id="main-nav" aria-label="主导航">{nav}</nav>
  </div>
</header>
<main>
{body}
</main>
<footer>
  <div class="wrap">
    <div class="cols">
      <div>
        <a class="brand pill" href="/"><img class="logo" src="/logo.png" alt="羊驼出海 LLAMA VISA" width="388" height="120"></a>
        <p class="slogan">要出国找羊驼</p>
      </div>
      <nav aria-label="页脚导航">{''.join(f'<a href="{h}">{t}</a>' for h, t in NAV[1:])}<a href="/contact">免费咨询</a></nav>
    </div>
    <div class="legal">
      <p>本站内容仅供参考，不构成法律意见。各国签证与移民政策会调整，以官方最新公布为准，申请结果由相关国家政府机构决定。</p>
      <p>图片来自 Unsplash。© 2026 羊驼出海</p>
    </div>
  </div>
</footer>
{js}
</body>
</html>
'''


ORG = {'@type': 'Organization', '@id': SITE + '/#org', 'name': '羊驼出海', 'alternateName': 'LLAMA VISA',
       'url': SITE + '/', 'logo': SITE + '/logo.png', 'slogan': '要出国找羊驼',
       'description': '美国移民签证、新西兰工作签证、新加坡工作签证、墨西哥工签绿卡办理。'}


def ld_common(slug, title, url):
    if slug == '/':
        return [dict(ORG, **{'@context': 'https://schema.org'}),
                {'@context': 'https://schema.org', '@type': 'WebSite', 'name': '羊驼出海 LLAMA VISA', 'url': SITE + '/',
                 'inLanguage': 'zh-CN', 'publisher': {'@id': SITE + '/#org'}}]
    crumbs = [('首页', SITE + '/')] + ([('新加坡工作签证', SITE + '/sg')] if slug == '/jobs' else []) + [(title.split('｜')[0], url)]
    return [{'@context': 'https://schema.org', '@type': 'BreadcrumbList', 'itemListElement': [
        {'@type': 'ListItem', 'position': i + 1, 'name': n, 'item': u} for i, (n, u) in enumerate(crumbs)]}]


def service_ld(name, desc, country, types):
    return {'@context': 'https://schema.org', '@type': 'Service', 'name': name, 'serviceType': types, 'description': desc,
            'provider': ORG, 'areaServed': {'@type': 'Country', 'name': '中国'},
            'audience': {'@type': 'Audience', 'audienceType': f'想去{country}工作、生活或移民的中国人'}}


def banner(pic, crumb, h1, p, chips=(), acts=''):
    ch = f'<div class="chips">{"".join(f"<span>{c}</span>" for c in chips)}</div>' if chips else ''
    return f'''<section class="banner">
  {img(pic, '', big=True, eager=True)}
  <div class="wrap">
    <nav class="crumb" aria-label="当前位置"><a href="/">首页</a><span>/</span><span>{crumb}</span></nav>
    <h1>{h1}</h1>
    <p>{p}</p>
    {ch}{acts}
  </div>
</section>'''


def head(kicker, h2, p='', side=''):
    return f'<div class="head"><div><span class="kicker">{kicker}</span><h2>{h2}</h2>{f"<p>{p}</p>" if p else ""}</div>{side}</div>'


def vtypes(items):
    return '<div class="vtypes">' + ''.join(
        f'<div class="vtype"><span class="ic">{ic(i)}</span><div><b>{b}<em>{e}</em></b><span>{s}</span></div></div>'
        for i, b, e, s in items) + '</div>'


def icards(items):
    out = []
    for it in items:
        i, h, p = it[:3]
        href = it[3] if len(it) > 3 else None
        tag = f'a class="icard" href="{href}"' if href else 'div class="icard"'
        out.append(f'<{tag}><span class="ic">{ic(i)}</span><h3>{h}</h3><p>{p}</p></{tag.split()[0]}>')
    return '<div class="icards">' + ''.join(out) + '</div>'


def ticks(items):
    return '<ul class="ticks">' + ''.join(f'<li>{ic("check")}<span>{t}</span></li>' for t in items) + '</ul>'


def split(pic, alt, kicker, h2, p, items, acts='', rev=False):
    return f'''<div class="split{' rev' if rev else ''}">
  {img(pic, alt) if not rev else ''}
  <div class="txt"><span class="kicker">{kicker}</span><h2>{h2}</h2>{f"<p>{p}</p>" if p else ""}{ticks(items)}{acts}</div>
  {img(pic, alt) if rev else ''}
</div>'''


def cta(pic='family', h='要出国找羊驼', p='说说你的情况，顾问 1 个工作日内联系你，评估不收费。', href='/contact', label='免费咨询'):
    return f'''<section class="cta">
  {img(pic, '', big=True)}
  <div class="wrap"><div><h2>{h}</h2><p>{p}</p></div><a class="btn sun" href="{href}">{ic('messages-square')}{label}</a></div>
</section>'''


def btn(href, label, kind='green', icon='arrow-right'):
    return f'<a class="btn {kind}" href="{href}">{label}{ic(icon) if icon else ""}</a>'


def consult(service):
    return f'/contact?service={service}'


# ---------------- 首页 ----------------
# 墨西哥身份 → 美签路线（墨西哥页、美国页、首页共用）
def mx_to_us(cls='sec mxus', link=True):
    steps = [('stamp', '办墨西哥工签', '当地雇主申请，领馆面签'),
             ('id-card', '拿居留卡', '入境换领墨西哥临时居留卡'),
             ('house', '在墨西哥住 5–6 个月', '工作、住址、生活记录都齐了'),
             ('plane-takeoff', '在墨西哥申请美签', '以墨西哥居民身份，到当地美国领馆面签')]
    road = ''.join(f'<div><span class="ic">{ic(i)}</span><b>{t}</b><span>{d}</span></div>' for i, t, d in steps)
    more = btn('/mx#to-us', '看墨西哥项目', 'green') if link else btn(consult('墨西哥工签绿卡'), '咨询这条路线', 'green', 'messages-square')
    return f"""<section class="{cls}" id="to-us"><div class="wrap">
  {head('去美国的新路线', '先拿墨西哥身份，再申请美签', '目前去美国我们最推荐的方案：手里有墨西哥居留卡，申请美签时身份更稳，美签没过也还有墨西哥这条退路。', more)}
  <div class="road four mxus-road">{road}</div>
  <div class="chips center"><span>墨西哥长期合法身份</span><span>在当地美国领馆申请</span><span>工作和居住记录完整</span><span>美签之外多一条退路</span></div>
  <p class="fine center">美国签证由美国领事馆审核决定，我们帮你把材料和面签准备好，但不承诺获签结果。</p>
</div></section>"""


SLIDES = [
    ('alpaca-sg', '羊驼出海 · LLAMA VISA', '要出国<em>找羊驼</em>', '美国、新西兰、新加坡、墨西哥。签证、工作、身份，一站帮你办好。',
     btn('/contact', '免费咨询', 'sun', 'messages-square') + btn('#services', '看看能去哪', 'glass')),
    ('us-nyc', '美国移民签证', '去美国，<em>签证绿卡</em>一起规划', '旅游、留学、H-1B、NIW、EB-5，先评估，再挑最稳的那条路。',
     btn('/us', '了解美国', 'sun') + btn(consult('美国移民签证'), '问问顾问', 'glass', 'messages-square')),
    ('nz-lake', '新西兰工作签证', '在新西兰<em>边工作边生活</em>', '认证雇主工签 AEWV，做满条件衔接居留。',
     btn('/nz', '了解新西兰', 'sun') + btn(consult('新西兰工作签证'), '问问顾问', 'glass', 'messages-square')),
    ('sg-merlion', '新加坡工作签证', f'<em data-jobs-count>{N_JOBS}</em> 个新加坡岗位在招', '餐饮、酒店、建筑、司机、工厂，按国籍和底薪一键筛。',
     btn('/jobs', '马上查职位', 'sun', 'search') + btn('/sg#check', 'EP 资格自测', 'glass', 'calculator')),
    ('mx-angel', '墨西哥工签绿卡', '墨西哥绿卡，<em>再签美国</em>', '先拿墨西哥工签和居留卡，住 5–6 个月，再在墨西哥申请美签。',
     btn('/mx#to-us', '看这条路线', 'sun') + btn(consult('墨西哥工签绿卡'), '问问顾问', 'glass', 'messages-square')),
]


def carousel():
    slides = []
    for n, (pic, tag, h, p, acts) in enumerate(SLIDES):
        hn = 'h1' if n == 0 else 'h2'
        slides.append(f'''<div class="slide" role="group" aria-roledescription="slide" aria-label="{n + 1} / {len(SLIDES)}">
    {img(pic, '', big=True, eager=n == 0)}
    <div class="wrap"><span class="tag">{tag}</span><{hn}>{h}</{hn}><p>{p}</p><div class="acts">{acts}</div></div>
  </div>''')
    dots = ''.join(f'<button type="button" aria-label="第 {i + 1} 张"></button>' for i in range(len(SLIDES)))
    return f'''<section class="carousel" aria-roledescription="carousel" aria-label="羊驼出海服务">
  <div class="slides" id="slides">
  {''.join(slides)}
  </div>
  <div class="car-ui"><div class="wrap"><div class="dots" id="dots">{dots}</div>
    <div class="arrows"><button type="button" id="prev" aria-label="上一张">{ic('chevron-left')}</button><button type="button" id="next" aria-label="下一张">{ic('chevron-right')}</button></div></div></div>
</section>'''


SERVICES = [
    ('/us', 'us-gg', '美国', '美国移民签证', ['B1/B2', 'F-1', 'H-1B', 'NIW', 'EB-5']),
    ('/nz', 'nz-hills', '新西兰', '新西兰工作签证', ['AEWV', '绿名单', '技术移民']),
    ('/sg', 'sg-bay', '新加坡', '新加坡工作签证', ['EP', 'S Pass', 'WP', '在线职位']),
    ('/mx', 'mx-gto', '墨西哥', '墨西哥工签绿卡', ['工作居留', '永久居留']),
]

index_body = f'''{carousel()}

<section class="sec stats-sec"><div class="wrap"><div class="stats">
  <div class="stat"><span class="ic">{ic('briefcase')}</span><div><b data-jobs-count>{N_JOBS}</b><span>新加坡在招岗位</span></div></div>
  <div class="stat"><span class="ic">{ic('globe')}</span><div><b>4</b><span>个目的地国家</span></div></div>
  <div class="stat"><span class="ic">{ic('user-check')}</span><div><b>1 对 1</b><span>专属顾问跟到底</span></div></div>
  <div class="stat"><span class="ic">{ic('badge-check')}</span><div><b>0 元</b><span>免费评估</span></div></div>
</div></div></section>

<section class="sec" id="services"><div class="wrap">
  {head('我们能帮你去哪', '四个国家，挑一个出发', '', btn('/contact', '不知道选哪个？问问我们', 'line', 'messages-square'))}
  <div class="svc-grid">
  {''.join(f"""<a class="svc-card" href="{h}">{img(pic, n)}<span class="flag">{f}</span><div class="body"><h3>{n}{ic('arrow-right')}</h3><div class="chips">{''.join(f'<span>{c}</span>' for c in cs)}</div></div></a>""" for h, pic, f, n, cs in SERVICES)}
  </div>
</div></section>

<section class="sec alt"><div class="wrap">
  {head('新加坡热门岗位', '今天在招的新加坡工作', '真实岗位，每天更新。看中了直接让顾问帮你对接。', btn('/jobs', '查看全部职位', 'green', 'search'))}
  <div class="jobrail" id="jobrail"></div>
</div></section>

<section class="sec"><div class="wrap">
  {head('你想怎么出去', '按你的目标来')}
  {icards([
      ('briefcase', '出国打工', '新加坡、新西兰有大量岗位，包住的也不少。', '/jobs'),
      ('graduation-cap', '出国读书', 'F-1 学生签证，从选校到面签都帮你。', '/us'),
      ('id-card', '拿绿卡 / 身份', '美国 NIW、EB-5，墨西哥永居，长期留下来。', '/us'),
      ('building-2', '出海开公司', '新加坡、墨西哥注册公司，老板和团队一起过去。', '/mx'),
  ])}
</div></section>

<section class="sec alt"><div class="wrap">
  {split('airport', '机场里拖着行李的旅客', '为什么找羊驼', '像有个靠谱朋友帮你办签证', '羊驼走山路，每一步都踩稳了再走。我们也这样陪你出海。',
         ['先评估再收费，评估不花钱', '费用一次写清楚，没有隐藏收费', '同一个顾问跟到底，不用来回转', '不乱承诺，风险提前讲明白'],
         btn('/about', '了解羊驼出海', 'line'))}
</div></section>

<section class="sec tint"><div class="wrap">
  {head('怎么办', '5 步，出发')}
  <ol class="steps">
    <li><span class="ic">{ic('messages-square')}</span><b>免费评估</b><span>聊聊你的情况和目标</span></li>
    <li><span class="ic">{ic('list-checks')}</span><b>定方案</b><span>选路径，费用写清楚</span></li>
    <li><span class="ic">{ic('file-check')}</span><b>备材料</b><span>清单 + 模板，逐项核对</span></li>
    <li><span class="ic">{ic('stamp')}</span><b>递交跟进</b><span>补件、面签全程陪</span></li>
    <li><span class="ic">{ic('plane-takeoff')}</span><b>出发落地</b><span>入境、住宿、开户都帮你</span></li>
  </ol>
</div></section>

{cta()}'''

# ---------------- 美国 ----------------
us_body = f'''{banner('us-gg', '美国移民签证', '美国移民签证', '短期签证还是长期绿卡，先评估，再挑最快最稳的路。', ['B1/B2', 'F-1', 'H-1B', 'L-1', 'O-1', 'EB-1A', 'NIW', 'EB-5'],
              f'<div class="acts">{btn(consult("美国移民签证"), "免费评估", "sun", "messages-square")}{btn("#to-us", "墨西哥转美签", "glass", "plane-takeoff")}</div>')}

{mx_to_us('sec tint mxus')}

<section class="sec"><div class="wrap">
  <h2 class="subhead">{ic('plane')}短期签证：旅游、读书、工作</h2>
  {vtypes([
      ('plane', 'B1/B2', '旅游 · 商务', '旅游、探亲、参展。面签模拟，拒签后再申请。'),
      ('graduation-cap', 'F-1 / J-1', '留学 · 交流', '读书、访学。I-20 核对、学习计划陈述。'),
      ('briefcase', 'H-1B', '专业工作', '有美国 offer。配合雇主律师，抽中后面签辅导。'),
      ('building-2', 'L-1', '跨国调派', '国内任职满 1 年，调往美国分公司。'),
      ('award', 'O-1', '杰出人才', '科研、艺术、体育、商业有突出成就。'),
  ])}
  <h2 class="subhead">{ic('id-card')}移民绿卡：长期留下来</h2>
  {vtypes([
      ('sparkles', 'EB-1A', '杰出人才', '满足 10 项标准中 3 项，无需雇主，可加急。'),
      ('trending-up', 'EB-2 NIW', '国家利益豁免', '硕士，或本科 + 5 年经验。无需雇主担保。'),
      ('piggy-bank', 'EB-5', '投资移民', '投资 80 万美元（TEA）或 105 万美元，不看学历语言。'),
      ('landmark', 'EB-1C', '跨国高管', '海外公司高管满 1 年，赴美任高管。'),
      ('users', '亲属移民', '直系 · F 类', '美国公民或绿卡持有人为你申请。'),
  ])}
</div></section>

<section class="sec alt"><div class="wrap">
  {split('us-esb', '纽约帝国大厦', '服务包含', '从评估到拿签，一路陪你', '',
         ['一对一评估：签证还是绿卡，走哪条路', 'DS-160 代填复核、面签预约与模拟', '绿卡证据链规划、推荐信和陈述撰写', 'EB-5 项目尽调、资金来源梳理', 'I-140 / I-485 / 领馆面谈全程跟进'],
         btn(consult('美国移民签证'), '咨询美国移民签证'))}
</div></section>

<section class="sec"><div class="wrap">
  {head('你需要知道', '提前说清楚')}
  {icards([
      ('rotate-ccw', '拒签过也能再签', '214(b) 拒签不是永久的，先复盘原因再申请。'),
      ('clock', '绿卡有排期', '中国大陆出生的申请人，多数类别需要排队。'),
      ('scale', '持牌律师递交', '法律文书由合作的美国执业律师签署。'),
      ('megaphone', '以官方为准', '投资金额等政策以 USCIS 最新公告为准。'),
  ])}
</div></section>

{cta('us-nyc', '想去美国？先免费评估', '告诉我们你的学历、工作和目标，顾问帮你挑路径。', consult('美国移民签证'))}'''

# ---------------- 新西兰 ----------------
NZ_REQ = [
    ('graduation-cap', '学历', '中专及以上', '中专、大专、本科等学历均可报名。'),
    ('briefcase', '工作经验', '2 年以上', '相关工作经验满 2 年。'),
    ('receipt', '经验证明', '社保或工资流水', '必须提供社保缴纳记录或工资流水。'),
    ('languages', '英语', 'PTE 29 分', 'PTE 成绩 29 分及以上。'),
]
NZ_MATCH = [
    ('wrench', '中专、大专', '协助匹配与所学专业相符的工作。'),
    ('graduation-cap', '本科＋学位证', '公司负责协助匹配任何工种的工作。'),
    ('award', '国内技能培训', '本科可协助在国内培训技能，到新西兰再就业。'),
]
NZ_STEPS = [
    ('search', '条件评估'), ('user-check', '岗位匹配'), ('messages-square', '雇主面试'),
    ('pen-line', '签订雇佣合同'), ('send', '递交签证'), ('plane-takeoff', '获批赴新'),
]
NZ_PAY = [('报名', 'pen-line', '¥10,000'), ('面试通过并确认雇佣合同后', 'file-check', '¥40,000'), ('签证获批后', 'stamp', '¥20,000')]

nz_body = f'''{banner('nz-lake', '新西兰工作签证', '新西兰工作项目开放报名', '有技术、有工作经验，想去新西兰工作？不限厨师，多行业岗位可咨询。', ['AEWV', '多行业岗位', '持牌律师服务'],
              f'<div class="acts">{btn(consult("新西兰工作签证"), "免费评估", "sun", "messages-square")}{btn("#fee", "看费用", "glass", "wallet")}</div>')}

<section class="sec" id="job"><div class="wrap">
  {head('申请条件', '这四项都要满足', '具体技能、英语和资质要求因岗位而异，根据你的经历与雇主实际需求匹配。')}
  {vtypes(NZ_REQ)}
</div></section>

<section class="sec alt"><div class="wrap">
  {head('岗位匹配', '按学历匹配工作')}
  {icards(NZ_MATCH)}
  <p class="fine center">工资、工时及食宿待遇，以具体岗位和正式雇佣合同为准。</p>
</div></section>

<section class="sec"><div class="wrap">
  {head('办理流程', '6 步，去新西兰')}
  <ol class="steps6">{''.join(f'<li><span class="ic">{ic(i)}</span><span class="no">{n + 1}</span><b>{t}</b></li>' for n, (i, t) in enumerate(NZ_STEPS))}</ol>
</div></section>

<section class="sec tint" id="fee"><div class="wrap">
  {head('服务费用', '总费用 7 万，分 3 期付')}
  <div class="fee">
    <div class="fee-total"><span>服务总费用</span><b>¥70,000</b><small>人民币，已包含持牌律师服务费</small></div>
    <ol class="fee-steps one">
    {''.join(f'<li><span class="ic">{ic(i)}</span><span class="when">第 {n + 1} 期 · {w}</span><b>{a}</b></li>' for n, (w, i, a) in enumerate(NZ_PAY))}
    </ol>
  </div>
  <p class="note-box">{ic('info')}<span>签证申请费、机票、体检、公证、翻译及保险等第三方费用另计。退款按协议约定，不承诺包签。</span></p>
</div></section>

<section class="sec"><div class="wrap">
  {split('nz-town', '新西兰小镇街景', '先评估，再办理', '有意向请发送这些信息', '顾问看完先帮你评估，符合条件再办理。',
         ['年龄', '职业和工作年限', '学历', '英语水平（PTE 成绩）', '能否提供社保或工资流水'],
         btn(consult('新西兰工作签证'), '发给顾问评估'), rev=True)}
</div></section>

<section class="sec alt"><div class="wrap">
  {head('签证类别', '四种方式去新西兰')}
  {vtypes([
      ('briefcase', 'AEWV', '认证雇主工签', '主流工签。雇主先认证、做岗位核查。'),
      ('leaf', '绿名单', 'Green List', '医护、工程、IT、建筑等紧缺职业，可直通或 2 年后申居留。'),
      ('id-card', 'SMC', '技术移民', '在新西兰工作，学历或收入达标，积分评估。'),
      ('tent-tree', 'WHV', '打工度假', '18–30 岁，名额有限，边玩边打工。'),
  ])}
</div></section>

{cta('nz-hills', '想出国，找羊驼！', '发送年龄＋职业＋工作年限＋学历＋英语水平，顾问先帮你评估。', consult('新西兰工作签证'))}'''

# ---------------- 新加坡 ----------------
sg_check = open(os.path.join(ROOT, 'tools', 'sg-check.html')).read()
sg_body = f'''{banner('sg-merlion', '新加坡工作签证', '新加坡工作签证', '离家近、说中文、税率低。准证由雇主申请，我们帮你把申请做对。', ['EP', 'S Pass', 'Work Permit', 'ONE Pass', 'EntrePass', 'DP'],
              f'<div class="acts">{btn("/jobs", "查新加坡职位", "sun", "search")}{btn("#check", "EP 资格自测", "glass", "calculator")}</div>')}

<section class="sec"><div class="wrap">
  {head('准证类别', '新加坡有哪些工作准证')}
  {vtypes([
      ('briefcase', 'EP', '就业准证', '专业和管理岗。月薪达标 + COMPASS 40 分。'),
      ('wrench', 'S Pass', '中级技术', '中级技术岗，有最低月薪，受配额限制。'),
      ('hard-hat', 'Work Permit', '工作准证', '餐饮、建筑、工厂等岗位，按国籍和行业申请。'),
      ('star', 'ONE Pass', '顶尖人才', '高收入或突出成就，5 年有效，可多家公司工作。'),
      ('rocket', 'EntrePass', '创业准证', '在新加坡创办创新企业的创始人。'),
      ('users', 'DP', '家属准证', 'EP / S Pass 持有人的配偶和孩子。'),
  ])}
</div></section>

<section class="sec alt"><div class="wrap">
  {split('sg-bay', '新加坡滨海湾', '在线查职位', '<span data-jobs-count>{N_JOBS}</span> 个新加坡岗位，随时查', '餐饮、酒店、建筑、司机、美业、工厂，按国籍、准证、底薪、包住筛选。',
         ['真实在招岗位，每天更新', '看中了，顾问帮你核实并安排面试', '不收求职者“买工作”的钱'],
         btn('/jobs', '马上查职位', 'green', 'search'))}
</div></section>

<section class="sec tint" id="check"><div class="wrap">
  {head('小工具', 'EP / S Pass 资格自测', '按新加坡人力部（MOM）公开的最低月薪和 COMPASS 积分估算，填完右边马上出结果。')}
  {sg_check}
</div></section>

<section class="sec"><div class="wrap">
  {head('服务包含', '工签、开公司、PR，一起规划')}
  {icards([
      ('calculator', 'COMPASS 预估', '按规则估分，提前找短板。'),
      ('building-2', '注册公司开户', '老板自己开公司，再给自己办准证。'),
      ('file-check', '准证申请续签', '主申请人和家属准证一起办。'),
      ('id-card', 'PR 规划', '工作几年后申请永久居民。'),
  ])}
</div></section>

{cta('sg-merlion2', '想去新加坡？先免费评估', '有 offer 或想找工作都可以，顾问帮你看准证。', consult('新加坡工作签证'))}'''

# ---------------- 职位查询 ----------------
# 职位行：和 src/app.js 的 row() 输出一致。前 20 个直接写进 HTML（JS 加载后会重新渲染）
IND_PIC = {'餐饮': 'job-chef', '酒店': 'job-hotel', '建筑': 'job-build', '司机': 'job-driver', '美业': 'job-salon', '工厂': 'job-factory'}


def job_row(j):
    from html import escape
    from urllib.parse import quote
    e = lambda x: escape(str(x), quote=True).replace('&#x27;', "'")
    pic = '/img/' + next((v for k, v in IND_PIC.items() if j['ind'].startswith(k)), 'sg-bay') + '-s.jpg'
    meta = []
    if j['p']: meta.append(f'<span class="pp">{e(" · ".join(j["p"]))}</span>')
    if j['nt']: meta.append(f'<span>限{e("/".join(j["nt"]))}籍</span>')
    if j['rg'] != '未注明': meta.append(f'<span>{e(j["rg"])}</span>')
    if j['hs']: meta.append('<span class="perk">包住</span>')
    if j['al']: meta.append('<span class="perk">住补</span>')
    dl = ''.join(f'<div><dt>{k}</dt><dd>{e(v)}</dd></div>' for k, v in [('薪资', j['pay']), ('工时与休息', j['h']), ('地点 / 编号', j['loc']),
                 ('地区', j['rg']), ('发布日期', j['d']), ('职位编号', j['id'])] if v)
    msg = f"【咨询职位 {j['id']}】{j['t']}" + (f"（{j['co']}）" if j['co'] else '') + f"，{j['pay'] or ''}。"
    link = '/contact?service=' + quote('新加坡工作签证', safe="-_.!~*'()") + '&msg=' + quote(msg, safe="-_.!~*'()")
    pay = f'S${round(j["b"]):,}<small>底薪起 / 月</small>' if j['b'] else '<small>薪资面议</small>'
    return (f'<details class="job"><summary><span class="th"><span class="ph"><img src="{pic}" alt="" loading="lazy" decoding="async"></span></span>'
            f'<span class="jt">{e(j["t"])}<small>{e(j["co"] or j["ind"])}</small><span class="jm">{"".join(meta)}</span></span>'
            f'<span class="jb">{pay}</span></summary><div class="job-body"><dl>{dl}</dl>' + (f'<pre>{e(j["raw"])}</pre>' if j['raw'] else '') +
            f'<div class="acts"><a class="btn green sm" href="{e(link)}">咨询这个职位</a><span>顾问帮你核实岗位并安排面试</span></div></div></details>')


jobs_body = f'''{banner('sg-bay', '新加坡职位', '新加坡职位查询', '真实在招岗位，看中了直接让顾问帮你对接。', [],
               f'<div class="chips"><span>共 <b data-jobs-count>{N_JOBS}</b> 个岗位</span><span id="jupd">更新于 {JOBS_UPDATED}</span></div>')}

<section class="sec"><div class="wrap">
  <div class="jobs-bar" role="search">
    <label class="q" for="jq">搜索<input id="jq" type="search" placeholder="岗位、公司或关键词，如：厨师、司机、包住"></label>
    <label for="jind">行业<select id="jind"><option value="">全部行业</option></select></label>
    <label for="jpass">准证<select id="jpass"><option value="">全部准证</option></select></label>
    <label for="jnt">国籍<select id="jnt"><option value="">不限国籍</option></select></label>
    <label for="jrg">地区<select id="jrg"><option value="">全部地区</option></select></label>
    <label for="jmin">底薪不低于<select id="jmin"><option value="0">不限</option><option value="1500">S$1,500</option><option value="2000">S$2,000</option><option value="2500">S$2,500</option><option value="3000">S$3,000</option><option value="3500">S$3,500</option></select></label>
  </div>
  <div class="cats" id="jcats" role="group" aria-label="按行业"></div>
  <div class="jobs-sub">
    <span class="count" aria-live="polite">找到 <b id="jcount">{N_JOBS}</b> 个职位</span>
    <label class="tick" for="jhs"><input type="checkbox" id="jhs">包住</label>
    <label class="tick" for="jal"><input type="checkbox" id="jal">有住房补贴</label>
    <span class="sortby" role="group" aria-label="排序">
      <button type="button" data-sort="new" aria-pressed="true">最新发布</button>
      <button type="button" data-sort="pay" aria-pressed="false">底薪最高</button>
    </span>
  </div>
  <div class="job-list" id="jlist">{''.join(job_row(j) for j in JOBS[:20])}</div>
  <div class="jobs-more"><button type="button" class="btn line" id="jmore" hidden>显示更多职位</button></div>
  <div class="jobs-legend">
    <span><b>WP</b>工作准证</span><span><b>SP</b>S Pass</span><span><b>EP</b>就业准证</span><span><b>NTS</b>非传统来源国</span><span><b>BCA</b>需建筑局技能认证</span>
  </div>
</div></section>

{cta('sg-mbs', '没找到合适的？', '告诉顾问你的工种和期望薪资，有新岗位第一时间通知你。', consult('新加坡工作签证'), '让顾问帮我找')}'''

# ---------------- 墨西哥 ----------------
MX_STEPS = [
    ('file-check', '申请批文', '墨西哥当地合法雇主向移民局递交申请', ['协助准备申请材料', '获得移民局工签批文', '批文同步至中国对应领事馆']),
    ('stamp', '领馆面签', '前往墨西哥驻华使领馆（北京 / 上海 / 广州）', ['参加官方面谈', '获批后获得入境签证', '签证有效期 180 天']),
    ('id-card', '入境换卡', '持签证入境墨西哥', ['协助预约移民局', '完成指纹录入', '领取临时居留卡，约 30 天']),
]
MX_PLAN = [
    ('id-card', '第一年', '1 年期临时居留'),
    ('rotate-ccw', '第二阶段', '续签 3 年期临时居留'),
    ('house', '第三阶段', '满 4 年申请永久居留（绿卡）'),
    ('flag', '第四阶段', '永居满 1 年，可申请墨西哥国籍'),
]
MX_PAY = [('签约后', 'pen-line'), ('获得工签批文后', 'file-check'), ('获得签证批准后', 'stamp'), ('入境领取居留卡前', 'id-card')]
MX_PERKS = [('shield-check', '合法合规办理'), ('languages', '全程中文服务'), ('user-check', '一对一顾问跟进'), ('calendar-check', '协助预约和备材料'),
            ('plane-takeoff', '协助入境换卡'), ('rotate-ccw', '可续签直至永居'), ('globe', '永居后无最低居住要求')]

mx_body = f'''{banner('mx-gto', '墨西哥工签绿卡', '墨西哥合法居留项目', '雇主工签起步，1 年临时居留 → 3 年续签 → 永久居留 → 入籍，全程协助办理。', ['全程中文', '一对一顾问', '可续签至永居'],
              f'<div class="acts">{btn(consult("墨西哥工签绿卡"), "免费评估", "sun", "messages-square")}{btn("#to-us", "转美签路线", "glass", "plane-takeoff")}{btn("#fee", "看费用", "glass", "wallet")}</div>')}

{mx_to_us('sec tint mxus', link=False)}

<section class="sec"><div class="wrap">
  {head('办理流程', '三步拿到墨西哥居留卡')}
  <div class="flow">
  {''.join(f"""<div class="flow-card"><div class="flow-top"><span class="ic">{ic(i)}</span><span class="no">第 {n + 1} 步</span></div><h3>{t}</h3><p>{d}</p>{ticks(items)}</div>""" for n, (i, t, d, items) in enumerate(MX_STEPS))}
  </div>
</div></section>

<section class="sec tint"><div class="wrap">
  {head('身份规划', '从临时居留到墨西哥国籍')}
  <div class="road four">
  {''.join(f'<div><span class="ic">{ic(i)}</span><b>{t}</b><span>{d}</span></div>' for i, t, d in MX_PLAN)}
  </div>
  <div class="chips center"><span>可长期合法居住</span><span>自由出入墨西哥</span><span>无最低居住时间限制</span><span>无强制长期居住要求</span></div>
  <p class="fine center">入籍以墨西哥政府现行法律及审批结果为准。</p>
</div></section>

<section class="sec" id="fee"><div class="wrap">
  {head('服务费用', '一口价，分 4 次付')}
  <div class="fee">
    <div class="fee-total"><span>项目总费用</span><b>¥160,000</b><small>人民币，按进度分 4 期支付</small></div>
    <ol class="fee-steps">
    {''.join(f'<li><span class="ic">{ic(i)}</span><span class="when">第 {n + 1} 期 · {w}</span><b>¥40,000</b></li>' for n, (w, i) in enumerate(MX_PAY))}
    </ol>
  </div>
</div></section>

<section class="sec alt"><div class="wrap">
  {head('项目优势', '为什么选这个项目')}
  <div class="perks">{''.join(f'<div><span class="ic">{ic(i)}</span><b>{t}</b></div>' for i, t in MX_PERKS)}</div>
</div></section>

<section class="sec tint"><div class="wrap">
  {head('适合谁', '这些人都在去墨西哥')}
  {icards([
      ('factory', '外派管理技术', '派驻墨西哥工厂的管理和技术人员。'),
      ('ship', '贸易电商老板', '在墨西哥做贸易、电商、开公司。'),
      ('users', '想要北美身份的家庭', '需要长期稳定居住身份。'),
  ])}
  <p class="note-box">{ic('info')}<span>风险提示：申请人须提供真实、完整、合法的申请材料。项目审批权归墨西哥移民局及相关领事机构所有，最终结果以官方审核为准。</span></p>
</div></section>

{cta('mx-angel', '想去墨西哥？先免费评估', '说说你的情况，顾问帮你看能不能办、多久能办好。', consult('墨西哥工签绿卡'))}'''

# ---------------- 关于 ----------------
FAQ = [
    ('免费评估要准备什么？', '准备好学历、工作经历、目前的签证或出境记录，以及大概预算和时间就行，不用提前准备正式材料。'),
    ('美国签证被拒过，还能再申请吗？', '可以。214(b) 拒签不是永久的，关键是找到上次被拒的原因，情况有实际变化后再申请。我们会先帮你复盘。'),
    ('你们能帮忙找新西兰或新加坡的工作吗？', '能对接合作雇主、优化简历、辅导面试，但最终录用由雇主决定。我们不向求职者出售工作机会。'),
    ('墨西哥身份对去美国有帮助吗？', '墨西哥居留不等于美国签证，更适合在北美做生意、需要长期居住身份的人。目标是美国的话，我们会把两条路一起比较。'),
    ('费用怎么收？', '按项目报价，分阶段付。政府费用实报实销，服务费签约时写明。评估不收费。'),
]
about_body = f'''{banner('meeting', '关于我们', '关于羊驼出海', '羊驼走山路不着急，每一步都踩稳了再走。我们也这样陪你出海。')}

<section class="sec"><div class="wrap">
  {split('meeting2', '顾问和客户沟通', '我们是谁', '不忽悠，不画饼，一步一步办踏实', '专注美国、新西兰、新加坡、墨西哥四国身份规划。一份材料写偏了，可能就是一次拒签、几个月等待，所以我们宁可在评估时把风险讲在前面。',
         ['四个国家，熟悉各自的审理思路', '清楚哪些承诺不能做', '从评估到获批，同一个顾问负责'])}
</div></section>

<section class="sec tint"><div class="wrap">
  {head('我们的承诺', '五件事，说到做到')}
  {icards([
      ('wallet', '收费透明', '政府费、第三方费、服务费分开写，没有隐藏收费。'),
      ('user-check', '一对一顾问', '同一个顾问从头跟到尾。'),
      ('shield-check', '不做获批承诺', '结果由各国移民机构决定，我们承诺材料和服务质量。'),
      ('scale', '持牌合作', '法律文书由当地持牌律师或注册移民顾问签署。'),
      ('lock', '资料保密', '签保密协议，资料只用于本次申请。'),
  ])}
</div></section>

<section class="sec" id="faq"><div class="wrap faq-wrap">
  {head('常见问题', '大家常问')}
  {''.join(f'<details class="qa"><summary>{q}</summary><p>{a}</p></details>' for q, a in FAQ)}
</div></section>

{cta()}'''

# ---------------- 咨询 ----------------
contact_body = f'''{banner('airport2', '免费咨询', '免费咨询', '留个联系方式，顾问 1 个工作日内找你。咨询不收费，资料不外传。')}

<section class="sec"><div class="wrap contact-grid">
  <aside class="next">
    {img('meeting', '顾问正在和客户沟通')}
    <div class="body">
      <h3>提交后会发生什么</h3>
      <ol>
        <li><span class="ic">{ic('phone-call')}</span><div><b>顾问联系你</b><span>1 个工作日内，周一至周六 9:00–19:00</span></div></li>
        <li><span class="ic">{ic('messages-square')}</span><div><b>免费评估</b><span>聊 20 分钟，看你适合哪条路</span></div></li>
        <li><span class="ic">{ic('list-checks')}</span><div><b>给你方案</b><span>路径、时间、费用一次讲清</span></div></li>
      </ol>
    </div>
  </aside>
  <form class="lead" id="lead" novalidate>
    <h2>说说你的情况</h2>
    <div class="fgrid">
      <label class="f" for="f-name">称呼<input id="f-name" name="name" autocomplete="name" placeholder="例如：王先生" required></label>
      <label class="f" for="f-contact">手机或微信号<input id="f-contact" name="contact" placeholder="方便顾问联系你" required></label>
    </div>
    <div class="fgrid">
      <label class="f" for="f-service">感兴趣的服务
        <select id="f-service" name="service">
          <option>美国移民签证</option><option>新西兰工作签证</option><option>新加坡工作签证</option><option>墨西哥工签绿卡</option><option>还不确定，想听建议</option>
        </select>
      </label>
      <label class="f" for="f-when">计划出发时间
        <select id="f-when" name="when"><option>3 个月内</option><option selected>半年内</option><option>1 年内</option><option>先了解，时间不定</option></select>
      </label>
    </div>
    <label class="f" for="f-msg">简单介绍一下<textarea id="f-msg" name="msg" placeholder="例如：厨师 8 年，想去新加坡工作，想知道能办什么准证。"></textarea></label>
    <label class="hp" aria-hidden="true">请勿填写<input id="f-site" name="website" tabindex="-1" autocomplete="off"></label>
    <p class="err" id="f-err" hidden>请填写称呼和联系方式，顾问才能联系到你。</p>
    <button class="btn green" type="submit" style="justify-self:start">{ic('send')}提交预约</button>
    <p class="fine">提交即表示你同意我们为联系你而使用以上信息，资料不会提供给第三方。</p>
    <div class="ok" id="f-ok" hidden><b>已收到你的预约</b><span id="f-ok-txt"></span></div>
  </form>
</div></section>'''

# (文件名, 路径, 标题, 描述, 正文, 脚本, 关键词, 分享图, 结构化数据)
FAQ_LD = {'@context': 'https://schema.org', '@type': 'FAQPage', 'mainEntity': [
    {'@type': 'Question', 'name': q, 'acceptedAnswer': {'@type': 'Answer', 'text': a}} for q, a in FAQ]}
PAGES = [
    ('index', '/', '羊驼出海 LLAMA VISA｜美国签证移民·新西兰工签·新加坡工签·墨西哥绿卡',
     f'羊驼出海（LLAMA VISA）出国签证与移民服务：美国旅游、留学、工作签证与绿卡，新西兰工作签证，新加坡 EP、S Pass、WP 工作准证和 {N_JOBS} 个在招职位，墨西哥工签与永久居留。要出国找羊驼，免费评估。',
     index_body, ('jobs-data.js', 'app.js'),
     '羊驼出海,LLAMA VISA,出国签证,移民中介,出国工作,美国签证,美国移民,新西兰工签,新加坡工签,新加坡工作,墨西哥绿卡,墨西哥签美国', 'alpaca-sg', ()),
    ('us', '/us', '美国签证与移民｜B1/B2、F-1、H-1B、NIW、EB-5 绿卡办理',
     '美国旅游签证 B1/B2、留学 F-1、工作签证 H-1B、L-1、O-1，以及 EB-1A、NIW、EB-5 绿卡规划。拒签复盘、材料准备、面签辅导，也可先拿墨西哥身份再申请美签。',
     us_body, ('app.js',),
     '美国签证,美国移民,美签,美国旅游签证,B1/B2,F-1留学签证,H-1B,L-1,O-1,EB-1A,NIW,EB-5,美国绿卡,美签拒签,墨西哥签美国', 'us-gg',
     (service_ld('美国签证与移民', '美国旅游、留学、工作签证与 EB-1A、NIW、EB-5 绿卡规划。', '美国', ['美国签证', '美国移民', '美国绿卡']),)),
    ('nz', '/nz', '新西兰工作签证｜AEWV 认证雇主工签、新西兰工作项目',
     '新西兰工作签证 AEWV 办理：中专以上学历、2 年以上工作经验、PTE 29 分即可报名，多行业岗位匹配，持牌移民律师服务，做满条件可衔接新西兰居留。',
     nz_body, ('app.js',),
     '新西兰工签,新西兰工作签证,AEWV,新西兰工作,新西兰打工,新西兰移民,新西兰绿名单,新西兰技术移民', 'nz-lake',
     (service_ld('新西兰工作签证', '新西兰认证雇主工作签证 AEWV 与多行业岗位匹配。', '新西兰', ['新西兰工作签证', 'AEWV']),)),
    ('sg', '/sg', '新加坡工作签证｜EP、S Pass、WP 准证办理与 EP 资格自测',
     f'新加坡工作准证办理：EP 就业准证、S Pass、Work Permit、ONE Pass、EntrePass、家属准证 DP。在线 EP 资格自测，{N_JOBS} 个新加坡在招岗位随时查。',
     sg_body, ('jobs-data.js', 'app.js'),
     '新加坡工签,新加坡工作签证,新加坡EP,新加坡S Pass,新加坡WP,新加坡工作准证,新加坡打工,新加坡劳务,新加坡就业准证,COMPASS', 'sg-merlion',
     (service_ld('新加坡工作签证', '新加坡 EP、S Pass、Work Permit 等工作准证申请协助与岗位对接。', '新加坡', ['新加坡工作签证', 'EP', 'S Pass', 'Work Permit']),)),
    ('jobs', '/jobs', f'新加坡招聘｜{N_JOBS} 个在招岗位：厨师、服务员、建筑、司机、工厂',
     f'新加坡最新招聘 {N_JOBS} 个岗位，{JOBS_UPDATED} 更新：餐饮厨师和服务员、酒店、建筑、司机、美容美发、工厂，标明 WP、S Pass、EP 准证、底薪、包住和住房补贴，可按国籍筛选。',
     jobs_body, ('jobs-data.js', 'app.js'),
     '新加坡招聘,新加坡工作,新加坡找工作,新加坡厨师,新加坡服务员,新加坡建筑工,新加坡司机,新加坡工厂,新加坡包吃住,新加坡劳务', 'sg-bay', ()),
    ('mx', '/mx', '墨西哥工签绿卡｜墨西哥工作居留、永久居留、墨西哥签美国',
     '墨西哥雇主工签起步：1 年临时居留、3 年续签、永久居留到入籍，全程中文协助。持墨西哥居留卡住满 5–6 个月，可在墨西哥当地申请美国签证。',
     mx_body, ('app.js',),
     '墨西哥工签,墨西哥绿卡,墨西哥移民,墨西哥工作签证,墨西哥临时居留,墨西哥永久居留,墨西哥居留卡,墨西哥签美国,墨西哥美签', 'mx-gto',
     (service_ld('墨西哥工签绿卡', '墨西哥工作临时居留、续签、永久居留办理，以及持墨西哥居留身份申请美签的规划。', '墨西哥', ['墨西哥工作签证', '墨西哥永久居留']),)),
    ('about', '/about', '关于我们｜出国签证与移民顾问',
     '羊驼出海专注美国、新西兰、新加坡、墨西哥四国签证与身份规划，先评估风险再办理，不忽悠不画饼。常见问题：免费评估准备什么、美签被拒还能不能再申请等。',
     about_body, ('app.js',), '羊驼出海,LLAMA VISA,签证中介,移民顾问,出国咨询,美签拒签', 'meeting', (FAQ_LD,)),
    ('contact', '/contact', '免费咨询｜预约出国签证移民评估',
     '留下称呼和联系方式，羊驼出海顾问 1 个工作日内联系你，免费评估美国、新西兰、新加坡、墨西哥签证与工作机会。咨询不收费，资料不外传。',
     contact_body, ('app.js',), '出国咨询,签证咨询,移民咨询,免费评估,羊驼出海', 'airport2', ()),
]

if os.path.isdir(OUT):
    shutil.rmtree(OUT)
os.makedirs(OUT)
for name, slug, title, desc, body, scripts, kw, pic, ld in PAGES:
    with open(os.path.join(OUT, name + '.html'), 'w') as f:
        f.write(page(slug, title, desc, body, scripts, kw, pic, ld))
# 搜索引擎：站点地图和 robots
urls = ''.join(f'<url><loc>{SITE}{slug}</loc><lastmod>{JOBS_UPDATED if slug in ("/jobs", "/sg") else BUILD_DATE}</lastmod>'
               f'<changefreq>{"daily" if slug == "/jobs" else "weekly"}</changefreq><priority>{"1.0" if slug == "/" else "0.8"}</priority></url>\n'
               for _, slug, *_ in PAGES)
open(os.path.join(OUT, 'sitemap.xml'), 'w').write(f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{urls}</urlset>\n')
open(os.path.join(OUT, 'robots.txt'), 'w').write(f'User-agent: *\nAllow: /\nDisallow: /api/\n\nSitemap: {SITE}/sitemap.xml\n')
for src, dst in [('src/styles.css', 'styles.css'), ('src/app.js', 'app.js'), ('src/jobs-data.js', 'jobs-data.js'), ('logo.svg', 'logo.svg'), ('src/brand/logo.png', 'logo.png'), ('src/brand/favicon.png', 'favicon.png'), ('src/brand/favicon.ico', 'favicon.ico'), ('src/brand/apple-touch-icon.png', 'apple-touch-icon.png')]:
    shutil.copy(os.path.join(ROOT, src), os.path.join(OUT, dst))
shutil.copytree(os.path.join(ROOT, 'src/img'), os.path.join(OUT, 'img'))  # 自有图片（Unsplash 图在 Vercel 构建时另外下载）
json.dump(icons, open(ICON_CACHE, 'w'), ensure_ascii=False, indent=0, sort_keys=True)
print('built', len(PAGES), 'pages,', len(icons), 'icons')
