# -*- coding: utf-8 -*-
"""答疑澄清专项条款落实核查（41项澄清 + 5项修改）"""
import re, sys, json
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _paths
_QC = _paths.qc()
sys.stdout.reconfigure(encoding='utf-8')

recs = json.load(open(os.path.join(_QC, 'bid_struct.json'), encoding='utf-8'))
items = [r for r in recs if r['t'] in ('p', 'tr') and r.get('text')]
full = '\n'.join(r['text'] for r in items)


def probe(label, must_any, must_not=(), note=''):
    """must_any: 至少命中其一；must_not: 均不得出现"""
    ok = [k for k in must_any if k in full]
    bad = [k for k in must_not if k in full]
    if ok and not bad:
        st = '符合'
    elif not ok and not bad:
        st = '未提及'
    elif bad:
        st = '冲突'
    else:
        st = '部分'
    print('  [%-4s] %s' % (st, label))
    if ok:
        print('         命中: %s' % '、'.join(ok))
    if bad:
        print('         冲突: %s' % '、'.join(bad))
    if note:
        print('         说明: %s' % note)


print('=' * 74)
print('答疑澄清关键条款落实核查')
print('=' * 74)

# 按项目填写：label 说明、must_any 至少命中其一、must_not 均不得出现、note 备注
probe('示例条款A: 某节点日期以答疑为准',
      ['YYYY年M月D日'], ['旧日期占位'],
      '技术文件可能仍采用澄清前旧日期')
probe('示例条款B: 某部位断面尺寸',
      ['示例尺寸'])
probe('示例条款C: 某材料强度等级',
      ['示例等级'], [], '属商务/技术交叉事项')

print()
print('=' * 74)
print('招标强制技术要求落实核查（技术标内应体现）')
print('=' * 74)
probe('安全文明施工费（否决投标项）', ['安全文明施工费'], [], '报价事项，仅提示')
probe('质量承诺：承诺创建优质工程并接受违约处罚', ['优质工程'], [])
probe('BIM 技术应用', ['BIM'], [])
probe('施工总平面图（附图表和说明）', ['施工总平面图', '总平面布置图'], [])
probe('施工进度网络图（关键线路）', ['网络图'], [])
probe('质量管理体系 ISO9001/14001/45001',
      ['ISO9001', 'ISO14001', 'ISO45001'], [])
