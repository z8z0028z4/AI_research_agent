# app/utils.py

import fitz  # PyMuPDF
import os

def load_and_parse_file(filepath):
    """讀取 PDF 檔案的全文文字"""
    try:
        doc = fitz.open(filepath)
        full_text = "\n".join([page.get_text() for page in doc])
        doc.close()
        return full_text
    except Exception as e:
        print(f"❌ 讀取文件失敗 {filepath}: {e}")
        raise

def get_page_number_for_chunk(filepath, chunk_text):
    """比對 chunk 對應的原始頁碼"""
    try:
        # 將相對路徑轉換為絕對路徑
        if not os.path.isabs(filepath):
            current_dir = os.getcwd()
            if os.path.basename(current_dir) == "backend":
                # 如果在 backend 目錄，向上兩級到項目根目錄
                project_root = os.path.dirname(os.path.dirname(current_dir))
                if os.path.basename(project_root) == "AI_research_agent":
                    absolute_path = os.path.join(project_root, filepath)
                else:
                    # 如果不在正確的項目結構中，嘗試其他方法
                    parent_dir = os.path.dirname(current_dir)
                    if os.path.exists(os.path.join(parent_dir, "experiment_data")):
                        absolute_path = os.path.join(parent_dir, filepath)
                    else:
                        absolute_path = os.path.abspath(filepath)
            else:
                absolute_path = os.path.abspath(filepath)
        else:
            absolute_path = filepath
        
        # 檢查文件是否存在
        if not os.path.exists(absolute_path):
            print(f"❌ 文件不存在: {absolute_path}")
            return "?"
        
        doc = fitz.open(absolute_path)
        for i, page in enumerate(doc):
            if chunk_text[:50] in page.get_text():
                doc.close()
                return i + 1  # PDF 頁碼從 1 開始
        doc.close()
        return "?"  # 無法找到對應頁碼
    except Exception as e:
        print(f"⚠️ 無法獲取頁碼信息 {filepath}: {e}")
        return "?"
