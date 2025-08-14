#!/usr/bin/env python3
"""
SI 文件打開問題檢測腳本
====================

逐步檢測第三個 SI 文件的問題
"""

import os
import sys
import requests
import urllib.parse
from pathlib import Path

def test_file_existence():
    """檢測文件是否存在"""
    print("🔍 步驟 1: 檢測文件是否存在")
    
    # 獲取項目根目錄
    current_dir = os.path.dirname(os.path.abspath(__file__))
    papers_dir = os.path.join(current_dir, "experiment_data", "papers")
    
    si_filename = "107_Welding_Metallophthalocyanines_into_Bimetallic_Molecular_Meshes_for_Ultrasensiti_SI.pdf"
    file_path = os.path.join(papers_dir, si_filename)
    
    print(f"📁 檢查路徑: {file_path}")
    
    if os.path.exists(file_path):
        print(f"✅ 文件存在")
        file_size = os.path.getsize(file_path)
        print(f"📊 文件大小: {file_size:,} bytes ({file_size/1024/1024:.2f} MB)")
        return file_path
    else:
        print(f"❌ 文件不存在")
        return None

def test_file_extension_detection(file_path):
    """檢測文件擴展名識別"""
    print("\n🔍 步驟 2: 檢測文件擴展名識別")
    
    filename = os.path.basename(file_path)
    print(f"📄 文件名: {filename}")
    
    # 測試不同的擴展名檢測方法
    methods = [
        ("os.path.splitext", lambda f: os.path.splitext(f)[1].lower()),
        ("endswith _si.pdf", lambda f: '.pdf' if f.lower().endswith('_si.pdf') else os.path.splitext(f)[1].lower()),
        ("endswith _SI.pdf", lambda f: '.pdf' if f.lower().endswith('_si.pdf') else os.path.splitext(f)[1].lower()),
    ]
    
    for method_name, method_func in methods:
        try:
            result = method_func(filename)
            print(f"🔧 {method_name}: {result}")
        except Exception as e:
            print(f"❌ {method_name}: 錯誤 - {e}")
    
    return filename

def test_backend_api_response():
    """測試後端 API 響應"""
    print("\n🔍 步驟 3: 測試後端 API 響應")
    
    # 假設後端運行在 localhost:8000
    base_url = "http://localhost:8000"
    api_url = f"{base_url}/api/v1/documents/107_Welding_Metallophthalocyanines_into_Bimetallic_Molecular_Meshes_for_Ultrasensiti_SI.pdf"
    
    print(f"🌐 測試 URL: {api_url}")
    
    try:
        response = requests.get(api_url, timeout=10)
        print(f"📊 響應狀態碼: {response.status_code}")
        print(f"📋 響應頭:")
        for header, value in response.headers.items():
            print(f"   {header}: {value}")
        
        if response.status_code == 200:
            print(f"✅ API 響應成功")
            print(f"📄 內容類型: {response.headers.get('Content-Type', 'Unknown')}")
            print(f"📎 Content-Disposition: {response.headers.get('Content-Disposition', 'Not set')}")
        else:
            print(f"❌ API 響應失敗")
            print(f"📝 錯誤內容: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ 無法連接到後端服務器")
        print("💡 請確保後端服務正在運行")
    except Exception as e:
        print(f"❌ 請求失敗: {e}")

def test_url_encoding():
    """測試 URL 編碼"""
    print("\n🔍 步驟 4: 測試 URL 編碼")
    
    filename = "107_Welding_Metallophthalocyanines_into_Bimetallic_Molecular_Meshes_for_Ultrasensiti_SI.pdf"
    
    # 測試不同的編碼方法
    encoding_methods = [
        ("urllib.parse.quote", urllib.parse.quote),
        ("urllib.parse.quote_plus", urllib.parse.quote_plus),
        ("無編碼", lambda x: x),
    ]
    
    for method_name, encode_func in encoding_methods:
        try:
            encoded = encode_func(filename)
            print(f"🔧 {method_name}: {encoded}")
            
            # 測試編碼後的 URL
            test_url = f"http://localhost:8000/api/v1/documents/{encoded}"
            print(f"   URL: {test_url}")
            
        except Exception as e:
            print(f"❌ {method_name}: 錯誤 - {e}")

