"""
AI 研究助理 - 文檔分塊和向量嵌入模塊 (OpenAI版本)
================================================

這個模塊負責將文檔轉換為向量表示，為RAG系統提供檢索基礎。
主要功能包括：
1. 文檔分塊和預處理
2. 文本向量化 (使用OpenAI Embeddings)
3. 向量數據庫存儲
4. 批量處理支持

架構說明：
- 使用LangChain的文本分割器
- 集成OpenAI嵌入模型
- 使用Chroma作為向量數據庫
- 支持批量處理以優化API調用

⚠️ 注意：此模塊使用OpenAI API，需要設置API密鑰
"""

import os
import sys
import time
import logging
from typing import List, Dict, Any, Optional
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
import chromadb
from chromadb.config import Settings
from pdf_read_and_chunk_page_get import load_and_parse_file, get_page_number_for_chunk

# 配置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ==================== 全局變量 ====================
# 配置路徑
VECTOR_INDEX_DIR = os.path.join(os.path.dirname(__file__), "..", "experiment_data", "vector_index")

# Add backend to path to import settings_manager
backend_path = os.path.join(os.path.dirname(__file__), "..", "backend")
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

# OpenAI配置
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    # Try to get from settings
    try:
        from core.settings_manager import settings_manager
        OPENAI_API_KEY = settings_manager.get_openai_api_key()
    except:
        logger.warning("⚠️ OpenAI API key not found in environment or settings")

# OpenAI嵌入模型選擇
# text-embedding-3-small: 便宜且快速，適合大多數用途
# text-embedding-3-large: 更高質量，但成本更高
# text-embedding-ada-002: 舊版本，但仍然穩定
EMBEDDING_MODEL_NAME = "text-embedding-3-small"

# 全局 Chroma 實例緩存，避免重複創建
_chroma_instances = {}
_embedding_model_instance = None

def get_embedding_model_instance():
    """
    獲取或創建一個全局的OpenAI嵌入模型實例
    
    Returns:
        OpenAIEmbeddings: OpenAI嵌入模型實例
    """
    global _embedding_model_instance
    if _embedding_model_instance is None:
        if not OPENAI_API_KEY:
            raise ValueError(
                "OpenAI API key not found! Please set it in one of these ways:\n"
                "1. Set environment variable: set OPENAI_API_KEY=your-key-here\n"
                "2. Add to .env file: OPENAI_API_KEY=your-key-here\n"
                "3. Add to settings.json: {\"openai_api_key\": \"your-key-here\"}\n"
                "Get your API key from: https://platform.openai.com/api-keys"
            )
        
        try:
            logger.info(f"🚀 Initializing OpenAI embedding model: {EMBEDDING_MODEL_NAME}")
            
            _embedding_model_instance = OpenAIEmbeddings(
                model=EMBEDDING_MODEL_NAME,
                openai_api_key=OPENAI_API_KEY,
                # Optional parameters for optimization
                chunk_size=1000,  # Process texts in chunks to avoid rate limits
                max_retries=3,     # Retry on failure
                show_progress_bar=False  # Set to True if you want to see progress
            )
            
            # Test the model
            try:
                test_embedding = _embedding_model_instance.embed_query("測試文本 test text")
                logger.info(f"✅ OpenAI embedding model loaded successfully, dimension: {len(test_embedding)}")
            except Exception as test_error:
                logger.error(f"❌ Model test failed: {test_error}")
                raise
                
        except Exception as e:
            logger.error(f"❌ Failed to load OpenAI embedding model: {e}")
            raise
    
    return _embedding_model_instance

def get_chroma_instance(vectorstore_type: str = "paper"):
    """
    獲取或創建 Chroma 實例（使用 ChromaDB 1.0+ 架構）
    
    參數：
        vectorstore_type (str): 向量數據庫類型（"paper" 或 "experiment"）
    
    返回：
        Chroma: 向量數據庫實例
    """
    if vectorstore_type not in _chroma_instances:
        try:
            embedding_model = get_embedding_model_instance()
            
            if vectorstore_type == "paper":
                vector_dir = os.path.join(VECTOR_INDEX_DIR, "paper_vector_openai")
                collection_name = "paper_openai"
            else:
                vector_dir = os.path.join(VECTOR_INDEX_DIR, "experiment_vector_openai")
                collection_name = "experiment_openai"
            
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
            logger.info(f"✅ ChromaDB instance '{collection_name}' created successfully with OpenAI embeddings.")
            
        except Exception as e:
            logger.error(f"❌ Failed to create vector database '{vectorstore_type}': {e}")
            raise
    
    return _chroma_instances[vectorstore_type]


