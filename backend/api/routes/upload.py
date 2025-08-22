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
import time
import logging
import re
from pathlib import Path
from datetime import datetime

# 添加原項目路徑到 sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../app'))

# 使用絕對導入來避免相對導入問題
import sys
import os
# sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../app'))  # 已重組，不再需要

from backend.services.file_service import process_uploaded_files
from backend.services.embedding_service import embed_documents_from_metadata, embed_experiment_txt_batch, get_vectorstore_stats
from backend.services.excel_service import export_new_experiments_to_txt
from backend.config import EXPERIMENT_DIR

# 配置日誌
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

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

class VectorStatsResponse(BaseModel):
    """向量統計響應模型"""
    paper_vectors: int
    experiment_vectors: int
    total_vectors: int

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
                # 重置文件指針到開始位置，確保能讀取完整內容
                file.file.seek(0)
                with open(file_path, "wb") as buffer:
                    shutil.copyfileobj(file.file, buffer)
                
                # 驗證文件是否成功保存
                saved_size = os.path.getsize(file_path)
                if saved_size == 0:
                    logger.warning(f"⚠️ 文件 {file.filename} 保存後大小為 0 bytes")
                else:
                    logger.info(f"✅ 文件 {file.filename} 成功保存，大小: {saved_size} bytes")
                
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
    start_time = time.time()
    logger.info(f"🚀 開始處理任務 {task_id}，共 {len(file_paths)} 個文件")
    logger.info(f"📁 臨時目錄: {temp_dir}")
    
    try:
        # 更新狀態為處理中
        processing_tasks[task_id]["status"] = "processing"
        processing_tasks[task_id]["progress"] = 0
        processing_tasks[task_id]["message"] = "開始處理..."
        
        # 分析文件類型（依副檔名分類）
        logger.info("🔍 開始分析文件類型...")
        file_info = _classify_files_by_type(file_paths)
        
        # 記錄文件分類結果
        for file_type, files in file_info.items():
            if files:
                logger.info(f"📂 {file_type}: {len(files)} 個文件")
                for f in files:
                    file_size = os.path.getsize(f) if os.path.exists(f) else 0
                    logger.info(f"   📄 {os.path.basename(f)} ({file_size} bytes)")
        
        # 計算進度分配
        has_papers = bool(file_info.get("papers"))
        has_experiments = bool(file_info.get("experiments"))
        
        logger.info(f"📊 文件類型分析完成 - 論文: {has_papers}, 實驗: {has_experiments}")
        
        # 根據文件類型調整進度分配
        if has_papers and has_experiments:
            # 混合文件：論文佔70%，實驗佔25%
            paper_progress_range = 70
            experiment_progress_range = 25
        elif has_papers:
            # 只有論文：論文佔95%
            paper_progress_range = 95
            experiment_progress_range = 0
        elif has_experiments:
            # 只有實驗：實驗佔95%
            paper_progress_range = 0
            experiment_progress_range = 95
        else:
            # 其他文件：直接完成
            paper_progress_range = 0
            experiment_progress_range = 0
        
        processing_tasks[task_id]["progress"] = 10
        processing_tasks[task_id]["message"] = "開始處理論文資料..."
        
        # 定義進度回調函數
        def update_progress(message: str, progress_percent: int = None):
            if progress_percent is not None:
                processing_tasks[task_id]["progress"] = progress_percent
            processing_tasks[task_id]["message"] = message
            logger.info(f"📈 進度更新: {processing_tasks[task_id]['progress']}% - {message}")
        
        # 處理論文資料（提取 metadata 並嵌入向量）
        paper_results: List[Dict[str, Any]] = []
        
        # 初始化進度變量
        current_progress = 10
        
        if has_papers:
            logger.info("📚 開始處理論文資料...")
            
            # 計算論文處理的進度分配（總共100%，分為4個關鍵節點）
            # 節點1: 文件上傳開始 (10%)
            # 節點2: 元數據提取開始 (25%)
            # 節點3: 向量嵌入開始 (50%)
            # 節點4: 處理完成 (100%)
            
            # 節點1: 文件上傳已完成 (10%)
            current_progress = 10
            
            # 節點2: 元數據提取開始 (25%)
            logger.info("📄 開始元數據提取...")
            metadata_start_time = time.time()
            current_progress = 25  # 進入元數據提取階段，設置為25%
            update_progress("📄 開始元數據提取...", current_progress)
        
        # 創建一個進度追蹤變量
        extraction_progress = current_progress
        
        # 初始化時間變量
        metadata_start_time = time.time()
        metadata_end_time = time.time()
        
        def extraction_progress_callback(msg: str):
                nonlocal extraction_progress
                # 根據消息內容更新進度
                if "提取第" in msg and "個文件元數據" in msg:
                    try:
                        # 匹配 "提取第 X/Y 個文件元數據：{filename}" 格式
                        match = re.search(r'提取第 (\d+)/(\d+) 個文件元數據', msg)
                        if match:
                            current_file = int(match.group(1))
                            total_files = int(match.group(2))
                            # 計算進度：25% 到 50% 之間
                            progress = 25 + int((current_file / total_files) * 25)
                            extraction_progress = progress
                            update_progress(msg, progress)
                            logger.info(f"📈 元數據提取進度: {current_file}/{total_files} ({progress}%)")
                        else:
                            update_progress(msg, extraction_progress)
                    except Exception as e:
                        logger.warning(f"⚠️ 進度解析失敗: {e}")
                        update_progress(msg, extraction_progress)
                else:
                    update_progress(msg, extraction_progress)
        
        if has_papers:
            metadata_list: List[Dict[str, Any]] = process_uploaded_files(
                file_info["papers"], 
                status_callback=extraction_progress_callback
            )
            
            metadata_end_time = time.time()
            logger.info(f"✅ 元數據提取完成，耗時: {metadata_end_time - metadata_start_time:.2f}秒")
            logger.info(f"📊 成功提取 {len(metadata_list)} 個文件的元數據")
            
            # 記錄每個文件的元數據提取結果
            for i, metadata in enumerate(metadata_list):
                logger.info(f"   📄 {i+1}. {metadata.get('title', '未知標題')} - DOI: {metadata.get('doi', '無')}")
            
            paper_results.extend(metadata_list)
            update_progress("✅ 元數據提取完成", current_progress)
        else:
            metadata_list = []
        
        # 節點3: 向量嵌入開始 (50%)
        current_progress = 50  # 進入向量嵌入階段，設置為50%
        update_progress("✅ 開始向量嵌入", current_progress)
        
        # 初始化時間變量
        embedding_start_time = time.time()
        paper_start_time = time.time()
        
        logger.info("🔢 開始向量嵌入...")
        update_progress("📚 開始向量嵌入...", current_progress)
        
        # 計算每個文件的嵌入進度
        def embedding_progress_callback(msg: str):
            nonlocal current_progress  # 聲明使用外部變量
            # 從消息中提取當前處理的文件索引
            if "處理第" in msg and "個文件" in msg:
                try:
                    # 提取 "處理第 X/Y 個文件" 中的 X
                    match = re.search(r'處理第 (\d+)/(\d+) 個文件', msg)
                    if match:
                        current_file = int(match.group(1))
                        total_files = int(match.group(2))
                        # 計算進度：50% 到 90% 之間
                        progress = 50 + int((current_file / total_files) * 40)
                        update_progress(msg, progress)
                        logger.info(f"🔢 向量嵌入進度: {current_file}/{total_files} ({progress}%)")
                    else:
                        update_progress(msg, current_progress)  # 使用當前進度
                except (ValueError, AttributeError) as parse_error:
                    logger.warning(f"解析進度信息失敗: {parse_error}")
                    update_progress(msg, current_progress)  # 使用當前進度
            elif "向量嵌入批次" in msg:
                try:
                    # 提取 "向量嵌入批次 X/Y" 中的進度信息
                    match = re.search(r'向量嵌入批次 (\d+)/(\d+)', msg)
                    if match:
                        current_batch = int(match.group(1))
                        total_batches = int(match.group(2))
                        # 向量嵌入階段：90% 到 95% 之間
                        progress = 90 + int((current_batch / total_batches) * 5)
                        update_progress(msg, progress)
                        logger.info(f"🔢 向量嵌入批次: {current_batch}/{total_batches} ({progress}%)")
                    else:
                        update_progress(msg, current_progress)  # 使用當前進度
                except (ValueError, AttributeError) as parse_error:
                    logger.warning(f"解析批次進度信息失敗: {parse_error}")
                    update_progress(msg, current_progress)  # 使用當前進度
            elif "開始向量嵌入" in msg:
                # 向量嵌入開始，設置進度為50%
                update_progress(msg, 50)
                logger.info("🔢 向量嵌入開始")
            elif "向量嵌入完成" in msg:
                # 向量嵌入完成，設置進度為95%
                update_progress(msg, 95)
                embedding_end_time = time.time()
                logger.info(f"✅ 向量嵌入完成，耗時: {embedding_end_time - embedding_start_time:.2f}秒")
            else:
                update_progress(msg, current_progress)  # 使用當前進度
                logger.info(f"📝 嵌入進度: {msg}")
        
        logger.info(f"🔢 開始對 {len(metadata_list)} 個文件進行向量嵌入...")
        embed_documents_from_metadata(
            metadata_list, 
            status_callback=embedding_progress_callback
        )
        
        paper_end_time = time.time()
        logger.info(f"✅ 論文處理完成，總耗時: {paper_end_time - paper_start_time:.2f}秒")
        
        # 處理實驗資料（Excel -> txt -> 向量嵌入）
        experiment_results: List[Dict[str, Any]] = []
        if has_experiments:
            logger.info("🧪 開始處理實驗資料...")
            experiment_start_time = time.time()
            
            # 設置實驗處理的起始進度
            experiment_start_progress = 50  # 實驗處理從50%開始
            processing_tasks[task_id]["progress"] = experiment_start_progress
            processing_tasks[task_id]["message"] = "處理實驗資料..."
            
            for i, f in enumerate(file_info["experiments"]):
                try:
                    logger.info(f"🧪 處理實驗文件 {i+1}/{len(file_info['experiments'])}: {os.path.basename(f)}")
                    processing_tasks[task_id]["message"] = f"處理實驗文件 {i+1}/{len(file_info['experiments'])}..."
                    processing_tasks[task_id]["progress"] = experiment_start_progress + int((i / len(file_info["experiments"])) * experiment_progress_range)
                    
                    # 記錄文件大小
                    file_size = os.path.getsize(f) if os.path.exists(f) else 0
                    logger.info(f"   📊 文件大小: {file_size} bytes")
                    
                    # 轉換Excel為TXT
                    logger.info(f"   📄 開始轉換Excel為TXT...")
                    excel_start_time = time.time()
                    df, txt_paths = export_new_experiments_to_txt(
                        excel_path=f,
                        output_dir=EXPERIMENT_DIR
                    )
                    excel_end_time = time.time()
                    logger.info(f"   ✅ Excel轉換完成，生成 {len(txt_paths)} 個TXT文件，耗時: {excel_end_time - excel_start_time:.2f}秒")
                    
                    # 向量嵌入
                    logger.info(f"   🔢 開始實驗數據向量嵌入...")
                    embed_start_time = time.time()
                    result = embed_experiment_txt_batch(txt_paths)
                    embed_end_time = time.time()
                    logger.info(f"   ✅ 實驗數據向量嵌入完成，耗時: {embed_end_time - embed_start_time:.2f}秒")
                    
                    experiment_results.append({
                        "file": f,
                        "txt_paths": txt_paths,
                        "embedded_count": len(txt_paths)
                    })
                    
                except Exception as e:
                    logger.error(f"❌ 實驗文件處理失敗 {os.path.basename(f)}: {e}")
                    experiment_results.append({
                        "file": f,
                        "error": str(e)
                    })
            
            experiment_end_time = time.time()
            logger.info(f"✅ 實驗處理完成，總耗時: {experiment_end_time - experiment_start_time:.2f}秒")
        
        # 節點4: 處理完成 (100%)
        # 添加短暫延遲，讓前端有機會看到95%的進度
        time.sleep(0.5)  # 延遲0.5秒
        
        # 更新進度到98%，表示正在完成最後的統計更新
        processing_tasks[task_id]["progress"] = 98
        processing_tasks[task_id]["message"] = "正在完成處理..."
        
        # 再延遲一下，讓前端看到98%的進度
        time.sleep(0.3)
        
        processing_tasks[task_id]["progress"] = 100
        processing_tasks[task_id]["message"] = "處理完成"
        
        # 更新向量統計緩存
        logger.info("📊 開始更新向量統計緩存...")
        vector_stats = {}
        try:
            from main import update_vector_stats_cache, get_cached_vector_stats
            update_vector_stats_cache()
            cached_stats = get_cached_vector_stats()
            vector_stats = {
                "paper_vectors": cached_stats["paper_vectors"],
                "experiment_vectors": cached_stats["experiment_vectors"],
                "total_vectors": cached_stats["total_vectors"]
            }
            logger.info(f"📊 向量統計緩存更新 - 論文: {vector_stats['paper_vectors']}, 實驗: {vector_stats['experiment_vectors']}, 總計: {vector_stats['total_vectors']}")
            print(f"📊 向量統計緩存更新 - 論文: {vector_stats['paper_vectors']}, 實驗: {vector_stats['experiment_vectors']}, 總計: {vector_stats['total_vectors']}")
        except Exception as e:
            logger.error(f"⚠️ 無法更新向量統計緩存: {e}")
            print(f"⚠️ 無法更新向量統計緩存: {e}")
            vector_stats = {"paper_vectors": 0, "experiment_vectors": 0, "total_vectors": 0}
        
        # 更新最終結果
        end_time = time.time()
        total_time = end_time - start_time
        logger.info(f"🎉 任務 {task_id} 處理完成，總耗時: {total_time:.2f}秒")
        
        processing_tasks[task_id]["status"] = "completed"
        # 進度已經在之前設置為100%，這裡不需要重複設置
        processing_tasks[task_id]["message"] = "處理完成"
        processing_tasks[task_id]["results"] = {
            "paper_results": paper_results,
            "experiment_results": experiment_results,
            "file_info": file_info,
            "vector_stats": vector_stats,
            "processing_time": total_time
        }
        
    except Exception as e:
        error_time = time.time()
        total_time = error_time - start_time
        logger.error(f"❌ 任務 {task_id} 處理失敗，耗時: {total_time:.2f}秒，錯誤: {e}")
        processing_tasks[task_id]["status"] = "failed"
        processing_tasks[task_id]["message"] = f"處理失敗: {str(e)}"
    finally:
        # 清理臨時目錄
        try:
            shutil.rmtree(temp_dir)
            logger.info(f"🧹 清理臨時目錄: {temp_dir}")
        except Exception as e:
            logger.warning(f"⚠️ 清理臨時目錄失敗: {e}")
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

