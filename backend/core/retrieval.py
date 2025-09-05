"""
檢索模組
========

負責文檔檢索和向量數據庫管理
"""

from typing import List, Dict, Any, Optional
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter

from backend.utils.logger import get_logger
from backend.utils.exceptions import VectorStoreError

logger = get_logger(__name__)


def load_paper_vectorstore():
    """
    載入文獻向量數據庫
    
    功能：
    1. 獲取或創建文獻向量數據庫實例
    2. 使用緩存避免重複創建
    
    返回：
        Chroma: 文獻向量數據庫對象
    
    技術細節：
    - 使用緩存的 Chroma 實例
    - 持久化存儲在paper_vector目錄
    - 集合名稱為"paper"
    """
    try:
        # 延遲導入避免循環依賴
        from backend.services.embedding_service import get_chroma_instance
        return get_chroma_instance("paper")
    except Exception as e:
        logger.error(f"載入文獻向量數據庫失敗: {e}")
        raise VectorStoreError(f"載入文獻向量數據庫失敗: {str(e)}")


def load_experiment_vectorstore():
    """
    載入實驗數據向量數據庫
    
    功能：
    1. 獲取或創建實驗數據向量數據庫實例
    2. 使用緩存避免重複創建
    
    返回：
        Chroma: 實驗數據向量數據庫對象
    
    技術細節：
    - 使用緩存的 Chroma 實例
    - 持久化存儲在experiment_vector目錄
    - 集合名稱為"experiment"
    """
    try:
        # 延遲導入避免循環依賴
        from backend.services.embedding_service import get_chroma_instance
        return get_chroma_instance("experiment")
    except Exception as e:
        logger.error(f"載入實驗向量數據庫失敗: {e}")
        raise VectorStoreError(f"載入實驗向量數據庫失敗: {str(e)}")


def retrieve_chunks_multi_query(
    vectorstore, 
    query_list: List[str], 
    k: int = 10, 
    fetch_k: int = 20, 
    score_threshold: float = 0.35
) -> List[Document]:
    """
    多查詢文檔檢索功能
    
    功能：
    1. 對多個查詢進行並行檢索
    2. 去重和排序檢索結果
    3. 提供詳細的檢索統計信息
    
    參數：
        vectorstore: 向量數據庫對象
        query_list (List[str]): 查詢列表
        k (int): 返回的文檔數量
        fetch_k (int): 初始檢索的文檔數量
        score_threshold (float): 相似度閾值
    
    返回：
        List[Document]: 檢索到的文檔列表
    
    技術細節：
    - 使用MMR（最大邊際相關性）搜索
    - 自動去重避免重複內容
    - 提供詳細的檢索日誌
    """
    try:
        retriever = vectorstore.as_retriever(
            search_type="mmr",
            search_kwargs={"k": k, "fetch_k": fetch_k, "score_threshold": score_threshold}
        )

        # 使用字典進行去重
        chunk_dict = {}
        logger.info(f"開始多查詢檢索，查詢列表：{query_list}")
        
        # 對每個查詢進行檢索
        for q in query_list:
            docs = retriever.get_relevant_documents(q)
            for doc in docs:
                # 使用唯一標識符進行去重
                key = doc.metadata.get("exp_id") or doc.metadata.get("source") or doc.page_content[:30]
                chunk_dict[key] = doc
        
        # 限制返回結果數量，使用傳入的 k 參數
        result = list(chunk_dict.values())[:k]

        # 檢索結果驗證
        if not result:
            logger.warning("沒有檢索到任何文檔，建議檢查檢索器或嵌入格式")
        else:
            logger.info(f"多查詢檢索完成，共找到 {len(result)} 個文檔")
            # 記錄檢索到的文檔預覽
            for i, doc in enumerate(result[:5], 1):
                meta = doc.metadata
                filename = meta.get("filename") or meta.get("source", "Unknown")
                page = meta.get("page_number") or meta.get("page", "?")
                preview = doc.page_content[:80].replace("\n", " ")
                logger.debug(f"文檔 {i}: {filename} (頁碼：{page}) - {preview}")

        return result
        
    except Exception as e:
        logger.error(f"多查詢檢索失敗: {e}")
        raise VectorStoreError(f"多查詢檢索失敗: {str(e)}")


