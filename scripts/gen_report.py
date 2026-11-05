# -*- coding: utf-8 -*-
"""质检报告渲染引擎：颜色常量、样式、表格构建"""
import docx
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.section import WD_ORIENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

# ---------- 等级配色 ----------
LV = {
    'P0': (RGBColor(0xC0, 0x00, 0x00), 'FCE4E4'),   # 致命
    'P1': (RGBColor(0xE3, 0x6C, 0x09), 'FDF0E4'),   # 严重
    'P2': (RGBColor(0xBF, 0x8F, 0x00), 'FFF9E0'),   # 一般
    'PASS': (RGBColor(0x00, 0x9E, 0x49), 'E8F5EC'),  # 通过
    'INFO': (RGBColor(0x59, 0x59, 0x59), None),    # 原文引用
    'ACT': (RGBColor(0x00, 0x70, 0x30), None),      # 处置建议
}
DIM = {
    'D1': (RGBColor(0x1F, 0x4E, 0x79), 'DDEBF7'),   # 第一重
    'D2': (RGBColor(0x0E, 0x7C, 0x86), 'D9F0F2'),   # 第二重
    'D3': (RGBColor(0x00, 0x70, 0xC0), 'DEEAF6'),   # 第三重
    'D4': (RGBColor(0x70, 0x30, 0xA0), 'EDE3F5'),   # 第四重
}

CN = '微软雅黑'


def _font(run, name=CN):
    run.font.name = name
    rPr = run._element.get_or_add_rPr()
    rf = rPr.find(qn('w:rFonts'))
    if rf is None:
        rf = OxmlElement('w:rFonts')
        rPr.append(rf)
    rf.set(qn('w:eastAsia'), name)
    rf.set(qn('w:ascii'), name)
    rf.set(qn('w:hAnsi'), name)


def shade(cell, hexcolor):
    tcPr = cell._tc.get_or_add_tcPr()
    for old in tcPr.findall(qn('w:shd')):
        tcPr.remove(old)
    shd = OxmlElement('w:shd')
    shd.set(qn('w:val'), 'clear')
    shd.set(qn('w:color'), 'auto')
    shd.set(qn('w:fill'), hexcolor)
    tcPr.append(shd)


def vcenter(cell):
    tcPr = cell._tc.get_or_add_tcPr()
    va = OxmlElement('w:vAlign')
    va.set(qn('w:val'), 'center')
    tcPr.append(va)


def cell_text(cell, text, size=8, bold=False, color=None, fill=None,
              align=None, valign_center=True):
    cell.text = ''
    p = cell.paragraphs[0]
    if align:
        p.alignment = align
    pf = p.paragraph_format
    pf.space_before = Pt(1.5)
    pf.space_after = Pt(1.5)
    pf.line_spacing = 1.05
    lines = str(text).split('\n')
    for i, ln in enumerate(lines):
        if i > 0:
            p = cell.add_paragraph()
            if align:
                p.alignment = align
            pf = p.paragraph_format
            pf.space_before = Pt(0)
            pf.space_after = Pt(1.5)
            pf.line_spacing = 1.05
        r = p.add_run(ln)
        r.font.size = Pt(size)
        r.bold = bold
        if color is not None:
            r.font.color.rgb = color
        _font(r)
    if fill:
        shade(cell, fill)
    if valign_center:
        vcenter(cell)


def repeat_header(row):
    trPr = row._tr.get_or_add_trPr()
    th = OxmlElement('w:tblHeader')
    th.set(qn('w:val'), 'true')
    trPr.append(th)


def set_widths(table, widths_cm):
    table.autofit = False
    for row in table.rows:
        for i, w in enumerate(widths_cm):
            if i < len(row.cells):
                row.cells[i].width = Cm(w)


