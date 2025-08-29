"""
生成模組
========

負責 LLM 調用和內容生成
"""

import time
import json
from typing import Dict, Any, Optional, List
from openai import OpenAI

from backend.utils.logger import get_logger
from backend.utils.exceptions import LLMError, APIRequestError
from backend.services.model_service import get_model_params, get_current_model

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
        
        logger.info(f"調用 LLM，模型：{current_model}")
        logger.debug(f"提示詞長度：{len(prompt)} 字符")
        
        # 根據模型類型選擇不同的調用方式
        if current_model.startswith('gpt-5'):
            return _call_gpt5_responses_api(prompt, llm_params, **kwargs)
        else:
            return _call_gpt4_chat_api(prompt, llm_params, **kwargs)
            
    except Exception as e:
        logger.error(f"LLM 調用失敗：{e}")
        raise LLMError(f"LLM 調用失敗：{str(e)}")


def _call_gpt5_responses_api(prompt: str, llm_params: Dict[str, Any], **kwargs) -> str:
    """
    調用 GPT-5 Responses API
    
    參數：
        prompt: 提示詞
        llm_params: 模型參數
        **kwargs: 額外參數
        
    返回：
        str: 生成的文本
    """
    try:
        client = OpenAI()
        
        # 添加 SSL 驗證禁用選項，解決企業網路環境的證書問題
        import httpx
        import os
        
        # 檢查環境變數，允許用戶控制 SSL 驗證
        disable_ssl_verify = os.getenv('DISABLE_SSL_VERIFY', 'false').lower() == 'true'
        if disable_ssl_verify:
            client._client = httpx.Client(verify=False)
            logger.warning("⚠️ SSL 驗證已禁用（環境變數控制）")
        else:
            # 嘗試使用預設設置，如果失敗則自動禁用
            try:
                # 測試連接
                test_client = httpx.Client()
                test_client.close()
            except Exception as e:
                if "certificate verify failed" in str(e).lower():
                    client._client = httpx.Client(verify=False)
                    logger.warning("⚠️ 檢測到 SSL 證書問題，自動禁用 SSL 驗證")
                else:
                    raise e
        
        # 構建 Responses API 參數 - 使用 input 而不是 prompt
        responses_params = {
            "model": llm_params.get("model", "gpt-5"),
            "input": [{"role": "user", "content": prompt}],  # 修正：使用 input 而不是 prompt
            "max_output_tokens": llm_params.get("max_output_tokens", 2000),
            "timeout": llm_params.get("timeout", 60)
        }
        
        # 添加可選參數
        if "reasoning_effort" in llm_params:
            responses_params["reasoning"] = {"effort": llm_params["reasoning_effort"]}
        if "verbosity" in llm_params:
            responses_params["text"] = {"verbosity": llm_params["verbosity"]}
        if "temperature" in llm_params:
            responses_params["temperature"] = llm_params["temperature"]
        
        logger.debug(f"使用 Responses API，參數：{responses_params}")
        
        # 重試機制
        max_retries = 3
        base_tokens = llm_params.get("max_output_tokens", 2000)
        
        for retry_count in range(max_retries):
            # 每次重試時增加 1000 tokens
            current_tokens = base_tokens + (retry_count * 1000)
            responses_params["max_output_tokens"] = current_tokens
            
            logger.info(f"嘗試 {retry_count + 1}/{max_retries}，使用 {current_tokens} tokens")
            
            try:
                response = client.responses.create(**responses_params)
                
                # 檢查響應狀態
                if hasattr(response, 'status') and response.status == 'incomplete':
                    logger.warning(f"檢測到 incomplete 狀態，嘗試提取部分內容")
                    
                    # 對於非結構化輸出，嘗試提取部分文本
                    if hasattr(response, 'output_text') and response.output_text:
                        output = response.output_text
                        logger.info(f"從 incomplete 響應中提取部分文本: {len(output)} 字符")
                        return output
                    
                    # 如果無法提取部分內容，則重試
                    if retry_count < max_retries - 1:
                        logger.warning(f"無法提取部分內容，重試 {retry_count + 1}/{max_retries}")
                        time.sleep(2)
                        continue
                
                # 提取文本內容
                if hasattr(response, 'output_text') and response.output_text:
                    output = response.output_text
                    logger.info(f"成功提取文本: {len(output)} 字符")
                    return output
                elif hasattr(response, 'output') and response.output:
                    # 從 output 陣列中提取文本
                    output_parts = []
                    for item in response.output:
                        if hasattr(item, 'message') and hasattr(item.message, 'content'):
                            for content in item.message.content:
                                if hasattr(content, 'text') and content.text:
                                    output_parts.append(content.text)
                    output = "".join(output_parts)
                    if output:
                        logger.info(f"成功提取文本: {len(output)} 字符")
                        return output
                
                # 如果都失敗了，嘗試使用 content
                if hasattr(response, 'content'):
                    output = response.content
                    logger.info(f"使用 content 提取文本: {len(output)} 字符")
                    return output
                    
            except Exception as e:
                logger.error(f"API 調用失敗 (嘗試 {retry_count + 1}/{max_retries}): {e}")
                if retry_count < max_retries - 1:
                    time.sleep(2)
                    continue
                raise
        
        raise APIRequestError("所有重試都失敗")
        
    except Exception as e:
        logger.error(f"GPT-5 Responses API 調用失敗: {e}")
        raise


