
import os
import pandas as pd
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import OpenAIEmbeddings
from langchain.chat_models import ChatOpenAI
from config import OPENAI_API_KEY, VECTOR_INDEX_DIR, EXPERIMENT_CSV_DIR
from sentence_transformers import SentenceTransformer
from langchain.embeddings import HuggingFaceEmbeddings

def load_experiment_log():
    if not os.path.exists(EXPERIMENT_CSV_DIR):
        return pd.DataFrame()
    csv_files = [f for f in os.listdir(EXPERIMENT_CSV_DIR) if f.endswith(".csv")]
    dfs = []
    for file in csv_files:
        try:
            df = pd.read_csv(os.path.join(EXPERIMENT_CSV_DIR, file))
            dfs.append(df)
        except:
            continue
    if dfs:
        return pd.concat(dfs, ignore_index=True)
    return pd.DataFrame()

def agent_answer(question: str, df: pd.DataFrame):
    embedding_model = HuggingFaceEmbeddings(
    model_name="nomic-ai/nomic-embed-text-v1.5",
    model_kwargs={"trust_remote_code": True}
    )

    vectorstore = Chroma(
    persist_directory=VECTOR_INDEX_DIR,
    embedding_function=embedding_model,
    collection_name="default"
    )

    retriever = vectorstore.as_retriever(
        search_type="mmr",
        search_kwargs={
            "k": 10, #增加 context 覆蓋率
            "fetch_k": 30, #提高 MMR 的初選候補數量
            "score_threshold": 0.35  # 取決於你 embedding scale，可微調
        }
    )
    context_docs = retriever.get_relevant_documents(question)
    
    if not context_docs:
        print("⚠️ 沒有抓到任何段落，建議檢查 retriever 或嵌入格式")

    print("🔍 Retriever 抓到的段落：")
    for i, doc in enumerate(context_docs, 1):
        print(f"\n--- Chunk {i} ---")
        print(f"📄 {doc.metadata.get('title')} | Page {doc.metadata.get('page_number')}")
        print(doc.page_content[:500])  # 前 500 字預覽

    # 建立 citation map
    citations = []
    citation_map = {}
    for i, doc in enumerate(context_docs):
        label = f"[{i+1}]"
        snippet = " ".join(doc.page_content.strip().split()[:5]) + "..."
        citation = {
            "label": label,
            "title": doc.metadata.get("title", "未知"),
            "page": doc.metadata.get("page_number", "?"),
            "snippet": snippet
        }
        citations.append(citation)
        citation_map[id(doc)] = label

    # 插入追蹤資訊 + snippet
    context = "\n---\n".join(
        f"{citation_map[id(doc)]} [來源: {doc.metadata.get('title', '')} | 頁碼: {doc.metadata.get('page_number')} | 段落開頭: \"{' '.join(doc.page_content.strip().split()[:5])}...\"]\n{doc.page_content}"
        for doc in context_docs
    )

    past_exp = df.head(10).to_string(index=False) if not df.empty else "（無紀錄）"


    system_prompt = f"""
    You are a scientific research assistant. Answer rigorously and only based on the provided documents and experimental records.
    You must cite sources in your response using numbered references (e.g., [1], [2]). Do not list the sources again at the end.

    If available, include specific experimental conditions (e.g., temperature, time, concentration) in your answer to enhance credibility.
    請以專業助理的身份作答，僅根據下列文獻內容與紀錄回答。請在回答中使用 [1], [2] 編號標註出處，不要額外列出來源。
    如文中有提及，請務必加入具體實驗條件（例如：溫度、時間、濃度等）以提升答案可信度與完整性。

    --- 文獻摘要 ---
    {context}

    --- 實驗紀錄 ---
    {past_exp}

    --- 問題 ---
    {question}
        """


    #llm = ChatOpenAI(model="gpt-4")
    llm = ChatOpenAI(model_name="gpt-4-1106-preview", temperature=0)
    response = llm.predict(system_prompt)
    return {
        "answer": response,
        "citations": citations
    }
