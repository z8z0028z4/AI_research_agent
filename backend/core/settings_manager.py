"""
設定管理器
========

管理應用程序的動態設定，包括模型選擇等
"""

import json
import os
from pathlib import Path
from typing import Optional, Dict, Any
from .config import settings

class SettingsManager:
    """設定管理器類"""
    
    def __init__(self):
        # 始終使用項目根目錄的settings.json文件
        # 從當前文件位置向上找到項目根目錄
        current_file = Path(__file__)
        project_root = current_file.parent.parent.parent  # backend/core -> backend -> project_root
        self.settings_file = project_root / "settings.json"
        
        # 調試：打印路徑信息
        print(f"🔧 SettingsManager 初始化:")
        print(f"   當前文件: {current_file}")
        print(f"   項目根目錄: {project_root}")
        print(f"   設定文件: {self.settings_file}")
        print(f"   設定文件存在: {self.settings_file.exists()}")
        
        self._current_settings = self._load_settings()
    
    def _load_settings(self) -> Dict[str, Any]:
        """載入設定文件"""
        if self.settings_file.exists():
            try:
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"載入設定文件錯誤: {e}")
                return {}
        return {}
    
    def _save_settings(self, settings_data: Dict[str, Any]):
        """儲存設定文件"""
        try:
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(settings_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"儲存設定文件錯誤: {e}")
            raise
    
    def get_setting(self, key: str, default: Any = None) -> Any:
        """獲取設定值"""
        return self._current_settings.get(key, default)
    
    def set_setting(self, key: str, value: Any):
        """設定值"""
        self._current_settings[key] = value
        self._save_settings(self._current_settings)
        
        # 如果是模型設定，同時更新全局設定
        if key == 'llm_model':
            settings.openai_model = value
    
    def get_embedding_model(self) -> str:
        """獲取當前嵌入模型"""
        return self.get_setting('embedding_model', 'BAAI/bge-small-zh-v1.5')

    def get_current_model(self) -> str:
        """獲取當前LLM模型"""
        return self.get_setting('llm_model', 'gpt-5-mini')
    
    def set_current_model(self, model: str):
        """設定當前LLM模型"""
        valid_models = [
            "gpt-5",
            "gpt-5-nano",
            "gpt-5-mini"
        ]
        
        if model not in valid_models:
            raise ValueError(f"無效的模型名稱: {model}")
        
        self.set_setting('llm_model', model)
    
    def get_llm_parameters(self) -> Dict[str, Any]:
        """獲取LLM參數設定"""
        return {
            "max_tokens": self.get_setting('llm_max_tokens', 4000),
            "timeout": self.get_setting('llm_timeout', 120),
            "reasoning_effort": self.get_setting('llm_reasoning_effort', 'medium'),
            "verbosity": self.get_setting('llm_verbosity', 'medium'),
        }
    
    def set_llm_parameters(self, max_tokens: int = None, 
                          timeout: int = None, reasoning_effort: str = None, 
                          verbosity: str = None):
        """設定LLM參數"""
        if max_tokens is not None:
            if not (1 <= max_tokens <= 32000):
                raise ValueError("max_tokens 必須在 1 到 32000 之間")
            self.set_setting('llm_max_tokens', max_tokens)
        
        if timeout is not None:
            if not (10 <= timeout <= 600):
                raise ValueError("timeout 必須在 10 到 600 秒之間")
            self.set_setting('llm_timeout', timeout)
        
        if reasoning_effort is not None:
            valid_efforts = ['minimal', 'low', 'medium', 'high']
            if reasoning_effort not in valid_efforts:
                raise ValueError(f"reasoning_effort 必須是以下之一: {valid_efforts}")
            self.set_setting('llm_reasoning_effort', reasoning_effort)
        
        if verbosity is not None:
            valid_verbosities = ['low', 'medium', 'high']
            if verbosity not in valid_verbosities:
                raise ValueError(f"verbosity 必須是以下之一: {valid_verbosities}")
            self.set_setting('llm_verbosity', verbosity)
    
    def get_model_supported_parameters(self, model_name: str = None) -> Dict[str, Any]:
        """獲取指定模型支援的參數"""
        if model_name is None:
            model_name = self.get_current_model()
        
        # GPT-5系列參數
        gpt5_params = {
            "max_tokens": {
                "type": "int",
                "range": [1, 32000],
                "default": 4000,
                "description": "回應的最大token數量"
            },
            "timeout": {
                "type": "int",
                "range": [10, 600],
                "default": 120,
                "description": "API調用的超時時間（秒）"
            },
            "reasoning_effort": {
                "type": "select",
                "options": ["minimal", "low", "medium", "high"],
                "default": "medium",
                "description": "控制推理密度和成本"
            },
            "verbosity": {
                "type": "select",
                "options": ["low", "medium", "high"],
                "default": "medium",
                "description": "控制輸出詳盡度"
            }
        }
        
        # 所有模型都是GPT-5系列
        return gpt5_params
    
    def get_json_schema_parameters(self) -> Dict[str, Any]:
        """獲取JSON Schema參數設定"""
        return {
            "min_length": self.get_setting('llm_min_length', 5),
            "max_length": self.get_setting('llm_max_length', 100),
        }
    
    def set_json_schema_parameters(self, min_length: int = None, max_length: int = None):
        """設定JSON Schema參數"""
        if min_length is not None:
            if not (1 <= min_length <= 50):
                raise ValueError("min_length 必須在 1 到 50 之間")
            self.set_setting('llm_min_length', min_length)
        
        if max_length is not None:
            if not (10 <= max_length <= 200):
                raise ValueError("max_length 必須在 10 到 200 之間")
            self.set_setting('llm_max_length', max_length)
    
    def get_json_schema_supported_parameters(self) -> Dict[str, Any]:
        """獲取JSON Schema支援的參數"""
        return {
            "min_length": {
                "type": "int",
                "range": [1, 50],
                "default": 5,
                "description": "JSON Schema 欄位最小長度約束"
            },
            "max_length": {
                "type": "int",
                "range": [10, 200],
                "default": 100,
                "description": "JSON Schema 欄位最大長度約束"
            }
        }
    
    def get_all_settings(self) -> Dict[str, Any]:
        """獲取所有設定"""
        return self._current_settings.copy()
    
    def reload_settings(self):
        """重新載入設定"""
        self._current_settings = self._load_settings()

# 創建全局設定管理器實例
settings_manager = SettingsManager() 