
import os
from metadata_extractor import extract_metadata
from semantic_lookup import lookup_semantic_scholar_metadata
from document_renamer import rename_and_copy_file
from metadata_registry import append_metadata_to_registry

def process_uploaded_files(file_paths: list, status_callback=None):
    valid_exts = [".pdf", ".docx"]
    file_paths = [
        path for path in file_paths
        if os.path.splitext(path)[1].lower() in valid_exts
    ]

    results = []

    for path in file_paths:
        filename = os.path.basename(path)

        if status_callback:
            status_callback(f"📄 抓取文件 `{filename}` 的 metadata 中...")

        metadata = extract_metadata(path)

        semantic_data = lookup_semantic_scholar_metadata(
            doi=metadata.get("doi", "") or None,
            title=metadata.get("title", "") or None
        )

        metadata.update({
            "title": semantic_data.get("title", metadata.get("title", "")),
            "authors": "; ".join(a["name"] for a in semantic_data.get("authors", [])),
            "year": semantic_data.get("year", ""),
            "venue": semantic_data.get("venue", ""),
            "url": semantic_data.get("url", "")
        })

        metadata = rename_and_copy_file(path, metadata)

        if status_callback:
            status_callback(f"📦 已複製 `{filename}` 至 papers 中，命名為 `{metadata['new_filename']}`")

        append_metadata_to_registry(metadata)

        if status_callback:
            status_callback(f"✅ 已寫入 metadata：{metadata['new_filename']}")

        print(f"✅ 完成：{metadata['new_filename']}")
        results.append(metadata)

    return results



if __name__ == "__main__":
    fake_test_file = "test_data/fake_paper.docx"
    try:
        result = process_uploaded_files([fake_test_file])
        print("✅ 測試完成")
        for r in result:
            print("📝 metadata：", r)
    except Exception as e:
        print("❌ 測試失敗：", e)
