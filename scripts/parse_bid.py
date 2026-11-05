# -*- coding: utf-8 -*-
"""将技术文件docx 按文档流顺序解析为带章节路径的结构化文本"""
import docx, sys, os, json
from docx.table import Table
from docx.text.paragraph import Paragraph

sys.stdout.reconfigure(encoding='utf-8')

import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _paths
SRC = _paths.find_bid_docx()
OUT_TXT = 'bid_struct.txt'
OUT_JSON = 'bid_struct.json'

doc = docx.Document(SRC)
body = doc.element.body

lines = []          # 结构化文本行
records = []        # 结构化记录
stack = []          # 标题栈
tbl_i = 0
para_i = 0

from docx.oxml.ns import qn

# 该文档样式ID已被混淆，改用 styles.xml 中的 name 与 outlineLvl 建立映射
SID2LVL = {}
def build_map(doc):
    for s in doc.part.styles.element:
        if not s.tag.endswith('}style'):
            continue
        if s.get(qn('w:type')) != 'paragraph':
            continue
        sid = s.get(qn('w:styleId'))
        nm_el = s.find(qn('w:name'))
        nm = (nm_el.get(qn('w:val')) or '') if nm_el is not None else ''
        if nm.lower().replace(' ', '').startswith('heading'):
            pPr = s.find(qn('w:pPr'))
            lvl = None
            if pPr is not None:
                o = pPr.find(qn('w:outlineLvl'))
                if o is not None:
                    lvl = int(o.get(qn('w:val')))
            if lvl is not None and lvl <= 8:
                SID2LVL[sid] = lvl + 1

def para_style_id(p_el):
    pPr = p_el.find(qn('w:pPr'))
    if pPr is None:
        return 'Normal'
    st = pPr.find(qn('w:pStyle'))
    if st is None:
        return 'Normal'
    return st.get(qn('w:val')) or 'Normal'

def iter_block_items(parent):
    for child in parent.iterchildren():
        if child.tag.endswith('}p'):
            yield Paragraph(child, parent)
        elif child.tag.endswith('}tbl'):
            yield Table(child, parent)


build_map(doc)

for block in iter_block_items(body):
    if isinstance(block, Paragraph):
        para_i += 1
        txt = block.text.strip()
        sid = para_style_id(block._p)
        lvl = SID2LVL.get(sid)
        m = lvl is not None
        if m:
            if lvl > 6:
                lvl = 6   # heading7~9 归为图表标题层级
            while stack and stack[-1][0] >= lvl:
                stack.pop()
            stack.append((lvl, txt))
            path = ' > '.join(s[1] for s in stack if s[1])
            lines.append('[H%d][%s] %s' % (lvl, path, txt))
            records.append({'t': 'h', 'lvl': lvl, 'text': txt, 'path': path, 'idx': para_i})
        else:
            path = ' > '.join(s[1] for s in stack if s[1])
            if txt:
                lines.append('[P][%s] %s' % (path, txt))
                records.append({'t': 'p', 'text': txt, 'path': path, 'idx': para_i})
    else:
        tbl_i += 1
        path = ' > '.join(s[1] for s in stack if s[1])
        lines.append('[TABLE %d][%s] ----' % (tbl_i, path))
        records.append({'t': 'table_start', 'tbl': tbl_i, 'path': path})
        for ri, row in enumerate(block.rows):
            cells = []
            try:
                for c in row.cells:
                    cells.append(c.text.replace('\n', ' ').strip())
            except Exception as e:
                cells = ['<读取失败>']
            line = ' | '.join(cells)
            lines.append('  R%d: %s' % (ri, line))
            records.append({'t': 'tr', 'tbl': tbl_i, 'row': ri, 'text': line, 'path': path})
        lines.append('[/TABLE %d] ----' % tbl_i)
        records.append({'t': 'table_end', 'tbl': tbl_i, 'path': path})

open(OUT_TXT, 'w', encoding='utf-8').write('\n'.join(lines))
json.dump(records, open(OUT_JSON, 'w', encoding='utf-8'), ensure_ascii=False)
print('段落流', para_i, '表格', tbl_i, '记录', len(records))
print('文本字节', os.path.getsize(OUT_TXT))