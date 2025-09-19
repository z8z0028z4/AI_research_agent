# AI Research Agent 測試開發環境

## 🎯 概述

這是一個完整的測試開發環境，旨在確保每次開發新功能時都能快速驗證是否影響了現有功能。通過自動化測試和持續集成，我們可以：

- ✅ 快速驗證功能完整性
- 🔍 自動檢測回歸問題
- 📊 監控代碼質量
- 🚀 提高開發效率

## 🏗️ 測試架構

### 測試分類

1. **單元測試 (Unit Tests)**
   - 測試個別函數和類
   - 執行時間：< 30 秒
   - 覆蓋率目標：> 90%

2. **整合測試 (Integration Tests)**
   - 測試模組間互動
   - 執行時間：< 2 分鐘
   - 覆蓋率目標：> 80%

3. **API 測試 (API Tests)**
   - 測試 HTTP 端點
   - 執行時間：< 1 分鐘
   - 覆蓋率目標：100%

4. **端到端測試 (E2E Tests)**
   - 測試完整用戶流程
   - 執行時間：< 5 分鐘
   - 覆蓋率目標：關鍵流程 100%

### 新增測試模組 (2025/9/19)

5. **文獻搜尋測試 (Paper Search Tests)**
   - 測試文獻瀏覽、搜尋、下載功能
   - 執行時間：< 30 秒
   - 覆蓋率目標：> 95%
   - 測試文件：`test_paper_search.py`

6. **化學品搜尋測試 (Chemical Search Tests)**
   - 測試化學品查詢、資料庫搜尋、結構繪製
   - 執行時間：< 45 秒
   - 覆蓋率目標：> 90%
   - 測試文件：`test_chemical_search.py`

## 🚀 快速開始

### 1. 環境設置

```bash
# 安裝測試依賴
pip install pytest pytest-cov pytest-mock

# 進入測試目錄
cd tests
```

### 2. 運行測試

```bash
# 運行所有測試
python -m pytest

# 運行特定測試模組
python -m pytest test_paper_search.py -v
python -m pytest test_chemical_search.py -v

# 運行測試並生成覆蓋率報告
python -m pytest --cov=backend --cov-report=html
# 快速測試（推薦日常使用）
quick_test.bat

# 完整測試套件
run_tests.bat

# 覆蓋率測試
coverage_test.bat
```

### 3. 開發流程

```bash
# 1. 開發新功能前，運行快速測試確保環境正常
quick_test.bat

# 2. 開發過程中，定期運行測試
python -m pytest test_core_modules.py -v

# 3. 完成功能後，運行完整測試
run_tests.bat

# 4. 檢查覆蓋率
coverage_test.bat
```

## 📁 測試文件結構

```
tests/
├── conftest.py              # 測試配置和 fixtures
├── pytest.ini              # pytest 配置
├── test_core_modules.py    # 核心模組測試
├── test_services.py        # 服務層測試
├── test_api.py             # API 測試
├── test_e2e.py             # 端到端測試
├── run_tests.bat           # 主測試運行器
├── quick_test.bat          # 快速測試
├── coverage_test.bat       # 覆蓋率測試
└── README.md               # 本文檔
```

## 🔧 測試工具

### 1. 主測試運行器 (`run_tests.bat`)

提供完整的測試管理功能：

- 🚀 快速測試：單元測試
- 🔍 完整測試：所有測試
- 📊 覆蓋率測試：生成報告
- 🎯 特定測試：自定義測試
- 🔧 修復測試：診斷問題
- 📋 測試狀態：查看結果
- 🧹 清理測試：清理數據

### 2. 快速測試 (`quick_test.bat`)

專門用於日常開發的快速驗證：

- 測試核心模組
- 驗證基礎功能
- 快速反饋
- 適合頻繁運行

### 3. 覆蓋率測試 (`coverage_test.bat`)

生成詳細的代碼覆蓋率報告：

- HTML 報告
- XML 報告
- 覆蓋率分析
- 質量監控

## 📊 測試指標

### 覆蓋率目標

- **代碼覆蓋率**: > 90%
- **分支覆蓋率**: > 85%
- **函數覆蓋率**: > 95%

### 性能目標

- **單元測試**: < 30 秒
- **整合測試**: < 2 分鐘
- **完整測試套件**: < 10 分鐘

### 質量目標

- **測試通過率**: > 99%
- **假陽性率**: < 1%
- **測試維護成本**: 最小化

## 🛠️ 開發最佳實踐

### 1. 測試驅動開發 (TDD)

```python
# 1. 先寫測試
def test_new_feature():
    result = new_feature("input")
    assert result == "expected_output"

# 2. 運行測試（應該失敗）
# 3. 實現功能
# 4. 運行測試（應該通過）
```

### 2. 測試命名規範

```python
# 好的命名
def test_upload_pdf_file_success():
def test_upload_invalid_file_returns_error():
def test_llm_response_contains_expected_content():

# 不好的命名
def test_upload():
def test_llm():
def test_something():
```

### 3. 測試結構 (AAA 模式)

```python
def test_function():
    # Arrange (準備)
    input_data = "test"
    expected = "expected"
    
    # Act (執行)
    result = function(input_data)
    
    # Assert (驗證)
    assert result == expected
```

### 4. Mock 使用

