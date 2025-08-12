"""
AI 研究助理 - 知識代理模塊
========================

這個模塊是整個AI研究助理系統的核心，負責整合多源信息並生成智能回答。
主要功能包括：
1. 多模式知識處理
2. 文獻和實驗數據整合
3. 智能推論和建議生成
4. 實驗方案設計

架構說明：
- 作為知識處理層的核心協調器
- 整合RAG核心功能
- 支持多種處理模式
- 提供統一的知識處理接口
"""

import pandas as pd
from rag_core import (
    load_paper_vectorstore, build_proposal_prompt, build_detail_experimental_plan_prompt, 
    build_iterative_proposal_prompt, load_experiment_vectorstore, preview_chunks, 
    retrieve_chunks_multi_query, build_prompt, call_llm, build_inference_prompt, 
    build_dual_inference_prompt, expand_query
)
from config import EXPERIMENT_DIR
import os

def agent_answer(question: str, mode: str = "make proposal", **kwargs):
    """
    知識代理的主要回答函數
    
    功能：
    1. 根據不同模式處理用戶查詢
    2. 整合文獻和實驗數據
    3. 生成智能回答和建議
    4. 提供相關引用信息
    
    參數：
        question (str): 用戶問題
        mode (str): 處理模式，支持多種模式
        **kwargs: 額外參數，如chunks、proposal、k等
    
    返回：
        dict: 包含回答、引用和相關文檔塊的字典
    
    支持的模式：
    - "納入實驗資料，進行推論與建議": 整合實驗數據進行推論
    - "make proposal": 生成研究提案
    - "允許延伸與推論": 基於文獻進行推論
    - "僅嚴謹文獻溯源": 嚴格基於文獻回答
    - "expand to experiment detail": 擴展實驗細節
    - "generate new idea": 生成新想法
    """
    
    # 獲取檢索參數
    k = kwargs.get("k", 10)  # 預設檢索 10 個文檔
    fetch_k = k * 2  # fetch_k 自動設為 k 的 2 倍
    
    # ==================== DEBUG 日誌 ====================
    print(f"🔍 DEBUG: agent_answer 被調用")
    print(f"🔍 DEBUG: question = '{question}'")
    print(f"🔍 DEBUG: mode = '{mode}'")
    print(f"🔍 DEBUG: k = {k}, fetch_k = {fetch_k}")
    print(f"🔍 DEBUG: kwargs = {kwargs}")
    print(f"🔍 DEBUG: mode type = {type(mode)}")
    print(f"🔍 DEBUG: mode == 'make proposal' = {mode == 'make proposal'}")
    print(f"🔍 DEBUG: mode == 'default' = {mode == 'default'}")
    
    # ==================== 模式1：納入實驗資料，進行推論與建議 ====================
    if mode == "納入實驗資料，進行推論與建議":
        """
        高級模式：整合文獻和實驗數據進行綜合推論
        
        特點：
        - 使用雙重檢索器（文獻 + 實驗數據）
        - 語義查詢擴展
        - 綜合推論和建議
        """
        print("🧪 啟用模式：納入實驗資料 + 推論")
        
        # 載入雙重向量庫
        paper_vectorstore = load_paper_vectorstore()  # 文獻向量庫
        experiment_vectorstore = load_experiment_vectorstore()  # 實驗向量庫
        print("📦 Paper 向量庫：", paper_vectorstore._collection.count())
        print("📦 Experiment 向量庫：", experiment_vectorstore._collection.count())

        # 語義查詢擴展和檢索
        query_list = expand_query(question)  # 為文獻檢索進行語義擴展
        chunks_paper = retrieve_chunks_multi_query(paper_vectorstore, query_list, k=5)
        experiment_chunks = retrieve_chunks_multi_query(experiment_vectorstore, [question], k=5)  # 實驗數據檢索
        
        # 預覽檢索結果
        preview_chunks(chunks_paper, title="文獻向量庫")
        preview_chunks(experiment_chunks, title="實驗向量庫")
        
        # 構建雙重推論提示詞
        prompt, citations = build_dual_inference_prompt(
            chunks_paper, question, experiment_chunks
        )
    
    # ==================== 模式2：生成研究提案 ====================
    elif mode == "make proposal":
        """
        研究提案生成模式
        
        特點：
        - 基於文獻生成研究提案
        - 使用較多的檢索結果（k=10）
        - 專注於提案結構化生成
        """
        print("📝 啟用模式：make proposal")
        paper_vectorstore = load_paper_vectorstore()
        print("📦 Paper 向量庫：", paper_vectorstore._collection.count())
        chunks = retrieve_chunks_multi_query(paper_vectorstore, [question], k=k, fetch_k=fetch_k)
        prompt, citations = build_proposal_prompt(chunks, question)

    # ==================== 模式3：允許延伸與推論 ====================
    elif mode == "允許延伸與推論":
        """
        推論模式：基於文獻進行智能推論
        
        特點：
        - 僅使用文獻數據
        - 允許AI進行推論和延伸
        - 不納入實驗數據
        """
        # 使用單一檢索器（僅文獻）
        paper_vectorstore = load_paper_vectorstore()
        chunks = retrieve_chunks_multi_query(paper_vectorstore, [question], k = 30, fetch_k = 50)
        print("📦 Paper 向量庫：", paper_vectorstore._collection.count())
        print("🧠 啟用模式：推論模式（不納入實驗資料）")
        prompt, citations = build_inference_prompt(chunks, [question])
    
    # ==================== 模式4：僅嚴謹文獻溯源 ====================
    elif mode == "僅嚴謹文獻溯源":
        """
        嚴謹模式：嚴格基於文獻回答
        
        特點：
        - 僅基於檢索到的文獻片段回答
        - 不進行推論和延伸
        - 確保回答的可追溯性
        """
        print("📚 啟用模式：嚴謹模式（僅文獻，無推論）")
        paper_vectorstore = load_paper_vectorstore()
        chunks = retrieve_chunks_multi_query(paper_vectorstore, [question], k = 20, fetch_k = 30)
        print("📦 Paper 向量庫：", paper_vectorstore._collection.count())
        prompt, citations = build_prompt(chunks, [question])

    # ==================== 模式5：擴展實驗細節 ====================
    elif mode == "expand to experiment detail":
        """
        實驗細節擴展模式
        
        特點：
        - 基於提案和文獻塊生成詳細實驗計劃
        - 需要外部提供chunks和proposal
        - 專注於實驗設計細節
        """
        print("🔬 啟用模式：expand to experiment detail")
        chunks = kwargs.get("chunks", [])
        proposal = kwargs.get("proposal", "")
        prompt, citations = build_detail_experimental_plan_prompt(chunks, proposal)

    # ==================== 模式6：生成新想法 ====================
    elif mode == "generate new idea":
        """
        新想法生成模式
        
        特點：
        - 基於現有提案生成新的研究想法
        - 使用迭代式提案生成
        - 需要外部提供old_chunks和proposal
        """
        print("💡 啟用模式：generate new idea")
        paper_vectorstore = load_paper_vectorstore()
        print("📦 Paper 向量庫：", paper_vectorstore._collection.count())
        query_list = expand_query(question)  # 語義擴展
        chunks = retrieve_chunks_multi_query(paper_vectorstore, query_list, k=5)
        old_chunks = kwargs.get("old_chunks", [])
        proposal = kwargs.get("proposal", "")
        prompt, citations = build_iterative_proposal_prompt(question, chunks, old_chunks, proposal)

    # ==================== 錯誤處理 ====================
    else:
        print(f"❌ DEBUG: 未知的模式：'{mode}'")
        print(f"❌ DEBUG: 可用的模式：{get_available_modes()}")
        raise ValueError(f"❌ 未知的模式：{mode}")

    # ==================== 調用LLM生成回答 ====================
    print(f"🔍 DEBUG: 準備調用 call_llm")
    print(f"🔍 DEBUG: prompt 長度: {len(prompt)}")
    print(f"🔍 DEBUG: prompt 前200字符: {prompt[:200]}...")
    
    response = call_llm(prompt)
    
    print(f"🔍 DEBUG: call_llm 返回結果")
    print(f"🔍 DEBUG: response 類型: {type(response)}")
    print(f"🔍 DEBUG: response 長度: {len(response) if response else 0}")
    print(f"🔍 DEBUG: response 內容: {response[:500] if response else 'None'}...")
    
    # ==================== 獲取使用的模型信息 ====================
    try:
        from model_config_bridge import get_current_model
        used_model = get_current_model()
        print(f"🔍 DEBUG: 使用的模型: {used_model}")
    except Exception as e:
        print(f"❌ DEBUG: 獲取模型信息失敗: {e}")
        used_model = "unknown"

    # ==================== 返回結果 ====================
    result = {
        "answer": response,      # AI生成的回答
        "citations": citations,  # 相關引用信息
        "chunks": chunks,       # 檢索到的相關文檔塊
        "used_model": used_model  # 使用的模型信息
    }
    
    print(f"🔍 DEBUG: 返回結果")
    print(f"🔍 DEBUG: answer 長度: {len(result['answer'])}")
    print(f"🔍 DEBUG: citations 數量: {len(result['citations'])}")
    print(f"🔍 DEBUG: chunks 數量: {len(result['chunks'])}")
    
    return result


