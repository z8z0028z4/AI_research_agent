import os
import pandas as pd
# 直接定義配置變量，避免循環導入
REGISTRY_PATH = "experiment_data/metadata_registry.xlsx"

# 欄位順序
METADATA_COLUMNS = [
    "tracing_number", "new_filename", "type", "doi", "title",
    "authors", "year", "venue", "url", "new_path"
]

def get_existing_metadata() -> pd.DataFrame:
    """
    獲取現有的元數據註冊表
    
    Returns:
        pd.DataFrame: 現有的元數據表格，如果文件不存在則返回None
    """
    try:
        if not os.path.exists(REGISTRY_PATH):
            return None
        return pd.read_excel(REGISTRY_PATH)
    except Exception as e:
        print(f"⚠️ 讀取元數據註冊表失敗: {e}")
        return None

def append_metadata_to_registry(metadata: dict):
    # 若檔案不存在，先建立空表格
    if not os.path.exists(REGISTRY_PATH):
        df = pd.DataFrame(columns=METADATA_COLUMNS)
    else:
        df = pd.read_excel(REGISTRY_PATH)

    # 若已有該 tracing number，跳過寫入
    if str(metadata["tracing_number"]) in df["tracing_number"].astype(str).values:
        print(f"⚠️ Tracing number {metadata['tracing_number']} 已存在，跳過寫入。")
        return

    # 加入新 metadata 並儲存
    new_row = {col: metadata.get(col, "") for col in METADATA_COLUMNS}
    original_len = len(df)
    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)

    try:
        df.to_excel(REGISTRY_PATH, index=False)
        print(f"✅ 已寫入 metadata：{metadata['new_filename']}")
        print(f"📈 寫入前筆數：{original_len}，寫入後筆數：{len(df)}")
    except Exception as e:
        print(f"❌ 寫入 Excel 時失敗：{e}")





if __name__ == "__main__":
    # 範例測試
    sample_metadata = {
        "tracing_number": "005",
        "new_filename": "005_Tuning_adsorption_capacity_SI.pdf",
        "type": "SI",
        "doi": "10.1016/j.matchemphys.2019.122601",
        "title": "Tuning adsorption capacity through ligand pre-modification in functionalized Zn-MOF analogues",
        "authors": "Yun-Si Hong; Shuangyong Sun; Qian Sun; E. Gao; M. Ye",
        "year": 2020,
        "venue": "Materials Chemistry and Physics",
        "url": "https://www.semanticscholar.org/paper/74b815089feb60969e71b5177e9629d788b7519d",
        "new_path": "experiment_data/papers/005_Tuning_adsorption_capacity_SI.pdf"
    }
    append_metadata_to_registry(sample_metadata)
