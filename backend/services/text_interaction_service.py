"""
文字互動服務
==========

負責處理文字反白互動功能，包括解釋和修改功能
"""

import time
import uuid
import traceback
from typing import Dict, Any, List, Optional
from backend.services.knowledge_service import agent_answer
from backend.services.rag_service import generate_structured_revision_proposal
from backend.core.retrieval import load_paper_vectorstore, retrieve_chunks_multi_query
from backend.core.query_expander import expand_query
from backend.services.chemical_service import ChemicalService
from backend.utils.logger import get_logger

logger = get_logger(__name__)


def process_text_interaction(
    highlighted_text: str,
    context_paragraph: str,
    user_input: str,
    interaction_type: str,
    highlighted_area: str = "proposal",  # 🔍 [NEW] 反白區域
    proposal: Optional[str] = None,
    old_chunks: Optional[List] = None,
    mode: str = "make proposal"
) -> Dict[str, Any]:
    """
    處理文字反白互動
    
    Args:
        highlighted_text: 反白的文字
        context_paragraph: 反白文字所在的段落
        user_input: 用戶輸入的問題或修改意見
        interaction_type: 互動類型 ("explain" 或 "revise")
        proposal: 原始提案（修改時需要）
        old_chunks: 原始文檔塊（修改時需要）
        mode: 處理模式
        
    Returns:
        Dict[str, Any]: 包含回答、引用和相關文檔塊的字典
    """
    
    # 生成唯一的請求 ID
    request_id = str(uuid.uuid4())[:8]
    start_time = time.time()
    
    # 驗證輸入參數
    if not highlighted_text or not highlighted_text.strip():
        raise ValueError("反白文字不能為空")
    
    if not user_input or not user_input.strip():
        raise ValueError("用戶輸入不能為空")
    
    # 獲取調用堆疊信息
    stack_info = traceback.extract_stack()
    caller_info = stack_info[-2] if len(stack_info) > 1 else stack_info[-1]
    
    logger.info(f"🧠 [TEXT-INTERACTION-{request_id}] ========== 文字互動處理開始 ==========")
    logger.info(f"🧠 [TEXT-INTERACTION-{request_id}] 時間戳: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"🧠 [TEXT-INTERACTION-{request_id}] 調用位置: {caller_info.filename}:{caller_info.lineno}")
    logger.info(f"🧠 [TEXT-INTERACTION-{request_id}] 互動類型: {interaction_type}")
    logger.info(f"🧠 [TEXT-INTERACTION-{request_id}] 反白區域: {highlighted_area}")  # 🔍 [NEW]
    logger.info(f"🧠 [TEXT-INTERACTION-{request_id}] 反白文字: '{highlighted_text[:100]}...'")
    logger.info(f"🧠 [TEXT-INTERACTION-{request_id}] 用戶輸入: '{user_input[:100]}...'")
    
    try:
        if interaction_type == "explain":
            return _process_explanation(
                highlighted_text, context_paragraph, user_input, mode, request_id
            )
        elif interaction_type == "revise":
            return _process_revision(
                highlighted_text, context_paragraph, user_input, highlighted_area, proposal, old_chunks, request_id
            )
        else:
            raise ValueError(f"不支援的互動類型: {interaction_type}")
            
    except Exception as e:
        logger.error(f"❌ [TEXT-INTERACTION-{request_id}] 處理失敗: {e}")
        raise e


def _process_explanation(
    highlighted_text: str,
    context_paragraph: str,
    user_input: str,
    mode: str,
    request_id: str
) -> Dict[str, Any]:
    """
    處理解釋功能
    
    Args:
        highlighted_text: 反白的文字
        context_paragraph: 反白文字所在的段落
        user_input: 用戶輸入的問題
        mode: 處理模式
        request_id: 請求ID
        
    Returns:
        Dict[str, Any]: 解釋結果
    """
    logger.info(f"🔍 [TEXT-INTERACTION-{request_id}] 開始處理解釋功能")
    
    # 構建查詢問題
    query = (
        f"Please explain the following text: {highlighted_text}\n\n"
        f"Context: {context_paragraph}\n\n"
        f"User question: {user_input}"
    )
    # 解釋功能始終使用嚴謹文獻溯源模式
    mode = "僅嚴謹文獻溯源"
    
    # 調用 agent_answer 函數
    result = agent_answer(query, mode=mode)
    
    logger.info(f"✅ [TEXT-INTERACTION-{request_id}] 解釋功能處理完成")
    
    # 轉換 chunks 為字典格式
    chunks = result.get("chunks", [])
    chunks_dict = []
    for chunk in chunks:
        if hasattr(chunk, 'page_content') and hasattr(chunk, 'metadata'):
            chunks_dict.append({
                "page_content": chunk.page_content,
                "metadata": chunk.metadata
            })
        else:
            chunks_dict.append(chunk)
    
    return {
        "answer": result.get("answer", ""),
        "citations": result.get("citations", []),
        "chunks": chunks_dict,
        "interaction_type": "explain",
        "highlighted_text": highlighted_text,
        "user_input": user_input,
        "timestamp": time.time(),
        "request_id": request_id  # 添加request_id
    }


def _process_revision(
    highlighted_text: str,
    context_paragraph: str,
    user_input: str,
    highlighted_area: str,  # 🔍 [NEW] 反白區域
    proposal: str,
    old_chunks: List,
    request_id: str
) -> Dict[str, Any]:
    """
    處理修改功能
    
    Args:
        highlighted_text: 反白的文字
        context_paragraph: 反白文字所在的段落
        user_input: 用戶輸入的修改意見
        highlighted_area: 反白區域 ("proposal", "experiment", "chemical")
        proposal: 原始提案
        old_chunks: 原始文檔塊
        request_id: 請求ID
        
    Returns:
        Dict[str, Any]: 修改結果
    """
    logger.info(f"🔧 [TEXT-INTERACTION-{request_id}] 開始處理修改功能")
    logger.info(f"🔧 [TEXT-INTERACTION-{request_id}] 反白區域: {highlighted_area}")
    
    # 🔍 [NEW] 根據反白區域選擇不同的 workflow
    if highlighted_area == "experiment":
        logger.info(f"🔧 [TEXT-INTERACTION-{request_id}] 使用實驗細節修改 workflow")
        return _process_experiment_revision(
            highlighted_text, context_paragraph, user_input, proposal, old_chunks, request_id
        )
    else:
        # 默認使用提案修改 workflow（包括 chemical 區域）
        logger.info(f"🔧 [TEXT-INTERACTION-{request_id}] 使用提案修改 workflow")
        return _process_proposal_revision(
            highlighted_text, context_paragraph, user_input, proposal, old_chunks, request_id
        )


def _process_proposal_revision(
    highlighted_text: str,
    context_paragraph: str,
    user_input: str,
    proposal: str,
    old_chunks: List,
    request_id: str
) -> Dict[str, Any]:
    """
    處理提案修改功能（原有的 generate new idea workflow）
    
    Args:
        highlighted_text: 反白的文字
        context_paragraph: 反白文字所在的段落
        user_input: 用戶輸入的修改意見
        proposal: 原始提案
        old_chunks: 原始文檔塊
        request_id: 請求ID
        
    Returns:
        Dict[str, Any]: 修改結果
    """
    logger.info(f"🔧 [TEXT-INTERACTION-{request_id}] 開始處理提案修改功能")
    
    # 使用與 "generate new idea" 相同的邏輯
    paper_vectorstore = load_paper_vectorstore()
    logger.info(f"📦 Paper 向量庫：{paper_vectorstore._collection.count()}")
    
    # 構建查詢問題
    query = (
        f"Please revise the relevant parts of the proposal according to the following feedback: {user_input}\n\n"
        f"Text to be revised: {highlighted_text}\n\n"
        f"Context: {context_paragraph}"
    )
    # 語義擴展
    query_list = expand_query(query)
    
    # 檢索新的文檔塊
    k_new_chunks = 3  # 每個查詢檢索的chunks數量
    new_chunks = retrieve_chunks_multi_query(paper_vectorstore, query_list, k=k_new_chunks)
    
    # 使用結構化修訂提案生成
    structured_data = generate_structured_revision_proposal(query, new_chunks, old_chunks, proposal)
    
    # 轉換為文本格式
    from backend.core.format_converter import structured_revision_proposal_to_text
    text_proposal = structured_revision_proposal_to_text(structured_data)
    
    # 轉換新檢索到的chunks為citations格式
    new_citations = []
    for i, doc in enumerate(new_chunks):
        if hasattr(doc, 'metadata'):
            metadata = doc.metadata
            page_content = doc.page_content
        else:
            metadata = doc.get('metadata', {})
            page_content = doc.get('page_content', '')
        
        title = metadata.get("title", "Untitled")
        filename = metadata.get("filename") or metadata.get("source", "Unknown")
        page = metadata.get("page_number") or metadata.get("page", "?")
        
        new_citations.append({
            "label": f"[{i+1}]",
            "title": title,
            "source": filename,
            "page": page
        })
    
    # 處理化學品信息
    chemicals = []
    if structured_data and 'materials_list' in structured_data:
        logger.info(f"🔧 [TEXT-INTERACTION-{request_id}] 處理材料列表: {structured_data['materials_list']}")
        
        # 提取化學品信息
        from backend.services.pubchem_service import extract_and_fetch_chemicals
        chemical_metadata_list, not_found_list = extract_and_fetch_chemicals(structured_data['materials_list'])
        
        # 添加 SMILES 繪製
        chemical_service = ChemicalService()
        chemicals = []
        for chemical in chemical_metadata_list:
            enhanced_chemical = chemical_service.add_smiles_drawing(chemical)
            chemicals.append(enhanced_chemical)
        
        logger.info(f"🔧 [TEXT-INTERACTION-{request_id}] 化學品處理完成，數量: {len(chemicals)}")
    
    # 轉換 chunks 為字典格式
    chunks_dict = []
    for doc in new_chunks + old_chunks:
        if hasattr(doc, 'metadata'):
            chunks_dict.append({
                "content": doc.page_content,
                "metadata": doc.metadata
            })
        else:
            chunks_dict.append(doc)
    
    logger.info(f"✅ [TEXT-INTERACTION-{request_id}] 提案修改功能處理完成")
    
    return {
        "answer": text_proposal,
        "citations": new_citations,
        "chunks": chunks_dict,
        "interaction_type": "revise",
        "highlighted_text": highlighted_text,
        "user_input": user_input,
        "timestamp": time.time(),
        "request_id": request_id,  # 添加request_id
        "structured_proposal": structured_data,
        "chemicals": chemicals
    }


def _process_experiment_revision(
    highlighted_text: str,
    context_paragraph: str,
    user_input: str,
    proposal: str,
    old_chunks: List,
    request_id: str
) -> Dict[str, Any]:
    """
    處理實驗細節修改功能
    
    Args:
        highlighted_text: 反白的文字
        context_paragraph: 反白文字所在的段落
        user_input: 用戶輸入的修改意見
        proposal: 原始提案
        old_chunks: 原始文檔塊
        request_id: 請求ID
        
    Returns:
        Dict[str, Any]: 修改結果
    """
    logger.info(f"🔧 [TEXT-INTERACTION-{request_id}] 開始處理實驗細節修改功能")
    
    # Construct user revision request in English
    user_prompt = (
        f"Please revise the relevant parts of the experimental details according to the following suggestion: {user_input}\n\n"
        f"Text to be revised: {highlighted_text}\n\n"
        f"Context: {context_paragraph}"
    )

    logger.info(f"🔧 [TEXT-INTERACTION-{request_id}] User revision request length: {len(user_prompt)}")
    # 獲取原始實驗細節（從 proposal 中提取）
    # 嘗試從 proposal 中提取實驗概述作為原始實驗細節
    original_experimental_detail = ""
    if proposal:
        # 簡單的提取邏輯：尋找包含 "Experimental" 或 "experimental" 的部分
        lines = proposal.split('\n')
        experimental_lines = []
        in_experimental_section = False
        
        for line in lines:
            if 'experimental' in line.lower() or 'experiment' in line.lower():
                in_experimental_section = True
                experimental_lines.append(line)
            elif in_experimental_section and line.strip():
                experimental_lines.append(line)
            elif in_experimental_section and not line.strip():
                break
        
        original_experimental_detail = '\n'.join(experimental_lines) if experimental_lines else "No experimental details found in proposal"
    else:
        original_experimental_detail = "No proposal provided"
    
    # 直接使用實驗細節修改功能，傳入用戶修改請求
    # 不需要語義擴展和向量檢索，直接使用原始chunks
    from backend.services.rag_service import generate_structured_revision_experimental_detail
    structured_data = generate_structured_revision_experimental_detail(
        user_prompt, [], old_chunks, proposal, original_experimental_detail
    )
    
    # 轉換為文本格式
    from backend.core.format_converter import structured_revision_experimental_detail_to_text
    text_experiment = structured_revision_experimental_detail_to_text(structured_data)
    
    # 轉換chunks為citations格式
    citations = []
    for i, doc in enumerate(old_chunks):
        if hasattr(doc, 'metadata'):
            metadata = doc.metadata
        else:
            metadata = doc.get('metadata', {})
        
        title = metadata.get("title", "Untitled")
        filename = metadata.get("filename") or metadata.get("source", "Unknown")
        page = metadata.get("page_number") or metadata.get("page", "?")
        
        citations.append({
            "label": f"[{i+1}]",
            "title": title,
            "source": filename,
            "page": page
        })
    
    # 轉換 chunks 為字典格式
    chunks_dict = []
    for doc in old_chunks:
        if hasattr(doc, 'metadata'):
            chunks_dict.append({
                "content": doc.page_content,
                "metadata": doc.metadata
            })
        else:
            chunks_dict.append(doc)
    
    logger.info(f"✅ [TEXT-INTERACTION-{request_id}] 實驗細節修改功能處理完成")
    
    return {
        "answer": text_experiment,
        "citations": citations,
        "chunks": chunks_dict,
        "interaction_type": "revise",
        "highlighted_text": highlighted_text,
        "user_input": user_input,
        "timestamp": time.time(),
        "request_id": request_id,  # 添加request_id
        "structured_experiment": structured_data,  # 注意：這裡返回 structured_experiment
        "chemicals": []  # 實驗細節修改不涉及化學品
    }





def extract_context_paragraph(text: str, highlighted_text: str, context_size: int = 200) -> str:
    """
    提取反白文字附近的上下文段落
    
    Args:
        text: 完整文本
        highlighted_text: 反白的文字
        context_size: 上下文大小（字符數）
        
    Returns:
        str: 上下文段落
    """
    try:
        # 找到反白文字在完整文本中的位置
        start_pos = text.find(highlighted_text)
        if start_pos == -1:
            return text[:context_size]  # 如果找不到，返回開頭部分
        
        # 計算上下文範圍
        context_start = max(0, start_pos - context_size // 2)
        context_end = min(len(text), start_pos + len(highlighted_text) + context_size // 2)
        
        # 嘗試找到段落邊界
        if context_start > 0:
            # 向前找到段落開始
            paragraph_start = text.rfind('\n\n', 0, context_start)
            if paragraph_start != -1:
                context_start = paragraph_start + 2
        
        if context_end < len(text):
            # 向後找到段落結束
            paragraph_end = text.find('\n\n', context_end)
            if paragraph_end != -1:
                context_end = paragraph_end
        
        # 提取上下文段落（修正：重新提取文本）
        context = text[context_start:context_end].strip()
        
        # 如果上下文太短，擴展範圍
        if len(context) < len(highlighted_text) + 50:
            # 擴展到包含更多上下文
            expanded_start = max(0, context_start - context_size // 4)
            expanded_end = min(len(text), context_end + context_size // 4)
            context = text[expanded_start:expanded_end].strip()
        
        return context
        
    except Exception as e:
        logger.error(f"提取上下文段落失敗: {e}")
        return text[:context_size] 