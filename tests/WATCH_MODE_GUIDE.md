# 👀 Watch Mode 使用指南

## 🎯 什麼是 Watch Mode？

Watch Mode 是一個**自動化測試監控工具**，它會：
- 🔍 **監控文件變化**：自動檢測你修改的 Python 文件
- 🚀 **自動運行測試**：文件保存後立即運行相關測試
- ⚡ **即時反饋**：立即告訴你修改是否破壞了現有功能
- 🔄 **持續監控**：在開發過程中持續運行，直到你手動停止

## 🚀 核心價值

### 1. **即時反饋循環**
```
修改代碼 → 保存文件 → 自動測試 → 立即知道結果
```
- **傳統方式**：修改 → 手動運行測試 → 等待結果
- **Watch Mode**：修改 → 自動測試 → 即時反饋

### 2. **防止回歸錯誤**
- 確保新修改不會破壞現有功能
- 在問題剛出現時立即發現
- 避免累積多個錯誤後才發現

### 3. **提升開發效率**
- 減少手動操作
- 專注於代碼邏輯，不用記住何時測試
- 快速迭代和調試

## 📋 使用方法

### 基本用法
```bash
# 在 tests/ 目錄中運行
python test_watch.py
```

### 進階選項
```bash
# 只運行快速測試（推薦開發時使用）
python test_watch.py --fast

# 運行完整測試套件
python test_watch.py --full

# 包含覆蓋率報告
python test_watch.py --coverage

# 失敗時自動重試
python test_watch.py --retry

# 只運行一次測試（不監控）
python test_watch.py --once
```

### 通過測試菜單使用
1. 運行 `run_tests.bat`
2. 選擇 `7. 👀 Watch Mode`
3. 選擇監控模式：
   - **Fast tests only** (推薦)
   - **Full tests with coverage**
   - **Custom watch settings**

## 🔧 工作原理

### 監控範圍
- **後端代碼**：`../backend/` 目錄下的所有 Python 文件
- **測試文件**：當前 `tests/` 目錄下的 Python 文件
- **忽略文件**：測試文件本身的變化（避免無限循環）

### 觸發條件
- 保存 `.py` 文件時自動觸發
- 有 2 秒冷卻時間，避免過於頻繁的測試
- 延遲 1 秒執行，確保文件完全保存

### 測試類型
- **Fast Mode**：只運行標記為 `@pytest.mark.fast` 的測試
- **Full Mode**：運行所有測試
- **Coverage Mode**：包含代碼覆蓋率分析

## 💡 實際使用場景

### 場景 1：開發新功能
```python
# 1. 啟動 Watch Mode
python test_watch.py --fast

# 2. 修改 backend/services/new_service.py
def new_function():
    return "new feature"

# 3. 保存文件 → 自動測試運行
# 4. 立即看到結果：✅ 或 ❌
```

### 場景 2：修復 Bug
```python
# 1. 發現 Bug，啟動 Watch Mode
python test_watch.py --fast

# 2. 修改有問題的代碼
def fix_bug():
    # 修復邏輯
    pass

# 3. 保存 → 自動測試 → 確認修復
```

### 場景 3：重構代碼
```python
# 1. 啟動完整測試監控
python test_watch.py --full

# 2. 重構代碼結構
# 3. 每次保存都確保所有功能正常
```

## ⚙️ 配置選項

### 測試冷卻時間
```python
# 在 test_watch.py 中修改
self.test_cooldown = 2  # 秒，避免過於頻繁的測試
```

### 監控目錄
```python
# 可以添加更多監控目錄
observer.schedule(event_handler, "path/to/other/dir", recursive=True)
```

### 忽略文件模式
```python
# 可以自定義忽略的文件模式
if any(pattern in file_path.name for pattern in ['temp_', 'backup_']):
    return
```

## 🎯 最佳實踐

### 1. **開發階段使用 Fast Mode**
- 快速反饋，不等待完整測試
- 專注於當前修改的功能

### 2. **提交前使用 Full Mode**
- 確保所有功能正常
- 包含覆蓋率檢查

### 3. **調試時使用 Retry Mode**
- 自動重試失敗的測試
- 快速定位問題

### 4. **團隊協作時**
- 每個開發者可以獨立使用
- 不影響其他人的開發環境

## 🚨 注意事項

### 性能考慮
- **Fast Mode**：適合日常開發，執行時間 < 30秒
- **Full Mode**：適合重要修改，執行時間 2-5分鐘
- **Coverage Mode**：適合品質檢查，執行時間 3-8分鐘

### 資源使用
- 持續監控會消耗少量 CPU 和內存
- 測試運行時會消耗更多資源
- 建議在性能較好的機器上使用

### 網絡依賴
- 某些測試需要網絡連接（API 測試）
- 離線開發時可能無法運行完整測試

## 🔄 與其他工具的整合

### IDE 整合
- 大多數 IDE 支持文件監控
- 可以與 IDE 的測試運行器配合使用

### CI/CD 整合
- Watch Mode 主要用於本地開發
- CI/CD 使用不同的測試策略

### 版本控制
- 建議在 `.gitignore` 中忽略測試產生的臨時文件
- Watch Mode 不會影響版本控制

## 📊 效果評估

### 開發效率提升
- **傳統方式**：手動測試，平均每次 2-3 分鐘
- **Watch Mode**：自動測試，節省 80% 的手動操作時間

### 錯誤發現速度
- **傳統方式**：可能在提交時才發現問題
- **Watch Mode**：修改後立即發現問題

### 代碼品質
- 持續測試確保代碼穩定性
- 減少回歸錯誤
- 提高代碼信心

---

**總結**：Watch Mode 是現代開發工作流程的重要工具，特別適合需要頻繁修改和測試的項目。它能顯著提升開發效率和代碼品質。