import requests
import time
import random

def lookup_semantic_scholar_metadata(doi=None, title=None, max_retries=3):
    """
    查詢Semantic Scholar元數據
    
    Args:
        doi: DOI號碼
        title: 論文標題
        max_retries: 最大重試次數
    
    Returns:
        Dict: 元數據字典
    """
    base_url = "https://api.semanticscholar.org/graph/v1/paper"
    fields = "title,authors,year,venue,url,externalIds"

    # 優先使用DOI查詢
    if doi:
        return _query_by_doi(base_url, doi, fields, max_retries)
    
    # 備用標題查詢
    elif title:
        return _query_by_title(base_url, title, fields, max_retries)
    
    else:
        print("⚠️ 沒有提供DOI或標題，無法查詢")
        return {}

def _query_by_doi(base_url, doi, fields, max_retries):
    """使用DOI查詢"""
    url = f"{base_url}/DOI:{doi}?fields={fields}"
    
    for attempt in range(max_retries):
        try:
            response = requests.get(url, verify=False, timeout=15)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ DOI查詢成功: {doi}")
                return data
            elif response.status_code == 404:
                print(f"⚠️ DOI不存在: {doi}")
                return {}
            else:
                print(f"⚠️ DOI查詢失敗 (嘗試 {attempt+1}/{max_retries}): {response.status_code}")
                if attempt < max_retries - 1:
                    time.sleep(random.uniform(1, 3))  # 隨機延遲
                    continue
                return {}
                
        except requests.exceptions.Timeout:
            print(f"⚠️ DOI查詢超時 (嘗試 {attempt+1}/{max_retries})")
            if attempt < max_retries - 1:
                time.sleep(random.uniform(2, 5))
                continue
            return {}
        except Exception as e:
            print(f"⚠️ DOI查詢異常 (嘗試 {attempt+1}/{max_retries}): {e}")
            if attempt < max_retries - 1:
                time.sleep(random.uniform(1, 3))
                continue
            return {}
    
    return {}

def _query_by_title(base_url, title, fields, max_retries):
    """使用標題查詢（備用方案）"""
    search_url = f"{base_url}/search"
    
    for attempt in range(max_retries):
        try:
            # 添加隨機延遲避免被拒絕
            if attempt > 0:
                time.sleep(random.uniform(2, 5))
            
            # 嘗試不同的查詢參數
            params = {
                "query": title,
                "fields": fields,
                "limit": 1,
                "offset": 0
            }
            
            # 添加User-Agent避免被拒絕
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
            
            response = requests.get(
                search_url, 
                params=params, 
                headers=headers,
                verify=False, 
                timeout=15
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("data") and len(data["data"]) > 0:
                    print(f"✅ 標題查詢成功: {title[:50]}...")
                    return data["data"][0]  # 返回最佳匹配
                else:
                    print(f"⚠️ 標題查詢無結果: {title[:50]}...")
                    return {}
            elif response.status_code == 429:  # Rate limit
                print(f"⚠️ 標題查詢被限制 (嘗試 {attempt+1}/{max_retries})")
                if attempt < max_retries - 1:
                    time.sleep(random.uniform(5, 10))  # 更長延遲
                    continue
                return {}
            elif response.status_code == 403:  # Forbidden
                print(f"⚠️ 標題查詢被拒絕訪問 (嘗試 {attempt+1}/{max_retries})")
                if attempt < max_retries - 1:
                    time.sleep(random.uniform(3, 7))
                    continue
                return {}
            else:
                print(f"⚠️ 標題查詢失敗 (嘗試 {attempt+1}/{max_retries}): {response.status_code}")
                if attempt < max_retries - 1:
                    time.sleep(random.uniform(1, 3))
                    continue
                return {}
                
        except requests.exceptions.Timeout:
            print(f"⚠️ 標題查詢超時 (嘗試 {attempt+1}/{max_retries})")
            if attempt < max_retries - 1:
                time.sleep(random.uniform(2, 5))
                continue
            return {}
        except Exception as e:
            print(f"⚠️ 標題查詢異常 (嘗試 {attempt+1}/{max_retries}): {e}")
            if attempt < max_retries - 1:
                time.sleep(random.uniform(1, 3))
                continue
            return {}
    
    return {}

if __name__ == "__main__":
    # 測試用
    test_doi = "10.1016/j.matchemphys.2019.122601"
    metadata = lookup_semantic_scholar_metadata(doi=test_doi)
    print(metadata)
