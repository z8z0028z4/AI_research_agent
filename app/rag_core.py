from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_core.documents import Document
from langchain.chat_models import ChatOpenAI
from config import VECTOR_INDEX_DIR, EMBEDDING_MODEL_NAME, LLM_MODEL_NAME
import pandas as pd
from typing import List, Tuple, Dict
import os
from collections import defaultdict


def load_paper_vectorstore():
    embedding_model = HuggingFaceEmbeddings(
    model_name=EMBEDDING_MODEL_NAME,
    model_kwargs={"trust_remote_code": True}
    )
    paper_vector_dir = os.path.join(VECTOR_INDEX_DIR, "paper_vector")
    vectorstore = Chroma(
        persist_directory=paper_vector_dir,
        embedding_function=embedding_model, 
        collection_name="paper"
        )
    return vectorstore

def load_experiment_vectorstore():
    embedding_model = HuggingFaceEmbeddings(
    model_name=EMBEDDING_MODEL_NAME,
    model_kwargs={"trust_remote_code": True}
    )
    experiment_vector_dir = os.path.join(VECTOR_INDEX_DIR, "experiment_vector")
    vectorstore = Chroma(
        persist_directory=experiment_vector_dir, 
        embedding_function=embedding_model, 
        collection_name="experiment"
        )
    return vectorstore

def retrieve_chunks_multi_query(
    vectorstore, query_list: List[str], k: int = 10, fetch_k: int = 20, score_threshold: float = 0.35) -> List[Document]:
    retriever = vectorstore.as_retriever(
        search_type="mmr",
        search_kwargs={"k": k, "fetch_k": fetch_k, "score_threshold": score_threshold}
    )

    chunk_dict = defaultdict(float)
    print("query_list為: ", query_list)
    for q in query_list:
        docs = retriever.get_relevant_documents(q)
        for doc in docs:
            key = doc.metadata.get("exp_id") or doc.metadata.get("source") or doc.page_content[:30]
            chunk_dict[key] = doc  # 去重 by id or chunk
    result = list(chunk_dict.values())[:10]

    if not result:
        print("⚠️ 沒有抓到任何段落，建議檢查 retriever 或嵌入格式")
    print(f"🔍 Multi-query 抓到共 {len(result)} 段落：")
    print("🔍 Retriever 抓到的段落：")
    for i, doc in enumerate(result[:5], 1):
        meta = doc.metadata
        filename = meta.get("filename") or meta.get("source", "Unknown")
        page = meta.get("page_number") or meta.get("page", "?")
        preview = doc.page_content[:80].replace("\n", " ")
        print(f"--- Chunk {i} ---")
        print(f"📄 {filename} | Page {page}")
        print(preview)
        print()

    return result


def preview_chunks(chunks: list[Document], title: str, max_preview: int = 5):
    print(f"\n📦【{title}】共抓到 {len(chunks)} 段落")

    if not chunks:
        print("⚠️ 沒有任何段落可顯示。")
        return

    for i, doc in enumerate(chunks[:max_preview], 1):
        meta = doc.metadata
        filename = meta.get("filename") or meta.get("source", "Unknown")
        page = meta.get("page_number") or meta.get("page", "?")
        preview = doc.page_content[:100].replace("\n", " ")
        print(f"--- Chunk {i} ---")
        print(f"📄 {filename} | Page {page}")
        print(f"📚 內容：{preview}")

# def retrieve_chunks(vectorstore, query: str, k: int = 10, fetch_k: int = 30, score_threshold: float = 0.35) -> List[Document]:
#     retriever = vectorstore.as_retriever(
#         search_type="mmr",
#         search_kwargs={"k": k, "fetch_k": fetch_k, "score_threshold": score_threshold}
#     )
#     context_docs = retriever.get_relevant_documents(query)

#     if not context_docs:
#         print("⚠️ 沒有抓到任何段落，建議檢查 retriever 或嵌入格式")
#     else:
#         print("🔍 Retriever 抓到的段落：")
#         for i, doc in enumerate(context_docs, 1):
#             meta = doc.metadata
#             filename = meta.get("filename") or meta.get("source", "Unknown")
#             page = meta.get("page_number") or meta.get("page", "?")
#             preview = doc.page_content[:100].replace("\n", " ")
#             print(f"--- Chunk {i} ---")
#             print(f"📄 {filename} | Page {page}")
#             print(preview)
#             print()

#     return context_docs


