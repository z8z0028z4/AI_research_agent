import streamlit as st
from perplexity_search_fallback import ask_perplexity
from search_agent import search_and_download_only
import os
import tempfile
import re
from knowledge_agent import agent_answer, load_experiment_log
from browser import select_files
from file_upload import process_uploaded_files
from chunk_embedding import embed_documents_from_metadata, embed_experiment_txt_batch
import pandas as pd
from excel_to_txt_by_row import export_new_experiments_to_txt
from config import EXPERIMENT_DIR

st.set_page_config(page_title="研究助理系統", layout="wide")
st.title("🧪 AI 研究助理系統")

tab1, tab2, tab3, tab4 = st.tabs([
    "📘 知識庫助理",
    "🔍 搜尋外部文獻並下載 PDF",
    "📥 論文/實驗資料上傳",
    "🌐 使用 Perplexity 搜尋"
])

def format_references_block(text):
    refs = []
    in_reference = False
    for line in text.splitlines():
        if line.strip().lower().startswith("reference") or line.strip().lower().startswith("references"):
            in_reference = True
            continue
        if in_reference and line.strip():
            refs.append(line.strip())
    markdown_links = []
    for ref in refs:
        match = re.match(r"\[(\d+)\]\s*(.*?)(https?://\S+)", ref)
        if match:
            idx, title, url = match.groups()
            markdown_links.append(f"[{idx}] [{title.strip()}]({url.strip()})")
        else:
            markdown_links.append(ref)
    return markdown_links

with tab1:
    st.subheader("📘 功能 1：利用知識庫回答問題")
    st.markdown("### ⚙️ 選擇回答模式")
    answer_mode = st.radio(
        "請選擇系統回答問題的方式：",
        options=[
            "僅嚴謹文獻溯源",
            "允許延伸與推論",
            "納入實驗資料，進行推論與建議"
        ],
        index=0,
        key="mode_selector"
    )

    q1 = st.text_area("請輸入研究問題：", height=100, key="search1")

    if st.button("由知識庫回答", key="knowledgebtn"):
        with st.spinner("查詢知識庫中..."):
            use_inference = answer_mode != "僅嚴謹文獻溯源"
            use_experiment = answer_mode == "納入實驗資料，進行推論與建議"
            df = load_experiment_log() if use_experiment else pd.DataFrame()

            result = agent_answer(q1, df, inference=use_inference, use_experiment=use_experiment)

            st.markdown("### 🤖 回答")
            st.markdown(result["answer"])

            st.markdown("### 📚 引用資料")
            for i, citation in enumerate(result["citations"], start=1):
                title = citation.get("title", "未知")
                page = citation.get("page", "?")
                snippet = citation.get("snippet", "...")
                st.markdown(f"**[{i}]** `{title}` | 頁碼：{page} | 段落開頭：{snippet}")

with tab2:
    st.subheader("🔍 功能 2：使用關鍵字搜尋外部文獻並下載 PDF")
    q2 = st.text_area("請輸入查詢問題（將自動萃取關鍵字）：", height=100, key="search_pdf")
    if st.button("執行查詢與下載", key="downloadbtn"):
        with st.spinner("🔍 查詢並下載中..."):
            pdfs = search_and_download_only(q2, top_k=5, storage_dir="data/chemrxiv")
            if pdfs:
                st.success(f"✅ 共下載 {len(pdfs)} 篇 PDF")
                for path in pdfs:
                    st.markdown(f"- `{os.path.basename(path)}`")
            else:
                st.warning("⚠️ 未成功下載任何 PDF")



with tab3:
    if "processed_files" not in st.session_state:
        st.session_state.processed_files = set()


    file_info = select_files() 
    if file_info:
        file_type = file_info["type"] 
        
        st.markdown(f"🔎 資料類型：{file_type}")
        for f in file_info["files"]:
            st.write(f"📄 {f.name}")

        if file_type == "📄 論文資料":
            new_files = [f for f in file_info["files"] if f.name not in st.session_state.processed_files]

            if not new_files:
                st.info("✅ 所有檔案都已處理過，不重複處理。")
            else:
                with st.spinner("📥 處理論文資料中..."):
                    new_file_paths = []
                    messages = []

                    def update_status(msg):
                        messages.append(msg)

                    for f in new_files:
                        suffix = os.path.splitext(f.name)[1]
                        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                            tmp.write(f.read())
                            tmp_path = tmp.name
                            new_file_paths.append(tmp_path)
                            st.session_state.processed_files.add(f.name)

                    metadata_list = process_uploaded_files(new_file_paths, status_callback=update_status)
                    embed_documents_from_metadata(metadata_list)

                    if messages:
                        with st.expander("📋 處理紀錄", expanded=True):
                            for m in messages:
                                st.markdown(f"- {m}")

        elif file_type == "🧪 實驗數據":
            with st.spinner("📥 開始處理實驗資料..."):
                for f in file_info["files"]:  # 每次都處理，不跳過
                    temp_path = os.path.join("uploaded", f.name)
                    os.makedirs("uploaded", exist_ok=True)
                    with open(temp_path, "wb") as tmp:
                        tmp.write(f.read())

                    result_df, txt_paths = export_new_experiments_to_txt(
                        excel_path=temp_path,
                        output_dir=EXPERIMENT_DIR
                    )

                    

                embed_experiment_txt_batch(txt_paths)
                st.success(f"✅ 已處理：{f.name}，共 {len(txt_paths)} 筆")
                st.dataframe(result_df)


with tab4:
    st.subheader("🌐 功能 4：使用 Perplexity 搜尋文獻")
    q4 = st.text_area("請輸入要搜尋的文獻問題：", height=100, key="search4")
    if st.button("使用 Perplexity 搜尋", key="perplexitybtn"):
        with st.spinner("使用 Perplexity 搜尋中..."):
            result = ask_perplexity(q4)
            if result["success"]:
                st.markdown("### 🤖 文獻摘要")
                st.write(result["answer"])

                st.markdown("### 🔗 引用來源")
                links = format_references_block(result["answer"])
                if links:
                    for link in links:
                        st.markdown(f"- {link}")
                else:
                    st.info("未偵測到結構化 Reference 區塊。")
            else:
                st.error("❌ 搜尋失敗：" + result["error"])