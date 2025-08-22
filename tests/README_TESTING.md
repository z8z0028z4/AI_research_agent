# AI研究助理 - 測試系統使用指南

## 統一測試入口

專案現在提供兩種測試方式：

### 1. Batch檔案入口（推薦）

```bash
# 快速測試（預設）
.\run_tests.bat

# 完整測試
.\run_tests.bat all

# 覆蓋率測試
.\run_tests.bat coverage

# API測試
.\run_tests.bat api

# 端到端測試
.\run_tests.bat e2e

# 檢查依賴
.\run_tests.bat deps

# 自定義測試
.\run_tests.bat tests/test_specific_file.py
```

### 2. Python腳本入口

```bash
# 快速測試
python tests\run_tests.py --type quick

# 完整測試
python tests\run_tests.py --type all

# 覆蓋率測試
python tests\run_tests.py --type coverage

# 檢查依賴
python tests\run_tests.py --check-deps

# 自定義測試
python tests\run_tests.py --test tests/test_specific_file.py
```

## 測試類型說明

- **quick**: 快速測試，只運行核心模組測試
- **all**: 完整測試，運行所有測試套件
- **coverage**: 覆蓋率測試，生成HTML覆蓋率報告
- **api**: API端點測試
- **e2e**: 端到端測試
- **services**: 服務層測試
- **core**: 核心模組測試
- **utils**: 工具函數測試
- **frontend**: 前端組件測試

## 測試策略

本專案採用「真實測試」策略：

- ✅ **真實API調用**：API測試使用實際的FastAPI TestClient
- ✅ **真實文件操作**：使用tempfile進行隔離的文件測試
- ✅ **真實服務調用**：直接調用後端服務而非mock
- ⚠️ **策略性Mock**：僅對外部API（OpenAI、PubChem等）和前端組件使用mock

## 依賴需求

測試系統需要以下Python套件：
- pytest
- pytest-cov
- fastapi
- httpx

使用 `.\run_tests.bat deps` 可檢查所有依賴是否已安裝。

## 覆蓋率報告

運行覆蓋率測試後，會在專案根目錄生成：
- `htmlcov/` 目錄：包含詳細的HTML覆蓋率報告
- 終端輸出：顯示覆蓋率百分比和缺失行數

## 故障排除

如果測試失敗：

1. 確保Python已安裝並在PATH中
2. 確保在專案根目錄執行
3. 檢查所有依賴是否已安裝：`.\run_tests.bat deps`
4. 查看具體錯誤信息並修復相關問題

## 測試檔案結構

```
tests/
├── run_tests.py          # Python測試腳本
├── README_TESTING.md     # 本說明文件
├── test_core_*.py        # 核心模組測試
├── test_services*.py     # 服務層測試
├── test_api.py           # API測試
├── test_e2e_real.py      # 端到端測試
├── test_utils.py         # 工具函數測試
└── test_frontend_*.py    # 前端組件測試
```
