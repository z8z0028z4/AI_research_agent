"""
模型配置橋接模組
==============

橋接app目錄和backend目錄的模型配置
基於GPT-5官方cookbook的最新參數支援
"""

import os
import sys
from typing import Dict, Any

# 添加backend目錄到Python路徑
backend_path = os.path.join(os.path.dirname(__file__), "..", "backend")
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

try:
    from core.settings_manager import settings_manager
    from model_parameter_detector import adapt_parameters, detect_model_parameters
    
    def get_current_model():
        """獲取當前模型名稱"""
        return settings_manager.get_current_model()
    
    def get_model_params(model_name=None):
        """獲取模型參數"""
        if model_name is None:
            model_name = get_current_model()
        
        # 從設定管理器獲取動態參數
        llm_params = settings_manager.get_llm_parameters()
        
        # 使用新的參數適配器
        try:
            adapted_params = adapt_parameters(model_name, llm_params)
            print(f"🔧 模型參數適配完成: {adapted_params}")
            return adapted_params
        except Exception as e:
            print(f"⚠️ 參數適配失敗，使用基礎參數: {e}")
            # 如果適配失敗，使用基礎參數
            return {
                "model": model_name,
                "max_tokens": llm_params.get("max_tokens", 2000),
                "timeout": llm_params.get("timeout", 60),
            }
    
    def get_model_supported_parameters(model_name: str = None) -> Dict[str, Any]:
        """
        獲取指定模型支援的參數資訊
        
        Args:
            model_name: 模型名稱，如果為None則使用當前模型
            
        Returns:
            包含支援參數資訊的字典
        """
        if model_name is None:
            model_name = get_current_model()
        
        try:
            # 使用新的參數檢測器
            model_info = detect_model_parameters(model_name)
            return model_info['supported_parameters']
        except Exception as e:
            print(f"⚠️ 無法檢測模型參數，使用預設配置: {e}")
            # 如果檢測失敗，使用預設配置
            base_params = {
                'max_tokens': {'type': 'int', 'range': [1, 32000], 'default': 2000},
                'timeout': {'type': 'int', 'range': [10, 600], 'default': 60}
            }
            
            if model_name.startswith('gpt-5'):
                base_params.update({
                    'reasoning_effort': {
                        'type': 'select', 
                        'options': ['minimal', 'low', 'medium', 'high'], 
                        'default': 'medium'
                    },
                    'verbosity': {
                        'type': 'select', 
                        'options': ['low', 'medium', 'high'], 
                        'default': 'medium'
                    }
                })
            
            return base_params
    
    def is_model_available(model_name):
        """檢查模型是否可用"""
        valid_models = [
            "gpt-5",
            "gpt-5-nano",
            "gpt-5-mini"
        ]
        return model_name in valid_models

except ImportError as e:
    print(f"警告：無法導入backend設定模組: {e}")
    # 提供fallback配置
    def get_current_model():
        return "gpt-5-mini"
    
    def get_model_params(model_name=None):
        if model_name is None:
            model_name = get_current_model()
        return {
            "model": model_name,
            "max_tokens": 4000,
            "timeout": 120,
        }
    
    def get_model_supported_parameters(model_name: str = None) -> Dict[str, Any]:
        """獲取模型支援的參數（fallback版本）"""
        if model_name is None:
            model_name = get_current_model()
        
        base_params = {
            'max_tokens': {'type': 'int', 'range': [1, 32000], 'default': 2000},
            'timeout': {'type': 'int', 'range': [10, 600], 'default': 60}
        }
        
        if model_name.startswith('gpt-5'):
            base_params.update({
                'reasoning_effort': {
                    'type': 'select', 
                    'options': ['minimal', 'low', 'medium', 'high'], 
                    'default': 'medium'
                },
                'verbosity': {
                    'type': 'select', 
                    'options': ['low', 'medium', 'high'], 
                    'default': 'medium'
                }
            })
        
        return base_params
    
    def is_model_available(model_name):
        valid_models = [
            "gpt-5",
            "gpt-5-nano",
            "gpt-5-mini"
        ]
        return model_name in valid_models

# 為了向後兼容，提供舊的配置接口
def get_llm_params():
    """獲取LLM參數（向後兼容）"""
    return get_model_params()

def get_llm_model_name():
    """獲取LLM模型名稱（向後兼容）"""
    return get_current_model() 