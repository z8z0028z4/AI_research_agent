from config import VECTOR_INDEX_DIR, EMBEDDING_MODEL_NAME
from langchain.text_splitter import RecursiveCharacterTextSplitter
from pdf_read_and_chunk_page_get import load_and_parse_file, get_page_number_for_chunk
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from tqdm import tqdm
import os
from typing import List
import torch

device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"🚀 嵌入模型使用設備：{device.upper()}")

def embed_documents_from_metadata(metadata_list, status_callback=None):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
        separators=["\n\n", "\n", ".", "。", " ", ""]
    )
    texts, metadatas = [], []

    for metadata in tqdm(metadata_list, desc="📚 Chunking & Metadata"):
        doc_type = metadata.get("type", "")
        title = metadata.get("title", "")
        tracing_number = metadata.get("tracing_number", "")
        filename = metadata["new_filename"]
        file_path = metadata["new_path"]

        doc_chunks = load_and_parse_file(file_path)
        for i, chunk in enumerate(splitter.split_text(doc_chunks)):
            if len(chunk.strip()) < 10:
                continue
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
        model_name=EMBEDDING_MODEL_NAME,
        model_kwargs={
            "trust_remote_code": True,
            "device": device,
        }
    )
    
    experiment_vector_dir = os.path.join(VECTOR_INDEX_DIR, "paper_vector")
    vectorstore = Chroma(
        persist_directory=experiment_vector_dir,
        embedding_function=embedding_model, 
        collection_name="paper"
        )

    BATCH_SIZE = 500
    for i in range(0, len(texts), BATCH_SIZE):
        batch_texts = texts[i:i+BATCH_SIZE]
        batch_metadatas = metadatas[i:i+BATCH_SIZE]
        vectorstore.add_texts(texts=batch_texts, metadatas=batch_metadatas)
    
    vectorstore.persist()  # ✅ 加這行才會寫入 collection
    doc_stats = vectorstore.get(include=["documents"])
    print("📦 向量庫目前共包含：", len(doc_stats["documents"]), "段")

    if status_callback:
        status_callback(f"✅ 嵌入完成，共新增 {len(texts)} 段")

    print("📊 嵌入段落統計：")
    for i, text in enumerate(texts[:10]):
        preview = text[:80].replace("\n", " ")
        print(f"Chunk {i+1} | 長度: {len(text)} | 頭部: {preview}")


def embed_experiment_txt_batch(txt_paths: List[str], status_callback=None):
    """
    將指定清單中的 txt 檔案嵌入（不遍歷整個資料夾）
    每個 txt 為一個 chunk，exp_id 為檔名（無副檔名）
    """

    embedding_model = HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL_NAME,
        model_kwargs={"trust_remote_code": True,
                      "device": device
        }
    
    )
    experiment_vector_dir = os.path.join(VECTOR_INDEX_DIR, "experiment_vector")
    vectorstore = Chroma(
        persist_directory=experiment_vector_dir, 
        embedding_function=embedding_model, 
        collection_name="experiment"
        )

    texts, metadatas = [], []

    for path in txt_paths:
        if not path.endswith(".txt"):
            continue
        exp_id = os.path.splitext(os.path.basename(path))[0]

        with open(path, "r", encoding="utf-8") as f:
            content = f.read().strip()
        if len(content) < 10:
            continue

        texts.append(content)
        metadatas.append({
            "type": "experiment",
            "exp_id": exp_id,
            "filename": os.path.basename(path),
        })

    if not texts:
        if status_callback:
            status_callback("⚠️ 沒有新的實驗摘要可嵌入")
        return

    vectorstore.add_texts(texts=texts, metadatas=metadatas)
    vectorstore.persist()  # ✅ 加這行才會寫入 collection

    docs = vectorstore.get(include=["documents"])
    print("📦 向量數量：", len(docs["documents"]))

    if status_callback:
        status_callback(f"✅ 嵌入完成，共 {len(texts)} 筆實驗摘要")

    print("📊 本次嵌入 preview：")
    for i, t in enumerate(texts[:5]):
        print(f"#{i+1} | {metadatas[i]['exp_id']} | 頭 80 字：{t[:80].replace(chr(10), ' ')}")

