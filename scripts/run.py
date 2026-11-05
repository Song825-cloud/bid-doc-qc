# -*- coding: utf-8 -*-
"""唯一入口：投标技术文件质检流程。

用法：
  python qc/run.py                # 快速：重建问题清单版报告 + 回归断言（约 10 秒）
  python qc/run.py --locate       # 重跑页码定位（约 5 分钟）后重建
  python qc/run.py --all          # 全流程：解析 → 扫描 → 定位 → 重建 → 断言（约 20 分钟）
  python qc/run.py --full-report  # 额外生成完整版（取证底册）

阶段划分见 README.md。任一阶段失败即中止并返回非 0。
"""
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
PY = sys.executable

# 统一注入项目根目录，子进程全部通过 _paths.root() 解析
sys.path.insert(0, HERE)
import _paths
ROOT = _paths.root()
os.environ['BID_QC_ROOT'] = ROOT
ENV = dict(os.environ)
print('项目根目录：%s' % ROOT)

STAGES_FAST = [
    ('阶段4 渲染问题清单版', ['build_slim.py']),
    ('阶段5 回归断言', ['check_slim.py']),
]
STAGES_LOCATE = [
    ('阶段3a 招标文件页码', ['tender_pages2.py']),
    ('阶段3b 投标文件页码', ['bid_pages_all.py']),
]
STAGES_ALL = [
    ('阶段1 解析技术文件', ['parse_bid.py']),
    ('阶段2a 扫描 第一重/第四重', ['scan_a_typo.py']),
    ('阶段2b 扫描 B组 工期', ['scan_b.py']),
    ('阶段2c 扫描 C/D/E组', ['scan_cde.py']),
    ('阶段2d 扫描 G组 范围串用', ['scan_g.py']),
    ('阶段2e 扫描 F组 规范', ['scan_f2.py']),
    ('阶段2f 扫描 答疑澄清落实', ['scan_clarify.py']),
    ('阶段2g 扫描 三项专项', ['scan_spot.py']),
] + STAGES_LOCATE + STAGES_FAST + [
    ('附加 完整版（取证底册）', ['build_report.py', 'build_report2.py', 'publish.py']),
]

ARG = sys.argv[1] if len(sys.argv) > 1 else ''
if ARG == '--all':
    PLAN = STAGES_ALL
elif ARG == '--locate':
    PLAN = STAGES_LOCATE + STAGES_FAST
elif ARG == '--full-report':
    PLAN = STAGES_FAST + [('附加 完整版（取证底册）',
                           ['build_report.py', 'build_report2.py', 'publish.py'])]
else:
    PLAN = STAGES_FAST

T0 = time.time()
print('=' * 68)
print('投标技术文件质检流程   模式：%s' % (ARG or '快速（重建+断言）'))
print('=' * 68)

for name, scripts in PLAN:
    print('\n>>> %s' % name, flush=True)
    for sc in scripts:
        path = os.path.join(HERE, sc)
        if not os.path.exists(path):
            print('  [跳过] 找不到 %s' % sc)
            continue
        r = subprocess.run([PY, path], cwd=HERE, env=ENV)
        if r.returncode != 0:
            print('\n!!! 阶段失败：%s（%s 退出码 %d）' % (name, sc, r.returncode))
            sys.exit(r.returncode)
    print('<<< %s 完成  [%.1fs]' % (name, time.time() - T0), flush=True)

print('\n' + '=' * 68)
print('全流程完成，总耗时 %.1f 秒' % (time.time() - T0))
print('交付物：../投标文件/技术文件质检报告（问题清单版）YYYYMMDD.docx')
print('=' * 68)
