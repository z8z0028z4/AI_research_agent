# AI Research Assistant - 使用指南

## 快速開始

### 方法一：React 版本啟動（推薦）
```bash
# 雙擊運行 - 啟動 React 版本
start_react.bat
```

### 方法二：通用啟動（自動選擇版本）
```bash
# 雙擊運行 - 自動選擇可用版本
run.bat
```

### 方法三：虛擬環境設置（首次使用）
```bash
# 雙擊運行
venv_setup.bat
```

### 方法四：分步啟動
```bash
# 啟動後端
cd backend
run_api.bat

# 啟動前端（新開一個終端）
cd frontend
run_frontend.bat
```

### 方法五：後端重啟
```bash
# 重啟後端服務
restart_backend.bat
```

## 虛擬環境管理

### ⚠️ 重要：虛擬環境統一管理

**虛擬環境位置：**
- **Windows**: `C:\ai_research_venv`
- **Linux/macOS**: `~/.ai_research_venv`
- 不會被上傳到雲端
- 每次啟動時自動檢查依賴版本

### 🔧 設置流程

#### 首次設置
```bash
# 1. 運行虛擬環境設置
venv_setup.bat
```

#### 日常使用
```bash
# 啟動 React 版本（推薦）
start_react.bat

# 或使用通用啟動（自動選擇版本）
run.bat
```

### 📁 可以共用的文件
- `requirements.txt` - Python 依賴（自動檢測 CUDA）
- `check_deps.py` - 依賴檢查腳本
- `package.json` - Node.js 依賴列表
- 源代碼文件
- 配置文件（`.env` 除外）

### 📁 不能共用的文件
- `C:\ai_research_venv\` - 虛擬環境目錄（Windows）
- `~/.ai_research_venv/` - 虛擬環境目錄（Linux/macOS）
- `node_modules/` 目錄（已加入 .gitignore）
- `.env` 文件（包含個人 API 金鑰）
- `.venv_config` 文件（本地配置）

## 依賴管理

### 智能依賴安裝

項目使用單一的 `requirements.txt` 文件：
- **CUDA 版本安裝** - `requirements.txt` 包含 CUDA 版本的 PyTorch 配置
- **簡化安裝** - 直接從 `requirements.txt` 安裝，無需回退邏輯
- **依賴檢查** - 每次啟動時自動檢查關鍵依賴
- **基於 requirements.txt** - 所有依賴都從 `requirements.txt` 安裝，確保版本一致性

### 自動依賴檢查

每次啟動時會自動：
- 檢查虛擬環境狀態
- 驗證依賴版本
- 提示缺失的依賴

## 系統要求

- **Python 3.10+** - 下載自 https://python.org
- **Node.js 16+** - 下載自 https://nodejs.org
- **Windows 10/11** - 支援 PowerShell 和 CMD
- **Linux/macOS** - 支援 bash/zsh
- **GPU（可選）** - 支援 CUDA 的 NVIDIA GPU 用於加速

## 安裝步驟

1. **下載並安裝 Python**
   - 從 https://python.org 下載 Python 3.10 或更新版本
   - 安裝時勾選 "Add Python to PATH"

2. **下載並安裝 Node.js**
   - 從 https://nodejs.org 下載 LTS 版本
   - 安裝時勾選 "Add to PATH"

3. **設置虛擬環境**
   ```bash
   venv_setup.bat
   ```

4. **配置 API 金鑰**
   - 編輯 `.env` 文件
   - 添加您的 API 金鑰：
     ```
     OPENAI_API_KEY=your_openai_api_key_here
     PERPLEXITY_API_KEY=your_perplexity_api_key_here
     ```

## 啟動應用

### React 版本啟動（推薦）
```bash
start_react.bat
```

### 通用啟動（自動選擇版本）
```bash
run.bat
```

### 分步啟動
```bash
# 後端啟動
cd backend
run_api.bat

# 前端啟動
cd frontend
run_frontend.bat
```

### 後端重啟
```bash
restart_backend.bat
```

## 訪問應用

- **前端應用**: http://localhost:3000
- **後端 API**: http://localhost:8000
- **API 文檔**: http://localhost:8000/api/docs

## 故障排除

### 常見問題

1. **Python 未找到**
   - 確保 Python 已安裝並添加到 PATH
   - 重新安裝 Python 並勾選 "Add to PATH"

2. **Node.js 未找到**
   - 確保 Node.js 已安裝並添加到 PATH
   - 重新安裝 Node.js 並勾選 "Add to PATH"

3. **虛擬環境問題**
   - 運行 `venv_setup.bat` 重新創建
   - 或手動刪除虛擬環境目錄後重新運行

4. **端口被佔用**
   - 檢查端口 3000 和 8000 是否被其他程序使用
   - 關閉佔用端口的程序

5. **依賴安裝失敗**
   - 檢查網絡連接
   - 嘗試使用 VPN 或代理
   - 重新運行 `venv_setup.bat`

6. **虛擬環境損壞**
   - 刪除虛擬環境目錄
   - 重新運行 `venv_setup.bat`

7. **PyTorch 安裝問題**
   - `venv_setup.bat` 會自動檢測 CUDA 並安裝合適版本
   - 如果 GPU 版本失敗，會自動回退到 CPU 版本

### 日誌查看

- **後端日誌**: 查看後端終端窗口
- **前端日誌**: 查看前端終端窗口
- **瀏覽器開發者工具**: F12 查看前端錯誤

## 開發模式

### 後端開發
```bash
cd backend
run_api.bat
```
後端使用 FastAPI，支援熱重載。

### 前端開發
```bash
cd frontend
run_frontend.bat
```
前端使用 Vite，支援熱重載。

## 在不同裝置間移動

### 準備工作
1. 複製整個項目目錄（除了 `node_modules`）
2. 確保目標裝置已安裝 Python 和 Node.js

### 在新裝置上運行
1. 運行 `venv_setup.bat`
2. 配置 API 金鑰

### 注意事項
- 虛擬環境會自動建立在適當的位置
- 不要複製 `node_modules` 目錄（已自動排除）
- 記得更新 `.env` 文件中的 API 金鑰

## 版本控制最佳實踐

### 已排除的文件
- `C:\ai_research_venv\` - 虛擬環境目錄（Windows）
- `~/.ai_research_venv/` - 虛擬環境目錄（Linux/macOS）
- `node_modules/` - Node.js 依賴目錄
- `.env` - 環境變數文件
- `.venv_config` - 虛擬環境配置文件
- `*.log` - 日誌文件
- `__pycache__/` - Python 緩存文件

### 建議的工作流程
1. 開發時使用 `start_react.bat`（React 版本）
2. 或使用 `run.bat`（自動選擇版本）
3. 新裝置使用 `venv_setup.bat`
4. 依賴檢查已整合到啟動腳本中

## 生產部署

這些腳本僅用於開發環境。生產部署請參考：
- FastAPI 部署文檔
- React 構建和部署文檔

## 支援

如果遇到問題：
1. 檢查系統要求
2. 查看故障排除部分
3. 檢查日誌輸出
4. 重新運行 `venv_setup.bat` 修復環境
