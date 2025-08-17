# Streamlit GUI 棄用檔案

## 📁 檔案說明

此目錄包含已棄用的 Streamlit GUI 相關檔案，這些檔案已在新架構中被 React 前端替代。

### 🚫 已棄用的檔案

| 檔案名稱 | 大小 | 行數 | 功能說明 | 替代方案 |
|----------|------|------|----------|----------|
| `research_gui.py` | 28KB | 613行 | 原 Streamlit 主界面 | `frontend/src/pages/` 各頁面組件 |
| `main.py` | 5.7KB | 159行 | 原 Streamlit 啟動器 | `start_react.bat` |
| `browser.py` | 7.5KB | 280行 | 原 Streamlit 文件選擇器 | `frontend/src/pages/Upload.jsx` |

### 🔄 功能對應關係

#### research_gui.py → React 頁面組件
- **提案生成功能** → `frontend/src/pages/Proposal.jsx`
- **文件上傳功能** → `frontend/src/pages/Upload.jsx`
- **設定管理功能** → `frontend/src/pages/Settings.jsx`
- **搜索功能** → `frontend/src/pages/Search.jsx`
- **化學品查詢功能** → `frontend/src/pages/Chemical.jsx`
- **知識查詢功能** → `frontend/src/pages/KnowledgeQuery.jsx`
- **儀表板功能** → `frontend/src/pages/Dashboard.jsx`

#### main.py → 啟動腳本
- **Streamlit 啟動邏輯** → `start_react.bat`
- **環境配置** → 虛擬環境自動配置
- **錯誤處理** → 改進的錯誤處理機制

#### browser.py → 文件處理組件
- **文件選擇功能** → `frontend/src/pages/Upload.jsx`
- **文件處理邏輯** → `backend/api/routes/upload.py`
- **文件驗證** → 前端和後端雙重驗證

### 📊 架構對比

#### 舊架構 (Streamlit)
```
app/
├── research_gui.py     # 單一大型 GUI 文件 (613行)
├── main.py            # 簡單啟動器 (159行)
└── browser.py         # 文件選擇器 (280行)
```

#### 新架構 (React + FastAPI)
```
frontend/src/pages/    # 7個頁面組件
backend/api/routes/    # 6個 API 路由
start_react.bat        # 現代化啟動器
```

### ⚠️ 注意事項

1. **不要直接使用**：這些檔案僅作為參考保留
2. **功能已遷移**：所有功能都已在新架構中實現
3. **代碼組織**：新架構提供更好的代碼組織和維護性
4. **用戶體驗**：新架構提供更好的用戶體驗

### 🎯 建議

1. 如需了解原功能實現，可參考這些檔案
2. 新功能開發應基於 React + FastAPI 架構
3. 在未來版本中可考慮完全移除這些檔案
4. 繼續改進新架構的功能和性能

---
*移動時間：2025-08-16*
*移動原因：重構完成，整理棄用檔案*
