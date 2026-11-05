# -*- coding: utf-8 -*-
"""问题清单版质检报告 —— 单入口渲染。

设计原则（针对「错误不多但资料很多、内容重复」的反馈）：
  1. 一问题一记：23 个问题只出现一次，全部出现位置并入同一行；
  2. 删除 2.5 速览表（与整改清单重复约 90%）；
  3. 「已核查且合规 / 待补充材料」全部下沉附录，正文只放需要动手的事；
  4. 问题描述用正常查找口径书写，不用「根因」等抽象表述；
  5. 问题清单不列责任人 / 完成时限 / 状态 / 复核人（用户明确不需要）。
输出：../投标文件/技术文件质检报告（问题清单版）YYYYMMDD.docx
"""
import os
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _paths
_QC = _paths.qc()
if os.path.isdir(_QC):
    sys.path.insert(0, _QC)   # 项目级结论数据优先于 skill 内置副本
sys.stdout.reconfigure(encoding='utf-8')

import docx
from docx.shared import Pt, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.section import WD_SECTION, WD_ORIENT

from gen_report import (LV, DIM, H, P, Q, mk_table, add_row,
                        add_footer_pagenum, landscape, portrait)
from data_s1 import SEC2, TITLE, TENDER_NO
from data_rc import build_rc, PASS_ROWS, INFO_ROWS, SEC2_TO_RC
import page_map as PM

HERE = os.path.dirname(os.path.abspath(__file__))
_BID = _paths.bid_dir()
TMP = os.path.join(_BID, '_问题清单_tmp.docx')
FIN = os.path.join(
    _BID, '技术文件质检报告（问题清单版）YYYYMMDD.docx')

doc = docx.Document()
sec = doc.sections[0]
portrait(sec)
sec.page_width, sec.page_height = Cm(21.0), Cm(29.7)
sec.left_margin = sec.right_margin = Cm(1.6)
sec.top_margin = sec.bottom_margin = Cm(1.8)
add_footer_pagenum(sec)

st = doc.styles['Normal']
st.font.name = '微软雅黑'
st.font.size = Pt(9)

# ===================== 封面 =====================
P(doc, '', before=40, after=0)
P(doc, '投标技术文件 质检报告', size=24, bold=True, color='C00000',
  align=WD_ALIGN_PARAGRAPH.CENTER, before=10, after=6)
P(doc, TITLE, size=13, bold=True, color='1F4E79',
  align=WD_ALIGN_PARAGRAPH.CENTER, before=0, after=2)
P(doc, '问题清单版：正文只列 23 个需整改问题', size=12, bold=True, color='C00000',
  align=WD_ALIGN_PARAGRAPH.CENTER, before=0, after=4)
P(doc, '招标编号：%s' % TENDER_NO, size=10, color='595959',
  align=WD_ALIGN_PARAGRAPH.CENTER, before=0, after=30)

RC_ROWS = build_rc()
n0 = sum(1 for r in RC_ROWS if r[2] == 'P0')
n1 = sum(1 for r in RC_ROWS if r[2] == 'P1')
n2 = sum(1 for r in RC_ROWS if r[2] == 'P2')

P(doc, '一页看懂：这份文件只需要你改 %d 件事' % len(RC_ROWS), size=13, bold=True,
  color='1F4E79', align=WD_ALIGN_PARAGRAPH.CENTER, before=0, after=8)
for t_ in [
    '经四重质检 + 三项专项核查，共执行 84 个检查项；'
    '按问题归并后，**真正需要整改的只有 %d 个问题**。' % len(RC_ROWS),
    '其中 致命（P0）%d 项、严重（P1）%d 项、一般（P2）%d 项。' % (n0, n1, n2),
    '另有 %d 项经核查确认无问题（附录一）、%d 项待你补充材料（附录二），均不占正文。'
    % (len(PASS_ROWS), len(INFO_ROWS)),
    '每个问题都给出：出现位置（投标文件页码，可直接翻页）· 招标依据页码 · 处理建议。',
]:
    P(doc, '· ' + t_, size=10, indent=0.5, before=2, after=2)

P(doc, '', before=26)
P(doc, '编制：（示例模板，作者信息已移除）', size=10, bold=True, color='007030',
  align=WD_ALIGN_PARAGRAPH.CENTER, before=0, after=2)
P(doc, '报告日期：YYYY年MM月DD日    依据版本：按项目实际版本',
  size=10, color='007030', align=WD_ALIGN_PARAGRAPH.CENTER, before=0, after=2)

