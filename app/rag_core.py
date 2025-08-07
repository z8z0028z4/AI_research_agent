"""
AI 研究助理 - RAG核心模塊
========================

這個模塊是整個系統的RAG（檢索增強生成）核心，負責：
1. 向量數據庫管理
2. 文檔檢索和相似度搜索
3. 提示詞構建和優化
4. LLM調用和回答生成

架構說明：
- 使用Chroma作為向量數據庫
- 支持多查詢檢索
- 提供多種提示詞模板
- 集成OpenAI GPT模型

⚠️ 注意：此模塊是系統的核心組件，所有知識處理都依賴於此模塊
"""

from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_core.documents import Document
from langchain.chat_models import ChatOpenAI
from config import VECTOR_INDEX_DIR, EMBEDDING_MODEL_NAME, LLM_MODEL_NAME, LLM_PARAMS
import pandas as pd
from typing import List, Tuple, Dict
import os
from collections import defaultdict

# Embedding model configuration

# ==================== 向量數據庫管理 ====================

def load_paper_vectorstore():
    """
    載入文獻向量數據庫
    
    功能：
    1. 初始化嵌入模型
    2. 連接文獻向量存儲
    3. 返回可用的向量數據庫對象
    
    返回：
        Chroma: 文獻向量數據庫對象
    
    技術細節：
    - 使用HuggingFace嵌入模型
    - 持久化存儲在paper_vector目錄
    - 集合名稱為"paper"
    """
    # Load Nomic embedding model
    try:
        print(f"🔧 Loading Nomic embedding model: {EMBEDDING_MODEL_NAME}")
        embedding_model = HuggingFaceEmbeddings(
            model_name=EMBEDDING_MODEL_NAME,
            model_kwargs={"trust_remote_code": True},
            encode_kwargs={"normalize_embeddings": True}
        )
        print("✅ Nomic embedding model loaded successfully")
    except Exception as e:
        print(f"❌ Nomic embedding failed: {e}")
        raise e
    
    paper_vector_dir = os.path.join(VECTOR_INDEX_DIR, "paper_vector")
    vectorstore = Chroma(
        persist_directory=paper_vector_dir,
        embedding_function=embedding_model, 
        collection_name="paper"
        )
    return vectorstore


def load_experiment_vectorstore():
    """
    載入實驗數據向量數據庫
    
    功能：
    1. 初始化嵌入模型
    2. 連接實驗數據向量存儲
    3. 返回可用的向量數據庫對象
    
    返回：
        Chroma: 實驗數據向量數據庫對象
    
    技術細節：
    - 使用相同的嵌入模型確保一致性
    - 持久化存儲在experiment_vector目錄
    - 集合名稱為"experiment"
    """
    # Load Nomic embedding model
    try:
        print(f"🔧 Loading Nomic embedding model: {EMBEDDING_MODEL_NAME}")
        embedding_model = HuggingFaceEmbeddings(
            model_name=EMBEDDING_MODEL_NAME,
            model_kwargs={"trust_remote_code": True},
            encode_kwargs={"normalize_embeddings": True}
        )
        print("✅ Nomic embedding model loaded successfully")
    except Exception as e:
        print(f"❌ Nomic embedding failed: {e}")
        raise e
    experiment_vector_dir = os.path.join(VECTOR_INDEX_DIR, "experiment_vector")
    vectorstore = Chroma(
        persist_directory=experiment_vector_dir, 
        embedding_function=embedding_model, 
        collection_name="experiment"
        )
    return vectorstore


# ==================== 文檔檢索功能 ====================

