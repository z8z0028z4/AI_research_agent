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

# 添加原項目路徑到 sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../app'))

from knowledge_agent import agent_answer
from rag_core import build_detail_experimental_plan_prompt
from pubchem_handler import chemical_metadata_extractor
from langchain_core.documents import Document

# SVG 轉換依賴檢查
try:
    from svglib.svglib import svg2rlg
    from reportlab.graphics import renderPDF
    SVGLIB_AVAILABLE = True
    print("✅ svglib 導入成功")
except ImportError as e:
    SVGLIB_AVAILABLE = False
    print(f"❌ svglib 導入失敗: {e}")

# PyMuPDF 用於 PDF 到 PNG 轉換
try:
    import fitz
    PYMUPDF_AVAILABLE = True
    print("✅ PyMuPDF 導入成功")
except ImportError as e:
    PYMUPDF_AVAILABLE = False
    print(f"⚠️ PyMuPDF 導入失敗: {e}")

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
    try:
        print(f"🔍 BACKEND DEBUG: 收到請求 research_goal = '{request.research_goal}'")
        print(f"🔍 BACKEND DEBUG: 準備調用 agent_answer with mode='make proposal'")
        print(f"🔍 BACKEND DEBUG: retrieval_count = {request.retrieval_count}")
        
        # 與 Streamlit Tab1 對齊：使用模式 make proposal 生成提案
        result = agent_answer(request.research_goal, mode="make proposal", k=request.retrieval_count)
        
        print(f"🔍 BACKEND DEBUG: agent_answer 調用成功")

        # 從回答中抽取化學品資訊與提案正文
        chemical_metadata_list, not_found_list, proposal_answer = chemical_metadata_extractor(
            result.get("answer", "")
        )

        citations = result.get("citations", [])
        chunks = result.get("chunks", [])

        # 修復 citations 中的 page 欄位類型問題
        fixed_citations = []
        for citation in citations:
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
            chunks=_serialize_chunks(chunks)
        )
        
    except Exception as e:
        print(f"❌ BACKEND DEBUG: 提案生成失敗: {str(e)}")
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
        # 與 Streamlit Tab1 對齊：採用 generate new idea 模式，並帶入原始提案與 chunks
        result = agent_answer(
            request.user_feedback,
            mode="generate new idea",
            old_chunks=_deserialize_chunks(request.chunks),
            proposal=request.original_proposal,
        )

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
            chunks=_serialize_chunks(result.get("chunks", []))
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
        # 與 Streamlit Tab1 對齊：由 agent 以指定模式展開實驗細節
        result = agent_answer(
            "",
            mode="expand to experiment detail",
            chunks=_deserialize_chunks(request.chunks),
            proposal=request.proposal,
        )

        return {
            "experiment_detail": result.get("answer", ""),
            "success": True
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

def clean_text_for_xml(text):
    """清理文本以確保XML兼容性"""
    if not text:
        return ""
    # 移除NULL字節和控制字符
    cleaned = "".join(char for char in text if ord(char) >= 32 or char in '\n\r\t')
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

def clean_markdown_text(text):
    """清理 markdown 格式，轉換為純文本"""
    if not text:
        return ""
    
    import re
    
    # 移除 markdown 格式
    cleaned = text
    cleaned = re.sub(r'\*\*(.*?)\*\*', r'\1', cleaned)  # 移除粗體標記
    cleaned = re.sub(r'\*(.*?)\*', r'\1', cleaned)  # 移除斜體標記
    cleaned = re.sub(r'`(.*?)`', r'\1', cleaned)  # 移除代碼標記
    cleaned = re.sub(r'^#+\s*(.*)$', r'\1', cleaned, flags=re.MULTILINE)  # 移除標題標記
    cleaned = re.sub(r'^\s*[-*+]\s+', '- ', cleaned, flags=re.MULTILINE)  # 統一項目符號
    cleaned = re.sub(r'^\s*\d+\.\s+', '', cleaned, flags=re.MULTILINE)  # 移除編號
    cleaned = re.sub(r'\n\s*\n\s*\n', '\n\n', cleaned)  # 移除多餘空行
    cleaned = re.sub(r'\n\s*\*\*', '\n', cleaned)  # 移除粗體前的換行
    cleaned = re.sub(r'\*\*\s*\n', '\n', cleaned)  # 移除粗體後的換行
    
    return cleaned

def get_nfpa_icon_image_stream(nfpa_code: str) -> io.BytesIO:
    """
    用 Headless Chrome 抓取 PubChem NFPA 圖，回傳 BytesIO PNG 圖片
    """
    nfpa_svg_url = f"https://pubchem.ncbi.nlm.nih.gov/image/nfpa.cgi?code={nfpa_code}"

    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=300,300")
    chrome_options.add_argument("--hide-scrollbars")

    driver = webdriver.Chrome(options=chrome_options)
    driver.get(nfpa_svg_url)
    time.sleep(1)

    png_data = driver.get_screenshot_as_png()
    driver.quit()

    image = Image.open(io.BytesIO(png_data))
    cropped = image.crop((0, 0, 100, 100))  # 你已經測試好的範圍
    output = io.BytesIO()
    cropped.save(output, format="PNG")
    output.seek(0)
    return output

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

            # 結構圖片
            img_url = chem.get("image_url")
            if img_url:
                try:
                    response = requests.get(img_url, verify=False, timeout=5)
                    if response.status_code == 200:
                        img_stream = BytesIO(response.content)
                        row[0].paragraphs[0].add_run().add_picture(img_stream, width=Inches(1))
                    else:
                        row[0].text = "Image not found"
                except Exception as e:
                    print(f"⚠️ 圖片下載失敗: {img_url}, {e}")
                    row[0].text = "Image error"
            else:
                row[0].text = "No image"

            # 文字欄位 - 使用清理函數
            row[1].text = clean_text_for_xml(chem.get("name", "-") or "-")
            row[2].text = clean_text_for_xml(chem.get("formula", "-") or "-")
            row[3].text = clean_text_for_xml(str(chem.get("weight", "-") or "-"))
            row[4].text = clean_text_for_xml(str(chem.get("boiling_point_c", "-") or "-"))
            row[5].text = clean_text_for_xml(str(chem.get("melting_point_c", "-") or "-"))
            row[6].text = clean_text_for_xml(chem.get("cas", "-") or "-")

            # Safety icons（支援多張 GHS + 1 張 NFPA）
            icons_cell = row[7].paragraphs[0]
            ghs_icons = chem.get("safety_icons", {}).get("ghs_icons", [])
            nfpa_icon_url = chem.get("safety_icons", {}).get("nfpa_image")
            
            for icon_url in ghs_icons:
                try:
                    icon_resp = requests.get(icon_url, verify=False, timeout=5)
                    if icon_resp.status_code == 200:
                        # 使用 svglib + PyMuPDF 轉換 SVG 為 PNG
                        if SVGLIB_AVAILABLE and PYMUPDF_AVAILABLE:
                            try:
                                # 步驟1：SVG 轉 PDF
                                drawing = svg2rlg(io.BytesIO(icon_resp.content))
                                if drawing:
                                    # 創建臨時 PDF 文件
                                    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_pdf:
                                        renderPDF.drawToFile(drawing, tmp_pdf.name)
                                    
                                    # 步驟2：PDF 轉 PNG
                                    pdf_document = fitz.open(tmp_pdf.name)
                                    page = pdf_document[0]
                                    pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))  # 2x 縮放
                                    
                                    # 將 PNG 轉換為 BytesIO
                                    png_stream = io.BytesIO()
                                    png_stream.write(pix.tobytes("png"))
                                    png_stream.seek(0)
                                    
                                    # 插入到 Word 文檔
                                    run = icons_cell.add_run()
                                    run.add_picture(png_stream, width=Inches(0.3))
                                    
                                    # 清理臨時文件
                                    pdf_document.close()
                                    os.unlink(tmp_pdf.name)
                                    
                                else:
                                    print(f"⚠️ SVG 轉換失敗 - drawing 為 None: {icon_url}")
                            except Exception as e:
                                print(f"⚠️ SVG 轉換錯誤: {icon_url}, {e}")
                        else:
                            print(f"⚠️ svglib 或 PyMuPDF 不可用，無法轉換 SVG: {icon_url}")
                except Exception as e:
                    print(f"⚠️ Failed to convert or insert icon: {icon_url}, {e}")

            if nfpa_icon_url:
                try:
                    # 從 URL 擷取出 NFPA code，例如 https://...code=130
                    from urllib.parse import urlparse, parse_qs
                    parsed = urlparse(nfpa_icon_url)
                    nfpa_code = parse_qs(parsed.query).get("code", [""])[0]

                    if nfpa_code:
                        image_stream = get_nfpa_icon_image_stream(nfpa_code)
                        if image_stream:
                            run = icons_cell.add_run()
                            run.add_picture(image_stream, width=Inches(0.3))
                    else:
                        print(f"⚠️ 無法從 URL 擷取 NFPA code: {nfpa_icon_url}")
                except Exception as e:
                    print(f"⚠️ Failed to convert or insert NFPA icon: {nfpa_icon_url}, {e}")

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