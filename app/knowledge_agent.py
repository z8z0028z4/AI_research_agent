import pandas as pd
from rag_core import load_paper_vectorstore, load_experiment_vectorstore, preview_chunks, retrieve_chunks_multi_query, build_prompt, call_llm, build_inference_prompt, build_dual_inference_prompt, expand_query
from config import EXPERIMENT_DIR
import os


def agent_answer(question: str, df: pd.DataFrame, inference=False, use_experiment=False):
    
    if use_experiment:
        print("🧪 啟用模式：納入實驗資料 + 推論")
        # 🧠 Dual retriever 啟用
        paper_vectorstore = load_paper_vectorstore()  # 文獻向量庫
        experiment_vectorstore = load_experiment_vectorstore()  # 實驗向量庫
        print("📦 Paper 向量庫：", paper_vectorstore._collection.count())
        print("📦 Experiment 向量庫：", experiment_vectorstore._collection.count())

        # 🔁 語意拓展
        query_list = expand_query(question) #給 chunks_paper的語意拓展用
        #給 chunks_experiment的語意拓展用

        # 分別召回
        chunks_paper = retrieve_chunks_multi_query(paper_vectorstore, query_list, k=5)
        chunks_experiment = retrieve_chunks_multi_query(experiment_vectorstore, [question], k=5) #question 問，語意未拓展
        preview_chunks(chunks_paper, title="文獻向量庫")
        preview_chunks(chunks_experiment, title="實驗向量庫")

        # 🧠 合併餵入 dual prompt injection
        prompt, citations = build_dual_inference_prompt(
            chunks_paper, df, question, experiment_chunks=chunks_experiment
        )

    else:
        # 一般模式使用單一 retriever
        paper_vectorstore = load_paper_vectorstore()
        chunks = retrieve_chunks_multi_query(paper_vectorstore, [question])
        print("📦 Paper 向量庫：", paper_vectorstore._collection.count())

        if inference:
            
            print("🧠 啟用模式：推論模式（不納入實驗資料）")
            prompt, citations = build_inference_prompt(chunks, df, [question])
        else:
            print("📚 啟用模式：嚴謹模式（僅文獻，無推論）")
            prompt, citations = build_prompt(chunks, df, [question])

    response = call_llm(prompt)

    return {
        "answer": response,
        "citations": citations
    }
    
    
    
    
    vectorstore = load_paper_vectorstore()
    if use_experiment:
        # ✅ 啟用語意拓展做 multi-query search
        query_list = expand_query(question)
        chunks = retrieve_chunks(vectorstore, query_list)
    else:
        # ✅ 一般嚴謹 / 推論模式，直接查原始 question
        chunks = retrieve_chunks(vectorstore, question)

    # 根據模式切換不同 prompt injection
    if inference and use_experiment:
        queries = expand_query(question)
        chunks = retrieve_chunks(vectorstore, queries)
        prompt, citations = build_dual_inference_prompt(chunks, df, question)  # 納入實驗資料模式
    elif inference:
        prompt, citations = build_inference_prompt(chunks, df, question) #推論模式
    else:
        prompt, citations = build_prompt(chunks, df, question) #嚴謹模式

    response = call_llm(prompt)

    return {
        "answer": response,
        "citations": citations
    }


def load_experiment_log(): ##########################################
    if not os.path.exists(EXPERIMENT_DIR):
        return pd.DataFrame()
    csv_files = [f for f in os.listdir(EXPERIMENT_DIR) if f.endswith(".csv")]
    dfs = []
    for file in csv_files:
        try:
            df = pd.read_csv(os.path.join(EXPERIMENT_DIR, file))
            dfs.append(df)
        except:
            continue
    if dfs:
        df_all = pd.concat(dfs, ignore_index=True)
        print(f"[DEBUG] 實驗資料總列數：{df_all.shape[0]}, 欄位數：{df_all.shape[1]}")
        print(f"[DEBUG] 將輸入 prompt 的 dataframe 預覽：\n{df_all.head(5)}")
        return df_all

    return pd.DataFrame()