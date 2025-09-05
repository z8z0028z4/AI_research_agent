# 🧪 測試工作流程指南 - 讓測試成為開發的核心

## 🎯 測試檔的正確使用時機

### 1. **開發前測試 (TDD - Test Driven Development)**
```
✅ 正確做法：
1. 先寫測試，定義期望的行為
2. 運行測試，確認失敗
3. 寫最少的代碼讓測試通過
4. 重構代碼，保持測試通過

❌ 錯誤做法：
- 先寫功能，再補測試
- 測試只是為了應付要求
```

### 2. **功能修改時的測試流程**
```
修改前：
1. 運行相關測試，確認當前狀態
2. 記錄測試結果作為基準

修改中：
1. 每次小修改後運行快速測試
2. 使用 watch 模式自動測試

修改後：
1. 運行完整測試套件
2. 檢查是否有回歸問題
3. 更新或新增測試案例
```

### 3. **日常開發的測試時機**

#### 🚀 每次提交前
```bash
# 快速測試 - 30秒內完成
pytest -m fast --tb=short

# 如果快速測試通過，運行完整測試
pytest --tb=short
```

#### 🔄 持續開發中
```bash
# 監控模式 - 自動運行測試
pytest-watch tests/ -- -m fast

# 或使用 VS Code 的測試擴展
# 在編輯器中直接運行測試
```

#### 📦 發布前
```bash
# 完整測試套件
pytest --cov=../backend --cov-report=html

# 端到端測試
pytest tests/e2e/ -v

# 前端測試
npm test  # 在 frontend/ 目錄
```

## 🛠️ 實用的測試工作流程

### 工作流程 1: 新功能開發
```bash
# 1. 創建功能分支
git checkout -b feature/new-functionality

# 2. 寫測試 (TDD)
# 編輯 test_*.py 文件，定義期望行為

# 3. 運行測試，確認失敗
pytest tests/test_new_feature.py -v

# 4. 實現功能
# 編輯對應的 .py 文件

# 5. 運行測試，確認通過
pytest tests/test_new_feature.py -v

# 6. 運行相關測試，確認無回歸
pytest -m related --tb=short

# 7. 提交代碼
git add .
git commit -m "feat: add new functionality with tests"
```

### 工作流程 2: 修復 Bug
```bash
# 1. 重現 Bug
# 手動測試或寫重現測試

# 2. 寫失敗測試案例
# 在對應測試文件中添加測試

# 3. 運行測試，確認失敗
pytest tests/test_bug_fix.py::test_bug_reproduction -v

# 4. 修復 Bug
# 修改代碼

# 5. 運行測試，確認修復
pytest tests/test_bug_fix.py::test_bug_reproduction -v

# 6. 運行完整測試，確認無副作用
pytest --tb=short
```

### 工作流程 3: 重構代碼
```bash
# 1. 確保現有測試覆蓋率高
pytest --cov=../backend --cov-report=term-missing

# 2. 運行所有測試，記錄基準
pytest > test_baseline.txt

# 3. 進行重構
# 修改代碼結構

# 4. 每次修改後運行測試
pytest --tb=short

# 5. 比較結果
diff test_baseline.txt <(pytest)
```

## 📋 測試檢查清單

### 開發前檢查
- [ ] 相關測試是否已存在？
- [ ] 是否需要新增測試案例？
- [ ] 測試環境是否準備好？

### 開發中檢查
- [ ] 每次修改後是否運行快速測試？
- [ ] 新功能是否有對應測試？
- [ ] 測試是否覆蓋邊界情況？

### 提交前檢查
- [ ] 所有測試是否通過？
- [ ] 測試覆蓋率是否足夠？
- [ ] 是否有新增的測試案例？

### 發布前檢查
- [ ] 完整測試套件是否通過？
- [ ] 端到端測試是否通過？
- [ ] 性能測試是否通過？

## 🎯 實用的測試命令

