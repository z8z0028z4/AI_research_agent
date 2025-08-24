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
- 添加配置驗證和錯誤處理
"""

import os
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# 配置日誌
logger = logging.getLogger(__name__)

# ==================== 環境變量載入 ====================
# 載入 .env 檔案，用於管理敏感信息（如API密鑰）
# .env文件應該包含：OPENAI_API_KEY 等
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


def validate_api_keys() -> Dict[str, bool]:
    """
    驗證API密鑰是否已設置
    
    Returns:
        Dict[str, bool]: 各API密鑰的驗證結果
    """
    validation_results = {
        "openai": bool(OPENAI_API_KEY)
    }
    
    missing_keys = [key for key, valid in validation_results.items() if not valid]
    if missing_keys:
        logger.warning(f"缺少API密鑰: {', '.join(missing_keys)}")
    
    return validation_results

# ==================== 項目路徑配置 ====================
# 設置基礎目錄路徑，確保跨平台兼容性
# BASE_DIR 應指向專案根目錄 AI-research-agent
# 原先設為上上層導致寫入到父資料夾（如 d:\OneDrive\3. tool\coding），現修正為上一層（專案根目錄）
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

def ensure_directory_exists(path: str) -> bool:
    """
    確保目錄存在，如果不存在則創建
    
    Args:
        path: 目錄路徑
        
    Returns:
        bool: 是否成功創建或已存在
    """
    try:
        Path(path).mkdir(parents=True, exist_ok=True)
        return True
    except Exception as e:
        logger.error(f"創建目錄失敗 {path}: {e}")
        return False

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

# 實驗元數據註冊表路徑
REGISTRY_EXPERIMENT_PATH = os.path.join(BASE_DIR, "experiment_data", "metadata_experiment_registry.xlsx")

# 化學品解析目錄：存儲從PubChem下載的化學品數據
# 用於存儲化學品的JSON格式數據和元數據
PARSED_CHEMICAL_DIR = os.path.join(BASE_DIR, "experiment_data", "parsed_chemicals")

# 上傳文件目錄
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")

# 日誌目錄
LOG_DIR = os.path.join(BASE_DIR, "logs")

def initialize_directories() -> bool:
    """
    初始化所有必要的目錄
    
    Returns:
        bool: 是否全部成功創建
    """
    directories = [
        VECTOR_INDEX_DIR,
        EXPERIMENT_DIR,
        PAPER_DIR,
        PARSED_CHEMICAL_DIR,
        UPLOAD_DIR,
        LOG_DIR
    ]
    
    success = True
    for directory in directories:
        if not ensure_directory_exists(directory):
            success = False
    
    if success:
        logger.info("所有目錄初始化完成")
    else:
        logger.error("部分目錄初始化失敗")
    
    return success

# ==================== 模型配置 ====================
# 定義系統使用的AI模型參數

# 嵌入模型：用於將文本轉換為向量表示
# 使用Nomic AI的嵌入模型進行語義搜索
EMBEDDING_MODEL_NAME = "nomic-ai/nomic-embed-text-v1.5"

# 大語言模型：用於生成回答和文本處理
LLM_MODEL_NAME = "gpt-5-mini"

# ==================== LLM參數配置 ====================
# 修復 LLM 參數配置，移除有問題的參數

# LLM調用參數（適用於所有LLM調用）
LLM_PARAMS = {
    "model": LLM_MODEL_NAME,  # 使用 "model" 而不是 "model_name"
    "max_tokens": 4000,  # 使用 max_tokens 而不是 max_completion_tokens
    "timeout": 120,  # 超時時間（秒）
}

# ==================== 文本處理參數配置 ====================
# 用於文檔分塊和向量化的參數

# 最大 token 數量：控制 AI 模型回應的最大長度
# 這個參數用於限制模型輸出的 token 數量，避免回應過長
MAX_TOKENS = 4000

# 文檔分塊大小：將長文檔分割成較小的塊進行處理
# 較大的塊可以保留更多上下文，但會增加處理時間
CHUNK_SIZE = 1000

# 文檔分塊重疊大小：相鄰塊之間的重疊部分
# 重疊可以幫助保持上下文連貫性
CHUNK_OVERLAP = 200

# ==================== 系統配置 ====================
# 系統運行相關的配置

# 批處理大小：一次處理的文件數量
BATCH_SIZE = 10

# 向量檢索的默認數量
DEFAULT_K = 5

# 最大文件大小（字節）- 已移除限制
# MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB - removed

# 支持的文件格式
SUPPORTED_FORMATS = {
    "pdf": [".pdf"],
    "word": [".docx", ".doc"],
    "excel": [".xlsx", ".xls"],
    "text": [".txt"]
}

def get_supported_extensions() -> list:
    """
    獲取所有支持的文件擴展名
    
    Returns:
        list: 支持的文件擴展名列表
    """
    extensions = []
    for format_exts in SUPPORTED_FORMATS.values():
        extensions.extend(format_exts)
    return extensions

# ==================== 日誌配置 ====================
# 日誌相關的配置

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_FILE = os.path.join(LOG_DIR, "ai_research_agent.log")

# ==================== 配置驗證 ====================
def validate_config() -> Dict[str, Any]:
    """
    驗證所有配置是否正確
    
    Returns:
        Dict[str, Any]: 驗證結果
    """
    validation_results = {
        "api_keys": validate_api_keys(),
        "directories": initialize_directories(),
        "base_dir_exists": os.path.exists(BASE_DIR),
        "config_complete": True
    }
    
    # 檢查必要的配置是否存在
    if not OPENAI_API_KEY:
        validation_results["config_complete"] = False
        logger.error("缺少 OPENAI_API_KEY 配置")
    
    if not os.path.exists(BASE_DIR):
        validation_results["config_complete"] = False
        logger.error(f"基礎目錄不存在: {BASE_DIR}")
    
    return validation_results

# ==================== 配置初始化 ====================
def initialize_config() -> bool:
    """
    初始化配置系統
    
    Returns:
        bool: 初始化是否成功
    """
    logger.info("開始初始化配置系統...")
    
    # 驗證配置
    validation = validate_config()
    
    if validation["config_complete"]:
        logger.info("配置系統初始化成功")
        return True
    else:
        logger.error("配置系統初始化失敗")
        return False

__version__ = "1.0.0"

# 自動初始化
if __name__ == "__main__":
    initialize_config()
