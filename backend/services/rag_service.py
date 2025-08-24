"""
RAG核心模組 (重構版)
==================

基於檢索增強生成的AI研究助手核心功能
整合文獻檢索、知識提取和智能問答

此版本是重構後的簡化版本，主要功能已分解到 core 模組中
"""

import os
import json
from typing import List, Dict, Any, Optional, Tuple

# 導入核心模組 - 直接從具體模塊導入避免循環導入
from ..core.schema_manager import (
    get_dynamic_schema_params,
    create_research_proposal_schema,
    create_experimental_detail_schema,
    create_revision_proposal_schema,
    get_schema_by_type
)
from ..core.vector_store import load_paper_vectorstore, load_experiment_vectorstore
from ..core.prompt_builder import (
    build_prompt,
    build_proposal_prompt,
    build_detail_experimental_plan_prompt,
    build_inference_prompt,
    build_dual_inference_prompt,
    build_iterative_proposal_prompt
)
from ..core.generation import (
    call_llm,
    call_llm_structured_proposal,
    call_llm_structured_experimental_detail,
    call_llm_structured_revision_proposal
)
from ..core.query_expander import expand_query, expand_query_with_fallback
from ..core.format_converter import (
    structured_proposal_to_text,
    structured_experimental_detail_to_text,
    structured_revision_proposal_to_text
)

from backend.utils.logger import get_logger

logger = get_logger(__name__)


# ==================== 便捷函數 ====================

def generate_structured_proposal(chunks: List, question: str) -> Dict[str, Any]:
    """
    生成結構化研究提案
    
    Args:
        chunks: 檢索到的文獻片段
        question: 用戶的研究問題
    
    Returns:
        Dict[str, Any]: 結構化的研究提案
    """
    logger.info(f"🔍 DEBUG: generate_structured_proposal 開始")
    logger.info(f"🔍 DEBUG: chunks 長度: {len(chunks) if chunks else 0}")
    logger.info(f"🔍 DEBUG: question: {question}")
    
    system_prompt, citations = build_proposal_prompt(question, chunks)
    
    # 構建用戶提示詞（包含文獻摘要）
    paper_context_text = ""
    for i, doc in enumerate(chunks):
        metadata = doc.metadata
        title = metadata.get("title", "Untitled")
        filename = metadata.get("filename") or metadata.get("source", "Unknown")
        page = metadata.get("page_number") or metadata.get("page", "?")
        
        paper_context_text += f"[{i+1}] {title} | Page {page}\n{doc.page_content}\n\n"
    
    user_prompt = f"""
    --- Literature Excerpts ---
    {paper_context_text}

    --- Research Objectives ---
    {question}
    """
    
    # 調用結構化LLM
    proposal_data = call_llm_structured_proposal(system_prompt, user_prompt)
    
    # 添加引用信息到返回結果
    if proposal_data:
        proposal_data['citations'] = citations
    
    return proposal_data


def generate_iterative_structured_proposal(
    question: str,
    new_chunks: List,
    old_chunks: List,
    past_proposal: str
) -> Dict[str, Any]:
    """
    生成迭代式結構化研究提案
    
    Args:
        question: 用戶反饋
        new_chunks: 新檢索到的文獻片段
        old_chunks: 原有的文獻片段
        past_proposal: 之前的提案內容
    
    Returns:
        Dict[str, Any]: 修改後的結構化研究提案
    """
    system_prompt, user_prompt, citations = build_iterative_proposal_prompt(
        question, new_chunks, old_chunks, past_proposal
    )
    
    # 調用結構化LLM
    proposal_data = call_llm_structured_proposal(system_prompt, user_prompt)
    
    # 添加引用信息到返回結果
    if proposal_data:
        proposal_data['citations'] = citations
    
    return proposal_data


def generate_structured_experimental_detail(chunks: List, proposal: str) -> Dict[str, Any]:
    """
    生成結構化實驗細節的便捷函數
    
    Args:
        chunks: 文獻片段
        proposal: 研究提案
    
    Returns:
        Dict[str, Any]: 結構化實驗細節
    """
    logger.info(f"🔍 DEBUG: generate_structured_experimental_detail 開始")
    logger.info(f"🔍 DEBUG: chunks 長度: {len(chunks) if chunks else 0}")
    logger.info(f"🔍 DEBUG: proposal 長度: {len(proposal) if proposal else 0}")
    
    # 使用標準化的提示詞構建流程
    system_prompt, citations = build_detail_experimental_plan_prompt(chunks, proposal)
    
    # 由於 system_prompt 已經包含了文獻摘要和提案內容，user_prompt 保持為空字串以保持一致性
    user_prompt = ""
    
    # 調用結構化LLM（使用正確的實驗細節schema）
    from backend.core.schema_manager import create_experimental_detail_schema
    from backend.core.generation import call_structured_llm
    
    # 構建完整的提示詞
    full_prompt = f"{system_prompt}\n\n{user_prompt}"
    
    # 使用正確的實驗細節schema
    current_schema = create_experimental_detail_schema()
    
    # 調用結構化LLM
    experimental_data = call_structured_llm(full_prompt, current_schema)
    
    # 添加引用信息到返回結果
    if experimental_data:
        experimental_data['citations'] = citations
    
    return experimental_data





def generate_structured_revision_proposal(
    question: str, 
    new_chunks: List, 
    old_chunks: List, 
    proposal: str
) -> Dict[str, Any]:
    """
    生成結構化修訂提案的便捷函數 (包含修訂說明)
    
    Args:
        question: 用戶反饋/問題
        new_chunks: 新檢索的文檔塊
        old_chunks: 原始文檔塊
        proposal: 原始提案
    
    Returns:
        Dict[str, Any]: 結構化修訂提案 (包含修訂說明)
    """
    return call_llm_structured_revision_proposal(question, new_chunks, old_chunks, proposal)


