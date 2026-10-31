# 把从微信群复制的新加坡招工信息追加到 src/jobs-data.js，并清理不该公开的内容。
# 用法：python3 tools/add_jobs.py 粘贴文本.txt
# 粘贴格式：日期分隔行「—————  2026-10-22  —————」，每条以「xxx(一手单)  11:34 PM」开头。
# 与已有职位正文相似度高的视为重复，跳过。每次运行也会重新清理已有职位。
import difflib, json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, 'src', 'jobs-data.js')
PREFIX = 'window.__JOBS = '

# ---------- 清理：中介内部信息、地域/外貌歧视 ----------
DROP_LINE = [
    re.compile(r'^\d{2}[A-Z]\d{4,5}$'),           # 中介执照/人员编号，如 94S0267
    re.compile(r'^费用\s*[$＄\d]'),                # 给同行的费用，如 费用$3500、费用1.3
    re.compile(r'^(收费|特价单)[：:]?\s*(中国)?\s*[\d.]+$'),  # 同上，如 收费1.5、收费：中国 1.0、特价单1.2
    re.compile(r'^美业订单[：:]'),
    re.compile(r'^([一-龥]{2,3}\s*)+不要$'),          # 地域歧视，如 河南 东北不要
]
DROP_PHRASE = [
    re.compile(r'[，,。 ]*合作价[：:][^，。\n]*'),
    re.compile(r'[（(]合作价[^）)]*[）)]'),
    re.compile(r'[，,\- ]*(代理|低)?收费\s*[：:]?\s*(\d(\.\d)?(?!\d)|\d+元)'),
    re.compile(r'特价\s*\d\.\d'),
    re.compile(r'[，,；; ]*优先[南北]方求职者'),
    re.compile(r'[，,；; ]*[一-龥]{2,4}的暂时不要'),
    re.compile(r'^低收费[,，]'),
    re.compile(r'[，,；;。 ]*(形象具备亲和力，符合高端美妆品牌的专柜形象|形象一定要好|形象气质好|形象较好|形象佳|形象端庄|长相漂亮|[南北]方人|体重\s*\d+-\d+kg|身高\s*\d{3}(cm)?\s*以上)'),
    re.compile(r'[，,；; ]*(形象好|大方端正|五官端正|皮肤状态良好|长相有亲和力|未婚未育|身高\d{3}以上|要求[一-龥]{2,5}华人)'),
    re.compile(r'[，,。 ]*(老板)?不要[一-龥]{1,4}人(和[一-龥]{1,4}人)*'),
    re.compile(r'[，,。 ]*要[一-龥]{2,3}(省)?人(?=[ ，,。\n]|$)'),
    re.compile(r'[，,。 ]*不要(戴|带)眼镜[一-龥]{0,8}'),
    re.compile(r'\[[一-龥]{1,3}\]'),       # 微信表情 [勾引][得意]
    re.compile(r'\s*\d{2}S\d{3,5}(?![\dA-Za-z])'),  # 地址后面的中介编号，如 北部 98S210
]
KEEP_REQUIRE = re.compile(r'要(人在新|会|有|求(?![一-龥]{2,5}华人))')  # “要会华语”之类不是地域要求


def clean(text):
    lines = []
    for line in text.split('\n'):
        s = line.strip()
        if any(p.match(s) for p in DROP_LINE):
            continue
        for p in DROP_PHRASE:
            s = p.sub(lambda m: m.group(0) if KEEP_REQUIRE.search(m.group(0)) else '', s)
        s = re.sub(r'([：:])\s*[，,]\s*', r'\1', s).lstrip('•').strip()
        if s:
            lines.append(s)
    return '\n'.join(lines)


# ---------- 字段提取 ----------
def field(text, *keys):
    for k in keys:
        m = re.search(r'^[•\s]*' + k + r'\s*[：:｜|]\s*(.+)$', text, re.M)
        if m and m.group(1).strip():
            return m.group(1).strip()
    return ''


NATIONS = [('中国', '中国'), ('越南', '越南'), ('缅甸', '缅甸'), ('马来西亚', '马来西亚'), ('马籍', '马来西亚'),
           ('印度', '印度'), ('孟加拉', '孟加拉'), ('斯里兰卡', '斯里兰卡'), ('菲律宾', '菲律宾')]
REGIONS = [('全岛', '全岛'), ('东部', '东部'), ('樟宜', '东部'), ('阿裕尼', '东部'), ('马林台', '东部'), ('加基武吉', '东部'),
           ('淡滨尼', '东部'), ('勿洛', '东部'), ('巴耶利峇', '东部'), ('西部', '西部'), ('大士', '西部'), ('裕廊', '西部'),
           ('北部', '北部'), ('兀兰', '北部'), ('义顺', '北部'), ('中部', '中部 / 市区'), ('市中心', '中部 / 市区'),
           ('大巴窑', '中部 / 市区'), ('牛车水', '中部 / 市区'), ('圣淘沙', '南部 / 圣淘沙')]
INDUSTRY = [
    ('司机/物流', r'司机|货车|物流|仓库|配送'),
    ('美业/按摩/美发', r'美发|美甲|美容|按摩|足疗|发型|睫毛'),
    ('建筑/装修/维修', r'木工|泥瓦|装修|钢筋|木模|空调|汽修|汽车维修|钣金|安装|电工|焊|水管|油漆|BCA'),
    ('工厂/制造', r'工厂|厂|车工|包装|生产'),
    ('餐饮', r'厨|服务员|餐|帮厨|水饺|烧烤|面包|档口|香锅|奶茶|咖啡|杂饭'),
]


