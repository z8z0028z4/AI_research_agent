"""
AI 研究助理 - 搜索代理模塊
========================

這個模塊負責協調多個搜索源，提供智能文獻搜索功能。
主要功能包括：
1. 關鍵詞提取和查詢優化
2. 多源搜索協調
3. 文獻下載和存儲管理
4. 搜索結果整合

架構說明：
- 作為搜索層的核心協調器
- 整合多個數據源（Europe PMC, PubChem等）
- 提供統一的搜索接口
"""

import os
from typing import List, Dict, Optional
from query_parser import extract_keywords
from europepmc_handler import search_source, download_and_store

def search_and_download_only(user_input: str, top_k: int = 5, storage_dir: str = "data/downloads") -> List[str]:
    """
    智能文獻搜索和下載功能
    
    功能流程：
    1. 從用戶輸入中提取關鍵詞
    2. 使用關鍵詞在Europe PMC中搜索相關文獻
    3. 下載並存儲相關的PDF文件
    4. 返回下載文件的本地路徑列表
    
    參數：
        user_input (str): 用戶的搜索查詢
        top_k (int): 返回的結果數量，默認5個
        storage_dir (str): 文件存儲目錄
    
    返回：
        List[str]: 下載文件的本地路徑列表
    
    示例：
        >>> filepaths = search_and_download_only("machine learning in chemistry", top_k=3)
        >>> print(f"下載了 {len(filepaths)} 個文件")
    """
    # ==================== 關鍵詞提取 ====================
    # 使用query_parser模塊從用戶輸入中提取關鍵詞
    # 這有助於提高搜索的準確性和相關性
    keywords = extract_keywords(user_input)
    print(f"🔑 提取的關鍵詞：{keywords}")
    
    # ==================== 文獻搜索 ====================
    # 使用提取的關鍵詞在Europe PMC數據庫中搜索
    # Europe PMC是歐洲最大的醫學和生命科學文獻數據庫
    results = search_source(keywords, limit=top_k)
    print(f"📚 找到 {len(results)} 篇相關文獻")
    
    # ==================== 文件下載和存儲 ====================
    # 遍歷搜索結果，下載相關的PDF文件
    filepaths = []
    for i, result in enumerate(results, 1):
        print(f"📥 正在下載第 {i}/{len(results)} 個文件...")
        
        # 下載並存儲文件，返回本地文件路徑
        filepath = download_and_store(result, storage_dir)
        
        # 如果下載成功，將文件路徑添加到列表中
        if filepath:
            filepaths.append(filepath)
            print(f"✅ 成功下載：{os.path.basename(filepath)}")
        else:
            print(f"❌ 下載失敗：{result.get('title', '未知標題')}")
    
    # ==================== 結果統計 ====================
    print(f"🎯 搜索完成！成功下載 {len(filepaths)}/{len(results)} 個文件")
    
    return filepaths


def search_with_metadata(user_input: str, top_k: int = 5) -> List[Dict]:
    """
    搜索文獻並返回元數據信息（不下載文件）
    
    功能：
    1. 提取關鍵詞
    2. 搜索相關文獻
    3. 返回文獻的元數據信息（標題、作者、摘要等）
    
    參數：
        user_input (str): 用戶搜索查詢
        top_k (int): 返回結果數量
    
    返回：
        List[Dict]: 文獻元數據列表
    """
    keywords = extract_keywords(user_input)
    print(f"🔍 搜索關鍵詞：{keywords}")
    
    # 只搜索，不下載
    results = search_source(keywords, limit=top_k)
    
    # 提取元數據信息
    metadata_list = []
    for result in results:
        metadata = {
            'title': result.get('title', '未知標題'),
            'authors': result.get('authors', []),
            'abstract': result.get('abstract', ''),
            'doi': result.get('doi', ''),
            'pmid': result.get('pmid', ''),
            'publication_date': result.get('publication_date', ''),
            'journal': result.get('journal', '')
        }
        metadata_list.append(metadata)
    
    return metadata_list


def multi_source_search(user_input: str, sources: List[str] = None) -> Dict[str, List]:
    """
    多源搜索功能（未來擴展）
    
    功能：
    1. 支持多個數據源同時搜索
    2. 整合不同來源的結果
    3. 提供統一的結果格式
    
    參數：
        user_input (str): 用戶查詢
        sources (List[str]): 搜索源列表，如 ['europepmc', 'pubchem', 'arxiv']
    
    返回：
        Dict[str, List]: 按數據源分組的搜索結果
    """
    if sources is None:
        sources = ['europepmc']  # 默認只使用Europe PMC
    
    results = {}
    
    for source in sources:
        print(f"🔍 正在搜索 {source}...")
        
        if source == 'europepmc':
            # Europe PMC搜索
            keywords = extract_keywords(user_input)
            source_results = search_source(keywords, limit=5)
            results[source] = source_results
        elif source == 'pubchem':
            # PubChem搜索（化學品信息）
            # TODO: 實現PubChem搜索功能
            results[source] = []
        else:
            print(f"⚠️ 不支持的搜索源：{source}")
            results[source] = []
    
    return results


# ==================== 輔助函數 ====================
def validate_search_input(user_input: str) -> bool:
    """
    驗證搜索輸入是否有效
    
    參數：
        user_input (str): 用戶輸入
    
    返回：
        bool: 輸入是否有效
    """
    if not user_input or not user_input.strip():
        return False
    
    # 檢查輸入長度
    if len(user_input.strip()) < 3:
        return False
    
    return True


def format_search_results(results: List[Dict]) -> str:
    """
    格式化搜索結果為可讀的文本
    
    參數：
        results (List[Dict]): 搜索結果列表
    
    返回：
        str: 格式化的結果文本
    """
    if not results:
        return "❌ 未找到相關結果"
    
    formatted_text = f"📚 找到 {len(results)} 篇相關文獻：\n\n"
    
    for i, result in enumerate(results, 1):
        title = result.get('title', '未知標題')
        authors = result.get('authors', [])
        abstract = result.get('abstract', '')[:200] + "..." if len(result.get('abstract', '')) > 200 else result.get('abstract', '')
        
        formatted_text += f"**{i}. {title}**\n"
        if authors:
            formatted_text += f"作者：{', '.join(authors[:3])}\n"
        if abstract:
            formatted_text += f"摘要：{abstract}\n"
        formatted_text += "\n"
    
    return formatted_text
