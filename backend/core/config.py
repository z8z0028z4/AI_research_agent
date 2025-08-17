"""
配置管理模塊
============

管理應用程序的配置設置，包括環境變量、數據庫連接等
"""

import os
from typing import Optional
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# 載入環境變量
load_dotenv()

class Settings(BaseSettings):
    """應用程序配置類"""
    
    # 應用基本信息
    app_name: str = "AI Research Assistant"
    app_version: str = "1.0.0"
    debug: bool = False
    
    # API 配置
    api_prefix: str = "/api/v1"
    cors_origins: list = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ]
    
    # 數據庫配置
    database_url: str = "sqlite:///./ai_research.db"
    
    # Redis 配置
    redis_url: str = "redis://localhost:6379"
    
    # 文件存儲配置
    upload_dir: str = "uploads"
    # max_file_size: removed - no file size limit
    allowed_file_types: list = [
        ".pdf", ".docx", ".xlsx", ".txt", 
        ".png", ".jpg", ".jpeg", ".gif"
    ]
    
    # AI 服務配置
    openai_api_key: Optional[str] = None
    openai_model: str = "gpt-5o-mini"  # 更新為 GPT-5 系列
    openai_max_tokens: int = 4000
    
    # 化學品查詢配置
    pubchem_base_url: str = "https://pubchem.ncbi.nlm.nih.gov/rest/pug"
    
    # 文獻搜尋配置
    perplexity_api_key: Optional[str] = None
    europepmc_base_url: str = "https://www.ebi.ac.uk/europepmc/webservices/rest"
    
    # 安全配置
    secret_key: str = "your-secret-key-here"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# 創建全局配置實例
settings = Settings()

# 確保上傳目錄存在
os.makedirs(settings.upload_dir, exist_ok=True) 