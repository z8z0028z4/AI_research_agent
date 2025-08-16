"""
化學品服務模組
============

統一管理化學品查詢和處理邏輯，提供快取機制和錯誤處理
"""

import json
import time
from typing import List, Dict, Any, Optional, Tuple
from functools import lru_cache

from ..utils.logger import get_logger
from ..utils.exceptions import ChemicalQueryError, APIError
from ..pubchem_handler import chemical_metadata_extractor

logger = get_logger(__name__)


class ChemicalService:
    """化學品服務類"""
    
    def __init__(self):
        self.cache = {}
        self.cache_ttl = 3600  # 快取1小時
    
    def extract_chemicals_from_text(self, text: str) -> Tuple[List[Dict[str, Any]], List[str], str]:
        """
        從文本中提取化學品信息
        
        Args:
            text: 包含化學品信息的文本
            
        Returns:
            Tuple[List[Dict], List[str], str]: (化學品列表, 未找到的化學品, 處理後的文本)
        """
        try:
            logger.info("開始從文本中提取化學品信息")
            start_time = time.time()
            
            # 檢查快取
            cache_key = hash(text)
            if cache_key in self.cache:
                cache_time, result = self.cache[cache_key]
                if time.time() - cache_time < self.cache_ttl:
                    logger.info("使用快取的化學品查詢結果")
                    return result
            
            # 調用原始函數
            result = chemical_metadata_extractor(text)
            
            # 儲存到快取
            self.cache[cache_key] = (time.time(), result)
            
            end_time = time.time()
            logger.info(f"化學品提取完成，耗時: {end_time - start_time:.2f}秒")
            
            return result
            
        except Exception as e:
            logger.error(f"化學品提取失敗: {e}")
            raise ChemicalQueryError(f"化學品提取失敗: {str(e)}")
    
    def get_chemical_info(self, chemical_name: str) -> Dict[str, Any]:
        """
        獲取單個化學品信息
        
        Args:
            chemical_name: 化學品名稱
            
        Returns:
            化學品信息字典
        """
        try:
            logger.info(f"查詢化學品信息: {chemical_name}")
            
            # 檢查快取
            if chemical_name in self.cache:
                cache_time, result = self.cache[chemical_name]
                if time.time() - cache_time < self.cache_ttl:
                    logger.info(f"使用快取的化學品信息: {chemical_name}")
                    return result
            
            # 調用原始函數
            chemicals, not_found, _ = chemical_metadata_extractor(chemical_name)
            
            if chemicals:
                result = chemicals[0]
                # 儲存到快取
                self.cache[chemical_name] = (time.time(), result)
                return result
            else:
                raise ChemicalQueryError(f"未找到化學品: {chemical_name}")
                
        except Exception as e:
            logger.error(f"化學品查詢失敗: {e}")
            raise ChemicalQueryError(f"化學品查詢失敗: {str(e)}")
    
    def batch_get_chemicals(self, chemical_names: List[str]) -> Dict[str, Any]:
        """
        批量查詢化學品信息
        
        Args:
            chemical_names: 化學品名稱列表
            
        Returns:
            化學品信息字典，鍵為化學品名稱
        """
        try:
            logger.info(f"批量查詢化學品信息: {len(chemical_names)} 個")
            results = {}
            
            for name in chemical_names:
                try:
                    results[name] = self.get_chemical_info(name)
                except ChemicalQueryError as e:
                    logger.warning(f"化學品 {name} 查詢失敗: {e}")
                    results[name] = {"error": str(e)}
            
            return results
            
        except Exception as e:
            logger.error(f"批量化學品查詢失敗: {e}")
            raise ChemicalQueryError(f"批量化學品查詢失敗: {str(e)}")
    
    def clear_cache(self):
        """清除快取"""
        self.cache.clear()
        logger.info("化學品服務快取已清除")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """獲取快取統計信息"""
        current_time = time.time()
        valid_entries = 0
        expired_entries = 0
        
        for cache_time, _ in self.cache.values():
            if current_time - cache_time < self.cache_ttl:
                valid_entries += 1
            else:
                expired_entries += 1
        
        return {
            "total_entries": len(self.cache),
            "valid_entries": valid_entries,
            "expired_entries": expired_entries,
            "cache_ttl": self.cache_ttl
        }


# 全局服務實例
chemical_service = ChemicalService()


# 向後相容的函數
def extract_chemicals_from_text(text: str) -> Tuple[List[Dict[str, Any]], List[str], str]:
    """
    向後相容的化學品提取函數
    
    Args:
        text: 包含化學品信息的文本
        
    Returns:
        Tuple[List[Dict], List[str], str]: (化學品列表, 未找到的化學品, 處理後的文本)
    """
    return chemical_service.extract_chemicals_from_text(text)


def get_chemical_info(chemical_name: str) -> Dict[str, Any]:
    """
    向後相容的化學品查詢函數
    
    Args:
        chemical_name: 化學品名稱
        
    Returns:
        化學品信息字典
    """
    return chemical_service.get_chemical_info(chemical_name)
