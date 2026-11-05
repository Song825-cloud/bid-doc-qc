# -*- coding: utf-8 -*-
"""路径解析模块：让同一套脚本既能跑在项目里，也能被打包成 skill 复用。

解析优先级：
  1. 环境变量 BID_QC_ROOT（由 run.py 统一注入，最可靠）
  2. 脚本所在目录的上一级 / 上两级（项目内安装时 <项目>/qc/xxx.py）
  3. 当前工作目录（skill 安装后由调用方在项目根目录执行）

约定目录结构：
  <项目根>/
    ├─ 招标文件/     招标 PDF
    ├─ 投标文件/     受检 docx + 交付的报告 docx
    ├─ output/       交付说明
    └─ qc/           本流程的脚本与中间数据（parsed/ 放 PDF 解析文本）
"""
import glob
import os


def _looks_like_root(p):
    if not p or not os.path.isdir(p):
        return False
    for sub in ('招标文件', '投标文件', 'qc'):
        if os.path.isdir(os.path.join(p, sub)):
            return True
    return False


def root():
    """项目根目录"""
    env = os.environ.get('BID_QC_ROOT')
    if env and os.path.isdir(env):
        return os.path.abspath(env)
    here = os.path.dirname(os.path.abspath(__file__))
    for cand in (os.path.abspath(os.path.join(here, '..')),
                 os.path.abspath(os.path.join(here, '..', '..')),
                 os.getcwd()):
        if _looks_like_root(cand):
            return cand
    return os.getcwd()


def qc():
    return os.path.join(root(), 'qc')


def bid_dir():
    return os.path.join(root(), '投标文件')


def tender_dir():
    return os.path.join(root(), '招标文件')


def out_dir():
    return os.path.join(root(), 'output')


def parsed_dir():
    return os.path.join(qc(), 'parsed')


def find_bid_docx():
    """在 投标文件/ 下找受检技术文件：取体积最大的 .docx，
    排除本流程产出的质检报告（文件名含「质检报告」或「问题清单」）。"""
    cands = []
    for p in glob.glob(os.path.join(bid_dir(), '*.docx')):
        b = os.path.basename(p)
        if '质检报告' in b or '问题清单' in b:
            continue
        cands.append((os.path.getsize(p), p))
    if not cands:
        raise FileNotFoundError(
            '投标文件/ 下未找到受检 docx（已排除质检报告类文件）')
    cands.sort(reverse=True)
    return cands[0][1]


def find_tender_txts():
    """在 qc/parsed/ 下按文件名关键词识别三类 PDF 解析文本。
    返回 {类型: 路径}，类型为 正文 / 答疑 / 图纸。"""
    pd = parsed_dir()
    found = {}
    if not os.path.isdir(pd):
        return found
    for p in sorted(glob.glob(os.path.join(pd, '*.txt'))):
        b = os.path.basename(p)
        if '正文' in b:
            found.setdefault('正文', p)
        elif '答疑' in b or '澄清' in b:
            found.setdefault('答疑', p)
        elif '施工图' in b or '图纸' in b:
            found.setdefault('图纸', p)
    return found


if __name__ == '__main__':
    print('项目根 :', root())
    print('qc     :', qc())
    print('受检文件:', find_bid_docx())
    print('PDF 文本:', {k: os.path.basename(v)
                        for k, v in find_tender_txts().items()})
