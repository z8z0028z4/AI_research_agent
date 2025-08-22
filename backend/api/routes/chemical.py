"""
化學品查詢 API 路由
==================

處理化學品信息查詢、安全數據等功能
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import sys
import os

# 添加原項目路徑到 sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../app'))

# 修正導入方式
try:
    from backend.services.pubchem_service import chemical_metadata_extractor
except ImportError:
    # 如果直接導入失敗，嘗試使用完整路徑 (已重組，不再需要)
    # sys.path.append(os.path.join(os.path.dirname(__file__), '../../../'))
    from backend.services.pubchem_service import chemical_metadata_extractor

router = APIRouter()

class ChemicalRequest(BaseModel):
    """化學品查詢請求模型"""
    chemical_name: str
    include_safety: bool = True
    include_properties: bool = True

class ChemicalResponse(BaseModel):
    """化學品查詢響應模型"""
    name: str
    formula: Optional[str] = None
    molecular_weight: Optional[str] = None
    cas_number: Optional[str] = None
    smiles: Optional[str] = None
    boiling_point: Optional[str] = None
    melting_point: Optional[str] = None
    pubchem_url: Optional[str] = None
    image_url: Optional[str] = None
    safety_data: Optional[Dict[str, Any]] = None
    properties: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

class ChemicalBatchRequest(BaseModel):
    """批量化學品查詢請求模型"""
    chemical_names: List[str]

class ChemicalBatchResponse(BaseModel):
    """批量化學品查詢響應模型"""
    results: List[ChemicalResponse]
    not_found: List[str]
    total_count: int
    success_count: int

@router.post("/chemical/search", response_model=ChemicalResponse)
async def search_chemical(request: ChemicalRequest):
    """
    查詢單個化學品信息
    
    Args:
        request: 化學品查詢請求
        
    Returns:
        化學品詳細信息
    """
    try:
        # 調用原有的化學品查詢功能
        result = chemical_metadata_extractor(request.chemical_name)
        
        if not result or result.get("error"):
            return ChemicalResponse(
                name=request.chemical_name,
                error=result.get("error", "未找到化學品信息")
            )
        
        # 構建響應數據
        safety_data = None
        if request.include_safety and result.get("safety_icons"):
            safety_data = {
                "nfpa_image": result["safety_icons"].get("nfpa_image", ""),
                "ghs_icons": result["safety_icons"].get("ghs_icons", [])
            }
        
        properties = None
        if request.include_properties:
            properties = {
                "formula": result.get("formula"),
                "molecular_weight": result.get("weight"),
                "cas_number": result.get("cas"),
                "smiles": result.get("smiles"),
                "boiling_point": result.get("boiling_point_c"),
                "melting_point": result.get("melting_point_c")
            }
        
        return ChemicalResponse(
            name=result.get("name", request.chemical_name),
            formula=result.get("formula"),
            molecular_weight=result.get("weight"),
            cas_number=result.get("cas"),
            smiles=result.get("smiles"),
            boiling_point=result.get("boiling_point_c"),
            melting_point=result.get("melting_point_c"),
            pubchem_url=result.get("pubchem_url"),
            image_url=result.get("image_url"),
            safety_data=safety_data,
            properties=properties
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"化學品查詢失敗: {str(e)}")

@router.post("/chemical/batch-search", response_model=ChemicalBatchResponse)
async def batch_search_chemicals(request: ChemicalBatchRequest):
    """
    批量查詢化學品信息
    
    Args:
        request: 批量化學品查詢請求
        
    Returns:
        批量查詢結果
    """
    try:
        results = []
        not_found = []
        
        for chemical_name in request.chemical_names:
            try:
                result = chemical_metadata_extractor(chemical_name)
                
                if result and not result.get("error"):
                    # 構建響應數據
                    safety_data = None
                    if result.get("safety_icons"):
                        safety_data = {
                            "nfpa_image": result["safety_icons"].get("nfpa_image", ""),
                            "ghs_icons": result["safety_icons"].get("ghs_icons", [])
                        }
                    
                    properties = {
                        "formula": result.get("formula"),
                        "molecular_weight": result.get("weight"),
                        "cas_number": result.get("cas"),
                        "smiles": result.get("smiles"),
                        "boiling_point": result.get("boiling_point_c"),
                        "melting_point": result.get("melting_point_c")
                    }
                    
                    results.append(ChemicalResponse(
                        name=result.get("name", chemical_name),
                        formula=result.get("formula"),
                        molecular_weight=result.get("weight"),
                        cas_number=result.get("cas"),
                        smiles=result.get("smiles"),
                        boiling_point=result.get("boiling_point_c"),
                        melting_point=result.get("melting_point_c"),
                        pubchem_url=result.get("pubchem_url"),
                        image_url=result.get("image_url"),
                        safety_data=safety_data,
                        properties=properties
                    ))
                else:
                    not_found.append(chemical_name)
                    
            except Exception as e:
                not_found.append(chemical_name)
        
        return ChemicalBatchResponse(
            results=results,
            not_found=not_found,
            total_count=len(request.chemical_names),
            success_count=len(results)
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"批量化學品查詢失敗: {str(e)}")

@router.get("/chemical/safety/{chemical_name}")
async def get_chemical_safety(chemical_name: str):
    """
    獲取化學品安全信息
    
    Args:
        chemical_name: 化學品名稱
        
    Returns:
        安全信息數據
    """
    try:
        result = chemical_metadata_extractor(chemical_name)
        
        if not result or result.get("error"):
            raise HTTPException(status_code=404, detail="未找到化學品安全信息")
        
        safety_data = {
            "nfpa_image": result.get("safety_icons", {}).get("nfpa_image", ""),
            "ghs_icons": result.get("safety_icons", {}).get("ghs_icons", []),
            "hazard_statements": result.get("hazard_statements", []),
            "precautionary_statements": result.get("precautionary_statements", [])
        }
        
        return {
            "chemical_name": chemical_name,
            "safety_data": safety_data
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"安全信息查詢失敗: {str(e)}")

@router.get("/chemical/properties/{chemical_name}")
async def get_chemical_properties(chemical_name: str):
    """
    獲取化學品物理化學性質
    
    Args:
        chemical_name: 化學品名稱
        
    Returns:
        物理化學性質數據
    """
    try:
        result = chemical_metadata_extractor(chemical_name)
        
        if not result or result.get("error"):
            raise HTTPException(status_code=404, detail="未找到化學品性質信息")
        
        properties = {
            "formula": result.get("formula"),
            "molecular_weight": result.get("weight"),
            "cas_number": result.get("cas"),
            "smiles": result.get("smiles"),
            "boiling_point": result.get("boiling_point_c"),
            "melting_point": result.get("melting_point_c"),
            "density": result.get("density"),
            "solubility": result.get("solubility")
        }
        
        return {
            "chemical_name": chemical_name,
            "properties": properties
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"性質信息查詢失敗: {str(e)}") 