"""
生成模組
========

負責 LLM 調用和內容生成
"""

import time
import json
from typing import Dict, Any, Optional, List
from openai import OpenAI

from ..utils.logger import get_logger
from ..utils.exceptions import ModelError, APIError
from ..model_config_bridge import get_model_params, get_current_model

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
        raise ModelError(f"LLM 調用失敗：{str(e)}")


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
        
        # 構建 Responses API 參數
        responses_params = {
            "model": llm_params.get("model", "gpt-5"),
            "prompt": prompt,
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
        for retry_count in range(max_retries):
            try:
                response = client.responses.create(**responses_params)
                
                # 檢查響應狀態
                if hasattr(response, 'status') and response.status == 'incomplete':
                    logger.warning(f"檢測到 incomplete 狀態，重試 {retry_count + 1}/{max_retries}")
                    if retry_count < max_retries - 1:
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
        
        raise APIError("所有重試都失敗")
        
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
            raise APIError("Chat API 返回空響應")
            
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
        
        logger.info(f"調用結構化 LLM，模型：{current_model}")
        
        if current_model.startswith('gpt-5'):
            return _call_gpt5_structured_api(prompt, schema, llm_params, **kwargs)
        else:
            return _call_gpt4_structured_api(prompt, schema, llm_params, **kwargs)
            
    except Exception as e:
        logger.error(f"結構化 LLM 調用失敗：{e}")
        raise ModelError(f"結構化 LLM 調用失敗：{str(e)}")


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
        
        # 構建 Responses API 參數
        responses_params = {
            "model": llm_params.get("model", "gpt-5"),
            "prompt": prompt,
            "max_output_tokens": llm_params.get("max_output_tokens", 2000),
            "timeout": llm_params.get("timeout", 60),
            "response_format": {"type": "json_object"},
            "json_schema": schema
        }
        
        logger.debug(f"使用 Responses API with JSON Schema，參數：{responses_params}")
        
        # 重試機制
        max_retries = 3
        for retry_count in range(max_retries):
            try:
                response = client.responses.create(**responses_params)
                
                # 檢查響應狀態
                if hasattr(response, 'status') and response.status == 'incomplete':
                    logger.warning(f"檢測到 incomplete 狀態，重試 {retry_count + 1}/{max_retries}")
                    if retry_count < max_retries - 1:
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
        
        raise APIError("所有重試都失敗")
        
    except Exception as e:
        logger.error(f"GPT-5 結構化 API 調用失敗: {e}")
        raise


def _call_gpt4_structured_api(prompt: str, schema: Dict[str, Any], llm_params: Dict[str, Any], **kwargs) -> Dict[str, Any]:
    """
    調用 GPT-4 結構化 API (使用 function calling)
    
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
        
        # 構建 function calling 參數
        function_params = {
            "model": llm_params.get("model", "gpt-4"),
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": llm_params.get("max_tokens", 2000),
            "temperature": llm_params.get("temperature", 0.7),
            "functions": [{
                "name": "generate_proposal",
                "description": "生成研究提案",
                "parameters": schema
            }],
            "function_call": {"name": "generate_proposal"}
        }
        
        logger.debug(f"使用 function calling API，參數：{function_params}")
        
        response = client.chat.completions.create(**function_params)
        
        if (response.choices and response.choices[0].message and 
            response.choices[0].message.function_call):
            
            function_call = response.choices[0].message.function_call
            if function_call.arguments:
                try:
                    result = json.loads(function_call.arguments)
                    logger.info("成功解析 function call 結構化提案")
                    return result
                except json.JSONDecodeError as e:
                    logger.error(f"Function call JSON 解析失敗: {e}")
                    raise
            else:
                raise APIError("無法從 function call 提取結果")
        else:
            raise APIError("Function call 調用失敗")
            
    except Exception as e:
        logger.error(f"Function calling API 調用失敗：{e}")
        raise


def generate_proposal_with_fallback(
    prompt: str, 
    schema: Dict[str, Any], 
    **kwargs
) -> Dict[str, Any]:
    """
    生成提案，帶有回退機制
    
    參數：
        prompt: 提示詞
        schema: JSON Schema
        **kwargs: 額外參數
        
    返回：
        Dict[str, Any]: 生成的提案
    """
    try:
        # 首先嘗試結構化生成
        return call_structured_llm(prompt, schema, **kwargs)
    except Exception as e:
        logger.warning(f"結構化生成失敗，嘗試非結構化生成: {e}")
        try:
            # 回退到非結構化生成
            response = call_llm(prompt, **kwargs)
            # 嘗試解析 JSON
            try:
                return json.loads(response)
            except json.JSONDecodeError:
                # 如果無法解析 JSON，返回原始文本
                return {"raw_response": response}
        except Exception as fallback_error:
            logger.error(f"回退生成也失敗: {fallback_error}")
            raise ModelError(f"所有生成方式都失敗: {str(e)}, {str(fallback_error)}")
