"""
AI 研究助理 - Perplexity搜索備用模塊
================================

這個模塊提供Perplexity AI作為搜索備用方案，當主要搜索源不可用時使用。
主要功能包括：
1. 智能搜索和回答生成
2. 引用和參考文獻提取
3. 結構化回答格式
4. SSL證書驗證和錯誤處理

架構說明：
- 使用Perplexity AI的chat/completions API
- 支持引用格式的結構化輸出
- 提供SSL證書驗證和備用模式
- 集成到搜索代理中作為備用方案

⚠️ 注意：此模塊需要有效的PERPLEXITY_API_KEY，格式為pplx-開頭
"""

import os
import requests
import re
import certifi
from dotenv import load_dotenv
from requests.exceptions import SSLError

# ==================== 環境配置 ====================
# 載入環境變量
load_dotenv()
API_KEY = os.getenv("PERPLEXITY_API_KEY")

# 驗證API密鑰格式
if not API_KEY or not API_KEY.startswith("pplx-"):
    raise ValueError("❌ 請設定正確的 PERPLEXITY_API_KEY（以 pplx- 開頭）")

# ==================== API配置 ====================
# 設置HTTP請求頭部
HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

# Perplexity AI API端點
API_URL = "https://api.perplexity.ai/chat/completions"


def ask_perplexity(question: str, return_citations: bool = True) -> dict:
    """
    使用Perplexity AI進行智能搜索和回答生成
    
    功能：
    1. 發送問題到Perplexity AI API
    2. 生成結構化的回答內容
    3. 提取引用和參考文獻
    4. 處理SSL證書驗證和錯誤
    
    參數：
        question (str): 用戶問題
        return_citations (bool): 是否返回引用信息
    
    返回：
        dict: 包含回答、引用和狀態信息的字典
    
    技術細節：
    - 使用sonar-pro模型進行回答生成
    - 支持結構化引用格式
    - 提供SSL證書驗證和備用模式
    - 自動提取URL引用
    
    回答格式：
    - 第一部分：文字說明內容，包含[1]、[2]格式的引用標記
    - 第二部分：Reference區塊，列出所有引用來源連結
    """
    
    # ==================== 系統指令配置 ====================
    # 指示模型輸出結構化的引用格式
    system_instruction = (
        "請將你的回答分為兩部分：\n"
        "第一部分為文字說明內容，請在關鍵處以 [1]、[2] 的格式標記引用出處。\n"
        "第二部分為 Reference 區塊，列出所有引用來源連結，格式如下：\n"
        "[1] 來源標題 - https://....\n[2] 來源標題 - https://...."
    )

    # ==================== API請求數據 ====================
    # 構建API請求數據
    data = {
        "model": "sonar-pro",  # 使用Perplexity的sonar-pro模型
        "messages": [
            {"role": "system", "content": system_instruction},
            {"role": "user", "content": question}
        ],
        "stream": False,  # 不使用流式響應
        "temperature": 0.7,  # 控制回答的創造性
        "return_citations": return_citations  # 是否返回引用信息
    }

    # ==================== SSL證書驗證 ====================
    # 使用certifi提供的證書路徑
    verify_path = certifi.where()

    try:
        # 嘗試使用SSL證書驗證
        response = requests.post(API_URL, headers=HEADERS, json=data, verify=verify_path)
        print("🔐 使用certifi憑證驗證成功")
        
    except SSLError:
        # SSL證書驗證失敗時的備用模式
        print("⚠️ 憑證驗證失敗，使用verify=False備用模式")
        try:
            response = requests.post(API_URL, headers=HEADERS, json=data, verify=False)
        except Exception as e:
            return {
                "success": False,
                "error": f"無法連線API（備用模式失敗）: {str(e)}"
            }

    # ==================== 響應處理 ====================
    if response.status_code == 200:
        # 成功響應
        result = response.json()
        text = result["choices"][0]["message"]["content"]
        
        # 提取引用連結
        citations = extract_links(text)
        
        return {
            "success": True,
            "answer": text,
            "citations": citations
        }
    else:
        # 錯誤響應
        return {
            "success": False,
            "error": f"HTTP {response.status_code}: {response.text}"
        }


