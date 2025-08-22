@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo.
echo ========================================
echo 📊 AI Research Agent 覆蓋率測試
echo ========================================
echo.

:: 檢查環境
if not exist "test_core_modules.py" (
    echo ❌ 錯誤：請在 tests/ 目錄中運行此腳本
    pause
    exit /b 1
)

echo 🔍 檢查測試環境...
python -c "import pytest" >nul 2>&1
if errorlevel 1 (
    echo ❌ 錯誤：找不到 pytest
    echo 請安裝：pip install pytest
    pause
    exit /b 1
)

python -c "import pytest_cov" >nul 2>&1
if errorlevel 1 (
    echo ⚠️  警告：找不到 pytest-cov
    echo 正在安裝：pip install pytest-cov
    pip install pytest-cov
    if errorlevel 1 (
        echo ❌ 安裝失敗
        pause
        exit /b 1
    )
)

echo ✅ 環境檢查完成
echo.

echo 📊 開始覆蓋率測試...
echo ========================================

:: 清理舊的覆蓋率報告
if exist "..\htmlcov" (
    echo 🧹 清理舊的覆蓋率報告...
    rmdir /s /q "..\htmlcov"
)

:: 運行覆蓋率測試
echo 🔍 運行測試並收集覆蓋率數據...
python -m pytest . --cov=..\backend --cov-report=html --cov-report=term-missing --cov-report=xml -v

if errorlevel 1 (
    echo.
    echo ❌ 覆蓋率測試失敗！
    echo 請檢查錯誤信息並修復問題
    goto end
)

echo.
echo ✅ 覆蓋率測試完成！
echo.

:: 顯示覆蓋率摘要
echo 📊 覆蓋率摘要：
echo ========================================
if exist "..\htmlcov\index.html" (
    echo ✅ HTML 報告已生成：..\htmlcov\index.html
) else (
    echo ❌ HTML 報告生成失敗
)

if exist "..\coverage.xml" (
    echo ✅ XML 報告已生成：..\coverage.xml
) else (
    echo ❌ XML 報告生成失敗
)

echo.
echo 📈 覆蓋率目標：
echo - 代碼覆蓋率: > 90%
echo - 分支覆蓋率: > 85%
echo - 函數覆蓋率: > 95%
echo.

:: 檢查覆蓋率是否達標
echo 🔍 檢查覆蓋率是否達標...
python -c "
import xml.etree.ElementTree as ET
try:
    tree = ET.parse('../coverage.xml')
    root = tree.getroot()
    for package in root.findall('.//package'):
        line_rate = float(package.get('line-rate', 0))
        branch_rate = float(package.get('branch-rate', 0))
        print(f'📊 行覆蓋率: {line_rate:.1%}')
        print(f'📊 分支覆蓋率: {branch_rate:.1%}')
        
        if line_rate < 0.9:
            print('⚠️  行覆蓋率未達標 (< 90%)')
        else:
            print('✅ 行覆蓋率達標')
            
        if branch_rate < 0.85:
            print('⚠️  分支覆蓋率未達標 (< 85%)')
        else:
            print('✅ 分支覆蓋率達標')
except Exception as e:
    print(f'❌ 無法解析覆蓋率報告: {e}')
"

echo.
echo 💡 使用建議：
echo 1. 打開 ..\htmlcov\index.html 查看詳細報告
echo 2. 關注紅色標記的未覆蓋代碼
echo 3. 為未覆蓋的功能添加測試用例
echo 4. 定期運行覆蓋率測試監控質量
echo.

:end
pause 