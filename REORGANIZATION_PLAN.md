# Repository 重組計劃

## 🎯 目標
將 `app/` 目錄整合到 `backend/` 中，建立更清晰的 React-based 架構

## 📋 重組步驟

### 階段 1: 創建新的目錄結構
```bash
# 在 backend/ 下創建新的目錄
mkdir -p backend/core
mkdir -p backend/services
mkdir -p backend/config
mkdir -p backend/types
```

### 階段 2: 移動核心模組
```bash
# 移動 core/ 目錄
mv app/core/* backend/core/

# 移動 utils/ 目錄
mv app/utils/* backend/utils/

# 移動 config/ 目錄
mv app/config/* backend/config/

# 移動 custom_types/ 目錄
mv app/custom_types/* backend/types/
```

### 階段 3: 重組服務層
將 `app/` 根目錄下的文件按功能分類到 `backend/services/`：

#### 3.1 化學相關服務
- `pubchem_handler.py` → `backend/services/chemical_service.py`
- `app/services/chemical_service.py` → 合併到 `backend/services/chemical_service.py`
- `app/services/smiles_drawer.py` → `backend/services/smiles_drawer.py`

#### 3.2 文件處理服務
- `file_upload.py` → `backend/services/file_service.py`
- `pdf_read_and_chunk_page_get.py` → `backend/services/document_service.py`
- `excel_to_txt_by_row.py` → `backend/services/excel_service.py`
- `document_renamer.py` → `backend/services/document_service.py`

#### 3.3 知識管理服務
- `knowledge_agent.py` → `backend/services/knowledge_service.py`
- `rag_core_refactored.py` → `backend/services/rag_service.py`
- `chunk_embedding.py` → `backend/services/embedding_service.py`

#### 3.4 搜索服務
- `search_agent.py` → `backend/services/search_service.py`
- `semantic_lookup.py` → `backend/services/semantic_service.py`
- `query_parser.py` → `backend/services/query_service.py`

#### 3.5 元數據服務
- `metadata_extractor.py` → `backend/services/metadata_service.py`
- `metadata_registry.py` → `backend/services/metadata_service.py`
- `metadata_experiment_registry.py` → `backend/services/metadata_service.py`

#### 3.6 模型配置服務
- `model_config_bridge.py` → `backend/services/model_service.py`
- `model_parameter_detector.py` → `backend/services/model_service.py`

#### 3.7 外部 API 服務
- `europepmc_handler.py` → `backend/services/external_api_service.py`

### 階段 4: 更新導入路徑
更新所有文件中的導入路徑，將 `from app.` 改為 `from backend.`

### 階段 5: 更新 main.py
移除 `sys.path.append` 的 hack，使用正確的相對導入

### 階段 6: 清理和測試
- 刪除空的 `app/` 目錄
- 運行測試確保所有功能正常
- 更新文檔

## 🔄 重組後的好處

1. **清晰的職責分離**
   - `frontend/`: React UI 組件
   - `backend/`: FastAPI + 業務邏輯

2. **更好的模組化**
   - 按功能分組的服務層
   - 清晰的依賴關係

3. **符合現代 Web 架構**
   - 前後端分離
   - RESTful API 設計

4. **更容易維護**
   - 統一的後端代碼庫
   - 清晰的目錄結構

## ⚠️ 注意事項

1. **備份當前代碼**：在開始重組前創建備份
2. **逐步進行**：一次只移動一個模組，確保功能正常
3. **更新測試**：確保所有測試路徑正確
4. **更新文檔**：更新 README 和 API 文檔 