def _call_gpt4_chat_api(prompt: str, llm_params: Dict[str, Any], **kwargs) -> str:
    """
    調用 GPT-4 Chat Completions API
    
    參數：
        prompt: 提示詞
        llm_params: 模型參數
        **kwargs: 額外參數
        
    返回：
        str: 生成的文本
    """
    try:
        client = OpenAI()
        
        # 構建 Chat Completions API 參數
        chat_params = {
            "model": llm_params.get("model", "gpt-4"),
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": llm_params.get("max_tokens", 2000),
            "temperature": llm_params.get("temperature", 0.7)
        }
        
        logger.debug(f"使用 Chat Completions API，參數：{chat_params}")
        
        response = client.chat.completions.create(**chat_params)
        
        if response.choices and response.choices[0].message:
            output = response.choices[0].message.content
            logger.info(f"Chat API 調用成功，回應長度：{len(output)} 字符")
            return output
        else:
            raise APIRequestError("Chat API 返回空響應")
            
    except Exception as e:
        logger.error(f"Chat Completions API 調用失敗：{e}")
        raise


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
        
        # 🔍 [DEBUG] 參數追蹤：檢查 call_structured_llm 中的參數
        logger.info(f"🔍 [DEBUG] call_structured_llm 參數追蹤:")
        logger.info(f"🔍 [DEBUG] - current_model: {current_model}")
        logger.info(f"🔍 [DEBUG] - llm_params 類型: {type(llm_params)}")
        logger.info(f"🔍 [DEBUG] - llm_params 內容: {llm_params}")
        logger.info(f"🔍 [DEBUG] - llm_params.get('reasoning'): {llm_params.get('reasoning')}")
        logger.info(f"🔍 [DEBUG] - llm_params.get('reasoning_effort'): {llm_params.get('reasoning_effort')}")
        logger.info(f"🔍 [DEBUG] - llm_params.get('text'): {llm_params.get('text')}")
        logger.info(f"🔍 [DEBUG] - llm_params.get('verbosity'): {llm_params.get('verbosity')}")
        
        logger.info(f"調用結構化 LLM，模型：{current_model}")
        
        # 只支援 GPT-5 系列
        if not current_model.startswith('gpt-5'):
            raise LLMError(f"不支援的模型：{current_model}，只支援 GPT-5 系列")
        
        return _call_gpt5_structured_api(prompt, schema, llm_params, **kwargs)
            
    except Exception as e:
        logger.error(f"結構化 LLM 調用失敗：{e}")
        raise LLMError(f"結構化 LLM 調用失敗：{str(e)}")


