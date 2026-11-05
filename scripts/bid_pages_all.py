# -*- coding: utf-8 -*-
"""合并重采集：一次性打开文档，重跑 bid_pages2.json 与 bid_pages3.json 的全部项。
关键修正：文档无封面/目录页（P1 即第1章首页），因此**不做页码过滤**，
         原 `pg > 20` 会丢弃第1章正文页码（P3—P20），已去除。
同时为若干项补充更易命中的短关键词。"""
import io
import json
import os
import time
import traceback

import win32com.client as win32

import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _paths
BASE = _paths.root()
QC = _paths.qc()
DOC = _paths.find_bid_docx()
# ---- 第三重 A—G / 第四重（原 bid_pages2） ----
# 按项目填写检索关键词：键名与报告编号对应，每个键给 2—4 个候选词（从短到长）
# 示例：'A-1': ['示例关键词1', '示例关键词2']
Q2 = {}

# ---- 三项专项核查 H/E/Q（原 bid_pages3） ----
# 键名 H-1…Q-8 与专项核查编号对应
Q3 = {}


def log(*a):
    print('[%6.1fs]' % (time.time() - T0), *a, flush=True)


def collect(doc, kws, maxn=15, guard_max=500):
    for kw in kws:
        rng = doc.Content
        pages = []
        f = rng.Find
        f.ClearFormatting()
        f.Text = kw
        f.Forward = True
        f.Wrap = 0
        f.MatchCase = False
        f.MatchWholeWord = False
        guard = 0
        while len(pages) < maxn and guard <= guard_max:
            guard += 1
            try:
                if not f.Execute():
                    break
            except Exception:
                break
            try:
                pg = int(rng.Information(3))
            except Exception:
                break
            if pg >= 1:
                pages.append(pg)
            if rng.End >= doc.Content.End:
                break
        if pages:
            return {'pages': pages, 'used': kw, 'total_hits': len(pages)}
    return {'pages': [], 'used': None, 'total_hits': 0}


T0 = time.time()
app = None
try:
    app = win32.DispatchEx('Word.Application')
    app.Visible = False
    app.DisplayAlerts = 0
    for k, v in dict(Pagination=True, CheckSpellingAsYouType=False,
                     CheckGrammarAsYouType=False, BackgroundSave=False).items():
        try:
            setattr(app.Options, k, v)
        except Exception:
            pass
    log('Open 193MB...')
    doc = app.Documents.Open(DOC, ReadOnly=True, AddToRecentFiles=False,
                             Visible=False, ConfirmConversions=False)
    doc.Repaginate()
    total = int(doc.ComputeStatistics(2))
    log('总页数 =', total)

    log('--- 第三重/第四重 (31 项) ---')
    res2 = {}
    for key, kws in Q2.items():
        rec = collect(doc, kws)
        res2[key] = rec
        log('  %-5s %-16s hits=%-3d %s' % (key, (rec['used'] or '')[:14],
                                           rec['total_hits'], rec['pages'][:8]))
    with io.open(os.path.join(QC, 'bid_pages2.json'), 'w',
                 encoding='utf-8') as fp:
        fp.write(json.dumps({'total_pages': total, 'items': res2},
                            ensure_ascii=False, indent=2))

    log('--- 专项 H/E/Q (24 项) ---')
    res3 = {}
    for key, kws in Q3.items():
        rec = collect(doc, kws)
        # 保留旧的补跑结果（若有）作为兜底
        res3[key] = rec
        log('  %-5s %-24s hits=%-3d %s' % (key, (rec['used'] or '')[:22],
                                           rec['total_hits'], rec['pages'][:8]))
    old = os.path.join(QC, 'bid_pages3.json')
    zero = {}
    if os.path.exists(old):
        with io.open(old, encoding='utf-8') as fh:
            zero = json.load(fh).get('zero_check', {})
    with io.open(old, 'w', encoding='utf-8') as fp:
        fp.write(json.dumps({'total_pages': total, 'items': res3,
                             'zero_check': zero}, ensure_ascii=False, indent=2))

    log('完成')
except Exception as e:
    log('失败:', e)
    log(traceback.format_exc()[-1500:])
finally:
    if app is not None:
        try:
            app.Quit()
        except Exception:
            pass
log('结束')