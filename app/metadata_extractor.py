import os
import re
import fitz  # PyMuPDF
import docx
import json
from openai import OpenAI
# 兼容性導入：支持相對導入和絕對導入
try:
    from .config import OPENAI_API_KEY
except ImportError:
    # 當作為模組導入時使用絕對導入
    from config import OPENAI_API_KEY

client = OpenAI(api_key=OPENAI_API_KEY)

def extract_text_from_pdf(pdf_path):
    try:
        # 確保使用絕對路徑
        if not os.path.isabs(pdf_path):
            pdf_path = os.path.abspath(pdf_path)
        
        # 檢查文件是否存在
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF文件不存在: {pdf_path}")
        
        doc = fitz.open(pdf_path)
        first_page_text = doc[0].get_text()
        full_text = "\n".join([page.get_text() for page in doc])
        doc.close()
        return first_page_text, full_text
    except Exception as e:
        print(f"❌ PDF文本提取失敗 {pdf_path}: {e}")
        raise

def extract_text_from_docx(docx_path):
    try:
        # 確保使用絕對路徑
        if not os.path.isabs(docx_path):
            docx_path = os.path.abspath(docx_path)
        
        # 檢查文件是否存在
        if not os.path.exists(docx_path):
            raise FileNotFoundError(f"DOCX文件不存在: {docx_path}")
        
        doc = docx.Document(docx_path)
        paragraphs = [para.text for para in doc.paragraphs if para.text.strip()]
        return paragraphs[0] if paragraphs else "", "\n".join(paragraphs)
    except Exception as e:
        print(f"❌ DOCX文本提取失敗 {docx_path}: {e}")
        raise

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
            
            # 修復參數名稱
            api_params = {
                "model": llm_params["model"],
                "messages": [
                    {"role": "system", "content": "You are a professional academic document classification and title extraction tool"},
                    {"role": "user", "content": prompt}
                ],
                "timeout": llm_params.get("timeout", 120),
            }
            
            # 根據模型類型使用正確的參數
            if "gpt-5" in llm_params["model"]:
                api_params["max_completion_tokens"] = llm_params.get("max_output_tokens", 4000)
            else:
                api_params["max_tokens"] = llm_params.get("max_tokens", 4000)
            
            response = client.chat.completions.create(**api_params)
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

    try:
        if ext == ".pdf":
            first_page, full_text = extract_text_from_pdf(file_path)
        elif ext == ".docx":
            first_page, full_text = extract_text_from_docx(file_path)
        else:
            raise ValueError(f"不支援的檔案格式：{ext}")

        # 1. 優先提取DOI
        doi_match = re.search(r"10\.\d{4,9}/[-._;()/:A-Z0-9]+", full_text, re.I)
        doi = doi_match.group(0) if doi_match else ""
        
        # 清理DOI（移除末尾的標點符號）
        if doi:
            doi = doi.rstrip('.,;:')

        # 2. 根據DOI和內容判斷類型
        if doi:
            # 有DOI = 主論文（99%的情況下）
            doc_type = "paper"
            print(f"✅ 找到DOI: {doi}，判斷為主論文")
            
            # 嘗試從內容提取標題（用於備用查詢）
            title = ""
            try:
                # 嘗試從第一頁提取標題
                lines = first_page.split('\n')
                for line in lines[:10]:  # 檢查前10行
                    line = line.strip()
                    if len(line) > 20 and len(line) < 200:  # 合理的標題長度
                        # 檢查是否包含常見的標題特徵
                        if any(keyword in line.lower() for keyword in ['carbon', 'co2', 'metal', 'organic', 'framework', 'adsorption', 'capture']):
                            title = line
                            print(f"✅ 從內容提取到標題: {title}")
                            break
            except Exception as e:
                print(f"⚠️ 從內容提取標題失敗: {e}")
        else:
            # 沒有DOI，使用LLM判斷類型和提取標題
            print(f"⚠️ 未找到DOI，使用LLM分析文件類型...")
            try:
                result = gpt_detect_type_and_title(first_page + "\n" + full_text[:3000], filename)
                doc_type = result.get("type", "unknown")
                title = result.get("title", "")
                
                if doc_type == "SI":
                    print(f"✅ LLM判斷為Supporting Information")
                elif doc_type == "paper":
                    print(f"✅ LLM判斷為主論文")
                else:
                    print(f"⚠️ LLM無法確定類型，設為unknown")
                    
            except Exception as e:
                print(f"⚠️ LLM分析失敗: {e}")
                doc_type = "unknown"
                title = ""

        return {
            "doi": doi.strip(),
            "type": doc_type,
            "title": title.strip(),
            "original_filename": filename,
            "path": file_path
        }
    except Exception as e:
        print(f"❌ 元數據提取失敗 {file_path}: {e}")
        # 返回基本的元數據信息
        return {
            "doi": "",
            "type": "unknown",
            "title": filename,
            "original_filename": filename,
            "path": file_path
        }


if __name__ == "__main__": #單檔測試用
    test_file = r"C:\Users\B30242\OneDrive - ITRI\ITRI D500\3. tool\coding\AI-research-agent\experiment_data\papers\1-s2.0-S1385894722017600-main.pdf"
    metadata = extract_metadata(test_file)
    print(metadata)