def retrieve_chunks_multi_query(
    vectorstore, query_list: List[str], k: int = 10, fetch_k: int = 20, score_threshold: float = 0.35
    ) -> List[Document]:
    """
    多查詢文檔檢索功能
    
    功能：
    1. 對多個查詢進行並行檢索
    2. 去重和排序檢索結果
    3. 提供詳細的檢索統計信息
    
    參數：
        vectorstore: 向量數據庫對象
        query_list (List[str]): 查詢列表
        k (int): 返回的文檔數量
        fetch_k (int): 初始檢索的文檔數量
        score_threshold (float): 相似度閾值
    
    返回：
        List[Document]: 檢索到的文檔列表
    
    技術細節：
    - 使用MMR（最大邊際相關性）搜索
    - 自動去重避免重複內容
    - 提供詳細的檢索日誌
    """
    retriever = vectorstore.as_retriever(
        search_type="mmr",
        search_kwargs={"k": k, "fetch_k": fetch_k, "score_threshold": score_threshold}
    )

    # 使用字典進行去重
    chunk_dict = defaultdict(float)
    print("🔍 查詢列表：", query_list)
    
    # 對每個查詢進行檢索
    for q in query_list:
        docs = retriever.get_relevant_documents(q)
        for doc in docs:
            # 使用唯一標識符進行去重
            key = doc.metadata.get("exp_id") or doc.metadata.get("source") or doc.page_content[:30]
            chunk_dict[key] = doc
    
    # 限制返回結果數量，使用傳入的 k 參數
    result = list(chunk_dict.values())[:k]

    # 檢索結果驗證
    if not result:
        print("⚠️ 沒有檢索到任何文檔，建議檢查檢索器或嵌入格式")
    else:
        print(f"🔍 多查詢檢索共找到 {len(result)} 個文檔：")
        print("🔍 檢索到的文檔預覽：")
        for i, doc in enumerate(result[:5], 1):
            meta = doc.metadata
            filename = meta.get("filename") or meta.get("source", "Unknown")
            page = meta.get("page_number") or meta.get("page", "?")
            preview = doc.page_content[:80].replace("\n", " ")
            print(f"--- 文檔 {i} ---")
            print(f"📄 {filename} | 頁碼 {page}")
            print(f"📝 內容預覽：{preview}")
            print()

    return result


def preview_chunks(chunks: List[Document], title: str, max_preview: int = 5):
    """
    預覽文檔塊內容
    
    功能：
    1. 顯示文檔塊的基本信息
    2. 提供內容預覽
    3. 幫助調試和驗證檢索結果
    
    參數：
        chunks (List[Document]): 文檔塊列表
        title (str): 預覽標題
        max_preview (int): 最大預覽數量
    """
    print(f"\n📦【{title}】共找到 {len(chunks)} 個文檔塊")

    if not chunks:
        print("⚠️ 沒有任何段落可顯示。")
        return

    # 顯示前幾個文檔塊的詳細信息
    for i, doc in enumerate(chunks[:max_preview], 1):
        meta = doc.metadata
        filename = meta.get("filename") or meta.get("source", "Unknown")
        page = meta.get("page_number") or meta.get("page", "?")
        preview = doc.page_content[:100].replace("\n", " ")
        print(f"--- Chunk {i} ---")
        print(f"📄 Filename: {filename} | Page: {page}")
        print(f"📚 Preview: {preview}")


# ==================== 提示詞構建功能 ====================

def build_prompt(chunks: List[Document], question: str) -> Tuple[str, List[Dict]]:
    # 檢查：chunks 必須是 List[Document]，question 應為 str
    context_text = ""
    citations = []
    citation_map = {}
    
    for i, doc in enumerate(chunks):
        # 檢查：doc 應有 metadata 屬性，且為 dict
        metadata = doc.metadata
        title = metadata.get("title", "Untitled")
        # 檢查：filename 來源於 "filename" 或 "source"，若都無則為 "Unknown"
        filename = metadata.get("filename") or metadata.get("source", "Unknown")
        # 檢查：page 來源於 "page_number" 或 "page"，若都無則為 "?"
        page = metadata.get("page_number") or metadata.get("page", "?")
        # 預覽片段，取前 80 字元，並將換行替換為空格
        snippet = doc.page_content[:80].replace("\n", " ")

        # 檢查：避免重複的 (filename, page) 組合
        citation_key = f"{filename}_p{page}"
        if citation_key not in citation_map:
            label = f"[{len(citations) + 1}]"
            citations.append({
                "label": label,
                "title": title,
                "source": filename,
                "page": page,
                "snippet": snippet
            })
            citation_map[citation_key] = label
        else:
            label = citation_map[citation_key]

        # context_text 累加每個 chunk 的內容，格式為 [n] title | Page n
        context_text += f"{label} {title} | Page {page}\n{doc.page_content}\n\n"

    # system_prompt 為最終提示詞，包含 context_text 及 question
    system_prompt = f"""

    你是一位研究文獻搜尋助理，僅根據提供的文獻段落來並回答問題。
    請在回答中使用 [1], [2] 等標註段落出處，不要在結尾重複列出來源。
    如段落中有提到具體的實驗條件（溫度、時間等），請務必包含在回答中。
    重要：只能引用提供的文獻段落，當前提供的文獻段落編號為 [1] 到 [{len(chunks)}]（共 {len(chunks)} 個段落）

    --- 文獻摘要 ---
    {context_text}


    --- 問題 ---
    {question}
    """
    # 檢查：回傳 system_prompt 去除首尾空白，以及 citations 列表
    return system_prompt.strip(), citations


