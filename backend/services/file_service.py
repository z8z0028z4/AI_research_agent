"""
AI 研究助理 - 文件上傳處理模塊
============================

這個模塊負責處理用戶上傳的文件，包括：
1. 文件格式驗證
2. 元數據提取
3. 文件重命名和複製
4. 元數據註冊表更新

架構說明：
- 支持PDF和DOCX格式文件
- 集成多個元數據提取源
- 提供進度回調機制
- 自動文件管理和組織
"""

import os
import time
import logging
from typing import List, Dict, Optional, Callable
# 導入服務模塊
from .metadata_extractor import extract_metadata
from .semantic_lookup import lookup_semantic_scholar_metadata
from .document_renamer import rename_and_copy_file
from .metadata_registry import append_metadata_to_registry, get_existing_metadata

# 配置日誌
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def check_batch_duplicate(current_metadata: dict, processed_metadata_list: List[Dict]) -> Dict[str, any]:
    """
    檢查當前文件是否與已處理的批次文件重複
    
    參數：
        current_metadata (dict): 當前文件的元數據
        processed_metadata_list (List[Dict]): 已處理的批次文件元數據列表
    
    返回：
        Dict: {
            "is_duplicate": bool,
            "duplicate_type": str,  # "doi", "title", "none"
            "existing_metadata": dict or None
        }
    """
    try:
        for meta in processed_metadata_list:
            # 1. 檢查 type + DOI 組合重複（最可靠）
            current_doi = (current_metadata.get("doi") or "").strip()
            current_type = (current_metadata.get("type") or "").strip()
            meta_doi = (meta.get("doi") or "").strip()
            meta_type = (meta.get("type") or "").strip()
            
            if current_doi and meta_doi and current_type and meta_type:
                if current_doi == meta_doi and current_type == meta_type:
                    return {
                        "is_duplicate": True,
                        "duplicate_type": "doi",
                        "existing_metadata": meta
                    }
            
            # 2. 檢查 title + type 組合重複（次可靠）
            current_title = (current_metadata.get("title") or "").strip()
            meta_title = (meta.get("title") or "").strip()
            
            if current_title and meta_title and current_type and meta_type:
                if current_title == meta_title and current_type == meta_type:
                    return {
                        "is_duplicate": True,
                        "duplicate_type": "title",
                        "existing_metadata": meta
                    }
        
        return {
            "is_duplicate": False,
            "duplicate_type": "none",
            "existing_metadata": None
        }
    except Exception as e:
        logger.error(f"❌ 批次去重檢查錯誤: {e}")
        return {
            "is_duplicate": False,
            "duplicate_type": "error",
            "existing_metadata": None
        }

def check_duplicate_file(file_path: str, metadata: dict) -> Dict[str, any]:
    """
    檢查文件是否為重複文件
    
    返回：
        Dict: {
            "is_duplicate": bool,
            "duplicate_type": str,  # "doi", "title", "none"
            "existing_metadata": dict or None
        }
    """
    try:
        # 獲取現有元數據
        existing_metadata = get_existing_metadata()
        
        if existing_metadata is not None and not existing_metadata.empty:
            # 1. 檢查 type + DOI 組合重複（最可靠）
            doi = (metadata.get("doi") or "").strip()
            doc_type = (metadata.get("type") or "").strip()
            
            if doi and doc_type:
                # 檢查相同type和DOI的組合
                type_doi_matches = existing_metadata[
                    (existing_metadata["doi"] == doi) & 
                    (existing_metadata["type"] == doc_type)
                ]
                if not type_doi_matches.empty:
                    return {
                        "is_duplicate": True,
                        "duplicate_type": "doi",
                        "existing_metadata": type_doi_matches.iloc[0].to_dict()
                    }
            
            # 2. 檢查 title + type 組合重複（次可靠）
            title = (metadata.get("title") or "").strip()
            if title and doc_type:
                # 檢查相同title和type的組合
                title_type_matches = existing_metadata[
                    (existing_metadata["title"] == title) & 
                    (existing_metadata["type"] == doc_type)
                ]
                if not title_type_matches.empty:
                    return {
                        "is_duplicate": True,
                        "duplicate_type": "title",
                        "existing_metadata": title_type_matches.iloc[0].to_dict()
                    }
        
        return {
            "is_duplicate": False,
            "duplicate_type": "none",
            "existing_metadata": None
        }
        
    except Exception as e:
        logger.error(f"❌ 去重檢查失敗: {e}")
        return {
            "is_duplicate": False,
            "duplicate_type": "error",
            "existing_metadata": None
        }

