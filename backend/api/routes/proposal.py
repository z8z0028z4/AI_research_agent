"""
提案生成 API 路由
================

處理研究提案的生成、編輯和修訂功能
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import asyncio
import sys
import os
import tempfile
import io
import requests
from docx import Document as DocxDocument
from docx.shared import Inches
from io import BytesIO
from ..services.docx_utils import (
    clean_text_for_xml,
    clean_markdown_text,
    get_image_stream_from_url,
    get_ghs_icon_stream,
    get_nfpa_icon_image_stream,
)

# 添加原項目路徑到 sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../app'))

# 延遲導入以避免循環導入問題
# from knowledge_agent import agent_answer
# from rag_core import build_detail_experimental_plan_prompt
from pubchem_handler import chemical_metadata_extractor
from langchain_core.documents import Document

# SVG 轉換依賴檢查
try:
    from svglib.svglib import svg2rlg
    from reportlab.graphics import renderPDF
    SVGLIB_AVAILABLE = True
except ImportError as e:
    SVGLIB_AVAILABLE = False

# PyMuPDF 用於 PDF 到 PNG 轉換
try:
    import fitz
    PYMUPDF_AVAILABLE = True
except ImportError as e:
    PYMUPDF_AVAILABLE = False

import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from PIL import Image

router = APIRouter()

class ProposalRequest(BaseModel):
    """提案生成請求模型"""
    research_goal: str
    user_feedback: Optional[str] = None
    previous_proposal: Optional[str] = None
    retrieval_count: Optional[int] = 10  # 預設檢索 10 個文檔

class ProposalResponse(BaseModel):
    """提案生成響應模型"""
    proposal: str
    chemicals: List[Dict[str, Any]]
    experiment_detail: Optional[str] = None
    citations: List[Dict[str, str]]
    not_found: List[str]
    # 以可序列化的結構回傳 chunks：[{ page_content, metadata }]
    chunks: List[Dict[str, Any]]
    used_model: Optional[str] = None
    structured_proposal: Optional[Dict[str, Any]] = None
    structured_revision_explain: Optional[Dict[str, Any]] = None

class ProposalRevisionRequest(BaseModel):
    """提案修訂請求模型"""
    original_proposal: str
    user_feedback: str
    # 來自前端的可序列化 chunks
    chunks: List[Dict[str, Any]]


def _serialize_chunks(chunks: List[Any]) -> List[Dict[str, Any]]:
    """將 LangChain Document 物件序列化為可回傳的 dict 結構。"""
    serialized: List[Dict[str, Any]] = []
    for doc in chunks or []:
        try:
            serialized.append({
                "page_content": getattr(doc, "page_content", ""),
                "metadata": getattr(doc, "metadata", {}) or {}
            })
        except Exception:
            continue
    return serialized


def _deserialize_chunks(chunks_like: List[Dict[str, Any]]) -> List[Document]:
    """將前端傳來的 dict 結構還原為 LangChain Document。"""
    documents: List[Document] = []
    for item in chunks_like or []:
        page_content = item.get("page_content", "")
        metadata = item.get("metadata", {}) or {}
        documents.append(Document(page_content=page_content, metadata=metadata))
    return documents

@router.post("/proposal/generate", response_model=ProposalResponse)
async def generate_proposal(request: ProposalRequest):
    """
    生成研究提案
    
    Args:
        request: 包含研究目標的請求
        
    Returns:
        生成的提案內容，包括化學品信息和實驗細節
    """
    import time
    import uuid
    
    # 生成唯一的請求 ID
    request_id = str(uuid.uuid4())[:8]
    start_time = time.time()
    
    print(f"🚀 [DEBUG-{request_id}] ========== 開始處理提案生成請求 ==========")
    print(f"🚀 [DEBUG-{request_id}] 時間戳: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🚀 [DEBUG-{request_id}] 收到請求 research_goal = '{request.research_goal}'")
    print(f"🚀 [DEBUG-{request_id}] retrieval_count = {request.retrieval_count}")
    print(f"🚀 [DEBUG-{request_id}] 請求來源: {request}")
    
    try:
        print(f"🔍 [DEBUG-{request_id}] 準備調用 agent_answer with mode='make proposal'")
        
        # 延遲導入以避免循環導入問題
        from knowledge_agent import agent_answer
        
        # 與 Streamlit Tab1 對齊：使用模式 make proposal 生成提案
        result = agent_answer(request.research_goal, mode="make proposal", k=request.retrieval_count)
        
        print(f"🔍 [DEBUG-{request_id}] agent_answer 調用成功")
        print(f"🔍 [DEBUG-{request_id}] result 類型: {type(result)}")
        print(f"🔍 [DEBUG-{request_id}] result 鍵: {list(result.keys())}")
        print(f"🔍 [DEBUG-{request_id}] result['answer'] 長度: {len(result.get('answer', ''))}")
        print(f"🔍 [DEBUG-{request_id}] result['answer'] 內容: {result.get('answer', '')[:200]}...")

        # 從回答中抽取化學品資訊與提案正文
        print(f"🔍 [DEBUG-{request_id}] 準備調用 chemical_metadata_extractor")
        chemical_metadata_list, not_found_list, proposal_answer = chemical_metadata_extractor(
            result.get("answer", "")
        )
        print(f"🔍 [DEBUG-{request_id}] chemical_metadata_extractor 完成")
        print(f"🔍 [DEBUG-{request_id}] proposal_answer 長度: {len(proposal_answer)}")
        print(f"🔍 [DEBUG-{request_id}] chemical_metadata_list 數量: {len(chemical_metadata_list)}")

        citations = result.get("citations", [])
        chunks = result.get("chunks", [])
        used_model = result.get("used_model", "unknown")

        # 修復 citations 中的 page 欄位類型問題
        fixed_citations = []
        for citation in citations:
            fixed_citation = citation.copy()
            # 確保 page 欄位是字串
            if "page" in fixed_citation:
                fixed_citation["page"] = str(fixed_citation["page"])
            fixed_citations.append(fixed_citation)

        end_time = time.time()
        duration = end_time - start_time
        
        print(f"✅ [DEBUG-{request_id}] ========== 提案生成完成 ==========")
        print(f"✅ [DEBUG-{request_id}] 總耗時: {duration:.2f} 秒")
        print(f"✅ [DEBUG-{request_id}] 檢索到的文檔數量: {len(chunks)}")
        print(f"✅ [DEBUG-{request_id}] 引用數量: {len(fixed_citations)}")
        print(f"✅ [DEBUG-{request_id}] 化學品數量: {len(chemical_metadata_list)}")

        return ProposalResponse(
            proposal=proposal_answer,
            chemicals=chemical_metadata_list,
            citations=fixed_citations,
            not_found=not_found_list,
            chunks=_serialize_chunks(chunks),
            used_model=used_model
        )
        
    except Exception as e:
        end_time = time.time()
        duration = end_time - start_time
        print(f"❌ [DEBUG-{request_id}] ========== 提案生成失敗 ==========")
        print(f"❌ [DEBUG-{request_id}] 總耗時: {duration:.2f} 秒")
        print(f"❌ [DEBUG-{request_id}] 錯誤: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"提案生成失敗: {str(e)}")

@router.post("/proposal/revise", response_model=ProposalResponse)
async def revise_proposal(request: ProposalRevisionRequest):
    """
    根據用戶反饋修訂提案
    
    Args:
        request: 包含原始提案和用戶反饋的請求
        
    Returns:
        修訂後的提案內容
    """
    try:
        # 延遲導入以避免循環導入問題
        from knowledge_agent import agent_answer
        
        # 與 Streamlit Tab1 對齊：採用 generate new idea 模式，並帶入原始提案與 chunks
        result = agent_answer(
            request.user_feedback,
            mode="generate new idea",
            old_chunks=_deserialize_chunks(request.chunks),
            proposal=request.original_proposal,
        )

        # 檢查是否有直接的材料列表（來自結構化輸出）
        if result.get("materials_list"):
            print(f"🔍 [DEBUG] 使用結構化數據中的材料列表: {result['materials_list']}")
            # 直接使用結構化數據中的材料列表
            from pubchem_handler import extract_and_fetch_chemicals, remove_json_chemical_block
            chemical_metadata_list, not_found_list = extract_and_fetch_chemicals(result["materials_list"])
            # 清理文本中的 JSON 化學品塊
            proposal_answer = remove_json_chemical_block(result.get("answer", ""))
        else:
            # 回退到從文本中提取
            print(f"🔍 [DEBUG] 回退到從文本中提取材料列表")
            chemical_metadata_list, not_found_list, proposal_answer = chemical_metadata_extractor(
                result.get("answer", "")
            )

        # 修復 citations 中的 page 欄位類型問題
        fixed_citations = []
        for citation in result.get("citations", []):
            fixed_citation = citation.copy()
            # 確保 page 欄位是字串
            if "page" in fixed_citation:
                fixed_citation["page"] = str(fixed_citation["page"])
            fixed_citations.append(fixed_citation)

        return ProposalResponse(
            proposal=proposal_answer,
            chemicals=chemical_metadata_list,
            citations=fixed_citations,
            not_found=not_found_list,
            chunks=_serialize_chunks(result.get("chunks", [])),
            structured_proposal=result.get("structured_proposal")
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"提案修訂失敗: {str(e)}")

class ExperimentDetailRequest(BaseModel):
    """生成實驗細節請求模型"""
    proposal: str
    chunks: List[Dict[str, Any]]


@router.post("/proposal/experiment-detail")
async def generate_experiment_detail(request: ExperimentDetailRequest):
    """
    生成實驗細節
    
    Args:
        proposal: 提案內容
        chunks: 相關文檔片段
        
    Returns:
        實驗細節內容
    """
    try:
        # 延遲導入以避免循環導入問題
        from knowledge_agent import agent_answer
        
        # 與 Streamlit Tab1 對齊：由 agent 以指定模式展開實驗細節
        result = agent_answer(
            "",
            mode="expand to experiment detail",
            chunks=_deserialize_chunks(request.chunks),
            proposal=request.proposal,
        )

        return {
            "experiment_detail": result.get("answer", ""),
            "structured_experiment": result.get("structured_experiment", {}),
            "success": True,
            "retry_info": {
                "retry_count": getattr(result, 'retry_count', 0),
                "final_tokens": getattr(result, 'final_tokens', 0)
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"實驗細節生成失敗: {str(e)}")

@router.get("/proposal/status/{task_id}")
async def get_proposal_status(task_id: str):
    """
    獲取提案生成任務狀態
    
    Args:
        task_id: 任務 ID
        
    Returns:
        任務狀態信息
    """
    # TODO: 實現任務狀態追蹤
    return {
        "task_id": task_id,
        "status": "completed",
        "progress": 100
    }


class DocxRequest(BaseModel):
    """DOCX 生成請求模型"""
    proposal: str
    chemicals: List[Dict[str, Any]]
    not_found: List[str]
    experiment_detail: Optional[str] = ""
    citations: List[Dict[str, str]]

@router.post("/proposal/generate-docx")
async def generate_docx(request: DocxRequest):
    """
    生成 DOCX 文件
    
    Args:
        request: 包含所有提案數據的請求
        
    Returns:
        DOCX 文件下載響應
    """
    tmp_path = None
    try:
        print(f"🔍 BACKEND DEBUG: 開始生成 DOCX 文件")
        print(f"🔍 BACKEND DEBUG: proposal 長度: {len(request.proposal)}")
        print(f"🔍 BACKEND DEBUG: chemicals 數量: {len(request.chemicals)}")
        print(f"🔍 BACKEND DEBUG: experiment_detail 長度: {len(request.experiment_detail)}")
        print(f"🔍 BACKEND DEBUG: citations 數量: {len(request.citations)}")
        
        doc = DocxDocument()
        doc.add_heading("AI Generated Research Proposal", 0)

        # Proposal Section
        doc.add_heading("Proposal", level=1)
        proposal_text = clean_text_for_xml(clean_markdown_text(request.proposal))
        doc.add_paragraph(proposal_text)

        # Chemical Table
        doc.add_heading("Chemical Summary Table", level=1)
        table = doc.add_table(rows=1, cols=8)  # 多兩欄：Structure + Safety
        hdr = table.rows[0].cells
        hdr[0].text = "Structure"
        hdr[1].text = "Name"
        hdr[2].text = "Formula"
        hdr[3].text = "MW"
        hdr[4].text = "Boiling Point (°C)"
        hdr[5].text = "Melting Point (°C)"
        hdr[6].text = "CAS No."
        hdr[7].text = "Safety Icons"

        for chem in request.chemicals:
            row = table.add_row().cells

            # Structure image
            img_url = chem.get("image_url")
            img_stream = get_image_stream_from_url(img_url)
            if img_stream:
                row[0].paragraphs[0].add_run().add_picture(img_stream, width=Inches(1))
            else:
                row[0].text = "No image"

            # Text fields - using cleaning functions
            row[1].text = clean_text_for_xml(chem.get("name", "-") or "-")
            row[2].text = clean_text_for_xml(chem.get("formula", "-") or "-")
            row[3].text = clean_text_for_xml(str(chem.get("weight", "-") or "-"))
            row[4].text = clean_text_for_xml(str(chem.get("boiling_point_c", "-") or "-"))
            row[5].text = clean_text_for_xml(str(chem.get("melting_point_c", "-") or "-"))
            row[6].text = clean_text_for_xml(chem.get("cas", "-") or "-")

            # Safety icons (GHS + NFPA)
            icons_cell = row[7].paragraphs[0]
            ghs_icons = chem.get("safety_icons", {}).get("ghs_icons", [])
            nfpa_icon_url = chem.get("safety_icons", {}).get("nfpa_image")

            for icon_url in ghs_icons:
                icon_stream = get_ghs_icon_stream(icon_url)
                if icon_stream:
                    run = icons_cell.add_run()
                    run.add_picture(icon_stream, width=Inches(0.3))

            if nfpa_icon_url:
                from urllib.parse import urlparse, parse_qs
                parsed = urlparse(nfpa_icon_url)
                nfpa_code = parse_qs(parsed.query).get("code", [""])[0]
                if nfpa_code:
                    image_stream = get_nfpa_icon_image_stream(nfpa_code)
                    if image_stream:
                        run = icons_cell.add_run()
                        run.add_picture(image_stream, width=Inches(0.3))

        # Not Found Chemicals
        if request.not_found:
            doc.add_heading("Not Found Chemicals", level=2)
            for name in request.not_found:
                doc.add_paragraph(f"- {clean_text_for_xml(name)}")

        # Experiment Details
        doc.add_heading("Experimental Plan", level=1)
        experiment_text = clean_text_for_xml(clean_markdown_text(request.experiment_detail))
        doc.add_paragraph(experiment_text)

        # Citations
        doc.add_heading("Citations", level=1)
        for i, c in enumerate(request.citations, 1):
            title = clean_text_for_xml(c.get('title', ''))
            page = clean_text_for_xml(str(c.get('page', '')))
            snippet = clean_text_for_xml(c.get('snippet', ''))
            doc.add_paragraph(f"[{i}] {title} | Page {page} | Snippet: {snippet}")

        # Save and Download
        with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as tmp:
            doc.save(tmp.name)
            tmp_path = tmp.name
            print(f"🔍 BACKEND DEBUG: DOCX 文件已保存到: {tmp_path}")

        print(f"🔍 BACKEND DEBUG: 準備返回 FileResponse")
        return FileResponse(
            path=tmp_path,
            filename="proposal_report.docx",
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
        
    except Exception as e:
        print(f"❌ BACKEND DEBUG: DOCX 生成失敗: {str(e)}")
        import traceback
        traceback.print_exc()
        # 清理臨時文件
        if tmp_path and os.path.exists(tmp_path):
            try:
                os.unlink(tmp_path)
            except:
                pass
        raise HTTPException(status_code=500, detail=f"DOCX 生成失敗: {str(e)}") 

@router.post("/proposal/test-docx")
async def test_docx_generation():
    """
    測試 DOCX 生成功能
    """
    try:
        print(f"🔍 BACKEND DEBUG: 測試 DOCX 生成")
        
        doc = DocxDocument()
        doc.add_heading("Test Document", 0)
        doc.add_paragraph("This is a test document to verify DOCX generation works.")

        # Save and Download
        with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as tmp:
            doc.save(tmp.name)
            tmp_path = tmp.name
            print(f"🔍 BACKEND DEBUG: 測試 DOCX 文件已保存到: {tmp_path}")

        return FileResponse(
            path=tmp_path,
            filename="test_document.docx",
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
        
    except Exception as e:
        print(f"❌ BACKEND DEBUG: 測試 DOCX 生成失敗: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"測試 DOCX 生成失敗: {str(e)}") 