# ---- 横向节 ----
sec2 = doc.add_section(WD_SECTION.NEW_PAGE)
landscape(sec2)
sec2.page_width, sec2.page_height = Cm(29.7), Cm(21.0)
sec2.left_margin = sec2.right_margin = Cm(1.5)
sec2.top_margin = sec2.bottom_margin = Cm(1.6)
sec2.footer.is_linked_to_previous = False
add_footer_pagenum(sec2)

# ===================== 一、等级与统计 =====================
H(doc, '一、等级图例与统计', size=16, before=0)
t = mk_table(doc, ['等级', '含义', '处置时限', '本次问题数'],
             [2.2, 11.6, 5.4, 3.0], size=9)
for lv, name, mean, dl in [
    ('P0', '致命', '可能造成否决投标，或评委一眼可见、必然扣分', '投标截止前必须改完'),
    ('P1', '严重', '影响评分点判定，或造成「前后不一致」的扣分判断', '投标截止前改完'),
    ('P2', '一般', '规范性、格式性问题，不影响实质评审', '建议改完'),
]:
    n = {'P0': n0, 'P1': n1, 'P2': n2}[lv]
    add_row(t, ['%s %s' % (lv, name), mean, dl, str(n)],
            [2.2, 11.6, 5.4, 3.0], level=lv)
add_row(t, ['通过', '经核查符合招标文件要求，无需修改', '—', '%d（附录一）' % len(PASS_ROWS)],
        [2.2, 11.6, 5.4, 3.0], level='PASS')
add_row(t, ['待核验', '需你补充其他投标文件或事实依据后才能判定', '—', '%d（附录二）' % len(INFO_ROWS)],
        [2.2, 11.6, 5.4, 3.0], level='INFO')
add_row(t, ['合计', '需整改问题 = P0 + P1 + P2', '—', str(len(RC_ROWS))],
        [2.2, 11.6, 5.4, 3.0])

P(doc, '统计规则：**一个问题只出现一次**。同一个问题（如同一表述多处出现）'
       '合并为 1 条，其全部出现位置并入该行的「出现位置」列；'
       '原检查项号保留在「原条目」列，既好改、又可查全。'
       '「通过」与「待核验」不计入问题数。',
  size=8.5, color=LV['INFO'][0], before=6)

# ===================== 二、问题清单 =====================
doc.add_page_break()
H(doc, '二、问题清单（共 %d 项）' % len(RC_ROWS), size=16, before=0)
P(doc, '本表按正常查找口径逐条列出：每条给出问题描述、出现位置（可直接翻页）、'
       '招标依据与处理建议。建议在投标截止前完成全部 P0 与 P1。',
  size=9, color=LV['INFO'][0])

W = [0.9, 7.2, 0.9, 2.4, 3.2, 2.8, 9.3]
t = mk_table(doc, ['编号', '问题', '等级', '原条目', '出现位置（投标页码）',
                   '招标依据页码', '处理建议'],
             W, size=8)
for no, item, lv, src, pages, ten, act in RC_ROWS:
    add_row(t, [no, item, lv, src, pages, ten, act],
            W, size=7.5, level=lv)

# ===================== 三、关键招标基准 =====================
doc.add_page_break()
H(doc, '三、关键招标基准（全文核查的锚点）', size=16, before=0)
P(doc, '下列 8 项为本次全部核查的招标文件依据页。技术文件凡与下表不一致，即构成缺陷。',
  size=9, color=LV['INFO'][0])

W3 = [4.6, 3.0, 11.0, 8.1]
t = mk_table(doc, ['依据项', '招标文件页码', '内容要点', '对技术文件的要求'], W3, size=8)
BASE = [
    ('里程碑项目关键节点表', '正文 Pxx',
     '开工、各关键节点、首台机组发电等里程碑日期（按项目填写）',
     '技术文件里程碑表须逐项一致，进度计划不得晚于节点'),
    ('招标范围界定', '正文 Pxx',
     '本标段工程范围与不含内容（按项目填写）',
     '凡超出本标段范围的内容均属标段外表述，须删除'),
    ('施工组织设计评分标准', '正文 Pxx',
     '评分分值、评分要素与评分点（按项目填写）',
     '资源配置须附计算说明；进度计划须有关键线路与历时计算'),
    ('BIM 技术应用评分点', '正文 Pxx',
     'BIM 技术应用是否必答及分值（按项目填写）',
     '须有 BIM 组织、人员、软硬件与实施计划的完整响应'),
    ('临时用电与充电设施', '正文 Pxx',
     '发包人提供的供电容量、充电设施建设责任（按项目填写）',
     '充电设施须按招标要求落实，并复核同时充电容量是否超限'),
    ('工程量清单', '正文 Pxx',
     '清单册是否单独印制、数值出处（按项目填写）',
     '清单逐项比对须以清单册为准'),
    ('图纸与清单不一致的处理', '正文 Pxx',
     '不一致时的优先顺序（按项目填写）',
     '投标报价与施工组织设计中的工程量口径须与清单一致'),
    ('答疑澄清关键条款', '答疑 Pxx',
     '答疑对节点、断面等关键参数的修改（按项目填写）',
     '技术文件中已作废的旧表述须全文替换'),
]
for a, b, c, d in BASE:
    add_row(t, [a, b, c, d], W3, size=7.5)

