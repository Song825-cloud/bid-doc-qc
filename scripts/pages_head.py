"""打印 docx 前 N 页的页码与每页首个段落。

用途：实测文档有没有封面/目录页，确定 toc_end 阈值。
     换新项目时必须先跑这个脚本确认正文起点，再写 toc.json。

用法：
    python pages_head.py <docx路径> [页数]
    python pages_head.py "D:/bid/技术文件.docx" 40

依赖：Windows + Microsoft Word + pywin32
输出：每行 = 页码<TAB>该页首个段落（截断 60 字）
"""
import sys


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    docx = sys.argv[1]
    n_pages = int(sys.argv[2]) if len(sys.argv) > 2 else 40

    import win32com.client
    word = win32com.client.DispatchEx('Word.Application')
    word.Visible = False
    word.Options.Pagination = True
    try:
        doc = word.Documents.Open(docx, ReadOnly=True)
        doc.Repaginate()
        seen = set()
        for para in doc.Paragraphs:
            pg = para.Range.Information(3)  # wdActiveEndPageNumber
            if pg > n_pages:
                break
            if pg in seen:
                continue
            seen.add(pg)
            text = para.Range.Text.strip().replace('\r', '').replace('\x07', '')
            if text:
                print(f'P{pg}\t{text[:60]}')
        doc.Close(False)
    finally:
        word.Quit()


if __name__ == '__main__':
    main()