@router.get("/upload/stats", response_model=VectorStatsResponse)
async def get_vector_stats():
    """
    獲取向量數據庫統計信息（使用緩存）
    
    Returns:
        向量數據庫統計信息
    """
    try:
        # 從主模塊獲取緩存的統計信息
        from main import get_cached_vector_stats
        cached_stats = get_cached_vector_stats()
        
        return VectorStatsResponse(
            paper_vectors=cached_stats["paper_vectors"],
            experiment_vectors=cached_stats["experiment_vectors"],
            total_vectors=cached_stats["total_vectors"]
        )
    except Exception as e:
        print(f"⚠️ 無法獲取緩存的向量統計信息: {e}")
        return VectorStatsResponse(
            paper_vectors=0,
            experiment_vectors=0,
            total_vectors=0
        )

@router.post("/upload/refresh-stats", response_model=VectorStatsResponse)
async def refresh_vector_stats():
    """
    手動刷新向量統計緩存
    
    Returns:
        更新後的向量數據庫統計信息
    """
    try:
        from main import update_vector_stats_cache, get_cached_vector_stats
        update_vector_stats_cache()
        cached_stats = get_cached_vector_stats()
        
        return VectorStatsResponse(
            paper_vectors=cached_stats["paper_vectors"],
            experiment_vectors=cached_stats["experiment_vectors"],
            total_vectors=cached_stats["total_vectors"]
        )
    except Exception as e:
        print(f"⚠️ 無法刷新向量統計緩存: {e}")
        return VectorStatsResponse(
            paper_vectors=0,
            experiment_vectors=0,
            total_vectors=0
        )

