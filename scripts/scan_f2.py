# -*- coding: utf-8 -*-
"""F组深化：同一标准号多个年份并存 / 疑似废止 / 格式错误"""
import re, sys, json
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _paths
_QC = _paths.qc()
from collections import defaultdict
sys.stdout.reconfigure(encoding='utf-8')

d = json.load(open(os.path.join(_QC, 'f_stds.json'), encoding='utf-8'))

def base_no(s):
    """取标准号主体（去年份）"""
    return re.split(r'-\d{2,4}$', s)[0]

groups = defaultdict(list)
for k in d:
    groups[base_no(k)].append(k)

print('=' * 70)
print('【类别1】同一标准号存在多个年份版本 —— 必改（同一文件内自相矛盾）')
print('=' * 70)
c1 = []
for b, ks in sorted(groups.items()):
    if len(ks) > 1:
        cnt = {k: len(d[k]) for k in ks}
        c1.append((b, ks, cnt))
        print('  %-16s %s   出现次数 %s' % (b, ' / '.join(ks), list(cnt.values())))

print()
print('=' * 70)
print('【类别2】缺少年份的标准号（GB、SL、JGJ、DL 强制要求标年份）')
print('=' * 70)
c2 = []
for k in sorted(d):
    if re.search(r'-\d{2,4}$', k):
        continue
    # 排除 SL/T 前缀与无年份惯例
    if re.match(r'^(GB|GB/T|JTG|JTG/T|SL|SL/T|DL|DL/T|JTJ|JGJ|JTS|CJJ|AQ)\d', k):
        c2.append((k, len(d[k])))
        print('  %-16s 出现 %d 次' % (k, len(d[k])))

print()
print('=' * 70)
print('【类别3】格式异常（缺连字符、年份粘连、疑似OCR错误）')
print('=' * 70)
c3 = []
BAD = re.compile(r'(GB\d{3,5}$)|(GB\d{5}\d{4})|(GB6-10)|(GB213632021)|(NB/T213632021)|(JTJ0\d{2,3}$)|(SL\d{2,4}$)|(DL\d{4}$)|(ZY\d+$)')
for k in sorted(d):
    if BAD.search(k):
        c3.append((k, len(d[k])))
        print('  %-18s 出现 %d 次' % (k, len(d[k])))

print()
print('汇总：类别1 %d 组 / 类别2 %d 条 / 类别3 %d 条' % (len(c1), len(c2), len(c3)))
json.dump({'c1': [[b, ks, list(cnt.values())] for b, ks, cnt in c1],
           'c2': c2, 'c3': c3}, open(os.path.join(_QC, 'f_conflicts.json'), 'w', encoding='utf-8'),
          ensure_ascii=False)