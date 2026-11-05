# -*- coding: utf-8 -*-
"""三项专项核查数据提取：H 工期矛盾 / E 设备配备 / Q 工程量自洽
输出专项核查原始数据，供后续整理入报告。
"""
import re, io, json, os

import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _paths
BASE = _paths.root()
QC = _paths.qc()
# ---------- 读入已解析的技术文件结构化文本 ----------
bid = io.open(os.path.join(QC, 'bid_struct.txt'), encoding='utf-8').read()
print('技术文件结构化文本：%d 字符' % len(bid))

lines = bid.split('\n')
print('行数：%d' % len(lines))

out = {}

# ==================== H  工期与节点矛盾 ====================
print('\n' + '=' * 60)
print('H  工期、日期与节点')
print('=' * 60)

# 全部日期型表述
DATE_RE = re.compile(r'(20\d{2})\s*[年\-/\.]\s*(\d{1,2})\s*[月\-/\.]\s*(\d{1,2})\s*日?')
date_hits = {}
for i, ln in enumerate(lines):
    for m in DATE_RE.finditer(ln):
        d = '%s-%02d-%02d' % (m.group(1), int(m.group(2)), int(m.group(3)))
        date_hits.setdefault(d, []).append((i, ln.strip()[:150]))

# 年份+月 型（无日）
YM_RE = re.compile(r'(20\d{2})\s*年\s*(\d{1,2})\s*月')
ym_hits = {}
for i, ln in enumerate(lines):
    for m in YM_RE.finditer(ln):
        d = '%s-%02d' % (m.group(1), int(m.group(2)))
        ym_hits.setdefault(d, []).append((i, ln.strip()[:150]))

print('完整日期种类：%d' % len(date_hits))
for d in sorted(date_hits):
    print('  %s  x%d' % (d, len(date_hits[d])))

out['date_full'] = {k: v[:40] for k, v in date_hits.items()}
out['date_ym'] = {k: v[:40] for k, v in ym_hits.items()}

# 工期表述
print('\n--- 工期表述 ---')
DUR_PAT = [r'\d+\s*日历天', r'\d+\s*个月', r'总工期[^\n]{0,40}',
           r'计划工期[^\n]{0,40}', r'工期[^\n]{0,6}\d+\s*[个月天]']
dur_hits = []
for i, ln in enumerate(lines):
    for p in DUR_PAT:
        for m in re.finditer(p, ln):
            dur_hits.append((i, p, m.group(0), ln.strip()[:160]))
for h in dur_hits[:40]:
    print('  L%-7d %-18s %s' % (h[0], h[1], h[3][:110]))
print('  合计 %d 处' % len(dur_hits))
out['duration'] = dur_hits[:200]

# ==================== E  设备配备 ====================
print('\n' + '=' * 60)
print('E  设备配备')
print('=' * 60)

EQUIP = ['挖掘机', '装载机', '推土机', '铲运机', '自卸汽车', '洒水车',
         '平仓机', '振动碾', '光面碾', '羊脚碾', '碎石机', '砂石料',
         '混凝土搅拌', '拌和站', '砼泵', '泵车', '振动器', '振捣',
         '灌浆机', '钻机', '锚杆', '喷浆', '钢模', '模板', '钢筋',
         '起重机', '塔机', '汽车吊', '卷扬机', '通风机', '空压机',
         '排水泵', '水泵', '柴油发电机', '变压器', '电缆', '潜水电泵']

eq_hits = {}
for i, ln in enumerate(lines):
    for e in EQUIP:
        if e in ln:
            eq_hits.setdefault(e, []).append((i, ln.strip()[:130]))

print('%-10s %s' % ('设备名', '命中行数 / 示例'))
for e in EQUIP:
    v = eq_hits.get(e, [])
    print('%-10s %4d  %s' % (e, len(v), (v[0][1][:70] if v else '—')))
out['equip'] = {k: v[:30] for k, v in eq_hits.items()}

# 设备表：含数量单位、台、套
print('\n--- 设备数量表述（X台/X套）---')
QTY_RE = re.compile(r'(\d+)\s*(?:台|套|辆|组|条|台套)')
qty = []
for i, ln in enumerate(lines):
    if any(e in ln for e in EQUIP):
        for m in QTY_RE.finditer(ln):
            qty.append((i, m.group(0), ln.strip()[:150]))
for q in qty[:50]:
    print('  L%-7d %-6s %s' % (q[0], q[1], q[2][:100]))
print('  合计 %d 处' % len(qty))
out['equip_qty'] = qty[:200]

# 产能表述
print('\n--- 产能/效率表述 ---')
CAP_RE = re.compile(r'(\d+(?:\.\d+)?)\s*(?:m3|m³|立方米|方)\s*/\s*(?:h|小时|台班|台时|d|天|月)')
cap = []
for i, ln in enumerate(lines):
    for m in CAP_RE.finditer(ln):
        cap.append((i, m.group(0), ln.strip()[:150]))
for c in cap[:40]:
    print('  L%-7d %-16s %s' % (c[0], c[1], c[2][:100]))
print('  合计 %d 处' % len(cap))
out['equip_cap'] = cap[:200]

# ==================== Q  工程量自洽 ====================
print('\n' + '=' * 60)
print('Q  工程量自洽性')
print('=' * 60)

# 万m3 / m3 数值
VOL_RE = re.compile(r'(\d+(?:\.\d+)?)\s*(?:万)?\s*(?:m3|m³|立方米|方)\b')
vol = {}
for i, ln in enumerate(lines):
    for m in VOL_RE.finditer(ln):
        key = m.group(0)
        vol.setdefault(key, []).append((i, ln.strip()[:140]))

print('--- 量值出现频次 top 40 ---')
for k, v in sorted(vol.items(), key=lambda x: -len(x[1]))[:40]:
    print('  %-14s x%-4d %s' % (k, len(v), v[0][1][:80]))

# 关键工程量的不同取值（同一工程量名称多个数值）
print('\n--- 同一工程量的不同取值（重点排查）---')
KEYS = ['围堰', '填筑', '土石方', '开挖', '混凝土', '面板', '防渗',
        '土工膜', '灌浆', '砌体', '钢筋', '洞室', '道路', '排水']
conflict = []
for kk in KEYS:
    vals = {}
    for i, ln in enumerate(lines):
        if kk not in ln:
            continue
        for m in VOL_RE.finditer(ln):
            vals.setdefault(m.group(0), []).append((i, ln.strip()[:130]))
    if len(vals) > 1:
        print('\n【%s】出现 %d 个不同量值：' % (kk, len(vals)))
        for vv, lst in sorted(vals.items(), key=lambda x: -len(x[1]))[:8]:
            print('   %-14s x%-4d 例: %s' % (vv, len(lst), lst[0][1][:85]))
        conflict.append((kk, {vv: len(lst) for vv, lst in vals.items()}))

out['vol_values'] = {k: {vv: len(lst) for vv, lst in v.items()}
                     for k, v in vol.items()}
out['vol_conflict'] = {k: v for k, v in conflict}

with io.open(os.path.join(QC, 'spot_raw.json'), 'w', encoding='utf-8') as f:
    json.dump(out, f, ensure_ascii=False, indent=2, default=str)
print('\n-> spot_raw.json')