def _call_gpt5_structured_api(prompt: str, schema: Dict[str, Any], llm_params: Dict[str, Any], **kwargs) -> Dict[str, Any]:
    """
    調用 GPT-5 結構化 API
    
    參數：
        prompt: 提示詞
        schema: JSON Schema
        llm_params: 模型參數
        **kwargs: 額外參數
        
    返回：
        Dict[str, Any]: 結構化數據
    """
    try:
        client = OpenAI()
        
        # 添加 SSL 驗證禁用選項，解決企業網路環境的證書問題
        import httpx
        import os
        
        # 檢查環境變數，允許用戶控制 SSL 驗證
        disable_ssl_verify = os.getenv('DISABLE_SSL_VERIFY', 'false').lower() == 'true'
        if disable_ssl_verify:
            client._client = httpx.Client(verify=False)
            logger.warning("⚠️ SSL 驗證已禁用（環境變數控制）")
        else:
            # 嘗試使用預設設置，如果失敗則自動禁用
            try:
                # 測試連接
                test_client = httpx.Client()
                test_client.close()
            except Exception as e:
                if "certificate verify failed" in str(e).lower():
                    client._client = httpx.Client(verify=False)
                    logger.warning("⚠️ 檢測到 SSL 證書問題，自動禁用 SSL 驗證")
                else:
                    raise e
        
        # 🔍 [DEBUG] 參數追蹤：檢查輸入的 llm_params
        logger.info(f"🔍 [DEBUG] _call_gpt5_structured_api 輸入參數:")
        logger.info(f"🔍 [DEBUG] - llm_params 類型: {type(llm_params)}")
        logger.info(f"🔍 [DEBUG] - llm_params 內容: {llm_params}")
        logger.info(f"🔍 [DEBUG] - llm_params.get('reasoning'): {llm_params.get('reasoning')}")
        logger.info(f"🔍 [DEBUG] - llm_params.get('reasoning_effort'): {llm_params.get('reasoning_effort')}")
        logger.info(f"🔍 [DEBUG] - llm_params.get('text'): {llm_params.get('text')}")
        logger.info(f"🔍 [DEBUG] - llm_params.get('verbosity'): {llm_params.get('verbosity')}")
        
        # 構建 Responses API 參數
        responses_params = {
            "model": llm_params.get("model", "gpt-5"),
            "input": [{"role": "user", "content": prompt}],
            "text": {
                "format": {
                    "type": "json_schema",
                    "name": "ResearchProposal",
                    "strict": True,
                    "schema": schema,
                },
                "verbosity": llm_params.get("verbosity", "low")
            },
            "max_output_tokens": llm_params.get("max_output_tokens", 2000),
            "timeout": llm_params.get("timeout", 60)
        }
        
        # 🔍 [DEBUG] 參數追蹤：檢查是否已經有適配過的參數
        if 'reasoning' in llm_params:
            logger.info(f"🔍 [DEBUG] 使用適配後的 reasoning 參數: {llm_params['reasoning']}")
            responses_params['reasoning'] = llm_params['reasoning']
        else:
            logger.info(f"🔍 [DEBUG] 使用默認 reasoning 參數")
            responses_params['reasoning'] = {"effort": llm_params.get("reasoning_effort", "medium")}
        
        if 'text' in llm_params:
            logger.info(f"🔍 [DEBUG] 使用適配後的 text 參數: {llm_params['text']}")
            # 保留 JSON Schema 格式信息，只更新 verbosity
            if 'verbosity' in llm_params['text']:
                responses_params['text']['verbosity'] = llm_params['text']['verbosity']
            logger.info(f"🔍 [DEBUG] 更新後的 text 參數: {responses_params['text']}")
        else:
            logger.info(f"🔍 [DEBUG] 使用默認 text 參數")
            responses_params['text']['verbosity'] = llm_params.get("verbosity", "low")
        
        # 🔍 [DEBUG] 參數追蹤：檢查構建的 responses_params
        logger.info(f"🔍 [DEBUG] 構建的 responses_params:")
        logger.info(f"🔍 [DEBUG] - responses_params 類型: {type(responses_params)}")
        logger.info(f"🔍 [DEBUG] - responses_params 內容: {responses_params}")
        logger.info(f"🔍 [DEBUG] - responses_params['reasoning']: {responses_params['reasoning']}")
        logger.info(f"🔍 [DEBUG] - responses_params['text']: {responses_params['text']}")
        
        # 🔍 [DEBUG] 檢查 JSON Schema 格式信息
        if 'text' in responses_params and 'format' in responses_params['text']:
            logger.info(f"🔍 [DEBUG] JSON Schema 格式信息存在:")
            logger.info(f"🔍 [DEBUG] - format.type: {responses_params['text']['format'].get('type', 'missing')}")
            logger.info(f"🔍 [DEBUG] - format.name: {responses_params['text']['format'].get('name', 'missing')}")
            logger.info(f"🔍 [DEBUG] - format.strict: {responses_params['text']['format'].get('strict', 'missing')}")
            logger.info(f"🔍 [DEBUG] - schema 存在: {'schema' in responses_params['text']['format']}")
        else:
            logger.warning(f"⚠️ [DEBUG] JSON Schema 格式信息缺失!")
            logger.warning(f"⚠️ [DEBUG] text 鍵存在: {'text' in responses_params}")
            if 'text' in responses_params:
                logger.warning(f"⚠️ [DEBUG] text 內容: {responses_params['text']}")
                logger.warning(f"⚠️ [DEBUG] format 鍵存在: {'format' in responses_params['text']}")
        
        # 🔍 [DEBUG] 參數追蹤：參數已經在構建時正確處理
        
        logger.debug(f"使用 Responses API with JSON Schema，參數：{responses_params}")
        
        # 重試機制
        max_retries = 3
        base_tokens = llm_params.get("max_output_tokens", 2000)
        
        for retry_count in range(max_retries):
            # 每次重試時增加 1000 tokens
            current_tokens = base_tokens + (retry_count * 1000)
            responses_params["max_output_tokens"] = current_tokens
            
            logger.info(f"嘗試 {retry_count + 1}/{max_retries}，使用 {current_tokens} tokens")
            
            try:
                response = client.responses.create(**responses_params)
                
                # 檢查響應狀態
                if hasattr(response, 'status') and response.status == 'incomplete':
                    logger.warning(f"檢測到 incomplete 狀態，嘗試提取部分內容")
                    
                    # 嘗試從 incomplete 響應中提取部分 JSON
                    partial_json = _extract_partial_json_from_response(response)
                    if partial_json:
                        logger.info("成功從 incomplete 響應中提取部分 JSON")
                        return partial_json
                    
                    # 如果無法提取部分內容，則重試
                    if retry_count < max_retries - 1:
                        logger.warning(f"無法提取部分內容，重試 {retry_count + 1}/{max_retries}")
                        time.sleep(2)
                        continue
                
                # 提取 JSON 內容
                if hasattr(response, 'output_text') and response.output_text:
                    try:
                        result = json.loads(response.output_text)
                        logger.info("成功解析 JSON 結構化提案")
                        return result
                    except json.JSONDecodeError as e:
                        logger.error(f"JSON 解析失敗: {e}")
                        logger.debug(f"嘗試的文本: {response.output_text[:200]}...")
                
                # 如果 output_text 失敗，嘗試從 output 提取
                if hasattr(response, 'output') and response.output:
                    text_content = ""
                    for item in response.output:
                        if hasattr(item, 'message') and hasattr(item.message, 'content'):
                            for content in item.message.content:
                                if hasattr(content, 'text') and content.text:
                                    text_content += content.text
                    
                    if text_content:
                        try:
                            result = json.loads(text_content)
                            logger.info("成功解析 JSON 結構化提案")
                            return result
                        except json.JSONDecodeError as e:
                            logger.error(f"JSON 解析失敗: {e}")
                            logger.debug(f"嘗試的文本: {text_content[:200]}...")
                
                logger.warning("無法從 Responses API 提取 JSON 內容")
                
            except Exception as e:
                logger.error(f"API 調用失敗 (嘗試 {retry_count + 1}/{max_retries}): {e}")
                if retry_count < max_retries - 1:
                    time.sleep(2)
                    continue
                raise
        
        raise APIRequestError("所有重試都失敗")
        
    except Exception as e:
        logger.error(f"GPT-5 結構化 API 調用失敗: {e}")
        raise


