import os
from typing import List
from query_parser import extract_keywords
from europepmc_handler import search_source, download_and_store

def search_and_download_only(user_input: str, top_k: int = 5, storage_dir: str = "data/downloads") -> List[str]:
    """
    Search literature from EuropePMC using user input, extract keywords,
    download relevant PDFs, and return their file paths.
    """
    keywords = extract_keywords(user_input)
    print(f"🔑 關鍵字：{keywords}")
    results = search_source(keywords, limit=top_k)

    filepaths = []
    for result in results:
        filepath = download_and_store(result, storage_dir)
        if filepath:
            filepaths.append(filepath)

    return filepaths
