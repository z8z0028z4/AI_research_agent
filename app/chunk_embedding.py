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

try:
    from core.settings_manager import settings_manager
    EMBEDDING_MODEL_NAME = settings_manager.get_embedding_model()
except (ImportError, AttributeError):
    EMBEDDING_MODEL_NAME = "BAAI/bge-small-zh-v1.5"


# 設備配置
device = "cuda" if torch.cuda.is_available() else "cpu"

# 全局 Chroma 實例緩存，避免重複創建
_chroma_instances = {}

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
            embedding_model = HuggingFaceEmbeddings(
                model_name=EMBEDDING_MODEL_NAME,
                model_kwargs={"trust_remote_code": True, "device": device}
            )
            
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
                path=vector_dir
            )
            
            _chroma_instances[vectorstore_type] = Chroma(
                client=client,
                collection_name=collection_name,
                embedding_function=embedding_model
            )
            
        except Exception as e:
            print(f"❌ 創建向量數據庫失敗：{e}")
            raise
    
    return _chroma_instances[vectorstore_type]


# ==================== 設備配置 ====================
# 自動檢測並使用GPU或CPU進行向量計算
device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"🚀 嵌入模型使用設備：{device.upper()}")


def embed_documents_from_metadata(metadata_list, status_callback=None):
    """
    根據元數據列表嵌入文檔
    
    功能：
    1. 讀取文檔並進行分塊處理
    2. 為每個文檔塊添加元數據
    3. 將文檔塊轉換為向量並存儲
    4. 提供進度回調和統計信息
    
    參數：
        metadata_list: 文檔元數據列表
        status_callback: 進度回調函數
    
    處理流程：
    1. 文本分割：將文檔分割為小塊
    2. 元數據提取：為每個塊添加標識信息
    3. 向量化：使用嵌入模型轉換為向量
    4. 存儲：保存到Chroma向量數據庫
    
    技術細節：
    - 使用遞歸字符分割器
    - 支持多種分隔符
    - 批量處理提高效率
    - 自動持久化存儲
    """
    start_time = time.time()
    logger.info(f"🚀 開始向量嵌入處理，共 {len(metadata_list)} 個文件")
    
    # ==================== 文本分割器配置 ====================
    # 配置文本分割參數
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,        # 每個塊的最大字符數
        chunk_overlap=50,      # 塊之間的重疊字符數
        separators=["\n\n", "\n", ".", "。", " ", ""]  # 分割符號優先級
    )
    
    texts, metadatas = [], []

    # ==================== 階段1: 文檔分塊處理 (40-70%) ====================
    if status_callback:
        status_callback("📚 開始文件分塊處理...")
    
    logger.info("📚 開始文件分塊處理...")
    chunking_start_time = time.time()
    
    # 使用tqdm顯示進度條
    for i, metadata in enumerate(metadata_list):
        file_start_time = time.time()
        filename = metadata.get("new_filename", metadata.get("original_filename", "unknown"))
        title = metadata.get("title", "未知標題")
        doc_type = metadata.get("type", "unknown")
        tracing_number = metadata.get("tracing_number", "unknown")
        
        logger.info(f"📄 處理第 {i+1}/{len(metadata_list)} 個文件: {filename}")
        logger.info(f"   📝 標題: {title}")
        logger.info(f"   🏷️ 類型: {doc_type}")
        logger.info(f"   🔢 追蹤號: {tracing_number}")
        
        # 獲取文件路徑
        file_path = metadata.get("new_path", metadata.get("original_path"))
        if not file_path:
            logger.error(f"❌ 無法獲取文件路徑: {filename}")
            continue
        
        # 轉換為絕對路徑
        if not os.path.isabs(file_path):
            # 如果是相對路徑，轉換為絕對路徑
            current_dir = os.getcwd()
            logger.info(f"   🔍 當前工作目錄: {current_dir}")
            logger.info(f"   🔍 相對路徑: {file_path}")
            
            # 檢查是否在backend目錄
            if os.path.basename(current_dir) == "backend":
                # 如果在backend目錄，向上兩級到項目根目錄
                project_root = os.path.dirname(os.path.dirname(current_dir))
                # 檢查項目根目錄是否正確
                if os.path.basename(project_root) == "AI_research_agent":
                    absolute_path = os.path.join(project_root, file_path)
                    logger.info(f"   🔍 backend目錄，項目根目錄: {project_root}")
                else:
                    # 如果不在正確的項目結構中，嘗試其他方法
                    # 檢查當前目錄的父目錄是否包含 experiment_data
                    parent_dir = os.path.dirname(current_dir)
                    if os.path.exists(os.path.join(parent_dir, "experiment_data")):
                        absolute_path = os.path.join(parent_dir, file_path)
                        logger.info(f"   🔍 使用父目錄: {parent_dir}")
                    else:
                        # 最後嘗試使用絕對路徑
                        absolute_path = os.path.abspath(file_path)
                        logger.info(f"   🔍 使用絕對路徑: {absolute_path}")
            else:
                # 在其他目錄，直接使用絕對路徑
                absolute_path = os.path.abspath(file_path)
                logger.info(f"   🔍 其他目錄，絕對路徑: {absolute_path}")
            
            file_path = absolute_path
        
        logger.info(f"   🔍 最終文件路徑: {file_path}")
        
        # 檢查文件是否存在
        if not os.path.exists(file_path):
            logger.error(f"❌ 文件不存在: {file_path}")
            # 嘗試列出目錄內容
            try:
                dir_path = os.path.dirname(file_path)
                if os.path.exists(dir_path):
                    files_in_dir = os.listdir(dir_path)
                    logger.info(f"   📁 目錄 {dir_path} 中的文件: {files_in_dir}")
                else:
                    logger.error(f"   ❌ 目錄不存在: {dir_path}")
            except Exception as e:
                logger.error(f"   ❌ 無法列出目錄內容: {e}")
            continue
        
        # 記錄文件大小
        file_size = os.path.getsize(file_path)
        logger.info(f"   📊 文件大小: {file_size} bytes")
        
        # 讀取文件內容
        try:
            read_start_time = time.time()
            doc_chunks = load_and_parse_file(file_path)
            read_end_time = time.time()
            logger.info(f"   ✅ 文件讀取完成，耗時: {read_end_time - read_start_time:.2f}秒")
            logger.info(f"   📄 原始文本長度: {len(doc_chunks)} 字符")
        except FileNotFoundError:
            logger.error(f"❌ 文件不存在: {file_path}")
            continue
        except Exception as e:
            logger.error(f"❌ 讀取文件失敗 {file_path}: {e}")
            continue
        
        # 對文檔進行分塊處理
        try:
            chunk_start_time = time.time()
            chunks = splitter.split_text(doc_chunks)
            chunk_end_time = time.time()
            logger.info(f"   ✅ 文本分塊完成，生成 {len(chunks)} 個文本塊，耗時: {chunk_end_time - chunk_start_time:.2f}秒")
            
            # 記錄分塊統計
            chunk_sizes = [len(chunk.strip()) for chunk in chunks]
            avg_chunk_size = sum(chunk_sizes) / len(chunk_sizes) if chunk_sizes else 0
            min_chunk_size = min(chunk_sizes) if chunk_sizes else 0
            max_chunk_size = max(chunk_sizes) if chunk_sizes else 0
            logger.info(f"   📊 分塊統計 - 平均: {avg_chunk_size:.1f}, 最小: {min_chunk_size}, 最大: {max_chunk_size} 字符")
            
        except Exception as e:
            logger.error(f"❌ 文本分塊失敗 {file_path}: {e}")
            continue
        
        if status_callback:
            status_callback(f"📚 分割文件為 {len(chunks)} 個文本塊...")
        
        valid_chunks = 0
        for j, chunk in enumerate(chunks):
            # 過濾過短的文本塊
            if len(chunk.strip()) < 10:
                logger.debug(f"   ⚠️ 跳過過短文本塊 {j+1}: {len(chunk.strip())} 字符")
                continue
                
            # 獲取頁碼信息
            try:
                page_num = get_page_number_for_chunk(file_path, chunk)
            except Exception as e:
                logger.warning(f"⚠️ 無法獲取頁碼信息 {file_path}: {e}")
                page_num = "?"
            
            # 添加到處理列表
            texts.append(chunk)
            metadatas.append({
                "source": filename,
                "title": title,
                "type": doc_type,
                "tracing_number": tracing_number,
                "page": page_num,
                "chunk_index": j,
                "total_chunks": len(chunks)
            })
            valid_chunks += 1
        
        file_end_time = time.time()
        logger.info(f"   ✅ 文件 {filename} 處理完成，有效文本塊: {valid_chunks}/{len(chunks)}，耗時: {file_end_time - file_start_time:.2f}秒")
        
        if status_callback:
            status_callback(f"✅ 完成文件 {filename} 的分塊處理")
    
    chunking_end_time = time.time()
    logger.info(f"✅ 所有文件分塊處理完成，總耗時: {chunking_end_time - chunking_start_time:.2f}秒")
    logger.info(f"📊 總共生成 {len(texts)} 個有效文本塊")
    
    # ==================== 階段2: 向量嵌入處理 (70-95%) ====================
    if not texts:
        logger.warning("⚠️ 沒有有效的文本塊進行嵌入")
        return
    
    if status_callback:
        status_callback(f"🔢 開始向量嵌入，共 {len(texts)} 個文本塊...")
    
    logger.info(f"🔢 開始向量嵌入，共 {len(texts)} 個文本塊")
    embedding_start_time = time.time()
    
    # 批量嵌入文本塊
    try:
        # 獲取向量數據庫實例
        logger.info("🔗 獲取向量數據庫實例...")
        vectorstore_start_time = time.time()
        vectorstore = get_chroma_instance()
        vectorstore_end_time = time.time()
        logger.info(f"✅ 向量數據庫實例獲取完成，耗時: {vectorstore_end_time - vectorstore_start_time:.2f}秒")
        
        # 分批處理向量嵌入，每批500個文本塊
        batch_size = 500
        total_batches = (len(texts) + batch_size - 1) // batch_size
        logger.info(f"📦 將分 {total_batches} 批進行向量嵌入，每批 {batch_size} 個文本塊")
        
        for batch_idx in range(total_batches):
            batch_start_time = time.time()
            start_idx = batch_idx * batch_size
            end_idx = min((batch_idx + 1) * batch_size, len(texts))
            
            batch_texts = texts[start_idx:end_idx]
            batch_metadatas = metadatas[start_idx:end_idx]
            
            logger.info(f"🔢 處理批次 {batch_idx + 1}/{total_batches} ({len(batch_texts)} 個文本塊)...")
            
            if status_callback:
                status_callback(f"🔢 向量嵌入批次 {batch_idx + 1}/{total_batches} ({len(batch_texts)} 個文本塊)...")
            
            # 批量添加文檔
            try:
                add_start_time = time.time()
                vectorstore.add_texts(texts=batch_texts, metadatas=batch_metadatas)
                add_end_time = time.time()
                logger.info(f"   ✅ 批次 {batch_idx + 1} 向量添加完成，耗時: {add_end_time - add_start_time:.2f}秒")
            except Exception as e:
                logger.error(f"❌ 批次 {batch_idx + 1} 向量添加失敗: {e}")
                raise
            
            batch_end_time = time.time()
            logger.info(f"   ✅ 批次 {batch_idx + 1}/{total_batches} 完成，耗時: {batch_end_time - batch_start_time:.2f}秒")
            
            if status_callback:
                progress_percent = 70 + int(((batch_idx + 1) / total_batches) * 25)  # 70-95%
                status_callback(f"✅ 完成批次 {batch_idx + 1}/{total_batches} 的向量嵌入")
        
        embedding_end_time = time.time()
        logger.info(f"✅ 所有批次向量嵌入完成，總耗時: {embedding_end_time - embedding_start_time:.2f}秒")
        
        if status_callback:
            status_callback(f"✅ 向量嵌入完成，共處理 {len(texts)} 個文本塊")
        
        print(f"✅ 向量嵌入完成，共處理 {len(texts)} 個文本塊")
        
    except Exception as e:
        logger.error(f"❌ 向量嵌入失敗: {e}")
        print(f"❌ 向量嵌入失敗: {e}")
        if status_callback:
            status_callback(f"❌ 向量嵌入失敗: {e}")
        raise
    
    end_time = time.time()
    total_time = end_time - start_time
    logger.info(f"🎉 向量嵌入處理完成，總耗時: {total_time:.2f}秒")
    logger.info(f"📊 處理統計 - 文件數: {len(metadata_list)}, 文本塊數: {len(texts)}, 平均每文件: {len(texts)/len(metadata_list):.1f} 塊")


