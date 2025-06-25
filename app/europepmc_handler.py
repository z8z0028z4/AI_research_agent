import requests
import warnings
from typing import List, Dict
import os
from document_renamer import sanitize_filename

warnings.filterwarnings("ignore", message="Unverified HTTPS request")

def search_source(keywords: List[str], limit: int = 5, or_batch: int = 30) -> List[Dict]:
    """
    Use OR logic to query EuropePMC ABSTRACT field.
    Rank results by keyword hit count in abstractText.
    Return top N high-relevance papers with PMCID and PDF access.
    """

    def run_query(query: str) -> List[Dict]:
        url = f"https://www.ebi.ac.uk/europepmc/webservices/rest/search?query={query}&format=json&pageSize={or_batch}"
        response = requests.get(url, verify=False)
        if response.status_code != 200:
            print(f"❌ EuropePMC API 錯誤：{response.status_code}")
            return []

        items = response.json().get("resultList", {}).get("result", [])
        results = []
        for item in items:
            pmcid = item.get("pmcid")
            if not pmcid:
                continue
            title = item.get("title", "no_title")
            doi = item.get("doi", "")
            source = item.get("source", "")
            abstract = item.get("abstractText", "") or ""
            pdf_url = f"https://europepmc.org/articles/{pmcid}?pdf=render"

            results.append({
                "title": title,
                "pdf_url": pdf_url,
                "doi": doi,
                "pmcid": pmcid,
                "source": source,
                "abstract": abstract,
            })

        return results

    def score_result(item: Dict, keywords: List[str]) -> int:
        abstract = item.get("abstract", "").lower()
        return sum(1 for kw in keywords if kw.lower() in abstract)

    # OR 查詢語法
    or_query = " OR ".join([f'ABSTRACT:"{kw}"' for kw in keywords])
    raw_results = run_query(or_query)

    # 根據 abstract 中出現的關鍵字數量排序
    scored_results = sorted(raw_results, key=lambda r: score_result(r, keywords), reverse=True)

    return scored_results[:limit]


def download_and_store(record: Dict, folder: str) -> str:
    """
    下載 PDF（使用 EuropePMC redirect 機制）
    """
    title = sanitize_filename(record.get("title", "no_title"))
    pmcid = record.get("pmcid", "")
    pdf_url = record.get("pdf_url")

    if not pmcid or not pdf_url:
        print("❌ 缺少 PMCID 或 PDF 連結")
        return ""

    os.makedirs(folder, exist_ok=True)
    filepath = os.path.join(folder, f"{title}_{pmcid}.pdf")

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    try:
        r = requests.get(pdf_url, timeout=20, verify=False, headers=headers, allow_redirects=True)
        if r.ok and "pdf" in r.headers.get("Content-Type", "").lower():
            with open(filepath, "wb") as f:
                f.write(r.content)
            print(f"✅ 已下載：{filepath}")
            return filepath
        else:
            print(f"⚠️ PDF 回應異常（可能仍為 HTML）：{pdf_url}")
    except Exception as e:
        print(f"❌ 下載錯誤：{e}")

    return ""
