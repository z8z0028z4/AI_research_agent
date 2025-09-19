"""
化學品數據庫服務
==============

處理化學品數據的數據庫存儲、查詢和管理
整合現有的 parsed_chemicals 文件系統
"""

import json
import os
from typing import List, Dict, Any, Optional
from datetime import datetime

from ..utils.logger import get_logger

logger = get_logger(__name__)

# 使用現有的 parsed_chemicals 目錄
PARSED_CHEMICAL_DIR = "experiment_data/parsed_chemicals"


class ChemicalDatabaseService:
    """化學品數據庫服務類 - 基於文件系統"""
    
    def __init__(self, parsed_dir: Optional[str] = None):
        """
        初始化化學品數據庫服務
        
        Args:
            parsed_dir: parsed_chemicals 目錄路徑
        """
        self.parsed_dir = parsed_dir or PARSED_CHEMICAL_DIR
        self._init_directory()
    
    def _init_directory(self):
        """初始化目錄結構"""
        try:
            os.makedirs(self.parsed_dir, exist_ok=True)
            logger.info(f"化學品數據目錄初始化完成: {self.parsed_dir}")
        except Exception as e:
            logger.error(f"初始化化學品數據目錄失敗: {e}")
            raise
    
    def save_chemical(self, chemical_data: Dict[str, Any]) -> bool:
        """
        保存化學品數據到文件系統
        
        Args:
            chemical_data: 化學品數據字典
            
        Returns:
            bool: 保存是否成功
        """
        try:
            cid = chemical_data.get('cid')
            if not cid:
                logger.warning("化學品沒有 CID，無法保存")
                return False
            
            # 使用與現有系統相同的文件名格式
            filename = f"parsed_cid{cid}.json"
            filepath = os.path.join(self.parsed_dir, filename)
            
            # 保存到文件
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(chemical_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"化學品數據已保存: {filename}")
            return True
                
        except Exception as e:
            logger.error(f"保存化學品數據失敗: {e}")
            return False
    
    def get_chemical_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """
        根據名稱查詢化學品
        
        Args:
            name: 化學品名稱
            
        Returns:
            Dict: 化學品數據，如果未找到則返回None
        """
        try:
            # 遍歷所有文件查找匹配的化學品
            for filename in os.listdir(self.parsed_dir):
                if filename.startswith("parsed_cid") and filename.endswith(".json"):
                    filepath = os.path.join(self.parsed_dir, filename)
                    try:
                        with open(filepath, 'r', encoding='utf-8') as f:
                            chemical_data = json.load(f)
                            if chemical_data.get('name', '').lower() == name.lower():
                                logger.info(f"從文件找到化學品: {name}")
                                return chemical_data
                    except Exception as e:
                        logger.warning(f"讀取文件失敗: {filename}, {e}")
                        continue
            
            logger.info(f"未找到化學品: {name}")
            return None
                
        except Exception as e:
            logger.error(f"查詢化學品失敗: {e}")
            return None
    
    def get_chemical_by_cid(self, cid: int) -> Optional[Dict[str, Any]]:
        """
        根據CID查詢化學品
        
        Args:
            cid: PubChem CID
            
        Returns:
            Dict: 化學品數據，如果未找到則返回None
        """
        try:
            filename = f"parsed_cid{cid}.json"
            filepath = os.path.join(self.parsed_dir, filename)
            
            if os.path.exists(filepath):
                with open(filepath, 'r', encoding='utf-8') as f:
                    chemical_data = json.load(f)
                    logger.info(f"從文件找到化學品 CID: {cid}")
                    return chemical_data
            else:
                logger.info(f"未找到化學品 CID: {cid}")
                return None
                
        except Exception as e:
            logger.error(f"查詢化學品失敗: {e}")
            return None
    
    def search_chemicals(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        搜索化學品
        
        Args:
            query: 搜索查詢
            limit: 結果數量限制
            
        Returns:
            List[Dict]: 化學品數據列表
        """
        try:
            results = []
            query_lower = query.lower()
            
            for filename in os.listdir(self.parsed_dir):
                if filename.startswith("parsed_cid") and filename.endswith(".json"):
                    filepath = os.path.join(self.parsed_dir, filename)
                    try:
                        with open(filepath, 'r', encoding='utf-8') as f:
                            chemical_data = json.load(f)
                            
                            # 檢查數據是否有效
                            if chemical_data and isinstance(chemical_data, dict):
                                # 搜索匹配
                                name = chemical_data.get('name', '')
                                formula = chemical_data.get('formula', '')
                                cas = chemical_data.get('cas', '')
                                
                                # 安全地轉換為小寫
                                name_lower = name.lower() if name else ''
                                formula_lower = formula.lower() if formula else ''
                                cas_lower = cas.lower() if cas else ''
                                
                                if (query_lower in name_lower or 
                                    query_lower in formula_lower or 
                                    query_lower in cas_lower):
                                    results.append(chemical_data)
                                    
                                    if len(results) >= limit:
                                        break
                            else:
                                logger.warning(f"⚠️ [DEBUG] 文件數據無效: {filename}, 數據不是字典或為空")
                                    
                    except Exception as e:
                        logger.warning(f"❌ [DEBUG] 讀取文件失敗: {filename}, 錯誤類型: {type(e)}, 錯誤信息: {e}")
                        continue
            
            logger.info(f"搜索到 {len(results)} 個化學品")
            return results
                
        except Exception as e:
            logger.error(f"搜索化學品失敗: {e}")
            return []
    
    def get_all_chemicals(self, limit: int = 1000) -> List[Dict[str, Any]]:
        """
        獲取所有化學品（按字母順序排列）
        
        Args:
            limit: 結果數量限制
            
        Returns:
            List[Dict]: 化學品數據列表（按名稱字母順序）
        """
        try:
            results = []
            filenames = [f for f in os.listdir(self.parsed_dir) 
                        if f.startswith("parsed_cid") and f.endswith(".json")]
            
            # 先讀取所有化學品數據
            for filename in filenames:
                filepath = os.path.join(self.parsed_dir, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        chemical_data = json.load(f)
                        logger.debug(f"🔍 [DEBUG] 讀取文件: {filename}")
                        logger.debug(f"🔍 [DEBUG] 數據類型: {type(chemical_data)}")
                        logger.debug(f"🔍 [DEBUG] 數據內容: {chemical_data}")
                        
                        # 檢查數據是否有效
                        if chemical_data and isinstance(chemical_data, dict):
                            name = chemical_data.get('name')
                            logger.debug(f"🔍 [DEBUG] name 字段: {name}, 類型: {type(name)}")
                            
                            if name:
                                results.append(chemical_data)
                                logger.debug(f"✅ [DEBUG] 成功添加化學品: {name}")
                            else:
                                logger.warning(f"⚠️ [DEBUG] 文件數據無效: {filename}, name 字段為空或 None")
                        else:
                            logger.warning(f"⚠️ [DEBUG] 文件數據無效: {filename}, 數據不是字典或為空")
                except Exception as e:
                    logger.warning(f"❌ [DEBUG] 讀取文件失敗: {filename}, 錯誤類型: {type(e)}, 錯誤信息: {e}")
                    continue
            
            # 按化學品名稱的字母順序排序，處理 None 值
            logger.debug(f"🔍 [DEBUG] 開始排序，化學品數量: {len(results)}")
            try:
                results.sort(key=lambda x: (x.get('name') or '').lower() if x.get('name') else '')
                logger.debug(f"✅ [DEBUG] 排序完成")
            except Exception as e:
                logger.error(f"❌ [DEBUG] 排序失敗: {e}")
                # 如果排序失敗，嘗試更安全的排序方式
                try:
                    results.sort(key=lambda x: str(x.get('name', '')).lower())
                    logger.debug(f"✅ [DEBUG] 使用安全排序完成")
                except Exception as e2:
                    logger.error(f"❌ [DEBUG] 安全排序也失敗: {e2}")
                    # 最後的備用方案：不排序
                    logger.warning(f"⚠️ [DEBUG] 跳過排序，保持原始順序")
            
            # 應用限制
            if limit > 0:
                results = results[:limit]
            
            logger.info(f"獲取到 {len(results)} 個化學品（按字母順序）")
            return results
                
        except Exception as e:
            logger.error(f"獲取化學品列表失敗: {e}")
            return []
    
    def delete_chemical(self, cid: int) -> bool:
        """
        刪除化學品
        
        Args:
            cid: 化學品CID
            
        Returns:
            bool: 刪除是否成功
        """
        try:
            filename = f"parsed_cid{cid}.json"
            filepath = os.path.join(self.parsed_dir, filename)
            
            if os.path.exists(filepath):
                os.remove(filepath)
                logger.info(f"刪除化學品成功: CID {cid}")
                return True
            else:
                logger.warning(f"未找到要刪除的化學品: CID {cid}")
                return False
                    
        except Exception as e:
            logger.error(f"刪除化學品失敗: {e}")
            return False
    
    def get_database_stats(self) -> Dict[str, Any]:
        """
        獲取數據庫統計信息
        
        Returns:
            Dict[str, Any]: 統計信息
        """
        try:
            filenames = [f for f in os.listdir(self.parsed_dir) 
                        if f.startswith("parsed_cid") and f.endswith(".json")]
            
            total_count = len(filenames)
            
            # 獲取文件修改時間作為最後更新時間
            last_updated = None
            if filenames:
                latest_file = max(filenames, key=lambda f: os.path.getmtime(os.path.join(self.parsed_dir, f)))
                last_updated = os.path.getmtime(os.path.join(self.parsed_dir, latest_file))
                last_updated = datetime.fromtimestamp(last_updated).isoformat()
            
            return {
                "total_chemicals": total_count,
                "last_updated": last_updated,
                "directory": self.parsed_dir
            }
                
        except Exception as e:
            logger.error(f"獲取數據庫統計失敗: {e}")
            return {}


# 創建全局實例
chemical_db_service = ChemicalDatabaseService()