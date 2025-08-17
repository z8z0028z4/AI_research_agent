# RAG Core 備份目錄

此目錄包含 RAG Core 重構前的原始文件和相關備份。

## 文件說明

- `original_rag_core.py`: 重構前的原始 rag_core.py 文件
- `fallback_removal_log.md`: 記錄移除的 fallback 機制
- `removed_functions.md`: 記錄移除的函數和功能

## 重構日期

2024年12月

## 重構目標

- 移除所有 GPT-4 支援
- 移除所有 fallback 機制
- 只保留 GPT-5 Responses API
- 只保留結構化輸出
- 模組化重構
