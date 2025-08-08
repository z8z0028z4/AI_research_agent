"""
文件上傳 API 路由
================

處理文件上傳、處理和狀態查詢功能
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, BackgroundTasks
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import os
import sys
import tempfile
import shutil
from pathlib import Path

# 添加原項目路徑到 sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../app'))

from file_upload import process_uploaded_files
from chunk_embedding import embed_documents_from_metadata, embed_experiment_txt_batch
from excel_to_txt_by_row import export_new_experiments_to_txt
from config import EXPERIMENT_DIR

router = APIRouter()

class FileUploadResponse(BaseModel):
    """文件上傳響應模型"""
    success: bool
    message: str
    file_info: Dict[str, Any]
    processing_status: str

class ProcessingStatus(BaseModel):
    """處理狀態模型"""
    task_id: str
    status: str  # pending, processing, completed, failed
    progress: int
    message: str
    results: Optional[Dict[str, Any]] = None

# 存儲處理任務狀態
processing_tasks = {}

@router.post("/upload/files", response_model=FileUploadResponse)
async def upload_files(
    background_tasks: BackgroundTasks,
    files: List[UploadFile] = File(...)
):
    """
    上傳並處理文件
    
    Args:
        background_tasks: 後台任務管理器
        files: 上傳的文件列表
        
    Returns:
        上傳結果和處理狀態
    """
    try:
        # 創建臨時目錄存儲上傳的文件
        temp_dir = tempfile.mkdtemp()
        uploaded_files = []
        
        # 保存上傳的文件
        for file in files:
            if file.filename:
                file_path = os.path.join(temp_dir, file.filename)
                with open(file_path, "wb") as buffer:
                    shutil.copyfileobj(file.file, buffer)
                uploaded_files.append(file_path)
        
        # 生成任務 ID
        task_id = f"task_{len(processing_tasks) + 1}"
        
        # 初始化任務狀態
        processing_tasks[task_id] = {
            "status": "pending",
            "progress": 0,
            "message": "文件上傳完成，開始處理...",
            "results": None
        }
        
        # 在後台處理文件
        background_tasks.add_task(
            process_files_background,
            task_id,
            uploaded_files,
            temp_dir
        )
        
        return FileUploadResponse(
            success=True,
            message="文件上傳成功，開始處理",
            file_info={
                "task_id": task_id,
                "file_count": len(files),
                "file_names": [f.filename for f in files if f.filename]
            },
            processing_status="pending"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"文件上傳失敗: {str(e)}")

def _classify_files_by_type(file_paths: List[str]) -> Dict[str, List[str]]:
    """根據副檔名將檔案分類為論文或實驗資料。"""
    papers: List[str] = []
    experiments: List[str] = []
    other: List[str] = []

    for path in file_paths:
        ext = os.path.splitext(path)[1].lower()
        if ext in [".pdf", ".docx"]:
            papers.append(path)
        elif ext in [".xlsx", ".xls"]:
            experiments.append(path)
        else:
            other.append(path)

    return {"type": "mixed", "papers": papers, "experiments": experiments, "others": other}


async def process_files_background(task_id: str, file_paths: List[str], temp_dir: str):
    """
    後台處理文件
    
    Args:
        task_id: 任務 ID
        file_paths: 文件路徑列表
        temp_dir: 臨時目錄
    """
    try:
        # 更新狀態為處理中
        processing_tasks[task_id]["status"] = "processing"
        processing_tasks[task_id]["progress"] = 10
        processing_tasks[task_id]["message"] = "分析文件類型..."
        
        # 分析文件類型（依副檔名分類）
        file_info = _classify_files_by_type(file_paths)
        
        processing_tasks[task_id]["progress"] = 30
        processing_tasks[task_id]["message"] = "處理論文資料..."
        
        # 處理論文資料（提取 metadata 並嵌入向量）
        paper_results: List[Dict[str, Any]] = []
        if file_info.get("papers"):
            # 先批次萃取 metadata
            metadata_list: List[Dict[str, Any]] = process_uploaded_files(file_info["papers"])
            paper_results.extend(metadata_list)
            # 進行嵌入
            embed_documents_from_metadata(metadata_list)
        
        processing_tasks[task_id]["progress"] = 60
        processing_tasks[task_id]["message"] = "處理實驗資料..."
        
        # 處理實驗資料（Excel -> txt -> 向量嵌入）
        experiment_results: List[Dict[str, Any]] = []
        if file_info.get("experiments"):
            for f in file_info["experiments"]:
                try:
                    df, txt_paths = export_new_experiments_to_txt(
                        excel_path=f,
                        output_dir=EXPERIMENT_DIR
                    )
                    result = embed_experiment_txt_batch(txt_paths)
                    experiment_results.append({
                        "file": f,
                        "txt_paths": txt_paths,
                        "embedded_count": len(txt_paths)
                    })
                except Exception as e:
                    experiment_results.append({
                        "file": f,
                        "error": str(e)
                    })
        
        processing_tasks[task_id]["progress"] = 90
        processing_tasks[task_id]["message"] = "完成處理..."
        
        # 更新最終結果
        processing_tasks[task_id]["status"] = "completed"
        processing_tasks[task_id]["progress"] = 100
        processing_tasks[task_id]["message"] = "處理完成"
        processing_tasks[task_id]["results"] = {
            "paper_results": paper_results,
            "experiment_results": experiment_results,
            "file_info": file_info
        }
        
    except Exception as e:
        processing_tasks[task_id]["status"] = "failed"
        processing_tasks[task_id]["message"] = f"處理失敗: {str(e)}"
    finally:
        # 清理臨時目錄
        try:
            shutil.rmtree(temp_dir)
        except:
            pass

@router.get("/upload/status/{task_id}", response_model=ProcessingStatus)
async def get_processing_status(task_id: str):
    """
    獲取文件處理狀態
    
    Args:
        task_id: 任務 ID
        
    Returns:
        處理狀態信息
    """
    if task_id not in processing_tasks:
        raise HTTPException(status_code=404, detail="任務不存在")
    
    task = processing_tasks[task_id]
    return ProcessingStatus(
        task_id=task_id,
        status=task["status"],
        progress=task["progress"],
        message=task["message"],
        results=task["results"]
    )

@router.get("/upload/download/{task_id}")
async def download_processed_files(task_id: str):
    """
    下載處理後的文件
    
    Args:
        task_id: 任務 ID
        
    Returns:
        處理後的文件
    """
    if task_id not in processing_tasks:
        raise HTTPException(status_code=404, detail="任務不存在")
    
    task = processing_tasks[task_id]
    if task["status"] != "completed":
        raise HTTPException(status_code=400, detail="任務尚未完成")
    
    # TODO: 實現文件打包和下載
    return {"message": "下載功能待實現"}

@router.delete("/upload/cancel/{task_id}")
async def cancel_processing(task_id: str):
    """
    取消文件處理任務
    
    Args:
        task_id: 任務 ID
        
    Returns:
        取消結果
    """
    if task_id not in processing_tasks:
        raise HTTPException(status_code=404, detail="任務不存在")
    
    processing_tasks[task_id]["status"] = "cancelled"
    processing_tasks[task_id]["message"] = "任務已取消"
    
    return {"message": "任務已取消", "task_id": task_id} 