"""
生成模組
========

負責 LLM 調用和內容生成
重構後使用新的模組架構，避免循環導入問題
"""

import time
import json
from typing import Dict, Any, Optional, List

from backend.utils.logger import get_logger
from backend.utils.exceptions import LLMError, APIRequestError
from backend.core.llm_client import get_llm_client
from backend.core.model_config import get_current_model, get_model_params

logger = get_logger(__name__)


def call_llm(prompt: str, **kwargs) -> str:
    """
    調用 LLM 生成文本
    
    參數：
        prompt: 提示詞
        **kwargs: 額外參數
        
    返回：
        str: 生成的文本
    """
    try:
        current_model = get_current_model()
        llm_params = get_model_params()
        
        # 使用新的 LLM 客戶端
        llm_client = get_llm_client()
        return llm_client.call_llm(prompt, current_model, llm_params, **kwargs)
            
    except Exception as e:
        logger.error(f"LLM 調用失敗：{e}")
        raise LLMError(f"LLM 調用失敗：{str(e)}")


# 舊的實現函數已被新的 LLM 客戶端替代
# _call_gpt5_responses_api 和 _call_gpt4_chat_api 現在在 llm_client.py 中實現


def call_structured_llm(prompt: str, schema: Dict[str, Any], **kwargs) -> Dict[str, Any]:
    """
    調用結構化 LLM 生成 JSON 格式內容
    
    參數：
        prompt: 提示詞
        schema: JSON Schema
        **kwargs: 額外參數
        
    返回：
        Dict[str, Any]: 結構化數據
    """
    try:
        current_model = get_current_model()
        llm_params = get_model_params()
        
        logger.info(f"調用結構化 LLM，模型：{current_model}")
        
        # 只支援 GPT-5 系列
        if not current_model.startswith('gpt-5'):
            raise LLMError(f"不支援的模型：{current_model}，只支援 GPT-5 系列")
        
        # 使用新的 LLM 客戶端
        llm_client = get_llm_client()
        return llm_client.call_structured_llm(prompt, schema, current_model, llm_params, **kwargs)
            
    except Exception as e:
        logger.error(f"結構化 LLM 調用失敗：{e}")
        raise LLMError(f"結構化 LLM 調用失敗：{str(e)}")


# 舊的 _call_gpt5_structured_api 函數已被新的 LLM 客戶端替代


# _call_gpt4_structured_api 函數已移除 - 不再支援 GPT-4 系列


# generate_proposal_with_fallback 函數已移除 - 不再支援非結構化輸出 fallback


# 舊的 _extract_partial_json_from_response 函數已被新的 LLM 客戶端替代


def call_llm_structured_proposal(system_prompt: str, user_prompt: str) -> Dict[str, Any]:
    """
    使用OpenAI Responses API的JSON structured output生成結構化研究提案
    
    Args:
        system_prompt: 系統提示詞
        user_prompt: 用戶提示詞（包含文獻摘要和研究目標）
    
    Returns:
        Dict[str, Any]: 符合RESEARCH_PROPOSAL_SCHEMA的結構化提案
    """
    logger.info(f"調用結構化LLM，系統提示詞長度：{len(system_prompt)} 字符")
    logger.info(f"用戶提示詞長度：{len(user_prompt)} 字符")
    
    try:
        current_model = get_current_model()
        llm_params = get_model_params()
        logger.info(f"使用模型：{current_model}")
        logger.debug(f"模型參數：{llm_params}")
    except Exception as e:
        logger.error(f"無法獲取模型信息：{e}")
        raise LLMError(f"無法獲取模型信息：{str(e)}")
    
    try:
        # 只支援 GPT-5 系列使用 Responses API
        if not current_model.startswith('gpt-5'):
            raise LLMError(f"不支援的模型：{current_model}，只支援 GPT-5 系列")
        
        from backend.core.schema_manager import create_research_proposal_schema
        
        # 動態獲取最新的 schema
        current_schema = create_research_proposal_schema()
        
        # 添加調試日誌
        logger.info(f"🔍 [DEBUG] 獲取到的 schema: {current_schema is not None}")
        if current_schema:
            logger.info(f"🔍 [DEBUG] Schema 類型: {current_schema.get('type', 'unknown')}")
            logger.info(f"🔍 [DEBUG] Schema 標題: {current_schema.get('title', 'unknown')}")
            logger.info(f"🔍 [DEBUG] Schema 必需字段: {current_schema.get('required', [])}")
        else:
            logger.warning("⚠️ [DEBUG] Schema 為空，將回退到傳統文本生成")
        
        # 構建完整的提示詞
        full_prompt = f"{system_prompt}\n\n{user_prompt}"
        
        return call_structured_llm(full_prompt, current_schema)
        
    except Exception as e:
        logger.error(f"結構化LLM調用失敗：{e}")
        raise LLMError(f"結構化LLM調用失敗：{str(e)}")


