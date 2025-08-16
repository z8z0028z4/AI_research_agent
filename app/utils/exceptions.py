"""
自定義異常類別模組
===============

定義應用程序專用的異常類別，提供統一的錯誤處理機制
"""

from typing import Optional, Any, Dict


class AIResearchAgentError(Exception):
    """
    AI研究助理基礎異常類別
    
    所有應用程序異常都應該繼承此類別
    """
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}
    
    def __str__(self) -> str:
        return f"{self.__class__.__name__}: {self.message}"


class FileProcessingError(AIResearchAgentError):
    """文件處理相關異常"""
    pass


class ChemicalQueryError(AIResearchAgentError):
    """化學品查詢相關異常"""
    pass


class RAGError(AIResearchAgentError):
    """RAG系統相關異常"""
    pass


class ConfigurationError(AIResearchAgentError):
    """配置相關異常"""
    pass


class ValidationError(AIResearchAgentError):
    """數據驗證相關異常"""
    pass


class APIError(AIResearchAgentError):
    """API調用相關異常"""
    
    def __init__(self, message: str, status_code: Optional[int] = None, response: Optional[Any] = None):
        super().__init__(message, {"status_code": status_code, "response": response})
        self.status_code = status_code
        self.response = response


class ModelError(AIResearchAgentError):
    """模型相關異常"""
    pass


class VectorStoreError(AIResearchAgentError):
    """向量數據庫相關異常"""
    pass


class MetadataError(AIResearchAgentError):
    """元數據處理相關異常"""
    pass


class SearchError(AIResearchAgentError):
    """搜尋相關異常"""
    pass


class ProposalGenerationError(AIResearchAgentError):
    """提案生成相關異常"""
    pass


def handle_exception(func):
    """
    異常處理裝飾器
    
    用於統一處理函數中的異常，並記錄詳細信息
    """
    from functools import wraps
    from .logger import get_logger
    
    logger = get_logger(__name__)
    
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except AIResearchAgentError as e:
            logger.error(f"應用程序異常: {e}", extra={"details": e.details})
            raise
        except Exception as e:
            logger.error(f"未預期的異常: {e}", exc_info=True)
            raise AIResearchAgentError(f"未預期的異常: {str(e)}", {"original_exception": str(e)})
    
    return wrapper
