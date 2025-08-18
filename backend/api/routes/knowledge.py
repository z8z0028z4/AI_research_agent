"""
知識庫查詢API路由
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import sys
import os

# 添加app目錄到路徑
app_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "app")
if app_path not in sys.path:
    sys.path.insert(0, app_path)

# 移除直接導入，使用延遲導入

router = APIRouter(prefix="/knowledge", tags=["knowledge"])

class KnowledgeQueryRequest(BaseModel):
    question: str
    retrieval_count: int = 10
    answer_mode: str = "rigorous"  # "rigorous" 或 "inference"

class KnowledgeQueryResponse(BaseModel):
    answer: str
    citations: List[Dict[str, Any]]
    chunks: List[Dict[str, Any]]

@router.post("/query", response_model=KnowledgeQueryResponse)
async def query_knowledge(request: KnowledgeQueryRequest):
    """
    知識庫查詢接口
    
    支持兩種回答模式：
    - rigorous: 嚴謹引用模式，基於文獻進行準確引用
    - inference: 推論模式，允許基於文獻進行推論和創新建議
    """
    try:
        print(f"🔍 知識庫查詢請求：{request.question}")
        print(f"🔍 檢索數量：{request.retrieval_count}")
        print(f"🔍 回答模式：{request.answer_mode}")
        
        # 延遲導入rag_core模組
        from rag_core import (
            load_paper_vectorstore,
            retrieve_chunks_multi_query,
            build_prompt,
            build_inference_prompt,
            call_llm
        )
        
        # 載入文獻向量數據庫
        vectorstore = load_paper_vectorstore()
        
        # 檢索文檔片段（直接使用用戶問題，不進行查詢擴展）
        chunks = retrieve_chunks_multi_query(
            vectorstore=vectorstore,
            query_list=[request.question],  # 直接使用用戶問題
            k=request.retrieval_count,
            fetch_k=request.retrieval_count * 2,
            score_threshold=0.35
        )
        
        if not chunks:
            raise HTTPException(status_code=404, detail="未找到相關文獻")
        
        print(f"🔍 檢索到 {len(chunks)} 個文檔片段")
        
        # 根據回答模式選擇不同的prompt構建函數
        if request.answer_mode == "rigorous":
            # 嚴謹引用模式
            system_prompt, citations = build_prompt(chunks, request.question)
        elif request.answer_mode == "inference":
            # 推論模式
            system_prompt, citations = build_inference_prompt(chunks, request.question)
        else:
            raise HTTPException(status_code=400, detail="無效的回答模式")
        
        # 調用LLM生成回答
        answer = call_llm(system_prompt)
        
        if not answer:
            raise HTTPException(status_code=500, detail="生成回答失敗")
        
        # 轉換chunks為可序列化的格式
        serializable_chunks = []
        for chunk in chunks:
            serializable_chunk = {
                "page_content": chunk.page_content,
                "metadata": chunk.metadata
            }
            serializable_chunks.append(serializable_chunk)
        
        return KnowledgeQueryResponse(
            answer=answer,
            citations=citations,
            chunks=serializable_chunks
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ 知識庫查詢失敗：{e}")
        raise HTTPException(status_code=500, detail=f"查詢失敗：{str(e)}") 