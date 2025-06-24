import os
import pickle
import shutil
from datetime import datetime
from pathlib import Path
from tqdm import tqdm
from sentence_transformers import SentenceTransformer
from langchain.text_splitter import RecursiveCharacterTextSplitter
from chromadb import Client
from chromadb.config import Settings
from config import VECTOR_INDEX_DIR
from pdf_read_and_chunk_page_get import load_and_parse_file, get_page_number_for_chunk
from langchain_community.vectorstores import Chroma
from langchain.docstore.document import Document
from langchain_community.embeddings import HuggingFaceEmbeddings

def embed_documents_from_metadata(metadata_list):
    # 文字切割器
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
        separators=["\n\n", "\n", ".", "。", " ", ""]
    )

    
    
    # 整理要嵌入的文字與對應 metadata
    texts, metadatas = [], []
    for metadata in tqdm(metadata_list, desc="📚 Chunking & Metadata"):
        doc_type = metadata["type"]
        title = metadata.get("title", "")
        tracing_number = metadata.get("tracing_number")
        filename = metadata["new_filename"]
        file_path = metadata["new_path"]

        doc_chunks = load_and_parse_file(file_path)
        for i, chunk in enumerate(splitter.split_text(doc_chunks)):
            page_num = get_page_number_for_chunk(file_path, chunk)
            texts.append(chunk)
            metadatas.append({
                "title": title,
                "type": doc_type,
                "tracing_number": tracing_number,
                "filename": filename,
                "chunk_index": i,
                "page_number": page_num
            })

    print("📡 嵌入中...")
    embedding_model = HuggingFaceEmbeddings(
    model_name="nomic-ai/nomic-embed-text-v1.5",
    model_kwargs={"trust_remote_code": True}
    )


    # 🛡 備份原有資料
    if os.path.exists(VECTOR_INDEX_DIR) and os.listdir(VECTOR_INDEX_DIR):
        backup_dir = Path(VECTOR_INDEX_DIR) / "backups" / datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir.mkdir(parents=True, exist_ok=True)
        for fname in ["chroma.sqlite3", "embedding_cache.pkl"]:
            fpath = Path(VECTOR_INDEX_DIR) / fname
            if fpath.exists():
                shutil.copy2(fpath, backup_dir / fname)
        print(f"🛡 已備份原有向量資料庫至 {backup_dir}")

    # ✅ 使用累積式 Chroma
    chroma_client = Client(Settings(persist_directory=VECTOR_INDEX_DIR))
    collection = chroma_client.get_or_create_collection("default")

    # 準備 Document 對象（包含 metadata）
    documents = [
        Document(page_content=text, metadata=meta)
        for text, meta in zip(texts, metadatas)
    ]

    # 建立 Chroma vector store 並持久化
    vectorstore = Chroma.from_documents(
        documents=documents,
        embedding=embedding_model,
        persist_directory=VECTOR_INDEX_DIR,
        collection_name="default"
    )

    vectorstore.persist()

    with open(os.path.join(VECTOR_INDEX_DIR, "embedding_cache.pkl"), "wb") as f:
        pickle.dump((texts, metadatas), f)

    print(f"✅ 嵌入完成，共新增 {len(texts)} 段")
