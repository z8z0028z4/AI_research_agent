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

## 📞 支持

如果遇到測試問題：

1. 查看本文檔的故障排除部分
2. 運行診斷測試
3. 檢查測試日誌
4. 聯繫開發團隊

---

**記住**：好的測試是代碼質量的保障，也是開發效率的加速器！ 