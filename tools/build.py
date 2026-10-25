# 生成多页面站点到 site/：共用页眉页脚，图标在生成时内联为 SVG（不依赖 CDN）。
# 用法：python3 tools/build.py [lucide-static 的 icons 目录]
# 图标会缓存到 tools/icons.json，之后没有 lucide 目录也能重新生成。
import json, os, re, shutil, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'site')
ICON_CACHE = os.path.join(ROOT, 'tools', 'icons.json')
ICON_DIR = sys.argv[1] if len(sys.argv) > 1 else None
icons = json.load(open(ICON_CACHE)) if os.path.exists(ICON_CACHE) else {}


def ic(name):
    if name not in icons:
        src = open(os.path.join(ICON_DIR, name + '.svg')).read()
        icons[name] = re.sub(r'\s+', ' ', ''.join(re.findall(r'<(?:path|circle|rect|line|polyline|polygon|ellipse)[^>]*/>', src)))
    return ('<svg class="ico" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
            'stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">' + icons[name] + '</svg>')


def img(name, alt='', big=False, eager=False):
    """图片放在 .ph 里：加载前/失败时显示渐变底色。"""
    attrs = 'loading="eager" fetchpriority="high"' if eager else 'loading="lazy"'
    if big:
        src = f'src="/img/{name}.jpg" srcset="/img/{name}-s.jpg 800w, /img/{name}.jpg 1800w" sizes="100vw"'
    else:
        src = f'src="/img/{name}-s.jpg"'
    return f'<div class="ph"><img {src} alt="{alt}" {attrs} decoding="async" onerror="this.remove()"></div>'


TOP = [('/us', '美国'), ('/nz', '新西兰'), ('/sg', '新加坡'), ('/mx', '墨西哥')]  # 顶部菜单只放四个国家
NAV = [('/', '首页'), ('/us', '美国移民签证'), ('/nz', '新西兰工签'), ('/sg', '新加坡工签'),
       ('/jobs', '新加坡职位'), ('/mx', '墨西哥工签绿卡'), ('/about', '关于我们')]


def page(slug, title, desc, body, scripts=('app.js',)):
    here = '/sg' if slug == '/jobs' else slug  # 职位查询归在新加坡下
    nav = ''.join(f'<a href="{h}"{" class=\"on\" aria-current=\"page\"" if h == here else ""}>{t}</a>' for h, t in TOP)
    js = ''.join(f'<script src="/{s}"></script>' for s in scripts)
    full_title = '羊驼出海 · 要出国找羊驼' if slug == '/' else f'{title} · 羊驼出海'
    return f'''<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{full_title}</title>
<meta name="description" content="{desc}">
<meta name="lead-endpoint" content="/api/lead">
<meta name="theme-color" content="#11866a">
<link rel="icon" href="/logo.svg" type="image/svg+xml">
<link rel="stylesheet" href="/styles.css">
</head>
<body>
<header class="top">
  <div class="wrap">
    <a class="brand" href="/" aria-label="羊驼出海首页"><img src="/logo.svg" alt="" width="34" height="42"><span><b>羊驼出海</b><small>Alpaca Overseas</small></span></a>
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
        <a class="brand" href="/"><img src="/logo.svg" alt="" width="34" height="42"><span><b>羊驼出海</b><small>Alpaca Overseas</small></span></a>
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
SLIDES = [
    ('hero-alpaca', '羊驼出海 · Alpaca Overseas', '要出国<em>找羊驼</em>', '美国、新西兰、新加坡、墨西哥。签证、工作、身份，一站帮你办好。',
     btn('/contact', '免费咨询', 'sun', 'messages-square') + btn('#services', '看看能去哪', 'glass')),
    ('us-nyc', '美国移民签证', '去美国，<em>签证绿卡</em>一起规划', '旅游、留学、H-1B、NIW、EB-5，先评估，再挑最稳的那条路。',
     btn('/us', '了解美国', 'sun') + btn(consult('美国移民签证'), '问问顾问', 'glass', 'messages-square')),
    ('nz-lake', '新西兰工作签证', '在新西兰<em>边工作边生活</em>', '认证雇主工签 AEWV，做满条件衔接居留。',
     btn('/nz', '了解新西兰', 'sun') + btn(consult('新西兰工作签证'), '问问顾问', 'glass', 'messages-square')),
    ('sg-mbs', '新加坡工作签证', '<em data-jobs-count>243</em> 个新加坡岗位在招', '餐饮、酒店、建筑、司机、工厂，按国籍和底薪一键筛。',
     btn('/jobs', '马上查职位', 'sun', 'search') + btn('/sg#check', 'EP 资格自测', 'glass', 'calculator')),
    ('mx-city', '墨西哥工签绿卡', '墨西哥，<em>北美</em>新机会', '工作居留满 4 年转永居，出海建厂的热门地。',
     btn('/mx', '了解墨西哥', 'sun') + btn(consult('墨西哥工签绿卡'), '问问顾问', 'glass', 'messages-square')),
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
    ('/mx', 'mx-street', '墨西哥', '墨西哥工签绿卡', ['工作居留', '永久居留']),
]

index_body = f'''{carousel()}

