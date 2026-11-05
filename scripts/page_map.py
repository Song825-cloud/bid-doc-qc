# -*- coding: utf-8 -*-
"""页码映射模块：把报告中的每个质检编号映射到
   投标文件页码（技术文件 docx，Word 渲染后取页）
   招标文件页码（PDF 解析文本按页定位）
两列均需按项目实测后写入（见 toc.json 与 *_pages.json）。
"""
import json
import io
import os

import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _paths
BASE = _paths.root()
QC = _paths.qc()
with io.open(os.path.join(QC, 'bid_pages.json'), encoding='utf-8') as f:
    _BID = json.load(f)
with io.open(os.path.join(QC, 'tender_pages.json'), encoding='utf-8') as f:
    _TEN = json.load(f)

# 第二轮精确取证结果（第三重 A—G 与第四重专用），存在则优先使用
_BID2 = {'total_pages': None, 'items': {}}
_p2 = os.path.join(QC, 'bid_pages2.json')
if os.path.exists(_p2):
    with io.open(_p2, encoding='utf-8') as f:
        _BID2 = json.load(f)

BID_TOTAL = _BID.get('total_pages') or 0
# 各类招标文件总页数（示例占位，按项目实测替换）
TEN_TOTAL = {'招标文件正文': 0, '答疑澄清': 0, '施工图': 0}

# 封面+目录的截止页（此页及以前视为非正文，页码一律剔除）
# 必须先实测：用 pages_head.py 打印每页首段确认正文起点，再写入 toc.json
# 示例项目实测无封面/目录页，故默认 0（不过滤任何页）
TOC_END = 0
_tp = os.path.join(QC, 'toc.json')
if os.path.exists(_tp):
    with io.open(_tp, encoding='utf-8') as _f:
        TOC_END = int(json.load(_f).get('toc_end', TOC_END))


def _fmt_bid(key, maxn=6):
    """技术文件页码 -> 'P44、P45、P68、P101'（去重，剔除封面/目录页）
    第二轮精确取证（bid_pages2）优先。"""
    src = _BID2 if key in _BID2['items'] else _BID
    it = src['items'].get(key)
    if not it or not it['pages']:
        return ''
    seen, pg = set(), []
    for p in it['pages']:
        if p in seen or p <= TOC_END:
            continue
        seen.add(p)
        pg.append(p)
    if not pg:
        return ''
    s = 'P' + '、P'.join(str(p) for p in pg[:maxn])
    if it['total_hits'] > maxn:
        s += f' 等{it["total_hits"]}处'
    return s


def _fmt_ten(key, maxn=4):
    """招标文件页码 -> 'P8' 或 'P52、P78'"""
    it = _TEN.get(key)
    if not it or not it['pages']:
        return ''
    return 'P' + '、P'.join(str(p) for p in it['pages'][:maxn])


def _fmt_ten_full(key, maxn=4):
    """带文件名"""
    it = _TEN.get(key)
    if not it or not it['pages']:
        return ''
    doc = it['doc'].replace('招标文件正文', '正文').replace('答疑澄清', '答疑')
    return doc + ' P' + '、P'.join(str(p) for p in it['pages'][:maxn])


# ============ 第一重 SEC1（16 项）============
SEC1_PAGES = {
    '1-01': ('1-01', '1-01'), '1-02': ('1-02', '1-02'),
    '1-03': ('1-03', '1-03'), '1-04': ('1-04', '1-04'),
    '1-05': ('1-05', '1-05'), '1-06': ('1-06', '1-06'),
    '1-07': ('1-07', '1-07'), '1-08': ('1-08', '1-08'),
    '1-09': ('1-09', '1-09'), '1-10': ('1-10', '1-10'),
    '1-11': ('1-11', '1-11'), '1-12': ('1-12', '1-12'),
    '1-13': ('1-13', '1-13'), '1-14': ('1-14', '1-14'),
    '1-15': ('1-15', '1-15'), '1-16': ('1-16', '1-16'),
}

