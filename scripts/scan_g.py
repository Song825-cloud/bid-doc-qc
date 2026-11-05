# -*- coding: utf-8 -*-
"""第三重 G组：工程范围与模板串用残留 全量扫描"""
import re, sys, json
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _paths
_QC = _paths.qc()
sys.stdout.reconfigure(encoding='utf-8')

recs = json.load(open(os.path.join(_QC, 'bid_struct.json'), encoding='utf-8'))

# 逐条记录的可检索文本
items = []
for r in recs:
    if r['t'] in ('p', 'tr'):
        items.append(r)

# 他项目/外省市地名（按项目填写，用于识别模板串用残留）
# 示例格式：['他项目A', '他项目B', '外省A', '外省B']
OTHER_PROJ = []

# 非本标段工程类型关键词（本标段为上水库土建+金属结构+营地）
FOREIGN_TYPE = [
    '市政', '道路工程', '桥梁', '地铁', '轨道交通', '房建', '住宅楼',
    '写字楼', '厂房', '商业综合体', '污水处理', '垃圾处理', '烟囱',
    '冷却塔', '化工', '冶金', '矿山', '疏浚', '航道', '港口', '码头',
    '海堤', '围堰', '船闸', '节制闸', '灌溉', '渠道', '渡槽', '倒虹吸',
    '泵站', '水闸', '闸门', '钢管', '压力钢管', '机电安装', '通风空调',
    '电梯', '幕墙', '园林绿化', '景观',
]

KEY = ['大坝', '土石坝', '隧洞', '洞挖', '面板堆石坝', '堆石坝', '金属结构',
       '防渗墙', '帷幕灌浆', '土工膜', '碾压混凝土', '沥青混凝土']

hits = []

def add(g, kw, r, ctx=''):
    hits.append({'group': g, 'kw': kw, 'path': r.get('path', ''),
                 'text': r.get('text', '')[:300], 'ctx': ctx,
                 'idx': r.get('idx', r.get('row'))})

for r in items:
    tx = r.get('text', '')
    if not tx:
        continue
    for kw in OTHER_PROJ:
        if kw in tx:
            add('G-地名', kw, r)
    for kw in FOREIGN_TYPE:
        if kw in tx:
            add('G-范围', kw, r)

# 汇总统计
from collections import Counter
cnt = Counter(h['kw'] for h in hits)
print('=== 命中统计（G组）===')
for k, v in cnt.most_common(60):
    print(f'{v:5d}  {k}')
print('总命中', len(hits))

json.dump(hits, open(os.path.join(_QC, 'g_hits.json'), 'w', encoding='utf-8'), ensure_ascii=False)