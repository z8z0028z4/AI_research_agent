"""
Backend Services Module
======================

業務服務層模組，包含：
- 化學服務
- 文件服務
- 知識服務
- 搜索服務
- 元數據服務
- 模型服務
- 外部 API 服務
"""

from .chemical_service import *
from .file_service import *
from .knowledge_service import *
from .search_service import *
from .semantic_service import *
from .query_service import *
from .metadata_service import *
from .model_service import *
from .external_api_service import *
from .embedding_service import *
from .excel_service import *
from .document_service import *
from .rag_service import *
from .pubchem_service import *
from .smiles_drawer import *

__all__ = [
    # 化學服務
    "chemical_service",
    "chemical_metadata_extractor",
    "extract_and_fetch_chemicals",
    "remove_json_chemical_block",
    
    # 文件服務
    "process_uploaded_files",
    
    # 知識服務
    "agent_answer",
    
    # 搜索服務
    "search_and_download_only",
    
    # 語義服務
    "semantic_search",
    
    # 查詢服務
    "parse_query",
    
    # 元數據服務
    "extract_metadata",
    "register_metadata",
    "register_experiment_metadata",
    
    # 模型服務
    "get_current_model",
    "get_model_params",
    "detect_model_parameters",
    
    # 外部 API 服務
    "europepmc_search",
    
    # 嵌入服務
    "embed_documents",
    "get_vectorstore_stats",
    "get_chroma_instance",
    
    # Excel 服務
    "export_experiments_to_txt",
    
    # 文檔服務
    "read_pdf",
    "rename_documents",
    
    # RAG 服務
    "generate_iterative_structured_proposal",
    "generate_structured_experimental_detail",
    
    # PubChem 服務
    "fetch_chemical_data",
    
    # SMILES 繪製服務
    "draw_smiles",
] 