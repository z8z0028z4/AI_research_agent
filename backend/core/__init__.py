"""
Backend Core Module
==================

核心業務邏輯模組，包含：
- LLM 管理
- 檢索系統
- 生成系統
- Schema 管理
- 向量存儲
- 查詢擴展
- 模式管理
- 格式轉換
- 處理器
"""

from .llm_manager import *
from .retrieval import *
from .generation import *
from .schema_manager import *
from .vector_store import *
from .query_expander import *
from .mode_manager import *
from .format_converter import *
from .processors import *
from .prompt_builder import *

__all__ = [
    # LLM 管理
    "get_current_model",
    "get_model_params",
    "call_llm",
    "call_structured_llm",
    
    # 檢索系統
    "load_paper_vectorstore",
    "load_experiment_vectorstore",
    "search_documents",
    "search_experiments",
    
    # 生成系統
    "generate_research_proposal",
    "generate_experimental_detail",
    "generate_revision_proposal",
    
    # Schema 管理
    "create_research_proposal_schema",
    "create_experimental_detail_schema",
    "create_revision_proposal_schema",
    "get_dynamic_schema_params",
    
    # 向量存儲
    "get_chroma_instance",
    "get_vectorstore_stats",
    
    # 查詢擴展
    "expand_query",
    
    # 模式管理
    "get_mode_config",
    "set_mode_config",
    
    # 格式轉換
    "convert_format",
    
    # 處理器
    "process_documents",
    
    # 提示詞構建
    "build_prompt",
]
