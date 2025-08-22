#!/usr/bin/env python3
"""
AI研究助理 - 統一測試入口
========================

提供多種測試運行選項：
- quick: 快速測試（核心功能）
- all: 完整測試（所有功能）
- coverage: 覆蓋率測試
- api: API端點測試
- e2e: 端到端測試
"""

import sys
import subprocess
import argparse

def run_command(command, description):
    """運行命令並顯示結果"""
    print(f"\n{'='*60}")
    print(f"🚀 {description}")
    print(f"{'='*60}")
    print(f"執行命令: {command}")
    print("-" * 60)
    
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print("✅ 命令執行成功")
        if result.stdout:
            print("輸出:")
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print("❌ 命令執行失敗")
        print(f"錯誤代碼: {e.returncode}")
        if e.stdout:
            print("標準輸出:")
            print(e.stdout)
        if e.stderr:
            print("錯誤輸出:")
            print(e.stderr)
        return False

def run_tests(test_type="quick"):
    """根據類型運行對應的測試"""
    test_commands = {
        "quick": ("pytest tests/test_core_modules.py -v --tb=short", "快速測試 - 核心功能"),
        "all": ("pytest tests/ -v --tb=short", "完整測試 - 所有功能"),
        "coverage": ("pytest tests/ --cov=backend --cov-report=html --cov-report=term-missing -v", "覆蓋率測試"),
        "api": ("pytest tests/test_api.py -v --tb=short", "API測試"),
        "e2e": ("pytest tests/test_e2e_real.py -v --tb=short", "端到端測試"),
        "services": ("pytest tests/ -k \"test_services\" -v --tb=short", "服務層測試"),
        "core": ("pytest tests/ -k \"test_core\" -v --tb=short", "核心模組測試"),
        "utils": ("pytest tests/test_utils.py -v --tb=short", "工具函數測試"),
        "frontend": ("pytest tests/ -k \"test_frontend\" -v --tb=short", "前端組件測試")
    }
    
    if test_type in test_commands:
        command, description = test_commands[test_type]
        return run_command(command, description)
    else:
        # 自定義測試路徑
        command = f"pytest {test_type} -v --tb=short"
        return run_command(command, f"自定義測試 - {test_type}")

def check_dependencies():
    """檢查測試依賴"""
    print("\n🔍 檢查測試依賴...")
    
    required_packages = [
        "pytest",
        "pytest-cov",
        "fastapi",
        "httpx"
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} - 未安裝")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n⚠️ 缺少依賴包: {', '.join(missing_packages)}")
        print("請運行: pip install " + " ".join(missing_packages))
        return False
    
    print("✅ 所有依賴包已安裝")
    return True

def main():
    """主函數"""
    parser = argparse.ArgumentParser(description="AI研究助理 - 統一測試入口")
    parser.add_argument("--type", choices=["quick", "all", "coverage", "api", "e2e", "services", "core", "utils", "frontend"], 
                       default="quick", help="測試類型")
    parser.add_argument("--test", help="運行特定測試文件或測試函數")
    parser.add_argument("--check-deps", action="store_true", help="檢查測試依賴")
    
    args = parser.parse_args()
    
    print("🧪 AI研究助理 - 統一測試入口")
    print("=" * 50)
    
    # 檢查依賴
    if args.check_deps:
        return 0 if check_dependencies() else 1
    
    if not check_dependencies():
        return 1
    
    # 運行測試
    if args.test:
        success = run_tests(args.test)
    else:
        success = run_tests(args.type)
    
    # 顯示結果
    print("\n" + "=" * 50)
    if success:
        print("🎉 測試完成！")
        print("✅ 所有測試通過")
    else:
        print("💥 測試失敗！")
        print("❌ 請檢查錯誤信息並修復問題")
    
    print("=" * 50)
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main()) 