def process_uploaded_files(file_paths: List[str], status_callback: Optional[Callable[[str], None]] = None) -> List[Dict]:
    """
    處理上傳的文件，提取元數據並組織存儲
    
    功能流程：
    1. 驗證文件格式（只支持PDF和DOCX）
    2. 批次提取文件元數據
    3. 批次與註冊文件去重
    4. 批次間去重
    5. 批次處理剩餘文件（重命名、複製、註冊）
    
    參數：
        file_paths (List[str]): 文件路徑列表
        status_callback (Optional[Callable]): 進度回調函數，用於更新UI狀態
    
    返回：
        List[Dict]: 處理結果列表，包含每個文件的元數據信息
    """
    start_time = time.time()
    logger.info(f"🚀 開始處理上傳文件，共 {len(file_paths)} 個文件")
    
    # ==================== 文件格式驗證 ====================
    logger.info("🔍 開始文件格式驗證...")
    validation_start_time = time.time()
    
    # 定義支持的文件格式
    valid_exts = [".pdf", ".docx"]
    
    # 過濾出支持格式的文件
    original_count = len(file_paths)
    file_paths = [
        path for path in file_paths
        if os.path.splitext(path)[1].lower() in valid_exts
    ]
    valid_count = len(file_paths)
    
    validation_end_time = time.time()
    logger.info(f"✅ 文件格式驗證完成，耗時: {validation_end_time - validation_start_time:.2f}秒")
    logger.info(f"📊 驗證結果 - 原始文件: {original_count}, 有效文件: {valid_count}, 跳過: {original_count - valid_count}")
    
    if not file_paths:
        logger.warning("⚠️ 沒有找到支持格式的文件")
        return []
    
    logger.info(f"📁 開始處理 {len(file_paths)} 個文件...")
    
    # ==================== 步驟1: 批次提取metadata ====================
    logger.info("📄 開始批次提取文件元數據...")
    extraction_start_time = time.time()
    
    if status_callback:
        status_callback("📄 批次提取文件元數據...")
    
    batch_metadata = []
    extraction_errors = []
    
    for i, path in enumerate(file_paths, 1):
        file_start_time = time.time()
        filename = os.path.basename(path)
        logger.info(f"📄 提取第 {i}/{len(file_paths)} 個文件元數據：{filename}")
        
        # 記錄文件信息
        file_size = os.path.getsize(path) if os.path.exists(path) else 0
        file_ext = os.path.splitext(path)[1].lower()
        logger.info(f"   📊 文件信息 - 大小: {file_size} bytes, 格式: {file_ext}")
        
        if status_callback:
            status_callback(f"📄 提取第 {i}/{len(file_paths)} 個文件元數據：{filename}")
        
        try:
            # 提取基本元數據
            extract_start_time = time.time()
            metadata = extract_metadata(path)
            extract_end_time = time.time()
            logger.info(f"   ✅ 基本元數據提取完成，耗時: {extract_end_time - extract_start_time:.2f}秒")
            logger.info(f"   📝 提取結果 - 標題: {metadata.get('title', '未知')}, DOI: {metadata.get('doi', '無')}")
            
            # Semantic Scholar補充信息
            try:
                logger.info(f"   🔍 開始Semantic Scholar查詢...")
                semantic_start_time = time.time()
                semantic_data = lookup_semantic_scholar_metadata(
                    doi=metadata.get("doi", "") or None,
                    title=metadata.get("title", "") or None
                )
                semantic_end_time = time.time()
                logger.info(f"   ✅ Semantic Scholar查詢完成，耗時: {semantic_end_time - semantic_start_time:.2f}秒")
                
                if semantic_data:
                    logger.info(f"   📊 Semantic Scholar結果 - 標題: {semantic_data.get('title', '無')}, 作者數: {len(semantic_data.get('authors', []))}")
                else:
                    logger.info(f"   ⚠️ Semantic Scholar無結果")
                    
            except Exception as e:
                logger.warning(f"⚠️ Semantic Scholar 查詢失敗 {path}: {e}")
                semantic_data = {}
            
            # 元數據整合
            merge_start_time = time.time()
            metadata.update({
                "title": semantic_data.get("title", metadata.get("title", "")),
                "authors": "; ".join(a["name"] for a in semantic_data.get("authors", [])),
                "year": semantic_data.get("year", ""),
                "venue": semantic_data.get("venue", ""),
                "url": semantic_data.get("url", ""),
                "original_path": path  # 保存原始路徑
            })
            merge_end_time = time.time()
            logger.info(f"   ✅ 元數據整合完成，耗時: {merge_end_time - merge_start_time:.2f}秒")
            
            # 如果原始文件沒有DOI但Semantic Scholar找到了DOI，則補回DOI
            if not metadata.get("doi") and semantic_data.get("externalIds", {}).get("DOI"):
                semantic_doi = semantic_data["externalIds"]["DOI"]
                metadata["doi"] = semantic_doi
                logger.info(f"✅ 通過Semantic Scholar補回DOI: {semantic_doi}")
            
            batch_metadata.append(metadata)
            file_end_time = time.time()
            logger.info(f"   ✅ 文件 {filename} 元數據提取完成，耗時: {file_end_time - file_start_time:.2f}秒")
            logger.info(f"   📝 最終結果 - 標題: {metadata.get('title', '未知標題')}")
            
        except Exception as e:
            logger.error(f"❌ 元數據提取失敗 {filename}: {e}")
            extraction_errors.append({
                "file": filename,
                "error": str(e)
            })
            if status_callback:
                status_callback(f"❌ 元數據提取失敗：{filename}")
    
    extraction_end_time = time.time()
    logger.info(f"✅ 批次元數據提取完成，耗時: {extraction_end_time - extraction_start_time:.2f}秒")
    logger.info(f"📊 提取統計 - 成功: {len(batch_metadata)}, 失敗: {len(extraction_errors)}")
    
    # ==================== 步驟2: 批次與註冊文件去重 ====================
    logger.info("🔍 開始與註冊文件去重檢查...")
    registry_duplicate_start_time = time.time()
    
    if status_callback:
        status_callback("🔍 檢查與現有文件重複...")
    
    registry_duplicates = []
    final_metadata = []
    
    for metadata in batch_metadata:
        duplicate_check_start_time = time.time()
        duplicate_result = check_duplicate_file(metadata["original_path"], metadata)
        duplicate_check_end_time = time.time()
        
        if duplicate_result["is_duplicate"]:
            logger.info(f"⚠️ 發現重複文件: {metadata.get('title', '未知標題')} - 類型: {duplicate_result['duplicate_type']}")
            registry_duplicates.append(metadata)
        else:
            final_metadata.append(metadata)
            logger.debug(f"✅ 文件無重複: {metadata.get('title', '未知標題')}")
    
    registry_duplicate_end_time = time.time()
    logger.info(f"✅ 註冊文件去重檢查完成，耗時: {registry_duplicate_end_time - registry_duplicate_start_time:.2f}秒")
    logger.info(f"📊 去重結果 - 重複: {len(registry_duplicates)}, 新增: {len(final_metadata)}")
    
    # ==================== 步驟3: 批次間去重 ====================
    logger.info("🔍 開始批次間去重檢查...")
    batch_duplicate_start_time = time.time()
    
    if status_callback:
        status_callback("🔍 檢查批次內重複...")
    
    batch_duplicates = []
    unique_metadata = []
    
    for metadata in final_metadata:
        batch_check_start_time = time.time()
        batch_result = check_batch_duplicate(metadata, unique_metadata)
        batch_check_end_time = time.time()
        
        if batch_result["is_duplicate"]:
            logger.info(f"⚠️ 發現批次內重複: {metadata.get('title', '未知標題')} - 類型: {batch_result['duplicate_type']}")
            batch_duplicates.append(metadata)
        else:
            unique_metadata.append(metadata)
            logger.debug(f"✅ 批次內無重複: {metadata.get('title', '未知標題')}")
    
    batch_duplicate_end_time = time.time()
    logger.info(f"✅ 批次間去重檢查完成，耗時: {batch_duplicate_end_time - batch_duplicate_start_time:.2f}秒")
    logger.info(f"📊 批次去重結果 - 重複: {len(batch_duplicates)}, 唯一: {len(unique_metadata)}")
    
    # ==================== 步驟4: 批次處理剩餘文件 ====================
    logger.info("📦 開始處理剩餘文件...")
    processing_start_time = time.time()
    
    if status_callback:
        status_callback(f"📦 開始處理 {len(unique_metadata)} 個文件...")
    
    results = []
    
    for i, metadata in enumerate(unique_metadata, 1):
        file_start_time = time.time()
        filename = os.path.basename(metadata["original_path"])
        logger.info(f"📦 處理第 {i}/{len(unique_metadata)} 個文件：{filename}")
        
        if status_callback:
            status_callback(f"📦 正在複製文件 `{filename}`...")
        
        try:
            # 重命名並複製文件
            copy_start_time = time.time()
            metadata = rename_and_copy_file(metadata["original_path"], metadata)
            copy_end_time = time.time()
            logger.info(f"   ✅ 文件複製完成，耗時: {copy_end_time - copy_start_time:.2f}秒")
            logger.info(f"   📄 新文件名: {metadata['new_filename']}")
            
            if status_callback:
                status_callback(f"📦 已複製 `{filename}` 至 papers 目錄，新文件名：`{metadata['new_filename']}`")
            
            # 更新元數據註冊表
            registry_start_time = time.time()
            append_metadata_to_registry(metadata)
            registry_end_time = time.time()
            logger.info(f"   ✅ 元數據註冊表更新完成，耗時: {registry_end_time - registry_start_time:.2f}秒")
            
            if status_callback:
                status_callback(f"✅ 已更新元數據註冊表：{metadata['new_filename']}")
            
            results.append(metadata)
            file_end_time = time.time()
            logger.info(f"   ✅ 文件 {filename} 處理完成，耗時: {file_end_time - file_start_time:.2f}秒")
            
        except Exception as e:
            logger.error(f"❌ 文件處理失敗 {filename}: {e}")
            if status_callback:
                status_callback(f"❌ 文件處理失敗：{filename}")
    
    processing_end_time = time.time()
    logger.info(f"✅ 文件處理完成，耗時: {processing_end_time - processing_start_time:.2f}秒")
    
    # ==================== 處理完成統計 ====================
    end_time = time.time()
    total_time = end_time - start_time
    total_skipped = len(extraction_errors) + len(registry_duplicates) + len(batch_duplicates)
    
    logger.info(f"🎯 文件處理完成！總耗時: {total_time:.2f}秒")
    logger.info(f"   📊 總文件數：{original_count}")
    logger.info(f"   ✅ 成功處理：{len(results)}")
    logger.info(f"   ⚠️ 跳過文件：{total_skipped}")
    logger.info(f"      - 提取失敗：{len(extraction_errors)}")
    logger.info(f"      - 註冊重複：{len(registry_duplicates)}")
    logger.info(f"      - 批次重複：{len(batch_duplicates)}")
    
    if status_callback:
        status_callback(f"✅ 處理完成！成功處理 {len(results)} 個文件，跳過 {total_skipped} 個文件")
    
    return results


