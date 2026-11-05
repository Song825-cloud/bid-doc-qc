# -*- coding: utf-8 -*-
"""C组+D组+E组：组织机构人员 / 设备试验 / 平面布置 与招标基准交叉校验"""
import re, sys, json
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _paths
_QC = _paths.qc()
from collections import Counter, defaultdict
sys.stdout.reconfigure(encoding='utf-8')

recs = json.load(open(os.path.join(_QC, 'bid_struct.json'), encoding='utf-8'))

# ---------- D组：施工设备与试验检测资源 ----------
print('=' * 70)
print('【D组-1】专业设备覆盖检查（本标段应覆盖的施工专业）')
print('=' * 70)
NEED = {
    '大坝填筑/堆石坝': ['堆石坝', '填筑', '碾压', '推土机', '振动碾', '平碾', '洒水车'],
    '面板混凝土': ['面板混凝土', '滑模', '模板', '振捣'],
    '土工膜/防渗': ['土工膜', '防渗', '铺设', '热熔'],
    '隧洞/洞挖': ['隧洞', '洞挖', '钻机', '台车', '喷混凝土', '初期支护', '锚杆'],
    '钻孔灌浆': ['灌浆', '钻孔'],
    '金属结构/闸门': ['金属结构', '闸门', '启闭机', '安装'],
    '土石方明挖': ['挖掘机', '明挖', '边坡', '支护', '锚索'],
    '路桥/场内交通': ['道路', '摊铺', '压实', '沥青'],
    '房建/营地': ['塔吊', '塔机', '施工电梯', '模板', '砌体', '装修'],
    '供水系统': ['泵站', '水泵', '管线', '供水'],
    '试验检测': ['试验', '检测', '测量', '试验室'],
}
alltext = []
for r in recs:
    if r['t'] in ('p', 'tr') and r.get('text'):
        alltext.append(r.get('text', ''))
full = '\n'.join(alltext)

for prof, kws in NEED.items():
    miss = [k for k in kws if k not in full]
    flag = 'OK ' if not miss else '缺失'
    print('  [%s] %-16s 缺: %s' % (flag, prof, miss if miss else '无'))

print()
print('=' * 70)
print('【D组-2】设备单位混用检查（辆/台/套/台班）')
print('=' * 70)
unit_pat = re.compile(r'(\d+(?:\.\d+)?)\s*(辆|台|套|个|部|台班|面|根|块|座|间|列|支|块)')
bad_unit = []
for r in recs:
    if r['t'] != 'tr':
        continue
    tx = r.get('text', '')
    if '台班' in tx:
        continue
    ms = unit_pat.findall(tx)
    if len(set(m[1] for m in ms)) > 2 and len(ms) > 4:
        bad_unit.append({'path': r.get('path', ''), 'text': tx[:220]})
print('  可疑量纲混用表格行：%d 条' % len(bad_unit))
for b in bad_unit[:12]:
    print('   [%s]' % b['path'][-60:])
    print('     ', b['text'][:180])

print()
print('=' * 70)
print('【C组】组织机构 / 部门名称一致性')
print('=' * 70)
DEPT = ['工程技术部', '质量安全部', '物资设备部', '财务部', '综合办公室',
        '工程管理部', '安全环保部', '测量队', '试验室', '调度室', '总工程师办公室']
for d in DEPT:
    print('  %-16s 出现 %d 次' % (d, full.count(d)))

print()
print('  --- 疑似部门名称变体 ---')
VAR = ['工程技术部', '工程部', '技术部', '质量安全部', '安全质量部', '质量部', '安全部',
       '物资设备部', '设备物资部', '物资部', '综合办', '办公室', '财务部', '计财部']
for v in VAR:
    c = full.count(v)
    if c:
        print('   %-12s %d 次' % (v, c))

print()
print('=' * 70)
print('【E组】地名一致性（本标段所在地 vs 其他）')
print('=' * 70)
# 按项目填写本标段真实地名，用于检查模板串用/他项目地名残留
# 示例格式：['本县', '本市', '本镇', '本村']
PLACE = []
for p in PLACE:
    print('  %-10s %d 次' % (p, full.count(p)))