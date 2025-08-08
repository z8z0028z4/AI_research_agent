# Changelog

## [React Version - 2024-01-XX]

### 🎉 重大更新：從 Streamlit 遷移到 React 前端

#### ✨ 新增功能
- **React 前端架構**：使用 React 18 + Vite + Ant Design
- **現代化 UI/UX**：響應式設計，流暢動畫，更好的用戶體驗
- **智能文本清理**：自動移除 markdown 格式，確保 DOCX 輸出乾淨
- **提案修訂功能**：支持基於用戶反饋的提案修訂
- **實驗細節生成**：獨立的實驗細節生成功能
- **DOCX 下載**：完整的 Word 文檔生成和下載
- **化學品查詢**：完整的化學品信息顯示和安全圖標

#### 🔧 技術改進
- **後端 API 重構**：使用 FastAPI 提供 RESTful API
- **模塊化架構**：組件化開發，更好的代碼組織
- **狀態管理**：使用 React Hooks 進行狀態管理
- **開發體驗**：熱重載，TypeScript 支持，ESLint 檢查
- **性能優化**：更快的加載速度和響應性

#### 🐛 修復
- 修復了 markdown 格式在 DOCX 中的顯示問題
- 修復了文本換行和寬度適配問題
- 修復了實驗細節生成的格式問題

#### 📦 依賴更新
- 新增 Node.js 16+ 依賴
- 新增 React 18 和相關前端依賴
- 更新 Python 依賴到最新穩定版本
- 新增 svglib 用於 SVG 到 PNG 轉換

#### 🚀 部署改進
- 一鍵安裝腳本：`install.bat`
- 一鍵啟動腳本：`start_react_app.bat`
- 自動依賴檢查和安裝
- 開發和生產環境配置

#### 📋 待實現功能
- 文獻助理頁面（RAG 模式選擇）
- 儀錶板功能恢復
- 文獻搜尋功能恢復
- 文件上傳處理
- 實驗顧問功能
- 數據顯示和比較
- 提案選擇器

---

## [Previous Versions]

### [0.1.0] - 2024-01-XX
- Initial Streamlit version
- Basic research proposal generation
- Chemical information lookup
- Document processing capabilities 