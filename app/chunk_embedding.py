"""
AI 研究助理 - 文檔分塊和向量嵌入模塊
================================

這個模塊負責將文檔轉換為向量表示，為RAG系統提供檢索基礎。
主要功能包括：
1. 文檔分塊和預處理
2. 文本向量化
3. 向量數據庫存儲
4. 批量處理支持

架構說明：
- 使用LangChain的文本分割器
- 集成HuggingFace嵌入模型
- 使用Chroma作為向量數據庫
- 支持GPU加速計算

⚠️ 注意：此模塊是RAG系統的基礎，所有文檔檢索都依賴於此模塊
"""

import os
import sys
import time
import logging
from typing import List, Dict, Any, Optional
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
import chromadb
from chromadb.config import Settings
from pdf_read_and_chunk_page_get import load_and_parse_file, get_page_number_for_chunk
import torch
from sentence_transformers import SentenceTransformer

# 配置日誌
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# ==================== 全局變量 ====================
# 配置路徑
VECTOR_INDEX_DIR = os.path.join(os.path.dirname(__file__), "..", "experiment_data", "vector_index")

# Add backend to path to import settings_manager
backend_path = os.path.join(os.path.dirname(__file__), "..", "backend")
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

try:
    from core.settings_manager import settings_manager
    EMBEDDING_MODEL_NAME = settings_manager.get_embedding_model()
except (ImportError, AttributeError):
    # Switched to a more stable model to resolve startup issues.
    EMBEDDING_MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"


# 設備配置
device = "cuda" if torch.cuda.is_available() else "cpu"

# 全局 Chroma 實例緩存，避免重複創建
_chroma_instances = {}
_embedding_model_instance = None

def get_embedding_model_instance():
    """
    獲取或創建一個全局的嵌入模型實例
    """
    global _embedding_model_instance
    if _embedding_model_instance is None:
        try:
            logger.info(f"🚀首次加載嵌入模型: {EMBEDDING_MODEL_NAME} on device: {device}")
            # 1. 直接使用 sentence_transformers 庫加載模型
            model = SentenceTransformer(
                EMBEDDING_MODEL_NAME,
                device=device,
                trust_remote_code=True
            )
            # 2. 將加載好的模型對象傳遞給 LangChain 封裝器
            _embedding_model_instance = HuggingFaceEmbeddings(client=model)
            logger.info("✅ 嵌入模型加載成功")
        except Exception as e:
            logger.error(f"❌ 加載嵌入模型失敗: {e}")
            raise
    return _embedding_model_instance

def get_chroma_instance(vectorstore_type: str = "paper"):
    """
    獲取或創建 Chroma 實例（使用新的 ChromaDB 架構）
    
    參數：
        vectorstore_type (str): 向量數據庫類型（"paper" 或 "experiment"）
    
    返回：
        Chroma: 向量數據庫實例
    """
    if vectorstore_type not in _chroma_instances:
        try:
            embedding_model = get_embedding_model_instance()
            
            if vectorstore_type == "paper":
                vector_dir = os.path.join(VECTOR_INDEX_DIR, "paper_vector")
                collection_name = "paper"
            else:
                vector_dir = os.path.join(VECTOR_INDEX_DIR, "experiment_vector")
                collection_name = "experiment"
            
            # 確保目錄存在
            os.makedirs(vector_dir, exist_ok=True)
            
            # 使用新的 ChromaDB 1.0+ 客戶端配置
            client = chromadb.PersistentClient(
                path=vector_dir,
                settings=Settings(anonymized_telemetry=False) # 禁用遙測
            )
            
            _chroma_instances[vectorstore_type] = Chroma(
                client=client,
                collection_name=collection_name,
                embedding_function=embedding_model
            )
            logger.info(f"✅ ChromaDB 實例 '{collection_name}' 創建成功.")
            
        except Exception as e:
            logger.error(f"❌ 創建向量數據庫 '{vectorstore_type}' 失敗: {e}")
            raise
    
    return _chroma_instances[vectorstore_type]


# ==================== 設備配置 ====================
# 自動檢測並使用GPU或CPU進行向量計算
print(f"🚀 嵌入模型使用設備：{device.upper()}")