def extract_links(text: str) -> list:
    """
    從文本中提取URL連結
    
    功能：
    1. 使用正則表達式匹配URL
    2. 提取所有HTTP和HTTPS連結
    3. 返回連結列表
    
    參數：
        text (str): 包含URL的文本
    
    返回：
        list: URL連結列表
    
    技術細節：
    - 使用正則表達式 r'(https?://[^\\s\\)\\]\\}]+)' 匹配URL
    - 支持HTTP和HTTPS協議
    - 自動過濾無效的URL格式
    """
    url_pattern = r'(https?://[^\s\)\]\}]+)'
    return re.findall(url_pattern, text)


# ==================== 輔助函數 ====================

def validate_perplexity_api():
    """
    驗證Perplexity API是否可用
    
    功能：
    1. 檢查API密鑰是否有效
    2. 發送測試請求
    3. 驗證響應格式
    
    返回：
        bool: API是否可用
    """
    try:
        # 檢查API密鑰
        if not API_KEY or not API_KEY.startswith("pplx-"):
            print("❌ Perplexity API密鑰格式錯誤")
            return False
        
        # 發送測試請求
        test_data = {
            "model": "sonar-pro",
            "messages": [
                {"role": "user", "content": "Hello"}
            ],
            "stream": False,
            "temperature": 0.1
        }
        
        response = requests.post(API_URL, headers=HEADERS, json=test_data, verify=False)
        
        if response.status_code == 200:
            print("✅ Perplexity API驗證成功")
            return True
        else:
            print(f"❌ Perplexity API響應錯誤：{response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Perplexity API連接失敗：{e}")
        return False


def format_citations(citations: list) -> str:
    """
    格式化引用列表
    
    功能：
    1. 將引用列表格式化為可讀的文本
    2. 添加編號和描述
    3. 返回格式化的引用文本
    
    參數：
        citations (list): 引用URL列表
    
    返回：
        str: 格式化的引用文本
    """
    if not citations:
        return "無引用來源"
    
    formatted = "引用來源：\n"
    for i, citation in enumerate(citations, 1):
        formatted += f"[{i}] {citation}\n"
    
    return formatted


def search_with_fallback(question: str, primary_search_func=None):
    """
    帶備用方案的搜索功能
    
    功能：
    1. 首先嘗試主要搜索源
    2. 如果失敗則使用Perplexity作為備用
    3. 提供統一的搜索接口
    
    參數：
        question (str): 搜索問題
        primary_search_func: 主要搜索函數
    
    返回：
        dict: 搜索結果
    """
    # 如果有主要搜索函數，先嘗試使用
    if primary_search_func:
        try:
            result = primary_search_func(question)
            if result and result.get("success", False):
                return result
        except Exception as e:
            print(f"⚠️ 主要搜索失敗，使用Perplexity備用：{e}")
    
    # 使用Perplexity作為備用方案
    print("🔄 使用Perplexity AI作為備用搜索源")
    return ask_perplexity(question)


# ==================== 測試代碼 ====================
if __name__ == "__main__":
    """
    測試Perplexity搜索功能
    
    這個測試代碼用於驗證Perplexity API是否正常工作
    """
    print("🧪 開始測試Perplexity搜索功能...")
    
    # 驗證API可用性
    if validate_perplexity_api():
        print("✅ Perplexity API驗證通過")
        
        # 測試搜索功能
        q = "請幫我找出最新用Zn-MOF捕捉CO2的研究論文，附上出處"
        result = ask_perplexity(q)
        
        if result["success"]:
            print("\n📘 回答內容：\n", result["answer"])
            if result["citations"]:
                print("\n🔗 提取的引用連結：")
                for link in result["citations"]:
                    print("-", link)
        else:
            print("❌ 查詢失敗：", result["error"])
    else:
        print("❌ Perplexity API驗證失敗")
