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
# 移除直接導入generation模組，避免循環依賴
# from .generation import *
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
    # 這些函數將通過延遲導入提供
    # "call_llm",
    # "call_structured_llm",
    
    # 檢索系統
    "load_paper_vectorstore",
    "load_experiment_vectorstore",
    "search_documents",
    "search_experiments",
    
    # 生成系統 - 通過延遲導入提供
    # "generate_research_proposal",
    # "generate_experimental_detail",
    # "generate_revision_proposal",
    
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

# 提供延遲導入的函數
def call_llm(*args, **kwargs):
    """延遲導入call_llm函數"""
    from .generation import call_llm as _call_llm
    return _call_llm(*args, **kwargs)

def call_structured_llm(*args, **kwargs):
    """延遲導入call_structured_llm函數"""
    from .generation import call_structured_llm as _call_structured_llm
    return _call_structured_llm(*args, **kwargs)

def generate_research_proposal(*args, **kwargs):
    """延遲導入generate_research_proposal函數"""
    from .generation import generate_research_proposal as _generate_research_proposal
    return _generate_research_proposal(*args, **kwargs)

def generate_experimental_detail(*args, **kwargs):
    """延遲導入generate_experimental_detail函數"""
    from .generation import generate_experimental_detail as _generate_experimental_detail
    return _generate_experimental_detail(*args, **kwargs)

def generate_revision_proposal(*args, **kwargs):
    """延遲導入generate_revision_proposal函數"""
    from .generation import generate_revision_proposal as _generate_revision_proposal
    return _generate_revision_proposal(*args, **kwargs)