# ===================== 四、评分点响应与失分风险 =====================
doc.add_page_break()
H(doc, '四、技术评分点响应与失分风险（20 分 / 8 要素）', size=16, before=0)
P(doc, '评分依据：评标办法前附表 2.2.4（1）施工组织设计。'
       '下表逐要素给出响应概况、页码与失分风险。', size=9, color=LV['INFO'][0])

W4 = [1.0, 2.6, 1.1, 4.6, 2.9, 5.0, 2.4, 2.3, 1.1, 3.7]
t = mk_table(doc, ['序', '评分要素', '分值', '招标文件评分标准要点', '对应章节',
                   '响应概况与失分风险', '投标文件页码', '招标文件页码', '等级', '对应问题编号'],
             W4, size=8)
for no, item, score, std, chap, resp, lv, risk in SEC2:
    add_row(t, [no, item, score, std, chap, resp + '\n【失分风险】' + risk,
                PM.bid(no), PM.ten(no), lv,
                SEC2_TO_RC.get(no, '—')],
            W4, size=7.5, level=lv)

# ===================== 五、专项核查关键取证 =====================
doc.add_page_break()
H(doc, '五、专项核查关键取证（工期 / 设备 / 工程量）', size=16, before=0)
P(doc, '按你的专项要求，对 ①工期前后矛盾 ②设备配备与部位匹配 ③工程量一致性 做了深度核查。'
       '以下 8 项为本轮最关键取证（含原文数值与页码），其余见问题清单。',
  size=9, color=LV['INFO'][0])

from data_s4 import H_ROWS, E_ROWS, Q_ROWS
_ALL = {r[0]: r for r in H_ROWS + E_ROWS + Q_ROWS}
KEY = ['H-2', 'H-4', 'H-6', 'Q-1', 'Q-2', 'Q-3', 'E-1', 'Q-8']

W5 = [1.1, 4.0, 3.6, 9.6, 2.6, 2.3, 3.5]
t = mk_table(doc, ['编号', '取证项', '招标基准', '技术文件原文数值（多口径并列）',
                   '投标页码', '招标页码', '结论'], W5, size=8)
for k in KEY:
    no, item, base, now, lv, act = _ALL[k]
    add_row(t, [no, item, base, now, PM.bid_spot(no), PM.ten_spot(no), lv],
            W5, size=7.5, level=lv)

P(doc, '⚠️ 招标文件《工程量清单》为单独印制册（正文 Pxx 明载「另册」），'
       '清单数值不在可获取范围内，故「清单 vs 投标文件」逐项比对尚未完成。'
       '本轮 Q 组结论均基于技术文件**内部**自洽性；若能提供清单册，可另作一次逐项比对。',
  size=8.5, color=LV['INFO'][0], before=6)

# ===================== 六、报送前形式要件自查 =====================
doc.add_page_break()
H(doc, '六、报送前形式要件自查（最后一道关）', size=16, before=0)
P(doc, '以下为投标文件**整体**的形式要件，超出技术文件范围，但属否决高风险项，'
       '建议装订密封前逐项打勾。依据：正文 Pxx—Pxx（3.5.1 / 3.7.1 投标文件格式要求）、'
       'Pxx—Pxx（第八章投标文件格式引用说明）。', size=9, color=LV['INFO'][0])

