import os
import pandas as pd
from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings
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
    embeddings = OpenAIEmbeddings()
    db = Chroma(persist_directory=VECTOR_INDEX_DIR, embedding_function=embeddings)
    retriever = db.as_retriever(search_kwargs={"k": 5})
    context_docs = retriever.get_relevant_documents(question)
    context = "\n---\n".join([doc.page_content for doc in context_docs])
    past_exp = experiment_df.head(10).to_string(index=False) if not experiment_df.empty else "（無紀錄）"
    system_prompt = (
        "你是一位研究助理，回答需嚴謹。若知識不足請說明，切勿捏造。\n\n"
        "根據以下資料回答問題：\n"
        "--- 文獻摘要 ---\n" + context + "\n\n"
        "--- 實驗紀錄 ---\n" + past_exp + "\n\n"
        "--- 問題 ---\n" + question
    )
    llm = ChatOpenAI(model="gpt-4")
    response = llm.predict(system_prompt)
    return response