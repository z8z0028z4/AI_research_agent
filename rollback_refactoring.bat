@echo off
echo ========================================
echo AI Research Agent - 重構回滾腳本
echo ========================================
echo.

echo 正在檢查 Git 狀態...
git status

echo.
echo 請選擇回滾選項：
echo 1. 回滾到重構前的提交 (推薦)
echo 2. 刪除新增的目錄和文件
echo 3. 查看重構前的提交歷史
echo 4. 退出
echo.

set /p choice="請輸入選項 (1-4): "

if "%choice%"=="1" (
    echo.
    echo 正在查找重構前的提交...
    git log --oneline -10
    
    echo.
    set /p commit_hash="請輸入要回滾到的提交哈希 (或按 Enter 使用最新的提交): "
    
    if "%commit_hash%"=="" (
        echo 使用最新的提交...
        git reset --hard HEAD~1
    ) else (
        echo 回滾到提交: %commit_hash%
        git reset --hard %commit_hash%
    )
    
    echo.
    echo 回滾完成！
    echo 請檢查代碼狀態是否正確。
    
) else if "%choice%"=="2" (
    echo.
    echo 正在刪除新增的目錄和文件...
    
    if exist "app\core" (
        echo 刪除 app\core 目錄...
        rmdir /s /q "app\core"
    )
    
    if exist "app\services" (
        echo 刪除 app\services 目錄...
        rmdir /s /q "app\services"
    )
    
    if exist "app\utils" (
        echo 刪除 app\utils 目錄...
        rmdir /s /q "app\utils"
    )
    
    if exist "app\types" (
        echo 刪除 app\types 目錄...
        rmdir /s /q "app\types"
    )
    
    if exist "app\config" (
        echo 刪除 app\config 目錄...
        rmdir /s /q "app\config"
    )
    
    if exist ".vscode" (
        echo 刪除 .vscode 目錄...
        rmdir /s /q ".vscode"
    )
    
    if exist "setup.py" (
        echo 刪除 setup.py...
        del "setup.py"
    )
    
    if exist "pyrightconfig.json" (
        echo 刪除 pyrightconfig.json...
        del "pyrightconfig.json"
    )
    
    if exist ".pre-commit-config.yaml" (
        echo 刪除 .pre-commit-config.yaml...
        del ".pre-commit-config.yaml"
    )
    
    echo.
    echo 刪除完成！
    echo 注意：此操作不會恢復原始文件，建議使用選項 1 進行完整回滾。
    
) else if "%choice%"=="3" (
    echo.
    echo 顯示最近的提交歷史：
    git log --oneline -20
    
) else if "%choice%"=="4" (
    echo 退出回滾腳本。
    exit /b 0
    
) else (
    echo 無效的選項，請重新運行腳本。
    exit /b 1
)

echo.
echo 回滾操作完成！
pause