def test_frontend_routing():
    """測試前端路由"""
    print("\n🔍 步驟 5: 測試前端路由")
    
    # 檢查前端代碼中的路由設置
    frontend_file = "frontend/src/pages/KnowledgeQuery.jsx"
    
    if os.path.exists(frontend_file):
        print(f"📄 檢查前端文件: {frontend_file}")
        
        with open(frontend_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 查找 citation 相關的代碼
        if 'citation.source' in content:
            print("✅ 找到 citation.source 引用")
        
        if 'API_BASE' in content:
            print("✅ 找到 API_BASE 配置")
        
        # 查找具體的 URL 構建邏輯
        if 'encodeURIComponent' in content:
            print("✅ 找到 encodeURIComponent 使用")
        
        # 查找 documents 路由
        if '/documents/' in content:
            print("✅ 找到 documents 路由")
            
    else:
        print(f"❌ 前端文件不存在: {frontend_file}")

def test_browser_behavior():
    """測試瀏覽器行為"""
    print("\n🔍 步驟 6: 測試瀏覽器行為")
    
    # 創建一個更詳細的 HTML 測試頁面
    html_content = """
<!DOCTYPE html>
<html>
<head>
    <title>SI 文件測試</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .test-section { margin: 20px 0; padding: 15px; border: 1px solid #ccc; }
        .success { background-color: #d4edda; }
        .error { background-color: #f8d7da; }
        a { display: inline-block; margin: 5px; padding: 10px; background: #007bff; color: white; text-decoration: none; border-radius: 5px; }
        a:hover { background: #0056b3; }
    </style>
</head>
<body>
    <h1>SI 文件打開測試</h1>
    
    <div class="test-section">
        <h2>測試 1: 直接 URL 訪問</h2>
        <p>點擊下面的連結測試 SI 文件是否直接打開：</p>
        <a href="http://localhost:8000/api/v1/documents/107_Welding_Metallophthalocyanines_into_Bimetallic_Molecular_Meshes_for_Ultrasensiti_SI.pdf" target="_blank">
            測試 SI 文件 (直接 URL)
        </a>
    </div>
    
    <div class="test-section">
        <h2>測試 2: URL 編碼版本</h2>
        <p>使用 URL 編碼的版本：</p>
        <a href="http://localhost:8000/api/v1/documents/107_Welding_Metallophthalocyanines_into_Bimetallic_Molecular_Meshes_for_Ultrasensiti_SI.pdf" target="_blank">
            測試 SI 文件 (編碼 URL)
        </a>
    </div>
    
    <div class="test-section">
        <h2>測試 3: 對比普通 PDF</h2>
        <p>對比：點擊下面的連結測試普通 PDF 文件：</p>
        <a href="http://localhost:8000/api/v1/documents/097_Selective_reduction_of_CO2_by_conductive_MOF_nanosheets_as_an_efficient_co-catal_PAPER.pdf" target="_blank">
            測試普通 PDF 文件
        </a>
    </div>
    
    <div class="test-section">
        <h2>測試 4: 其他 SI 文件</h2>
        <p>測試其他 SI 文件：</p>
        <a href="http://localhost:8000/api/v1/documents/104_Three-Dimensional_Phthalocyanine_Metal-Catecholates_for_High_Electrochemical_Car_SI.pdf" target="_blank">
            測試另一個 SI 文件
        </a>
    </div>
    
    <div class="test-section">
        <h2>瀏覽器檢查</h2>
        <p>請打開瀏覽器的開發者工具 (F12)，然後點擊上面的連結，觀察：</p>
        <ul>
            <li>Network 標籤中的請求狀態</li>
            <li>Response Headers 中的 Content-Disposition</li>
            <li>是否觸發下載或直接打開</li>
        </ul>
    </div>
</body>
</html>
"""
    
    test_file = "test_si_file_detailed.html"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(html_content)
    
    print(f"📄 已創建詳細測試頁面: {test_file}")
    print(f"💡 請在瀏覽器中打開 {test_file} 來測試文件打開行為")

def analyze_filename_pattern():
    """分析文件名模式"""
    print("\n🔍 步驟 7: 分析文件名模式")
    
    current_dir = os.path.dirname(os.path.abspath(__file__))
    papers_dir = os.path.join(current_dir, "experiment_data", "papers")
    
    # 查找所有 SI 文件
    si_files = []
    for file in os.listdir(papers_dir):
        if file.lower().endswith('_si.pdf'):
            si_files.append(file)
    
    print(f"📊 找到 {len(si_files)} 個 SI 文件:")
    for i, file in enumerate(si_files, 1):
        print(f"   {i}. {file}")
    
    # 分析文件名模式
    print(f"\n🔍 文件名模式分析:")
    for file in si_files:
        base_name = file[:-7]  # 移除 '_SI.pdf'
        print(f"   {file} -> 基礎名稱: {base_name}")

def test_citation_data():
    """測試 citation 數據"""
    print("\n🔍 步驟 8: 測試 citation 數據")
    
    # 模擬 citation 數據結構
    citation_data = {
        "label": "[3]",
        "title": "Welding Metallophthalocyanines into Bimetallic Molecular Meshes for Ultrasensitive, Low-Power Chemiresistive Detection of Gases",
        "source": "107_Welding_Metallophthalocyanines_into_Bimetallic_Molecular_Meshes_for_Ultrasensiti_SI.pdf",
        "page": "2",
        "snippet": "141-78-6) were purchased from BDH Chemicals. Compounds 4,5-dimethoxyphthalodinit"
    }
    
    print(f"📋 Citation 數據:")
    for key, value in citation_data.items():
        print(f"   {key}: {value}")
    
    # 測試 URL 構建
    api_base = "http://localhost:8000/api/v1"
    url = f"{api_base}/documents/{urllib.parse.quote(citation_data['source'])}"
    print(f"\n🔗 構建的 URL: {url}")
    
    # 測試 URL 是否可訪問
    try:
        response = requests.head(url, timeout=5)
        print(f"📊 HEAD 請求狀態碼: {response.status_code}")
        if response.status_code == 200:
            print(f"✅ URL 可訪問")
            print(f"📄 Content-Type: {response.headers.get('Content-Type')}")
            print(f"📎 Content-Disposition: {response.headers.get('Content-Disposition')}")
        else:
            print(f"❌ URL 不可訪問")
    except Exception as e:
        print(f"❌ 測試失敗: {e}")

def main():
    """主函數"""
    print("🚀 開始 SI 文件問題檢測")
    print("=" * 50)
    
    # 步驟 1: 檢測文件是否存在
    file_path = test_file_existence()
    if not file_path:
        print("❌ 文件不存在，無法繼續檢測")
        return
    
    # 步驟 2: 檢測文件擴展名識別
    filename = test_file_extension_detection(file_path)
    
    # 步驟 3: 測試後端 API 響應
    test_backend_api_response()
    
    # 步驟 4: 測試 URL 編碼
    test_url_encoding()
    
    # 步驟 5: 測試前端路由
    test_frontend_routing()
    
    # 步驟 6: 測試瀏覽器行為
    test_browser_behavior()
    
    # 步驟 7: 分析文件名模式
    analyze_filename_pattern()
    
    # 步驟 8: 測試 citation 數據
    test_citation_data()
    
    print("\n" + "=" * 50)
    print("✅ 檢測完成")
    print("💡 請檢查上述結果來定位問題")
    print("🔍 特別注意瀏覽器開發者工具中的 Network 標籤")

if __name__ == "__main__":
    main() 