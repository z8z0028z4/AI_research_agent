from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from config import VECTOR_INDEX_DIR

# 設定嵌入模型（要跟 summarize_and_embed.py 相同）
embedding_model = HuggingFaceEmbeddings(
    model_name="nomic-ai/nomic-embed-text-v1.5",
    model_kwargs={"trust_remote_code": True}
)

# 載入 vectorstore
vectorstore = Chroma(
    persist_directory=VECTOR_INDEX_DIR,
    embedding_function=embedding_model,
    collection_name="default"
)

# 搜尋測試問題
query = "fiber sorbent MOF conversion"
docs = vectorstore.similarity_search(query, k=5)

# 印出結果
if not docs:
    print("❌ 沒有抓到任何段落。")
else:
    print(f"✅ 找到 {len(docs)} 筆段落：\n")
    for i, doc in enumerate(docs, 1):
        meta = doc.metadata
        print(f"--- Chunk {i} ---")
        print(f"📄 {meta.get('title', 'N/A')} | Page {meta.get('page_number', '?')}")
        print(doc.page_content[:500])
        print()
