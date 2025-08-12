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
from dotenv import load_dotenv

# 載入環境變量
load_dotenv()

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
from api.routes import proposal, search, chemical, upload, experiment, settings

# 註冊路由
app.include_router(proposal.router, prefix="/api/v1", tags=["proposal"])
app.include_router(search.router, prefix="/api/v1", tags=["search"])
app.include_router(chemical.router, prefix="/api/v1", tags=["chemical"])
app.include_router(upload.router, prefix="/api/v1", tags=["upload"])
app.include_router(experiment.router, prefix="/api/v1", tags=["experiment"])
app.include_router(settings.router, prefix="/api/v1", tags=["settings"])

@app.get("/")
async def root():
    """根路徑，返回 API 信息"""
    return {
        "message": "AI Research Assistant API",
        "version": "1.0.0",
        "docs": "/api/docs"
    }

@app.get("/health")
async def health_check():
    """健康檢查端點"""
    return {"status": "healthy", "service": "ai-research-assistant"}

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) 