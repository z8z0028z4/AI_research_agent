"""
API 路由包
==========

包含所有 API 端點的路由模塊
"""

from .upload_refactored import router as upload_router
from .document_download import router as document_router
from .search import router as search_router
from .knowledge import router as knowledge_router
from .chemical import router as chemical_router
from .experiment import router as experiment_router
from .proposal import router as proposal_router
from .settings import router as settings_router

# 路由列表，用於在主應用中註冊
routers = [
    upload_router,
    document_router,
    search_router,
    knowledge_router,
    chemical_router,
    experiment_router,
    proposal_router,
    settings_router
] 