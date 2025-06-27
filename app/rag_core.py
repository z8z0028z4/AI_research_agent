from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_core.documents import Document
from langchain.chat_models import ChatOpenAI
from config import VECTOR_INDEX_DIR, EMBEDDING_MODEL_NAME, LLM_MODEL_NAME
import pandas as pd
from typing import List, Tuple, Dict
import re


def load_vectorstore():
    embedding_model = HuggingFaceEmbeddings(
    model_name=EMBEDDING_MODEL_NAME,
    model_kwargs={"trust_remote_code": True}
    )
    vectorstore = Chroma(persist_directory=VECTOR_INDEX_DIR, embedding_function=embedding_model)
    return vectorstore


def retrieve_chunks(vectorstore, query: str, k: int = 10, fetch_k: int = 30, score_threshold: float = 0.35) -> List[Document]:
    retriever = vectorstore.as_retriever(
        search_type="mmr",
        search_kwargs={"k": k, "fetch_k": fetch_k, "score_threshold": score_threshold}
    )
    context_docs = retriever.get_relevant_documents(query)

    if not context_docs:
        print("⚠️ 沒有抓到任何段落，建議檢查 retriever 或嵌入格式")
    else:
        print("🔍 Retriever 抓到的段落：")
        for i, doc in enumerate(context_docs, 1):
            meta = doc.metadata
            filename = meta.get("filename") or meta.get("source", "Unknown")
            page = meta.get("page_number") or meta.get("page", "?")
            preview = doc.page_content[:100].replace("\n", " ")
            print(f"--- Chunk {i} ---")
            print(f"📄 {filename} | Page {page}")
            print(preview)
            print()

    return context_docs


def build_prompt(chunks: List[Document], df: pd.DataFrame, question: str) -> Tuple[str, List[Dict]]:
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

    past_exp = df.to_string(index=False) if not df.empty else "無紀錄"

    system_prompt = f"""
你是一位研究助理，僅根據下列文獻段落與實驗紀錄回答問題。
請在回答中使用 [1], [2] 等標註段落出處，不要在結尾重複列出來源。
如段落中有提到具體的實驗條件（溫度、時間等），請務必包含在回答中。
--- 文獻摘要 ---
{context_text}

--- 實驗紀錄 ---
{past_exp}

--- 問題 ---
{question}
"""
    return system_prompt.strip(), citations


def call_llm(prompt: str) -> str:
    llm = ChatOpenAI(model_name=LLM_MODEL_NAME, temperature=0)
    return llm.predict(prompt)

def build_inference_prompt(chunks: List[Document], df: pd.DataFrame, question: str) -> Tuple[str, List[Dict]]:
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

    past_exp = df.to_string(index=False) if not df.empty else "無紀錄"

    system_prompt = f"""
你是一位材料合成顧問，善於針對尚未有明確文獻的情境，根據相似條件推論出創新建議。

請根據以下文獻與實驗資料，進行延伸思考：
- 你可以提出新的組合、溫度、時間或路徑。
- 即使沒有直接證據，只要推理合理也可以建議。
- 只要合理，允許提出創新構想，即使文獻中尚未記載
- 推論、延伸思考的同時，請儘可能提到「這樣的想法源於哪種文獻線索」來輔助解釋，請在回答中使用 [1], [2] 等標註段落出處，不要在結尾重複列出來源。


--- 文獻摘要 ---
{context_text}

--- 實驗紀錄 ---
{past_exp}

--- 問題 ---
{question}
"""
    return system_prompt.strip(), citations