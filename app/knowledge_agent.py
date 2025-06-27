import pandas as pd
from rag_core import load_vectorstore, retrieve_chunks, build_prompt, call_llm
from config import EXPERIMENT_CSV_DIR
import os

def agent_answer(question: str, df: pd.DataFrame):
    vectorstore = load_vectorstore()
    chunks = retrieve_chunks(vectorstore, question)
    prompt, citations = build_prompt(chunks, df, question)
    response = call_llm(prompt)

    return {
        "answer": response,
        "citations": citations
    }

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
        df_all = pd.concat(dfs, ignore_index=True)
        print(f"[DEBUG] 實驗資料總列數：{df_all.shape[0]}, 欄位數：{df_all.shape[1]}")
        print(f"[DEBUG] 將輸入 prompt 的 dataframe 預覽：\n{df_all.head(5)}")
        return df_all

    return pd.DataFrame()
