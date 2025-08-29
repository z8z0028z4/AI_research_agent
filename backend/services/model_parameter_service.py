"""
模型參數檢測和適配器
用於動態檢測不同OpenAI模型的支援參數並進行適配
基於GPT-5官方cookbook的最新參數支援
"""

import json
import logging
from typing import Dict, Any, List, Optional
from openai import OpenAI
import time

logger = logging.getLogger(__name__)

class ModelParameterDetector:
    """模型參數檢測器"""
    
    def __init__(self, api_key: str = None):
        self.client = OpenAI(api_key=api_key)
        self.cache = {}  # 快取檢測結果
        
    def detect_model_parameters(self, model_name: str) -> Dict[str, Any]:
        """
        檢測指定模型支援的參數
        
        Args:
            model_name: 模型名稱
            
        Returns:
            包含支援參數資訊的字典
        """
        # 檢查快取
        if model_name in self.cache:
            logger.info(f"使用快取的模型參數: {model_name}")
            return self.cache[model_name]
        
        logger.info(f"開始檢測模型參數: {model_name}")
        
        # 根據cookbook，GPT-5系列使用Responses API
        if model_name.startswith('gpt-5'):
            # GPT-5系列支援的參數（Responses API）
            supported_params = {
                'max_tokens': {
                    'type': 'int', 
                    'range': [1, 32000], 
                    'default': 2000,
                    'api_name': 'max_output_tokens',  # 修正：Responses API使用max_output_tokens
                    'description': '控制回應的最大長度'
                },
                'timeout': {
                    'type': 'int', 
                    'range': [10, 600], 
                    'default': 60,
                    'api_name': 'timeout',
                    'description': 'API調用超時時間'
                },
                'reasoning_effort': {
                    'type': 'select', 
                    'options': ['minimal', 'low', 'medium', 'high'], 
                    'default': 'medium',
                    'api_name': 'reasoning.effort',
                    'description': '控制推理密度和成本'
                },
                'verbosity': {
                    'type': 'select', 
                    'options': ['low', 'medium', 'high'], 
                    'default': 'medium',
                    'api_name': 'text.verbosity',
                    'description': '控制回應的詳細程度'
                }
            }
            
            # 如果是GPT-5完整版，還支援temperature
            if model_name == 'gpt-5':
                supported_params['temperature'] = {
                    'type': 'float', 
                    'range': [0.0, 2.0], 
                    'default': 0.7,
                    'api_name': 'temperature',
                    'description': '控制回應的隨機性'
                }
                
        else:
            # 不支援的模型系列
            raise ValueError(f"不支援的模型：{model_name}，僅支援 GPT-5 系列")
        
        result = {
            'model_name': model_name,
            'supported_parameters': supported_params,
            'api_type': 'responses' if model_name.startswith('gpt-5') else 'chat_completions',
            'detection_time': time.time()
        }
        
        # 快取結果
        self.cache[model_name] = result
        logger.info(f"模型參數檢測完成: {model_name}")
        
        return result
    
    def adapt_parameters(self, model_name: str, user_params: Dict[str, Any]) -> Dict[str, Any]:
        """
        適配用戶參數到實際API調用格式
        
        Args:
            model_name: 模型名稱
            user_params: 用戶提供的參數
            
        Returns:
            適配後的參數字典
        """
        # 獲取模型參數資訊
        model_info = self.detect_model_parameters(model_name)
        supported_params = model_info['supported_parameters']
        
        # 適配參數
        adapted_params = {'model': model_name}
        
        # 添加調試日誌
        logger.info(f"🔍 [DEBUG] 開始參數適配")
        logger.info(f"🔍 [DEBUG] 模型名稱: {model_name}")
        logger.info(f"🔍 [DEBUG] 用戶參數: {user_params}")
        logger.info(f"🔍 [DEBUG] 支援參數: {list(supported_params.keys())}")
        
        for param_name, param_value in user_params.items():
            logger.info(f"🔍 [DEBUG] 處理參數: {param_name} = {param_value}")
            
            # 特殊處理：將 max_tokens 映射到 max_output_tokens（GPT-5系列）
            if param_name == 'max_tokens' and model_name.startswith('gpt-5'):
                adapted_params['max_output_tokens'] = param_value
                logger.info(f"🔍 [DEBUG] 映射 max_tokens -> max_output_tokens: {param_value}")
                continue
                
            if param_name not in supported_params:
                logger.warning(f"跳過不支援的參數: {param_name}")
                continue
                
            param_config = supported_params[param_name]
            api_name = param_config['api_name']
            logger.info(f"🔍 [DEBUG] 參數 {param_name} 的 API 名稱: {api_name}")
            
            # 根據API名稱進行適配
            if api_name == 'reasoning.effort':
                # 正確處理reasoning參數
                adapted_params['reasoning'] = {'effort': param_value}
                logger.info(f"🔍 [DEBUG] 設置 reasoning.effort: {param_value}")
            elif api_name == 'max_output_tokens':
                adapted_params['max_output_tokens'] = param_value
                logger.info(f"🔍 [DEBUG] 設置 max_output_tokens: {param_value}")
            elif api_name == 'text.verbosity':
                # 處理 verbosity 參數
                if 'text' not in adapted_params:
                    adapted_params['text'] = {}
                adapted_params['text']['verbosity'] = param_value
                logger.info(f"🔍 [DEBUG] 設置 text.verbosity: {param_value}")
            else:
                adapted_params[api_name] = param_value
                logger.info(f"🔍 [DEBUG] 設置 {api_name}: {param_value}")
                
        logger.info(f"🔍 [DEBUG] 參數適配完成: {adapted_params}")
        return adapted_params
    
    def create_cfg_tool(self, grammar_definition: str, tool_name: str = "custom_grammar") -> Dict[str, Any]:
        """
        創建CFG工具（Context-Free Grammar）
        
        Args:
            grammar_definition: 語法定義（Lark或Regex格式）
            tool_name: 工具名稱
            
        Returns:
            CFG工具配置
        """
        return {
            "type": "custom",
            "name": tool_name,
            "description": "Emit ONLY output valid under the specified grammar.",
            "format": {
                "type": "grammar",
                "syntax": "regex",  # 或 "lark"
                "definition": grammar_definition
            }
        }
    
    def create_response_format(self, format_type: str = "json_object") -> Dict[str, Any]:
        """
        創建回應格式配置
        
        Args:
            format_type: 格式類型（json_object, text等）
            
        Returns:
            回應格式配置
        """
        return {"type": format_type}
    
    def get_model_info_summary(self, model_name: str) -> Dict[str, Any]:
        """
        獲取模型資訊摘要
        """
        model_info = self.detect_model_parameters(model_name)
        
        return {
            'model_name': model_name,
            'supported_parameters': list(model_info['supported_parameters'].keys()),
            'parameter_count': len(model_info['supported_parameters']),
            'api_type': model_info['api_type'],
            'is_gpt5_series': model_name.startswith('gpt-5'),
            'detection_time': model_info['detection_time']
        }
    
    def test_model_call(self, model_name: str, test_params: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        測試模型調用
        
        Args:
            model_name: 模型名稱
            test_params: 測試參數
            
        Returns:
            測試結果
        """
        if test_params is None:
            test_params = {
                'max_tokens': 100,
                'timeout': 30
            }
            
            if model_name.startswith('gpt-5'):
                test_params.update({
                    'reasoning_effort': 'medium',
                    'verbosity': 'low'
                })
        
        try:
            # 適配參數
            adapted_params = self.adapt_parameters(model_name, test_params)
            
            # 根據API類型選擇調用方式
            if model_name.startswith('gpt-5'):
                # 使用Responses API
                adapted_params['input'] = [
                    {'role': 'user', 'content': 'Hello, please respond with "Test successful"'}
                ]
                
                response = self.client.responses.create(**adapted_params)
                
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
                
                result = {
                    'success': True,
                    'response': output,
                    'api_type': 'responses'
                }
            else:
                # 使用Chat Completions API
                adapted_params['messages'] = [
                    {'role': 'user', 'content': 'Hello, please respond with "Test successful"'}
                ]
                
                response = self.client.chat.completions.create(**adapted_params)
                result = {
                    'success': True,
                    'response': response.choices[0].message.content,
                    'api_type': 'chat_completions'
                }
                
            return result
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'api_type': 'responses' if model_name.startswith('gpt-5') else 'chat_completions'
            }
    
    def clear_cache(self):
        """清除快取"""
        self.cache.clear()
        logger.info("模型參數快取已清除")
    
    def export_cache(self, filepath: str):
        """匯出快取到檔案"""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.cache, f, indent=2, ensure_ascii=False)
        logger.info(f"快取已匯出到: {filepath}")
    
    def import_cache(self, filepath: str):
        """從檔案匯入快取"""
        with open(filepath, 'r', encoding='utf-8') as f:
            self.cache = json.load(f)
        logger.info(f"快取已從檔案匯入: {filepath}")


# 全域檢測器實例
_detector = None

def get_detector(api_key: str = None) -> ModelParameterDetector:
    """獲取全域檢測器實例"""
    global _detector
    if _detector is None:
        _detector = ModelParameterDetector(api_key)
    return _detector

def detect_model_parameters(model_name: str, api_key: str = None) -> Dict[str, Any]:
    """便捷函數：檢測模型參數"""
    detector = get_detector(api_key)
    return detector.detect_model_parameters(model_name)

def adapt_parameters(model_name: str, user_params: Dict[str, Any], api_key: str = None) -> Dict[str, Any]:
    """便捷函數：適配參數"""
    detector = get_detector(api_key)
    return detector.adapt_parameters(model_name, user_params)

def test_model_call(model_name: str, test_params: Dict[str, Any] = None, api_key: str = None) -> Dict[str, Any]:
    """便捷函數：測試模型調用"""
    detector = get_detector(api_key)
    return detector.test_model_call(model_name, test_params)

def create_cfg_tool(grammar_definition: str, tool_name: str = "custom_grammar", api_key: str = None) -> Dict[str, Any]:
    """便捷函數：創建CFG工具"""
    detector = get_detector(api_key)
    return detector.create_cfg_tool(grammar_definition, tool_name)

def create_response_format(format_type: str = "json_object", api_key: str = None) -> Dict[str, Any]:
    """便捷函數：創建回應格式配置"""
    detector = get_detector(api_key)
    return detector.create_response_format(format_type) 