def embed_documents_from_metadata(metadata_list, status_callback=None):
    """
    根據元數據列表嵌入文檔
    """
    start_time = time.time()
    logger.info(f"🚀 開始向量嵌入處理，共 {len(metadata_list)} 個文件")
    
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
        separators=["\n\n", "\n", ".", "。", " ", ""]
    )
    
    texts, metadatas = [], []

    if status_callback:
        status_callback("📚 開始文件分塊處理...")
    
    logger.info("📚 開始文件分塊處理...")
    for i, metadata in enumerate(metadata_list):
        filename = metadata.get("new_filename", metadata.get("original_filename", "unknown"))
        file_path = metadata.get("new_path", metadata.get("original_path"))
        
        if not file_path:
            logger.error(f"❌ 無法獲取文件路徑: {filename}")
            continue

        absolute_path = file_path
        if not os.path.isabs(file_path):
             current_dir = os.getcwd()
             if os.path.basename(current_dir) == "backend":
                 project_root = os.path.dirname(os.path.dirname(current_dir))
                 absolute_path = os.path.join(project_root, file_path)
             else:
                 absolute_path = os.path.abspath(file_path)

        if not os.path.exists(absolute_path):
            logger.error(f"❌ 文件不存在: {absolute_path}")
            continue
        
        try:
            doc_chunks = load_and_parse_file(absolute_path)
            chunks = splitter.split_text(doc_chunks)

            for j, chunk in enumerate(chunks):
                if len(chunk.strip()) < 10:
                    continue
                page_num = get_page_number_for_chunk(absolute_path, chunk)
                texts.append(chunk)
                metadatas.append({
                    "source": filename,
                    "title": metadata.get("title", "未知標題"),
                    "type": metadata.get("type", "unknown"),
                    "tracing_number": metadata.get("tracing_number", "unknown"),
                    "page": page_num,
                    "chunk_index": j,
                    "total_chunks": len(chunks)
                })
        except Exception as e:
            logger.error(f"❌ 處理文件失敗 {absolute_path}: {e}")
            continue
    
    if not texts:
        logger.warning("⚠️ 沒有有效的文本塊進行嵌入")
        return
    
    if status_callback:
        status_callback(f"🔢 開始向量嵌入，共 {len(texts)} 個文本塊...")
    
    try:
        vectorstore = get_chroma_instance()
        batch_size = 500
        for i in range(0, len(texts), batch_size):
            batch_texts = texts[i:i + batch_size]
            batch_metadatas = metadatas[i:i + batch_size]
            vectorstore.add_texts(texts=batch_texts, metadatas=batch_metadatas)
            if status_callback:
                status_callback(f"🔢 向量嵌入批次 {i//batch_size + 1}/{(len(texts) + batch_size - 1)//batch_size}...")
    except Exception as e:
        logger.error(f"❌ 向量嵌入失敗: {e}")
        if status_callback:
            status_callback(f"❌ 向量嵌入失敗: {e}")
        raise
    
    end_time = time.time()
    logger.info(f"🎉 向量嵌入處理完成，總耗時: {end_time - start_time:.2f}秒")


def embed_experiment_txt_batch(txt_paths: List[str], status_callback=None):
    """
    批量嵌入實驗文本文件
    """
    vectorstore = get_chroma_instance("experiment")
    texts, metadatas = [], []

    for path in txt_paths:
        if not path.endswith(".txt"):
            continue
        exp_id = os.path.splitext(os.path.basename(path))[0]
        
        absolute_path = path
        if not os.path.isabs(path):
            current_dir = os.getcwd()
            if os.path.basename(current_dir) == "backend":
                project_root = os.path.dirname(os.path.dirname(current_dir))
                absolute_path = os.path.join(project_root, path)
            else:
                absolute_path = os.path.abspath(path)

        if not os.path.exists(absolute_path):
            print(f"❌ 文件不存在: {absolute_path}")
            continue
            
        try:
            with open(absolute_path, "r", encoding="utf-8") as f:
                content = f.read().strip()
            if len(content) < 10:
                continue
            texts.append(content)
            metadatas.append({"type": "experiment", "exp_id": exp_id, "filename": os.path.basename(path)})
        except Exception as e:
            print(f"❌ 讀取文件失敗 {path}: {e}")
            continue

    if not texts:
        if status_callback:
            status_callback("⚠️ 沒有新的實驗摘要可嵌入")
        return

    try:
        vectorstore.add_texts(texts=texts, metadatas=metadatas)
    except Exception as e:
        print(f"❌ 實驗數據嵌入失敗: {e}")
        if status_callback:
            status_callback(f"❌ 實驗數據嵌入失敗: {e}")
        return

    if status_callback:
        status_callback(f"✅ 嵌入完成，共 {len(texts)} 筆實驗摘要")


def get_vectorstore(vectorstore_type: str = "paper"):
    return get_chroma_instance(vectorstore_type)


def validate_embedding_model():
    try:
        get_embedding_model_instance()
        print(f"✅ 嵌入模型驗證成功：{EMBEDDING_MODEL_NAME}")
        return True
    except Exception as e:
        print(f"❌ 嵌入模型驗證失敗：{e}")
        return False


def get_vectorstore_stats(vectorstore_type: str = "paper"):
    try:
        vectorstore = get_chroma_instance(vectorstore_type)
        docs = vectorstore.get(include=["documents", "metadatas"])
        
        if vectorstore_type == "paper":
            vector_dir = os.path.join(VECTOR_INDEX_DIR, "paper_vector")
            collection_name = "paper"
        else:
            vector_dir = os.path.join(VECTOR_INDEX_DIR, "experiment_vector")
            collection_name = "experiment"
        
        return {
            "total_documents": len(docs["documents"]),
            "collection_name": collection_name,
            "vector_dir": vector_dir
        }
    except Exception as e:
        print(f"❌ 獲取統計信息失敗：{e}")
        return {"error": str(e)}

if __name__ == "__main__":
    print("🧪 開始測試嵌入功能...")
    if validate_embedding_model():
        print("✅ 嵌入模型驗證通過")
        paper_stats = get_vectorstore_stats("paper")
        experiment_stats = get_vectorstore_stats("experiment")
        print("📊 向量數據庫統計：")
        print(f"  文獻向量庫：{paper_stats}")
        print(f"  實驗向量庫：{experiment_stats}")
    else:
        print("❌ 嵌入模型驗證失敗")