"""
簡化版 RAG 核心模組
================

基於模組化架構的 RAG 系統核心功能
使用新的核心模組和工具函數
"""

import time
import logging
from typing import List, Dict, Any, Optional, Tuple

from .core import (
    get_schema_by_type,
    load_paper_vectorstore,
    load_experiment_vectorstore,
    search_documents,
    preview_chunks,
    combine_search_results,
    get_default_llm_manager
)
from .utils import extract_text_snippet
from .utils.exceptions import LLMError, VectorStoreError

# 配置日誌
logger = logging.getLogger(__name__)

class RAGCore:
    """RAG 核心類別"""
    
    def __init__(self):
        """初始化 RAG 核心"""
        self.llm_manager = get_default_llm_manager()
        self.paper_vectorstore = None
        self.experiment_vectorstore = None
        self._initialize_vectorstores()
    
    def _initialize_vectorstores(self) -> None:
        """初始化向量數據庫"""
        try:
            self.paper_vectorstore = load_paper_vectorstore()
            self.experiment_vectorstore = load_experiment_vectorstore()
            logger.info("向量數據庫初始化成功")
        except Exception as e:
            logger.error(f"向量數據庫初始化失敗: {e}")
            raise VectorStoreError(f"初始化失敗: {e}")
    
    def search_papers(self, query: str, k: int = 5) -> List[Any]:
        """
        搜索論文文檔
        
        Args:
            query: 搜索查詢
            k: 返回結果數量
            
        Returns:
            List[Any]: 搜索結果
        """
        try:
            if not self.paper_vectorstore:
                raise VectorStoreError("論文向量數據庫未初始化")
            
            results = search_documents(self.paper_vectorstore, query, k=k)
            preview_chunks(results, "論文搜索結果")
            return results
            
        except Exception as e:
            logger.error(f"論文搜索失敗: {e}")
            return []
    
    def search_experiments(self, query: str, k: int = 5) -> List[Any]:
        """
        搜索實驗文檔
        
        Args:
            query: 搜索查詢
            k: 返回結果數量
            
        Returns:
            List[Any]: 搜索結果
        """
        try:
            if not self.experiment_vectorstore:
                raise VectorStoreError("實驗向量數據庫未初始化")
            
            results = search_documents(self.experiment_vectorstore, query, k=k)
            preview_chunks(results, "實驗搜索結果")
            return results
            
        except Exception as e:
            logger.error(f"實驗搜索失敗: {e}")
            return []
    
    def search_combined(self, query: str, k: int = 5) -> List[Any]:
        """
        組合搜索論文和實驗
        
        Args:
            query: 搜索查詢
            k: 返回結果數量
            
        Returns:
            List[Any]: 組合搜索結果
        """
        try:
            paper_results = self.search_papers(query, k=k//2)
            experiment_results = self.search_experiments(query, k=k//2)
            
            combined_results = combine_search_results(
                paper_results, 
                experiment_results, 
                max_total=k
            )
            
            return combined_results
            
        except Exception as e:
            logger.error(f"組合搜索失敗: {e}")
            return []
    
    def generate_proposal(self, query: str, include_experiments: bool = True) -> Dict[str, Any]:
        """
        生成研究提案
        
        Args:
            query: 研究主題
            include_experiments: 是否包含實驗數據
            
        Returns:
            Dict[str, Any]: 結構化研究提案
        """
        try:
            start_time = time.time()
            logger.info(f"開始生成研究提案: {query}")
            
            # 搜索相關文檔
            if include_experiments:
                chunks = self.search_combined(query, k=10)
            else:
                chunks = self.search_papers(query, k=10)
            
            if not chunks:
                raise ValueError("未找到相關文檔")
            
            # 構建上下文
            context = self._build_context(chunks)
            
            # 獲取 schema
            schema = get_schema_by_type("research_proposal")
            if not schema:
                raise ValueError("無法獲取研究提案 schema")
            
            # 構建提示
            prompt = self._build_proposal_prompt(query, context)
            
            # 生成結構化回應
            response = self.llm_manager.generate_structured_response(
                prompt=prompt,
                schema=schema,
                system_message="你是一個專業的研究提案生成助手，擅長基於文獻分析生成高質量的研究提案。"
            )
            
            # 驗證回應
            if not self.llm_manager.validate_response(response, schema):
                raise LLMError("生成的提案不符合 schema 要求")
            
            end_time = time.time()
            logger.info(f"研究提案生成完成，耗時: {end_time - start_time:.2f}秒")
            
            return response
            
        except Exception as e:
            logger.error(f"研究提案生成失敗: {e}")
            raise
    
    def generate_experimental_detail(self, query: str) -> Dict[str, Any]:
        """
        生成實驗詳情
        
        Args:
            query: 實驗主題
            
        Returns:
            Dict[str, Any]: 結構化實驗詳情
        """
        try:
            start_time = time.time()
            logger.info(f"開始生成實驗詳情: {query}")
            
            # 搜索相關文檔
            chunks = self.search_combined(query, k=8)
            
            if not chunks:
                raise ValueError("未找到相關文檔")
            
            # 構建上下文
            context = self._build_context(chunks)
            
            # 獲取 schema
            schema = get_schema_by_type("experimental_detail")
            if not schema:
                raise ValueError("無法獲取實驗詳情 schema")
            
            # 構建提示
            prompt = self._build_experimental_detail_prompt(query, context)
            
            # 生成結構化回應
            response = self.llm_manager.generate_structured_response(
                prompt=prompt,
                schema=schema,
                system_message="你是一個專業的實驗設計助手，擅長基於文獻分析生成詳細的實驗方案。"
            )
            
            # 驗證回應
            if not self.llm_manager.validate_response(response, schema):
                raise LLMError("生成的實驗詳情不符合 schema 要求")
            
            end_time = time.time()
            logger.info(f"實驗詳情生成完成，耗時: {end_time - start_time:.2f}秒")
            
            return response
            
        except Exception as e:
            logger.error(f"實驗詳情生成失敗: {e}")
            raise
    
    def _build_context(self, chunks: List[Any]) -> str:
        """
        構建上下文文本
        
        Args:
            chunks: 文檔塊列表
            
        Returns:
            str: 上下文文本
        """
        context_parts = []
        
        for i, chunk in enumerate(chunks, 1):
            try:
                metadata = chunk.metadata
                content = chunk.page_content
                
                # 提取文件名和頁碼
                filename = metadata.get("filename", "Unknown")
                page = metadata.get("page", "")
                
                # 清理和截斷內容
                clean_content = extract_text_snippet(content, max_length=300)
                
                context_part = f"文檔 {i}: {filename} (頁碼: {page})\n{clean_content}\n"
                context_parts.append(context_part)
                
            except Exception as e:
                logger.warning(f"處理文檔塊 {i} 失敗: {e}")
        
        return "\n".join(context_parts)
    
    def _build_proposal_prompt(self, query: str, context: str) -> str:
        """
        構建研究提案提示
        
        Args:
            query: 研究主題
            context: 上下文
            
        Returns:
            str: 提示文本
        """
        return f"""
基於以下研究主題和相關文獻，生成一個詳細的研究提案：

研究主題：{query}

相關文獻：
{context}

請生成一個包含以下要素的研究提案：
1. 研究背景和需求分析
2. 創新解決方案
3. 與現有研究的差異化
4. 預期效益
5. 實驗概述
6. 所需材料清單

請確保提案具有創新性、可行性和實用價值。
"""
    
    def _build_experimental_detail_prompt(self, query: str, context: str) -> str:
        """
        構建實驗詳情提示
        
        Args:
            query: 實驗主題
            context: 上下文
            
        Returns:
            str: 提示文本
        """
        return f"""
基於以下實驗主題和相關文獻，生成詳細的實驗方案：

實驗主題：{query}

相關文獻：
{context}

請生成一個包含以下要素的實驗方案：
1. 實驗目標
2. 實驗方法
3. 所需材料清單
4. 詳細實驗步驟
5. 預期結果

請確保實驗方案具有可操作性和可重複性。
"""

# 全局 RAG 實例
_rag_core_instance = None

def get_rag_core() -> RAGCore:
    """
    獲取 RAG 核心實例（單例模式）
    
    Returns:
        RAGCore: RAG 核心實例
    """
    global _rag_core_instance
    if _rag_core_instance is None:
        _rag_core_instance = RAGCore()
    return _rag_core_instance

def generate_research_proposal(query: str, include_experiments: bool = True) -> Dict[str, Any]:
    """
    生成研究提案（便捷函數）
    
    Args:
        query: 研究主題
        include_experiments: 是否包含實驗數據
        
    Returns:
        Dict[str, Any]: 結構化研究提案
    """
    rag_core = get_rag_core()
    return rag_core.generate_proposal(query, include_experiments)

def generate_experimental_detail(query: str) -> Dict[str, Any]:
    """
    生成實驗詳情（便捷函數）
    
    Args:
        query: 實驗主題
        
    Returns:
        Dict[str, Any]: 結構化實驗詳情
    """
    rag_core = get_rag_core()
    return rag_core.generate_experimental_detail(query)
