import requests

def lookup_semantic_scholar_metadata(doi=None, title=None):
    base_url = "https://api.semanticscholar.org/graph/v1/paper"
    fields = "title,authors,year,venue,url,externalIds"

    if doi:
        url = f"{base_url}/DOI:{doi}?fields={fields}"
    elif title:
        search_url = f"{base_url}/search"
        response = requests.get(search_url, params={"query": title, "fields": fields, "limit": 1}, verify=False)
        if response.status_code == 200:
            data = response.json()
            if data.get("data"):
                return data["data"][0]  # top match
            else:
                print("⚠️ 找不到符合的標題。")
                return {}
        else:
            print(f"⚠️ Semantic Scholar 搜尋失敗：{response.status_code}")
            return {}
    else:
        raise ValueError("請提供 DOI 或 title 作為查詢依據")

    # 如果是 DOI 查詢
    response = requests.get(url, verify=False)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"⚠️ Semantic Scholar DOI 查詢失敗：{response.status_code}")
        return {}

if __name__ == "__main__":
    # 測試用
    test_doi = "10.1016/j.matchemphys.2019.122601"
    metadata = lookup_semantic_scholar_metadata(doi=test_doi)
    print(metadata)
