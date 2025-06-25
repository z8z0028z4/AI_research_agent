import os
from dotenv import load_dotenv

# 載入 .env 檔案
load_dotenv()

# API 金鑰
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY")

# 專案路徑設定
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

# 資料目錄（知識庫與實驗）
VECTOR_INDEX_DIR = os.path.join(BASE_DIR, "experiment_data", "vector_index")
EXPERIMENT_CSV_DIR = os.path.join(BASE_DIR, "experiment_data", "experiment")
PAPER_DIR = os.path.join(BASE_DIR, "experiment_data", "papers")
REGISTRY_PATH = os.path.join(BASE_DIR, "experiment_data", "metadata_registry.xlsx")
EMBEDDING_MODEL_NAME = "nomic-ai/nomic-embed-text-v1.5"