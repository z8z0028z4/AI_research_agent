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

# Use a simple, stable model that doesn't require special configurations
# This model is lightweight and works well for multilingual text
DEFAULT_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

def get_working_model_name():
    """
    Get a working embedding model name with simplified approach
    """
    # Try to get from settings first
    try:
        from core.settings_manager import settings_manager
        model_from_settings = settings_manager.get_embedding_model()
        
        # List of models known to have issues with certain configurations
        problematic_models = [
            "paraphrase-multilingual-MiniLM-L12-v2",
            "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
        ]
        
        # If the model from settings is problematic, use default
        if any(prob in model_from_settings for prob in problematic_models):
            logger.warning(f"Model {model_from_settings} may have compatibility issues, using default model instead")
            return DEFAULT_MODEL
            
        return model_from_settings
    except Exception as e:
        logger.warning(f"Could not get model from settings: {e}, using default")
        return DEFAULT_MODEL

# Get model name
EMBEDDING_MODEL_NAME = get_working_model_name()

# 設備配置
device = "cuda" if torch.cuda.is_available() else "cpu"

# 全局 Chroma 實例緩存，避免重複創建
_chroma_instances = {}
_embedding_model_instance = None

def get_embedding_model_instance():
    """
    獲取或創建一個全局的嵌入模型實例
    使用最簡單的配置以避免兼容性問題
    """
    global _embedding_model_instance
    if _embedding_model_instance is None:
        try:
            logger.info(f"🚀 Loading embedding model: {EMBEDDING_MODEL_NAME} on device: {device}")
            
            # Use the simplest possible configuration
            # Avoid using sentence_transformers directly to prevent config issues
            _embedding_model_instance = HuggingFaceEmbeddings(
                model_name=EMBEDDING_MODEL_NAME,
                model_kwargs={
                    'device': device,
                    # Don't use trust_remote_code to avoid custom configs
                },
                encode_kwargs={
                    'normalize_embeddings': True,
                    'batch_size': 32
                }
            )
            
            # Test the model
            try:
                test_embedding = _embedding_model_instance.embed_query("test embedding")
                logger.info(f"✅ Model loaded successfully, embedding dimension: {len(test_embedding)}")
            except Exception as test_error:
                logger.error(f"Model test failed: {test_error}")
                # Fall back to a very basic configuration
                logger.info("Trying minimal configuration...")
                _embedding_model_instance = HuggingFaceEmbeddings(
                    model_name=DEFAULT_MODEL,
                    model_kwargs={'device': 'cpu'}
                )
                test_embedding = _embedding_model_instance.embed_query("test")
                logger.info(f"✅ Fallback model loaded, dimension: {len(test_embedding)}")
                
        except Exception as e:
            logger.error(f"Failed to load embedding model: {e}")
            # Last resort: use the most basic model
            logger.info(f"Using absolute fallback model: {DEFAULT_MODEL}")
            try:
                # Clear any cached models that might be causing issues
                import shutil
                cache_dir = os.path.expanduser("~/.cache/huggingface/hub")
                problem_dirs = [
                    "models--sentence-transformers--paraphrase-multilingual-MiniLM-L12-v2",
                ]
                for prob_dir in problem_dirs:
                    prob_path = os.path.join(cache_dir, prob_dir)
                    if os.path.exists(prob_path):
                        logger.info(f"Removing problematic cache: {prob_path}")
                        try:
                            shutil.rmtree(prob_path)
                        except:
                            pass
                
                # Now try with the default model
                _embedding_model_instance = HuggingFaceEmbeddings(
                    model_name=DEFAULT_MODEL,
                    model_kwargs={'device': 'cpu'},
                    encode_kwargs={'normalize_embeddings': True}
                )
                logger.info("✅ Default model loaded successfully")
            except Exception as final_error:
                logger.error(f"Could not load any embedding model: {final_error}")
                raise RuntimeError(
                    f"Failed to load embedding model. Please try:\n"
                    f"1. pip uninstall sentence-transformers transformers -y\n"
                    f"2. pip install sentence-transformers==2.2.2 transformers==4.36.0\n"
                    f"3. Clear cache: rmdir /s %USERPROFILE%\\.cache\\huggingface (Windows)\n"
                    f"Error: {final_error}"
                )
    
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
                settings=Settings(
                    anonymized_telemetry=False,
                    allow_reset=True,
                    is_persistent=True
                )
            )
            
            _chroma_instances[vectorstore_type] = Chroma(
                client=client,
                collection_name=collection_name,
                embedding_function=embedding_model
            )
            logger.info(f"✅ ChromaDB instance '{collection_name}' created successfully.")
            
        except Exception as e:
            logger.error(f"❌ Failed to create vector database '{vectorstore_type}': {e}")
            raise
    
    return _chroma_instances[vectorstore_type]


# ==================== 設備配置 ====================
# 自動檢測並使用GPU或CPU進行向量計算
print(f"🚀 Embedding model device: {device.upper()}")


