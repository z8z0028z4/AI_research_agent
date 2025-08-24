# AI Research Agent 測試覆蓋計劃

## 🎯 測試覆蓋目標

### 核心功能測試 (100% 覆蓋)
- [x] 配置管理 (`test_core_modules.py`)
- [x] LLM 管理 (`test_core_modules.py`)
- [x] 向量存儲 (`test_core_modules.py`)
- [x] 檢索功能 (`test_core_modules.py`)

### 服務層測試 (100% 覆蓋)
- [x] 文件處理服務 (`test_services.py`)
- [x] 嵌入服務 (`test_services.py`)
- [x] 知識代理服務 (`test_services.py`)
- [x] 搜索服務 (`test_services.py`)
- [x] RAG 服務 (`test_services.py`)
- [x] 化學服務 (`test_services.py`)

### API 端點測試 (100% 覆蓋)
- [x] 文件上傳 API (`test_api.py`)
- [x] 知識查詢 API (`test_api.py`)
- [x] 搜索 API (`test_api.py`)
- [x] 化學信息 API (`test_api.py`)
- [x] 提案生成 API (`test_api.py`)

### 端到端測試 (關鍵流程)
- [x] 完整工作流程 (`test_e2e.py`)
- [x] 錯誤處理 (`test_e2e.py`)
- [x] 性能測試 (`test_e2e.py`)
- [x] 安全性測試 (`test_e2e.py`)

## 📊 測試分類

### 1. 單元測試 (Unit Tests)
**目標**: 測試個別函數和類
**覆蓋率**: 90%+
**執行時間**: < 1 分鐘

```python
# 示例：測試單個函數
def test_extract_metadata():
    metadata = extract_metadata("test.pdf")
    assert metadata["filename"] == "test.pdf"
    assert metadata["file_size"] > 0
```

### 2. 整合測試 (Integration Tests)
**目標**: 測試模組間互動
**覆蓋率**: 80%+
**執行時間**: < 5 分鐘

```python
# 示例：測試文件上傳到向量化流程
def test_file_upload_to_vectorization():
    # 1. 上傳文件
    upload_result = upload_file("test.pdf")
    assert upload_result["success"]
    
    # 2. 檢查向量化
    vectors = get_vectorstore_stats("paper")
    assert vectors["total_documents"] > 0
```

### 3. API 測試 (API Tests)
**目標**: 測試 HTTP 端點
**覆蓋率**: 100%
**執行時間**: < 2 分鐘

```python
# 示例：測試 API 端點
def test_upload_endpoint():
    response = client.post("/api/v1/upload/files", files={"file": "test.pdf"})
    assert response.status_code == 200
    assert "task_id" in response.json()
```

### 4. 端到端測試 (E2E Tests)
**目標**: 測試完整用戶流程
**覆蓋率**: 關鍵流程 100%
**執行時間**: < 10 分鐘

```python
# 示例：完整用戶流程
def test_complete_user_workflow():
    # 1. 用戶上傳論文
    # 2. 系統向量化
    # 3. 用戶查詢
    # 4. 系統回答
    # 5. 驗證結果
```

## 🔧 測試優先級

### 高優先級 (P0)
- 核心配置加載
- 文件上傳處理
- LLM 調用
- 向量存儲操作
- API 端點響應

### 中優先級 (P1)
- 錯誤處理
- 邊界條件
- 性能測試
- 數據驗證

### 低優先級 (P2)
- 邊緣情況
- 可選功能
- 優化測試

## 📈 測試指標

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

## 🚀 實施策略

### 階段 1: 核心功能 (已完成)
- [x] 配置管理測試
- [x] 基本服務測試
- [x] API 端點測試

### 階段 2: 完整覆蓋 (進行中)
- [ ] 添加缺失的測試用例
- [ ] 提高覆蓋率到目標水平
- [ ] 優化測試性能

### 階段 3: 持續改進
- [ ] 自動化測試執行
- [ ] 測試報告生成
- [ ] 測試質量監控

## 📝 測試最佳實踐

### 1. 測試命名
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

### 2. 測試結構 (AAA 模式)
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

### 3. 測試隔離
```python
# 每個測試都是獨立的
def test_1():
    # 不依賴 test_2 的結果
    pass

def test_2():
    # 不依賴 test_1 的結果
    pass
```

### 4. Mock 使用
```python
# 外部依賴使用 Mock
@patch('external.api.call')
def test_with_mock(mock_api):
    mock_api.return_value = "mocked_response"
    result = function_that_calls_api()
    assert result == "mocked_response"
```

## 🔍 測試工具

### 1. 覆蓋率工具
```bash
# 生成覆蓋率報告
pytest --cov=backend --cov-report=html

# 查看覆蓋率
pytest --cov=backend --cov-report=term-missing
```

### 2. 測試發現
```bash
# 發現所有測試
pytest --collect-only

# 發現特定測試
pytest -k "test_upload"
```

### 3. 測試執行
```bash
# 運行所有測試
pytest

# 運行特定測試
pytest tests/test_core_modules.py

# 運行失敗的測試
pytest --lf
```

## 📊 監控和報告

### 1. 測試報告
- 測試執行時間
- 通過/失敗統計
- 覆蓋率報告
- 錯誤詳情

### 2. 持續集成
- 每次提交自動運行測試
- 測試失敗阻止合併
- 覆蓋率門檻檢查

### 3. 質量門檻
- 覆蓋率 > 90%
- 測試通過率 > 99%
- 無嚴重錯誤 