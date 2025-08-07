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
from typing import List, Dict, Optional, Callable
from metadata_extractor import extract_metadata
from semantic_lookup import lookup_semantic_scholar_metadata
from document_renamer import rename_and_copy_file
from metadata_registry import append_metadata_to_registry

def process_uploaded_files(file_paths: List[str], status_callback: Optional[Callable[[str], None]] = None) -> List[Dict]:
    """
    處理上傳的文件，提取元數據並組織存儲
    
    功能流程：
    1. 驗證文件格式（只支持PDF和DOCX）
    2. 提取文件元數據
    3. 從Semantic Scholar獲取補充信息
    4. 重命名並複製文件到papers目錄
    5. 更新元數據註冊表
    
    參數：
        file_paths (List[str]): 文件路徑列表
        status_callback (Optional[Callable]): 進度回調函數，用於更新UI狀態
    
    返回：
        List[Dict]: 處理結果列表，包含每個文件的元數據信息
    
    示例：
        >>> results = process_uploaded_files(['paper1.pdf', 'paper2.docx'])
        >>> for result in results:
        >>>     print(f"處理完成：{result['new_filename']}")
    """
    
    # ==================== 文件格式驗證 ====================
    # 定義支持的文件格式
    valid_exts = [".pdf", ".docx"]
    
    # 過濾出支持格式的文件
    file_paths = [
        path for path in file_paths
        if os.path.splitext(path)[1].lower() in valid_exts
    ]
    
    print(f"📁 找到 {len(file_paths)} 個有效文件")
    
    # ==================== 文件處理循環 ====================
    results = []
    
    for i, path in enumerate(file_paths, 1):
        filename = os.path.basename(path)
        print(f"🔄 處理第 {i}/{len(file_paths)} 個文件：{filename}")
        
        # ==================== 元數據提取 ====================
        # 通知UI更新狀態
        if status_callback:
            status_callback(f"📄 正在提取文件 `{filename}` 的元數據...")
        
        # 從文件中提取基本元數據（標題、作者、DOI等）
        metadata = extract_metadata(path)
        print(f"📋 提取到元數據：{metadata.get('title', '未知標題')}")
        
        # ==================== Semantic Scholar 補充信息 ====================
        # 使用DOI或標題從Semantic Scholar獲取更詳細的信息
        semantic_data = lookup_semantic_scholar_metadata(
            doi=metadata.get("doi", "") or None,  # 如果有DOI就用DOI查詢
            title=metadata.get("title", "") or None  # 否則用標題查詢
        )
        
        # ==================== 元數據整合 ====================
        # 將Semantic Scholar的信息與本地提取的信息合併
        # 優先使用Semantic Scholar的信息，因為通常更準確
        metadata.update({
            "title": semantic_data.get("title", metadata.get("title", "")),
            "authors": "; ".join(a["name"] for a in semantic_data.get("authors", [])),
            "year": semantic_data.get("year", ""),
            "venue": semantic_data.get("venue", ""),  # 期刊或會議名稱
            "url": semantic_data.get("url", "")  # 論文URL
        })
        
        # ==================== 文件重命名和複製 ====================
        # 通知UI更新狀態
        if status_callback:
            status_callback(f"📦 正在複製文件 `{filename}`...")
        
        # 重命名文件並複製到papers目錄
        # 新文件名格式：作者_年份_標題.pdf/docx
        metadata = rename_and_copy_file(path, metadata)
        
        if status_callback:
            status_callback(f"📦 已複製 `{filename}` 至 papers 目錄，新文件名：`{metadata['new_filename']}`")
        
        # ==================== 元數據註冊 ====================
        # 將元數據信息添加到註冊表中
        append_metadata_to_registry(metadata)
        
        if status_callback:
            status_callback(f"✅ 已更新元數據註冊表：{metadata['new_filename']}")
        
        print(f"✅ 完成處理：{metadata['new_filename']}")
        results.append(metadata)
    
    # ==================== 處理完成統計 ====================
    print(f"🎯 文件處理完成！共處理 {len(results)} 個文件")
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