@router.get("/documents/{filename:path}")
async def download_document(filename: str):
    """
    下載文檔文件
    
    Args:
        filename: 文件名（支持子目錄路徑）
        
    Returns:
        文件內容
    """
    try:
        import os
        # 獲取項目根目錄（從backend目錄向上兩級到項目根目錄）
        current_file_dir = os.path.dirname(__file__)  # backend/api/routes/
        backend_dir = os.path.dirname(os.path.dirname(current_file_dir))  # backend/
        project_root = os.path.dirname(backend_dir)  # 項目根目錄
        print(f"🔍 DEBUG: current_file_dir = {current_file_dir}")
        print(f"🔍 DEBUG: backend_dir = {backend_dir}")
        print(f"🔍 DEBUG: project_root = {project_root}")
        print(f"🔍 DEBUG: filename = {filename}")
        
        # 檢查是否為直接文件名（不包含路徑）
        if not os.path.dirname(filename):
            # 如果是直接文件名，則假設在papers目錄中
            file_path = os.path.join(project_root, "experiment_data", "papers", filename)
        else:
            # 如果包含路徑，則使用完整路徑
            file_path = os.path.join(project_root, filename)
        
        # 安全檢查：確保文件路徑在允許的目錄內
        allowed_dirs = [
            os.path.join(project_root, "experiment_data", "papers"),
            os.path.join(project_root, "uploads")
        ]
        
        file_path_abs = os.path.abspath(file_path)
        is_allowed = any(file_path_abs.startswith(allowed_dir) for allowed_dir in allowed_dirs)
        
        if not is_allowed:
            print(f"❌ 訪問被拒絕: {file_path_abs}")
            print(f"❌ 允許的目錄: {allowed_dirs}")
            raise HTTPException(status_code=403, detail="訪問被拒絕")
        
        if not os.path.exists(file_path):
            print(f"❌ 文件不存在: {file_path}")
            raise HTTPException(status_code=404, detail="文件不存在")
        
        print(f"✅ 提供文件: {file_path}")
        
        # 設置MIME類型映射
        mime_types = {
            '.pdf': 'application/pdf',
            '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            '.doc': 'application/msword',
            '.txt': 'text/plain',
            '.html': 'text/html',
            '.htm': 'text/html'
        }
        
        # 根據文件類型設置正確的MIME類型和響應頭
        # 特殊處理：檢查文件名是否以_SI.pdf結尾，也應該識別為PDF
        if filename.lower().endswith('_si.pdf'):
            file_extension = '.pdf'
        else:
            file_extension = os.path.splitext(filename)[1].lower()
        
        media_type = mime_types.get(file_extension, 'application/octet-stream')
        
        # 對於PDF文件，設置響應頭讓瀏覽器直接顯示而不是下載
        headers = {}
        if file_extension == '.pdf':
            # 強制設置 PDF 文件的響應頭
            headers['Content-Disposition'] = 'inline'
            headers['Content-Type'] = 'application/pdf'
            # 添加額外的頭來確保瀏覽器正確處理
            headers['X-Content-Type-Options'] = 'nosniff'
            headers['Cache-Control'] = 'public, max-age=3600'
            # 對於 SI 文件，添加特殊標識
            if filename.lower().endswith('_si.pdf'):
                headers['X-File-Type'] = 'supplementary-information'
        else:
            headers['Content-Disposition'] = f'inline; filename="{os.path.basename(filename)}"'
        
        # 返回文件
        return FileResponse(
            path=file_path,
            filename=os.path.basename(filename),
            media_type=media_type,
            headers=headers
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ 文件下載失敗: {str(e)}")
        raise HTTPException(status_code=500, detail=f"文件下載失敗: {str(e)}") 