# _call_gpt4_structured_api 函數已移除 - 不再支援 GPT-4 系列


# generate_proposal_with_fallback 函數已移除 - 不再支援非結構化輸出 fallback


def _extract_partial_json_from_response(response) -> Optional[Dict[str, Any]]:
    """
    從 incomplete 響應中提取部分 JSON 內容
    
    Args:
        response: OpenAI Responses API 響應對象
        
    Returns:
        Optional[Dict[str, Any]]: 提取的 JSON 對象，如果失敗則返回 None
    """
    try:
        # 嘗試從 output_text 提取
        if hasattr(response, 'output_text') and response.output_text:
            text = response.output_text
            logger.debug(f"嘗試從 output_text 提取部分 JSON: {text[:200]}...")
            
            # 嘗試找到最後一個完整的 JSON 對象
            brace_count = 0
            last_complete_pos = -1
            
            for i, char in enumerate(text):
                if char == '{':
                    brace_count += 1
                elif char == '}':
                    brace_count -= 1
                    if brace_count == 0:
                        last_complete_pos = i
            
            if last_complete_pos > 0:
                complete_json = text[:last_complete_pos + 1]
                try:
                    result = json.loads(complete_json)
                    logger.info(f"成功修復不完整的 JSON，長度: {len(complete_json)} 字符")
                    return result
                except json.JSONDecodeError as e:
                    logger.debug(f"JSON 修復失敗: {e}")
        
        # 嘗試從 output 陣列提取
        if hasattr(response, 'output') and response.output:
            text_content = ""
            for item in response.output:
                if hasattr(item, 'message') and hasattr(item.message, 'content'):
                    for content in item.message.content:
                        if hasattr(content, 'text') and content.text:
                            text_content += content.text
            
            if text_content:
                logger.debug(f"嘗試從 output 陣列提取部分 JSON: {text_content[:200]}...")
                
                # 同樣嘗試修復不完整的 JSON
                brace_count = 0
                last_complete_pos = -1
                
                for i, char in enumerate(text_content):
                    if char == '{':
                        brace_count += 1
                    elif char == '}':
                        brace_count -= 1
                        if brace_count == 0:
                            last_complete_pos = i
                
                if last_complete_pos > 0:
                    complete_json = text_content[:last_complete_pos + 1]
                    try:
                        result = json.loads(complete_json)
                        logger.info(f"成功從 output 陣列修復不完整的 JSON，長度: {len(complete_json)} 字符")
                        return result
                    except json.JSONDecodeError as e:
                        logger.debug(f"output 陣列 JSON 修復失敗: {e}")
        
        logger.warning("無法從 incomplete 響應中提取有效的 JSON 內容")
        return None
        
    except Exception as e:
        logger.error(f"提取部分 JSON 時發生錯誤: {e}")
        return None


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