def validate_file_format(file_path: str) -> bool:
    """
    驗證文件格式是否支持
    
    參數：
        file_path (str): 文件路徑
    
    返回：
        bool: 文件格式是否支持
    """
    valid_exts = [".pdf", ".docx"]
    file_ext = os.path.splitext(file_path)[1].lower()
    return file_ext in valid_exts


def get_file_info(file_path: str) -> Dict[str, any]:
    """
    獲取文件基本信息
    
    參數：
        file_path (str): 文件路徑
    
    返回：
        Dict[str, any]: 文件信息字典
    """
    if not os.path.exists(file_path):
        return {"error": "文件不存在"}
    
    file_info = {
        "filename": os.path.basename(file_path),
        "filepath": file_path,
        "size": os.path.getsize(file_path),
        "extension": os.path.splitext(file_path)[1].lower(),
        "is_valid": validate_file_format(file_path)
    }
    
    return file_info


def batch_process_files(file_paths: List[str], batch_size: int = 5) -> List[Dict]:
    """
    批量處理文件，支持分批處理大量文件
    
    參數：
        file_paths (List[str]): 文件路徑列表
        batch_size (int): 每批處理的文件數量
    
    返回：
        List[Dict]: 所有處理結果
    """
    all_results = []
    
    # 分批處理文件
    for i in range(0, len(file_paths), batch_size):
        batch = file_paths[i:i + batch_size]
        print(f"📦 處理批次 {i//batch_size + 1}/{(len(file_paths) + batch_size - 1)//batch_size}")
        
        try:
            batch_results = process_uploaded_files(batch)
            all_results.extend(batch_results)
        except Exception as e:
            print(f"❌ 批次處理失敗：{e}")
            # 繼續處理下一批
    
    return all_results


# ==================== 測試代碼 ====================
if __name__ == "__main__":
    """
    測試文件上傳處理功能
    
    這個測試代碼用於驗證文件處理流程是否正常工作
    """
    fake_test_file = "test_data/fake_paper.docx"
    
    try:
        print("🧪 開始測試文件上傳處理...")
        
        # 測試單個文件處理
        result = process_uploaded_files([fake_test_file])
        
        print("✅ 測試完成")
        
        # 輸出處理結果
        for r in result:
            print("📝 元數據：", r)
            
    except Exception as e:
        print(f"❌ 測試失敗：{e}")
        print("�� 請確保測試文件存在且格式正確")
