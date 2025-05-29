import os
import pandas as pd
from dotenv import load_dotenv
from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings
from langchain.chat_models import ChatOpenAI

# === 環境與路徑設定 ===
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("⚠️ 請在 .env 檔中設定 OPENAI_API_KEY")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INDEX_DIR = os.path.join(BASE_DIR, "..", "experiment_data", "vector_index")
EXPERIMENT_DIR = os.path.join(BASE_DIR, "..", "experiment_data", "itri_experiment")

# === 載入所有實驗紀錄 CSV ===
def load_experiment_log():
    if not os.path.exists(EXPERIMENT_DIR):
        print(f"⚠️ 找不到資料夾：{EXPERIMENT_DIR}")
        return pd.DataFrame()

    csv_files = [f for f in os.listdir(EXPERIMENT_DIR) if f.endswith(".csv")]
    if not csv_files:
        print(f"⚠️ 沒有找到任何 CSV 檔案於：{EXPERIMENT_DIR}")
        return pd.DataFrame()

    all_dfs = []
    for file in csv_files:
        file_path = os.path.join(EXPERIMENT_DIR, file)
        try:
            df = pd.read_csv(file_path)
            all_dfs.append(df)
            print(f"📄 已載入：{file}")
        except Exception as e:
            print(f"❌ 無法讀取 {file}：{e}")

    if all_dfs:
        combined_df = pd.concat(all_dfs, ignore_index=True)
        print(f"✅ 已合併 {len(all_dfs)} 份實驗紀錄，共 {len(combined_df)} 筆資料。")
        return combined_df
    else:
        return pd.DataFrame()

# === 組合提示文字 ===
def build_prompt(question, context, experiment_df):
    past_experiments = experiment_df.head(10).to_string(index=False) if not experiment_df.empty else "（目前無資料）"

    return f"""你是一位研究助理，以下是系統彙整的文獻段落與實驗紀錄摘要，請根據此資訊回答下列研究問題：
--- 文獻摘要 ---
{context}

--- 實驗紀錄（前幾筆） ---
{past_experiments}

--- 問題 ---
{question}

請條列式回應建議，若資料中出現相似條件請指出，並給出可能的下一步實驗方向。
"""

# === 回答主流程 ===
def ask_agent(question, experiment_df):
    embeddings = OpenAIEmbeddings()
    db = Chroma(persist_directory=INDEX_DIR, embedding_function=embeddings)
    retriever = db.as_retriever(search_kwargs={"k": 5})
    context_docs = retriever.get_relevant_documents(question)
    context = "\n---\n".join([doc.page_content for doc in context_docs])
    prompt = build_prompt(question, context, experiment_df)
    llm = ChatOpenAI(model="gpt-4")
    response = llm.predict(prompt)
    return response

# === 主執行區 ===
if __name__ == "__main__":
    experiment_df = load_experiment_log()
    print("🤖 AI 研究助理啟動，請輸入你的研究問題（輸入 exit 離開）：\n")
    while True:
        q = input("🔎 問題：")
        if q.strip().lower() == "exit":
            print("👋 已離開助理。")
            break
        answer = ask_agent(q, experiment_df)
        print("\n📘 回答：\n", answer)