```python
@patch('external.api.call')
def test_with_mock(mock_api):
    mock_api.return_value = "mocked_response"
    result = function_that_calls_api()
    assert result == "mocked_response"
```

## 🔍 故障排除

### 常見問題

1. **導入錯誤**
   ```bash
   # 檢查 Python 路徑
   python -c "import backend.core.config"
   ```

2. **測試失敗**
   ```bash
   # 運行診斷測試
   python -m pytest test_core_modules.py::TestConfigManagement::test_settings_loading -v
   ```

3. **覆蓋率問題**
   ```bash
   # 檢查覆蓋率報告
   # 打開 ..\htmlcov\index.html
   ```

### 修復步驟

1. 檢查 `conftest.py` 中的 mock 設置
2. 確認 backend 模組導入正常
3. 檢查測試依賴是否完整
4. 運行完整測試查看詳細錯誤

## 📈 持續改進

### 1. 自動化測試

- 每次提交自動運行測試
- 測試失敗阻止合併
- 覆蓋率門檻檢查

### 2. 測試質量監控

- 測試執行時間
- 通過/失敗統計
- 覆蓋率趨勢
- 錯誤詳情

### 3. 測試維護

- 定期更新測試用例
- 移除過時的測試
- 優化測試性能
- 改進測試覆蓋率

## 🎯 使用建議

### 日常開發

1. **開始工作前**：運行 `quick_test.bat` 確保環境正常
2. **開發過程中**：定期運行相關測試
3. **完成功能後**：運行完整測試套件
4. **提交前**：檢查覆蓋率報告

### 新功能開發

1. **設計階段**：考慮測試策略
2. **實現階段**：同步編寫測試
3. **測試階段**：確保所有路徑都有測試
4. **文檔階段**：更新測試文檔

### 維護階段

1. **定期檢查**：運行完整測試套件
2. **監控覆蓋率**：確保不低於目標
3. **優化性能**：改進測試執行時間
4. **更新文檔**：保持測試文檔最新

## 🆕 新增測試功能 (2025/9/19)

### 文獻搜尋測試 (test_paper_search.py)

測試文獻管理系統的完整功能：

#### 測試範圍
- ✅ **文獻統計 API** (`/api/v1/paper/stats`)
- ✅ **文獻列表 API** (`/api/v1/paper/list`)
- ✅ **文獻搜尋 API** (`/api/v1/paper/search`)
- ✅ **文獻下載 API** (`/api/v1/paper/download/{filename}`)
- ✅ **文獻查看 API** (`/api/v1/paper/view/{filename}`)

#### 測試場景
- 正常情況下的 API 響應
- 文件不存在時的錯誤處理
- 目錄不存在時的處理
- 搜尋功能的正確性
- 參數驗證和錯誤處理

#### 運行測試
```bash
# 運行文獻搜尋測試
python -m pytest test_paper_search.py -v

# 運行特定測試類
python -m pytest test_paper_search.py::TestPaperSearch -v

# 運行特定測試方法
python -m pytest test_paper_search.py::TestPaperSearch::test_paper_stats_success -v
```

### 化學品搜尋測試 (test_chemical_search.py)

測試化學品查詢系統的完整功能：

#### 測試範圍
- ✅ **化學品搜尋 API** (`/api/v1/chemical/search`)
- ✅ **化學品批量搜尋 API** (`/api/v1/chemical/batch-search`)
- ✅ **化學品資料庫搜尋 API** (`/api/v1/chemical/database-search`)
- ✅ **化學品資料庫統計 API** (`/api/v1/chemical/database-stats`)
- ✅ **化學品資料庫列表 API** (`/api/v1/chemical/database-list`)

#### 測試場景
- 化學品搜尋成功和失敗情況
- 批量搜尋功能
- 資料庫操作（搜尋、統計、列表）
- 結構繪製功能
- 安全數據處理
- 錯誤處理和參數驗證

#### 運行測試
```bash
# 運行化學品搜尋測試
python -m pytest test_chemical_search.py -v

# 運行特定測試類
python -m pytest test_chemical_search.py::TestChemicalSearch -v

# 運行整合測試
python -m pytest test_chemical_search.py::TestChemicalSearchIntegration -v
```

### 測試覆蓋率目標

| 模組 | 覆蓋率目標 | 當前狀態 |
|------|------------|----------|
| 文獻搜尋 | > 95% | 🎯 目標達成 |
| 化學品搜尋 | > 90% | 🎯 目標達成 |
| API 端點 | 100% | ✅ 完全覆蓋 |
| 錯誤處理 | > 85% | ✅ 高覆蓋率 |

### 測試數據

#### 文獻測試數據
- 測試文件：263 個 PDF 文獻
- 總大小：360.5 MB
- 支援搜尋：按文件名搜尋
- 支援操作：查看、下載

#### 化學品測試數據
- 資料庫化學品：333 個
- 支援搜尋：按名稱、分子式、CAS 號
- 支援功能：結構繪製、安全數據
- 支援操作：資料庫查詢、統計

## 📞 支持

如果遇到測試問題：

1. 查看本文檔的故障排除部分
2. 運行診斷測試
3. 檢查測試日誌
4. 聯繫開發團隊

---

**記住**：好的測試是代碼質量的保障，也是開發效率的加速器！ 