def embed_experiment_txt_batch(txt_paths: List[str], status_callback=None):
    """
    批量嵌入實驗文本文件
    
    功能：
    1. 讀取指定的TXT文件列表
    2. 將每個文件作為一個完整的文檔塊
    3. 提取實驗ID作為標識符
    4. 批量向量化並存儲
    
    參數：
        txt_paths (List[str]): TXT文件路徑列表
        status_callback: 進度回調函數
    
    特點：
    - 每個TXT文件作為一個完整的實驗記錄
    - 使用文件名（不含擴展名）作為實驗ID
    - 專門用於實驗數據的向量化
    - 存儲到獨立的實驗向量數據庫
    
    技術細節：
    - 使用相同的嵌入模型確保一致性
    - 存儲到experiment_vector目錄
    - 集合名稱為"experiment"
    """
    
    # ==================== 獲取實驗向量數據庫實例 ====================
    vectorstore = get_chroma_instance("experiment")

    texts, metadatas = [], []

    # ==================== 文件處理循環 ====================
    for path in txt_paths:
        # 只處理TXT文件
        if not path.endswith(".txt"):
            continue
            
        # 提取實驗ID（文件名不含擴展名）
        exp_id = os.path.splitext(os.path.basename(path))[0]

        # 讀取文件內容
        try:
            # 將相對路徑轉換為絕對路徑進行文件讀取
            if not os.path.isabs(path):
                current_dir = os.getcwd()
                if os.path.basename(current_dir) == "backend":
                    # 如果在 backend 目錄，向上兩級到項目根目錄
                    project_root = os.path.dirname(os.path.dirname(current_dir))
                    if os.path.basename(project_root) == "AI_research_agent":
                        absolute_path = os.path.join(project_root, path)
                    else:
                        # 如果不在正確的項目結構中，嘗試其他方法
                        parent_dir = os.path.dirname(current_dir)
                        if os.path.exists(os.path.join(parent_dir, "experiment_data")):
                            absolute_path = os.path.join(parent_dir, path)
                        else:
                            absolute_path = os.path.abspath(path)
                else:
                    absolute_path = os.path.abspath(path)
            else:
                absolute_path = path
            
            # 檢查文件是否存在
            if not os.path.exists(absolute_path):
                print(f"❌ 文件不存在: {absolute_path}")
                continue
            
            with open(absolute_path, "r", encoding="utf-8") as f:
                content = f.read().strip()
        except Exception as e:
            print(f"❌ 讀取文件失敗 {path}: {e}")
            continue
            
        # 過濾過短的內容
        if len(content) < 10:
            continue

        # 添加到處理列表
        texts.append(content)
        metadatas.append({
            "type": "experiment",
            "exp_id": exp_id,
            "filename": os.path.basename(path),
        })

    # ==================== 驗證處理結果 ====================
    if not texts:
        if status_callback:
            status_callback("⚠️ 沒有新的實驗摘要可嵌入")
        return

    # ==================== 批量向量化 ====================
    try:
        vectorstore.add_texts(texts=texts, metadatas=metadatas)
        # vectorstore.persist()  # 已棄用，自動持久化
    except Exception as e:
        print(f"❌ 實驗數據嵌入失敗: {e}")
        if status_callback:
            status_callback(f"❌ 實驗數據嵌入失敗: {e}")
        return

    # ==================== 統計信息 ====================
    try:
        docs = vectorstore.get(include=["documents"])
        print("📦 向量數量：", len(docs["documents"]))
    except Exception as e:
        print(f"⚠️ 無法獲取實驗向量庫統計信息: {e}")
        docs = {"documents": []}

    # ==================== 進度回調 ====================
    if status_callback:
        status_callback(f"✅ 嵌入完成，共 {len(texts)} 筆實驗摘要")

    # ==================== 詳細預覽 ====================
    print("📊 本次嵌入預覽：")
    for i, t in enumerate(texts[:5]):
        try:
            print(f"#{i+1} | {metadatas[i]['exp_id']} | 頭 80 字：{t[:80].replace(chr(10), ' ')}")
        except Exception as e:
            print(f"#{i+1} | 預覽顯示失敗: {e}")


