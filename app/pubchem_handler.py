import requests
import os
import json
from typing import List, Dict
import re
from typing import Optional
# 兼容性導入：支持相對導入和絕對導入
try:
    from .config import PARSED_CHEMICAL_DIR
except ImportError:
    # 當作為模組導入時使用絕對導入
    from config import PARSED_CHEMICAL_DIR

BASE_URL = "https://pubchem.ncbi.nlm.nih.gov/rest/pug"

def search_source(keywords: List[str], limit: int = 5) -> List[Dict]:
    """
    Search PubChem by keyword and return metadata with CID
    """
    results = []
    for keyword in keywords:
        url = f"{BASE_URL}/compound/name/{keyword}/cids/JSON"
        try:
            r = requests.get(url, timeout=10,verify=False)
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
    下載 PubChem JSON metadata
    """
    cid = result.get("cid")
    if not cid:
        print("❌ 無 CID，跳過")
        return ""

    url = f"{BASE_URL}/compound/cid/{cid}/JSON"
    os.makedirs(storage_dir, exist_ok=True)
    filepath = os.path.join(storage_dir, f"pubchem_cid{cid}.json")

    try:
        r = requests.get(url, timeout=15, verify=False)
        if r.ok:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(r.text)
            print(f"✅ Stored PubChem CID {cid} to {filepath}")
            return filepath
        else:
            print(f"⚠️ PubChem 回傳錯誤：{r.status_code}")
    except Exception as e:
        print(f"❌ Failed to download CID {cid}: {e}")

    return ""

def extract_json_chemical_list_from_llm(text: str) -> list:
    # 首先嘗試提取完整的 JSON 物件
    json_match = re.search(r"```json\s*(\{.*?\})\s*```", text, re.DOTALL)
    if json_match:
        try:
            json_obj = json.loads(json_match.group(1))
            if 'materials_list' in json_obj and isinstance(json_obj['materials_list'], list):
                print(f"✅ 從完整 JSON 物件中提取到 materials_list: {json_obj['materials_list']}")
                return json_obj['materials_list']
        except Exception as e:
            print(f"❌ 完整 JSON 物件解析失敗：{e}")
    
    # 如果沒有找到完整 JSON 物件，嘗試提取單獨的陣列
    array_match = re.search(r"```json\s*(\[[^\]]+\])\s*```", text, re.DOTALL)
    if array_match:
        try:
            return json.loads(array_match.group(1))
        except Exception as e:
            print("❌ JSON chemical list 解析失敗：", e)
    
    # 如果都沒有找到，嘗試直接解析整個文本為 JSON
    try:
        # 移除可能的 markdown 格式
        cleaned_text = re.sub(r"```json\s*", "", text)
        cleaned_text = re.sub(r"\s*```", "", cleaned_text)
        json_obj = json.loads(cleaned_text)
        if 'materials_list' in json_obj and isinstance(json_obj['materials_list'], list):
            print(f"✅ 從清理後的文本中提取到 materials_list: {json_obj['materials_list']}")
            return json_obj['materials_list']
    except Exception as e:
        print(f"❌ 直接 JSON 解析失敗：{e}")
    
    return []

def parse_pubchem_json(json_data: dict) -> dict:
    props = json_data["PC_Compounds"][0].get("props", [])
    cid = json_data["PC_Compounds"][0]["id"]["id"]["cid"]

    def find_prop(label: str, name: str = None):
        for p in props:
            urn = p.get("urn", {})
            if urn.get("label") == label and (name is None or urn.get("name") == name):
                return p.get("value", {}).get("sval") or p.get("value", {}).get("fval")
        return None

    def clean_text_for_xml(text):
        """清理文本以確保XML兼容性"""
        if not text:
            return ""
        # 移除NULL字節和控制字符
        cleaned = "".join(char for char in str(text) if ord(char) >= 32 or char in '\n\r\t')
        # 移除其他可能導致XML問題的字符
        cleaned = cleaned.replace('\x00', '')  # NULL字節
        cleaned = cleaned.replace('\x01', '')  # SOH
        cleaned = cleaned.replace('\x02', '')  # STX
        cleaned = cleaned.replace('\x03', '')  # ETX
        cleaned = cleaned.replace('\x04', '')  # EOT
        cleaned = cleaned.replace('\x05', '')  # ENQ
        cleaned = cleaned.replace('\x06', '')  # ACK
        cleaned = cleaned.replace('\x07', '')  # BEL
        cleaned = cleaned.replace('\x08', '')  # BS
        cleaned = cleaned.replace('\x0b', '')  # VT
        cleaned = cleaned.replace('\x0c', '')  # FF
        cleaned = cleaned.replace('\x0e', '')  # SO
        cleaned = cleaned.replace('\x0f', '')  # SI
        return cleaned

    # 優先使用IUPAC名稱，如果沒有則使用其他名稱
    iupac_name = find_prop("IUPAC Name", "Preferred") or find_prop("IUPAC Name", "Traditional")
    if not iupac_name:
        # 如果沒有IUPAC名稱，嘗試其他名稱
        iupac_name = find_prop("IUPAC Name") or find_prop("Title") or "Unknown"
    
    return {
        "cid": cid,
        "name": clean_text_for_xml(iupac_name),
        "iupac_name": clean_text_for_xml(iupac_name),  # 明確標記IUPAC名稱
        "formula": clean_text_for_xml(find_prop("Molecular Formula")),
        "weight": clean_text_for_xml(find_prop("Molecular Weight")),
        "smiles": clean_text_for_xml(find_prop("SMILES", "Absolute") or find_prop("SMILES", "Connectivity")),
        "image_url": f"https://pubchem.ncbi.nlm.nih.gov/image/imgsrv.fcgi?cid={cid}&t=l"
    }

def get_boiling_and_melting_point(cid: int) -> dict:
    url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug_view/data/compound/{cid}/JSON"
    try:
        r = requests.get(url, timeout=15, verify=False)
        if not r.ok:
            print(f"⚠️ View API 回傳失敗：CID {cid}, status: {r.status_code}")
            return {}

        data = r.json()
        sections = data.get("Record", {}).get("Section", [])
        result = {}

        def find_in_sections(sections, keyword):
            for section in sections:
                toc = section.get("TOCHeading", "")
                if keyword.lower() in toc.lower():
                    for info in section.get("Information", []):
                        val = info.get("Value", {}).get("StringWithMarkup", [])
                        if val:
                            return val[0].get("String", "").strip()
                sub = section.get("Section")
                if sub:
                    found = find_in_sections(sub, keyword)
                    if found:
                        return found
            return None

        def extract_celsius(temp_str: str):
            if not temp_str:
                return None
            match = re.search(r"([-+]?[0-9.]+)\s*°F", temp_str)
            if match:
                f = float(match.group(1))
                c = round((f - 32) * 5 / 9, 1)
                return f"{c} °C"
            match = re.search(r"([-+]?[0-9.]+)\s*°C", temp_str)
            if match:
                return match.group(0)
            return None

        def clean_text_for_xml(text):
            """清理文本以確保XML兼容性"""
            if not text:
                return ""
            # 移除NULL字節和控制字符
            cleaned = "".join(char for char in str(text) if ord(char) >= 32 or char in '\n\r\t')
            # 移除其他可能導致XML問題的字符
            cleaned = cleaned.replace('\x00', '')  # NULL字節
            cleaned = cleaned.replace('\x01', '')  # SOH
            cleaned = cleaned.replace('\x02', '')  # STX
            cleaned = cleaned.replace('\x03', '')  # ETX
            cleaned = cleaned.replace('\x04', '')  # EOT
            cleaned = cleaned.replace('\x05', '')  # ENQ
            cleaned = cleaned.replace('\x06', '')  # ACK
            cleaned = cleaned.replace('\x07', '')  # BEL
            cleaned = cleaned.replace('\x08', '')  # BS
            cleaned = cleaned.replace('\x0b', '')  # VT
            cleaned = cleaned.replace('\x0c', '')  # FF
            cleaned = cleaned.replace('\x0e', '')  # SO
            cleaned = cleaned.replace('\x0f', '')  # SI
            return cleaned

        bp_raw = find_in_sections(sections, "Boiling Point")
        mp_raw = find_in_sections(sections, "Melting Point")

        result["boiling_point"] = clean_text_for_xml(bp_raw)
        result["melting_point"] = clean_text_for_xml(mp_raw)
        result["boiling_point_c"] = clean_text_for_xml(extract_celsius(bp_raw) if bp_raw else None)
        result["melting_point_c"] = clean_text_for_xml(extract_celsius(mp_raw) if mp_raw else None)

        return result

    except Exception as e:
        print(f"❌ 擷取熔點沸點失敗 CID {cid}: {e}")
        return {}

def get_safety_info(cid: int) -> dict:
    """
    從 PubChem PUG View API 擷取：
    - GHS hazard icon URL list
    - NFPA diamond image URL
    - CAS No.（第一組合法格式）
    """
    url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug_view/data/compound/{cid}/JSON"
    try:
        r = requests.get(url, timeout=15, verify=False)
        if not r.ok:
            print(f"⚠️ PubChem View 查詢失敗：CID {cid} / {r.status_code}")
            return {"ghs_icons": [], "nfpa_image": None, "cas": None}

        json_data = r.json()
        sections = json_data.get("Record", {}).get("Section", [])

        ghs_urls = set()
        nfpa_url = None
        cas_number = None

        def clean_text_for_xml(text):
            """清理文本以確保XML兼容性"""
            if not text:
                return ""
            # 移除NULL字節和控制字符
            cleaned = "".join(char for char in str(text) if ord(char) >= 32 or char in '\n\r\t')
            # 移除其他可能導致XML問題的字符
            cleaned = cleaned.replace('\x00', '')  # NULL字節
            cleaned = cleaned.replace('\x01', '')  # SOH
            cleaned = cleaned.replace('\x02', '')  # STX
            cleaned = cleaned.replace('\x03', '')  # ETX
            cleaned = cleaned.replace('\x04', '')  # EOT
            cleaned = cleaned.replace('\x05', '')  # ENQ
            cleaned = cleaned.replace('\x06', '')  # ACK
            cleaned = cleaned.replace('\x07', '')  # BEL
            cleaned = cleaned.replace('\x08', '')  # BS
            cleaned = cleaned.replace('\x0b', '')  # VT
            cleaned = cleaned.replace('\x0c', '')  # FF
            cleaned = cleaned.replace('\x0e', '')  # SO
            cleaned = cleaned.replace('\x0f', '')  # SI
            return cleaned

        def walk(sections):
            nonlocal ghs_urls, nfpa_url, cas_number
            for sec in sections:
                heading = sec.get("TOCHeading", "")

                # GHS 圖示
                if heading == "GHS Classification":
                    for info in sec.get("Information", []):
                        if info.get("Name") == "Pictogram(s)":
                            for val in info.get("Value", {}).get("StringWithMarkup", []):
                                for markup in val.get("Markup", []):
                                    if markup.get("Type") == "Icon":
                                        ghs_urls.add(markup.get("URL"))

                elif heading == "NFPA Hazard Classification":
                    for info in sec.get("Information", []):
                        if info.get("Name") == "NFPA 704 Diamond":
                            for val in info.get("Value", {}).get("StringWithMarkup", []):
                                for markup in val.get("Markup", []):
                                    if markup.get("Type") == "Icon":
                                        nfpa_url = markup.get("URL")

                # CAS Number
                elif heading == "CAS" and not cas_number:
                    for info in sec.get("Information", []):
                        val = info.get("Value", {}).get("StringWithMarkup", [])
                        if val:
                            for entry in val:
                                maybe_cas = entry.get("String", "")
                                if "-" in maybe_cas and maybe_cas.count("-") == 2:
                                    cas_number = clean_text_for_xml(maybe_cas)
                                    break

                # 遞迴深入子區塊
                if "Section" in sec:
                    walk(sec["Section"])

        walk(sections)

        return {
            "ghs_icons": sorted(ghs_urls),
            "nfpa_image": nfpa_url,
            "cas": cas_number
        }

    except Exception as e:
        print(f"❌ 擷取 hazard icon / CAS No. 失敗 CID {cid}: {e}")
        return {"ghs_icons": [], "nfpa_image": None, "cas": None}




def extract_and_fetch_chemicals(name_list: List[str], save_dir=PARSED_CHEMICAL_DIR) -> List[dict]:
    """
    接收一組 GPT 傳回的化學品名稱清單，逐一查詢、擷取、儲存乾淨的 JSON。
    僅留下 parse 過的 parsed_cid{cid}.json
    """
    os.makedirs(save_dir, exist_ok=True)
    summaries = []
    not_found = []

    for name in name_list:
        results = search_source([name], limit=2)
        if not results:
            print(f"❌ 找不到化學品：{name}")
            not_found.append(name)
            continue

        cid = results[0].get("cid")
        if not cid:
            print(f"❌ 無 CID：{name}")
            not_found.append(name)
            continue

        try:
            # Step 1: General compound JSON
            url_main = f"{BASE_URL}/compound/cid/{cid}/JSON"
            r_main = requests.get(url_main, timeout=15, verify=False)
            if not r_main.ok:
                print(f"⚠️ 主查詢失敗 CID {cid}: {r_main.status_code}")
                not_found.append(name)
                continue

            json_data = r_main.json()
            parsed = parse_pubchem_json(json_data)

            #加入pubchem超連結:
            parsed["pubchem_url"] = f"https://pubchem.ncbi.nlm.nih.gov/compound/{cid}"

            # Step 2: 補充熔/沸點資訊（含轉攝氏）
            bp_info = get_boiling_and_melting_point(cid)
            parsed.update(bp_info)

            # Step 3: 補充 GHS icon URLs
            safety_info = get_safety_info(cid)

            parsed["safety_icons"] = {
                "ghs_icons": safety_info.get("ghs_icons", []),
                "nfpa_image": safety_info.get("nfpa_image")
            }
            parsed["cas"] = safety_info.get("cas")

            # Step 4: 儲存乾淨版本
            save_path = os.path.join(save_dir, f"parsed_cid{cid}.json")
            with open(save_path, "w", encoding="utf-8") as f:
                json.dump(parsed, f, indent=2)
            # print(f"✅ Saved parsed info: {save_path}")
            summaries.append(parsed)

        except Exception as e:
            print(f"❌ Failed to process {name} (CID {cid}): {e}")
            not_found.append(name)

    return summaries, not_found

def remove_json_chemical_block(text: str) -> str:
    return re.sub(r"```json\s*\[[^\]]+\]\s*```", "", text, flags=re.DOTALL)

    
def chemical_metadata_extractor(proposal_text: str):
    print(f"🔍 開始提取化學品，提案文本長度：{len(proposal_text)} 字符")
    print(f"📝 提案文本預覽：{proposal_text[:300]}...")
    
    name_list = extract_json_chemical_list_from_llm(proposal_text)
    print(f"🔍 擷取到的化學品：{name_list}")
    
    if not name_list:
        print("⚠️ 沒有找到化學品列表，這可能是因為 LLM 沒有生成 JSON 格式的化學品列表")
        print("🔍 檢查提案文本中是否包含 JSON 格式的化學品列表...")
        json_match = re.search(r"```json\s*\[[^\]]+\]\s*```", proposal_text, re.DOTALL)
        if json_match:
            print(f"✅ 找到 JSON 格式：{json_match.group(0)}")
        else:
            print("❌ 沒有找到 JSON 格式的化學品列表")
    
    summaries, not_found = extract_and_fetch_chemicals(name_list)
    cleaned_proposal_text = remove_json_chemical_block(proposal_text)
    return summaries, not_found, cleaned_proposal_text