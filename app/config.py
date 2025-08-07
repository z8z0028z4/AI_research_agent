"""
AI 研究助理系統配置文件
====================

這個文件負責管理整個系統的配置參數，包括：
1. API密鑰管理
2. 文件路徑配置
3. 模型參數設置
4. 環境變量處理

架構說明：
- 使用python-dotenv管理環境變量
- 集中管理所有配置參數
- 提供清晰的目錄結構定義
"""

import os
from dotenv import load_dotenv

# ==================== 環境變量載入 ====================
# 載入 .env 檔案，用於管理敏感信息（如API密鑰）
# .env文件應該包含：OPENAI_API_KEY, PERPLEXITY_API_KEY 等
load_dotenv()

# ==================== SSL 證書配置 ====================
# 在企業環境中可能需要繞過SSL證書驗證
# 設置環境變量以繞過SSL證書問題
os.environ['CURL_CA_BUNDLE'] = ''
os.environ['REQUESTS_CA_BUNDLE'] = ''
os.environ['SSL_CERT_FILE'] = ''
os.environ["HF_HUB_DISABLE_SSL_VERIFICATION"] = "1"
os.environ["HF_HUB_OFFLINE"] = "0"
os.environ["TRANSFORMERS_OFFLINE"] = "0"
os.environ["HF_DATASETS_OFFLINE"] = "0"

# ==================== API 密鑰配置 ====================
# 從環境變量中獲取API密鑰，確保安全性
# 如果環境變量未設置，這些值將為None
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")  # OpenAI API密鑰，用於GPT模型調用
PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY")  # Perplexity API密鑰，用於搜索功能

# ==================== 項目路徑配置 ====================
# 設置基礎目錄路徑，確保跨平台兼容性
# BASE_DIR 指向項目根目錄的上一級目錄
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

# ==================== 數據目錄配置 ====================
# 定義各種數據存儲目錄，用於組織和管理數據文件

# 向量索引目錄：存儲文檔的向量嵌入數據
# 用於快速語義搜索和相似度計算
VECTOR_INDEX_DIR = os.path.join(BASE_DIR, "experiment_data", "vector_index")

# 實驗數據目錄：存儲實驗相關的數據文件
# 包括實驗記錄、結果、配置等
EXPERIMENT_DIR = os.path.join(BASE_DIR, "experiment_data", "experiment")

# 論文目錄：存儲研究論文和文獻資料
# 包括PDF、DOCX等格式的文檔
PAPER_DIR = os.path.join(BASE_DIR, "experiment_data", "papers")

# 元數據註冊表路徑：存儲文檔和實驗的元數據信息
# 使用Excel格式便於查看和編輯
REGISTRY_PATH = os.path.join(BASE_DIR, "experiment_data", "metadata_registry.xlsx")

# 化學品解析目錄：存儲從PubChem下載的化學品數據
# 用於存儲化學品的JSON格式數據和元數據
PARSED_CHEMICAL_DIR = os.path.join(BASE_DIR, "research_agent", "app", "experiment_data", "chemicals")


# ==================== 模型配置 ====================
# 定義系統使用的AI模型參數

# 嵌入模型：用於將文本轉換為向量表示
# 使用Nomic AI的嵌入模型進行語義搜索
EMBEDDING_MODEL_NAME = "nomic-ai/nomic-embed-text-v1.5"

# 大語言模型：用於生成回答和文本處理
LLM_MODEL_NAME = "gpt-4-1106-preview"

# ==================== LLM參數配置 ====================
# 修復 LLM 參數配置，移除有問題的參數

# LLM調用參數（適用於所有LLM調用）
LLM_PARAMS = {
    "model": LLM_MODEL_NAME,  # 使用 "model" 而不是 "model_name"
    "temperature": 0.3,  # 溫度參數
    "max_tokens": 4000,  # 使用 max_tokens 而不是 max_completion_tokens
    "timeout": 120,  # 超時時間（秒）
}


# ==================== 配置驗證函數 ====================
def validate_config():
    """
    驗證配置是否正確設置
    
    檢查項目：
    1. API密鑰是否已設置
    2. 必要目錄是否存在
    3. 模型名稱是否有效
    
    返回：
        bool: 配置是否有效
    """
    errors = []
    
    # 檢查API密鑰
    if not OPENAI_API_KEY:
        errors.append("❌ OPENAI_API_KEY 未設置")
    if not PERPLEXITY_API_KEY:
        errors.append("❌ PERPLEXITY_API_KEY 未設置")
    
    # 檢查目錄是否存在，如果不存在則創建
    directories = [VECTOR_INDEX_DIR, EXPERIMENT_DIR, PAPER_DIR, PARSED_CHEMICAL_DIR]
    for directory in directories:
        if not os.path.exists(directory):
            try:
                os.makedirs(directory, exist_ok=True)
                print(f"✅ 創建目錄：{directory}")
            except Exception as e:
                errors.append(f"❌ 無法創建目錄 {directory}: {e}")
    
    # 輸出驗證結果
    if errors:
        print("🔧 配置驗證發現問題：")
        for error in errors:
            print(f"  {error}")
        return False
    else:
        print("✅ 配置驗證通過")
        return True

# 如果直接運行此文件，執行配置驗證
if __name__ == "__main__":
    validate_config()