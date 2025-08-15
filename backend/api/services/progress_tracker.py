"""
進度追蹤服務
============

管理文件處理任務的進度和狀態
"""

import time
import logging
from typing import Dict, Any, Optional, Callable
from ..models.upload_models import ProcessingStatus

logger = logging.getLogger(__name__)


class ProgressTracker:
    """進度追蹤器"""
    
    def __init__(self):
        self.tasks: Dict[str, Dict[str, Any]] = {}
    
    def create_task(self, task_id: str) -> None:
        """創建新任務"""
        self.tasks[task_id] = {
            "status": "pending",
            "progress": 0,
            "message": "任務已創建",
            "results": None,
            "start_time": time.time()
        }
        logger.info(f"📋 創建任務: {task_id}")
    
    def update_task(self, task_id: str, status: str = None, 
                   progress: int = None, message: str = None,
                   results: Dict[str, Any] = None) -> None:
        """更新任務狀態"""
        if task_id not in self.tasks:
            logger.warning(f"⚠️ 任務不存在: {task_id}")
            return
            
        task = self.tasks[task_id]
        
        if status is not None:
            task["status"] = status
        if progress is not None:
            task["progress"] = progress
        if message is not None:
            task["message"] = message
        if results is not None:
            task["results"] = results
            
        logger.info(f"📈 任務 {task_id} 更新: {task['status']} - {task['progress']}% - {task['message']}")
    
    def get_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        """獲取任務狀態"""
        return self.tasks.get(task_id)
    
    def get_task_status(self, task_id: str) -> Optional[ProcessingStatus]:
        """獲取任務狀態模型"""
        task = self.get_task(task_id)
        if not task:
            return None
            
        return ProcessingStatus(
            task_id=task_id,
            status=task["status"],
            progress=task["progress"],
            message=task["message"],
            results=task["results"]
        )
    
    def cancel_task(self, task_id: str) -> bool:
        """取消任務"""
        if task_id not in self.tasks:
            return False
            
        self.update_task(task_id, status="cancelled", message="任務已取消")
        return True
    
    def complete_task(self, task_id: str, results: Dict[str, Any]) -> None:
        """完成任務"""
        end_time = time.time()
        start_time = self.tasks[task_id].get("start_time", end_time)
        processing_time = end_time - start_time
        
        self.update_task(
            task_id,
            status="completed",
            progress=100,
            message="處理完成",
            results={**results, "processing_time": processing_time}
        )
    
    def fail_task(self, task_id: str, error_message: str) -> None:
        """標記任務失敗"""
        end_time = time.time()
        start_time = self.tasks[task_id].get("start_time", end_time)
        processing_time = end_time - start_time
        
        self.update_task(
            task_id,
            status="failed",
            message=f"處理失敗: {error_message}",
            results={"error": error_message, "processing_time": processing_time}
        )
    
    def create_progress_callback(self, task_id: str, 
                               start_progress: int = 0, 
                               end_progress: int = 100) -> Callable[[str, int], None]:
        """創建進度回調函數"""
        def progress_callback(message: str, progress_percent: int = None):
            if progress_percent is not None:
                # 將進度映射到指定範圍
                mapped_progress = start_progress + int((progress_percent / 100) * (end_progress - start_progress))
                self.update_task(task_id, progress=mapped_progress, message=message)
            else:
                self.update_task(task_id, message=message)
                
        return progress_callback


# 全局進度追蹤器實例
progress_tracker = ProgressTracker()