def first_amount(pay):
    for n in re.findall(r'\d[\d,]*', pay):
        v = int(n.replace(',', ''))
        if 800 <= v <= 9000:
            return v
    return None


def parse(block, date):
    raw = clean(block)
    if not raw:
        return None
    t = field(raw, '职位', '岗位/准证', '岗位')
    head = raw.split('\n')[0]
    if not t:
        m = re.search(r'【(.+?)】', raw)
        t = m.group(1) if m else head
    co = field(raw, '公司名称', '公司', '雇主')
    pay_full = field(raw, '薪水/住补', '薪水', '薪资待遇', '薪资')
    pay = pay_full if len(pay_full) <= 40 else pay_full[:40] + '…'
    h = ' '.join(x for x in [field(raw, '工作时间/月休', '工作时间', '时间', '工时'), field(raw, '月休息日')] if x)
    loc = field(raw, '工作地址', '地址', '工作地点', '地点', '备注', '面试')
    t = re.sub(r'^(更新|急招|急)\s*[|｜]\s*', '', t)
    scope = ' '.join([t, co] + [field(raw, k) for k in ('准证', '国籍/准证', '国籍', '岗位/准证')]).upper()
    passes = [p for p in ['WP', 'SP', 'NTS', 'EP', 'TEP'] if re.search(r'(?<![A-Z])' + p + r'(?![A-Z])', scope)]
    if 'BCA' in raw.upper() and not re.search(r'不(需要|要)\s*BCA', raw.upper()):
        passes.append('BCA')
    nt = []
    for k, v in NATIONS:
        if k in scope and v not in nt:
            nt.append(v)
    if re.search(r'任何国籍', raw):
        nt = []
    rg = next((v for k, v in REGIONS if k in loc + ' ' + t), '未注明')
    ind = next((name for name, pat in INDUSTRY if re.search(pat, t + ' ' + co)), '酒店/销售/办公/其他')
    return {'d': date, 'ind': ind, 't': t, 'co': co, 'pay': pay, 'b': first_amount(pay_full), 'h': h, 'loc': loc,
            'p': passes, 'rg': rg, 'hs': bool(re.search(r'包住|提供住宿', raw)), 'al': bool(re.search(r'住补|住房津贴|住房补', raw)),
            'n': 1, 'raw': raw, 'nt': nt}


def split_paste(text):
    date, buf, out = None, [], []
    def flush():
        if date and buf:
            out.append((date, '\n'.join(buf).strip()))
    for line in text.split('\n'):
        m = re.match(r'^[—\-\s]*(\d{4}-\d{2}-\d{2})[—\-\s]*$', line)
        if m:
            flush(); buf = []; date = m.group(1); continue
        if re.search(r'\(一手单\)\s+\d{1,2}:\d{2}\s*[AP]M\s*$', line):
            flush(); buf = []; continue
        buf.append(line)
    flush()
    return [(d, b) for d, b in out if b]


def sig(s):
    return re.sub(r'[^\w]', '', s)


jobs = json.loads(open(DATA).read()[len(PREFIX):].rstrip().rstrip(';'))
for j in jobs:
    j['raw'] = clean(j['raw'])
    for k in ('t', 'pay', 'loc'):
        j[k] = clean(j[k])

added, dup, reposted = [], [], []
if len(sys.argv) > 1:
    for date, block in split_paste(open(sys.argv[1]).read()):
        job = parse(block, date)
        if not job:
            continue
        s, st = sig(job['raw']), sig(job['t'])
        # 同一岗位再发（正文相近、标题相近）：更新为最新内容，发布次数 +1
        def close(o):
            r = difflib.SequenceMatcher(None, s, sig(o['raw'])).ratio()
            return r > 0.97 or (r > 0.75 and difflib.SequenceMatcher(None, st, sig(o['t'])).ratio() > 0.8)
        same = [o for o in jobs + added if close(o)]
        if same:
            o = max(same, key=lambda o: difflib.SequenceMatcher(None, s, sig(o['raw'])).ratio())
            if date > o['d']:
                for k in ('d', 'pay', 'b', 'h', 'loc', 'raw', 'hs', 'al'):
                    if job[k] or k in ('hs', 'al'):
                        o[k] = job[k]
                o['n'] = o.get('n', 1) + 1
                reposted.append(o)
            else:
                dup.append(o)
            continue
        added.append(job)

added.sort(key=lambda j: j['d'])
n = max(int(j['id'][2:]) for j in jobs)
for i, j in enumerate(added):
    n += 1
    added[i] = {'id': 'SG%03d' % n, **j}
    jobs.append(added[i])
jobs.sort(key=lambda j: int(j['id'][2:]), reverse=True)
open(DATA, 'w').write(PREFIX + json.dumps(jobs, ensure_ascii=False, separators=(',', ':')) + ';\n')
print('total', len(jobs), 'added', len(added), 'reposted', len(reposted), 'already there', len(dup))
for o in reposted:
    print('  ~', o['id'], o['d'], o['t'], o['pay'], 'n=%d' % o['n'])
for j in added:
    print('  +', j['id'], j['d'], j['ind'], '|', j['t'], '|', j['b'], j['p'], j['nt'], j['rg'])