def call_llm(prompt: str) -> str:
    print(f"🔍 調用 LLM，提示詞長度：{len(prompt)} 字符")
    try:
        llm = ChatOpenAI(**LLM_PARAMS)
        response = llm.invoke(prompt)
        print(f"✅ LLM 調用成功，回應長度：{len(response.content)} 字符")
        print(f"📝 LLM 回應預覽：{response.content[:200]}...")
        return response.content
    except Exception as e:
        print(f"❌ LLM 調用失敗：{e}")
        return ""

def build_inference_prompt(chunks: List[Document], question: str) -> Tuple[str, List[Dict]]:
    context_text = ""
    citations = []
    citation_map = {}
    
    for i, doc in enumerate(chunks):
        meta = doc.metadata
        title = meta.get("title", "Untitled")
        filename = meta.get("filename") or meta.get("source", "Unknown")
        page = meta.get("page_number") or meta.get("page", "?")
        snippet = doc.page_content[:80].replace("\n", " ")
        
        # 檢查：避免重複的 (filename, page) 組合
        citation_key = f"{filename}_p{page}"
        if citation_key not in citation_map:
            label = f"[{len(citations) + 1}]"
            citations.append({
                "label": label,
                "title": title,
                "source": filename,
                "page": page,
                "snippet": snippet
            })
            citation_map[citation_key] = label
        else:
            label = citation_map[citation_key]

        context_text += f"{label} {title} | Page {page}\n{doc.page_content}\n\n"

    system_prompt = f"""
    你是一位材料合成顧問，你了解並善於比較材料間於化學、物理性質上的差異，能夠針對尚未有明確文獻的情境，根據已知之實驗條件推論出創新建議。

    請根據以下文獻與實驗資料，進行延伸思考：
    - 你可以提出新的組合、溫度、時間或路徑。
    - 即使文獻中尚未記載的組合也可以建議，但要提出合理推論。
    - 推論、延伸思考的同時，請儘可能提到「這樣的想法源於哪種文獻線索」來輔助解釋，當前提供的文獻段落編號為 [1] 到 [{len(chunks)}]（共 {len(chunks)} 個段落）

    --- 文獻摘要 ---
    {context_text}

    --- 問題 ---
    {question}
    """
    return system_prompt.strip(), citations

