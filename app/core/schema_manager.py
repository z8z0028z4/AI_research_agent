"""
Schema 管理模組
==============

管理各種 JSON Schema 的創建和驗證
"""

import json
import os
from typing import Dict, Any, Optional

from ..utils.logger import get_logger
from ..utils.exceptions import ConfigurationError

logger = get_logger(__name__)


def get_dynamic_schema_params() -> Dict[str, int]:
    """
    從設定管理器獲取動態的 JSON Schema 參數
    
    Returns:
        Dict: 包含 min_length 和 max_length 的字典
    """
    try:
        # 導入設定管理器
        import sys
        backend_path = os.path.join(os.path.dirname(__file__), "..", "..", "backend")
        if backend_path not in sys.path:
            sys.path.insert(0, backend_path)
        
        from core.settings_manager import settings_manager
        json_schema_params = settings_manager.get_json_schema_parameters()
        
        return {
            "min_length": json_schema_params.get("min_length", 5),
            "max_length": json_schema_params.get("max_length", 100)
        }
    except Exception as e:
        logger.warning(f"無法獲取動態 schema 參數，使用預設值: {e}")
        return {
            "min_length": 5,
            "max_length": 100
        }


def create_research_proposal_schema() -> Dict[str, Any]:
    """
    動態創建研究提案的 JSON Schema
    
    Returns:
        Dict: 研究提案的 JSON Schema
    """
    schema_params = get_dynamic_schema_params()
    
    return {
        "type": "object",
        "title": "ResearchProposal",
        "additionalProperties": False,
        "required": [
            "proposal_title",
            "need",
            "solution", 
            "differentiation",
            "benefit",
            "experimental_overview",
            "materials_list"
        ],
        "properties": {
            "proposal_title": {
                "type": "string",
                "description": "研究提案的標題，總結研究目標和創新點",
                "minLength": 10
            },
            "need": {
                "type": "string", 
                "description": "研究需求和現有解決方案的局限性，明確需要解決的技術瓶頸",
                "minLength": schema_params["min_length"],
                "maxLength": schema_params["max_length"]
            },
            "solution": {
                "type": "string",
                "description": "提出的解決方案和技術路線",
                "minLength": schema_params["min_length"],
                "maxLength": schema_params["max_length"]
            },
            "differentiation": {
                "type": "string",
                "description": "與現有技術的差異化和創新點",
                "minLength": schema_params["min_length"],
                "maxLength": schema_params["max_length"]
            },
            "benefit": {
                "type": "string",
                "description": "預期的技術和經濟效益",
                "minLength": schema_params["min_length"],
                "maxLength": schema_params["max_length"]
            },
            "experimental_overview": {
                "type": "string",
                "description": "實驗設計概述和關鍵步驟",
                "minLength": schema_params["min_length"],
                "maxLength": schema_params["max_length"]
            },
            "materials_list": {
                "type": "array",
                "description": "所需材料和化學品清單",
                "items": {
                    "type": "string",
                    "minLength": 1
                },
                "minItems": 1
            }
        }
    }


def create_experimental_detail_schema() -> Dict[str, Any]:
    """
    創建實驗細節的 JSON Schema
    
    Returns:
        Dict: 實驗細節的 JSON Schema
    """
    schema_params = get_dynamic_schema_params()
    
    return {
        "type": "object",
        "title": "ExperimentalDetail",
        "additionalProperties": False,
        "required": [
            "experiment_title",
            "objective",
            "materials",
            "procedure",
            "expected_results"
        ],
        "properties": {
            "experiment_title": {
                "type": "string",
                "description": "實驗標題",
                "minLength": 5
            },
            "objective": {
                "type": "string",
                "description": "實驗目標和目的",
                "minLength": schema_params["min_length"],
                "maxLength": schema_params["max_length"]
            },
            "materials": {
                "type": "array",
                "description": "實驗材料清單",
                "items": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "specification": {"type": "string"},
                        "quantity": {"type": "string"}
                    },
                    "required": ["name"]
                }
            },
            "procedure": {
                "type": "array",
                "description": "實驗步驟",
                "items": {
                    "type": "string",
                    "minLength": 1
                }
            },
            "expected_results": {
                "type": "string",
                "description": "預期結果和分析",
                "minLength": schema_params["min_length"],
                "maxLength": schema_params["max_length"]
            }
        }
    }


def validate_schema(data: Dict[str, Any], schema: Dict[str, Any]) -> bool:
    """
    驗證數據是否符合 Schema
    
    Args:
        data: 要驗證的數據
        schema: JSON Schema
        
    Returns:
        bool: 是否符合 Schema
    """
    try:
        import jsonschema
        jsonschema.validate(instance=data, schema=schema)
        return True
    except ImportError:
        logger.warning("jsonschema 未安裝，跳過驗證")
        return True
    except Exception as e:
        logger.error(f"Schema 驗證失敗: {e}")
        return False


def get_schema_by_name(schema_name: str) -> Optional[Dict[str, Any]]:
    """
    根據名稱獲取 Schema
    
    Args:
        schema_name: Schema 名稱
        
    Returns:
        Schema 字典或 None
    """
    schemas = {
        "research_proposal": create_research_proposal_schema,
        "experimental_detail": create_experimental_detail_schema
    }
    
    if schema_name in schemas:
        return schemas[schema_name]()
    
    logger.error(f"未知的 Schema 名稱: {schema_name}")
    return None
