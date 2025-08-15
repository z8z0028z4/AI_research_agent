# AI Research Assistant 啟動指南

## 🚀 推薦啟動方式

### 方式1：一鍵啟動（推薦）
```bash
# 在項目根目錄執行
start_ai_assistant.bat
```

**特點**：
- ✅ 同時啟動前後端
- ✅ 已修復後端重啟問題
- ✅ 使用優化版主程式
- ✅ 自動設置環境變量

### 方式2：使用修復版 React 啟動器
```bash
# 在項目根目錄執行
start_react.bat
```

**特點**：
- ✅ 同時啟動前後端
- ✅ 已修復後端重啟問題
- ✅ 保持原有啟動邏輯

### 方式3：分別啟動

#### 啟動後端（修復版）
```bash
# 在 backend 目錄執行
start_backend_fixed.bat
```

#### 啟動前端
```bash
# 在 frontend 目錄執行
run_frontend.bat
```

## 🔧 修復內容

### 後端重啟問題解決
1. **異步初始化向量統計**
   - 服務器快速啟動（1-2秒）
   - 向量統計在後台異步執行
   - 不阻塞主服務器啟動

2. **排除數據庫文件監控**
   - 不再監控 `experiment_data/**`
   - 不再監控 `*.sqlite3` 和 `*.db`
   - 正常的向量增加操作不會觸發重啟

3. **延遲重載機制**
   - `reload_delay=2.0` 避免頻繁重啟
   - 給文件系統穩定時間

## 📊 啟動效果對比

### 修復前（問題狀態）
```
🚀 開始初始化向量統計信息...
✅ 向量統計初始化完成，耗時: 10.96秒
WARNING: WatchFiles detected changes... Reloading...
INFO: Shutting down
INFO: Started server process [33256]
🚀 開始初始化向量統計信息...  # 重複循環
```

### 修復後（正常狀態）
```
🚀 AI Research Assistant 後端服務啟動中...
✅ 後端服務啟動完成（向量統計在後台初始化中）
INFO: Application startup complete.
🚀 開始異步初始化向量統計信息...  # 後台執行
✅ 向量統計異步初始化完成，耗時: 9.26秒
```

## 🌐 服務地址

啟動成功後，可以訪問以下地址：

- **前端應用**: http://localhost:3000
- **後端 API**: http://localhost:8000
- **API 文檔**: http://localhost:8000/api/docs
- **健康檢查**: http://localhost:8000/health

## 📝 注意事項

1. **虛擬環境**：腳本會自動檢查和設置虛擬環境
2. **依賴項**：確保已安裝所有必要的 Python 套件
3. **端口佔用**：確保 3000 和 8000 端口未被佔用
4. **向量統計**：啟動後會在後台初始化，可以通過 `/health` 查看狀態

## 🔍 故障排除

### 問題1：後端仍然重啟
**解決方案**：確保使用 `main_optimized:app` 而不是 `main:app`

### 問題2：端口被佔用
**解決方案**：
```bash
# 查看端口佔用
netstat -ano | findstr :8000
netstat -ano | findstr :3000

# 終止進程
taskkill /PID <進程ID> /F
```

### 問題3：依賴項缺失
**解決方案**：
```bash
# 在 backend 目錄執行
pip install -r requirements.txt

# 在 frontend 目錄執行
npm install
```

## ✅ 驗證啟動成功

1. **後端檢查**：訪問 http://localhost:8000/health
2. **前端檢查**：訪問 http://localhost:3000
3. **API 文檔**：訪問 http://localhost:8000/api/docs
4. **日誌檢查**：查看後端窗口的啟動日誌

## 🎯 最佳實踐

1. **使用推薦啟動方式**：`start_ai_assistant.bat`
2. **保持虛擬環境**：定期更新依賴項
3. **監控日誌**：注意啟動過程中的警告和錯誤
4. **定期重啟**：長時間運行後建議重啟服務
