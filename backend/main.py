"""
AI Research Assistant Backend API
================================

FastAPI 後端服務，為 React 前端提供 API 接口
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn
import os
import sys
import time
import logging
from dotenv import load_dotenv

# 添加原項目路徑到 sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), '../app'))

# 載入環境變量
load_dotenv()

# 配置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 全局變量存儲向量統計信息
vector_stats_cache = {
    "paper_vectors": 0,
    "experiment_vectors": 0,
    "total_vectors": 0,
    "last_updated": None,
    "is_initialized": False
}

def initialize_vector_stats():
    """
    初始化向量統計信息
    在後端啟動時預先計算並緩存統計信息
    """
    global vector_stats_cache
    
    try:
        logger.info("🚀 開始初始化向量統計信息...")
        start_time = time.time()
        
        # 導入統計函數
        from chunk_embedding import get_vectorstore_stats
        
        # 獲取論文和實驗向量統計
        paper_stats = get_vectorstore_stats("paper")
        experiment_stats = get_vectorstore_stats("experiment")
        
        # 提取統計數據
        paper_count = paper_stats.get("total_documents", 0) if isinstance(paper_stats, dict) else 0
        experiment_count = experiment_stats.get("total_documents", 0) if isinstance(experiment_stats, dict) else 0
        
        # 更新緩存
        vector_stats_cache.update({
            "paper_vectors": paper_count,
            "experiment_vectors": experiment_count,
            "total_vectors": paper_count + experiment_count,
            "last_updated": time.time(),
            "is_initialized": True
        })
        
        end_time = time.time()
        logger.info(f"✅ 向量統計初始化完成，耗時: {end_time - start_time:.2f}秒")
        logger.info(f"📊 統計結果 - 論文: {paper_count}, 實驗: {experiment_count}, 總計: {paper_count + experiment_count}")
        
    except Exception as e:
        logger.error(f"❌ 向量統計初始化失敗: {e}")
        # 設置默認值
        vector_stats_cache.update({
            "paper_vectors": 0,
            "experiment_vectors": 0,
            "total_vectors": 0,
            "last_updated": time.time(),
            "is_initialized": True
        })

def get_cached_vector_stats():
    """
    獲取緩存的向量統計信息
    """
    return vector_stats_cache

def update_vector_stats_cache():
    """
    更新向量統計緩存
    在文件處理完成後調用此函數
    """
    global vector_stats_cache
    
    try:
        logger.info("🔄 開始更新向量統計緩存...")
        from chunk_embedding import get_vectorstore_stats
        
        paper_stats = get_vectorstore_stats("paper")
        experiment_stats = get_vectorstore_stats("experiment")
        
        paper_count = paper_stats.get("total_documents", 0) if isinstance(paper_stats, dict) else 0
        experiment_count = experiment_stats.get("total_documents", 0) if isinstance(experiment_stats, dict) else 0
        
        vector_stats_cache.update({
            "paper_vectors": paper_count,
            "experiment_vectors": experiment_count,
            "total_vectors": paper_count + experiment_count,
            "last_updated": time.time()
        })
        
        logger.info(f"✅ 向量統計緩存更新完成 - 論文: {paper_count}, 實驗: {experiment_count}, 總計: {paper_count + experiment_count}")
        
    except Exception as e:
        logger.error(f"❌ 更新向量統計緩存失敗: {e}")

# 創建 FastAPI 應用
app = FastAPI(
    title="AI Research Assistant API",
    description="AI 研究助理後端 API 服務",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # React 開發服務器
        "http://localhost:5173",  # Vite 開發服務器
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 掛載靜態文件
if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

# 導入路由
from api.routes import proposal, search, chemical, upload, experiment, settings, knowledge

# 註冊路由
app.include_router(proposal.router, prefix="/api/v1", tags=["proposal"])
app.include_router(search.router, prefix="/api/v1", tags=["search"])
app.include_router(chemical.router, prefix="/api/v1", tags=["chemical"])
app.include_router(upload.router, prefix="/api/v1", tags=["upload"])
app.include_router(experiment.router, prefix="/api/v1", tags=["experiment"])
app.include_router(settings.router, prefix="/api/v1", tags=["settings"])
app.include_router(knowledge.router, prefix="/api/v1", tags=["knowledge"])

@app.on_event("startup")
async def startup_event():
    """
    應用啟動時的事件處理
    """
    logger.info("🚀 AI Research Assistant 後端服務啟動中...")
    
    # 初始化向量統計信息
    initialize_vector_stats()
    
    logger.info("✅ 後端服務啟動完成")

@app.get("/")
async def root():
    """根路徑，返回 API 信息"""
    return {
        "message": "AI Research Assistant API",
        "version": "1.0.0",
        "docs": "/api/docs",
        "vector_stats_initialized": vector_stats_cache["is_initialized"]
    }

@app.get("/health")
async def health_check():
    """健康檢查端點"""
    return {
        "status": "healthy", 
        "service": "ai-research-assistant",
        "vector_stats_initialized": vector_stats_cache["is_initialized"]
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) 