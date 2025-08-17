# 棄用檔案收集目錄

## 重構狀態檢查報告

### 🎯 重構完成狀態：✅ 已完成

根據檢查結果，軟體已成功從 **Streamlit 架構** 重構為 **React + FastAPI 架構**：

#### ✅ 重構成功的部分：

1. **前端架構**：
   - ✅ 從 Streamlit 遷移到 React 18 + Vite + Ant Design
   - ✅ 完整的頁面組件：Proposal、Search、Settings、Upload、Chemical、KnowledgeQuery、Dashboard
   - ✅ 現代化的響應式 UI 設計

2. **後端架構**：
   - ✅ 從 Streamlit 後端遷移到 FastAPI RESTful API
   - ✅ 模組化的 API 路由：proposal、search、settings、knowledge、upload、chemical
   - ✅ 完整的設定管理系統

3. **啟動腳本**：
   - ✅ `start_react.bat` - React 版本啟動器
   - ✅ `restart_backend.bat` - 後端重啟腳本
   - ✅ 虛擬環境自動配置

### 📁 準備棄用的原檔案

以下檔案已在新架構中被替代，但保留作為參考：

#### 1. Streamlit GUI 相關檔案
- `app/research_gui.py` - 原 Streamlit 主界面
- `app/main.py` - 原 Streamlit 啟動器
- `app/browser.py` - 原 Streamlit 文件選擇器

#### 2. 舊的啟動腳本
- 任何直接啟動 Streamlit 的腳本

#### 3. 舊的配置文件
- 僅適用於 Streamlit 的配置文件

### 🔄 架構對比

#### 舊架構 (Streamlit)：
```
app/
├── research_gui.py     # Streamlit 單頁面應用
├── main.py            # Streamlit 啟動器
└── browser.py         # Streamlit 文件選擇器
```

#### 新架構 (React + FastAPI)：
```
frontend/              # React 前端
├── src/
│   ├── pages/        # 多頁面組件
│   └── components/   # 可重用組件
backend/               # FastAPI 後端
├── api/routes/       # API 路由
└── core/             # 核心配置
```

### 📋 保留原因

這些檔案保留作為：
1. **參考文檔** - 了解原功能實現
2. **備份** - 以防需要回滾
3. **學習資源** - 對比新舊架構差異

### 🚀 當前推薦使用方式

1. **開發環境**：使用 `start_react.bat`
2. **後端重啟**：使用 `restart_backend.bat`
3. **前端開發**：在 `frontend/` 目錄下進行

### ⚠️ 注意事項

- 不要直接運行 `app/research_gui.py`
- 不要使用舊的 Streamlit 啟動方式
- 新的 React 前端需要 Node.js 環境
- 後端 API 運行在 port 8000，前端運行在 port 3000

---
*最後更新：2025-08-16*
