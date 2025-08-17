"""
文件處理服務模組
==============

統一管理文件驗證、分類和處理邏輯，提供一致的接口
"""

import os
from typing import List, Dict, Any, Optional
from pathlib import Path

from ..utils.logger import get_logger
from ..utils.exceptions import FileProcessingError, ValidationError

logger = get_logger(__name__)


class FileService:
    """文件處理服務類"""
    
    # 支援的文件類型
    SUPPORTED_EXTENSIONS = {
        "papers": [".pdf", ".docx", ".doc"],
        "experiments": [".xlsx", ".xls"],
        "text": [".txt", ".md"],
        "images": [".png", ".jpg", ".jpeg", ".gif"]
    }
    
    # 文件大小限制 (MB) - 已移除限制
    # MAX_FILE_SIZE = 100  # removed
    
    def __init__(self):
        self.valid_extensions = []
        for extensions in self.SUPPORTED_EXTENSIONS.values():
            self.valid_extensions.extend(extensions)
    
    def validate_file(self, file_path: str) -> Dict[str, Any]:
        """
        驗證單個文件
        
        Args:
            file_path: 文件路徑
            
        Returns:
            驗證結果字典
        """
        try:
            logger.info(f"驗證文件: {file_path}")
            
            if not os.path.exists(file_path):
                raise ValidationError(f"文件不存在: {file_path}")
            
            # 檢查文件大小 - 限制已移除
            file_size = os.path.getsize(file_path)
            # File size check removed - no limit
            
            # 檢查文件擴展名
            file_ext = os.path.splitext(file_path)[1].lower()
            if file_ext not in self.valid_extensions:
                raise ValidationError(f"不支援的文件類型: {file_ext}")
            
            # 確定文件類型
            file_type = self._get_file_type(file_ext)
            
            return {
                "valid": True,
                "file_path": file_path,
                "file_name": os.path.basename(file_path),
                "file_size": file_size,
                "file_extension": file_ext,
                "file_type": file_type
            }
            
        except Exception as e:
            logger.error(f"文件驗證失敗: {e}")
            return {
                "valid": False,
                "file_path": file_path,
                "error": str(e)
            }
    
    def validate_files(self, file_paths: List[str]) -> Dict[str, List[Dict[str, Any]]]:
        """
        批量驗證文件
        
        Args:
            file_paths: 文件路徑列表
            
        Returns:
            驗證結果字典
        """
        try:
            logger.info(f"批量驗證文件: {len(file_paths)} 個")
            
            results = {
                "valid_files": [],
                "invalid_files": [],
                "summary": {
                    "total": len(file_paths),
                    "valid": 0,
                    "invalid": 0
                }
            }
            
            for file_path in file_paths:
                result = self.validate_file(file_path)
                if result["valid"]:
                    results["valid_files"].append(result)
                    results["summary"]["valid"] += 1
                else:
                    results["invalid_files"].append(result)
                    results["summary"]["invalid"] += 1
            
            logger.info(f"文件驗證完成: {results['summary']['valid']} 個有效, {results['summary']['invalid']} 個無效")
            return results
            
        except Exception as e:
            logger.error(f"批量文件驗證失敗: {e}")
            raise FileProcessingError(f"批量文件驗證失敗: {str(e)}")
    
    def classify_files(self, file_paths: List[str]) -> Dict[str, List[str]]:
        """
        根據文件類型分類文件
        
        Args:
            file_paths: 文件路徑列表
            
        Returns:
            分類結果字典
        """
        try:
            logger.info(f"分類文件: {len(file_paths)} 個")
            
            classification = {
                "papers": [],
                "experiments": [],
                "text": [],
                "images": [],
                "others": []
            }
            
            for file_path in file_paths:
                file_ext = os.path.splitext(file_path)[1].lower()
                file_type = self._get_file_type(file_ext)
                
                if file_type in classification:
                    classification[file_type].append(file_path)
                else:
                    classification["others"].append(file_path)
            
            # 記錄分類結果
            for file_type, files in classification.items():
                if files:
                    logger.info(f"{file_type}: {len(files)} 個文件")
            
            return classification
            
        except Exception as e:
            logger.error(f"文件分類失敗: {e}")
            raise FileProcessingError(f"文件分類失敗: {str(e)}")
    
    def get_file_info(self, file_path: str) -> Dict[str, Any]:
        """
        獲取文件詳細信息
        
        Args:
            file_path: 文件路徑
            
        Returns:
            文件信息字典
        """
        try:
            if not os.path.exists(file_path):
                raise FileProcessingError(f"文件不存在: {file_path}")
            
            stat = os.stat(file_path)
            
            return {
                "file_path": file_path,
                "file_name": os.path.basename(file_path),
                "file_size": stat.st_size,
                "file_extension": os.path.splitext(file_path)[1].lower(),
                "file_type": self._get_file_type(os.path.splitext(file_path)[1].lower()),
                "created_time": stat.st_ctime,
                "modified_time": stat.st_mtime,
                "is_readable": os.access(file_path, os.R_OK),
                "is_writable": os.access(file_path, os.W_OK)
            }
            
        except Exception as e:
            logger.error(f"獲取文件信息失敗: {e}")
            raise FileProcessingError(f"獲取文件信息失敗: {str(e)}")
    
    def _get_file_type(self, file_ext: str) -> str:
        """
        根據文件擴展名確定文件類型
        
        Args:
            file_ext: 文件擴展名
            
        Returns:
            文件類型
        """
        for file_type, extensions in self.SUPPORTED_EXTENSIONS.items():
            if file_ext in extensions:
                return file_type
        return "others"
    
    def get_supported_extensions(self) -> Dict[str, List[str]]:
        """
        獲取支援的文件類型
        
        Returns:
            支援的文件類型字典
        """
        return self.SUPPORTED_EXTENSIONS.copy()


# 全局服務實例
file_service = FileService()


# 向後相容的函數
def validate_file_format(file_path: str) -> bool:
    """
    向後相容的文件格式驗證函數
    
    Args:
        file_path: 文件路徑
        
    Returns:
        文件格式是否有效
    """
    result = file_service.validate_file(file_path)
    return result.get("valid", False)


def classify_files_by_type(file_paths: List[str]) -> Dict[str, List[str]]:
    """
    向後相容的文件分類函數
    
    Args:
        file_paths: 文件路徑列表
        
    Returns:
        分類結果字典
    """
    return file_service.classify_files(file_paths)
