# -*- coding: utf-8 -*-
"""第一重 + 第四重：项目名称一致性、错字格式全面扫描"""
import re, sys, json
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _paths
_QC = _paths.qc()
from collections import Counter, defaultdict
sys.stdout.reconfigure(encoding='utf-8')

recs = json.load(open(os.path.join(_QC, 'bid_struct.json'), encoding='utf-8'))
items = [r for r in recs if r['t'] in ('p', 'tr') and r.get('text')]

print('=' * 72)
print('【第一重-A】项目名称一致性 —— 全称/简称/错字')
print('=' * 72)
NAME_OK = '上水库'
name_hits = defaultdict(list)
for r in items:
    tx = r.get('text', '')
    if '水库' in tx and ('工程' in tx or '施工' in tx):
        if '下水库' in tx:
            name_hits['下水库'].append(r)
        elif '上水库' in tx:
            name_hits['上水库'].append(r)
        else:
            name_hits['其他'].append(r)

for k, v in name_hits.items():
    print('  【%s】 出现 %d 条' % (k, len(v)))
print()
print('  --- 「下水库」逐条明细（须逐句确认是否属其他标段引用）---')
for r in name_hits['下水库']:
    tx = r['text']
    # 排除明显属于其他标段/C2标/地下工程的语境
    flag = ''
    if any(x in tx for x in ['C2标', '另一标段', '其他标段', '本标段不承担', '下水库工程', '下水库枢纽']):
        flag = '[可能属他标段引用]'
    print('   %s' % flag)
    print('     路径: ...%s' % r['path'][-72:])
    print('     原文: %s' % tx[:230])
    print()

print('=' * 72)
print('【第一重-B】标段名称一致性（C1/C2 标、YAP C1）')
print('=' * 72)
full = '\n'.join(r['text'] for r in items)
for kw in ['C1标', 'C2标', 'YAP C1', 'C1 标', 'C2 标', '本标段', '本合同']:
    print('  %-8s %d 次' % (kw, full.count(kw)))

print()
print('=' * 72)
print('【第四重】错字与格式扫描')
print('=' * 72)

pairs = '的的|了了|在在|是是|和和|及及|与与|部部|。。|、、|一一|将将|我们我|以以|和和'
pat_dup = re.compile(pairs)
pat_cn_space = re.compile(r'[\u4e00-\u9fa5] [\u4e00-\u9fa5]')
pat_paren = re.compile(r'[（(]\s*[）)]')
pat_punct = re.compile(r'[，。、；：]\s*[）)]|[(（]\s*[，。]')

typos = defaultdict(list)
for r in items:
    tx = r['text']
    for m in pat_dup.finditer(tx):
        typos['重复字'].append((r, m.group(0)))
    for m in pat_cn_space.finditer(tx):
        # 过滤正常的"图 X"式（中文间空格少见，多为误入）
        typos['中文词内空格'].append((r, tx[max(0, m.start()-12):m.start()+12]))
    for m in pat_paren.finditer(tx):
        typos['空括号'].append((r, tx[max(0, m.start()-15):m.start()+15]))

for k, v in typos.items():
    print()
    print('  【%s】 %d 处' % (k, len(v)))
    seen = set()
    n = 0
    for r, ctx in v:
        key = (k, ctx[:20], r['path'][-40:])
        if key in seen:
            continue
        seen.add(key)
        n += 1
        if n > 25:
            print('     ......（略）')
            break
        print('     · [%s] %r' % (r['path'][-50:], ctx))
    if n <= 25:
        print('     合计去重后 %d 处' % n)

json.dump({k: [[r['path'], c] for r, c in v] for k, v in typos.items()},
          open(os.path.join(_QC, 'typos.json'), 'w', encoding='utf-8'), ensure_ascii=False)