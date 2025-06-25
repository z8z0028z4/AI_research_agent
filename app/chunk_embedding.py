from config import VECTOR_INDEX_DIR, EMBEDDING_MODEL_NAME
from langchain.text_splitter import RecursiveCharacterTextSplitter
from pdf_read_and_chunk_page_get import load_and_parse_file, get_page_number_for_chunk
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from tqdm import tqdm

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
        model_kwargs={"trust_remote_code": True}
    )
    vectorstore = Chroma(persist_directory=VECTOR_INDEX_DIR, embedding_function=embedding_model)

    BATCH_SIZE = 500
    for i in range(0, len(texts), BATCH_SIZE):
        batch_texts = texts[i:i+BATCH_SIZE]
        batch_metadatas = metadatas[i:i+BATCH_SIZE]
        vectorstore.add_texts(texts=batch_texts, metadatas=batch_metadatas)

    if status_callback:
        status_callback(f"✅ 嵌入完成，共新增 {len(texts)} 段")

    print("📊 嵌入段落統計：")
    for i, text in enumerate(texts[:10]):
        preview = text[:80].replace("\n", " ")
        print(f"Chunk {i+1} | 長度: {len(text)} | 頭部: {preview}")