def build_dual_inference_prompt(
    chunks_paper: List[Document],
    question: str,
    experiment_chunks: List[Document]
    ) -> Tuple[str, List[Dict]]:

    paper_context_text = ""
    exp_context_text = ""
    citations = []
    label_index = 1

    # --- 文獻摘要 ---
    paper_context_text += "--- 文獻摘要 ---\n"
    for doc in chunks_paper:
        meta = doc.metadata
        title = meta.get("title", "Untitled")
        filename = meta.get("filename") or meta.get("source", "Unknown")
        page = meta.get("page_number") or meta.get("page", "?")
        snippet = doc.page_content[:80].replace("\n", " ")
        label = f"[{label_index}]"

        citations.append({
            "label": label,
            "title": title,
            "source": filename,
            "page": page,
            "snippet": snippet,
            "type": "paper"
        })

        paper_context_text += f"{label} {title} | Page {page}\n{doc.page_content}\n\n"
        label_index += 1

    # --- 實驗摘要 ---
    exp_context_text += "--- 類似實驗摘要 ---\n"
    for doc in experiment_chunks:
        meta = doc.metadata
        filename = meta.get("filename") or meta.get("source", "Unknown")
        exp_id = meta.get("exp_id", "unknown_exp")
        snippet = doc.page_content[:80].replace("\n", " ")
        label = f"[{label_index}]"

        citations.append({
            "label": label,
            "title": exp_id,
            "source": filename,
            "page": "-",  # 沒有頁數
            "snippet": snippet,
            "type": "experiment"
        })

        exp_context_text += f"{label} 實驗 {exp_id}\n{doc.page_content}\n\n"
        label_index += 1
        
    # --- Prompt 注入 ---
    system_prompt = f"""
    你是一位材料合成顧問，你了解並善於比較材料在化學與物理性質上的差異。

    你將看到三個部分資訊，請綜合分析，對實驗進行具體推論與創新建議：
    1. 文獻摘要（有標註來源 [1]、[2]）
    2. 類似實驗摘要（來自向量資料庫）
    3. 實驗紀錄（表格）

    請針對研究問題提出新的建議，包含：
    - 調整的合成路徑、條件（如溫度、時間、配比）
    - 可能影響合成成功率的變因
    - 推論其背後的原因，必要時引用文獻（[1]、[2]...）或類似實驗結果
    重要：只能引用提供的文獻段落，當前提供的文獻段落編號為 [1] 到 [{len(chunks_paper) + len(experiment_chunks)}]（共 {len(chunks_paper) + len(experiment_chunks)} 個段落）

    --- 文獻知識來源 ---
    {paper_context_text}

    --- 實驗紀錄 ---
    {exp_context_text}

    --- 研究問題 ---
    {question}
    """
    return system_prompt.strip(), citations



def expand_query(user_prompt: str) -> List[str]:
    """
    將使用者輸入的自然語言問題轉為多個 semantic search 查詢語句。
    回傳的英文語句可用於文獻向量檢索。
    """
    llm = ChatOpenAI(**LLM_PARAMS)

    system_prompt = """You are a scientific assistant helping expand a user's synthesis question into multiple semantic search queries. 
    Each query should be precise, relevant, and useful for retrieving related technical documents. 
    Only return a list of 3 to 6 search queries in English. Do not explain, do not include numbering if not needed.

    你是一位科學助理，協助將使用者的合成相關問題擴展為多個語意搜尋查詢。
    每個查詢都應該準確、相關，並有助於檢索相關的技術文件。
    只需回傳 3 到 6 個英文查詢的列表。不需要解釋，也不需加上編號（除非必要）。"""

    full_prompt = f"{system_prompt}\n\nUser question:\n{user_prompt}"

    output = llm.predict(full_prompt).strip()

    # 嘗試解析成 query list
    if output.startswith("[") and output.endswith("]"):
        try:
            return eval(output)
        except Exception:
            pass  # fall back

    queries = [line.strip("-• ").strip() for line in output.split("\n") if line.strip()]
    return [q for q in queries if len(q) > 4]