# ==================== 向後兼容性函數 ====================

# 為了保持向後兼容性，保留一些原始函數名稱的別名
def get_dynamic_schema_params_compat():
    """向後兼容性函數"""
    return get_dynamic_schema_params()


def create_research_proposal_schema_compat():
    """向後兼容性函數"""
    return create_research_proposal_schema()


def create_experimental_detail_schema_compat():
    """向後兼容性函數"""
    return create_experimental_detail_schema()





def create_revision_proposal_schema_compat():
    """向後兼容性函數"""
    return create_revision_proposal_schema()


def load_paper_vectorstore_compat():
    """向後兼容性函數"""
    return load_paper_vectorstore()


def load_experiment_vectorstore_compat():
    """向後兼容性函數"""
    return load_experiment_vectorstore()


def retrieve_chunks_multi_query_compat(*args, **kwargs):
    """向後兼容性函數"""
    return retrieve_chunks_multi_query(*args, **kwargs)


def preview_chunks_compat(*args, **kwargs):
    """向後兼容性函數"""
    return preview_chunks(*args, **kwargs)


def build_prompt_compat(*args, **kwargs):
    """向後兼容性函數"""
    return build_prompt(*args, **kwargs)


def build_proposal_prompt_compat(*args, **kwargs):
    """向後兼容性函數"""
    return build_proposal_prompt(*args, **kwargs)


def build_detail_experimental_plan_prompt_compat(*args, **kwargs):
    """向後兼容性函數"""
    return build_detail_experimental_plan_prompt(*args, **kwargs)


def build_inference_prompt_compat(*args, **kwargs):
    """向後兼容性函數"""
    return build_inference_prompt(*args, **kwargs)


def build_dual_inference_prompt_compat(*args, **kwargs):
    """向後兼容性函數"""
    return build_dual_inference_prompt(*args, **kwargs)


def build_iterative_proposal_prompt_compat(*args, **kwargs):
    """向後兼容性函數"""
    return build_iterative_proposal_prompt(*args, **kwargs)


def call_llm_compat(*args, **kwargs):
    """向後兼容性函數"""
    return call_llm(*args, **kwargs)


def call_llm_structured_proposal_compat(*args, **kwargs):
    """向後兼容性函數"""
    return call_llm_structured_proposal(*args, **kwargs)


def call_llm_structured_experimental_detail_compat(*args, **kwargs):
    """向後兼容性函數"""
    return call_llm_structured_experimental_detail(*args, **kwargs)





def call_llm_structured_revision_proposal_compat(*args, **kwargs):
    """向後兼容性函數"""
    return call_llm_structured_revision_proposal(*args, **kwargs)


def expand_query_compat(*args, **kwargs):
    """向後兼容性函數"""
    return expand_query(*args, **kwargs)


def expand_query_with_fallback_compat(*args, **kwargs):
    """向後兼容性函數"""
    return expand_query_with_fallback(*args, **kwargs)


def structured_proposal_to_text_compat(*args, **kwargs):
    """向後兼容性函數"""
    return structured_proposal_to_text(*args, **kwargs)


def structured_experimental_detail_to_text_compat(*args, **kwargs):
    """向後兼容性函數"""
    return structured_experimental_detail_to_text(*args, **kwargs)


def structured_revision_proposal_to_text_compat(*args, **kwargs):
    """向後兼容性函數"""
    return structured_revision_proposal_to_text(*args, **kwargs)


# ==================== 導出所有函數 ====================

__all__ = [
    # 核心功能
    'generate_structured_proposal',
    'generate_iterative_structured_proposal',
    'generate_structured_experimental_detail',
    
    'generate_structured_revision_proposal',
    
    # Schema 管理
    'get_dynamic_schema_params',
    'create_research_proposal_schema',
    'create_experimental_detail_schema',
    
    'create_revision_proposal_schema',
    'get_schema_by_type',
    
    # 向量數據庫操作
    'load_paper_vectorstore',
    'load_experiment_vectorstore',
    
    # 提示詞構建
    'build_prompt',
    'build_proposal_prompt',
    'build_detail_experimental_plan_prompt',
    'build_inference_prompt',
    'build_dual_inference_prompt',
    'build_iterative_proposal_prompt',
    
    # LLM 生成
    'call_llm',
    'call_llm_structured_proposal',
    'call_llm_structured_experimental_detail',
    
    'call_llm_structured_revision_proposal',
    
    # 查詢擴展
    'expand_query',
    'expand_query_with_fallback',
    
    # 格式轉換
    'structured_proposal_to_text',
    'structured_experimental_detail_to_text',
    'structured_revision_proposal_to_text',
    
    # 向後兼容性函數
    'get_dynamic_schema_params_compat',
    'create_research_proposal_schema_compat',
    'create_experimental_detail_schema_compat',
    
    'create_revision_proposal_schema_compat',
    'load_paper_vectorstore_compat',
    'load_experiment_vectorstore_compat',
    'retrieve_chunks_multi_query_compat',
    'preview_chunks_compat',
    'build_prompt_compat',
    'build_proposal_prompt_compat',
    'build_detail_experimental_plan_prompt_compat',
    'build_inference_prompt_compat',
    'build_dual_inference_prompt_compat',
    'build_iterative_proposal_prompt_compat',
    'call_llm_compat',
    'call_llm_structured_proposal_compat',
    'call_llm_structured_experimental_detail_compat',

    'call_llm_structured_revision_proposal_compat',
    'expand_query_compat',
    'expand_query_with_fallback_compat',
    'structured_proposal_to_text_compat',
    'structured_experimental_detail_to_text_compat',
    'structured_revision_proposal_to_text_compat'
]
