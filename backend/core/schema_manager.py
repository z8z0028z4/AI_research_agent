"""
Schema 管理模組
============

負責管理和創建各種 JSON Schema，用於結構化輸出
"""

import os
import sys
import logging
from typing import Dict, Any, Optional

# 配置日誌
logger = logging.getLogger(__name__)

__all__ = [
    'get_dynamic_schema_params',
    'create_research_proposal_schema',
    'create_experimental_detail_schema',
    'create_revision_proposal_schema',
    'create_revision_experimental_detail_schema',
    'get_schema_by_type'
]

def get_dynamic_schema_params() -> Dict[str, int]:
    """
    從設定管理器獲取動態的 JSON Schema 參數
    
    Returns:
        Dict[str, int]: schema 參數字典
    """
    try:
        backend_path = os.path.join(os.path.dirname(__file__), "..", "..", "backend")
        if backend_path not in sys.path:
            sys.path.insert(0, backend_path)
        
        try:
            from backend.core.settings_manager import settings_manager
        except ImportError:
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
            "max_length": 2000
        }

def create_research_proposal_schema() -> Dict[str, Any]:
    """
    創建研究提案的 JSON Schema
    
    Returns:
        Dict[str, Any]: 研究提案的 schema
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
                "minLength": 10,
                "maxLength": schema_params["max_length"]
            },
            "need": {
                "type": "string",
                "description": "研究需求背景，說明為什麼需要這個研究",
                "minLength": schema_params["min_length"],
                "maxLength": schema_params["max_length"]
            },
            "solution": {
                "type": "string",
                "description": "解決方案概述，描述如何解決研究需求",
                "minLength": schema_params["min_length"],
                "maxLength": schema_params["max_length"]
            },
            "differentiation": {
                "type": "string",
                "description": "創新點和差異化，說明與現有研究的區別",
                "minLength": schema_params["min_length"],
                "maxLength": schema_params["max_length"]
            },
            "benefit": {
                "type": "string",
                "description": "預期效益，說明研究的潛在影響和價值",
                "minLength": schema_params["min_length"],
                "maxLength": schema_params["max_length"]
            },
            "experimental_overview": {
                "type": "string",
                "description": "實驗概述，簡要描述實驗設計和方法",
                "minLength": schema_params["min_length"],
                "maxLength": schema_params["max_length"]
            },
            "materials_list": {
                "type": "array",
                "description": "材料清單，列出實驗所需的主要材料",
                "items": {
                    "type": "string",
                    "minLength": 1,
                    "maxLength": 100
                },
                "minItems": 1,
                "maxItems": 20
            }
        }
    }

def create_experimental_detail_schema() -> Dict[str, Any]:
    """
    創建實驗詳情的 JSON Schema
    
    Returns:
        Dict[str, Any]: 實驗詳情的 schema
    """
    schema_params = get_dynamic_schema_params()
    
    return {
        "type": "object",
        "title": "ExperimentalDetail",
        "additionalProperties": False,
        "required": [
            "synthesis_process",
            "materials_and_conditions",
            "analytical_methods",
            "precautions"
        ],
        "properties": {
            "synthesis_process": {
                "type": "string",
                "description": "詳細的合成步驟、條件、時間等",
                "minLength": schema_params["min_length"],
                "maxLength": schema_params["max_length"]
            },
            "materials_and_conditions": {
                "type": "string",
                "description": "使用的材料、濃度、溫度、壓力和其他反應條件",
                "minLength": schema_params["min_length"],
                "maxLength": schema_params["max_length"]
            },
            "analytical_methods": {
                "type": "string",
                "description": "表徵技術，如 XRD、SEM、NMR 等",
                "minLength": schema_params["min_length"],
                "maxLength": schema_params["max_length"]
            },
            "precautions": {
                "type": "string",
                "description": "實驗注意事項和安全預防措施",
                "minLength": schema_params["min_length"],
                "maxLength": schema_params["max_length"]
            }
        }
    }



def create_revision_proposal_schema() -> Dict[str, Any]:
    """
    創建修訂提案的 JSON Schema
    
    Returns:
        Dict[str, Any]: 修訂提案的 schema
    """
    schema_params = get_dynamic_schema_params()
    
    return {
        "type": "object",
        "title": "RevisionProposal",
        "additionalProperties": False,
        "required": [
            "revision_explanation",
            "proposal_title",
            "need",
            "solution",
            "differentiation",
            "benefit",
            "experimental_overview",
            "materials_list"
        ],
        "properties": {
            "revision_explanation": {
                "type": "string",
                "description": "修訂邏輯和關鍵改進的簡要說明",
                "minLength": schema_params["min_length"],
                "maxLength": schema_params["max_length"]
            },
            "proposal_title": {
                "type": "string",
                "description": "研究提案標題",
                "minLength": 10,
                "maxLength": schema_params["max_length"]
            },
            "need": {
                "type": "string",
                "description": "研究需求背景和當前限制",
                "minLength": schema_params["min_length"],
                "maxLength": schema_params["max_length"]
            },
            "solution": {
                "type": "string",
                "description": "建議的設計和開發策略",
                "minLength": schema_params["min_length"],
                "maxLength": schema_params["max_length"]
            },
            "differentiation": {
                "type": "string",
                "description": "與現有技術的比較",
                "minLength": schema_params["min_length"],
                "maxLength": schema_params["max_length"]
            },
            "benefit": {
                "type": "string",
                "description": "預期改進和效益",
                "minLength": schema_params["min_length"],
                "maxLength": schema_params["max_length"]
            },
            "experimental_overview": {
                "type": "string",
                "description": "實驗方法和方法論",
                "minLength": schema_params["min_length"],
                "maxLength": schema_params["max_length"]
            },
            "materials_list": {
                "type": "array",
                "description": "材料清單，列出實驗所需的主要材料",
                "items": {
                    "type": "string",
                    "minLength": 1,
                    "maxLength": 100
                },
                "minItems": 1,
                "maxItems": 20
            }
        }
    }

def create_revision_experimental_detail_schema() -> Dict[str, Any]:
    """
    創建修訂實驗細節的 JSON Schema
    
    Returns:
        Dict[str, Any]: 修訂實驗細節的 schema
    """
    schema_params = get_dynamic_schema_params()
    
    return {
        "type": "object",
        "title": "RevisionExperimentalDetail",
        "additionalProperties": False,
        "required": [
            "revision_explanation",
            "synthesis_process",
            "materials_and_conditions",
            "analytical_methods",
            "precautions"
        ],
        "properties": {
            "revision_explanation": {
                "type": "string",
                "description": "修訂邏輯和關鍵改進的簡要說明，基於用戶反饋",
                "minLength": schema_params["min_length"],
                "maxLength": schema_params["max_length"]
            },
            "synthesis_process": {
                "type": "string",
                "description": "詳細的合成步驟、條件、時間等，包含修改後的內容",
                "minLength": schema_params["min_length"],
                "maxLength": schema_params["max_length"]
            },
            "materials_and_conditions": {
                "type": "string",
                "description": "使用的材料、濃度、溫度、壓力和其他反應條件，包含修改後的內容",
                "minLength": schema_params["min_length"],
                "maxLength": schema_params["max_length"]
            },
            "analytical_methods": {
                "type": "string",
                "description": "表徵技術，如 XRD、SEM、NMR 等，包含修改後的內容",
                "minLength": schema_params["min_length"],
                "maxLength": schema_params["max_length"]
            },
            "precautions": {
                "type": "string",
                "description": "實驗注意事項和安全預防措施，包含修改後的內容",
                "minLength": schema_params["min_length"],
                "maxLength": schema_params["max_length"]
            }
        }
    }

def get_schema_by_type(schema_type: str) -> Optional[Dict[str, Any]]:
    """
    根據類型獲取對應的 schema
    
    Args:
        schema_type: schema 類型
        
    Returns:
        Dict[str, Any]: 對應的 schema，如果不存在則返回 None
    """
    schema_functions = {
        "research_proposal": create_research_proposal_schema,
        "experimental_detail": create_experimental_detail_schema,
        "revision_proposal": create_revision_proposal_schema,
        "revision_experimental_detail": create_revision_experimental_detail_schema
    }
    
    if schema_type not in schema_functions:
        logger.warning(f"未知的 schema 類型: {schema_type}")
        return None
    
    try:
        return schema_functions[schema_type]()
    except Exception as e:
        logger.error(f"創建 schema 失敗 {schema_type}: {e}")
        return None