def call_llm_structured_experimental_detail(chunks: List, proposal: str) -> Dict[str, Any]:
    """
    使用OpenAI Responses API的JSON structured output生成結構化實驗細節
    
    Args:
        chunks: 文獻片段
        proposal: 研究提案
    
    Returns:
        Dict[str, Any]: 符合EXPERIMENTAL_DETAIL_SCHEMA的結構化實驗細節
    """
    logger.info(f"調用結構化實驗細節LLM，文獻片段數量：{len(chunks)}")
    logger.info(f"提案長度：{len(proposal)} 字符")
    
    try:
        current_model = get_current_model()
        llm_params = get_model_params()
        logger.info(f"使用模型：{current_model}")
        logger.debug(f"模型參數：{llm_params}")
    except Exception as e:
        logger.error(f"無法獲取模型信息：{e}")
        raise LLMError(f"無法獲取模型信息：{str(e)}")
    
    try:
        # 只支援 GPT-5 系列使用 Responses API
        if not current_model.startswith('gpt-5'):
            raise LLMError(f"不支援的模型：{current_model}，只支援 GPT-5 系列")
        
        from backend.core.schema_manager import create_experimental_detail_schema
        
        # 構建系統提示詞
        system_prompt = f"""
        You are a professional materials synthesis consultant, skilled at generating detailed experimental procedures based on literature and research proposals.

        Based on the following research proposal and literature information, please generate detailed experimental details:

        --- Research Proposal ---
        {proposal}

        Please generate detailed experimental details including the following four sections:
        1. Synthesis Process: Detailed synthesis steps, conditions, durations, etc.
        2. Materials and Conditions: Materials used, concentrations, temperatures, pressures, and other reaction conditions
        3. Analytical Methods: Characterization techniques such as XRD, SEM, NMR, etc.
        4. Precautions: Experimental notes and safety precautions
        """
        
        # 構建用戶提示詞（包含文獻摘要）
        context_text = ""
        citations = []
        for i, doc in enumerate(chunks):
            meta = doc.metadata
            title = meta.get("title", "Untitled")
            filename = meta.get("filename") or meta.get("source", "Unknown")
            page = meta.get("page_number") or meta.get("page", "?")
            
            context_text += f"[{i+1}] {title} | Page {page}\n{doc.page_content}\n\n"
            citations.append({
                "label": f"[{i+1}]",
                "title": title,
                "source": filename,
                "page": page
            })
        
        user_prompt = f"""
        Based on the following literature information, generate detailed experimental procedures:

        --- Literature Excerpts ---
        {context_text}
        
        
        """
        
        # 動態獲取最新的 schema
        current_schema = create_experimental_detail_schema()
        
        # 構建完整的提示詞
        full_prompt = f"{system_prompt}\n\n{user_prompt}"
        
        # 調用結構化 LLM
        experimental_data = call_structured_llm(full_prompt, current_schema)
        
        # 添加引用信息
        if experimental_data:
            experimental_data['citations'] = citations
        
        return experimental_data
        
    except Exception as e:
        logger.error(f"結構化實驗細節LLM調用失敗：{e}")
        return {}






