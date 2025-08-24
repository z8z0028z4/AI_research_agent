
import os
import re
import shutil
# 直接定義配置變量，避免循環導入
PAPER_DIR = "experiment_data/papers"
from html import unescape

def sanitize_filename(name, max_length=100):
    name = unescape(name)  # 轉換 HTML 實體，例如 &lt; → <
    name = re.sub(r'<[^>]+>', '', name)  # 移除 HTML 標籤
    name = re.sub(r'[^a-zA-Z0-9\-_ ]', '', name)  # 移除非法字元
    name = name.strip().replace(' ', '_')
    return name[:max_length]

def generate_tracing_number(existing_filenames):
    numbers = []
    for f in existing_filenames:
        match = re.match(r'(\d+)_', f)
        if match:
            try:
                numbers.append(int(match.group(1)))
            except ValueError:
                continue
    next_number = max(numbers, default=0) + 1
    return f"{next_number:03d}"

def rename_and_copy_file(original_path: str, metadata: dict) -> dict:
    # 確保使用絕對路徑
    if not os.path.isabs(original_path):
        original_path = os.path.abspath(original_path)
    
    # 確保 PAPER_DIR 使用絕對路徑
    if not os.path.isabs(PAPER_DIR):
        current_dir = os.getcwd()
        if os.path.basename(current_dir) == "backend":
            # 如果在 backend 目錄，向上兩級到項目根目錄
            project_root = os.path.dirname(os.path.dirname(current_dir))
            if os.path.basename(project_root) == "AI_research_agent":
                paper_dir = os.path.join(project_root, PAPER_DIR)
            else:
                # 如果不在正確的項目結構中，嘗試其他方法
                parent_dir = os.path.dirname(current_dir)
                if os.path.exists(os.path.join(parent_dir, "experiment_data")):
                    paper_dir = os.path.join(parent_dir, PAPER_DIR)
                else:
                    paper_dir = os.path.abspath(PAPER_DIR)
        else:
            paper_dir = os.path.abspath(PAPER_DIR)
    else:
        paper_dir = PAPER_DIR
    
    os.makedirs(paper_dir, exist_ok=True)

    # 取得追蹤編號
    existing_files = os.listdir(paper_dir)
    tracing_number = generate_tracing_number(existing_files)

    # 組合新檔名
    title_snippet = sanitize_filename(metadata.get("title", "")[:80])
    file_ext = os.path.splitext(original_path)[1].lower()
    doc_type = metadata.get("type", "").upper()
    new_filename = f"{tracing_number}_{title_snippet}_{doc_type}{file_ext}".replace("__", "_")
    new_path = os.path.join(paper_dir, new_filename)

    # ✅ 複製檔案（保留原始路徑的檔案）
    try:
        shutil.copyfile(original_path, new_path)
    except Exception as e:
        print(f"❌ 複製文件失敗 {original_path} -> {new_path}: {e}")
        raise

    # 更新 metadata
    metadata["tracing_number"] = tracing_number
    metadata["new_filename"] = new_filename
    
    # 在 metadata 中保存相對路徑，保持靈活性
    metadata["new_path"] = os.path.join("experiment_data", "papers", new_filename)

    return metadata

