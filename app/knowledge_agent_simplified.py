"""
簡化版知識代理模組
================

基於模組化架構的知識代理系統，整合多源信息並生成智能回答。
使用新的處理器架構，提供更清晰的代碼結構和更好的可維護性。
"""

import time
import uuid
import logging
from typing import Dict, List, Any, Optional

from .core.mode_manager import validate_mode, get_mode_description, get_available_modes
from .core.processors import get_processor
from .utils.exceptions import AIResearchAgentError, ValidationError

# 配置日誌
logger = logging.getLogger(__name__)


class KnowledgeAgent:
    """知識代理主類"""
    
    def __init__(self):
        """初始化知識代理"""
        self.request_counter = 0
    
    def answer(
        self, 
        question: str, 
        mode: str = "make proposal", 
        **kwargs
    ) -> Dict[str, Any]:
        """
        知識代理的主要回答函數
        
        Args:
            question: 用戶問題
            mode: 處理模式
            **kwargs: 額外參數
            
        Returns:
            Dict[str, Any]: 包含回答、引用和相關文檔塊的字典
            
        Raises:
            ValidationError: 模式驗證失敗
            AIResearchAgentError: 處理過程中發生錯誤
        """
        # 生成請求ID
        request_id = self._generate_request_id()
        start_time = time.time()
        
        # 記錄請求信息
        self._log_request_info(request_id, question, mode, kwargs)
        
        try:
            # 驗證模式
            if not validate_mode(mode):
                available_modes = get_available_modes()
                raise ValidationError(
                    f"未知的模式：{mode}",
                    field_name="mode",
                    details={"available_modes": available_modes}
                )
            
            # 獲取對應的處理器
            processor = get_processor(mode)
            if not processor:
                raise AIResearchAgentError(f"無法獲取模式 '{mode}' 的處理器")
            
            # 處理請求
            result = self._process_request(processor, question, mode, **kwargs)
            
            # 添加元數據
            result.update(self._add_metadata(request_id, start_time, mode))
            
            # 記錄完成信息
            self._log_completion_info(request_id, result, start_time)
            
            return result
            
        except Exception as e:
            # 記錄錯誤信息
            self._log_error_info(request_id, e, start_time)
            raise
    
    def _process_request(
        self, 
        processor, 
        question: str, 
        mode: str, 
        **kwargs
    ) -> Dict[str, Any]:
        """
        處理具體的請求
        
        Args:
            processor: 對應的處理器實例
            question: 用戶問題
            mode: 處理模式
            **kwargs: 額外參數
            
        Returns:
            Dict[str, Any]: 處理結果
        """
        # 根據模式調用不同的處理邏輯
        if mode == "納入實驗資料，進行推論與建議":
            k = kwargs.get("k", 5)
            return processor.process(question, k=k)
            
        elif mode == "make proposal":
            k = kwargs.get("k", 10)
            return processor.process(question, k=k)
            
        elif mode == "允許延伸與推論":
            k = kwargs.get("k", 30)
            return processor.process(question, k=k)
            
        elif mode == "僅嚴謹文獻溯源":
            k = kwargs.get("k", 20)
            return processor.process(question, k=k)
            
        elif mode == "expand to experiment detail":
            chunks = kwargs.get("chunks", [])
            proposal = kwargs.get("proposal", "")
            return processor.process(question, chunks, proposal)
            
        elif mode == "generate new idea":
            old_chunks = kwargs.get("old_chunks", [])
            proposal = kwargs.get("proposal", "")
            k = kwargs.get("k", 5)
            return processor.process(question, old_chunks, proposal, k=k)
            
        else:
            raise AIResearchAgentError(f"未實現的模式處理邏輯：{mode}")
    
    def _generate_request_id(self) -> str:
        """生成請求ID"""
        self.request_counter += 1
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        return f"REQ_{timestamp}_{unique_id}_{self.request_counter:04d}"
    
    def _log_request_info(self, request_id: str, question: str, mode: str, kwargs: Dict):
        """記錄請求信息"""
        logger.info(f"🧠 [AGENT-{request_id}] ========== 開始處理請求 ==========")
        logger.info(f"🧠 [AGENT-{request_id}] 時間戳: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info(f"🧠 [AGENT-{request_id}] 問題: '{question}'")
        logger.info(f"🧠 [AGENT-{request_id}] 模式: '{mode}'")
        logger.info(f"🧠 [AGENT-{request_id}] 額外參數: {kwargs}")
        logger.info(f"🧠 [AGENT-{request_id}] 模式描述: {get_mode_description(mode)}")
    
    def _log_completion_info(self, request_id: str, result: Dict[str, Any], start_time: float):
        """記錄完成信息"""
        end_time = time.time()
        duration = end_time - start_time
        
        logger.info(f"✅ [AGENT-{request_id}] ========== 請求處理完成 ==========")
        logger.info(f"✅ [AGENT-{request_id}] 總耗時: {duration:.2f} 秒")
        logger.info(f"✅ [AGENT-{request_id}] 回答長度: {len(result.get('answer', ''))}")
        logger.info(f"✅ [AGENT-{request_id}] 引用數量: {len(result.get('citations', []))}")
        logger.info(f"✅ [AGENT-{request_id}] 文檔塊數量: {len(result.get('chunks', []))}")
    
    def _log_error_info(self, request_id: str, error: Exception, start_time: float):
        """記錄錯誤信息"""
        end_time = time.time()
        duration = end_time - start_time
        
        logger.error(f"❌ [AGENT-{request_id}] ========== 請求處理失敗 ==========")
        logger.error(f"❌ [AGENT-{request_id}] 總耗時: {duration:.2f} 秒")
        logger.error(f"❌ [AGENT-{request_id}] 錯誤類型: {type(error).__name__}")
        logger.error(f"❌ [AGENT-{request_id}] 錯誤信息: {str(error)}")
    
    def _add_metadata(self, request_id: str, start_time: float, mode: str) -> Dict[str, Any]:
        """添加元數據"""
        end_time = time.time()
        return {
            "request_id": request_id,
            "processing_time": end_time - start_time,
            "mode": mode,
            "mode_description": get_mode_description(mode),
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }


# 全局知識代理實例
_knowledge_agent_instance = None


def get_knowledge_agent() -> KnowledgeAgent:
    """
    獲取知識代理實例（單例模式）
    
    Returns:
        KnowledgeAgent: 知識代理實例
    """
    global _knowledge_agent_instance
    if _knowledge_agent_instance is None:
        _knowledge_agent_instance = KnowledgeAgent()
    return _knowledge_agent_instance


def agent_answer(question: str, mode: str = "make proposal", **kwargs) -> Dict[str, Any]:
    """
    知識代理的主要回答函數（便捷接口）
    
    Args:
        question: 用戶問題
        mode: 處理模式
        **kwargs: 額外參數
        
    Returns:
        Dict[str, Any]: 包含回答、引用和相關文檔塊的字典
    """
    agent = get_knowledge_agent()
    return agent.answer(question, mode, **kwargs)


def get_available_modes() -> List[str]:
    """
    獲取所有可用的處理模式
    
    Returns:
        List[str]: 可用模式列表
    """
    from .core.mode_manager import get_available_modes as get_modes
    return get_modes()


def validate_mode(mode: str) -> bool:
    """
    驗證模式是否有效
    
    Args:
        mode: 要驗證的模式
        
    Returns:
        bool: 模式是否有效
    """
    from .core.mode_manager import validate_mode as validate
    return validate(mode)


def get_mode_description(mode: str) -> str:
    """
    獲取模式的詳細描述
    
    Args:
        mode: 模式名稱
        
    Returns:
        str: 模式描述
    """
    from .core.mode_manager import get_mode_description as get_desc
    return get_desc(mode)
