import streamlit as st
from perplexity_search_fallback import ask_perplexity
import os
import pandas as pd
import re
from knowledge_agent import agent_answer, load_experiment_log
from config import OPENAI_API_KEY
from browser import select_files  # ← 加在 import 區域
from file_upload import process_uploaded_files
import tempfile
from file_upload import process_uploaded_files
from chunk_embedding import embed_documents_from_metadata

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

st.set_page_config(page_title="研究助理系統", layout="wide")
st.title("🧪 AI 研究助理系統")
tab1, tab2, tab3 = st.tabs(["📘 知識庫助理", "🔍 搜尋外部文獻", "📥 論文/實驗資料上傳"])

with tab1:
    st.subheader("📘 功能 1：利用知識庫回答問題")
    q1 = st.text_area("請輸入研究問題：", height=100, key="search1")

    if st.button("由知識庫回答", key="knowledgebtn"):
        with st.spinner("查詢知識庫中..."):
            df = load_experiment_log()
            result = agent_answer(q1, df)

            # 顯示回答區
            st.markdown("### 🤖 回答")
            st.markdown(result["answer"])

            # 顯示引用區
            st.markdown("### 📚 引用資料")
            for i, citation in enumerate(result["citations"], start=1):
                title = citation.get("title", "未知")
                page = citation.get("page", "?")
                snippet = citation.get("snippet", "...")

                st.markdown(f"**[{i}]** `{title}` | 頁碼：{page} | 段落開頭：\"{snippet}\"")


with tab2:
    st.subheader("🔍 功能 2：使用 Perplexity 搜尋文獻")
    q2 = st.text_area("請輸入要搜尋的文獻問題：", height=100, key="search2")
    if st.button("搜尋文獻", key="searchbtn"):
        with st.spinner("使用 Perplexity 搜尋中..."):
            result = ask_perplexity(q2)
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

if "processed_files" not in st.session_state:
    st.session_state.processed_files = set()

with tab3:
    file_info = select_files()
    if file_info:
        st.markdown(f"🔎 資料類型：{file_info['type']}")
        for f in file_info["files"]:
            st.write(f"📄 {f.name}")

        # 🧠 過濾掉已處理的檔案（依檔名）
        new_streamlit_files = [f for f in file_info["files"] if f.name not in st.session_state.processed_files]

        if new_streamlit_files:
            new_file_paths = []
            messages = []

            with st.spinner("📥 處理上傳的資料中..."):
                def update_status(msg):
                    messages.append(msg)

                # 將 UploadedFile 寫入暫存檔，取得實際路徑
                for f in new_streamlit_files:
                    suffix = os.path.splitext(f.name)[1]
                    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                        tmp.write(f.read())
                        tmp_path = tmp.name
                        new_file_paths.append(tmp_path)
                        st.session_state.processed_files.add(f.name)  # ✅ 僅記錄檔名避免重複

                # 開始處理資料
                metadata_list = process_uploaded_files(new_file_paths, status_callback=update_status)
                print("🧾 本次處理檔案：", new_file_paths)
                embed_documents_from_metadata(metadata_list)

            if messages:
                with st.expander("📋 處理紀錄", expanded=True):
                    for m in messages:
                        st.markdown(f"- {m}")
        else:
            st.info("✅ 所有檔案都已處理過，不重複處理。")