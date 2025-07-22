# app/utils.py

import fitz  # PyMuPDF

def load_and_parse_file(filepath):
    """讀取 PDF 檔案的全文文字"""
    doc = fitz.open(filepath)
    full_text = "\n".join([page.get_text() for page in doc])
    doc.close()
    return full_text

def get_page_number_for_chunk(filepath, chunk_text):
    """比對 chunk 對應的原始頁碼"""
    doc = fitz.open(filepath)
    for i, page in enumerate(doc):
        if chunk_text[:50] in page.get_text():
            return i + 1  # PDF 頁碼從 1 開始
    return "?"  # 無法找到對應頁碼