def build_proposal_prompt(chunks: List[Document], question: str) -> Tuple[str, List[Dict]]:
    paper_context_text = ""
    citations = []
    citation_map = {}

    for i, doc in enumerate(chunks):
        
        meta = doc.metadata
        title = meta.get("title", "Untitled")
        filename = meta.get("filename") or meta.get("source", "Unknown")
        page = meta.get("page_number") or meta.get("page", "?")
        snippet = doc.page_content[:80].replace("\n", " ")
        
        # 檢查：避免重複的 (filename, page) 組合
        citation_key = f"{filename}_p{page}"
        if citation_key not in citation_map:
            label = f"[{len(citations) + 1}]"
            citations.append({
                "label": label,
                "title": title,
                "source": filename,
                "page": page,
                "snippet": snippet
            })
            citation_map[citation_key] = label
        else:
            label = citation_map[citation_key]

        paper_context_text += f"{label} {title} | Page {page}\n{doc.page_content}\n\n"

    system_prompt = f"""
    你是一位材料化學專家，擅長根據文獻摘要與研究目標，提出具有創新性與可行性的材料合成研究提案。
    如能根據文獻提出新的配體種類（如 pyridyl, biphenyl, sulfonate）或金屬節點（如 Zn, Mg, Zr），請具體列出並說明其結構優勢與反應性。

    請你根據下方文獻內容與研究目標，撰寫一份結構化提案，格式如下（請完整產出每一段）：

    ---
    Proposal: （請自動產生提案標題，濃縮研究目標與創新點）

    Need:
    - 簡述研究目標與目前材料在應用上的限制
    - 明確指出產業、世界、政府等待解決的痛點或技術瓶頸

    Solution:
    - 提出具體的材料設計與合成策略
    - 建議新的化學結構（如金屬、有機配體、功能官能基)，明確指出化學結構名稱(例如配體名稱)
    - 請說明新設計的化學邏輯（如配位環境、孔徑、官能基作用）

    Differentiation:
    - 列表比較與現有文獻材料的差異
    - 強調結構、條件或性能上的突破

    Benefit:
    - 預期改善的性能或應用面向
    - 列出量化的預估值（如提升 CO₂ 吸附量、穩定性、選擇性）

    Based Literature:
    - 使用段落標籤列出引用的依據，每段話都需要提供文獻段落編號，文獻段落編號為 [1] 到 [{len(chunks)}]（共 {len(chunks)} 個段落）
    - 請確保每個推論都有文獻對照依據或合理延伸理由

    Experimental overview:
    1. 使用的起始材料與反應條件（如溫度、時間）
    2. 合成使用儀器、設備描述並列表
    3. 合成步驟敘述（描述關鍵邏輯）



    最後，請在回答最末段，以 JSON 格式列出此提案所使用到的所有化學品（包含金屬鹽、有機配體、溶劑等）。以IUPAC Name回答，格式與範例如下：

    ```markdown

    ```json
    ["formic acid", "N,N-dimethylformamide", "copper;dinitrate;trihydrate"]
    ```
    ---

    請注意：
    - 結構建議要有邏輯依據，避免隨意編造不合理結構
    - 請保持科學性、可讀性，並避免空泛敘述
    - 引用標註請使用提供的文獻段落標籤 [1]、[2]，不要使用虛構來源

    --- 文獻段落 ---
    {paper_context_text}

    --- 研究目標 ---
    {question}

    """
    
    return system_prompt.strip(), citations

def build_detail_experimental_plan_prompt(chunks: List[Document], proposal_text: str) -> Tuple[str, List[Dict]]:
    context_text = ""
    citations = []
    citation_map = {}
    
    for i, doc in enumerate(chunks):
        # 檢查：doc 應有 metadata 屬性，且為 dict
        metadata = doc.metadata
        title = metadata.get("title", "Untitled")
        # 檢查：filename 來源於 "filename" 或 "source"，若都無則為 "Unknown"
        filename = metadata.get("filename") or metadata.get("source", "Unknown")
        # 檢查：page 來源於 "page_number" 或 "page"，若都無則為 "?"
        page = metadata.get("page_number") or metadata.get("page", "?")
        # 預覽片段，取前 80 字元，並將換行替換為空格
        snippet = doc.page_content[:80].replace("\n", " ")

        # 檢查：避免重複的 (filename, page) 組合
        citation_key = f"{filename}_p{page}"
        if citation_key not in citation_map:
            label = f"[{len(citations) + 1}]"
            citations.append({
                "label": label,
                "title": title,
                "source": filename,
                "page": page,
                "snippet": snippet
            })
            citation_map[citation_key] = label
        else:
            label = citation_map[citation_key]

        # context_text 累加每個 chunk 的內容，格式為 [n] title | Page n
        context_text += f"{label} {title} | Page {page}\n{doc.page_content}\n\n"

    system_prompt = f"""
    You are an experienced consultant in materials experiment design. Based on the following research proposal and related literature excerpts, please provide the researcher with a detailed set of recommended experimental procedures:

    Please include:

    Synthesis Process: A step-by-step description of each experimental operation, including sequence, logic, and purpose. 
    guidline for synthesis process:
    - Suggest a specific range of experimental conditions(temperature, time, pressure, etc.)
    - For each reaction conditons and steps that have been mentioned in the literature, make sure to cite ([1],[2], ...).
    - For suggested, not literature-based conditions, explain the your logic to convince the user.

    Materials and Conditions: The required raw materials for each step (including proportions), and the reaction conditions (temperature, time, containers).

    Analytical Methods: Suggested characterization tools (such as XRD, BET, TGA) and the purpose for each.

    Precautions: Key points or parameter limitations mentioned in the literature.

    Please clearly list the information in bullet points or paragraphs.
    Please use [1], [2], etc. to cite the literature sources in your response, 只能引用提供的文獻段落，當前提供的文獻段落編號為 [1] 到 [{len(chunks)}]（共 {len(chunks)} 個段落）

    --- literature chunks ---
    {context_text}

    --- User's Proposal ---
    {proposal_text}
    """
    return system_prompt.strip(), citations



