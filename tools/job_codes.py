# 新加坡职位查询码：生成、作废、查看。仓库里只存哈希（api/_codes.json），明文码只打印一次，要自己保存。
# 用法：
#   python3 tools/job_codes.py new 20 [备注]   生成 20 个新码
#   python3 tools/job_codes.py revoke YT-ABCD-2345   作废一个码
#   python3 tools/job_codes.py list   看现有码的备注和数量
# 改完要提交并部署才生效。
import hashlib, json, os, secrets, sys

PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'api', '_codes.json')
ALPHA = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789'  # 去掉容易看错的 0 O 1 I


def norm(code):
    return code.upper().replace('-', '').replace(' ', '')


def h(code):
    return hashlib.sha256(norm(code).encode()).hexdigest()


codes = json.load(open(PATH)) if os.path.exists(PATH) else {}
cmd = sys.argv[1] if len(sys.argv) > 1 else 'list'
if cmd == 'new':
    n, note = int(sys.argv[2]), (sys.argv[3] if len(sys.argv) > 3 else '')
    for _ in range(n):
        raw = ''.join(secrets.choice(ALPHA) for _ in range(8))
        code = f'YT-{raw[:4]}-{raw[4:]}'
        codes[h(code)] = note
        print(code)
elif cmd == 'revoke':
    for code in sys.argv[2:]:
        print(code, '已作废' if codes.pop(h(code), None) is not None else '不存在')
else:
    notes = {}
    for v in codes.values():
        notes[v] = notes.get(v, 0) + 1
    print(len(codes), '个有效码', notes)
json.dump(codes, open(PATH, 'w'), ensure_ascii=False, indent=0, sort_keys=True)
