import requests
import os
import json
from typing import List, Dict

BASE_URL = "https://pubchem.ncbi.nlm.nih.gov/rest/pug"

def search_source(keywords: List[str], limit: int = 5) -> List[Dict]:
    """
    Search PubChem by keyword and return metadata with CID
    """
    results = []
    for keyword in keywords:
        url = f"{BASE_URL}/compound/name/{keyword}/cids/JSON"
        try:
            r = requests.get(url, timeout=10)
            if r.status_code == 200 and 'IdentifierList' in r.json():
                cids = r.json()['IdentifierList']['CID'][:limit]
                for cid in cids:
                    results.append({
                        "cid": cid,
                        "query": keyword,
                        "source": "PubChem"
                    })
        except Exception as e:
            print(f"PubChem search failed for '{keyword}': {e}")
    return results

def download_and_store(result: Dict, storage_dir: str) -> str:
    """
    Download compound summary for CID and store as JSON file
    """
    cid = result["cid"]
    url = f"{BASE_URL}/compound/cid/{cid}/JSON"
    try:
        r = requests.get(url, timeout=15)
        if r.status_code == 200:
            data = r.json()
            filename = os.path.join(storage_dir, f"pubchem_cid{cid}.json")
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            print(f"✅ Stored PubChem CID {cid} to {filename}")
            return filename
        else:
            raise Exception(f"HTTP {r.status_code}")
    except Exception as e:
        print(f"❌ Failed to download CID {cid}: {e}")
        return ""