def call_llm_structured_revision_proposal(question: str, new_chunks: List, old_chunks: List, proposal: str) -> Dict[str, Any]:
    """
    使用OpenAI Responses API的JSON structured output生成結構化修訂提案 (包含修訂說明)
    
    Args:
        question: 用戶反饋/問題
        new_chunks: 新檢索的文檔塊
        old_chunks: 原始文檔塊
        proposal: 原始提案
    
    Returns:
        Dict[str, Any]: 符合REVISION_PROPOSAL_SCHEMA的結構化修訂提案
    """
    logger.info(f"調用結構化修訂提案LLM，用戶反饋長度：{len(question)}")
    logger.info(f"新文檔塊數量：{len(new_chunks)}")
    logger.info(f"原文檔塊數量：{len(old_chunks)}")
    logger.info(f"原始提案長度：{len(proposal)} 字符")
    
    try:
        current_model = get_current_model()
        llm_params = get_model_params()
        logger.info(f"使用模型：{current_model}")
        logger.debug(f"模型參數：{llm_params}")
    except Exception as e:
        logger.error(f"無法獲取模型信息：{e}")
        raise LLMError(f"無法獲取模型信息：{str(e)}")
    
    try:
        # 只支援 GPT-5 系列使用 Responses API
        if not current_model.startswith('gpt-5'):
            raise LLMError(f"不支援的模型：{current_model}，只支援 GPT-5 系列")
        
        from backend.core.schema_manager import create_revision_proposal_schema
        
        # 動態獲取最新的 schema
        current_schema = create_revision_proposal_schema()
        
        # 添加調試日誌
        logger.info(f"🔍 [DEBUG] 獲取到的 schema: {current_schema is not None}")
        if current_schema:
            logger.info(f"🔍 [DEBUG] Schema 類型: {current_schema.get('type', 'unknown')}")
            logger.info(f"🔍 [DEBUG] Schema 標題: {current_schema.get('title', 'unknown')}")
            logger.info(f"🔍 [DEBUG] Schema 必需字段: {current_schema.get('required', [])}")
        else:
            logger.warning("⚠️ [DEBUG] Schema 為空，將回退到傳統文本生成")
        
        # 構建提示詞
        system_prompt = """
        You are an experienced materials experiment design consultant. Please help modify parts of the research proposal based on user feedback, original proposal, and literature content.

        Your task is to generate a modified research proposal based on user feedback, original proposal, and literature content. The proposal should be innovative, scientifically rigorous, and feasible.

        IMPORTANT: You must respond in valid JSON format only. Do not include any text before or after the JSON object.

        The JSON must have the following structure:
        {
            "revision_explanation": "Brief explanation of revision logic and key improvements based on user feedback",
            "proposal_title": "Title of the research proposal",
            "need": "Research need and current limitations",
            "solution": "Proposed design and development strategies",
            "differentiation": "Comparison with existing technologies",
            "benefit": "Expected improvements and benefits",
            "experimental_overview": "Experimental approach and methodology",
            "materials_list": ["material1", "material2", "material3"]
        }

        Key requirements:
        1. Prioritize the areas that the user wants to modify and look for possible improvement directions from the literature
        2. Except for the areas that the user is dissatisfied with, other parts should maintain the original proposal content without changes
        3. Maintain scientific rigor, clarity, and avoid vague descriptions
        4. Use only the provided literature labels ([1], [2], etc.) for citations, and do not fabricate sources
        5. Ensure every claim is supported by a cited source or reasonable extension from the literature
        6. For materials_list, include ONLY IUPAC chemical names without any descriptions, notes, or parenthetical explanations. Each item must be a single chemical name only.
        7. The revision_explanation should briefly explain the logic of changes and key improvements based on user feedback
        """
        
        # 構建文檔內容
        old_text = ""
        for i, doc in enumerate(old_chunks):
            # 處理可能是字典格式的 chunks
            if hasattr(doc, 'metadata'):
                metadata = doc.metadata
                page_content = doc.page_content
            else:
                metadata = doc.get('metadata', {})
                page_content = doc.get('page_content', '')
            
            title = metadata.get("title", "Untitled")
            filename = metadata.get("filename") or metadata.get("source", "Unknown")
            page = metadata.get("page_number") or metadata.get("page", "?")
            snippet = page_content[:80].replace("\n", " ")
            old_text += f"    [{i+1}] {title} | Page {page}\n{snippet}\n\n"
        
        new_text = ""
        for i, doc in enumerate(new_chunks):
            # 處理可能是字典格式的 chunks
            if hasattr(doc, 'metadata'):
                metadata = doc.metadata
                page_content = doc.page_content
            else:
                metadata = doc.get('metadata', {})
                page_content = doc.get('page_content', '')
            
            title = metadata.get("title", "Untitled")
            filename = metadata.get("filename") or metadata.get("source", "Unknown")
            page = metadata.get("page_number") or metadata.get("page", "?")
            snippet = page_content[:80].replace("\n", " ")
            new_text += f"    [{i+1}] {title} | Page {page}\n{snippet}\n\n"
        
        user_prompt = f"""
        --- User Feedback ---
        {question}

        --- Original Proposal Content ---
        {proposal}

        --- Literature Excerpts Based on Original Proposal ---
        {old_text}

        --- New Retrieved Excerpts Based on Feedback ---
        {new_text}
        """
        
        # 構建完整的提示詞
        full_prompt = f"{system_prompt}\n\n{user_prompt}"
        
        return call_structured_llm(full_prompt, current_schema)
        
    except Exception as e:
        logger.error(f"結構化修訂提案LLM調用失敗：{e}")
        return {}