def embed_documents_from_metadata(metadata_list, status_callback=None):
    """
    根據元數據列表嵌入文檔
    """
    start_time = time.time()
    logger.info(f"🚀 Starting vector embedding, total {len(metadata_list)} files")
    
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
        separators=["\n\n", "\n", ".", "。", " ", ""]
    )
    
    texts, metadatas = [], []

    if status_callback:
        status_callback("📚 Starting file chunking...")
    
    logger.info("📚 Starting file chunking...")
    for i, metadata in enumerate(metadata_list):
        filename = metadata.get("new_filename", metadata.get("original_filename", "unknown"))
        file_path = metadata.get("new_path", metadata.get("original_path"))
        
        if not file_path:
            logger.error(f"❌ Cannot get file path: {filename}")
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
            logger.error(f"❌ File does not exist: {absolute_path}")
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
                    "title": metadata.get("title", "Unknown Title"),
                    "type": metadata.get("type", "unknown"),
                    "tracing_number": metadata.get("tracing_number", "unknown"),
                    "page": page_num,
                    "chunk_index": j,
                    "total_chunks": len(chunks)
                })
        except Exception as e:
            logger.error(f"❌ Failed to process file {absolute_path}: {e}")
            continue
    
    if not texts:
        logger.warning("⚠️ No valid text chunks for embedding")
        return
    
    if status_callback:
        status_callback(f"🔢 Starting vector embedding, total {len(texts)} text chunks...")
    
    try:
        vectorstore = get_chroma_instance()
        batch_size = 100
        for i in range(0, len(texts), batch_size):
            batch_texts = texts[i:i + batch_size]
            batch_metadatas = metadatas[i:i + batch_size]
            vectorstore.add_texts(texts=batch_texts, metadatas=batch_metadatas)
            if status_callback:
                status_callback(f"🔢 Embedding batch {i//batch_size + 1}/{(len(texts) + batch_size - 1)//batch_size}...")
    except Exception as e:
        logger.error(f"❌ Vector embedding failed: {e}")
        if status_callback:
            status_callback(f"❌ Vector embedding failed: {e}")
        raise
    
    end_time = time.time()
    logger.info(f"🎉 Vector embedding completed, total time: {end_time - start_time:.2f} seconds")


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
            print(f"❌ File does not exist: {absolute_path}")
            continue
            
        try:
            with open(absolute_path, "r", encoding="utf-8") as f:
                content = f.read().strip()
            if len(content) < 10:
                continue
            texts.append(content)
            metadatas.append({"type": "experiment", "exp_id": exp_id, "filename": os.path.basename(path)})
        except Exception as e:
            print(f"❌ Failed to read file {path}: {e}")
            continue

    if not texts:
        if status_callback:
            status_callback("⚠️ No new experiment summaries to embed")
        return

    try:
        vectorstore.add_texts(texts=texts, metadatas=metadatas)
    except Exception as e:
        print(f"❌ Experiment data embedding failed: {e}")
        if status_callback:
            status_callback(f"❌ Experiment data embedding failed: {e}")
        return

    if status_callback:
        status_callback(f"✅ Embedding completed, total {len(texts)} experiment summaries")


def get_vectorstore(vectorstore_type: str = "paper"):
    return get_chroma_instance(vectorstore_type)


def validate_embedding_model():
    try:
        model = get_embedding_model_instance()
        test_embedding = model.embed_query("test embedding model 測試嵌入模型")
        print(f"✅ Embedding model validation successful: {EMBEDDING_MODEL_NAME}")
        print(f"   Vector dimension: {len(test_embedding)}")
        return True
    except Exception as e:
        print(f"❌ Embedding model validation failed: {e}")
        return False


def get_vectorstore_stats(vectorstore_type: str = "paper"):
    try:
        vectorstore = get_chroma_instance(vectorstore_type)
        
        # Try to get collection info
        try:
            collection = vectorstore._collection
            count = collection.count()
        except:
            # Fallback method
            docs = vectorstore.get(include=["metadatas"])
            count = len(docs["ids"]) if "ids" in docs else 0
        
        if vectorstore_type == "paper":
            vector_dir = os.path.join(VECTOR_INDEX_DIR, "paper_vector")
            collection_name = "paper"
        else:
            vector_dir = os.path.join(VECTOR_INDEX_DIR, "experiment_vector")
            collection_name = "experiment"
        
        return {
            "total_documents": count,
            "collection_name": collection_name,
            "vector_dir": vector_dir,
            "model": EMBEDDING_MODEL_NAME
        }
    except Exception as e:
        print(f"❌ Failed to get statistics: {e}")
        return {"error": str(e), "total_documents": 0}

if __name__ == "__main__":
    print("🧪 Starting embedding function test...")
    print(f"📦 Using model: {EMBEDDING_MODEL_NAME}")
    print(f"🖥️ Using device: {device.upper()}")
    
    if validate_embedding_model():
        print("✅ Embedding model validation passed")
        paper_stats = get_vectorstore_stats("paper")
        experiment_stats = get_vectorstore_stats("experiment")
        print("📊 Vector database statistics:")
        print(f"  Paper vector database: {paper_stats}")
        print(f"  Experiment vector database: {experiment_stats}")
    else:
        print("❌ Embedding model validation failed")