def embed_documents_from_metadata(metadata_list, status_callback=None):
    """
    根據元數據列表嵌入文檔
    
    參數：
        metadata_list: 文檔元數據列表
        status_callback: 狀態回調函數
    """
    start_time = time.time()
    logger.info(f"🚀 Starting vector embedding process, total {len(metadata_list)} files")
    
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
        status_callback(f"🔢 Starting OpenAI embedding, total {len(texts)} text chunks...")
    
    try:
        vectorstore = get_chroma_instance()
        
        # OpenAI has rate limits, so we process in smaller batches
        batch_size = 20  # Smaller batch size for OpenAI API
        total_batches = (len(texts) + batch_size - 1) // batch_size
        
        for i in range(0, len(texts), batch_size):
            batch_texts = texts[i:i + batch_size]
            batch_metadatas = metadatas[i:i + batch_size]
            
            current_batch = i // batch_size + 1
            logger.info(f"Processing batch {current_batch}/{total_batches}")
            
            if status_callback:
                status_callback(f"🔢 Embedding batch {current_batch}/{total_batches}...")
            
            # Add texts with retry logic
            retry_count = 0
            max_retries = 3
            while retry_count < max_retries:
                try:
                    vectorstore.add_texts(texts=batch_texts, metadatas=batch_metadatas)
                    break
                except Exception as e:
                    retry_count += 1
                    if retry_count >= max_retries:
                        raise e
                    logger.warning(f"Retry {retry_count}/{max_retries} after error: {e}")
                    time.sleep(2 ** retry_count)  # Exponential backoff
            
            # Small delay to respect rate limits
            time.sleep(0.5)
            
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
    
    參數：
        txt_paths: 文本文件路徑列表
        status_callback: 狀態回調函數
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
            logger.error(f"❌ File does not exist: {absolute_path}")
            continue
            
        try:
            with open(absolute_path, "r", encoding="utf-8") as f:
                content = f.read().strip()
            if len(content) < 10:
                continue
            texts.append(content)
            metadatas.append({"type": "experiment", "exp_id": exp_id, "filename": os.path.basename(path)})
        except Exception as e:
            logger.error(f"❌ Failed to read file {path}: {e}")
            continue

    if not texts:
        if status_callback:
            status_callback("⚠️ No new experiment summaries to embed")
        return

    try:
        # Process in batches for OpenAI
        batch_size = 20
        for i in range(0, len(texts), batch_size):
            batch_texts = texts[i:i + batch_size]
            batch_metadatas = metadatas[i:i + batch_size]
            vectorstore.add_texts(texts=batch_texts, metadatas=batch_metadatas)
            time.sleep(0.5)  # Respect rate limits
            
    except Exception as e:
        logger.error(f"❌ Experiment data embedding failed: {e}")
        if status_callback:
            status_callback(f"❌ Experiment data embedding failed: {e}")
        return

    if status_callback:
        status_callback(f"✅ Embedding completed, total {len(texts)} experiment summaries")


def get_vectorstore(vectorstore_type: str = "paper"):
    """獲取向量數據庫實例"""
    return get_chroma_instance(vectorstore_type)


def validate_embedding_model():
    """驗證嵌入模型是否正常工作"""
    try:
        model = get_embedding_model_instance()
        test_embedding = model.embed_query("test embedding model 測試嵌入模型")
        print(f"✅ OpenAI embedding model validation successful: {EMBEDDING_MODEL_NAME}")
        print(f"   Vector dimension: {len(test_embedding)}")
        print(f"   API Key configured: {'Yes' if OPENAI_API_KEY else 'No'}")
        return True
    except Exception as e:
        print(f"❌ Embedding model validation failed: {e}")
        return False


def get_vectorstore_stats(vectorstore_type: str = "paper"):
    """獲取向量數據庫統計信息"""
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
            vector_dir = os.path.join(VECTOR_INDEX_DIR, "paper_vector_openai")
            collection_name = "paper_openai"
        else:
            vector_dir = os.path.join(VECTOR_INDEX_DIR, "experiment_vector_openai")
            collection_name = "experiment_openai"
        
        return {
            "total_documents": count,
            "collection_name": collection_name,
            "vector_dir": vector_dir,
            "model": EMBEDDING_MODEL_NAME,
            "provider": "OpenAI"
        }
    except Exception as e:
        logger.error(f"❌ Failed to get statistics: {e}")
        return {"error": str(e), "total_documents": 0}


def estimate_embedding_cost(num_tokens: int) -> float:
    """
    估算OpenAI嵌入成本
    
    參數：
        num_tokens: token數量
    
    返回：
        float: 預估成本（美元）
    """
    # OpenAI pricing (as of 2024)
    # text-embedding-3-small: $0.00002 per 1K tokens
    # text-embedding-3-large: $0.00013 per 1K tokens
    # text-embedding-ada-002: $0.00010 per 1K tokens
    
    pricing = {
        "text-embedding-3-small": 0.00002,
        "text-embedding-3-large": 0.00013,
        "text-embedding-ada-002": 0.00010
    }
    
    price_per_1k = pricing.get(EMBEDDING_MODEL_NAME, 0.00002)
    cost = (num_tokens / 1000) * price_per_1k
    return cost


if __name__ == "__main__":
    print("🧪 Starting OpenAI embedding function test...")
    print(f"📦 Using model: {EMBEDDING_MODEL_NAME}")
    print(f"🔑 API Key configured: {'Yes' if OPENAI_API_KEY else 'No'}")
    
    if not OPENAI_API_KEY:
        print("\n❌ OpenAI API key not configured!")
        print("Please set your API key using one of these methods:")
        print("1. Set environment variable: set OPENAI_API_KEY=your-key-here")
        print("2. Create .env file with: OPENAI_API_KEY=your-key-here")
        print("3. Add to settings.json")
        print("\nGet your API key from: https://platform.openai.com/api-keys")
    else:
        if validate_embedding_model():
            print("✅ Embedding model validation passed")
            
            # Estimate costs
            sample_text = "This is a sample text for cost estimation" * 10
            estimated_tokens = len(sample_text.split()) * 1.3  # Rough estimate
            cost = estimate_embedding_cost(int(estimated_tokens))
            print(f"💰 Estimated cost per 100 similar chunks: ${cost * 100:.4f}")
            
            paper_stats = get_vectorstore_stats("paper")
            experiment_stats = get_vectorstore_stats("experiment")
            print("\n📊 Vector database statistics:")
            print(f"  Paper vector database: {paper_stats}")
            print(f"  Experiment vector database: {experiment_stats}")
        else:
            print("❌ Embedding model validation failed")