# ============ 第二重 SEC2（8 评分要素）============
# 投标文件：对应技术文件章节起始页；招标文件：评分标准出处
SEC2_PAGES = {
    '1': ('1-01', '1-13'),   # 项目理解及投标能力 -> 承诺函页 + 联合体要求
    '2': ('2-01', '2-01'),   # 施工总体布置
    '3': ('2-02', '2-02'),   # 施工方案与技术措施
    '4': ('2-03', '2-03'),   # 质量体系与措施
    '5': ('2-04', '2-04'),   # 安全生产
    '6': ('2-05', '2-05'),   # 文明施工
    '7': ('2-06', '2-06'),   # 工程进度计划与措施
    '8': ('2-07', '2-07'),   # 资源配备计划
}

# ============ 第三重 A—G（28 项）============
# 左侧为投标文件精确定位key（bid_pages2），右侧为招标文件定位key
CONFLICT_PAGES = {
    'A-1': ('A-1', 'A-03'), 'A-2': ('A-2', 'A-02'),
    'A-3': ('A-3', 'A-01'), 'A-4': ('A-4', 'F-01'),
    'B-1': ('B-1', 'B-01'), 'B-2': ('B-2', 'B-02'),
    'B-3': ('B-3', 'B-03'), 'B-4': ('B-4', 'B-04'),
    'B-5': ('B-5', 'B-04'), 'B-6': ('B-6', 'B-02'),
    'C-1': ('C-1', 'C-03'), 'C-2': ('C-2', 'C-02'),
    'C-3': ('C-3', 'D-02'), 'C-4': ('C-4', '2-03'),
    'D-1': ('D-1', 'D-01'), 'D-2': ('D-2', 'D-01'),
    'D-3': ('D-3', '2-07'),
    'E-1': ('E-1', 'E-01'), 'E-2': ('E-2', 'A-02'),
    'E-3': ('E-3', 'E-02'), 'E-4': ('E-4', '1-05'),
    'F-1': ('F-1', 'F-01'), 'F-2': ('F-2', 'F-01'),
    'F-3': ('F-3', 'F-02'),
    'G-1': ('G-1', 'G-01'), 'G-2': ('G-2', 'G-01'),
    'G-3': ('G-3', '1-03'), 'G-4': ('G-4', 'G-01'),
}

# ============ 第四重 错字（8 项）============
TYPO_PAGES = {
    '4-01': ('T-1', 'T-01'), '4-02': ('T-2', 'T-02'),
    '4-03': ('T-3', 'F-02'), '4-04': ('T-2', 'F-01'),
    '4-05': ('T-3', 'F-01'), '4-06': ('T-3', 'F-02'),
    '4-07': ('C-1', 'C-03'), '4-08': ('D-3', '2-07'),
}


def bid(no):
    """按报告编号取投标文件页码字符串"""
    for m in (SEC1_PAGES, CONFLICT_PAGES, TYPO_PAGES):
        if no in m:
            return _fmt_bid(m[no][0])
    if no in SEC2_PAGES:
        return _fmt_bid(SEC2_PAGES[no][0], maxn=3)
    return ''


def ten(no):
    """按报告编号取招标文件页码字符串"""
    for m in (SEC1_PAGES, CONFLICT_PAGES, TYPO_PAGES):
        if no in m:
            return _fmt_ten_full(m[no][1])
    if no in SEC2_PAGES:
        return _fmt_ten_full(SEC2_PAGES[no][1])
    return ''


def ten_chapter(no):
    """招标文件章节"""
    for m in (SEC1_PAGES, CONFLICT_PAGES, TYPO_PAGES, SEC2_PAGES):
        if no in m:
            it = _TEN.get(m[no][1])
            if it:
                return it['chapter']
    return ''


