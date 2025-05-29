import os
import fitz
import docx
from dotenv import load_dotenv
from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("⚠️ 請在 .env 檔案中設定 OPENAI_API_KEY")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "..", "experiment_data", "papers")
INDEX_DIR = os.path.join(BASE_DIR, "..", "experiment_data", "vector_index")

def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    return "\n".join([page.get_text() for page in doc])

def extract_text_from_docx(docx_path):
    doc = docx.Document(docx_path)
    return "\n".join([para.text for para in doc.paragraphs if para.text.strip()])

def embed_documents():
    embeddings = OpenAIEmbeddings()
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    documents = []

    print(f"📂 掃描資料夾：{DATA_DIR}")
    for filename in os.listdir(DATA_DIR):
        filepath = os.path.join(DATA_DIR, filename)

        if filename.endswith(".pdf"):
            print(f"🔍 讀取 PDF：{filename}")
            text = extract_text_from_pdf(filepath)
        elif filename.endswith(".docx"):
            print(f"🔍 讀取 Word：{filename}")
            text = extract_text_from_docx(filepath)
        else:
            print(f"⚠️ 忽略不支援的檔案格式：{filename}")
            continue

        chunks = text_splitter.create_documents([text])
        documents.extend(chunks)

    if documents:
        db = Chroma.from_documents(documents, embeddings, persist_directory=INDEX_DIR)
        db.persist()
        print(f"✅ 嵌入完成並儲存至：{INDEX_DIR}")
    else:
        print("⚠️ 沒有可用的文檔建立語意嵌入。")

if __name__ == "__main__":
    embed_documents()