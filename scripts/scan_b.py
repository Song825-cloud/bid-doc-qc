# -*- coding: utf-8 -*-
"""第三重 B组：工期、日期与里程碑节点一致性核查"""
import re, sys, json
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _paths
_QC = _paths.qc()
sys.stdout.reconfigure(encoding='utf-8')

recs = json.load(open(os.path.join(_QC, 'bid_struct.json'), encoding='utf-8'))
items = [r for r in recs if r['t'] in ('p', 'tr') and r.get('text')]

# 招标基准里程碑节点（按项目专用合同条款填写：节点名 -> YYYY-MM-DD）
# 以下仅示结构，实际使用时替换为本项目招标文件中的节点
NODES = {
    # '工程开工': 'YYYY-MM-01',
    # '关键节点A': 'YYYY-MM-DD',
    # '关键节点B': 'YYYY-MM-DD',
}

# 提取所有日期
DATE_RE = re.compile(r'(20\d{2})\s*年\s*(\d{1,2})\s*月\s*(\d{1,2})\s*日')
DATE_RE2 = re.compile(r'(20\d{2})\s*[-/\.]\s*(\d{1,2})\s*[-/\.]\s*(\d{1,2})')
YEAR_RE = re.compile(r'(20\d{2})\s*年')

def norm(y, m, d):
    return '%s-%02d-%02d' % (y, int(m), int(d))

dates = []
for r in items:
    tx = r.get('text', '')
    for m in DATE_RE.finditer(tx):
        dates.append((norm(*m.groups()), m.group(0), tx, r))
    for m in DATE_RE2.finditer(tx):
        dates.append((norm(*m.groups()), m.group(0), tx, r))

# 聚焦关键节点名称
KEYNODE_KW = ['围堰', '坝体填筑', '面板混凝土', '库底防渗', '具备蓄水',
              '蓄水条件', '首台机组', '进/出水口', '进水口', '出水口',
              '营地交付', '交付使用', '投用', '2#道路', '砂石加工系统',
              '混凝土生产系统', '供水系统']

rows = []
seen = set()
for iso, raw, tx, r in dates:
    path = r.get('path', '')
    if not any(k in tx for k in KEYNODE_KW):
        continue
    if not any(k in tx or k in path for k in KEYNODE_KW):
        continue
    key = (iso, path[:60])
    if key in seen:
        continue
    seen.add(key)
    rows.append({'date': iso, 'path': path, 'text': tx[:260]})

json.dump(rows, open(os.path.join(_QC, 'b_hits.json'), 'w', encoding='utf-8'), ensure_ascii=False)
print('关键节点相关日期条目', len(rows))
print()
from collections import Counter
c = Counter(r['date'] for r in rows)
print('=== 出现的日期（按章节）===')
for r in rows:
    print(r['date'], '|', r['path'][-95:])
    print('      ', r['text'][:170])