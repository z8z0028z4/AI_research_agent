# AI Research Assistant - 快速開始指南

## 🚀 首次安裝

### 1. 運行安裝腳本
```bash
.\simple_setup.bat
```

這個腳本會自動完成：
- ✅ 創建虛擬環境
- ✅ 安裝所有 Python 依賴
- ✅ 安裝前端依賴
- ✅ 創建環境配置文件
- ✅ 驗證所有依賴

### 2. 啟動應用程式
安裝完成後，您可以啟動 AI Research Assistant：

**啟動後端**：
```bash
.\restart_backend.bat
```

**啟動前端**：
```bash
.\start_react.bat
```

## 🔧 故障排除

### 如果應用程式無法啟動

**第一步：檢查依賴**
```bash
.\dependency_manager.bat
```

這個腳本會：
- 自動激活正確的虛擬環境
- 檢查所有 Python 依賴
- 檢查前端依賴
- 提供詳細的診斷信息

### 常見問題解決

**問題 1：`.venv_config` 文件不存在**
- **解決方案**：運行 `.\simple_setup.bat`

**問題 2：虛擬環境損壞**
- **解決方案**：刪除 `C:\ai_research_venv` 目錄，然後運行 `.\simple_setup.bat`

**問題 3：依賴缺失**
- **解決方案**：運行 `.\dependency_manager.bat` 查看具體問題，然後運行 `.\simple_setup.bat`

**問題 4：前端依賴問題**
- **解決方案**：進入 `frontend` 目錄，運行 `npm install`

## 📁 腳本說明

| 腳本 | 用途 | 何時使用 |
|------|------|----------|
| `simple_setup.bat` | 完整安裝 | 首次安裝或重新安裝 |
| `dependency_manager.bat` | 依賴檢查 | 故障排除時 |
| `restart_backend.bat` | 啟動後端 | 正常使用 |
| `start_react.bat` | 啟動前端 | 正常使用 |

## 🎯 最佳實踐

1. **首次使用**：總是先運行 `simple_setup.bat`
2. **遇到問題**：第一個除錯步驟就是運行 `dependency_manager.bat`
3. **重新安裝**：如果問題無法解決，刪除虛擬環境並重新運行 `simple_setup.bat`

## 📞 需要幫助？

如果遇到問題：
1. 運行 `.\dependency_manager.bat` 查看診斷信息
2. 檢查錯誤信息並按照提示操作
3. 如果問題持續，考慮重新運行 `.\simple_setup.bat`