def mk_table(doc, headers, widths, size=8):
    t = doc.add_table(rows=1, cols=len(headers))
    t.style = 'Table Grid'
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    for i, h in enumerate(headers):
        c = t.rows[0].cells[i]
        cell_text(c, h, size=size, bold=True,
                  color=RGBColor(0xFF, 0xFF, 0xFF), fill='1F4E79',
                  align=WD_ALIGN_PARAGRAPH.CENTER)
    repeat_header(t.rows[0])
    set_widths(t, widths)
    return t


def add_row(table, cells, widths, size=8, level=None, dim=None):
    row = table.add_row()
    fill = None
    color = None
    if level and level in LV:
        color, fill = LV[level]
    elif dim and dim in DIM:
        color, fill = DIM[dim]
    for i, v in enumerate(cells):
        al = WD_ALIGN_PARAGRAPH.CENTER if i == 0 and len(str(v)) <= 6 else None
        cell_text(row.cells[i], v, size=size, color=color, fill=fill, align=al)
    set_widths(table, widths)
    return row


def _rgb(c):
    """接受 str(hex) 或 RGBColor，返回 RGBColor"""
    if c is None:
        return None
    if isinstance(c, RGBColor):
        return c
    c = str(c).lstrip('#')
    return RGBColor(int(c[0:2], 16), int(c[2:4], 16), int(c[4:6], 16))


def H(doc, text, size=15, color='1F4E79', before=14, after=8, level=0):
    p = doc.add_paragraph()
    p.style = doc.styles['Heading %d' % min(level + 1, 4)]
    pf = p.paragraph_format
    pf.space_before = Pt(before)
    pf.space_after = Pt(after)
    r = p.add_run(text)
    r.font.size = Pt(size)
    r.bold = True
    r.font.color.rgb = _rgb(color)
    _font(r)
    return p


def P(doc, text, size=9, bold=False, color=None, before=2, after=4,
      indent=0, align=None):
    p = doc.add_paragraph()
    if align:
        p.alignment = align
    pf = p.paragraph_format
    pf.space_before = Pt(before)
    pf.space_after = Pt(after)
    pf.line_spacing = 1.25
    if indent:
        pf.left_indent = Cm(indent)
    r = p.add_run(text)
    r.font.size = Pt(size)
    r.bold = bold
    if color is not None:
        r.font.color.rgb = _rgb(color)
    _font(r)
    return p


def Q(doc, label, text, kind='INFO', size=9, color=None):
    """带标签的引用/建议块"""
    p = doc.add_paragraph()
    pf = p.paragraph_format
    pf.space_before = Pt(2)
    pf.space_after = Pt(3)
    pf.line_spacing = 1.25
    pf.left_indent = Cm(0.6)
    r1 = p.add_run(label)
    r1.font.size = Pt(size)
    r1.bold = True
    r1.font.color.rgb = LV[kind][0]
    _font(r1)
    r2 = p.add_run(text)
    r2.font.size = Pt(size)
    r2.font.color.rgb = _rgb(color) if color is not None else (
        LV[kind][0] if kind in ('INFO', 'ACT') else None)
    _font(r2)
    return p


def add_footer_pagenum(section):
    p = section.footer.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run('第 ')
    r.font.size = Pt(8)
    _font(r)
    for instr in ('PAGE',):
        fld = OxmlElement('w:fldSimple')
        fld.set(qn('w:instr'), instr)
        p._p.append(fld)
    r2 = p.add_run(' 页  共 ')
    r2.font.size = Pt(8)
    _font(r2)
    fld2 = OxmlElement('w:fldSimple')
    fld2.set(qn('w:instr'), 'NUMPAGES')
    p._p.append(fld2)
    r3 = p.add_run(' 页')
    r3.font.size = Pt(8)
    _font(r3)


def landscape(section):
    w, h = section.page_width, section.page_height
    section.orientation = WD_ORIENT.LANDSCAPE
    section.page_width, section.page_height = h, w


def portrait(section):
    w, h = section.page_width, section.page_height
    section.orientation = WD_ORIENT.PORTRAIT
    if w > h:
        section.page_width, section.page_height = h, w