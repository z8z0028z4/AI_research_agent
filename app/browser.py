
import streamlit as st
import os
import pandas as pd


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
            return {"type": "📄 論文資料", "files": paper_files}

    elif file_type == "🧪 實驗數據":
        data_files = st.file_uploader("請選擇 excel 或 word 檔（可多選）：", type=["xlsx", "docx"], accept_multiple_files=True)

        if data_files:
            return {"type": "🧪 實驗數據", "files": data_files}
    return None
