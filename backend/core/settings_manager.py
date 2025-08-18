"""
設定管理器
========

管理應用程序的動態設定，包括模型選擇、OpenAI API等
"""

import json
import os
from pathlib import Path
from typing import Optional, Dict, Any
from .config import settings

class SettingsManager:
    """設定管理器類"""
    
    def __init__(self):
        # Use a robust method to find the project root and settings.json
        # Resolves the path of the current file and finds its grandparent's parent (project root)
        project_root = Path(__file__).resolve().parents[2]
        self.settings_file = project_root / "settings.json"
        self.env_file = project_root / ".env"
        
        # 調試：打印路徑信息
        print(f"🔧 SettingsManager 初始化:")
        print(f"   當前文件: {Path(__file__).resolve()}")
        print(f"   項目根目錄: {project_root}")
        print(f"   設定文件: {self.settings_file}")
        print(f"   設定文件存在: {self.settings_file.exists()}")
        print(f"   .env文件存在: {self.env_file.exists()}")
        
        # Load .env file if it exists
        self._load_env_file()
        
        self._current_settings = self._load_settings()
    
    def _load_env_file(self):
        """載入.env文件中的環境變量"""
        if self.env_file.exists():
            try:
                from dotenv import load_dotenv
                load_dotenv(self.env_file)
                print(f"✅ 已載入.env文件: {self.env_file}")
            except ImportError:
                print("⚠️ python-dotenv未安裝，跳過.env文件")
    
    def _load_settings(self) -> Dict[str, Any]:
        """載入設定文件"""
        # Default settings including OpenAI configurations
        default_settings = {
            "llm_model": "gpt-5-mini",
            "embedding_model": "text-embedding-3-small",  # OpenAI embedding model
            "openai_api_key": "",
            "openai_embedding_model": "text-embedding-3-small",
            "llm_max_tokens": 4000,
            "llm_timeout": 120,
            "llm_reasoning_effort": "medium",
            "llm_verbosity": "medium",
            "llm_min_length": 5,
            "llm_max_length": 100
        }
        
        if self.settings_file.exists():
            try:
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    loaded_settings = json.load(f)
                    # Merge loaded settings with defaults
                    default_settings.update(loaded_settings)
                    print(f"✅ 已載入設定文件")
            except Exception as e:
                print(f"載入設定文件錯誤: {e}")
                return default_settings
        else:
            # Create default settings file
            self._save_settings(default_settings)
            print(f"📝 已創建默認設定文件: {self.settings_file}")
        
        return default_settings
    
    def _save_settings(self, settings_data: Dict[str, Any]):
        """儲存設定文件"""
        try:
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(settings_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"儲存設定文件錯誤: {e}")
            raise
    
    def get_setting(self, key: str, default: Any = None) -> Any:
        """獲取設定值（優先順序：環境變量 > 設定文件）"""
        # First check environment variables
        env_key = key.upper()
        env_value = os.getenv(env_key)
        if env_value:
            return env_value
        
        # Then check settings file
        return self._current_settings.get(key, default)
    
    def set_setting(self, key: str, value: Any):
        """設定值"""
        self._current_settings[key] = value
        self._save_settings(self._current_settings)
        
        # 如果是模型設定，同時更新全局設定
        if key == 'llm_model':
            settings.openai_model = value
    
    def get_openai_api_key(self) -> Optional[str]:
        """獲取OpenAI API密鑰（優先順序：環境變量 > .env > 設定文件）"""
        # Priority: Environment variable > .env file > settings.json
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            api_key = self._current_settings.get("openai_api_key", "")
        return api_key if api_key else None
    
    def set_openai_api_key(self, api_key: str):
        """設定OpenAI API密鑰"""
        self.set_setting("openai_api_key", api_key)
    
    def validate_openai_key(self) -> bool:
        """驗證OpenAI API密鑰是否已配置"""
        api_key = self.get_openai_api_key()
        if not api_key or api_key == "your-openai-api-key-here" or not api_key.startswith("sk-"):
            print("❌ OpenAI API密鑰未配置或無效！")
            print("請使用以下方式之一設定您的API密鑰：")
            print("1. 設定環境變量: set OPENAI_API_KEY=sk-...")
            print("2. 添加到.env文件: OPENAI_API_KEY=sk-...")
            print("3. 添加到settings.json: {\"openai_api_key\": \"sk-...\"}")
            print("\n從這裡獲取您的API密鑰: https://platform.openai.com/api-keys")
            return False
        return True
    
    def get_embedding_model(self) -> str:
        """獲取當前嵌入模型（現在使用OpenAI）"""
        # Check environment variable first
        env_model = os.getenv("OPENAI_EMBEDDING_MODEL")
        if env_model:
            return env_model
        
        # For OpenAI embeddings
        return self.get_setting('openai_embedding_model', 'text-embedding-3-small')
    
    def set_embedding_model(self, model: str):
        """設定嵌入模型"""
        valid_openai_models = [
            "text-embedding-3-small",
            "text-embedding-3-large",
            "text-embedding-ada-002"
        ]
        
        if model in valid_openai_models:
            self.set_setting('openai_embedding_model', model)
        else:
            raise ValueError(f"無效的嵌入模型: {model}")

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
    
    def get_embedding_model_info(self) -> Dict[str, Any]:
        """獲取嵌入模型信息"""
        model = self.get_embedding_model()
        
        # OpenAI embedding models info
        model_info = {
            "text-embedding-3-small": {
                "dimensions": 1536,
                "max_tokens": 8191,
                "cost_per_1k_tokens": 0.00002,
                "description": "最便宜快速的OpenAI嵌入模型"
            },
            "text-embedding-3-large": {
                "dimensions": 3072,
                "max_tokens": 8191,
                "cost_per_1k_tokens": 0.00013,
                "description": "最高質量的OpenAI嵌入模型"
            },
            "text-embedding-ada-002": {
                "dimensions": 1536,
                "max_tokens": 8191,
                "cost_per_1k_tokens": 0.00010,
                "description": "舊版OpenAI嵌入模型，穩定但較貴"
            }
        }
        
        return model_info.get(model, {
            "description": f"使用模型: {model}",
            "provider": "OpenAI"
        })
    
    def get_all_settings(self) -> Dict[str, Any]:
        """獲取所有設定"""
        settings_copy = self._current_settings.copy()
        # 不顯示API密鑰的完整內容
        if "openai_api_key" in settings_copy and settings_copy["openai_api_key"]:
            key = settings_copy["openai_api_key"]
            if len(key) > 8:
                settings_copy["openai_api_key"] = f"{key[:7]}...{key[-4:]}"
        return settings_copy
    
    def reload_settings(self):
        """重新載入設定"""
        self._load_env_file()  # Reload .env file
        self._current_settings = self._load_settings()

# 創建全局設定管理器實例
settings_manager = SettingsManager()