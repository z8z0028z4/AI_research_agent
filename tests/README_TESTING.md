# 測試文檔

## 概述

本專案包含完整的測試套件，涵蓋單元測試、整合測試和端到端測試。

## 測試結構

```
tests/
├── test_text_interaction_service.py      # 文字互動服務單元測試
├── test_text_interaction_api.py          # 文字互動 API 單元測試
├── test_text_interaction_integration.py  # 文字互動整合測試
├── test_core_modules.py                  # 核心模組測試（包含新增的修改功能）
├── test_services.py                      # 服務層測試（包含新增的 RAG 服務）
├── frontend/                             # 前端測試
│   └── test_text_highlight_components.js # 文字反白組件測試
├── e2e/                                  # 端到端測試
│   └── test_text_highlight_workflows.spec.js # 文字反白工作流程測試
├── conftest.py                           # 測試配置
├── pytest.ini                           # pytest 配置
└── README_TESTING.md                     # 本文件
```

## 新增功能測試

### 文字反白互動功能

#### 後端測試

1. **`test_text_interaction_service.py`**
   - 測試文字互動服務的核心邏輯
   - 包含解釋、提案修改、實驗細節修改功能
   - 測試上下文提取和錯誤處理

2. **`test_text_interaction_api.py`**
   - 測試 API 端點的請求和響應
   - 驗證數據模型和錯誤處理
   - 測試請求 ID 生成和計時信息

3. **`test_text_interaction_integration.py`**
   - 測試完整的後端工作流程
   - API 到服務層的整合測試
   - 上下文提取和錯誤處理整合

4. **擴展的 `test_core_modules.py`**
   - 新增實驗細節修改的 LLM 調用測試
   - 測試完整文檔內容的 old_text 構建
   - 測試字典格式和 Document 對象的 chunks 處理

5. **擴展的 `test_services.py`**
   - 新增實驗細節修改的 RAG 服務測試
   - 測試結構化數據轉文本的兼容函數
   - 測試提案修改和實驗細節修改的生成功能

#### 前端測試

1. **`frontend/test_text_highlight_components.js`**
   - 測試文字反白提供者組件
   - 測試彈窗組件
   - 測試互動輸入和響應組件
   - 包含完整的用戶流程測試

#### 端到端測試

1. **`e2e/test_text_highlight_workflows.spec.js`**
   - 使用 Playwright 測試完整的用戶流程
   - 包含解釋、提案修改、實驗細節修改工作流程
   - 測試錯誤處理和 UI/UX 功能
   - 包含 API E2E 測試

## 運行測試

### 後端測試

```bash
# 運行所有後端測試
pytest

# 運行文字反白相關測試
pytest -m text_highlight

# 運行後端測試
pytest -m backend

# 運行快速測試（單元測試）
pytest -m fast

# 運行慢速測試（整合和E2E測試）
pytest -m slow

# 運行特定測試文件
pytest tests/test_text_interaction_service.py
pytest tests/test_text_interaction_api.py
pytest tests/test_text_interaction_integration.py

# 運行特定測試類
pytest tests/test_text_interaction_service.py::TestTextInteractionService

# 運行特定測試方法
pytest tests/test_text_interaction_service.py::TestTextInteractionService::test_process_explanation
```

### 前端測試

```bash
# 進入前端目錄
cd frontend

# 安裝依賴（如果還沒安裝）
npm install

# 運行前端測試
npm test

# 運行特定測試文件
npm test -- tests/frontend/test_text_highlight_components.js
```

### 端到端測試

```bash
# 安裝 Playwright（如果還沒安裝）
npm install -D @playwright/test

# 運行 E2E 測試
npx playwright test

# 運行特定 E2E 測試文件
npx playwright test tests/e2e/test_text_highlight_workflows.spec.js

# 在瀏覽器中運行測試
npx playwright test --headed
```

## 測試覆蓋率

### 後端覆蓋率

```bash
# 安裝覆蓋率工具
pip install pytest-cov

# 運行測試並生成覆蓋率報告
pytest --cov=backend --cov-report=html --cov-report=term

# 查看 HTML 覆蓋率報告
open htmlcov/index.html
```

### 前端覆蓋率

```bash
# 運行前端測試並生成覆蓋率報告
npm test -- --coverage

# 查看覆蓋率報告
open coverage/lcov-report/index.html
```

## 測試數據

測試使用模擬數據和真實數據的組合：

- **模擬數據**：用於單元測試，確保測試的獨立性
- **真實數據**：用於整合測試，驗證與實際系統的兼容性

## 測試標記

使用 pytest 標記來分類和運行測試：

- `@pytest.mark.unit`：單元測試
- `@pytest.mark.integration`：整合測試
- `@pytest.mark.api`：API 測試
- `@pytest.mark.e2e`：端到端測試
- `@pytest.mark.slow`：慢速測試
- `@pytest.mark.fast`：快速測試
- `@pytest.mark.text_highlight`：文字反白功能測試
- `@pytest.mark.frontend`：前端組件測試
- `@pytest.mark.backend`：後端功能測試

## 持續集成

測試已配置為在 CI/CD 流程中自動運行：

1. **後端測試**：在每次提交時運行
2. **前端測試**：在每次提交時運行
3. **E2E 測試**：在合併到主分支時運行

## 故障排除

### 常見問題

1. **測試失敗**
   - 檢查測試環境配置
   - 確認依賴已正確安裝
   - 查看測試日誌獲取詳細錯誤信息

2. **E2E 測試失敗**
   - 確認前端和後端服務正在運行
   - 檢查網絡連接
   - 確認測試數據可用

3. **覆蓋率報告問題**
   - 確認 pytest-cov 已安裝
   - 檢查覆蓋率配置

### 調試技巧

1. **使用 `-s` 標誌查看輸出**
   ```bash
   pytest -s tests/test_text_interaction_service.py
   ```

2. **使用 `--pdb` 進行調試**
   ```bash
   pytest --pdb tests/test_text_interaction_service.py
   ```

3. **使用 `-x` 在第一次失敗時停止**
   ```bash
   pytest -x tests/
   ```

## 最佳實踐

1. **測試命名**：使用描述性的測試名稱
2. **測試隔離**：每個測試應該獨立運行
3. **模擬外部依賴**：使用 mock 來隔離外部服務
4. **測試數據管理**：使用 fixtures 來管理測試數據
5. **錯誤處理測試**：確保錯誤情況被正確處理
6. **性能測試**：對關鍵功能進行性能測試

## 更新日誌

### 2025-08-29
- 新增文字反白互動功能的完整測試套件
- 包含後端單元測試、API 測試、整合測試
- 新增前端組件測試
- 新增 E2E 測試
- 更新測試配置和文檔
