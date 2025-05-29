import streamlit as st
from perplexity_search_fallback import ask_perplexity
from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings
from langchain.chat_models import ChatOpenAI
import os
import pandas as pd
import re
from knowledge_agent import agent_answer, load_experiment_log
from config import OPENAI_API_KEY


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
tab1, tab2 = st.tabs(["📘 知識庫助理", "🔍 搜尋外部文獻"])

with tab1:
    st.subheader("📘 功能 1：利用知識庫回答問題")
    q1 = st.text_area("請輸入研究問題：", height=100, key="search1")
    if st.button("由知識庫回答", key="knowledgebtn"):
        with st.spinner("查詢知識庫中..."):
            df = load_experiment_log()
            result = agent_answer(q1, df)
            st.markdown("### 🤖 回答")
            st.write(result)
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