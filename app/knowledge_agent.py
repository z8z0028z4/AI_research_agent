
import os
import pandas as pd
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import OpenAIEmbeddings
from langchain.chat_models import ChatOpenAI
from config import OPENAI_API_KEY, VECTOR_INDEX_DIR, EXPERIMENT_CSV_DIR

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

def agent_answer(question, experiment_df):
    embeddings = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)
    db = Chroma(persist_directory=VECTOR_INDEX_DIR, embedding_function=embeddings)
    retriever = db.as_retriever(search_kwargs={"k": 5})
    context_docs = retriever.get_relevant_documents(question)

    # 建立 citation map
    citations = []
    citation_map = {}
    for i, doc in enumerate(context_docs):
        label = f"[{i+1}]"
        snippet = " ".join(doc.page_content.strip().split()[:5]) + "..."
        citation = {
            "label": label,
            "filename": doc.metadata.get("filename", "未知"),
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

    past_exp = experiment_df.head(10).to_string(index=False) if not experiment_df.empty else "（無紀錄）"

    system_prompt = f"""
        You are a scientific research assistant. Answer rigorously based on the given documents.
        Please cite sources in your response using numbered references (e.g., [1], [2]).
        At the end of your answer, list all cited sources in the format:
        [1] Filename | Page number | Beginning of paragraph: "..."\n
        你是一位研究助理，回答需嚴謹。請根據下列文獻與資料內容作答，並在回答中標註來源編號（例如 [1], [2]）。
        回答末尾請列出所有引用的來源對應標記與說明：
        [1] 檔名 | 頁碼 | 段落開頭: "..."
        --- 文獻摘要 ---
        {context}

        --- 實驗紀錄 ---
        {past_exp}

        --- 問題 ---
        {question}
        """
        # "--- 文獻摘要 ---\n" + context + "\n\n"
        # "--- 實驗紀錄 ---\n" + past_exp + "\n\n"
        # "--- 問題 ---\n" + question

    llm = ChatOpenAI(model="gpt-4")
    response = llm.predict(system_prompt)
    return response
