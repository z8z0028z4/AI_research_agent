import argparse
import os

def run_gui():
    os.system("streamlit run research_gui.py")

def run_cli():
    from knowledge_agent import load_experiment_log, agent_answer
    df = load_experiment_log()
    print("🧠 CLI 研究助理啟動，輸入問題（輸入 exit 離開）")
    while True:
        q = input("🔎 問題：")
        if q.strip().lower() == "exit":
            break
        print("📡 回答中...\n")
        result = agent_answer(q, df)
        print("📘 回答：\n", result)
        print("—" * 40)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AI 研究助理啟動器")
    parser.add_argument("--mode", choices=["gui", "cli"], default="gui", help="選擇執行模式")
    args = parser.parse_args()

    if args.mode == "gui":
        run_gui()
    else:
        run_cli()