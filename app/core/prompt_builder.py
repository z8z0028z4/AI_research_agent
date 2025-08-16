"""
提示詞構建模組
============

負責構建各種類型的提示詞，包括提案生成、實驗設計等
"""

from typing import List, Dict, Any, Optional
from langchain.schema import Document

from ..utils.logger import get_logger

logger = get_logger(__name__)


def build_proposal_prompt(
    research_goal: str, 
    chunks: List[Document], 
    user_feedback: Optional[str] = None
) -> str:
    """
    構建研究提案生成提示詞
    
    Args:
        research_goal: 研究目標
        chunks: 檢索到的文檔塊
        user_feedback: 用戶反饋
        
    Returns:
        構建好的提示詞
    """
    # 構建文檔上下文
    context = build_context_from_chunks(chunks)
    
    # 基礎提示詞
    prompt = f"""
你是一個專業的化學研究助理，需要基於提供的文獻資料生成研究提案。

研究目標：{research_goal}

相關文獻資料：
{context}

請生成一個結構化的研究提案，包含以下部分：
1. 提案標題：簡潔明了的標題
2. 研究需求：分析現有技術的局限性和需要解決的問題
3. 解決方案：提出具體的技術路線和方法
4. 差異化：與現有技術的比較和創新點
5. 預期效益：技術和經濟效益分析
6. 實驗概述：實驗設計和關鍵步驟
7. 材料清單：所需的化學品和材料

要求：
- 基於提供的文獻資料進行分析
- 確保技術可行性和創新性
- 提供具體的實驗設計
- 使用專業的化學術語
"""
    
    # 添加用戶反饋
    if user_feedback:
        prompt += f"\n\n用戶反饋：{user_feedback}\n請根據用戶反饋調整提案內容。"
    
    return prompt


def build_detail_experimental_plan_prompt(
    proposal: str, 
    chunks: List[Document]
) -> str:
    """
    構建詳細實驗計劃生成提示詞
    
    Args:
        proposal: 研究提案
        chunks: 檢索到的文檔塊
        
    Returns:
        構建好的提示詞
    """
    context = build_context_from_chunks(chunks)
    
    prompt = f"""
你是一個專業的化學實驗設計師，需要基於研究提案和相關文獻設計詳細的實驗計劃。

研究提案：
{proposal}

相關文獻資料：
{context}

請設計詳細的實驗計劃，包含：
1. 實驗標題
2. 實驗目標
3. 實驗材料（包括規格和用量）
4. 詳細的實驗步驟
5. 預期結果和分析方法
6. 安全注意事項
7. 可能的問題和解決方案

要求：
- 步驟要詳細且可操作
- 包含具體的實驗條件（溫度、時間、濃度等）
- 考慮實驗安全
- 提供數據分析方法
"""
    
    return prompt


def build_iterative_proposal_prompt(
    original_proposal: str,
    user_feedback: str,
    chunks: List[Document]
) -> str:
    """
    構建迭代提案生成提示詞
    
    Args:
        original_proposal: 原始提案
        user_feedback: 用戶反饋
        chunks: 檢索到的文檔塊
        
    Returns:
        構建好的提示詞
    """
    context = build_context_from_chunks(chunks)
    
    prompt = f"""
你是一個專業的化學研究助理，需要根據用戶反饋修改研究提案。

原始提案：
{original_proposal}

用戶反饋：
{user_feedback}

相關文獻資料：
{context}

請根據用戶反饋修改提案，要求：
1. 保持提案的整體結構
2. 針對用戶反饋進行具體修改
3. 確保修改後的提案更加完善
4. 提供修改說明
5. 保持技術可行性和創新性

修改原則：
- 僅修改用戶不滿意的部分
- 其他部分保持原提案內容不變
- 確保修改後的內容與文獻資料一致
"""
    
    return prompt


def build_inference_prompt(
    question: str, 
    chunks: List[Document], 
    mode: str = "rigorous"
) -> str:
    """
    構建推理提示詞
    
    Args:
        question: 用戶問題
        chunks: 檢索到的文檔塊
        mode: 推理模式 ("rigorous" 或 "inference")
        
    Returns:
        構建好的提示詞
    """
    context = build_context_from_chunks(chunks)
    
    if mode == "rigorous":
        prompt = f"""
你是一個嚴謹的化學研究助理，請基於提供的文獻資料回答問題。

問題：{question}

相關文獻資料：
{context}

請嚴格基於提供的文獻資料回答問題，要求：
1. 只使用文獻中的信息
2. 提供具體的引用來源
3. 避免推測和假設
4. 如果文獻中沒有相關信息，請明確說明
5. 使用專業的化學術語
"""
    else:
        prompt = f"""
你是一個創新的化學研究助理，請基於提供的文獻資料進行推理和建議。

問題：{question}

相關文獻資料：
{context}

請基於文獻資料進行推理和建議，要求：
1. 分析文獻中的相關信息
2. 提出合理的推論和建議
3. 考慮技術發展趨勢
4. 提供創新的解決方案
5. 明確區分事實和推論
"""
    
    return prompt


def build_context_from_chunks(chunks: List[Document]) -> str:
    """
    從文檔塊構建上下文
    
    Args:
        chunks: 文檔塊列表
        
    Returns:
        格式化的上下文字符串
    """
    if not chunks:
        return "未找到相關文獻資料。"
    
    context_parts = []
    for i, chunk in enumerate(chunks, 1):
        metadata = chunk.metadata
        filename = metadata.get("filename") or metadata.get("source", "Unknown")
        page = metadata.get("page_number") or metadata.get("page", "?")
        
        context_parts.append(f"""
文獻 {i}：{filename} (頁碼：{page})
內容：{chunk.page_content}
---""")
    
    return "\n".join(context_parts)


def build_expand_query_prompt(original_query: str) -> str:
    """
    構建查詢擴展提示詞
    
    Args:
        original_query: 原始查詢
        
    Returns:
        構建好的提示詞
    """
    prompt = f"""
你是一個專業的化學文獻檢索專家，需要擴展查詢詞以提高檢索效果。

原始查詢：{original_query}

請生成3-5個相關的查詢詞，要求：
1. 包含同義詞和相關術語
2. 使用不同的表達方式
3. 涵蓋查詢的不同方面
4. 使用標準的化學術語
5. 每個查詢詞應該能夠獨立檢索到相關文獻

請直接返回查詢詞列表，每行一個，不要包含編號或其他格式。
"""
    
    return prompt
