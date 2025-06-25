from typing import List, Literal
import re
from openai import OpenAI
import os
from config import LLM_MODEL_NAME
import ast

# You can use a local LLM or API call depending on your setup
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def extract_keywords(question: str) -> List[str]:
    prompt = f"""
    You are an expert scientific assistant.  
    Extract only the most relevant **English** scientific keywords or material names from the following research question.

    - Only return keywords or entities that are likely to appear in scientific English papers' abstract.
    - If the input is in another language (e.g., Chinese), translate the scientific terms and return **only English keywords**.
    - Do not return explanations or extra formatting.

    Return the result as a valid Python list of quoted strings.  
    Example: ["direct air capture", "CO2", "MOFs"]

    Question: "{question}"
    """

    response = client.chat.completions.create(
        model=LLM_MODEL_NAME,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
    )

    raw = response.choices[0].message.content.strip()
    print("🧠 原始回傳：", raw)

    try:
        # 擷取第一個類似 list 的 [] 片段
        match = re.search(r'\[.*\]', raw, re.DOTALL)
        if match:
            return ast.literal_eval(match.group(0))
        else:
            print("⚠️ 沒有偵測到合法 list 格式")
            return []
    except Exception as e:
        print("Keyword extraction failed:", e)
        return []