# ==================== 輔助函數 ====================

def get_vectorstore(vectorstore_type: str = "paper"):
    """
    獲取向量數據庫實例（已棄用，請使用 get_chroma_instance）
    
    功能：
    1. 獲取或創建指定的向量數據庫實例
    2. 使用緩存避免重複創建
    
    參數：
        vectorstore_type (str): 向量數據庫類型（"paper" 或 "experiment"）
    
    返回：
        Chroma: 向量數據庫實例
    """
    return get_chroma_instance(vectorstore_type)


def validate_embedding_model():
    """
    驗證嵌入模型是否可用
    
    功能：
    1. 檢查模型文件是否存在
    2. 測試模型加載
    3. 驗證設備配置
    
    返回：
        bool: 模型是否可用
    """
    try:
        embedding_model = HuggingFaceEmbeddings(
            model_name=EMBEDDING_MODEL_NAME,
            model_kwargs={"trust_remote_code": True, "device": device}
        )
        print(f"✅ 嵌入模型驗證成功：{EMBEDDING_MODEL_NAME}")
        return True
    except Exception as e:
        print(f"❌ 嵌入模型驗證失敗：{e}")
        return False


def get_vectorstore_stats(vectorstore_type: str = "paper"):
    """
    獲取向量數據庫統計信息
    
    功能：
    1. 連接指定的向量數據庫
    2. 獲取文檔數量統計
    3. 返回詳細的統計信息
    
    參數：
        vectorstore_type (str): 向量數據庫類型（"paper" 或 "experiment"）
    
    返回：
        Dict: 統計信息字典
    """
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


# ==================== 測試代碼 ====================
if __name__ == "__main__":
    """
    測試嵌入功能
    
    這個測試代碼用於驗證嵌入功能是否正常工作
    """
    print("🧪 開始測試嵌入功能...")
    
    # 驗證嵌入模型
    if validate_embedding_model():
        print("✅ 嵌入模型驗證通過")
        
        # 獲取統計信息
        paper_stats = get_vectorstore_stats("paper")
        experiment_stats = get_vectorstore_stats("experiment")
        
        print("📊 向量數據庫統計：")
        print(f"  文獻向量庫：{paper_stats}")
        print(f"  實驗向量庫：{experiment_stats}")
    else:
        print("❌ 嵌入模型驗證失敗")

