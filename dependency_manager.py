#!/usr/bin/env python3
"""
AI Research Assistant - Dependency Manager
整合的依賴檢查和自動修復工具
"""

import sys
import os
import importlib
import subprocess
import json
from pathlib import Path
from typing import List, Dict, Tuple

# Python 依賴定義
PYTHON_DEPS = {
    # 核心 AI 和 ML
    "langchain": ("langchain", "langchain"),
    "langchain_openai": ("langchain_openai", "langchain-openai"),
    "langchain_community": ("langchain_community", "langchain-community"),
    "langchain_core": ("langchain_core", "langchain-core"),
    "langchain_huggingface": ("langchain_huggingface", "langchain-huggingface"),
    "openai": ("openai", "openai"),
    
    # 向量數據庫和嵌入
    "chromadb": ("chromadb", "chromadb"),
    "sentence_transformers": ("sentence_transformers", "sentence-transformers"),
    "transformers": ("transformers", "transformers"),
    "tokenizers": ("tokenizers", "tokenizers"),
    "huggingface_hub": ("huggingface_hub", "huggingface-hub"),
    "einops": ("einops", "einops"),
    
    # 文檔處理
    "fitz": ("fitz", "PyMuPDF"),
    "docx": ("docx", "python-docx"),
    "openpyxl": ("openpyxl", "openpyxl"),
    "yaml": ("yaml", "PyYAML"),
    
    # 數據處理
    "pandas": ("pandas", "pandas"),
    "sklearn": ("sklearn", "scikit-learn"),
    "numpy": ("numpy", "numpy"),
    "scipy": ("scipy", "scipy"),
    
    # Web 框架
    "fastapi": ("fastapi", "fastapi"),
    "uvicorn": ("uvicorn", "uvicorn[standard]"),
    
    # HTTP 和網絡
    "requests": ("requests", "requests"),
    "certifi": ("certifi", "certifi"),
    
    # 圖像處理
    "PIL": ("PIL", "Pillow"),
    "svglib": ("svglib", "svglib"),
    "reportlab": ("reportlab", "reportlab"),
    
    # Web 自動化
    "selenium": ("selenium", "selenium"),
    
    # 環境和配置
    "dotenv": ("dotenv", "python-dotenv"),
    "pydantic": ("pydantic", "pydantic-settings"),
    
    # 進度追蹤
    "tqdm": ("tqdm", "tqdm"),
    
    # PyTorch
    "torch": ("torch", "torch"),
    "torchaudio": ("torchaudio", "torchaudio"),
    
    # 額外工具
    "urllib3": ("urllib3", "urllib3"),
    "bs4": ("bs4", "beautifulsoup4"),
    "lxml": ("lxml", "lxml"),
    
    # 可選依賴
    "aiofiles": ("aiofiles", "aiofiles"),
    "jose": ("jose", "python-jose[cryptography]"),
    "passlib": ("passlib", "passlib[bcrypt]"),
}

# 關鍵依賴（需要特殊處理）
CRITICAL_DEPS = [
    ("numpy", "numpy>=1.24.0"),
    ("scipy", "scipy>=1.11.0"),
    ("scikit-learn", "scikit-learn>=1.6.1"),
    ("torch", "torch>=2.0.0"),
    ("sentence-transformers", "sentence-transformers==5.0.0"),
    ("transformers", "transformers==4.53.2"),
    ("tokenizers", "tokenizers==0.21.2"),
    ("langchain-huggingface", "langchain-huggingface>=0.1.0"),
]

# 前端關鍵二進制文件
FRONTEND_CRITICAL_BINS = ["vite", "eslint", "tsc"]

def print_header(title: str):
    """打印標題"""
    print("=" * 80)
    print(f"AI Research Assistant - {title}")
    print("=" * 80)
    print()

