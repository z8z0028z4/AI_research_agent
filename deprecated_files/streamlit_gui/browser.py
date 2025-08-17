"""
AI 研究助理 - 文件選擇器模塊
========================

這個模塊提供Streamlit界面中的文件選擇和處理功能。
主要功能包括：
1. 文件上傳界面
2. Excel文件轉換為CSV
3. 多文件類型支持
4. 文件類型驗證

架構說明：
- 使用Streamlit的文件上傳組件
- 支持PDF、DOCX、XLSX等多種格式
- 提供Excel到CSV的轉換功能
- 集成到GUI界面中

⚠️ 注意：此模塊主要用於GUI界面，依賴於Streamlit框架
"""

import streamlit as st
import os
import pandas as pd


def save_excel_as_csvs(uploaded_file, save_dir):
    """
    將Excel文件轉換為多個CSV文件
    
    功能：
    1. 讀取Excel文件的所有工作表
    2. 將每個工作表轉換為獨立的CSV文件
    3. 保存到指定目錄
    4. 返回保存的文件路徑列表
    
    參數：
        uploaded_file: Streamlit上傳的文件對象
        save_dir (str): 保存目錄路徑
    
    返回：
        list: 保存的CSV文件路徑列表
    
    技術細節：
    - 使用pandas讀取Excel文件
    - 自動創建保存目錄
    - 使用UTF-8-SIG編碼確保中文正確顯示
    - 文件名格式：原文件名_工作表名.csv
    
    示例：
        >>> paths = save_excel_as_csvs(excel_file, "data/excel")
        >>> print(f"轉換了 {len(paths)} 個工作表")
    """
    # 創建保存目錄
    os.makedirs(save_dir, exist_ok=True)
    
    # 讀取Excel文件
    excel = pd.ExcelFile(uploaded_file)
    saved_paths = []
    
    # 遍歷所有工作表
    for sheet_name in excel.sheet_names:
        # 讀取工作表數據
        df = excel.parse(sheet_name)
        
        # 構建CSV文件名
        filename = f"{os.path.splitext(uploaded_file.name)[0]}_{sheet_name}.csv"
        path = os.path.join(save_dir, filename)
        
        # 保存為CSV文件
        df.to_csv(path, index=False, encoding="utf-8-sig")
        saved_paths.append(path)
    
    return saved_paths


def select_files():
    """
    通用文件選擇器
    
    功能：
    1. 提供文件類型選擇界面
    2. 支持論文資料和實驗數據兩種模式
    3. 根據文件類型顯示不同的上傳選項
    4. 返回選擇的文件信息
    
    返回：
        dict: 包含文件類型和文件列表的字典，如果沒有選擇則返回None
    
    支持的文件類型：
    - 論文資料：PDF、DOCX
    - 實驗數據：XLSX、DOCX
    
    界面特點：
    - 使用Streamlit的radio組件選擇文件類型
    - 使用file_uploader組件支持多文件上傳
    - 提供清晰的用戶提示和說明
    """
    st.subheader("📂 功能3：選擇欲匯入的資料")
    
    # 文件類型選擇
    file_type = st.radio("請選擇要匯入的資料類型：", ["📄 論文資料", "🧪 實驗數據"])

    if file_type == "📄 論文資料":
        # 論文資料上傳界面
        paper_files = st.file_uploader(
            "請選擇PDF或Word檔（可多選）：", 
            type=["pdf", "docx"], 
            accept_multiple_files=True
        )
        
        if paper_files:
            return {"type": "📄 論文資料", "files": paper_files}

    elif file_type == "🧪 實驗數據":
        # 實驗數據上傳界面
        data_files = st.file_uploader(
            "請選擇excel或word檔（可多選）：", 
            type=["xlsx", "docx"], 
            accept_multiple_files=True
        )

        if data_files:
            return {"type": "🧪 實驗數據", "files": data_files}
    
    return None


def select_files_paper_mode():
    """
    論文模式文件選擇器
    
    功能：
    1. 專門用於論文資料上傳
    2. 簡化的界面，只支持論文文件
    3. 提供英文界面標題
    4. 返回論文文件信息
    
    返回：
        dict: 包含文件類型和文件列表的字典
    
    特點：
    - 專門針對論文資料優化
    - 使用英文界面標題
    - 只支持PDF和DOCX格式
    - 簡化的用戶體驗
    
    使用場景：
    - 當系統主要用於論文處理時
    - 需要英文界面時
    - 簡化用戶選擇流程時
    """
    st.subheader("📂 Import the literature to the system")

    # 論文文件上傳界面
    paper_files = st.file_uploader(
        "請選擇PDF或Word檔（可多選）：", 
        type=["pdf", "docx"], 
        accept_multiple_files=True
    )

    return {"type": "📄 論文資料", "files": paper_files}


# ==================== 輔助函數 ====================

def validate_file_type(file, allowed_types):
    """
    驗證文件類型是否允許
    
    功能：
    1. 檢查文件擴展名
    2. 驗證文件類型是否在允許列表中
    3. 返回驗證結果
    
    參數：
        file: 文件對象
        allowed_types (list): 允許的文件類型列表
    
    返回：
        bool: 文件類型是否有效
    """
    if file is None:
        return False
    
    file_extension = os.path.splitext(file.name)[1].lower()
    return file_extension in allowed_types


def get_file_info(files):
    """
    獲取文件列表的統計信息
    
    功能：
    1. 統計文件數量和類型
    2. 計算總文件大小
    3. 返回文件統計信息
    
    參數：
        files: 文件列表
    
    返回：
        dict: 文件統計信息
    """
    if not files:
        return {"count": 0, "total_size": 0, "types": {}}
    
    total_size = 0
    type_count = {}
    
    for file in files:
        # 計算文件大小
        file.seek(0, 2)  # 移動到文件末尾
        size = file.tell()
        file.seek(0)  # 重置到文件開頭
        total_size += size
        
        # 統計文件類型
        file_type = os.path.splitext(file.name)[1].lower()
        type_count[file_type] = type_count.get(file_type, 0) + 1
    
    return {
        "count": len(files),
        "total_size": total_size,
        "types": type_count
    }


def format_file_size(size_bytes):
    """
    格式化文件大小顯示
    
    功能：
    1. 將字節數轉換為人類可讀的格式
    2. 自動選擇合適的單位（B、KB、MB、GB）
    3. 保留適當的小數位數
    
    參數：
        size_bytes (int): 文件大小（字節）
    
    返回：
        str: 格式化後的文件大小字符串
    """
    if size_bytes == 0:
        return "0 B"
    
    units = ['B', 'KB', 'MB', 'GB']
    unit_index = 0
    
    while size_bytes >= 1024 and unit_index < len(units) - 1:
        size_bytes /= 1024
        unit_index += 1
    
    return f"{size_bytes:.1f} {units[unit_index]}"


# ==================== 測試代碼 ====================
if __name__ == "__main__":
    """
    測試文件選擇器功能
    
    這個測試代碼用於驗證文件處理功能是否正常工作
    """
    print("🧪 開始測試文件選擇器功能...")
    
    # 測試文件類型驗證
    test_files = [
        {"name": "test.pdf", "type": "pdf"},
        {"name": "test.docx", "type": "docx"},
        {"name": "test.xlsx", "type": "xlsx"}
    ]
    
    allowed_types = [".pdf", ".docx"]
    
    print("📋 文件類型驗證測試：")
    for file_info in test_files:
        is_valid = file_info["type"] in [t[1:] for t in allowed_types]
        print(f"  {file_info['name']}: {'✅' if is_valid else '❌'}")
    
    print("✅ 文件選擇器功能測試完成")
