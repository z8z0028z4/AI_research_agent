#!/usr/bin/env python3
"""
測試運行腳本
==========

提供多種測試運行選項：
1. 快速測試 - 只運行單元測試
2. 完整測試 - 運行所有測試
3. 覆蓋率測試 - 生成覆蓋率報告
4. 特定模組測試 - 測試特定功能
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path

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

def run_quick_tests():
    """運行快速測試（單元測試）"""
    command = "pytest tests/test_core_modules.py -v --tb=short"
    return run_command(command, "快速測試 - 核心模組單元測試")

def run_integration_tests():
    """運行整合測試"""
    command = "pytest tests/test_services.py -v --tb=short"
    return run_command(command, "整合測試 - 服務層測試")

def run_api_tests():
    """運行 API 測試"""
    command = "pytest tests/test_api.py -v --tb=short"
    return run_command(command, "API 測試 - 端點功能測試")

def run_e2e_tests():
    """運行端到端測試"""
    command = "pytest tests/test_e2e.py -v --tb=short"
    return run_command(command, "端到端測試 - 完整流程測試")

def run_all_tests():
    """運行所有測試"""
    command = "pytest tests/ -v --tb=short"
    return run_command(command, "完整測試 - 所有測試套件")

def run_coverage_tests():
    """運行覆蓋率測試"""
    command = "pytest tests/ --cov=backend --cov-report=html --cov-report=term-missing -v"
    return run_command(command, "覆蓋率測試 - 生成覆蓋率報告")

def run_specific_test(test_path):
    """運行特定測試"""
    command = f"pytest {test_path} -v --tb=short"
    return run_command(command, f"特定測試 - {test_path}")

def run_performance_tests():
    """運行性能測試"""
    command = "pytest tests/test_e2e.py::TestPerformance -v --tb=short"
    return run_command(command, "性能測試 - 系統性能測試")

def run_security_tests():
    """運行安全測試"""
    command = "pytest tests/test_e2e.py::TestSecurity -v --tb=short"
    return run_command(command, "安全測試 - 安全性測試")

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
    parser = argparse.ArgumentParser(description="AI Research Agent 測試運行器")
    parser.add_argument("--type", choices=["quick", "integration", "api", "e2e", "all", "coverage", "performance", "security"], 
                       default="quick", help="測試類型")
    parser.add_argument("--test", help="運行特定測試文件或測試函數")
    parser.add_argument("--check-deps", action="store_true", help="檢查測試依賴")
    
    args = parser.parse_args()
    
    print("🧪 AI Research Agent 測試運行器")
    print("=" * 60)
    
    # 檢查依賴
    if args.check_deps or not check_dependencies():
        if not check_dependencies():
            return 1
    
    # 根據參數運行測試
    success = True
    
    if args.test:
        success = run_specific_test(args.test)
    elif args.type == "quick":
        success = run_quick_tests()
    elif args.type == "integration":
        success = run_integration_tests()
    elif args.type == "api":
        success = run_api_tests()
    elif args.type == "e2e":
        success = run_e2e_tests()
    elif args.type == "all":
        success = run_all_tests()
    elif args.type == "coverage":
        success = run_coverage_tests()
    elif args.type == "performance":
        success = run_performance_tests()
    elif args.type == "security":
        success = run_security_tests()
    
    # 顯示結果
    print("\n" + "=" * 60)
    if success:
        print("🎉 測試完成！")
        print("✅ 所有測試通過")
    else:
        print("💥 測試失敗！")
        print("❌ 請檢查錯誤信息並修復問題")
    
    print("=" * 60)
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main()) 