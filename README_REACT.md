# AI Research Assistant - React 版本

這是 AI Research Assistant 的 React 前端版本，提供現代化的用戶界面和更好的用戶體驗。**主要變更：從 Streamlit 遷移到 React 前端，並已恢復核心功能。**

## 🚀 快速開始

### 前置要求

1. **Node.js** (版本 16 或更高)
   - 下載並安裝 [Node.js](https://nodejs.org/)

2. **Python** (版本 3.8 或更高)
   - 確保已安裝 Python 和 pip

3. **虛擬環境**
   - 確保已創建並激活 Python 虛擬環境

### 一鍵安裝和運行

```bash
# 雙擊運行安裝腳本
install.bat

# 雙擊運行應用
start_react_app.bat
```

這將自動：
- 檢查並安裝所有依賴
- 啟動後端 API 服務器 (http://localhost:8000)
- 啟動前端開發服務器 (http://localhost:3000)

## 📁 項目結構

```
AI-research-agent/
├── backend/                 # FastAPI 後端
│   ├── main.py             # 主應用文件
│   ├── requirements.txt    # Python 依賴
│   ├── run_api.bat        # 後端啟動腳本
│   ├── core/              # 核心配置
│   └── api/               # API 路由
│       └── routes/        # API 端點
├── frontend/               # React 前端
│   ├── package.json       # Node.js 依賴
│   ├── run_frontend.bat   # 前端啟動腳本
│   ├── src/               # 源代碼
│   │   ├── components/    # React 組件
│   │   ├── pages/         # 頁面組件
│   │   └── services/      # API 服務
│   └── public/            # 靜態資源
├── app/                    # 原有 Streamlit 應用
├── start_react_app.bat    # 總體啟動腳本
└── README_REACT.md        # 本文檔
```

## 🌟 新功能特性

### 1. 現代化用戶界面
- 使用 Ant Design 組件庫
- 響應式設計，支持移動端
- 流暢的動畫和交互效果

### 2. 更好的用戶體驗
- 實時狀態更新
- 進度條和加載狀態
- 錯誤處理和用戶反饋
- 智能文本清理（移除 markdown 格式）

### 3. 模塊化架構
- 組件化開發
- 狀態管理
- API 服務封裝

### 4. 開發體驗
- 熱重載開發
- TypeScript 支持
- ESLint 代碼檢查

## 🔧 開發指南

### 後端開發

1. **安裝依賴：**
```bash
cd backend
pip install -r requirements.txt
```

2. **運行開發服務器：**
```bash
python main.py
```

3. **API 文檔：**
- 訪問 http://localhost:8000/api/docs 查看 Swagger 文檔

### 前端開發

1. **安裝依賴：**
```bash
cd frontend
npm install
```

2. **運行開發服務器：**
```bash
npm run dev
```

3. **構建生產版本：**
```bash
npm run build
```

## 📊 功能對比

| 功能 | Streamlit 版本 | React 版本 | 狀態 |
|------|----------------|------------|------|
| 研究提案生成 | ✅ | ✅ | 已完成 |
| 提案修訂 | ✅ | ✅ | 已完成 |
| 實驗細節生成 | ✅ | ✅ | 已完成 |
| DOCX 下載 | ✅ | ✅ | 已完成 |
| 化學品查詢 | ✅ | ✅ | 已完成 |
| 文獻搜尋下載 | ✅ | ❌ | 待實現 |
| 文件上傳處理 | ✅ | ❌ | 待實現 |
| 儀錶板 | ✅ | ❌ | 待實現 |
| 用戶界面 | 基礎 | 現代化 | 已完成 |
| 響應式設計 | 有限 | 完整 | 已完成 |
| 開發體驗 | 簡單 | 專業 | 已完成 |
| 性能 | 中等 | 優化 | 已完成 |

## 🔄 遷移進度

### 已完成 ✅
- [x] 後端 API 框架搭建
- [x] 基礎路由和端點
- [x] 前端項目結構
- [x] 基礎組件和頁面
- [x] 開發環境配置
- [x] 研究提案生成頁面
- [x] 提案修訂功能
- [x] 實驗細節生成
- [x] DOCX 下載功能
- [x] 化學品查詢頁面
- [x] 文本格式清理
- [x] 響應式設計

### 進行中 🚧
- [ ] 文獻搜尋頁面
- [ ] 文件上傳頁面
- [ ] 儀錶板頁面

### 待完成 📋
- [ ] 文獻助理頁面（RAG 模式選擇）
- [ ] 實驗顧問功能
- [ ] 數據顯示和比較
- [ ] 提案選擇器
- [ ] 用戶認證
- [ ] 數據持久化
- [ ] 性能優化
- [ ] 測試覆蓋

## 🛠️ 技術棧

### 後端
- **框架**: FastAPI
- **AI/ML**: LangChain, OpenAI, Sentence Transformers
- **文檔處理**: PyMuPDF, python-docx, PyYAML
- **數據處理**: Pandas, NumPy, Scikit-learn
- **圖像處理**: Pillow, svglib, reportlab
- **Web 自動化**: Selenium
- **文檔**: Swagger/OpenAPI

### 前端
- **框架**: React 18
- **構建工具**: Vite
- **UI 庫**: Ant Design
- **狀態管理**: React Hooks
- **HTTP 客戶端**: Axios
- **路由**: React Router
- **Markdown**: React Markdown

## 🐛 故障排除

### 常見問題

1. **後端啟動失敗**
   - 檢查 Python 虛擬環境是否激活
   - 確認所有依賴已安裝
   - 檢查端口 8000 是否被佔用

2. **前端啟動失敗**
   - 確認 Node.js 版本 >= 16
   - 刪除 node_modules 並重新安裝
   - 檢查端口 3000 是否被佔用

3. **API 連接失敗**
   - 確認後端服務正在運行
   - 檢查 CORS 配置
   - 查看瀏覽器控制台錯誤

### 日誌查看

- **後端日誌**: 查看後端終端窗口
- **前端日誌**: 查看瀏覽器開發者工具
- **API 請求**: 使用瀏覽器 Network 標籤

## 📞 支持

如果遇到問題，請：

1. 檢查本文檔的故障排除部分
2. 查看控制台錯誤信息
3. 確認所有服務正常運行
4. 重啟開發服務器

## 🔮 未來計劃

### 短期目標（1-2 週）
- [ ] 文獻助理頁面：實現 RAG 模式選擇
  - "允許延伸與推論" 模式
  - "僅嚴謹文獻溯源" 模式
- [ ] 恢復儀錶板功能
- [ ] 恢復文獻搜尋功能

### 中期目標（1 個月）
- [ ] 實驗顧問功能
  - 生成實驗表格
  - 自動 embedding
  - 串接 dual retriever
- [ ] 數據顯示和比較功能
- [ ] 提案選擇器功能

### 長期目標（2-3 個月）
- [ ] 用戶認證和權限管理
- [ ] 實時通知系統
- [ ] 數據可視化功能
- [ ] 多語言界面支持
- [ ] 移動端應用開發
- [ ] 雲端部署支持

---

**注意**: 這是 React 版本的開發版本，已從 Streamlit 成功遷移並恢復核心功能。建議同時保留原有的 Streamlit 版本作為備用。 