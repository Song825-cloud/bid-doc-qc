# -*- coding: utf-8 -*-
"""精修版招标文件页码索引 —— 所有页码均经关键词实测核验。
输出 tender_pages.json
"""
import re, json, os, io

import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _paths
BASE = _paths.root()
PARSED = _paths.parsed_dir()
# PDF 解析文本按文件名关键词自动识别（正文 / 答疑 / 图纸），无需硬编码文件名
DOCS = {k: os.path.basename(v) for k, v in _paths.find_tender_txts().items()}
SHORT = {'正文': '招标文件正文', '答疑': '答疑澄清', '图纸': '施工图'}
TOTAL = {'正文': 224, '答疑': 19, '图纸': 6}


def norm(s):
    s = re.sub(r'\s+', '', s)
    for a, b in (('（', '('), ('）', ')'), ('，', ','), ('、', ','),
                 ('。', '.'), ('；', ';'), ('：', ':'), ('　', '')):
        s = s.replace(a, b)
    return s


PAGED = {}
for k, v in DOCS.items():
    with io.open(os.path.join(PARSED, v), encoding='utf-8') as f:
        raw = f.read()
    parts = re.split(r'=====\s*\[.*?\]\s*第(\d+)页\s*=====', raw)
    PAGED[k] = [(int(parts[i]), norm(parts[i + 1]))
                for i in range(1, len(parts) - 1, 2)]

# 目录页（含大量点线）识别
TOC = set()
for pg, t in PAGED['正文']:
    if len(re.findall(r'\.{4,}', t)) >= 4:
        TOC.add(pg)

CH_RE = re.compile(r'第[一二三四五六七八九十]+章\s*[^\s第，。、]{2,22}')


def chapter_map(key):
    """返回 {页: 章节简称}；章节名截到第一个可断点，避免吞入后续文字"""
    out, cur = {}, '封面'
    for pg, t in PAGED[key]:
        if pg in TOC:
            out[pg] = cur
            continue
        for m in CH_RE.finditer(t):
            cand = m.group(0)
            tail = t[m.end():m.end() + 30]
            if re.match(r'\.{4,}', tail) or re.match(r'[\.．]{3,}', tail):
                continue
            # 只取「第三章评标办法」这类前缀，遇括号/长尾即止
            mm = re.match(r'(第[一二三四五六七八九十]+章\s*[^，。、（）()]{2,10})',
                          cand)
            cur = mm.group(1) if mm else cand[:12]
            break
        out[pg] = cur
    return out


CHAP = {k: chapter_map(k) for k in PAGED}


def find(key, kws, limit=6):
    for kw in kws:
        nk = norm(kw)
        if len(nk) < 2:
            continue
        pgs = [pg for pg, t in PAGED[key] if nk in t]
        if pgs:
            return pgs[:limit], kw
    return [], None


# ==== 经实测核验的定位项 ====
# (doc, [关键词优先级], 人工确认的代表页或 None)
Q = {}


def q(item, doc, kws, note=None):
    Q[item] = (doc, list(kws), note)


# ---- 定位项示例（按项目填写：编号, 文档类别, [关键词优先级], 说明）----
# 文档类别：正文 / 答疑 / 图纸；关键词从短到长，命中即止
q('1-01', '正文', ['工程名称'], '封面/公告标注的标段名称')
q('1-02', '正文', ['投标人须知'], '投标人须知相关条款')
q('2-01', '正文', ['施工组织设计'], '评分要素对应章节')
q('A-01', '正文', ['工程量清单'], '招标范围与工程量清单说明')
q('B-01', '正文', ['里程碑'], '里程碑节点表')
q('E-01', '正文', ['施工总平面'], '施工总平面布置图附表')
# ……按报告编号补齐全部定位项（1-xx / 2-xx / A-xx…G-xx / T-xx）

result = {}
for item in sorted(Q):
    doc, kws, note = Q[item]
    pgs, used = find(doc, kws)
    chap = CHAP[doc].get(pgs[0], '') if pgs else ''
    result[item] = {
        'doc': SHORT[doc],
        'pages': pgs,
        'page_str': ('P' + '、P'.join(str(p) for p in pgs[:6])) if pgs else '',
        'chapter': chap,
        'keyword': used or '',
        'note': note,
        'doc_pages': TOTAL[doc],
    }

out = os.path.join(BASE, 'qc', 'tender_pages.json')
with io.open(out, 'w', encoding='utf-8') as f:
    json.dump(result, f, ensure_ascii=False, indent=2)

miss = [k for k, v in result.items() if not v['pages']]
print('文档总页数：', {SHORT[k]: v for k, v in TOTAL.items()})
print('共 %d 项，未定位 %d 项：%s\n' % (len(result), len(miss), miss))
for k in sorted(result):
    v = result[k]
    print('%-6s %-8s %-30s %-22s %s' % (
        k, v['doc'], v['page_str'] or '—', v['chapter'][:20], v['note'][:30]))
print('\n->', out)