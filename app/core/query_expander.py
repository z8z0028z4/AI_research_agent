"""
查詢擴展模組
==========

負責將用戶的自然語言查詢擴展為多個語義搜索查詢
"""

from typing import List
import json

from app.utils.logger import get_logger
from app.model_config_bridge import get_current_model, get_model_params

logger = get_logger(__name__)


def expand_query(user_prompt: str) -> List[str]:
    """
    將用戶輸入的自然語言問題轉換為多個語義搜索查詢語句。
    返回的英文語句可用於文獻向量檢索。
    
    Args:
        user_prompt: 用戶輸入的查詢
        
    Returns:
        List[str]: 擴展後的查詢列表
    """
    # 獲取動態模型參數
    try:
        current_model = get_current_model()
        llm_params = get_model_params()
    except Exception as e:
        logger.error(f"❌ 無法獲取模型參數：{e}")
        raise Exception(f"無法獲取模型參數：{str(e)}")

    system_prompt = """You are a scientific assistant helping expand a user's synthesis question into multiple semantic search queries. 
    Each query should be precise, relevant, and useful for retrieving related technical documents. 
    Only return a list of 3 to 6 search queries in English. Do not explain, do not include numbering if not needed."""

    full_prompt = f"{system_prompt}\n\nUser question:\n{user_prompt}"

    try:
        # 根據模型類型選擇不同的API
        if current_model.startswith('gpt-5'):
            # GPT-5系列使用Responses API
            from openai import OpenAI
            client = OpenAI()
            
            # 準備Responses API的參數
            responses_params = {
                'model': current_model,
                'input': [{'role': 'user', 'content': full_prompt}]
            }
            
            # 添加其他參數（排除model和input）
            for key, value in llm_params.items():
                if key not in ['model', 'input']:
                    responses_params[key] = value
            
            # 修復：移除reasoning參數，避免返回ResponseReasoningItem
            if 'reasoning' in responses_params:
                del responses_params['reasoning']
            
            # 確保移除reasoning參數
            if 'reasoning' in responses_params:
                logger.debug(f"🔍 DEBUG: 移除 reasoning 參數: {responses_params['reasoning']}")
                del responses_params['reasoning']
                logger.debug(f"🔍 DEBUG: 更新後的參數: {responses_params}")
            
            response = client.responses.create(**responses_params)
            
            # 修復：根據GPT-5 cookbook正確處理Responses API的回應格式
            output = ""
            if hasattr(response, 'output') and response.output:
                for item in response.output:
                    # 跳過ResponseReasoningItem對象
                    if hasattr(item, 'type') and item.type == 'reasoning':
                        continue
                    
                    if hasattr(item, "content"):
                        for content in item.content:
                            if hasattr(content, "text"):
                                output += content.text
                    elif hasattr(item, "text"):
                        # 直接文本輸出
                        output += item.text
                    elif hasattr(item, "message"):
                        # message對象
                        if hasattr(item.message, "content"):
                            output += item.message.content
                        else:
                            output += str(item.message)
                    else:
                        # 其他情況，嘗試轉換為字符串，但過濾掉ResponseReasoningItem
                        item_str = str(item)
                        if not item_str.startswith('ResponseReasoningItem'):
                            output += item_str
            
            output = output.strip()
            
        else:
            logger.error(f"❌ 不支援的模型：{current_model}，僅支援 GPT-5 系列")
            raise Exception(f"不支援的模型：{current_model}，僅支援 GPT-5 系列")

        # 解析查詢列表
        queries = [line.strip("-• ").strip() for line in output.split("\n") if line.strip()]
        return [q for q in queries if len(q) > 4]
        
    except Exception as e:
        logger.error(f"❌ 查詢擴展失敗：{e}")
        raise Exception(f"查詢擴展失敗：{str(e)}")


def expand_query_with_fallback(user_prompt: str) -> List[str]:
    """
    查詢擴展功能（已移除 fallback）
    
    Args:
        user_prompt: 用戶輸入的查詢
        
    Returns:
        List[str]: 擴展後的查詢列表
    """
    return expand_query(user_prompt)