# ==================== 輔助函數 ====================
def get_available_modes():
    """
    獲取所有可用的處理模式
    
    返回：
        List[str]: 可用模式列表
    """
    return [
        "納入實驗資料，進行推論與建議",
        "make proposal",
        "允許延伸與推論",
        "僅嚴謹文獻溯源",
        "expand to experiment detail",
        "generate new idea"
    ]


def validate_mode(mode: str) -> bool:
    """
    驗證模式是否有效
    
    參數：
        mode (str): 要驗證的模式
    
    返回：
        bool: 模式是否有效
    """
    available_modes = get_available_modes()
    return mode in available_modes


def get_mode_description(mode: str) -> str:
    """
    獲取模式的詳細描述
    
    參數：
        mode (str): 模式名稱
    
    返回：
        str: 模式描述
    """
    descriptions = {
        "納入實驗資料，進行推論與建議": "整合文獻和實驗數據進行綜合推論",
        "make proposal": "生成研究提案",
        "允許延伸與推論": "基於文獻進行智能推論",
        "僅嚴謹文獻溯源": "嚴格基於文獻回答，無推論",
        "expand to experiment detail": "擴展實驗細節設計",
        "generate new idea": "生成新的研究想法"
    }
    return descriptions.get(mode, "未知模式")

    
    