<section class="sec stats-sec"><div class="wrap"><div class="stats">
  <div class="stat"><span class="ic">{ic('briefcase')}</span><div><b data-jobs-count>243</b><span>新加坡在招岗位</span></div></div>
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
              f'<div class="acts">{btn(consult("美国移民签证"), "免费评估", "sun", "messages-square")}</div>')}

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
nz_body = f'''{banner('nz-lake', '新西兰工作签证', '新西兰工作签证', '先拿认证雇主 offer，再办工签；做满条件，衔接居留。', ['AEWV', '绿名单', '技术移民 SMC', '打工度假'],
              f'<div class="acts">{btn(consult("新西兰工作签证"), "免费评估", "sun", "messages-square")}</div>')}

<section class="sec"><div class="wrap">
  {head('签证类别', '四种方式去新西兰')}
  {vtypes([
      ('briefcase', 'AEWV', '认证雇主工签', '主流工签。雇主先认证、做岗位核查。'),
      ('leaf', '绿名单', 'Green List', '医护、工程、IT、建筑等紧缺职业，可直通或 2 年后申居留。'),
      ('id-card', 'SMC', '技术移民', '在新西兰工作，学历或收入达标，积分评估。'),
      ('tent-tree', 'WHV', '打工度假', '18–30 岁，名额有限，边玩边打工。'),
  ])}
</div></section>

<section class="sec alt"><div class="wrap">
  {head('热门岗位方向', '这些工种好找工作')}
  {icards([
      ('chef-hat', '厨师', '中餐、西餐厨师长期缺人。'),
      ('wrench', '技术工种', '汽修、电工、焊工、水管工。'),
      ('stethoscope', '护理养老', '护士、护工、养老护理。'),
      ('code', 'IT 与工程', '软件开发、各类工程师。'),
  ])}
</div></section>

<section class="sec"><div class="wrap">
  {split('nz-town', '新西兰小镇街景', '服务包含', '从找雇主到落地', '',
         ['岗位匹配，对接认证雇主', '英文简历、面试辅导', '学历认证（NZQA）、体检、无犯罪证明', '递签、补件跟进，配偶子女随行规划'],
         btn(consult('新西兰工作签证'), '咨询新西兰工签'), rev=True)}
  <p class="note-box">{ic('shield-check')}<span>我们不向求职者收“买工作”的钱。新西兰移民局明确规定，雇主不得向员工收招聘费。</span></p>
</div></section>

{cta('nz-hills', '想去新西兰？先免费评估', '说说你的工种和英语水平，顾问帮你看机会。', consult('新西兰工作签证'))}'''

