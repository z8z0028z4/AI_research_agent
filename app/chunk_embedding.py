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

from config import VECTOR_INDEX_DIR, EMBEDDING_MODEL_NAME
from langchain.text_splitter import RecursiveCharacterTextSplitter
from pdf_read_and_chunk_page_get import load_and_parse_file, get_page_number_for_chunk
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from tqdm import tqdm
import os
from typing import List
import torch

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
    # ==================== 文本分割器配置 ====================
    # 配置文本分割參數
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,        # 每個塊的最大字符數
        chunk_overlap=50,      # 塊之間的重疊字符數
        separators=["\n\n", "\n", ".", "。", " ", ""]  # 分割符號優先級
    )
    
    texts, metadatas = [], []

    # ==================== 文檔處理循環 ====================
    # 使用tqdm顯示進度條
    for metadata in tqdm(metadata_list, desc="📚 分塊和元數據處理"):
        # 提取文檔基本信息
        doc_type = metadata.get("type", "")
        title = metadata.get("title", "")
        tracing_number = metadata.get("tracing_number", "")
        filename = metadata["new_filename"]
        file_path = metadata["new_path"]

        # 讀取和解析文檔
        doc_chunks = load_and_parse_file(file_path)
        
        # 對文檔進行分塊處理
        for i, chunk in enumerate(splitter.split_text(doc_chunks)):
            # 過濾過短的文本塊
            if len(chunk.strip()) < 10:
                continue
                
            # 獲取頁碼信息
            page_num = get_page_number_for_chunk(file_path, chunk)
            
            # 添加到處理列表
            texts.append(chunk)
            metadatas.append({
                "title": title,
                "type": doc_type,
                "tracing_number": tracing_number,
                "filename": filename,
                "chunk_index": i,
                "page_number": page_num
            })

    print("📡 開始向量嵌入...")
    
    # ==================== 嵌入模型初始化 ====================
    # 使用HuggingFace嵌入模型
    embedding_model = HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL_NAME,
        model_kwargs={
            "trust_remote_code": True,
            "device": device,  # 使用GPU或CPU
        }
    )
    
    # ==================== 向量數據庫配置 ====================
    # 配置Chroma向量數據庫
    experiment_vector_dir = os.path.join(VECTOR_INDEX_DIR, "paper_vector")
    vectorstore = Chroma(
        persist_directory=experiment_vector_dir,
        embedding_function=embedding_model, 
        collection_name="paper"
    )

    # ==================== 批量向量化處理 ====================
    # 使用批量處理提高效率
    BATCH_SIZE = 500
    for i in range(0, len(texts), BATCH_SIZE):
        batch_texts = texts[i:i+BATCH_SIZE]
        batch_metadatas = metadatas[i:i+BATCH_SIZE]
        vectorstore.add_texts(texts=batch_texts, metadatas=batch_metadatas)
    
    # ==================== 持久化存儲 ====================
    # Chroma 0.4.x 版本後會自動持久化，不需要手動調用 persist()
    # vectorstore.persist()  # 已棄用，自動持久化
    
    # ==================== 統計信息 ====================
    doc_stats = vectorstore.get(include=["documents"])
    print("📦 向量庫目前共包含：", len(doc_stats["documents"]), "段")

    # ==================== 驗證嵌入結果 ====================
    # 驗證新添加的文檔是否真的被存儲
    try:
        # 嘗試檢索一個新添加的文檔來驗證
        if texts:
            test_query = texts[0][:50]  # 使用第一個文檔的前50個字符作為測試查詢
            test_results = vectorstore.similarity_search(test_query, k=1)
            if test_results:
                print("✅ 嵌入驗證成功：可以檢索到新添加的文檔")
            else:
                print("⚠️ 嵌入驗證失敗：無法檢索到新添加的文檔")
    except Exception as e:
        print(f"⚠️ 嵌入驗證時出現錯誤：{e}")

    # ==================== 進度回調 ====================
    if status_callback:
        status_callback(f"✅ 嵌入完成，共新增 {len(texts)} 段")

    # ==================== 詳細統計 ====================
    print("📊 嵌入段落統計：")
    for i, text in enumerate(texts[:10]):
        preview = text[:80].replace("\n", " ")
        print(f"Chunk {i+1} | 長度: {len(text)} | 頭部: {preview}")


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
    
    # ==================== 嵌入模型初始化 ====================
    embedding_model = HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL_NAME,
        model_kwargs={
            "trust_remote_code": True,
            "device": device
        }
    )
    
    # ==================== 實驗向量數據庫配置 ====================
    # 使用專門的實驗向量存儲目錄
    experiment_vector_dir = os.path.join(VECTOR_INDEX_DIR, "experiment_vector")
    vectorstore = Chroma(
        persist_directory=experiment_vector_dir, 
        embedding_function=embedding_model, 
        collection_name="experiment"
    )

    texts, metadatas = [], []

    # ==================== 文件處理循環 ====================
    for path in txt_paths:
        # 只處理TXT文件
        if not path.endswith(".txt"):
            continue
            
        # 提取實驗ID（文件名不含擴展名）
        exp_id = os.path.splitext(os.path.basename(path))[0]

        # 讀取文件內容
        with open(path, "r", encoding="utf-8") as f:
            content = f.read().strip()
            
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
    vectorstore.add_texts(texts=texts, metadatas=metadatas)
    # vectorstore.persist()  # 已棄用，自動持久化

    # ==================== 統計信息 ====================
    docs = vectorstore.get(include=["documents"])
    print("📦 向量數量：", len(docs["documents"]))

    # ==================== 進度回調 ====================
    if status_callback:
        status_callback(f"✅ 嵌入完成，共 {len(texts)} 筆實驗摘要")

    # ==================== 詳細預覽 ====================
    print("📊 本次嵌入預覽：")
    for i, t in enumerate(texts[:5]):
        print(f"#{i+1} | {metadatas[i]['exp_id']} | 頭 80 字：{t[:80].replace(chr(10), ' ')}")


# ==================== 輔助函數 ====================

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
            
        vectorstore = Chroma(
            persist_directory=vector_dir,
            embedding_function=embedding_model,
            collection_name=collection_name
        )
        
        docs = vectorstore.get(include=["documents", "metadatas"])
        
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