# ============ 2.5 节速览表编号 -> 正文章号 ============
LVL2MAP = {
    '1-01': '1-01', '1-08': '1-08', '1-03': '1-03', '1-04': '1-04',
    '1-05': '1-05', '1-06': '1-06', '1-07': '1-07', '1-16': '1-16',
    '3-1': 'B-1', '3-2': 'B-2', '4-01': '4-01',
    '3-F1': 'F-1', '3-F2': 'F-2', '3-F3': 'F-3',
    '2-1': '1', '2-7': '7',
}


def bid_lvl(no):
    """2.5 速览表编号 -> 投标文件页码"""
    return bid(LVL2MAP.get(no, no))


def ten_lvl(no):
    """2.5 速览表编号 -> 招标文件页码"""
    return ten(LVL2MAP.get(no, no))


# ============ 第五章之二 专项核查页码映射 ============
_BID3 = {'total_pages': None, 'items': {}}
_p3 = os.path.join(QC, 'bid_pages3.json')
if os.path.exists(_p3):
    with io.open(_p3, encoding='utf-8') as f:
        _BID3 = json.load(f)

# 专项核查项 -> 招标文件定位key（与技术文件定位key 同名）
SPOT_PAGES = {
    'H-1': 'B-01', 'H-2': 'B-03', 'H-3': 'B-02', 'H-4': 'B-03',
    'H-5': 'B-03', 'H-6': 'B-03', 'H-7': 'B-03', 'H-8': '1-09',
    'E-1': '2-07', 'E-2': 'D-01', 'E-3': '2-07', 'E-4': 'D-01',
    'E-5': 'A-01', 'E-6': 'E-03', 'E-7': 'D-01', 'E-8': 'D-01',
    'Q-1': 'A-01', 'Q-2': 'A-01', 'Q-3': 'A-01', 'Q-4': 'A-01',
    'Q-5': 'A-01', 'Q-6': 'A-01', 'Q-7': 'A-01', 'Q-8': 'A-01',
}


def bid_spot(no, maxn=4):
    """第五章之二专项核查 -> 投标文件页码"""
    d = BID_SPOT_DIRECT.get(no)
    if d:
        return d
    it = _BID3['items'].get(no)
    if not it or not it['pages']:
        return ''
    seen, pg = set(), []
    for p in it['pages']:
        if p in seen or p <= TOC_END:
            continue
        seen.add(p)
        pg.append(p)
    if not pg:
        return ''
    s = 'P' + '、P'.join(str(p) for p in pg[:maxn])
    if it['total_hits'] > maxn:
        s += f' 等{it["total_hits"]}处'
    return s


# 专项核查 -> 投标文件页码（无关键词可稳定定位时人工指定）
# 按项目填写，如 {'H-4': 'Pxx、Pxx'}
BID_SPOT_DIRECT = {}


# 直接指定页码（无关键词可稳定定位时人工填写）
# 按项目填写，如 {'Q-1': '正文 Pxx、Pxx'}
TEN_SPOT_DIRECT = {}


def ten_spot(no, maxn=3):
    """第五章之二专项核查 -> 招标文件页码"""
    d = TEN_SPOT_DIRECT.get(no)
    if d:
        return d
    return _fmt_ten_full(SPOT_PAGES.get(no, ''), maxn)


# 自检
if __name__ == '__main__':
    print('投标文件总页数：%d' % BID_TOTAL)
    print('招标文件总页数：', TEN_TOTAL)
    print()
    for no in list(SEC1_PAGES) + list(SEC2_PAGES):
        print('%-6s bid=%-30s ten=%s' % (no, bid(no), ten(no)))
    print()
    for no in CONFLICT_PAGES:
        print('%-6s bid=%-26s ten=%s' % (no, bid(no), ten(no)))
    print()
    for no in TYPO_PAGES:
        print('%-6s bid=%-26s ten=%s' % (no, bid(no), ten(no)))