def retrieve_chunks_single_query(
    vectorstore, 
    query: str, 
    k: int = 10, 
    score_threshold: float = 0.35
) -> List[Document]:
    """
    單查詢文檔檢索功能
    
    參數：
        vectorstore: 向量數據庫對象
        query (str): 查詢字符串
        k (int): 返回的文檔數量
        score_threshold (float): 相似度閾值
    
    返回：
        List[Document]: 檢索到的文檔列表
    """
    try:
        retriever = vectorstore.as_retriever(
            search_type="mmr",
            search_kwargs={"k": k, "score_threshold": score_threshold}
        )
        
        result = retriever.get_relevant_documents(query)
        logger.info(f"單查詢檢索完成，查詢：{query}，找到 {len(result)} 個文檔")
        
        return result
        
    except Exception as e:
        logger.error(f"單查詢檢索失敗: {e}")
        raise VectorStoreError(f"單查詢檢索失敗: {str(e)}")


def preview_chunks(chunks: List[Document], title: str, max_preview: int = 5):
    """
    預覽文檔塊內容
    
    參數：
        chunks: 文檔塊列表
        title: 預覽標題
        max_preview: 最大預覽數量
    """
    if not chunks:
        logger.warning(f"【{title}】沒有任何段落可顯示。")
        return
    
    logger.info(f"\n📦【{title}】共找到 {len(chunks)} 個文檔塊")
    
    for i, chunk in enumerate(chunks[:max_preview], 1):
        metadata = chunk.metadata
        filename = metadata.get("filename") or metadata.get("source", "Unknown")
        page = metadata.get("page_number") or metadata.get("page", "?")
        preview = chunk.page_content[:100].replace("\n", " ")
        
        logger.info(f"--- Chunk {i} ---")
        logger.info(f"📄 Filename: {filename} | Page: {page}")
        logger.info(f"📚 Preview: {preview}")


def expand_query_with_llm_client(original_query: str, llm_client) -> List[str]:
    """
    使用 LLM 客戶端擴展查詢詞
    
    參數：
        original_query: 原始查詢
        llm_client: LLM客戶端
        
    返回：
        List[str]: 擴展後的查詢詞列表
    """
    try:
        from .prompt_builder import build_expand_query_prompt
        
        prompt = build_expand_query_prompt(original_query)
        response = llm_client.invoke(prompt)
        
        # 解析擴展的查詢詞
        expanded_queries = [original_query]  # 包含原始查詢
        
        if response and hasattr(response, 'content'):
            content = response.content
            # 按行分割並清理
            lines = [line.strip() for line in content.split('\n') if line.strip()]
            expanded_queries.extend(lines)
        
        logger.info(f"查詢擴展完成，原始查詢：{original_query}，擴展為 {len(expanded_queries)} 個查詢")
        return expanded_queries
        
    except Exception as e:
        logger.error(f"查詢擴展失敗: {e}")
        # 如果擴展失敗，返回原始查詢
        return [original_query]


def get_vectorstore_stats(vectorstore_type: str = "paper") -> Dict[str, Any]:
    """
    獲取向量數據庫統計信息
    
    參數：
        vectorstore_type: 向量數據庫類型 ("paper" 或 "experiment")
        
    返回：
        Dict[str, Any]: 統計信息
    """
    try:
        # 延遲導入避免循環依賴
        from backend.services.embedding_service import get_chroma_instance
        vectorstore = get_chroma_instance(vectorstore_type)
        collection = vectorstore._collection
        
        stats = {
            "total_documents": collection.count(),
            "vectorstore_type": vectorstore_type
        }
        
        logger.info(f"向量數據庫統計 - {vectorstore_type}: {stats['total_documents']} 個文檔")
        return stats
        
    except Exception as e:
        logger.error(f"獲取向量數據庫統計失敗: {e}")
        return {
            "total_documents": 0,
            "vectorstore_type": vectorstore_type,
            "error": str(e)
        }
