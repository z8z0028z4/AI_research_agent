
import os
import re
import shutil
from config import PAPER_DIR
from html import unescape

def sanitize_filename(name, max_length=100):
    name = unescape(name)  # 轉換 HTML 實體，例如 &lt; → <
    name = re.sub(r'<[^>]+>', '', name)  # 移除 HTML 標籤
    name = re.sub(r'[^a-zA-Z0-9\-_ ]', '', name)  # 移除非法字元
    name = name.strip().replace(' ', '_')
    return name[:max_length]

def generate_tracing_number(existing_filenames):
    numbers = [
        int(re.match(r'(\d+)_', f).group(1))
        for f in existing_filenames
        if re.match(r'(\d+)_', f)
    ]
    next_number = max(numbers, default=0) + 1
    return f"{next_number:03d}"

def rename_and_copy_file(original_path: str, metadata: dict) -> dict:
    os.makedirs(PAPER_DIR, exist_ok=True)

    # 取得追蹤編號
    existing_files = os.listdir(PAPER_DIR)
    tracing_number = generate_tracing_number(existing_files)

    # 組合新檔名
    title_snippet = sanitize_filename(metadata.get("title", "")[:80])
    file_ext = os.path.splitext(original_path)[1].lower()
    doc_type = metadata.get("type", "").upper()
    new_filename = f"{tracing_number}_{title_snippet}_{doc_type}{file_ext}".replace("__", "_")
    new_path = os.path.join(PAPER_DIR, new_filename)

    # ✅ 複製檔案（保留原始路徑的檔案）
    shutil.copyfile(original_path, new_path)

    # 更新 metadata
    metadata["tracing_number"] = tracing_number
    metadata["new_filename"] = new_filename
    metadata["new_path"] = new_path

    return metadata