def check_python_version() -> bool:
    """檢查 Python 版本"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 10):
        print(f"[ERROR] Python 3.10+ 需要，當前版本: {version.major}.{version.minor}.{version.micro}")
        return False
    print(f"[OK] Python {version.major}.{version.minor}.{version.micro} 版本相容")
    return True

def check_pip() -> bool:
    """檢查 pip 是否可用"""
    try:
        subprocess.run([sys.executable, "-m", "pip", "--version"], 
                      capture_output=True, check=True)
        print("[OK] pip 可用")
        return True
    except subprocess.CalledProcessError:
        print("[ERROR] pip 不可用")
        return False

def check_import(module_name: str, package_name: str) -> Tuple[bool, str]:
    """檢查模組是否可以導入"""
    try:
        importlib.import_module(module_name)
        return True, f"[OK] {package_name} 導入成功"
    except ImportError as e:
        return False, f"[ERROR] {package_name} 導入失敗: {str(e)}"
    except Exception as e:
        return False, f"[ERROR] {package_name} 導入錯誤: {str(e)}"

def get_package_version(package_name: str) -> str:
    """獲取已安裝套件的版本"""
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "show", package_name],
            capture_output=True,
            text=True,
            check=True
        )
        for line in result.stdout.split('\n'):
            if line.startswith('Version:'):
                return line.split(':', 1)[1].strip()
        return "Unknown"
    except subprocess.CalledProcessError:
        return "Not installed"

def run_pip_command(command: List[str]) -> bool:
    """執行 pip 命令"""
    try:
        print(f"執行: {' '.join(command)}")
        result = subprocess.run(
            [sys.executable, "-m", "pip"] + command,
            capture_output=True,
            text=True,
            check=True
        )
        print("[OK] 成功")
        return True
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] 失敗: {e.stderr}")
        return False

def install_critical_deps() -> bool:
    """安裝關鍵依賴"""
    print("安裝關鍵依賴...")
    print("-" * 40)
    
    success = True
    for module_name, package_spec in CRITICAL_DEPS:
        if not importlib.util.find_spec(module_name):
            print(f"安裝 {package_spec}...")
            if not run_pip_command(["install", package_spec]):
                success = False
        else:
            print(f"[OK] {module_name} 已安裝")
    
    return success

def install_pytorch_cuda() -> bool:
    """安裝 PyTorch with CUDA 支援"""
    print("安裝 PyTorch with CUDA 支援...")
    print("-" * 40)
    
    cuda_command = [
        "install", 
        "torch>=2.0.0", 
        "torchaudio==2.5.1+cu121",
        "--extra-index-url", 
        "https://download.pytorch.org/whl/cu121"
    ]
    
    if not run_pip_command(cuda_command):
        print("CUDA PyTorch 失敗，嘗試 CPU 版本...")
        return run_pip_command(["install", "torch>=2.0.0", "torchaudio>=2.0.0"])
    
    return True



def install_requirements() -> bool:
    """安裝 requirements.txt 中的依賴"""
    print("安裝 requirements.txt 中的依賴...")
    print("-" * 40)
    
    if Path("requirements.txt").exists():
        return run_pip_command(["install", "-r", "requirements.txt"])
    else:
        print("[ERROR] requirements.txt 不存在")
        return False

def check_python_dependencies() -> Tuple[bool, List[str]]:
    """檢查 Python 依賴"""
    print("檢查 Python 依賴...")
    print("-" * 40)
    
    missing_deps = []
    installed_deps = []
    
    for module_name, (import_name, package_name) in PYTHON_DEPS.items():
        success, message = check_import(import_name, package_name)
        if success:
            version = get_package_version(package_name)
            print(f"{message} (v{version})")
            
            # 特殊檢查 ChromaDB 版本
            if package_name == "chromadb":
                if version == "1.0.11":
                    print(f"  ✅ ChromaDB 版本 {version} 符合要求 (固定版本)")
                elif version.startswith("1."):
                    print(f"  ⚠️ ChromaDB 版本 {version} 不是固定版本")
                    print(f"  💡 建議安裝固定版本: pip install chromadb==1.0.11")
                elif version.startswith("0.4."):
                    print(f"  ⚠️ ChromaDB 版本 {version} 是舊版本")
                    print(f"  💡 建議升級: pip install chromadb==1.0.11")
                else:
                    print(f"  ⚠️ ChromaDB 版本 {version} 未知")
                    print(f"  💡 建議安裝固定版本: pip install chromadb==1.0.11")
            
            installed_deps.append(package_name)
        else:
            print(message)
            missing_deps.append(package_name)
    
    print(f"\n[INFO] 已安裝: {len(installed_deps)} 個依賴")
    if missing_deps:
        print(f"[WARN] 缺失: {len(missing_deps)} 個依賴")
    
    return len(missing_deps) == 0, missing_deps

def check_nodejs() -> bool:
    """檢查 Node.js"""
    try:
        result = subprocess.run(
            ["node", "--version"], 
            capture_output=True, 
            text=True, 
            check=True,
            shell=True
        )
        version = result.stdout.strip()
        print(f"[OK] Node.js 找到: {version}")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("[ERROR] Node.js 未找到或不在 PATH 中")
        print("請從 https://nodejs.org/ 安裝 Node.js")
        return False

def check_npm() -> bool:
    """檢查 npm"""
    try:
        result = subprocess.run(
            ["npm", "--version"], 
            capture_output=True, 
            text=True, 
            check=True,
            shell=True
        )
        version = result.stdout.strip()
        print(f"[OK] npm 找到: {version}")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("[ERROR] npm 未找到")
        return False

def check_frontend_dependencies() -> Tuple[bool, List[str]]:
    """檢查前端依賴"""
    print("檢查前端依賴...")
    print("-" * 40)
    
    frontend_dir = Path("frontend")
    if not frontend_dir.exists():
        print("[ERROR] frontend 目錄不存在")
        return False, ["frontend directory"]
    
    issues = []
    
    # 檢查 package.json
    package_json = frontend_dir / "package.json"
    if not package_json.exists():
        issues.append("package.json")
        print("[ERROR] package.json 不存在")
    else:
        try:
            with open(package_json, 'r', encoding='utf-8') as f:
                data = json.load(f)
            print(f"[OK] package.json 找到: {data.get('name', 'Unknown')} v{data.get('version', 'Unknown')}")
        except (json.JSONDecodeError, UnicodeDecodeError) as e:
            issues.append("invalid package.json")
            print(f"[ERROR] 無效的 package.json: {e}")
    
    # 檢查 node_modules
    node_modules = frontend_dir / "node_modules"
    if not node_modules.exists():
        issues.append("node_modules")
        print("[ERROR] node_modules 不存在")
    else:
        bin_dir = node_modules / ".bin"
        if not bin_dir.exists():
            issues.append("node_modules/.bin")
            print("[ERROR] node_modules/.bin 不存在")
        else:
            # 檢查關鍵二進制文件
            missing_bins = []
            for bin_name in FRONTEND_CRITICAL_BINS:
                bin_file = bin_dir / bin_name
                bin_cmd = bin_dir / f"{bin_name}.cmd"
                bin_ps1 = bin_dir / f"{bin_name}.ps1"
                if not bin_file.exists() and not bin_cmd.exists() and not bin_ps1.exists():
                    missing_bins.append(bin_name)
            
            if missing_bins:
                issues.append(f"missing binaries: {', '.join(missing_bins)}")
                print(f"[ERROR] 缺失關鍵二進制文件: {', '.join(missing_bins)}")
            else:
                print("[OK] node_modules 結構有效")
    
    # 檢查 vite.config.js
    vite_config = frontend_dir / "vite.config.js"
    if not vite_config.exists():
        issues.append("vite.config.js")
        print("[ERROR] vite.config.js 不存在")
    else:
        print("[OK] vite.config.js 找到")
    
    return len(issues) == 0, issues

def install_frontend_dependencies() -> bool:
    """安裝前端依賴"""
    print("安裝前端依賴...")
    print("-" * 40)
    
    frontend_dir = Path("frontend")
    if not frontend_dir.exists():
        print("[ERROR] frontend 目錄不存在")
        return False
    
    try:
        # 安裝依賴
        result = subprocess.run(
            ["npm", "install"],
            cwd=frontend_dir,
            capture_output=True,
            text=True,
            check=True,
            shell=True
        )
        print("[OK] 前端依賴安裝成功")
        
        # 修復安全漏洞
        print("檢查並修復安全漏洞...")
        try:
            audit_result = subprocess.run(
                ["npm", "audit", "fix"],
                cwd=frontend_dir,
                capture_output=True,
                text=True,
                shell=True
            )
            if audit_result.returncode == 0:
                print("[OK] 安全漏洞修復成功")
            else:
                print("[WARN] 部分安全漏洞無法自動修復")
        except Exception as e:
            print(f"[WARN] 安全漏洞檢查失敗: {e}")
        
        return True
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] 前端依賴安裝失敗: {e.stderr}")
        return False

def auto_fix_dependencies() -> bool:
    """自動修復依賴"""
    print("開始自動修復依賴...")
    print("-" * 40)
    
    # 升級 pip 和工具
    print("升級 pip 和構建工具...")
    if not run_pip_command(["install", "--upgrade", "pip"]):
        return False
    
    if not run_pip_command(["install", "--upgrade", "setuptools", "wheel"]):
        return False
    
    # 安裝關鍵依賴
    if not install_critical_deps():
        return False
    
    # 安裝 PyTorch
    if not install_pytorch_cuda():
        return False
    
    # 安裝 requirements.txt
    if not install_requirements():
        return False
    
    # 安裝前端依賴
    if check_nodejs() and check_npm():
        if not install_frontend_dependencies():
            print("[WARN] 前端依賴安裝失敗，但繼續進行")
    
    return True

def main():
    """主函數"""
    print_header("依賴管理器")
    
    # 檢查基本環境
    if not check_python_version():
        return 1
    
    if not check_pip():
        return 1
    
    print()
    
    # 檢查 Python 依賴
    python_ok, python_missing = check_python_dependencies()
    
    print()
    
    # 檢查前端依賴
    frontend_ok = True
    frontend_issues = []
    if check_nodejs() and check_npm():
        frontend_ok, frontend_issues = check_frontend_dependencies()
    else:
        frontend_ok = False
        frontend_issues = ["Node.js/npm not available"]
    
    print()
    print("=" * 80)
    print("依賴檢查總結")
    print("=" * 80)
    
    if python_ok and frontend_ok:
        print("[SUCCESS] 所有依賴都已準備就緒！")
        print("[OK] Python 依賴: 正常")
        print("[OK] 前端依賴: 正常")
        print()
        print("您現在可以運行 AI Research Assistant:")
        print("1. 啟動後端: 運行 restart_backend.bat")
        print("2. 啟動前端: 運行 start_react.bat")
        print("3. 或使用整合腳本: 運行 start_react.bat")
        return 0
    else:
        print("[WARN] 部分依賴缺失:")
        if not python_ok:
            print(f"   - Python 依賴缺失: {len(python_missing)} 個")
        if not frontend_ok:
            print(f"   - 前端依賴問題: {len(frontend_issues)} 個")
        
        print()
        print("自動修復缺失的依賴...")
        if auto_fix_dependencies():
            print()
            print("[SUCCESS] 依賴修復完成！")
            print("請重新運行此腳本檢查依賴狀態。")
            return 0
        else:
            print()
            print("[ERROR] 依賴修復失敗")
            return 1

if __name__ == "__main__":
    sys.exit(main()) 