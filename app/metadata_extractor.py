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
    You are an academic paper analysis tool. Please help determine from the following content:
    1. Is this document a main paper or Supporting Information (SI)?
    2. Please extract the corresponding main paper title (if available).

    Reply only in the following JSON format, do not add any extra text, and do not use code blocks:
    {{"type": "SI" or "paper", "title": "main paper title (empty string if none)"}}

    File name: {filename}
    File content: {text.strip()[:3000]}
    """

    for attempt in range(2):
        try:
            from model_config_bridge import get_model_params
            llm_params = get_model_params()
            
            response = client.chat.completions.create(
                model=llm_params["model"],
                messages=[
                    {"role": "system", "content": "You are a professional academic document classification and title extraction tool"},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=llm_params.get("max_tokens", 4000),
                timeout=llm_params.get("timeout", 120),
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