def build_prompt(chunks: List[Document], question: str) -> Tuple[str, List[Dict]]:
    context_text = ""
    citations = []
    citation_map = {}
    
    for i, doc in enumerate(chunks):
        metadata = doc.metadata
        title = metadata.get("title", "Untitled")
        filename = metadata.get("filename") or metadata.get("source", "Unknown")
        page = metadata.get("page_number") or metadata.get("page", "?")
        snippet = doc.page_content[:80].replace("\n", " ")

        label = f"[{i+1}]"
 
        if label not in citation_map.values():
            citations.append({
                "label": label,
                "title": title,
                "source": filename,
                "page": page,
                "snippet": snippet
            })
        citation_map[f"{filename}_p{page}"] = label

        context_text += f"{label} {title} | Page {page}\n{doc.page_content}\n\n"

    system_prompt = f"""
你是一位研究文獻搜尋助理，僅根據提供的文獻段落來並回答問題。
請在回答中使用 [1], [2] 等標註段落出處，不要在結尾重複列出來源。
如段落中有提到具體的實驗條件（溫度、時間等），請務必包含在回答中。
--- 文獻摘要 ---
{context_text}


--- 問題 ---
{question}
"""
    return system_prompt.strip(), citations


def call_llm(prompt: str) -> str:
    llm = ChatOpenAI(model_name=LLM_MODEL_NAME, temperature=0)
    return llm.predict(prompt)

def build_inference_prompt(chunks: List[Document], question: str) -> Tuple[str, List[Dict]]:
    context_text = ""
    citations = []
    for i, doc in enumerate(chunks):
        meta = doc.metadata
        title = meta.get("title", "Untitled")
        filename = meta.get("filename") or meta.get("source", "Unknown")
        page = meta.get("page_number") or meta.get("page", "?")
        snippet = doc.page_content[:80].replace("\n", " ")
        label = f"[{i+1}]"

        citations.append({
            "label": label,
            "title": title,
            "source": filename,
            "page": page,
            "snippet": snippet
        })

        context_text += f"{label} {title} | Page {page}\n{doc.page_content}\n\n"

    system_prompt = f"""
你是一位材料合成顧問，你了解並善於比較材料間於化學、物理性質上的差異，能夠針對尚未有明確文獻的情境，根據已知之實驗條件推論出創新建議。

請根據以下文獻與實驗資料，進行延伸思考：
- 你可以提出新的組合、溫度、時間或路徑。
- 即使文獻中尚未記載的組合也可以建議，但要提出合理推論。
- 推論、延伸思考的同時，請儘可能提到「這樣的想法源於哪種文獻線索」來輔助解釋，請在回答中使用 [1], [2] 等標註段落出處，不要在結尾重複列出來源。


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
    llm = ChatOpenAI(model_name=LLM_MODEL_NAME, temperature=0.3)

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

    for i, doc in enumerate(chunks):
        
        meta = doc.metadata
        title = meta.get("title", "Untitled")
        filename = meta.get("filename") or meta.get("source", "Unknown")
        page = meta.get("page_number") or meta.get("page", "?")
        snippet = doc.page_content[:80].replace("\n", " ")
        label = f"[{i+1}]"

        citations.append({
            "label": label,
            "title": title,
            "source": filename,
            "page": page,
            "snippet": snippet
        })

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
- 建議新的化學結構（如金屬、有機配體、功能官能基)，明確指出建議的化學結構名稱(如配體名稱)
- 請說明新設計的化學邏輯（如配位環境、孔徑、官能基作用）

Differentiation:
- 與現有文獻材料的差異（可列表比較）
- 強調結構、條件或性能上的突破

Benefit:
- 預期改善的性能或應用面向
- 若能量化（如提升 CO₂ 吸附量、穩定性、選擇性）請盡量列出

Based Literature:
- 使用段落標籤列出引用的依據，例如：[1]、[2]...
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

def build_detail_experimental_plan_prompt(chunks: List[Document], proposal_text: str) -> str:
    paper_context_text = "\n\n".join(doc.page_content for doc in chunks)

    system_prompt = f"""
你是一位熟練的材料實驗設計顧問，請根據以下研究提案內容與相關文獻段落，為研究者提供一份詳細的建議實驗步驟：

請包含：
1. 合成流程：步驟-by-步驟說明每個實驗操作，含順序、邏輯與目的
2. 材料與條件：每步驟所需的原料（含比例）、反應條件（溫度、時間、容器）
3. 分析方法：建議使用哪些表徵工具（如 XRD, BET, TGA），以及目的為何
4. 注意事項：文獻中提醒的重點或參數限制

請以條列或分段方式清楚列出。

--- 文獻段落 ---
{paper_context_text}

--- 使用者的 Proposal ---
{proposal_text}
"""
    return system_prompt.strip()

def build_rejection_feedback_prompt(reason: str, old_proposal: str, goal: str) -> str:
    return f"""
使用者針對以下提案給出了批評與修改建議，請根據此理由重寫一份新的 proposal，格式與風格需保持一致，內容需貼近原始研究目標但具新意。

--- 研究目標 ---
{goal}

--- 不喜歡的原因 ---
{reason}

--- 原始 Proposal ---
{old_proposal}
"""