# ---------------- 新加坡 ----------------
sg_check = open(os.path.join(ROOT, 'tools', 'sg-check.html')).read()
sg_body = f'''{banner('sg-mbs', '新加坡工作签证', '新加坡工作签证', '离家近、说中文、税率低。准证由雇主申请，我们帮你把申请做对。', ['EP', 'S Pass', 'Work Permit', 'ONE Pass', 'EntrePass', 'DP'],
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
  {split('sg-bay', '新加坡滨海湾', '在线查职位', '<span data-jobs-count>243</span> 个新加坡岗位，随时查', '餐饮、酒店、建筑、司机、美业、工厂，按国籍、准证、底薪、包住筛选。',
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

{cta('sg-mbs', '想去新加坡？先免费评估', '有 offer 或想找工作都可以，顾问帮你看准证。', consult('新加坡工作签证'))}'''

# ---------------- 职位查询 ----------------
jobs_body = f'''{banner('sg-bay', '新加坡职位', '新加坡职位查询', '真实在招岗位，看中了直接让顾问帮你对接。', [],
               '<div class="chips"><span>共 <b data-jobs-count>243</b> 个岗位</span><span id="jupd"></span></div>')}

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
    <span class="count" aria-live="polite">找到 <b id="jcount">0</b> 个职位</span>
    <label class="tick" for="jhs"><input type="checkbox" id="jhs">包住</label>
    <label class="tick" for="jal"><input type="checkbox" id="jal">有住房补贴</label>
    <span class="sortby" role="group" aria-label="排序">
      <button type="button" data-sort="new" aria-pressed="true">最新发布</button>
      <button type="button" data-sort="pay" aria-pressed="false">底薪最高</button>
    </span>
  </div>
  <div class="job-list" id="jlist"></div>
  <div class="jobs-more"><button type="button" class="btn line" id="jmore" hidden>显示更多职位</button></div>
  <div class="jobs-legend">
    <span><b>WP</b>工作准证</span><span><b>SP</b>S Pass</span><span><b>EP</b>就业准证</span><span><b>NTS</b>非传统来源国</span><span><b>BCA</b>需建筑局技能认证</span>
  </div>
</div></section>

{cta('sg-mbs', '没找到合适的？', '告诉顾问你的工种和期望薪资，有新岗位第一时间通知你。', consult('新加坡工作签证'), '让顾问帮我找')}'''