W6 = [1.0, 5.0, 12.0, 3.4, 5.3]
t = mk_table(doc, ['序', '形式要件', '自查要点', '依据页码', '状态'], W6, size=8)
FORM = [
    ('投标函及投标函附录', '项目名称、招标编号、投标报价、工期承诺与招标文件完全一致；'
     '按第八章格式填写', '正文 Pxx、Pxx'),
    ('投标保证金', '金额、形式、有效期符合投标人须知；保函或汇付凭证齐全', '正文 Pxx'),
    ('签字与盖章', '凡要求「盖单位章」处使用 CA 数字证书加盖电子章；'
     '法定代表人或授权委托人签字齐全', '正文 Pxx'),
    ('授权委托书', '授权范围、期限明确；附法定代表人及被授权人身份证明', '正文 Pxx'),
    ('资格审查表', '按第八章规定表格内容填写，不得增删行列', '正文 Pxx'),
    ('施工组织设计', '含目录、页码完整、无空页错页；插图清晰可辨', '正文 Pxx'),
    ('附图附表', '施工总平面图、进度网络图、临时用地表等图签图号比例齐全并加盖出图章',
     '正文 Pxx2'),
    ('联合体文件', '联合体协议书及成员分工（如为联合体投标）；各方资质与业绩证明',
     '正文 Pxx'),
    ('已标价工程量清单', '报价唯一、与清单册口径一致；安全文明施工费按非竞争性费用填报',
     '正文 Pxx、Pxx'),
    ('份数装订与密封', '正本 / 副本 / 电子版份数、装订方式、内外封套标识与密封符合须知',
     '正文 Pxx—Pxx'),
]
for i, (a, b, c) in enumerate(FORM, 1):
    add_row(t, [str(i), a, b, c, '待核验'], W6, size=7.5, level='INFO')

# ===================== 附录 =====================
doc.add_page_break()
H(doc, '附录一  已核查且合规（%d 项，不占正文）' % len(PASS_ROWS), size=16, before=0)
P(doc, '下列事项**已经核查且未发现问题**，列出是为了说明「查过了、是合规的」，'
       '避免下次复核时重复怀疑。无需整改。', size=9, color=LV['INFO'][0])

WA = [2.6, 12.0, 6.0, 6.1]
t = mk_table(doc, ['原条目', '核查项', '投标文件页码', '招标文件页码'], WA, size=8)
for no, item, bp, tp in PASS_ROWS:
    add_row(t, [no, item, bp or '—', tp or '—'], WA, size=7.5, level='PASS')

doc.add_page_break()
H(doc, '附录二  待你补充材料（%d 项）' % len(INFO_ROWS), size=16, before=0)
P(doc, '下列事项因受检文件范围所限无法判定，需你提供对应资料后才能下结论，'
       '**不计入缺陷统计**。', size=9, color=LV['INFO'][0])

WB = [2.6, 12.0, 6.0, 6.1]
t = mk_table(doc, ['原条目', '待核验事项', '投标文件页码', '招标文件页码'], WB, size=8)
for no, item, bp, tp in INFO_ROWS:
    add_row(t, [no, item, bp or '—', tp or '—'], WB, size=7.5, level='INFO')

doc.add_page_break()
H(doc, '附录三  页码定位方法与口径', size=16, before=0)
for t_ in [
    '**投标文件页码**：受检技术文件经 Word 重新分页后取绝对页序，可直接翻页核对；'
    '总页数以本报告出具时的排版状态为准。',
    '**招标文件页码**：招标文件正文、答疑澄清、施工图分别解析后按页定位，'
    '标注为「正文 Pxxx」「答疑 Pxx」，均已注明来源文件。',
    '**取页方式**：用 Microsoft Word 打开 docx 并重新分页后，逐项定位原文取页码；'
    '对含数字的长句改用逐段遍历定位。页码用于快速翻页，最终以文件原件为准。',
    '**可追溯性**：问题清单的「原条目」列保留了它在完整版报告中的编号，'
    '需要看完整取证过程时可对照完整版报告（按需生成）。',
    '**局限**：docx 无固定分页，若调整字体、页边距或插图，页码会整体漂移，'
    '请以本报告出具时的排版状态为准；图片内嵌内容未做文本核验，'
    '涉及图纸内容的判断均以「建议确认」方式提出。',
    '**输入版本**：以项目实际提供的技术文件与招标文件版本为准。',
]:
    P(doc, '· ' + t_, size=8.5, indent=0.5, before=2, after=2, color=LV['INFO'][0])

P(doc, '', before=10)
P(doc, '— 报告结束 —', size=10, color='595959',
  align=WD_ALIGN_PARAGRAPH.CENTER, before=10, after=2)
P(doc, '编制：（示例模板，作者信息已移除）    报告日期：YYYY年MM月DD日',
  size=9, color='007030', align=WD_ALIGN_PARAGRAPH.CENTER, before=0, after=2)

doc.save(TMP)
print('OK ->', TMP)
print('段落', len(doc.paragraphs), '表格', len(doc.tables))

for target in (FIN,):
    try:
        shutil.copy2(TMP, target)
        os.remove(TMP)
        print('已输出 ->', target)
        print('尺寸 %.1f KB' % (os.path.getsize(target) / 1024.0))
        break
    except PermissionError:
        print('被占用：', os.path.basename(target))
else:
    print('保留临时文件：', TMP)
