# -*- coding: utf-8 -*-
"""三项专项核查：精确定位原文并核对一致性"""
import re, io, os

import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _paths
BASE = _paths.root()
bid = io.open(os.path.join(BASE, 'qc', 'bid_struct.txt'), encoding='utf-8').read()
lines = bid.split('\n')


def clean(s):
    s = re.sub(r'\[P\]', '', s)
    s = re.sub(r'\[H\d+\]', '[表]', s)
    return re.sub(r'\s+', ' ', s).strip()


def show(kw, limit=12, ctx=170):
    print('\n' + '#' * 70)
    print('# 检索：%s' % kw)
    print('#' * 70)
    n = 0
    for i, ln in enumerate(lines):
        if kw in ln:
            n += 1
            if n > limit:
                print('   ... 另有命中')
                break
            print('[L%-6d] %s' % (i, clean(ln)[:ctx]))
    if n == 0:
        print('   未命中')


# ========== 一、工期矛盾（示例：按项目替换检索词） ==========
print('\n\n' + '=' * 74)
print('一、工期、节点矛盾专项')
print('=' * 74)

show('YYYY年M月D日', 14)
show('示例道路', 8)
show('枯水期', 8)

print('\n' + '=' * 74)
print('坝体填筑起止时间（多个版本）')
print('=' * 74)
for kw in ['开始填筑', '填筑完成时间', '填筑安排', '开始填筑时间']:
    print('\n-- %s --' % kw)
    n = 0
    for i, ln in enumerate(lines):
        if kw in ln:
            n += 1
            if n > 5:
                break
            print('  [L%-6d] %s' % (i, clean(ln)[:200]))

# ========== 二、设备配备（示例词） ==========
print('\n\n' + '=' * 74)
print('二、设备配备专项')
print('=' * 74)
show('主要施工设备配置计算', 4, 500)
show('填筑施工机械设备', 5, 300)
show('混凝土浇筑设备', 6, 260)
show('平仓机', 5)
show('光面碾', 5)
show('羊脚碾', 5)

# ========== 三、工程量自洽（示例词） ==========
print('\n\n' + '=' * 74)
print('三、工程量自洽专项')
print('=' * 74)
for kw in ['土石方开挖总量', '填筑工程主要指', '总量约',
           '混凝土总量', '面板混凝土', '总方量', '工程量约']:
    print('\n-- %s --' % kw)
    n = 0
    for i, ln in enumerate(lines):
        if kw in ln:
            n += 1
            if n > 6:
                break
            print('  [L%-6d] %s' % (i, clean(ln)[:230]))
