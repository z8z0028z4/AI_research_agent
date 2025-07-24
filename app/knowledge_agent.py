import pandas as pd
from rag_core import load_paper_vectorstore,build_proposal_prompt,build_detail_experimental_plan_prompt, load_experiment_vectorstore, preview_chunks, retrieve_chunks_multi_query, build_prompt, call_llm, build_inference_prompt, build_dual_inference_prompt, expand_query
from config import EXPERIMENT_DIR
import os


def agent_answer(question: str, mode:str ="defualt",  **kwargs):
    
    if mode == "納入實驗資料，進行推論與建議":
        print("🧪 啟用模式：納入實驗資料 + 推論")
        # 🧠 Dual retriever 啟用
        paper_vectorstore = load_paper_vectorstore()  # 文獻向量庫
        experiment_vectorstore = load_experiment_vectorstore()  # 實驗向量庫
        print("📦 Paper 向量庫：", paper_vectorstore._collection.count())
        print("📦 Experiment 向量庫：", experiment_vectorstore._collection.count())

        # 🔁 語意拓展
        query_list = expand_query(question) #給 chunks_paper的語意拓展用
        chunks_paper = retrieve_chunks_multi_query(paper_vectorstore, query_list, k=5)
        experiment_chunks = retrieve_chunks_multi_query(experiment_vectorstore, [question], k=5) #question 問，語意未拓展
        preview_chunks(chunks_paper, title="文獻向量庫")
        preview_chunks(experiment_chunks, title="實驗向量庫")
        prompt, citations = build_dual_inference_prompt(
            chunks_paper, question, experiment_chunks
        )
    elif mode == "make proposal":
        paper_vectorstore = load_paper_vectorstore()
        print("📦 Paper 向量庫：", paper_vectorstore._collection.count())
        chunks = retrieve_chunks_multi_query(paper_vectorstore, [question], k=10)
        prompt, citations = build_proposal_prompt(chunks, question)


    elif mode == "允許延伸與推論":
        # 一般模式使用單一 retriever
        paper_vectorstore = load_paper_vectorstore()
        chunks = retrieve_chunks_multi_query(paper_vectorstore, [question])
        print("📦 Paper 向量庫：", paper_vectorstore._collection.count())
        print("🧠 啟用模式：推論模式（不納入實驗資料）")
        prompt, citations = build_inference_prompt(chunks, [question])
    
    elif mode == "僅嚴謹文獻溯源":
        print("📚 啟用模式：嚴謹模式（僅文獻，無推論）")
        paper_vectorstore = load_paper_vectorstore()
        chunks = retrieve_chunks_multi_query(paper_vectorstore, [question])
        print("📦 Paper 向量庫：", paper_vectorstore._collection.count())
        prompt, citations = build_prompt(chunks, [question])

    elif mode == "expand to experiment detail":
    # 使用 proposal + paper_chunks 產出 detail
        chunks = kwargs.get("chunks", [])
        proposal = kwargs.get("proposal", "")
        prompt = build_detail_experimental_plan_prompt(chunks, proposal)
        response = call_llm(prompt)
        return {
            "answer": response,
            "citations": [],  # 你可以留空或保留 chunks 資訊
        }

    else:
        raise ValueError(f"未知的模式：{mode}")

    response = call_llm(prompt)

    return {
        "answer": response,
        "citations": citations,
        "chunks":chunks
    }

    
    


