import os
import re
import fitz  # PyMuPDF
import docx
import json
from openai import OpenAI
from config import OPENAI_API_KEY

client = OpenAI(api_key=OPENAI_API_KEY)

def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    first_page_text = doc[0].get_text()
    full_text = "\n".join([page.get_text() for page in doc])
    return first_page_text, full_text

def extract_text_from_docx(docx_path):
    doc = docx.Document(docx_path)
    paragraphs = [para.text for para in doc.paragraphs if para.text.strip()]
    return paragraphs[0] if paragraphs else "", "\n".join(paragraphs)

def gpt_detect_type_and_title(text, filename):
    prompt = f"""
    你是一位學術論文分析工具，請從以下內容協助判斷：
    1. 此文件是主文（paper）還是 Supporting Information（SI）？
    2. 請擷取對應主文的標題（若可得）。

    僅以以下 JSON 格式回覆，不要加入任何多餘文字，也不要使用 code block：
    {{"type": "SI" 或 "paper", "title": "主文標題（若無則為空字串）"}}

    檔案名稱：{filename}
    檔案內容：{text.strip()[:3000]}
    """

    for attempt in range(2):
        try:
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "你是專業的學術文件分類與標題擷取工具"},
                    {"role": "user", "content": prompt}
                ]
            )
            content = response.choices[0].message.content.strip()
            parsed = json.loads(content)
            return parsed
        except Exception as e:
            print(f"⚠️ GPT 回傳格式錯誤（第 {attempt+1} 次）：{e}")
            if attempt == 1:
                return {"type": "unknown", "title": ""}

def extract_metadata(file_path):
    filename = os.path.basename(file_path)
    ext = os.path.splitext(filename)[1].lower()

    if ext == ".pdf":
        first_page, full_text = extract_text_from_pdf(file_path)
    elif ext == ".docx":
        first_page, full_text = extract_text_from_docx(file_path)
    else:
        raise ValueError(f"不支援的檔案格式：{ext}")

    doi_match = re.search(r"10\.\d{4,9}/[-._;()/:A-Z0-9]+", full_text, re.I)
    doi = doi_match.group(0) if doi_match else ""

    if doi:
        doc_type = "paper"
        title = ""
    else:
        print(f"⚠️ 使用 regex 判斷 DOI 失敗，啟用 GPT 協助分析...")
        result = gpt_detect_type_and_title(first_page + "\n" + full_text[:3000], filename)
        doc_type = result.get("type", "unknown")
        title = result.get("title", "")

    return {
        "doi": doi.strip(),
        "type": doc_type,
        "title": title.strip(),
        "original_filename": filename,
        "path": file_path
    }


if __name__ == "__main__": #單檔測試用
    test_file = r"C:\Users\B30242\OneDrive - ITRI\ITRI D500\3. tool\coding\AI-research-agent\experiment_data\papers\1-s2.0-S1385894722017600-main.pdf"
    metadata = extract_metadata(test_file)
    print(metadata)