### 快速測試命令
```bash
# 單元測試 (快速)
pytest -m "fast and not slow" --tb=short

# 特定模組測試
pytest tests/test_core_modules.py -v

# 特定測試方法
pytest tests/test_core_modules.py::TestConfigManagement::test_settings_loading -v

# 失敗的測試
pytest --lf -v

# 上次失敗的測試
pytest --ff -v
```

### 監控模式
```bash
# 自動運行測試 (需要安裝 pytest-watch)
pip install pytest-watch
ptw tests/ -- -m fast

# 或使用 VS Code 測試擴展
# 在測試文件中點擊 "Run Test" 按鈕
```

### 覆蓋率測試
```bash
# 生成覆蓋率報告
pytest --cov=../backend --cov-report=html --cov-report=term-missing

# 檢查覆蓋率閾值
pytest --cov=../backend --cov-fail-under=80
```

## 🔧 測試工具整合

### VS Code 設置
```json
{
    "python.testing.pytestEnabled": true,
    "python.testing.unittestEnabled": false,
    "python.testing.pytestArgs": [
        "tests"
    ],
    "python.testing.autoTestDiscoverOnSaveEnabled": true
}
```

### Git Hooks (可選)
```bash
# .git/hooks/pre-commit
#!/bin/bash
echo "Running tests before commit..."
pytest -m fast --tb=short
if [ $? -ne 0 ]; then
    echo "Tests failed! Commit aborted."
    exit 1
fi
echo "Tests passed! Proceeding with commit."
```

### CI/CD 整合
```yaml
# .github/workflows/test.yml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.9
    - name: Install dependencies
      run: pip install -r requirements.txt
    - name: Run tests
      run: pytest --cov=backend --cov-report=xml
```

## 🚨 常見問題解決

### 問題 1: 測試運行太慢
**解決方案:**
```bash
# 使用並行測試
pytest -n auto

# 只運行快速測試
pytest -m fast

# 使用緩存
pytest --cache-clear  # 清除緩存
```

### 問題 2: 測試不穩定
**解決方案:**
```bash
# 重複運行測試
pytest --count=3 tests/test_flaky.py

# 使用隨機種子
pytest --randomly-seed=42
```

### 問題 3: 測試環境問題
**解決方案:**
```bash
# 檢查測試環境
python -c "import backend.core.config; print('Environment OK')"

# 重新設置測試環境
python tests/setup_test_env.py
```

## 📊 測試指標追蹤

### 每日測試報告
```bash
# 生成測試報告
pytest --junitxml=test-results.xml --cov=../backend --cov-report=html

# 查看測試趨勢
python tests/analyze_test_trends.py
```

### 測試覆蓋率目標
- 核心模組: 90%+
- 服務層: 80%+
- API層: 85%+
- 整體: 80%+

## 🎉 成功案例

### 案例 1: 新功能開發
```
✅ 使用 TDD 開發文字反白功能
- 先寫測試定義期望行為
- 實現功能讓測試通過
- 重構代碼保持測試通過
- 結果: 功能穩定，Bug 少
```

### 案例 2: Bug 修復
```
✅ 修復配置加載問題
- 寫重現測試案例
- 修復問題
- 確認測試通過
- 運行完整測試確認無回歸
- 結果: 問題徹底解決
```

### 案例 3: 重構優化
```
✅ 重構向量存儲模組
- 確保測試覆蓋率 90%+
- 逐步重構，每次運行測試
- 保持功能不變
- 結果: 代碼更清晰，性能提升
```

---

## 📞 需要幫助？

如果您在使用測試時遇到問題：

1. **查看測試文檔**: `tests/README_TESTING.md`
2. **運行診斷**: `python tests/run_tests.py --diagnose`
3. **檢查環境**: `python tests/check_test_env.py`
4. **查看示例**: `tests/examples/`

記住：**好的測試不是負擔，而是開發的助力！** 🚀 