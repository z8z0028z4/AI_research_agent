from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
import os
from config import VECTOR_INDEX_DIR

print(f"🔍 載入向量資料庫： {VECTOR_INDEX_DIR}")

# 建立嵌入模型（與 summarize_and_embed.py 相同設定）
embedding_model = HuggingFaceEmbeddings(
    model_name="nomic-ai/nomic-embed-text-v1.5",
    model_kwargs={"trust_remote_code": True}
)

# 指定正確的 collection name（nomic）
vectorstore = Chroma(
    persist_directory=VECTOR_INDEX_DIR,
    embedding_function=embedding_model,
    collection_name="default"
)

# 印出 collection 確認資料庫是否載入
print(vectorstore._client.list_collections())

# 用 dummy 查詢獲取前幾筆資料
docs = vectorstore.similarity_search("test", k=3)

if not docs:
    print("⚠️ 尚未嵌入任何文件。")
else:
    print(f"✅ 共載入 {len(docs)} 筆嵌入文件。以下為前幾筆：\n")
    for i, doc in enumerate(docs, start=1):
        metadata = doc.metadata
        print(f"🔹 第 {i} 筆文件：")
        print(f"    📄 檔名: {metadata.get('filename', 'N/A')}")
        print(f"    📄 標題: {metadata.get('title', 'N/A')}")
        print(f"    📄 頁碼: {metadata.get('page_number', 'N/A')}")
        print(f"    📄 文字摘要: {doc.page_content[:100]}...\n")
