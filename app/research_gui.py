import streamlit as st
from perplexity_search_fallback import ask_perplexity
from search_agent import search_and_download_only
import os
import tempfile
import re
from knowledge_agent import agent_answer
from browser import select_files
from file_upload import process_uploaded_files
from chunk_embedding import embed_documents_from_metadata, embed_experiment_txt_batch
import pandas as pd
from excel_to_txt_by_row import export_new_experiments_to_txt
from config import EXPERIMENT_DIR
from pubchem_handler import chemical_metadata_extractor
from rag_core import build_detail_experimental_plan_prompt
from docx import Document
from docx.shared import Inches
from io import BytesIO
def update_gui_with_docx_data():
    docx_data = st.session_state.get("docx_data", {})

    st.markdown("### 🤖 Generated proposal")
    st.markdown(docx_data.get("proposal", ""))

    render_chemical_table(docx_data.get("chemicals", []))

    if docx_data.get("not_found"):
        st.markdown("### ⚠️ 以下化學品未能查詢成功")
        for name in docx_data["not_found"]:
            st.markdown(f"- {name}")

    if docx_data.get("experiment_detail"):
        st.markdown("### 🔬 Suggested experiment details")
        st.markdown(docx_data["experiment_detail"])

    with st.expander("📚 Citations ", expanded=False):
        st.markdown("### 📚 Citations ")
        for i, citation in enumerate(docx_data.get("citations", []), start=1):
            title = citation.get("title", "未知")
            page = citation.get("page", "?")
            snippet = citation.get("snippet", "...")
            st.markdown(f"**[{i}]** {title} | 頁碼：{page} | 段落開頭：{snippet}")
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
def render_chemical_table(chemical_metadata_list):
    st.markdown("### 🧪 Chemical Summary Table")

    for chem in chemical_metadata_list:
        cols = st.columns([2, 2, 3, 3])

        # Chemical Name
        with cols[0]:
            url = chem.get("pubchem_url")
            if url:
                st.markdown(f"[**{chem.get('name', 'Unknown')}**]({url})")
            else:
                st.markdown(f"**{chem.get('name', 'Unknown')}**")
            

        # Structure Image
        with cols[1]:
            st.image(chem.get("image_url", ""), width=200)

        # Properties block
        with cols[2]:
            st.markdown("**Properties**")
            st.markdown(f"- **Formula**: `{chem.get('formula', '-')}`")
            st.markdown(f"- **MW**: `{chem.get('weight', '-')}`")
            st.markdown(f"- **Boiling Point**: `{chem.get('boiling_point_c', '-')}`")
            st.markdown(f"- **Melting Point**: `{chem.get('melting_point_c', '-')}`")
            st.markdown(f"- **CAS No.**: `{chem.get('cas', '-')}`")
            st.markdown(f"- **SMILES**: `{chem.get('smiles', '-')}`")

        # Safety block (GHS + NFPA)
        with cols[3]:
            st.markdown("**Handling Safety**")
            if chem.get("safety_icons", {}).get("nfpa_image"):
                st.image(chem["safety_icons"]["nfpa_image"], width=60)

            ghs = chem.get("safety_icons", {}).get("ghs_icons", [])
            if ghs:
                st.image(ghs, width=50)

        st.markdown("---")

st.set_page_config(page_title="AI Chemist", layout="wide")
st.title("🧪 AI Chemist")

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Proposal generator",
    "🔍 搜尋外部文獻並下載 PDF",
    "📥 論文/實驗資料上傳",
    "🌐 使用 Perplexity 搜尋",
    "📘 知識庫助理, archive functions"
])

