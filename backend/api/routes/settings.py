"""
設定管理API路由
==============

提供系統設定的管理功能，包括LLM模型選擇等
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
import json
import os
from pathlib import Path

import sys
import os
from pathlib import Path

# 添加項目根目錄到Python路徑
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from backend.core.config import settings
from backend.core.settings_manager import settings_manager

router = APIRouter(prefix="/settings", tags=["settings"])

class ModelSettings(BaseModel):
    """模型設定模型"""
    llm_model: str

class LLMParameters(BaseModel):
    """LLM參數設定模型"""
    max_tokens: Optional[int] = None
    timeout: Optional[int] = None
    reasoning_effort: Optional[str] = None
    verbosity: Optional[str] = None

class ModelSettingsResponse(BaseModel):
    """模型設定回應模型"""
    current_model: str
    available_models: list

class LLMParametersResponse(BaseModel):
    """LLM參數回應模型"""
    max_tokens: int
    timeout: int
    reasoning_effort: Optional[str] = None
    verbosity: Optional[str] = None

class JSONSchemaParameters(BaseModel):
    """JSON Schema參數設定模型"""
    min_length: Optional[int] = None
    max_length: Optional[int] = None

class JSONSchemaParametersResponse(BaseModel):
    """JSON Schema參數回應模型"""
    min_length: int
    max_length: int

class ModelParametersInfo(BaseModel):
    """模型參數資訊回應模型"""
    supported_parameters: dict
    current_parameters: dict

@router.get("/model", response_model=ModelSettingsResponse)
async def get_model_settings():
    """獲取當前LLM模型設定"""
    try:
        # 獲取當前模型
        current_model = settings_manager.get_current_model()
        
        # 可用的模型列表
        available_models = [
            {
                "value": "gpt-5",
                "label": "GPT-5",
                "description": "最新的GPT-5模型，功能最強大，支援推理控制和工具鏈"
            },
            {
                "value": "gpt-5-nano",
                "label": "GPT-5 Nano",
                "description": "GPT-5的輕量版本，速度最快，適合簡單格式化任務"
            },
            {
                "value": "gpt-5-mini",
                "label": "GPT-5 Mini",
                "description": "GPT-5的平衡版本，速度與功能兼具，支援推理控制"
            }
        ]
        
        return ModelSettingsResponse(
            current_model=current_model,
            available_models=available_models
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"獲取設定失敗: {str(e)}")

@router.post("/model")
async def update_model_settings(model_settings: ModelSettings):
    """更新LLM模型設定"""
    try:
        # 使用設定管理器更新模型
        settings_manager.set_current_model(model_settings.llm_model)
        
        return {
            "message": "模型設定已成功更新",
            "current_model": model_settings.llm_model
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新設定失敗: {str(e)}")

@router.get("/llm-parameters", response_model=LLMParametersResponse)
async def get_llm_parameters():
    """獲取當前LLM參數設定"""
    try:
        params = settings_manager.get_llm_parameters()
        return LLMParametersResponse(**params)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"獲取LLM參數失敗: {str(e)}")

@router.post("/llm-parameters")
async def update_llm_parameters(parameters: LLMParameters):
    """更新LLM參數設定"""
    try:
        # 使用設定管理器更新參數
        settings_manager.set_llm_parameters(
            max_tokens=parameters.max_tokens,
            timeout=parameters.timeout,
            reasoning_effort=parameters.reasoning_effort,
            verbosity=parameters.verbosity
        )
        
        # 獲取更新後的參數
        updated_params = settings_manager.get_llm_parameters()
        
        return {
            "message": "LLM參數已成功更新",
            "parameters": updated_params
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新LLM參數失敗: {str(e)}")

@router.get("/model-parameters-info", response_model=ModelParametersInfo)
async def get_model_parameters_info(model_name: Optional[str] = None):
    """獲取指定模型支援的參數資訊"""
    try:
        if model_name is None:
            model_name = settings_manager.get_current_model()
        
        # 獲取模型支援的參數
        supported_params = settings_manager.get_model_supported_parameters(model_name)
        
        # 獲取當前參數
        current_params = settings_manager.get_llm_parameters()
        
        return ModelParametersInfo(
            supported_parameters=supported_params,
            current_parameters=current_params
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"獲取模型參數資訊失敗: {str(e)}")

@router.get("/json-schema-parameters", response_model=JSONSchemaParametersResponse)
async def get_json_schema_parameters():
    """獲取當前JSON Schema參數設定"""
    try:
        params = settings_manager.get_json_schema_parameters()
        return JSONSchemaParametersResponse(**params)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"獲取JSON Schema參數失敗: {str(e)}")

@router.post("/json-schema-parameters")
async def update_json_schema_parameters(parameters: JSONSchemaParameters):
    """更新JSON Schema參數設定"""
    try:
        # 使用設定管理器更新參數
        settings_manager.set_json_schema_parameters(
            min_length=parameters.min_length,
            max_length=parameters.max_length
        )
        
        # 獲取更新後的參數
        updated_params = settings_manager.get_json_schema_parameters()
        
        return {
            "message": "JSON Schema參數已成功更新",
            "parameters": updated_params
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新JSON Schema參數失敗: {str(e)}")

@router.get("/json-schema-parameters-info")
async def get_json_schema_parameters_info():
    """獲取JSON Schema參數資訊"""
    try:
        # 獲取支援的參數
        supported_params = settings_manager.get_json_schema_supported_parameters()
        
        # 獲取當前參數
        current_params = settings_manager.get_json_schema_parameters()
        
        return {
            "supported_parameters": supported_params,
            "current_parameters": current_params
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"獲取JSON Schema參數資訊失敗: {str(e)}")

@router.get("/system")
async def get_system_settings():
    """獲取系統設定資訊"""
    try:
        return {
            "app_name": settings.app_name,
            "app_version": settings.app_version,
            "debug": settings.debug,
            "api_prefix": settings.api_prefix,
            "upload_dir": settings.upload_dir,
            "max_file_size": settings.max_file_size,
            "allowed_file_types": settings.allowed_file_types
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"獲取系統設定失敗: {str(e)}") 