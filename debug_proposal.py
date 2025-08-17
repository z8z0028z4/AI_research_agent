#!/usr/bin/env python3
"""
研究提案功能診斷腳本
==================

用於診斷研究提案功能的各個組件是否正常工作
"""

import os
import sys
import time
import traceback
from pathlib import Path

# 添加項目路徑
project_root = Path(__file__).parent
sys.path.append(str(project_root))
sys.path.append(str(project_root / "app"))

def test_imports():
    """測試所有必要的導入"""
    print("🔍 測試導入...")
    
    try:
        # 測試基礎模塊
        import logging
        print("✅ logging 導入成功")
        
        # 測試配置
        from app.config import OPENAI_API_KEY, PERPLEXITY_API_KEY
        print("✅ config 導入成功")
        print(f"   OPENAI_API_KEY: {'已設置' if OPENAI_API_KEY else '未設置'}")
        print(f"   PERPLEXITY_API_KEY: {'已設置' if PERPLEXITY_API_KEY else '未設置'}")
        
        # 測試向量數據庫
        from app.chunk_embedding import get_chroma_instance
        print("✅ chunk_embedding 導入成功")
        
        # 測試知識代理
        from app.knowledge_agent import agent_answer
        print("✅ knowledge_agent 導入成功")
        
        # 測試化學品處理
        from app.pubchem_handler import chemical_metadata_extractor
        print("✅ pubchem_handler 導入成功")
        
        return True
        
    except Exception as e:
        print(f"❌ 導入失敗: {e}")
        traceback.print_exc()
        return False

def test_vector_database():
    """測試向量數據庫"""
    print("\n🔍 測試向量數據庫...")
    
    try:
        from app.chunk_embedding import get_chroma_instance, get_vectorstore_stats
        
        # 測試論文向量庫
        paper_vectorstore = get_chroma_instance("paper")
        paper_stats = get_vectorstore_stats("paper")
        print(f"✅ 論文向量庫: {paper_stats}")
        
        # 測試實驗向量庫
        experiment_vectorstore = get_chroma_instance("experiment")
        experiment_stats = get_vectorstore_stats("experiment")
        print(f"✅ 實驗向量庫: {experiment_stats}")
        
        return True
        
    except Exception as e:
        print(f"❌ 向量數據庫測試失敗: {e}")
        traceback.print_exc()
        return False

def test_knowledge_agent():
    """測試知識代理"""
    print("\n🔍 測試知識代理...")
    
    try:
        from app.knowledge_agent import agent_answer
        
        # 測試簡單查詢
        test_question = "測試查詢"
        result = agent_answer(test_question, mode="make proposal", k=1)
        
        print(f"✅ 知識代理測試成功")
        print(f"   結果類型: {type(result)}")
        print(f"   結果鍵: {list(result.keys()) if isinstance(result, dict) else 'N/A'}")
        
        return True
        
    except Exception as e:
        print(f"❌ 知識代理測試失敗: {e}")
        traceback.print_exc()
        return False

def test_chemical_extraction():
    """測試化學品提取"""
    print("\n🔍 測試化學品提取...")
    
    try:
        from app.pubchem_handler import chemical_metadata_extractor
        
        # 測試文本
        test_text = "使用甲醇和乙醇進行實驗"
        chemicals, not_found, cleaned_text = chemical_metadata_extractor(test_text)
        
        print(f"✅ 化學品提取測試成功")
        print(f"   提取到的化學品: {len(chemicals)}")
        print(f"   未找到的化學品: {len(not_found)}")
        
        return True
        
    except Exception as e:
        print(f"❌ 化學品提取測試失敗: {e}")
        traceback.print_exc()
        return False

def test_api_endpoint():
    """測試API端點"""
    print("\n🔍 測試API端點...")
    
    try:
        import requests
        
        # 測試健康檢查
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            print("✅ 後端服務運行正常")
            return True
        else:
            print(f"❌ 後端服務響應異常: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ 無法連接到後端服務 (http://localhost:8000)")
        print("   請確保後端服務正在運行")
        return False
    except Exception as e:
        print(f"❌ API測試失敗: {e}")
        return False

def main():
    """主診斷函數"""
    print("🚀 開始研究提案功能診斷...")
    print("=" * 50)
    
    results = {}
    
    # 測試導入
    results['imports'] = test_imports()
    
    # 測試向量數據庫
    results['vector_database'] = test_vector_database()
    
    # 測試知識代理
    results['knowledge_agent'] = test_knowledge_agent()
    
    # 測試化學品提取
    results['chemical_extraction'] = test_chemical_extraction()
    
    # 測試API端點
    results['api_endpoint'] = test_api_endpoint()
    
    # 總結
    print("\n" + "=" * 50)
    print("📊 診斷結果總結:")
    
    for test_name, result in results.items():
        status = "✅ 通過" if result else "❌ 失敗"
        print(f"   {test_name}: {status}")
    
    all_passed = all(results.values())
    
    if all_passed:
        print("\n🎉 所有測試通過！研究提案功能應該正常工作。")
    else:
        print("\n⚠️ 部分測試失敗，請檢查上述錯誤信息。")
        print("\n建議的解決步驟:")
        print("1. 確保已安裝所有依賴: pip install -r backend/requirements.txt")
        print("2. 確保已設置環境變量 (.env 文件)")
        print("3. 確保後端服務正在運行: python backend/main.py")
        print("4. 檢查向量數據庫是否已初始化")

if __name__ == "__main__":
    main()
