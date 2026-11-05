# -*- coding: utf-8 -*-
"""问题清单版报告 —— 回归断言（作为流程的验收关卡）。

用法：python qc/check_slim.py [报告路径]
任一条不满足即以非 0 退出，可直接用于流程「跑完即验收」。
"""
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')
import docx

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _paths
DEFAULT = os.path.join(_paths.bid_dir(), '技术文件质检报告（问题清单版）YYYYMMDD.docx')

F = sys.argv[1] if len(sys.argv) > 1 else DEFAULT

EXP = {
    'tables': 8,
    'sections': 2,
    'issues': 23,
    'levels': {'P0': 6, 'P1': 7, 'P2': 10},
    'pass_rows': 32,
    'info_rows': 5,
    'issue_cols': 7,
    'anchor_rows': 8,
    'score_rows': 8,
    'evidence_rows': 8,
    'form_rows': 10,
}

fails = []


def ck(name, got, want):
    ok = (got == want)
    print('%s %-34s got=%-6s want=%s' % ('PASS' if ok else 'FAIL',
                                         name, got, want))
    if not ok:
        fails.append(name)


d = docx.Document(F)
ck('表格总数', len(d.tables), EXP['tables'])
ck('节数（封面纵向+正文横向）', len(d.sections), EXP['sections'])

t = d.tables[1]
ck('问题清单列数（无责任人/时限/状态/复核人）', len(t.columns), EXP['issue_cols'])
rows = t.rows[1:]
ck('问题清单条数', len(rows), EXP['issues'])

lv = {}
empty = []
for r in rows:
    c = r.cells
    lv[c[2].text.strip()] = lv.get(c[2].text.strip(), 0) + 1
    if not c[4].text.strip() or not c[5].text.strip():
        empty.append(c[0].text.strip())
for k, v in EXP['levels'].items():
    ck('问题清单 %s 条数' % k, lv.get(k, 0), v)
ck('问题清单页码空值', len(empty), 0)

ck('关键招标基准条数', len(d.tables[2].rows) - 1, EXP['anchor_rows'])
ck('评分点条数', len(d.tables[3].rows) - 1, EXP['score_rows'])
ck('专项取证条数', len(d.tables[4].rows) - 1, EXP['evidence_rows'])
ck('形式要件条数', len(d.tables[5].rows) - 1, EXP['form_rows'])
ck('附录一 已核查合规条数', len(d.tables[6].rows) - 1, EXP['pass_rows'])
ck('附录二 待补充材料条数', len(d.tables[7].rows) - 1, EXP['info_rows'])

# 全文不得出现「根因」等抽象管理术语
alltxt = '\n'.join(p.text for p in d.paragraphs)
for tb in d.tables:
    for r in tb.rows:
        for c in r.cells:
            alltxt += '\n' + c.text
for bad in ('根因', '责任人', '复核人'):
    ck('全文不含「%s」' % bad, bad in alltxt, False)

# 页脚页码域
ft = d.sections[-1].footer.paragraphs[0]._p.xml if d.sections[-1].footer.paragraphs else ''
ck('页脚含 PAGE 域', 'PAGE' in ft, True)

print()
if fails:
    print('断言失败 %d 项：%s' % (len(fails), '、'.join(fails)))
    sys.exit(1)
print('全部断言通过 → %s' % os.path.basename(F))
