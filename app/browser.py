
import streamlit as st
import os
import pandas as pd
from config import PAPER_DIR, EXPERIMENT_CSV_DIR


def save_excel_as_csvs(uploaded_file, save_dir):
    os.makedirs(save_dir, exist_ok=True)
    excel = pd.ExcelFile(uploaded_file)
    saved_paths = []
    for sheet_name in excel.sheet_names:
        df = excel.parse(sheet_name)
        filename = f"{os.path.splitext(uploaded_file.name)[0]}_{sheet_name}.csv"
        path = os.path.join(save_dir, filename)
        df.to_csv(path, index=False, encoding="utf-8-sig")
        saved_paths.append(path)
    return saved_paths

def select_files():
    st.subheader("📂 功能 3：選擇欲匯入的資料")
    file_type = st.radio("請選擇要匯入的資料類型：", ["📄 論文資料", "🧪 實驗數據"])

    if file_type == "📄 論文資料":
        paper_files = st.file_uploader("請選擇 PDF 或 Word 檔（可多選）：", type=["pdf", "docx"], accept_multiple_files=True)
        if paper_files:
            return {"type": "paper", "files": paper_files}

    elif file_type == "🧪 實驗數據":
        data_files = st.file_uploader("請選擇 CSV 或 Excel 檔（可多選）：", type=["csv", "xlsx"], accept_multiple_files=True)
        saved_paths = []

        if data_files:
            os.makedirs(EXPERIMENT_CSV_DIR, exist_ok=True)

            for f in data_files:
                if f.name.endswith(".csv"):
                    save_path = os.path.join(EXPERIMENT_CSV_DIR, f.name)
                    with open(save_path, "wb") as out:
                        out.write(f.getbuffer())
                    saved_paths.append(save_path)

                elif f.name.endswith(".xlsx"):
                    # ⬇️ 使用你寫好的這個函式
                    paths = save_excel_as_csvs(f, EXPERIMENT_CSV_DIR)
                    saved_paths.extend(paths)

            if saved_paths:
                st.success(f"✅ 已儲存 {len(saved_paths)} 筆檔案到 {EXPERIMENT_CSV_DIR}")

            return {"type": "experiment", "files": data_files}

    return None