with tab1:
    st.subheader("✍️ Proposal Generator")

    q1 = st.text_area("Please enter your research goal：", height=100, key="search1")

    if st.button("✍️ Generate proposal", key="generate_proposal_btn"):
        with st.spinner("📖 Gathering information from knowledgebase and drafting proposal..."):
            result = agent_answer(q1, mode="make proposal")
            chemical_metadata_list, not_found_list, proposal_answer = chemical_metadata_extractor(result["answer"])

            st.session_state["docx_data"] = {
                "proposal": proposal_answer,
                "chemicals": chemical_metadata_list,
                "not_found": not_found_list,
                "citations": result.get("citations", []),
                "experiment_detail": ""
            }
            st.session_state["proposal_chunks"] = result.get("chunks", [])
            st.rerun()

    if "docx_data" in st.session_state:
        update_gui_with_docx_data()
    
        st.markdown("### 💡 Don't like the proposal？ Provide your opinion here")
        user_reason = st.text_input("How you want to revise?", key="revise_reason")

        if st.button("💡 Generate New Idea", key="new_idea_btn"): #修改proposal
            with st.spinner("🔄 Revise proposal based on your reason and knowledgebase..."):
                old_chunks = st.session_state.get("proposal_chunks", [])
                past_proposal = st.session_state["docx_data"].get("proposal", "")
                result = agent_answer(
                    user_reason,
                    mode="generate new idea",
                    chunks=old_chunks,
                    proposal=past_proposal
                )
                chemical_metadata_list, not_found_list, proposal_answer = chemical_metadata_extractor(result["answer"])
                st.session_state["docx_data"].update({
                    "proposal": proposal_answer,
                    "chemicals": chemical_metadata_list,
                    "not_found": not_found_list,
                    "citations": result.get("citations", []),
                    "experiment_detail": ""
                })
                st.session_state["proposal_chunks"] = result.get("chunks", [])
                st.rerun()

        if st.button("✅ Accept & Generate Experiment Detail", key="accept_btn"): #生成實驗細節
                    with st.spinner("🧪 Generating experimental details..."):
                        chunks = st.session_state.get("proposal_chunks", [])
                        proposal = st.session_state["docx_data"].get("proposal", "")
                        result = agent_answer(
                            "",
                            mode="expand to experiment detail",
                            chunks=chunks,
                            proposal=proposal
                        )
                        st.session_state["docx_data"]["experiment_detail"] = result["answer"]
                        st.rerun()
                        
        if st.button("📥 Prepare proposal.docx"): #下載文件按鈕
            docx_data = st.session_state.get("docx_data", {})
            doc = Document()
            doc.add_heading("AI Generated Research Proposal", 0)

            # Proposal Section
            doc.add_heading("Proposal", level=1)
            doc.add_paragraph(docx_data.get("proposal", ""))

            # Chemical Table
            doc.add_heading("Chemical Summary Table", level=1)
            table = doc.add_table(rows=1, cols=6)
            hdr = table.rows[0].cells
            hdr[0].text = "Name"
            hdr[1].text = "Formula"
            hdr[2].text = "MW"
            hdr[3].text = "Boiling Point (°C)"
            hdr[4].text = "Melting Point (°C)"
            hdr[5].text = "CAS No."

            for chem in docx_data.get("chemicals", []):
                row = table.add_row().cells
                row[0].text = chem.get("name", "-") or "-"
                row[1].text = chem.get("formula", "-") or "-"
                row[2].text = str(chem.get("weight", "-") or "-")
                row[3].text = str(chem.get("boiling_point_c", "-") or "-")
                row[4].text = str(chem.get("melting_point_c", "-") or "-")
                row[5].text = chem.get("cas", "-") or "-"

            # Not Found Chemicals
            not_found = docx_data.get("not_found", [])
            if not_found:
                doc.add_heading("Not Found Chemicals", level=2)
                for name in not_found:
                    doc.add_paragraph(f"- {name}")

            # Experiment Details
            doc.add_heading("Experimental Plan", level=1)
            doc.add_paragraph(docx_data.get("experiment_detail", ""))

            # Citations
            doc.add_heading("Citations", level=1)
            for i, c in enumerate(docx_data.get("citations", []), 1):
                doc.add_paragraph(f"[{i}] {c.get('title', '')} | Page {c.get('page', '')} | Snippet: {c.get('snippet', '')}")

            # Save and Download
            with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as tmp:
                doc.save(tmp.name)
                tmp_path = tmp.name

            with open(tmp_path, "rb") as f:
                st.download_button(
                    label="📥 Click to download",
                    data=f,
                    file_name="proposal_report.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                )

            os.unlink(tmp_path)

            

with tab2:
    st.subheader("🔍 功能 2：使用關鍵字搜尋外部文獻並下載 PDF")
    q2 = st.text_area("請輸入查詢問題（將自動萃取關鍵字）：", height=100, key="search_pdf")
    if st.button("執行查詢與下載", key="downloadbtn"):
        with st.spinner("🔍 查詢並下載中..."):
            pdfs = search_and_download_only(q2, top_k=5, storage_dir="data/paper")
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


with tab5:
    st.subheader("📘 功能 1：利用知識庫回答問題")
    st.markdown("### ⚙️ 選擇回答模式")
    answer_mode = st.radio(
        "請選擇系統回答問題的方式：",
        options=[
            "僅嚴謹文獻溯源",
            "允許延伸與推論",
            "納入實驗資料，進行推論與建議",
            "make proposal"
        ],
        index=0,
        key="mode_selector"
    )

    q1 = st.text_area("請輸入研究問題：", height=100, key="search_2")

    if st.button("由知識庫回答", key="knowledgebtn"):
        with st.spinner("查詢知識庫中..."):
            result = agent_answer(q1, mode = answer_mode)
            #產生乾淨答案 (分離LLM答案中的json)
            if answer_mode == "make proposal":
                chemical_metadata_list, not_found_list, proposal_answer = chemical_metadata_extractor(result["answer"])
                st.session_state["proposal_chunks"] = result.get("chunks", [])
                st.session_state["proposal_answer"] = proposal_answer
                st.session_state["not_found_list"] = not_found_list
                st.session_state["chemical_metadata_list"] = chemical_metadata_list
                st.session_state["result"] = result
    
    has_proposal = (
    "proposal_answer" in st.session_state and
    "chemical_metadata_list" in st.session_state
    )

    if has_proposal:
        st.markdown("### 🤖 回答")
        st.markdown(st.session_state["proposal_answer"])

        if st.session_state.get("chemical_metadata_list"):
            render_chemical_table(st.session_state["chemical_metadata_list"])
        if st.session_state.get("not_found_list"):
            st.markdown("### ⚠️ 以下化學品未能查詢成功")
            for name in st.session_state["not_found_list"]:
                st.markdown(f"- {name}")      
            
        
        st.markdown("### 💡 Don't like the proposal？ Provide your opinion here")
        user_reason = st.text_input("How you want to revise?", key="revise_reason_2")
        if st.button("💡 Generate New Idea", key="new_idea_btn_2"):
            with st.spinner("🔄 根據您的理由重新檢索文獻並生成提案..."):
                old_chunks = st.session_state.get("proposal_chunks", [])
                past_proposal = st.session_state.get("proposal_answer", "")

                result = agent_answer(
                    user_reason,
                    mode="generate new idea",
                    chunks=old_chunks,
                    proposal=past_proposal
                )

                # ✅ 直接覆蓋 session_state，繼續共用顯示區塊
                st.session_state["proposal_chunks"] = result.get("chunks", [])
                st.session_state["proposal_answer"] = result["answer"]
                print(result["answer"])
                print(result.get("chunks", []))

                chemical_metadata_list, not_found_list, _ = chemical_metadata_extractor(result["answer"])
                st.session_state["chemical_metadata_list"] = chemical_metadata_list
                st.session_state["not_found_list"] = not_found_list

                st.rerun()

        if st.button("✅ Accept & Generate Experiment Detail", key="accept_btn_2"): #按鈕生成實驗細節
            with st.spinner("🧪 正在分析實驗細節..."):
                chunks = st.session_state.get("proposal_chunks", [])
                proposal = st.session_state["result"]["answer"]
                result = agent_answer(
                    "",  # 問題不重要，給空也可以
                    mode="expand to experiment detail",
                    chunks=chunks,
                    proposal=proposal
                )
                st.markdown("### 🔬 建議實驗細節")
                st.markdown(result["answer"])


        # 📚 引用資料（支援原始或改寫皆可）
        st.markdown("### 📚 引用資料")
        for i, citation in enumerate(st.session_state.get("result", {}).get("citations", []), start=1):
            title = citation.get("title", "未知")
            page = citation.get("page", "?")
            snippet = citation.get("snippet", "...")
            st.markdown(f"**[{i}]** {title} | 頁碼：{page} | 段落開頭：{snippet}")