# -*- coding: utf-8 -*-
"""回读校验报告"""
import sys, os
sys.stdout.reconfigure(encoding='utf-8')
import docx
from docx.oxml.ns import qn

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _paths
F = (sys.argv[1] if len(sys.argv) > 1 else
     os.path.join(_paths.bid_dir(), '技术文件四重质检报告（含页码版）YYYYMMDD.docx'))
d = docx.Document(F)

print('段落数', len(d.paragraphs))
print('表格数', len(d.tables))
print('节数', len(d.sections))
for i, s in enumerate(d.sections):
    print('  节%d 宽%.1fcm 高%.1fcm' % (i, s.page_width.cm, s.page_height.cm))

print()
print('=== 各表规模 ===')
for i, t in enumerate(d.tables):
    hdr = ' | '.join(c.text.strip()[:12] for c in t.rows[0].cells)
    print('  表%-2d %2d行 x %d列  表头: %s' % (i + 1, len(t.rows), len(t.columns), hdr[:78]))

print()
print('=== 配色校验（统计各表等级单元格底纹与字体色）===')
from collections import Counter
fill_cnt = Counter()
color_cnt = Counter()
for ti, t in enumerate(d.tables):
    for ri, row in enumerate(t.rows):
        for c in row.cells:
            tcPr = c._tc.find(qn('w:tcPr'))
            if tcPr is None:
                continue
            shd = tcPr.find(qn('w:shd'))
            if shd is not None:
                fill_cnt[shd.get(qn('w:fill'))] += 1
            for p in c.paragraphs:
                for r in p.runs:
                    if r.font.color and r.font.color.rgb is not None:
                        color_cnt[str(r.font.color.rgb)] += 1
print('底纹颜色分布:')
for k, v in fill_cnt.most_common(14):
    print('   #%s  %d 处' % (k, v))
print('字体颜色分布:')
for k, v in color_cnt.most_common(14):
    print('   #%s  %d 处' % (k, v))

print()
print('=== 章节标题 ===')
for p in d.paragraphs:
    if p.style.name.startswith('Heading') and p.text.strip():
        print('  %s%s' % ('  ' * (int(p.style.name[-1]) - 1), p.text.strip()[:70]))

print()
print('=== 页脚页码域 ===')
for s in d.sections:
    ftxt = s.footer.paragraphs[0]._p.xml if s.footer.paragraphs else ''
    has_page = 'PAGE' in ftxt
    has_num = 'NUMPAGES' in ftxt
    print('  PAGE域:', has_page, ' NUMPAGES域:', has_num)

print()
print('=== 等级统计自洽核对 ===')
rows_total = sum(len(t.rows) - 1 for t in d.tables)
print('  全部表格数据行合计(含重复表头):', rows_total)
lv_count = Counter()
for t in d.tables:
    hdr0 = t.rows[0].cells[0].text.strip()
    for row in t.rows[1:]:
        for c in row.cells:
            tcPr = c._tc.find(qn('w:tcPr'))
            if tcPr is None:
                continue
            shd = tcPr.find(qn('w:shd'))
            if shd is not None:
                f = shd.get(qn('w:fill'))
                if f == 'FCE4E4':
                    lv_count['P0'] += 1
                elif f == 'FDF0E4':
                    lv_count['P1'] += 1
                elif f == 'FFF9E0':
                    lv_count['P2'] += 1
                elif f == 'E8F5EC':
                    lv_count['PASS'] += 1
print('  各等级着色单元格数:', dict(lv_count))