# ---------------- 墨西哥 ----------------
mx_body = f'''{banner('mx-street', '墨西哥工签绿卡', '墨西哥工签绿卡', '紧邻美国，门槛友好。工作居留满 4 年，转墨西哥“绿卡”。', ['临时居留', '永久居留', 'CURP', 'RFC'],
              f'<div class="acts">{btn(consult("墨西哥工签绿卡"), "免费评估", "sun", "messages-square")}</div>')}

<section class="sec"><div class="wrap">
  {head('拿身份的路线', '三步拿到墨西哥绿卡')}
  <div class="road">
    <div><span class="ic">{ic('stamp')}</span><b>办签证</b><span>雇主邀请或经济能力证明，在驻华使领馆办签证</span></div>
    <div><span class="ic">{ic('id-card')}</span><b>临时居留卡</b><span>入境 30 天内换卡，合法居住和工作</span></div>
    <div><span class="ic">{ic('house')}</span><b>永久居留</b><span>临时居留满 4 年转永居，不用再续签</span></div>
  </div>
</div></section>

<section class="sec alt"><div class="wrap">
  {head('身份类别', '适合你的是哪种')}
  {vtypes([
      ('briefcase', '工作临时居留', '雇主邀请', '墨西哥雇主向移民局（INM）提交工作邀请。'),
      ('wallet', '经济能力临时居留', '存款 / 收入', '不需要雇主，用存款或稳定收入证明申请。'),
      ('house', '永久居留', '绿卡', '临时居留满 4 年转换，或高收入、高资产直接申请。'),
      ('receipt', '落地配套', 'CURP · RFC', '身份编码和税号，开户、签约、开公司都要用。'),
  ])}
</div></section>

<section class="sec"><div class="wrap">
  {split('mx-dome', '墨西哥城建筑', '服务包含', '签证、换卡、开公司，一条龙', '',
         ['判断走雇主邀请还是经济能力路线', '使馆预约、材料翻译和公证认证', '入境换卡，办 CURP 和 RFC', '墨西哥公司注册、银行开户对接'],
         btn(consult('墨西哥工签绿卡'), '咨询墨西哥身份'))}
</div></section>

<section class="sec tint"><div class="wrap">
  {head('适合谁', '这些人都在去墨西哥')}
  {icards([
      ('factory', '外派管理技术', '派驻墨西哥工厂的管理和技术人员。'),
      ('ship', '贸易电商老板', '在墨西哥做贸易、电商、开公司。'),
      ('users', '想要北美身份的家庭', '需要长期稳定居住身份。'),
  ])}
  <p class="note-box">{ic('info')}<span>经济能力路线的存款和收入标准按墨西哥最低工资倍数计算，每年调整，以当年使领馆要求为准。</span></p>
</div></section>

{cta('mx-city', '想去墨西哥？先免费评估', '说说你是外派、开公司还是想要身份，顾问帮你选路线。', consult('墨西哥工签绿卡'))}'''

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
    <p class="err" id="f-err" hidden>请填写称呼和联系方式，顾问才能联系到你。</p>
    <button class="btn green" type="submit" style="justify-self:start">{ic('send')}提交预约</button>
    <p class="fine">提交即表示你同意我们为联系你而使用以上信息，资料不会提供给第三方。</p>
    <div class="ok" id="f-ok" hidden><b>已收到你的预约</b><span id="f-ok-txt"></span></div>
  </form>
</div></section>'''

PAGES = [
    ('index', '/', '首页', '羊驼出海：美国移民签证、新西兰工作签证、新加坡工作签证、墨西哥工签绿卡。要出国找羊驼。', index_body, ('jobs-data.js', 'app.js')),
    ('us', '/us', '美国移民签证', '美国旅游、留学、工作签证与 EB-1A、NIW、EB-5 绿卡规划。', us_body, ('app.js',)),
    ('nz', '/nz', '新西兰工作签证', '新西兰认证雇主工签 AEWV、绿名单、技术移民。', nz_body, ('app.js',)),
    ('sg', '/sg', '新加坡工作签证', '新加坡 EP、S Pass、Work Permit 申请与 EP 资格自测。', sg_body, ('jobs-data.js', 'app.js')),
    ('jobs', '/jobs', '新加坡职位查询', '新加坡在招岗位查询：餐饮、酒店、建筑、司机、美业、工厂。', jobs_body, ('jobs-data.js', 'app.js')),
    ('mx', '/mx', '墨西哥工签绿卡', '墨西哥工作临时居留、经济能力居留、永久居留。', mx_body, ('app.js',)),
    ('about', '/about', '关于我们', '关于羊驼出海与常见问题。', about_body, ('app.js',)),
    ('contact', '/contact', '免费咨询', '预约羊驼出海顾问免费评估。', contact_body, ('app.js',)),
]

if os.path.isdir(OUT):
    shutil.rmtree(OUT)
os.makedirs(OUT)
for name, slug, title, desc, body, scripts in PAGES:
    with open(os.path.join(OUT, name + '.html'), 'w') as f:
        f.write(page(slug, title, desc, body, scripts))
for src, dst in [('src/styles.css', 'styles.css'), ('src/app.js', 'app.js'), ('src/jobs-data.js', 'jobs-data.js'), ('logo.svg', 'logo.svg')]:
    shutil.copy(os.path.join(ROOT, src), os.path.join(OUT, dst))
json.dump(icons, open(ICON_CACHE, 'w'), ensure_ascii=False, indent=0, sort_keys=True)
print('built', len(PAGES), 'pages,', len(icons), 'icons')