def build_iterative_proposal_prompt(
    question: str,
    new_chunks: List[Document],
    old_chunks: List[Document],
    past_proposal: str
) -> Tuple[str, List[Dict]]:
    """
    建立新的研究提案 prompt，結合使用者的反饋、新檢索文獻、舊文獻與原始提案。
    同時回傳 citation list。
    """
    citations = []

    def format_chunks(chunks: List[Document], label_offset=0) -> Tuple[str, List[Dict]]:
        text = ""
        local_citations = []
        for i, doc in enumerate(chunks):
            meta = doc.metadata
            title = meta.get("title", "Untitled")
            filename = meta.get("filename") or meta.get("source", "Unknown")
            page = meta.get("page_number") or meta.get("page", "?")
            snippet = doc.page_content[:80].replace("\n", " ")
            label = f"[{label_offset + i + 1}]"

            local_citations.append({
                "label": label,
                "title": title,
                "source": filename,
                "page": page,
                "snippet": snippet
            })

            text += f"{label} {title} | Page {page}\n{doc.page_content}\n\n"

        return text, local_citations

    old_text, old_citations = format_chunks(old_chunks)
    new_text, new_citations = format_chunks(new_chunks, label_offset=len(old_citations))
    citations.extend(old_citations + new_citations)

    system_prompt = f"""
    你是一位熟練的材料實驗設計顧問，請根據使用者提供的反饋、原始提案、與文獻內容，協助修改部分的研究提案。

    請依循以下指引：
    1. 優先處理使用者提出欲修改之處，並從文獻中尋找可能的改進方向。
    2. 除了使用者提出之不滿意處進行修改外，其他部分(NSDB)請保持原提案內容，不須更動，直接輸出
    3. 保持提案格式與原始提案內容一致，並請於第一段簡要說明更改的方向，總共包含下列區塊：
    - revision explanation: 簡要說明本次提案與前次提案的差異
    - Need
    - Solution
    - Differentiation
    - Benefit
    - Based Literature
    - Experimental overview
    重要：只能引用提供的文獻段落，當前提供的文獻段落編號為 [1] 到 [{len(old_chunks) + len(new_chunks)}]（共 {len(old_chunks) + len(new_chunks)} 個段落）

    最後，請在回答最末段，以 JSON 格式列出此提案所使用到的所有化學品（包含金屬鹽、有機配體、溶劑等）。以 IUPAC Name 回答，回答格式與範例如下：

    ```json
    ["formic acid", "N,N-dimethylformamide", "copper;dinitrate;trihydrate"]
    --- 使用者的反饋 ---
    {question}

    --- 原始提案內容 ---
    {past_proposal}

    --- 原始提案所基於的文獻段落 ---
    {old_text}

    --- 根據反饋補充的新檢索段落 ---
    {new_text}
    """
    return system_prompt.strip(), citations

