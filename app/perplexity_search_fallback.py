import os
import requests
import re
import certifi
from dotenv import load_dotenv
from requests.exceptions import SSLError

load_dotenv()
API_KEY = os.getenv("PERPLEXITY_API_KEY")

if not API_KEY or not API_KEY.startswith("pplx-"):
    raise ValueError("❌ 請設定正確的 PERPLEXITY_API_KEY（以 pplx- 開頭）")

HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

API_URL = "https://api.perplexity.ai/chat/completions"

def ask_perplexity(question: str, return_citations: bool = True) -> dict:
    # 指示模型輸出 citation 與 reference 區塊
    system_instruction = (
        "請將你的回答分為兩部分：\n"
        "第一部分為文字說明內容，請在關鍵處以 [1]、[2] 的格式標記引用出處。\n"
        "第二部分為 Reference 區塊，列出所有引用來源連結，格式如下：\n"
        "[1] 來源標題 - https://....\n[2] 來源標題 - https://...."
    )

    data = {
        "model": "sonar-pro",
        "messages": [
            {"role": "system", "content": system_instruction},
            {"role": "user", "content": question}
        ],
        "stream": False,
        "temperature": 0.7,
        "return_citations": return_citations
    }

    verify_path = certifi.where()

    try:
        response = requests.post(API_URL, headers=HEADERS, json=data, verify=verify_path)
        print("🔐 使用 certifi 憑證驗證成功")
    except SSLError:
        print("⚠️ 憑證驗證失敗，使用 verify=False fallback 模式")
        try:
            response = requests.post(API_URL, headers=HEADERS, json=data, verify=False)
        except Exception as e:
            return {
                "success": False,
                "error": f"無法連線 API（fallback 模式失敗）: {str(e)}"
            }

    if response.status_code == 200:
        result = response.json()
        text = result["choices"][0]["message"]["content"]
        citations = extract_links(text)
        return {
            "success": True,
            "answer": text,
            "citations": citations
        }
    else:
        return {
            "success": False,
            "error": f"HTTP {response.status_code}: {response.text}"
        }

def extract_links(text: str):
    url_pattern = r'(https?://[^\s\)\]\}]+)'
    return re.findall(url_pattern, text)

if __name__ == "__main__":
    q = "請幫我找出最新用 Zn-MOF 捕捉 CO2 的研究論文，附上出處"
    result = ask_perplexity(q)
    if result["success"]:
        print("\n📘 回答內容：\n", result["answer"])
        if result["citations"]:
            print("\n🔗 擷取的 citation 連結：")
            for link in result["citations"]:
                print("-", link)
    else:
        print("❌ 查詢失敗：", result["error"])