def call_llm_structured_revision_experimental_detail(
    question: str, 
    new_chunks: List, 
    old_chunks: List, 
    proposal: str,
    original_experimental_detail: str
) -> Dict[str, Any]:
    """
    使用OpenAI Responses API的JSON structured output生成結構化修訂實驗細節
    
    Args:
        question: 用戶反饋/問題
        new_chunks: 新檢索的文檔塊（修改實驗細節時為空）
        old_chunks: 原始文檔塊
        proposal: 原始提案
        original_experimental_detail: 原始實驗細節
    
    Returns:
        Dict[str, Any]: 符合REVISION_EXPERIMENTAL_DETAIL_SCHEMA的結構化修訂實驗細節
    """
    logger.info(f"調用結構化修訂實驗細節LLM，用戶反饋長度：{len(question)}")
    logger.info(f"原文檔塊數量：{len(old_chunks)}")
    logger.info(f"原始提案長度：{len(proposal)} 字符")
    logger.info(f"原始實驗細節長度：{len(original_experimental_detail)} 字符")
    
    try:
        current_model = get_current_model()
        llm_params = get_model_params()
        logger.info(f"使用模型：{current_model}")
        logger.debug(f"模型參數：{llm_params}")
    except Exception as e:
        logger.error(f"無法獲取模型信息：{e}")
        raise LLMError(f"無法獲取模型信息：{str(e)}")
    
    try:
        # 只支援 GPT-5 系列使用 Responses API
        if not current_model.startswith('gpt-5'):
            raise LLMError(f"不支援的模型：{current_model}，只支援 GPT-5 系列")
        
        from backend.core.schema_manager import create_revision_experimental_detail_schema
        
        # 動態獲取最新的 schema
        current_schema = create_revision_experimental_detail_schema()
        
        # 添加調試日誌
        logger.info(f"🔍 [DEBUG] 獲取到的 schema: {current_schema is not None}")
        if current_schema:
            logger.info(f"🔍 [DEBUG] Schema 類型: {current_schema.get('type', 'unknown')}")
            logger.info(f"🔍 [DEBUG] Schema 標題: {current_schema.get('title', 'unknown')}")
            logger.info(f"🔍 [DEBUG] Schema 必需字段: {current_schema.get('required', [])}")
        else:
            logger.warning("⚠️ [DEBUG] Schema 為空，將回退到傳統文本生成")
        
        # 構建提示詞
        system_prompt = """
        You are an experienced materials experiment design consultant. Please help modify parts of the experimental details based on user feedback, original proposal, original experimental details, and literature content.

        Your task is to generate modified experimental details based on user feedback, original proposal, original experimental details, and literature content. The experimental details should be scientifically rigorous, feasible, and address the user's specific modification requests.

        IMPORTANT: You must respond in valid JSON format only. Do not include any text before or after the JSON object.

        The JSON must have the following structure:
        {
            "revision_explanation": "Brief explanation of revision logic and key improvements based on user feedback",
            "synthesis_process": "Detailed synthesis steps, conditions, durations, etc. with modifications",
            "materials_and_conditions": "Materials used, concentrations, temperatures, pressures, and other reaction conditions with modifications",
            "analytical_methods": "Characterization techniques such as XRD, SEM, NMR, etc. with modifications",
            "precautions": "Experimental notes and safety precautions with modifications"
        }

        Key requirements:
        1. Prioritize the areas that the user wants to modify and look for possible improvement directions from the literature
        2. Except for the areas that the user is dissatisfied with, other parts should maintain the original experimental detail content without changes
        3. Maintain scientific rigor, clarity, and avoid vague descriptions
        4. Use only the provided literature labels ([1], [2], etc.) for citations, and do not fabricate sources
        5. Ensure every claim is supported by a cited source or reasonable extension from the literature
        6. The revision_explanation should briefly explain the logic of changes and key improvements based on user feedback
        7. Focus on the specific experimental step or section that the user wants to modify
        """
        
        # 構建文檔內容（只使用原始chunks）
        old_text = ""
        for i, doc in enumerate(old_chunks):
            # 處理可能是字典格式的 chunks
            if hasattr(doc, 'metadata'):
                metadata = doc.metadata
                page_content = doc.page_content
            else:
                metadata = doc.get('metadata', {})
                page_content = doc.get('page_content', '')
            
            title = metadata.get("title", "Untitled")
            filename = metadata.get("filename") or metadata.get("source", "Unknown")
            page = metadata.get("page_number") or metadata.get("page", "?")
            
            # 顯示完整的文檔內容，而不是只有前80個字符
            old_text += f"    [{i+1}] {title} | Page {page}\n{page_content}\n\n"
        
        user_prompt = f"""
        --- User Feedback ---
        {question}

        --- Original Proposal Content ---
        {proposal}

        --- Original Experimental Details ---
        {original_experimental_detail}

        --- Literature Excerpts Based on Original Proposal ---
        {old_text}
        """
        
        # 構建完整的提示詞
        full_prompt = f"{system_prompt}\n\n{user_prompt}"
        
        return call_structured_llm(full_prompt, current_schema)
        
    except Exception as e:
        logger.error(f"結構化修訂實驗細節LLM調用失敗：{e}")
        return {}
