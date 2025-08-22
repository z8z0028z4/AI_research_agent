"""
Backend Config Module
====================

配置管理模組，包含：
- 實驗目錄配置
- API 配置
- 模型配置
- 系統配置
"""

from ..core.config import settings, reload_config, validate_config

# 為了向後兼容，保留舊的變量名
EXPERIMENT_DIR = "experiment_data/experiment"
PAPER_DIR = "experiment_data/papers"
VECTOR_INDEX_DIR = "experiment_data/vector_index"
PARSED_CHEMICALS_DIR = "experiment_data/parsed_chemicals"

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

# API 配置
API_CONFIG = {
    "prefix": settings.api_prefix,
    "cors_origins": settings.cors_origins,
    "secret_key": settings.secret_key,
    "algorithm": settings.algorithm,
    "access_token_expire_minutes": settings.access_token_expire_minutes
}

# 模型配置
MODEL_CONFIG = {
    "openai_api_key": settings.openai_api_key,
    "openai_model": settings.openai_model,
    "openai_max_tokens": settings.openai_max_tokens
}

# 系統配置
SYSTEM_CONFIG = {
    "app_name": settings.app_name,
    "app_version": settings.app_version,
    "debug": settings.debug,
    "upload_dir": settings.upload_dir,
    "allowed_file_types": settings.allowed_file_types
}

__all__ = [
    "settings",
    "reload_config", 
    "validate_config",
    "EXPERIMENT_DIR",
    "PAPER_DIR",
    "VECTOR_INDEX_DIR",
    "PARSED_CHEMICALS_DIR",
    "SUPPORTED_FORMATS",
    "get_supported_extensions",
    "API_CONFIG",
    "MODEL_CONFIG",
    "SYSTEM_CONFIG",
]
